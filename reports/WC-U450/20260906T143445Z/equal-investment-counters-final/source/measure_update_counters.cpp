#include "CatalogFixture.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

// Selected compositions are experimental deployments, never altered hero statistics.
// Equal purchase cost excludes acquisition probability, rerolls, and level XP.
namespace {
int checks = 0, fights = 0, totalEvents = 0, timeouts = 0;
void Require(bool condition, const std::string& why) {
    ++checks;
    if (!condition) throw std::runtime_error(why);
}
struct Slot { const char* hero; int x, y; };
struct Formation {
    const char* name;
    const char* focus;
    const char* trait;
    std::array<Slot, 6> slots;
};
const std::array<Formation, 4> subjects{{
    {"Neris_Mage4", "wc_u_elf_mage", "mage", {{{"wc_u_human_guardian", 3, 3}, {"wc_u_dwarf_guardian", 4, 3},
        {"wc_u_human_mage", 1, 1}, {"wc_u_orc_mage", 3, 1}, {"wc_u_elf_mage", 4, 1}, {"wc_u_halfling_mage", 6, 1}}}},
    {"Elin_Priest4", "wc_u_elf_priest", "priest", {{{"wc_u_dragonkin_guardian", 3, 3}, {"wc_u_dwarf_warrior", 4, 3},
        {"wc_u_human_priest", 2, 2}, {"wc_u_elf_priest", 3, 2}, {"wc_u_dwarf_priest", 4, 2}, {"wc_u_dragonkin_priest", 5, 2}}}},
    {"Elin_Elf4", "wc_u_elf_priest", "elf", {{{"wc_u_human_guardian", 3, 3}, {"wc_u_orc_guardian", 4, 3},
        {"wc_u_elf_rogue", 1, 3}, {"wc_u_elf_priest", 3, 2}, {"wc_u_elf_ranger", 2, 1}, {"wc_u_elf_mage", 5, 1}}}},
    {"Iri_Rogue4", "wc_u_dragonkin_rogue", "rogue", {{{"wc_u_human_guardian", 3, 3}, {"wc_u_dwarf_guardian", 4, 3},
        {"wc_u_elf_rogue", 1, 3}, {"wc_u_orc_rogue", 6, 3}, {"wc_u_halfling_rogue", 2, 3}, {"wc_u_dragonkin_rogue", 5, 3}}}}
}};
const std::array<Formation, 3> pressures{{
    {"Warrior4_frontline", "", "warrior", {{{"wc_u_human_warrior", 2, 3}, {"wc_u_dwarf_warrior", 4, 3},
        {"wc_u_orc_warrior", 5, 3}, {"wc_u_halfling_warrior", 6, 3}, {"wc_u_dragonkin_guardian", 3, 3}, {"wc_u_elf_mage", 3, 1}}}},
    {"Ranger4_spread", "", "ranger", {{{"wc_u_dragonkin_guardian", 3, 3}, {"wc_u_elf_rogue", 6, 3},
        {"wc_u_elf_ranger", 0, 0}, {"wc_u_dwarf_ranger", 2, 0}, {"wc_u_halfling_ranger", 5, 0}, {"wc_u_dragonkin_ranger", 7, 0}}}},
    {"Control_mixed", "", "", {{{"wc_u_dwarf_guardian", 3, 3}, {"wc_u_orc_guardian", 4, 3},
        {"wc_u_halfling_rogue", 2, 3}, {"wc_u_elf_rogue", 6, 3}, {"wc_u_elf_mage", 3, 1}, {"wc_u_halfling_ranger", 5, 1}}}}
}};
int Definition(const wc::Catalog& catalog, const char* id) {
    for (int i = 0; i < int(catalog.units.size()); ++i)
        if (catalog.units[i].id == id) return i;
    throw std::runtime_error(std::string("missing canonical definition ") + id);
}
std::vector<wc::OwnedUnit> Deploy(const wc::Catalog& catalog, const Formation& f, int star) {
    std::vector<wc::OwnedUnit> result;
    std::set<std::pair<int,int>> cells;
    std::set<int> definitions;
    int baseCost = 0, tierMembers = 0;
    for (const auto& slot : f.slots) {
        const int definition = Definition(catalog, slot.hero);
        const auto& d = catalog.units[definition];
        Require(cells.emplace(slot.x, slot.y).second, "duplicate deployment cell");
        Require(definitions.insert(definition).second, "duplicate hero would change distinct trait budget");
        Require(slot.x >= 0 && slot.x < catalog.rules.columns && slot.y >= 0 && slot.y < catalog.rules.deploymentRows,
                "illegal deployment cell");
        baseCost += d.cost;
        tierMembers += (d.race == f.trait || d.unitClass == f.trait);
        wc::OwnedUnit u;
        u.id = result.size() + 1; u.definition = definition; u.star = star; u.onBoard = true; u.cell = {slot.x, slot.y};
        result.push_back(u);
    }
    Require(result.size() == 6 && baseCost == 12, "experiment requires six slots and twelve base gold on every side");
    Require(!*f.trait || tierMembers == 4, "named four-member trait is not actually reachable in deployment");
    Require(!*f.focus || definitions.count(Definition(catalog, f.focus)) == 1, "missing focus hero");
    return result;
}
const char* EffectName(wc::Effect effect) {
    switch (effect) {
    case wc::Effect::Damage: return "damage";
    case wc::Effect::Heal: return "heal";
    case wc::Effect::Shield: return "shield";
    case wc::Effect::Stun: return "stun";
    case wc::Effect::Dash: return "dash";
    case wc::Effect::StatModifier: return "attack_rate_modifier";
    }
    throw std::runtime_error("unknown effect");
}
const char* DamageName(wc::DamageType type) {
    return type == wc::DamageType::Physical ? "physical" : type == wc::DamageType::Magic ? "magic" : "true";
}
struct Metrics {
    wc::Int basicLoss = 0, skillLoss = 0, absorbed = 0, healing = 0, shields = 0, overkill = 0;
    wc::Int healedIn = 0, damageIn = 0, appliedStunMs = 0;
    int stunTicks = 0, aliveTicks = 0, movingTicks = 0, shieldTicks = 0, buffTicks = 0, debuffTicks = 0;
    int dashEvents = 0, statusEvents = 0;
    std::set<wc::Id> activeActions, basicActions;
};
struct Group {
    int runs = 0, wins = 0, losses = 0, draws = 0, timeout = 0, ticks = 0;
    wc::Int focusBasicLoss = 0, focusSkillLoss = 0, focusHealing = 0, focusAbsorbed = 0, focusAppliedStunMs = 0;
    int focusActions = 0, focusAliveTicks = 0, focusDashEvents = 0;
};
void Flush(std::ofstream& stream) { stream.flush(); Require(bool(stream), "evidence write failed"); }
}

int main() {
    std::ofstream summary("summary.json");
    try {
        const auto catalog = FixtureCatalog();
        Require(catalog.Validate().empty(), "canonical catalog validation");
        Require(catalog.units.size() == 24, "all24 canonical roster required");
        std::ofstream deployments("deployments.csv"), events("events.csv"), outcomes("outcomes.csv"), units("unit-outcomes.csv"), groups("counter-summary.csv");
        Require(bool(summary) && bool(deployments) && bool(events) && bool(outcomes) && bool(units) && bool(groups), "cannot open evidence");
        deployments << "fight,subject,pressure,star,seed,subject_side,side,formation,instance,unit_id,cost,copies,purchase_gold,local_col,local_row,combat_col,combat_row,initiative,max_health,basic_damage,armor,resistance,basic_bonus_bp,skill_bonus_bp,all_bonus_bp,rate_bonus_bp,support_bonus_bp,movement_bonus_bp\n";
        events << "fight,tick,source,target,action,source_hero,target_hero,effect,basic,damage_type,requested,resolved,absorbed,health_loss,overkill,absorbed_from,col,row,source_damage_bonus_bp,target_armor,target_resistance\n";
        outcomes << "fight,subject,pressure,star,seed,subject_side,slots_each,copies_each,purchase_gold_each,winner_side,subject_result,ticks,simulated_ms,timeout,subject_survivors,pressure_survivors,event_count\n";
        units << "fight,side,unit_id,instance,focus,alive,health,max_health,alive_ms,moving_ms,stunned_ms,shield_present_ms,positive_rate_modifier_ms,negative_rate_modifier_ms,basic_actions,active_actions,damage_basic_hp100,damage_skill_hp100,healing_hp100,shield_granted_hp100,shield_absorbed_hp100,overkill_hp100,applied_stun_packet_ms,dash_events,rate_modifier_events,received_healing_hp100,received_damage_hp100\n";
        groups << "subject,pressure,star,runs,wins,losses,draws,timeouts,mean_seconds,focus_basic_damage_hp100,focus_skill_damage_hp100,focus_effective_healing_hp100,focus_shield_absorbed_hp100,focus_active_actions,focus_applied_stun_packet_ms,focus_mean_alive_seconds,focus_dash_events\n";
        std::map<std::string, Group> aggregate;
        constexpr std::array<wc::Id, 4> seeds{1103, 2207, 3301, 4409};
        for (const auto& subject : subjects) for (const auto& pressure : pressures) for (int star : {1, 2}) {
            const auto subjectDeployment = Deploy(catalog, subject, star);
            const auto pressureDeployment = Deploy(catalog, pressure, star);
            for (const auto seed : seeds) for (int subjectSide = 0; subjectSide < 2; ++subjectSide) {
                const int fight = ++fights;
                const int copies = star == 1 ? 1 : 3;
                const std::array<const Formation*,2> formation = subjectSide == 0
                    ? std::array<const Formation*,2>{&subject, &pressure} : std::array<const Formation*,2>{&pressure, &subject};
                const auto& left = subjectSide == 0 ? subjectDeployment : pressureDeployment;
                const auto& right = subjectSide == 0 ? pressureDeployment : subjectDeployment;
                wc::Combat combat(catalog, left, right, seed, wc::Id(fight));
                std::map<wc::Id, wc::CombatUnit> initial;
                std::map<wc::Id, Metrics> measured;
                for (const auto& u : combat.Units()) {
                    initial.emplace(u.id, u);
                    measured.emplace(u.id, Metrics{});
                    const auto& d = catalog.units[u.definition];
                    const auto& owned = (u.side == 0 ? left : right).at(std::size_t((u.id & ((wc::Id(1) << 20) - 1)) - 1));
                    deployments << fight << ',' << subject.name << ',' << pressure.name << ',' << star << ',' << seed << ',' << subjectSide << ','
                        << u.side << ',' << formation[u.side]->name << ',' << u.id << ',' << d.id << ',' << d.cost << ',' << copies << ',' << d.cost * copies
                        << ',' << owned.cell.column << ',' << owned.cell.row << ',' << u.cell.column << ',' << u.cell.row << ',' << u.initiative << ','
                        << u.maxHealth << ',' << u.basicDamage << ',' << u.armor << ',' << u.resistance << ',' << u.basicBonus << ',' << u.abilityBonus << ','
                        << u.allBonus << ',' << u.rateBonus << ',' << u.supportBonus << ',' << u.movementBonus << '\n';
                    if (u.side == subjectSide && d.id == subject.focus) {
                        if (std::string(subject.trait) == "mage") Require(u.abilityBonus == 4000, "Mage4 focus skill bonus");
                        if (std::string(subject.trait) == "priest") Require(u.supportBonus == 3000, "Priest4 focus source support bonus");
                        if (std::string(subject.trait) == "elf") Require(u.rateBonus == 2000, "Elf4 focus rate bonus");
                        if (std::string(subject.trait) == "rogue") Require(u.rateBonus == 3000, "Rogue4 focus rate bonus");
                    }
                }
                Require(initial.size() == 12, "both full canonical deployments reached actual combat");
                while (!combat.Result().complete) {
                    // State observed at the start of each simulated interval, avoiding fictitious post-death uptime.
                    for (const auto& u : combat.Units()) {
                        if (u.health <= 0) continue;
                        auto& m = measured.at(u.id);
                        ++m.aliveTicks;
                        m.stunTicks += u.state == wc::ActionState::Stunned && u.stunExpiry > combat.CurrentTick();
                        m.movingTicks += u.state == wc::ActionState::Moving;
                        m.shieldTicks += u.shield > 0 && u.shieldExpiry > combat.CurrentTick();
                        bool positive = false, negative = false;
                        for (const auto& modifier : u.modifiers) if (modifier.expiry > combat.CurrentTick()) {
                            positive |= modifier.magnitude > 0; negative |= modifier.magnitude < 0;
                        }
                        m.buffTicks += positive; m.debuffTicks += negative;
                    }
                    combat.Tick();
                    Require(combat.InvariantError().empty(), "per-tick actual combat invariant");
                    Require(combat.CurrentTick() <= (catalog.rules.combatTimeoutMs / catalog.rules.tickMs) + 2, "combat exceeded canonical timeout");
                }
                const auto& result = combat.Result();
                timeouts += result.timeout;
                totalEvents += int(combat.Events().size());
                std::map<wc::Id, wc::Int> nerisDamageTick;
                for (const auto& event : combat.Events()) {
                    Require(initial.count(event.source) && initial.count(event.target), "event has real source and target");
                    const auto& source = initial.at(event.source);
                    const auto& target = initial.at(event.target);
                    const auto& sd = catalog.units[source.definition];
                    const auto& td = catalog.units[target.definition];
                    auto& sm = measured.at(event.source); auto& tm = measured.at(event.target);
                    (event.basicAttack ? sm.basicActions : sm.activeActions).insert(event.action);
                    const int damageBonus = source.allBonus + (event.basicAttack ? source.basicBonus : source.abilityBonus);
                    if (event.effect == wc::Effect::Damage) {
                        Require(event.resolved == wc::ResolveDamage(event.requested, event.damageType, target.armor, target.resistance, damageBonus), "recorded mitigation matches actual source and target snapshot");
                        Require(event.resolved == event.absorbed + event.healthLoss + event.overkill, "damage event conserves shield health and overkill");
                        (event.basicAttack ? sm.basicLoss : sm.skillLoss) += event.healthLoss;
                        sm.overkill += event.overkill; tm.damageIn += event.healthLoss;
                        if (event.absorbed) {
                            Require(measured.count(event.absorbedFrom) == 1, "shield absorption attributes to actual caster");
                            measured.at(event.absorbedFrom).absorbed += event.absorbed;
                        }
                        if (sd.id == "wc_u_elf_mage" && !event.basicAttack) nerisDamageTick[event.action] = event.tick;
                    } else if (event.effect == wc::Effect::Heal) {
                        sm.healing += event.resolved; tm.healedIn += event.resolved;
                    } else if (event.effect == wc::Effect::Shield) sm.shields += event.resolved;
                    else if (event.effect == wc::Effect::Stun) {
                        sm.appliedStunMs += event.resolved;
                        if (sd.id == "wc_u_elf_mage") Require(nerisDamageTick.count(event.action) && nerisDamageTick.at(event.action) == event.tick, "Neris stun follows same-action damage at same tick");
                    } else if (event.effect == wc::Effect::Dash) ++sm.dashEvents;
                    else if (event.effect == wc::Effect::StatModifier) ++sm.statusEvents;
                    events << fight << ',' << event.tick << ',' << event.source << ',' << event.target << ',' << event.action << ',' << sd.id << ',' << td.id << ','
                        << EffectName(event.effect) << ',' << event.basicAttack << ',' << DamageName(event.damageType) << ',' << event.requested << ',' << event.resolved << ','
                        << event.absorbed << ',' << event.healthLoss << ',' << event.overkill << ',' << event.absorbedFrom << ',' << event.cell.column << ',' << event.cell.row << ','
                        << (event.effect == wc::Effect::Damage ? damageBonus : 0) << ',' << target.armor << ',' << target.resistance << '\n';
                }
                const int outcome = result.winner < 0 ? 0 : result.winner == subjectSide ? 1 : -1;
                outcomes << fight << ',' << subject.name << ',' << pressure.name << ',' << star << ',' << seed << ',' << subjectSide << ",6," << 6 * copies << ',' << 12 * copies << ','
                    << result.winner << ',' << outcome << ',' << result.ticks << ',' << result.ticks * catalog.rules.tickMs << ',' << result.timeout << ','
                    << result.survivors[subjectSide] << ',' << result.survivors[1-subjectSide] << ',' << combat.Events().size() << '\n';
                const std::string key = std::string(subject.name) + ',' + pressure.name + ',' + std::to_string(star);
                auto& group = aggregate[key]; ++group.runs; group.wins += outcome > 0; group.losses += outcome < 0; group.draws += outcome == 0;
                group.timeout += result.timeout; group.ticks += result.ticks;
                for (const auto& u : combat.Units()) {
                    const auto& m = measured.at(u.id); const auto& d = catalog.units[u.definition];
                    const bool focus = u.side == subjectSide && d.id == subject.focus;
                    Require(u.health == initial.at(u.id).health + m.healedIn - m.damageIn, "per-unit end health reconciles every actual heal and hit");
                    units << fight << ',' << u.side << ',' << d.id << ',' << u.id << ',' << focus << ',' << (u.health > 0) << ',' << u.health << ',' << u.maxHealth << ','
                        << m.aliveTicks * catalog.rules.tickMs << ',' << m.movingTicks * catalog.rules.tickMs << ',' << m.stunTicks * catalog.rules.tickMs << ','
                        << m.shieldTicks * catalog.rules.tickMs << ',' << m.buffTicks * catalog.rules.tickMs << ',' << m.debuffTicks * catalog.rules.tickMs << ','
                        << m.basicActions.size() << ',' << m.activeActions.size() << ',' << m.basicLoss << ',' << m.skillLoss << ',' << m.healing << ',' << m.shields << ','
                        << m.absorbed << ',' << m.overkill << ',' << m.appliedStunMs << ',' << m.dashEvents << ',' << m.statusEvents << ',' << m.healedIn << ',' << m.damageIn << '\n';
                    if (focus) {
                        group.focusBasicLoss += m.basicLoss; group.focusSkillLoss += m.skillLoss; group.focusHealing += m.healing; group.focusAbsorbed += m.absorbed;
                        group.focusActions += int(m.activeActions.size()); group.focusAppliedStunMs += m.appliedStunMs;
                        group.focusAliveTicks += m.aliveTicks; group.focusDashEvents += m.dashEvents;
                    }
                }
                Require(!combat.Events().empty(), "outcome must contain actual combat events");
            }
        }
        for (const auto& [key, group] : aggregate) {
            Require(group.runs == 8, "each group has four seeds and both sides");
            groups << key << ',' << group.runs << ',' << group.wins << ',' << group.losses << ',' << group.draws << ',' << group.timeout << ','
                << double(group.ticks * catalog.rules.tickMs) / (1000 * group.runs) << ',' << group.focusBasicLoss << ',' << group.focusSkillLoss << ','
                << group.focusHealing << ',' << group.focusAbsorbed << ',' << group.focusActions << ',' << group.focusAppliedStunMs << ','
                << double(group.focusAliveTicks * catalog.rules.tickMs) / (1000 * group.runs) << ',' << group.focusDashEvents << '\n';
        }
        Require(fights == 192 && aggregate.size() == 24, "exact bounded counter matrix completed");
        Flush(deployments); Flush(events); Flush(outcomes); Flush(units); Flush(groups);
        summary << "{\n  \"status\":\"PASS_EXECUTION_NOT_BALANCE_ACCEPTANCE\",\n  \"schema_version\":\"" << catalog.schemaVersion
            << "\",\n  \"balance_version\":\"" << catalog.balanceVersion << "\",\n  \"content_digest\":\"" << catalog.contentDigest
            << "\",\n  \"actual_combats\":" << fights << ",\n  \"assertions\":" << checks << ",\n  \"events\":" << totalEvents << ",\n  \"timeouts\":" << timeouts
            << ",\n  \"seeds\":[1103,2207,3301,4409],\n  \"stars\":[1,2],\n  \"slots_each\":6,\n  \"purchase_gold_each_by_star\":[12,36],\n"
            << "  \"copies_each_by_star\":[6,18],\n  \"numeric_catalog_edits\":false,\n  \"scope\":\"Selected fully assembled six-slot deployments; no shop acquisition, XP, reroll, bot decision, tournament, render, human, or LAN measurement. Both sides use identical canonical rules.\",\n"
            << "  \"measurement_limits\":\"Active actions count distinct resolved-event action IDs, not all commitments. Stun packet milliseconds can overlap; per-target stunned_ms records actual observed intervals. Composition results cannot isolate a single hero or establish population win rates.\"\n}\n";
        summary.flush();
        if (!summary) throw std::runtime_error("summary write failed");
        std::cout << "PASS " << fights << " actual combats " << checks << " assertions " << totalEvents << " events " << timeouts << " timeouts; no balance acceptance\n";
        return 0;
    } catch (const std::exception& error) {
        summary << "{\"status\":\"FAIL\",\"completed_or_started_combats\":" << fights << ",\"assertions_before_failure\":" << checks << "}\n";
        std::cerr << "FAIL " << error.what() << '\n';
        return 1;
    }
}
