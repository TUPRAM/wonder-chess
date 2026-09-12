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
Cell FacingStep(Facing facing)
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
std::vector<Cell> LineCells(Cell from, Cell to)
{
    std::vector<Cell> cells;
    const int dx = std::abs(to.column - from.column), dy = -std::abs(to.row - from.row);
    const int sx = from.column < to.column ? 1 : -1, sy = from.row < to.row ? 1 : -1;
    int error = dx + dy;
    while (!(from == to))
    {
        const int twice = 2 * error;
        if (twice >= dy) { error += dy; from.column += sx; }
        if (twice <= dx) { error += dx; from.row += sy; }
        cells.push_back(from);
    }
    return cells;
}
std::vector<Cell> BeamCells(Cell center, int radius, bool vertical, const Rules &rules)
{
    std::vector<Cell> cells;
    for (int offset = -radius; offset <= radius; ++offset)
    {
        Cell cell{center.column + (vertical ? 0 : offset), center.row + (vertical ? offset : 0)};
        if (cell.column >= 0 && cell.column < rules.columns && cell.row >= 0 && cell.row < rules.rows)
            cells.push_back(cell);
    }
    return cells;
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
    if (!trait.tiers.empty())
    {
        int value = 0;
        for (const auto &tier : trait.tiers) if (count >= tier.first) value = tier.second;
        return value;
    }
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
bool RelicCompatible(const RelicDef &relic, AbilityMechanic mechanic)
{
    return std::find(relic.compatibleMechanics.begin(), relic.compatibleMechanics.end(), mechanic) !=
           relic.compatibleMechanics.end();
}
AbilityDef EffectiveAbility(const Catalog &catalog, const UnitDef &unit, int relic)
{
    auto ability = unit.ability;
    if (relic < 0) return ability;
    if (relic >= int(catalog.relics.size()) || !RelicCompatible(catalog.relics[relic], ability.mechanic))
        throw std::invalid_argument("Incompatible or unknown equipped relic");
    const auto &item = catalog.relics[relic];
    auto duration = [&](int ms, int bp, bool positive) {
        return std::max(positive ? catalog.rules.tickMs : 0,
            Ticks(int(HalfUp(Int(ms) * bp, 10000)), catalog.rules) * catalog.rules.tickMs);
    };
    for (auto &amount : ability.magnitude) amount = HalfUp(amount * item.magnitudeBp, 10000);
    for (auto &effect : ability.effects)
    {
        for (auto &amount : effect.magnitude) amount = HalfUp(amount * item.magnitudeBp, 10000);
        effect.durationMs = duration(effect.durationMs, item.durationBp, false);
    }
    ability.guardReductionBp = std::min(9000, int(HalfUp(Int(ability.guardReductionBp) * item.magnitudeBp, 10000)));
    ability.momentumPerStepBp = int(HalfUp(Int(ability.momentumPerStepBp) * item.magnitudeBp, 10000));
    ability.range = std::clamp(ability.range + item.rangeDelta, 1, 8);
    ability.radius = std::clamp(ability.radius + item.radiusDelta, 0, 8);
    ability.durationMs = duration(ability.durationMs, item.durationBp, false);
    ability.castMs = duration(ability.castMs, item.castBp, true);
    ability.cooldownMs = duration(ability.cooldownMs, item.cooldownBp, true);
    return ability;
}
std::string Catalog::Validate() const
{
    const auto &r = rules;
    const bool vnext = profileId == "wonder_vnext";
    if (!vnext && profileId != "alpha_24") return "Unsupported gameplay profile";
    if (r.columns != 8 || r.rows != 8 || r.deploymentRows != 4 || r.tickMs != 50 || r.seatCount != 8)
        return "Unsupported board, tick or seat contract";
    if ((!vnext && units.size() != 24) || units.empty() || bots.size() != 7 ||
        r.benchCapacity != (vnext ? 10 : 8) || r.shopSlots != 5)
        return "Update requires twenty-four units, seven personas, eight bench and five shop slots";
    if (r.startingHealth <= 0 || r.maximumLevel > (vnext ? 10 : 6) || r.startingLevel < 1 ||
        r.startingLevel > r.maximumLevel || r.interestDivisor <= 0 || r.combatTimeoutMs <= 0 ||
        r.maxRounds <= 0 || r.minAttackRate <= 0 || r.maxAttackRate < r.minAttackRate)
        return "Invalid numeric rules";
    if (r.maxHealth <= 0 || r.maxHealth > 100000000 || r.maxRawDamage <= 0 || r.maxRawDamage > 10000000 ||
        r.maxArmor < 0 || r.maxArmor > 10000)
        return "Unsafe integer bounds";
    if (vnext && std::any_of(units.begin(), units.end(), [](const UnitDef &u) { return u.cost < 1; }))
        return "Recruited heroes must have a positive cost";
    std::set<std::string> ids, abilities;
    std::vector<UnitDef> allDefinitions = units;
    allDefinitions.insert(allDefinitions.end(), neutrals.begin(), neutrals.end());
    for (const auto &u : allDefinitions)
    {
        if (!ids.insert(u.id).second || (u.ability.enabled && !abilities.insert(u.ability.id).second) || u.id.empty() ||
            (u.ability.enabled && u.ability.id.empty()))
            return "Duplicate or empty unit/ability ID";
        if (u.cost < 0 || u.cost > (vnext ? 5 : 3) || u.health <= 0 || u.health > r.maxHealth || u.attackDamage < 0 ||
            u.attackDamage > r.maxRawDamage || u.armor < 0 || u.armor > r.maxArmor || u.resistance < 0 ||
            u.resistance > r.maxArmor || u.attackRate <= 0 || u.movementRate <= 0 || u.range < 1)
            return "Invalid unit numeric field: " + u.id;
        const auto &a = u.ability;
        if ((a.enabled && (a.castMs <= 0 || a.cooldownMs <= 0 || a.maxTargets <= 0 || a.maxTargets > (vnext ? 24 : 12) ||
            a.firstCastMs < 0 || a.recoveryMs < 0 || a.travelMs < 0 || a.durationMs < 0)) ||
            u.attackWindupMs <= 0)
            return "Invalid ability timing: " + u.id;
        if (a.mechanic < AbilityMechanic::Standard || a.mechanic > AbilityMechanic::TidalPush ||
            (!vnext && a.mechanic != AbilityMechanic::Standard)) return "Unsupported ability mechanic: " + u.id;
        if (a.mechanic != AbilityMechanic::Standard)
        {
            if (!a.enabled || a.range < 1 || a.range > 8 || a.radius < 0 || a.radius > 8 ||
                !a.effects.empty()) return "Invalid mechanic shape/effects: " + u.id;
            if (a.mechanic == AbilityMechanic::DirectionalGuard &&
                (a.guardReductionBp < 1 || a.guardReductionBp > 9000 || a.radius < 1))
                return "Invalid directional guard: " + u.id;
            if (a.mechanic == AbilityMechanic::MomentumCharge &&
                (a.maxDash < 1 || a.maxDash > 3 || a.maxMomentumSteps < 1 || a.maxMomentumSteps > 8 ||
                 a.momentumPerStepBp < 0 || a.momentumPerStepBp > 3000))
                return "Invalid momentum charge: " + u.id;
            if (a.mechanic == AbilityMechanic::StationaryGrove &&
                (a.stationaryMs < r.tickMs || a.pulseMs < r.tickMs || a.durationMs < a.pulseMs ||
                 a.durationMs / a.pulseMs > 32)) return "Invalid stationary grove: " + u.id;
            if (a.mechanic == AbilityMechanic::CrossingBeams &&
                (a.secondaryDelayMs < r.tickMs || a.secondaryDelayMs > 5000))
                return "Invalid crossing beam delay: " + u.id;
            if (a.mechanic == AbilityMechanic::TidalPush &&
                (a.displacementCells < 1 || a.displacementCells > 2)) return "Invalid displacement: " + u.id;
        }
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
    {
        if (!traitIds.insert(trait.id).second || !supportedStats.count(trait.stat) ||
            (!vnext && (trait.threshold != 2 || trait.threshold4 != 4 || !trait.tiers.empty())) ||
            trait.value < 0 || trait.value4 < 0)
            return "Invalid trait definition";
        int previous = 0;
        for (const auto &tier : trait.tiers)
        {
            if (tier.first <= previous || tier.first > r.maximumLevel || tier.second < 0 || tier.second > 10000)
                return "Invalid ordered trait tiers";
            previous = tier.first;
        }
    }
    if (!vnext && (!relics.empty() || !r.relicRounds.empty())) return "Relics require wonder_vnext";
    std::set<std::string> relicIds;
    for (const auto &relic : relics)
    {
        if (relic.id.empty() || !relicIds.insert(relic.id).second || relic.compatibleMechanics.empty() ||
            relic.magnitudeBp < 5000 || relic.magnitudeBp > 15000 || std::abs(relic.rangeDelta) > 2 ||
            std::abs(relic.radiusDelta) > 2 || relic.durationBp < 5000 || relic.durationBp > 20000 ||
            relic.castBp < 5000 || relic.castBp > 20000 || relic.cooldownBp < 5000 || relic.cooldownBp > 20000)
            return "Invalid relic definition";
        for (auto mechanic : relic.compatibleMechanics)
            if (mechanic <= AbilityMechanic::Standard || mechanic > AbilityMechanic::TidalPush)
                return "Unsupported relic compatibility";
    }
    if (vnext && r.maximumRelics != 3) return "VNext requires three relic slots";
    int previousRelicRound = 0;
    for (int round : r.relicRounds)
    {
        if (round <= previousRelicRound || round > r.maxRounds || relics.size() < 3)
            return "Invalid relic draft rounds";
        previousRelicRound = round;
    }
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
        for (int tier = 0; tier < 5; ++tier)
        {
            int w = it->second[tier];
            if (w < 0 || (!vnext && tier >= 3 && w != 0))
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
                if (o.facing < Facing::Forward || o.facing > Facing::Left)
                    throw std::invalid_argument("Invalid preparation orientation");
                u.facing = Facing((int(o.facing) + side * 2) % 4);
                u.relic = o.relic;
                u.ability = EffectiveAbility(c, d, o.relic);
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
                u.cooldownTick = Ticks(u.ability.firstCastMs, c.rules);
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
    const auto &a = s.ability;
    if (!a.enabled || tick_ < s.cooldownTick)
        return false;
    if (a.mechanic != AbilityMechanic::Standard) return CommitMechanic(source, a);
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
bool Combat::ChargeLanding(int source, const AbilityDef &a, int target, Cell &landing) const
{
    const auto &s = units_[source];
    if (target < 0 || !Alive(units_[target]) || Distance(s.cell, units_[target].cell) > a.range)
        return false;
    const auto path = LineCells(s.cell, units_[target].cell);
    if (path.empty() || int(path.size()) - 1 > a.maxDash) return false;
    if (path.size() == 1)
    {
        landing = s.cell;
        return s.momentumSteps > 0;
    }
    Cell previous = s.cell;
    for (std::size_t i = 0; i + 1 < path.size(); ++i)
    {
        const auto cell = path[i];
        if (!Free(cell, source)) return false;
        if (cell.column != previous.column && cell.row != previous.row &&
            (!Free({cell.column, previous.row}, source) || !Free({previous.column, cell.row}, source)))
            return false;
        previous = cell;
    }
    landing = previous;
    return true;
}
bool Combat::CommitMechanic(int source, const AbilityDef &a)
{
    auto &s = units_[source];
    if (a.mechanic == AbilityMechanic::DirectionalGuard) return false;
    if (a.mechanic == AbilityMechanic::MomentumCharge)
    {
        Cell landing;
        if (!ChargeLanding(source, a, s.target, landing)) return false;
        if (!(landing == s.cell)) s.destination = landing;
        s.abilityAim = units_[s.target].cell;
    }
    else if (a.mechanic == AbilityMechanic::StationaryGrove)
    {
        if (tick_ - s.lastMovementTick < Ticks(a.stationaryMs, catalog_->rules)) return false;
        bool injured = false;
        for (const auto &u : units_)
            if (Alive(u) && u.side == s.side && (u.id != s.id || a.allowSelf) &&
                u.health < u.maxHealth && Distance(u.cell, s.cell) <= a.radius) injured = true;
        if (!injured) return false;
        s.abilityAim = s.cell;
    }
    else if (a.mechanic == AbilityMechanic::TidalPush)
    {
        const Cell step = FacingStep(s.facing);
        bool target = false;
        for (const auto &u : units_)
        {
            const int x = u.cell.column - s.cell.column, y = u.cell.row - s.cell.row;
            const int distance = x * step.column + y * step.row;
            if (Alive(u) && u.side != s.side && distance > 0 && distance <= a.range &&
                x * step.row - y * step.column == 0) target = true;
        }
        if (!target) return false;
        s.abilityAim = {std::clamp(s.cell.column + step.column * a.range, 0, catalog_->rules.columns - 1),
                       std::clamp(s.cell.row + step.row * a.range, 0, catalog_->rules.rows - 1)};
    }
    else
    {
        int target = -1;
        for (int i = 0; i < int(units_.size()); ++i)
        {
            const auto &u = units_[i];
            if (!Alive(u) || u.side == s.side || Distance(s.cell, u.cell) > a.range) continue;
            if (target < 0 || std::make_tuple(a.mechanic == AbilityMechanic::ScreenedStrike ?
                    -Distance(s.cell, u.cell) : Distance(s.cell, u.cell), u.initiative, u.id) <
                std::make_tuple(a.mechanic == AbilityMechanic::ScreenedStrike ?
                    -Distance(s.cell, units_[target].cell) : Distance(s.cell, units_[target].cell),
                    units_[target].initiative, units_[target].id)) target = i;
        }
        if (target < 0) return false;
        s.target = target;
        s.abilityAim = units_[target].cell;
    }
    s.actionId = nextAction_++;
    s.state = ActionState::CastWindup;
    s.releaseTick = tick_ + Ticks(a.castMs, catalog_->rules);
    s.recoveryTick = s.releaseTick + Ticks(a.recoveryMs, catalog_->rules);
    s.cooldownTick = tick_ + Ticks(a.cooldownMs, catalog_->rules);
    return true;
}
void Combat::MoveUnit(int unit, Cell cell, AbilityMechanic mechanic, Id action, int source)
{
    auto &u = units_[unit];
    if (u.cell == cell) return;
    CombatEvent event;
    event.tick = tick_; event.source = units_[source].id; event.target = u.id;
    event.action = action; event.effect = Effect::Dash; event.mechanic = mechanic;
    event.origin = u.cell; event.cell = cell;
    u.cell = cell;
    u.lastMovementTick = tick_;
    ++u.positionEpoch;
    if (u.ability.mechanic == AbilityMechanic::MomentumCharge && mechanic == AbilityMechanic::Standard)
        u.momentumSteps = std::min(u.ability.maxMomentumSteps, u.momentumSteps + 1);
    if (catalog_->profileId == "wonder_vnext") events_.push_back(event);
}
std::vector<int> Combat::PacketTargets(const Packet &packet) const
{
    std::vector<int> targets;
    const auto &source = units_[packet.source];
    if (packet.tethered && (!Alive(source) || source.state == ActionState::Stunned ||
        source.positionEpoch != packet.positionEpoch || !(source.cell == packet.origin))) return targets;
    for (int i = 0; i < int(units_.size()); ++i)
    {
        const auto &u = units_[i];
        if (!Alive(u) || (packet.allied ? u.side != source.side : u.side == source.side) ||
            (packet.allied && i == packet.source && !packet.allowSelf)) continue;
        const bool within = packet.cells.empty() ? Distance(u.cell, packet.center) <= packet.radius :
            std::find(packet.cells.begin(), packet.cells.end(), u.cell) != packet.cells.end();
        if (within && (packet.effect != Effect::Heal || u.health < u.maxHealth)) targets.push_back(i);
    }
    std::sort(targets.begin(), targets.end(), [&](int x, int y) {
        if (packet.mechanic == AbilityMechanic::ScreenedStrike || packet.mechanic == AbilityMechanic::TidalPush)
            return std::make_tuple(Distance(packet.origin, units_[x].cell), units_[x].initiative) <
                   std::make_tuple(Distance(packet.origin, units_[y].cell), units_[y].initiative);
        return units_[x].initiative < units_[y].initiative;
    });
    if (int(targets.size()) > packet.maxTargets) targets.resize(packet.maxTargets);
    return targets;
}
void Combat::ReleaseMechanic(int source, const AbilityDef &a)
{
    auto &s = units_[source];
    const auto &rules = catalog_->rules;
    s.state = ActionState::CastRecovery;
    Packet packet;
    packet.source = source; packet.action = s.actionId; packet.releasedAt = tick_;
    packet.due = tick_ + Ticks(a.travelMs, rules); packet.origin = s.cell;
    packet.center = s.abilityAim; packet.key = a.id; packet.mechanic = a.mechanic;
    packet.damageType = a.damageType; packet.effect = a.effect;
    packet.magnitude = a.magnitude[s.star - 1]; packet.radius = a.radius;
    packet.bonus = s.abilityBonus + s.allBonus; packet.maxTargets = a.maxTargets;
    packet.duration = Ticks(a.durationMs, rules);
    if (a.mechanic == AbilityMechanic::MomentumCharge)
    {
        Cell landing;
        if (!ChargeLanding(source, a, s.target, landing) || !(units_[s.target].cell == s.abilityAim))
        { CancelReservation(source); return; }
        const int steps = std::min(a.maxMomentumSteps, s.momentumSteps + Distance(s.cell, landing));
        packet.bonus += steps * a.momentumPerStepBp;
        MoveUnit(source, landing, a.mechanic, s.actionId, source);
        CancelReservation(source);
        s.momentumSteps = 0;
        packet.target = s.target;
        packets_.push_back(packet);
    }
    else if (a.mechanic == AbilityMechanic::StationaryGrove)
    {
        if (!(s.cell == s.abilityAim)) return;
        packet.area = packet.allied = packet.tethered = true;
        packet.allowSelf = a.allowSelf; packet.positionEpoch = s.positionEpoch;
        packet.magnitude = HalfUp(packet.magnitude * (10000 + s.supportBonus), 10000);
        for (int elapsed = 0; elapsed < Ticks(a.durationMs, rules); elapsed += Ticks(a.pulseMs, rules))
        {
            packet.due = tick_ + elapsed;
            packets_.push_back(packet);
        }
    }
    else if (a.mechanic == AbilityMechanic::CrossingBeams)
    {
        packet.area = true;
        packet.cells = BeamCells(s.abilityAim, a.radius, false, rules);
        packets_.push_back(packet);
        packet.cells = BeamCells(s.abilityAim, a.radius, true, rules);
        packet.due += Ticks(a.secondaryDelayMs, rules);
        packets_.push_back(packet);
    }
    else if (a.mechanic == AbilityMechanic::ScreenedStrike || a.mechanic == AbilityMechanic::TidalPush)
    {
        packet.area = true;
        packet.cells = LineCells(s.cell, s.abilityAim);
        if (a.mechanic == AbilityMechanic::ScreenedStrike) packet.maxTargets = 1;
        else packet.displacementCells = a.displacementCells;
        packets_.push_back(packet);
    }
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
        v.impactTick = v.releaseTick + Ticks(basic ? definition.projectileTravelMs : source.ability.travelMs, catalog_->rules);
        v.radius = basic ? 0 : source.ability.radius;
        v.effect = basic ? Effect::Damage : (source.ability.effects.empty() ? source.ability.effect : source.ability.effects.front().effect);
        v.damageType = basic ? definition.damageType : (source.ability.effects.empty() ? source.ability.damageType : source.ability.effects.front().damageType);
        v.mechanic = basic ? AbilityMechanic::Standard : source.ability.mechanic;
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
        if (packet.tethered && (!Alive(source) || source.positionEpoch != packet.positionEpoch)) continue;
        auto found = std::find_if(result.begin(), result.end(), [&](const VisualAction& v) {
            return v.source == source.id && v.action == packet.action &&
                (packet.mechanic == AbilityMechanic::StationaryGrove || v.impactTick == packet.due);
        });
        if (found == result.end())
        {
            auto visual = describe(source, packet.basicAttack);
            visual.action = packet.action; visual.origin = packet.origin; visual.center = packet.center;
            visual.radius = packet.radius; visual.effect = packet.effect; visual.damageType = packet.damageType;
            visual.releaseTick = packet.releasedAt; visual.impactTick = packet.due;
            visual.released = true; visual.provisional = false;
            visual.fixedArea = packet.area; visual.recipientsProvisional = packet.area;
            visual.cells = packet.cells;
            if (packet.area)
                for (int target : PacketTargets(packet)) visual.recipients.push_back(units_[target].id);
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
        const auto& ability = source.ability;
        if (!basic && ability.mechanic != AbilityMechanic::Standard)
        {
            Packet packet;
            packet.source = i; packet.origin = source.cell; packet.center = source.abilityAim;
            packet.mechanic = ability.mechanic; packet.radius = ability.radius;
            packet.maxTargets = ability.maxTargets; packet.effect = ability.effect;
            visual.center = source.abilityAim;
            visual.fixedArea = true;
            if (ability.mechanic == AbilityMechanic::MomentumCharge)
            {
                visual.center = source.destination.column >= 0 ? source.destination : source.cell;
                visual.cells = LineCells(source.cell, visual.center);
                if (source.target >= 0 && Alive(units_[source.target]))
                { visual.target = units_[source.target].id; visual.recipients.push_back(visual.target); }
            }
            else
            {
                if (ability.mechanic == AbilityMechanic::StationaryGrove)
                { packet.allied = true; packet.allowSelf = ability.allowSelf; }
                else if (ability.mechanic == AbilityMechanic::CrossingBeams)
                    packet.cells = BeamCells(source.abilityAim, ability.radius, false, catalog_->rules);
                else
                {
                    packet.cells = LineCells(source.cell, source.abilityAim);
                    if (ability.mechanic == AbilityMechanic::ScreenedStrike) packet.maxTargets = 1;
                }
                visual.cells = packet.cells;
                for (int target : PacketTargets(packet)) visual.recipients.push_back(units_[target].id);
                if (ability.mechanic == AbilityMechanic::CrossingBeams)
                {
                    result.push_back(visual);
                    visual.impactTick += Ticks(ability.secondaryDelayMs, catalog_->rules);
                    packet.cells = BeamCells(source.abilityAim, ability.radius, true, catalog_->rules);
                    visual.cells = packet.cells;
                    visual.recipients.clear();
                    for (int target : PacketTargets(packet)) visual.recipients.push_back(units_[target].id);
                }
            }
            result.push_back(visual);
            continue;
        }
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
    p.key = s.ability.id;
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
    const auto &a = s.ability;
    if (a.mechanic != AbilityMechanic::Standard) { ReleaseMechanic(source, a); return; }
    s.state = ActionState::CastRecovery;
    if ((a.effects.empty() ? a.effect : a.effects.front().effect) == Effect::Dash)
    {
        if (s.target >= 0 && Alive(units_[s.target]) && Free(s.destination, source))
        {
            MoveUnit(source, s.destination, AbilityMechanic::Standard, s.actionId, source);
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
    e.origin = p.origin;
    e.mechanic = p.mechanic;
    switch (p.effect)
    {
    case Effect::Damage: {
        e.resolved = ResolveDamage(p.magnitude, p.damageType, t.armor, t.resistance, p.bonus);
        int guard = -1;
        for (int i = 0; i < int(units_.size()); ++i)
        {
            const auto &g = units_[i];
            const auto &a = g.ability;
            if (!Alive(g) || g.state == ActionState::Stunned || g.side != t.side || i == target ||
                a.mechanic != AbilityMechanic::DirectionalGuard || !a.enabled) continue;
            const Cell step = FacingStep(g.facing);
            auto sector = [&](Cell cell, bool behind) {
                const int x = cell.column - g.cell.column, y = cell.row - g.cell.row;
                const int dot = (x * step.column + y * step.row) * (behind ? -1 : 1);
                return dot > 0 && std::abs(x * step.row - y * step.column) <= dot;
            };
            if (!sector(p.origin, false) || !sector(t.cell, true) || Distance(g.cell, t.cell) > a.radius) continue;
            int recipient = -1;
            for (int ally = 0; ally < int(units_.size()); ++ally)
            {
                const auto &u = units_[ally];
                if (!Alive(u) || u.side != g.side || ally == i || !sector(u.cell, true) ||
                    Distance(g.cell, u.cell) > a.radius) continue;
                if (recipient < 0 || std::make_tuple(Distance(g.cell, u.cell), u.initiative) <
                    std::make_tuple(Distance(g.cell, units_[recipient].cell), units_[recipient].initiative)) recipient = ally;
            }
            if (recipient != target) continue;
            if (guard < 0 || std::make_tuple(-a.guardReductionBp, g.initiative) <
                std::make_tuple(-units_[guard].ability.guardReductionBp, units_[guard].initiative)) guard = i;
        }
        if (guard >= 0)
        {
            const Int remaining = HalfUp(e.resolved * (10000 - units_[guard].ability.guardReductionBp), 10000);
            e.prevented = e.resolved - remaining;
            e.resolved = remaining;
            e.guardedBy = units_[guard].id;
        }
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
            ++t.positionEpoch;
            t.lastMovementTick = tick_;
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
    if (p.displacementCells > 0 && Alive(t))
    {
        const Cell direction{(p.center.column > p.origin.column) - (p.center.column < p.origin.column),
                             (p.center.row > p.origin.row) - (p.center.row < p.origin.row)};
        Cell destination = t.cell;
        for (int step = 0; step < p.displacementCells; ++step)
        {
            Cell next{destination.column + direction.column, destination.row + direction.row};
            if (!Free(next, target)) break;
            destination = next;
        }
        if (!(destination == t.cell))
        {
            CancelReservation(target);
            MoveUnit(target, destination, p.mechanic, p.action, p.source);
            if (t.state == ActionState::Moving) t.state = ActionState::Idle;
            else if (t.state == ActionState::AttackWindup) t.state = ActionState::AttackRecovery;
            else if (t.state == ActionState::CastWindup) t.state = ActionState::CastRecovery;
        }
    }
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
                    if (!PacketTargets(p).empty()) { draining_ = true; return; }
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
                    MoveUnit(i, u.destination, AbilityMechanic::Standard, 0, i);
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
            const auto targets = PacketTargets(p);
            for (std::size_t index = 0; index < targets.size(); ++index)
            {
                Packet impact = p;
                if (index > 0) impact.displacementCells = 0;
                Apply(impact, targets[index]);
            }
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
            ++u.basicAttackOrdinal;
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
