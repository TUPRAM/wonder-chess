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
        if (weak.units[hero].ability.mechanic == wc::AbilityMechanic::DirectionalGuard)
            weak.units[hero].ability.guardReductionBp = 1;
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
