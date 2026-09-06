#include "CatalogFixture.h"
#include <algorithm>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <tuple>

namespace {
int assertions = 0, cases = 0, failures = 0, combats = 0;
std::string active;
std::ofstream rows("trait-cases.csv"), events("trait-events.csv");
void Check(bool condition, const char* why) { ++assertions; if (!condition) throw std::runtime_error(why); }
void Case(const std::string& name, const std::function<void()>& run) {
    active = name; ++cases; const int before = assertions;
    try { run(); rows << name << ",PASS," << assertions - before << ",\n"; }
    catch (const std::exception& e) { ++failures; rows << name << ",FAIL," << assertions - before << ',' << e.what() << '\n'; std::cerr << name << ": " << e.what() << '\n'; }
}
wc::OwnedUnit Unit(wc::Id id, int def, int x, int star = 1, bool board = true) {
    wc::OwnedUnit u; u.id=id; u.definition=def; u.star=star; u.onBoard=board; u.cell={x,3}; u.bench=board ? -1 : 0; return u;
}
std::vector<int> Members(const wc::Catalog& c, const std::string& trait) {
    std::vector<int> result;
    for (int i=0; i<int(c.units.size()); ++i) if (c.units[i].race==trait || c.units[i].unitClass==trait) result.push_back(i);
    return result;
}
wc::TraitDef Trait(const wc::Catalog& c, const std::string& id) {
    for (const auto& t:c.traits) if (t.id==id) return t;
    throw std::runtime_error("Unknown trait");
}
const wc::CombatUnit& Find(const wc::Combat& c, int side, wc::Id local) {
    for (const auto& u:c.Units()) if(u.side==side && (u.id & ((wc::Id(1)<<20)-1))==local) return u;
    throw std::runtime_error("Missing combat unit");
}
auto Stats(const wc::CombatUnit& u) { return std::make_tuple(u.health,u.maxHealth,u.basicDamage,u.armor,u.resistance,u.basicBonus,u.abilityBonus,u.allBonus,u.rateBonus,u.supportBonus,u.cooldownTick,u.movementBonus); }
void ExpectedBonus(wc::CombatUnit& u, const wc::TraitDef& t, const wc::Catalog& c) {
    if(t.stat=="max_health_bonus_bp") {
        const auto base=c.units[u.definition].health;
        const auto numerator=base*c.rules.starMultiplierBp[u.star-1]*(10000+t.value);
        u.health=u.maxHealth=(numerator+50000000)/100000000;
    } else if(t.stat=="attack_rate_bonus_bp") u.rateBonus+=t.value;
    else if(t.stat=="physical_armor_flat") u.armor+=t.value;
    else if(t.stat=="all_damage_bonus_bp") u.allBonus+=t.value;
    else if(t.stat=="basic_damage_bonus_bp") u.basicBonus+=t.value;
    else if(t.stat=="ability_damage_bonus_bp") u.abilityBonus+=t.value;
    else if(t.stat=="support_power_bonus_bp") u.supportBonus+=t.value;
    else if(t.stat=="magic_resistance_flat") u.resistance+=t.value;
    else if(t.stat=="movement_bonus_bp") u.movementBonus+=t.value;
    else throw std::runtime_error("Uncovered parsed trait statistic");
}
void Snapshot(const wc::Catalog& canonical, const wc::TraitDef& t, const std::vector<wc::OwnedUnit>& a,
              const std::vector<wc::OwnedUnit>& b, bool aActive, bool bActive) {
    auto isolated=canonical, baseline=canonical; isolated.traits={t}; baseline.traits.clear();
    wc::Combat actual(isolated,a,b,52), plain(baseline,a,b,52); combats+=2;
    Check(actual.InvariantError().empty(),"Snapshot obeys runtime invariants");
    Check(actual.Units().size()==plain.Units().size(),"Trait never creates a combat unit");
    for(const auto& base:plain.Units()) {
        auto expected=base; const auto& d=canonical.units[base.definition];
        if((base.side ? bActive:aActive) && (d.race==t.id || d.unitClass==t.id)) ExpectedBonus(expected,t,canonical);
        Check(Stats(Find(actual,base.side,base.id & ((wc::Id(1)<<20)-1)))==Stats(expected),"Exact matching recipient stats with no duplicate or cross-field application");
    }
}
wc::Catalog Controlled(const wc::Catalog& source) {
    auto c=source;
    for(auto& d:c.units) {
        d.health=100000; d.attackDamage=0; d.armor=d.resistance=0; d.attackRate=1000;
        d.range=8; d.attackWindupMs=50; d.projectileTravelMs=0; d.ability.firstCastMs=100000;
    }
    return c;
}
void Ability(wc::UnitDef& d, wc::Effect effect, wc::Selector selector, wc::Int value, int first=0) {
    auto& a=d.ability; a.effects.clear(); a.effect=effect; a.selector=selector; a.damageType=wc::DamageType::True;
    a.magnitude={value,value,value}; a.firstCastMs=first; a.castMs=50; a.recoveryMs=50; a.cooldownMs=100000;
    a.durationMs=1000; a.travelMs=0; a.radius=8; a.range=8; a.maxTargets=12; a.allowSelf=true;
}
void Step(wc::Combat& c,int ticks) {
    for(int i=0;i<ticks;++i) { c.Tick(); Check(c.InvariantError().empty(),"Per-tick combat invariants"); }
    for(const auto& e:c.Events()) events<<active<<','<<e.tick<<','<<e.source<<','<<e.target<<','<<int(e.effect)<<','<<e.basicAttack<<','<<e.requested<<','<<e.resolved<<'\n';
}
void Damage(const wc::Catalog& canonical,const std::vector<std::string>& traitIds,int source,
            const std::vector<int>& providers,int basicBp,int abilityBp) {
    auto c=Controlled(canonical); c.traits.clear(); for(const auto& id:traitIds)c.traits.push_back(Trait(canonical,id));
    c.units[source].attackDamage=10000; c.units[source].damageType=wc::DamageType::True;
    Ability(c.units[source],wc::Effect::Damage,wc::Selector::CurrentEnemy,10000,200);
    std::vector<wc::OwnedUnit> a{Unit(1,source,0)}; for(int d:providers)a.push_back(Unit(a.size()+1,d,int(a.size())));
    wc::Combat combat(c,a,{Unit(100,0,0)},9); ++combats; Step(combat,32);
    bool basic=false,ability=false;
    for(const auto& e:combat.Events()) if(e.source==1 && e.effect==wc::Effect::Damage) {
        Check(e.requested==10000,"Unmodified raw damage packet magnitude");
        Check(e.resolved==10000+(e.basicAttack?basicBp:abilityBp),"Source bonuses resolve once with additive basis points");
        (e.basicAttack?basic:ability)=true;
    }
    Check(basic&&ability,"Actual basic and ability impacts both executed");
}
void Support(const wc::Catalog& canonical,wc::Effect effect,wc::Int magnitude,bool priests) {
    auto c=Controlled(canonical); c.traits={Trait(canonical,"priest"),Trait(canonical,"orc"),Trait(canonical,"mage")};
    const int caster=priests?1:10;
    Ability(c.units[caster],effect,wc::Selector::AdjacentAllies,magnitude,200);
    // This adversarial damage source wounds every recipient before the support release.
    Ability(c.units[6],wc::Effect::Damage,wc::Selector::AdjacentEnemies,30000);
    c.units[6].ability.firstCastMs=0;
    const std::vector<wc::OwnedUnit> a=priests ? std::vector<wc::OwnedUnit>{Unit(1,1,0),Unit(2,4,1),Unit(3,0,2)}
                                             : std::vector<wc::OwnedUnit>{Unit(1,10,0),Unit(2,9,1),Unit(3,2,2)};
    wc::Combat combat(c,a,{Unit(100,6,0)},73); ++combats; Step(combat,32);
    int delivered=0; const wc::Int expected=priests && magnitude>0 ? (magnitude*11500+5000)/10000:magnitude;
    for(const auto& e:combat.Events()) if(e.source==1 && e.effect==effect) {
        ++delivered; Check(e.requested==expected,"Support is amplified once at caster, never by recipient, Orc or Mage");
        Check(e.resolved==expected,"Actual support result matches the once-amplified magnitude");
    }
    Check(delivered==3,"Support actually reached all three recipients including priest/nonpriest distinctions");
}
void RateTiming(const wc::Catalog& canonical, const std::vector<std::string>& traitIds, int expectedInterval) {
    auto boosted=Controlled(canonical); boosted.traits.clear();
    for(const auto& id:traitIds)boosted.traits.push_back(Trait(canonical,id));
    boosted.units[5].attackDamage=1000;
    auto plain=boosted; plain.traits.clear();
    const std::vector<wc::OwnedUnit> a{Unit(1,5,0),Unit(2,4,1),Unit(3,11,2)}, b{Unit(100,6,0)};
    std::vector<int> basicTimes[2];
    for(int variant=0;variant<2;++variant) {
        const auto& catalog=variant?boosted:plain;
        wc::Combat combat(catalog,a,b,21);++combats;Step(combat,100);
        for(const auto& e:combat.Events())if(e.source==1&&e.basicAttack)basicTimes[variant].push_back(e.tick);
        Check(basicTimes[variant].size()>=5,"Five actual basic releases observed");
        for(size_t i=1;i<basicTimes[variant].size();++i)
            Check(basicTimes[variant][i]-basicTimes[variant][i-1]==(variant?expectedInterval:20),"Exact actual basic release interval with active versus plain rates");
    }
    Check(basicTimes[1].back()!=basicTimes[0].back(),"Active rate changes the actual combat trace");
    // A fixed700ms skill cycle prevents a basic recovery from delaying the controlled cast.
    // Cooldown ticks are also checked so a wrongly shortened cooldown cannot hide behind recovery.
    for(auto* catalog:{&boosted,&plain}) {
        Ability(catalog->units[5],wc::Effect::Damage,wc::Selector::CurrentEnemy,1000);
        catalog->units[5].ability.cooldownMs=700;catalog->units[5].ability.recoveryMs=650;
    }
    std::vector<int> abilityTimes[2];
    for(int variant=0;variant<2;++variant) {
        wc::Combat combat(variant?boosted:plain,a,b,21);++combats;
        for(int i=0;i<60;++i) {
            combat.Tick();Check(combat.InvariantError().empty(),"Ability timing invariant");
            const auto& source=Find(combat,0,1);
            if(source.state==wc::ActionState::CastWindup)
                Check(source.cooldownTick==combat.CurrentTick()+14,"Every committed ability keeps its authored700ms cooldown");
        }
        for(const auto& e:combat.Events())if(e.source==1&&!e.basicAttack&&e.effect==wc::Effect::Damage)abilityTimes[variant].push_back(e.tick);
        Check(abilityTimes[variant].size()>=4,"At least four actual ability releases observed");
        for(size_t i=1;i<abilityTimes[variant].size();++i)
            Check(abilityTimes[variant][i]-abilityTimes[variant][i-1]==14,"Subsequent ability release intervals remain700ms");
    }
    Check(abilityTimes[0]==abilityTimes[1],"Elf and Rogue rate bonuses do not change actual repeated ability release timing");
}
}
int main() {
    rows<<"case,status,assertions,error\n"; events<<"case,tick,source,target,effect,basic,requested,resolved\n";
    const auto c=FixtureCatalog();
    Case("canonical_alpha_trait_contract",[&]{
        Check(c.Validate().empty(),"Canonical catalog valid"); Check(c.traits.size()==12,"All twelve parsed traits covered");
        for(const auto& t:c.traits) { Check(t.threshold==2 && t.threshold4==4,"Two and four thresholds parsed"); Check(Members(c,t.id).size()==4,"Every enabled trait has four distinct members"); }
    });
    for(const auto& t:c.traits) {
        const auto members=Members(c,t.id); int other=0;
        while(std::find(members.begin(),members.end(),other)!=members.end())++other;
        for(int star=1;star<=3;++star) {
            const std::string suffix="_star"+std::to_string(star);
            Case(t.id+"_two_distinct_matching_only"+suffix,[&]{Snapshot(c,t,{Unit(1,members[0],0,star),Unit(2,members[1],1,star),Unit(3,other,2,star)},{Unit(100,members[0],0,star)},true,false);});
            Case(t.id+"_duplicate_stars_do_not_count"+suffix,[&]{Snapshot(c,t,{Unit(1,members[0],0,star),Unit(2,members[0],1,star%3+1),Unit(3,other,2,star)},{Unit(100,other,0,star)},false,false);});
            Case(t.id+"_bench_excluded"+suffix,[&]{Snapshot(c,t,{Unit(1,members[0],0,star),Unit(2,members[1],1,star,false),Unit(3,other,2,star)},{Unit(100,members[1],0,star)},false,false);});
        }
        Case(t.id+"_four_distinct_replace_tier_two",[&]{
            auto expected=t; expected.value=t.value4;
            Snapshot(c,expected,{Unit(1,members[0],0),Unit(2,members[1],1),Unit(3,members[2],2),Unit(4,members[3],3),Unit(5,other,4)},{Unit(100,other,0)},true,false);
        });
        Case(t.id+"_duplicate_recipient_gets_bonus_once",[&]{Snapshot(c,t,{Unit(1,members[0],0),Unit(2,members[1],1),Unit(3,members[0],2),Unit(4,other,3)},{Unit(100,other,0)},true,false);});
        Case(t.id+"_opponent_types_do_not_enable_friendly",[&]{Snapshot(c,t,{Unit(1,members[0],0),Unit(2,other,1)},{Unit(100,members[0],0),Unit(101,members[1],1),Unit(102,other,2)},false,true);});
        Case(t.id+"_four_instances_three_distinct_keep_tier_two",[&]{
            Snapshot(c,t,{Unit(1,members[0],0),Unit(2,members[1],1),Unit(3,members.back(),2),Unit(4,members[0],3),Unit(5,other,4)},{Unit(100,other,0)},true,false);
        });
    }
    Case("overlapping_dwarf_guardian_armor_additive",[&]{
        wc::Combat combat(c,{Unit(1,6,0),Unit(2,8,1),Unit(3,0,2)},{Unit(100,11,0)},7);++combats;
        Check(Find(combat,0,1).armor==c.units[6].armor+25,"Borin receives dwarf10 plus guardian15 exactly once");
        Check(Find(combat,0,2).armor==c.units[8].armor+10,"Dagna receives only matching dwarf10");
        Check(Find(combat,0,3).armor==c.units[0].armor+15,"Ada receives only matching guardian15");
    });
    Case("overlapping_elf_rogue_rate_additive",[&]{
        wc::Combat combat(c,{Unit(1,5,0),Unit(2,4,1),Unit(3,11,2)},{Unit(100,6,0)},7);++combats;
        Check(Find(combat,0,1).rateBonus==2500,"Sylas receives elf10 plus rogue15");
        Check(Find(combat,0,2).rateBonus==1000 && Find(combat,0,3).rateBonus==1500,"Only matching rate recipients");
        for(const auto& u:combat.Units())Check(u.cooldownTick==(c.units[u.definition].ability.firstCastMs+49)/50,"Rate traits preserve first cast time");
    });
    Case("orc_basic_and_skill_once",[&]{Damage(c,{"orc"},10,{9},1000,1000);});
    Case("warrior_basic_only_once",[&]{Damage(c,{"warrior"},9,{8},1500,0);});
    Case("ranger_basic_only_once",[&]{Damage(c,{"ranger"},3,{7},1500,0);});
    Case("mage_skill_only_once",[&]{Damage(c,{"mage"},2,{10},0,2000);});
    Case("orc_mage_direct_bonuses_add_not_multiply",[&]{Damage(c,{"orc","mage"},10,{9,2},1000,3000);});
    for(const auto effect:{wc::Effect::Heal,wc::Effect::Shield,wc::Effect::StatModifier}) {
        Case("priest_support_once_effect"+std::to_string(int(effect)),[&]{Support(c,effect,effect==wc::Effect::StatModifier?500:10000,true);});
        Case("orc_mage_do_not_boost_support_effect"+std::to_string(int(effect)),[&]{Support(c,effect,effect==wc::Effect::StatModifier?500:10000,false);});
    }
    Case("priest_does_not_boost_negative_modifier",[&]{Support(c,wc::Effect::StatModifier,-500,true);});
    Case("elf_actual_attack_and_ability_timing",[&]{RateTiming(c,{"elf"},19);});
    Case("rogue_actual_attack_and_ability_timing",[&]{RateTiming(c,{"rogue"},18);});
    Case("elf_rogue_actual_attack_and_ability_timing",[&]{RateTiming(c,{"elf","rogue"},16);});
    std::ofstream summary("summary.json"); summary<<"{\"cases\":"<<cases<<",\"failed\":"<<failures<<",\"assertions\":"<<assertions<<",\"combat_constructions\":"<<combats<<",\"content_digest\":\""<<c.contentDigest<<"\"}\n";
    std::cout<<"cases="<<cases<<" failed="<<failures<<" assertions="<<assertions<<" combats="<<combats<<'\n';
    return failures?1:0;
}
