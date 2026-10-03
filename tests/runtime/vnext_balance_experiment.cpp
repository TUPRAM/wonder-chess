#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <tuple>

namespace
{
void Require(bool condition, const std::string& message)
{
    if (!condition) throw std::runtime_error(message);
}
int Copies(int star) { return star == 3 ? 9 : star == 2 ? 3 : 1; }
auto EventKey(const wc::CombatEvent& e)
{
    return std::make_tuple(e.tick,e.source,e.target,e.action,e.effect,e.requested,e.resolved,e.absorbed,
        e.healthLoss,e.overkill,e.cell.column,e.cell.row,e.absorbedFrom,e.damageType,e.basicAttack,
        e.radius,e.mechanic,e.origin.column,e.origin.row,e.guardedBy,e.prevented);
}
void VerifyDiagnosticReplay(const wc::Combat& observed, const wc::Combat& original)
{
    const auto& a = observed.Result(); const auto& b = original.Result();
    Require(std::tie(a.complete,a.timeout,a.winner,a.ticks,a.survivors) ==
        std::tie(b.complete,b.timeout,b.winner,b.ticks,b.survivors), "Diagnostic replay result parity");
    Require(observed.Events().size() == original.Events().size(), "Diagnostic replay event count parity");
    for (std::size_t i = 0; i < observed.Events().size(); ++i)
        Require(EventKey(observed.Events()[i]) == EventKey(original.Events()[i]), "Diagnostic replay all event fields parity");
    Require(observed.Units().size() == original.Units().size(), "Diagnostic replay unit count parity");
    for (std::size_t i = 0; i < observed.Units().size(); ++i)
    {
        const auto& x = observed.Units()[i]; const auto& y = original.Units()[i];
        Require(std::tie(x.id,x.health,x.shield,x.cell.column,x.cell.row,x.state,x.actionId,x.positionEpoch,x.momentumSteps) ==
            std::tie(y.id,y.health,y.shield,y.cell.column,y.cell.row,y.state,y.actionId,y.positionEpoch,y.momentumSteps),
            "Diagnostic replay final state parity");
    }
}
void WriteTraces(std::ostream& out, const wc::Catalog& catalog, const wc::Combat& combat,
    const std::string& variant, int seed, int round, int index, const std::string& kind)
{
    std::map<wc::Id, int> definitions;
    for (const auto& unit : combat.Units()) definitions[unit.id] = unit.definition;
    using Key = std::tuple<int, wc::MechanicPhase, wc::MechanicReason>;
    std::map<Key, std::array<wc::Int, 5>> grouped;
    std::map<wc::Id, std::array<int, 3>> actions;
    for (const auto& t : combat.Diagnostics())
    {
        auto& sum = grouped[{definitions.at(t.source), t.phase, t.reason}];
        ++sum[0]; sum[1] += t.recipients; sum[2] += t.fullHealthAllies; sum[3] += t.requested; sum[4] += t.resolved;
        if (t.phase == wc::MechanicPhase::Committed) ++actions[t.action][0];
        if (t.phase == wc::MechanicPhase::Released) ++actions[t.action][1];
        if (t.phase == wc::MechanicPhase::Cancelled) ++actions[t.action][2];
    }
    for (const auto& entry : actions)
        Require(entry.second[0] == 1 && entry.second[1] + entry.second[2] == 1,
            "Every diagnostic commitment has exactly one release or cancellation");
    for (const auto& entry : grouped)
    {
        out << variant << ',' << seed << ',' << round << ',' << index << ',' << kind << ','
            << catalog.units[std::get<0>(entry.first)].id << ',' << wc::MechanicPhaseName(std::get<1>(entry.first))
            << ',' << wc::MechanicReasonName(std::get<2>(entry.first));
        for (const auto value : entry.second) out << ',' << value;
        out << '\n';
    }
}
int Definition(const wc::Catalog& catalog, const std::string& id)
{
    for (int i = 0; i < int(catalog.units.size()); ++i) if (catalog.units[i].id == id) return i;
    throw std::runtime_error("Missing canonical unit: " + id);
}
wc::OwnedUnit Unit(wc::Id id, int definition, int x, int y, int star = 1)
{
    wc::OwnedUnit unit;
    unit.id = id; unit.definition = definition; unit.onBoard = true; unit.cell = {x, y}; unit.star = star;
    return unit;
}
struct Metrics
{
    wc::Int damage = 0, healing = 0, overheal = 0, prevented = 0, chargeDamage = 0;
    int firstAction = -1, firstDeath = -1, deaths = 0, chargeLandings = 0, chargeSources = 0, crags = 0;
    std::array<int, 2> roots{}, duplicateMax{}, survivorInvestment{};
};
Metrics Measure(const wc::Catalog& catalog, const wc::Combat& combat)
{
    Metrics metrics;
    std::map<wc::Id, wc::Int> health;
    std::map<wc::Id, int> definitions;
    std::array<std::map<int, int>, 2> compositions;
    std::set<wc::Id> chargeSources;
    for (const auto& unit : combat.Units())
    {
        health[unit.id] = unit.maxHealth;
        definitions[unit.id] = unit.definition;
        if (unit.neutral) continue;
        const auto& definition = catalog.units[unit.definition];
        ++compositions[unit.side][unit.definition];
        if (definition.ability.mechanic == wc::AbilityMechanic::StationaryGrove) ++metrics.roots[unit.side];
        if (definition.ability.mechanic == wc::AbilityMechanic::MomentumCharge) ++metrics.crags;
        if (unit.health > 0) metrics.survivorInvestment[unit.side] += definition.cost * Copies(unit.star);
    }
    for (int side = 0; side < 2; ++side)
        for (const auto& entry : compositions[side]) metrics.duplicateMax[side] = std::max(metrics.duplicateMax[side], entry.second);
    for (const auto& event : combat.Events())
    {
        if (metrics.firstAction < 0 && (event.healthLoss > 0 || event.resolved > 0 || event.effect == wc::Effect::Dash))
            metrics.firstAction = event.tick;
        if (event.effect == wc::Effect::Damage)
        {
            Require(event.resolved == event.healthLoss + event.absorbed + event.overkill, "Damage reconciliation");
            metrics.damage += event.healthLoss; metrics.prevented += event.prevented;
            health[event.target] -= event.healthLoss;
            if (health[event.target] == 0)
            {
                ++metrics.deaths;
                if (metrics.firstDeath < 0) metrics.firstDeath = event.tick;
            }
            if (event.mechanic == wc::AbilityMechanic::MomentumCharge)
            { metrics.chargeDamage += event.healthLoss; chargeSources.insert(event.source); }
        }
        else if (event.effect == wc::Effect::Heal)
        {
            Require(event.requested >= event.resolved && event.resolved >= 0, "Healing reconciliation");
            metrics.healing += event.resolved; metrics.overheal += event.requested - event.resolved;
            health[event.target] += event.resolved;
        }
        else if (event.effect == wc::Effect::Dash && event.mechanic == wc::AbilityMechanic::MomentumCharge)
            ++metrics.chargeLandings;
    }
    for (const auto& unit : combat.Units()) Require(health[unit.id] == unit.health, "Per-unit final health reconciliation");
    metrics.chargeSources = int(chargeSources.size());
    return metrics;
}
void MetricHeader(std::ostream& out)
{
    out << "ticks,timeout,winner,survivors_a,survivors_b,health_damage_cp,effective_healing_cp,logged_recipient_overheal_cp,guard_prevented_cp,first_action_tick,first_death_tick,deaths,crag_instances,charging_sources,charge_movement_landings,charge_damage_cp,roots_a,roots_b,max_duplicates_a,max_duplicates_b,survivor_investment_a,survivor_investment_b";
}
void WriteMetrics(std::ostream& out, const wc::Combat& combat, const Metrics& m)
{
    const auto& r = combat.Result();
    out << r.ticks << ',' << r.timeout << ',' << r.winner << ',' << r.survivors[0] << ',' << r.survivors[1] << ','
        << m.damage << ',' << m.healing << ',' << m.overheal << ',' << m.prevented << ',' << m.firstAction << ',' << m.firstDeath
        << ',' << m.deaths << ',' << m.crags << ',' << m.chargeSources << ',' << m.chargeLandings << ',' << m.chargeDamage
        << ',' << m.roots[0] << ',' << m.roots[1] << ',' << m.duplicateMax[0] << ',' << m.duplicateMax[1]
        << ',' << m.survivorInvestment[0] << ',' << m.survivorInvestment[1];
}
struct Fixture
{
    std::string id, variable;
    std::array<std::vector<wc::OwnedUnit>, 2> a;
    std::vector<wc::OwnedUnit> opponent;
};
void Fixtures(const wc::Catalog& catalog, const std::string& variant)
{
    const int bell = Definition(catalog, "wc_vn_shieldbearer"), crag = Definition(catalog, "wc_vn_boar_rusher"),
        root = Definition(catalog, "wc_vn_grove_druid"), snap = Definition(catalog, "wc_vn_hookjaw");
    std::vector<Fixture> fixtures;
    Fixture approach;
    approach.id = "charge_approach"; approach.variable = "crag_row_3_vs_0";
    approach.a[0] = {Unit(1, crag, 3, 3), Unit(2, bell, 1, 3), Unit(3, root, 1, 2)};
    approach.a[1] = approach.a[0]; approach.a[1][0].cell.row = 0;
    approach.opponent = {Unit(4, bell, 4, 3), Unit(5, crag, 6, 3), Unit(6, root, 6, 2)};
    fixtures.push_back(approach);
    Fixture screen = approach;
    screen.id = "charge_own_screen"; screen.variable = "bell_column_1_vs_3";
    screen.a[0][0].cell.row = 0; screen.a[1] = screen.a[0]; screen.a[1][1].cell.column = 3;
    fixtures.push_back(screen);
    Fixture grove;
    grove.id = "grove_cluster"; grove.variable = "root_column_3_vs_0";
    grove.a[0] = {Unit(1, bell, 3, 3), Unit(2, root, 3, 2), Unit(3, crag, 4, 3)};
    grove.a[1] = grove.a[0]; grove.a[1][1].cell.column = 0;
    grove.opponent = {Unit(4, bell, 3, 3), Unit(5, root, 3, 2), Unit(6, crag, 4, 3)};
    fixtures.push_back(grove);
    Fixture pressure = grove;
    pressure.id = "grove_screened_pressure"; pressure.variable = "root_column_3_vs_0";
    pressure.a[0].push_back(Unit(7, snap, 5, 2)); pressure.a[1].push_back(Unit(7, snap, 5, 2));
    pressure.opponent.push_back(Unit(8, snap, 5, 2));
    fixtures.push_back(pressure);
    std::ofstream out("fixtures.csv"), inputs("fixture_inputs.csv"), actions("fixture_charge_actions.csv");
    out << "variant,fixture,formation,mirrored,star,seed,declared_variable,investment_a,investment_b,";
    MetricHeader(out); out << ",charge_commitments,charge_released_actions,charge_unresolved_commitments\n";
    inputs << "fixture,formation,mirrored,star,side,id,hero,column,row,facing,relic,represented_copies\n";
    actions << "variant,fixture,formation,mirrored,star,seed,source,action,commit_tick,release_tick,origin_column,origin_row,aim_column,aim_row,momentum_steps,outcome\n";
    for (const auto& fixture : fixtures) for (int formation = 0; formation < 2; ++formation)
        for (int mirrored = 0; mirrored < 2; ++mirrored) for (int star : {1, 2, 3})
    {
        auto a = fixture.a[formation], b = fixture.opponent;
        for (auto& unit : a) unit.star = star;
        for (auto& unit : b) unit.star = star;
        if (mirrored) a.swap(b);
        int investment[2]{};
        for (int side = 0; side < 2; ++side) for (const auto& unit : (side ? b : a))
        {
            investment[side] += catalog.units[unit.definition].cost * Copies(unit.star);
            inputs << fixture.id << ',' << formation << ',' << mirrored << ',' << star << ',' << side << ',' << unit.id
                << ',' << catalog.units[unit.definition].id << ',' << unit.cell.column << ',' << unit.cell.row << ','
                << int(unit.facing) << ',' << unit.relic << ',' << Copies(unit.star) << '\n';
        }
        Require(investment[0] == investment[1], "Equal army investment fixture");
        for (int seed : {19, 41, 97, 251})
        {
            wc::Combat combat(catalog, a, b, seed), replay(catalog, a, b, seed);
            struct Commit { wc::CombatUnit unit; int tick = 0; };
            std::map<wc::Id, Commit> commitments;
            while (!combat.Result().complete)
            {
                combat.Tick(); replay.Tick();
                Require(combat.InvariantError().empty(), "Fixture occupancy/state invariant");
                for (const auto& unit : combat.Units())
                    if (unit.ability.mechanic == wc::AbilityMechanic::MomentumCharge && unit.state == wc::ActionState::CastWindup)
                        commitments.try_emplace(unit.actionId, Commit{unit, combat.CurrentTick()});
            }
            const auto measured = Measure(catalog, combat);
            Require(replay.Events().size() == combat.Events().size() && replay.Result().ticks == combat.Result().ticks &&
                replay.Result().winner == combat.Result().winner, "Fixture exact replay outcome");
            for (std::size_t i = 0; i < combat.Events().size(); ++i)
            {
                const auto& x = combat.Events()[i]; const auto& y = replay.Events()[i];
                Require(std::tie(x.tick,x.source,x.target,x.action,x.effect,x.requested,x.resolved,x.absorbed,x.healthLoss,x.overkill,
                    x.cell.column,x.cell.row,x.origin.column,x.origin.row,x.mechanic,x.guardedBy,x.prevented) ==
                    std::tie(y.tick,y.source,y.target,y.action,y.effect,y.requested,y.resolved,y.absorbed,y.healthLoss,y.overkill,
                    y.cell.column,y.cell.row,y.origin.column,y.origin.row,y.mechanic,y.guardedBy,y.prevented), "Fixture event replay");
            }
            std::set<wc::Id> released;
            for (const auto& event : combat.Events())
                if (event.mechanic == wc::AbilityMechanic::MomentumCharge &&
                    (event.effect == wc::Effect::Damage || event.effect == wc::Effect::Dash)) released.insert(event.action);
            for (const auto& entry : commitments)
            {
                const auto& c = entry.second;
                actions << variant << ',' << fixture.id << ',' << formation << ',' << mirrored << ',' << star << ',' << seed << ','
                    << c.unit.id << ',' << entry.first << ',' << c.tick << ',' << c.unit.releaseTick << ',' << c.unit.cell.column
                    << ',' << c.unit.cell.row << ',' << c.unit.abilityAim.column << ',' << c.unit.abilityAim.row << ','
                    << c.unit.momentumSteps << ',' << (released.count(entry.first) ? "resolved_charge_event" : "no_resolved_charge_event_reason_uninstrumented") << '\n';
            }
            out << variant << ',' << fixture.id << ',' << formation << ',' << mirrored << ',' << star << ',' << seed << ','
                << fixture.variable << ',' << investment[0] << ',' << investment[1] << ',';
            WriteMetrics(out, combat, measured);
            out << ',' << commitments.size() << ',' << released.size() << ',' << commitments.size() - released.size() << '\n';
        }
    }
}
struct Recruitment
{
    wc::Int offers = 0, affordableOffers = 0, legalOffers = 0, purchases = 0, deployedUnits = 0, deployedCopies = 0;
};
void ActivityHeader(std::ostream& out)
{
    out << "variant,seed,round,index,kind,unit_id,hero,side,star,alive,casts,first_cast_tick,mana_from_attacks,mana_from_damage,mana_spent,mana_remaining,mana_on_death,blocked_ready_decisions\n";
}
void WriteActivity(std::ostream& out,const wc::Catalog& catalog,const wc::Combat& combat,
                   const std::string& variant,int seed,int round,int index,const std::string& kind)
{
    for(const auto& u:combat.Units())if(!u.neutral)
        out << variant << ',' << seed << ',' << round << ',' << index << ',' << kind << ',' << u.id << ','
            << catalog.units[u.definition].id << ',' << u.side << ',' << u.star << ',' << (u.health>0) << ','
            << u.castsCommitted << ',' << u.firstCastTick << ',' << u.manaFromAttacks << ',' << u.manaFromDamage << ','
            << u.manaSpent << ',' << u.mana << ',' << u.manaOnDeath << ',' << u.manaBlockedAttempts << '\n';
}
void ManaFixtures(const wc::Catalog& catalog,const std::string& variant)
{
    std::ofstream out("mana_formations.csv"),activity("mana_formation_activity.csv");
    out << "variant,hero,layout,star,mirror,seed,";MetricHeader(out);out << '\n';ActivityHeader(activity);
    int index=0;
    for(int hero=3;hero<6;++hero)for(int exposed=0;exposed<2;++exposed)for(int star=1;star<=3;++star)
        for(int mirror=0;mirror<2;++mirror)for(int seed=1001;seed<=1016;++seed)
    {
        std::vector<wc::OwnedUnit> a{Unit(1,hero,3,exposed?3:1,star),Unit(2,0,3,exposed?1:2),Unit(3,1,4,3)};
        std::vector<wc::OwnedUnit> b{Unit(4,0,4,3),Unit(5,2,4,1,star),Unit(6,1,3,3)};
        if(mirror)std::swap(a,b);
        wc::Combat fight(catalog,a,b,seed),replay(catalog,a,b,seed);
        while(!fight.Result().complete){fight.Tick();replay.Tick();Require(fight.InvariantError().empty(),"Mana formation invariant");}
        VerifyDiagnosticReplay(replay,fight);
        for(std::size_t i=0;i<fight.Units().size();++i)
        {
            const auto& x=fight.Units()[i];const auto& y=replay.Units()[i];
            Require(std::tie(x.mana,x.manaSpent,x.manaFromAttacks,x.manaFromDamage,x.castsCommitted,x.firstCastTick,x.manaOnDeath)==
                    std::tie(y.mana,y.manaSpent,y.manaFromAttacks,y.manaFromDamage,y.castsCommitted,y.firstCastTick,y.manaOnDeath),"Mana activity replay parity");
        }
        out << variant << ',' << catalog.units[hero].id << ',' << (exposed?"exposed":"protected") << ',' << star << ',' << mirror << ',' << seed << ',';
        WriteMetrics(out,fight,Measure(catalog,fight));out << '\n';
        WriteActivity(activity,catalog,fight,variant,seed,0,index++,exposed?"exposed":"protected");
    }
}

void Tournaments(const wc::Catalog& catalog, const std::string& variant, int count, int firstSeed, bool diagnostics)
{
    std::ofstream encounters("encounters.csv"), tournaments("tournaments.csv"), recruitment("recruitment.csv"), activity("ability_activity.csv");
    ActivityHeader(activity);
    std::ofstream traces, seatRounds, levels;
    if (diagnostics)
    {
        traces.open("mechanic_outcomes.csv");
        traces << "variant,seed,round,index,kind,hero,phase,reason,count,recipients,full_health_ally_pulses,requested_cp,resolved_cp\n";
        seatRounds.open("seat_rounds.csv");
        seatRounds << "variant,seed,round,pvp_round,kind,seat,level,health_before,health_after,damage,gold,deployed_units,roots,crags,snaps,prisms,reefs\n";
        levels.open("recruitment_by_level.csv");
        levels << "variant,seed,level,hero,new_offer_slots,affordable_at_first_observed_offer,legal_buy_at_first_observed_offer,purchased_copies,deployed_unit_rounds,deployed_represented_copy_rounds\n";
    }
    encounters << "variant,seed,round,index,kind,"; MetricHeader(encounters); encounters << '\n';
    tournaments << "variant,seed,rounds,capped,simulated_ms,preparation_ms,combat_ms,settlement_ms,encounters,timeouts,command_rejects\n";
    recruitment << "variant,seed,hero,new_offer_slots,affordable_at_first_observed_offer,legal_buy_at_first_observed_offer,purchased_copies,deployed_unit_rounds,deployed_represented_copy_rounds\n";
    for (int seed = firstSeed; seed < firstSeed + count; ++seed)
    {
        wc::Match match(catalog, seed, 0);
        std::vector<Recruitment> usage(catalog.units.size());
        std::map<std::pair<int, int>, Recruitment> levelUsage;
        std::vector<wc::Combat> diagnosticCombats;
        std::array<int, 8> startingHealth{};
        struct Shop { wc::Id rng = 0; std::vector<int> offers; };
        std::array<Shop, 8> shops;
        auto observe = [&]() {
            for (const auto& seat : match.Seats())
            {
                if (seat.health <= 0) continue;
                auto& previous = shops[seat.id];
                const bool fresh = previous.rng != seat.shopRng.state;
                for (int slot = 0; slot < int(seat.shop.size()); ++slot)
                {
                    const int definition = seat.shop[slot];
                    if (fresh && definition >= 0)
                    {
                        auto& u = usage[definition]; auto& byLevel = levelUsage[{seat.level, definition}];
                        ++u.offers; ++byLevel.offers;
                        if (seat.gold >= catalog.units[definition].cost) { ++u.affordableOffers; ++byLevel.affordableOffers; }
                        wc::Command command; command.type = wc::CommandType::Buy; command.slot = slot;
                        if (wc::PreviewRosterCommand(catalog, seat, command).accepted) { ++u.legalOffers; ++byLevel.legalOffers; }
                    }
                    else if (!fresh && definition < 0 && slot < int(previous.offers.size()) && previous.offers[slot] >= 0)
                    { ++usage[previous.offers[slot]].purchases; ++levelUsage[{seat.level, previous.offers[slot]}].purchases; }
                }
                previous = {seat.shopRng.state, seat.shop};
            }
        };
        observe();
        std::array<int, 3> phaseMs{};
        int fights = 0, timeouts = 0, ticks = 0;
        while (match.CurrentPhase() != wc::Phase::Finished && match.CurrentPhase() != wc::Phase::Aborted)
        {
            const auto before = match.CurrentPhase(); const int elapsed = match.ElapsedMs();
            match.Tick(catalog.rules.tickMs); ++ticks;
            phaseMs[int(before)] += match.ElapsedMs() - elapsed;
            if (before == wc::Phase::Preparation || match.CurrentPhase() == wc::Phase::Preparation) observe();
            if (ticks % 20 == 0 || match.CurrentPhase() != before)
                Require(match.InvariantError().empty(), "Tournament invariant seed " + std::to_string(seed));
            if (before == wc::Phase::Preparation && match.CurrentPhase() == wc::Phase::Combat)
            {
                if (diagnostics)
                {
                    diagnosticCombats.clear();
                    for (const auto& encounter : match.Encounters())
                    {
                        diagnosticCombats.push_back(encounter.combat);
                        Require(diagnosticCombats.back().EnableDiagnostics(), "Encounter copy begins before first combat tick");
                    }
                }
                for (const auto& seat : match.Seats()) startingHealth[seat.id] = seat.health;
                for (const auto& seat : match.Seats()) if (seat.health > 0)
                    for (const auto& unit : seat.roster) if (unit.onBoard)
                    {
                        ++usage[unit.definition].deployedUnits; usage[unit.definition].deployedCopies += Copies(unit.star);
                        auto& byLevel = levelUsage[{seat.level, unit.definition}];
                        ++byLevel.deployedUnits; byLevel.deployedCopies += Copies(unit.star);
                    }
            }
            if (before != wc::Phase::Combat || match.CurrentPhase() == wc::Phase::Combat) continue;
            for (int index = 0; index < int(match.Encounters().size()); ++index)
            {
                const auto& encounter = match.Encounters()[index];
                if (diagnostics)
                {
                    auto& copy = diagnosticCombats.at(index);
                    while (!copy.Result().complete) copy.Tick();
                    VerifyDiagnosticReplay(copy, encounter.combat);
                    WriteTraces(traces, catalog, copy, variant, seed, match.Round(), index,
                        encounter.kind == wc::EncounterKind::Pvp ? "pvp" : encounter.kind == wc::EncounterKind::Ghost ? "ghost" : "neutral");
                }
                Require(encounter.combat.InvariantError().empty(), "Completed encounter invariant");
                const auto metrics = Measure(catalog, encounter.combat);
                encounters << variant << ',' << seed << ',' << match.Round() << ',' << index << ','
                    << (encounter.kind == wc::EncounterKind::Pvp ? "pvp" : encounter.kind == wc::EncounterKind::Ghost ? "ghost" : "neutral") << ',';
                WriteMetrics(encounters, encounter.combat, metrics); encounters << '\n';
                WriteActivity(activity,catalog,encounter.combat,variant,seed,match.Round(),index,
                    encounter.kind==wc::EncounterKind::Pvp?"pvp":encounter.kind==wc::EncounterKind::Ghost?"ghost":"neutral");
                ++fights; if (encounter.combat.Result().timeout) ++timeouts;
            }
            if (diagnostics)
            {
                const auto& record = match.Records().back();
                for (const auto& seat : match.Seats()) if (startingHealth[seat.id] > 0)
                {
                    std::array<int, 6> composition{}; int deployed = 0;
                    for (const auto& unit : seat.roster) if (unit.onBoard) { ++deployed; ++composition.at(unit.definition); }
                    Require(seat.health == std::max(0, startingHealth[seat.id] - record.damage[seat.id]), "Seat damage reconciles with settlement");
                    seatRounds << variant << ',' << seed << ',' << match.Round() << ',' << record.pvpRoundIndex << ','
                        << (record.neutral ? "neutral" : "pvp_or_ghost") << ',' << seat.id << ',' << seat.level << ','
                        << startingHealth[seat.id] << ',' << seat.health << ',' << record.damage[seat.id] << ',' << seat.gold
                        << ',' << deployed << ',' << composition[2] << ',' << composition[1] << ',' << composition[3]
                        << ',' << composition[4] << ',' << composition[5] << '\n';
                }
            }
        }
        Require(match.CurrentPhase() == wc::Phase::Finished, "Tournament finished");
        Require(phaseMs[0] + phaseMs[1] + phaseMs[2] == match.ElapsedMs(), "Phase time reconciliation");
        int rejects = 0, buys = 0;
        for (const auto& decision : match.BotLog())
        { if (!decision.reply.accepted) ++rejects; else if (decision.action == "buy") ++buys; }
        wc::Int observedBuys = 0;
        for (int i = 0; i < int(usage.size()); ++i)
        {
            const auto& u = usage[i]; observedBuys += u.purchases;
            recruitment << variant << ',' << seed << ',' << catalog.units[i].id << ',' << u.offers << ',' << u.affordableOffers
                << ',' << u.legalOffers << ',' << u.purchases << ',' << u.deployedUnits << ',' << u.deployedCopies << '\n';
        }
        Require(observedBuys == buys, "Shop transition purchases reconcile with authoritative bot buy replies");
        if (diagnostics) for (const auto& entry : levelUsage)
        {
            const auto& u = entry.second;
            levels << variant << ',' << seed << ',' << entry.first.first << ',' << catalog.units[entry.first.second].id
                << ',' << u.offers << ',' << u.affordableOffers << ',' << u.legalOffers << ',' << u.purchases
                << ',' << u.deployedUnits << ',' << u.deployedCopies << '\n';
        }
        Require(rejects == 0, "No bot command rejection");
        tournaments << variant << ',' << seed << ',' << match.Round() << ',' << match.Capped() << ',' << match.ElapsedMs()
            << ',' << phaseMs[0] << ',' << phaseMs[1] << ',' << phaseMs[2] << ',' << fights << ',' << timeouts << ',' << rejects << '\n';
        encounters.flush(); tournaments.flush(); recruitment.flush();
        if ((seed - firstSeed + 1) % 25 == 0 || count < 25)
            std::cout << "Completed " << variant << " seed " << seed << " (" << seed - firstSeed + 1 << '/' << count << ")\n";
    }
}
}
int main(int argc, char** argv)
{
    try
    {
        const std::string variant = argc > 1 ? argv[1] : "control";
        const int count = argc > 2 ? std::stoi(argv[2]) : 10, firstSeed = argc > 3 ? std::stoi(argv[3]) : 1;
        const bool diagnostics = argc > 4 && std::string(argv[4]) == "diagnostics";
        Require(variant == "control" || variant == "root75" || variant == "mana100" || variant == "mana20" || variant == "targeting" || variant == "clarity" || variant == "roster", "Variant must be control, root75, mana100, mana20 or roster");
        Require(count >= 0 && count <= 1000 && firstSeed >= 1 && firstSeed <= 1000000 - count, "Bounded seed interval");
        auto catalog = wcvnext::WonderVNextCatalog();
        Require(catalog.Validate().empty(), "Canonical catalog validation");
        if (variant == "root75")
        {
            auto& ability = catalog.units[Definition(catalog, "wc_vn_grove_druid")].ability;
            Require(ability.mechanic == wc::AbilityMechanic::StationaryGrove, "Root mechanic identity");
            for (auto& magnitude : ability.magnitude) magnitude = wc::HalfUp(magnitude * 7500, 10000);
        }
        if (variant == "mana100") catalog = wcvnext::WonderVNextManaCatalog();
        if (variant == "mana20") catalog = wcvnext::WonderVNextMana20Catalog();
        if (variant == "roster") catalog = wcvnext::WonderVNextRosterCatalog();
        if (variant == "targeting" || variant == "clarity") catalog = wcvnext::WonderVNextCombatClarityCatalog(variant == "clarity");
        Require(catalog.Validate().empty(), "Experimental catalog validation");
        std::ofstream identity("variant.json");
        identity << "{\"variant\":\"" << variant << "\",\"origin_catalog_digest\":\"" << catalog.contentDigest
            << "\",\"first_seed\":" << firstSeed << ",\"tournaments\":" << count
            << ",\"recipe\":\"" << (variant == "root75" ? "Root base pulse magnitudes HalfUp(value*7500/10000) only" : variant == "mana100" ? "Canonical opt-in mana100_v1 recipe; three heroes only" : variant == "mana20" ? "Canonical mana100_hit20_v1 recipe; basic-hit gain20 only" : variant == "roster" ? "Canonical roster_v1 recipe; four mana casters and seven stat traits" : "Unmodified canonical control")
            << "\",\"boundary\":\"In-memory experiment; no canonical tuning or human acceptance\"}\n";
        Fixtures(catalog, variant);
        if(variant!="root75") ManaFixtures(catalog,variant);
        Tournaments(catalog, variant, count, firstSeed, diagnostics);
        std::cout << "PASS " << variant << ": fixed-army mirrored replay fixtures and " << count
            << " native tournaments. Numeric balance screen evaluated separately; no tuning promotion.\n";
    }
    catch (const std::exception& error) { std::cerr << "FAIL " << error.what() << '\n'; return 1; }
}
