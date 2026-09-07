#include "CatalogFixture.h"
#include "Presentation/WCAttackWindow.h"
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>

namespace {
int checks = 0;
void Check(bool value, const char* reason) { ++checks; if (!value) throw std::runtime_error(reason); }
wc::OwnedUnit Owned(wc::Id id, int definition, int column, int row) {
    wc::OwnedUnit unit; unit.id = id; unit.definition = definition; unit.onBoard = true; unit.cell = {column,row}; return unit;
}
int Definition(const wc::Catalog& catalog, const char* id) {
    for (int i=0; i<int(catalog.units.size()); ++i) if (catalog.units[i].id==id) return i;
    throw std::runtime_error("Missing actual catalog definition");
}
void Windows() {
    using namespace wc::presentation;
    const AttackWindows windows{{{0,.25,.65},{.65,.90,1.30}}};
    std::string reason;
    Check(ValidateAttackWindows(windows,1.3,.25,reason),"Two complete authored windows validate");
    for (const auto bad : {AttackWindows{{{0,.26,.65},{.65,.90,1.30}}},
                           AttackWindows{{{0,.25,.70},{.65,.90,1.30}}},
                           AttackWindows{{{0,.25,.65},{.65,.90,1.31}}}})
        Check(!ValidateAttackWindows(bad,1.3,.25,reason),"Wrong release, overlap and overflow rejected");
    Check(SampleAttack(windows,0,0).window==-1,"No fabricated attack before first commitment");
    for (std::uint64_t ordinal=1; ordinal<=24; ++ordinal) {
        const int expected=int((ordinal-1)%2);
        for (double elapsed : {-.1,0.,.249,.25,.3,.65,3.}) {
            const auto pose=SampleAttack(windows,ordinal,elapsed);
            Check(pose.window==expected,"Ordinal chooses correct hand independently of global action ID");
            Check(pose.position>=windows[expected].start && pose.position<=windows[expected].end,"Never crosses into other cut");
            if (elapsed==.25) Check(std::abs(pose.position-windows[expected].release)<1e-9,"Each hand reaches release at250ms");
        }
    }
    AttackClock live;
    live.Update(71,2,101,100,.05,.016);
    const auto recovery=SampleAttack(windows,live.ordinal,live.elapsed);
    Check(recovery.window==1,"Recovery preserves committed ordinal");
    live.Update(71,2,105,100,.05,.016);
    Check(std::abs(SampleAttack(windows,live.ordinal,live.elapsed).position-.90)<1e-9,"Release snapshot aligns left cut");
    AttackClock reconstructed;
    reconstructed.Update(71,2,105,100,.05,.016);
    Check(SampleAttack(windows,reconstructed.ordinal,reconstructed.elapsed).position==SampleAttack(windows,live.ordinal,live.elapsed).position,"Scouting reconstruction matches live ordinal and clock");
    live.Update(71,2,111,100,.05,.016);
    for (int i=0;i<120;++i) live.Update(71,2,111,100,.05,.016);
    Check(live.elapsed<=.60+1e-9,"Missing snapshots extrapolate at most one tick");
    live.Update(155,3,121,120,.05,.016);
    Check(SampleAttack(windows,live.ordinal,live.elapsed).window==0,"Intervening global actions do not break alternation");
    AttackClock restarted;
    restarted.Update(1,1,1,1,.05,0);
    Check(SampleAttack(windows,restarted.ordinal,restarted.elapsed).window==0,"New combat starts at first window");
}
void ActualOrdinals(wc::Catalog catalog) {
    const int sylas=Definition(catalog,"wc_u_elf_rogue");
    const int rowan=Definition(catalog,"wc_u_human_mage");
    const int ada=Definition(catalog,"wc_u_human_guardian");
    const int neris=Definition(catalog,"wc_u_elf_mage");
    // Sustained actual-combat fixture: only HP is enlarged to observe many interrupted cycles.
    for (auto& unit:catalog.units) unit.health*=100;
    wc::Combat combat(catalog,{Owned(1,sylas,3,3),Owned(2,rowan,2,3),Owned(3,ada,4,3),Owned(7,neris,3,2)},
                              {Owned(4,sylas,3,3),Owned(5,rowan,2,3),Owned(6,ada,4,3),Owned(8,neris,3,2)},91823);
    std::map<wc::Id,wc::CombatUnit> previous;
    for (const auto& unit:combat.Units()) { Check(unit.basicAttackOrdinal==0,"Fresh combat ordinal0"); previous[unit.id]=unit; }
    std::map<std::pair<wc::Id,wc::Id>,std::pair<wc::Id,int>> commitments;
    std::set<std::pair<wc::Id,wc::Id>> delivered;
    int basics=0,casts=0,recoveries=0,stuns=0,misleadingParity=0;
    std::ofstream evidence("actual-attack-ordinals.csv");
    evidence<<"tick,unit,action,ordinal,state,release_tick,window\n";
    for (int tick=0;tick<1200&&!combat.Result().complete;++tick) {
        combat.Tick(); Check(combat.InvariantError().empty(),"Actual combat invariant");
        for (const auto& unit:combat.Units()) {
            const auto& old=previous[unit.id];
            if (unit.actionId!=old.actionId && unit.state==wc::ActionState::AttackWindup) {
                ++basics; Check(unit.basicAttackOrdinal==old.basicAttackOrdinal+1,"Exactly one ordinal increment at basic commitment");
                const auto& definition=catalog.Definition(unit.definition,unit.neutral);
                commitments[{unit.id,unit.actionId}]={unit.basicAttackOrdinal,unit.releaseTick+(definition.projectileTravelMs+catalog.rules.tickMs-1)/catalog.rules.tickMs};
                if (int((unit.actionId-1)%2)!=int((unit.basicAttackOrdinal-1)%2)) ++misleadingParity;
                evidence<<combat.CurrentTick()<<','<<unit.id<<','<<unit.actionId<<','<<unit.basicAttackOrdinal<<','<<int(unit.state)<<','<<unit.releaseTick<<','<<(unit.basicAttackOrdinal-1)%2<<'\n';
            } else Check(unit.basicAttackOrdinal==old.basicAttackOrdinal,"Casts, recovery, movement and hit states do not increment ordinal");
            if (unit.actionId!=old.actionId&&unit.state==wc::ActionState::CastWindup) ++casts;
            if (unit.state==wc::ActionState::AttackRecovery&&unit.actionId==old.actionId) ++recoveries;
            if (unit.state==wc::ActionState::Stunned) ++stuns;
            previous[unit.id]=unit;
        }
    }
    for (const auto& event:combat.Events()) if (event.basicAttack) {
        const auto key=std::make_pair(event.source,event.action);
        Check(commitments.count(key)==1,"Each actual basic packet belongs to recorded commitment");
        Check(delivered.insert(key).second,"One actual basic damage event per action, no second cut packet");
        Check(event.tick==commitments[key].second,"Basic packet impact timing remains release plus canonical travel");
    }
    Check(basics>20&&casts>5&&recoveries>20,"Actual fixture exercised interleaved basics, spells and recoveries");
    Check(misleadingParity>0,"Actual interleaving demonstrates global-ID parity is unsuitable");
    Check(stuns>0,"Actual interruption states preserve committed ordinals");
    wc::Combat fresh(catalog,{Owned(1,sylas,3,3)},{Owned(2,ada,3,3)},91823);
    for (const auto& unit:fresh.Units()) Check(unit.basicAttackOrdinal==0,"Fresh/restarted fight resets counter");
    std::cout<<"actual_basics="<<basics<<" casts="<<casts<<" recovery_samples="<<recoveries<<" stun_samples="<<stuns<<" basic_events="<<delivered.size()<<'\n';
}
}
int main() {
    try { Windows(); ActualOrdinals(FixtureCatalog()); std::cout<<"PASS checks="<<checks<<'\n'; return 0; }
    catch(const std::exception& error) { std::cerr<<"FAIL checks="<<checks<<" reason="<<error.what()<<'\n'; return 1; }
}
