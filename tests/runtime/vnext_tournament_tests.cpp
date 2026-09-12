#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include "vnext_bot_tests.h"

namespace
{
int checks = 0;
wc::Id requests = 1000;
void Check(bool condition, const std::string &message)
{
    ++checks;
    if (!condition) throw std::runtime_error(message);
}
wc::Command Intent(const wc::Match &match, int seat, wc::CommandType type, int slot = -1, wc::Id unit = 0)
{
    wc::Command command;
    command.type = type; command.seat = seat; command.requestId = ++requests;
    command.sequence = match.Seats()[seat].sequence + 1; command.revision = match.Seats()[seat].revision;
    command.slot = slot; command.unit = unit;
    return command;
}
wc::Reply Send(wc::Match &match, int seat, wc::CommandType type, int slot = -1, wc::Id unit = 0)
{
    return match.Submit(seat, Intent(match, seat, type, slot, unit));
}
void AdvanceTo(wc::Match &match, int round)
{
    const int maxTicks = 200000;
    for (int tick = 0; tick < maxTicks; ++tick)
    {
        if (match.Round() == round && match.CurrentPhase() == wc::Phase::Preparation) return;
        if (match.CurrentPhase() == wc::Phase::Finished || match.CurrentPhase() == wc::Phase::Aborted) break;
        match.Tick(match.Definitions().rules.tickMs);
        Check(match.InvariantError().empty(), "advance preserves all tournament invariants");
    }
    throw std::runtime_error("Expected preparation round was not reached");
}
void Commands(const wc::Catalog &canonical)
{
    // Explicit economy fixture gives time/resources to exercise all levels and capacity transactions.
    auto catalog = canonical;
    catalog.rules.startingGold = 1000;
    wc::Match match(catalog, 129, 1);
    Check(match.CurrentPhase() == wc::Phase::Preparation, "successor match initializes");
    Check(match.Seats()[0].shop.size() == 5, "five independent offers");
    const auto opponentShop = match.Seats()[1].shop;
    const auto opponentRng = match.Seats()[1].shopRng.state;
    Check(Send(match, 0, wc::CommandType::Buy, 0).accepted, "buy through authority");
    const auto id = match.Seats()[0].roster[0].id;
    Check(match.Seats()[1].shop == opponentShop && match.Seats()[1].shopRng.state == opponentRng,
          "purchase cannot alter an opponent's independent shop");
    auto orient = Intent(match, 0, wc::CommandType::SetFacing, -1, id);
    orient.facing = wc::Facing::Left;
    Check(match.Submit(0, orient).accepted, "orientation accepted");
    const auto orientedRevision = match.Seats()[0].revision;
    Check(match.Submit(0, orient).accepted && match.Seats()[0].revision == orientedRevision, "orientation retransmit is idempotent");
    orient.facing = wc::Facing::Right;
    Check(!match.Submit(0, orient).accepted, "changed facing with same request rejected");
    auto invalid = Intent(match, 0, wc::CommandType::SetFacing, -1, id);
    invalid.facing = static_cast<wc::Facing>(4);
    Check(!match.Submit(0, invalid).accepted && match.Seats()[0].revision == orientedRevision,
          "invalid facing has no state changes");
    Check(!match.Submit(1, Intent(match, 0, wc::CommandType::SetFacing, -1, id)).accepted, "wrong seat cannot rotate unit");
    auto move = Intent(match, 0, wc::CommandType::Move, 9, id);
    Check(match.Submit(0, move).accepted && match.Seats()[0].roster[0].bench == 9, "tenth bench slot is legal");
    while (match.Seats()[0].level < catalog.rules.maximumLevel)
        Check(Send(match, 0, wc::CommandType::BuyXp).accepted, "level progression to ten");
    Check(match.Seats()[0].level == 10 && match.Seats()[0].xp == 0, "level ten cap normalized");
    Check(!Send(match, 0, wc::CommandType::BuyXp).accepted, "buy XP at cap rejects");
    std::set<int> costs;
    for (int n = 0; n < 50; ++n)
    {
        Check(Send(match, 0, wc::CommandType::Reroll).accepted, "reroll at level ten");
        for (int offer : match.Seats()[0].shop) costs.insert(catalog.units[offer].cost);
    }
    Check(costs.count(4) && costs.count(5), "fourth and fifth recruitment tiers are actually drawn");
    Check(match.Seats()[1].shop == opponentShop && match.Seats()[1].shopRng.state == opponentRng,
          "rerolls cannot consume another player's offers");
}
void Relics(const wc::Catalog &canonical)
{
    wc::Match match(canonical, 234, 1);
    Check(Send(match, 0, wc::CommandType::Buy, 0).accepted, "relic holder recruited normally");
    const auto holder = match.Seats()[0].roster[0];
    AdvanceTo(match, 4);
    Check(match.Seats()[0].health > 0 && match.Seats()[0].relicOffers.size() == 3,
          "opening neutral loss still awards three relic choices");
    Check(match.Seats()[0].pendingRelicDrafts == 1, "one draft per milestone");
    const auto before = match.SavePreparation();
    Check(!Send(match, 0, wc::CommandType::ChooseRelic, 3).accepted && match.SavePreparation() == before,
          "out-of-range draft choice is atomic");
    int choice = -1;
    for (int i = 0; i < int(match.Seats()[0].relicOffers.size()); ++i)
        if (wc::RelicCompatible(canonical.relics[match.Seats()[0].relicOffers[i]], canonical.units[holder.definition].ability.mechanic)) choice = i;
    if (choice < 0) choice = 0;
    const int relic = match.Seats()[0].relicOffers[choice];
    auto choose = Intent(match, 0, wc::CommandType::ChooseRelic, choice);
    Check(match.Submit(0, choose).accepted && match.Submit(0, choose).accepted, "draft selection and retransmit accepted exactly once");
    Check(match.Seats()[0].ownedRelics.size() == 1 && match.Seats()[0].relicOffers.empty() &&
          match.Seats()[0].pendingRelicDrafts == 0, "draft conserves one owned relic");
    Check(!Send(match, 0, wc::CommandType::ChooseRelic, 0).accepted, "cannot choose a second relic from an exhausted draft");
    if (wc::RelicCompatible(canonical.relics[relic], canonical.units[holder.definition].ability.mechanic))
    {
        Check(Send(match, 0, wc::CommandType::EquipRelic, relic, holder.id).accepted, "compatible owned relic equips");
        Check(match.Seats()[0].roster[0].relic == relic, "equipped relic exposed by owned state");
        Check(Send(match, 0, wc::CommandType::UnequipRelic, -1, holder.id).accepted, "relic unequips without consumption");
        Check(Send(match, 0, wc::CommandType::EquipRelic, relic, holder.id).accepted, "relic can be equipped again");
    }
    else Check(!Send(match, 0, wc::CommandType::EquipRelic, relic, holder.id).accepted, "incompatible relic rejected");
    Check(!Send(match, 0, wc::CommandType::EquipRelic, 100, holder.id).accepted, "unknown relic rejected");
    Check(Send(match, 0, wc::CommandType::Sell, -1, holder.id).accepted && match.Seats()[0].ownedRelics.size() == 1,
          "selling returns the relic to inventory");
    const auto relicsBefore = match.Seats()[0].ownedRelics;
    const auto relicRng = match.Seats()[0].relicRng.state;
    Check(Send(match, 0, wc::CommandType::Reroll).accepted && match.Seats()[0].relicRng.state == relicRng &&
          match.Seats()[0].ownedRelics == relicsBefore, "shop reroll does not reroll relics");
}
void Saves(const wc::Catalog &catalog)
{
    wc::Match original(catalog, 991, 0);
    AdvanceTo(original, 6);
    original.Tick(1750);
    Check(original.CurrentPhase() == wc::Phase::Preparation, "save fixture is in preparation");
    const std::string saved = original.SavePreparation();
    Check(!saved.empty(), "preparation checkpoint serialized");
    std::ofstream("preparation.wcsave", std::ios::binary).write(saved.data(), std::streamsize(saved.size()));
    wc::Match restored(catalog, 77, 0);
    std::string error;
    Check(restored.RestorePreparation(saved, error), "save restored: " + error);
    Check(restored.Namespace() != original.Namespace(), "restore receives a fresh transport namespace");
    Check(restored.SavePreparation() == saved, "logical save roundtrip exact including RNG and decisions");
    Check(!restored.Records().front().encounters.empty(), "save retains previous combat recaps");
    for (std::size_t round = 0; round < original.Records().size(); ++round)
    {
        const auto &a = original.Records()[round].encounters, &b = restored.Records()[round].encounters;
        Check(a.size() == b.size(), "all historical encounter recaps restored");
        for (std::size_t fight = 0; fight < a.size(); ++fight)
            Check(a[fight].healthLoss == b[fight].healthLoss && a[fight].absorbed == b[fight].absorbed &&
                  a[fight].healing == b[fight].healing && a[fight].sides[1].waveId == b[fight].sides[1].waveId,
                  "recap totals and neutral identity preserved");
    }
    // Mutate a real saved unit, then recompute the public checksum: semantic validation must still reject it.
    auto appendNumber = [](std::string &bytes, wc::Id value) {
        for (int i = 0; i < 8; ++i) bytes.push_back(char((value >> (8 * i)) & 255));
    };
    const auto publicSeats = original.PublicSeats();
    const wc::OwnedUnit *sample = nullptr;
    for (const auto &seat : publicSeats) if (!seat.deployment.empty()) { sample = &seat.deployment.front(); break; }
    Check(sample != nullptr, "deployed save validation fixture exists");
    std::string unitBytes;
    for (wc::Int field : {wc::Int(sample->id), wc::Int(sample->definition), wc::Int(sample->star), wc::Int(sample->onBoard),
        wc::Int(sample->cell.column), wc::Int(sample->cell.row), wc::Int(sample->bench), wc::Int(sample->neutral),
        wc::Int(sample->hpScaleBp), wc::Int(sample->damageScaleBp), wc::Int(sample->facing), wc::Int(sample->relic)})
        appendNumber(unitBytes, wc::Id(field));
    const auto firstUnit = saved.find(unitBytes), lastUnit = saved.rfind(unitBytes);
    Check(firstUnit != std::string::npos && lastUnit > firstUnit, "save contains both owner and cached public unit");
    auto withChecksum = [&](std::string bytes) {
        wc::Id hash = 14695981039346656037ULL;
        for (unsigned char byte : bytes) { hash ^= byte; hash *= 1099511628211ULL; }
        appendNumber(bytes, hash); return bytes;
    };
    auto tamper = [&](std::size_t offset, wc::Id value) {
        std::string bytes = saved.substr(0, saved.size() - 8), replacement;
        appendNumber(replacement, value); bytes.replace(offset, 8, replacement);
        return withChecksum(bytes);
    };
    Check(!restored.RestorePreparation(tamper(firstUnit, 0), error), "checksummed zero owner identity rejected");
    Check(!restored.RestorePreparation(tamper(firstUnit + 8 * 8, 1000000), error), "checksummed inflated ordinary hero stats rejected");
    Check(!restored.RestorePreparation(tamper(lastUnit + 8, 9999), error), "checksummed invalid cached public definition rejected");
    Check(!restored.RestorePreparation(tamper(firstUnit + 8 * 10, 4), error), "checksummed invalid owner facing rejected");
    std::size_t modeOffset = 0;
    for (int textField = 0; textField < 5; ++textField)
    {
        wc::Id length = 0;
        for (int byte = 0; byte < 8; ++byte)
            length |= wc::Id(static_cast<unsigned char>(saved.at(modeOffset + byte))) << (8 * byte);
        modeOffset += 8 + static_cast<std::size_t>(length);
    }
    Check(modeOffset < firstUnit, "save mode metadata follows the five version identity strings");
    Check(!restored.RestorePreparation(tamper(modeOffset, 2), error), "checksummed multiplayer origin rejected");
    Check(!restored.RestorePreparation(tamper(modeOffset + 8, 1), error), "checksummed hosted match origin rejected");
    Check(!restored.RestorePreparation(tamper(modeOffset, 1), error), "origin must agree with original-human and takeover flags");
    auto oldVersion = saved.substr(0, saved.size() - 8);
    const std::string oldMagic = "WCVNEXT-PREPARATION-2";
    oldVersion.replace(8, oldMagic.size(), oldMagic);
    Check(!restored.RestorePreparation(withChecksum(oldVersion), error), "v2 saves reject explicitly instead of loading without origin metadata");
    Check(restored.SavePreparation() == saved, "semantic save rejection leaves the running match intact");
    auto damaged = saved; damaged[damaged.size() / 2] ^= 1;
    Check(!restored.RestorePreparation(damaged, error) && restored.SavePreparation() == saved,
          "corrupt save rejects without altering running match");
    Check(!restored.RestorePreparation(saved.substr(0, saved.size() - 1), error), "truncated save rejected");
    auto changed = catalog; changed.contentDigest += "changed";
    wc::Match incompatible(changed, 1, 0);
    Check(!incompatible.RestorePreparation(saved, error), "different catalog save rejected");
    for (int tick = 0; tick < 200000 && original.CurrentPhase() != wc::Phase::Finished; ++tick)
    {
        original.Tick(catalog.rules.tickMs); restored.Tick(catalog.rules.tickMs);
        Check(original.CurrentPhase() == restored.CurrentPhase() && original.Round() == restored.Round(),
              "resume preserves phase progression");
        Check(restored.InvariantError().empty(), "resumed match invariants");
        if (original.CurrentPhase() == wc::Phase::Combat)
            Check(original.SavePreparation().empty(), "combat cannot be serialized as preparation");
    }
    Check(original.CurrentPhase() == wc::Phase::Finished && restored.CurrentPhase() == wc::Phase::Finished,
          "original and resumed tournaments finish");
    Check(original.Records().size() == restored.Records().size(), "resume retains round history");
    for (std::size_t i = 0; i < original.Records().size(); ++i)
        Check(original.Records()[i].postHash == restored.Records()[i].postHash, "same logical round hashes after resume");
    for (int seat = 0; seat < 8; ++seat)
        Check(original.Seats()[seat].health == restored.Seats()[seat].health &&
              original.Seats()[seat].placement == restored.Seats()[seat].placement,
              "same final health and placement after resume");
    wc::Match network(catalog, 1, 2);
    Check(network.SavePreparation().empty(), "network match cannot produce a solo save");
    network.TakeOver(1);
    Check(network.SavePreparation().empty(), "one remaining human does not convert network play into solo");
    network.TakeOver(0);
    Check(network.SavePreparation().empty() && network.InvariantError().empty(),
          "all bot takeovers retain original network authority");
    const auto networkNamespace = network.Namespace();
    Check(!network.RestorePreparation(saved, error) && network.Namespace() == networkNamespace &&
          network.Seed() == 1 && network.Round() == 1 && network.Seats()[0].takeover && network.Seats()[1].takeover,
          "offline restore into taken-over network target rejects atomically");
    wc::Match hosted(catalog, 47, 1, true);
    const auto hostedNamespace = hosted.Namespace();
    Check(hosted.SavePreparation().empty(), "explicit hosted one-human match cannot produce a solo save");
    Check(!hosted.RestorePreparation(saved, error) && hosted.Namespace() == hostedNamespace &&
          hosted.Seed() == 47 && hosted.Seats()[0].human && hosted.Round() == 1,
          "offline restore into hosted one-human target rejects atomically");
    wc::Match solo(catalog, 55, 1);
    solo.TakeOver(0);
    const auto takeoverSave = solo.SavePreparation();
    Check(!takeoverSave.empty() && solo.InvariantError().empty(), "ordinary solo remains saveable after bot takeover");
    wc::Match soloRestored(catalog, 56, 0);
    Check(soloRestored.RestorePreparation(takeoverSave, error) && soloRestored.Seats()[0].takeover &&
          soloRestored.SavePreparation() == takeoverSave, "solo takeover origin persists in exact save roundtrip");
    wc::Match zeroIdentity(catalog, 78, 1);
    Check(Send(zeroIdentity, 0, wc::CommandType::Buy, 0).accepted, "zero identity invariant fixture recruits through authority");
    // Deliberately corrupt an otherwise authoritative state to test the public invariant checker.
    const_cast<wc::OwnedUnit &>(zeroIdentity.Seats()[0].roster.front()).id = 0;
    Check(!zeroIdentity.InvariantError().empty() && zeroIdentity.SavePreparation().empty(),
          "zero ordinary identity fails invariants and cannot be serialized");
}
void Tournaments(const wc::Catalog &catalog, int count, int firstSeed = 1)
{
    std::ofstream rounds("tournaments.csv");
    std::ofstream combatRows("encounters.csv"), stateRows("rounds.csv");
    combatRows << "seed,round,index,a,b,kind,winner,ticks,timeout,survivors_a,survivors_b\n";
    stateRows << "seed,round,pre_hash,post_hash\n";
    rounds << "seed,rounds,simulated_ms,preparation_ms,combat_ms,settlement_ms,capped,encounters,timeouts,relic_choices,relic_equips,command_rejects\n";
    int fights = 0, timeouts = 0, drafts = 0, equips = 0, rejects = 0;
    for (int seed = firstSeed; seed < firstSeed + count; ++seed)
    {
        wc::Match match(catalog, wc::Id(seed), 0);
        std::array<int, 3> phaseMs{};
        Check(match.InvariantError().empty(), "initial tournament invariant");
        for (int tick = 0; tick < 200000 && match.CurrentPhase() != wc::Phase::Finished &&
             match.CurrentPhase() != wc::Phase::Aborted; ++tick)
        {
            const int phase = int(match.CurrentPhase()), elapsed = match.ElapsedMs();
            match.Tick(catalog.rules.tickMs);
            if (phase >= 0 && phase < 3) phaseMs[phase] += match.ElapsedMs() - elapsed;
            Check(match.InvariantError().empty(), "full tournament invariant seed " + std::to_string(seed));
        }
        Check(match.CurrentPhase() == wc::Phase::Finished, "full actual combat tournament completed");
        int matchFights = 0, matchTimeouts = 0, matchDrafts = 0, matchEquips = 0, matchRejects = 0;
        for (const auto &record : match.Records())
        {
            stateRows << seed << ',' << record.round << ',' << record.preHash << ',' << record.postHash << '\n';
            for (std::size_t index = 0; index < record.results.size(); ++index)
            {
                const auto &result = record.results[index]; const auto &pair = record.pairs[index];
                ++matchFights; if (result.timeout) ++matchTimeouts;
                combatRows << seed << ',' << record.round << ',' << index << ',' << pair.a << ',' << pair.b << ','
                    << int(pair.kind) << ',' << result.winner << ',' << result.ticks << ',' << result.timeout << ','
                    << result.survivors[0] << ',' << result.survivors[1] << '\n';
            }
        }
        for (const auto &decision : match.BotLog())
        {
            if (!decision.reply.accepted) ++matchRejects;
            if (decision.reply.accepted && decision.action == "choose_relic") ++matchDrafts;
            if (decision.reply.accepted && decision.action == "equip_relic") ++matchEquips;
        }
        for (const auto &seat : match.Seats())
            Check(seat.ownedRelics.size() <= 3, "maximum three relics conserved");
        Check(phaseMs[0] + phaseMs[1] + phaseMs[2] == match.ElapsedMs(), "all simulated time attributed to actual phase");
        rounds << seed << ',' << match.Round() << ',' << match.ElapsedMs() << ',' << phaseMs[0] << ',' << phaseMs[1] << ','
               << phaseMs[2] << ',' << int(match.Capped()) << ',' << matchFights << ',' << matchTimeouts
               << ',' << matchDrafts << ',' << matchEquips << ',' << matchRejects << '\n';
        rounds.flush();
        fights += matchFights; timeouts += matchTimeouts; drafts += matchDrafts; equips += matchEquips; rejects += matchRejects;
    }
    std::ofstream summary("summary.json");
    summary << "{\"profile\":\"wonder_vnext\",\"catalog_digest\":\"" << catalog.contentDigest
            << "\",\"actual_combat_tournaments\":" << count << ",\"first_seed\":" << firstSeed << ",\"encounters\":" << fights
            << ",\"timeouts\":" << timeouts << ",\"relic_choices\":" << drafts << ",\"relic_equips\":" << equips
            << ",\"command_rejects\":" << rejects << ",\"checks\":" << checks
            << ",\"boundary\":\"Six-hero native prototype; not engine packaging, full roster, human fun or balance acceptance\"}\n";
    Check(drafts > 0 && equips > 0, "bots actually draft and equip relics through authority");
}
}
int main(int argc, char **argv)
{
    try
    {
        const int count = argc > 1 ? std::stoi(argv[1]) : 10;
        const int firstSeed = argc > 2 ? std::stoi(argv[2]) : 1;
        Check(count >= 1 && count <= 10000, "bounded tournament count");
        Check(firstSeed >= 1 && firstSeed <= 10000 && count <= 10001 - firstSeed, "bounded tournament seed interval");
        const auto catalog = wcvnext::WonderVNextCatalog();
        Check(catalog.Validate().empty(), "canonical successor validates: " + catalog.Validate());
        VNextBotTests(catalog, Check);
        Commands(catalog); Relics(catalog); Saves(catalog); Tournaments(catalog, count, firstSeed);
        std::cout << "PASS " << checks << " checks; " << count << " actual six-hero vNext tournaments\n";
        return 0;
    }
    catch (const std::exception &error) { std::cerr << "FAIL after " << checks << " checks: " << error.what() << '\n'; return 1; }
}
