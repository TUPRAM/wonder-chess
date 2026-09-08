#include "CatalogFixture.h"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <tuple>

namespace
{
int assertions = 0;
void Check(bool condition, const char *message)
{
    ++assertions;
    if (!condition)
        throw std::runtime_error(message);
}
wc::OwnedUnit Unit(wc::Id id, int definition, int col, int row, int star = 1)
{
    wc::OwnedUnit u;
    u.id = id;
    u.definition = definition;
    u.onBoard = true;
    u.cell = {col, row};
    u.star = star;
    return u;
}
wc::Reply Send(wc::Match &m, int seat, wc::CommandType type, int slot = -1, wc::Id unit = 0,
               bool board = false, wc::Cell cell = {})
{
    static wc::Id request = 100;
    const auto &s = m.Seats()[seat];
    wc::Command c;
    c.type = type;
    c.seat = seat;
    c.requestId = ++request;
    c.sequence = s.sequence + 1;
    c.revision = s.revision;
    c.slot = slot;
    c.unit = unit;
    c.toBoard = board;
    c.cell = cell;
    const bool previewable = m.CurrentPhase() == wc::Phase::Preparation && s.health > 0 &&
        (type == wc::CommandType::Buy || type == wc::CommandType::Move || type == wc::CommandType::Sell);
    const auto before = s;
    const auto space = m.Namespace();
    wc::RosterPreview preview;
    if (previewable)
    {
        preview = wc::PreviewRosterCommand(m.Definitions(), before, c);
        Check(m.Namespace() == space && s.gold == before.gold && s.revision == before.revision &&
              s.shop == before.shop && s.roster.size() == before.roster.size() &&
              s.shopRng.state == before.shopRng.state && s.botRng.state == before.botRng.state,
              "Inventory preview must not mutate live economy, RNG, namespace or revision");
    }
    const auto reply = m.Submit(seat, c);
    if (previewable)
    {
        const auto &actual = m.Seats()[seat];
        Check(preview.accepted == reply.accepted, "Preview acceptance matches real submitted command");
        Check(preview.resulting.gold == actual.gold && preview.resulting.shop == actual.shop &&
              preview.resulting.roster.size() == actual.roster.size(), "Preview economy and roster match authority");
        wc::Id allocated = 0;
        for (const auto &u : actual.roster)
            if (std::none_of(before.roster.begin(), before.roster.end(),
                             [&](const wc::OwnedUnit &old) { return old.id == u.id; })) allocated = u.id;
        for (auto expected : preview.resulting.roster)
        {
            if (preview.hypotheticalId && expected.id == preview.hypotheticalId) expected.id = allocated;
            const auto found = std::find_if(actual.roster.begin(), actual.roster.end(),
                                           [&](const wc::OwnedUnit &u) { return u.id == expected.id; });
            Check(found != actual.roster.end(), "Preview preserves survivor identities");
            Check(std::tie(found->definition, found->star, found->onBoard, found->cell.column,
                           found->cell.row, found->bench) ==
                  std::tie(expected.definition, expected.star, expected.onBoard, expected.cell.column,
                           expected.cell.row, expected.bench), "Preview stars and destinations match authority");
        }
        if (!reply.accepted)
            Check(preview.mergeSteps.empty() && preview.hypotheticalId == 0,
                  "Rejected preview has no fabricated completed merge");
    }
    return reply;
}
void RunCombat(wc::Combat &combat)
{
    while (!combat.Result().complete)
    {
        combat.Tick();
        Check(combat.InvariantError().empty(), "Combat occupancy or numeric invariant");
    }
    Check(combat.Result().ticks <= 800, "Combat exceeded timeout");
}
void Numeric(const wc::Catalog &c)
{
    Check(c.Validate().empty(), "Canonical catalog validation");
    Check(wc::ResolveDamage(12000, wc::DamageType::Physical, 50, 0) == 8000, "Physical mitigation");
    Check(wc::ResolveDamage(12000, wc::DamageType::Magic, 0, 20) == 10000, "Magic mitigation");
    Check(wc::ResolveDamage(9000, wc::DamageType::True, 999, 999) == 9000, "True bypass");
    Check(wc::ResolveDamage(10000, wc::DamageType::Physical, 25, 0, 2500) == 10000, "Additive source bonus");
    Check(wc::StarValue(100000, 2, 2500, c.rules) == 225000, "Star plus maximum health");
    Check(wc::AttackInterval(800, 2500, c.rules) == 20, "Rate additivity");
    Check(wc::EncounterCell({1, 3}, 1, c.rules) == wc::Cell{6, 4}, "Rotate both board axes");
}
void Commands(const wc::Catalog &c)
{
    wc::Match m(c, 11, 1);
    auto &s = m.Seats()[0];
    wc::Command buy;
    buy.type = wc::CommandType::Buy;
    buy.seat = 0;
    buy.slot = 0;
    buy.requestId = 7;
    buy.sequence = s.sequence + 1;
    buy.revision = s.revision;
    const int price = c.units[s.shop[0]].cost, gold = s.gold;
    Check(!m.Submit(1, buy).accepted, "Authentication rejection");
    auto accepted = m.Submit(0, buy);
    Check(accepted.accepted, "Purchase accepted");
    Check(m.Seats()[0].gold == gold - price, "Purchase pays authored price");
    Check(m.Submit(0, buy).accepted && m.Seats()[0].gold == gold - price, "Idempotent retransmission");
    buy.slot = 1;
    Check(!m.Submit(0, buy).accepted, "Request payload reuse rejected");
    Check(Send(m, 0, wc::CommandType::Ready).accepted, "Ready accepted");
    wc::Id unit = m.Seats()[0].roster[0].id;
    Check(Send(m, 0, wc::CommandType::Move, -1, unit, true, {2, 3}).accepted, "Deploy accepted");
    Check(!m.Seats()[0].ready, "Editing clears ready");
    int currentGold = m.Seats()[0].gold;
    Check(!Send(m, 0, wc::CommandType::Move, -1, unit, true, {2, 4}).accepted,
          "Opponent preparation destination rejected");
    Check(m.Seats()[0].gold == currentGold && m.Seats()[0].roster[0].cell == wc::Cell{2, 3},
          "Rejected transaction preserves state");
    Check(Send(m, 0, wc::CommandType::ToggleLock).accepted, "Shop lock accepted");
    Check(Send(m, 0, wc::CommandType::Reroll).accepted && !m.Seats()[0].shopLocked,
          "Paid reroll clears lock");
    Check(Send(m, 0, wc::CommandType::Sell, -1, unit).accepted, "Sale accepted");
    Check(m.InvariantError().empty(), "Command invariants");
    m.TakeOver(0);
    Check(!m.Seats()[0].human && m.Seats()[0].takeover, "Human takeover retains seat");
    m.Restart(11, 1);
    Check(m.Seats()[0].roster.empty() && m.Seats()[0].gold == c.rules.startingGold && m.Seats()[0].human,
          "Restart resets roster/economy/controllers");
}
int Offer(wc::Match &m, int definition)
{
    for (int rerolls = 0; rerolls < 200; ++rerolls)
    {
        for (int i = 0; i < int(m.Seats()[0].shop.size()); ++i)
            if (m.Seats()[0].shop[i] == definition)
                return i;
        Check(Send(m, 0, wc::CommandType::Reroll).accepted, "Fixture reroll");
    }
    throw std::runtime_error("Fixture could not draw requested offer");
}
void MergesAndEconomy(const wc::Catalog &canonical)
{
    auto c = canonical;
    c.rules.startingGold = 10000;
    for (auto &u : c.units)
        u.cost = 1;
    for (auto &entry : c.rules.shopWeights)
        entry.second = {10000, 0, 0};
    wc::Match m(c, 45, 1);
    Check(Send(m, 0, wc::CommandType::Buy, Offer(m, 0)).accepted, "First owned merge member");
    auto survivor = m.Seats()[0].roster.front();
    Check(Send(m, 0, wc::CommandType::Move, -1, survivor.id, true, {1, 3}).accepted,
          "Deployed merge survivor");
    for (int i = 1; i < 9; ++i)
    {
        const int slot = Offer(m, 0);
        wc::Command purchase; purchase.type = wc::CommandType::Buy; purchase.slot = slot;
        const auto projection = wc::PreviewRosterCommand(c, m.Seats()[0], purchase);
        if (i == 8)
        {
            Check(projection.mergeSteps.size() == 2, "Ninth-copy preview explains both cascade steps");
            Check(projection.mergeSteps[0].fromStar == 1 && projection.mergeSteps[0].toStar == 2 &&
                  projection.mergeSteps[1].fromStar == 2 && projection.mergeSteps[1].toStar == 3 &&
                  projection.mergeSteps[1].survivorId == survivor.id,
                  "Cascade preview preserves deployed survivor and upgrade order");
        }
        Check(Send(m, 0, wc::CommandType::Buy, slot).accepted, "Three-level merge purchase");
    }
    Check(m.Seats()[0].roster.size() == 1, "Nine copies become one instance");
    Check(m.Seats()[0].roster[0].id == survivor.id && m.Seats()[0].roster[0].star == 3 &&
              m.Seats()[0].roster[0].cell == wc::Cell{1, 3},
          "Nested merge preserves deployed identity and location");
    int beforeSell = m.Seats()[0].gold;
    Check(Send(m, 0, wc::CommandType::Sell, -1, survivor.id).accepted && m.Seats()[0].gold == beforeSell + 9,
          "Three-star sale conserves purchased value");
    m.Restart(45, 1);
    for (int definition : {0, 0, 1, 2, 3, 4, 5, 6})
        Check(Send(m, 0, wc::CommandType::Buy, Offer(m, definition)).accepted, "Fill legal bench");
    Check(m.Seats()[0].roster.size() == 8, "Fixed eight-slot bench");
    int slot = Offer(m, 7);
    int gold = m.Seats()[0].gold;
    auto shop = m.Seats()[0].shop;
    Check(!Send(m, 0, wc::CommandType::Buy, slot).accepted, "Full bench unmerged purchase rejects");
    Check(m.Seats()[0].gold == gold && m.Seats()[0].shop == shop && m.Seats()[0].roster.size() == 8,
          "Full-bench rejection atomic");
    slot = Offer(m, 0);
    auto oldest = m.Seats()[0].roster.front();
    Check(Send(m, 0, wc::CommandType::Buy, slot).accepted, "Full bench transaction-local merge succeeds");
    Check(m.Seats()[0].roster.size() == 7 && m.Seats()[0].roster.front().id == oldest.id &&
              m.Seats()[0].roster.front().bench == oldest.bench && m.Seats()[0].roster.front().star == 2,
          "Full bench merge identity and legal location");
    for (int i = 0; i < 3; ++i)
        Check(Send(m, 0, wc::CommandType::Move, -1, m.Seats()[0].roster[i].id, true, {i, 3}).accepted,
              "Deploy to level cap");
    auto benchUnit = m.Seats()[0].roster[3];
    Check(!Send(m, 0, wc::CommandType::Move, -1, benchUnit.id, true, {4, 3}).accepted,
          "Deployment above level rejected");
    Check(Send(m, 0, wc::CommandType::Move, -1, benchUnit.id, true, {0, 3}).accepted,
          "Bench to full-board occupied destination swaps atomically");
    Check(m.InvariantError().empty(), "Merge and swap invariants");
    while (m.Seats()[0].level < c.rules.maximumLevel)
        Check(Send(m, 0, wc::CommandType::BuyXp).accepted, "XP leveling accepted");
    gold = m.Seats()[0].gold;
    Check(!Send(m, 0, wc::CommandType::BuyXp).accepted && m.Seats()[0].gold == gold && m.Seats()[0].xp == 0,
          "XP at cap rejects without cost");
    wc::Match lock(canonical, 15, 1);
    Check(Send(lock, 0, wc::CommandType::Buy, 0).accepted, "Locked empty offer setup");
    Check(Send(lock, 0, wc::CommandType::ToggleLock).accepted, "Lock remaining offers");
    auto lockedOffers = lock.Seats()[0].shop;
    int lockGold = lock.Seats()[0].gold;
    Check(Send(lock, 0, wc::CommandType::Ready).accepted, "Ready locked shop");
    while (lock.Round() == 1)
    {
        lock.Tick(50);
        if (lock.CurrentPhase() == wc::Phase::Combat)
            Check(!Send(lock, 0, wc::CommandType::Sell, -1, lock.Seats()[0].roster.front().id).accepted,
                  "Combat sale rejects");
    }
    Check(lock.Seats()[0].shop == lockedOffers && lock.Seats()[0].shop[0] == -1,
          "Lock preserves remaining offers and empty slots");
    Check(lock.Seats()[0].gold ==
              lockGold + canonical.rules.baseIncome +
                  std::min(canonical.rules.interestCap, lockGold / canonical.rules.interestDivisor),
          "Next preparation uses snapshotted interest and no loss bonus");
    Check(lock.Seats()[0].xp == canonical.rules.passiveXp, "Survivor receives passive XP");
}
void PreviewIsolation(const wc::Catalog &catalog)
{
    wc::Match before(catalog, 17, 1);
    const auto owner = before.Seats()[0];
    wc::Command buy; buy.type = wc::CommandType::Buy; buy.slot = 0;
    for (int i = 0; i < 32; ++i)
        Check(wc::PreviewRosterCommand(catalog, owner, buy).accepted, "Repeated first-buy previews are stable");
    wc::Match after(catalog, 17, 1);
    Check(after.Namespace() == before.Namespace() + 1 && after.Seats()[0].shop == owner.shop,
          "Previews allocate no match namespaces and do not change seeded shops");
    auto invalid = owner;
    invalid.shop[0] = int(catalog.units.size());
    Check(!wc::PreviewRosterCommand(catalog, invalid, buy).accepted,
          "Malformed private offer is rejected without indexing outside definitions");
    invalid = owner; invalid.gold = 0;
    const auto poor = wc::PreviewRosterCommand(catalog, invalid, buy);
    Check(!poor.accepted && poor.resulting.gold == 0 && poor.resulting.shop == invalid.shop,
          "Unaffordable preview preserves offers and gold");
    wc::Command reroll; reroll.type = wc::CommandType::Reroll;
    const auto unsupported = wc::PreviewRosterCommand(catalog, owner, reroll);
    Check(!unsupported.accepted && unsupported.resulting.shopRng.state == owner.shopRng.state,
          "Inventory preview cannot speculate hidden reroll RNG");
}
void EffectFixtures(const wc::Catalog &canonical, int star)
{
    auto c = canonical;
    for (auto &u : c.units)
    {
        u.ability.firstCastMs = 100000;
        u.attackDamage = 100;
        u.health = 1000000;
        u.armor = 0;
        u.resistance = 0;
    }
    for (int def = 0; def < int(c.units.size()); ++def)
    {
        auto local = c;
        local.units[def].ability = canonical.units[def].ability;
        std::vector<wc::OwnedUnit> a{Unit(1, def, 3, def == 11 ? 0 : 3, star), Unit(2, 1, 2, 3)};
        std::vector<wc::OwnedUnit> b{Unit(3, 0, 4, 3), Unit(4, 3, 3, 3)};
        wc::Combat combat(local, a, b, 123 + def);
        RunCombat(combat);
        bool saw = false;
        for (const auto &e : combat.Events())
        {
            if (e.source == 1)
            {
                const auto& d = canonical.units[def];
                const bool declared = std::any_of(d.ability.effects.begin(), d.ability.effects.end(),
                    [&](const wc::AbilityEffect &fx) { return fx.effect == e.effect && fx.damageType == e.damageType; });
                Check(e.basicAttack ? e.damageType == d.damageType : declared ||
                      (d.ability.effects.empty() && e.damageType == d.ability.damageType),
                      "Released event carries its actual basic or skill damage type");
                Check(e.radius == (e.basicAttack ? 0 : d.ability.radius),
                      "Released event carries actual authored radius");
                Check(e.basicAttack ? e.effect == wc::Effect::Damage : declared || e.effect == d.ability.effect,
                      "Event distinguishes basic attack from authored skill");
            }
            if (e.source == 1 && !e.basicAttack && e.effect == canonical.units[def].ability.effect && e.action > 0 &&
                (e.effect == wc::Effect::Dash || e.resolved != 0))
                saw = true;
        }
        Check(saw, ("Authored ability executed: " + canonical.units[def].id).c_str());
    }
    auto duel = c;
    duel.units[0].health = 10000;
    duel.units[0].attackDamage = 10000;
    duel.units[0].projectileTravelMs = 200;
    duel.units[0].range = 8;
    duel.units[0].attackWindupMs = 50;
    wc::Combat simultaneous(duel, {Unit(1, 0, 0, 0)}, {Unit(2, 0, 0, 0)}, 7);
    RunCombat(simultaneous);
    Check(simultaneous.Result().winner == -1 && simultaneous.Result().survivors[0] == 0 &&
              simultaneous.Result().survivors[1] == 0,
          "Released packets survive source defeat and draw");
    wc::Combat empty(c, {}, {}, 1);
    Check(empty.Result().complete && empty.Result().winner == -1, "Empty encounter immediate draw");
    wc::Combat one(c, {Unit(1, 0, 0, 0)}, {}, 1);
    Check(one.Result().complete && one.Result().winner == 0, "Empty opponent ordinary loss");
    auto traits = canonical;
    wc::Combat distinct(traits, {Unit(1, 0, 3, 3), Unit(2, 1, 2, 3)}, {Unit(3, 0, 3, 3)}, 1);
    Check(distinct.Units()[0].maxHealth == 115500, "Two distinct humans activate health trait");
    wc::Combat duplicate(traits, {Unit(1, 0, 3, 3), Unit(2, 0, 2, 3)}, {Unit(3, 0, 3, 3)}, 1);
    Check(duplicate.Units()[0].maxHealth == 105000, "Duplicate definitions do not activate trait");
}
void AllEmpty(const wc::Catalog &canonical)
{
    auto c = canonical;
    c.rules.startingGold = 0;
    c.rules.startingHealth = 2;
    c.rules.baseIncome = 0; c.rules.passiveXp = 0;
    wc::Match m(c, 987, 0);
    for (int i = 0; i < 5000 && m.CurrentPhase() != wc::Phase::Finished; ++i)
        m.Tick(50);
    Check(m.CurrentPhase() == wc::Phase::Finished, "Zero survivors finishes");
    for (const auto &s : m.Seats())
        Check(s.health == 0 && s.placement == 1 && s.gold == 0 && s.xp == 0,
              "Simultaneous shared first has no final income");
}
void OrderingAndRestart(const wc::Catalog &canonical)
{
    auto c = canonical;
    for (auto &u : c.units) u.ability.effects.clear();
    c.traits.clear();
    for (auto &unit : c.units)
    {
        unit.ability.firstCastMs = 100000;
        unit.health = 10000;
        unit.attackDamage = 10000;
        unit.armor = unit.resistance = 0;
        unit.range = 8;
        unit.attackWindupMs = 50;
        unit.projectileTravelMs = 0;
    }
    c.units[0].projectileTravelMs = 200;
    c.units[1].attackWindupMs = 100;
    wc::Combat drain(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 92);
    RunCombat(drain);
    Check(drain.Result().winner == -1 && drain.Result().ticks == 6,
          "Dead caster projectile drains before finalizing winner");
    auto &shield = c.units[0];
    shield.health = 100000;
    shield.attackDamage = 0;
    shield.ability = canonical.units[0].ability;
    shield.ability.effects.clear();
    shield.ability.firstCastMs = 0;
    shield.ability.castMs = 50;
    shield.ability.durationMs = 100;
    shield.ability.magnitude = {3000, 3000, 3000};
    c.units[1].attackDamage = 5000;
    c.units[1].attackWindupMs = 150;
    wc::Combat expiry(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 9);
    for (int tick = 0; tick < 4; ++tick)
        expiry.Tick();
    bool expiredBeforeImpact = false;
    for (const auto &event : expiry.Events())
        if (event.tick == 4 && event.target == 1 && event.effect == wc::Effect::Damage)
            expiredBeforeImpact = event.absorbed == 0 && event.healthLoss == 5000;
    Check(expiredBeforeImpact, "Shields expire before impacts on their expiry tick");
    c.units[0].health = 10000;
    auto &stun = c.units[0].ability;
    stun.effect = wc::Effect::Stun;
    stun.selector = wc::Selector::CurrentEnemy;
    stun.range = 8;
    stun.durationMs = 1000;
    stun.magnitude = {0, 0, 0};
    c.units[1].attackDamage = 10000;
    c.units[1].attackWindupMs = 50;
    wc::Combat releasedBeforeStun(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 1234);
    releasedBeforeStun.Tick();
    releasedBeforeStun.Tick();
    bool sawStun = false, sawDamage = false;
    for (const auto &event : releasedBeforeStun.Events())
    {
        sawStun |= event.tick == 2 && event.effect == wc::Effect::Stun;
        sawDamage |= event.tick == 2 && event.target == 1 && event.healthLoss == 10000;
    }
    Check(sawStun && sawDamage, "Same-tick stun cannot recall materialized release");
    c.units[1].attackWindupMs = 150;
    wc::Combat interrupted(c, {Unit(1, 0, 0, 0)}, {Unit(2, 1, 0, 0)}, 55);
    for (int tick = 0; tick < 8; ++tick)
        interrupted.Tick();
    Check(interrupted.Units()[0].health == 10000, "Stun cancels unreleased windup");
    wc::Match restart(canonical, 1, 1);
    wc::Command stale;
    stale.type = wc::CommandType::Buy;
    stale.seat = 0;
    stale.slot = 0;
    stale.requestId = 123;
    stale.sequence = 1;
    stale.revision = restart.Seats()[0].revision;
    const auto name = restart.Namespace();
    restart.Restart(1, 1);
    Check(restart.Namespace() != name && !restart.Submit(0, stale).accepted,
          "Restart namespace rejects prior in-flight command");
}
void Mirrors(const wc::Catalog &c)
{
    std::vector<wc::OwnedUnit> a, b;
    for (int i = 0; i < 6; ++i)
    {
        a.push_back(Unit(i + 1, i, 2 + i % 3, i < 3 ? 3 : 1, 2));
        b.push_back(Unit(i + 7, i + 6, 2 + i % 3, i < 3 ? 3 : 1, 2));
    }
    std::ofstream output("mirror-combats.csv");
    output << "seed,original_winner,swapped_winner,original_ticks,swapped_ticks,team_outcome_changed\n";
    int changes = 0;
    for (int seed = 1; seed <= 32; ++seed)
    {
        wc::Combat forward(c, a, b, seed), reverse(c, b, a, seed);
        RunCombat(forward);
        RunCombat(reverse);
        const int translated = reverse.Result().winner < 0 ? -1 : 1 - reverse.Result().winner;
        bool changed = forward.Result().winner != translated;
        changes += changed ? 1 : 0;
        output << seed << ',' << forward.Result().winner << ',' << reverse.Result().winner << ','
               << forward.Result().ticks << ',' << reverse.Result().ticks << ',' << changed << '\n';
    }
    std::cout << "mirror_pairs=32 outcome_changes=" << changes
              << " (measured ordering sensitivity, not fairness certification)\n";
}
void CheckEncounterSummaries(const wc::Match &match)
{
    const auto &record = match.Records().back();
    Check(record.encounters.size() == match.Encounters().size(), "One retained summary per actual encounter");
    for (std::size_t i = 0; i < record.encounters.size(); ++i)
    {
        const auto &summary = record.encounters[i];
        const auto &encounter = match.Encounters()[i];
        const auto &result = encounter.combat.Result();
        Check(summary.pairing.a == encounter.pairing.a && summary.pairing.b == encounter.pairing.b &&
                  summary.pairing.ghost == encounter.pairing.ghost, "Retained encounter pairing");
        Check(summary.result.complete == result.complete && summary.result.timeout == result.timeout &&
                  summary.result.winner == result.winner && summary.result.ticks == result.ticks &&
                  summary.result.survivors == result.survivors, "Retained actual result");
        std::array<wc::Int, 2> loss{}, absorbed{}, healed{};
        for (const auto &unit : encounter.combat.Units())
            for (const auto &event : encounter.combat.Events())
                if (event.target == unit.id)
                {
                    loss[unit.side] += event.healthLoss;
                    absorbed[unit.side] += event.absorbed;
                    if (event.effect == wc::Effect::Heal)
                        healed[unit.side] += event.resolved;
                }
        Check(summary.healthLoss == loss && summary.absorbed == absorbed && summary.healing == healed,
              "Retained totals recompute from live events by actual target-side IDs");
    }
}
void RetainedRecapAcrossHitch(const wc::Catalog &c)
{
    wc::Match match(c, 1, 0);
    while (match.Records().empty() && match.ElapsedMs() < 100000)
        match.Tick(50);
    Check(!match.Records().empty() && match.CurrentPhase() == wc::Phase::Settlement,
          "Actual first settlement reached for retained recap fixture");
    CheckEncounterSummaries(match);
    const auto record = match.Records().back();
    match.Tick(c.rules.settlementMs + 50);
    Check(match.CurrentPhase() == wc::Phase::Preparation && match.Round() == record.round + 1 &&
              match.Encounters().empty(), "Hitch advances through settlement and clears live encounter state");
    const auto &retained = match.Records().back();
    Check(retained.round == record.round && retained.preHash == record.preHash && retained.postHash == record.postHash &&
              retained.damage == record.damage && retained.health == record.health &&
              retained.encounters.size() == record.encounters.size(), "Prior settled outcome retained across hitch");
    for (std::size_t i = 0; i < record.encounters.size(); ++i)
        Check(retained.encounters[i].healthLoss == record.encounters[i].healthLoss &&
                  retained.encounters[i].absorbed == record.encounters[i].absorbed &&
                  retained.encounters[i].healing == record.encounters[i].healing &&
                  retained.encounters[i].result.ticks == record.encounters[i].result.ticks,
              "Prior encounter totals remain available when no live encounter exists");
}
void Tournament(const wc::Catalog &c, int count)
{
    std::ofstream output("tournaments.csv");
    output << "seed,rounds,simulated_ms,wall_ms,winner_seats,timeouts,encounters,combat_events,bot_commands,"
              "bot_rejects,ghosts,final_hash,idle_unit_ms,stunned_unit_ms\n";
    std::ofstream rounds("round-economy.csv"), compositions("compositions.csv"),
        decisions("bot-decisions.csv");
    rounds << "seed,round,seat,health,gold,damage,wins,placement,settlement_id,pre_hash,post_hash,pvp_round_index,neutral,pending_reward\n";
    compositions << "seed,round,seat,level,gold,unit_id,definition,star,on_board,column,row,bench\n";
    decisions << "seed,round,seat,observation_revision,action,score,deployment_gain,upgrade_gain,trait_gain,"
                 "role_gain,pair_gain,gold_spent,interest_loss,bench_pressure,accepted,gold_after\n";
    std::ofstream outcomes("encounter-outcomes.csv"), skills("ability-coverage.csv"), tiers("trait-coverage.csv");
    outcomes << "seed,round,pvp_round_index,kind,wave_id,seat_a,seat_b,winner,ticks,timeout,survivors_a,survivors_b\n";
    skills << "seed,round,definition,star,effect,events\n";
    tiers << "seed,round,seat,trait,count,value\n";
    std::set<int> activeCounts;
    int timeoutTotal = 0, eventTotal = 0, ghostTotal = 0;
    for (int seed = 0; seed < count; ++seed)
    {
        auto started = std::chrono::steady_clock::now();
        wc::Match m(c, wc::Id(seed + 1), 0);
        int events = 0, oldRecords = 0, capturedRound = 0;
        std::int64_t idleUnitMs = 0, stunnedUnitMs = 0;
        while (m.CurrentPhase() != wc::Phase::Finished && m.CurrentPhase() != wc::Phase::Aborted &&
               m.ElapsedMs() < 4000000)
        {
            m.Tick(50);
            Check(m.InvariantError().empty(), "Tournament invariant");
            if (m.CurrentPhase() == wc::Phase::Combat)
            {
                for (const auto &encounter : m.Encounters())
                    if (!encounter.combat.Result().complete)
                        for (const auto &unit : encounter.combat.Units())
                            if (unit.health > 0)
                            {
                                if (unit.state == wc::ActionState::Idle ||
                                    unit.state == wc::ActionState::Seeking ||
                                    (unit.state == wc::ActionState::AttackRecovery && unit.target < 0))
                                    idleUnitMs += 50;
                                if (unit.state == wc::ActionState::Stunned)
                                    stunnedUnitMs += 50;
                            }
                if (capturedRound != m.Round())
                {
                    capturedRound = m.Round();
                    for (const auto &seat : m.Seats())
                        if (seat.health > 0)
                            for (const auto &unit : seat.roster)
                                compositions << seed + 1 << ',' << m.Round() << ',' << seat.id << ','
                                             << seat.level << ',' << seat.gold << ',' << unit.id << ','
                                             << c.units[unit.definition].id << ',' << unit.star << ','
                                             << unit.onBoard << ',' << unit.cell.column << ','
                                             << unit.cell.row << ',' << unit.bench << '\n';
                }
            }
            if (m.CurrentPhase() == wc::Phase::Preparation)
            {
                int active = int(std::count_if(m.Seats().begin(), m.Seats().end(),
                                               [](const wc::SeatState &s) { return s.health > 0; }));
                activeCounts.insert(active);
            }
            if (int(m.Records().size()) > oldRecords)
            {
                CheckEncounterSummaries(m);
                for (const auto &e : m.Encounters())
                {
                    events += int(e.combat.Events().size());
                    const auto &result=e.combat.Result();
                    outcomes << seed+1 << ',' << m.Round() << ',' << m.PvpRoundIndex() << ',' << int(e.kind)
                        << ',' << e.pairing.waveId << ',' << e.pairing.a << ',' << e.pairing.b << ',' << result.winner
                        << ',' << result.ticks << ',' << result.timeout << ',' << result.survivors[0] << ',' << result.survivors[1] << '\n';
                    std::map<std::tuple<std::string,int,int>,int> counts;
                    for (const auto &unit:e.combat.Units())
                        for (const auto &event:e.combat.Events())
                            if (event.source==unit.id && !event.basicAttack)
                                ++counts[{c.Definition(unit.definition,unit.neutral).id,unit.star,int(event.effect)}];
                    for(const auto &entry:counts) skills << seed+1 << ',' << m.Round() << ',' << std::get<0>(entry.first)
                        << ',' << std::get<1>(entry.first) << ',' << std::get<2>(entry.first) << ',' << entry.second << '\n';
                }
                for(const auto &seat:m.Seats())
                {
                    std::map<std::string,std::set<int>> counts;
                    for(const auto &unit:seat.roster) if(unit.onBoard)
                    {
                        counts[c.units[unit.definition].race].insert(unit.definition);
                        counts[c.units[unit.definition].unitClass].insert(unit.definition);
                    }
                    for(const auto &trait:c.traits) if(!counts[trait.id].empty())
                        tiers << seed+1 << ',' << m.Round() << ',' << seat.id << ',' << trait.id << ','
                            << counts[trait.id].size() << ',' << wc::TraitValue(trait,int(counts[trait.id].size())) << '\n';
                }
                oldRecords = int(m.Records().size());
            }
        }
        Check(m.CurrentPhase() == wc::Phase::Finished, "Actual all-bot combat tournament finishes");
        Check(m.Round() <= c.rules.maxRounds, "Tournament round cap");
        int timeouts = 0, encounters = 0, ghosts = 0, rejects = 0;
        for (const auto &r : m.Records())
        {
            for (int seat = 0; seat < 8; ++seat)
                rounds << seed + 1 << ',' << r.round << ',' << seat << ',' << r.health[seat] << ','
                       << r.gold[seat] << ',' << r.damage[seat] << ',' << r.wins[seat] << ','
                       << r.placement[seat] << ',' << r.settlementId << ',' << r.preHash << ',' << r.postHash
                       << ',' << r.pvpRoundIndex << ',' << r.neutral << ',' << r.pendingRewards[seat] << '\n';
            for (const auto &result : r.results)
            {
                ++encounters;
                timeouts += result.timeout ? 1 : 0;
            }
            for (auto p : r.pairs)
                ghosts += p.ghost ? 1 : 0;
        }
        std::map<std::pair<int, int>, int> commands, rerolls;
        for (const auto &l : m.BotLog())
        {
            rejects += l.reply.accepted ? 0 : 1;
            ++commands[{l.round, l.seat}];
            if (l.action == "bounded_reroll")
                ++rerolls[{l.round, l.seat}];
            decisions << seed + 1 << ',' << l.round << ',' << l.seat << ',' << l.observationRevision << ','
                      << l.action << ',' << l.score;
            for (double feature : l.features)
            {
                Check(feature >= -1.0 && feature <= 1.0, "Bot features stay normalized");
                decisions << ',' << feature;
            }
            decisions << ',' << l.reply.accepted << ',' << l.goldAfter << '\n';
        }
        for (const auto &entry : commands)
            Check(entry.second <= c.bots[m.Seats()[entry.first.second].botIndex].maxCommands,
                  "Bot command cap includes ready");
        for (const auto &entry : rerolls)
            Check(entry.second <= c.bots[m.Seats()[entry.first.second].botIndex].maxRerolls,
                  "Bot reroll cap");
        Check(rejects == 0, "Bots submit legal commands");
        int winners = 0;
        for (const auto &s : m.Seats())
            if (s.placement == 1)
                ++winners;
        Check(winners > 0, "Final winner or shared rank exists");
        auto wall =
            std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - started)
                .count();
        output << seed + 1 << ',' << m.Round() << ',' << m.ElapsedMs() << ',' << wall << ',' << winners << ','
               << timeouts << ',' << encounters << ',' << events << ',' << m.BotLog().size() << ',' << rejects
               << ',' << ghosts << ',' << m.Records().back().postHash << ',' << idleUnitMs << ','
               << stunnedUnitMs << '\n';
        output.flush();
        timeoutTotal += timeouts;
        eventTotal += events;
        ghostTotal += ghosts;
        std::cout << "tournament seed=" << seed + 1 << " rounds=" << m.Round() << " encounters=" << encounters
                  << " events=" << events << " timeouts=" << timeouts << " simulated_ms=" << m.ElapsedMs()
                  << " wall_ms=" << wall << std::endl;
        if (seed == 0)
        {
            wc::Match replay(c, 1, 0);
            while (replay.CurrentPhase() != wc::Phase::Finished)
                replay.Tick(50);
            Check(replay.Records().back().postHash == m.Records().back().postHash &&
                      replay.ElapsedMs() == m.ElapsedMs(),
                  "Same build seeded tournament replay");
        }
    }
    std::cout << "aggregate tournaments=" << count << " events=" << eventTotal << " timeouts=" << timeoutTotal
              << " ghosts=" << ghostTotal << " observed_active_counts=";
    for (int active : activeCounts)
        std::cout << active << ' ';
    std::cout << '\n';
    if (count >= 100)
        for (int active = 2; active <= 8; ++active)
            Check(activeCounts.count(active) > 0, "All active-seat counts exercised by actual tournaments");
}
#include "update_contract_tests.h"
} // namespace
int main(int argc, char **argv)
{
    try
    {
        auto catalog = FixtureCatalog();
        Numeric(catalog);
        Commands(catalog);
        MergesAndEconomy(catalog);
        PreviewIsolation(catalog);
        for (int star = 1; star <= 3; ++star) EffectFixtures(catalog, star);
        UpdatedSkills(catalog);
        UpdatedVisualActions(catalog);
        UpdatedTournament(catalog);
        UpdatedBotSkillPurchases(catalog);
        AllEmpty(catalog);
        OrderingAndRestart(catalog);
        RetainedRecapAcrossHitch(catalog);
        Mirrors(catalog);
        Tournament(catalog, argc > 1 ? std::stoi(argv[1]) : 1);
        std::cout << "PASS assertions=" << assertions << " data_digest=" << catalog.contentDigest << '\n';
        return 0;
    }
    catch (const std::exception &e)
    {
        std::cerr << "FAIL after assertions=" << assertions << ": " << e.what() << '\n';
        return 1;
    }
}
