#include "VNext/WonderVNextCatalog.generated.h"
#include "../../game/Source/WonderChessRuntime/Private/Simulation/WonderManaTests.h"
#include "../../game/Source/WonderChessRuntime/Private/Simulation/WonderCombatClarityTests.h"
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
    Check(catalog.profileId == "wonder_vnext" && catalog.units.size() == 14, "Seven ported mechanics plus seven standard-ability heroes");
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
    Check(base.traits.empty() && roster.traits.size() == 7, "Control keeps no traits; recipe carries seven stat traits");
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
        auto bad = roster; bad.traits[0].stat = "evasion_bp";
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
int main()
{
    try
    {
        assertions += wctest::RunManaContractChecks();
        assertions += wctest::RunCombatClarityChecks();
        Contract(); Guard(); Screening(); Charge(); Beams(); TideAndGrove(); RelicsAndReplay(); Diagnostics(); Cocoons(); CanonicalSilkmotherPlacement(); CrowdedEncounters(); RosterRecipe(); UniversalRelics(); DirectMovement();
        std::cout << "PASS vNext native combat: " << assertions << " assertions. Technical synthetic fixtures only; no human art/balance acceptance.\n";
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << "FAIL after " << assertions << " assertions: " << error.what() << '\n';
        return 1;
    }
}
