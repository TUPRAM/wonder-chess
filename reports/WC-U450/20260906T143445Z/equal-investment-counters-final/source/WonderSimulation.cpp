#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <cmath>
#include <deque>
#include <functional>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <tuple>

namespace wc
{
namespace
{
int Ticks(int ms, const Rules &r)
{
    return (ms + r.tickMs - 1) / r.tickMs;
}
bool Alive(const CombatUnit &u)
{
    return u.health > 0;
}
bool SameCommand(const Command &a, const Command &b)
{
    return std::tie(a.type, a.seat, a.requestId, a.sequence, a.revision, a.unit, a.slot, a.toBoard,
                    a.cell.column, a.cell.row) == std::tie(b.type, b.seat, b.requestId, b.sequence,
                                                           b.revision, b.unit, b.slot, b.toBoard,
                                                           b.cell.column, b.cell.row);
}
std::pair<int, int> PairKey(int a, int b)
{
    return {std::min(a, b), std::max(a, b)};
}
Id Mix(Id n)
{
    n += 0x9e3779b97f4a7c15ULL;
    n = (n ^ (n >> 30)) * 0xbf58476d1ce4e5b9ULL;
    n = (n ^ (n >> 27)) * 0x94d049bb133111ebULL;
    return n ^ (n >> 31);
}
int Copies(int star)
{
    return star == 3 ? 9 : star == 2 ? 3 : 1;
}
// Small arbitrary-precision integers keep timeout comparisons exact without
// assuming that the product of up to twelve maximum-health values fits uint64.
struct Big
{
    std::vector<std::uint32_t> digits{0};
    explicit Big(std::uint32_t v = 0) : digits{v}
    {
    }
    void Multiply(Int v)
    {
        std::uint64_t carry = 0;
        for (auto &d : digits)
        {
            auto n = std::uint64_t(d) * std::uint64_t(v) + carry;
            d = std::uint32_t(n % 1000000000ULL);
            carry = n / 1000000000ULL;
        }
        while (carry)
        {
            digits.push_back(std::uint32_t(carry % 1000000000ULL));
            carry /= 1000000000ULL;
        }
    }
    void Add(const Big &b)
    {
        digits.resize(std::max(digits.size(), b.digits.size()), 0);
        std::uint64_t carry = 0;
        for (std::size_t i = 0; i < digits.size(); ++i)
        {
            auto n = std::uint64_t(digits[i]) + (i < b.digits.size() ? b.digits[i] : 0) + carry;
            digits[i] = std::uint32_t(n % 1000000000ULL);
            carry = n / 1000000000ULL;
        }
        if (carry)
            digits.push_back(std::uint32_t(carry));
    }
    int Compare(const Big &b) const
    {
        if (digits.size() != b.digits.size())
            return digits.size() < b.digits.size() ? -1 : 1;
        for (std::size_t i = digits.size(); i-- > 0;)
            if (digits[i] != b.digits[i])
                return digits[i] < b.digits[i] ? -1 : 1;
        return 0;
    }
};
} // namespace
Int HalfUp(Int n, Int d)
{
    return n / d + ((n % d) * 2 >= d ? 1 : 0);
}
Int ResolveDamage(Int raw, DamageType type, int armor, int resistance, int bonusBp)
{
    const int defense = type == DamageType::Physical ? armor : type == DamageType::Magic ? resistance : 0;
    return HalfUp(raw * (10000 + bonusBp) * 100, Int(10000) * (100 + defense));
}
Int StarValue(Int base, int star, int bonusBp, const Rules &r)
{
    return HalfUp(base * r.starMultiplierBp[star - 1] * (10000 + bonusBp), 100000000);
}
int AttackInterval(int rate, int bonusBp, const Rules &r)
{
    const Int adjusted = std::clamp<Int>(HalfUp(Int(rate) * std::max(0, 10000 + bonusBp), 10000),
                                         r.minAttackRate, r.maxAttackRate);
    return int((1000000 + adjusted * r.tickMs - 1) / (adjusted * r.tickMs));
}
int MovementInterval(int baseRate, int bonusBp, const Rules &rules)
{
    const Int rate = std::max<Int>(1, HalfUp(Int(baseRate) * std::max(0, 10000 + bonusBp), 10000));
    return int((1000000 + rate * rules.tickMs - 1) / (rate * rules.tickMs));
}
int Distance(Cell a, Cell b)
{
    return std::max(std::abs(a.column - b.column), std::abs(a.row - b.row));
}
Cell EncounterCell(Cell local, int side, const Rules &r)
{
    return side ? Cell{r.columns - 1 - local.column, r.rows - 1 - local.row} : local;
}
Id Random::Next()
{
    state += 0x9e3779b97f4a7c15ULL;
    Id z = state;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
int Random::Below(int exclusive)
{
    const Id bound = Id(exclusive), threshold = (Id(0) - bound) % bound;
    Id value;
    do
    {
        value = Next();
    } while (value < threshold);
    return int(value % bound);
}
int TraitValue(const TraitDef &trait, int count)
{
    if (trait.threshold4 > trait.threshold && count >= trait.threshold4 && trait.value4 != 0)
        return trait.value4;
    return count >= trait.threshold ? trait.value : 0;
}
bool IsNeutralRound(int round, const Rules &rules)
{
    return round > 0 && (round <= rules.neutralOpeningRounds ||
           (rules.neutralEvery > 0 && round % rules.neutralEvery == 0));
}
const UnitDef &Catalog::Definition(int index, bool neutral) const
{
    return neutral ? neutrals.at(index) : units.at(index);
}
const NeutralWave *Catalog::Wave(int round) const
{
    for (const auto &wave : waves) if (wave.round == round) return &wave;
    return nullptr;
}
std::string Catalog::Validate() const
{
    const auto &r = rules;
    if (r.columns != 8 || r.rows != 8 || r.deploymentRows != 4 || r.tickMs != 50 || r.seatCount != 8)
        return "Unsupported board, tick or seat contract";
    if (units.size() != 24 || bots.size() != 7 || r.benchCapacity != 8 || r.shopSlots != 5)
        return "Update requires twenty-four units, seven personas, eight bench and five shop slots";
    if (r.startingHealth <= 0 || r.maximumLevel > 6 || r.startingLevel < 1 ||
        r.startingLevel > r.maximumLevel || r.interestDivisor <= 0 || r.combatTimeoutMs <= 0 ||
        r.maxRounds <= 0 || r.minAttackRate <= 0 || r.maxAttackRate < r.minAttackRate)
        return "Invalid numeric rules";
    if (r.maxHealth <= 0 || r.maxHealth > 100000000 || r.maxRawDamage <= 0 || r.maxRawDamage > 10000000 ||
        r.maxArmor < 0 || r.maxArmor > 10000)
        return "Unsafe integer bounds";
    std::set<std::string> ids, abilities;
    std::vector<UnitDef> allDefinitions = units;
    allDefinitions.insert(allDefinitions.end(), neutrals.begin(), neutrals.end());
    for (const auto &u : allDefinitions)
    {
        if (!ids.insert(u.id).second || (u.ability.enabled && !abilities.insert(u.ability.id).second) || u.id.empty() ||
            (u.ability.enabled && u.ability.id.empty()))
            return "Duplicate or empty unit/ability ID";
        if (u.cost < 0 || u.cost > 3 || u.health <= 0 || u.health > r.maxHealth || u.attackDamage < 0 ||
            u.attackDamage > r.maxRawDamage || u.armor < 0 || u.armor > r.maxArmor || u.resistance < 0 ||
            u.resistance > r.maxArmor || u.attackRate <= 0 || u.movementRate <= 0 || u.range < 1)
            return "Invalid unit numeric field: " + u.id;
        const auto &a = u.ability;
        if ((a.enabled && (a.castMs <= 0 || a.cooldownMs <= 0 || a.maxTargets <= 0 || a.maxTargets > 12 ||
            a.firstCastMs < 0 || a.recoveryMs < 0 || a.travelMs < 0 || a.durationMs < 0)) ||
            u.attackWindupMs <= 0)
            return "Invalid ability timing: " + u.id;
        if (Ticks(u.attackWindupMs, r) >= AttackInterval(r.maxAttackRate, 0, r))
            return "Attack windup leaves no recovery at maximum rate: " + u.id;
        auto effects = a.effects;
        if (effects.empty() && a.enabled) effects.push_back({a.effect, a.damageType, a.durationMs, a.magnitude});
        if (effects.size() > 2 || (effects.size() == 2 &&
            (effects[0].effect != Effect::Damage || effects[1].effect != Effect::Stun)))
            return "Unsupported effect list: " + u.id;
        for (const auto &effect : effects)
        {
            if (effect.durationMs < 0) return "Invalid effect duration: " + u.id;
            for (auto magnitude : effect.magnitude)
            {
                if (magnitude > r.maxRawDamage || magnitude < -10000)
                    return "Unsafe effect magnitude: " + u.id;
                if (effect.effect != Effect::StatModifier && magnitude < 0)
                    return "Negative non-stat effect magnitude: " + u.id;
                if ((effect.effect == Effect::Dash || effect.effect == Effect::Stun) && magnitude != 0)
                    return "Dash and stun cannot carry hidden magnitude: " + u.id;
            }
        }
        for (int star = 1; star <= 3; ++star)
            if (StarValue(u.health, star, 10000, r) > r.maxHealth)
                return "Derived health exceeds supported bounds";
    }
    const std::set<std::string> supportedStats{"max_health_bonus_bp", "attack_rate_bonus_bp",
        "physical_armor_flat", "magic_resistance_flat", "all_damage_bonus_bp", "basic_damage_bonus_bp",
        "ability_damage_bonus_bp", "support_power_bonus_bp", "movement_bonus_bp"};
    std::set<std::string> traitIds;
    for (const auto &trait : traits)
        if (!traitIds.insert(trait.id).second || !supportedStats.count(trait.stat) ||
            trait.threshold != 2 || trait.threshold4 != 4 || trait.value < 0 || trait.value4 < 0)
            return "Invalid trait definition";
    std::set<int> waveRounds;
    std::set<std::string> waveIds;
    for (const auto &wave : waves)
    {
        if (!waveRounds.insert(wave.round).second || !waveIds.insert(wave.id).second ||
            wave.id.empty() || !IsNeutralRound(wave.round, r) || wave.slots.empty() || wave.slots.size() > 6 ||
            wave.hpScaleBp <= 0 || wave.hpScaleBp > 100000 || wave.damageScaleBp <= 0 || wave.damageScaleBp > 100000)
            return "Invalid neutral wave";
        std::set<std::pair<int,int>> cells;
        for (const auto &slot : wave.slots)
        {
            if (slot.definition < 0 || slot.definition >= int(neutrals.size()) || slot.cell.column < 0 ||
                slot.cell.column >= r.columns || slot.cell.row < 0 || slot.cell.row >= r.deploymentRows ||
                !cells.insert({slot.cell.column, slot.cell.row}).second) return "Invalid neutral slot";
            const auto &d = neutrals[slot.definition];
            if (HalfUp(d.health * wave.hpScaleBp, 10000) > r.maxHealth ||
                HalfUp(d.attackDamage * wave.damageScaleBp, 10000) > r.maxRawDamage)
                return "Unsafe scaled neutral stats";
            for (const auto &effect : d.ability.effects)
                if (effect.effect == Effect::Damage || effect.effect == Effect::Shield)
                    for (Int magnitude : effect.magnitude)
                        if (HalfUp(magnitude * (effect.effect == Effect::Shield ? wave.hpScaleBp : wave.damageScaleBp), 10000) > r.maxRawDamage)
                            return "Unsafe scaled neutral skill";
        }
    }
    for (int round = 1; round <= r.maxRounds; ++round)
        if (IsNeutralRound(round, r) && !Wave(round)) return "Missing neutral wave";
    for (int level = r.startingLevel; level <= r.maximumLevel; ++level)
    {
        auto it = r.shopWeights.find(level);
        if (it == r.shopWeights.end())
            return "Missing shop weights";
        int sum = 0;
        for (int tier = 0; tier < 3; ++tier)
        {
            int w = it->second[tier];
            if (w < 0)
                return "Negative shop weight";
            sum += w;
            if (w > 0 && std::none_of(units.begin(), units.end(),
                                      [&](const UnitDef &u) { return u.cost == tier + 1; }))
                return "Enabled shop tier is empty";
        }
        if (sum != 10000)
            return "Shop weights must sum to 10000";
        if (level < r.maximumLevel && (r.xpToNext.count(level) == 0 || r.xpToNext.at(level) <= 0))
            return "Missing XP threshold";
    }
    for (const auto &b : bots)
        if (b.decisionIntervalMs <= 0 || b.observationMs <= 0 || b.maxCommands <= 0 || b.maxRerolls < 0)
            return "Invalid bot budget";
    return {};
}

Combat::Combat(const Catalog &c, const std::vector<OwnedUnit> &a, const std::vector<OwnedUnit> &b, Id seed,
               Id encounterId)
    : catalog_(&c)
{
    for (int side = 0; side < 2; ++side)
    {
        const auto &formation = side ? b : a;
        std::map<std::string, std::set<int>> counts;
        for (const auto &o : formation)
            if (o.onBoard && !o.neutral)
            {
                const auto &d = c.units[o.definition];
                counts[d.race].insert(o.definition);
                counts[d.unitClass].insert(o.definition);
            }
        for (const auto &o : formation)
            if (o.onBoard)
            {
                const auto &d = c.Definition(o.definition, o.neutral);
                CombatUnit u;
                u.neutral = o.neutral;
                u.hpScaleBp = o.hpScaleBp;
                u.damageScaleBp = o.damageScaleBp;
                // 32 encounter bits + 1 side bit + 20 instance bits fit exactly in JSON's 53-bit integer range.
                if (encounterId >= (Id(1) << 32) || o.id >= (Id(1) << 20))
                    throw std::overflow_error("Combat identity exceeds exact snapshot integer range");
                u.id = (encounterId << 21) | (Id(side) << 20) | o.id;
                u.definition = o.definition;
                u.side = side;
                u.star = o.star;
                u.cell = EncounterCell(o.cell, side, c.rules);
                u.armor = d.armor;
                u.resistance = d.resistance;
                int healthBonus = 0;
                for (const auto &t : c.traits)
                    if (!o.neutral && (t.id == d.race || t.id == d.unitClass) && TraitValue(t, int(counts[t.id].size())) != 0)
                    {
                        const int value = TraitValue(t, int(counts[t.id].size()));
                        if (t.stat == "max_health_bonus_bp")
                            healthBonus += value;
                        else if (t.stat == "attack_rate_bonus_bp")
                            u.rateBonus += value;
                        else if (t.stat == "physical_armor_flat")
                            u.armor += value;
                        else if (t.stat == "magic_resistance_flat")
                            u.resistance += value;
                        else if (t.stat == "all_damage_bonus_bp")
                            u.allBonus += value;
                        else if (t.stat == "basic_damage_bonus_bp")
                            u.basicBonus += value;
                        else if (t.stat == "ability_damage_bonus_bp")
                            u.abilityBonus += value;
                        else if (t.stat == "support_power_bonus_bp")
                            u.supportBonus += value;
                        else if (t.stat == "movement_bonus_bp")
                            u.movementBonus += value;
                    }
                u.health = u.maxHealth = StarValue(HalfUp(d.health * o.hpScaleBp, 10000), o.star, healthBonus, c.rules);
                u.basicDamage = StarValue(HalfUp(d.attackDamage * o.damageScaleBp, 10000), o.star, 0, c.rules);
                u.cooldownTick = Ticks(d.ability.firstCastMs, c.rules);
                units_.push_back(u);
            }
    }
    Random rng{seed};
    std::vector<int> order(units_.size());
    std::iota(order.begin(), order.end(), 0);
    for (int i = int(order.size()) - 1; i > 0; --i)
        std::swap(order[i], order[rng.Below(i + 1)]);
    for (int i = 0; i < int(order.size()); ++i)
        units_[order[i]].initiative = i;
    Assess(false);
}
bool Combat::Free(Cell cell, int except) const
{
    if (cell.column < 0 || cell.column >= catalog_->rules.columns || cell.row < 0 ||
        cell.row >= catalog_->rules.rows)
        return false;
    for (int i = 0; i < int(units_.size()); ++i)
        if (i != except && Alive(units_[i]))
        {
            const auto &u = units_[i];
            if (u.cell == cell || u.destination == cell)
                return false;
        }
    return true;
}
void Combat::CancelReservation(int i)
{
    units_[i].destination = {};
    units_[i].movementTick = 0;
}
bool Combat::FindPath(int source, int target, Cell &next, int &length) const
{
    const auto &u = units_[source];
    const auto &enemy = units_[target];
    const auto &r = catalog_->rules;
    std::array<int, 64> dist, previous;
    dist.fill(-1);
    previous.fill(-1);
    auto index = [&](Cell p) { return p.row * r.columns + p.column; };
    auto cell = [&](int i) { return Cell{i % r.columns, i / r.columns}; };
    std::deque<Cell> queue;
    queue.push_back(u.cell);
    dist[index(u.cell)] = 0;
    while (!queue.empty())
    {
        Cell at = queue.front();
        queue.pop_front();
        const int p = index(at);
        if (Distance(at, enemy.cell) <= catalog_->Definition(u.definition, u.neutral).range)
        {
            length = dist[p];
            next = u.cell;
            if (length)
            {
                int child = p;
                while (previous[child] != index(u.cell))
                    child = previous[child];
                next = cell(child);
            }
            return true;
        }
        for (int y = -1; y <= 1; ++y)
            for (int x = -1; x <= 1; ++x)
                if (x || y)
                {
                    Cell dest{at.column + x, at.row + y};
                    if (!Free(dest, source))
                        continue;
                    if (x && y &&
                        (!Free({at.column + x, at.row}, source) || !Free({at.column, at.row + y}, source)))
                        continue;
                    int n = index(dest);
                    if (dist[n] >= 0)
                        continue;
                    dist[n] = dist[p] + 1;
                    previous[n] = p;
                    queue.push_back(dest);
                }
    }
    return false;
}
int Combat::ChooseEnemy(int source, Cell &next, int &length) const
{
    const auto &u = units_[source];
    if (u.target >= 0 && Alive(units_[u.target]) && units_[u.target].side != u.side &&
        FindPath(source, u.target, next, length))
        return u.target;
    int best = -1;
    std::tuple<int, int, Id> bestKey{999, 999, 0};
    for (int i = 0; i < int(units_.size()); ++i)
        if (Alive(units_[i]) && units_[i].side != u.side)
        {
            Cell candidate;
            int distance = 0;
            if (!FindPath(source, i, candidate, distance))
                continue;
            auto key = std::make_tuple(distance, units_[i].initiative, units_[i].id);
            if (key < bestKey)
            {
                bestKey = key;
                best = i;
                next = candidate;
                length = distance;
            }
        }
    return best;
}
std::vector<int> Combat::Select(int source, const AbilityDef &a) const
{
    const auto &s = units_[source];
    const AbilityEffect primary = a.effects.empty() ? AbilityEffect{a.effect,a.damageType,a.durationMs,a.magnitude} : a.effects.front();
    std::vector<int> selected;
    for (int i = 0; i < int(units_.size()); ++i)
    {
        const auto &t = units_[i];
        if (!Alive(t))
            continue;
        bool valid = false;
        switch (a.selector)
        {
        case Selector::Self:
            valid = i == source;
            break;
        case Selector::CurrentEnemy:
        case Selector::CurrentEnemyArea:
            valid = i == s.target && t.side != s.side && Distance(s.cell, t.cell) <= a.range;
            break;
        case Selector::AdjacentEnemies:
            valid = t.side != s.side && Distance(s.cell, t.cell) <= a.radius;
            break;
        case Selector::AdjacentAllies:
            valid = t.side == s.side && (i != source || a.allowSelf) && Distance(s.cell, t.cell) <= a.radius;
            break;
        case Selector::HighestAttackRateEnemy:
            valid = t.side != s.side && Distance(s.cell, t.cell) <= a.range;
            break;
        case Selector::LowestHealthAlly:
            valid = t.side == s.side && (i != source || a.allowSelf) && Distance(s.cell, t.cell) <= a.range;
            break;
        default:
            break;
        }
        if (primary.effect == Effect::Heal && t.health >= t.maxHealth)
            valid = false;
        if (primary.effect == Effect::Shield)
        {
            auto magnitude = HalfUp(primary.magnitude[s.star - 1] * (10000 + s.supportBonus), 10000);
            if (magnitude < t.shield ||
                (magnitude == t.shield && tick_ + Ticks(primary.durationMs, catalog_->rules) <= t.shieldExpiry))
                valid = false;
        }
        if (valid)
            selected.push_back(i);
    }
    std::sort(selected.begin(), selected.end(), [&](int x, int y) {
        const auto &l = units_[x];
        const auto &r = units_[y];
        if (a.selector == Selector::HighestAttackRateEnemy)
        {
            auto rate = [&](const CombatUnit &u) {
                int bonus = u.rateBonus;
                for (const auto &m : u.modifiers) bonus += int(m.magnitude);
                return std::clamp<Int>(HalfUp(Int(catalog_->Definition(u.definition, u.neutral).attackRate) *
                    std::max(0, 10000 + bonus), 10000), catalog_->rules.minAttackRate, catalog_->rules.maxAttackRate);
            };
            return std::make_tuple(-rate(l), Distance(s.cell,l.cell), l.id) <
                   std::make_tuple(-rate(r), Distance(s.cell,r.cell), r.id);
        }
        if (a.selector == Selector::LowestHealthAlly)
        {
            auto crossA = l.health * r.maxHealth, crossB = r.health * l.maxHealth;
            if (crossA != crossB)
                return crossA < crossB;
            if (l.maxHealth - l.health != r.maxHealth - r.health)
                return l.maxHealth - l.health > r.maxHealth - r.health;
        }
        return std::tie(l.initiative, l.id) < std::tie(r.initiative, r.id);
    });
    const int max = (a.selector == Selector::LowestHealthAlly || a.selector == Selector::HighestAttackRateEnemy) ? 1 : a.maxTargets;
    if (int(selected.size()) > max)
        selected.resize(max);
    return selected;
}
bool Combat::DashLanding(int source, const AbilityDef &a, int &target, Cell &cell) const
{
    const auto &s = units_[source];
    target = s.target;
    if (a.selector == Selector::FarthestEnemyAdjacent)
    {
        target = -1;
        for (int i = 0; i < int(units_.size()); ++i)
            if (Alive(units_[i]) && units_[i].side != s.side)
                if (target < 0 ||
                    std::make_tuple(-Distance(s.cell, units_[i].cell), units_[i].initiative) <
                        std::make_tuple(-Distance(s.cell, units_[target].cell), units_[target].initiative))
                    target = i;
    }
    if (target < 0 || !Alive(units_[target]) || Distance(s.cell, units_[target].cell) > a.range)
        return false;
    bool found = false;
    std::tuple<int, int, int> best{999, 999, 999};
    const int original = Distance(s.cell, units_[target].cell);
    for (int row = 0; row < catalog_->rules.rows; ++row)
        for (int col = 0; col < catalog_->rules.columns; ++col)
        {
            Cell candidate{col, row};
            const int dash = Distance(s.cell, candidate),
                      separation = Distance(candidate, units_[target].cell);
            if (!dash || dash > a.maxDash || !Free(candidate))
                continue;
            if (a.selector == Selector::RetreatFromCurrentEnemy)
            {
                if (separation <= original || separation > catalog_->Definition(s.definition, s.neutral).range)
                    continue;
            }
            else if (separation != 1 ||
                     (a.selector == Selector::CurrentEnemyAdjacent && separation >= original))
                continue;
            auto key = std::make_tuple(a.selector == Selector::RetreatFromCurrentEnemy ? -separation : dash,
                                       a.selector == Selector::RetreatFromCurrentEnemy ? dash : 0,
                                       row * catalog_->rules.columns + col);
            if (key < best)
            {
                best = key;
                cell = candidate;
                found = true;
            }
        }
    return found;
}
bool Combat::CommitAbility(int source)
{
    auto &s = units_[source];
    const auto &a = catalog_->Definition(s.definition, s.neutral).ability;
    if (!a.enabled || tick_ < s.cooldownTick)
        return false;
    if ((a.effects.empty() ? a.effect : a.effects.front().effect) == Effect::Dash)
    {
        int target;
        Cell landing;
        if (!DashLanding(source, a, target, landing))
            return false;
        s.target = target;
        s.destination = landing;
    }
    else if (Select(source, a).empty())
        return false;
    s.actionId = nextAction_++;
    s.state = ActionState::CastWindup;
    s.releaseTick = tick_ + Ticks(a.castMs, catalog_->rules);
    s.recoveryTick = s.releaseTick + Ticks(a.recoveryMs, catalog_->rules);
    s.cooldownTick = tick_ + Ticks(a.cooldownMs, catalog_->rules);
    return true;
}
std::vector<VisualAction> Combat::VisualActions() const
{
    std::vector<VisualAction> result;
    auto describe = [&](const CombatUnit& source, bool basic) {
        VisualAction v;
        const auto& definition = catalog_->Definition(source.definition, source.neutral);
        v.source = source.id; v.action = source.actionId;
        v.definition = source.definition; v.neutral = source.neutral; v.basicAttack = basic;
        v.origin = v.center = source.cell; v.releaseTick = source.releaseTick;
        v.impactTick = v.releaseTick + Ticks(basic ? definition.projectileTravelMs : definition.ability.travelMs, catalog_->rules);
        v.radius = basic ? 0 : definition.ability.radius;
        v.effect = basic ? Effect::Damage : (definition.ability.effects.empty() ? definition.ability.effect : definition.ability.effects.front().effect);
        v.damageType = basic ? definition.damageType : (definition.ability.effects.empty() ? definition.ability.damageType : definition.ability.effects.front().damageType);
        return v;
    };
    auto areaRecipients = [&](VisualAction& visual, int side, int maximum) {
        std::vector<const CombatUnit*> ordered;
        for (const auto& unit : units_)
            if (Alive(unit) && unit.side != side && Distance(unit.cell, visual.center) <= visual.radius)
                ordered.push_back(&unit);
        std::sort(ordered.begin(), ordered.end(), [](const CombatUnit* a, const CombatUnit* b) { return a->initiative < b->initiative; });
        for (const auto* unit : ordered)
            if (int(visual.recipients.size()) < maximum) visual.recipients.push_back(unit->id);
    };
    for (const auto& packet : packets_)
    {
        if (packet.effectOrder != 0 || packet.due <= tick_) continue;
        const auto& source = units_[packet.source];
        auto found = std::find_if(result.begin(), result.end(), [&](const VisualAction& v) { return v.source == source.id && v.action == packet.action; });
        if (found == result.end())
        {
            auto visual = describe(source, packet.basicAttack);
            visual.action = packet.action; visual.origin = packet.origin; visual.center = packet.center;
            visual.radius = packet.radius; visual.effect = packet.effect; visual.damageType = packet.damageType;
            visual.releaseTick = packet.releasedAt; visual.impactTick = packet.due;
            visual.released = true; visual.provisional = false;
            visual.fixedArea = packet.area; visual.recipientsProvisional = packet.area;
            if (packet.area) areaRecipients(visual, source.side, packet.maxTargets);
            result.push_back(visual); found = result.end() - 1;
        }
        if (packet.target >= 0)
        {
            const auto target = units_[packet.target].id;
            if (!found->target) found->target = target;
            if (std::find(found->recipients.begin(), found->recipients.end(), target) == found->recipients.end())
                found->recipients.push_back(target);
        }
    }
    for (int i = 0; i < int(units_.size()); ++i)
    {
        const auto& source = units_[i];
        if (!Alive(source) || (source.state != ActionState::AttackWindup && source.state != ActionState::CastWindup)) continue;
        const bool basic = source.state == ActionState::AttackWindup;
        auto visual = describe(source, basic);
        const auto& ability = catalog_->Definition(source.definition, source.neutral).ability;
        if (basic || visual.effect == Effect::Dash)
        {
            if (source.target >= 0 && Alive(units_[source.target]))
                visual.target = units_[source.target].id;
            if (visual.effect == Effect::Dash) visual.center = source.destination;
            if (visual.target) visual.recipients.push_back(visual.target);
        }
        else
        {
            const auto selected = Select(i, ability);
            if (!selected.empty()) visual.target = units_[selected.front()].id;
            visual.fixedArea = ability.selector == Selector::CurrentEnemyArea;
            if (visual.fixedArea)
            {
                visual.center = selected.empty() ? Cell{} : units_[selected.front()].cell;
                if (!selected.empty()) areaRecipients(visual, source.side, ability.maxTargets);
            }
            else for (int target : selected) visual.recipients.push_back(units_[target].id);
        }
        result.push_back(visual);
    }
    return result;
}
void Combat::Release(int source)
{
    auto &s = units_[source];
    const auto &d = catalog_->Definition(s.definition, s.neutral);
    const auto &r = catalog_->rules;
    Packet p;
    p.source = source;
    p.action = s.actionId;
    p.due = tick_;
    p.releasedAt = tick_;
    p.origin = p.center = s.cell;
    p.key = d.ability.id;
    if (s.state == ActionState::AttackWindup)
    {
        s.state = ActionState::AttackRecovery;
        if (s.target < 0 || !Alive(units_[s.target]) || Distance(s.cell, units_[s.target].cell) > d.range)
            return;
        p.effect = Effect::Damage;
        p.basicAttack = true;
        p.damageType = d.damageType;
        p.magnitude = s.basicDamage;
        p.bonus = s.basicBonus + s.allBonus;
        p.target = s.target;
        p.due += Ticks(d.projectileTravelMs, r);
        packets_.push_back(p);
        return;
    }
    const auto &a = d.ability;
    s.state = ActionState::CastRecovery;
    if ((a.effects.empty() ? a.effect : a.effects.front().effect) == Effect::Dash)
    {
        if (s.target >= 0 && Alive(units_[s.target]) && Free(s.destination, source))
        {
            s.cell = s.destination;
            CombatEvent event;
            event.tick = tick_;
            event.source = event.target = s.id;
            event.action = s.actionId;
            event.effect = Effect::Dash;
            event.cell = s.cell;
            event.damageType = a.damageType;
            event.radius = a.radius;
            events_.push_back(event);
        }
        CancelReservation(source);
        return;
    }
    auto targets = Select(source, a);
    if (targets.empty()) return;
    auto effects = a.effects;
    if (effects.empty()) effects.push_back({a.effect, a.damageType, a.durationMs, a.magnitude});
    for (std::size_t order = 0; order < effects.size(); ++order)
    {
        const auto &effect = effects[order];
        p.effectOrder = int(order);
        p.effect = effect.effect;
        p.damageType = effect.damageType;
        p.radius = a.radius;
        p.maxTargets = a.maxTargets;
        p.center = s.cell;
        p.magnitude = effect.magnitude[s.star - 1];
        if (s.neutral && (effect.effect == Effect::Damage || effect.effect == Effect::Shield))
            p.magnitude = HalfUp(p.magnitude * (effect.effect == Effect::Shield ? s.hpScaleBp : s.damageScaleBp), 10000);
        p.duration = Ticks(effect.durationMs, r);
        p.due = tick_ + Ticks(a.travelMs, r);
        p.bonus = s.abilityBonus + s.allBonus;
        if (effect.effect == Effect::Heal || effect.effect == Effect::Shield ||
            (effect.effect == Effect::StatModifier && p.magnitude > 0))
            p.magnitude = HalfUp(p.magnitude * (10000 + s.supportBonus), 10000);
        if (a.selector == Selector::CurrentEnemyArea)
        {
            p.area = true;
            p.center = units_[targets.front()].cell;
            packets_.push_back(p);
        }
        else for (int target : targets)
        {
            p.target = target;
            packets_.push_back(p);
        }
    }
}
void Combat::Apply(const Packet &p, int target)
{
    auto &t = units_[target];
    if (!Alive(t))
        return;
    CombatEvent e;
    e.tick = tick_;
    e.source = units_[p.source].id;
    e.target = t.id;
    e.action = p.action;
    e.effect = p.effect;
    e.damageType = p.damageType;
    e.basicAttack = p.basicAttack;
    e.radius = p.radius;
    e.requested = p.magnitude;
    e.cell = p.radius > 0 ? p.center : t.cell;
    switch (p.effect)
    {
    case Effect::Damage: {
        e.resolved = ResolveDamage(p.magnitude, p.damageType, t.armor, t.resistance, p.bonus);
        e.absorbed = std::min(t.shield, e.resolved);
        e.absorbedFrom = e.absorbed ? t.shieldSource : 0;
        t.shield -= e.absorbed;
        const Int remaining = e.resolved - e.absorbed;
        e.healthLoss = std::min(t.health, remaining);
        e.overkill = remaining - e.healthLoss;
        t.health -= e.healthLoss;
        if (!Alive(t))
        {
            t.state = ActionState::Defeated;
            CancelReservation(target);
        }
        break;
    }
    case Effect::Heal:
        e.resolved = std::min(p.magnitude, t.maxHealth - t.health);
        t.health += e.resolved;
        break;
    case Effect::Shield:
        if (p.magnitude > 0 && p.duration > 0 &&
            (p.magnitude > t.shield || (p.magnitude == t.shield && tick_ + p.duration > t.shieldExpiry)))
        {
            e.resolved = p.magnitude;
            t.shield = p.magnitude;
            t.shieldExpiry = tick_ + p.duration;
            t.shieldSource = e.source;
            t.shieldKey = p.key;
        }
        break;
    case Effect::Stun:
        if (p.duration > 0)
        {
            t.stunExpiry = std::max(t.stunExpiry, tick_ + p.duration);
            t.state = ActionState::Stunned;
            CancelReservation(target);
            e.resolved = p.duration * catalog_->rules.tickMs;
        }
        break;
    case Effect::StatModifier:
        if (p.duration > 0 && p.magnitude != 0)
        {
            auto it = std::find_if(t.modifiers.begin(), t.modifiers.end(),
                                   [&](const Modifier &m) { return m.key == p.key; });
            if (it == t.modifiers.end())
            {
                t.modifiers.push_back({p.key, p.magnitude, tick_ + p.duration});
                e.resolved = p.magnitude;
            }
            else if ((p.magnitude > 0 && p.magnitude >= it->magnitude) ||
                     (p.magnitude < 0 && p.magnitude <= it->magnitude))
            {
                if (p.magnitude == it->magnitude)
                    it->expiry = std::max(it->expiry, tick_ + p.duration);
                else
                {
                    it->magnitude = p.magnitude;
                    it->expiry = tick_ + p.duration;
                }
                e.resolved = p.magnitude;
            }
        }
        break;
    case Effect::Dash:
        break;
    }
    events_.push_back(e);
}
void Combat::Assess(bool timeout)
{
    result_.survivors = {};
    for (const auto &u : units_)
        if (Alive(u))
            ++result_.survivors[u.side];
    result_.ticks = tick_;
    if (timeout)
    {
        Big totals[2];
        for (std::size_t i = 0; i < units_.size(); ++i)
            if (Alive(units_[i]))
            {
                Big term(1);
                term.Multiply(units_[i].health);
                for (std::size_t j = 0; j < units_.size(); ++j)
                    if (i != j && Alive(units_[j]))
                        term.Multiply(units_[j].maxHealth);
                totals[units_[i].side].Add(term);
            }
        int comparison = totals[0].Compare(totals[1]);
        result_.winner = comparison > 0 ? 0 : comparison < 0 ? 1 : -1;
        result_.timeout = true;
        result_.complete = true;
        packets_.clear();
        return;
    }
    if (result_.survivors[0] && result_.survivors[1])
        return;
    if (result_.survivors[0] || result_.survivors[1])
    {
        const int livingSide = result_.survivors[0] ? 0 : 1;
        for (const auto &p : packets_)
            if (p.effect == Effect::Damage && units_[p.source].side != livingSide)
            {
                if (p.area)
                {
                    for (const auto &u : units_)
                        if (Alive(u) && u.side == livingSide && Distance(u.cell, p.center) <= p.radius)
                        {
                            draining_ = true;
                            return;
                        }
                }
                else if (p.target >= 0 && Alive(units_[p.target]))
                {
                    draining_ = true;
                    return;
                }
            }
    }
    result_.winner = result_.survivors[0] ? 0 : result_.survivors[1] ? 1 : -1;
    result_.complete = true;
}
void Combat::Tick()
{
    if (result_.complete)
        return;
    ++tick_;
    std::vector<int> order(units_.size());
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(),
              [&](int a, int b) { return units_[a].initiative < units_[b].initiative; });
    for (int i : order)
    {
        auto &u = units_[i];
        if (u.shieldExpiry <= tick_)
            u.shield = 0;
        u.modifiers.erase(std::remove_if(u.modifiers.begin(), u.modifiers.end(),
                                         [&](const Modifier &m) { return m.expiry <= tick_; }),
                          u.modifiers.end());
        if (u.state == ActionState::Stunned && u.stunExpiry <= tick_)
            u.state = u.recoveryTick > tick_ ? ActionState::AttackRecovery : ActionState::Idle;
        if (!Alive(u) || draining_)
            CancelReservation(i);
    }
    if (!draining_)
        for (int i : order)
        {
            auto &u = units_[i];
            if (Alive(u) && u.state == ActionState::Moving && u.movementTick <= tick_)
            {
                if (Free(u.destination, i))
                    u.cell = u.destination;
                CancelReservation(i);
                u.state = ActionState::Idle;
            }
        }
    if (!draining_)
        for (int i : order)
        {
            const auto &u = units_[i];
            if (Alive(u) && (u.state == ActionState::AttackWindup || u.state == ActionState::CastWindup) &&
                u.releaseTick <= tick_)
                Release(i);
        }
    std::stable_sort(packets_.begin(), packets_.end(), [&](const Packet &a, const Packet &b) {
        return std::make_tuple(a.due, units_[a.source].initiative, a.action, a.effectOrder,
                               a.target < 0 ? -1 : units_[a.target].initiative) <
               std::make_tuple(b.due, units_[b.source].initiative, b.action, b.effectOrder,
                               b.target < 0 ? -1 : units_[b.target].initiative);
    });
    std::vector<Packet> future;
    for (const auto &p : packets_)
    {
        if (p.due > tick_)
        {
            future.push_back(p);
            continue;
        }
        if (p.area)
        {
            int applied = 0;
            for (int i : order)
                if (Alive(units_[i]) && units_[i].side != units_[p.source].side &&
                    Distance(units_[i].cell, p.center) <= p.radius && applied < p.maxTargets)
                { Apply(p, i); ++applied; }
        }
        else if (p.target >= 0)
            Apply(p, p.target);
    }
    packets_ = std::move(future);
    const bool timeout = tick_ >= Ticks(catalog_->rules.combatTimeoutMs, catalog_->rules);
    Assess(timeout);
    if (result_.complete || draining_)
        return;
    for (int i : order)
    {
        auto &u = units_[i];
        if (!Alive(u) || u.state == ActionState::Stunned || u.state == ActionState::Moving ||
            u.state == ActionState::AttackWindup || u.state == ActionState::CastWindup)
            continue;
        if ((u.state == ActionState::AttackRecovery || u.state == ActionState::CastRecovery) &&
            u.recoveryTick > tick_)
            continue;
        Cell next;
        int length = 0;
        u.target = ChooseEnemy(i, next, length);
        if (CommitAbility(i))
            continue;
        const auto &d = catalog_->Definition(u.definition, u.neutral);
        if (u.target >= 0 && length == 0)
        {
            int rateBonus = u.rateBonus;
            for (const auto &m : u.modifiers)
                rateBonus += int(m.magnitude);
            u.state = ActionState::AttackWindup;
            u.actionId = nextAction_++;
            u.releaseTick = tick_ + Ticks(d.attackWindupMs, catalog_->rules);
            u.recoveryTick = tick_ + AttackInterval(d.attackRate, rateBonus, catalog_->rules);
        }
        else if (u.target >= 0)
        {
            u.state = ActionState::Moving;
            u.destination = next;
            u.movementTick = tick_ + MovementInterval(d.movementRate, u.movementBonus, catalog_->rules);
        }
        else
        {
            u.state = ActionState::AttackRecovery;
            u.recoveryTick = tick_ + 2;
        }
    }
}
std::string Combat::InvariantError() const
{
    std::set<std::pair<int, int>> cells, reservations;
    std::set<Id> ids;
    for (const auto &u : units_)
    {
        if (!ids.insert(u.id).second)
            return "Duplicate combat identity";
        if (u.health < 0 || u.health > u.maxHealth || u.shield < 0)
            return "Invalid health/shield";
        if (!Alive(u))
            continue;
        if (u.cell.column < 0 || u.cell.column >= 8 || u.cell.row < 0 || u.cell.row >= 8)
            return "Out of bounds combatant";
        if (!cells.insert({u.cell.column, u.cell.row}).second)
            return "Duplicate occupancy";
        if (u.destination.column >= 0 &&
            !reservations.insert({u.destination.column, u.destination.row}).second)
            return "Duplicate reservation";
    }
    for (auto p : reservations)
        if (cells.count(p))
            return "Reservation overlaps occupied cell";
    return {};
}
} // namespace wc
