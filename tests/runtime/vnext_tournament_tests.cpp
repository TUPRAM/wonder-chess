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
    AdvanceTo(match, 11);
    Check(match.Seats()[0].health > 0 && match.Seats()[0].relicOffers.size() == 3,
          "first boss round awards three relic choices even after a loss");
    Check(match.Seats()[0].pendingRelicDrafts == 1, "one draft per milestone");
    const auto before = match.SavePreparation();
    std::ofstream("relic-study-preparation.wcsave", std::ios::binary).write(before.data(), std::streamsize(before.size()));
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
void OwnedTeamRelicPolicy(const wc::Catalog &catalog)
{
    Check(catalog.ownedTeamRelicOffers, "solo candidate declares owned-team relic policy");
    int guaranteedOffers = 0, naturalFallbacks = 0;
    for (wc::Id seed = 20; seed < 32; ++seed)
    {
        wc::Match original(catalog, seed, 1);
        Check(Send(original, 0, wc::CommandType::Buy, 0).accepted, "policy fixture buys from real opening shop");
        const auto holder = original.Seats()[0].roster.front();
        Check(!holder.onBoard, "benched ownership qualifies without deployment");
        const auto initial = original.SavePreparation();
        wc::Match restored(catalog, 99, 1); std::string error;
        Check(restored.RestorePreparation(initial, error), "pre-draft state restores");
        AdvanceTo(original, 11); AdvanceTo(restored, 11);
        const auto offers = original.Seats()[0].relicOffers;
        Check(offers.size() == 3 && std::set<int>(offers.begin(), offers.end()).size() == 3,
              "draft contains three unique options");
        const bool compatibleAvailable = std::any_of(catalog.relics.begin(), catalog.relics.end(), [&](const auto &relic) {
            return wc::RelicCompatible(relic, catalog.units[holder.definition].ability.mechanic);
        });
        const bool compatibleOffered = std::any_of(offers.begin(), offers.end(), [&](int relic) {
            return wc::RelicCompatible(catalog.relics[relic], catalog.units[holder.definition].ability.mechanic);
        });
        if (compatibleAvailable) {
            ++guaranteedOffers;
            Check(compatibleOffered, "available compatible relic guarantees an offer for the owned bench creature");
        } else {
            ++naturalFallbacks;
            Check(!compatibleOffered, "a genuine catalogue compatibility gap uses honest speculative offers");
        }
        Check(offers == restored.Seats()[0].relicOffers &&
              original.Seats()[0].relicRng.state == restored.Seats()[0].relicRng.state,
              "cold logical resume preserves constrained draft and RNG");
        Check(Send(original, 0, wc::CommandType::Sell, -1, holder.id).accepted,
              "roster can change after draft generation");
        Check(original.Seats()[0].relicOffers == offers, "selling holder does not reroll existing offers");
        Check(Send(original, 0, wc::CommandType::ChooseRelic, 0).accepted,
              "now-speculative offer remains a valid choice");
        Check(original.Seats()[0].ownedRelics.size() == 1 && original.Seats()[0].pendingRelicDrafts == 0 &&
              original.Seats()[0].relicOffers.empty(), "guaranteed and fallback drafts conserve exactly one selected relic");
    }
    Check(guaranteedOffers > 0, "normal shop fixtures actually exercise the compatible-offer guarantee");
    std::cout << "Owned-team draft coverage: " << guaranteedOffers << " compatible guarantees, " << naturalFallbacks << " natural compatibility gaps.\n";
    wc::Match empty(catalog, 50, 1);
    AdvanceTo(empty, 11);
    Check(empty.Seats()[0].roster.empty() && empty.Seats()[0].relicOffers.size() == 3,
          "empty team falls back to catalog-compatible offers");

    auto noCompatible = catalog;
    wc::Match preview(catalog, 51, 1);
    const auto openingMechanic = catalog.units[preview.Seats()[0].shop[0]].ability.mechanic;
    // Canonical relics fit every hero. Bind this fixture's relics to two other mechanics so a real
    // owned-team compatibility gap exists without editing a seat.
    for (auto &relic : noCompatible.relics)
        for (auto mechanic : {wc::AbilityMechanic::DirectionalGuard, wc::AbilityMechanic::MomentumCharge,
                              wc::AbilityMechanic::StationaryGrove})
            if (mechanic != openingMechanic && relic.compatibleMechanics.size() < 2)
                relic.compatibleMechanics.push_back(mechanic);
    Check(!noCompatible.relics.empty(), "fallback fixture retains other-mechanic relics");
    Check(noCompatible.Validate().empty(), "restricted relic fixture is a valid catalog");
    wc::Match gap(noCompatible, 51, 1);
    Check(Send(gap, 0, wc::CommandType::Buy, 0).accepted, "gap fixture acquires opening recruit");
    AdvanceTo(gap, 11);
    Check(!gap.Seats()[0].relicOffers.empty(), "no owned-compatible option still produces an eligible draft");
    Check(std::none_of(gap.Seats()[0].relicOffers.begin(), gap.Seats()[0].relicOffers.end(), [&](int r) {
        return wc::RelicCompatible(noCompatible.relics[r], noCompatible.units[gap.Seats()[0].roster.front().definition].ability.mechanic);
    }), "fallback fixture actually has no compatible owned option");
    Check(Send(gap, 0, wc::CommandType::ChooseRelic, 0).accepted && gap.Seats()[0].ownedRelics.size() == 1 &&
          gap.Seats()[0].pendingRelicDrafts == 0 && gap.Seats()[0].relicOffers.empty(),
          "explicit no-compatible fallback also conserves draft ownership and entitlement");
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
void Economy(const wc::Catalog &catalog)
{
    const auto &rules = catalog.rules;
    // Preparation time by stage: the first round keeps its own longer time.
    Check(wc::PreparationMs(rules, 1) == 60000 && wc::PreparationMs(rules, 2) == 25000 && wc::PreparationMs(rules, 5) == 25000 &&
          wc::PreparationMs(rules, 6) == 30000 && wc::PreparationMs(rules, 20) == 30000 && wc::PreparationMs(rules, 21) == 35000 &&
          wc::PreparationMs(rules, 60) == 35000, "preparation is 60 s first, then 25 / 30 / 35 s by stage");
    auto uncovered = catalog;
    uncovered.rules.preparationStages.pop_back();
    Check(wc::PreparationMs(uncovered.rules, 40) == uncovered.rules.preparationMs, "a round outside every stage uses the plain preparation time");
    auto wrong = catalog;
    wrong.rules.preparationStages[1].start = 5;
    Check(!wrong.Validate().empty(), "overlapping preparation stages are rejected");
    wrong = catalog;
    wrong.rules.streakIncome[1].gold = 1;
    Check(!wrong.Validate().empty(), "streak income must rise with the streak");

    // Streak income: 3 in a row pays 1, 5 pays 2, 7 pays 3; a losing run pays the same.
    const int expected[] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 3};
    for (int length = 0; length < 10; ++length)
        Check(wc::StreakIncome(rules, length) == expected[length] && wc::StreakIncome(rules, -length) == expected[length],
              "streak income steps at 3, 5 and 7, for wins and losses alike");

    // A real match: the timer follows the stages, the streak follows player fights only, and income is paid by the formula.
    wc::Match match(catalog, 733, 0);
    std::array<int, 8> streak{}, gold{};
    std::size_t settled = 0;
    bool anyStreakPaid = false;
    for (int tick = 0; tick < 200000 && match.Round() <= 16 && match.CurrentPhase() != wc::Phase::Finished; ++tick)
    {
        const auto phase = match.CurrentPhase();
        for (const auto &seat : match.Seats()) gold[seat.id] = seat.gold;
        match.Tick(rules.tickMs);
        for (; settled < match.Records().size(); ++settled)
        {
            const auto &record = match.Records()[settled];
            if (record.neutral) continue;
            for (std::size_t index = 0; index < record.pairs.size(); ++index)
                for (int side = 0; side < 2; ++side)
                {
                    const auto &pair = record.pairs[index];
                    const int seat = side == 0 ? pair.a : pair.b;
                    if (seat < 0 || (side == 1 && pair.kind != wc::EncounterKind::Pvp)) continue;
                    const int winner = record.results[index].winner;
                    streak[seat] = winner < 0 ? 0 : winner == side ? std::max(streak[seat], 0) + 1 : std::min(streak[seat], 0) - 1;
                }
        }
        for (const auto &seat : match.Seats())
            Check(seat.streak == streak[seat.id], "a seat's streak counts player fights only and resets on a draw");
        if (phase == wc::Phase::Settlement && match.CurrentPhase() == wc::Phase::Preparation)
        {
            Check(match.RemainingMs() == wc::PreparationMs(rules, match.Round()), "the round starts with its stage's preparation time");
            const auto &record = match.Records().back();
            for (const auto &seat : match.Seats())
            {
                if (seat.health <= 0) continue;
                const int paid = rules.baseIncome + record.pendingRewards[seat.id] + wc::StreakIncome(rules, seat.streak) +
                                 std::min(rules.interestCap, seat.lockGold / rules.interestDivisor);
                Check(seat.gold - gold[seat.id] == paid, "income is base, reward, streak and interest");
                anyStreakPaid = anyStreakPaid || wc::StreakIncome(rules, seat.streak) > 0;
            }
        }
    }
    Check(anyStreakPaid, "some seat was paid for a streak in sixteen rounds");

    // The streak survives a save.
    const auto saved = match.SavePreparation();
    wc::Match resumed(catalog, 1, 0);
    std::string error;
    Check(!saved.empty() && resumed.RestorePreparation(saved, error) && resumed.SavePreparation() == saved, "a match with streaks saves and restores exactly");
    bool same = true, nonzero = false;
    for (const auto &seat : match.Seats())
    {
        same = same && resumed.Seats()[seat.id].streak == seat.streak;
        nonzero = nonzero || seat.streak != 0;
    }
    Check(same && nonzero, "restored seats keep their streaks");

    // Auto-deploy: a unit left on the bench is placed when preparation ends, at the middle of the back row.
    auto idleCaptain = [&](wc::Match &solo) {
        Check(Send(solo, 0, wc::CommandType::Buy, 0).accepted && Send(solo, 0, wc::CommandType::Buy, 1).accepted, "the captain buys two heroes and leaves them benched");
        for (int tick = 0; tick < 2000 && solo.CurrentPhase() == wc::Phase::Preparation; ++tick) solo.Tick(rules.tickMs);
        Check(solo.CurrentPhase() == wc::Phase::Combat && solo.InvariantError().empty(), "preparation ends by the clock with the captain idle");
    };
    {
        wc::Match solo(catalog, 808, 1);
        idleCaptain(solo);
        const auto &roster = solo.Seats()[0].roster;
        Check(roster.size() == 2 && roster[0].onBoard && roster[1].onBoard && roster[0].bench == -1 &&
              roster[0].cell == wc::Cell{3, 0} && roster[1].cell == wc::Cell{4, 0},
              "benched heroes are placed in bench order on the middle of the back row");
        Check(solo.AutoDeployed(0) == std::vector<wc::Id>({roster[0].id, roster[1].id}), "the match reports what it placed");
        int fielded = 0;
        for (const auto &unit : solo.Encounters().front().combat.Units()) fielded += unit.side == 0 && !unit.neutral;
        Check(fielded == 2, "the placed heroes fight");
    }
    {
        auto manual = catalog;
        manual.rules.autoDeploy = false;
        wc::Match solo(manual, 808, 1);
        idleCaptain(solo);
        Check(!solo.Seats()[0].roster[0].onBoard && solo.AutoDeployed(0).empty(), "without the rule a benched hero stays benched");
    }
    {
        // Never more than the level allows.
        auto rich = catalog;
        rich.rules.startingGold = 1000;
        wc::Match solo(rich, 809, 1);
        int bought = 0;
        for (int attempt = 0; attempt < 40 && bought < 6; ++attempt)
        {
            for (int slot = 0; slot < 5 && bought < 6; ++slot)
                if (solo.Seats()[0].shop[slot] >= 0 && Send(solo, 0, wc::CommandType::Buy, slot).accepted) ++bought;
            Send(solo, 0, wc::CommandType::Reroll);
        }
        const int owned = int(solo.Seats()[0].roster.size());
        for (int tick = 0; tick < 2000 && solo.CurrentPhase() == wc::Phase::Preparation; ++tick) solo.Tick(rich.rules.tickMs);
        int deployed = 0;
        for (const auto &unit : solo.Seats()[0].roster) deployed += unit.onBoard;
        Check(deployed == std::min(owned, solo.Seats()[0].level) && solo.InvariantError().empty(), "auto-deploy stops at the level's board limit");
    }
}
void Guided(const wc::Catalog &catalog)
{
    // Plays the whole guided first match the way a captain following it would: every step is completed with the
    // orders that step allows, every lesson's fight is fought, and the captain wins each one.
    const auto tutorial = wcvnext::WonderVNextTutorial();
    const auto &rules = catalog.rules;
    Check(tutorial.stages.size() == 6, "the guided match has six stages");
    // Fights differ a little from seed to seed (who acts first, critical hits). The captain must win every lesson on each.
    for (const wc::Id seed : {wc::Id(4242), wc::Id(1), wc::Id(2), wc::Id(3), wc::Id(77), wc::Id(1000), wc::Id(31337), wc::Id(8)})
    {
    wc::Match match(catalog, seed, 1);
    for (const auto &stage : tutorial.stages)
    {
        const std::string where = "guided stage " + stage.id + " (seed " + std::to_string(seed) + ")";
        match.BeginGuidedStage(stage);
        Check(match.Guided() && match.CurrentPhase() == wc::Phase::Preparation && match.Round() == stage.round, where + " starts in preparation");
        Check(match.InvariantError().empty(), where + " is a valid match state: " + match.InvariantError());
        Check(match.SavePreparation().empty(), where + " is never saved");
        Check(match.Seats()[0].gold == stage.gold && match.Seats()[0].level == stage.level && match.Seats()[2].health == 0 &&
              match.Pairings().size() >= 1 && match.Pairings()[0].a == 0, where + " sets up the captain, one opponent and nobody else");
        const int held = match.RemainingMs();
        for (int tick = 0; tick < 100; ++tick) match.Tick(rules.tickMs);
        Check(match.RemainingMs() == held && match.CurrentPhase() == wc::Phase::Preparation, where + " holds the preparation clock");
        wc::GuidedView view;
        for (const auto &step : stage.steps)
        {
            const std::string what = where + ", step '" + step.done + "'";
            Check(!step.textEn.empty() && !step.textId.empty(), what + " has text in both languages");
            const auto order = [&](wc::Command command) {
                Check(wc::GuidedAllows(step, command.type), what + " allows the order it asks for");
                const auto reply = match.Submit(0, command);
                Check(reply.accepted, what + " order accepted: " + reply.reason);
            };
            const auto move = [&](wc::Id unit, wc::Cell cell) {
                auto command = Intent(match, 0, wc::CommandType::Move, -1, unit);
                command.toBoard = true; command.cell = cell;
                order(command);
            };
            const auto freeCell = [&] {
                for (int row = rules.deploymentRows - 1; row >= 0; --row)
                    for (int column = 0; column < rules.columns; ++column)
                    {
                        bool taken = false;
                        for (const auto &unit : match.Seats()[0].roster) taken = taken || (unit.onBoard && unit.cell == wc::Cell{column, row});
                        if (!taken) return wc::Cell{column, row};
                    }
                return wc::Cell{};
            };
            for (int attempt = 0; attempt < 20 && !match.GuidedStepDone(step, view); ++attempt)
            {
                const auto roster = match.Seats()[0].roster;
                const auto &captain = match.Seats()[0];
                if (step.done == "deployed_at_least" || step.done == "trait_at_least")
                {
                    for (const auto &unit : roster)
                    {
                        const auto &hero = catalog.units[unit.definition];
                        if (!unit.onBoard && (step.done == "deployed_at_least" || hero.race == step.trait || hero.unitClass == step.trait))
                        { move(unit.id, freeCell()); break; }
                    }
                }
                else if (step.done == "ready") order(Intent(match, 0, wc::CommandType::Ready));
                else if (step.done == "fight_over")
                    for (int tick = 0; tick < 4000 && !match.GuidedStepDone(step, view); ++tick)
                    {
                        match.Tick(rules.tickMs);
                        Check(match.InvariantError().empty(), what + " keeps the match valid: " + match.InvariantError());
                    }
                else if (step.done == "shop_open") view.shopOpen = true;
                else if (step.done == "trait_focus") view.traitFocus = step.trait;
                else if (step.done == "owns" || step.done == "star_at_least")
                {
                    for (int slot = 0; slot < int(captain.shop.size()); ++slot)
                        if (captain.shop[slot] == step.definition) { order(Intent(match, 0, wc::CommandType::Buy, slot)); break; }
                }
                else if (step.done == "level_at_least") order(Intent(match, 0, wc::CommandType::BuyXp));
                else if (step.done == "row_at_least" || step.done == "row_at_most")
                {
                    for (const auto &unit : roster)
                        if (unit.definition == step.definition) { move(unit.id, {unit.cell.column, step.value}); break; }
                }
                else if (step.done == "gold_at_least")
                {
                    for (const auto &unit : roster)
                        if (!unit.onBoard) { order(Intent(match, 0, wc::CommandType::Sell, -1, unit.id)); break; }
                }
                else if (step.done == "shop_locked") order(Intent(match, 0, wc::CommandType::ToggleLock));
                else if (step.done == "relic_owned") order(Intent(match, 0, wc::CommandType::ChooseRelic, 0));
                else if (step.done == "relic_equipped")
                    order(Intent(match, 0, wc::CommandType::EquipRelic, captain.ownedRelics.front(), roster.front().id));
            }
            Check(match.GuidedStepDone(step, view), what + " can be completed");
        }
        if (stage.fight)
        {
            const auto &record = match.Records().back();
            Check(record.pairs[0].a == 0 && record.results[0].winner == 0, where + ": the captain wins the lesson's fight");
            for (int tick = 0; tick < 300; ++tick) match.Tick(rules.tickMs);
            Check(match.CurrentPhase() == wc::Phase::Settlement && match.Round() == stage.round, where + " waits for the next lesson after its fight");
        }
        else Check(match.CurrentPhase() == wc::Phase::Preparation && match.Records().empty(), where + " has no fight");
    }
    }
    wc::Match match(catalog, 4242, 1);
    match.BeginGuidedStage(tutorial.stages.front());
    match.Restart(77, 1);
    Check(!match.Guided() && match.InvariantError().empty() && match.Seats()[7].health > 0 && match.Round() == 1,
          "an ordinary match starts normally after the guide");
}
void Tournaments(const wc::Catalog &catalog, int count, int firstSeed = 1, const std::string &lossOverride = "")
{
    std::ofstream rounds("tournaments.csv");
    std::ofstream combatRows("encounters.csv"), stateRows("rounds.csv");
    combatRows << "seed,round,index,a,b,kind,winner,ticks,timeout,survivors_a,survivors_b\n";
    stateRows << "seed,round,pre_hash,post_hash\n";
    rounds << "seed,rounds,simulated_ms,preparation_ms,combat_ms,settlement_ms,capped,encounters,timeouts,relic_choices,relic_equips,command_rejects\n";
    // Per-seat balance data, sampled when preparation locks and when the round settles.
    std::ofstream seatRows("seats.csv"), boardRows("boards.csv"), traitRows("traits.csv"), settleRows("settlements.csv"),
        waveRows("waves.csv"), placementRows("placements.csv");
    seatRows << "seed,round,seat,bot,gold,level,health,deployed,benched,board_cost,relics,streak\n";
    boardRows << "seed,round,seat,hero,cost,star,relic\n";
    traitRows << "seed,round,seat,trait,count,tier\n";
    settleRows << "seed,round,seat,neutral,damage,reward,health,placement\n";
    waveRows << "seed,round,seat,wave,result,ticks,timeout\n";
    placementRows << "seed,seat,bot,placement,health,wins,neutral_wins,neutral_losses,level,rounds\n";
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
            if (phase == int(wc::Phase::Preparation) && match.CurrentPhase() == wc::Phase::Combat)
                for (const auto &seat : match.Seats())
                {
                    if (seat.health <= 0) continue;
                    int deployed = 0, benched = 0, boardCost = 0;
                    std::map<std::string, std::set<int>> families;
                    for (const auto &unit : seat.roster)
                    {
                        if (!unit.onBoard) { ++benched; continue; }
                        const auto &hero = catalog.units[unit.definition];
                        ++deployed;
                        boardCost += hero.cost * (unit.star == 3 ? 9 : unit.star == 2 ? 3 : 1);
                        families[hero.race].insert(unit.definition);
                        families[hero.unitClass].insert(unit.definition);
                        boardRows << seed << ',' << match.Round() << ',' << seat.id << ',' << hero.id << ',' << hero.cost << ','
                                  << unit.star << ',' << (unit.relic >= 0 ? catalog.relics[unit.relic].id : "") << '\n';
                    }
                    seatRows << seed << ',' << match.Round() << ',' << seat.id << ',' << catalog.bots[seat.botIndex].id << ','
                             << seat.gold << ',' << seat.level << ',' << seat.health << ',' << deployed << ',' << benched << ','
                             << boardCost << ',' << seat.ownedRelics.size() << ',' << seat.streak << '\n';
                    std::set<std::string> listed;
                    for (const auto &trait : catalog.traits)
                    {
                        if (!listed.insert(trait.id).second) continue;
                        const int members = int(families[trait.id].size());
                        int tier = 0;
                        for (const auto &step : trait.tiers) tier += members >= step.first;
                        if (members > 0)
                            traitRows << seed << ',' << match.Round() << ',' << seat.id << ',' << trait.id << ',' << members << ','
                                      << tier << '\n';
                    }
                }
            Check(match.InvariantError().empty(), "full tournament invariant seed " + std::to_string(seed));
        }
        Check(match.CurrentPhase() == wc::Phase::Finished, "full actual combat tournament completed");
        int matchFights = 0, matchTimeouts = 0, matchDrafts = 0, matchEquips = 0, matchRejects = 0;
        for (const auto &record : match.Records())
        {
            stateRows << seed << ',' << record.round << ',' << record.preHash << ',' << record.postHash << '\n';
            for (std::size_t index = 0; index < record.results.size(); ++index)
            {
                const auto &pair = record.pairs[index]; const auto &result = record.results[index];
                for (int side = 0; side < 2; ++side)
                {
                    const int seat = side == 0 ? pair.a : pair.b;
                    if (seat < 0 || (side == 1 && pair.kind != wc::EncounterKind::Pvp)) continue;
                    settleRows << seed << ',' << record.round << ',' << seat << ',' << int(record.neutral) << ','
                               << record.damage[seat] << ',' << record.pendingRewards[seat] << ',' << record.health[seat] << ','
                               << record.placement[seat] << '\n';
                    if (pair.kind == wc::EncounterKind::Neutral)
                        waveRows << seed << ',' << record.round << ',' << seat << ',' << pair.waveId << ','
                                 << (result.winner == side ? "won" : result.winner < 0 ? "draw" : "lost") << ',' << result.ticks << ','
                                 << result.timeout << '\n';
                }
            }
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
        {
            Check(seat.ownedRelics.size() <= 3, "maximum three relics conserved");
            placementRows << seed << ',' << seat.id << ',' << catalog.bots[seat.botIndex].id << ',' << seat.placement << ','
                          << seat.health << ',' << seat.wins << ',' << seat.neutralWins << ',' << seat.neutralLosses << ','
                          << seat.level << ',' << match.Round() << '\n';
        }
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
            << ",\"enabled_heroes\":" << catalog.units.size()
            << ",\"balance_version\":\"" << catalog.balanceVersion << "\",\"traits\":" << catalog.traits.size()
            << ",\"loss_damage_override\":\"" << lossOverride << "\""
            << ",\"boundary\":\"Current enabled native prototype; not engine packaging, full roster, human fun or balance acceptance\"}\n";
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
        VNextBotRoleTests(wcvnext::WonderVNextRosterCatalog(), Check);
        // Contract tests always run on the control catalogue. The tournaments themselves run on
        // the control catalogue by default, or on the live roster rules when asked.
        const std::string ruleSet = argc > 3 ? argv[3] : "control";
        Check(ruleSet == "control" || ruleSet == "roster", "rule set is control or roster");
        Commands(catalog); Relics(catalog); OwnedTeamRelicPolicy(catalog); Saves(catalog); Economy(catalog); Guided(wcvnext::WonderVNextRosterCatalog());
        // A measurement run may try other loss damage per stage, as "2,4,6,9". The catalogue itself is not changed.
        auto played = ruleSet == "roster" ? wcvnext::WonderVNextRosterCatalog() : catalog;
        const std::string lossOverride = argc > 4 ? argv[4] : "";
        if (!lossOverride.empty())
        {
            std::size_t stage = 0, at = 0;
            while (at <= lossOverride.size() && stage < played.rules.lossStages.size())
            {
                const auto comma = std::min(lossOverride.find(',', at), lossOverride.size());
                played.rules.lossStages[stage++].damage = std::stoi(lossOverride.substr(at, comma - at));
                at = comma + 1;
            }
            Check(stage == played.rules.lossStages.size() && at > lossOverride.size() && played.Validate().empty(),
                  "a loss damage override names one value per stage");
        }
        Tournaments(played, count, firstSeed, lossOverride);
        std::cout << "PASS " << checks << " checks; " << count << " actual " << catalog.units.size() << "-hero vNext tournaments ("
                  << ruleSet << " rules)\n";
        return 0;
    }
    catch (const std::exception &error) { std::cerr << "FAIL after " << checks << " checks: " << error.what() << '\n'; return 1; }
}
