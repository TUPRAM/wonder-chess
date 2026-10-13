#pragma once
#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <functional>
#include <string>

inline void VNextBotTests(const wc::Catalog &canonical,
                         const std::function<void(bool, const std::string &)> &check)
{
    // Force one available hero per shop tier in a local fixture, isolating the
    // purchase evaluator from acquisition randomness and economic alternatives.
    auto firstPurchase = [&](wc::Catalog catalog, int hero) {
        const int cost = catalog.units[hero].cost;
        for (int i = 0; i < int(catalog.units.size()); ++i)
            if (i != hero && catalog.units[i].cost == cost) catalog.units[i].cost = cost == 1 ? 2 : 1;
        for (auto &level : catalog.rules.shopWeights)
        {
            level.second = {};
            level.second[cost - 1] = 10000;
        }
        catalog.rules.buyXpGold = 1000;
        for (auto &bot : catalog.bots) bot.noiseBp = 0;
        wc::Match match(catalog, 741, 0);
        check(match.CurrentPhase() == wc::Phase::Preparation, "bot evaluation fixture is a valid native match");
        match.Tick(catalog.rules.tickMs);
        const auto found = std::find_if(match.BotLog().begin(), match.BotLog().end(), [](const wc::BotDecision &decision) {
            return decision.seat == 0 && decision.action == "buy" && decision.reply.accepted;
        });
        check(found != match.BotLog().end(), "bot buys available pilot through the command authority");
        return found == match.BotLog().end() ? wc::BotDecision{} : *found;
    };
    for (int hero = 0; hero < int(canonical.units.size()); ++hero)
    {
        auto weak = canonical;
        weak.units[hero].ability.magnitude = {};
        for (auto &effect : weak.units[hero].ability.effects)
        {
            effect.magnitude = {};
            if (effect.effect == wc::Effect::Stun) effect.durationMs = canonical.rules.tickMs;
            // A summon is only as strong as the unit it calls.
            if (effect.effect == wc::Effect::Summon)
            {
                weak.neutrals[effect.summon].attackDamage = 0;
                weak.neutrals[effect.summon].health = 1;
            }
            // A status carries its duration as its magnitude; the weakest valid one lasts a tick.
            if (wc::IsStatusEffect(effect.effect))
            {
                effect.durationMs = canonical.rules.tickMs;
                effect.magnitude = {canonical.rules.tickMs, canonical.rules.tickMs, canonical.rules.tickMs};
            }
        }
        if (weak.units[hero].ability.mechanic == wc::AbilityMechanic::DirectionalGuard)
            weak.units[hero].ability.guardReductionBp = 1;
        // A damage-free cocoon's authored benefit is control time. Zeroing its
        // already-zero magnitude does not weaken it; retain a valid one-tick
        // control fixture so the comparison measures actual utility valuation.
        if (weak.units[hero].ability.mechanic == wc::AbilityMechanic::CocoonProjectile)
            weak.units[hero].ability.durationMs = canonical.rules.tickMs;
        const auto low = firstPurchase(weak, hero);
        const auto high = firstPurchase(canonical, hero);
        check(high.features[0] > low.features[0], "authored skill strength changes pilot recruitment value: " + canonical.units[hero].id);
        if (canonical.units[hero].unitClass == "healer")
            check(high.features[3] >= 0.1, "successor healer contributes the support role");
        if (canonical.units[hero].unitClass == "assassin")
            check(high.features[3] >= 0.3, "successor assassin contributes the damage role");
    }
    wc::SeatState owner;
    owner.gold = 10; owner.level = 3;
    wc::OwnedUnit unit;
    unit.id = 1; unit.definition = 0; unit.bench = 0; unit.hpScaleBp = 20000;
    owner.roster.push_back(unit);
    wc::Command sell; sell.type = wc::CommandType::Sell; sell.unit = 1;
    check(!wc::PreviewRosterCommand(canonical, owner, sell).accepted,
          "inflated ordinary hero health scaling cannot enter an authoritative roster transaction");
    owner.roster[0].hpScaleBp = 10000; owner.roster[0].damageScaleBp = 20000;
    check(!wc::PreviewRosterCommand(canonical, owner, sell).accepted,
          "inflated ordinary hero damage scaling cannot enter an authoritative roster transaction");
}

// The roster rule set names its classes differently from the legacy profile. Bots take a
// class's role and row from the catalogue, and must see a trait only once it is reached.
inline void VNextBotRoleTests(const wc::Catalog &roster,
                             const std::function<void(bool, const std::string &)> &check)
{
    check(roster.Validate().empty(), "roster rule set validates: " + roster.Validate());
    auto roleOf = [&](const wc::UnitDef &unit) -> const wc::ClassRole * {
        for (const auto &role : roster.classRoles) if (role.id == unit.unitClass) return &role;
        return nullptr;
    };
    for (const auto &unit : roster.units)
        check(roleOf(unit) != nullptr, "every roster hero's class has a bot role: " + unit.id);

    // Trait visibility: one tank reaches no tier, two different tanks reach the first.
    std::vector<int> tanks;
    for (int i = 0; i < int(roster.units.size()); ++i)
        if (roster.units[i].unitClass == "tank" && (tanks.empty() || roster.units[i].race != roster.units[tanks[0]].race))
            tanks.push_back(i);
    check(tanks.size() >= 2, "roster has two tanks of different races");
    if (tanks.size() >= 2)
    {
        auto withoutTraits = roster;
        withoutTraits.traits.clear();
        auto seatWith = [&](int count) {
            wc::SeatState seat;
            seat.id = 0; seat.level = 3;
            for (int i = 0; i < count; ++i)
            {
                wc::OwnedUnit unit;
                unit.id = wc::Id(i + 1); unit.definition = tanks[i]; unit.onBoard = true; unit.cell = {i, 3};
                seat.roster.push_back(unit);
            }
            return seat;
        };
        const auto &bot = roster.bots[0];
        const auto one = seatWith(1), two = seatWith(2);
        check(wc::BotLineupValue(one, roster, bot) == wc::BotLineupValue(one, withoutTraits, bot),
              "bot gives no trait credit below the first tier");
        check(wc::BotLineupValue(two, roster, bot) > wc::BotLineupValue(two, withoutTraits, bot),
              "bot values reaching a two-unit trait");
    }

    // Formation: over the opening rounds of a bot-only match, frontline classes stand in
    // the front half and ranged damage classes in the back half.
    wc::Match match(roster, 4107, 0);
    int frontlineSeen = 0, rangedSeen = 0, frontlineMisplaced = 0, rangedMisplaced = 0;
    for (int round = 0; round < 6 && match.CurrentPhase() != wc::Phase::Finished; ++round)
    {
        for (int guard = 0; guard < 4000 && match.CurrentPhase() == wc::Phase::Preparation; ++guard)
            match.Tick(roster.rules.tickMs);
        for (const auto &seat : match.Seats())
            for (const auto &unit : seat.roster)
            {
                if (!unit.onBoard) continue;
                const auto &definition = roster.units[unit.definition];
                const auto *role = roleOf(definition);
                if (!role) continue;
                if (role->role == wc::BotRole::Frontline) { ++frontlineSeen; frontlineMisplaced += unit.cell.row < 2; }
                else if (role->role == wc::BotRole::Damage && definition.range > 1) { ++rangedSeen; rangedMisplaced += unit.cell.row > 1; }
            }
        for (int guard = 0; guard < 20000 && match.CurrentPhase() != wc::Phase::Preparation &&
             match.CurrentPhase() != wc::Phase::Finished; ++guard)
            match.Tick(roster.rules.tickMs);
    }
    check(frontlineSeen > 0 && rangedSeen > 0, "formation fixture fielded frontline and ranged heroes");
    check(frontlineMisplaced == 0, "bots deploy frontline classes in the front half: " + std::to_string(frontlineMisplaced) +
          " of " + std::to_string(frontlineSeen) + " misplaced");
    check(rangedMisplaced == 0, "bots deploy ranged damage classes in the back half: " + std::to_string(rangedMisplaced) +
          " of " + std::to_string(rangedSeen) + " misplaced");

// Goblin: gold for a won player fight comes from fielded Goblins only.
    auto heroIndex = [&](const char *identity) {
        for (int i = 0; i < int(roster.units.size()); ++i) if (roster.units[i].id == identity) return i;
        return -1;
    };
    const int hookjaw = heroIndex("wc_vn_hookjaw"), bomber = heroIndex("wc_vn_bomber"), jinxer = heroIndex("wc_vn_jinxer"),
        dart = heroIndex("wc_vn_dartblower");
    check(hookjaw >= 0 && bomber >= 0 && jinxer >= 0 && dart >= 0, "four Goblins are in the roster");
    auto goblinSeat = [&](std::vector<int> board, std::vector<int> bench) {
        wc::SeatState state;
        state.level = 10;
        wc::Id next = 1;
        for (int definition : board)
        {
            wc::OwnedUnit unit; unit.id = next; unit.definition = definition; unit.onBoard = true; unit.cell = {int(next++) % 8, 0};
            state.roster.push_back(unit);
        }
        for (int definition : bench)
        {
            wc::OwnedUnit unit; unit.id = next++; unit.definition = definition;
            state.roster.push_back(unit);
        }
        return state;
    };
    check(wc::TraitWinGold(goblinSeat({hookjaw}, {bomber, jinxer}), roster) == 0, "benched Goblins pay nothing");
    check(wc::TraitWinGold(goblinSeat({hookjaw, bomber}, {}), roster) == 1, "two fielded Goblins pay one extra gold for a win");
    check(wc::TraitWinGold(goblinSeat({hookjaw, bomber, jinxer, dart}, {}), roster) == 2, "four fielded Goblins pay two extra gold");
    auto control = roster;
    control.traits.clear();
    check(wc::TraitWinGold(goblinSeat({hookjaw, bomber}, {}), control) == 0, "without the trait there is no extra gold");
    // Economy: gold above the interest cap is spent on experience, so levels arrive earlier
    // than when experience is bought only if one purchase finishes the level.
    auto levelsAfter = [&](wc::Catalog catalog, int rounds) {
        wc::Match run(catalog, 5203, 0);
        for (int guard = 0; guard < 400000 && run.Round() <= rounds && run.CurrentPhase() != wc::Phase::Finished; ++guard)
            run.Tick(catalog.rules.tickMs);
        int levels = 0;
        for (const auto &seat : run.Seats()) levels += seat.level;
        return levels;
    };
    auto hoarding = roster;
    hoarding.botSpendsSurplus = false;
    check(roster.botSpendsSurplus, "roster rule set lets bots spend surplus gold");
    const int spending = levelsAfter(roster, 25), saving = levelsAfter(hoarding, 25);
    check(spending > saving, "bots that spend surplus gold reach higher levels by round 25: " + std::to_string(spending) +
          " against " + std::to_string(saving));
}
