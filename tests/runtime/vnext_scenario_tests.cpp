#include "Simulation/WonderScenario.h"
#include "Simulation/WonderScenarioFile.h"
#include "WonderVNextCatalog.h"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <Windows.h>
#endif

namespace
{
int assertions = 0;
void Check(bool condition, const std::string &message)
{
    ++assertions;
    if (!condition) throw std::runtime_error(message);
}
wc::Id Hash(const std::string &bytes)
{
    wc::Id value = 14695981039346656037ULL;
    for (unsigned char c : bytes) { value ^= c; value *= 1099511628211ULL; }
    return value;
}
void SetNumber(std::string &bytes, std::size_t at, wc::Id value)
{
    for (int i = 0; i < 8; ++i) bytes.at(at + i) = char((value >> (i * 8)) & 255);
}
wc::Id Number(const std::string &bytes, std::size_t &at)
{
    wc::Id value = 0;
    for (int i = 0; i < 8; ++i) value |= wc::Id(static_cast<unsigned char>(bytes.at(at++))) << (i * 8);
    return value;
}
void SkipText(const std::string &bytes, std::size_t &at) { const auto size = Number(bytes, at); at += std::size_t(size); }
void Rehash(std::string &bytes) { SetNumber(bytes, bytes.size() - 8, Hash(bytes.substr(0, bytes.size() - 8))); }

void Acquisition(const wc::Catalog &catalog)
{
    std::ofstream results("counter-acquisition.csv"), commands("counter-acquisition-commands.csv"), inputs("counter-acquisition-inputs.csv");
    results << "plan,shop_seed,preparation_round,level,total_spend_limit,initial_gold,spent,purchase_gold,reroll_gold,rerolls,acquired,combat_seed,winner,ticks,timeout,combat_signature\n";
    commands << "plan,shop_seed,total_spend_limit,sequence,command,slot,hero,gold_before,gold_after,accepted\n";
    inputs << "plan,shop_seed,total_spend_limit,side,order,id,hero,star,column,row,facing\n";
    for (const auto& plan : wc::BuiltinEarlyResponseScenarios(catalog))
    {
        if (plan.level != catalog.rules.startingLevel) continue;
        for (int budget : {plan.investmentBudget, catalog.rules.startingGold}) for (int seed = 61001; seed <= 61100; ++seed)
        {
            wc::Match match(catalog, seed, 1);
            const auto opponentShop = match.Seats()[1].shop;
            const auto opponentRng = match.Seats()[1].shopRng.state;
            const int startingGold = match.Seats()[0].gold;
            std::map<int, int> missing;
            for (const auto& unit : plan.scenario.armies[0]) missing[unit.definition] += unit.star == 3 ? 9 : unit.star == 2 ? 3 : 1;
            int purchaseGold = 0, rerollGold = 0, rerolls = 0;
            auto submit = [&](wc::Command command) {
                const auto& seat = match.Seats()[0];
                const int before = seat.gold;
                const std::string hero = command.type == wc::CommandType::Buy ? catalog.units[seat.shop[command.slot]].id : "none";
                command.seat = 0; command.sequence = seat.sequence + 1; command.requestId = command.sequence; command.revision = seat.revision;
                const auto reply = match.Submit(0, command);
                commands << plan.id << ',' << seed << ',' << budget << ',' << command.sequence << ',' << int(command.type)
                    << ',' << command.slot << ',' << hero << ',' << before << ',' << match.Seats()[0].gold << ',' << reply.accepted << '\n';
                Check(reply.accepted, "Visible-shop acquisition command accepted through authority");
                return before - match.Seats()[0].gold;
            };
            for (int action = 0; action < 20; ++action)
            {
                const auto& seat = match.Seats()[0];
                int minimumPurchases = 0;
                for (const auto& entry : missing) minimumPurchases += entry.second * catalog.units[entry.first].cost;
                if (minimumPurchases == 0) break;
                const int remaining = budget - (startingGold - seat.gold);
                int slot = -1;
                for (int i = 0; i < int(seat.shop.size()); ++i)
                    if (seat.shop[i] >= 0 && missing[seat.shop[i]] > 0 && catalog.units[seat.shop[i]].cost <= remaining)
                    { slot = i; break; }
                wc::Command command;
                if (slot >= 0)
                {
                    const int definition = seat.shop[slot];
                    command.type = wc::CommandType::Buy; command.slot = slot;
                    purchaseGold += submit(command); --missing[definition];
                }
                else if (remaining >= catalog.rules.rerollCost + minimumPurchases)
                { command.type = wc::CommandType::Reroll; rerollGold += submit(command); ++rerolls; }
                else break;
            }
            const bool acquired = std::all_of(missing.begin(), missing.end(), [](const auto& entry) { return entry.second == 0; });
            const auto& seat = match.Seats()[0];
            Check(startingGold - seat.gold == purchaseGold + rerollGold && purchaseGold + rerollGold <= budget,
                "Purchase and reroll spending reconcile with real starting gold");
            Check(seat.level == plan.level && seat.xp == 0 && match.Round() == 1 && match.ElapsedMs() == 0,
                "Opening acquisition uses no granted XP, income, elapsed time or hidden shop samples");
            Check(match.Seats()[1].shop == opponentShop && match.Seats()[1].shopRng.state == opponentRng,
                "Recruitment policy cannot consume another captain's shop");
            wc::ScenarioRun run;
            if (acquired)
            {
                auto scenario = plan.scenario; scenario.armies[0].clear();
                std::set<wc::Id> used;
                for (const auto& required : plan.scenario.armies[0])
                {
                    const auto found = std::find_if(seat.roster.begin(), seat.roster.end(), [&](const auto& unit) {
                        return unit.definition == required.definition && unit.star == required.star && !used.count(unit.id);
                    });
                    Check(found != seat.roster.end(), "Normal purchases and automatic merges produce the exact requested stars");
                    const auto id = found->id; used.insert(id);
                    wc::Command move; move.type = wc::CommandType::Move; move.unit = id; move.toBoard = true; move.cell = required.cell;
                    submit(move);
                }
                for (const auto& unit : match.Seats()[0].roster) if (unit.onBoard) scenario.armies[0].push_back(unit);
                Check(wc::ScenarioInvestment(catalog, scenario.armies[0]) == purchaseGold, "Deployed army contains exactly the purchased copies");
                for (int side = 0; side < 2; ++side) for (int i = 0; i < int(scenario.armies[side].size()); ++i)
                {
                    const auto& unit = scenario.armies[side][i];
                    inputs << plan.id << ',' << seed << ',' << budget << ',' << side << ',' << i << ',' << unit.id << ','
                        << catalog.units[unit.definition].id << ',' << unit.star << ',' << unit.cell.column << ',' << unit.cell.row << ',' << int(unit.facing) << '\n';
                }
                run = wc::RunScenario(catalog, scenario);
            }
            results << plan.id << ',' << seed << ",1," << plan.level << ',' << budget << ',' << startingGold << ','
                << purchaseGold + rerollGold << ',' << purchaseGold << ',' << rerollGold << ',' << rerolls << ',' << acquired
                << ',' << plan.scenario.seed << ',' << (acquired ? run.result.winner : -2) << ',' << run.result.ticks << ',' << run.result.timeout << ',' << run.signature << '\n';
        }
    }
}

void WidthSensitivity(const wc::Catalog& catalog)
{
    const auto plans = wc::BuiltinEarlyResponseScenarios(catalog);
    const auto found = std::find_if(plans.begin(), plans.end(), [](const auto& plan) { return plan.id == "F07-L3-width"; });
    Check(found != plans.end(), "Width response exists for the bounded ordering/approach experiment");
    std::ofstream out("width-sensitivity.csv");
    out << "order,front_crag,mirrored,combat_seed,response_won,winner,ticks,timeout,response_charge_hits,response_health_damage,response_healing\n";
    const std::array<std::array<int, 3>, 3> orders{{{0,1,2},{0,2,1},{2,0,1}}};
    for (int order = 0; order < int(orders.size()); ++order) for (int front = 0; front < 2; ++front)
        for (int mirrored = 0; mirrored < 2; ++mirrored) for (int seed = 61401; seed <= 61432; ++seed)
    {
        auto scenario = found->scenario;
        if (front) scenario.armies[0][0].cell.row = 3;
        const auto army = scenario.armies[0];
        for (int i = 0; i < 3; ++i) scenario.armies[0][i] = army[orders[order][i]];
        if (mirrored) scenario.armies[0].swap(scenario.armies[1]);
        scenario.seed = seed;
        const auto result = wc::RunScenario(catalog, scenario);
        const auto& own = result.sides[mirrored];
        Check(result.result.complete && own.investment == 3, "Ordering/approach experiment preserves the three-gold response army");
        out << order << ',' << front << ',' << mirrored << ',' << seed << ',' << (result.result.winner == mirrored) << ','
            << result.result.winner << ',' << result.result.ticks << ',' << result.result.timeout << ',' << own.chargeHits
            << ',' << own.healthLoss << ',' << own.healing << '\n';
    }
}

void Persistence(const wc::Catalog &catalog, const wc::FormationScenario &source)
{
    std::string error;
    auto baseline = source;
    baseline.name = "Saved formation: guard A/B";
    baseline.armies[0][1].star = 3;
    for (int i = 0; i < int(catalog.relics.size()); ++i)
        if (wc::RelicCompatible(catalog.relics[i], catalog.units[baseline.armies[0][1].definition].ability.mechanic))
        { baseline.armies[0][1].relic = i; break; }
    const auto saved = wc::SaveScenario(catalog, baseline, error);
    Check(!saved.empty() && error.empty(), "Valid starred and equipped scenario serializes");
    Check(saved.find(catalog.units[baseline.armies[0][1].definition].id) != std::string::npos &&
        saved.find(catalog.relics[baseline.armies[0][1].relic].id) != std::string::npos,
        "Wire format persists canonical hero and relic identifiers");
    auto restored = source;
    Check(wc::LoadScenario(catalog, saved, restored, error), "Valid scenario loads: " + error);
    Check(wc::SaveScenario(catalog, restored, error) == saved, "Scenario fields round trip exactly");
    Check(wc::RunScenario(catalog, baseline).signature == wc::RunScenario(catalog, restored).signature,
        "Scenario round trip replays every event and result identically");
    auto reordered = catalog;
    std::reverse(reordered.units.begin(), reordered.units.end());
    std::reverse(reordered.relics.begin(), reordered.relics.end());
    auto stable = source;
    Check(wc::LoadScenario(reordered, saved, stable, error), "Stable identifiers resolve after adapter order changes: " + error);
    Check(reordered.units[stable.armies[0][1].definition].id == catalog.units[baseline.armies[0][1].definition].id &&
        reordered.relics[stable.armies[0][1].relic].id == catalog.relics[baseline.armies[0][1].relic].id,
        "Loading never treats an old array offset as a hero or relic identity");
    auto reject = [&](const std::string &bytes, const std::string &message) {
        const auto before = wc::SaveScenario(catalog, restored, error);
        Check(!wc::LoadScenario(catalog, bytes, restored, error) && !error.empty(), message);
        Check(wc::SaveScenario(catalog, restored, error) == before, "Rejected load preserves the prior valid scenario");
    };
    for (std::size_t size = 0; size < saved.size(); ++size) reject(saved.substr(0, size), "Every truncated prefix is rejected");
    for (std::size_t at = 0; at < saved.size(); ++at)
    {
        auto corrupt = saved; corrupt[at] ^= 1;
        reject(corrupt, "Single-byte corruption is rejected");
    }
    reject(std::string(64 * 1024 + 1, 'x'), "Oversized scenario rejected before parsing");
    auto corrupt = saved; corrupt[8] = 'X'; Rehash(corrupt);
    reject(corrupt, "Unsupported version with a valid checksum is rejected");
    corrupt = saved; SetNumber(corrupt, 0, std::numeric_limits<wc::Id>::max()); Rehash(corrupt);
    reject(corrupt, "Oversized string length with valid checksum is rejected");
    std::size_t countOffset = 0;
    for (int i = 0; i < 8; ++i) SkipText(saved, countOffset);
    countOffset += 8;
    corrupt = saved; SetNumber(corrupt, countOffset, 11); Rehash(corrupt);
    reject(corrupt, "More than ten units is rejected with a valid checksum");
    corrupt = saved; SetNumber(corrupt, countOffset, 0); Rehash(corrupt);
    reject(corrupt, "Empty side rejected with a valid checksum");
    const std::size_t unitOffset = countOffset + 8;
    corrupt = saved; SetNumber(corrupt, unitOffset, wc::Id(1) << 20); Rehash(corrupt);
    reject(corrupt, "Out-of-range combat identity rejected");
    corrupt = saved; SetNumber(corrupt, unitOffset, 0); Rehash(corrupt);
    reject(corrupt, "Zero combat identity rejected");
    const auto heroAt = saved.find(catalog.units[baseline.armies[0][0].definition].id);
    corrupt = saved; corrupt[heroAt] = 'x'; Rehash(corrupt);
    reject(corrupt, "Unknown stable hero ID rejected");
    std::size_t starAt = unitOffset + 8; SkipText(saved, starAt);
    corrupt = saved; SetNumber(corrupt, starAt, 4); Rehash(corrupt);
    reject(corrupt, "Unsupported star rejected");
    std::size_t cellAt = starAt + 8; SkipText(saved, cellAt);
    corrupt = saved; SetNumber(corrupt, cellAt, 8); Rehash(corrupt);
    reject(corrupt, "Out-of-board column rejected");
    corrupt = saved; SetNumber(corrupt, cellAt + 8, 4); Rehash(corrupt);
    reject(corrupt, "Opponent-half deployment rejected");
    corrupt = saved; SetNumber(corrupt, cellAt + 16, 4); Rehash(corrupt);
    reject(corrupt, "Unknown facing rejected");
    corrupt = saved; corrupt.insert(corrupt.size() - 8, "unused"); Rehash(corrupt);
    reject(corrupt, "Trailing payload rejected even with valid checksum");
    auto wrongCatalog = catalog; wrongCatalog.contentDigest += "-different";
    const auto unchanged = wc::SaveScenario(catalog, restored, error);
    Check(!wc::LoadScenario(wrongCatalog, saved, restored, error), "Content identity mismatch rejected");
    Check(wc::SaveScenario(catalog, restored, error) == unchanged, "Identity rejection is transactional");
    wrongCatalog = catalog; wrongCatalog.balanceVersion += "-candidate";
    Check(!wc::LoadScenario(wrongCatalog, saved, restored, error), "Balance identity mismatch rejected");
    wrongCatalog = catalog; wrongCatalog.schemaVersion += "-future";
    Check(!wc::LoadScenario(wrongCatalog, saved, restored, error), "Catalog schema mismatch rejected");
    wrongCatalog = catalog; wrongCatalog.profileId = "alpha_24";
    Check(!wc::LoadScenario(wrongCatalog, saved, restored, error), "Legacy profile rejected");

    auto invalid = baseline;
    auto invalidSave = [&](const std::string &reason) {
        Check(wc::SaveScenario(catalog, invalid, error).empty() && !error.empty(), reason);
        invalid = baseline;
    };
    invalid.armies[0][1].cell = invalid.armies[0][0].cell; invalidSave("Occupied cells rejected on save");
    invalid.armies[0][1].id = invalid.armies[0][0].id; invalidSave("Duplicate IDs rejected on save");
    invalid.armies[1][0].id = invalid.armies[0][0].id; invalidSave("Cross-side duplicate IDs cannot confuse UI selection");
    invalid.armies[0][0].neutral = true; invalidSave("Neutral stat scales cannot enter formation fixtures");
    invalid.armies[0][0].hpScaleBp++; invalidSave("Hidden health scales rejected");
    invalid.armies[0][0].damageScaleBp++; invalidSave("Hidden damage scales rejected");
    invalid.armies[0][0].bench = 0; invalidSave("Bench identity rejected for deployed scenario");
    invalid.armies[0][0].onBoard = false; invalidSave("Hidden nondeployed units rejected");
    invalid.armies[0][0].definition = int(catalog.units.size()); invalidSave("Bad definition rejected before serialization");
    invalid.name = std::string(513, 'a'); invalidSave("Unbounded scenario text rejected");
    invalid.name = "hidden\nrow"; invalidSave("Control characters in labels rejected");
    invalid.armies[0][0].relic = baseline.armies[0][1].relic;
    invalidSave("Incompatible or duplicated relic rejected");
    invalid.armies[0].clear(); invalidSave("Empty side rejected on save");
    for (int i = 0; i < 9; ++i) invalid.armies[0].push_back(baseline.armies[0][0]);
    invalidSave("Oversized army rejected on save");
}

void PairContract(const wc::Catalog &catalog, const std::vector<wc::ScenarioPair> &pairs)
{
    std::string error;
    Check(pairs.size() == 7, "Seven core-mechanic causal pairs exist");
    std::set<wc::AbilityMechanic> mechanics;
    for (const auto &pair : pairs)
    {
        Check(wc::ValidateScenarioPair(catalog, pair, error), pair.id + " causal contract: " + error);
        Check(wc::ValidateScenarioPair(catalog, wc::MirrorScenarioPair(pair), error), pair.id + " mirror contract: " + error);
        mechanics.insert(pair.mechanic);
        for (int side = 0; side < 2; ++side)
            Check(wc::ScenarioInvestment(catalog, pair.a.armies[side]) == wc::ScenarioInvestment(catalog, pair.b.armies[side]),
                "Causal comparison fixes purchase investment including star copies");
    }
    Check(mechanics.size() == 7, "Every active mechanic has its own pair");
    auto bad = pairs[0]; bad.b.seed++;
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Changed causal seed rejected");
    bad = pairs[0]; bad.b.armies[0][1].star++;
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Changed causal star rejected");
    bad = pairs[0]; bad.b.armies[0][1].definition = 1;
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Changed causal recruit rejected");
    bad = pairs[0]; bad.b.armies[0][1].cell = {0,0};
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Undeclared cell movement rejected");
    bad = pairs[0]; bad.changes[0].facing = false; bad.changes[0].position = true;
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Declared variable mismatch rejected");
    bad = pairs[0]; bad.changes.push_back(bad.changes.front());
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Duplicate variable declaration rejected");
    bad = pairs[0]; bad.changes[0].unit = 999;
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Missing changed unit rejected");
    bad = pairs[0]; std::swap(bad.b.armies[0][0], bad.b.armies[0][1]);
    Check(!wc::ValidateScenarioPair(catalog, bad, error), "Combat initiative input order cannot change silently");
}

void DurableFiles(const wc::Catalog &catalog, const wc::ScenarioPair &pair, const std::filesystem::path &root)
{
    namespace fs = std::filesystem;
    auto suffix = [](fs::path path, const char *value) { path += value; return path; };
    auto write = [](const fs::path &path, const std::string &bytes) {
        fs::create_directories(path.parent_path());
        std::ofstream file(path, std::ios::binary); file.write(bytes.data(), std::streamsize(bytes.size()));
        Check(bool(file), "Disk failure fixture written");
    };
    auto read = [](const fs::path &path) {
        std::ifstream file(path, std::ios::binary);
        Check(bool(file), "Scenario disk fixture readable");
        return std::string(std::istreambuf_iterator<char>(file), {});
    };
    std::string error;
    const auto a = wc::SaveScenario(catalog, pair.a, error), b = wc::SaveScenario(catalog, pair.b, error);
    const auto slot = root / fs::path(L"unicode-\u732b") / "formation.wcf";
    auto result = wc::SaveScenarioFile(catalog, pair.a, slot);
    Check(result.succeeded && !result.recoveredPrevious && read(slot) == a, "Initial durable Unicode-path save");
    Check(!fs::exists(suffix(slot, ".previous")) && !fs::exists(suffix(slot, ".pending")), "Initial save is committed without invented previous save");
    Check(wc::SaveScenarioFile(catalog, pair.b, slot).succeeded && read(slot) == b && read(suffix(slot, ".previous")) == a,
        "Atomic replacement retains exact previous scenario");
    auto restored = pair.a;
    result = wc::LoadScenarioFile(catalog, slot, restored);
    Check(result.succeeded && !result.recoveredPrevious && wc::SaveScenario(catalog, restored, error) == b,
        "Latest committed formation loads");
    Check(wc::RunScenario(catalog, restored).signature == wc::RunScenario(catalog, pair.b).signature,
        "Durable scenario preserves every later combat event");
    const auto interrupted = root / "interrupted" / "formation.wcf";
    write(interrupted, a);
    for(const auto &bytes : {std::string{}, b.substr(0,b.size()/2), b}) {
        write(suffix(interrupted, ".pending"), bytes);
        write(suffix(interrupted, ".previous.pending"), a.substr(0,a.size()/2));
        result = wc::LoadScenarioFile(catalog, interrupted, restored);
        Check(result.succeeded && wc::SaveScenario(catalog, restored, error) == a,
            "Before/during/after staging interruption loads only committed primary");
    }
    Check(wc::SaveScenarioFile(catalog, pair.b, interrupted).succeeded && read(interrupted) == b,
        "Abandoned staging can be replaced by a complete new write");
    const auto pendingOnly = root / "pending-only" / "formation.wcf";
    write(suffix(pendingOnly, ".pending"), a);
    const auto before = wc::SaveScenario(catalog, restored, error);
    Check(!wc::LoadScenarioFile(catalog, pendingOnly, restored).succeeded && wc::SaveScenario(catalog, restored, error) == before,
        "Uncommitted-only scenario never replaces current formation");
    const auto corrupt = root / "corrupt" / "formation.wcf";
    write(corrupt, "corrupt primary"); write(suffix(corrupt, ".previous"), a);
    result = wc::LoadScenarioFile(catalog, corrupt, restored);
    Check(result.succeeded && result.recoveredPrevious && wc::SaveScenario(catalog, restored, error) == a,
        "Corrupt primary recovers previous with explicit status");
    Check(!wc::SaveScenarioFile(catalog, pair.b, corrupt).succeeded && read(corrupt) == "corrupt primary",
        "New save preserves corrupt primary for diagnosis");
    write(suffix(corrupt, ".previous"), "broken backup");
    Check(!wc::LoadScenarioFile(catalog, corrupt, restored).succeeded && wc::SaveScenario(catalog, restored, error) == a,
        "Both corrupt files leave current formation intact");
    const auto missing = root / "missing-primary" / "formation.wcf";
    write(suffix(missing, ".previous"), b);
    result = wc::LoadScenarioFile(catalog, missing, restored);
    Check(result.succeeded && result.recoveredPrevious, "Missing primary recovers a committed previous scenario");
    auto incompatible = catalog; incompatible.contentDigest += "-different";
    const auto last = wc::SaveScenario(catalog, restored, error);
    Check(!wc::LoadScenarioFile(incompatible, missing, restored).succeeded && wc::SaveScenario(catalog, restored, error) == last,
        "Incompatible catalog does not change current formation");
    const auto oversized = root / "oversized" / "formation.wcf";
    write(oversized, std::string(64*1024+1, 'a'));
    Check(!wc::LoadScenarioFile(catalog, oversized, restored).succeeded && wc::SaveScenario(catalog, restored, error) == last,
        "Oversized on-disk scenario is bounded before parsing");
    const auto blocked = root / "staging-directory" / "formation.wcf";
    write(blocked, a); fs::create_directory(suffix(blocked, ".pending"));
    Check(!wc::SaveScenarioFile(catalog, pair.b, blocked).succeeded && read(blocked) == a,
        "Staging I/O failure preserves primary");
    const auto backupBlocked = root / "backup-directory" / "formation.wcf";
    write(backupBlocked, a); fs::create_directory(suffix(backupBlocked, ".previous"));
    Check(!wc::SaveScenarioFile(catalog, pair.b, backupBlocked).succeeded && read(backupBlocked) == a,
        "Backup publication failure preserves primary");
    const auto parentFile = root / "parent-is-file";
    write(parentFile, "preserve");
    Check(!wc::SaveScenarioFile(catalog, pair.b, parentFile / "formation.wcf").succeeded && read(parentFile) == "preserve",
        "Directory creation failure preserves unrelated file");
    Check(!wc::SaveScenarioFile(catalog, pair.b, {}).succeeded, "Empty save path rejected");
    auto invalid = pair.b; invalid.armies[0][0].star=4;
    Check(!wc::SaveScenarioFile(catalog, invalid, slot).succeeded && read(slot) == b,
        "Invalid in-memory formation cannot replace a valid slot");
#if defined(_WIN32)
    const auto lockPath = suffix(slot, ".lock");
    HANDLE lock = CreateFileW(lockPath.c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_ALWAYS,FILE_FLAG_DELETE_ON_CLOSE,nullptr);
    Check(lock != INVALID_HANDLE_VALUE, "Concurrency fixture acquires exclusive slot");
    result = wc::SaveScenarioFile(catalog,pair.a,slot); CloseHandle(lock);
    Check(!result.succeeded && read(slot) == b, "Competing application cannot publish same slot");
#endif
}

void Row(std::ostream &out, const wc::FormationScenario &scenario, const wc::ScenarioRun &run,
    int level = 0, int budget = 0, int maximumCost = 0)
{
    out << scenario.id << '\t' << scenario.seed << '\t' << level << '\t' << budget << '\t' << maximumCost
        << '\t' << run.signature << '\t' << run.result.winner << '\t' << run.result.timeout
        << '\t' << run.result.ticks << '\t' << run.firstMeaningfulTick << '\t' << run.firstDeathTick;
    for (int side = 0; side < 2; ++side)
    {
        const auto &m = run.sides[side];
        out << '\t' << m.investment << '\t' << m.survivorInvestment << '\t' << run.result.survivors[side]
            << '\t' << m.healthLoss << '\t' << m.healing << '\t' << m.deliveredOverheal
            << '\t' << m.guardPrevented << '\t' << m.guardedHits << '\t' << m.chargeHits << '\t' << m.chargeLandings
            << '\t' << m.grovePulses << '\t' << m.strikeHits << '\t' << m.beamHits << '\t' << m.tideHits << '\t' << m.tidePushes;
    }
    out << '\n';
}
wc::Int MechanicObserved(const wc::ScenarioRun &run, wc::AbilityMechanic mechanic)
{
    // This scenario asks which approaching enemy is caught, not how many casts occur.
    if(mechanic==wc::AbilityMechanic::CocoonProjectile){
        for(const auto& event:run.events)if(event.mechanic==mechanic&&event.effect==wc::Effect::Stun&&event.resolved>0)
            return event.target;
        return 0;
    }
    wc::Int count = 0;
    for (const auto &side : run.sides)
    {
        if (mechanic == wc::AbilityMechanic::DirectionalGuard) count += side.guardPrevented;
        if (mechanic == wc::AbilityMechanic::MomentumCharge) count += side.chargeLandings;
        if (mechanic == wc::AbilityMechanic::StationaryGrove) count += side.healing;
        if (mechanic == wc::AbilityMechanic::ScreenedStrike) count += side.strikeHits;
        if (mechanic == wc::AbilityMechanic::CrossingBeams) count += side.beamHits;
        if (mechanic == wc::AbilityMechanic::TidalPush) count += side.tidePushes;
        if (mechanic == wc::AbilityMechanic::CocoonProjectile) count += side.cocoons;
    }
    return count;
}
void ExportFixture(const wc::Catalog &catalog, const wc::FormationScenario &scenario,
    const wc::ScenarioRun &run, const std::filesystem::path &directory, std::ostream *events)
{
    if (directory.empty()) return;
    std::filesystem::create_directories(directory);
    const auto path = directory / (scenario.id + ".wcf");
    std::string error;
    const auto bytes = wc::SaveScenario(catalog, scenario, error);
    Check(!bytes.empty(), "Executed scenario serializes for file export");
    {
        std::ofstream output(path, std::ios::binary);
        output.write(bytes.data(), std::streamsize(bytes.size())); output.close();
        Check(bool(output), "Scenario fixture bytes written successfully");
    }
    std::ifstream input(path, std::ios::binary);
    const std::string read((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
    Check(read == bytes, "On-disk scenario fixture matches serialized bytes");
    auto restored = scenario;
    Check(wc::LoadScenario(catalog, read, restored, error) && wc::RunScenario(catalog, restored).signature == run.signature,
        "On-disk saved scenario replays the exact executed encounter");
    if (!events) return;
    auto hero = [&](wc::Id id) -> std::string {
        const int side = int((id >> 20) & 1);
        for (const auto &unit : scenario.armies[side])
            if (unit.id == (id & ((wc::Id(1) << 20) - 1))) return catalog.units[unit.definition].id;
        throw std::runtime_error("Event references unknown scenario identity");
    };
    int index = 0;
    for (const auto &event : run.events)
        *events << scenario.id << '\t' << index++ << '\t' << event.tick << '\t' << event.source << '\t' << hero(event.source)
            << '\t' << event.target << '\t' << hero(event.target) << '\t' << event.action << '\t' << int(event.effect)
            << '\t' << int(event.mechanic) << '\t' << event.basicAttack << '\t' << event.origin.column << '\t' << event.origin.row
            << '\t' << event.cell.column << '\t' << event.cell.row << '\t' << event.requested << '\t' << event.resolved
            << '\t' << event.absorbed << '\t' << event.healthLoss << '\t' << event.overkill << '\t' << event.prevented
            << '\t' << event.guardedBy << '\n';
}
void Battles(const wc::Catalog &catalog, const std::vector<wc::ScenarioPair> &pairs, std::ostream &out,
    const std::filesystem::path &directory, std::ostream *events)
{
    out << "id\tseed\tlevel\tbudget\tmaximum_cost\tsignature\twinner\ttimeout\tticks\tfirst_action\tfirst_death";
    for (const char *side : {"a", "b"})
        for (const char *column : {"investment","survivor_investment","survivors","health_loss","healing","delivered_overheal",
            "guard_prevented","guarded_hits","charge_hits","charge_landings","grove_recipient_pulses","strike_hits","beam_hits","tide_hits","tide_pushes"})
            out << '\t' << side << '_' << column;
    out << '\n';
    for (const auto &pair : pairs)
    {
        wc::Int observed[2]{};
        for (int mirrored = 0; mirrored < 2; ++mirrored)
        {
            const auto variant = mirrored ? wc::MirrorScenarioPair(pair) : pair;
            const wc::FormationScenario *scenarios[2]{&variant.a, &variant.b};
            wc::Id signature = 0;
            for (int version = 0; version < 2; ++version)
            {
                const auto &scenario = *scenarios[version];
                const auto run = wc::RunScenario(catalog, scenario), repeat = wc::RunScenario(catalog, scenario);
                Check(run.result.complete && repeat.signature == run.signature, scenario.id + " deterministic native execution");
                Check(run.firstMeaningfulTick > 0 && run.firstDeathTick > 0, scenario.id + " has observable action and defeat");
                Check(run.findings.size() == 2, "Recap contains actual result and event totals");
                if (!mirrored) observed[version] = MechanicObserved(run, pair.mechanic);
                if (version == 0) signature = run.signature;
                else Check(signature != run.signature, "Formation change produces a different real event trace");
                Row(out, scenario, run);
                ExportFixture(catalog, scenario, run, directory, events);
            }
        }
        Check(observed[0] > 0 || observed[1] > 0, pair.id + " actually executes its mechanic");
        Check(observed[0] != observed[1], pair.id + " formation changes its mechanic's observed signal");
        std::cout << pair.id << " mechanic observation A/B: " << observed[0] << '/' << observed[1] << '\n';
    }
    const auto early = wc::BuiltinEarlyResponseScenarios(catalog);
    Check(early.size() == 5, "Early response covers two cost-1 forms and levels 4 through 6");
    std::string error;
    for (const auto &test : early)
    {
        Check(wc::ValidateEarlyResponse(catalog, test, error), test.id + " acquisition budget: " + error);
        const auto run = wc::RunScenario(catalog, test.scenario);
        Check(wc::RunScenario(catalog, test.scenario).signature == run.signature, "Early response exact repeat");
        Row(out, test.scenario, run, test.level, test.investmentBudget, test.maximumRecruitCost);
        ExportFixture(catalog, test.scenario, run, directory, events);
        std::cout << test.id << ": " << run.findings[0] << '\n';
    }
    auto bad = early[0]; bad.investmentBudget = 3;
    Check(!wc::ValidateEarlyResponse(catalog, bad, error), "Star copy investment enforces budget");
    bad = early[2]; bad.level = 3;
    Check(!wc::ValidateEarlyResponse(catalog, bad, error), "Zero shop-weight Snapvine access fails closed at level 3");
    bad = early[3]; bad.level = 4;
    Check(!wc::ValidateEarlyResponse(catalog, bad, error), "Zero shop-weight Prism access fails closed at level 4");
    bad = early[0]; bad.scenario.armies[0][0].definition = 5;
    Check(!wc::ValidateEarlyResponse(catalog, bad, error), "Free Reefglass cannot conceal early counter access");
}
} // namespace
int main(int argc, char **argv)
{
    try
    {
        const auto catalog = wcvnext::WonderVNextCatalog();
        const auto pairs = wc::BuiltinScenarioPairs(catalog);
        PairContract(catalog, pairs); Persistence(catalog, pairs[0].a);
        std::ofstream file, events;
        std::filesystem::path directory;
        if (argc > 1)
        {
            file.open(argv[1]); Check(bool(file), "Scenario evidence output opens");
            directory = std::filesystem::path(argv[1]).parent_path() / "fixtures";
            const auto diskRoot = directory.parent_path() / ("disk-test-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
            DurableFiles(catalog, pairs[0], diskRoot);
            events.open(directory.parent_path() / "scenario-events.tsv");
            Check(bool(events), "Scenario event evidence output opens");
            events << "scenario\tevent\ttick\tsource\tsource_hero\ttarget\ttarget_hero\taction\teffect\tmechanic\tbasic\torigin_x\torigin_y\tcell_x\tcell_y\trequested\tresolved\tabsorbed\thealth_loss\toverkill\tprevented\tguarded_by\n";
        }
        Battles(catalog, pairs, argc > 1 ? file : std::cout, directory, argc > 1 ? &events : nullptr);
        Acquisition(catalog);
        WidthSensitivity(catalog);
        std::cout << "PASS vNext scenario persistence and causal native fixtures: " << assertions
            << " assertions. Native synthetic evidence only; no external-player, balance, art or release acceptance.\n";
        return 0;
    }
    catch (const std::exception &exception)
    {
        std::cerr << "FAIL after " << assertions << " assertions: " << exception.what() << '\n';
        return 1;
    }
}
