#include "VNext/WonderVNextCatalog.generated.h"
#include "Simulation/WonderDamageChart.h"
#include "../../game/Source/WonderChessRuntime/Private/Simulation/WonderManaTests.h"
#include "../../game/Source/WonderChessRuntime/Private/Simulation/WonderCombatClarityTests.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
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
    Check(catalog.profileId == "wonder_vnext" && catalog.units.size() == 40, "Seven ported mechanics plus thirty-three standard-ability heroes");
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
    Check(observed.EnableDiagnostics(), "Diagnostics can be enabled before the first tick");
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
        Check(std::tie(x.tick,x.source,x.target,x.action,x.effect,x.requested,x.resolved,x.absorbed,x.healthLoss,
                  x.overkill,x.cell.column,x.cell.row,x.absorbedFrom,x.damageType,x.basicAttack,x.radius,
                  x.mechanic,x.origin.column,x.origin.row,x.guardedBy,x.prevented) ==
              std::tie(y.tick,y.source,y.target,y.action,y.effect,y.requested,y.resolved,y.absorbed,y.healthLoss,
                  y.overkill,y.cell.column,y.cell.row,y.absorbedFrom,y.damageType,y.basicAttack,y.radius,
                  y.mechanic,y.origin.column,y.origin.row,y.guardedBy,y.prevented),
              "Diagnostics preserve every combat event field against the disabled replay");
    }
    Check(!observed.Diagnostics().empty() && unseen.Diagnostics().empty(), "Diagnostics are opt-in and separate from events");
    Check(!unseen.EnableDiagnostics(), "Late diagnostics cannot present an incomplete encounter as complete evidence");
    Check(observed.Result().ticks == unseen.Result().ticks && observed.Result().timeout == unseen.Result().timeout &&
        observed.Result().survivors == unseen.Result().survivors, "Diagnostics preserve timing and survivors");
    for (std::size_t i = 0; i < observed.Units().size(); ++i)
    {
        const auto &x = observed.Units()[i], &y = unseen.Units()[i];
        Check(std::tie(x.health,x.shield,x.cell.column,x.cell.row,x.state,x.actionId,x.positionEpoch,x.momentumSteps) ==
              std::tie(y.health,y.shield,y.cell.column,y.cell.row,y.state,y.actionId,y.positionEpoch,y.momentumSteps),
              "Diagnostics preserve final health, position and action state");
    }
}
bool HasTrace(const wc::Combat &combat, wc::MechanicPhase phase, wc::MechanicReason reason)
{
    return std::any_of(combat.Diagnostics().begin(), combat.Diagnostics().end(), [&](const auto &trace) {
        return trace.phase == phase && trace.reason == reason;
    });
}
void Diagnostics()
{
    using P = wc::MechanicPhase; using R = wc::MechanicReason;
    auto catalog = Quiet(); Enable(catalog, 1); catalog.units[1].ability.range = 4;
    wc::Combat open(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    open.EnableDiagnostics(); Ticks(open, 2);
    Check(HasTrace(open, P::Committed, R::Ready) && HasTrace(open, P::Released, R::Ready) &&
        HasTrace(open, P::Impact, R::Resolved), "A successful charge has commitment, release and actual impact evidence");
    auto released = std::find_if(open.Diagnostics().begin(), open.Diagnostics().end(), [](const auto &t) { return t.phase == P::Released; });
    Check(released->origin == wc::Cell{3, 3} && released->landing == wc::Cell{3, 5}, "Charge trace retains reserved landing before movement");
    wc::Combat blocked(catalog, {Unit(1, 1, 3, 2), Unit(3, 0, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    blocked.EnableDiagnostics(); Ticks(blocked, 2);
    Check(HasTrace(blocked, P::Attempt, R::PathOccupied) && !HasTrace(blocked, P::Committed, R::Ready),
        "Own-screen obstruction is a failed attempt, not a cancelled commitment");
    wc::Combat adjacent(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 3)}, 5);
    adjacent.EnableDiagnostics(); Ticks(adjacent, 2);
    Check(HasTrace(adjacent, P::Attempt, R::NoMomentum), "An adjacent unmoved charger reports missing momentum");
    catalog.units[0].range = 1; catalog.units[0].movementRate = 10000;
    catalog.units[1].ability.castMs = 500;
    wc::Combat moving(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    moving.EnableDiagnostics(); Ticks(moving, 12);
    Check(HasTrace(moving, P::Cancelled, R::TargetMoved) || HasTrace(moving, P::Cancelled, R::NoMomentum),
        "A target approaching during windup produces an explicit cancelled charge");
    catalog = Quiet(); Enable(catalog, 1); catalog.units[1].ability.castMs = 1000;
    catalog.rules.combatTimeoutMs = 100;
    wc::Combat timeout(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    timeout.EnableDiagnostics(); Ticks(timeout, 3);
    Check(timeout.Result().timeout && HasTrace(timeout, P::Cancelled, R::CombatEnded), "Timeout closes outstanding windup evidence");
    catalog = Quiet(); Enable(catalog, 1); catalog.units[1].ability.castMs = 1000;
    catalog.units[1].health = 1000; catalog.units[0].attackDamage = 100000;
    wc::Combat defeated(catalog, {Unit(1, 1, 3, 3)}, {Unit(2, 0, 4, 1)}, 5);
    defeated.EnableDiagnostics(); Ticks(defeated, 3);
    Check(HasTrace(defeated, P::Cancelled, R::SourceDefeated), "Defeat closes a committed windup without fabricating a release");

    catalog = Quiet(); Enable(catalog, 2);
    catalog.units[2].ability.stationaryMs = 200;
    wc::Combat waiting(catalog, {Unit(1, 2, 3, 3)}, {Unit(2, 0, 4, 1)}, 21);
    waiting.EnableDiagnostics(); Ticks(waiting, 90);
    Check(HasTrace(waiting, P::Attempt, R::NotEstablished) && HasTrace(waiting, P::Attempt, R::NoInjuredAlly),
        "Grove attempts distinguish establishing from waiting for injury");
    catalog = Quiet(); Enable(catalog, 2); Enable(catalog, 5);
    catalog.units[2].ability.stationaryMs = 50; catalog.units[2].ability.durationMs = 4000;
    catalog.units[2].ability.pulseMs = 500; catalog.units[2].ability.radius = 1;
    catalog.units[5].ability.firstCastMs = 4100;
    catalog.units[5].attackRate = 1000; catalog.units[5].attackDamage = 1000;
    wc::Combat grove(catalog, {Unit(1, 2, 3, 3), Unit(2, 0, 2, 3)}, {Unit(3, 5, 4, 1)}, 21);
    grove.EnableDiagnostics(); Ticks(grove, 145);
    Check(HasTrace(grove, P::Impact, R::SourceMoved), "Displaced-source pulses have explicit tether cancellation evidence");
    Check(HasTrace(grove, P::Impact, R::NoInjuredAlly), "A pulse with no injured recipients remains observable");
    wc::Int requested = 0, resolved = 0, eventRequested = 0, eventResolved = 0; int fullHealth = 0;
    for (const auto &t : grove.Diagnostics()) if (t.phase == P::Impact)
    { requested += t.requested; resolved += t.resolved; fullHealth += t.fullHealthAllies; }
    for (const auto &e : Events(grove, wc::AbilityMechanic::StationaryGrove, wc::Effect::Heal))
    { eventRequested += e.requested; eventResolved += e.resolved; }
    Check(requested == eventRequested && resolved == eventResolved && fullHealth > 0,
        "Pulse totals reconcile with real healing and count skipped full-health allies separately");
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
void Cocoons()
{
    auto catalog = Quiet();
    auto &a = catalog.units[1].ability;
    a = {}; a.id = "silkmother_test"; a.name = "Silken Snare";
    a.mechanic = wc::AbilityMechanic::CocoonProjectile; a.effect = wc::Effect::Stun;
    a.range = 4; a.maxTargets = 1; a.castMs = 50; a.travelMs = 200;
    a.durationMs = 2000; a.cooldownMs = 60000; a.recoveryMs = 50;
    auto successful = [](const wc::Combat &c) {
        auto result = Events(c, wc::AbilityMechanic::CocoonProjectile, wc::Effect::Stun);
        result.erase(std::remove_if(result.begin(), result.end(), [](const auto &e) { return e.resolved == 0; }), result.end());
        return result;
    };
    const std::vector<wc::OwnedUnit> allies{Unit(1,1,3,3)};
    const std::vector<wc::OwnedUnit> enemies{Unit(2,0,4,1),Unit(3,0,0,0)};
    wc::Combat c(catalog, allies, enemies, 123);
    Ticks(c,2);
    const auto actions = c.VisualActions();
    Check(std::any_of(actions.begin(), actions.end(), [](const auto &v) {
        return v.mechanic == wc::AbilityMechanic::CocoonProjectile && v.released && !v.fixedArea &&
            v.target == ((wc::Id(1)<<20)|2) && v.recipients.size()==1;
    }), "Released cocoon is one tracking projectile to nearest enemy");
    Check(successful(c).empty(), "Cocoon cannot land before projectile travel finishes");
    Ticks(c,4);
    auto hits = successful(c);
    Check(hits.size()==1 && hits.front().resolved==2000 && hits.front().healthLoss==0,
        "Single impact applies exactly two seconds of control with zero damage");
    const auto &target=c.Units()[1];
    const auto ordinal=target.basicAttackOrdinal; const auto cell=target.cell;
    const int expiry=target.cocoonExpiry;
    Check(target.state==wc::ActionState::Stunned && target.cocoonSource==1 && target.health==target.maxHealth,
        "Cocoon has distinct expiry/source identity and preserves enemy health");
    while(c.CurrentTick()<expiry-1) {
        Ticks(c,1);
        Check(target.state==wc::ActionState::Stunned && target.basicAttackOrdinal==ordinal && target.cell==cell,
            "Cocoon suppresses attacks, casting and locomotion for its entire duration");
    }
    Ticks(c,1); Check(target.state!=wc::ActionState::Stunned,"Cocoon releases at exact expiry tick");
    wc::Combat replay(catalog,allies,enemies,123);Ticks(replay,c.CurrentTick());
    Check(successful(replay).front().tick==hits.front().tick && replay.Units()[1].cell==target.cell,
        "Identical authoritative replay reproduces cocoon timing and outcome");

    // Synthetic short cooldown forces a second selection while the first target is trapped.
    a.cooldownMs=500;
    catalog.units[1].attackRate=3500;
    wc::Combat skip(catalog,allies,enemies,123);Ticks(skip,35);hits=successful(skip);
    Check(hits.size()==2 && hits[0].target!=hits[1].target,"Next cast skips an existing cocoon");
    wc::Combat noTargets(catalog,allies,{enemies.front()},123);Ticks(noTargets,30);
    Check(successful(noTargets).size()==1,"No recast refresh when every eligible target is trapped");
    a.cooldownMs=60000;
    wc::Combat doubles(catalog,{Unit(1,1,3,3),Unit(4,1,2,3)},{enemies.front()},123);
    Ticks(doubles,8);
    Check(successful(doubles).size()==1,"Concurrent in-flight cocoons do not stack or refresh");

    catalog.units[0].range=1;
    wc::Combat moving(catalog,allies,{enemies.front()},123);Ticks(moving,6);
    Check(moving.Units()[1].state==wc::ActionState::Stunned && moving.Units()[1].destination.column<0,
        "Impact cancels a moving enemy's reserved step");
    const auto stopped=moving.Units()[1].cell;Ticks(moving,20);
    Check(moving.Units()[1].cell==stopped,"No reserved movement completes through the cocoon");

    // A generic stun may interrupt Silkmother before release but isn't itself a cocoon.
    auto &interrupt=catalog.units[0].ability;interrupt={};interrupt.id="interrupt";
    interrupt.effect=wc::Effect::Stun;interrupt.range=8;interrupt.maxTargets=1;
    interrupt.castMs=50;interrupt.durationMs=2000;interrupt.cooldownMs=60000;
    a.castMs=500;
    wc::Combat cancelled(catalog,allies,{enemies.front()},123);Ticks(cancelled,16);
    Check(successful(cancelled).empty() && cancelled.Units()[0].cocoonExpiry==0,
        "Interrupt before release creates no web and generic stun is not marked cocoon");
    a.castMs=50;interrupt.castMs=150;interrupt.effect=wc::Effect::Damage;
    interrupt.magnitude={2000000,2000000,2000000};
    wc::Combat deadCaster(catalog,{Unit(1,1,3,3),Unit(4,2,0,0)},{enemies.front()},123);Ticks(deadCaster,8);
    Check(deadCaster.Units()[0].health==0 && successful(deadCaster).size()==1,
        "Released web survives caster defeat while combat continues");
}
void CanonicalSilkmotherPlacement()
{
    const auto source = wcvnext::WonderVNextCatalog();
    const auto definition = std::find_if(source.units.begin(), source.units.end(), [](const auto &u) {
        return u.id == "wc_vn_soul_jailer";
    });
    Check(definition != source.units.end(), "Canonical Silkmother exists in the enabled runtime catalogue");
    const int silk = int(definition - source.units.begin());
    auto catalog = Quiet();
    // Isolate formation access while preserving every canonical cocoon timing/range value.
    // High health, zero basic damage and range-eight basics keep both formations stationary.
    catalog.units[silk].ability = definition->ability;
    const std::vector<wc::OwnedUnit> inRange{Unit(1, silk, 3, 3)};
    const std::vector<wc::OwnedUnit> outOfRange{Unit(1, silk, 0, 0)};
    const std::vector<wc::OwnedUnit> nearby{Unit(2, 0, 4, 2)};
    const std::vector<wc::OwnedUnit> distant{Unit(2, 0, 0, 0)};
    auto successful = [](const wc::Combat &c) {
        auto events = Events(c, wc::AbilityMechanic::CocoonProjectile, wc::Effect::Stun);
        events.erase(std::remove_if(events.begin(), events.end(), [](const auto &e) { return e.resolved == 0; }), events.end());
        return events;
    };
    for (wc::Id seed : {7011, 7012, 7013, 7014})
    {
        wc::Combat accessible(catalog, inRange, nearby, seed);
        Check(accessible.EnableDiagnostics(), "Canonical cocoon fixture enables complete diagnostics");
        Ticks(accessible, 150);
        const auto hits = successful(accessible);
        Check(hits.size() == 1 && hits.front().resolved == definition->ability.durationMs &&
              hits.front().healthLoss == 0, "In-range placement delivers the canonical damage-free control duration");
        const auto release = std::find_if(accessible.Diagnostics().begin(), accessible.Diagnostics().end(), [](const auto &t) {
            return t.phase == wc::MechanicPhase::Released;
        });
        Check(release != accessible.Diagnostics().end() &&
              hits.front().tick - release->tick == definition->ability.travelMs / catalog.rules.tickMs,
              "Canonical web impact follows authored projectile travel after actual release");
        const int expiry = hits.front().tick + definition->ability.durationMs / catalog.rules.tickMs;
        wc::Combat expiryCheck(catalog, inRange, nearby, seed);
        Ticks(expiryCheck, expiry - 1);
        Check(expiryCheck.Units()[1].cocoonExpiry == expiry &&
              expiryCheck.Units()[1].state == wc::ActionState::Stunned,
              "Canonical cocoon retains its target through the tick before exact expiry");
        Ticks(expiryCheck, 1);
        Check(expiryCheck.Units()[1].cocoonExpiry == 0 && expiryCheck.Units()[1].cocoonSource == 0 &&
              expiryCheck.Units()[1].state != wc::ActionState::Stunned,
              "Canonical expiry clears cocoon identity and permits ordinary action again");
        wc::Combat mirrored(catalog, nearby, inRange, seed);
        Ticks(mirrored, 150);
        const auto mirroredHits = successful(mirrored);
        Check(mirroredHits.size() == 1 && mirroredHits.front().tick == hits.front().tick &&
              mirroredHits.front().resolved == hits.front().resolved && mirroredHits.front().target == 2,
              "Side-swapped canonical Silkmother retains impact timing and the intended opposing recipient");
        wc::Combat inaccessible(catalog, outOfRange, distant, seed);
        Ticks(inaccessible, 150);
        Check(successful(inaccessible).empty(), "Out-of-range stationary placement cannot claim useful cocoon access");
        auto disabled = catalog;
        disabled.units[silk].ability.enabled = false;
        wc::Combat control(disabled, inRange, nearby, seed);
        Ticks(control, 150);
        Check(successful(control).empty() && control.Units()[1].cocoonExpiry == 0,
              "Identical formation with only the skill disabled has no fabricated control effect");
    }
    auto &interrupt = catalog.units[0].ability;
    interrupt = {}; interrupt.id = "canonical_cocoon_interruption_fixture";
    interrupt.effect = wc::Effect::Stun; interrupt.selector = wc::Selector::CurrentEnemy;
    interrupt.range = 8; interrupt.maxTargets = 1; interrupt.firstCastMs = definition->ability.firstCastMs + 100;
    interrupt.castMs = 50; interrupt.durationMs = 2000; interrupt.cooldownMs = 60000;
    wc::Combat cancelled(catalog, inRange, nearby, 7011);
    Check(cancelled.EnableDiagnostics(), "Canonical interruption fixture enables complete diagnostics");
    Ticks(cancelled, 150);
    Check(successful(cancelled).empty() && HasTrace(cancelled, wc::MechanicPhase::Committed, wc::MechanicReason::Ready) &&
          HasTrace(cancelled, wc::MechanicPhase::Cancelled, wc::MechanicReason::SourceStunned),
          "An actual stun inside canonical weaving windup cancels its commitment without a web impact");
}
void RosterRecipe()
{
    const auto base = wcvnext::WonderVNextCatalog();
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    Check(roster.Validate().empty() && roster.contentDigest != base.contentDigest &&
          roster.balanceVersion != base.balanceVersion, "Roster recipe validates with its own save/replay identity");
    Check(base.traits.empty() && roster.traits.size() == 22, "Control keeps no traits; recipe carries twenty executed traits in twenty-two parts");
    for (int i = 0; i < 7; ++i)
    {
        const auto &a = base.units[i]; const auto &b = roster.units[i];
        Check(a.ability.mana.maximum == 0 && b.ability.mana.maximum == (i >= 3 ? 10000 : 0) &&
              (i < 3 || a.ability.mechanic != wc::AbilityMechanic::Standard),
              "Cast abilities use mana; guard, charge and grove stay passive");
        Check(std::tie(a.id, a.cost, a.health, a.attackDamage, a.attackRate, a.range, a.armor, a.resistance) ==
              std::tie(b.id, b.cost, b.health, b.attackDamage, b.attackRate, b.range, b.armor, b.resistance),
              "Recipe preserves identities, prices and stats");
    }
    const int shield = 0, rusher = 1, hook = 3, scholar = 4, tide = 5, jailer = 6;
    for (int i = 7; i < int(roster.units.size()); ++i)
        Check(base.units[i].ability.mechanic == wc::AbilityMechanic::Standard && base.units[i].ability.mana.maximum == 0 &&
              roster.units[i].ability.mana.maximum == 10000, "Standard-ability heroes use timers in the control and mana in the recipe");
    const std::vector<wc::OwnedUnit> enemy{Unit(9, rusher, 0, 0)};
    {
        wc::Combat pair(roster, {Unit(1, shield, 0, 0), Unit(2, scholar, 1, 0), Unit(3, hook, 2, 0)}, enemy, 1);
        Check(pair.Units()[1].mana == 1000 && pair.Units()[2].mana == 1000 && pair.Units()[0].mana == 0,
              "Two Humans give every mana user on the team 10 starting mana; passive heroes hold none");
        Check(pair.Units()[3].mana == 0 && pair.InvariantError().empty(), "Opponents receive no Human bonus and the mana ledger balances");
        wc::Combat single(roster, {Unit(2, scholar, 1, 0), Unit(3, hook, 2, 0)}, enemy, 1);
        Check(single.Units()[0].mana == 0 && single.Units()[1].mana == 0, "One Human activates nothing");
        wc::Combat copies(roster, {Unit(1, scholar, 0, 0), Unit(2, scholar, 1, 0)}, enemy, 1);
        Check(copies.Units()[0].mana == 0, "Two copies of one hero count once");
    }
    {
        wc::Combat mages(roster, {Unit(1, scholar, 0, 0), Unit(2, tide, 1, 0), Unit(3, hook, 2, 0)}, enemy, 1);
        Check(mages.Units()[0].abilityBonus == 2000 && mages.Units()[1].abilityBonus == 2000 &&
              mages.Units()[2].abilityBonus == 2000 && mages.Units()[3].abilityBonus == 0,
              "Two Mages give the whole team 20% skill damage and the enemy none");
        wc::Combat one(roster, {Unit(1, scholar, 0, 0), Unit(3, hook, 2, 0)}, enemy, 1);
        Check(one.Units()[0].abilityBonus == 0, "One Mage activates nothing");
    }
    {
        auto c = roster;
        c.units[shield].race = "orc"; c.units[rusher].unitClass = "tank";
        wc::Combat members(c, {Unit(1, shield, 0, 0), Unit(2, rusher, 1, 0), Unit(3, hook, 2, 0)}, enemy, 1);
        const auto &u = members.Units();
        Check(u[0].maxHealth == wc::StarValue(c.units[shield].health, 1, 2000, c.rules) &&
              u[1].maxHealth == wc::StarValue(c.units[rusher].health, 1, 2000, c.rules) &&
              u[2].maxHealth == c.units[hook].health, "Two Orcs gain 20% health; a non-Orc ally does not");
        Check(u[0].armor == c.units[shield].armor + 20 && u[1].armor == c.units[rusher].armor + 20 &&
              u[2].armor == c.units[hook].armor, "Two Tanks gain 20 armour; a non-Tank ally does not");
        auto bad = roster; bad.traits[0].stat = "made_up_stat_bp";
        Check(!bad.Validate().empty(), "Unknown trait stats are rejected");
        bad = roster; bad.units[shield].ability.mana = roster.units[hook].ability.mana;
        Check(!bad.Validate().empty(), "A passive guard cannot carry a mana contract");
    }
    {
        auto c = roster;
        c.traits.clear();
        for (auto &unit : c.units)
        {
            unit.health = 1000000; unit.attackDamage = 0; unit.armor = unit.resistance = 0;
            unit.range = 8; unit.attackRate = 1000; unit.attackWindupMs = 50; unit.projectileTravelMs = 0;
            unit.ability.enabled = false;
        }
        c.units[jailer].ability = roster.units[jailer].ability;
        c.units[jailer].attackDamage = 100;
        wc::Combat fight(c, {Unit(1, jailer, 3, 3)}, {Unit(2, shield, 4, 3)}, 77);
        Ticks(fight, 70);
        Check(fight.Units()[0].castsCommitted == 0 && fight.Units()[0].mana > 0 && fight.Units()[0].mana < 10000,
              "The cage waits for mana instead of its old opening timer");
        Ticks(fight, 130);
        const auto cages = Events(fight, wc::AbilityMechanic::CocoonProjectile, wc::Effect::Stun);
        Check(fight.Units()[0].castsCommitted >= 1 && fight.Units()[0].manaSpent == 10000 * fight.Units()[0].castsCommitted &&
              !cages.empty() && cages.front().healthLoss == 0, "Full mana releases a real damage-free cage");
    }
}
void DirectMovement()
{
    const auto base = wcvnext::WonderVNextCatalog();
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    Check(!base.rules.directMovement && !base.rules.nearestReachableTarget && roster.rules.directMovement &&
          roster.rules.nearestReachableTarget, "Only the roster recipe uses nearest targets and direct movement");
    int walker = -1;
    for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == "wc_vn_hammerer") walker = i;
    Check(walker >= 0 && roster.units[walker].range == 1, "The movement fixture uses a melee hero");
    auto firstStep = [&](const wc::Catalog &catalog, std::vector<wc::OwnedUnit> team, wc::Cell enemyWorld) {
        wc::Combat combat(catalog, team, {Unit(9, walker, 7 - enemyWorld.column, 7 - enemyWorld.row)}, 1);
        for (int tick = 0; tick < 4 && combat.Units()[0].destination.column < 0; ++tick) combat.Tick();
        return combat.Units()[0].destination;
    };
    Check(firstStep(roster, {Unit(1, walker, 3, 0)}, {3, 6}) == wc::Cell{3, 1}, "A unit walks straight at an enemy directly ahead");
    Check(firstStep(roster, {Unit(1, walker, 0, 0)}, {5, 5}) == wc::Cell{1, 1}, "A unit walks diagonally at a diagonal enemy");
    const std::vector<wc::OwnedUnit> flanked{Unit(1, walker, 0, 0), Unit(2, walker, 1, 0), Unit(3, walker, 0, 1)};
    Check(firstStep(roster, flanked, {5, 5}) == wc::Cell{1, 1}, "Neighbours beside the route do not block a diagonal step");
    Check(!(firstStep(base, flanked, {5, 5}) == wc::Cell{1, 1}), "The control keeps its blocked-corner rule");
    {
        // A charge under the roster rules hits along its line and leaves the charger on its own cell.
        const int rusher = 1;
        // Count charges begun from at least two cells away, and how many of them left the charger elsewhere.
        const auto run = [&](const wc::Catalog &catalog) {
            int charges = 0, displaced = 0;
            for (int seed = 1; seed <= 12; ++seed)
                for (int row = 2; row <= 4; ++row)
                {
                    wc::Combat combat(catalog, {Unit(1, rusher, 3, 0)}, {Unit(9, walker, 4, row), Unit(10, walker, 1, row)}, seed);
                    bool casting = false, far = false;
                    wc::Cell from;
                    for (int tick = 0; tick < 600 && !combat.Result().complete; ++tick)
                    {
                        combat.Tick();
                        const auto &charger = combat.Units()[0];
                        const bool now = charger.state == wc::ActionState::CastWindup || charger.state == wc::ActionState::CastRecovery;
                        if (now && !casting)
                        {
                            from = charger.cell;
                            far = charger.target >= 0 && wc::Distance(charger.cell, combat.Units()[charger.target].cell) >= 2;
                        }
                        if (!now && casting && far) { ++charges; displaced += !(charger.cell == from); }
                        casting = now;
                    }
                }
            return std::make_pair(charges, displaced);
        };
        Check(roster.rules.chargeReturns && !base.rules.chargeReturns, "Only the roster recipe returns the charger");
        const auto returned = run(roster), moved = run(base);
        std::cout << "Long charges: roster " << returned.first << " (displaced " << returned.second << "), control "
                  << moved.first << " (displaced " << moved.second << ")\n";
        Check(returned.second == 0, "A roster charge ends on the cell it started from");
        Check(moved.first == 0 || moved.second > 0, "A control charge still lands beside its target");
    }
    Check(firstStep(roster, {Unit(1, walker, 0, 0)}, {4, 1}) == wc::Cell{1, 0} ||
          firstStep(roster, {Unit(1, walker, 0, 0)}, {4, 1}) == wc::Cell{1, 1}, "A shallow approach heads toward the enemy");
}
void UniversalRelics()
{
    const auto catalog = wcvnext::WonderVNextRosterCatalog();
    Check(catalog.relics.size() == 12, "Twelve relics remain in the catalogue");
    for (const auto &relic : catalog.relics)
        for (const auto &unit : catalog.units)
            Check(wc::RelicCompatible(relic, unit.ability.mechanic), "Every relic fits every hero");
    auto index = [&](const char *id) {
        for (int i = 0; i < int(catalog.relics.size()); ++i) if (catalog.relics[i].id == id) return i;
        throw std::runtime_error("Missing relic fixture");
    };
    const std::vector<wc::OwnedUnit> enemy{Unit(9, 1, 0, 0)};
    for (int hero = 0; hero < int(catalog.units.size()); ++hero)
    {
        const auto &d = catalog.units[hero];
        auto holder = Unit(1, hero, 0, 0);
        wc::Combat plain(catalog, {holder}, enemy, 3);
        holder.relic = index("wc_vn_r_broad_canopy");
        wc::Combat canopy(catalog, {holder}, enemy, 3);
        Check(canopy.Units()[0].maxHealth == wc::StarValue(d.health, 1, 2500, catalog.rules) &&
              plain.Units()[0].maxHealth == d.health && canopy.Units()[1].maxHealth == plain.Units()[1].maxHealth,
              "Broad Canopy gives its holder 25% health and nobody else");
        holder.relic = index("wc_vn_r_tight_choir");
        wc::Combat choir(catalog, {holder}, enemy, 3);
        Check(choir.Units()[0].armor == plain.Units()[0].armor + 25, "Tight Choir gives 25 armour");
        holder.relic = index("wc_vn_r_urgent_shard");
        wc::Combat shard(catalog, {holder}, enemy, 3);
        Check(shard.Units()[0].basicBonus == plain.Units()[0].basicBonus + 1500 &&
              shard.Units()[0].abilityBonus == plain.Units()[0].abilityBonus + 1500 &&
              shard.Units()[0].supportBonus == plain.Units()[0].supportBonus + 1500,
              "Urgent Shard gives 15% attack damage and 15% skill power");
        holder.relic = index("wc_vn_r_quick_wick");
        wc::Combat wick(catalog, {holder}, enemy, 3);
        Check(wick.Units()[0].rateBonus == plain.Units()[0].rateBonus + 1000 &&
              wick.Units()[0].ability.cooldownMs < d.ability.cooldownMs, "Quick Wick shortens the skill and speeds attacks");
        Check(wick.InvariantError().empty(), "Relic holders keep combat invariants");
    }
    auto bad = catalog; bad.relics[0].healthBp = 9000;
    Check(!bad.Validate().empty(), "Out-of-range relic stats are rejected");
}
}
void Modifiers()
{
    // The damage curve: unchanged at zero and above, mirrored below zero, floored at -75.
    Check(wc::ResolveDamage(1000, wc::DamageType::Physical, 25, 0) == 800, "25 armour removes a fifth");
    Check(wc::ResolveDamage(1000, wc::DamageType::Physical, -25, 0) == 1200, "-25 armour adds a fifth");
    Check(wc::ResolveDamage(1000, wc::DamageType::Physical, -500, 0) == wc::ResolveDamage(1000, wc::DamageType::Physical, -75, 0),
          "Negative defence is floored at -75");
    Check(wc::ResolveDamage(1000, wc::DamageType::Magic, 0, -25) == 1200 && wc::ResolveDamage(1000, wc::DamageType::True, -25, -25) == 1000,
          "The mirrored curve applies to resistance and never to true damage");

    // One cast puts three different modifiers on the enemy; they must coexist, act, and expire.
    auto catalog = Quiet();
    catalog.units[0].attackDamage = 100000; catalog.units[0].attackRate = 1000;
    catalog.units[1].attackDamage = 100000; catalog.units[1].attackRate = 1000; catalog.units[1].armor = 25;
    Enable(catalog, 0);
    auto &curse = catalog.units[0].ability;
    curse.mechanic = wc::AbilityMechanic::Standard; curse.guardReductionBp = 0;
    curse.effect = wc::Effect::StatModifier; curse.selector = wc::Selector::CurrentEnemy;
    curse.range = 8; curse.radius = 0; curse.maxTargets = 1; curse.travelMs = 0; curse.durationMs = 2000; curse.magnitude = {0, 0, 0};
    curse.effects = {{wc::Effect::StatModifier, wc::DamageType::Physical, 2000, {-50, -50, -50}, 0, false, wc::Selector::CurrentEnemy, wc::ModifierStat::Armor},
                     {wc::Effect::StatModifier, wc::DamageType::Physical, 2000, {-5000, -5000, -5000}, 0, false, wc::Selector::CurrentEnemy, wc::ModifierStat::AttackDamage},
                     {wc::Effect::StatModifier, wc::DamageType::Physical, 2000, {5000, 5000, 5000}, 0, false, wc::Selector::CurrentEnemy, wc::ModifierStat::DamageTaken}};
    wc::Combat combat(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 44);
    Ticks(combat, 120);
    wc::Id caster = 0;
    int applied = 0;
    std::set<wc::ModifierStat> stats;
    for (const auto &event : combat.Events())
        if (event.effect == wc::Effect::StatModifier) { caster = event.source; ++applied; stats.insert(event.stat); }
    Check(applied == 3 && stats.size() == 3, "Three modifiers from one ability land as three separate stats");
    std::vector<wc::Int> mine, theirs;
    for (const auto &event : combat.Events())
        if (event.basicAttack && event.effect == wc::Effect::Damage) (event.source == caster ? mine : theirs).push_back(event.healthLoss);
    Check(!mine.empty() && !theirs.empty(), "Both sides land basic attacks in the modifier fixture");
    for (auto hit : mine)
        Check(hit == 180000 || hit == 80000, "Attacker's hits are either cursed (armour -25, +50% taken) or normal (armour 25)");
    for (auto hit : theirs)
        Check(hit == 50000 || hit == 100000, "Defender's hits are either halved or normal");
    Check(std::count(mine.begin(), mine.end(), 180000) >= 1 && mine.back() == 80000,
          "The armour and damage-taken modifiers act and then expire");
    Check(std::count(theirs.begin(), theirs.end(), 50000) >= 1 && theirs.back() == 100000,
          "The attack-damage modifier acts and then expires");

    // Undead: two different Undead heroes strip armour from every enemy; one does not.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    int archer = -1, weaver = -1, tank = -1;
    for (int i = 0; i < int(roster.units.size()); ++i)
    {
        if (roster.units[i].id == "wc_vn_bone_archer") archer = i;
        if (roster.units[i].id == "wc_vn_curse_weaver") weaver = i;
        if (roster.units[i].id == "wc_vn_shieldbearer") tank = i;
    }
    Check(archer >= 0 && weaver >= 0 && tank >= 0, "Bone Archer and Curse Weaver are in the executable roster");
    auto enemyArmour = [&](std::vector<wc::OwnedUnit> undead) {
        wc::Combat fight(roster, undead, {Unit(9, tank, 3, 3)}, 5);
        for (const auto &unit : fight.Units()) if (unit.side == 1) return unit.armor;
        return -999;
    };
    const int base = roster.units[tank].armor;
    Check(enemyArmour({Unit(1, archer, 3, 0)}) == base, "One Undead hero changes nothing");
    Check(enemyArmour({Unit(1, archer, 3, 0), Unit(2, weaver, 4, 0)}) == base - 10, "Two Undead heroes strip 10 armour from enemies");

    // The reworked abilities do what their tooltips say.
    auto firstModifier = [&](const char *hero, wc::ModifierStat stat) {
        int index = -1;
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == hero) index = i;
        Check(index >= 0, "Reworked hero is executable");
        wc::Combat fight(roster, {Unit(1, index, 3, 3)}, {Unit(2, tank, 3, 3)}, 21);
        Ticks(fight, 600);
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::StatModifier && event.stat == stat) return event.resolved;
        return wc::Int(0);
    };
    Check(firstModifier("wc_vn_jinxer", wc::ModifierStat::AttackDamage) == -2500, "Jinxer lowers the target's attack damage by a quarter");
    Check(firstModifier("wc_vn_bone_archer", wc::ModifierStat::Armor) == -10, "Bone Archer lowers the target's armour by 10");
    Check(firstModifier("wc_vn_curse_weaver", wc::ModifierStat::DamageTaken) == 2000, "Curse Weaver raises the damage its target takes by a fifth");
    Check(firstModifier("wc_vn_ironwall", wc::ModifierStat::Armor) == 30, "Ironwall gains 30 armour");
}
void FightStartAndPerSecondTraits()
{
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    const int tank = find("wc_vn_shieldbearer"), hammerer = find("wc_vn_hammerer"), rifleman = find("wc_vn_rifleman"),
        druid = find("wc_vn_grove_druid"), healer = find("wc_vn_chapel_healer"), bomber = find("wc_vn_bomber"),
        siege = find("wc_vn_siege_master"), scout = find("wc_vn_longbow_scout"), tide = find("wc_vn_tide_caller"),
        wisp = find("wc_vn_ember_wisp"), dart = find("wc_vn_dartblower");
    auto side0 = [&](const std::vector<wc::OwnedUnit> &team) {
        wc::Combat fight(roster, team, {Unit(9, tank, 3, 3)}, 3);
        std::vector<wc::CombatUnit> mine;
        for (const auto &unit : fight.Units()) if (unit.side == 0) mine.push_back(unit);
        return mine;
    };

    // Dwarf: a fight-start shield on the dwarves only.
    for (const auto &unit : side0({Unit(1, hammerer, 3, 3)})) Check(unit.shield == 0, "One Dwarf starts without a shield");
    for (const auto &unit : side0({Unit(1, hammerer, 3, 3), Unit(2, rifleman, 3, 0), Unit(3, scout, 4, 0)}))
        Check(unit.shield == (roster.units[unit.definition].race == "dwarf" ? unit.maxHealth / 5 : 0),
              "Two Dwarves start with a shield of a fifth of their health; others get none");

    // Sniper: reach and basic damage for the snipers only.
    for (const auto &unit : side0({Unit(1, scout, 3, 0), Unit(2, rifleman, 4, 0), Unit(3, hammerer, 3, 3)}))
    {
        const bool sniper = roster.units[unit.definition].unitClass == "sniper";
        Check(unit.rangeBonus == (sniper ? 1 : 0), "Two Snipers gain one cell of reach; others gain none");
        Check(!sniper || unit.basicBonus >= 1000, "Two Snipers gain basic attack damage");
    }
    for (const auto &unit : side0({Unit(1, scout, 3, 0), Unit(2, rifleman, 4, 0), Unit(3, dart, 2, 0), Unit(4, find("wc_vn_bone_archer"), 5, 0)}))
        Check(unit.rangeBonus == 2, "Four Snipers gain two cells of reach");

    // Elemental and Engineer and Priest set their values on the whole team.
    for (const auto &unit : side0({Unit(1, tide, 3, 0), Unit(2, wisp, 4, 0), Unit(3, hammerer, 3, 3)}))
        Check(unit.abilityReductionBp == 1500, "Two Elementals protect every ally from 15% of ability damage");
    for (const auto &unit : side0({Unit(1, bomber, 3, 0), Unit(2, siege, 4, 0), Unit(3, hammerer, 3, 3)}))
        Check(unit.manaPerSecond == 300, "Two Engineers give every ally three mana a second");
    for (const auto &unit : side0({Unit(1, druid, 3, 0), Unit(2, healer, 4, 0), Unit(3, hammerer, 3, 3)}))
        Check(unit.regenBp == 150, "Two Priests give every ally regeneration");

    // Mana per second lands exactly once a second and keeps the mana ledger balanced.
    {
        wc::Combat fight(roster, {Unit(1, bomber, 0, 0), Unit(2, siege, 7, 0)}, {Unit(9, tank, 0, 0)}, 8);
        Ticks(fight, 20);
        for (const auto &unit : fight.Units())
            if (unit.side == 0) Check(unit.manaFromRegen == 300, "One second of Engineer income is three mana");
        Ticks(fight, 20);
        for (const auto &unit : fight.Units())
            if (unit.side == 0 && unit.castsCommitted == 0 && unit.mana < unit.ability.mana.maximum)
                Check(unit.manaFromRegen == 600, "Two seconds of Engineer income is six mana");
    }

    // Regeneration heals a wounded ally by 1.5% of its health each second and never overheals.
    {
        wc::Combat fight(roster, {Unit(1, druid, 0, 0), Unit(2, healer, 7, 0), Unit(3, tank, 3, 3)}, {Unit(9, hammerer, 3, 3)}, 6);
        Ticks(fight, 300);
        int ticksSeen = 0;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Heal && event.source == event.target && event.action == 0)
            {
                ++ticksSeen;
                Check(event.tick % 20 == 0, "Regeneration lands once a second");
                wc::Int maxHealth = 0;
                for (const auto &unit : fight.Units()) if (unit.id == event.target) maxHealth = unit.maxHealth;
                Check(event.resolved > 0 && event.resolved <= (maxHealth * 150 + 5000) / 10000, "A regeneration tick is at most 1.5% of health");
            }
        Check(ticksSeen > 0, "A wounded ally regenerates under two Priests");
    }

    // Elemental: ability damage is reduced, basic attacks are not.
    {
        auto catalog = Quiet();
        catalog.units[0].attackDamage = 100000; catalog.units[0].attackRate = 1000;
        Enable(catalog, 0);
        auto &bolt = catalog.units[0].ability;
        bolt.mechanic = wc::AbilityMechanic::Standard; bolt.guardReductionBp = 0;
        bolt.effect = wc::Effect::Damage; bolt.selector = wc::Selector::CurrentEnemy; bolt.damageType = wc::DamageType::True;
        bolt.range = 8; bolt.radius = 0; bolt.maxTargets = 1; bolt.travelMs = 0; bolt.durationMs = 0;
        bolt.magnitude = {100000, 100000, 100000}; bolt.effects.clear();
        wc::TraitDef ward;
        ward.id = catalog.units[1].race; ward.stat = "ability_damage_taken_reduction_bp"; ward.team = true; ward.tiers = {{1, 1500}};
        catalog.traits.push_back(ward);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 17);
        Ticks(fight, 60);
        bool ability = false, basic = false;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && event.healthLoss > 0)
            {
                if (event.basicAttack) { basic = true; Check(event.healthLoss == 100000, "Basic attacks ignore the ability ward"); }
                else { ability = true; Check(event.healthLoss == 85000, "Ability damage is reduced by 15%"); }
            }
        Check(ability && basic, "The ward fixture lands both an ability and a basic attack");
    }

}
void Chance()
{
    // Quiet duel: unit 0 attacks unit 1 once a second for 1000; traits are added per test.
    auto duel = [](std::vector<wc::TraitDef> traits, int defenderArmor = 0, int defenderDamage = 0, int attackerDamage = 100000) {
        auto catalog = Quiet();
        catalog.units[0].attackDamage = attackerDamage; catalog.units[0].attackRate = 2500;
        catalog.units[1].attackDamage = defenderDamage; catalog.units[1].attackRate = 1000; catalog.units[1].armor = defenderArmor;
        catalog.traits = std::move(traits);
        return catalog;
    };
    auto trait = [](const wc::Catalog &catalog, int unit, const char *stat, int value) {
        wc::TraitDef t;
        t.id = catalog.units[unit].race; t.stat = stat; t.tiers = {{1, value}};
        return t;
    };
    const auto plain = Quiet();
    auto hits = [](const wc::Combat &fight, bool fromFirstSide) {
        std::vector<wc::CombatEvent> result;
        wc::Id first = 0;
        for (const auto &unit : fight.Units()) if (unit.side == 0) first = unit.id;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && !event.secondary && event.basicAttack && (event.source == first) == fromFirstSide)
                result.push_back(event);
        return result;
    };

    // No chance rule, no draw: the control catalogue's fights cannot move.
    {
        const auto canonical = wcvnext::WonderVNextCatalog();
        wc::Combat fight(canonical, {Unit(1, 0, 3, 3), Unit(2, 1, 4, 3), Unit(3, 7, 3, 0)}, {Unit(4, 3, 3, 3), Unit(5, 5, 4, 3)}, 4);
        Ticks(fight, 600);
        Check(fight.ChanceDraws() == 0, "A fight without chance rules draws nothing from the stream");
    }

    // Evasion: about half of the basic attacks miss, a miss deals nothing, and the fight replays exactly.
    {
        const auto catalog = duel({trait(plain, 1, "evasion_bp", 5000)}, 0, 0, 5000);
        auto run = [&](wc::Id seed) {
            wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, seed);
            Ticks(fight, 900);
            std::string pattern;
            for (const auto &event : hits(fight, true))
            {
                pattern += event.evaded ? 'm' : 'h';
                Check(event.evaded ? (event.resolved == 0 && event.healthLoss == 0) : event.healthLoss == 5000,
                      "A dodged attack deals nothing; a landed one deals full damage");
            }
            Check(fight.ChanceDraws() == int(pattern.size()), "Each basic attack against an evasive target draws once");
            return pattern;
        };
        const auto first = run(11);
        const int misses = int(std::count(first.begin(), first.end(), 'm'));
        Check(first.size() >= 60, "The evasion fixture lands enough attacks to judge the rate");
        Check(misses * 100 >= int(first.size()) * 33 && misses * 100 <= int(first.size()) * 67, "A 50% dodge chance misses about half the time");
        Check(run(11) == first, "The same seed replays the same hits and misses");
        Check(run(12) != first, "A different seed gives a different sequence");
    }

    // Crit: a critical basic attack deals one and a half times the damage and says so.
    {
        const auto catalog = duel({trait(plain, 0, "crit_chance_bp", 5000)}, 0, 0, 5000);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 21);
        Ticks(fight, 900);
        int crits = 0, normal = 0;
        for (const auto &event : hits(fight, true))
        {
            Check(event.healthLoss == (event.critical ? 7500 : 5000), "A crit deals 150% and a normal hit 100%");
            (event.critical ? crits : normal) += 1;
        }
        Check(crits > 10 && normal > 10, "A 50% crit chance produces both crits and normal hits");
    }

    // Lifesteal: the attacker heals a fifth of the health it removes, never above its maximum.
    {
        auto lifesteal = trait(plain, 0, "lifesteal_bp", 2000);
        lifesteal.team = true;
        const auto catalog = duel({lifesteal}, 0, 50000);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 31);
        Ticks(fight, 400);
        int full = 0, heals = 0;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Heal && event.secondary)
            {
                ++heals;
                Check(event.source == event.target && event.resolved <= 20000 && event.requested == 20000, "Lifesteal returns a fifth of the damage dealt");
                full += event.resolved == 20000;
            }
        Check(heals > 5 && full > 0, "A wounded attacker with lifesteal heals on its hits");
        for (const auto &unit : fight.Units()) Check(unit.health <= unit.maxHealth, "Lifesteal never overheals");
    }

    // Bonus true damage: 30% of the health removed lands again, ignoring armour, and never chains.
    {
        const auto catalog = duel({trait(plain, 0, "bonus_true_damage_bp", 3000)}, 25);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 41);
        Ticks(fight, 60);
        int primary = 0, bonus = 0;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage)
            {
                if (event.secondary) { ++bonus; Check(event.damageType == wc::DamageType::True && event.healthLoss == 24000, "Bonus true damage is 30% of the 800 that got through armour"); }
                else if (event.basicAttack && event.healthLoss > 0) { ++primary; Check(event.healthLoss == 80000, "The main hit is reduced by armour as usual"); }
            }
        Check(primary > 5 && bonus == primary, "Every landed hit carries exactly one bonus hit");
    }

    // Reflect: a defender with a reflect modifier returns half of what it loses, as true damage, once.
    {
        auto catalog = duel({}, 0, 0);
        Enable(catalog, 1);
        auto &thorns = catalog.units[1].ability;
        thorns.mechanic = wc::AbilityMechanic::Standard; thorns.guardReductionBp = 0; thorns.momentumPerStepBp = 0; thorns.maxMomentumSteps = 0;
        thorns.effect = wc::Effect::StatModifier; thorns.selector = wc::Selector::Self; thorns.allowSelf = true;
        thorns.range = 1; thorns.radius = 0; thorns.maxTargets = 1; thorns.maxDash = 0; thorns.travelMs = 0; thorns.durationMs = 60000; thorns.magnitude = {5000, 5000, 5000};
        thorns.effects = {{wc::Effect::StatModifier, wc::DamageType::Physical, 60000, {5000, 5000, 5000}, 0, false, wc::Selector::Self, wc::ModifierStat::Reflect}};
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 51);
        Ticks(fight, 200);
        wc::Id attacker = 0;
        for (const auto &unit : fight.Units()) if (unit.side == 0) attacker = unit.id;
        int reflected = 0;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && event.secondary)
            {
                ++reflected;
                Check(event.target == attacker && event.damageType == wc::DamageType::True && event.healthLoss == 50000, "Half of each hit comes back as true damage");
            }
        Check(reflected > 5, "Reflect answers the attacker's hits");
    }

    // The authored traits set the right values, and Scaleguard's cast is a reflect modifier.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    auto team = [&](const std::vector<wc::OwnedUnit> &units) {
        wc::Combat fight(roster, units, {Unit(9, find("wc_vn_shieldbearer"), 3, 3)}, 3);
        std::vector<wc::CombatUnit> mine;
        for (const auto &unit : fight.Units()) if (unit.side == 0) mine.push_back(unit);
        return mine;
    };
    for (const auto &unit : team({Unit(1, find("wc_vn_longbow_scout"), 3, 0), Unit(2, find("wc_vn_grove_druid"), 4, 0), Unit(3, find("wc_vn_hammerer"), 3, 3)}))
        Check(unit.evasionBp == (roster.units[unit.definition].race == "elf" ? 2000 : 0), "Two Elves dodge a fifth of basic attacks; others do not");
    for (const auto &unit : team({Unit(1, find("wc_vn_hookjaw"), 3, 3), Unit(2, find("wc_vn_foxclaw"), 4, 3), Unit(3, find("wc_vn_hammerer"), 2, 3)}))
        Check(unit.critChanceBp == (roster.units[unit.definition].unitClass == "assassin" ? 1500 : 0), "Two Assassins crit 15% of the time; others do not");
    for (const auto &unit : team({Unit(1, find("wc_vn_soul_jailer"), 3, 0), Unit(2, find("wc_vn_curse_weaver"), 4, 0), Unit(3, find("wc_vn_hammerer"), 3, 3)}))
        Check(unit.lifestealBp == 1000, "Two Warlocks give every ally 10% lifesteal");
    {
        wc::Combat fight(roster, {Unit(1, find("wc_vn_scaleguard"), 3, 3)}, {Unit(2, find("wc_vn_hammerer"), 3, 3)}, 61);
        Ticks(fight, 400);
        bool cast = false, returned = false;
        for (const auto &event : fight.Events())
        {
            cast |= event.effect == wc::Effect::StatModifier && event.stat == wc::ModifierStat::Reflect && event.resolved == 3000;
            returned |= event.effect == wc::Effect::Damage && event.secondary && event.damageType == wc::DamageType::True && event.healthLoss > 0;
        }
        Check(cast && returned, "Scaleguard raises a 30% reflect and attackers are hurt by it");
    }
}
void RepeatingEffects()
{
    auto caster = [](int repeatSeconds, wc::Selector selector, bool follow, int cooldownMs = 60000) {
        auto catalog = Quiet();
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = wc::Effect::Damage; ability.selector = selector; ability.damageType = wc::DamageType::True;
        ability.range = 8; ability.radius = 1; ability.maxTargets = 8; ability.travelMs = 0; ability.durationMs = 0;
        ability.magnitude = {1000, 1000, 1000}; ability.cooldownMs = cooldownMs;
        ability.effects = {{wc::Effect::Damage, wc::DamageType::True, repeatSeconds * 1000, {1000, 1000, 1000}, 0, false, selector,
                            wc::ModifierStat::AttackRate, 1000, follow}};
        return catalog;
    };
    auto ability = [](const wc::Combat &fight) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && !event.basicAttack && event.healthLoss > 0) result.push_back(event);
        return result;
    };

    // Damage over time: one hit a second for the duration, then it stops.
    {
        const auto catalog = caster(3, wc::Selector::CurrentEnemy, false);
        auto valid = wcvnext::WonderVNextCatalog();
        valid.units[0].ability = catalog.units[0].ability;
        if (!valid.Validate().empty()) throw std::runtime_error("A repeating damage effect validates: " + valid.Validate());
        auto wrong = valid;
        wrong.units[0].ability.effects[0].repeatMs = 25;
        Check(!wrong.Validate().empty(), "A repeat interval shorter than a tick is rejected");
        wrong = valid;
        wrong.units[0].ability.effects[0].effect = wc::Effect::Stun; wrong.units[0].ability.effects[0].magnitude = {0, 0, 0};
        Check(!wrong.Validate().empty(), "Only damage and healing may repeat");
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 71);
        Ticks(fight, 200);
        const auto ticks = ability(fight);
        Check(ticks.size() == 3, "Three seconds of damage over time is three hits");
        Check(ticks[1].tick - ticks[0].tick == 20 && ticks[2].tick - ticks[1].tick == 20, "The hits are one second apart");
        for (const auto &hit : ticks) Check(hit.healthLoss == 1000 && hit.target == ticks[0].target, "Each hit deals the per-second amount to the same target");
    }

    // Recasting refreshes: the target is never hit twice in the same tick by the same effect.
    {
        const auto catalog = caster(3, wc::Selector::CurrentEnemy, false, 2000);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 72);
        Ticks(fight, 300);
        const auto ticks = ability(fight);
        Check(ticks.size() > 6, "A recast damage over time keeps hitting");
        for (std::size_t i = 1; i < ticks.size(); ++i)
            Check(ticks[i].tick != ticks[i - 1].tick, "A refreshed damage over time never doubles up");
    }

    // The damage keeps coming after its caster has fallen.
    {
        auto catalog = caster(3, wc::Selector::CurrentEnemy, false);
        catalog.units[0].health = 1000;
        // A melee enemy walks to the nearer unit, the caster, and kills it after the cast.
        catalog.units[1].attackDamage = 100000; catalog.units[1].attackWindupMs = 500; catalog.units[1].range = 1;
        // A second ally far away keeps the fight going after the caster falls.
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3), Unit(3, 2, 7, 0)}, {Unit(2, 1, 3, 3)}, 73);
        Ticks(fight, 200);
        const auto ticks = ability(fight);
        bool casterDead = false;
        for (const auto &unit : fight.Units()) if (unit.side == 0 && unit.definition == 0) casterDead = unit.health == 0;
        if (!(casterDead && ticks.size() == 3)) throw std::runtime_error("Damage over time finishes even though its caster died: dead=" + std::to_string(casterDead) + " hits=" + std::to_string(ticks.size()) + " events=" + std::to_string(fight.Events().size()) + " complete=" + std::to_string(fight.Result().complete) + " tick=" + std::to_string(fight.CurrentTick()));
        ++assertions;
    }

    // A ground zone: every second, every enemy inside it is hit; one outside never is.
    {
        const auto catalog = caster(3, wc::Selector::CurrentEnemyArea, false);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3), Unit(3, 2, 4, 3), Unit(4, 3, 7, 0)}, 74);
        Ticks(fight, 200);
        const auto ticks = ability(fight);
        std::set<wc::Id> struck;
        for (const auto &hit : ticks) struck.insert(hit.target);
        Check(ticks.size() == 6 && struck.size() == 2, "A three-second zone hits both enemies inside it three times and nobody else");
    }

    // An aura follows its caster and burns whoever is adjacent each second.
    {
        auto catalog = caster(3, wc::Selector::AdjacentEnemies, true);
        catalog.units[0].range = 1;
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, 75);
        Ticks(fight, 300);
        const auto ticks = ability(fight);
        Check(ticks.size() == 3, "A three-second aura burns the adjacent enemy three times");
    }

    // The authored heroes.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    auto casts = [&](const char *hero, wc::DamageType type) {
        wc::Combat fight(roster, {Unit(1, find(hero), 3, 3)}, {Unit(2, find("wc_vn_shieldbearer"), 3, 3)}, 76);
        Ticks(fight, 700);
        std::map<wc::Id, int> perAction;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && !event.basicAttack && !event.secondary && event.damageType == type && event.healthLoss + event.absorbed > 0)
                ++perAction[event.action];
        int most = 0;
        for (const auto &entry : perAction) most = std::max(most, entry.second);
        return most;
    };
    Check(casts("wc_vn_dartblower", wc::DamageType::Magic) == 4, "Dartblower's poison hits four times over four seconds");
    Check(casts("wc_vn_foxclaw", wc::DamageType::Physical) == 5, "Foxclaw strikes once and the bleed hits four times");
    Check(casts("wc_vn_hellblade", wc::DamageType::Magic) >= 3, "Hellblade's aura burns the enemy beside him every second");
    Check(casts("wc_vn_pit_lord", wc::DamageType::Magic) >= 3, "Pit Lord's fire keeps falling on the target's cell");
}
void SelectorsAndShapes()
{
    // The caster stands at (3,3). Enemy cells are given in their own half and mirror onto the board:
    // enemy (4,3) is directly ahead at (3,4), enemy (4,1) is behind it at (3,6), and so on.
    auto caster = [](wc::Selector selector, int radius, int maxTargets, int range = 8) {
        auto catalog = Quiet();
        catalog.units[0].range = 1; // a melee caster always targets the enemy directly ahead
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = wc::Effect::Damage; ability.selector = selector; ability.damageType = wc::DamageType::True;
        ability.range = range; ability.radius = radius; ability.maxTargets = maxTargets; ability.travelMs = 0; ability.durationMs = 0;
        ability.magnitude = {1000, 1000, 1000}; ability.effects.clear();
        return catalog;
    };
    auto struck = [](const wc::Combat &fight, wc::Effect effect = wc::Effect::Damage) {
        std::vector<int> ids;
        for (const auto &event : fight.Events())
            if (event.effect == effect && !event.basicAttack && (effect != wc::Effect::Damage || event.healthLoss > 0))
                ids.push_back(int(event.target & 0xFFFFF));
        return ids;
    };
    auto fight = [&](const wc::Catalog &catalog, std::vector<wc::OwnedUnit> enemies, wc::Id seed, std::vector<wc::OwnedUnit> allies = {}) {
        allies.insert(allies.begin(), Unit(1, 0, 3, 3));
        wc::Combat combat(catalog, allies, enemies, seed);
        Ticks(combat, 100);
        return combat;
    };

    Check(struck(fight(caster(wc::Selector::FarthestEnemy, 0, 1), {Unit(10, 1, 4, 3), Unit(11, 2, 4, 0)}, 81)) == std::vector<int>{11},
          "Farthest enemy picks the one at the back");
    {
        const auto hit = struck(fight(caster(wc::Selector::EnemyLine, 0, 8), {Unit(10, 1, 4, 3), Unit(11, 2, 4, 1), Unit(12, 3, 0, 3)}, 82));
        Check(hit.size() == 2 && std::count(hit.begin(), hit.end(), 10) == 1 && std::count(hit.begin(), hit.end(), 11) == 1,
              "A line hits the target and the enemy behind it, and nobody to the side");
    }
    {
        const auto hit = struck(fight(caster(wc::Selector::EnemyCone, 3, 8), {Unit(10, 1, 4, 3), Unit(11, 2, 3, 2), Unit(12, 3, 0, 3), Unit(13, 4, 4, 0)}, 83));
        Check(hit.size() == 2 && std::count(hit.begin(), hit.end(), 10) == 1 && std::count(hit.begin(), hit.end(), 11) == 1,
              "A cone hits enemies inside its angle and length, not one far to the side or beyond its reach");
    }
    {
        const auto combat = fight(caster(wc::Selector::ChainFromCurrentEnemy, 2, 3), {Unit(10, 1, 4, 3), Unit(11, 2, 3, 2), Unit(12, 3, 2, 1), Unit(13, 4, 0, 3)}, 84);
        Check(struck(combat) == std::vector<int>({10, 11, 12}), "A chain jumps to the nearest enemy each time and stops at its limit");
        std::vector<int> ticks;
        for (const auto &event : combat.Events()) if (event.effect == wc::Effect::Damage && !event.basicAttack && event.healthLoss > 0) ticks.push_back(event.tick);
        Check(ticks.size() == 3 && ticks[1] - ticks[0] == 2 && ticks[2] - ticks[1] == 2, "Each jump of a chain lands a moment after the last");
    }
    {
        const auto hit = struck(fight(caster(wc::Selector::DensestEnemyArea, 1, 8), {Unit(10, 1, 4, 3), Unit(11, 2, 3, 3), Unit(12, 3, 0, 0)}, 85));
        Check(hit.size() == 2 && std::count(hit.begin(), hit.end(), 12) == 0, "The densest area lands on the pair, not on the enemy standing alone");
    }
    {
        const std::vector<wc::OwnedUnit> spread{Unit(10, 1, 0, 0), Unit(11, 2, 3, 0), Unit(12, 3, 6, 0), Unit(13, 4, 0, 3), Unit(14, 5, 4, 3)};
        const auto catalog = caster(wc::Selector::RandomEnemyAreas, 1, 3);
        const auto first = fight(catalog, spread, 86);
        const auto hit = struck(first);
        Check(hit.size() == 3 && std::set<int>(hit.begin(), hit.end()).size() == 3, "Three rockets land on three different enemies");
        Check(first.ChanceDraws() == 3, "Each rocket takes one draw from the fight's stream");
        Check(struck(fight(catalog, spread, 86)) == hit, "The same seed sends the rockets to the same enemies");
    }
    {
        auto catalog = caster(wc::Selector::AllAllies, 0, 10);
        auto &ward = catalog.units[0].ability;
        ward.effect = wc::Effect::Shield; ward.durationMs = 3000; ward.allowSelf = true;
        const auto hit = struck(fight(catalog, {Unit(10, 1, 4, 3)}, 87, {Unit(2, 2, 0, 0), Unit(3, 3, 7, 0)}), wc::Effect::Shield);
        Check(hit.size() == 3 && std::set<int>(hit.begin(), hit.end()) == std::set<int>({1, 2, 3}), "All allies reaches every ally wherever it stands");
    }
    {
        auto valid = wcvnext::WonderVNextCatalog();
        valid.units[0].ability = caster(wc::Selector::EnemyCone, 3, 8).units[0].ability;
        if (!valid.Validate().empty()) throw std::runtime_error("A cone ability validates: " + valid.Validate());
        ++assertions;
    }

    // The authored heroes.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    const int tank = find("wc_vn_shieldbearer"), fighter = find("wc_vn_hammerer"), scout = find("wc_vn_longbow_scout");
    auto mostTargets = [&](const char *hero, wc::Effect effect, std::vector<wc::OwnedUnit> allies, std::vector<wc::OwnedUnit> enemies) {
        allies.insert(allies.begin(), Unit(1, find(hero), 3, 0));
        wc::Combat combat(roster, allies, enemies, 88);
        Ticks(combat, 800);
        std::map<wc::Id, std::set<wc::Id>> targets;
        for (const auto &event : combat.Events())
            if (event.effect == effect && !event.basicAttack && !event.secondary && event.action != 0 && event.resolved > 0 &&
                int(event.source & 0xFFFFF) == 1)
                targets[event.action].insert(event.target);
        std::size_t most = 0;
        for (const auto &entry : targets) most = std::max(most, entry.second.size());
        return int(most);
    };
    const std::vector<wc::OwnedUnit> pair{Unit(10, tank, 4, 3), Unit(11, fighter, 3, 3)};
    Check(mostTargets("wc_vn_storm_spirit", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 2, "Storm Spirit's lightning jumps to a second enemy");
    Check(mostTargets("wc_vn_bonechanter", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 2, "Bonechanter's drain chains to a second enemy");
    Check(mostTargets("wc_vn_flame_regent", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 1, "Flame Regent's cone burns enemies");
    Check(mostTargets("wc_vn_siege_master", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 2, "Siege Master's shell lands on the pair");
    Check(mostTargets("wc_vn_forge_king", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 1, "Forge King's rockets land");
    Check(mostTargets("wc_vn_longbow_scout", wc::Effect::Damage, {Unit(2, tank, 3, 3)}, pair) >= 1, "Longbow Scout's arrow lands");
    Check(mostTargets("wc_vn_dawn_oracle", wc::Effect::Heal, {Unit(2, tank, 3, 3), Unit(3, fighter, 4, 3)}, pair) >= 1, "Dawn Oracle heals wounded allies");
    {
        wc::Combat combat(roster, {Unit(1, find("wc_vn_rifleman"), 3, 0), Unit(2, tank, 3, 3)}, {Unit(10, tank, 4, 3), Unit(11, scout, 4, 0)}, 89);
        Ticks(combat, 800);
        int shotAt = 0;
        for (const auto &event : combat.Events())
            if (!shotAt && event.effect == wc::Effect::Damage && !event.basicAttack && !event.secondary && int(event.source & 0xFFFFF) == 1)
                shotAt = int(event.target & 0xFFFFF);
        Check(shotAt == 11, "Rifleman's heavy shot goes to the enemy at the back");
    }
}
void Statuses()
{
    // Unit 0 casts on the enemy it is fighting; that enemy (unit 1) swings once a second.
    auto fixture = [](wc::Effect effect, int ms) {
        auto catalog = Quiet();
        catalog.rules.nearestReachableTarget = true;
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = effect; ability.selector = wc::Selector::CurrentEnemy; ability.damageType = wc::DamageType::True;
        ability.range = 8; ability.radius = 8; ability.maxTargets = 8; ability.travelMs = 0; ability.durationMs = ms;
        ability.magnitude = {ms, ms, ms}; ability.effects.clear();
        catalog.units[1].attackRate = 1000; catalog.units[1].projectileTravelMs = 0;
        return catalog;
    };
    auto swings = [](const wc::Combat &fight, int unit, int from, int to) {
        int count = 0;
        for (const auto &event : fight.Events())
            count += event.basicAttack && int(event.source & 0xFFFFF) == unit && event.tick >= from && event.tick < to;
        return count;
    };
    auto of = [](const wc::Combat &fight, wc::Effect effect) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events()) if (event.effect == effect && !event.basicAttack) result.push_back(event);
        return result;
    };

    // Hex: no attacks for the duration, then attacks resume.
    {
        const auto catalog = fixture(wc::Effect::Hex, 2000);
        auto valid = wcvnext::WonderVNextCatalog();
        valid.units[0].ability = catalog.units[0].ability;
        if (!valid.Validate().empty()) throw std::runtime_error("A hex ability validates: " + valid.Validate());
        auto wrong = valid;
        wrong.units[0].ability.durationMs = 1000;
        Check(!wrong.Validate().empty(), "A status repeats its one-star duration");
        wrong = valid;
        wrong.units[0].ability.durationMs = 2025; wrong.units[0].ability.magnitude = {2025, 2025, 2025};
        Check(!wrong.Validate().empty(), "A status duration is a whole number of ticks");
        wrong = valid;
        wrong.units[0].ability.effect = wc::Effect::ManaDrain;
        Check(!wrong.Validate().empty(), "A mana drain has no duration");
        auto plain = catalog;
        plain.units[0].ability.enabled = false;
        wc::Combat free(plain, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 91);
        wc::Combat hexed(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 91);
        Ticks(free, 100); Ticks(hexed, 100);
        const auto hexes = of(hexed, wc::Effect::Hex);
        Check(hexes.size() == 1 && hexes[0].tick == 2 && hexes[0].resolved == 2000 && int(hexes[0].target & 0xFFFFF) == 10,
              "The hex lands on the current enemy and reports its duration");
        Check(swings(free, 10, 10, 42) > 0, "Left alone, the enemy keeps attacking");
        Check(swings(hexed, 10, 10, 42) == 0, "A hexed unit performs no attack for the duration");
        Check(swings(hexed, 10, 42, 100) > 0, "It attacks again once the hex ends");
    }

    // The same status does not stack: the one that ends later stays.
    {
        auto catalog = fixture(wc::Effect::Hex, 3000);
        catalog.units[0].ability.effects = {{wc::Effect::Hex, wc::DamageType::True, 3000, {3000, 3000, 3000}},
                                            {wc::Effect::Hex, wc::DamageType::True, 1000, {1000, 1000, 1000}, 500}};
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 92);
        Ticks(fight, 20);
        const auto hexes = of(fight, wc::Effect::Hex);
        Check(hexes.size() == 2 && hexes[0].resolved == 3000 && hexes[1].resolved == 0 &&
              fight.Units()[1].statuses[int(wc::UnitStatus::Hex)].expiry == hexes[0].tick + 60,
              "A shorter hex does not replace a longer one");
    }

    // Silence: no casts for the duration, but attacks continue.
    {
        auto catalog = fixture(wc::Effect::Silence, 3000);
        Enable(catalog, 1);
        auto &bolt = catalog.units[1].ability;
        bolt.mechanic = wc::AbilityMechanic::Standard; bolt.guardReductionBp = 0;
        bolt.effect = wc::Effect::Damage; bolt.selector = wc::Selector::CurrentEnemy; bolt.damageType = wc::DamageType::True;
        bolt.range = 8; bolt.radius = 0; bolt.maxTargets = 1; bolt.travelMs = 0; bolt.durationMs = 0;
        bolt.magnitude = {1000, 1000, 1000}; bolt.effects.clear();
        bolt.firstCastMs = 500; bolt.cooldownMs = 500;
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 93);
        Ticks(fight, 120);
        int early = 0, late = 0;
        for (const auto &event : of(fight, wc::Effect::Damage))
            if (int(event.source & 0xFFFFF) == 10) ++(event.tick < 62 ? early : late);
        Check(early == 0 && late > 0, "A silenced unit casts nothing until the silence ends");
        Check(swings(fight, 10, 10, 62) > 0, "A silenced unit still attacks");
    }

    // Taunt: the enemy leaves its target for the taunter, and goes back when the taunter falls.
    {
        auto catalog = fixture(wc::Effect::Taunt, 2000);
        catalog.units[0].ability.selector = wc::Selector::AdjacentEnemies;
        catalog.units[0].health = 1000;
        catalog.units[1].attackDamage = 100000;
        wc::Combat fight(catalog, {Unit(1, 0, 0, 0), Unit(2, 2, 3, 3)}, {Unit(10, 1, 4, 3)}, 94);
        Ticks(fight, 100);
        std::vector<int> order;
        for (const auto &event : fight.Events())
            if (event.basicAttack && int(event.source & 0xFFFFF) == 10 &&
                (order.empty() || order.back() != int(event.target & 0xFFFFF)))
                order.push_back(int(event.target & 0xFFFFF));
        Check(order == std::vector<int>({2, 1, 2}), "A taunted unit switches to the taunter and back when the taunter dies");
        Check(fight.Units()[0].health == 0 && of(fight, wc::Effect::Taunt).size() == 1, "The taunter drew the blow that killed it");
    }

    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    const int tank = find("wc_vn_shieldbearer"), fighter = find("wc_vn_hammerer"), scout = find("wc_vn_longbow_scout");

    // Mana drain: takes what is there, never below zero, and the ledger still balances.
    {
        auto catalog = roster;
        catalog.traits.clear();
        for (auto &unit : catalog.units) { unit.attackDamage = 0; unit.health = 1000000; }
        auto &ability = catalog.units[find("wc_vn_void_wyrm")].ability;
        ability.mana = {}; ability.firstCastMs = 0; ability.cooldownMs = 500; ability.castMs = 50; ability.recoveryMs = 50;
        ability.effects = {{wc::Effect::ManaDrain, wc::DamageType::Magic, 0, {4000, 4000, 4000}}};
        catalog.units[fighter].ability.mana.starting = 6000;
        wc::Combat fight(catalog, {Unit(1, find("wc_vn_void_wyrm"), 3, 3)}, {Unit(10, fighter, 4, 3)}, 95);
        Ticks(fight, 200);
        const auto drains = of(fight, wc::Effect::ManaDrain);
        Check(drains.size() >= 3 && drains[0].resolved == 4000 && drains[1].resolved == 2000 && drains[2].resolved == 0,
              "A mana drain takes what is there and stops at zero");
        Check(fight.Units()[1].mana == 0 && fight.Units()[1].manaDrained == 6000, "Drained mana is accounted for");
    }

    // A hexed hero gains no mana and starts no swing or cast.
    {
        wc::Combat fight(roster, {Unit(1, find("wc_vn_owl_seer"), 3, 0), Unit(2, tank, 3, 3)}, {Unit(10, find("wc_vn_earthbreaker"), 4, 3)}, 96);
        int hexedTicks = 0;
        bool frozen = true;
        for (int tick = 0; tick < 800 && !fight.Result().complete; ++tick)
        {
            const auto before = fight.Units()[2];
            const bool was = before.statuses[int(wc::UnitStatus::Hex)].expiry > fight.CurrentTick();
            fight.Tick();
            const auto &after = fight.Units()[2];
            if (was && after.statuses[int(wc::UnitStatus::Hex)].expiry > fight.CurrentTick() && after.health > 0)
            {
                ++hexedTicks;
                frozen = frozen && after.mana == before.mana && after.state != wc::ActionState::AttackWindup &&
                         after.state != wc::ActionState::CastWindup;
            }
        }
        Check(hexedTicks >= 40, "Owl Seer hexes the enemy it is fighting");
        Check(frozen, "A hexed hero gains no mana and starts no swing or cast");
    }

    // Shaman trait: 1 / 2 random enemies hexed for three seconds as the fight starts.
    {
        const std::vector<wc::OwnedUnit> foes{Unit(10, tank, 4, 3), Unit(11, fighter, 3, 3), Unit(12, scout, 4, 0)};
        auto opening = [&](const wc::Combat &fight) {
            std::vector<int> ids;
            for (const auto &event : fight.Events())
                if (event.effect == wc::Effect::Hex && event.tick == 0 && event.resolved == 3000) ids.push_back(int(event.target & 0xFFFFF));
            return ids;
        };
        const int jinxer = find("wc_vn_jinxer"), drummer = find("wc_vn_blood_drummer");
        wc::Combat one(roster, {Unit(1, jinxer, 3, 0)}, foes, 97);
        Check(opening(one).empty() && one.ChanceDraws() == 0, "One Shaman hexes nobody");
        wc::Combat two(roster, {Unit(1, jinxer, 3, 0), Unit(2, drummer, 4, 0)}, foes, 97);
        const auto hexed = opening(two);
        Check(hexed.size() == 1 && two.ChanceDraws() == 1, "Two Shamans hex one enemy, with one draw from the fight's stream");
        wc::Combat again(roster, {Unit(1, jinxer, 3, 0), Unit(2, drummer, 4, 0)}, foes, 97);
        Check(opening(again) == hexed, "The same seed hexes the same enemy");
        for (const auto &unit : two.Units())
            if (unit.side == 1)
                Check((unit.statuses[int(wc::UnitStatus::Hex)].expiry == 60) == (int(unit.id & 0xFFFFF) == hexed[0]),
                      "Only the chosen enemy is hexed, for three seconds");
        Ticks(two, 70);
        int early = 0;
        for (const auto &event : two.Events())
            early += event.basicAttack && int(event.source & 0xFFFFF) == hexed[0] && event.tick <= 60;
        Check(early == 0, "The hexed enemy makes no attack in its first three seconds");
        wc::Combat four(roster, {Unit(1, jinxer, 3, 0), Unit(2, drummer, 4, 0), Unit(3, find("wc_vn_owl_seer"), 2, 0),
                                 Unit(4, find("wc_vn_storm_spirit"), 5, 0)}, foes, 97);
        const auto pair = opening(four);
        Check(pair.size() == 2 && pair[0] != pair[1] && four.ChanceDraws() == 2, "Four Shamans hex two different enemies");
    }

    // The authored heroes.
    auto emits = [&](const char *hero, wc::Effect effect, bool behindTank = false) {
        // Behind a tank the hero is still within three cells of both enemies.
        std::vector<wc::OwnedUnit> allies{Unit(1, find(hero), 3, behindTank ? 1 : 3)};
        if (behindTank) allies.push_back(Unit(2, tank, 3, 3));
        wc::Combat fight(roster, allies, {Unit(10, fighter, 4, 3), Unit(11, find("wc_vn_bearguard"), 3, 3)}, 98);
        Ticks(fight, 800);
        int count = 0;
        for (const auto &event : fight.Events())
            count += event.effect == effect && int(event.source & 0xFFFFF) == 1 && event.resolved > 0;
        return count;
    };
    Check(emits("wc_vn_ironwall", wc::Effect::Taunt) > 0, "Ironwall taunts the enemies beside him");
    Check(emits("wc_vn_owl_seer", wc::Effect::Hex) > 0, "Owl Seer hexes");
    Check(emits("wc_vn_void_wyrm", wc::Effect::Silence, true) >= 2, "Void Wyrm silences the enemies around it");
    Check(emits("wc_vn_void_wyrm", wc::Effect::ManaDrain, true) > 0, "Void Wyrm drains mana");
}
void BlinkAndLeap()
{
    // The caster stands at (3,3). Enemy cells are given in their own half and mirror onto the board:
    // enemy (4,3) stands at (3,4), enemy (4,1) at (3,6), enemy (4,0) at (3,7).
    auto caster = [](wc::Selector target, wc::Selector cell, bool critical = false) {
        auto catalog = Quiet();
        catalog.rules.nearestReachableTarget = true;
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = wc::Effect::Damage; ability.selector = target; ability.damageType = wc::DamageType::True;
        ability.range = 8; ability.radius = 0; ability.maxTargets = 8; ability.maxDash = 4; ability.travelMs = 0; ability.durationMs = 0;
        ability.magnitude = {1000, 1000, 1000};
        wc::AbilityEffect hit{wc::Effect::Damage, wc::DamageType::True, 0, {1000, 1000, 1000}};
        hit.critical = critical;
        ability.effects = {{wc::Effect::Blink, wc::DamageType::True, 0, {0, 0, 0}, 0, true, cell}, hit};
        return catalog;
    };
    auto blinks = [](const wc::Combat &fight) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events()) if (event.effect == wc::Effect::Blink) result.push_back(event);
        return result;
    };
    auto struck = [](const wc::Combat &fight) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage && !event.basicAttack && event.healthLoss > 0) result.push_back(event);
        return result;
    };

    // Beside the target: the free neighbouring cell nearest the caster.
    {
        const auto catalog = caster(wc::Selector::CurrentEnemy, wc::Selector::CellBesideTarget);
        auto valid = wcvnext::WonderVNextCatalog();
        valid.units[0].ability = catalog.units[0].ability;
        if (!valid.Validate().empty()) throw std::runtime_error("A blink ability validates: " + valid.Validate());
        auto wrong = valid;
        wrong.units[0].ability.effects[0].ownSelector = false;
        Check(!wrong.Validate().empty(), "A blink needs its own cell selector");
        wrong = valid;
        wrong.units[0].ability.effects[1].ownSelector = true; wrong.units[0].ability.effects[1].selector = wc::Selector::CellBesideTarget;
        Check(!wrong.Validate().empty(), "Only a blink may name a cell selector");
        wrong = valid;
        wrong.units[0].ability.effects[1].effect = wc::Effect::Heal; wrong.units[0].ability.effects[1].critical = true;
        Check(!wrong.Validate().empty(), "Only damage can be a guaranteed critical");
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 1)}, 101);
        Ticks(fight, 5);
        const auto moves = blinks(fight);
        Check(moves.size() == 1 && moves[0].origin == wc::Cell{3, 3} && moves[0].cell == wc::Cell{3, 5} &&
              fight.Units()[0].cell == wc::Cell{3, 5}, "A blink beside the target lands on the nearest free neighbouring cell");
        Check(struck(fight).size() == 1 && !struck(fight)[0].critical && struck(fight)[0].healthLoss == 1000,
              "The rest of the chain follows the blink");
        wc::Combat close(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 101);
        Ticks(close, 5);
        Check(blinks(close).empty() && struck(close).size() == 1, "Already beside the target, the caster stays and still strikes");
    }

    // Behind the target, and a guaranteed critical hit.
    {
        const auto catalog = caster(wc::Selector::FarthestEnemy, wc::Selector::CellBehindTarget, true);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3), Unit(11, 2, 4, 1)}, 102);
        Ticks(fight, 5);
        Check(blinks(fight).size() == 1 && fight.Units()[0].cell == wc::Cell{3, 7}, "A blink behind the farthest enemy lands straight past it");
        const auto hits = struck(fight);
        Check(hits.size() == 1 && int(hits[0].target & 0xFFFFF) == 11 && hits[0].critical && hits[0].healthLoss == 1500,
              "The strike is a critical hit for one and a half times its damage");
        Check(fight.ChanceDraws() == 0, "A guaranteed critical draws nothing from the fight's stream");
        wc::Combat edge(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3), Unit(11, 2, 4, 0)}, 102);
        Ticks(edge, 5);
        Check(edge.Units()[0].cell == wc::Cell{2, 7}, "With the board edge behind the target, the blink lands beside it");
    }

    // No free cell: the blink is skipped and the rest of the chain still runs.
    {
        const auto catalog = caster(wc::Selector::FarthestEnemy, wc::Selector::CellBehindTarget);
        wc::Combat fight(catalog, {Unit(1, 0, 0, 0), Unit(2, 2, 6, 7), Unit(3, 3, 7, 6), Unit(4, 4, 6, 6)}, {Unit(10, 1, 0, 0)}, 103);
        Ticks(fight, 5);
        Check(blinks(fight).empty() && fight.Units()[0].cell == wc::Cell{0, 0}, "A blink with no free cell does not move the caster");
        Check(struck(fight).size() == 1, "The strike still lands when the blink is skipped");
    }

    // A dash along a line: everyone on the line within the dash is hit, and the caster lands on the last free cell.
    {
        auto catalog = caster(wc::Selector::CurrentEnemy, wc::Selector::CellThroughTarget);
        auto &effects = catalog.units[0].ability.effects;
        effects[1].ownSelector = true; effects[1].selector = wc::Selector::EnemyLine;
        std::swap(effects[0], effects[1]);
        const std::vector<wc::OwnedUnit> foes{Unit(10, 1, 4, 3), Unit(11, 2, 4, 1), Unit(12, 3, 2, 2)};
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, foes, 104);
        Ticks(fight, 5);
        std::set<int> hit;
        for (const auto &event : struck(fight)) hit.insert(int(event.target & 0xFFFFF));
        Check(hit == std::set<int>({10, 11}), "A dash damages the enemies on its line and nobody to the side");
        Check(fight.Units()[0].cell == wc::Cell{3, 7}, "The dash ends on the farthest free cell of the line");
        catalog.units[0].ability.maxDash = 2;
        wc::Combat brief(catalog, {Unit(1, 0, 3, 3)}, foes, 104);
        Ticks(brief, 5);
        hit.clear();
        for (const auto &event : struck(brief)) hit.insert(int(event.target & 0xFFFFF));
        Check(hit == std::set<int>({10}) && brief.Units()[0].cell == wc::Cell{3, 5}, "A shorter dash reaches and hits less");
    }

    // The Assassin trait: two assassins leap behind the farthest enemy before the first tick.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    const int tank = find("wc_vn_shieldbearer"), scout = find("wc_vn_longbow_scout");
    const int fox = find("wc_vn_foxclaw"), moon = find("wc_vn_moonblade"), fiend = find("wc_vn_shadow_fiend");
    {
        const std::vector<wc::OwnedUnit> foes{Unit(10, tank, 4, 3), Unit(11, scout, 4, 0)};
        wc::Combat alone(roster, {Unit(1, fox, 2, 3), Unit(2, tank, 5, 3)}, foes, 105);
        Check(blinks(alone).empty() && alone.Units()[0].cell == wc::Cell{2, 3}, "One assassin does not leap");
        wc::Combat pair(roster, {Unit(1, fox, 2, 3), Unit(2, moon, 5, 3)}, foes, 105);
        const auto leaps = blinks(pair);
        const wc::Cell back = pair.Units()[3].cell;
        Check(leaps.size() == 2 && leaps[0].tick == 0 && leaps[1].tick == 0, "Two assassins leap before the first tick");
        Check(wc::Distance(pair.Units()[0].cell, back) == 1 && wc::Distance(pair.Units()[1].cell, back) == 1 &&
              !(pair.Units()[0].cell == pair.Units()[1].cell), "Each lands on its own cell next to the enemy at the back");
        Check(pair.ChanceDraws() == 0 && pair.InvariantError().empty(), "Leaps use no chance and leave the board valid");
        Ticks(pair, 60);
        int first = 0;
        for (const auto &event : pair.Events())
            if (!first && event.basicAttack && int(event.source & 0xFFFFF) == 1) first = int(event.target & 0xFFFFF);
        Check(first == 11, "After the leap an assassin attacks the back-line enemy");
    }

    // The authored heroes, starting with full mana so they cast at once.
    auto full = roster;
    for (auto &unit : full.units) unit.ability.mana.starting = unit.ability.mana.maximum;
    {
        wc::Combat fight(full, {Unit(1, moon, 3, 3)}, {Unit(10, tank, 4, 3), Unit(11, scout, 4, 1)}, 106);
        Ticks(fight, 40);
        const auto hits = struck(fight);
        bool critical = false;
        for (const auto &hit : hits) critical = critical || (hit.critical && int(hit.source & 0xFFFFF) == 1 && int(hit.target & 0xFFFFF) == 11);
        Check(!blinks(fight).empty() && fight.Units()[0].cell == wc::Cell{3, 7} && critical,
              "Moonblade blinks behind the farthest enemy and lands a critical strike on it");
    }
    {
        wc::Combat fight(full, {Unit(1, fox, 3, 3)}, {Unit(10, tank, 4, 1)}, 107);
        Ticks(fight, 120);
        int own = 0;
        for (const auto &hit : struck(fight)) own += int(hit.source & 0xFFFFF) == 1;
        Check(!blinks(fight).empty() && int(blinks(fight)[0].target & 0xFFFFF) == 1 && own >= 5,
              "Foxclaw leaps onto its target, strikes and leaves it bleeding");
    }
    {
        wc::Combat fight(full, {Unit(1, fiend, 3, 3)}, {Unit(10, tank, 4, 2), Unit(11, scout, 4, 0)}, 108);
        Ticks(fight, 40);
        std::set<int> hit;
        for (const auto &event : struck(fight)) if (int(event.source & 0xFFFFF) == 1) hit.insert(int(event.target & 0xFFFFF));
        Check(hit == std::set<int>({10, 11}) && !blinks(fight).empty() && blinks(fight)[0].cell.column == 3 && blinks(fight)[0].cell.row >= 5,
              "Shadow Fiend dashes through the line, hitting both enemies on it");
    }
}
void Summons()
{
    // Unit 0 summons "pups" beside itself. The enemy (unit 1) stands next to it and does no damage unless a test says so.
    auto fixture = [](int count, int lifetimeMs = 0, bool inert = false) {
        auto catalog = Quiet();
        catalog.rules.nearestReachableTarget = true;
        wc::UnitDef pup;
        pup.id = "test_pup"; pup.name = pup.displayName = "Pup";
        pup.health = 50000; pup.attackDamage = 100; pup.attackRate = 1000; pup.range = 1; pup.movementRate = 1000; pup.attackWindupMs = 50;
        pup.ability.enabled = false; pup.inert = inert;
        catalog.neutrals.push_back(pup);
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = wc::Effect::Summon; ability.selector = wc::Selector::Self; ability.damageType = wc::DamageType::True;
        ability.range = 1; ability.radius = 0; ability.maxTargets = 1; ability.travelMs = 0; ability.durationMs = 0;
        ability.magnitude = {0, 0, 0}; ability.cooldownMs = 500;
        wc::AbilityEffect call{wc::Effect::Summon, wc::DamageType::True, lifetimeMs, {0, 0, 0}};
        call.summon = int(catalog.neutrals.size()) - 1; call.count = count;
        ability.effects = {call};
        catalog.units[1].projectileTravelMs = 0; catalog.units[1].attackRate = 1000;
        return catalog;
    };
    auto arrivals = [](const wc::Combat &fight) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events()) if (event.effect == wc::Effect::Summon && event.source != event.target) result.push_back(event);
        return result;
    };
    auto departures = [](const wc::Combat &fight) {
        std::vector<wc::CombatEvent> result;
        for (const auto &event : fight.Events()) if (event.effect == wc::Effect::Summon && event.source == event.target) result.push_back(event);
        return result;
    };

    // A summon appears on the tick after the cast, beside its owner, as a unit of the owner's star.
    {
        const auto catalog = fixture(2);
        auto valid = wcvnext::WonderVNextCatalog();
        valid.neutrals.push_back(catalog.neutrals.back());
        valid.units[0].ability = catalog.units[0].ability;
        if (!valid.Validate().empty()) throw std::runtime_error("A summon ability validates: " + valid.Validate());
        auto wrong = valid;
        wrong.units[0].ability.effects[0].summon = int(wrong.neutrals.size());
        Check(!wrong.Validate().empty(), "A summon must name a unit that exists");
        wrong = valid;
        wrong.summonLimit = 0;
        Check(!wrong.Validate().empty(), "A catalogue with summons needs a summon limit");
        wrong = valid;
        wrong.units[0].ability.effects[0].effect = wc::Effect::Damage;
        Check(!wrong.Validate().empty(), "Only a summon effect names a unit to summon");
        auto owned = Unit(1, 0, 3, 3);
        owned.star = 2;
        wc::Combat fight(catalog, {owned}, {Unit(10, 1, 4, 3)}, 111);
        Ticks(fight, 2);
        Check(fight.Units().size() == 2 && arrivals(fight).empty(), "Nothing arrives on the tick of the cast");
        Ticks(fight, 1);
        const auto born = arrivals(fight);
        Check(fight.Units().size() == 4 && born.size() == 2 && born[0].tick == 3 && born[1].tick == 3, "Both summons arrive on the next tick");
        const auto &first = fight.Units()[2], &second = fight.Units()[3];
        Check(first.summoned && second.summoned && first.owner == 0 && first.side == 0 && first.neutral && first.star == 2,
              "A summon belongs to its owner's side and takes its star");
        Check(wc::Distance(first.cell, {3, 3}) == 1 && wc::Distance(second.cell, {3, 3}) == 1 && !(first.cell == second.cell),
              "Summons take separate free cells beside their owner");
        Check(first.maxHealth == wc::StarValue(50000, 2, 0, catalog.rules) && born[0].resolved == first.maxHealth,
              "A summon's health follows its owner's star, and the event carries it");
        Check(first.id != second.id && first.initiative > fight.Units()[1].initiative && second.initiative > first.initiative,
              "Summons get their own identities and act after the units that started the fight");
    }

    // The limit: a side has at most four summons alive. A cast that could add none is held.
    {
        const auto catalog = fixture(3);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 112);
        int most = 0;
        for (int tick = 0; tick < 120; ++tick)
        {
            Ticks(fight, 1);
            int living = 0;
            for (const auto &unit : fight.Units()) living += unit.summoned && unit.health > 0;
            most = std::max(most, living);
        }
        Check(most == 4 && fight.Units().size() == 6, "A side never has more than four summons alive");
        Check(fight.SummonsRefused() == 2, "The fifth and sixth summons are refused");
        Check(fight.Units()[0].castsCommitted == 2, "At the limit the caster holds its cast instead of wasting it");
        wc::Combat again(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 112);
        Ticks(again, 120);
        bool same = again.Events().size() == fight.Events().size();
        for (std::size_t i = 0; same && i < fight.Events().size(); ++i)
        {
            const auto &l = fight.Events()[i], &r = again.Events()[i];
            same = std::tie(l.tick, l.source, l.target, l.effect, l.resolved, l.healthLoss) ==
                   std::tie(r.tick, r.source, r.target, r.effect, r.resolved, r.healthLoss);
        }
        Check(same, "A fight with summons replays identically");
    }

    // Lifetime: the summon leaves when its time is up.
    {
        const auto catalog = fixture(1, 1000);
        auto slow = catalog;
        slow.units[0].ability.cooldownMs = 60000;
        wc::Combat fight(slow, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 113);
        Ticks(fight, 22);
        Check(fight.Units().size() == 3 && fight.Units()[2].health > 0 && departures(fight).empty(), "A timed summon is still there before its time is up");
        Ticks(fight, 1);
        const auto gone = departures(fight);
        Check(gone.size() == 1 && gone[0].tick == 23 && gone[0].healthLoss == 50000 && fight.Units()[2].health == 0,
              "A timed summon leaves one second after it arrived");
    }

    // Summons keep a fight going after their owner falls, but are not survivors.
    {
        auto catalog = fixture(2);
        catalog.units[0].ability.cooldownMs = 60000;
        catalog.units[0].health = 150000;
        catalog.units[1].attackDamage = 100000;
        catalog.neutrals.back().attackDamage = 300000;
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 114);
        bool carriedOn = false;
        for (int tick = 0; tick < 200 && !fight.Result().complete; ++tick)
        {
            Ticks(fight, 1);
            carriedOn = carriedOn || (fight.Units()[0].health == 0 && !fight.Result().complete);
        }
        Check(carriedOn, "The fight goes on while only summons are left on a side");
        Check(fight.Result().complete && fight.Result().winner == 0, "The summons can win it");
        Check(fight.Result().survivors[0] == 0 && fight.Result().survivors[1] == 0, "Summons do not count as survivors");
    }

    // A wall does nothing, and alone does not keep a fight going.
    {
        auto catalog = fixture(1, 0, true);
        catalog.units[0].ability.cooldownMs = 60000;
        catalog.units[0].health = 150000;
        catalog.units[1].attackDamage = 100000;
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 115);
        Ticks(fight, 200);
        const auto &wall = fight.Units()[2];
        int acted = 0;
        for (const auto &event : fight.Events()) acted += event.source == wall.id && event.effect != wc::Effect::Summon;
        Check(wall.health > 0 && acted == 0 && wall.state == wc::ActionState::Idle, "A wall never moves, attacks or casts");
        Check(fight.Result().complete && fight.Result().winner == 1, "A wall alone does not keep its side in the fight");
    }

    // Fallen units: the cast is held until someone falls, then the summon rises on that cell.
    {
        auto catalog = fixture(2);
        catalog.units[0].ability.cooldownMs = 60000;
        catalog.units[0].ability.effects[0].ownSelector = true;
        catalog.units[0].ability.effects[0].selector = wc::Selector::FallenUnits;
        catalog.units[2].health = 1000;
        catalog.units[1].attackDamage = 100000;
        auto harmless = catalog;
        harmless.units[1].attackDamage = 0;
        wc::Combat idle(harmless, {Unit(1, 0, 0, 0), Unit(2, 2, 3, 3)}, {Unit(10, 1, 4, 3)}, 116);
        Ticks(idle, 40);
        Check(idle.Units()[0].castsCommitted == 0 && arrivals(idle).empty(), "With nobody fallen the cast is held");
        wc::Combat fight(catalog, {Unit(1, 0, 0, 0), Unit(2, 2, 3, 3)}, {Unit(10, 1, 4, 3)}, 116);
        // The caster swings once while it waits, so its cast follows that swing's recovery.
        Ticks(fight, 100);
        const auto born = arrivals(fight);
        Check(fight.Units()[1].health == 0 && born.size() == 1 && born[0].cell == wc::Cell{3, 3},
              "One unit fell, so one summon rises, on the cell where it fell");
    }

    // The authored heroes and the Summoner trait, starting with full mana.
    const auto roster = wcvnext::WonderVNextRosterCatalog();
    auto find = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing roster hero: ") + identity);
    };
    auto summonOf = [&](const char *identity) {
        for (int i = 0; i < int(roster.neutrals.size()); ++i) if (roster.neutrals[i].id == identity) return i;
        throw std::runtime_error(std::string("Missing summoned unit: ") + identity);
    };
    auto full = roster;
    for (auto &unit : full.units) unit.ability.mana.starting = unit.ability.mana.maximum;
    const int tank = find("wc_vn_shieldbearer"), wolves = find("wc_vn_wolf_caller"), treants = find("wc_vn_treant_caller");
    Check(roster.summonLimit == 4 && roster.neutrals[summonOf("wc_vn_s_rock_wall")].inert, "The catalogue carries the limit and the wall");
    {
        wc::Combat alone(full, {Unit(1, wolves, 3, 0), Unit(2, tank, 3, 3)}, {Unit(10, tank, 4, 3)}, 117);
        Ticks(alone, 20);
        int count = 0;
        wc::Int health = 0;
        for (const auto &unit : alone.Units())
            if (unit.summoned && unit.definition == summonOf("wc_vn_s_wolf")) { ++count; health = unit.maxHealth; }
        Check(count == 2 && health == 22000, "Wolf Caller summons two wolves");
        wc::Combat paired(full, {Unit(1, wolves, 3, 0), Unit(2, treants, 4, 0), Unit(3, tank, 3, 3)}, {Unit(10, tank, 4, 3)}, 117);
        Ticks(paired, 20);
        count = 0;
        bool treant = false;
        for (const auto &unit : paired.Units())
        {
            if (unit.summoned && unit.definition == summonOf("wc_vn_s_wolf")) { ++count; health = unit.maxHealth; }
            treant = treant || (unit.summoned && unit.definition == summonOf("wc_vn_s_treant"));
        }
        Check(count == 2 && health == 28600 && treant, "Two Summoners make summons 30% stronger, and Treant Caller summons a treant");
    }
    {
        wc::Combat fight(full, {Unit(1, treants, 3, 2), Unit(2, tank, 0, 0)}, {Unit(10, tank, 4, 3), Unit(11, find("wc_vn_hammerer"), 3, 3)}, 118);
        Ticks(fight, 300);
        // She may summon more than one over the fight; any of them taunting is enough.
        std::set<wc::Id> treant;
        for (const auto &unit : fight.Units()) if (unit.summoned) treant.insert(unit.id);
        int taunts = 0;
        for (const auto &event : fight.Events()) taunts += event.effect == wc::Effect::Taunt && treant.count(event.source) && event.resolved > 0;
        Check(!treant.empty() && taunts > 0, "The treant taunts the enemies next to it");
    }
    {
        wc::Combat fight(full, {Unit(1, find("wc_vn_stone_shaper"), 3, 1), Unit(2, tank, 3, 3)}, {Unit(10, tank, 4, 3)}, 119);
        Ticks(fight, 20);
        int walls = 0;
        for (const auto &unit : fight.Units()) walls += unit.summoned && unit.health > 0 && unit.definition == summonOf("wc_vn_s_rock_wall");
        Check(walls == 3, "Stone Shaper raises three walls");
        Ticks(fight, 100);
        Check(departures(fight).size() + 0 >= 1, "The walls crumble when their time is up");
        for (const auto &event : departures(fight)) Check(event.tick <= 20 + 81, "A wall stands for four seconds");
    }
    {
        wc::Combat fight(full, {Unit(1, find("wc_vn_necromancer"), 3, 0), Unit(2, find("wc_vn_jinxer"), 3, 3)},
                         {Unit(10, find("wc_vn_earthbreaker"), 4, 3), Unit(11, find("wc_vn_hammerer"), 3, 3)}, 120);
        bool heldUntilDeath = true;
        for (int tick = 0; tick < 900 && !fight.Result().complete; ++tick)
        {
            bool fallen = false;
            for (const auto &unit : fight.Units()) fallen = fallen || (!unit.summoned && unit.health == 0);
            Ticks(fight, 1);
            if (!fallen && fight.Units()[0].castsCommitted > 0) heldUntilDeath = false;
        }
        bool skeleton = false;
        for (const auto &unit : fight.Units()) skeleton = skeleton || (unit.summoned && unit.definition == summonOf("wc_vn_s_skeleton"));
        Check(heldUntilDeath && skeleton, "Necromancer waits for a unit to fall, then raises a skeleton");
    }
}
void FightCharts()
{
    // Side A: unit 0 hits for physical damage and casts a magic bolt. Side B: unit 1 hits back.
    auto catalog = Quiet();
    catalog.units[0].attackDamage = 1000; catalog.units[0].attackRate = 1000;
    catalog.units[1].attackDamage = 400; catalog.units[1].attackRate = 1000;
    Enable(catalog, 0);
    auto &bolt = catalog.units[0].ability;
    bolt.mechanic = wc::AbilityMechanic::Standard; bolt.guardReductionBp = 0;
    bolt.effect = wc::Effect::Damage; bolt.selector = wc::Selector::CurrentEnemy; bolt.damageType = wc::DamageType::Magic;
    bolt.range = 8; bolt.radius = 0; bolt.maxTargets = 1; bolt.travelMs = 0; bolt.durationMs = 0;
    bolt.magnitude = {700, 700, 700}; bolt.cooldownMs = 1000; bolt.effects.clear();
    wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3), Unit(11, 2, 4, 0)}, 121);
    Ticks(fight, 120);
    std::array<wc::Int, 3> dealt{};
    wc::Int taken = 0;
    for (const auto &event : fight.Events())
        if (event.effect == wc::Effect::Damage)
        {
            if (int(event.source & 0xFFFFF) == 1) dealt[int(event.damageType)] += event.healthLoss;
            if (int(event.target & 0xFFFFF) == 1) taken += event.healthLoss;
        }
    const auto mine = wc::FightChart(fight, 0, wc::ChartMode::Dealt);
    Check(mine.size() == 1 && mine[0].parts == dealt && mine[0].total == dealt[0] + dealt[1] + dealt[2] && dealt[0] > 0 && dealt[1] > 0 && dealt[2] == 0,
          "The chart splits a hero's damage into physical and magic");
    const auto hurt = wc::FightChart(fight, 0, wc::ChartMode::Taken);
    Check(hurt.size() == 1 && hurt[0].total == taken && taken > 0, "Damage taken is listed for the same side");
    // The viewer may be the second seat of a pairing: its heroes are then side 1, and only they are listed.
    const auto second = wc::FightChart(fight, 1, wc::ChartMode::Dealt);
    Check(second.size() == 2 && int(second[0].unit & 0xFFFFF) == 10 && second[0].total == taken && second[1].total == 0 &&
          ((second[0].unit >> 20) & 1) == 1 && ((second[1].unit >> 20) & 1) == 1,
          "Seen from the second side the chart lists that side's heroes, largest first");
    wc::Int received = 0;
    for (const auto &row : wc::FightChart(fight, 1, wc::ChartMode::Taken)) received += row.total;
    Check(received == mine[0].total, "One side's damage dealt is the other side's damage taken");

    // Blocked: a shield's absorbed damage is credited to the hero that gave it.
    auto warded = Quiet();
    warded.rules.nearestReachableTarget = true;
    warded.units[1].attackDamage = 400; warded.units[1].attackRate = 1000;
    Enable(warded, 0);
    auto &ward = warded.units[0].ability;
    ward.mechanic = wc::AbilityMechanic::Standard; ward.guardReductionBp = 0;
    ward.effect = wc::Effect::Shield; ward.selector = wc::Selector::AdjacentAllies; ward.damageType = wc::DamageType::True;
    ward.range = 8; ward.radius = 8; ward.maxTargets = 8; ward.travelMs = 0; ward.durationMs = 3000; ward.allowSelf = false;
    ward.magnitude = {1000, 1000, 1000}; ward.effects.clear();
    wc::Combat guarded(warded, {Unit(1, 0, 0, 0), Unit(2, 2, 3, 3)}, {Unit(10, 1, 4, 3)}, 122);
    Ticks(guarded, 100);
    wc::Int absorbed = 0;
    for (const auto &event : guarded.Events()) absorbed += event.absorbed;
    const auto blocked = wc::FightChart(guarded, 0, wc::ChartMode::Blocked);
    Check(absorbed > 0 && int(blocked[0].unit & 0xFFFFF) == 1 && blocked[0].total == absorbed && blocked[1].total == 0,
          "Blocked damage is credited to the hero whose shield took it");
    Check(wc::FightChart(guarded, 0, wc::ChartMode::Healed)[0].total == 0, "Nobody healed in a fight without healing");

    // A summoned unit's damage is added to its owner's row; it has no row of its own.
    auto summoning = Quiet();
    summoning.rules.nearestReachableTarget = true;
    wc::UnitDef pup;
    pup.id = "test_pup"; pup.name = pup.displayName = "Pup";
    pup.health = 50000; pup.attackDamage = 900; pup.attackRate = 1000; pup.range = 1; pup.movementRate = 1000; pup.attackWindupMs = 50;
    pup.ability.enabled = false;
    summoning.neutrals.push_back(pup);
    Enable(summoning, 0);
    auto &call = summoning.units[0].ability;
    call.mechanic = wc::AbilityMechanic::Standard; call.guardReductionBp = 0;
    call.effect = wc::Effect::Summon; call.selector = wc::Selector::Self; call.damageType = wc::DamageType::True;
    call.range = 1; call.radius = 0; call.maxTargets = 1; call.travelMs = 0; call.durationMs = 0; call.magnitude = {0, 0, 0};
    wc::AbilityEffect summon{wc::Effect::Summon, wc::DamageType::True, 0, {0, 0, 0}};
    summon.summon = int(summoning.neutrals.size()) - 1;
    call.effects = {summon};
    wc::Combat pack(summoning, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 123);
    Ticks(pack, 100);
    wc::Int bites = 0;
    for (const auto &event : pack.Events()) if (event.effect == wc::Effect::Damage) bites += event.healthLoss;
    const auto owner = wc::FightChart(pack, 0, wc::ChartMode::Dealt);
    Check(bites > 0 && owner.size() == 1 && int(owner[0].unit & 0xFFFFF) == 1 && owner[0].total == bites,
          "A summon's damage is shown in its owner's row");
}
void PresentationViews()
{
    // What the presentation reads about repeating effects: flagged hits, zones still running, and who is under damage over time.
    auto caster = [](wc::Selector selector, bool follow) {
        auto catalog = Quiet();
        Enable(catalog, 0);
        auto &ability = catalog.units[0].ability;
        ability.mechanic = wc::AbilityMechanic::Standard; ability.guardReductionBp = 0;
        ability.effect = wc::Effect::Damage; ability.selector = selector; ability.damageType = wc::DamageType::Magic;
        ability.range = 8; ability.radius = 1; ability.maxTargets = 8; ability.travelMs = 0; ability.durationMs = 0;
        ability.magnitude = {1000, 1000, 1000};
        ability.effects = {{wc::Effect::Damage, wc::DamageType::Magic, 3000, {1000, 1000, 1000}, 0, false, selector,
                            wc::ModifierStat::AttackRate, 1000, follow}};
        return catalog;
    };
    {
        // A fight keeps a pointer to its catalogue, so the catalogue must outlive it.
        const auto catalog = caster(wc::Selector::CurrentEnemy, false);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 131);
        Ticks(fight, 10);
        Check(fight.PeriodicTargets() == std::vector<int>{1} && fight.Zones().empty(), "A unit under damage over time is reported, and it is not a zone");
        Ticks(fight, 80);
        int flagged = 0, plain = 0;
        for (const auto &event : fight.Events())
            if (event.effect == wc::Effect::Damage) ++(event.periodic ? flagged : plain);
        Check(flagged == 3 && fight.PeriodicTargets().empty(), "Each hit of damage over time is flagged, and the report ends with the effect");
    }
    {
        const auto catalog = caster(wc::Selector::CurrentEnemyArea, false);
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 132);
        Ticks(fight, 10);
        const auto zones = fight.Zones();
        Check(zones.size() == 1 && zones[0].center == wc::Cell{3, 4} && zones[0].radius == 1 && zones[0].side == 0 &&
              zones[0].damageType == wc::DamageType::Magic && !zones[0].follow && zones[0].untilTick == 62 && fight.PeriodicTargets().empty(),
              "A ground zone is reported with its centre, size, owner's side and last hit");
        Ticks(fight, 60);
        Check(fight.Zones().empty(), "A finished zone is no longer reported");
    }
    {
        auto catalog = caster(wc::Selector::AdjacentEnemies, true);
        catalog.units[0].range = 1;
        wc::Combat fight(catalog, {Unit(1, 0, 3, 3)}, {Unit(10, 1, 4, 3)}, 133);
        Ticks(fight, 10);
        const auto zones = fight.Zones();
        Check(zones.size() == 1 && zones[0].follow && zones[0].center == fight.Units()[0].cell, "An aura is reported where its caster stands");
    }
}
void EffectChains()
{
    auto catalog = Quiet();
    Enable(catalog, 0);
    auto &chain = catalog.units[0].ability;
    chain.mechanic = wc::AbilityMechanic::Standard; chain.guardReductionBp = 0;
    chain.effect = wc::Effect::Damage; chain.selector = wc::Selector::CurrentEnemy; chain.damageType = wc::DamageType::True;
    chain.range = 8; chain.radius = 0; chain.maxTargets = 1; chain.travelMs = 0; chain.durationMs = 0; chain.allowSelf = true;
    chain.magnitude = {1000, 1000, 1000};
    chain.effects = {{wc::Effect::Damage, wc::DamageType::True, 0, {1000, 1000, 1000}},
                     {wc::Effect::Shield, wc::DamageType::Magic, 2000, {500, 500, 500}, 200, true, wc::Selector::Self},
                     {wc::Effect::Damage, wc::DamageType::True, 0, {300, 300, 300}, 400},
                     {wc::Effect::Stun, wc::DamageType::True, 500, {0, 0, 0}, 400}};
    // The quiet fixture bends unit stats, so the chain is validated on the canonical catalogue.
    auto valid = wcvnext::WonderVNextCatalog();
    valid.units[0].ability = chain;
    if (!valid.Validate().empty()) throw std::runtime_error("A four-effect chain with its own selector validates: " + valid.Validate());
    ++assertions;
    auto run = [&](wc::Id seed) {
        wc::Combat combat(catalog, {Unit(1, 0, 3, 3)}, {Unit(2, 1, 3, 3)}, seed);
        Ticks(combat, 40);
        std::vector<wc::CombatEvent> cast;
        for (const auto &event : combat.Events())
            if (!event.basicAttack && event.effect != wc::Effect::Dash) cast.push_back(event);
        return cast;
    };
    const auto cast = run(31);
    Check(cast.size() == 4, "Each effect of the chain resolves exactly once per cast");
    Check(cast[0].effect == wc::Effect::Damage && cast[1].effect == wc::Effect::Shield &&
          cast[2].effect == wc::Effect::Damage && cast[3].effect == wc::Effect::Stun, "Chain effects resolve in authored order");
    Check(cast[1].tick - cast[0].tick == 4 && cast[2].tick - cast[0].tick == 8 && cast[3].tick == cast[2].tick,
          "Each effect lands after its own delay");
    Check(cast[0].healthLoss == 1000 && cast[2].healthLoss == 300, "Chained damage keeps its own magnitude");
    Check(cast[1].target == cast[1].source && cast[0].target != cast[0].source && cast[2].target == cast[0].target,
          "An effect with its own selector picks its own target; the others share the ability's");
    const auto again = run(31);
    Check(again.size() == cast.size() && again[3].tick == cast[3].tick && again[1].target == cast[1].target,
          "A chained cast replays identically from the same seed");
    auto wrong = valid;
    wrong.units[0].ability.effects.push_back({wc::Effect::Damage, wc::DamageType::True, 0, {1, 1, 1}});
    Check(!wrong.Validate().empty(), "More than four chained effects are rejected");
    wrong = valid;
    wrong.units[0].ability.effects[2].delayMs = 20000;
    Check(!wrong.Validate().empty(), "An unbounded effect delay is rejected");
    wrong = valid;
    wrong.units[0].ability.effects[3] = {wc::Effect::Dash, wc::DamageType::True, 0, {0, 0, 0}};
    Check(!wrong.Validate().empty(), "A dash cannot be chained with other effects");

    // Stitcher, as authored: heal the lowest-health ally, then shield it a moment later.
    const auto canonical = wcvnext::WonderVNextCatalog();
    int stitcher = -1, tank = -1, fighter = -1;
    for (int i = 0; i < int(canonical.units.size()); ++i)
    {
        if (canonical.units[i].id == "wc_vn_stitcher") stitcher = i;
        if (canonical.units[i].id == "wc_vn_shieldbearer") tank = i;
        if (canonical.units[i].id == "wc_vn_hammerer") fighter = i;
    }
    Check(stitcher >= 0 && tank >= 0 && fighter >= 0, "Stitcher is in the executable roster");
    wc::Combat ward(canonical, {Unit(1, stitcher, 3, 0), Unit(2, tank, 3, 3)}, {Unit(3, fighter, 3, 3)}, 12);
    Ticks(ward, 400);
    const wc::CombatEvent *heal = nullptr, *shield = nullptr;
    for (const auto &event : ward.Events())
    {
        if (!heal && event.effect == wc::Effect::Heal) heal = &event;
        else if (heal && !shield && event.effect == wc::Effect::Shield && event.action == heal->action) shield = &event;
    }
    Check(heal && shield, "Stitcher's cast heals and then shields");
    Check(heal && shield && shield->target == heal->target && shield->source == heal->source &&
          shield->tick - heal->tick == 5 && heal->target != heal->source,
          "The shield follows the heal on the same injured ally a quarter of a second later");
}
int main()
{
    try
    {
        assertions += wctest::RunManaContractChecks();
        assertions += wctest::RunCombatClarityChecks();
        Contract(); EffectChains(); Modifiers(); FightStartAndPerSecondTraits(); Chance(); RepeatingEffects(); SelectorsAndShapes(); Statuses(); BlinkAndLeap(); Summons(); FightCharts(); PresentationViews(); Guard(); Screening(); Charge(); Beams(); TideAndGrove(); RelicsAndReplay(); Diagnostics(); Cocoons(); CanonicalSilkmotherPlacement(); CrowdedEncounters(); RosterRecipe(); UniversalRelics(); DirectMovement();
        std::cout << "PASS vNext native combat: " << assertions << " assertions. Technical synthetic fixtures only; no human art/balance acceptance.\n";
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << "FAIL after " << assertions << " assertions: " << error.what() << '\n';
        return 1;
    }
}
