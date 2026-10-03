#pragma once
#define main RunPreservedNativeCombatContracts
#include "../../tests/runtime/vnext_combat_tests.cpp"
#undef main
#include <fstream>
#include <map>
#include <set>

namespace cocoonstudy {
#ifdef WC_COCOON_RESERVATION_EXPERIMENT
constexpr bool Experiment = true;
#else
constexpr bool Experiment = false;
#endif
inline int contractChecks = 0, fixtureIndex = 0;
inline void Verify(bool ok, const char *message) {
    ++contractChecks; if (!ok) throw std::runtime_error(message);
}
inline wc::OwnedUnit Make(wc::Id id, int definition, int x, int y) {
    wc::OwnedUnit u; u.id=id; u.definition=definition; u.cell={x,y}; u.onBoard=true; return u;
}
inline void DumpContract(const char *name, const wc::Combat &combat, int mirror) {
    const std::string prefix=std::string(name)+"-mirror-"+std::to_string(mirror);
    std::ofstream traces(prefix+"-traces.csv"),events(prefix+"-events.csv"),units(prefix+"-units.csv");
    traces << "tick,source,target,action,phase,reason\n";
    for(const auto &t:combat.Diagnostics())traces << t.tick << ',' << t.source << ',' << t.target << ',' << t.action << ',' << wc::MechanicPhaseName(t.phase) << ',' << wc::MechanicReasonName(t.reason) << '\n';
    events << "tick,source,target,mechanic,effect,resolved,health_loss\n";
    for(const auto &e:combat.Events())events << e.tick << ',' << e.source << ',' << e.target << ',' << int(e.mechanic) << ',' << int(e.effect) << ',' << e.resolved << ',' << e.healthLoss << '\n';
    units << "id,definition,health,state,casts,target,stun_expiry,cocoon_expiry,cooldown\n";
    for(const auto &u:combat.Units())units << u.id << ',' << u.definition << ',' << u.health << ',' << int(u.state) << ',' << u.castsCommitted << ',' << u.target << ',' << u.stunExpiry << ',' << u.cocoonExpiry << ',' << u.cooldownTick << '\n';
}
inline void RunContracts(const wc::Catalog &canonical) {
    Verify(RunPreservedNativeCombatContracts()==0, "Preserved canonical mechanics/mana/clarity native contracts failed");
    const int preservedAssertions=assertions;
    const auto found = std::find_if(canonical.units.begin(),canonical.units.end(),[](const auto &u){return u.id=="wc_vn_silkmother";});
    Verify(found!=canonical.units.end(), "Reservation fixture requires enabled Silkmother");
    const int silk=int(found-canonical.units.begin());
    for(int mirror=0;mirror<2;++mirror) {
        auto catalog=Quiet();
        auto &web=catalog.units[silk].ability;
        web=found->ability; web.firstCastMs=0; web.castMs=50; web.travelMs=200; web.cooldownMs=60000;
        for(auto &u:catalog.units)u.attackRate=20000;
        const auto formation=std::vector<wc::OwnedUnit>{Make(1,silk,3,3),Make(4,silk,3,2)};
        const auto enemy=std::vector<wc::OwnedUnit>{Make(2,0,4,3)};
        auto fight=[&](const std::vector<wc::OwnedUnit> &a,const std::vector<wc::OwnedUnit> &b){return mirror?wc::Combat(catalog,b,a,7011):wc::Combat(catalog,a,b,7011);};
        auto one=fight(formation,enemy); Ticks(one,2);
        int commits=0, unspent=0;
        for(const auto &u:one.Units())if(u.definition==silk) {
            commits+=u.castsCommitted;
            if(u.castsCommitted==0 && u.cooldownTick==0 && u.basicAttackOrdinal>0)++unspent;
        }
        Verify(commits==(Experiment?1:2), "Single-target allied reservation commitment count mismatch");
        Verify(!Experiment || unspent==1, "Reserved-target rejection must preserve cooldown and ordinary basic opportunities");
        Ticks(one,8);
        auto impacts=Events(one,wc::AbilityMechanic::CocoonProjectile,wc::Effect::Stun);
        Verify(std::count_if(impacts.begin(),impacts.end(),[](const auto &e){return e.resolved>0;})==1,
               "Single-target reservation must retain damage-free non-stacking control");
        const auto enemies=std::vector<wc::OwnedUnit>{Make(2,0,4,3),Make(3,0,1,2)};
        auto two=fight(formation,enemies); Ticks(two,2);
        std::set<wc::Id> selected; commits=0;
        for(const auto &t:two.VisualActions())if(t.mechanic==wc::AbilityMechanic::CocoonProjectile && t.released)selected.insert(t.target);
        for(const auto &u:two.Units())if(u.definition==silk)commits+=u.castsCommitted;
        Verify(commits==2 && (!Experiment || selected.size()==2), "Two-target reservation must use two distinct legal recipients");
        auto opposing=fight({Make(1,silk,3,3)}, {Make(2,silk,4,3)}); Ticks(opposing,2);
        commits=0; for(const auto &u:opposing.Units())commits+=u.castsCommitted;
        Verify(commits==2, "Hostile cocoon commitments must not reserve an ally's target");

        // A generic stun cancels the first weaving commitment before the second becomes ready.
        web.castMs=500;
        auto &second=catalog.units[1].ability; second=web; second.firstCastMs=200; second.castMs=50;
        catalog.units[1].attackRate=10000;
        auto &interrupt=catalog.units[0].ability; interrupt={}; interrupt.id="reservation_interrupt";
        interrupt.effect=wc::Effect::Stun; interrupt.selector=wc::Selector::HighestAttackRateEnemy;
        interrupt.range=8; interrupt.maxTargets=1; interrupt.firstCastMs=100; interrupt.castMs=50;
        interrupt.durationMs=2000; interrupt.cooldownMs=60000;
        auto cancelled=fight({Make(1,silk,3,3),Make(4,1,3,2)},enemy);
        // The unreserved caster may already have started an ordinary basic when
        // the first windup is interrupted; allow its real minimum attack recovery
        // to finish before requiring the next legal ability decision/impact.
        Verify(cancelled.EnableDiagnostics(), "Interruption fixture diagnostic start mismatch"); Ticks(cancelled,24);
        DumpContract("interrupted-reservation",cancelled,mirror);
        impacts=Events(cancelled,wc::AbilityMechanic::CocoonProjectile,wc::Effect::Stun);
        Verify(HasTrace(cancelled,wc::MechanicPhase::Cancelled,wc::MechanicReason::SourceStunned) &&
               std::any_of(impacts.begin(),impacts.end(),[](const auto &e){return (e.source&((wc::Id(1)<<20)-1))==4 && e.resolved>0;}),
               "Interrupted windup must release its reservation for another allied caster");

        // An already released web continues to reserve its target after its caster is killed.
        web.castMs=50; web.travelMs=1000; second=web; second.firstCastMs=200;
        interrupt.effect=wc::Effect::Damage; interrupt.magnitude={2000000,2000000,2000000};
        auto dead=fight({Make(1,silk,3,3),Make(4,1,3,2)},enemy); Ticks(dead,30);
        const auto caster=std::find_if(dead.Units().begin(),dead.Units().end(),[](const auto &u){return (u.id&((wc::Id(1)<<20)-1))==1;});
        const auto later=std::find_if(dead.Units().begin(),dead.Units().end(),[](const auto &u){return (u.id&((wc::Id(1)<<20)-1))==4;});
        Verify(caster!=dead.Units().end() && caster->health==0, "Released-caster defeat fixture did not execute");
        Verify(later!=dead.Units().end() && later->castsCommitted==(Experiment?0:1),
               "Released packet reservation must survive caster defeat until impact");
        impacts=Events(dead,wc::AbilityMechanic::CocoonProjectile,wc::Effect::Stun);
        Verify(std::count_if(impacts.begin(),impacts.end(),[](const auto &e){return e.resolved>0;})==1 &&
               std::all_of(impacts.begin(),impacts.end(),[](const auto &e){return e.healthLoss==0;}),
               "Released web still lands once without creating skill damage");
    }
    std::ofstream out("reservation_contracts.json");
    out << "{\"variant\":\"" << (Experiment?"cocoon_reservation":"baseline") << "\",\"focused_checks\":" << contractChecks
        << ",\"preserved_native_assertions\":" << preservedAssertions << ",\"focused_fixture_tick_assertions\":" << assertions-preservedAssertions
        << ",\"status\":\"PASS\",\"canonical_timing_changed\":false}\n";
    std::cout << "PASS " << contractChecks << " focused reservation lifecycle checks, both orientations.\n";
}
inline void Observe(const wc::Combat &combat,const wc::Catalog &catalog,const char *context,int seed,int round,int index,
                    const char *layout,int enabled,int mirror,int star) {
    static std::ofstream intervals("cocoon_intervals.csv"), fixtureUnits("fixture_unit_activity.csv");
    static bool headers=false;
    if(!headers) {
        intervals << "context,seed,round,index,layout,skill_enabled,mirror,star,source,target,source_side,target_hero,silkmothers_on_source_side,silkmothers_in_encounter,impact_tick,release_tick,scheduled_end_tick,observed_end_tick,applied_duration_ms,observed_control_ms,previous_same_target_end_tick,gap_ms,target_damage_during_cp,target_healing_during_cp,all_damage_during_cp,all_healing_during_cp,source_basic_hits_in_gap,source_damage_in_gap_cp\n";
        fixtureUnits << "layout,skill_enabled,mirror,star,seed,unit_id,hero,side,final_health_cp,basic_hits,damage_cp,healing_cp,casts_committed,cocoon_impacts\n";
        headers=true;
    }
    std::map<wc::Id,const wc::CombatUnit*> definitions;
    std::map<wc::Id,wc::Int> health;
    std::map<wc::Id,int> death;
    std::array<int,2> sideSilks{};
    struct Counts { int basics=0,controls=0; wc::Int damage=0,healing=0; };
    std::map<wc::Id,Counts> counts;
    for(const auto &u:combat.Units()) {
        definitions[u.id]=&u; health[u.id]=u.maxHealth;
        if(!u.neutral && catalog.units[u.definition].id=="wc_vn_silkmother")++sideSilks[u.side];
    }
    for(const auto &e:combat.Events()) {
        auto &a=counts[e.source];
        if(e.effect==wc::Effect::Damage) { a.damage+=e.healthLoss; if(e.basicAttack)++a.basics; health[e.target]-=e.healthLoss;
            if(health[e.target]==0 && !death.count(e.target))death[e.target]=e.tick; }
        if(e.effect==wc::Effect::Heal) { a.healing+=e.resolved; health[e.target]+=e.resolved; }
        if(e.mechanic==wc::AbilityMechanic::CocoonProjectile && e.effect==wc::Effect::Stun && e.resolved>0)++a.controls;
    }
    std::map<std::pair<wc::Id,wc::Id>,int> previous;
    for(const auto &e:combat.Events()) {
        if(e.mechanic!=wc::AbilityMechanic::CocoonProjectile || e.effect!=wc::Effect::Stun || e.resolved<=0)continue;
        const auto &source=*definitions.at(e.source),&target=*definitions.at(e.target);
        const int scheduled=e.tick+int(e.resolved)/catalog.rules.tickMs;
        const int end=std::min({scheduled,death.count(e.target)?death.at(e.target):scheduled,combat.CurrentTick()+1});
        int release=-1; for(const auto &t:combat.Diagnostics())if(t.source==e.source && t.action==e.action && t.phase==wc::MechanicPhase::Released)release=t.tick;
        const auto key=std::make_pair(e.source,e.target); const int last=previous.count(key)?previous.at(key):-1;
        wc::Int targetDamage=0,targetHeal=0,damage=0,healing=0,gapDamage=0; int gapBasics=0;
        for(const auto &event:combat.Events()) {
            if(event.tick>=e.tick && event.tick<end) {
                if(event.effect==wc::Effect::Damage) { damage+=event.healthLoss; if(event.target==e.target)targetDamage+=event.healthLoss; }
                if(event.effect==wc::Effect::Heal) { healing+=event.resolved; if(event.target==e.target)targetHeal+=event.resolved; }
            }
            if(last>=0 && event.tick>=last && event.tick<e.tick && event.source==e.source && event.effect==wc::Effect::Damage) {
                gapDamage+=event.healthLoss; if(event.basicAttack)++gapBasics;
            }
        }
        intervals << context << ',' << seed << ',' << round << ',' << index << ',' << layout << ',' << enabled << ',' << mirror << ',' << star << ','
            << e.source << ',' << e.target << ',' << source.side << ',' << catalog.Definition(target.definition,target.neutral).id << ','
            << sideSilks[source.side] << ',' << sideSilks[0]+sideSilks[1] << ',' << e.tick << ',' << release << ',' << scheduled << ',' << end << ','
            << e.resolved << ',' << std::max(0,end-e.tick)*catalog.rules.tickMs << ',' << last << ',' << (last<0?-1:(e.tick-last)*catalog.rules.tickMs) << ','
            << targetDamage << ',' << targetHeal << ',' << damage << ',' << healing << ',' << gapBasics << ',' << gapDamage << '\n';
        previous[key]=end;
    }
    if(std::string(context)=="fixture")for(const auto &u:combat.Units()) {
        const auto &a=counts[u.id];
        fixtureUnits << layout << ',' << enabled << ',' << mirror << ',' << star << ',' << seed << ',' << u.id << ','
            << catalog.Definition(u.definition,u.neutral).id << ',' << u.side << ',' << u.health << ',' << a.basics << ',' << a.damage << ','
            << a.healing << ',' << u.castsCommitted << ',' << a.controls << '\n';
    }
}
}
