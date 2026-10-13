#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <functional>
#include <numeric>
#include <set>
#include <stdexcept>
#include <tuple>

namespace wc
{
namespace
{
std::atomic<Id> NextMatchNamespace{1};
Id HashValue(Id n)
{
    n += 0x9e3779b97f4a7c15ULL;
    n = (n ^ (n >> 30)) * 0xbf58476d1ce4e5b9ULL;
    n = (n ^ (n >> 27)) * 0x94d049bb133111ebULL;
    return n ^ (n >> 31);
}
std::pair<int, int> Key(int a, int b)
{
    return {std::min(a, b), std::max(a, b)};
}
int CountCopies(int star)
{
    return star == 3 ? 9 : star == 2 ? 3 : 1;
}
bool EqualCommand(const Command &a, const Command &b)
{
    return std::tie(a.type, a.seat, a.requestId, a.sequence, a.revision, a.unit, a.slot, a.toBoard,
                    a.cell.column, a.cell.row, a.facing) == std::tie(b.type, b.seat, b.requestId, b.sequence,
                                                           b.revision, b.unit, b.slot, b.toBoard,
                                                           b.cell.column, b.cell.row, b.facing);
}
void OfferRelics(const Catalog &catalog, SeatState &seat)
{
    if (seat.pendingRelicDrafts <= 0 || !seat.relicOffers.empty()) return;
    std::vector<int> available;
    for (int i = 0; i < int(catalog.relics.size()); ++i)
        if (std::find(seat.ownedRelics.begin(), seat.ownedRelics.end(), i) == seat.ownedRelics.end() &&
            std::any_of(catalog.units.begin(), catalog.units.end(), [&](const UnitDef &unit) {
                return RelicCompatible(catalog.relics[i], unit.ability.mechanic);
            }))
            available.push_back(i);
    if (catalog.ownedTeamRelicOffers)
    {
        std::vector<int> compatible;
        for (int relic : available)
            if (std::any_of(seat.roster.begin(), seat.roster.end(), [&](const OwnedUnit &unit) {
                return RelicCompatible(catalog.relics[relic], catalog.units[unit.definition].ability.mechanic);
            }))
                compatible.push_back(relic);
        if (!compatible.empty())
        {
            const int selected = compatible[seat.relicRng.Below(int(compatible.size()))];
            seat.relicOffers.push_back(selected);
            available.erase(std::find(available.begin(), available.end(), selected));
        }
    }
    while (!available.empty() && seat.relicOffers.size() < 3)
    {
        const int choice = seat.relicRng.Below(int(available.size()));
        seat.relicOffers.push_back(available[choice]);
        available.erase(available.begin() + choice);
    }
}
struct Features
{
    double budget = 0, upgrades = 0, traits = 0, pairs = 0, roles = 0, bench = 0;
};
double SkillBudget(const UnitDef &unit, int star, int capacity, const Catalog &catalog, int relic = -1)
{
    const auto ability = catalog.profileId == "wonder_vnext" ? EffectiveAbility(catalog, unit, relic) : unit.ability;
    const int horizon = std::min(20000, catalog.rules.combatTimeoutMs);
    const int firstRelease = ability.firstCastMs + ability.castMs + ability.travelMs;
    if (!ability.enabled || firstRelease >= horizon)
        return 0;
    // Public authored potential, discounted for interruption, positioning and wasted support.
    // It influences legal purchases only; every encounter still resolves actual combat.
    const int casts = 1 + (horizon - firstRelease - 1) /
                             std::max(catalog.rules.tickMs, ability.cooldownMs);
    const bool area = ability.selector == Selector::CurrentEnemyArea ||
                      ability.selector == Selector::AdjacentEnemies ||
                      ability.selector == Selector::AdjacentAllies ||
                      ability.selector == Selector::AllAllies || ability.selector == Selector::DensestEnemyArea ||
                      ability.selector == Selector::RandomEnemyAreas || ability.selector == Selector::EnemyLine ||
                      ability.selector == Selector::EnemyCone || ability.selector == Selector::ChainFromCurrentEnemy;
    const double recipients = area ? std::min({3, std::max(1, capacity), ability.maxTargets}) : 1;
    const double basicPerSecond = double(StarValue(unit.attackDamage, star, 0, catalog.rules)) *
                                  unit.attackRate / 1000.0;
    double potential = 0;
    if (catalog.profileId == "wonder_vnext" && ability.mechanic != AbilityMechanic::Standard)
    {
        // Authored opportunity estimates for shopping; actual battles always use Combat.
        const double magnitude = double(ability.magnitude[star - 1]);
        switch (ability.mechanic)
        {
        case AbilityMechanic::DirectionalGuard:
            return capacity > 1 ? double(StarValue(unit.health, star, 0, catalog.rules)) / 100000.0 *
                ability.guardReductionBp / 10000.0 * 0.5 : 0.0;
        case AbilityMechanic::MomentumCharge:
            potential = magnitude * (1.0 + std::min(2, ability.maxMomentumSteps) * ability.momentumPerStepBp / 10000.0);
            break;
        case AbilityMechanic::StationaryGrove:
            potential = magnitude * std::min(3, std::max(1, capacity)) * 0.6 *
                ((ability.durationMs + ability.pulseMs - 1) / std::max(1, ability.pulseMs));
            break;
        case AbilityMechanic::ScreenedStrike: potential = magnitude; break;
        case AbilityMechanic::CrossingBeams: potential = magnitude * std::min(3, std::max(1, capacity)); break;
        case AbilityMechanic::TidalPush: potential = magnitude * std::min(2, std::max(1, capacity)); break;
        case AbilityMechanic::CocoonProjectile:
            potential = basicPerSecond * ability.durationMs / 1000.0;
            break;
        case AbilityMechanic::Standard: break;
        }
    }
    else for (const auto &effect : ability.effects)
    {
        const double magnitude = double(effect.magnitude[star - 1]);
        switch (effect.effect)
        {
        case Effect::Damage:
            potential += magnitude * recipients * (effect.repeatMs > 0 ? effect.durationMs / effect.repeatMs : 1) *
                         (effect.critical ? 1.5 : 1.0);
            break;
        case Effect::Heal:
        case Effect::Shield: potential += magnitude * recipients * 0.6; break;
        case Effect::Stun:
            potential += basicPerSecond * effect.durationMs / 1000.0 * recipients;
            break;
        case Effect::StatModifier:
            // Armour and resistance are flat points, worth about one percent each; the rest are basis points.
            potential += basicPerSecond * std::abs(magnitude) /
                         (effect.stat == ModifierStat::Armor || effect.stat == ModifierStat::Resistance ? 100.0 : 10000.0) *
                         effect.durationMs / 1000.0 * recipients;
            break;
        case Effect::Dash:
            potential += basicPerSecond * std::min(2, ability.maxDash) * 0.25;
            break;
        // A status is worth the basic attacks it takes away; magnitude is its duration in milliseconds.
        case Effect::Hex:
            potential += basicPerSecond * magnitude / 1000.0 * recipients;
            break;
        case Effect::Silence:
        case Effect::Taunt:
            potential += basicPerSecond * magnitude / 1000.0 * recipients * 0.5;
            break;
        case Effect::ManaDrain: // a full bar is about three seconds of basic attacks
            potential += basicPerSecond * 3.0 * magnitude / 10000.0 * recipients;
            break;
        case Effect::Blink: // reaching a target at once saves about half a second of walking
            potential += basicPerSecond * 0.5;
            break;
        case Effect::Summon:
        {
            // About four seconds of each summoned unit's attacks, plus a tenth of its health as cover.
            const auto &summon = catalog.neutrals[effect.summon];
            potential += effect.count * (double(StarValue(summon.attackDamage, star, 0, catalog.rules)) * summon.attackRate / 1000.0 * 4.0 +
                                         double(StarValue(summon.health, star, 0, catalog.rules)) * 0.1);
            break;
        }
        }
    }
    const double occupied = basicPerSecond * (ability.castMs + ability.recoveryMs) / 1000.0;
    return std::max(0.0, potential * 0.75 - occupied) * casts / (horizon * 10.0);
}
// Bot hints for a unit's class, or null when the catalogue carries none and the
// legacy class names below still apply.
const ClassRole *RoleOf(const Catalog &c, const UnitDef &d)
{
    for (const auto &role : c.classRoles)
        if (role.id == d.unitClass) return &role;
    return nullptr;
}
bool IsFrontline(const Catalog &c, const UnitDef &d)
{
    if (const auto *role = RoleOf(c, d)) return role->role == BotRole::Frontline;
    return d.unitClass == "guardian" || d.unitClass == "warrior";
}
bool IsSupport(const Catalog &c, const UnitDef &d)
{
    if (const auto *role = RoleOf(c, d)) return role->role == BotRole::Support;
    return d.unitClass == "priest" || (c.profileId == "wonder_vnext" && d.unitClass == "healer");
}
// A catalogue that carries cost values asks its bots to plan: see Catalog::botCostValueBp.
bool Plans(const Catalog &c)
{
    return !c.botCostValueBp.empty();
}
// What a trait is worth to a bot at a member count.
double TraitCredit(const TraitDef &t, int count, bool plans)
{
    if (!t.tiers.empty())
    {
        // Tiered traits: one step for the first tier, two for the second, and a
        // nudge when one more member reaches the next tier.
        int reached = 0;
        for (const auto &tier : t.tiers) reached += count >= tier.first;
        const bool oneShort = reached < int(t.tiers.size()) && count + 1 == t.tiers[reached].first;
        // A planning bot rates a trait by what it measured as in a fight (trait_power.csv from
        // vnext_hero_power): the first tier is worth about a third of a hero, the second a whole one.
        if (plans) return reached >= 2 ? 1.0 : reached == 1 ? (oneShort ? 0.4 : 0.3) : 0.0;
        return reached >= 2 ? 2.0 / 6.0 : reached == 1 ? (oneShort ? 1.25 : 1.0) / 6.0 : 0.0;
    }
    if (count >= t.threshold4) return 2.0 / 6.0;
    if (count >= t.threshold) return (count == 3 ? 1.25 : 1.0) / 6.0;
    return 0.0;
}
// How well a line-up covers the three jobs. A planning bot wants about a third of the board in
// front and a third dealing damage, and the cover matters more as the board grows.
double RoleCover(const std::array<int, 3> &roles, int fielded, bool plans)
{
    const int frontline = roles[int(BotRole::Frontline)], damage = roles[int(BotRole::Damage)],
        support = roles[int(BotRole::Support)];
    if (!plans) return (frontline ? 0.6 : 0) + (damage ? 0.3 : 0) + (support ? 0.1 : 0);
    const int wantFront = std::max(1, (fielded * 35 + 50) / 100), wantDamage = std::max(1, (fielded * 30 + 50) / 100);
    return (0.6 * std::min(1.0, double(frontline) / wantFront) + 0.3 * std::min(1.0, double(damage) / wantDamage) +
            (support ? 0.1 : 0)) * std::max(1.0, fielded * 0.25);
}
struct Choice
{
    double budget = 0;
    const OwnedUnit *unit = nullptr;
    // Job (-1: none), and the positions of the unit's race and class among the catalogue's traits (-1: none).
    int role = -1, race = -1, unitClass = -1;
};
// Member counts of each trait and of each job among the first `fielded` choices. Two copies of
// one hero count once toward a trait.
void CountLineup(const std::vector<Choice> &choices, int fielded, std::vector<int> &members, std::array<int, 3> &roles)
{
    std::fill(members.begin(), members.end(), 0);
    roles.fill(0);
    for (int i = 0; i < fielded; ++i)
    {
        if (choices[i].role >= 0) ++roles[choices[i].role];
        bool repeated = false;
        for (int j = 0; j < i && !repeated; ++j) repeated = choices[j].unit->definition == choices[i].unit->definition;
        if (repeated) continue;
        if (choices[i].race >= 0) ++members[choices[i].race];
        if (choices[i].unitClass >= 0) ++members[choices[i].unitClass];
    }
}
// Starting from the strongest units, swap one fielded unit for one left out for as long as the
// line-up gains more in job cover and traits than it loses in strength.
void PlanLineup(std::vector<Choice> &choices, int fielded, const std::vector<const TraitDef *> &traits, double synergy)
{
    if (fielded >= int(choices.size())) return;
    std::vector<int> members(traits.size());
    std::array<int, 3> roles{};
    for (int pass = 0; pass < fielded; ++pass)
    {
        CountLineup(choices, fielded, members, roles);
        const double cover = RoleCover(roles, fielded, true);
        double best = 1e-9;
        int bestOut = -1, bestIn = -1;
        for (int out = 0; out < fielded; ++out)
            for (int in = fielded; in < int(choices.size()); ++in)
            {
                double gain = choices[in].budget - choices[out].budget;
                auto swapped = roles;
                if (choices[out].role >= 0) --swapped[choices[out].role];
                if (choices[in].role >= 0) ++swapped[choices[in].role];
                gain += RoleCover(swapped, fielded, true) - cover;
                bool outRepeated = false, inRepeated = false;
                for (int other = 0; other < fielded; ++other)
                {
                    if (other == out) continue;
                    outRepeated |= choices[other].unit->definition == choices[out].unit->definition;
                    inRepeated |= choices[other].unit->definition == choices[in].unit->definition;
                }
                // Up to four traits change: the two the leaving hero held and the two the arriving one brings.
                std::array<std::pair<int, int>, 4> changes{{{-1, 0}, {-1, 0}, {-1, 0}, {-1, 0}}};
                auto change = [&](int trait, int by) {
                    if (trait < 0) return;
                    for (auto &entry : changes)
                        if (entry.first == trait || entry.first < 0) { entry.first = trait; entry.second += by; return; }
                };
                if (!outRepeated) { change(choices[out].race, -1); change(choices[out].unitClass, -1); }
                if (!inRepeated) { change(choices[in].race, 1); change(choices[in].unitClass, 1); }
                for (const auto &entry : changes)
                    if (entry.first >= 0 && entry.second != 0)
                        gain += synergy * (TraitCredit(*traits[entry.first], members[entry.first] + entry.second, true) -
                                           TraitCredit(*traits[entry.first], members[entry.first], true));
                if (gain > best) { best = gain; bestOut = out; bestIn = in; }
            }
        if (bestOut < 0) return;
        std::swap(choices[bestOut], choices[bestIn]);
    }
}
Features Evaluate(const SeatState &s, const Catalog &c, const BotDef &b)
{
    Features f;
    const bool plans = Plans(c);
    // A trait with several parts is still one trait to a bot.
    std::vector<const TraitDef *> traits;
    for (const auto &t : c.traits)
        if (std::none_of(traits.begin(), traits.end(), [&](const TraitDef *seen) { return seen->id == t.id; }))
            traits.push_back(&t);
    auto traitOf = [&](const std::string &identity) {
        for (int i = 0; i < int(traits.size()); ++i) if (traits[i]->id == identity) return i;
        return -1;
    };
    std::vector<Choice> choices;
    std::map<int, int> copies;
    for (const auto &u : s.roster)
    {
        const auto &d = c.units[u.definition];
        const auto *role = RoleOf(c, d);
        double weight = role ? (role->role == BotRole::Frontline ? b.frontline
                                : role->role == BotRole::Support ? b.support : b.damage)
                        : d.unitClass == "guardian" ? b.frontline
                        : IsSupport(c, d) ? b.support
                                          : b.damage;
        double budget = double(StarValue(d.health, u.star, 0, c.rules)) / 100000.0 +
                        double(StarValue(d.attackDamage, u.star, 0, c.rules)) * d.attackRate / 10000000.0 +
                        SkillBudget(d, u.star, s.level, c, u.relic);
        // A planning bot takes nearly all of a hero's worth from its cost and star, so that no class
        // is passed over because its strength is in its ability, and a little from its numbers.
        if (plans)
            budget = 0.85 * c.botCostValueBp[std::clamp(d.cost, 1, int(c.botCostValueBp.size())) - 1] / 10000.0 *
                         double(StarValue(10000, u.star, 0, c.rules)) / 10000.0 +
                     0.15 * budget;
        Choice choice;
        choice.budget = budget * weight;
        choice.unit = &u;
        if (IsFrontline(c, d)) choice.role = int(BotRole::Frontline);
        else if (IsSupport(c, d)) choice.role = int(BotRole::Support);
        else if (role || d.unitClass == "ranger" || d.unitClass == "mage" || d.unitClass == "rogue" ||
                 (c.profileId == "wonder_vnext" && (d.unitClass == "assassin" || d.unitClass == "controller")))
            choice.role = int(BotRole::Damage);
        choice.race = traitOf(d.race);
        choice.unitClass = traitOf(d.unitClass);
        choices.push_back(choice);
        copies[u.definition] += CountCopies(u.star);
        if (!plans) f.upgrades += u.star == 3 ? 1.0 : u.star == 2 ? 1.0 / 3.0 : 0.0;
        if (!u.onBoard)
            f.bench += 1.0 / c.rules.benchCapacity;
    }
    std::stable_sort(choices.begin(), choices.end(),
                     [](const Choice &a, const Choice &b) { return a.budget > b.budget; });
    const int fielded = std::min(s.level, int(choices.size()));
    if (plans) PlanLineup(choices, fielded, traits, b.synergy);
    for (int i = 0; i < fielded; ++i)
    {
        f.budget += choices[i].budget;
        // A planning bot credits an upgrade only where it is fielded; a star on the bench wins nothing.
        if (plans) f.upgrades += choices[i].unit->star == 3 ? 1.0 : choices[i].unit->star == 2 ? 1.0 / 3.0 : 0.0;
    }
    std::vector<int> members(traits.size());
    std::array<int, 3> roles{};
    CountLineup(choices, fielded, members, roles);
    for (int i = 0; i < int(traits.size()); ++i)
        f.traits += TraitCredit(*traits[i], members[i], plans);
    // A lone copy is a small start and a pair is one purchase from an upgrade; a planning bot
    // holds pairs and lets lone copies go first.
    for (auto pair : copies)
        f.pairs += plans ? (pair.second % 3 == 2 ? 2.5 : pair.second % 3 == 1 ? 0.5 : 0.0) / 6.0
                         : std::min(2, pair.second % 3) / 6.0;
    f.roles = RoleCover(roles, fielded, plans);
    return f;
}
// A planning bot keeps two bench slots free, so that it can always buy and reroll. A bench with
// one free slot presses a little and a full bench twice as much.
double BenchPressure(const SeatState &s, const Catalog &c)
{
    if (!Plans(c)) return 0;
    const int benched =
        int(std::count_if(s.roster.begin(), s.roster.end(), [](const OwnedUnit &u) { return !u.onBoard; }));
    return std::max(0, benched + 2 - c.rules.benchCapacity) * 0.3;
}
Cell FacingDirection(Facing facing)
{
    switch (facing)
    {
    case Facing::Forward: return {0, 1};
    case Facing::Right: return {1, 0};
    case Facing::Backward: return {0, -1};
    case Facing::Left: return {-1, 0};
    }
    return {0, 1};
}
double SpatialOpportunity(const OwnedUnit &unit, const SeatState &seat, const PublicSeat *opponent,
                          const Catalog &catalog)
{
    const auto ability = EffectiveAbility(catalog, catalog.units[unit.definition], unit.relic);
    const Cell forward = FacingDirection(unit.facing);
    auto friendlyAt = [&](Cell cell) {
        return std::any_of(seat.roster.begin(), seat.roster.end(), [&](const OwnedUnit &ally) {
            return ally.onBoard && ally.id != unit.id && ally.cell == cell;
        });
    };
    if (ability.mechanic == AbilityMechanic::DirectionalGuard)
    {
        const bool recipient = std::any_of(seat.roster.begin(), seat.roster.end(), [&](const OwnedUnit &ally) {
            const int x = ally.cell.column - unit.cell.column, y = ally.cell.row - unit.cell.row;
            const int behind = -(x * forward.column + y * forward.row);
            return ally.onBoard && ally.id != unit.id && behind > 0 &&
                std::abs(x * forward.row - y * forward.column) <= behind &&
                Distance(unit.cell, ally.cell) <= ability.radius;
        });
        // All rival deployment is in the forward half of local preparation space.
        return recipient ? (forward.row > 0 ? 0.8 : forward.row == 0 ? 0.15 : 0.0) : 0.0;
    }
    if (ability.mechanic == AbilityMechanic::StationaryGrove)
    {
        int allies = 0;
        for (const auto &ally : seat.roster)
            if (ally.onBoard && ally.id != unit.id && Distance(unit.cell, ally.cell) <= ability.radius) ++allies;
        return std::min(3, allies) * 0.2;
    }
    if (ability.mechanic == AbilityMechanic::MomentumCharge)
        return !friendlyAt({unit.cell.column, unit.cell.row + 1}) ? 0.25 : -0.25;
    if (!opponent || opponent->deployment.empty()) return 0;
    std::vector<Cell> enemies;
    for (const auto &enemy : opponent->deployment) enemies.push_back(EncounterCell(enemy.cell, 1, catalog.rules));
    if (ability.mechanic == AbilityMechanic::CocoonProjectile)
        return std::any_of(enemies.begin(), enemies.end(), [&](Cell enemy) {
            return Distance(unit.cell, enemy) <= ability.range;
        }) ? 0.25 : 0.0;
    if (ability.mechanic == AbilityMechanic::TidalPush)
    {
        int aligned = 0;
        for (Cell enemy : enemies)
        {
            const int x = enemy.column - unit.cell.column, y = enemy.row - unit.cell.row;
            const int distance = x * forward.column + y * forward.row;
            if (distance > 0 && distance <= ability.range && x * forward.row == y * forward.column) ++aligned;
        }
        return std::min(3, aligned) * 0.3;
    }
    const bool backline = ability.mechanic == AbilityMechanic::ScreenedStrike;
    if (!backline && ability.mechanic != AbilityMechanic::CrossingBeams) return 0;
    std::stable_sort(enemies.begin(), enemies.end(), [&](Cell a, Cell b) {
        return backline ? Distance(unit.cell, a) > Distance(unit.cell, b) : Distance(unit.cell, a) < Distance(unit.cell, b);
    });
    auto target = std::find_if(enemies.begin(), enemies.end(), [&](Cell cell) { return Distance(unit.cell, cell) <= ability.range; });
    if (target == enemies.end()) return 0;
    if (!backline)
    {
        int crossings = 0;
        for (Cell enemy : enemies)
        {
            if (Distance(enemy, *target) > ability.radius) continue;
            crossings += enemy.column == target->column;
            crossings += enemy.row == target->row;
        }
        return std::min(4, crossings) * 0.12;
    }
    Cell at = unit.cell;
    const int dx = std::abs(target->column - at.column), dy = -std::abs(target->row - at.row);
    const int sx = at.column < target->column ? 1 : -1, sy = at.row < target->row ? 1 : -1;
    int error = dx + dy;
    while (!(at == *target))
    {
        const int twice = 2 * error;
        if (twice >= dy) { error += dy; at.column += sx; }
        if (twice <= dx) { error += dx; at.row += sy; }
        if (!(at == *target) && std::find(enemies.begin(), enemies.end(), at) != enemies.end()) return 0;
    }
    return 0.3;
}
double TacticalScore(const SeatState &seat, const PublicSeat *opponent, const Catalog &catalog)
{
    double score = 0;
    int deployed = 0;
    for (const auto &unit : seat.roster)
    {
        if (!unit.onBoard)
            continue;
        ++deployed;
        const auto &definition = catalog.units[unit.definition];
        const bool frontline = IsFrontline(catalog, definition);
        if (frontline)
            score += double(unit.cell.row) / 3.0;
        else if (IsSupport(catalog, definition))
        {
            int supportRecipients = 0;
            for (const auto &ally : seat.roster)
                if (ally.onBoard && ally.id != unit.id &&
                    Distance(unit.cell, ally.cell) <= (definition.ability.mechanic == AbilityMechanic::StationaryGrove ?
                        EffectiveAbility(catalog, definition, unit.relic).radius : definition.ability.range))
                    ++supportRecipients;
            score += std::min(3, supportRecipients) / 3.0;
        }
        else if (definition.range > 1)
        {
            score += double(3 - unit.cell.row) / 3.0;
            for (const auto &ally : seat.roster)
                if (ally.onBoard && ally.cell.row > unit.cell.row &&
                    std::abs(ally.cell.column - unit.cell.column) <= 1 &&
                    IsFrontline(catalog, catalog.units[ally.definition]))
                {
                    score += 0.4;
                    break;
                }
            if (definition.ability.selector == Selector::RetreatFromCurrentEnemy && unit.cell.row > 0)
            {
                Cell retreat{unit.cell.column, unit.cell.row - 1};
                if (std::none_of(seat.roster.begin(), seat.roster.end(),
                                 [&](const OwnedUnit &ally) { return ally.onBoard && ally.cell == retreat; }))
                    score += 0.5;
            }
        }
        if (opponent && !opponent->deployment.empty())
        {
            int closestColumn = 8;
            bool enemyArea = false;
            for (const auto &enemy : opponent->deployment)
            {
                closestColumn = std::min(closestColumn, std::abs(unit.cell.column - (7 - enemy.cell.column)));
                const auto &enemyAbility = catalog.Definition(enemy.definition, enemy.neutral).ability;
                enemyArea |= enemyAbility.selector == Selector::CurrentEnemyArea ||
                    (catalog.profileId == "wonder_vnext" && enemyAbility.mechanic == AbilityMechanic::CrossingBeams);
            }
            if (frontline)
                score += 0.3 / (1 + closestColumn);
            if (enemyArea)
                for (const auto &ally : seat.roster)
                    if (ally.onBoard && ally.id != unit.id && Distance(unit.cell, ally.cell) <= 1)
                        score -= 0.04;
        }
        if (catalog.profileId == "wonder_vnext") score += SpatialOpportunity(unit, seat, opponent, catalog);
    }
    return score / std::max(1, deployed);
}
} // namespace
Match::Match(Catalog catalog, Id seed, int humans, bool networked) : catalog_(std::move(catalog))
{
    Restart(seed, humans, networked);
}
void Match::Restart(Id seed, int humans, bool networked)
{
    matchNamespace_ = NextMatchNamespace.fetch_add(1);
    if (matchNamespace_ >= (Id(1) << 23))
        throw std::overflow_error("Match namespace exceeds exact snapshot integer range");
    seed_ = seed;
    originalHumans_ = humans;
    networked_ = networked || humans > 1;
    nextUnit_ = 1;
    nextRequest_ = 1;
    round_ = 0;
    pvpRoundIndex_ = 0;
    elapsedMs_ = 0;
    accumulatorMs_ = 0;
    previousGhost_ = -1;
    capped_ = false;
    guided_ = false;
    seats_.clear();
    pairs_.clear();
    encounters_.clear();
    records_.clear();
    botLog_.clear();
    replies_.clear();
    meetings_.clear();
    previousPairs_.clear();
    ghostCounts_.fill(0);
    lastWon_.fill(false);
    pendingRewards_.fill(0);
    for (auto &placed : autoDeployed_) placed.clear();
    botObserveNextMs_.fill(0);
    botObservationRevision_.fill(0);
    for (auto &observation : botObservations_)
        observation.clear();
    if (!catalog_.Validate().empty() || humans < 0 || humans > (catalog_.profileId == "wonder_vnext" ? 8 : 2))
    {
        phase_ = Phase::Aborted;
        remainingMs_ = 0;
        return;
    }
    const auto &r = catalog_.rules;
    for (int i = 0; i < r.seatCount; ++i)
    {
        SeatState s;
        s.id = i;
        s.revision = matchNamespace_ << 32;
        s.health = r.startingHealth;
        s.gold = r.startingGold;
        s.level = r.startingLevel;
        s.human = i < humans;
        s.botIndex = s.human ? i % int(catalog_.bots.size()) : (i - humans) % int(catalog_.bots.size());
        s.label = s.human ? "Captain " + std::to_string(i + 1)
                          : catalog_.bots[(i - humans) % catalog_.bots.size()].label;
        s.shopRng.state = HashValue(seed ^ Id(i + 1) * 0x51ed2705ULL);
        s.botRng.state = HashValue(seed ^ Id(i + 1) * 0xa0761d6478bd642fULL);
        s.relicRng.state = HashValue(seed ^ Id(i + 1) * 0xe7037ed1a0b428dbULL);
        seats_.push_back(s);
    }
    Prepare();
}
void Match::Refresh(SeatState &s)
{
    const auto &weights = catalog_.rules.shopWeights.at(s.level);
    s.shop.clear();
    for (int slot = 0; slot < catalog_.rules.shopSlots; ++slot)
    {
        int draw = s.shopRng.Below(10000), tier = 0;
        while (tier < int(weights.size()) - 1 && draw >= weights[tier])
        {
            draw -= weights[tier];
            ++tier;
        }
        std::vector<int> eligible;
        for (int i = 0; i < int(catalog_.units.size()); ++i)
            if (catalog_.units[i].cost == tier + 1)
                eligible.push_back(i);
        s.shop.push_back(eligible[s.shopRng.Below(int(eligible.size()))]);
    }
}
void Match::GainXp(SeatState &s, int xp)
{
    const auto &r = catalog_.rules;
    if (s.level >= r.maximumLevel)
    {
        s.xp = 0;
        return;
    }
    s.xp += xp;
    while (s.level < r.maximumLevel && s.xp >= r.xpToNext.at(s.level))
    {
        s.xp -= r.xpToNext.at(s.level);
        ++s.level;
    }
    if (s.level == r.maximumLevel)
        s.xp = 0;
}
namespace
{
void MergeRoster(const Catalog &catalog, SeatState &s, std::vector<MergeStep> *steps)
{
    for (int star = 1; star < 3; ++star)
        for (int definition = 0; definition < int(catalog.units.size()); ++definition)
        {
            while (true)
            {
                std::vector<OwnedUnit> group;
                for (const auto &u : s.roster)
                    if (u.definition == definition && u.star == star)
                        group.push_back(u);
                if (group.size() < 3)
                    break;
                std::sort(group.begin(), group.end(), [](const OwnedUnit &a, const OwnedUnit &b) {
                    auto rank = [](const OwnedUnit &u) {
                        return std::make_tuple(u.onBoard      ? 0
                                               : u.bench >= 0 ? 1
                                                              : 2,
                                               u.onBoard ? u.id : Id(u.bench >= 0 ? u.bench : 0), u.id);
                    };
                    return rank(a) < rank(b);
                });
                Id survivor = group[0].id, remove1 = group[1].id, remove2 = group[2].id;
                if (steps) steps->push_back({survivor, star, star + 1, {remove1, remove2}});
                s.roster.erase(
                    std::remove_if(s.roster.begin(), s.roster.end(),
                                   [&](const OwnedUnit &u) { return u.id == remove1 || u.id == remove2; }),
                    s.roster.end());
                for (auto &u : s.roster)
                    if (u.id == survivor)
                        ++u.star;
            }
        }
    for (auto &u : s.roster)
        if (!u.onBoard && u.bench < 0)
        {
            for (int slot = 0; slot < catalog.rules.benchCapacity; ++slot)
                if (std::none_of(s.roster.begin(), s.roster.end(),
                                 [&](const OwnedUnit &v) { return !v.onBoard && v.bench == slot; }))
                {
                    u.bench = slot;
                    break;
                }
        }
}
bool LegalRoster(const Catalog &catalog, const SeatState &s)
{
    if (s.gold < 0 || s.level < catalog.rules.startingLevel || s.level > catalog.rules.maximumLevel)
        return false;
    std::set<int> bench;
    std::set<std::pair<int, int>> cells;
    std::set<Id> ids;
    std::set<int> ownedRelics(s.ownedRelics.begin(), s.ownedRelics.end()), assignedRelics, offers;
    if (ownedRelics.size() != s.ownedRelics.size() ||
        int(ownedRelics.size()) > catalog.rules.maximumRelics || s.pendingRelicDrafts < 0 ||
        int(ownedRelics.size()) + s.pendingRelicDrafts > catalog.rules.maximumRelics ||
        s.relicOffers.size() > 3 || (!s.relicOffers.empty() && s.pendingRelicDrafts == 0))
        return false;
    for (int relic : ownedRelics)
        if (relic < 0 || relic >= int(catalog.relics.size())) return false;
    for (int relic : s.relicOffers)
        if (relic < 0 || relic >= int(catalog.relics.size()) || ownedRelics.count(relic) ||
            !offers.insert(relic).second) return false;
    int deployed = 0;
    for (const auto &u : s.roster)
    {
        if (u.id == 0 || u.id >= (Id(1) << 20) || !ids.insert(u.id).second || u.definition < 0 || u.definition >= int(catalog.units.size()) ||
            u.star < 1 || u.star > 3 || u.neutral || u.hpScaleBp != 10000 || u.damageScaleBp != 10000 ||
            int(u.facing) < 0 || int(u.facing) > 3)
            return false;
        if (u.relic < -1 || (u.relic >= 0 &&
            (!ownedRelics.count(u.relic) || !assignedRelics.insert(u.relic).second ||
             !RelicCompatible(catalog.relics[u.relic], catalog.units[u.definition].ability.mechanic))))
            return false;
        if (u.onBoard)
        {
            ++deployed;
            if (u.cell.column < 0 || u.cell.column >= catalog.rules.columns || u.cell.row < 0 ||
                u.cell.row >= catalog.rules.deploymentRows ||
                !cells.insert({u.cell.column, u.cell.row}).second)
                return false;
        }
        else if (u.bench < 0 || u.bench >= catalog.rules.benchCapacity || !bench.insert(u.bench).second)
            return false;
    }
    return deployed <= s.level;
}
bool ApplyRosterCommand(const Catalog &catalog, SeatState &s, const Command &cmd, Id &nextUnit,
                        std::string &reason, std::vector<MergeStep> *steps = nullptr)
{
    const auto &r = catalog.rules;
    auto reject = [&](const std::string &text) { reason = text; return false; };
    if (cmd.type == CommandType::Buy)
    {
        if (cmd.slot < 0 || cmd.slot >= int(s.shop.size()) || s.shop[cmd.slot] < 0)
            return reject("Offer is empty or unavailable");
        int definition = s.shop[cmd.slot];
        if (definition >= int(catalog.units.size())) return reject("Offer definition is invalid");
        int cost = catalog.units[definition].cost;
        if (s.gold < cost)
            return reject("Not enough gold");
        OwnedUnit u;
        u.id = nextUnit++;
        u.definition = definition;
        s.roster.push_back(u);
        s.gold -= cost;
        s.shop[cmd.slot] = -1;
        MergeRoster(catalog, s, steps);
        if (!LegalRoster(catalog, s))
            return reject("Bench full; purchase does not resolve into a legal merge");
    }
    else if (cmd.type == CommandType::Sell)
    {
        auto it = std::find_if(s.roster.begin(), s.roster.end(),
                               [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (it == s.roster.end())
            return reject("Unit is not owned");
        s.gold += catalog.units[it->definition].cost * CountCopies(it->star);
        s.roster.erase(it);
    }
    else if (cmd.type == CommandType::Move)
    {
        auto it = std::find_if(s.roster.begin(), s.roster.end(),
                               [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (it == s.roster.end())
            return reject("Unit is not owned");
        if (cmd.toBoard && (cmd.cell.column < 0 || cmd.cell.column >= r.columns || cmd.cell.row < 0 ||
                            cmd.cell.row >= r.deploymentRows))
            return reject("Destination is outside own deployment");
        if (!cmd.toBoard && (cmd.slot < 0 || cmd.slot >= r.benchCapacity))
            return reject("Invalid bench slot");
        auto occupied = std::find_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &u) {
            return u.id != cmd.unit && u.onBoard == cmd.toBoard &&
                   (cmd.toBoard ? u.cell == cmd.cell : u.bench == cmd.slot);
        });
        bool oldBoard = it->onBoard;
        Cell oldCell = it->cell;
        int oldBench = it->bench;
        if (occupied != s.roster.end())
        {
            occupied->onBoard = oldBoard;
            occupied->cell = oldCell;
            occupied->bench = oldBench;
        }
        it->onBoard = cmd.toBoard;
        it->cell = cmd.toBoard ? cmd.cell : Cell{};
        it->bench = cmd.toBoard ? -1 : cmd.slot;
        if (!LegalRoster(catalog, s))
            return reject("Move exceeds deployment capacity");
    }
    else
        return reject("This preview supports purchases, placement and sales only");
    s.ready = false;
    return true;
}
} // namespace
bool Match::Legal(const SeatState &s) const
{
    return LegalRoster(catalog_, s);
}
RosterPreview PreviewRosterCommand(const Catalog &catalog, const SeatState &owner, const Command &command)
{
    RosterPreview preview;
    preview.resulting = owner;
    if (!LegalRoster(catalog, owner))
    {
        preview.reason = "Owner roster is unavailable or invalid";
        return preview;
    }
    Id next = 1;
    for (const auto &u : owner.roster) next = std::max(next, u.id + 1);
    if (next >= (Id(1) << 20))
    {
        preview.reason = "Unit identity space is exhausted";
        return preview;
    }
    preview.hypotheticalId = command.type == CommandType::Buy ? next : 0;
    preview.accepted = ApplyRosterCommand(catalog, preview.resulting, command, next, preview.reason,
                                          &preview.mergeSteps);
    if (!preview.accepted)
    {
        preview.resulting = owner;
        preview.mergeSteps.clear();
        preview.hypotheticalId = 0;
    }
    else preview.reason = "Owner-state preview; final action requires server acceptance";
    return preview;
}
bool Match::ApplyCommand(SeatState &s, const Command &cmd, Id &nextUnit, std::string &reason)
{
    const auto &r = catalog_.rules;
    auto reject = [&](const std::string &text) {
        reason = text;
        return false;
    };
    if (cmd.type == CommandType::Buy || cmd.type == CommandType::Move || cmd.type == CommandType::Sell)
        return ApplyRosterCommand(catalog_, s, cmd, nextUnit, reason);
    else if (cmd.type == CommandType::Reroll)
    {
        if (s.gold < r.rerollCost)
            return reject("Not enough gold");
        s.gold -= r.rerollCost;
        s.shopLocked = false;
        Refresh(s);
    }
    else if (cmd.type == CommandType::ToggleLock)
        s.shopLocked = !s.shopLocked;
    else if (cmd.type == CommandType::BuyXp)
    {
        if (s.level >= r.maximumLevel)
            return reject("Already at maximum level");
        if (s.gold < r.buyXpGold)
            return reject("Not enough gold");
        s.gold -= r.buyXpGold;
        GainXp(s, r.buyXpAmount);
    }
    else if (cmd.type == CommandType::SetFacing)
    {
        if (catalog_.profileId != "wonder_vnext") return reject("Orientation is unavailable in this profile");
        if (int(cmd.facing) < 0 || int(cmd.facing) > 3) return reject("Invalid orientation");
        auto unit = std::find_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (unit == s.roster.end()) return reject("Unit is not owned");
        unit->facing = cmd.facing;
    }
    else if (cmd.type == CommandType::ChooseRelic)
    {
        if (s.pendingRelicDrafts <= 0 || cmd.slot < 0 || cmd.slot >= int(s.relicOffers.size()) ||
            int(s.ownedRelics.size()) >= r.maximumRelics) return reject("Relic choice is unavailable");
        s.ownedRelics.push_back(s.relicOffers[cmd.slot]);
        s.relicOffers.clear();
        --s.pendingRelicDrafts;
        OfferRelics(catalog_, s);
    }
    else if (cmd.type == CommandType::EquipRelic || cmd.type == CommandType::UnequipRelic)
    {
        auto unit = std::find_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (unit == s.roster.end()) return reject("Unit is not owned");
        if (cmd.type == CommandType::UnequipRelic) unit->relic = -1;
        else
        {
            if (cmd.slot < 0 || cmd.slot >= int(catalog_.relics.size()) ||
                std::find(s.ownedRelics.begin(), s.ownedRelics.end(), cmd.slot) == s.ownedRelics.end())
                return reject("Relic is not owned");
            if (!RelicCompatible(catalog_.relics[cmd.slot], catalog_.units[unit->definition].ability.mechanic))
                return reject("Relic is incompatible with this ability");
            for (auto &other : s.roster) if (other.relic == cmd.slot) other.relic = -1;
            unit->relic = cmd.slot;
        }
    }
    else if (cmd.type == CommandType::Ready)
        s.ready = true;
    else
        return reject("Unknown command");
    if (cmd.type != CommandType::Ready)
        s.ready = false;
    if (!Legal(s)) return reject("Command would produce invalid owned state");
    return true;
}
Reply Match::Submit(int authenticatedSeat, const Command &cmd)
{
    Reply reply;
    reply.reason = "Invalid seat ownership";
    if (authenticatedSeat < 0 || authenticatedSeat >= int(seats_.size()) || cmd.seat != authenticatedSeat)
        return reply;
    auto &s = seats_[authenticatedSeat];
    reply.revision = s.revision;
    reply.sequence = s.sequence;
    auto cached = replies_.find({authenticatedSeat, cmd.requestId});
    if (cached != replies_.end())
    {
        if (EqualCommand(cached->second.command, cmd))
            return cached->second.reply;
        reply.reason = "Request ID reused with different payload";
        return reply;
    }
    if (phase_ != Phase::Preparation)
    {
        reply.reason = "Preparation is locked";
        return reply;
    }
    if (s.health <= 0)
    {
        reply.reason = "Seat is eliminated";
        return reply;
    }
    if (cmd.sequence != s.sequence + 1)
    {
        reply.reason = "Out-of-order command sequence";
        return reply;
    }
    if (cmd.revision != s.revision)
    {
        reply.reason = "Stale seat revision";
        return reply;
    }
    SeatState pending = s;
    Id next = nextUnit_;
    std::string reason;
    if (!ApplyCommand(pending, cmd, next, reason))
    {
        reply.reason = reason;
        return reply;
    }
    pending.sequence = cmd.sequence;
    ++pending.revision;
    s = std::move(pending);
    nextUnit_ = next;
    reply.accepted = true;
    reply.reason = "Accepted";
    reply.revision = s.revision;
    reply.sequence = s.sequence;
    replies_[{authenticatedSeat, cmd.requestId}] = {cmd, reply};
    return reply;
}
std::vector<PublicSeat> Match::PublicSeats() const
{
    std::vector<PublicSeat> result;
    for (const auto &s : seats_)
    {
        PublicSeat p;
        p.id = s.id;
        p.health = s.health;
        p.level = s.level;
        p.placement = s.placement;
        p.wins = s.wins;
        p.human = s.human;
        p.ready = s.ready;
        p.takeover = s.takeover;
        p.label = s.label;
        for (const auto &u : s.roster)
            if (u.onBoard)
                p.deployment.push_back(u);
        result.push_back(p);
    }
    return result;
}
void Match::Pair()
{
    std::vector<int> active;
    for (const auto &s : seats_)
        if (s.health > 0)
            active.push_back(s.id);
    pairs_.clear();
    auto prior = [&](int a, int b) {
        return std::find(previousPairs_.begin(), previousPairs_.end(), Key(a, b)) != previousPairs_.end();
    };
    auto tie = [&](Id value) { return HashValue(seed_ ^ Id(round_) * 0x9e3779b9ULL ^ value); };
    if (active.size() % 2)
    {
        int recipient = *std::min_element(active.begin(), active.end(), [&](int a, int b) {
            return std::make_tuple(ghostCounts_[a], a == previousGhost_, tie(Id(a) ^ 0xabcULL)) <
                   std::make_tuple(ghostCounts_[b], b == previousGhost_, tie(Id(b) ^ 0xabcULL));
        });
        active.erase(std::find(active.begin(), active.end(), recipient));
        int donor = *std::min_element(active.begin(), active.end(), [&](int a, int b) {
            return std::make_tuple(prior(a, recipient), meetings_[Key(a, recipient)],
                                   tie(Id(a + recipient * 8) ^ 0xdefULL)) <
                   std::make_tuple(prior(b, recipient), meetings_[Key(b, recipient)],
                                   tie(Id(b + recipient * 8) ^ 0xdefULL));
        });
        pairs_.push_back({recipient, donor, true, EncounterKind::Ghost, {}});
        ++ghostCounts_[recipient];
        previousGhost_ = recipient;
    }
    std::vector<std::pair<int, int>> best;
    std::tuple<int, int, Id> bestScore{999, 999, ~Id(0)};
    std::function<void(std::vector<int>, std::vector<std::pair<int, int>>)> enumerate =
        [&](std::vector<int> remaining, std::vector<std::pair<int, int>> candidate) {
            if (remaining.empty())
            {
                std::sort(candidate.begin(), candidate.end());
                int repeats = 0, history = 0;
                Id hash = 0;
                for (auto p : candidate)
                {
                    repeats += prior(p.first, p.second) ? 1 : 0;
                    history += meetings_[p];
                    hash = HashValue(hash ^ Id(p.first * 8 + p.second + 1));
                }
                auto score = std::make_tuple(repeats, history, tie(hash));
                if (score < bestScore)
                {
                    bestScore = score;
                    best = candidate;
                }
                return;
            }
            int a = remaining.front();
            for (std::size_t i = 1; i < remaining.size(); ++i)
            {
                auto rest = remaining;
                int b = rest[i];
                rest.erase(rest.begin() + i);
                rest.erase(rest.begin());
                auto next = candidate;
                next.push_back(Key(a, b));
                enumerate(rest, next);
            }
        };
    enumerate(active, {});
    for (auto p : best)
        pairs_.push_back({p.first, p.second, false});
    previousPairs_.clear();
    for (auto p : pairs_)
    {
        auto key = Key(p.a, p.b);
        ++meetings_[key];
        previousPairs_.push_back(key);
    }
}
void Match::Prepare()
{
    ++round_;
    phase_ = Phase::Preparation;
    remainingMs_ = PreparationMs(catalog_.rules, round_);
    for (auto &placed : autoDeployed_) placed.clear();
    botCommands_.fill(0);
    botRerolls_.fill(0);
    botNextMs_.fill(elapsedMs_);
    encounters_.clear();
    for (auto &s : seats_)
        if (s.health > 0)
        {
            if (round_ > 1)
            {
                s.gold += catalog_.rules.baseIncome + pendingRewards_[s.id] + StreakIncome(catalog_.rules, s.streak) +
                          std::min(catalog_.rules.interestCap, s.lockGold / catalog_.rules.interestDivisor);
                GainXp(s, catalog_.rules.passiveXp);
                pendingRewards_[s.id] = 0;
            }
            if (!s.shopLocked || round_ == 1)
                Refresh(s);
            if (std::find(catalog_.rules.relicRounds.begin(), catalog_.rules.relicRounds.end(), round_ - 1) !=
                catalog_.rules.relicRounds.end() &&
                int(s.ownedRelics.size()) + s.pendingRelicDrafts < catalog_.rules.maximumRelics)
                ++s.pendingRelicDrafts;
            OfferRelics(catalog_, s);
            s.ready = false;
            ++s.revision;
        }
    if (NeutralRound())
    {
        pairs_.clear();
        const auto *wave = CurrentWave();
        if (!wave) { Abort(); return; }
        for (const auto &s : seats_) if (s.health > 0)
            pairs_.push_back({s.id, -1, false, EncounterKind::Neutral, wave->id});
    }
    else
    {
        ++pvpRoundIndex_;
        Pair();
    }
}
void Match::BeginGuidedStage(const GuidedStage &stage)
{
    const auto &r = catalog_.rules;
    guided_ = true;
    phase_ = Phase::Preparation;
    round_ = stage.round;
    pvpRoundIndex_ = 0;
    for (int round = 1; round <= round_; ++round) pvpRoundIndex_ += !IsNeutralRound(round, r);
    remainingMs_ = PreparationMs(r, round_);
    encounters_.clear(); records_.clear(); pairs_.clear(); previousPairs_.clear(); meetings_.clear();
    pendingRewards_.fill(0); lastWon_.fill(false); botCommands_.fill(0); botRerolls_.fill(0);
    for (auto &placed : autoDeployed_) placed.clear();
    const auto fill = [&](SeatState &seat, const std::vector<GuidedUnit> &board, const std::vector<GuidedUnit> &bench) {
        seat.roster.clear();
        int slot = 0;
        for (int benched = 0; benched < 2; ++benched)
            for (const auto &unit : benched ? bench : board)
            {
                OwnedUnit owned;
                owned.id = nextUnit_++;
                owned.definition = unit.definition;
                owned.star = unit.star;
                owned.onBoard = !benched;
                if (benched) owned.bench = slot++;
                else owned.cell = unit.cell;
                seat.roster.push_back(owned);
            }
    };
    for (auto &seat : seats_)
    {
        seat.ready = seat.shopLocked = false;
        seat.lockGold = seat.xp = seat.streak = seat.pendingRelicDrafts = 0;
        seat.relicOffers.clear();
        seat.ownedRelics.clear();
        ++seat.revision;
        // Only the captain and one opponent play; the others are out and hold the last places.
        seat.health = seat.id < 2 ? r.startingHealth : 0;
        seat.placement = seat.id < 2 ? 0 : seat.id + 1;
        if (seat.id >= 2) seat.roster.clear();
    }
    auto &captain = seats_[0];
    auto &opponent = seats_[1];
    captain.gold = stage.gold;
    captain.level = stage.level;
    captain.streak = stage.streak;
    fill(captain, stage.board, stage.bench);
    captain.shop = stage.shop;
    captain.shop.resize(r.shopSlots, -1);
    if (stage.relicDraft)
    {
        captain.pendingRelicDrafts = 1;
        OfferRelics(catalog_, captain);
    }
    opponent.gold = 0;
    opponent.level = std::clamp(int(stage.opponent.size()), r.startingLevel, r.maximumLevel);
    fill(opponent, stage.opponent, {});
    opponent.shop.assign(r.shopSlots, -1);
    opponent.ready = true;
    if (IsNeutralRound(round_, r))
    {
        if (const auto *wave = CurrentWave())
            for (int seat = 0; seat < 2; ++seat) pairs_.push_back({seat, -1, false, EncounterKind::Neutral, wave->id});
    }
    else pairs_.push_back({0, 1, false, EncounterKind::Pvp, {}});
}
bool Match::GuidedStepDone(const GuidedStep &step, const GuidedView &view) const
{
    const auto &captain = seats_[0];
    const auto owns = [&](auto &&test) {
        return std::any_of(captain.roster.begin(), captain.roster.end(),
                           [&](const OwnedUnit &unit) { return unit.definition == step.definition && test(unit); });
    };
    if (step.done == "deployed_at_least")
        return std::count_if(captain.roster.begin(), captain.roster.end(), [](const OwnedUnit &unit) { return unit.onBoard; }) >= step.value;
    if (step.done == "ready") return captain.ready || phase_ != Phase::Preparation;
    if (step.done == "fight_over") return !records_.empty();
    if (step.done == "shop_open") return view.shopOpen;
    if (step.done == "trait_focus") return view.traitFocus == step.trait;
    if (step.done == "owns") return owns([](const OwnedUnit &) { return true; });
    if (step.done == "star_at_least") return owns([&](const OwnedUnit &unit) { return unit.star >= step.value; });
    if (step.done == "row_at_least") return owns([&](const OwnedUnit &unit) { return unit.onBoard && unit.cell.row >= step.value; });
    if (step.done == "row_at_most") return owns([&](const OwnedUnit &unit) { return unit.onBoard && unit.cell.row <= step.value; });
    if (step.done == "level_at_least") return captain.level >= step.value;
    if (step.done == "gold_at_least") return captain.gold >= step.value;
    if (step.done == "shop_locked") return captain.shopLocked;
    if (step.done == "relic_owned") return int(captain.ownedRelics.size()) >= step.value;
    if (step.done == "relic_equipped")
        return std::any_of(captain.roster.begin(), captain.roster.end(), [](const OwnedUnit &unit) { return unit.relic >= 0; });
    if (step.done == "trait_at_least")
    {
        std::set<int> members;
        for (const auto &unit : captain.roster)
            if (unit.onBoard && (catalog_.units[unit.definition].race == step.trait || catalog_.units[unit.definition].unitClass == step.trait))
                members.insert(unit.definition);
        return int(members.size()) >= step.value;
    }
    return false;
}
// Fills free board places from the bench, lowest bench slot first. Each unit takes the free cell
// nearest the middle of the back row, so a unit nobody placed is at least not in front.
void Match::AutoDeploy(SeatState &s)
{
    int deployed = 0;
    std::vector<OwnedUnit *> bench;
    for (auto &u : s.roster)
    {
        if (u.onBoard) ++deployed;
        else bench.push_back(&u);
    }
    std::sort(bench.begin(), bench.end(), [](const OwnedUnit *l, const OwnedUnit *r) { return l->bench < r->bench; });
    const auto &r = catalog_.rules;
    for (auto *unit : bench)
    {
        if (deployed >= s.level) break;
        bool found = false;
        Cell best;
        std::tuple<int, int, int> bestKey{};
        for (int row = 0; row < r.deploymentRows; ++row)
            for (int column = 0; column < r.columns; ++column)
            {
                const Cell cell{column, row};
                if (std::any_of(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &v) { return v.onBoard && v.cell == cell; }))
                    continue;
                const auto key = std::make_tuple(row, std::abs(2 * column - (r.columns - 1)), column);
                if (!found || key < bestKey) { bestKey = key; best = cell; found = true; }
            }
        if (!found) break;
        unit->onBoard = true;
        unit->cell = best;
        unit->bench = -1;
        ++deployed;
        autoDeployed_[s.id].push_back(unit->id);
    }
}
void Match::Lock()
{
    if (phase_ != Phase::Preparation)
        return;
    phase_ = Phase::Combat;
    remainingMs_ = catalog_.rules.combatTimeoutMs;
    encounters_.clear();
    for (auto &s : seats_)
        if (s.health > 0)
        {
            if (catalog_.rules.autoDeploy) AutoDeploy(s);
            s.lockGold = s.gold;
            ++s.revision;
        }
    for (std::size_t i = 0; i < pairs_.size(); ++i)
    {
        auto p = pairs_[i];
        Id encounterId = Id(round_) * 8 + i + 1;
        const Id identityNamespace = (matchNamespace_ << 9) | encounterId;
        if (p.kind == EncounterKind::Neutral)
        {
            const auto *wave = CurrentWave();
            std::vector<OwnedUnit> neutral;
            for (std::size_t slot = 0; slot < wave->slots.size(); ++slot)
            {
                OwnedUnit unit;
                unit.id = slot + 1;
                unit.definition = wave->slots[slot].definition;
                unit.cell = wave->slots[slot].cell;
                unit.onBoard = true;
                unit.neutral = true;
                unit.hpScaleBp = wave->hpScaleBp;
                unit.damageScaleBp = wave->damageScaleBp;
                neutral.push_back(unit);
            }
            encounters_.emplace_back(p, Combat(catalog_, seats_[p.a].roster, neutral,
                                               HashValue(seed_ ^ encounterId), identityNamespace));
        }
        else encounters_.emplace_back(p, Combat(catalog_, seats_[p.a].roster, seats_[p.b].roster,
                                               HashValue(seed_ ^ encounterId), identityNamespace));
    }
}
Id Match::StateHash() const
{
    Id hash = HashValue(seed_ ^ Id(round_));
    auto add = [&](Id value) { hash = HashValue(hash ^ HashValue(value)); };
    auto text = [&](const std::string &value) {
        for (unsigned char ch : value)
            add(ch);
    };
    text(catalog_.contentDigest);
    add(Id(phase_));
    add(Id(pvpRoundIndex_));
    add(nextUnit_);
    add(nextRequest_);
    add(Id(remainingMs_));
    if (catalog_.profileId == "wonder_vnext")
    {
        add(Id(originalHumans_));
        add(networked_);
    }
    for (const auto &s : seats_)
    {
        add(Id(s.id));
        add(Id(s.health));
        add(Id(s.gold));
        add(Id(s.xp));
        add(Id(s.level));
        add(Id(s.wins));
        add(Id(s.neutralWins)); add(Id(s.neutralLosses)); add(Id(s.neutralDraws));
        if (catalog_.profileId == "wonder_vnext") add(Id(static_cast<Int>(s.streak)));
        add(Id(pendingRewards_[s.id]));
        add(Id(s.placement));
        add(Id(s.lockGold));
        add(Id(s.botIndex));
        add(s.human);
        add(s.takeover);
        add(s.ready);
        add(s.shopLocked);
        // Transport namespace deliberately does not affect seeded replay equivalence.
        add(s.revision & 0xffffffffULL);
        add(s.sequence);
        add(s.shopRng.state);
        add(s.botRng.state);
        if (catalog_.profileId == "wonder_vnext")
        {
            add(s.relicRng.state);
            add(Id(s.pendingRelicDrafts));
            add(Id(s.ownedRelics.size()));
            for (int relic : s.ownedRelics) add(Id(relic + 1));
            add(Id(s.relicOffers.size()));
            for (int relic : s.relicOffers) add(Id(relic + 1));
        }
        for (int offer : s.shop)
            add(Id(offer + 1));
        for (const auto &u : s.roster)
        {
            add(u.id);
            add(Id(u.definition));
            add(Id(u.star));
            add(u.onBoard);
            add(Id(u.cell.column + 1));
            add(Id(u.cell.row + 1));
            add(Id(u.bench + 1));
            if (catalog_.profileId == "wonder_vnext") { add(Id(u.facing)); add(Id(u.relic + 1)); }
        }
    }
    for (auto pair : pairs_)
    {
        add(Id(pair.a));
        add(Id(pair.b));
        add(pair.ghost);
    }
    for (const auto &history : meetings_)
    {
        add(Id(history.first.first));
        add(Id(history.first.second));
        add(Id(history.second));
    }
    for (int count : ghostCounts_)
        add(Id(count));
    add(Id(previousGhost_ + 1));
    return hash;
}
void Match::Settle()
{
    if (!records_.empty() && records_.back().round == round_)
        return;
    RoundRecord record;
    record.round = round_;
    record.pvpRoundIndex = pvpRoundIndex_;
    record.neutral = NeutralRound();
    record.settlementId = HashValue(seed_ ^ Id(round_) ^ (matchNamespace_ << 32));
    record.preHash = StateHash();
    record.pairs = pairs_;
    lastWon_.fill(false);
    int base = 0;
    for (const auto &stage : catalog_.rules.lossStages)
        if (pvpRoundIndex_ >= stage.start && pvpRoundIndex_ <= stage.end)
            base = stage.damage;
    for (const auto &e : encounters_)
    {
        const auto &r = e.combat.Result();
        record.results.push_back(r);
        EncounterSummary summary;
        summary.pairing = e.pairing;
        summary.kind = e.kind;
        summary.sides = e.sides;
        summary.result = r;
        std::map<Id, int> targetSides;
        for (const auto &unit : e.combat.Units())
            targetSides.emplace(unit.id, unit.side);
        for (const auto &event : e.combat.Events())
        {
            const int side = targetSides.at(event.target);
            summary.healthLoss[side] += event.healthLoss;
            summary.absorbed[side] += event.absorbed;
            if (event.effect == Effect::Heal)
                summary.healing[side] += event.resolved;
        }
        record.encounters.push_back(std::move(summary));
        for (int side = 0; side < 2; ++side)
        {
            if (!e.sides[side].seat || (e.kind == EncounterKind::Ghost && side == 1))
                continue;
            int seat = *e.sides[side].seat;
            bool win = r.winner == side;
            if (e.kind == EncounterKind::Neutral)
            {
                if (win) ++seats_[seat].neutralWins;
                else if (r.winner < 0) ++seats_[seat].neutralDraws;
                else ++seats_[seat].neutralLosses;
                pendingRewards_[seat] = win ? catalog_.rules.neutralWinIncome : 0;
                record.damage[seat] = win ? 0 : round_ <= catalog_.rules.neutralOpeningRounds ?
                    catalog_.rules.neutralOpeningDamage : catalog_.rules.neutralLossDamage;
            }
            else
            {
                lastWon_[seat] = win;
                auto &streak = seats_[seat].streak;
                streak = r.winner < 0 ? 0 : win ? std::max(streak, 0) + 1 : std::min(streak, 0) - 1;
                if (win) ++seats_[seat].wins;
                pendingRewards_[seat] = win ? catalog_.rules.winIncome + TraitWinGold(seats_[seat], catalog_) : 0;
                record.damage[seat] = r.winner < 0 ? catalog_.rules.drawDamage
                                      : win ? 0 : base + r.survivors[1 - side];
            }
            record.pendingRewards[seat] = pendingRewards_[seat];
        }
    }
    std::vector<int> eliminated, alive;
    std::array<int, 8> raw{};
    for (auto &s : seats_)
        if (s.health > 0)
        {
            raw[s.id] = s.health - record.damage[s.id];
            if (raw[s.id] <= 0)
                eliminated.push_back(s.id);
            else
                alive.push_back(s.id);
            s.health = std::max(0, raw[s.id]);
        }
    auto rank = [&](std::vector<int> group, int starting) {
        std::sort(group.begin(), group.end(), [&](int a, int b) {
            return std::make_tuple(raw[a], seats_[a].wins) > std::make_tuple(raw[b], seats_[b].wins);
        });
        int place = starting;
        for (std::size_t i = 0; i < group.size(); ++i)
        {
            if (i && std::make_tuple(raw[group[i]], seats_[group[i]].wins) !=
                         std::make_tuple(raw[group[i - 1]], seats_[group[i - 1]].wins))
                place = starting + int(i);
            seats_[group[i]].placement = place;
        }
    };
    rank(eliminated, int(alive.size()) + 1);
    if (alive.size() <= 1 || round_ >= catalog_.rules.maxRounds)
    {
        rank(alive, 1);
        capped_ = alive.size() > 1;
        phase_ = Phase::Finished;
        remainingMs_ = 0;
    }
    else
    {
        phase_ = Phase::Settlement;
        remainingMs_ = catalog_.rules.settlementMs;
    }
    for (const auto &s : seats_)
    {
        record.gold[s.id] = s.gold;
        record.health[s.id] = s.health;
        record.placement[s.id] = s.placement;
        record.wins[s.id] = s.wins;
    }
    record.postHash = StateHash();
    records_.push_back(record);
}
Cell Match::FormationCell(const SeatState &s, const OwnedUnit &u) const
{
    const auto &d = catalog_.units[u.definition];
    const auto *role = RoleOf(catalog_, d);
    int preferred = role ? role->row
                    : d.unitClass == "guardian"  ? 3
                    : d.unitClass == "warrior" ? 3
                    : d.unitClass == "rogue"   ? 2
                    : d.unitClass == "priest"  ? 1
                                               : 0;
    std::array<int, 8> columns{3, 4, 2, 5, 1, 6, 0, 7};
    if (role ? role->flank : d.unitClass == "rogue")
        columns = {0, 7, 1, 6, 2, 5, 3, 4};
    for (int delta = 0; delta < 4; ++delta)
    {
        int row = (preferred + delta) % 4;
        for (int col : columns)
        {
            Cell cell{col, row};
            if (std::none_of(s.roster.begin(), s.roster.end(),
                             [&](const OwnedUnit &v) { return v.onBoard && v.cell == cell; }))
                return cell;
        }
    }
    return {};
}
int TraitWinGold(const SeatState &s, const Catalog &c)
{
    std::map<std::string, std::set<int>> counts;
    for (const auto &u : s.roster)
        if (u.onBoard)
        {
            counts[c.units[u.definition].race].insert(u.definition);
            counts[c.units[u.definition].unitClass].insert(u.definition);
        }
    int gold = 0;
    for (const auto &t : c.traits)
        if (t.stat == "win_gold_flat") gold += TraitValue(t, int(counts[t.id].size()));
    return gold;
}
double BotLineupValue(const SeatState &s, const Catalog &c, const BotDef &b)
{
    auto f = Evaluate(s, c, b);
    return f.budget + f.roles + f.traits * b.synergy;
}
double Match::FormationScore(const SeatState &s, const BotDef &b) const
{
    return BotLineupValue(s, catalog_, b);
}
void Match::BotTurn(int seat)
{
    auto &s = seats_[seat];
    const auto &bot = catalog_.bots[s.botIndex];
    if (s.human || s.health <= 0 || s.ready)
        return;
    if (catalog_.profileId == "wonder_vnext" && botCommands_[seat] < bot.maxCommands - 1)
    {
        Command relicCommand;
        std::string relicAction;
        if (!s.relicOffers.empty())
        {
            relicCommand.type = CommandType::ChooseRelic;
            relicCommand.slot = 0;
            int bestMatches = -1;
            for (int slot = 0; slot < int(s.relicOffers.size()); ++slot)
            {
                int matches = 0;
                for (const auto &unit : s.roster)
                    if (RelicCompatible(catalog_.relics[s.relicOffers[slot]], catalog_.units[unit.definition].ability.mechanic))
                        matches += unit.onBoard ? 2 : 1;
                if (matches > bestMatches) { bestMatches = matches; relicCommand.slot = slot; }
            }
            relicAction = "choose_relic";
        }
        else
            for (int relic : s.ownedRelics)
            {
                if (std::any_of(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &unit) { return unit.relic == relic; }))
                    continue;
                const OwnedUnit *holder = nullptr;
                for (const auto &unit : s.roster)
                    if (unit.onBoard && unit.relic < 0 &&
                        RelicCompatible(catalog_.relics[relic], catalog_.units[unit.definition].ability.mechanic) &&
                        (!holder || unit.star > holder->star || (unit.star == holder->star && unit.id < holder->id)))
                        holder = &unit;
                if (holder)
                {
                    relicCommand.type = CommandType::EquipRelic;
                    relicCommand.slot = relic;
                    relicCommand.unit = holder->id;
                    relicAction = "equip_relic";
                    break;
                }
            }
        if (!relicAction.empty())
        {
            relicCommand.seat = seat;
            relicCommand.requestId = (Id(1) << 63) | nextRequest_++;
            relicCommand.sequence = s.sequence + 1;
            relicCommand.revision = s.revision;
            BotDecision log;
            log.round = round_; log.seat = seat; log.action = relicAction;
            log.observationRevision = botObservationRevision_[seat];
            log.reply = Submit(seat, relicCommand); log.goldAfter = seats_[seat].gold;
            botLog_.push_back(log);
            if (log.reply.accepted) ++botCommands_[seat];
            return;
        }
    }
    Command chosen;
    chosen.type = CommandType::Ready;
    std::string action = "ready";
    double best = 0;
    std::array<double, 8> features{};
    int deployed =
        int(std::count_if(s.roster.begin(), s.roster.end(), [](const OwnedUnit &u) { return u.onBoard; }));
    // Repair deployment before economic evaluation, through the same transaction API.
    if (botCommands_[seat] < bot.maxCommands - 1 && deployed < s.level)
    {
        const OwnedUnit *bestUnit = nullptr;
        double score = -1;
        for (const auto &u : s.roster)
            if (!u.onBoard)
            {
                SeatState single;
                single.level = 1;
                single.roster = {u};
                double value = FormationScore(single, bot);
                if (value > score)
                {
                    score = value;
                    bestUnit = &u;
                }
            }
        if (bestUnit)
        {
            chosen.type = CommandType::Move;
            chosen.unit = bestUnit->id;
            chosen.toBoard = true;
            chosen.cell = FormationCell(s, *bestUnit);
            best = 1;
            action = "deploy";
        }
    }
    // A unit swapped in from the bench inherits the replaced unit's cell and can stand in the
    // wrong half for its class. Only catalogues that carry class roles ask for this.
    if (chosen.type == CommandType::Ready && botCommands_[seat] < bot.maxCommands - 1 &&
        remainingMs_ > catalog_.rules.botRepositionCutoffMs)
        for (const auto &u : s.roster)
        {
            if (!u.onBoard) continue;
            const auto &d = catalog_.units[u.definition];
            const auto *role = RoleOf(catalog_, d);
            if (!role) continue;
            const bool frontline = role->role == BotRole::Frontline;
            // A ranged class that the catalogue stands in the front half, such as an assassin with a short reach, is left there.
            const bool wrongHalf = frontline ? u.cell.row < 2
                : role->role == BotRole::Damage && d.range > 1 && role->row < 2 && u.cell.row > 1;
            if (!wrongHalf) continue;
            const Cell target = FormationCell(s, u);
            if (frontline != (target.row >= 2)) continue; // no free cell in the right half
            chosen.type = CommandType::Move;
            chosen.unit = u.id;
            chosen.toBoard = true;
            chosen.cell = target;
            best = 0.3;
            action = "formation_correction";
            break;
        }
    if (chosen.type == CommandType::Ready && botCommands_[seat] < bot.maxCommands - 1)
    {
        // A stronger benched unit can replace a board unit without changing capacity.
        if (remainingMs_ > catalog_.rules.botRepositionCutoffMs)
            for (const auto &bench : s.roster)
                if (!bench.onBoard)
                    for (const auto &board : s.roster)
                        if (board.onBoard)
                        {
                            auto utility = [&](SeatState formation) {
                                formation.roster.erase(
                                    std::remove_if(formation.roster.begin(), formation.roster.end(),
                                                   [](const OwnedUnit &unit) { return !unit.onBoard; }),
                                    formation.roster.end());
                                auto value = Evaluate(formation, catalog_, bot);
                                return value.budget + value.roles + value.traits * bot.synergy;
                            };
                            // The newcomer takes the old unit's cell. Where that is the wrong half for
                            // its class, a second move must follow, so there has to be a command and
                            // time left for it.
                            if (const auto *role = RoleOf(catalog_, catalog_.units[bench.definition]))
                            {
                                const bool wrongHalf = role->role == BotRole::Frontline ? board.cell.row < 2
                                    : role->role == BotRole::Damage && catalog_.units[bench.definition].range > 1 && role->row < 2 && board.cell.row > 1;
                                if (wrongHalf && (botCommands_[seat] >= bot.maxCommands - 2 ||
                                                  remainingMs_ <= catalog_.rules.botRepositionCutoffMs + 2 * bot.decisionIntervalMs))
                                    continue;
                            }
                            SeatState pending = s;
                            Command replacement;
                            replacement.type = CommandType::Move;
                            replacement.unit = bench.id;
                            replacement.toBoard = true;
                            replacement.cell = board.cell;
                            Id next = nextUnit_;
                            std::string reject;
                            if (ApplyCommand(pending, replacement, next, reject) &&
                                utility(pending) > utility(s) + 0.1)
                            {
                                chosen.type = CommandType::Move;
                                chosen.unit = bench.id;
                                chosen.toBoard = true;
                                chosen.cell = board.cell;
                                best = 0.2;
                                action = "replace_deployment";
                                break;
                            }
                            if (chosen.type != CommandType::Ready)
                                break;
                        }
        if (chosen.type == CommandType::Ready)
        {
            auto before = Evaluate(s, catalog_, bot);
            const bool plans = Plans(catalog_);
            int interestReserve = catalog_.rules.interestCap * catalog_.rules.interestDivisor;
            // Gold saved for interest is no use to a seat about to fall: a planning bot keeps
            // half of it two losses from the end and none of it one loss from the end.
            if (plans && s.health <= 20) interestReserve = 0;
            else if (plans && s.health <= 40) interestReserve /= 2;
            const double benchPressure = BenchPressure(s, catalog_);
            std::vector<Command> candidates;
            for (int i = 0; i < int(s.shop.size()); ++i)
                if (s.shop[i] >= 0)
                {
                    Command cmd;
                    cmd.type = CommandType::Buy;
                    cmd.slot = i;
                    candidates.push_back(cmd);
                }
            Command xp;
            xp.type = CommandType::BuyXp;
            candidates.push_back(xp);
            // A planning bot with a crowded bench may let any benched unit go; the scoring below
            // picks the one it loses least by.
            if (plans)
            {
                if (benchPressure > 0)
                    for (const auto &unit : s.roster)
                        if (!unit.onBoard)
                        {
                            Command sell;
                            sell.type = CommandType::Sell;
                            sell.unit = unit.id;
                            candidates.push_back(sell);
                        }
            }
            else if (int(s.roster.size()) > s.level + 4)
                for (const auto &unit : s.roster)
                    if (!unit.onBoard && unit.star == 1 &&
                        std::count_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &other) {
                            return other.definition == unit.definition;
                        }) == 1)
                    {
                        SeatState without = s;
                        without.roster.erase(
                            std::remove_if(without.roster.begin(), without.roster.end(),
                                           [&](const OwnedUnit &other) { return other.id == unit.id; }),
                            without.roster.end());
                        if (Evaluate(without, catalog_, bot).budget >= before.budget)
                        {
                            Command sell;
                            sell.type = CommandType::Sell;
                            sell.unit = unit.id;
                            candidates.push_back(sell);
                        }
                    }
            for (const auto &candidate : candidates)
            {
                SeatState pending = s;
                Id next = nextUnit_;
                std::string reject;
                if (!ApplyCommand(pending, candidate, next, reject))
                    continue;
                auto after = Evaluate(pending, catalog_, bot);
                // Gold above the interest cap earns nothing, so spending it is not a saving loss.
                const int spent = s.gold - pending.gold;
                const int fromSurplus = catalog_.botSpendsSurplus ? std::clamp(s.gold - interestReserve, 0, std::max(0, spent)) : 0;
                std::array<double, 8> f{
                    std::clamp((after.budget - before.budget) / std::max(1.0, double(s.level)), -1.0, 1.0),
                    std::clamp(after.upgrades - before.upgrades, -1.0, 1.0),
                    std::clamp(after.traits - before.traits, -1.0, 1.0),
                    after.roles - before.roles,
                    std::clamp(after.pairs - before.pairs, -1.0, 1.0),
                    double(spent - fromSurplus) / std::max(10, s.gold),
                    double(
                        std::min(catalog_.rules.interestCap, s.gold / catalog_.rules.interestDivisor) -
                        std::min(catalog_.rules.interestCap, pending.gold / catalog_.rules.interestDivisor)) /
                        3.0,
                    after.bench - before.bench};
                double urgency = s.health <= 15 ? 1.5 : 1.0;
                double score = urgency * (3 * f[0] + 2 * f[1] * bot.upgrade + 1.5 * f[2] * bot.synergy +
                                          f[3] + 0.6 * f[4] * bot.upgrade) -
                               0.35 * f[5] * bot.save - 0.25 * f[6] * bot.save - 0.25 * f[7];
                if (plans)
                {
                    score -= BenchPressure(pending, catalog_) - benchPressure;
                    // Of the units it could let go, the least valuable goes first.
                    if (candidate.type == CommandType::Sell)
                    {
                        SeatState alone;
                        alone.level = 1;
                        alone.roster = {*std::find_if(s.roster.begin(), s.roster.end(),
                                                      [&](const OwnedUnit &unit) { return unit.id == candidate.unit; })};
                        score -= 0.05 * Evaluate(alone, catalog_, bot).budget;
                    }
                }
                if (candidate.type == CommandType::BuyXp)
                {
                    score += double(pending.level - s.level) * 0.24 * bot.level;
                    if (s.xp + catalog_.rules.buyXpAmount >= catalog_.rules.xpToNext.at(s.level))
                        score += 0.04;
                    // A planning bot counts each purchase as its share of what the next level brings:
                    // one more fielded unit, and whatever that does for traits and cover.
                    else if (plans)
                    {
                        SeatState raised = s;
                        ++raised.level;
                        const auto levelled = Evaluate(raised, catalog_, bot);
                        const double gain = 3 * (levelled.budget - before.budget) / std::max(1.0, double(s.level)) +
                                            1.5 * (levelled.traits - before.traits) * bot.synergy + (levelled.roles - before.roles);
                        score += double(catalog_.rules.buyXpAmount) / catalog_.rules.xpToNext.at(s.level) *
                                 (0.24 * bot.level + 0.6 * std::max(0.0, gain));
                    }
                    // Credit progress toward the next level, or experience is only ever bought
                    // when a single purchase finishes the level.
                    else if (catalog_.botSpendsSurplus)
                        score += double(catalog_.rules.buyXpAmount) / catalog_.rules.xpToNext.at(s.level) * 0.24 * bot.level;
                }
                score += (double(s.botRng.Below(20001)) - 10000.0) / 10000.0 * bot.noiseBp / 10000.0;
                if (score > best + 0.01)
                {
                    best = score;
                    chosen = candidate;
                    features = f;
                    action = candidate.type == CommandType::Buy    ? "buy"
                             : candidate.type == CommandType::Sell ? "sell_replaceable_bench"
                                                                   : "buy_xp";
                }
            }
            if (chosen.type == CommandType::Ready && remainingMs_ > catalog_.rules.botRepositionCutoffMs)
            {
                int opponentId = -1;
                for (const auto &pair : pairs_)
                {
                    if (pair.a == seat)
                        opponentId = pair.b;
                    else if (pair.b == seat && !pair.ghost)
                        opponentId = pair.a;
                }
                const PublicSeat *opponent = nullptr;
                for (const auto &observed : botObservations_[seat])
                    if (observed.id == opponentId)
                        opponent = &observed;
                PublicSeat neutralPreview;
                if (const auto *wave = CurrentWave())
                {
                    for (const auto &slot : wave->slots)
                    {
                        OwnedUnit unit;
                        unit.definition = slot.definition; unit.cell = slot.cell;
                        unit.onBoard = true; unit.neutral = true;
                        neutralPreview.deployment.push_back(unit);
                    }
                    opponent = &neutralPreview;
                }
                const double current = TacticalScore(s, opponent, catalog_);
                int considered = 0;
                for (const auto &unit : s.roster)
                    if (unit.onBoard)
                        for (Cell direction : {Cell{-1, 0}, Cell{1, 0}, Cell{0, -1}, Cell{0, 1}})
                        {
                            if (++considered > 24)
                                break;
                            Command move;
                            move.type = CommandType::Move;
                            move.unit = unit.id;
                            move.toBoard = true;
                            move.cell = {unit.cell.column + direction.column, unit.cell.row + direction.row};
                            SeatState pending = s;
                            Id next = nextUnit_;
                            std::string reject;
                            if (!ApplyCommand(pending, move, next, reject))
                                continue;
                            const double improvement = TacticalScore(pending, opponent, catalog_) - current;
                            if (improvement > std::max(0.04, best))
                            {
                                chosen = move;
                                best = improvement;
                                features[3] = improvement;
                                action = "sampled_opponent_reposition";
                            }
                        }
            }
            const bool surplusReroll = catalog_.botSpendsSurplus &&
                s.gold >= interestReserve + catalog_.rules.rerollCost;
            if (plans)
            {
                // A planning bot rerolls only with gold it does not need for interest, and weighs a
                // reroll against experience: each pair it holds is one copy from an upgrade.
                if (surplusReroll && int(s.roster.size()) < s.level + catalog_.rules.benchCapacity &&
                    (chosen.type == CommandType::Ready || chosen.type == CommandType::BuyXp))
                {
                    std::map<int, int> copies;
                    for (const auto &unit : s.roster) copies[unit.definition] += CountCopies(unit.star);
                    const int pairsHeld = int(std::count_if(copies.begin(), copies.end(),
                                                            [](const auto &entry) { return entry.second % 3 == 2; }));
                    const double rerollScore = std::min(0.08, 0.02 + 0.015 * pairsHeld);
                    if (chosen.type == CommandType::Ready || rerollScore > best)
                    {
                        chosen = Command{};
                        chosen.type = CommandType::Reroll;
                        features = {};
                        action = "bounded_reroll";
                        best = rerollScore;
                    }
                }
            }
            else if (chosen.type == CommandType::Ready && s.gold >= catalog_.rules.rerollCost + 10 &&
                (surplusReroll || botRerolls_[seat] < bot.maxRerolls) &&
                int(s.roster.size()) < s.level + catalog_.rules.benchCapacity)
            {
                chosen.type = CommandType::Reroll;
                action = "bounded_reroll";
                best = 0.01;
            }
        }
    }
    chosen.seat = seat;
    chosen.requestId = (Id(1) << 63) | nextRequest_++;
    chosen.sequence = s.sequence + 1;
    chosen.revision = s.revision;
    BotDecision log;
    log.round = round_;
    log.seat = seat;
    log.observationRevision = botObservationRevision_[seat];
    log.action = action;
    log.features = features;
    log.score = best;
    log.reply = Submit(seat, chosen);
    log.goldAfter = seats_[seat].gold;
    botLog_.push_back(log);
    if (log.reply.accepted)
    {
        ++botCommands_[seat];
        if (chosen.type == CommandType::Reroll)
            ++botRerolls_[seat];
    }
}
void Match::Tick(int ms)
{
    if (ms <= 0 || phase_ == Phase::Finished || phase_ == Phase::Aborted)
        return;
    accumulatorMs_ += ms;
    int steps = 0;
    // Keep excess accumulated time for subsequent calls; never discard simulation ticks.
    while (accumulatorMs_ >= catalog_.rules.tickMs && steps++ < 200 && phase_ != Phase::Finished &&
           phase_ != Phase::Aborted)
    {
        accumulatorMs_ -= catalog_.rules.tickMs;
        elapsedMs_ += catalog_.rules.tickMs;
        // A guided lesson holds the preparation clock: the captain takes as long as the step needs.
        if (!(guided_ && phase_ == Phase::Preparation)) remainingMs_ -= catalog_.rules.tickMs;
        if (phase_ == Phase::Preparation)
        {
            // Snapshot all bot observations before any policy acts on this tick.
            // Decision cadence (700 ms) must not stretch the observation cadence (1500 ms).
            for (const auto &seat : seats_)
                if (!seat.human && seat.health > 0 && elapsedMs_ >= botObserveNextMs_[seat.id])
                {
                    botObservations_[seat.id] = PublicSeats();
                    botObserveNextMs_[seat.id] = elapsedMs_ + catalog_.bots[seat.botIndex].observationMs;
                    ++botObservationRevision_[seat.id];
                }
            for (auto &s : seats_)
                if (!s.human && s.health > 0 && !s.ready && elapsedMs_ >= botNextMs_[s.id])
                {
                    BotTurn(s.id);
                    botNextMs_[s.id] = elapsedMs_ + catalog_.bots[s.botIndex].decisionIntervalMs;
                }
            bool ready = std::all_of(seats_.begin(), seats_.end(),
                                     [](const SeatState &s) { return s.health <= 0 || s.ready; });
            if (remainingMs_ <= 0 || ready)
                Lock();
        }
        else if (phase_ == Phase::Combat)
        {
            for (auto &e : encounters_)
                e.combat.Tick();
            if (std::all_of(encounters_.begin(), encounters_.end(),
                            [](const Encounter &e) { return e.combat.Result().complete; }))
                Settle();
        }
        else if (phase_ == Phase::Settlement && remainingMs_ <= 0 && !guided_)
            Prepare();
    }
}
void Match::TakeOver(int seat)
{
    if (seat < 0 || seat >= int(seats_.size()) || !seats_[seat].human)
        return;
    auto &s = seats_[seat];
    s.human = false;
    s.takeover = true;
    s.label = catalog_.bots[s.botIndex].label + " (takeover)";
    s.ready = false;
}
void Match::Abort()
{
    phase_ = Phase::Aborted;
    remainingMs_ = 0;
    for (auto &s : seats_)
        s.placement = 0;
}
std::string Match::InvariantError() const
{
    if (phase_ == Phase::Aborted)
        return catalog_.Validate();
    if (seats_.size() != 8)
        return "Missing persistent seats";
    if (catalog_.profileId == "wonder_vnext" &&
        (originalHumans_ < 0 || originalHumans_ > int(seats_.size()) || (!networked_ && originalHumans_ > 1)))
        return "Invalid original match mode";
    std::set<Id> identities;
    for (const auto &s : seats_)
    {
        if (!Legal(s))
            return "Invalid owned roster or economy for seat " + std::to_string(s.id);
        if (catalog_.profileId == "wonder_vnext" &&
            ((s.id < originalHumans_ && s.human == s.takeover) ||
             (s.id >= originalHumans_ && (s.human || s.takeover))))
            return "Seat authority does not match the original human configuration";
        for (const auto &u : s.roster)
            if (!identities.insert(u.id).second || u.id >= nextUnit_)
                return "Duplicated or invalid instance ID";
        if (s.health == 0 && s.placement == 0)
            return "Eliminated seat lacks placement";
    }
    if (phase_ == Phase::Preparation || phase_ == Phase::Combat)
    {
        std::array<int, 8> exposure{};
        for (const auto &p : pairs_)
        {
            if (p.a < 0 || p.a >= int(seats_.size()) || seats_[p.a].health <= 0)
                return "Invalid encounter owner";
            ++exposure[p.a];
            if (p.kind == EncounterKind::Neutral)
            {
                if (p.b != -1 || p.ghost || !NeutralRound() || !CurrentWave() || p.waveId != CurrentWave()->id)
                    return "Invalid neutral ownership";
            }
            else
            {
                if (p.b < 0 || p.b >= int(seats_.size()) || p.a == p.b || seats_[p.b].health <= 0)
                    return "Invalid pairing";
                if (!p.ghost) ++exposure[p.b];
            }
        }
        for (const auto &s : seats_)
            if (s.health > 0 && exposure[s.id] != 1)
                return "Real seat receives other than one result";
    }
    for (const auto &e : encounters_)
    {
        auto issue = e.combat.InvariantError();
        if (!issue.empty())
            return issue;
    }
    if (phase_ == Phase::Finished)
        for (const auto &s : seats_)
            if (!s.placement)
                return "Final placement missing";
    return {};
}
} // namespace wc
