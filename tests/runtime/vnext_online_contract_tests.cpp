#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace
{
int checks = 0;
wc::Id request = 4000;
template <class T> constexpr bool ExposesPrivateState =
    requires(T value) { value.gold; } || requires(T value) { value.xp; } ||
    requires(T value) { value.shop; } || requires(T value) { value.roster; } ||
    requires(T value) { value.ownedRelics; } || requires(T value) { value.relicOffers; } ||
    requires(T value) { value.pendingRelicDrafts; } || requires(T value) { value.shopRng; } ||
    requires(T value) { value.botRng; } || requires(T value) { value.relicRng; };
static_assert(!ExposesPrivateState<wc::PublicSeat>, "Public scouting must exclude private economy, inventory and RNG");
void Check(bool condition, const std::string &message)
{
    ++checks;
    if (!condition) throw std::runtime_error(message);
}
void Owned(std::ostream &out, const wc::OwnedUnit &unit)
{
    out << unit.id << ',' << unit.definition << ',' << unit.star << ',' << unit.onBoard << ',' << unit.cell.column << ','
        << unit.cell.row << ',' << unit.bench << ',' << unit.neutral << ',' << unit.hpScaleBp << ',' << unit.damageScaleBp << ','
        << int(unit.facing) << ',' << unit.relic << ';';
}
std::string PublicState(const wc::Match &match)
{
    std::ostringstream out;
    for (const auto &seat : match.PublicSeats())
    {
        out << seat.id << ',' << seat.health << ',' << seat.level << ',' << seat.placement << ',' << seat.wins << ','
            << seat.human << ',' << seat.ready << ',' << seat.takeover << ',' << seat.label << ':';
        for (const auto &unit : seat.deployment) Owned(out, unit);
    }
    return out.str();
}
// Covers resources, identities and all owner RNG streams; later dual tournaments also
// detect side effects on hidden pairing/bot state that a rejected command must not change.
std::string OwnerState(const wc::Match &match)
{
    std::ostringstream out;
    out << match.Seed() << ',' << match.Namespace() << ',' << match.Round() << ',' << int(match.CurrentPhase()) << ','
        << match.ElapsedMs() << ',' << match.RemainingMs() << ':';
    for (const auto &seat : match.Seats())
    {
        out << seat.id << ',' << seat.health << ',' << seat.gold << ',' << seat.xp << ',' << seat.level << ',' << seat.placement << ','
            << seat.wins << ',' << seat.lockGold << ',' << seat.botIndex << ',' << seat.human << ',' << seat.takeover << ',' <<
            seat.ready << ',' << seat.shopLocked << ',' << seat.label << ',' << seat.revision << ',' << seat.sequence << ',' <<
            seat.shopRng.state << ',' << seat.botRng.state << ',' << seat.relicRng.state << ',' << seat.neutralWins << ',' <<
            seat.neutralLosses << ',' << seat.neutralDraws << ',' << seat.pendingRelicDrafts << ':';
        for (int item : seat.shop) out << item << ',';
        out << '/'; for (int item : seat.ownedRelics) out << item << ',';
        out << '/'; for (int item : seat.relicOffers) out << item << ',';
        out << '/'; for (const auto &unit : seat.roster) Owned(out, unit);
    }
    return out.str();
}
wc::Command Intent(const wc::Match &match, int seat, wc::CommandType type, int slot = -1, wc::Id unit = 0)
{
    wc::Command result;
    result.type = type; result.seat = seat; result.slot = slot; result.unit = unit; result.requestId = ++request;
    result.sequence = match.Seats()[seat].sequence + 1; result.revision = match.Seats()[seat].revision;
    return result;
}
void Accepted(wc::Match &match, wc::Command command, const std::string &message)
{
    const auto reply = match.Submit(command.seat, command);
    Check(reply.accepted, message + ": " + reply.reason);
}
void Rejected(wc::Match &match, int authenticated, const wc::Command &command, const std::string &message)
{
    const auto before = OwnerState(match);
    const auto reply = match.Submit(authenticated, command);
    Check(!reply.accepted && !reply.reason.empty(), message + ": rejection required");
    Check(OwnerState(match) == before && match.InvariantError().empty(), message + ": rejection must preserve all owner state");
}
wc::Id Recruit(wc::Match &match, int seat)
{
    const auto before = match.Seats()[seat].roster;
    for (int slot = 0; slot < int(match.Seats()[seat].shop.size()); ++slot)
    {
        const int definition = match.Seats()[seat].shop[slot];
        if (definition < 0 || match.Definitions().units[definition].cost > match.Seats()[seat].gold) continue;
        Accepted(match, Intent(match, seat, wc::CommandType::Buy, slot), "normal affordable recruitment");
        for (const auto &unit : match.Seats()[seat].roster)
            if (std::none_of(before.begin(), before.end(), [&](const auto &prior) { return prior.id == unit.id; })) return unit.id;
        throw std::runtime_error("Two-copy recruitment unexpectedly merged");
    }
    throw std::runtime_error("Fixture has no affordable recruit");
}
void AdvanceTo(wc::Match &match, int round)
{
    for (int tick = 0; tick < 200000; ++tick)
    {
        if (match.Round() == round && match.CurrentPhase() == wc::Phase::Preparation) return;
        if (match.CurrentPhase() == wc::Phase::Finished || match.CurrentPhase() == wc::Phase::Aborted) break;
        match.Tick(match.Definitions().rules.tickMs);
    }
    throw std::runtime_error("Expected preparation round was not reached");
}
void ForgedCommands(wc::Match &match, wc::Id victim)
{
    auto command = Intent(match, 1, wc::CommandType::ChooseRelic, 0);
    Rejected(match, 0, command, "forged victim seat cannot consume their private draft");
    command = Intent(match, 0, wc::CommandType::Ready);
    Rejected(match, -1, command, "unauthenticated caller");
    Rejected(match, 8, command, "out-of-range authenticated seat");
    for (auto type : {wc::CommandType::Sell, wc::CommandType::Move, wc::CommandType::SetFacing,
                      wc::CommandType::EquipRelic, wc::CommandType::UnequipRelic})
    {
        command = Intent(match, 0, type, 0, victim);
        command.toBoard = true; command.cell = {3, 3}; command.facing = wc::Facing::Left;
        Rejected(match, 0, command, "public victim unit identity cannot confer ownership");
    }
    command = Intent(match, 0, wc::CommandType::Reroll); command.sequence += 5;
    Rejected(match, 0, command, "future command sequence cannot skip authority");
    command = Intent(match, 0, wc::CommandType::Reroll); command.revision += 1;
    Rejected(match, 0, command, "forged revision cannot spend gold");
    command = Intent(match, 0, static_cast<wc::CommandType>(999));
    Rejected(match, 0, command, "unknown command enum");
    command = Intent(match, 0, wc::CommandType::ChooseRelic, 999);
    Rejected(match, 0, command, "catalog identity is not an arbitrary draft index");
}
void ProjectionAndDrafts(const wc::Catalog &catalog, int humans)
{
    wc::Match match(catalog, 314159 + humans, humans, true);
    Check(match.CurrentPhase() == wc::Phase::Preparation, "online-origin core supports requested human count");
    Check(std::count_if(match.Seats().begin(), match.Seats().end(), [](const auto &seat) { return seat.human; }) == humans,
          "requested 2H6B, 4H4B or 8H0B count is explicit");
    const auto owner = Recruit(match, 0);
    auto move = Intent(match, 0, wc::CommandType::Move, -1, owner); move.toBoard = true; move.cell = {2, 2};
    Accepted(match, move, "deploy owner through authority");
    const auto victim = Recruit(match, 1);
    move = Intent(match, 1, wc::CommandType::Move, -1, victim); move.toBoard = true; move.cell = {3, 2};
    Accepted(match, move, "deploy future public attack target");
    const auto publicBeforeBench = PublicState(match);
    const auto benched = Recruit(match, 0);
    Check(PublicState(match) == publicBeforeBench, "private bench recruitment does not expose purchase or shop state");
    const auto view = match.PublicSeats();
    Check(view[0].deployment.size() == 1 && view[0].deployment[0].id == owner && view[1].deployment[0].id == victim,
          "public projection contains actual deployed identities only");
    Check(std::none_of(view[0].deployment.begin(), view[0].deployment.end(), [&](const auto &unit) { return unit.id == benched; }) &&
          view[0].deployment[0].bench == -1, "bench identity and slot never appear in public deployment");
    AdvanceTo(match, 4);
    Check(match.Seats()[0].relicOffers.size() == 3 && match.Seats()[1].relicOffers.size() == 3, "both humans earn private normal-round drafts");
    ForgedCommands(match, victim);
    const auto publicBeforeDraft = PublicState(match);
    const int relic = match.Seats()[0].relicOffers[0];
    auto draft = Intent(match, 0, wc::CommandType::ChooseRelic, 0);
    Accepted(match, draft, "normal owner draft");
    Check(PublicState(match) == publicBeforeDraft, "unequipped private draft result is absent from public projection");
    const auto afterDraft = OwnerState(match);
    Check(match.Submit(0, draft).accepted && OwnerState(match) == afterDraft, "retransmitted draft cannot duplicate a relic");
    auto changed = draft; changed.slot = 1;
    Rejected(match, 0, changed, "same draft request with altered choice cannot select twice");
    int victimChoice = 0;
    while (match.Seats()[1].relicOffers[victimChoice] == relic) ++victimChoice;
    const int victimRelic = match.Seats()[1].relicOffers[victimChoice];
    Accepted(match, Intent(match, 1, wc::CommandType::ChooseRelic, victimChoice), "distinct victim-owned relic");
    Rejected(match, 0, Intent(match, 0, wc::CommandType::EquipRelic, victimRelic, owner), "other captain's relic identity cannot be equipped");
    auto ready = Intent(match, 0, wc::CommandType::Ready);
    Accepted(match, ready, "owner explicitly readies");
    Check(match.PublicSeats()[0].ready, "readiness is intentionally public");
    auto rotate = Intent(match, 0, wc::CommandType::SetFacing, -1, owner); rotate.facing = wc::Facing::Right;
    Accepted(match, rotate, "owner prepares orientation");
    Check(!match.PublicSeats()[0].ready && match.PublicSeats()[0].deployment[0].facing == wc::Facing::Right,
          "accepted formation change publishes orientation and withdraws ready");
    for (int seat = 0; seat < humans; ++seat) match.TakeOver(seat);
    const auto beforeRepeatedTakeover = OwnerState(match);
    for (int seat = 0; seat < humans; ++seat) match.TakeOver(seat);
    Check(OwnerState(match) == beforeRepeatedTakeover, "repeat disconnect notification cannot duplicate takeover state");
    Check(match.SavePreparation().empty(), "all-bot takeover does not change online save eligibility");
    std::cout << "PASS " << humans << "H" << 8 - humans << "B native_authority_private_projection_and_draft_attacks\n";
}
void StaleAndDeterministic(const wc::Catalog &catalog)
{
    wc::Match clean(catalog, 9821, 2, true), attacked(catalog, 9821, 2, true);
    wc::Command delayed;
    for (wc::Match *match : {&clean, &attacked})
    {
        for (int seat = 0; seat < 2; ++seat)
        {
            const auto unit = Recruit(*match, seat);
            auto move = Intent(*match, seat, wc::CommandType::Move, -1, unit); move.toBoard = true; move.cell = {seat + 2, 2};
            Accepted(*match, move, "deterministic legitimate formation");
        }
        if (match == &attacked) delayed = Intent(*match, 0, wc::CommandType::Reroll);
        AdvanceTo(*match, 4);
    }
    Rejected(attacked, 0, delayed, "delayed earlier-round message has stale revision");
    ForgedCommands(attacked, attacked.Seats()[1].roster.front().id);
    const auto beforeAbortProbe = OwnerState(attacked);
    auto preDisconnect = Intent(attacked, 0, wc::CommandType::Reroll);
    for (wc::Match *match : {&clean, &attacked}) { match->TakeOver(0); match->TakeOver(1); }
    for (int tick = 0; tick < 1000 && attacked.Seats()[0].sequence == preDisconnect.sequence - 1; ++tick)
    { clean.Tick(catalog.rules.tickMs); attacked.Tick(catalog.rules.tickMs); }
    Check(attacked.Seats()[0].sequence >= preDisconnect.sequence, "real takeover bot advances authoritative command sequence");
    Rejected(attacked, 0, preDisconnect, "pre-disconnect message cannot execute after bot advances sequence");
    Check(OwnerState(attacked) != beforeAbortProbe, "takeover fixture actually changed authoritative state");
    bool sawCombat = false;
    for (int tick = 0; tick < 200000 && clean.CurrentPhase() != wc::Phase::Finished; ++tick)
    {
        clean.Tick(catalog.rules.tickMs); attacked.Tick(catalog.rules.tickMs);
        if (clean.CurrentPhase() != attacked.CurrentPhase() || clean.Round() != attacked.Round())
            throw std::runtime_error("Rejected attacks changed deterministic phase progression");
        if (!sawCombat && attacked.CurrentPhase() == wc::Phase::Combat)
        {
            sawCombat = true;
            Rejected(attacked, 0, Intent(attacked, 0, wc::CommandType::Reroll), "new economic request during combat is phase-locked");
            Rejected(attacked, 0, Intent(attacked, 0, wc::CommandType::SetFacing, -1, attacked.Seats()[0].roster.front().id),
                     "new orientation request during combat is phase-locked");
        }
    }
    Check(sawCombat && clean.CurrentPhase() == wc::Phase::Finished && attacked.CurrentPhase() == wc::Phase::Finished,
          "both real combat tournaments finish");
    Check(clean.Records().size() == attacked.Records().size(), "rejected attacks preserve settlement count");
    for (std::size_t round = 0; round < clean.Records().size(); ++round)
        Check(clean.Records()[round].postHash == attacked.Records()[round].postHash, "rejected attacks preserve every settlement hash");
    for (int seat = 0; seat < 8; ++seat)
        Check(clean.Seats()[seat].placement == attacked.Seats()[seat].placement && clean.Seats()[seat].health == attacked.Seats()[seat].health &&
              clean.Seats()[seat].shopRng.state == attacked.Seats()[seat].shopRng.state &&
              clean.Seats()[seat].botRng.state == attacked.Seats()[seat].botRng.state &&
              clean.Seats()[seat].relicRng.state == attacked.Seats()[seat].relicRng.state,
              "rejected attacks do not change outcomes or future random streams");
    auto fromPriorMatch = Intent(attacked, 0, wc::CommandType::Ready);
    attacked.Restart(9821, 2, true);
    fromPriorMatch.sequence = attacked.Seats()[0].sequence + 1;
    Rejected(attacked, 0, fromPriorMatch, "prior-match revision cannot acquire a restarted seat");
    attacked.Abort();
    const auto aborted = OwnerState(attacked);
    attacked.Tick(100000);
    Check(attacked.CurrentPhase() == wc::Phase::Aborted && OwnerState(attacked) == aborted &&
          std::all_of(attacked.Seats().begin(), attacked.Seats().end(), [](const auto &seat) { return seat.placement == 0; }),
          "server abort remains aborted with no fabricated final placement");
    std::cout << "PASS stale_messages_takeover_phase_locks_deterministic_outcomes_and_abort\n";
}
} // namespace
int main()
{
    try
    {
        const auto catalog = wcvnext::WonderVNextCatalog();
        Check(catalog.Validate().empty(), "frozen successor catalog validates");
        for (int humans : {2, 4, 8}) ProjectionAndDrafts(catalog, humans);
        StaleAndDeterministic(catalog);
        std::cout << "PASS " << checks << " native checks; no transport, authenticated reclaim, EOS or remote-device acceptance\n";
        return 0;
    }
    catch (const std::exception &exception)
    {
        std::cerr << "FAIL after " << checks << " checks: " << exception.what() << '\n';
        return 1;
    }
}
