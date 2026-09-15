#pragma once
#include "VNext/WonderVNextCatalog.generated.h"
#include <stdexcept>
#include <tuple>

namespace wctest
{
inline int RunManaContractChecks()
{
    int checks = 0;
    const auto requireMana = [&](bool value, const char* message) { ++checks; if (!value) throw std::runtime_error(std::string(message)+" (mana check "+std::to_string(checks)+")"); };
    const auto base = wcvnext::WonderVNextCatalog();
    const auto mana = wcvnext::WonderVNextManaCatalog();
    const auto mana20 = wcvnext::WonderVNextMana20Catalog();
    requireMana(mana20.Validate().empty() && mana20.contentDigest!=mana.contentDigest && mana20.balanceVersion!=mana.balanceVersion,"Mana20 has a valid distinct experiment identity");
    requireMana(base.Validate().empty() && mana.Validate().empty(), "Both activation variants validate");
    requireMana(base.contentDigest != mana.contentDigest && base.balanceVersion != mana.balanceVersion, "Experiment identity isolates saves and replay");
    for (int i = 0; i < 6; ++i)
    {
        const auto& a=base.units[i]; const auto& b=mana.units[i];
        requireMana(base.units[i].ability.mana.maximum == 0, "Default control has no mana");
        requireMana(b.ability.mana.maximum == (i >= 3 ? 10000 : 0), "Only the three named heroes use mana");
        requireMana(std::tie(a.cost,a.health,a.attackDamage,a.attackRate,a.range,a.armor,a.resistance,a.movementRate) ==
              std::tie(b.cost,b.health,b.attackDamage,b.attackRate,b.range,b.armor,b.resistance,b.movementRate), "Mana does not alter stats or prices");
        requireMana(std::tie(a.ability.mechanic,a.ability.selector,a.ability.magnitude,a.ability.range,a.ability.radius,a.ability.castMs,a.ability.recoveryMs) ==
              std::tie(b.ability.mechanic,b.ability.selector,b.ability.magnitude,b.ability.range,b.ability.radius,b.ability.castMs,b.ability.recoveryMs), "Mana preserves effect, targeting and commitment");
    }
    const auto unit=[](wc::Id id,int definition,int x,int y) { wc::OwnedUnit u;u.id=id;u.definition=definition;u.onBoard=true;u.cell={x,y};return u; };
    const auto quiet=[&](int hero) {
        auto c=mana;
        for(auto& u:c.units){u.health=1000000;u.attackDamage=0;u.range=8;u.armor=u.resistance=0;u.attackRate=1000;u.attackWindupMs=50;u.projectileTravelMs=0;u.ability.enabled=false;u.ability.mana={};}
        c.units[hero].ability=mana.units[hero].ability;
        return c;
    };
    const auto tick=[&](wc::Combat& combat,int n){for(int i=0;i<n&&!combat.Result().complete;++i){combat.Tick();requireMana(combat.InvariantError().empty(),"Mana ledger and occupancy hold every tick");}};
    const auto find=[](const wc::Combat& combat,wc::Id id)->const wc::CombatUnit& {for(const auto& u:combat.Units())if(u.id==id)return u;throw std::runtime_error("Missing fixture unit");};
    for(int i=0;i<6;++i){
        const auto& a=mana.units[i];const auto& b=mana20.units[i];
        const auto& x=a.ability.mana;const auto& y=b.ability.mana;
        requireMana(y.basicAttackGain==(i>=3?2000:0),"Only the three mana users receive20 per basic hit");
        requireMana(std::tie(x.maximum,x.starting,x.damageGainAtFullHealth,x.damageEventCap,x.damageWindowCap,x.damageWindowMs,x.gainDivisorBp)==
                    std::tie(y.maximum,y.starting,y.damageGainAtFullHealth,y.damageEventCap,y.damageWindowCap,y.damageWindowMs,y.gainDivisorBp),"All other mana rules remain equal");
        requireMana(std::tie(a.cost,a.health,a.attackDamage,a.attackRate,a.range,a.armor,a.resistance,a.movementRate)==
                    std::tie(b.cost,b.health,b.attackDamage,b.attackRate,b.range,b.armor,b.resistance,b.movementRate),"Mana20 preserves stats and purchase prices");
        requireMana(std::tie(a.ability.mechanic,a.ability.selector,a.ability.magnitude,a.ability.range,a.ability.radius,a.ability.castMs,a.ability.recoveryMs)==
                    std::tie(b.ability.mechanic,b.ability.selector,b.ability.magnitude,b.ability.range,b.ability.radius,b.ability.castMs,b.ability.recoveryMs),"Mana20 preserves effects and targeting");
    }
    {
        auto c=quiet(3);c.units[3].ability=mana20.units[3].ability;c.units[3].attackDamage=100;
        wc::Combat fight(c,{unit(1,3,3,3)},{unit(2,0,4,3)},41);tick(fight,81);
        requireMana(find(fight,1).mana==8000&&find(fight,1).castsCommitted==0,"Four landed basics leave80 mana and no cast");
        tick(fight,1);
        requireMana(find(fight,1).mana==10000&&find(fight,1).manaFromAttacks==10000,"Fifth landed basic fills100 mana");
        tick(fight,25);
        requireMana(find(fight,1).castsCommitted==1&&find(fight,1).manaSpent==10000&&find(fight,1).manaFromDamage==0,"Five attacks cause one real cast without incoming mana");
        requireMana(find(fight,1).firstCastTick>=80&&find(fight,1).firstCastTick<110,"Attack driven first cast advances with20 gain");
    }
    // Ten actual landed basics trigger a cast, with no initial timer or old cooldown prerequisite.
    {
        auto c=quiet(3);c.units[3].attackDamage=100;
        wc::Combat fight(c,{unit(1,3,3,3)},{unit(2,0,4,3)},41);
        tick(fight,182);
        const auto& u=find(fight,1);
        requireMana(u.manaFromAttacks==10000&&u.manaFromDamage==0,"Exactly ten landed basics earn 100 mana");
        tick(fight,25);
        requireMana(find(fight,1).castsCommitted==1&&find(fight,1).manaSpent==10000,"100 mana is spent once on an automatic cast");
        requireMana(find(fight,1).firstCastTick>=180,"Zero start prevents a free opening cast");
        wc::Combat reset(c,{unit(1,3,3,3)},{unit(2,0,4,3)},41);
        requireMana(find(reset,1).mana==0&&find(reset,1).castsCommitted==0,"New encounter resets mana and activity");
    }
    // Incoming gain follows post-mitigation HP loss, not attack count, raw damage or overkill.
    {
        auto c=quiet(4);c.units[0].attackDamage=200000;c.units[4].armor=100;
        wc::Combat fight(c,{unit(1,4,3,3)},{unit(2,0,4,3)},42);tick(fight,2);
        requireMana(find(fight,1).health==900000&&find(fight,1).mana==1000,"Losing ten percent actual HP earns ten mana");
        c.units[0].attackDamage=500000;
        wc::Combat capped(c,{unit(1,4,3,3)},{unit(2,0,4,3)},42);tick(capped,2);
        requireMana(find(capped,1).mana==2000,"Incoming per-event cap applies after mitigation");
        c.units[4].ability.mana.starting=7000;c.units[0].attackDamage=2000000;
        wc::Combat lethal(c,{unit(1,4,3,3)},{unit(2,0,4,3)},42);tick(lethal,2);
        requireMana(find(lethal,1).mana==0&&find(lethal,1).manaOnDeath==7000&&find(lethal,1).manaFromDamage==0,"Death clears held mana and grants none for lethal damage");
    }
    {
        auto c=quiet(5);c.units[5].health=10000000;c.units[0].attackDamage=2000000;
        wc::Combat fight(c,{unit(1,5,3,3)},{unit(2,0,4,3),unit(3,0,3,3),unit(4,0,2,3)},43);tick(fight,2);
        requireMana(find(fight,1).mana==4000,"Three incoming twenty-mana events obey the forty-mana window cap");
    }
    // Full mana and blocked facing keep the resource; no target/space is fabricated.
    {
        auto c=quiet(5);c.units[5].ability.mana.starting=10000;
        wc::Combat fight(c,{unit(1,5,1,3)},{unit(2,0,5,3)},44);tick(fight,80);
        requireMana(find(fight,1).mana==10000&&find(fight,1).castsCommitted==0&&find(fight,1).manaBlockedAttempts>0,"Full mana is held for an empty facing lane");
    }
    // Commitment spends before a stun; delayed release cannot refund or gain through recovery.
    {
        auto c=quiet(4);c.units[4].ability.mana.starting=10000;
        auto& stun=c.units[0].ability;stun.enabled=true;stun.mechanic=wc::AbilityMechanic::Standard;stun.effect=wc::Effect::Stun;
        stun.selector=wc::Selector::CurrentEnemy;stun.firstCastMs=0;stun.castMs=50;stun.cooldownMs=60000;stun.range=8;stun.durationMs=1000;
        wc::Combat fight(c,{unit(1,4,3,3)},{unit(2,0,4,3)},45);tick(fight,8);
        requireMana(find(fight,1).castsCommitted==1&&find(fight,1).mana==0&&find(fight,1).manaSpent==10000,"Interrupted commitment does not refund mana");
        requireMana(find(fight,1).state==wc::ActionState::Stunned,"Actual hostile stun interrupts the cast");
        for(const auto& e:fight.Events())requireMana(e.mechanic!=wc::AbilityMechanic::CrossingBeams,"Unreleased interrupted beams do not hit");
    }
    // A multi-target spell gives no outgoing mana; incoming damage during its cast/recovery is paused.
    {
        auto c=quiet(4);c.units[4].ability.mana.starting=10000;c.units[0].attackDamage=100000;
        wc::Combat fight(c,{unit(1,4,3,3)},{unit(2,0,4,3),unit(3,0,3,3)},46);tick(fight,25);
        requireMana(find(fight,1).manaFromAttacks==0&&find(fight,1).manaFromDamage==0,"Cast and recovery pause gain; area spell gives no outgoing mana");
        bool damage=false;for(const auto& e:fight.Events())if(e.mechanic==wc::AbilityMechanic::CrossingBeams&&e.healthLoss>0)damage=true;
        requireMana(damage,"No-outgoing-mana assertion includes a real damaging beam");
    }
    // Shield absorption earns no incoming mana, while the landed basic still charges its attacker.
    {
        auto c=quiet(3);c.units[0].attackDamage=10000;c.units[0].range=1;
        auto& shield=c.units[0].ability;shield.enabled=true;shield.mechanic=wc::AbilityMechanic::Standard;
        shield.effect=wc::Effect::Shield;shield.selector=wc::Selector::AdjacentAllies;shield.allowSelf=true;
        shield.firstCastMs=0;shield.castMs=50;shield.cooldownMs=60000;shield.radius=8;shield.range=8;shield.maxTargets=10;shield.durationMs=10000;
        shield.magnitude={100000,100000,100000};c.units[3].attackDamage=10000;
        wc::Combat fight(c,{unit(1,3,3,3),unit(3,0,1,1)},{unit(2,0,4,3)},47);tick(fight,50);
        bool absorbed=false;for(const auto& e:fight.Events())if(e.target==1&&e.absorbed>0)absorbed=true;
        if(!absorbed||find(fight,1).manaFromDamage!=0){
            std::string detail="Shield fixture: absorbed="+std::to_string(absorbed)+" mana="+std::to_string(find(fight,1).manaFromDamage);
            for(const auto& e:fight.Events())detail+="; t="+std::to_string(e.tick)+" src="+std::to_string(e.source)+" dst="+std::to_string(e.target)+" effect="+std::to_string(int(e.effect))+" resolved="+std::to_string(e.resolved)+" absorbed="+std::to_string(e.absorbed)+" hp="+std::to_string(e.healthLoss);
            throw std::runtime_error(detail);
        }
        requireMana(true,"Shield-only damage gives no incoming mana");
        requireMana(find(fight,1).manaFromAttacks>0,"Landed basic attacks into a shield earn outgoing mana");
    }
    for(int relic=0;relic<int(mana.relics.size());++relic)if(wc::RelicCompatible(mana.relics[relic],mana.units[4].ability.mechanic))
    {
        const auto effective=wc::EffectiveAbility(mana,mana.units[4],relic);
        requireMana(effective.mana.maximum==10000&&effective.mana.gainDivisorBp==mana.relics[relic].cooldownBp,"Relic cadence transforms gain without changing 100 cost");
        requireMana(effective.magnitude==wc::EffectiveAbility(base,base.units[4],relic).magnitude,"Relic impact unchanged across activation variants");
    }
    auto invalid=mana;invalid.units[3].ability.mana.damageWindowCap=1;
    requireMana(!invalid.Validate().empty(),"Invalid mana caps are rejected");
    return checks;
}
}
