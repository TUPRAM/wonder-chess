#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <cmath>
#include <deque>
#include <functional>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
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
std::string Catalog::Validate() const
{
    const auto &r = rules;
    if (r.columns != 8 || r.rows != 8 || r.deploymentRows != 4 || r.tickMs != 50 || r.seatCount != 8)
        return "Unsupported board, tick or seat contract";
    if (units.size() != 12 || bots.size() != 7 || r.benchCapacity != 8 || r.shopSlots != 5)
        return "Alpha requires twelve units, seven personas, eight bench and five shop slots";
    if (r.startingHealth <= 0 || r.maximumLevel > 6 || r.startingLevel < 1 ||
        r.startingLevel > r.maximumLevel || r.interestDivisor <= 0 || r.combatTimeoutMs <= 0 ||
        r.maxRounds <= 0 || r.minAttackRate <= 0 || r.maxAttackRate < r.minAttackRate)
        return "Invalid numeric rules";
    if (r.maxHealth <= 0 || r.maxHealth > 100000000 || r.maxRawDamage <= 0 || r.maxRawDamage > 10000000 ||
        r.maxArmor < 0 || r.maxArmor > 10000)
        return "Unsafe integer bounds";
    std::set<std::string> ids, abilities;
    for (const auto &u : units)
    {
        if (!ids.insert(u.id).second || !abilities.insert(u.ability.id).second || u.id.empty() ||
            u.ability.id.empty())
            return "Duplicate or empty unit/ability ID";
        if (u.cost < 1 || u.cost > 3 || u.health <= 0 || u.health > r.maxHealth || u.attackDamage < 0 ||
            u.attackDamage > r.maxRawDamage || u.armor < 0 || u.armor > r.maxArmor || u.resistance < 0 ||
            u.resistance > r.maxArmor || u.attackRate <= 0 || u.movementRate <= 0 || u.range < 1)
            return "Invalid unit numeric field: " + u.id;
        const auto &a = u.ability;
        if (a.castMs <= 0 || a.cooldownMs <= 0 || a.maxTargets <= 0 || a.maxTargets > 12 ||
            a.firstCastMs < 0 || a.recoveryMs < 0 || a.travelMs < 0 || a.durationMs < 0 ||
            u.attackWindupMs <= 0)
            return "Invalid ability timing: " + u.id;
        if (Ticks(u.attackWindupMs, r) >= AttackInterval(r.maxAttackRate, 0, r))
            return "Attack windup leaves no recovery at maximum rate: " + u.id;
        for (auto magnitude : a.magnitude)
        {
            if (magnitude > r.maxRawDamage || magnitude < -10000)
                return "Unsafe effect magnitude: " + u.id;
            if (a.effect != Effect::StatModifier && magnitude < 0)
                return "Negative non-stat effect magnitude: " + u.id;
            if ((a.effect == Effect::Dash || a.effect == Effect::Stun) && magnitude != 0)
                return "Dash and stun cannot carry hidden magnitude: " + u.id;
        }
        for (int star = 1; star <= 3; ++star)
            if (StarValue(u.health, star, 10000, r) > r.maxHealth)
                return "Derived health exceeds supported bounds";
    }
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
            if (o.onBoard)
            {
                const auto &d = c.units[o.definition];
                counts[d.race].insert(o.definition);
                counts[d.unitClass].insert(o.definition);
            }
        for (const auto &o : formation)
            if (o.onBoard)
            {
                const auto &d = c.units[o.definition];
                CombatUnit u;
                u.id = (encounterId << 40) | (Id(side) << 39) | o.id;
                u.definition = o.definition;
                u.side = side;
                u.star = o.star;
                u.cell = EncounterCell(o.cell, side, c.rules);
                u.armor = d.armor;
                u.resistance = d.resistance;
                int healthBonus = 0;
                for (const auto &t : c.traits)
                    if ((t.id == d.race || t.id == d.unitClass) && int(counts[t.id].size()) >= t.threshold)
                    {
                        if (t.stat == "max_health_bonus_bp")
                            healthBonus += t.value;
                        else if (t.stat == "attack_rate_bonus_bp")
                            u.rateBonus += t.value;
                        else if (t.stat == "physical_armor_flat")
                            u.armor += t.value;
                        else if (t.stat == "magic_resistance_flat")
                            u.resistance += t.value;
                        else if (t.stat == "all_damage_bonus_bp")
                            u.allBonus += t.value;
                        else if (t.stat == "basic_damage_bonus_bp")
                            u.basicBonus += t.value;
                        else if (t.stat == "ability_damage_bonus_bp")
                            u.abilityBonus += t.value;
                        else if (t.stat == "support_power_bonus_bp")
                            u.supportBonus += t.value;
                    }
                u.health = u.maxHealth = StarValue(d.health, o.star, healthBonus, c.rules);
                u.basicDamage = StarValue(d.attackDamage, o.star, 0, c.rules);
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
        if (Distance(at, enemy.cell) <= catalog_->units[u.definition].range)
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
        case Selector::LowestHealthAlly:
            valid = t.side == s.side && (i != source || a.allowSelf) && Distance(s.cell, t.cell) <= a.range;
            break;
        default:
            break;
        }
        if (a.effect == Effect::Heal && t.health >= t.maxHealth)
            valid = false;
        if (a.effect == Effect::Shield)
        {
            auto magnitude = HalfUp(a.magnitude[s.star - 1] * (10000 + s.supportBonus), 10000);
            if (magnitude < t.shield ||
                (magnitude == t.shield && tick_ + Ticks(a.durationMs, catalog_->rules) <= t.shieldExpiry))
                valid = false;
        }
        if (valid)
            selected.push_back(i);
    }
    std::sort(selected.begin(), selected.end(), [&](int x, int y) {
        const auto &l = units_[x];
        const auto &r = units_[y];
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
    const int max = a.selector == Selector::LowestHealthAlly ? 1 : a.maxTargets;
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
                if (separation <= original || separation > catalog_->units[s.definition].range)
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
    const auto &a = catalog_->units[s.definition].ability;
    if (tick_ < s.cooldownTick)
        return false;
    if (a.effect == Effect::Dash)
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
void Combat::Release(int source)
{
    auto &s = units_[source];
    const auto &d = catalog_->units[s.definition];
    const auto &r = catalog_->rules;
    Packet p;
    p.source = source;
    p.action = s.actionId;
    p.due = tick_;
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
    if (a.effect == Effect::Dash)
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
    p.effect = a.effect;
    p.damageType = a.damageType;
    p.radius = a.radius;
    p.center = s.cell;
    p.magnitude = a.magnitude[s.star - 1];
    p.duration = Ticks(a.durationMs, r);
    p.due += Ticks(a.travelMs, r);
    p.bonus = s.abilityBonus + s.allBonus;
    if (a.effect == Effect::Heal || a.effect == Effect::Shield ||
        (a.effect == Effect::StatModifier && p.magnitude > 0))
        p.magnitude = HalfUp(p.magnitude * (10000 + s.supportBonus), 10000);
    auto targets = Select(source, a);
    if (a.selector == Selector::CurrentEnemyArea)
    {
        if (targets.empty())
            return;
        p.area = true;
        p.center = units_[targets.front()].cell;
        p.radius = a.radius;
        packets_.push_back(p);
    }
    else
        for (int target : targets)
        {
            p.target = target;
            packets_.push_back(p);
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
        return std::make_tuple(a.due, units_[a.source].initiative, a.action,
                               a.target < 0 ? -1 : units_[a.target].initiative) <
               std::make_tuple(b.due, units_[b.source].initiative, b.action,
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
            for (int i : order)
                if (Alive(units_[i]) && units_[i].side != units_[p.source].side &&
                    Distance(units_[i].cell, p.center) <= p.radius)
                    Apply(p, i);
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
        const auto &d = catalog_->units[u.definition];
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
            u.movementTick = tick_ + int((1000000 + Int(d.movementRate) * catalog_->rules.tickMs - 1) /
                                         (Int(d.movementRate) * catalog_->rules.tickMs));
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
