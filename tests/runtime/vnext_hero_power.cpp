// Measures how strong each hero is in real fights, apart from bots and shops.
//
// A hero joins a fixed four-hero reference squad and fights the same squad joined by a plain
// yardstick fighter. The yardstick's health and damage are scaled until the two sides are even;
// that scale is the hero's power: 1.0 is a Hammerer of the same star, 1.8 is as much as one
// star adds. Traits are switched off so that a hero is measured by itself.
//
// The same fights at scale 1.0 give how the hero's damage divides between basic attacks and
// its ability, what its ability does per cast, and when it first casts.
//
// A second table measures traits: a squad that reaches a trait against a fixed squad that reaches
// none, with traits on and off.
//
// Measurement only: it checks nothing and changes nothing.
#include "Simulation/WonderSimulation.h"
#include "VNext/WonderVNextCatalog.generated.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>

namespace
{
const int Seeds = 24;

int Definition(const wc::Catalog &catalog, const std::string &id)
{
    for (int i = 0; i < int(catalog.units.size()); ++i) if (catalog.units[i].id == id) return i;
    throw std::runtime_error("Missing hero: " + id);
}
wc::OwnedUnit Unit(wc::Id id, int definition, wc::Cell cell, int star, int scaleBp = 10000)
{
    wc::OwnedUnit unit;
    unit.id = id; unit.definition = definition; unit.onBoard = true; unit.cell = cell; unit.star = star;
    unit.hpScaleBp = unit.damageScaleBp = scaleBp;
    return unit;
}
// Where a hero of this class stands: the row its class prefers, beside the reference squad.
wc::Cell Station(const wc::Catalog &catalog, const wc::UnitDef &hero)
{
    for (const auto &role : catalog.classRoles)
        if (role.id == hero.unitClass) return {role.flank ? 1 : 2, role.row};
    return {2, 3};
}
struct Squad
{
    std::vector<wc::OwnedUnit> units;
    wc::Id subject = 0;
};
Squad Build(const wc::Catalog &catalog, int subject, int star, int scaleBp, wc::Id firstId)
{
    // Two in front, two behind: a plain mixed squad of cheap heroes.
    const std::pair<const char *, wc::Cell> reference[] = {
        {"wc_vn_ironwall", {3, 3}}, {"wc_vn_bearguard", {4, 3}}, {"wc_vn_longbow_scout", {3, 0}}, {"wc_vn_bomber", {4, 0}}};
    Squad squad;
    wc::Id id = firstId;
    for (const auto &entry : reference) squad.units.push_back(Unit(id++, Definition(catalog, entry.first), entry.second, star));
    squad.subject = id;
    squad.units.push_back(Unit(id, subject, Station(catalog, catalog.units[subject]), star, scaleBp));
    return squad;
}
struct Tally
{
    double margin = 0, wins = 0, fights = 0, timeouts = 0;
    double basic = 0, ability = 0, healed = 0, shielded = 0, casts = 0, firstCastTicks = 0, fightsWithCast = 0, seconds = 0;
};
// Share of a side's starting health still standing; summoned units are not counted.
double Standing(const wc::Combat &combat, int side)
{
    double health = 0, full = 0;
    for (const auto &unit : combat.Units())
        if (unit.side == side && !unit.summoned) { health += double(std::max<wc::Int>(0, unit.health)); full += double(unit.maxHealth); }
    return full > 0 ? health / full : 0;
}
void Fight(const wc::Catalog &catalog, const Squad &heroSquad, const Squad &yardSquad, wc::Id seed, bool heroFirst, Tally &tally)
{
    wc::Combat combat(catalog, heroFirst ? heroSquad.units : yardSquad.units, heroFirst ? yardSquad.units : heroSquad.units, seed);
    while (!combat.Result().complete) combat.Tick();
    const int heroSide = heroFirst ? 0 : 1;
    tally.margin += Standing(combat, heroSide) - Standing(combat, 1 - heroSide);
    tally.wins += combat.Result().winner == heroSide ? 1.0 : combat.Result().winner < 0 ? 0.5 : 0.0;
    tally.timeouts += combat.Result().timeout;
    tally.seconds += combat.Result().ticks * catalog.rules.tickMs / 1000.0;
    ++tally.fights;
    // What the hero did, with its summoned units counted as its own.
    const auto &units = combat.Units();
    std::map<wc::Id, bool> own;
    for (int i = 0; i < int(units.size()); ++i)
    {
        int at = i;
        while (units[at].summoned && units[at].owner >= 0 && units[at].owner < int(units.size())) at = units[at].owner;
        own[units[i].id] = units[at].id == heroSquad.subject;
        if (units[i].id == heroSquad.subject)
        {
            tally.casts += units[i].castsCommitted;
            if (units[i].firstCastTick >= 0) { tally.firstCastTicks += units[i].firstCastTick; ++tally.fightsWithCast; }
        }
    }
    for (const auto &event : combat.Events())
    {
        if (event.effect == wc::Effect::Damage)
        {
            if (own[event.source])
                (event.basicAttack && event.source == heroSquad.subject ? tally.basic : tally.ability) += double(event.healthLoss);
            if (own[event.absorbedFrom]) tally.shielded += double(event.absorbed);
        }
        else if (event.effect == wc::Effect::Heal && own[event.source]) tally.healed += double(event.resolved);
    }
}
Tally Measure(const wc::Catalog &catalog, int subject, int star, int yardScaleBp)
{
    const int yardstick = Definition(catalog, "wc_vn_hammerer");
    const Squad heroSquad = Build(catalog, subject, star, 10000, 1), yardSquad = Build(catalog, yardstick, star, yardScaleBp, 101);
    Tally tally;
    for (int seed = 1; seed <= Seeds; ++seed)
    {
        Fight(catalog, heroSquad, yardSquad, wc::Id(seed), true, tally);
        Fight(catalog, heroSquad, yardSquad, wc::Id(1000 + seed), false, tally);
    }
    return tally;
}
// --- Traits ---------------------------------------------------------------------------------
// A squad that reaches a trait fights a fixed opponent squad that reaches none, with traits on
// and with traits off. The opponent is scaled until the fight is even each time; the ratio of
// the two scales is what the trait adds to the whole squad of five.
std::vector<wc::OwnedUnit> Deploy(const wc::Catalog &catalog, const std::vector<int> &heroes, wc::Id firstId, int scaleBp)
{
    std::vector<wc::OwnedUnit> squad;
    const int columns[] = {3, 4, 2, 5, 1, 6, 0, 7};
    for (int hero : heroes)
    {
        int row = 3;
        for (const auto &role : catalog.classRoles) if (role.id == catalog.units[hero].unitClass) row = role.row;
        for (int column : columns)
        {
            const wc::Cell cell{column, row};
            if (std::none_of(squad.begin(), squad.end(), [&](const wc::OwnedUnit &unit) { return unit.cell == cell; }))
            {
                squad.push_back(Unit(firstId + wc::Id(squad.size()), hero, cell, 1, scaleBp));
                break;
            }
        }
    }
    return squad;
}
double SquadMargin(const wc::Catalog &catalog, const std::vector<int> &squad, const std::vector<int> &opponent, int opponentScaleBp)
{
    const auto a = Deploy(catalog, squad, 1, 10000), b = Deploy(catalog, opponent, 101, opponentScaleBp);
    double margin = 0;
    for (int seed = 1; seed <= Seeds; ++seed)
        for (bool first : {true, false})
        {
            wc::Combat combat(catalog, first ? a : b, first ? b : a, wc::Id(first ? seed : 1000 + seed));
            while (!combat.Result().complete) combat.Tick();
            margin += Standing(combat, first ? 0 : 1) - Standing(combat, first ? 1 : 0);
        }
    return margin;
}
double EvenScale(const wc::Catalog &catalog, const std::vector<int> &squad, const std::vector<int> &opponent)
{
    int low = 2500, high = 80000;
    for (int step = 0; step < 11; ++step)
    {
        const int middle = (low + high) / 2;
        (SquadMargin(catalog, squad, opponent, middle) > 0 ? low : high) = middle;
    }
    return (low + high) / 20000.0;
}
void Traits(const wc::Catalog &withTraits, const wc::Catalog &withoutTraits, const std::string &balance)
{
    // Heroes that share no race and no class with anyone already chosen, cheapest first.
    auto extend = [&](std::vector<int> chosen, int size, const std::string &avoid) {
        for (int cost = 1; cost <= 5 && int(chosen.size()) < size; ++cost)
            for (int hero = 0; hero < int(withTraits.units.size()) && int(chosen.size()) < size; ++hero)
            {
                const auto &candidate = withTraits.units[hero];
                if (candidate.cost != cost || candidate.race == avoid || candidate.unitClass == avoid) continue;
                if (std::none_of(chosen.begin(), chosen.end(), [&](int other) {
                        return withTraits.units[other].race == candidate.race || withTraits.units[other].unitClass == candidate.unitClass;
                    }))
                    chosen.push_back(hero);
            }
        return chosen;
    };
    std::ofstream out("trait_power.csv");
    out << "balance_version,trait,members,squad,opponent,even_scale_without,even_scale_with,trait_gain\n";
    std::vector<std::string> seen;
    for (const auto &trait : withTraits.traits)
    {
        if (std::find(seen.begin(), seen.end(), trait.id) != seen.end()) continue;
        seen.push_back(trait.id);
        std::vector<int> all;
        for (int cost = 1; cost <= 5; ++cost)
            for (int hero = 0; hero < int(withTraits.units.size()); ++hero)
                if (withTraits.units[hero].cost == cost &&
                    (withTraits.units[hero].race == trait.id || withTraits.units[hero].unitClass == trait.id))
                    all.push_back(hero);
        for (const auto &tier : trait.tiers)
        {
            if (int(all.size()) < tier.first || tier.first > 5) continue;
            // The members, then fillers that add no second trait.
            std::vector<int> squad(all.begin(), all.begin() + tier.first);
            for (int cost = 1; cost <= 5 && int(squad.size()) < 5; ++cost)
                for (int hero = 0; hero < int(withTraits.units.size()) && int(squad.size()) < 5; ++hero)
                {
                    const auto &candidate = withTraits.units[hero];
                    if (candidate.cost != cost || candidate.race == trait.id || candidate.unitClass == trait.id) continue;
                    if (std::none_of(squad.begin(), squad.end(), [&](int other) {
                            return withTraits.units[other].race == candidate.race || withTraits.units[other].unitClass == candidate.unitClass;
                        }))
                        squad.push_back(hero);
                }
            const auto opponent = extend({}, 5, trait.id);
            if (squad.size() < 5 || opponent.size() < 5) continue;
            const double without = EvenScale(withoutTraits, squad, opponent), with = EvenScale(withTraits, squad, opponent);
            auto names = [&](const std::vector<int> &heroes) {
                std::string text;
                for (int hero : heroes) text += (text.empty() ? "" : " ") + withTraits.units[hero].name;
                return text;
            };
            out << balance << ',' << trait.id << ',' << tier.first << ',' << names(squad) << ',' << names(opponent) << ','
                << without << ',' << with << ',' << (without > 0 ? with / without : 0) << '\n';
        }
    }
}
} // namespace

int main()
{
    try
    {
        const auto roster = wcvnext::WonderVNextRosterCatalog();
        auto catalog = roster;
        const std::string balance = catalog.balanceVersion;
        catalog.traits.clear();
        Traits(roster, catalog, balance);
        std::map<int, double> healthOfCost, heroesOfCost;
        for (const auto &hero : catalog.units) { healthOfCost[hero.cost] += double(hero.health); ++heroesOfCost[hero.cost]; }
        std::ofstream out("hero_power.csv");
        out << "balance_version,hero,name,class,race,cost,star,power,win_rate_vs_plain,timeout_share,fight_seconds,"
               "basic_damage,ability_damage,ability_share,healing,shielding,casts_per_fight,first_cast_seconds,"
               "ability_per_cast,ability_per_cast_vs_cost_health\n";
        for (int subject = 0; subject < int(catalog.units.size()); ++subject)
            for (int star : {1, 2})
            {
                // The margin falls as the yardstick grows; find where it crosses zero.
                int low = 2500, high = 80000;
                const bool beatsCeiling = Measure(catalog, subject, star, high).margin > 0;
                for (int step = 0; step < 11 && !beatsCeiling; ++step)
                {
                    const int middle = (low + high) / 2;
                    (Measure(catalog, subject, star, middle).margin > 0 ? low : high) = middle;
                }
                const double power = beatsCeiling ? high / 10000.0 : (low + high) / 20000.0;
                const Tally plain = Measure(catalog, subject, star, 10000);
                const auto &hero = catalog.units[subject];
                const double dealt = plain.basic + plain.ability, perCast = plain.casts > 0 ? plain.ability / plain.casts : 0;
                const double costHealth = healthOfCost[hero.cost] / heroesOfCost[hero.cost] *
                    catalog.rules.starMultiplierBp[star - 1] / 10000.0;
                out << balance << ',' << hero.id << ',' << hero.name << ',' << hero.unitClass << ',' << hero.race << ',' << hero.cost << ','
                    << star << ',' << power << ',' << plain.wins / plain.fights << ',' << plain.timeouts / plain.fights << ','
                    << plain.seconds / plain.fights << ',' << plain.basic / plain.fights / 100.0 << ','
                    << plain.ability / plain.fights / 100.0 << ',' << (dealt > 0 ? plain.ability / dealt : 0) << ','
                    << plain.healed / plain.fights / 100.0 << ',' << plain.shielded / plain.fights / 100.0 << ','
                    << plain.casts / plain.fights << ','
                    << (plain.fightsWithCast > 0 ? plain.firstCastTicks / plain.fightsWithCast * catalog.rules.tickMs / 1000.0 : -1) << ','
                    << perCast / 100.0 << ',' << (costHealth > 0 ? perCast / costHealth : 0) << '\n';
            }
        std::cout << "WROTE hero_power.csv and trait_power.csv for " << catalog.units.size() << " heroes at one and two stars (" << balance << ")\n";
        return 0;
    }
    catch (const std::exception &error) { std::cerr << "FAIL: " << error.what() << '\n'; return 1; }
}
