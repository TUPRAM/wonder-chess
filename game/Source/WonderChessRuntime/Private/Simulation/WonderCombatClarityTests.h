#pragma once
#include "VNext/WonderVNextCatalog.generated.h"
#include <stdexcept>
#include <map>
#include <tuple>

namespace wctest
{
inline wc::Catalog StatusCueCatalog(const wc::Catalog& base)
{
    auto c=base;
    for(auto& u:c.units){u.ability.enabled=false;u.attackDamage=0;u.range=8;u.attackRate=1000;u.projectileTravelMs=0;}
    auto& a=c.units[0].ability;a={};a.id="synthetic_status_cues";a.name="Status effect demonstration";
    a.enabled=true;a.selector=wc::Selector::CurrentEnemy;a.range=8;a.maxTargets=1;
    a.firstCastMs=1000;a.castMs=150;a.recoveryMs=300;a.cooldownMs=60000;
    a.effects={{wc::Effect::Damage,wc::DamageType::True,0,{5000,5000,5000}},
               {wc::Effect::Heal,wc::DamageType::True,0,{2500,2500,2500}},
               {wc::Effect::Shield,wc::DamageType::True,4000,{2000,2000,2000}},
               {wc::Effect::Stun,wc::DamageType::True,4000,{0,0,0}},
               {wc::Effect::StatModifier,wc::DamageType::True,4000,{-1000,-1000,-1000}}};
    return c;
}

inline int RunCombatClarityChecks()
{
    int checks=0;
    const auto requireClarity=[&](bool ok,const char* message){++checks;if(!ok)throw std::runtime_error(message);};
    const auto unit=[](wc::Id id,int def,int x,int y){wc::OwnedUnit u;u.id=id;u.definition=def;u.onBoard=true;u.cell={x,y};return u;};
    const auto quiet=[](bool mobile){auto c=wcvnext::WonderVNextCombatClarityCatalog(mobile);for(auto& u:c.units){u.ability.enabled=false;u.attackDamage=0;u.health=100000;u.range=8;u.attackRate=1000;u.attackWindupMs=50;u.projectileTravelMs=0;u.armor=u.resistance=0;}return c;};
    const auto base=wcvnext::WonderVNextMana20Catalog(),candidate=wcvnext::WonderVNextCombatClarityCatalog();
    requireClarity(!base.rules.nearestReachableTarget&&!base.rules.mobileAttackRecovery,"Mana20 control retains both old rules");
    requireClarity(candidate.Validate().empty()&&candidate.contentDigest!=base.contentDigest,"Clarity identity validates and separates saves");
    for(int seed=1;seed<=32;++seed){
        auto c=quiet(true);
        wc::Combat f(c,{unit(1,0,3,3)},{unit(2,1,4,3),unit(3,1,0,0)},seed);
        f.Tick();const auto& source=f.Units()[0];const int chosen=source.target;
        requireClarity(f.Units()[source.target].cell==wc::Cell{3,4},"Nearest ranged target wins over initiative among in-range enemies");
        for(int n=0;n<60;++n){f.Tick();requireClarity(f.InvariantError().empty(),"Clarity combat preserves invariants");}
        requireClarity(f.Units()[0].target==chosen,"In-range engagement remains stable");
    }
    {
        auto c=quiet(true);
        wc::Combat f(c,{unit(1,0,1,3),unit(2,0,6,3)},{unit(3,1,6,3),unit(4,1,1,3)},17);
        f.Tick();f.Tick();
        std::map<int,int> hits;
        for(const auto& e:f.Events())if(e.basicAttack)++hits[e.tick];
        requireClarity(hits[2]==4,"Four independent basic attacks release on the same tick");
    }
    {
        auto moving=quiet(true);moving.units[0].range=1;moving.units[0].attackRate=250;moving.units[0].attackDamage=2000;
        moving.units[2].health=1000;
        auto stationary=moving;stationary.rules.mobileAttackRecovery=false;
        const std::vector<wc::OwnedUnit> a{unit(1,0,3,3)},b{unit(2,2,4,3),unit(3,1,0,0)};
        wc::Combat fast(moving,a,b,42),control(stationary,a,b,42);
        fast.Tick();control.Tick();fast.Tick();control.Tick();
        requireClarity(fast.Units()[0].state==wc::ActionState::Moving,"Defeated target permits movement immediately after release");
        requireClarity(control.Units()[0].state==wc::ActionState::AttackRecovery,"Recovery-only comparison waits in place");
        int previous=-10000;
        for(int i=0;i<240&&!fast.Result().complete;++i){fast.Tick();requireClarity(fast.InvariantError().empty(),"Moving recovery preserves reservations");}
        for(const auto& e:fast.Events())if(e.source==fast.Units()[0].id&&e.basicAttack){
            requireClarity(e.tick-previous>=80,"Movement never bypasses the original four-second attack interval");previous=e.tick;
        }
    }
    {
        auto c=StatusCueCatalog(candidate);
        wc::Combat f(c,{unit(1,0,3,3)},{unit(2,1,4,3)},12);
        bool stunned=false,shielded=false,healed=false,modified=false;
        for(int n=0;n<160;++n){
            f.Tick();requireClarity(f.InvariantError().empty(),"Synthetic status effects preserve combat invariants");
            for(const auto& u:f.Units()){stunned|=u.state==wc::ActionState::Stunned;shielded|=u.shield>0;modified|=!u.modifiers.empty();}
        }
        for(const auto& e:f.Events())healed|=e.effect==wc::Effect::Heal&&e.resolved==2500;
        requireClarity(stunned&&shielded&&healed&&modified,"Status demo exercises actual stun, shield, effective heal and modifier");
        for(const auto& u:f.Units())requireClarity(u.state!=wc::ActionState::Stunned&&u.shield==0&&u.modifiers.empty(),"Temporary status cues expire with authoritative states");
    }
    {
        const std::vector<wc::OwnedUnit> a{unit(1,0,3,3),unit(2,3,1,2),unit(3,4,5,1)},b{unit(4,1,3,3),unit(5,2,1,2),unit(6,5,5,1)};
        wc::Combat observed(base,a,b,91),unobserved(base,a,b,91);
        while(!observed.Result().complete){
            observed.Tick();unobserved.Tick();
            for(int i=0;i<3;++i)(void)observed.VisualActions();
            requireClarity(observed.InvariantError().empty(),"Visual observation preserves invariants");
        }
        requireClarity(observed.Events().size()==unobserved.Events().size(),"Repeated presentation reads do not add events");
        for(std::size_t i=0;i<observed.Events().size();++i){const auto& a0=observed.Events()[i];const auto& b0=unobserved.Events()[i];
            requireClarity(std::tie(a0.tick,a0.source,a0.target,a0.action,a0.resolved,a0.healthLoss)==std::tie(b0.tick,b0.source,b0.target,b0.action,b0.resolved,b0.healthLoss),"Visual observation preserves every combat event");}
    }
    return checks;
}
}
