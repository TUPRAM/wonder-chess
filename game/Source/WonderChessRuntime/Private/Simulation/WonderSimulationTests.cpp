#if WITH_DEV_AUTOMATION_TESTS
#include "HAL/FileManager.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Simulation/WonderSimulation.h"
#include "WCDefinitionRegistry.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCArithmeticTest, "WonderChess.Runtime.IntegerContracts",
                                 EAutomationTestFlags_ApplicationContextMask |
                                     EAutomationTestFlags::EngineFilter)
bool FWCArithmeticTest::RunTest(const FString &Parameters)
{
    wc::Catalog Catalog;
    FString Error;
    if (!TestTrue(TEXT("Load staged canonical catalog"), wc::LoadCatalog(Catalog, Error)))
    {
        AddError(Error);
        return false;
    }
    TestEqual(TEXT("Twelve alpha definitions"), static_cast<int32>(Catalog.units.size()), 12);
    TestEqual(TEXT("Physical mitigation"), wc::ResolveDamage(12000, wc::DamageType::Physical, 50, 0),
              wc::Int(8000));
    TestEqual(TEXT("Magic mitigation"), wc::ResolveDamage(12000, wc::DamageType::Magic, 0, 20),
              wc::Int(10000));
    TestEqual(TEXT("True bypass"), wc::ResolveDamage(9000, wc::DamageType::True, 100, 100), wc::Int(9000));
    TestEqual(TEXT("Additive rate bonuses"), wc::AttackInterval(800, 2500, Catalog.rules), 20);
    TestEqual(TEXT("Star health with additive bonus"), wc::StarValue(100000, 2, 2500, Catalog.rules),
              wc::Int(225000));
    wc::Match Match(Catalog, 7, 1);
    wc::Command Buy;
    Buy.type = wc::CommandType::Buy;
    Buy.seat = 0;
    Buy.requestId = 1;
    Buy.sequence = Match.Seats()[0].sequence + 1;
    Buy.revision = Match.Seats()[0].revision;
    Buy.slot = 0;
    TestFalse(TEXT("Reject unauthenticated seat"), Match.Submit(1, Buy).accepted);
    TestTrue(TEXT("Accept authenticated purchase"), Match.Submit(0, Buy).accepted);
    const int Gold = Match.Seats()[0].gold;
    TestTrue(TEXT("Idempotent replay"), Match.Submit(0, Buy).accepted);
    TestEqual(TEXT("Replay pays once"), Match.Seats()[0].gold, Gold);
    TestTrue(TEXT("Persistent state valid"), Match.InvariantError().empty());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCRetainedRecapTest, "WonderChess.Runtime.RetainedRecapAfterHitch",
                                 EAutomationTestFlags_ApplicationContextMask |
                                     EAutomationTestFlags::EngineFilter)
bool FWCRetainedRecapTest::RunTest(const FString &Parameters)
{
    wc::Catalog Catalog;
    FString Error;
    if (!wc::LoadCatalog(Catalog, Error))
    {
        AddError(Error);
        return false;
    }
    wc::Match Match(Catalog, 1, 0);
    while (Match.Records().empty() && Match.ElapsedMs() < 100000)
        Match.Tick(50);
    if (!TestTrue(TEXT("Actual settlement reached"), !Match.Records().empty() &&
                      Match.CurrentPhase() == wc::Phase::Settlement))
        return false;
    const auto Record = Match.Records().back();
    if (!TestEqual(TEXT("One summary per actual encounter"), Record.encounters.size(), Match.Encounters().size()))
        return false;
    for (std::size_t Index = 0; Index < Record.encounters.size(); ++Index)
    {
        const auto &Encounter = Match.Encounters()[Index];
        const auto &Summary = Record.encounters[Index];
        std::array<wc::Int, 2> Loss{}, Absorbed{}, Healed{};
        for (const auto &Unit : Encounter.combat.Units())
            for (const auto &Event : Encounter.combat.Events())
                if (Event.target == Unit.id)
                {
                    Loss[Unit.side] += Event.healthLoss;
                    Absorbed[Unit.side] += Event.absorbed;
                    if (Event.effect == wc::Effect::Heal)
                        Healed[Unit.side] += Event.resolved;
                }
        TestTrue(TEXT("Target-side totals match actual events"), Summary.healthLoss == Loss &&
                     Summary.absorbed == Absorbed && Summary.healing == Healed);
        TestEqual(TEXT("Actual result retained"), Summary.result.ticks, Encounter.combat.Result().ticks);
    }
    Match.Tick(Catalog.rules.settlementMs + 50);
    TestTrue(TEXT("Hitch entered next preparation with live encounter data cleared"),
             Match.CurrentPhase() == wc::Phase::Preparation && Match.Round() == Record.round + 1 &&
             Match.Encounters().empty());
    const auto &Retained = Match.Records().back();
    TestTrue(TEXT("Settlement arrays and hash unchanged"), Retained.damage == Record.damage &&
             Retained.health == Record.health && Retained.postHash == Record.postHash);
    for (std::size_t Index = 0; Index < Record.encounters.size(); ++Index)
        TestTrue(TEXT("Recap remains available after hitch"),
                 Retained.encounters[Index].healthLoss == Record.encounters[Index].healthLoss &&
                 Retained.encounters[Index].absorbed == Record.encounters[Index].absorbed &&
                 Retained.encounters[Index].healing == Record.encounters[Index].healing);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCAllBotCombatTest, "WonderChess.Runtime.OneHundredActualCombatTournaments",
                                 EAutomationTestFlags_ApplicationContextMask |
                                     EAutomationTestFlags::EngineFilter)
bool FWCAllBotCombatTest::RunTest(const FString &Parameters)
{
    wc::Catalog Catalog;
    FString Error;
    if (!wc::LoadCatalog(Catalog, Error))
    {
        AddError(Error);
        return false;
    }
    FString Csv = TEXT("seed,rounds,simulated_ms,encounters,timeouts,ghosts,commands,rejects,final_hash\n");
    FString RoundCsv =
        TEXT("seed,round,seat,health,gold,damage,wins,placement,settlement_id,pre_hash,post_hash\n");
    int64 TotalEncounters = 0;
    for (int Seed = 1; Seed <= 100; ++Seed)
    {
        wc::Match Match(Catalog, Seed, 0);
        while (Match.CurrentPhase() != wc::Phase::Finished && Match.CurrentPhase() != wc::Phase::Aborted &&
               Match.ElapsedMs() < 2000000)
        {
            Match.Tick(50);
            const auto Invariant = Match.InvariantError();
            if (!Invariant.empty())
            {
                AddError(
                    FString::Printf(TEXT("Seed %d invariant: %s"), Seed, UTF8_TO_TCHAR(Invariant.c_str())));
                return false;
            }
        }
        if (!TestTrue(FString::Printf(TEXT("Seed %d finishes real combat"), Seed),
                      Match.CurrentPhase() == wc::Phase::Finished))
            return false;
        int Encounters = 0, Timeouts = 0, Ghosts = 0, Rejects = 0;
        for (const auto &Record : Match.Records())
        {
            Encounters += static_cast<int>(Record.results.size());
            for (const auto &Result : Record.results)
                Timeouts += Result.timeout ? 1 : 0;
            for (const auto &Pair : Record.pairs)
                Ghosts += Pair.ghost ? 1 : 0;
            for (int Seat = 0; Seat < 8; ++Seat)
                RoundCsv += FString::Printf(TEXT("%d,%d,%d,%d,%d,%d,%d,%d,%llu,%llu,%llu\n"), Seed,
                                            Record.round, Seat, Record.health[Seat], Record.gold[Seat],
                                            Record.damage[Seat], Record.wins[Seat], Record.placement[Seat],
                                            Record.settlementId, Record.preHash, Record.postHash);
        }
        for (const auto &Log : Match.BotLog())
            Rejects += Log.reply.accepted ? 0 : 1;
        TestEqual(FString::Printf(TEXT("Seed %d legal bot commands"), Seed), Rejects, 0);
        TotalEncounters += Encounters;
        Csv += FString::Printf(TEXT("%d,%d,%d,%d,%d,%d,%d,%d,%llu\n"), Seed, Match.Round(), Match.ElapsedMs(),
                               Encounters, Timeouts, Ghosts, static_cast<int>(Match.BotLog().size()), Rejects,
                               Match.Records().back().postHash);
    }
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence");
    IFileManager::Get().MakeDirectory(*Directory, true);
    TestTrue(TEXT("Write actual combat tournament CSV"),
             FFileHelper::SaveStringToFile(Csv, *(Directory / TEXT("engine-tournaments.csv"))));
    TestTrue(TEXT("Write per-round gold/health/settlement evidence"),
             FFileHelper::SaveStringToFile(RoundCsv, *(Directory / TEXT("engine-rounds.csv"))));
    FFileHelper::SaveStringToFile(UTF8_TO_TCHAR(Catalog.contentDigest.c_str()),
                                  *(Directory / TEXT("catalog-digest.txt")));
    AddInfo(FString::Printf(TEXT("Executed 100 actual combat tournaments, %lld encounters; %s"),
                            TotalEncounters, *Directory));
    return true;
}
#endif
