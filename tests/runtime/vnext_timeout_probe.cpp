#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>

namespace
{
wc::Id Mix(wc::Id value)
{
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}
struct Activity
{
    wc::Int damage = 0, received = 0, healing = 0, healed = 0, prevented = 0;
    wc::Int tailDamage = 0, tailHealing = 0;
    int attacks = 0, skills = 0, moves = 0, lastDamage = 0, lastMove = 0;
};
void Describe(std::ostream &out, const wc::Catalog &catalog, const wc::Combat &combat,
              int seed, int round, int index, const char *variant)
{
    std::map<wc::Id, Activity> totals;
    const int tail = combat.CurrentTick() - 100;
    for (const auto &event : combat.Events())
    {
        auto &source = totals[event.source]; auto &target = totals[event.target];
        if (event.effect == wc::Effect::Damage)
        {
            source.damage += event.healthLoss; target.received += event.healthLoss;
            target.prevented += event.prevented;
            if (event.basicAttack) ++source.attacks; else ++source.skills;
            if (event.healthLoss > 0) source.lastDamage = event.tick;
            if (event.tick > tail) source.tailDamage += event.healthLoss;
        }
        if (event.effect == wc::Effect::Heal)
        {
            source.healing += event.resolved; target.healed += event.resolved;
            if (event.tick > tail) source.tailHealing += event.resolved;
        }
        if (event.effect == wc::Effect::Dash) { ++target.moves; target.lastMove = event.tick; }
    }
    for (const auto &unit : combat.Units())
    {
        const auto &activity = totals[unit.id];
        out << seed << ',' << round << ',' << index << ',' << variant << ',' << unit.side << ','
            << catalog.Definition(unit.definition, unit.neutral).id << ',' << unit.star << ',' << unit.relic << ','
            << unit.maxHealth << ',' << unit.health << ',' << activity.damage << ',' << activity.received << ','
            << activity.healing << ',' << activity.healed << ',' << activity.prevented << ',' << activity.attacks << ','
            << activity.skills << ',' << activity.moves << ',' << activity.lastDamage << ',' << activity.lastMove << ','
            << activity.tailDamage << ',' << activity.tailHealing << ',' << int(unit.state) << ','
            << unit.cell.column << ',' << unit.cell.row << '\n';
    }
}
}
int main(int argc, char **argv)
{
    try
    {
        const int seeds = argc > 1 ? std::stoi(argv[1]) : 1;
        if (seeds < 1 || seeds > 10) throw std::runtime_error("Probe is bounded to ten seeds");
        const auto catalog = wcvnext::WonderVNextCatalog();
        std::ofstream units("timeout-units.csv"), counters("counterfactuals.csv"), composition("all-encounter-composition.csv");
        units << "seed,round,index,variant,side,hero,star,relic,max_health_cp,final_health_cp,damage_done_cp,damage_received_cp,healing_done_cp,healing_received_cp,guard_prevented_cp,basic_hits,skill_damage_hits,moves,last_damage_tick,last_move_tick,last_5s_damage_cp,last_5s_healing_cp,final_state,column,row\n";
        counters << "seed,round,index,variant,timeout,winner,ticks,survivors_a,survivors_b\n";
        composition << "seed,round,index,timeout,side,hero,star,final_health_cp\n";
        bool probed = false;
        int timed = 0;
        for (int seed = 1; seed <= seeds; ++seed)
        {
            wc::Match match(catalog, wc::Id(seed), 0);
            std::vector<std::array<std::vector<wc::OwnedUnit>, 2>> locked;
            while (match.CurrentPhase() != wc::Phase::Finished && match.CurrentPhase() != wc::Phase::Aborted)
            {
                const auto before = match.CurrentPhase();
                match.Tick(catalog.rules.tickMs);
                if (!match.InvariantError().empty()) throw std::runtime_error(match.InvariantError());
                if (before == wc::Phase::Preparation && match.CurrentPhase() == wc::Phase::Combat)
                {
                    locked.clear();
                    for (const auto &encounter : match.Encounters())
                    {
                        std::array<std::vector<wc::OwnedUnit>, 2> inputs;
                        inputs[0] = match.Seats()[encounter.pairing.a].roster;
                        if (encounter.kind != wc::EncounterKind::Neutral) inputs[1] = match.Seats()[encounter.pairing.b].roster;
                        locked.push_back(std::move(inputs));
                    }
                }
                if (before != wc::Phase::Combat || match.CurrentPhase() == wc::Phase::Combat) continue;
                for (int index = 0; index < int(match.Encounters().size()); ++index)
                {
                    const auto &encounter = match.Encounters()[index];
                    const auto &combat = encounter.combat;
                    for (const auto &unit : combat.Units())
                        composition << seed << ',' << match.Round() << ',' << index << ',' << combat.Result().timeout << ','
                            << unit.side << ',' << catalog.Definition(unit.definition, unit.neutral).id << ',' << unit.star << ',' << unit.health << '\n';
                    if (!combat.Result().timeout) continue;
                    ++timed;
                    Describe(units, catalog, combat, seed, match.Round(), index, "actual_tournament");
                    if (probed || encounter.kind == wc::EncounterKind::Neutral) continue;
                    probed = true;
                    std::ofstream inputs("first-timeout-inputs.csv");
                    inputs << "seed,round,index,side,id,hero,star,on_board,column,row,bench,facing,relic\n";
                    for (int side = 0; side < 2; ++side) for (const auto &unit : locked[index][side])
                        inputs << seed << ',' << match.Round() << ',' << index << ',' << side << ',' << unit.id << ','
                            << catalog.units[unit.definition].id << ',' << unit.star << ',' << unit.onBoard << ','
                            << unit.cell.column << ',' << unit.cell.row << ',' << unit.bench << ',' << int(unit.facing) << ',' << unit.relic << '\n';
                    for (const char *variant : {"baseline_replay", "zero_healing_fixture", "90s_timeout_fixture", "125pct_basic_damage_fixture"})
                    {
                        auto candidate = catalog;
                        const std::string label = variant;
                        if (label == "zero_healing_fixture")
                            for (auto &unit : candidate.units) if (unit.ability.mechanic == wc::AbilityMechanic::StationaryGrove)
                                unit.ability.magnitude = {};
                        if (label == "90s_timeout_fixture") candidate.rules.combatTimeoutMs = 90000;
                        if (label == "125pct_basic_damage_fixture")
                            for (auto &unit : candidate.units) unit.attackDamage = wc::HalfUp(unit.attackDamage * 12500, 10000);
                        const wc::Id encounterId = wc::Id(match.Round()) * 8 + index + 1;
                        const wc::Id identity = combat.Units().front().id >> 21;
                        wc::Combat replay(candidate, locked[index][0], locked[index][1], Mix(wc::Id(seed) ^ encounterId), identity);
                        while (!replay.Result().complete)
                        {
                            replay.Tick();
                            if (!replay.InvariantError().empty()) throw std::runtime_error(replay.InvariantError());
                        }
                        if (label == "baseline_replay" && (replay.Result().winner != combat.Result().winner ||
                            replay.Result().ticks != combat.Result().ticks || replay.Events().size() != combat.Events().size()))
                            throw std::runtime_error("Reconstructed encounter differs from actual tournament");
                        const auto &result = replay.Result();
                        counters << seed << ',' << match.Round() << ',' << index << ',' << variant << ',' << result.timeout << ','
                            << result.winner << ',' << result.ticks << ',' << result.survivors[0] << ',' << result.survivors[1] << '\n';
                        Describe(units, candidate, replay, seed, match.Round(), index, variant);
                    }
                }
            }
            if (match.CurrentPhase() != wc::Phase::Finished) throw std::runtime_error("Probe match aborted");
        }
        std::cout << "PASS timeout probe: " << seeds << " native tournaments, " << timed << " timeouts inspected. "
                  << "Counterfactuals are isolated fixture experiments, not adopted tuning. Catalog " << catalog.contentDigest << '\n';
    }
    catch (const std::exception &error) { std::cerr << "FAIL " << error.what() << '\n'; return 1; }
}
