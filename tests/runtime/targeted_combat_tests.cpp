#include "CatalogFixture.h"
#include <algorithm>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <tuple>

namespace {
int assertions = 0, failures = 0, cases = 0, executions = 0;
std::string activeCase;
std::ofstream checks("edge-cases.csv"), events("edge-events.csv"), positions("edge-positions.csv");
void Check(bool condition, const char* message) {
    ++assertions;
    if (!condition) throw std::runtime_error(message);
}
wc::OwnedUnit Unit(wc::Id id, int definition, int x, int y, int star = 1) {
    wc::OwnedUnit u; u.id = id; u.definition = definition; u.cell = {x, y}; u.star = star; u.onBoard = true; return u;
}
const wc::CombatUnit& Find(const wc::Combat& combat, wc::Id localId) {
    for (const auto& u : combat.Units()) if ((u.id & ((wc::Id(1) << 20) - 1)) == localId) return u;
    throw std::runtime_error("Missing fixture unit");
}
void Capture(const wc::Combat& combat) {
    for (const auto& u : combat.Units()) positions << activeCase << ',' << combat.CurrentTick() << ',' << u.id << ','
        << u.cell.column << ',' << u.cell.row << ',' << u.destination.column << ',' << u.destination.row << ','
        << int(u.state) << ',' << u.health << ',' << u.shield << ',' << u.shieldExpiry << ',' << u.stunExpiry << '\n';
}
void Step(wc::Combat& combat, int count) {
    for (int i = 0; i < count; ++i) { combat.Tick(); Check(combat.InvariantError().empty(), "Per-tick invariant"); Capture(combat); }
}
void Events(const wc::Combat& combat) {
    for (const auto& e : combat.Events()) events << activeCase << ',' << e.tick << ',' << e.source << ',' << e.target << ','
        << int(e.effect) << ',' << e.basicAttack << ',' << e.requested << ',' << e.resolved << ',' << e.absorbed << ','
        << e.healthLoss << ',' << e.overkill << ',' << e.absorbedFrom << '\n';
}
void Case(const char* name, const std::function<void()>& run) {
    activeCase = name; ++cases; const int before = assertions;
    try { run(); checks << name << ",PASS," << assertions - before << ",\n"; }
    catch (const std::exception& e) { ++failures; checks << name << ",FAIL," << assertions - before << ',' << e.what() << '\n'; std::cerr << name << ": " << e.what() << '\n'; }
}
wc::Catalog Controlled(const wc::Catalog& canonical) {
    auto c = canonical; c.traits.clear();
    for (auto& u : c.units) {
        u.health = 100000; u.attackDamage = 0; u.armor = u.resistance = 0; u.range = 8;
        u.attackRate = 250; u.attackWindupMs = 50; u.projectileTravelMs = 0; u.movementRate = 1000;
        u.ability.firstCastMs = 100000;
    }
    return c;
}
void Ability(wc::UnitDef& unit, wc::Effect effect, wc::Selector selector, wc::Int magnitude, int duration = 1000) {
    auto& a = unit.ability;
    a.effects.clear();
    a.effect = effect; a.selector = selector; a.magnitude = {magnitude, magnitude, magnitude};
    a.firstCastMs = 0; a.castMs = 50; a.cooldownMs = 100000; a.recoveryMs = 50;
    a.durationMs = duration; a.travelMs = 0; a.radius = 1; a.range = 8; a.maxTargets = 12; a.allowSelf = false;
    a.maxDash = 8;
}
void Shield(const wc::Catalog& canonical, wc::Int incoming, int duration, wc::Int expected, int expiry, bool replaces) {
    auto c = Controlled(canonical);
    Ability(c.units[0], wc::Effect::Shield, wc::Selector::Self, 3000);
    Ability(c.units[1], wc::Effect::Shield, wc::Selector::AdjacentAllies, incoming, duration);
    c.units[1].ability.travelMs = 100;
    Check(c.Validate().empty(), "Controlled catalog remains numerically valid");
    wc::Combat combat(c, {Unit(1, 0, 3, 3), Unit(2, 1, 2, 3)}, {Unit(3, 2, 0, 0)}, 91); ++executions;
    Step(combat, 2);
    Check(Find(combat, 1).shield == 3000 && Find(combat, 1).shieldExpiry == 22, "Initial pool and expiry");
    Step(combat, 2); Events(combat);
    const auto& target = Find(combat, 1);
    Check(target.shield == expected && target.shieldExpiry == expiry, "Replacement amount and exact expiry");
    Check(target.shieldSource == (replaces ? 2 : 1), "Current shield attribution");
    bool delivered = false;
    for (const auto& e : combat.Events()) if (e.tick == 4 && e.source == 2 && e.target == 1 && e.effect == wc::Effect::Shield) {
        delivered = true; Check(e.requested == incoming && e.resolved == (replaces ? incoming : 0), "Delayed shield packet resolved truthfully");
    }
    Check(delivered, "Second shield actually arrived after existing pool");
}
void DamageOverflow(const wc::Catalog& canonical, wc::DamageType type, wc::Int raw, int armor,
                    wc::Int hp, wc::Int shield, wc::Int resolved, wc::Int loss, wc::Int overkill) {
    auto c = Controlled(canonical); c.units[0].health = hp; c.units[0].armor = armor;
    Ability(c.units[0], wc::Effect::Shield, wc::Selector::Self, shield);
    c.units[1].attackDamage = raw; c.units[1].damageType = type; c.units[1].attackWindupMs = 150;
    wc::Combat combat(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 14); ++executions;
    Step(combat, 4); Events(combat); bool delivered = false;
    for (const auto& e : combat.Events()) if (e.target == 1 && e.effect == wc::Effect::Damage) {
        delivered = true;
        Check(e.resolved == resolved && e.absorbed == shield && e.healthLoss == loss && e.overkill == overkill,
              "Damage separates mitigation absorption HP loss and overkill");
        Check(e.absorbedFrom == 1, "Shield absorption credited to shield caster");
    }
    Check(delivered && Find(combat, 1).health == hp - loss && Find(combat, 1).shield == 0, "Overflow applied exactly once");
}
void HealCap(const wc::Catalog& canonical, bool lethal) {
    auto c = Controlled(canonical); c.units[0].health = 10000;
    Ability(c.units[1], wc::Effect::Heal, wc::Selector::AdjacentAllies, 10000);
    c.units[1].attackRate = 2500; c.units[1].ability.travelMs = 100;
    c.units[2].attackDamage = lethal ? 20000 : 5000; c.units[2].range = 1;
    // Enemy is adjacent only to the wounded ally; healer is one tile behind.
    wc::Combat combat(c, {Unit(1, 0, 3, 3), Unit(2, 1, 3, 2)}, {Unit(3, 2, 4, 3)}, 11); ++executions;
    Step(combat, 13); Events(combat); bool healed = false;
    for (const auto& e : combat.Events()) if (e.effect == wc::Effect::Heal && e.target == 1) {
        healed = true; Check(!lethal && e.requested == 10000 && e.resolved == 5000, "Only effective healing is recorded");
    }
    Check(lethal ? !healed && Find(combat, 1).health == 0 : healed && Find(combat, 1).health == 10000,
          "Heal caps at max HP and never revives a defeated target");
}
void Corner(const wc::Catalog& canonical, bool horizontal) {
    auto c = Controlled(canonical); c.units[0].range = 1;
    wc::Cell origin{3, horizontal ? 3 : 2}, forbidden{4, horizontal ? 4 : 3};
    auto blocker = horizontal ? Unit(2, 1, 4, 3) : Unit(2, 1, 3, 3);
    wc::Combat combat(c, {Unit(1, 0, origin.column, origin.row), blocker}, {Unit(3, 2, 2, horizontal ? 2 : 3)}, 8); ++executions;
    Step(combat, 1);
    const auto& mover = Find(combat, 1);
    Check(mover.state == wc::ActionState::Moving && mover.cell == origin, "Origin occupied throughout movement");
    Check(!(mover.destination == forbidden), "Either orthogonal blocker independently forbids corner cutting");
    Check(wc::Distance(mover.destination, Find(combat, 3).cell) > 1, "Blocked one-step diagonal requires a detour");
    Step(combat, 20); Events(combat);
}
void ReservedCorner(const wc::Catalog& canonical) {
    auto c = Controlled(canonical); c.units[0].range = c.units[1].range = 1;
    bool exercised = false;
    for (int seed = 1; seed <= 32 && !exercised; ++seed) {
        wc::Combat combat(c, {Unit(1, 0, 3, 2), Unit(2, 1, 5, 1)}, {Unit(3, 2, 2, 3)}, seed); ++executions;
        Step(combat, 1); const auto& a = Find(combat, 1); const auto& b = Find(combat, 2);
        if (b.initiative < a.initiative && b.destination == wc::Cell{4, 2}) {
            exercised = true;
            Check(!(a.destination == wc::Cell{4, 3}), "Reserved orthogonal cell blocks diagonal even when physically empty");
            Check(!(a.destination == b.destination), "First reservation wins destination contention");
            Check(a.cell == wc::Cell{3, 2} && b.cell == wc::Cell{5, 1}, "Both origins retained while destinations reserved");
            Step(combat, 20); Events(combat);
        }
    }
    Check(exercised, "Deterministic bounded seed set actually exercises reserved corner");
}
void CancelMove(const wc::Catalog& canonical, bool defeat, bool dash) {
    auto c = Controlled(canonical); c.units[0].range = 1;
    if (dash) { Ability(c.units[0], wc::Effect::Dash, wc::Selector::FarthestEnemyAdjacent, 0); c.units[0].ability.castMs = 150; }
    if (defeat) { c.units[1].attackDamage = 200000; c.units[1].attackWindupMs = 100; }
    else { Ability(c.units[1], wc::Effect::Stun, wc::Selector::CurrentEnemy, 0); c.units[1].ability.castMs = 100; }
    wc::Combat combat(c, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 0, 0)}, 21); ++executions;
    Step(combat, 1); Check(Find(combat, 1).destination.column >= 0, "Movement or dash reservation committed");
    Step(combat, 2); Events(combat);
    const auto& target = Find(combat, 1);
    Check(target.destination.column == -1 && target.movementTick == 0 && target.cell == wc::Cell{3, 3},
          "Interrupt releases reservation and preserves occupied origin");
    Check(target.state == (defeat ? wc::ActionState::Defeated : wc::ActionState::Stunned), "Interrupt actually reached target");
    if (dash) {
        Step(combat, 4); Events(combat);
        Check(Find(combat, 1).cooldownTick > combat.CurrentTick(), "Canceled dash retains committed cooldown");
        for (const auto& e : combat.Events()) Check(e.effect != wc::Effect::Dash, "Canceled dash never materializes");
    }
}
void NoPath(const wc::Catalog& canonical) {
    auto c = Controlled(canonical); c.units[0].range = 1;
    wc::Combat combat(c, {Unit(1, 0, 0, 0), Unit(2, 1, 1, 0), Unit(3, 1, 0, 1)}, {Unit(4, 2, 0, 0)}, 5); ++executions;
    Step(combat, 8); Events(combat);
    Check(Find(combat, 1).cell == wc::Cell{0, 0} && Find(combat, 1).destination.column == -1,
          "Enclosed corner neither teleports nor leaks reservations");
}
void DashNoDamage(const wc::Catalog& canonical) {
    auto c = Controlled(canonical); Ability(c.units[0], wc::Effect::Dash, wc::Selector::FarthestEnemyAdjacent, 0);
    wc::Combat combat(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 5); ++executions;
    Step(combat, 2); Events(combat); bool dash = false;
    for (const auto& e : combat.Events()) if (e.effect == wc::Effect::Dash) {
        dash = true; Check(!e.basicAttack && e.requested == 0 && e.resolved == 0 && e.healthLoss == 0 && e.absorbed == 0,
                           "Dash contains no implicit damage or shield absorption");
    }
    Check(dash && !(Find(combat, 1).cell == wc::Cell{0, 0}), "Legal dash actually changed cell");
    Check(Find(combat, 1).destination.column == -1 && Find(combat, 2).health == Find(combat, 2).maxHealth,
          "Successful dash releases reservation without damaging target");
}
void StunRefresh(const wc::Catalog& canonical, int secondDuration, int expected) {
    auto c = Controlled(canonical);
    Ability(c.units[1], wc::Effect::Stun, wc::Selector::CurrentEnemy, 0, 1000);
    Ability(c.units[2], wc::Effect::Stun, wc::Selector::CurrentEnemy, 0, secondDuration); c.units[2].ability.travelMs = 100;
    wc::Combat combat(c, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3), Unit(3, 2, 4, 3)}, 6); ++executions;
    Step(combat, 2); Check(Find(combat, 1).stunExpiry == 22, "Initial stun expiry");
    Step(combat, 2); Events(combat); Check(Find(combat, 1).stunExpiry == expected, "Stun refresh uses maximum expiry not duration sum");
}

struct Formation { const char* name; std::vector<std::pair<int, wc::Cell>> units; };
std::vector<Formation> Formations() {
    return {
        {"shield_heavy", {{0,{2,3}},{0,{4,3}},{6,{3,3}},{10,{4,1}},{5,{6,2}},{1,{3,2}}}},
        {"sustain", {{6,{3,3}},{10,{4,1}},{7,{6,0}},{1,{2,2}},{1,{4,2}},{4,{3,2}}}},
        {"spread_ranged", {{0,{2,3}},{6,{5,3}},{3,{0,0}},{7,{7,0}},{2,{2,1}},{10,{5,1}}}},
        {"paired_mage", {{0,{2,3}},{6,{3,3}},{8,{4,3}},{2,{2,1}},{10,{4,1}},{1,{3,2}}}},
        {"rogue_pressure", {{0,{2,3}},{8,{3,3}},{9,{4,3}},{5,{0,2}},{11,{7,2}},{3,{5,0}}}}
    };
}
std::vector<wc::OwnedUnit> Roster(const Formation& f, int star, wc::Id base) {
    std::vector<wc::OwnedUnit> roster;
    for (const auto& entry : f.units) roster.push_back(Unit(++base, entry.first, entry.second.column, entry.second.row, star));
    return roster;
}
std::string Signature(const wc::Combat& combat) {
    std::string out = std::to_string(combat.Result().winner) + ":" + std::to_string(combat.Result().ticks);
    for (const auto& u : combat.Units()) out += ":" + std::to_string(u.id) + "/" + std::to_string(u.health) + "/" + std::to_string(u.shield) + "/" + std::to_string(u.cell.column) + "/" + std::to_string(u.cell.row);
    for (const auto& e : combat.Events()) out += ":" + std::to_string(e.tick) + "/" + std::to_string(e.source) + "/" + std::to_string(e.target) + "/" + std::to_string(e.action) + "/" + std::to_string(int(e.effect)) + "/" + std::to_string(e.resolved) + "/" + std::to_string(e.absorbed) + "/" + std::to_string(e.healthLoss) + "/" + std::to_string(e.overkill);
    return out;
}
void Finish(wc::Combat& combat, bool observed) {
    while (!combat.Result().complete && combat.CurrentTick() < 801) {
        combat.Tick(); Check(combat.InvariantError().empty(), "Formation per-tick invariant");
        if (observed) { const auto inspected = Signature(combat); Check(!inspected.empty(), "Read-only observation available"); }
    }
    Check(combat.Result().complete && combat.Result().ticks <= 800, "Formation completes within canonical timeout");
}
void Matrix(const wc::Catalog& c) {
    const auto formations = Formations(); std::ofstream definitions("formations.csv"), rows("formation-combats.csv");
    definitions << "formation,unit_id,cost,column,row\n";
    rows << "formation_a,formation_b,star,investment_per_side,seed,swapped,winner,ticks,timeout,survivors_a,survivors_b,events,observed_replay_exact\n";
    for (const auto& f : formations) { int cost = 0; std::map<int,int> copies; for (const auto& u : f.units) {
        Check(++copies[u.first] <= 2, "Same-star duplicates remain below automatic three-copy merge threshold");
        cost += c.units[u.first].cost; definitions << f.name << ',' << c.units[u.first].id << ',' << c.units[u.first].cost << ',' << u.second.column << ',' << u.second.row << '\n';
    } Check(cost == 10 && f.units.size() == 6, "Every canonical formation costs ten gold with six heroes"); }
    for (const auto& f : formations) {
        int shields = 0, heals = 0;
        for (const auto& u : f.units) {
            shields += c.units[u.first].ability.effect == wc::Effect::Shield;
            heals += c.units[u.first].ability.effect == wc::Effect::Heal;
        }
        if (std::string(f.name) == "shield_heavy") Check(shields >= 2, "Shield-heavy composition actually has multiple shield casters");
        if (std::string(f.name) == "sustain") Check(heals >= 2, "Sustain composition actually has multiple healers");
    }
    for (int a = 0; a < int(formations.size()); ++a) for (int b = a; b < int(formations.size()); ++b)
        for (int star = 1; star <= 3; ++star) for (int seed = 1; seed <= 8; ++seed) for (int swapped = 0; swapped < 2; ++swapped) {
            auto left = Roster(formations[swapped ? b : a], star, 0), right = Roster(formations[swapped ? a : b], star, 6);
            wc::Combat combat(c, left, right, seed), observed(c, left, right, seed); executions += 2;
            Finish(combat, false); Finish(observed, true);
            Check(Signature(combat) == Signature(observed), "Observed and unobserved final units and ordered event replay agree exactly");
            const auto& r = combat.Result();
            rows << formations[a].name << ',' << formations[b].name << ',' << star << ',' << 10 * (star == 1 ? 1 : star == 2 ? 3 : 9) << ','
                 << seed << ',' << swapped << ',' << r.winner << ',' << r.ticks << ',' << r.timeout << ',' << r.survivors[0] << ',' << r.survivors[1] << ',' << combat.Events().size() << ",1\n";
        }
}
}
int main() {
    checks << "case,status,assertions,error\n";
    events << "case,tick,source,target,effect,basic,requested,resolved,absorbed,health_loss,overkill,shield_source\n";
    positions << "case,tick,unit,x,y,dest_x,dest_y,state,health,shield,shield_expiry,stun_expiry\n";
    const auto c = FixtureCatalog();
    Case("canonical_catalog", [&] { Check(c.Validate().empty(), "Canonical catalog validates"); });
    Case("shield_stronger_replaces", [&] { Shield(c, 4000, 1000, 4000, 24, true); });
    Case("shield_equal_later_refreshes", [&] { Shield(c, 3000, 1000, 3000, 24, true); });
    Case("shield_weaker_changes_nothing", [&] { Shield(c, 2000, 2000, 3000, 22, false); });
    Case("shield_equal_earlier_changes_nothing", [&] { Shield(c, 3000, 500, 3000, 22, false); });
    Case("physical_shield_overflow", [&] { DamageOverflow(c, wc::DamageType::Physical, 12000, 50, 100000, 3000, 8000, 5000, 0); });
    Case("true_damage_shield_overkill", [&] { DamageOverflow(c, wc::DamageType::True, 5000, 50, 1000, 3000, 5000, 1000, 1000); });
    Case("heal_effective_cap", [&] { HealCap(c, false); });
    Case("heal_no_revive", [&] { HealCap(c, true); });
    Case("horizontal_orthogonal_corner", [&] { Corner(c, true); });
    Case("vertical_orthogonal_corner", [&] { Corner(c, false); });
    Case("reserved_orthogonal_corner", [&] { ReservedCorner(c); });
    Case("stun_cancels_step", [&] { CancelMove(c, false, false); });
    Case("defeat_cancels_step", [&] { CancelMove(c, true, false); });
    Case("stun_cancels_dash", [&] { CancelMove(c, false, true); });
    Case("enclosed_corner_no_path", [&] { NoPath(c); });
    Case("dash_has_no_secret_damage", [&] { DashNoDamage(c); });
    Case("stun_shorter_does_not_stack", [&] { StunRefresh(c, 500, 22); });
    Case("stun_longer_extends_maximum", [&] { StunRefresh(c, 2000, 44); });
    Case("canonical_equal_investment_matrix", [&] { Matrix(c); });
    std::ofstream summary("execution.json");
    summary << "{\"status\":\"" << (failures ? "FAIL" : "PASS") << "\",\"cases\":" << cases << ",\"failures\":" << failures
            << ",\"assertions\":" << assertions << ",\"combat_executions\":" << executions << ",\"compiler_msc_full_ver\":" << _MSC_FULL_VER
            << ",\"catalog_digest\":\"" << c.contentDigest << "\"}\n";
    std::cout << (failures ? "FAIL" : "PASS") << " cases=" << cases << " failed=" << failures << " assertions=" << assertions << " combats=" << executions << '\n';
    return failures ? 1 : 0;
}
