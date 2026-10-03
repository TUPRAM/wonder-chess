#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <tuple>

namespace {
int checks = 0;
void Require(bool ok, const char *message) { ++checks; if (!ok) throw std::runtime_error(message); }
const char *Kind(wc::EncounterKind kind) {
    return kind == wc::EncounterKind::Pvp ? "pvp" : kind == wc::EncounterKind::Ghost ? "ghost" : "neutral";
}
struct Activity {
    wc::Int damage = 0, healing = 0, tailDamage = 0, tailHealing = 0;
    int attacks = 0, skillHits = 0, controls = 0, lastDamage = 0;
};
void OutcomeHeader(std::ostream &out) {
    out << "winner,ticks,timeout,deaths,damage_cp,skill_damage_cp,effective_healing_cp,requested_healing_cp,guard_prevented_cp,cocoon_impacts,cocoon_duration_ms,last_5s_damage_cp,last_5s_healing_cp";
}
void Outcome(std::ostream &out, const wc::Combat &combat) {
    wc::Int damage = 0, skills = 0, healing = 0, requested = 0, guard = 0, controlMs = 0, tailDamage = 0, tailHeal = 0;
    int controls = 0, deaths = 0;
    const int tail = combat.CurrentTick() - 100;
    for (const auto &u : combat.Units()) if (!u.health) ++deaths;
    for (const auto &e : combat.Events()) {
        if (e.effect == wc::Effect::Damage) {
            damage += e.healthLoss; guard += e.prevented;
            if (!e.basicAttack) skills += e.healthLoss;
            if (e.tick > tail) tailDamage += e.healthLoss;
        }
        if (e.effect == wc::Effect::Heal) {
            healing += e.resolved; requested += e.requested;
            if (e.tick > tail) tailHeal += e.resolved;
        }
        if (e.mechanic == wc::AbilityMechanic::CocoonProjectile && e.effect == wc::Effect::Stun && e.resolved > 0) {
            ++controls; controlMs += e.resolved;
        }
    }
    const auto &r = combat.Result();
    out << r.winner << ',' << r.ticks << ',' << r.timeout << ',' << deaths << ',' << damage << ',' << skills << ','
        << healing << ',' << requested << ',' << guard << ',' << controls << ',' << controlMs << ',' << tailDamage << ',' << tailHeal;
}
void VerifyReplay(const wc::Combat &actual, const wc::Combat &copy) {
    Require(std::tie(actual.Result().ticks, actual.Result().winner, actual.Result().timeout, actual.Result().survivors) ==
            std::tie(copy.Result().ticks, copy.Result().winner, copy.Result().timeout, copy.Result().survivors), "Diagnostic copy outcome mismatch");
    Require(actual.Events().size() == copy.Events().size(), "Diagnostic copy event count mismatch");
    for (std::size_t i = 0; i < actual.Events().size(); ++i) {
        const auto &a = actual.Events()[i], &b = copy.Events()[i];
        Require(std::tie(a.tick,a.source,a.target,a.action,a.effect,a.requested,a.resolved,a.healthLoss,a.absorbed,a.overkill,a.prevented,a.guardedBy,a.cell.column,a.cell.row,a.mechanic) ==
                std::tie(b.tick,b.source,b.target,b.action,b.effect,b.requested,b.resolved,b.healthLoss,b.absorbed,b.overkill,b.prevented,b.guardedBy,b.cell.column,b.cell.row,b.mechanic), "Diagnostic copy event mismatch");
    }
    Require(actual.Units().size() == copy.Units().size(), "Diagnostic copy unit count mismatch");
    for (std::size_t i = 0; i < actual.Units().size(); ++i) {
        const auto &a = actual.Units()[i], &b = copy.Units()[i];
        Require(std::tie(a.health,a.state,a.cell.column,a.cell.row,a.cocoonExpiry,a.cocoonSource,a.castsCommitted) ==
                std::tie(b.health,b.state,b.cell.column,b.cell.row,b.cocoonExpiry,b.cocoonSource,b.castsCommitted), "Diagnostic copy final-state mismatch");
    }
}
void WriteDetails(const wc::Catalog &catalog, const wc::Combat &combat, std::ostream &units, std::ostream &traces,
                  int seed, int round, int index, wc::EncounterKind kind) {
    std::map<wc::Id, Activity> activity;
    const int tail = combat.CurrentTick() - 100;
    for (const auto &e : combat.Events()) {
        auto &a = activity[e.source];
        if (e.effect == wc::Effect::Damage) {
            a.damage += e.healthLoss;
            if (e.basicAttack) ++a.attacks; else ++a.skillHits;
            if (e.healthLoss > 0) a.lastDamage = e.tick;
            if (e.tick > tail) a.tailDamage += e.healthLoss;
        }
        if (e.effect == wc::Effect::Heal) { a.healing += e.resolved; if (e.tick > tail) a.tailHealing += e.resolved; }
        if (e.mechanic == wc::AbilityMechanic::CocoonProjectile && e.effect == wc::Effect::Stun && e.resolved > 0) ++a.controls;
    }
    std::map<wc::Id, std::string> names;
    for (const auto &u : combat.Units()) {
        const auto &name = catalog.Definition(u.definition,u.neutral).id; names[u.id] = name;
        const auto &a = activity[u.id];
        units << seed << ',' << round << ',' << index << ',' << Kind(kind) << ',' << combat.Result().timeout << ',' << u.id << ','
            << name << ',' << u.side << ',' << u.star << ',' << u.health << ',' << u.maxHealth << ',' << a.damage << ',' << a.healing << ','
            << a.attacks << ',' << a.skillHits << ',' << a.controls << ',' << u.castsCommitted << ',' << u.firstCastTick << ','
            << a.lastDamage << ',' << a.tailDamage << ',' << a.tailHealing << ',' << int(u.state) << ',' << u.cell.column << ',' << u.cell.row << '\n';
    }
    struct Totals { int count = 0, recipients = 0; wc::Int requested = 0, resolved = 0; };
    std::map<std::tuple<std::string,std::string,std::string>,Totals> outcomes;
    for (const auto &t : combat.Diagnostics()) {
        auto &a = outcomes[{names.at(t.source),wc::MechanicPhaseName(t.phase),wc::MechanicReasonName(t.reason)}];
        ++a.count; a.recipients += t.recipients; a.requested += t.requested; a.resolved += t.resolved;
    }
    for (const auto &entry : outcomes) {
        const auto &[hero,phase,reason] = entry.first; const auto &a = entry.second;
        traces << seed << ',' << round << ',' << index << ',' << Kind(kind) << ',' << hero << ',' << phase << ',' << reason << ','
            << a.count << ',' << a.recipients << ',' << a.requested << ',' << a.resolved << '\n';
    }
}
wc::OwnedUnit Unit(wc::Id id, int definition, int x, int y, int star) {
    wc::OwnedUnit u; u.id = id; u.definition = definition; u.cell = {x,y}; u.onBoard = true; u.star = star; return u;
}
void Fixtures(const wc::Catalog &canonical) {
    std::ofstream out("silkmother_formations.csv");
    out << "fixture,skill_enabled,mirror,star,seed,"; OutcomeHeader(out); out << '\n';
    const auto it = std::find_if(canonical.units.begin(),canonical.units.end(),[](const auto &u){return u.id == "wc_vn_silkmother";});
    Require(it != canonical.units.end(), "Current enabled Silkmother missing");
    const int silk = int(it - canonical.units.begin());
    for (int exposed = 0; exposed < 2; ++exposed) for (int mirror = 0; mirror < 2; ++mirror)
        for (int star = 1; star <= 3; ++star) for (int seed = 7001; seed <= 7004; ++seed) for (int enabled = 0; enabled < 2; ++enabled) {
            auto catalog = canonical; catalog.units[silk].ability.enabled = bool(enabled);
            auto a = std::vector<wc::OwnedUnit>{Unit(1,silk,3,exposed?3:1,star),Unit(2,0,3,exposed?1:2,star),Unit(3,1,4,3,star)};
            auto b = std::vector<wc::OwnedUnit>{Unit(4,0,4,3,star),Unit(5,2,4,1,star),Unit(6,1,3,3,star)};
            if (mirror) std::swap(a,b);
            wc::Combat c(catalog,a,b,seed);
            while (!c.Result().complete) { c.Tick(); Require(c.InvariantError().empty(), "Silkmother formation invariant"); }
            out << (exposed?"exposed":"protected") << ',' << enabled << ',' << mirror << ',' << star << ',' << seed << ',';
            Outcome(out,c); out << '\n';
        }
}
}
int main(int argc, char **argv) {
    try {
        const int count = argc > 1 ? std::stoi(argv[1]) : 25, first = argc > 2 ? std::stoi(argv[2]) : 7001;
        Require(count >= 1 && count <= 50 && first >= 1 && first + count - 1 <= 10000, "Bounded development interval required");
        const auto catalog = wcvnext::WonderVNextCatalog();
        Require(catalog.Validate().empty(), "Current canonical runtime catalogue invalid");
        Fixtures(catalog);
        std::ofstream tournaments("tournaments.csv"), encounters("encounters.csv"), units("unit_activity.csv"), traces("mechanic_outcomes.csv");
        tournaments << "seed,rounds,capped,simulated_ms,preparation_ms,combat_ms,settlement_ms,encounters,timeouts,command_rejects\n";
        encounters << "seed,round,index,kind,"; OutcomeHeader(encounters); encounters << '\n';
        units << "seed,round,index,kind,timeout,unit_id,hero,side,star,final_health_cp,max_health_cp,damage_cp,healing_cp,basic_hits,skill_damage_hits,cocoon_impacts,casts_committed,first_cast_tick,last_damage_tick,last_5s_damage_cp,last_5s_healing_cp,final_state,column,row\n";
        traces << "seed,round,index,kind,hero,phase,reason,count,recipients,requested_cp,resolved\n";
        for (int seed = first; seed < first + count; ++seed) {
            wc::Match match(catalog,seed,0); std::array<int,3> phaseMs{}; std::vector<wc::Combat> copies;
            int fights = 0, timeouts = 0, ticks = 0;
            while (match.CurrentPhase() != wc::Phase::Finished && match.CurrentPhase() != wc::Phase::Aborted) {
                Require(++ticks <= 200000, "Tournament tick safety bound exceeded");
                const auto before = match.CurrentPhase(); const int elapsed = match.ElapsedMs();
                match.Tick(catalog.rules.tickMs); phaseMs.at(int(before)) += match.ElapsedMs() - elapsed;
                if (ticks % 20 == 0 || before != match.CurrentPhase()) Require(match.InvariantError().empty(), "Tournament invariant");
                if (before == wc::Phase::Preparation && match.CurrentPhase() == wc::Phase::Combat) {
                    copies.clear(); for (const auto &encounter : match.Encounters()) {
                        copies.push_back(encounter.combat); Require(copies.back().EnableDiagnostics(), "Diagnostic copy did not begin at tick zero");
                    }
                }
                if (before != wc::Phase::Combat || match.CurrentPhase() == wc::Phase::Combat) continue;
                for (int index = 0; index < int(match.Encounters().size()); ++index) {
                    const auto &encounter = match.Encounters()[index]; auto &copy = copies.at(index);
                    while (!copy.Result().complete) { copy.Tick(); Require(copy.InvariantError().empty(), "Diagnostic combat invariant"); }
                    VerifyReplay(encounter.combat,copy);
                    encounters << seed << ',' << match.Round() << ',' << index << ',' << Kind(encounter.kind) << ',';
                    Outcome(encounters,copy); encounters << '\n';
                    WriteDetails(catalog,copy,units,traces,seed,match.Round(),index,encounter.kind);
                    ++fights; if (copy.Result().timeout) ++timeouts;
                }
            }
            Require(match.CurrentPhase() == wc::Phase::Finished, "Tournament aborted");
            Require(phaseMs[0]+phaseMs[1]+phaseMs[2] == match.ElapsedMs(), "Tournament phase accounting mismatch");
            int rejects = 0; for (const auto &decision : match.BotLog()) if (!decision.reply.accepted) ++rejects;
            Require(rejects == 0, "Actual bot command rejected");
            tournaments << seed << ',' << match.Round() << ',' << match.Capped() << ',' << match.ElapsedMs() << ',' << phaseMs[0] << ','
                << phaseMs[1] << ',' << phaseMs[2] << ',' << fights << ',' << timeouts << ',' << rejects << '\n';
            tournaments.flush(); encounters.flush(); units.flush(); traces.flush();
            if ((seed-first+1)%5 == 0) std::cout << "Completed current seven-hero diagnostic seed " << seed << " (" << seed-first+1 << '/' << count << ")\n";
        }
        std::ofstream identity("identity.json");
        identity << "{\"profile\":\"" << catalog.profileId << "\",\"balance_version\":\"" << catalog.balanceVersion << "\",\"catalog_digest\":\""
            << catalog.contentDigest << "\",\"enabled_heroes\":" << catalog.units.size() << ",\"checks\":" << checks
            << ",\"human_pacing\":\"NOT_RUN\",\"balance_promotion\":\"NONE\"}\n";
        std::cout << "PASS " << checks << " current-candidate native diagnostic checks; " << count << " actual tournaments, diagnostic copies reconciled, 96 isolated formation/control fixtures. No human pacing or balance acceptance.\n";
        return 0;
    } catch (const std::exception &e) { std::cerr << "FAIL after " << checks << " checks: " << e.what() << '\n'; return 1; }
}
