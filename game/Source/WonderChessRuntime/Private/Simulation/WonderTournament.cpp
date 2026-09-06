#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <atomic>
#include <cmath>
#include <functional>
#include <numeric>
#include <set>
#include <tuple>

namespace wc
{
namespace
{
std::atomic<Id> NextMatchNamespace{1};
Id HashValue(Id n)
{
    n += 0x9e3779b97f4a7c15ULL;
    n = (n ^ (n >> 30)) * 0xbf58476d1ce4e5b9ULL;
    n = (n ^ (n >> 27)) * 0x94d049bb133111ebULL;
    return n ^ (n >> 31);
}
std::pair<int, int> Key(int a, int b)
{
    return {std::min(a, b), std::max(a, b)};
}
int CountCopies(int star)
{
    return star == 3 ? 9 : star == 2 ? 3 : 1;
}
bool EqualCommand(const Command &a, const Command &b)
{
    return std::tie(a.type, a.seat, a.requestId, a.sequence, a.revision, a.unit, a.slot, a.toBoard,
                    a.cell.column, a.cell.row) == std::tie(b.type, b.seat, b.requestId, b.sequence,
                                                           b.revision, b.unit, b.slot, b.toBoard,
                                                           b.cell.column, b.cell.row);
}
struct Features
{
    double budget = 0, upgrades = 0, traits = 0, pairs = 0, roles = 0, bench = 0;
};
Features Evaluate(const SeatState &s, const Catalog &c, const BotDef &b)
{
    Features f;
    std::vector<std::pair<double, const OwnedUnit *>> choices;
    std::map<int, int> copies;
    for (const auto &u : s.roster)
    {
        const auto &d = c.units[u.definition];
        double weight = d.unitClass == "guardian" ? b.frontline
                        : d.unitClass == "priest" ? b.support
                                                  : b.damage;
        double budget = (double(StarValue(d.health, u.star, 0, c.rules)) / 100000.0 +
                         double(StarValue(d.attackDamage, u.star, 0, c.rules)) * d.attackRate / 10000000.0) *
                        weight;
        choices.push_back({budget, &u});
        copies[u.definition] += CountCopies(u.star);
        f.upgrades += u.star == 3 ? 1.0 : u.star == 2 ? 1.0 / 3.0 : 0.0;
        if (!u.onBoard)
            f.bench += 1.0 / c.rules.benchCapacity;
    }
    std::stable_sort(choices.begin(), choices.end(),
                     [](const auto &a, const auto &b) { return a.first > b.first; });
    std::map<std::string, std::set<int>> counts;
    bool frontline = false, damage = false, support = false;
    for (int i = 0; i < std::min(s.level, int(choices.size())); ++i)
    {
        auto &u = *choices[i].second;
        auto &d = c.units[u.definition];
        f.budget += choices[i].first;
        counts[d.race].insert(u.definition);
        counts[d.unitClass].insert(u.definition);
        frontline |= d.unitClass == "guardian" || d.unitClass == "warrior";
        support |= d.unitClass == "priest";
        damage |= d.unitClass == "ranger" || d.unitClass == "mage" || d.unitClass == "rogue";
    }
    for (const auto &t : c.traits)
        if (int(counts[t.id].size()) >= t.threshold)
            f.traits += 1.0 / 6.0;
    for (auto pair : copies)
        f.pairs += std::min(2, pair.second % 3) / 6.0;
    f.roles = (frontline ? 0.6 : 0) + (damage ? 0.3 : 0) + (support ? 0.1 : 0);
    return f;
}
double TacticalScore(const SeatState &seat, const PublicSeat *opponent, const Catalog &catalog)
{
    double score = 0;
    int deployed = 0;
    for (const auto &unit : seat.roster)
    {
        if (!unit.onBoard)
            continue;
        ++deployed;
        const auto &definition = catalog.units[unit.definition];
        const bool frontline = definition.unitClass == "guardian" || definition.unitClass == "warrior";
        if (frontline)
            score += double(unit.cell.row) / 3.0;
        else if (definition.unitClass == "priest")
        {
            int supportRecipients = 0;
            for (const auto &ally : seat.roster)
                if (ally.onBoard && ally.id != unit.id &&
                    Distance(unit.cell, ally.cell) <= definition.ability.range)
                    ++supportRecipients;
            score += std::min(3, supportRecipients) / 3.0;
        }
        else if (definition.range > 1)
        {
            score += double(3 - unit.cell.row) / 3.0;
            for (const auto &ally : seat.roster)
                if (ally.onBoard && ally.cell.row > unit.cell.row &&
                    std::abs(ally.cell.column - unit.cell.column) <= 1 &&
                    (catalog.units[ally.definition].unitClass == "guardian" ||
                     catalog.units[ally.definition].unitClass == "warrior"))
                {
                    score += 0.4;
                    break;
                }
            if (definition.ability.selector == Selector::RetreatFromCurrentEnemy && unit.cell.row > 0)
            {
                Cell retreat{unit.cell.column, unit.cell.row - 1};
                if (std::none_of(seat.roster.begin(), seat.roster.end(),
                                 [&](const OwnedUnit &ally) { return ally.onBoard && ally.cell == retreat; }))
                    score += 0.5;
            }
        }
        if (opponent && !opponent->deployment.empty())
        {
            int closestColumn = 8;
            bool enemyArea = false;
            for (const auto &enemy : opponent->deployment)
            {
                closestColumn = std::min(closestColumn, std::abs(unit.cell.column - (7 - enemy.cell.column)));
                enemyArea |= catalog.units[enemy.definition].ability.selector == Selector::CurrentEnemyArea;
            }
            if (frontline)
                score += 0.3 / (1 + closestColumn);
            if (enemyArea)
                for (const auto &ally : seat.roster)
                    if (ally.onBoard && ally.id != unit.id && Distance(unit.cell, ally.cell) <= 1)
                        score -= 0.04;
        }
    }
    return score / std::max(1, deployed);
}
} // namespace
Match::Match(Catalog catalog, Id seed, int humans) : catalog_(std::move(catalog))
{
    Restart(seed, humans);
}
void Match::Restart(Id seed, int humans)
{
    matchNamespace_ = NextMatchNamespace.fetch_add(1);
    seed_ = seed;
    nextUnit_ = 1;
    nextRequest_ = 1;
    round_ = 0;
    elapsedMs_ = 0;
    accumulatorMs_ = 0;
    previousGhost_ = -1;
    capped_ = false;
    seats_.clear();
    pairs_.clear();
    encounters_.clear();
    records_.clear();
    botLog_.clear();
    replies_.clear();
    meetings_.clear();
    previousPairs_.clear();
    ghostCounts_.fill(0);
    lastWon_.fill(false);
    botObserveNextMs_.fill(0);
    botObservationRevision_.fill(0);
    for (auto &observation : botObservations_)
        observation.clear();
    if (!catalog_.Validate().empty() || humans < 0 || humans > 2)
    {
        phase_ = Phase::Aborted;
        remainingMs_ = 0;
        return;
    }
    const auto &r = catalog_.rules;
    for (int i = 0; i < r.seatCount; ++i)
    {
        SeatState s;
        s.id = i;
        s.revision = matchNamespace_ << 32;
        s.health = r.startingHealth;
        s.gold = r.startingGold;
        s.level = r.startingLevel;
        s.human = i < humans;
        s.botIndex = s.human ? i % int(catalog_.bots.size()) : (i - humans) % int(catalog_.bots.size());
        s.label = s.human ? "Captain " + std::to_string(i + 1)
                          : catalog_.bots[(i - humans) % catalog_.bots.size()].label;
        s.shopRng.state = HashValue(seed ^ Id(i + 1) * 0x51ed2705ULL);
        s.botRng.state = HashValue(seed ^ Id(i + 1) * 0xa0761d6478bd642fULL);
        seats_.push_back(s);
    }
    Prepare();
}
void Match::Refresh(SeatState &s)
{
    const auto &weights = catalog_.rules.shopWeights.at(s.level);
    s.shop.clear();
    for (int slot = 0; slot < catalog_.rules.shopSlots; ++slot)
    {
        int draw = s.shopRng.Below(10000), tier = 0;
        while (tier < 2 && draw >= weights[tier])
        {
            draw -= weights[tier];
            ++tier;
        }
        std::vector<int> eligible;
        for (int i = 0; i < int(catalog_.units.size()); ++i)
            if (catalog_.units[i].cost == tier + 1)
                eligible.push_back(i);
        s.shop.push_back(eligible[s.shopRng.Below(int(eligible.size()))]);
    }
}
void Match::GainXp(SeatState &s, int xp)
{
    const auto &r = catalog_.rules;
    if (s.level >= r.maximumLevel)
    {
        s.xp = 0;
        return;
    }
    s.xp += xp;
    while (s.level < r.maximumLevel && s.xp >= r.xpToNext.at(s.level))
    {
        s.xp -= r.xpToNext.at(s.level);
        ++s.level;
    }
    if (s.level == r.maximumLevel)
        s.xp = 0;
}
void Match::Merge(SeatState &s)
{
    for (int star = 1; star < 3; ++star)
        for (int definition = 0; definition < int(catalog_.units.size()); ++definition)
        {
            while (true)
            {
                std::vector<OwnedUnit> group;
                for (const auto &u : s.roster)
                    if (u.definition == definition && u.star == star)
                        group.push_back(u);
                if (group.size() < 3)
                    break;
                std::sort(group.begin(), group.end(), [](const OwnedUnit &a, const OwnedUnit &b) {
                    auto rank = [](const OwnedUnit &u) {
                        return std::make_tuple(u.onBoard      ? 0
                                               : u.bench >= 0 ? 1
                                                              : 2,
                                               u.onBoard ? u.id : Id(u.bench >= 0 ? u.bench : 0), u.id);
                    };
                    return rank(a) < rank(b);
                });
                Id survivor = group[0].id, remove1 = group[1].id, remove2 = group[2].id;
                s.roster.erase(
                    std::remove_if(s.roster.begin(), s.roster.end(),
                                   [&](const OwnedUnit &u) { return u.id == remove1 || u.id == remove2; }),
                    s.roster.end());
                for (auto &u : s.roster)
                    if (u.id == survivor)
                        ++u.star;
            }
        }
    for (auto &u : s.roster)
        if (!u.onBoard && u.bench < 0)
        {
            for (int slot = 0; slot < catalog_.rules.benchCapacity; ++slot)
                if (std::none_of(s.roster.begin(), s.roster.end(),
                                 [&](const OwnedUnit &v) { return !v.onBoard && v.bench == slot; }))
                {
                    u.bench = slot;
                    break;
                }
        }
}
bool Match::Legal(const SeatState &s) const
{
    if (s.gold < 0 || s.level < catalog_.rules.startingLevel || s.level > catalog_.rules.maximumLevel)
        return false;
    std::set<int> bench;
    std::set<std::pair<int, int>> cells;
    std::set<Id> ids;
    int deployed = 0;
    for (const auto &u : s.roster)
    {
        if (!ids.insert(u.id).second || u.definition < 0 || u.definition >= int(catalog_.units.size()) ||
            u.star < 1 || u.star > 3)
            return false;
        if (u.onBoard)
        {
            ++deployed;
            if (u.cell.column < 0 || u.cell.column >= catalog_.rules.columns || u.cell.row < 0 ||
                u.cell.row >= catalog_.rules.deploymentRows ||
                !cells.insert({u.cell.column, u.cell.row}).second)
                return false;
        }
        else if (u.bench < 0 || u.bench >= catalog_.rules.benchCapacity || !bench.insert(u.bench).second)
            return false;
    }
    return deployed <= s.level;
}
bool Match::ApplyCommand(SeatState &s, const Command &cmd, Id &nextUnit, std::string &reason)
{
    const auto &r = catalog_.rules;
    auto reject = [&](const std::string &text) {
        reason = text;
        return false;
    };
    if (cmd.type == CommandType::Buy)
    {
        if (cmd.slot < 0 || cmd.slot >= int(s.shop.size()) || s.shop[cmd.slot] < 0)
            return reject("Offer is empty or unavailable");
        int definition = s.shop[cmd.slot], cost = catalog_.units[definition].cost;
        if (s.gold < cost)
            return reject("Not enough gold");
        OwnedUnit u;
        u.id = nextUnit++;
        u.definition = definition;
        s.roster.push_back(u);
        s.gold -= cost;
        s.shop[cmd.slot] = -1;
        Merge(s);
        if (!Legal(s))
            return reject("Bench full; purchase does not resolve into a legal merge");
    }
    else if (cmd.type == CommandType::Sell)
    {
        auto it = std::find_if(s.roster.begin(), s.roster.end(),
                               [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (it == s.roster.end())
            return reject("Unit is not owned");
        s.gold += catalog_.units[it->definition].cost * CountCopies(it->star);
        s.roster.erase(it);
    }
    else if (cmd.type == CommandType::Reroll)
    {
        if (s.gold < r.rerollCost)
            return reject("Not enough gold");
        s.gold -= r.rerollCost;
        s.shopLocked = false;
        Refresh(s);
    }
    else if (cmd.type == CommandType::ToggleLock)
        s.shopLocked = !s.shopLocked;
    else if (cmd.type == CommandType::BuyXp)
    {
        if (s.level >= r.maximumLevel)
            return reject("Already at maximum level");
        if (s.gold < r.buyXpGold)
            return reject("Not enough gold");
        s.gold -= r.buyXpGold;
        GainXp(s, r.buyXpAmount);
    }
    else if (cmd.type == CommandType::Move)
    {
        auto it = std::find_if(s.roster.begin(), s.roster.end(),
                               [&](const OwnedUnit &u) { return u.id == cmd.unit; });
        if (it == s.roster.end())
            return reject("Unit is not owned");
        if (cmd.toBoard && (cmd.cell.column < 0 || cmd.cell.column >= r.columns || cmd.cell.row < 0 ||
                            cmd.cell.row >= r.deploymentRows))
            return reject("Destination is outside own deployment");
        if (!cmd.toBoard && (cmd.slot < 0 || cmd.slot >= r.benchCapacity))
            return reject("Invalid bench slot");
        auto occupied = std::find_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &u) {
            return u.id != cmd.unit && u.onBoard == cmd.toBoard &&
                   (cmd.toBoard ? u.cell == cmd.cell : u.bench == cmd.slot);
        });
        bool oldBoard = it->onBoard;
        Cell oldCell = it->cell;
        int oldBench = it->bench;
        if (occupied != s.roster.end())
        {
            occupied->onBoard = oldBoard;
            occupied->cell = oldCell;
            occupied->bench = oldBench;
        }
        it->onBoard = cmd.toBoard;
        it->cell = cmd.toBoard ? cmd.cell : Cell{};
        it->bench = cmd.toBoard ? -1 : cmd.slot;
        if (!Legal(s))
            return reject("Move exceeds deployment capacity");
    }
    else if (cmd.type == CommandType::Ready)
        s.ready = true;
    else
        return reject("Unknown command");
    if (cmd.type != CommandType::Ready)
        s.ready = false;
    return true;
}
Reply Match::Submit(int authenticatedSeat, const Command &cmd)
{
    Reply reply;
    reply.reason = "Invalid seat ownership";
    if (authenticatedSeat < 0 || authenticatedSeat >= int(seats_.size()) || cmd.seat != authenticatedSeat)
        return reply;
    auto &s = seats_[authenticatedSeat];
    reply.revision = s.revision;
    reply.sequence = s.sequence;
    auto cached = replies_.find({authenticatedSeat, cmd.requestId});
    if (cached != replies_.end())
    {
        if (EqualCommand(cached->second.command, cmd))
            return cached->second.reply;
        reply.reason = "Request ID reused with different payload";
        return reply;
    }
    if (phase_ != Phase::Preparation)
    {
        reply.reason = "Preparation is locked";
        return reply;
    }
    if (s.health <= 0)
    {
        reply.reason = "Seat is eliminated";
        return reply;
    }
    if (cmd.sequence != s.sequence + 1)
    {
        reply.reason = "Out-of-order command sequence";
        return reply;
    }
    if (cmd.revision != s.revision)
    {
        reply.reason = "Stale seat revision";
        return reply;
    }
    SeatState pending = s;
    Id next = nextUnit_;
    std::string reason;
    if (!ApplyCommand(pending, cmd, next, reason))
    {
        reply.reason = reason;
        return reply;
    }
    pending.sequence = cmd.sequence;
    ++pending.revision;
    s = std::move(pending);
    nextUnit_ = next;
    reply.accepted = true;
    reply.reason = "Accepted";
    reply.revision = s.revision;
    reply.sequence = s.sequence;
    replies_[{authenticatedSeat, cmd.requestId}] = {cmd, reply};
    return reply;
}
std::vector<PublicSeat> Match::PublicSeats() const
{
    std::vector<PublicSeat> result;
    for (const auto &s : seats_)
    {
        PublicSeat p;
        p.id = s.id;
        p.health = s.health;
        p.level = s.level;
        p.placement = s.placement;
        p.wins = s.wins;
        p.human = s.human;
        p.ready = s.ready;
        p.takeover = s.takeover;
        p.label = s.label;
        for (const auto &u : s.roster)
            if (u.onBoard)
                p.deployment.push_back(u);
        result.push_back(p);
    }
    return result;
}
void Match::Pair()
{
    std::vector<int> active;
    for (const auto &s : seats_)
        if (s.health > 0)
            active.push_back(s.id);
    pairs_.clear();
    auto prior = [&](int a, int b) {
        return std::find(previousPairs_.begin(), previousPairs_.end(), Key(a, b)) != previousPairs_.end();
    };
    auto tie = [&](Id value) { return HashValue(seed_ ^ Id(round_) * 0x9e3779b9ULL ^ value); };
    if (active.size() % 2)
    {
        int recipient = *std::min_element(active.begin(), active.end(), [&](int a, int b) {
            return std::make_tuple(ghostCounts_[a], a == previousGhost_, tie(Id(a) ^ 0xabcULL)) <
                   std::make_tuple(ghostCounts_[b], b == previousGhost_, tie(Id(b) ^ 0xabcULL));
        });
        active.erase(std::find(active.begin(), active.end(), recipient));
        int donor = *std::min_element(active.begin(), active.end(), [&](int a, int b) {
            return std::make_tuple(prior(a, recipient), meetings_[Key(a, recipient)],
                                   tie(Id(a + recipient * 8) ^ 0xdefULL)) <
                   std::make_tuple(prior(b, recipient), meetings_[Key(b, recipient)],
                                   tie(Id(b + recipient * 8) ^ 0xdefULL));
        });
        pairs_.push_back({recipient, donor, true});
        ++ghostCounts_[recipient];
        previousGhost_ = recipient;
    }
    std::vector<std::pair<int, int>> best;
    std::tuple<int, int, Id> bestScore{999, 999, ~Id(0)};
    std::function<void(std::vector<int>, std::vector<std::pair<int, int>>)> enumerate =
        [&](std::vector<int> remaining, std::vector<std::pair<int, int>> candidate) {
            if (remaining.empty())
            {
                std::sort(candidate.begin(), candidate.end());
                int repeats = 0, history = 0;
                Id hash = 0;
                for (auto p : candidate)
                {
                    repeats += prior(p.first, p.second) ? 1 : 0;
                    history += meetings_[p];
                    hash = HashValue(hash ^ Id(p.first * 8 + p.second + 1));
                }
                auto score = std::make_tuple(repeats, history, tie(hash));
                if (score < bestScore)
                {
                    bestScore = score;
                    best = candidate;
                }
                return;
            }
            int a = remaining.front();
            for (std::size_t i = 1; i < remaining.size(); ++i)
            {
                auto rest = remaining;
                int b = rest[i];
                rest.erase(rest.begin() + i);
                rest.erase(rest.begin());
                auto next = candidate;
                next.push_back(Key(a, b));
                enumerate(rest, next);
            }
        };
    enumerate(active, {});
    for (auto p : best)
        pairs_.push_back({p.first, p.second, false});
    previousPairs_.clear();
    for (auto p : pairs_)
    {
        auto key = Key(p.a, p.b);
        ++meetings_[key];
        previousPairs_.push_back(key);
    }
}
void Match::Prepare()
{
    ++round_;
    phase_ = Phase::Preparation;
    remainingMs_ = round_ == 1 ? catalog_.rules.firstPreparationMs : catalog_.rules.preparationMs;
    botCommands_.fill(0);
    botRerolls_.fill(0);
    botNextMs_.fill(elapsedMs_);
    encounters_.clear();
    for (auto &s : seats_)
        if (s.health > 0)
        {
            if (round_ > 1)
            {
                s.gold += catalog_.rules.baseIncome + (lastWon_[s.id] ? catalog_.rules.winIncome : 0) +
                          std::min(catalog_.rules.interestCap, s.lockGold / catalog_.rules.interestDivisor);
                GainXp(s, catalog_.rules.passiveXp);
            }
            if (!s.shopLocked || round_ == 1)
                Refresh(s);
            s.ready = false;
            ++s.revision;
        }
    Pair();
}
void Match::Lock()
{
    if (phase_ != Phase::Preparation)
        return;
    phase_ = Phase::Combat;
    remainingMs_ = catalog_.rules.combatTimeoutMs;
    encounters_.clear();
    for (auto &s : seats_)
        if (s.health > 0)
        {
            s.lockGold = s.gold;
            ++s.revision;
        }
    for (std::size_t i = 0; i < pairs_.size(); ++i)
    {
        auto p = pairs_[i];
        Id encounterId = Id(round_) * 8 + i + 1;
        encounters_.emplace_back(p, Combat(catalog_, seats_[p.a].roster, seats_[p.b].roster,
                                           HashValue(seed_ ^ encounterId), encounterId));
    }
}
Id Match::StateHash() const
{
    Id hash = HashValue(seed_ ^ Id(round_));
    auto add = [&](Id value) { hash = HashValue(hash ^ HashValue(value)); };
    auto text = [&](const std::string &value) {
        for (unsigned char ch : value)
            add(ch);
    };
    text(catalog_.contentDigest);
    add(Id(phase_));
    add(nextUnit_);
    add(nextRequest_);
    add(Id(remainingMs_));
    for (const auto &s : seats_)
    {
        add(Id(s.id));
        add(Id(s.health));
        add(Id(s.gold));
        add(Id(s.xp));
        add(Id(s.level));
        add(Id(s.wins));
        add(Id(s.placement));
        add(Id(s.lockGold));
        add(Id(s.botIndex));
        add(s.human);
        add(s.takeover);
        add(s.ready);
        add(s.shopLocked);
        // Transport namespace deliberately does not affect seeded replay equivalence.
        add(s.revision & 0xffffffffULL);
        add(s.sequence);
        add(s.shopRng.state);
        add(s.botRng.state);
        for (int offer : s.shop)
            add(Id(offer + 1));
        for (const auto &u : s.roster)
        {
            add(u.id);
            add(Id(u.definition));
            add(Id(u.star));
            add(u.onBoard);
            add(Id(u.cell.column + 1));
            add(Id(u.cell.row + 1));
            add(Id(u.bench + 1));
        }
    }
    for (auto pair : pairs_)
    {
        add(Id(pair.a));
        add(Id(pair.b));
        add(pair.ghost);
    }
    for (const auto &history : meetings_)
    {
        add(Id(history.first.first));
        add(Id(history.first.second));
        add(Id(history.second));
    }
    for (int count : ghostCounts_)
        add(Id(count));
    add(Id(previousGhost_ + 1));
    return hash;
}
void Match::Settle()
{
    if (!records_.empty() && records_.back().round == round_)
        return;
    RoundRecord record;
    record.round = round_;
    record.settlementId = HashValue(seed_ ^ Id(round_));
    record.preHash = StateHash();
    record.pairs = pairs_;
    lastWon_.fill(false);
    int base = 0;
    for (const auto &stage : catalog_.rules.lossStages)
        if (round_ >= stage.start && round_ <= stage.end)
            base = stage.damage;
    for (const auto &e : encounters_)
    {
        const auto &r = e.combat.Result();
        record.results.push_back(r);
        EncounterSummary summary;
        summary.pairing = e.pairing;
        summary.result = r;
        std::map<Id, int> targetSides;
        for (const auto &unit : e.combat.Units())
            targetSides.emplace(unit.id, unit.side);
        for (const auto &event : e.combat.Events())
        {
            const int side = targetSides.at(event.target);
            summary.healthLoss[side] += event.healthLoss;
            summary.absorbed[side] += event.absorbed;
            if (event.effect == Effect::Heal)
                summary.healing[side] += event.resolved;
        }
        record.encounters.push_back(std::move(summary));
        for (int side = 0; side < 2; ++side)
        {
            if (e.pairing.ghost && side == 1)
                continue;
            int seat = side ? e.pairing.b : e.pairing.a;
            bool win = r.winner == side;
            lastWon_[seat] = win;
            if (win)
                ++seats_[seat].wins;
            record.damage[seat] = r.winner < 0 ? catalog_.rules.drawDamage
                                  : win        ? 0
                                               : base + r.survivors[1 - side];
        }
    }
    std::vector<int> eliminated, alive;
    std::array<int, 8> raw{};
    for (auto &s : seats_)
        if (s.health > 0)
        {
            raw[s.id] = s.health - record.damage[s.id];
            if (raw[s.id] <= 0)
                eliminated.push_back(s.id);
            else
                alive.push_back(s.id);
            s.health = std::max(0, raw[s.id]);
        }
    auto rank = [&](std::vector<int> group, int starting) {
        std::sort(group.begin(), group.end(), [&](int a, int b) {
            return std::make_tuple(raw[a], seats_[a].wins) > std::make_tuple(raw[b], seats_[b].wins);
        });
        int place = starting;
        for (std::size_t i = 0; i < group.size(); ++i)
        {
            if (i && std::make_tuple(raw[group[i]], seats_[group[i]].wins) !=
                         std::make_tuple(raw[group[i - 1]], seats_[group[i - 1]].wins))
                place = starting + int(i);
            seats_[group[i]].placement = place;
        }
    };
    rank(eliminated, int(alive.size()) + 1);
    if (alive.size() <= 1 || round_ >= catalog_.rules.maxRounds)
    {
        rank(alive, 1);
        capped_ = alive.size() > 1;
        phase_ = Phase::Finished;
        remainingMs_ = 0;
    }
    else
    {
        phase_ = Phase::Settlement;
        remainingMs_ = catalog_.rules.settlementMs;
    }
    for (const auto &s : seats_)
    {
        record.gold[s.id] = s.gold;
        record.health[s.id] = s.health;
        record.placement[s.id] = s.placement;
        record.wins[s.id] = s.wins;
    }
    record.postHash = StateHash();
    records_.push_back(record);
}
Cell Match::FormationCell(const SeatState &s, const OwnedUnit &u) const
{
    const auto &d = catalog_.units[u.definition];
    int preferred = d.unitClass == "guardian"  ? 3
                    : d.unitClass == "warrior" ? 3
                    : d.unitClass == "rogue"   ? 2
                    : d.unitClass == "priest"  ? 1
                                               : 0;
    std::array<int, 8> columns{3, 4, 2, 5, 1, 6, 0, 7};
    if (d.unitClass == "rogue")
        columns = {0, 7, 1, 6, 2, 5, 3, 4};
    for (int delta = 0; delta < 4; ++delta)
    {
        int row = (preferred + delta) % 4;
        for (int col : columns)
        {
            Cell cell{col, row};
            if (std::none_of(s.roster.begin(), s.roster.end(),
                             [&](const OwnedUnit &v) { return v.onBoard && v.cell == cell; }))
                return cell;
        }
    }
    return {};
}
double Match::FormationScore(const SeatState &s, const BotDef &b) const
{
    auto f = Evaluate(s, catalog_, b);
    return f.budget + f.roles + f.traits * b.synergy;
}
void Match::BotTurn(int seat)
{
    auto &s = seats_[seat];
    const auto &bot = catalog_.bots[s.botIndex];
    if (s.human || s.health <= 0 || s.ready)
        return;
    Command chosen;
    chosen.type = CommandType::Ready;
    std::string action = "ready";
    double best = 0;
    std::array<double, 8> features{};
    int deployed =
        int(std::count_if(s.roster.begin(), s.roster.end(), [](const OwnedUnit &u) { return u.onBoard; }));
    // Repair deployment before economic evaluation, through the same transaction API.
    if (botCommands_[seat] < bot.maxCommands - 1 && deployed < s.level)
    {
        const OwnedUnit *bestUnit = nullptr;
        double score = -1;
        for (const auto &u : s.roster)
            if (!u.onBoard)
            {
                SeatState single;
                single.level = 1;
                single.roster = {u};
                double value = FormationScore(single, bot);
                if (value > score)
                {
                    score = value;
                    bestUnit = &u;
                }
            }
        if (bestUnit)
        {
            chosen.type = CommandType::Move;
            chosen.unit = bestUnit->id;
            chosen.toBoard = true;
            chosen.cell = FormationCell(s, *bestUnit);
            best = 1;
            action = "deploy";
        }
    }
    if (chosen.type == CommandType::Ready && botCommands_[seat] < bot.maxCommands - 1)
    {
        // A stronger benched unit can replace a board unit without changing capacity.
        if (remainingMs_ > catalog_.rules.botRepositionCutoffMs)
            for (const auto &bench : s.roster)
                if (!bench.onBoard)
                    for (const auto &board : s.roster)
                        if (board.onBoard)
                        {
                            auto utility = [&](SeatState formation) {
                                formation.roster.erase(
                                    std::remove_if(formation.roster.begin(), formation.roster.end(),
                                                   [](const OwnedUnit &unit) { return !unit.onBoard; }),
                                    formation.roster.end());
                                auto value = Evaluate(formation, catalog_, bot);
                                return value.budget + value.roles + value.traits * bot.synergy;
                            };
                            SeatState pending = s;
                            Command replacement;
                            replacement.type = CommandType::Move;
                            replacement.unit = bench.id;
                            replacement.toBoard = true;
                            replacement.cell = board.cell;
                            Id next = nextUnit_;
                            std::string reject;
                            if (ApplyCommand(pending, replacement, next, reject) &&
                                utility(pending) > utility(s) + 0.1)
                            {
                                chosen.type = CommandType::Move;
                                chosen.unit = bench.id;
                                chosen.toBoard = true;
                                chosen.cell = board.cell;
                                best = 0.2;
                                action = "replace_deployment";
                                break;
                            }
                            if (chosen.type != CommandType::Ready)
                                break;
                        }
        if (chosen.type == CommandType::Ready)
        {
            auto before = Evaluate(s, catalog_, bot);
            std::vector<Command> candidates;
            for (int i = 0; i < int(s.shop.size()); ++i)
                if (s.shop[i] >= 0)
                {
                    Command cmd;
                    cmd.type = CommandType::Buy;
                    cmd.slot = i;
                    candidates.push_back(cmd);
                }
            Command xp;
            xp.type = CommandType::BuyXp;
            candidates.push_back(xp);
            if (int(s.roster.size()) > s.level + 4)
                for (const auto &unit : s.roster)
                    if (!unit.onBoard && unit.star == 1 &&
                        std::count_if(s.roster.begin(), s.roster.end(), [&](const OwnedUnit &other) {
                            return other.definition == unit.definition;
                        }) == 1)
                    {
                        SeatState without = s;
                        without.roster.erase(
                            std::remove_if(without.roster.begin(), without.roster.end(),
                                           [&](const OwnedUnit &other) { return other.id == unit.id; }),
                            without.roster.end());
                        if (Evaluate(without, catalog_, bot).budget >= before.budget)
                        {
                            Command sell;
                            sell.type = CommandType::Sell;
                            sell.unit = unit.id;
                            candidates.push_back(sell);
                        }
                    }
            for (const auto &candidate : candidates)
            {
                SeatState pending = s;
                Id next = nextUnit_;
                std::string reject;
                if (!ApplyCommand(pending, candidate, next, reject))
                    continue;
                auto after = Evaluate(pending, catalog_, bot);
                std::array<double, 8> f{
                    std::clamp((after.budget - before.budget) / std::max(1.0, double(s.level)), -1.0, 1.0),
                    std::clamp(after.upgrades - before.upgrades, -1.0, 1.0),
                    std::clamp(after.traits - before.traits, -1.0, 1.0),
                    after.roles - before.roles,
                    std::clamp(after.pairs - before.pairs, -1.0, 1.0),
                    double(s.gold - pending.gold) / std::max(10, s.gold),
                    double(
                        std::min(catalog_.rules.interestCap, s.gold / catalog_.rules.interestDivisor) -
                        std::min(catalog_.rules.interestCap, pending.gold / catalog_.rules.interestDivisor)) /
                        3.0,
                    after.bench - before.bench};
                double urgency = s.health <= 15 ? 1.5 : 1.0;
                double score = urgency * (3 * f[0] + 2 * f[1] * bot.upgrade + 1.5 * f[2] * bot.synergy +
                                          f[3] + 0.6 * f[4] * bot.upgrade) -
                               0.35 * f[5] * bot.save - 0.25 * f[6] * bot.save - 0.25 * f[7];
                if (candidate.type == CommandType::BuyXp)
                {
                    score += double(pending.level - s.level) * 0.24 * bot.level;
                    if (s.xp + catalog_.rules.buyXpAmount >= catalog_.rules.xpToNext.at(s.level))
                        score += 0.04;
                }
                score += (double(s.botRng.Below(20001)) - 10000.0) / 10000.0 * bot.noiseBp / 10000.0;
                if (score > best + 0.01)
                {
                    best = score;
                    chosen = candidate;
                    features = f;
                    action = candidate.type == CommandType::Buy    ? "buy"
                             : candidate.type == CommandType::Sell ? "sell_replaceable_bench"
                                                                   : "buy_xp";
                }
            }
            if (chosen.type == CommandType::Ready && remainingMs_ > catalog_.rules.botRepositionCutoffMs)
            {
                int opponentId = -1;
                for (const auto &pair : pairs_)
                {
                    if (pair.a == seat)
                        opponentId = pair.b;
                    else if (pair.b == seat && !pair.ghost)
                        opponentId = pair.a;
                }
                const PublicSeat *opponent = nullptr;
                for (const auto &observed : botObservations_[seat])
                    if (observed.id == opponentId)
                        opponent = &observed;
                const double current = TacticalScore(s, opponent, catalog_);
                int considered = 0;
                for (const auto &unit : s.roster)
                    if (unit.onBoard)
                        for (Cell direction : {Cell{-1, 0}, Cell{1, 0}, Cell{0, -1}, Cell{0, 1}})
                        {
                            if (++considered > 24)
                                break;
                            Command move;
                            move.type = CommandType::Move;
                            move.unit = unit.id;
                            move.toBoard = true;
                            move.cell = {unit.cell.column + direction.column, unit.cell.row + direction.row};
                            SeatState pending = s;
                            Id next = nextUnit_;
                            std::string reject;
                            if (!ApplyCommand(pending, move, next, reject))
                                continue;
                            const double improvement = TacticalScore(pending, opponent, catalog_) - current;
                            if (improvement > std::max(0.04, best))
                            {
                                chosen = move;
                                best = improvement;
                                features[3] = improvement;
                                action = "sampled_opponent_reposition";
                            }
                        }
            }
            if (chosen.type == CommandType::Ready && s.gold >= catalog_.rules.rerollCost + 10 &&
                botRerolls_[seat] < bot.maxRerolls &&
                int(s.roster.size()) < s.level + catalog_.rules.benchCapacity)
            {
                chosen.type = CommandType::Reroll;
                action = "bounded_reroll";
                best = 0.01;
            }
        }
    }
    chosen.seat = seat;
    chosen.requestId = (Id(1) << 63) | nextRequest_++;
    chosen.sequence = s.sequence + 1;
    chosen.revision = s.revision;
    BotDecision log;
    log.round = round_;
    log.seat = seat;
    log.observationRevision = botObservationRevision_[seat];
    log.action = action;
    log.features = features;
    log.score = best;
    log.reply = Submit(seat, chosen);
    log.goldAfter = seats_[seat].gold;
    botLog_.push_back(log);
    if (log.reply.accepted)
    {
        ++botCommands_[seat];
        if (chosen.type == CommandType::Reroll)
            ++botRerolls_[seat];
    }
}
void Match::Tick(int ms)
{
    if (ms <= 0 || phase_ == Phase::Finished || phase_ == Phase::Aborted)
        return;
    accumulatorMs_ += ms;
    int steps = 0;
    // Keep excess accumulated time for subsequent calls; never discard simulation ticks.
    while (accumulatorMs_ >= catalog_.rules.tickMs && steps++ < 200 && phase_ != Phase::Finished &&
           phase_ != Phase::Aborted)
    {
        accumulatorMs_ -= catalog_.rules.tickMs;
        elapsedMs_ += catalog_.rules.tickMs;
        remainingMs_ -= catalog_.rules.tickMs;
        if (phase_ == Phase::Preparation)
        {
            // Snapshot all bot observations before any policy acts on this tick.
            // Decision cadence (700 ms) must not stretch the observation cadence (1500 ms).
            for (const auto &seat : seats_)
                if (!seat.human && seat.health > 0 && elapsedMs_ >= botObserveNextMs_[seat.id])
                {
                    botObservations_[seat.id] = PublicSeats();
                    botObserveNextMs_[seat.id] = elapsedMs_ + catalog_.bots[seat.botIndex].observationMs;
                    ++botObservationRevision_[seat.id];
                }
            for (auto &s : seats_)
                if (!s.human && s.health > 0 && !s.ready && elapsedMs_ >= botNextMs_[s.id])
                {
                    BotTurn(s.id);
                    botNextMs_[s.id] = elapsedMs_ + catalog_.bots[s.botIndex].decisionIntervalMs;
                }
            bool ready = std::all_of(seats_.begin(), seats_.end(),
                                     [](const SeatState &s) { return s.health <= 0 || s.ready; });
            if (remainingMs_ <= 0 || ready)
                Lock();
        }
        else if (phase_ == Phase::Combat)
        {
            for (auto &e : encounters_)
                e.combat.Tick();
            if (std::all_of(encounters_.begin(), encounters_.end(),
                            [](const Encounter &e) { return e.combat.Result().complete; }))
                Settle();
        }
        else if (phase_ == Phase::Settlement && remainingMs_ <= 0)
            Prepare();
    }
}
void Match::TakeOver(int seat)
{
    if (seat < 0 || seat >= int(seats_.size()) || !seats_[seat].human)
        return;
    auto &s = seats_[seat];
    s.human = false;
    s.takeover = true;
    s.label = catalog_.bots[s.botIndex].label + " (takeover)";
    s.ready = false;
}
void Match::Abort()
{
    phase_ = Phase::Aborted;
    remainingMs_ = 0;
    for (auto &s : seats_)
        s.placement = 0;
}
std::string Match::InvariantError() const
{
    if (phase_ == Phase::Aborted)
        return catalog_.Validate();
    if (seats_.size() != 8)
        return "Missing persistent seats";
    std::set<Id> identities;
    for (const auto &s : seats_)
    {
        if (!Legal(s))
            return "Invalid owned roster or economy for seat " + std::to_string(s.id);
        for (const auto &u : s.roster)
            if (!identities.insert(u.id).second || u.id >= nextUnit_)
                return "Duplicated or invalid instance ID";
        if (s.health == 0 && s.placement == 0)
            return "Eliminated seat lacks placement";
    }
    if (phase_ == Phase::Preparation || phase_ == Phase::Combat)
    {
        std::array<int, 8> exposure{};
        for (const auto &p : pairs_)
        {
            if (p.a == p.b || seats_[p.a].health <= 0 || seats_[p.b].health <= 0)
                return "Invalid pairing";
            ++exposure[p.a];
            if (!p.ghost)
                ++exposure[p.b];
        }
        for (const auto &s : seats_)
            if (s.health > 0 && exposure[s.id] != 1)
                return "Real seat receives other than one result";
    }
    for (const auto &e : encounters_)
    {
        auto issue = e.combat.InvariantError();
        if (!issue.empty())
            return issue;
    }
    if (phase_ == Phase::Finished)
        for (const auto &s : seats_)
            if (!s.placement)
                return "Final placement missing";
    return {};
}
} // namespace wc
