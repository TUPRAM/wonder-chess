#pragma once
#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <map>

// Who did what in one fight, read from its events. Presentation only: nothing here changes a fight.
namespace wc
{
enum class ChartMode
{
    Dealt,
    Taken,
    Healed,
    // Damage kept off a unit's health by a shield (credited to whoever gave the shield) or a guard.
    Blocked
};
struct ChartRow
{
    Id unit = 0;
    int definition = -1, star = 1;
    bool neutral = false;
    // Damage split as physical, magic and true. Healing and blocked amounts use the first part only.
    std::array<Int, 3> parts{};
    Int total = 0;
};
// One row for each unit that started the fight on `side`, largest total first. What a summoned
// unit does is added to the row of the unit that summoned it.
inline std::vector<ChartRow> FightChart(const Combat &combat, int side, ChartMode mode)
{
    const auto &units = combat.Units();
    std::vector<ChartRow> rows;
    std::map<Id, std::size_t> rowOf;
    for (const auto &u : units)
        if (u.side == side && !u.summoned)
        {
            rowOf[u.id] = rows.size();
            ChartRow row;
            row.unit = u.id; row.definition = u.definition; row.star = u.star; row.neutral = u.neutral;
            rows.push_back(row);
        }
    for (const auto &u : units)
        if (u.side == side && u.summoned)
        {
            int owner = u.owner;
            while (owner >= 0 && owner < int(units.size()) && units[owner].summoned) owner = units[owner].owner;
            if (owner >= 0 && owner < int(units.size()) && rowOf.count(units[owner].id)) rowOf[u.id] = rowOf[units[owner].id];
        }
    const auto add = [&](Id who, DamageType type, Int amount) {
        const auto found = rowOf.find(who);
        if (found == rowOf.end() || amount <= 0) return;
        rows[found->second].parts[int(type)] += amount;
        rows[found->second].total += amount;
    };
    for (const auto &e : combat.Events())
    {
        if (mode == ChartMode::Healed)
        {
            if (e.effect == Effect::Heal) add(e.source, DamageType::Physical, e.resolved);
        }
        else if (e.effect == Effect::Damage)
        {
            if (mode == ChartMode::Dealt) add(e.source, e.damageType, e.healthLoss);
            else if (mode == ChartMode::Taken) add(e.target, e.damageType, e.healthLoss);
            else
            {
                add(e.absorbedFrom, DamageType::Physical, e.absorbed);
                add(e.guardedBy, DamageType::Physical, e.prevented);
            }
        }
    }
    std::stable_sort(rows.begin(), rows.end(), [](const ChartRow &l, const ChartRow &r) { return l.total > r.total; });
    return rows;
}
} // namespace wc
