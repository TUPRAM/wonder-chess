#include "WonderVNextCatalog.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <tuple>

namespace
{
int assertions = 0;
void Check(bool condition, const char *message)
{
    ++assertions;
    if (!condition) throw std::runtime_error(message);
}
wc::OwnedUnit Unit(wc::Id id, int definition, int x, int y, wc::Facing facing = wc::Facing::Forward)
{
    wc::OwnedUnit unit;
    unit.id = id; unit.definition = definition; unit.onBoard = true; unit.cell = {x, y}; unit.facing = facing;
    return unit;
}
wc::Catalog Quiet()
{
    auto catalog = wcvnext::WonderVNextCatalog();
    catalog.traits.clear();
    for (auto &unit : catalog.units)
    {
        unit.health = 1000000; unit.attackDamage = 0; unit.armor = unit.resistance = 0;
        unit.range = 8; unit.attackRate = 250; unit.movementRate = 1000; unit.attackWindupMs = 50;
        unit.ability.enabled = false;
    }
    return catalog;
}
void Enable(wc::Catalog &catalog, int index)
{
    auto &ability = catalog.units[index].ability;
    ability.enabled = true; ability.firstCastMs = 0; ability.castMs = 50;
    ability.cooldownMs = 60000; ability.recoveryMs = 50;
}
void Ticks(wc::Combat &combat, int count)
{
    for (int i = 0; i < count && !combat.Result().complete; ++i)
    {
        combat.Tick();
        Check(combat.InvariantError().empty(), "Combat invariants hold after every tick");
    }
}
std::vector<wc::CombatEvent> Events(const wc::Combat &combat, wc::AbilityMechanic mechanic, wc::Effect effect)
{
    std::vector<wc::CombatEvent> result;
    for (const auto &event : combat.Events())
        if (event.mechanic == mechanic && event.effect == effect) result.push_back(event);
    return result;
}
void Contract()
{
    auto catalog = wcvnext::WonderVNextCatalog();
    const auto error = catalog.Validate();
    if (!error.empty()) throw std::runtime_error(error);
    Check(catalog.profileId == "wonder_vnext" && catalog.units.size() == 6, "Canonical six hero lab profile");
    for (int cost = 1; cost <= 5; ++cost)
        Check(std::any_of(catalog.units.begin(), catalog.units.end(), [&](const auto &u) { return u.cost == cost; }),
              "Every enabled recruitment cost has a source unit");
    auto wrong = catalog;
    wrong.profileId = "alpha_24";
    Check(!wrong.Validate().empty(), "Legacy contract cannot silently load successor roster");
    wrong = catalog;
    wrong.units[2].ability.pulseMs = 0;
    Check(!wrong.Validate().empty(), "Zero interval persistent effects are rejected");
    wrong = catalog;
    wrong.units[5].ability.displacementCells = 8;
    Check(!wrong.Validate().empty(), "Unbounded displacement rejected");
    wc::TraitDef trait;
    trait.tiers = {{2, 100}, {5, 350}, {8, 600}};
    Check(wc::TraitValue(trait, 1) == 0 && wc::TraitValue(trait, 4) == 100 &&
          wc::TraitValue(trait, 7) == 350 && wc::TraitValue(trait, 10) == 600, "Asymmetric ordered trait tiers");
}
void Guard()
{
    auto catalog = Quiet();
    Enable(catalog, 0);
    catalog.units[1].attackRate = 1000;
    auto &shot = catalog.units[4].ability;
    shot = {};
    shot.id = "test_shot"; shot.enabled = true; shot.selector = wc::Selector::HighestAttackRateEnemy;
    shot.range = 8; shot.maxTargets = 1; shot.castMs = 50; shot.cooldownMs = 60000;
    shot.magnitude = {10000, 10000, 10000};
    const auto attacker = std::vector<wc::OwnedUnit>{Unit(3, 4, 4, 2)};
    wc::Combat guarded(catalog, {Unit(1, 0, 3, 3), Unit(2, 1, 3, 2)}, attacker, 41);
    Ticks(guarded, 3);
    auto found = std::find_if(guarded.Events().begin(), guarded.Events().end(), [](const auto &e) { return e.target == 2 && !e.basicAttack; });
    Check(found != guarded.Events().end() && found->guardedBy == 1 && found->prevented == 3000 &&
          found->healthLoss == 7000, "Frontal guard protects selected ally behind and reports prevented damage");
    wc::Combat exposed(catalog, {Unit(1, 0, 3, 3, wc::Facing::Backward), Unit(2, 1, 3, 2)}, attacker, 41);
    Ticks(exposed, 3);
    found = std::find_if(exposed.Events().begin(), exposed.Events().end(), [](const auto &e) { return e.target == 2 && !e.basicAttack; });
    Check(found != exposed.Events().end() && found->prevented == 0 && found->healthLoss == 10000,
          "Turning guarded sector away exposes the ally");
    wc::Combat mirrored(catalog, attacker, {Unit(1, 0, 3, 3), Unit(2, 1, 3, 2)}, 41);
    Ticks(mirrored, 3);
    Check(std::any_of(mirrored.Events().begin(), mirrored.Events().end(), [](const auto &e) { return e.prevented == 3000; }),
          "Side B local facing rotates with both board axes");
}
void Screening()
{
    auto catalog = Quiet();
    Enable(catalog, 3);
    catalog.units[3].ability.range = 8;
    wc::Combat screened(catalog, {Unit(1, 3, 3, 3)}, {Unit(2, 0, 4, 3), Unit(3, 1, 4, 0)}, 2);
    Ticks(screened, 2);
    const auto hits = Events(screened, wc::AbilityMechanic::ScreenedStrike, wc::Effect::Damage);
    Check(hits.size() == 1 && hits[0].target == ((wc::Id(1) << 20) | 2), "A defender intercepts the farthest-target strike");
    wc::Combat open(catalog, {Unit(1, 3, 3, 3)}, {Unit(3, 1, 4, 0)}, 2);
    Ticks(open, 2);
    const auto openHits = Events(open, wc::AbilityMechanic::ScreenedStrike, wc::Effect::Damage);
    Check(openHits.size() == 1 && openHits[0].target == ((wc::Id(1) << 20) | 3), "Exposed backline receives the strike");
}
void Charge()
{
    auto catalog = Quiet();
    Enable(catalog, 1);
    catalog.units[1].ability.range = 4;
    wc::Combat open(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    Ticks(open, 2);
    const auto moves = Events(open, wc::AbilityMechanic::MomentumCharge, wc::Effect::Dash);
    const auto hits = Events(open, wc::AbilityMechanic::MomentumCharge, wc::Effect::Damage);
    Check(moves.size() == 1 && moves[0].cell == wc::Cell{3, 5}, "Charge occupies the legal adjacent landing");
    Check(hits.size() == 1 && hits[0].resolved == 16900, "Two movement cells add bounded momentum to the charge");
    wc::Combat blocked(catalog, {Unit(1, 1, 3, 2), Unit(3, 0, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    Ticks(blocked, 2);
    Check(Events(blocked, wc::AbilityMechanic::MomentumCharge, wc::Effect::Damage).empty(),
          "Charge cannot tunnel through its own screen");
}
void Beams()
{
    auto catalog = Quiet();
    Enable(catalog, 4);
    auto &beam = catalog.units[4].ability;
    beam.radius = 3; beam.range = 8; beam.secondaryDelayMs = 100; beam.travelMs = 100;
    wc::Combat combat(catalog, {Unit(1, 4, 3, 3)},
        {Unit(2, 0, 4, 3), Unit(3, 1, 2, 3), Unit(4, 2, 4, 1), Unit(5, 3, 1, 1)}, 9);
    Ticks(combat, 1);
    const auto visual = combat.VisualActions();
    Check(visual.size() >= 2 && std::count_if(visual.begin(), visual.end(), [](const auto &v) {
        return v.mechanic == wc::AbilityMechanic::CrossingBeams && v.provisional && !v.cells.empty();
    }) == 2, "Both committed beam lanes expose distinct telegraphs");
    Ticks(combat, 6);
    const auto hits = Events(combat, wc::AbilityMechanic::CrossingBeams, wc::Effect::Damage);
    Check(hits.size() == 4, "Cross hits row and column; center can be struck once per pulse");
    Check(hits.front().tick == 4 && hits.back().tick == 6, "Sequential crossing lanes obey authored travel and delay");
    Check(std::none_of(hits.begin(), hits.end(), [](const auto &e) { return e.target == ((wc::Id(1) << 20) | 5); }),
          "Off-axis unit avoids both beam lanes");

    catalog.units[4].health = 10000;
    catalog.units[0].attackDamage = 100000;
    wc::Combat released(catalog, {Unit(1, 4, 3, 3)}, {Unit(2, 0, 4, 3)}, 9);
    Ticks(released, 2);
    Check(released.Units()[0].health == 0 && !released.Result().complete,
          "Defeated caster leaves released hostile beams to drain");
    Ticks(released, 5);
    Check(Events(released, wc::AbilityMechanic::CrossingBeams, wc::Effect::Damage).size() == 2 && released.Result().complete,
          "Both already released beam lanes survive caster defeat and then settle");

    catalog = Quiet(); Enable(catalog, 4);
    catalog.units[4].ability.radius = 3; catalog.units[4].ability.range = 8;
    catalog.units[4].ability.travelMs = 100; catalog.units[4].ability.secondaryDelayMs = 100;
    catalog.units[0].range = 1; catalog.units[0].movementRate = 10000;
    wc::Combat moving(catalog, {Unit(1, 4, 3, 3)}, {Unit(2, 0, 4, 0)}, 9);
    Ticks(moving, 7);
    const auto movingHits = Events(moving, wc::AbilityMechanic::CrossingBeams, wc::Effect::Damage);
    Check(std::none_of(movingHits.begin(), movingHits.end(), [](const auto &e) { return e.tick == 4; }),
          "First beam remains at its committed row when the target moves away");
}
void TideAndGrove()
{
    auto catalog = Quiet();
    Enable(catalog, 5);
    catalog.units[5].ability.range = 8;
    wc::Combat open(catalog, {Unit(1, 5, 3, 3)}, {Unit(2, 0, 4, 3), Unit(3, 1, 4, 0)}, 8);
    Ticks(open, 2);
    auto moves = Events(open, wc::AbilityMechanic::TidalPush, wc::Effect::Dash);
    Check(moves.size() == 1 && moves[0].cell == wc::Cell{3, 6}, "Only first lane enemy is pushed by two free cells");
    Check(Events(open, wc::AbilityMechanic::TidalPush, wc::Effect::Damage).size() == 2,
          "Tide continues to damage the second lane enemy");
    wc::Combat blocked(catalog, {Unit(1, 5, 3, 3)}, {Unit(2, 0, 4, 3), Unit(3, 1, 4, 2)}, 8);
    Ticks(blocked, 2);
    Check(Events(blocked, wc::AbilityMechanic::TidalPush, wc::Effect::Dash).empty(),
          "Occupied push destination cancels displacement without canceling damage");

    catalog = Quiet(); Enable(catalog, 2); Enable(catalog, 5);
    catalog.units[2].ability.stationaryMs = 50;
    catalog.units[2].ability.durationMs = 4000;
    catalog.units[2].ability.pulseMs = 500;
    catalog.units[2].ability.radius = 1;
    catalog.units[5].ability.firstCastMs = 4100;
    catalog.units[5].attackRate = 1000; catalog.units[5].attackDamage = 1000;
    wc::Combat grove(catalog, {Unit(1, 2, 3, 3), Unit(2, 0, 2, 3)}, {Unit(3, 5, 4, 1)}, 21);
    Ticks(grove, 145);
    const auto heals = Events(grove, wc::AbilityMechanic::StationaryGrove, wc::Effect::Heal);
    moves = Events(grove, wc::AbilityMechanic::TidalPush, wc::Effect::Dash);
    Check(!heals.empty(), "Stationary grove heals injured allies through real incoming damage");
    Check(!moves.empty() && moves.front().target == 1, "Tidal displacement moves the grove source");
    Check(std::none_of(heals.begin(), heals.end(), [&](const auto &e) { return e.tick > moves.front().tick; }),
          "All pending grove pulses terminate when its source is displaced");
}
void RelicsAndReplay()
{
    auto catalog = wcvnext::WonderVNextCatalog();
    wc::RelicDef item;
    item.id = "test_broad_but_brief";
    item.compatibleMechanics = {wc::AbilityMechanic::StationaryGrove, wc::AbilityMechanic::CrossingBeams};
    item.radiusDelta = 1; item.durationBp = 5000; item.castBp = 15000;
    catalog.relics.push_back(item);
    const auto base = catalog.units[2].ability;
    const auto effective = wc::EffectiveAbility(catalog, catalog.units[2], int(catalog.relics.size()) - 1);
    Check(effective.radius == base.radius + 1 && effective.durationMs == base.durationMs / 2 &&
          effective.castMs > base.castMs, "Relic trades larger grove for shorter duration and slower windup");
    Check(catalog.units[2].ability.radius == base.radius, "Evaluating a relic does not mutate canonical ability");
    bool rejected = false;
    try { wc::EffectiveAbility(catalog, catalog.units[0], int(catalog.relics.size()) - 1); }
    catch (const std::invalid_argument &) { rejected = true; }
    Check(rejected, "Incompatible relic fails closed before combat");
    std::vector<wc::OwnedUnit> a{Unit(1, 0, 3, 3), Unit(2, 2, 3, 2), Unit(3, 4, 2, 1)},
        b{Unit(4, 1, 3, 3), Unit(5, 3, 2, 1), Unit(6, 5, 3, 2)};
    auto relicHolder = a; relicHolder[1].relic = int(catalog.relics.size()) - 1;
    wc::Combat evaluated(catalog, relicHolder, b, 19);
    Check(evaluated.Units()[1].ability.radius == effective.radius, "Combat consumes evaluated relic ability");
    wc::Combat observed(catalog, a, b, 19), unseen(catalog, a, b, 19);
    while (!observed.Result().complete)
    {
        observed.VisualActions(); observed.Tick(); unseen.Tick();
        Check(observed.InvariantError().empty(), "Whole native encounter invariant");
    }
    Check(unseen.Result().complete && observed.Result().winner == unseen.Result().winner &&
          observed.Events().size() == unseen.Events().size(), "Observed and off-screen encounters produce identical outcomes");
    for (std::size_t i = 0; i < observed.Events().size(); ++i)
    {
        const auto &x = observed.Events()[i], &y = unseen.Events()[i];
        Check(std::tie(x.tick,x.source,x.target,x.action,x.effect,x.resolved,x.cell.column,x.cell.row,x.prevented) ==
              std::tie(y.tick,y.source,y.target,y.action,y.effect,y.resolved,y.cell.column,y.cell.row,y.prevented),
              "Replay preserves every timed damage and spatial event");
    }
}
void CrowdedEncounters()
{
    const auto catalog = wcvnext::WonderVNextCatalog();
    int timeouts = 0;
    for (wc::Id seed = 1; seed <= 32; ++seed)
    {
        wc::Random random{seed};
        std::vector<wc::OwnedUnit> formations[2];
        for (int side = 0; side < 2; ++side)
            for (int index = 0; index < 10; ++index)
            {
                auto unit = Unit(index + 1, random.Below(int(catalog.units.size())),
                    index < 8 ? index : (index - 8) * 4 + 2, index < 8 ? 3 : 2);
                unit.star = 1 + random.Below(3);
                formations[side].push_back(unit);
            }
        wc::Combat combat(catalog, formations[0], formations[1], seed);
        while (!combat.Result().complete)
        {
            combat.Tick();
            Check(combat.InvariantError().empty(), "Crowded ten-versus-ten occupancy and reservations remain valid");
        }
        if (combat.Result().timeout) ++timeouts;
        for (const auto &event : combat.Events())
            if (event.effect == wc::Effect::Damage)
                Check(event.resolved == event.absorbed + event.healthLoss + event.overkill && event.prevented >= 0,
                      "Every crowded battle damage event reconciles after directional mitigation");
    }
    std::cout << "Crowded native synthetic encounters: 32 seeds, " << timeouts << " timeouts.\n";
}
}
int main()
{
    try
    {
        Contract(); Guard(); Screening(); Charge(); Beams(); TideAndGrove(); RelicsAndReplay(); CrowdedEncounters();
        std::cout << "PASS vNext native combat: " << assertions << " assertions. Technical synthetic fixtures only; no human art/balance acceptance.\n";
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << "FAIL after " << assertions << " assertions: " << error.what() << '\n';
        return 1;
    }
}
