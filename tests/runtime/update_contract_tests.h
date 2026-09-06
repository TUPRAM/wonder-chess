#pragma once

wc::Catalog QuietUpdateFixture(const wc::Catalog &canonical)
{
    auto c = canonical;
    c.traits.clear();
    for (auto &u : c.units)
    {
        u.health = 100000; u.attackDamage = 0; u.range = 8;
        u.armor = u.resistance = 0; u.ability.enabled = false;
    }
    return c;
}

void UpdatedSkills(const wc::Catalog &canonical)
{
    for (int variant = 0; variant < 4; ++variant)
    {
        auto c = QuietUpdateFixture(canonical);
        c.units[13].ability = canonical.units[13].ability;
        auto &a = c.units[13].ability;
        a.firstCastMs = 0; a.castMs = 50; a.travelMs = 100; a.range = 8;
        c.units[0].health = variant == 1 ? 5000 : 10000;
        std::vector<wc::OwnedUnit> team{Unit(1,13,3,3)};
        if (variant == 3)
        {
            for (const auto &t : canonical.traits) if (t.id == "mage") c.traits.push_back(t);
            team.push_back(Unit(3,2,2,3));
        }
        if (variant == 2)
        {
            c.units[0].ability = canonical.units[0].ability;
            auto &shield = c.units[0].ability;
            shield.firstCastMs = 0; shield.castMs = 50;
            shield.effects[0].magnitude = {8000,8000,8000};
            shield.magnitude = shield.effects[0].magnitude;
        }
        wc::Combat combat(c,team,{Unit(2,0,3,3)},190 + variant);
        for (int tick = 0; tick < 8; ++tick) combat.Tick();
        std::vector<wc::CombatEvent> effects;
        for (const auto &event : combat.Events())
            if (event.source == 1 && !event.basicAttack) effects.push_back(event);
        Check(!effects.empty() && effects[0].effect == wc::Effect::Damage,
              "Neris resolves authored damage first");
        Check(effects[0].resolved == (variant == 3 ? 7200 : 6000),
              "Mage amplifies Neris damage exactly once");
        if (variant == 1)
            Check(effects.size() == 1, "Neris cannot stun a target defeated by its damage packet");
        else
        {
            Check(effects.size() == 2 && effects[1].effect == wc::Effect::Stun &&
                  effects[1].resolved == 1250 && effects[1].tick == effects[0].tick,
                  "Surviving target receives unamplified stun after same-impact damage");
            if (variant == 2) Check(effects[0].absorbed == 6000 && effects[0].healthLoss == 0,
                                    "Shield absorption still permits Neris surviving-target stun");
        }
    }
    {
        auto c = QuietUpdateFixture(canonical);
        c.units[17].ability = canonical.units[17].ability;
        c.units[17].ability.firstCastMs = 0; c.units[17].ability.castMs = 50;
        c.units[17].ability.range = 8;
        c.units[0].attackRate = 500; c.units[1].attackRate = 1500;
        wc::Combat combat(c,{Unit(1,17,3,3)},{Unit(2,0,3,3),Unit(3,1,0,0)},55);
        for (int tick=0; tick<20; ++tick) combat.Tick();
        bool saw = false;
        for (const auto &e:combat.Events()) if(e.source==1 && !e.basicAttack)
        {
            saw = true;
            Check((e.target & ((wc::Id(1)<<20)-1)) == 3 && e.requested == -2000,
                  "Finn selects highest effective enemy attack rate rather than nearest enemy");
        }
        Check(saw,"Finn revised targeting executes");
    }
    {
        auto c = QuietUpdateFixture(canonical);
        c.units[23].ability = canonical.units[23].ability;
        c.units[23].ability.firstCastMs = 150; c.units[23].ability.castMs = 50;
        c.units[23].ability.range = 8;
        c.units[0].health = 50000;
        c.units[0].ability = canonical.units[0].ability;
        c.units[0].ability.firstCastMs=0; c.units[0].ability.castMs=50;
        c.units[0].ability.effects[0].magnitude={25000,25000,25000};
        c.units[0].ability.magnitude=c.units[0].ability.effects[0].magnitude;
        wc::Combat combat(c,{Unit(1,23,3,3),Unit(2,0,2,3),Unit(3,1,4,3)},
                          {Unit(4,2,0,0)},56);
        for(int tick=0;tick<45;++tick)combat.Tick();
        bool saw=false;
        for(const auto &e:combat.Events())if(e.source==1&&!e.basicAttack)
        {
            saw=true; Check(e.target!=2 && e.resolved==19000,
                            "Oren skips a recipient protected by a stronger unrefreshable shield");
        }
        Check(saw,"Oren finds eligible recipient after strongest shield filtering");
    }
    Check(wc::MovementInterval(1000,0,canonical.rules)==20 &&
          wc::MovementInterval(1000,1000,canonical.rules)==19 &&
          wc::MovementInterval(1000,2000,canonical.rules)==17,
          "Halfling movement uses effective rate and ceiling tick quantization");
}

void UpdatedVisualActions(const wc::Catalog &canonical)
{
    for (int hero : {2,13})
    {
        auto c=QuietUpdateFixture(canonical);
        c.units[hero].ability=canonical.units[hero].ability;
        auto& ability=c.units[hero].ability;
        ability.firstCastMs=0; ability.castMs=100; ability.travelMs=500; ability.recoveryMs=50; ability.range=8;
        if(hero==13) { c.units[0].attackDamage=900000; c.units[0].attackWindupMs=200; }
        else { c.units[0].range=1; c.units[0].movementRate=4000; }
        std::vector<wc::OwnedUnit> a{Unit(1,hero,hero==2?0:3,3),Unit(4,1,0,0)},b{Unit(2,0,hero==2?0:3,hero==2?0:3)};
        wc::Combat observed(c,a,b,412),control(c,a,b,412);
        bool windup=false,released=false,survivedSource=false,movedFromCenter=false;
        wc::Cell captured; wc::Id action=0;
        for(int tick=0;tick<20;++tick)
        {
            observed.Tick();control.Tick();
            const auto visuals=observed.VisualActions();
            const auto again=observed.VisualActions();
            Check(visuals.size()==again.size(),"Visual readback is stable and does not consume packets");
            Check(observed.Events().size()==control.Events().size(),"Visual readback does not alter event count");
            for(std::size_t i=0;i<observed.Units().size();++i)
            {
                const auto& x=observed.Units()[i];const auto& y=control.Units()[i];
                Check(x.health==y.health && x.cell==y.cell && x.state==y.state && x.actionId==y.actionId,
                      "Visual readback leaves actual combat outcomes unchanged");
            }
            int copies=0;
            for(const auto& v:visuals) if(v.source==1 && !v.basicAttack)
            {
                ++copies;
                Check(v.definition==hero && !v.neutral && v.impactTick==v.releaseTick+10,
                      "Visual packet carries exact source definition and authoritative impact time");
                if(v.provisional) { windup=true;Check(!v.released && v.recipientsProvisional,"Windup recipients are explicitly provisional"); }
                else
                {
                    if(!released) { captured=v.center; action=v.action; }
                    released=true;
                    Check(v.released && v.action==action && v.center==captured,"Released center and action remain immutable");
                    if(hero==2)
                    {
                        Check(v.fixedArea && v.recipientsProvisional,"Fixed area preserves geometry while occupants remain provisional");
                        if(!(observed.Units().back().cell==captured)) movedFromCenter=true;
                    }
                    else
                    {
                        Check(v.recipients.size()==1 && !v.recipientsProvisional,"Ordered Neris payload emits one target visual action");
                        if(observed.Units().front().health==0) survivedSource=true;
                    }
                }
            }
            Check(copies<=1,"One visual action per composite cast, not one per effect");
        }
        Check(windup && released,"Actual cast exposes both provisional and released presentation states");
        Check(hero==2?movedFromCenter:survivedSource,"Captured area survives target motion; released projectile survives source defeat");
    }
}

void UpdatedBotSkillPurchases(const wc::Catalog &canonical)
{
    auto c = canonical;
    c.rules.startingGold = 1;
    c.rules.startingLevel = 1;
    c.rules.maximumLevel = 1;
    c.rules.shopWeights[1] = {10000, 0, 0};
    for (auto &unit : c.units) unit.cost = 3;
    c.units[1] = c.units[0];
    c.units[1].id = canonical.units[1].id;
    c.units[0].cost = c.units[1].cost = 1;
    c.units[0].health = c.units[1].health = 20000;
    c.units[0].attackDamage = c.units[1].attackDamage = 1000;
    c.units[0].ability.enabled = false;
    c.units[1].ability = canonical.units[2].ability;
    c.units[1].ability.id = canonical.units[1].ability.id;
    for (auto &bot : c.bots) { bot.noiseBp = 0; bot.decisionIntervalMs = 50; }
    if (!c.Validate().empty()) throw std::runtime_error("Skill purchase fixture invalid: " + c.Validate());
    int compared = 0;
    for (wc::Id seed = 1; seed <= 48 && compared < 8; ++seed)
    {
        wc::Match match(c, seed, 0);
        const auto offers = match.Seats()[0].shop;
        const auto weak = std::find(offers.begin(), offers.end(), 0);
        const auto strong = std::find(offers.begin(), offers.end(), 1);
        if (weak == offers.end() || strong == offers.end() || weak > strong) continue;
        match.Tick(50);
        Check(match.Seats()[0].roster.size() == 1 && match.Seats()[0].roster[0].definition == 1,
              "Normal bot purchase values an available active skill over identical earlier basic-only offer");
        Check(match.Seats()[0].gold == 0 && match.InvariantError().empty(),
              "Skill-aware purchase uses ordinary cost and command invariants");
        for (int unavailable = 0; unavailable < 2; ++unavailable)
        {
            auto without = c;
            if (unavailable == 0) without.units[1].ability.enabled = false;
            else without.units[1].ability.firstCastMs = without.rules.combatTimeoutMs;
            wc::Match control(without, seed, 0);
            control.Tick(50);
            Check(control.Seats()[0].roster.size() == 1 && control.Seats()[0].roster[0].definition == 0,
                  "Disabled or too-late skill grants no speculative purchase advantage");
        }
        ++compared;
    }
    Check(compared == 8, "Skill-aware purchase exercised eight distinct real shop seeds");
}

void UpdatedTournament(const wc::Catalog &canonical)
{
    int neutralCount=0,pvpCount=0;
    for(int round=-2;round<=45;++round)
    {
        const bool expected=round>0&&(round<=3||round%5==0);
        Check(wc::IsNeutralRound(round,canonical.rules)==expected,"Positive round schedule resolver");
        if(round>0&&round<=40) (expected?neutralCount:pvpCount)++;
    }
    Check(neutralCount==11 && pvpCount==29,"Forty-round profile has eleven neutral and twenty-nine PvP rounds");
    auto invalid=canonical;
    invalid.waves.erase(invalid.waves.begin());
    Check(!invalid.Validate().empty(),"Missing required wave fails closed");
    invalid=canonical; invalid.waves[0].slots.push_back(invalid.waves[0].slots[0]);
    Check(!invalid.Validate().empty(),"Duplicate neutral occupancy fails closed");
    invalid=canonical; invalid.waves[0].slots[0].definition=999;
    Check(!invalid.Validate().empty(),"Unknown neutral definition fails closed");

    auto c=canonical;
    c.rules.startingHealth=100000;
    wc::Match match(c,891,0);
    std::vector<wc::Pairing> round4;
    std::set<int> observedWaves;
    std::set<wc::Id> combatIds;
    int previousRecords=0, lastPreparation=1;
    while(match.CurrentPhase()!=wc::Phase::Finished && match.ElapsedMs()<4000000)
    {
        match.Tick(50);
        Check(match.InvariantError().empty(),"Forced-cap real tournament invariants");
        if(match.CurrentPhase()==wc::Phase::Preparation && match.Round()!=lastPreparation)
        {
            lastPreparation=match.Round();
            const auto &previous=match.Records().back();
            for(const auto &seat:match.Seats())
                Check(seat.gold==previous.gold[seat.id]+c.rules.baseIncome+previous.pendingRewards[seat.id]+
                    std::min(c.rules.interestCap,seat.lockGold/c.rules.interestDivisor),
                    "Next preparation applies normal income and exactly one settlement entitlement");
        }
        if(match.CurrentPhase()==wc::Phase::Combat && match.NeutralRound() &&
           observedWaves.insert(match.Round()).second)
        {
            Check(match.Encounters().size()==8,"All eight seats run isolated neutral combats");
            const auto *wave=match.CurrentWave();
            for(const auto &encounter:match.Encounters())
            {
                Check(encounter.kind==wc::EncounterKind::Neutral && encounter.sides[0].seat.has_value() &&
                      !encounter.sides[1].seat.has_value() && encounter.sides[1].waveId==wave->id,
                      "Neutral has wave ownership and no competitor seat");
                int neutralUnits=0;
                for(const auto &unit:encounter.combat.Units())
                {
                    Check(combatIds.insert(unit.id).second,"Independent encounter unit identity");
                    Check(unit.id<(wc::Id(1)<<53)&&wc::Id(double(unit.id))==unit.id,
                          "Namespaced combat identity survives JSON-number snapshot exactly");
                    if(unit.neutral)
                    {
                        ++neutralUnits;
                        Check(unit.maxHealth==wc::HalfUp(c.neutrals[unit.definition].health*wave->hpScaleBp,10000),
                              "Neutral health scaling applied once without hero traits or stars");
                    }
                }
                Check(neutralUnits==int(wave->slots.size()),"Every authored wave slot instantiated");
            }
        }
        if(int(match.Records().size())>previousRecords)
        {
            previousRecords=int(match.Records().size());
            const auto &record=match.Records().back();
            if(record.round==4)round4=record.pairs;
            if(record.round==6)
            {
                Check(record.pvpRoundIndex==2,"Neutral round preserves PvP index");
                for(auto a:round4)for(auto b:record.pairs)
                    Check(!(a.a==b.a&&a.b==b.b),"Round six avoids previous PvP round-four pairings");
            }
            for(int seat=0;seat<8;++seat)
            {
                if(record.neutral)
                {
                    Check(record.pendingRewards[seat]==0||record.pendingRewards[seat]==2,
                          "Neutral grants only declared two-gold entitlement");
                    if(record.round<=3)Check(record.damage[seat]==0,"Opening neutral failures are forgiving");
                }
            }
        }
    }
    Check(match.CurrentPhase()==wc::Phase::Finished&&match.Round()==40&&match.Capped(),
          "Actual round forty neutral settles before cap adjudication");
    Check(observedWaves.size()==11,"Every reachable neutral wave executed with eight real seats");
    Check(match.PvpRoundIndex()==29,"Final PvP index counts competitive rounds only");
    const auto finalRecord=match.Records().back();
    for(int seat=0;seat<8;++seat)
        Check(match.Seats()[seat].gold==finalRecord.gold[seat],"No post-cap preparation income applied");
    match.Tick(10000);
    Check(match.Records().size()==40,"Repeated finished callbacks never resettle or pay rewards");
    match.Restart(891,0);
    Check(match.Round()==1&&match.PvpRoundIndex()==0&&match.Records().empty()&&match.NeutralRound(),
          "Restart clears prior PvP, encounter, settlement and reward state");

    auto empty=canonical;
    empty.rules.startingHealth=1000; empty.rules.startingGold=0;
    empty.rules.baseIncome=0; empty.rules.passiveXp=0;
    wc::Match losing(empty,445,0);
    while(losing.CurrentPhase()!=wc::Phase::Finished && losing.ElapsedMs()<1000000) losing.Tick(50);
    Check(losing.CurrentPhase()==wc::Phase::Finished&&losing.Round()==40,
          "Empty-roster neutral loss path reaches cap without fabricated wins");
    for(const auto &record:losing.Records()) for(int seat=0;seat<8;++seat)
    {
        const int expected=record.neutral ? (record.round<=3?0:2) : empty.rules.drawDamage;
        Check(record.damage[seat]==expected&&record.pendingRewards[seat]==0&&record.wins[seat]==0,
              "Opening/later neutral failures and PvP draws obey separate damage and reward rules");
    }
    for(const auto &seat:losing.Seats())
        Check(seat.neutralLosses==11&&seat.neutralWins==0&&seat.gold==0&&seat.xp==0,
              "All eleven neutral losses preserve separate counters and no final income");

    auto draw=QuietUpdateFixture(canonical);
    draw.rules.startingHealth=1000; draw.rules.startingLevel=1; draw.rules.maximumLevel=1;
    draw.rules.shopWeights[1]={10000,0,0};
    for(auto &unit:draw.units) { unit.cost=1; unit.attackDamage=0; unit.ability.enabled=false; }
    for(auto &unit:draw.neutrals) { unit.attackDamage=0; unit.ability.enabled=false; unit.ability.effects.clear(); }
    for(auto &wave:draw.waves) wave.slots.resize(1);
    wc::Match drawing(draw,446,0);
    while(drawing.Records().size()<5&&drawing.ElapsedMs()<1000000) drawing.Tick(50);
    Check(drawing.Records().size()==5,"Neutral timeout-draw fixture executed through round five");
    for(const auto &record:drawing.Records())if(record.neutral)
        for(int seat=0;seat<8;++seat)
            Check(record.damage[seat]==(record.round<=3?0:2)&&record.pendingRewards[seat]==0,
                  "Neutral timeout draw earns no gold and uses declared failure damage");
    for(const auto &seat:drawing.Seats())
        Check(seat.neutralDraws==4&&seat.neutralWins==0&&seat.wins==0,
              "Neutral timeout draws never inflate competitive wins");
}
