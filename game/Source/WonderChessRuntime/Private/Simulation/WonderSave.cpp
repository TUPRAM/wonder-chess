#include "Simulation/WonderSimulation.h"
#include <algorithm>
#include <limits>
#include <set>
#include <stdexcept>

namespace wc
{
namespace
{
constexpr std::size_t MaxSaveBytes = 4 * 1024 * 1024;
constexpr const char *SaveMagic = "WCVNEXT-PREPARATION-3";
Id Checksum(const std::string &bytes)
{
    Id hash = 14695981039346656037ULL;
    for (unsigned char byte : bytes) { hash ^= byte; hash *= 1099511628211ULL; }
    return hash;
}
struct Writer
{
    std::string bytes;
    void Number(Id value) { for (int i = 0; i < 8; ++i) bytes.push_back(char((value >> (i * 8)) & 255)); }
    void Integer(int value) { Number(static_cast<Id>(static_cast<Int>(value))); }
    void Boolean(bool value) { Number(value ? 1 : 0); }
    void Text(const std::string &value) { Number(value.size()); bytes.append(value); }
    template <class T, class F> void List(const T &values, F write)
    {
        Number(values.size());
        for (const auto &value : values) write(value);
    }
};
struct Reader
{
    const std::string &bytes;
    std::size_t offset = 0;
    Id Number()
    {
        if (offset > bytes.size() || bytes.size() - offset < 8) throw std::runtime_error("Truncated save");
        Id value = 0;
        for (int i = 0; i < 8; ++i) value |= Id(static_cast<unsigned char>(bytes[offset++])) << (i * 8);
        return value;
    }
    int Integer(int low = std::numeric_limits<int>::min(), int high = std::numeric_limits<int>::max())
    {
        const Int value = static_cast<Int>(Number());
        if (value < low || value > high) throw std::runtime_error("Save integer outside bounds");
        return static_cast<int>(value);
    }
    bool Boolean() { return Integer(0, 1) != 0; }
    std::string Text()
    {
        const Id size = Number();
        if (size > 65536 || offset > bytes.size() || size > bytes.size() - offset)
            throw std::runtime_error("Invalid save string");
        const auto value = bytes.substr(offset, static_cast<std::size_t>(size));
        offset += static_cast<std::size_t>(size);
        return value;
    }
    template <class F> void Count(int limit, F read)
    {
        const int size = Integer(0, limit);
        for (int i = 0; i < size; ++i) read();
    }
};
void WriteUnit(Writer &out, const OwnedUnit &unit)
{
    out.Number(unit.id); out.Integer(unit.definition); out.Integer(unit.star); out.Boolean(unit.onBoard);
    out.Integer(unit.cell.column); out.Integer(unit.cell.row); out.Integer(unit.bench);
    out.Boolean(unit.neutral); out.Integer(unit.hpScaleBp); out.Integer(unit.damageScaleBp);
    out.Integer(int(unit.facing)); out.Integer(unit.relic);
}
OwnedUnit ReadUnit(Reader &in)
{
    OwnedUnit unit;
    unit.id = in.Number(); unit.definition = in.Integer(0, 10000); unit.star = in.Integer(1, 3);
    unit.onBoard = in.Boolean(); unit.cell.column = in.Integer(-1, 7); unit.cell.row = in.Integer(-1, 7);
    unit.bench = in.Integer(-1, 9); unit.neutral = in.Boolean();
    unit.hpScaleBp = in.Integer(1, 1000000); unit.damageScaleBp = in.Integer(1, 1000000);
    unit.facing = Facing(in.Integer(0, 3)); unit.relic = in.Integer(-1, 10000);
    return unit;
}
void WritePair(Writer &out, const Pairing &pair)
{
    out.Integer(pair.a); out.Integer(pair.b); out.Boolean(pair.ghost);
    out.Integer(int(pair.kind)); out.Text(pair.waveId);
}
Pairing ReadPair(Reader &in)
{
    Pairing pair;
    pair.a = in.Integer(0, 7); pair.b = in.Integer(-1, 7); pair.ghost = in.Boolean();
    pair.kind = EncounterKind(in.Integer(0, 2)); pair.waveId = in.Text();
    return pair;
}
void WritePublic(Writer &out, const PublicSeat &seat)
{
    out.Integer(seat.id); out.Integer(seat.health); out.Integer(seat.level); out.Integer(seat.placement);
    out.Integer(seat.wins); out.Boolean(seat.human); out.Boolean(seat.ready); out.Boolean(seat.takeover);
    out.Text(seat.label); out.List(seat.deployment, [&](const OwnedUnit &unit) { WriteUnit(out, unit); });
}
PublicSeat ReadPublic(Reader &in)
{
    PublicSeat seat;
    seat.id = in.Integer(0, 7); seat.health = in.Integer(0, 1000000); seat.level = in.Integer(3, 10);
    seat.placement = in.Integer(0, 8); seat.wins = in.Integer(0, 10000);
    seat.human = in.Boolean(); seat.ready = in.Boolean(); seat.takeover = in.Boolean(); seat.label = in.Text();
    in.Count(10, [&] { seat.deployment.push_back(ReadUnit(in)); });
    return seat;
}
void WriteResult(Writer &out, const CombatResult &result)
{
    out.Boolean(result.complete); out.Boolean(result.timeout); out.Integer(result.winner);
    out.Integer(result.ticks); out.Integer(result.survivors[0]); out.Integer(result.survivors[1]);
}
CombatResult ReadResult(Reader &in, const Catalog &catalog)
{
    CombatResult result;
    result.complete = in.Boolean(); result.timeout = in.Boolean(); result.winner = in.Integer(-1, 1);
    result.ticks = in.Integer(0, catalog.rules.combatTimeoutMs / catalog.rules.tickMs);
    result.survivors[0] = in.Integer(0, 32); result.survivors[1] = in.Integer(0, 32);
    if (!result.complete) throw std::runtime_error("Saved round has an incomplete combat");
    return result;
}
void ValidateObservations(const std::vector<PublicSeat> &observations, const Catalog &catalog, Id nextUnit)
{
    std::set<int> seats;
    std::set<Id> identities;
    for (const auto &seat : observations)
    {
        if (!seats.insert(seat.id).second || seat.health > catalog.rules.startingHealth ||
            seat.level > catalog.rules.maximumLevel || int(seat.deployment.size()) > seat.level)
            throw std::runtime_error("Invalid saved public seat");
        std::set<int> cells;
        std::set<int> relics;
        for (const auto &unit : seat.deployment)
        {
            if (unit.id == 0 || unit.id >= nextUnit || !identities.insert(unit.id).second || unit.neutral ||
                unit.definition < 0 || unit.definition >= int(catalog.units.size()) || !unit.onBoard ||
                unit.cell.column < 0 || unit.cell.column >= catalog.rules.columns || unit.cell.row < 0 ||
                unit.cell.row >= catalog.rules.deploymentRows || !cells.insert(unit.cell.row * catalog.rules.columns + unit.cell.column).second ||
                unit.bench != -1 || unit.hpScaleBp != 10000 || unit.damageScaleBp != 10000)
                throw std::runtime_error("Invalid saved public deployment");
            if (unit.relic != -1 && (unit.relic < 0 || unit.relic >= int(catalog.relics.size()) ||
                !relics.insert(unit.relic).second ||
                !RelicCompatible(catalog.relics[unit.relic], catalog.units[unit.definition].ability.mechanic)))
                throw std::runtime_error("Invalid saved public relic");
        }
    }
}
} // namespace

std::string Match::SavePreparation() const
{
    if (catalog_.profileId != "wonder_vnext" || phase_ != Phase::Preparation || networked_ ||
        !InvariantError().empty())
        return {};
    Writer out;
    out.Text(SaveMagic); out.Text(catalog_.profileId); out.Text(catalog_.schemaVersion);
    out.Text(catalog_.balanceVersion); out.Text(catalog_.contentDigest);
    out.Integer(originalHumans_); out.Boolean(networked_);
    out.Number(seed_); out.Number(nextUnit_); out.Number(nextRequest_);
    out.Integer(round_); out.Integer(pvpRoundIndex_); out.Integer(remainingMs_); out.Integer(elapsedMs_);
    out.Integer(accumulatorMs_); out.Integer(previousGhost_); out.Boolean(capped_);
    out.List(seats_, [&](const SeatState &seat) {
        out.Integer(seat.id); out.Integer(seat.health); out.Integer(seat.gold); out.Integer(seat.xp);
        out.Integer(seat.level); out.Integer(seat.placement); out.Integer(seat.wins); out.Integer(seat.lockGold);
        out.Integer(seat.botIndex); out.Boolean(seat.human); out.Boolean(seat.takeover); out.Boolean(seat.ready);
        out.Boolean(seat.shopLocked); out.Text(seat.label); out.Number(seat.revision & 0xffffffffULL);
        out.Number(seat.sequence); out.Number(seat.shopRng.state); out.Number(seat.botRng.state);
        out.Number(seat.relicRng.state); out.Integer(seat.neutralWins); out.Integer(seat.neutralLosses);
        out.Integer(seat.neutralDraws); out.Integer(seat.pendingRelicDrafts);
        out.List(seat.shop, [&](int value) { out.Integer(value); });
        out.List(seat.roster, [&](const OwnedUnit &unit) { WriteUnit(out, unit); });
        out.List(seat.ownedRelics, [&](int value) { out.Integer(value); });
        out.List(seat.relicOffers, [&](int value) { out.Integer(value); });
    });
    out.List(pairs_, [&](const Pairing &pair) { WritePair(out, pair); });
    out.List(meetings_, [&](const auto &entry) {
        out.Integer(entry.first.first); out.Integer(entry.first.second); out.Integer(entry.second);
    });
    out.List(previousPairs_, [&](const auto &pair) { out.Integer(pair.first); out.Integer(pair.second); });
    for (int seat = 0; seat < 8; ++seat)
    {
        out.Integer(ghostCounts_[seat]); out.Integer(botCommands_[seat]); out.Integer(botRerolls_[seat]);
        out.Integer(botNextMs_[seat]); out.Integer(botObserveNextMs_[seat]); out.Number(botObservationRevision_[seat]);
        out.Boolean(lastWon_[seat]); out.Integer(pendingRewards_[seat]);
        out.List(botObservations_[seat], [&](const PublicSeat &observation) { WritePublic(out, observation); });
    }
    // Preserve recap history as well as the state needed for identical future decisions.
    out.List(records_, [&](const RoundRecord &record) {
        out.Integer(record.round); out.Integer(record.pvpRoundIndex); out.Number(record.settlementId);
        out.Number(record.preHash); out.Number(record.postHash); out.Boolean(record.neutral);
        out.List(record.pairs, [&](const Pairing &pair) { WritePair(out, pair); });
        out.List(record.results, [&](const CombatResult &result) { WriteResult(out, result); });
        out.List(record.encounters, [&](const EncounterSummary &encounter) {
            WritePair(out, encounter.pairing); WriteResult(out, encounter.result); out.Integer(int(encounter.kind));
            for (int side = 0; side < 2; ++side)
            {
                out.Number(encounter.healthLoss[side]); out.Number(encounter.absorbed[side]); out.Number(encounter.healing[side]);
                out.Integer(encounter.sides[side].seat.value_or(-1)); out.Text(encounter.sides[side].waveId);
            }
        });
        for (int seat = 0; seat < 8; ++seat)
        {
            out.Integer(record.damage[seat]); out.Integer(record.gold[seat]); out.Integer(record.health[seat]);
            out.Integer(record.placement[seat]); out.Integer(record.wins[seat]); out.Integer(record.pendingRewards[seat]);
        }
    });
    out.Number(Checksum(out.bytes));
    return out.bytes.size() <= MaxSaveBytes ? out.bytes : std::string{};
}

bool Match::RestorePreparation(const std::string &bytes, std::string &error)
{
    error.clear();
    if (catalog_.profileId != "wonder_vnext") { error = "Saves require the wonder_vnext profile"; return false; }
    if (networked_) { error = "A network match cannot restore an offline save"; return false; }
    try
    {
        if (bytes.size() < 8 || bytes.size() > MaxSaveBytes) throw std::runtime_error("Invalid save size");
        const std::string payload = bytes.substr(0, bytes.size() - 8);
        Reader checksumReader{bytes, bytes.size() - 8};
        if (checksumReader.Number() != Checksum(payload)) throw std::runtime_error("Save integrity check failed");
        Reader in{payload};
        if (in.Text() != SaveMagic || in.Text() != catalog_.profileId || in.Text() != catalog_.schemaVersion ||
            in.Text() != catalog_.balanceVersion || in.Text() != catalog_.contentDigest)
            throw std::runtime_error("Save profile or content version does not match this build");
        Match pending(catalog_, 1, 0);
        pending.seats_.clear(); pending.pairs_.clear(); pending.meetings_.clear(); pending.previousPairs_.clear();
        pending.originalHumans_ = in.Integer(0, 1); pending.networked_ = in.Boolean();
        if (pending.networked_) throw std::runtime_error("Save is not an offline match");
        pending.seed_ = in.Number(); pending.nextUnit_ = in.Number(); pending.nextRequest_ = in.Number();
        if (pending.nextUnit_ == 0 || pending.nextUnit_ >= (Id(1) << 20)) throw std::runtime_error("Invalid next unit identity");
        pending.round_ = in.Integer(1, catalog_.rules.maxRounds);
        pending.pvpRoundIndex_ = in.Integer(0, pending.round_);
        pending.remainingMs_ = in.Integer(0, std::max(catalog_.rules.firstPreparationMs, catalog_.rules.preparationMs));
        pending.elapsedMs_ = in.Integer(0, 1000000000); pending.accumulatorMs_ = in.Integer(0, 1000000);
        pending.previousGhost_ = in.Integer(-1, 7); pending.capped_ = in.Boolean();
        in.Count(8, [&] {
            SeatState seat;
            seat.id = in.Integer(0, 7); seat.health = in.Integer(0, catalog_.rules.startingHealth);
            seat.gold = in.Integer(0, 1000000); seat.xp = in.Integer(0, 1000000);
            seat.level = in.Integer(catalog_.rules.startingLevel, catalog_.rules.maximumLevel);
            seat.placement = in.Integer(0, 8); seat.wins = in.Integer(0, catalog_.rules.maxRounds);
            seat.lockGold = in.Integer(0, 1000000); seat.botIndex = in.Integer(0, int(catalog_.bots.size()) - 1);
            seat.human = in.Boolean(); seat.takeover = in.Boolean(); seat.ready = in.Boolean();
            seat.shopLocked = in.Boolean(); seat.label = in.Text();
            const Id revision = in.Number();
            if (revision > 0xffffffffULL) throw std::runtime_error("Invalid logical revision");
            seat.revision = (pending.matchNamespace_ << 32) | revision; seat.sequence = in.Number();
            if (seat.sequence > 1000000) throw std::runtime_error("Invalid command sequence");
            seat.shopRng.state = in.Number(); seat.botRng.state = in.Number(); seat.relicRng.state = in.Number();
            seat.neutralWins = in.Integer(0, catalog_.rules.maxRounds);
            seat.neutralLosses = in.Integer(0, catalog_.rules.maxRounds);
            seat.neutralDraws = in.Integer(0, catalog_.rules.maxRounds);
            seat.pendingRelicDrafts = in.Integer(0, catalog_.rules.maximumRelics);
            in.Count(catalog_.rules.shopSlots, [&] { seat.shop.push_back(in.Integer(-1, int(catalog_.units.size()) - 1)); });
            if (int(seat.shop.size()) != catalog_.rules.shopSlots) throw std::runtime_error("Save shop size mismatch");
            in.Count(catalog_.rules.maximumLevel + catalog_.rules.benchCapacity, [&] { seat.roster.push_back(ReadUnit(in)); });
            in.Count(catalog_.rules.maximumRelics, [&] { seat.ownedRelics.push_back(in.Integer(0, int(catalog_.relics.size()) - 1)); });
            in.Count(3, [&] { seat.relicOffers.push_back(in.Integer(0, int(catalog_.relics.size()) - 1)); });
            if (seat.id != int(pending.seats_.size())) throw std::runtime_error("Save seats are not in canonical order");
            if ((seat.level == catalog_.rules.maximumLevel && seat.xp != 0) ||
                (seat.level < catalog_.rules.maximumLevel && seat.xp >= catalog_.rules.xpToNext.at(seat.level)))
                throw std::runtime_error("Save XP is not normalized");
            pending.seats_.push_back(std::move(seat));
        });
        if (pending.seats_.size() != 8 || std::count_if(pending.seats_.begin(), pending.seats_.end(),
            [](const SeatState &seat) { return seat.human; }) > 1) throw std::runtime_error("Save is not an offline match");
        in.Count(8, [&] { pending.pairs_.push_back(ReadPair(in)); });
        in.Count(28, [&] {
            const int a = in.Integer(0, 7), b = in.Integer(0, 7), count = in.Integer(0, catalog_.rules.maxRounds);
            if (a >= b || !pending.meetings_.emplace(std::make_pair(a, b), count).second)
                throw std::runtime_error("Invalid pairing history");
        });
        in.Count(4, [&] {
            const int a = in.Integer(0, 7), b = in.Integer(0, 7);
            if (a >= b) throw std::runtime_error("Invalid previous pair");
            pending.previousPairs_.emplace_back(a, b);
        });
        for (int seat = 0; seat < 8; ++seat)
        {
            pending.ghostCounts_[seat] = in.Integer(0, catalog_.rules.maxRounds);
            pending.botCommands_[seat] = in.Integer(0, 10000); pending.botRerolls_[seat] = in.Integer(0, 10000);
            pending.botNextMs_[seat] = in.Integer(0, 1000000000);
            pending.botObserveNextMs_[seat] = in.Integer(0, 1000000000);
            pending.botObservationRevision_[seat] = in.Number(); pending.lastWon_[seat] = in.Boolean();
            pending.pendingRewards_[seat] = in.Integer(0, 1000000); pending.botObservations_[seat].clear();
            in.Count(8, [&] { pending.botObservations_[seat].push_back(ReadPublic(in)); });
            ValidateObservations(pending.botObservations_[seat], catalog_, pending.nextUnit_);
        }
        in.Count(catalog_.rules.maxRounds, [&] {
            RoundRecord record;
            record.round = in.Integer(1, pending.round_ - 1); record.pvpRoundIndex = in.Integer(0, record.round);
            record.settlementId = in.Number(); record.preHash = in.Number(); record.postHash = in.Number();
            record.neutral = in.Boolean();
            in.Count(8, [&] { record.pairs.push_back(ReadPair(in)); });
            in.Count(8, [&] {
                record.results.push_back(ReadResult(in, catalog_));
            });
            in.Count(8, [&] {
                EncounterSummary encounter;
                encounter.pairing = ReadPair(in); encounter.result = ReadResult(in, catalog_);
                encounter.kind = EncounterKind(in.Integer(0, 2));
                for (int side = 0; side < 2; ++side)
                {
                    const Id loss = in.Number(), absorbed = in.Number(), healing = in.Number();
                    if (loss > 1000000000000ULL || absorbed > 1000000000000ULL || healing > 1000000000000ULL)
                        throw std::runtime_error("Invalid saved recap totals");
                    encounter.healthLoss[side] = Int(loss); encounter.absorbed[side] = Int(absorbed); encounter.healing[side] = Int(healing);
                    const int owner = in.Integer(-1, 7);
                    if (owner >= 0) encounter.sides[side].seat = owner;
                    encounter.sides[side].waveId = in.Text();
                }
                const auto index = record.encounters.size();
                if (index >= record.pairs.size() || index >= record.results.size() || encounter.pairing.a != record.pairs[index].a ||
                    encounter.pairing.b != record.pairs[index].b || encounter.kind != record.pairs[index].kind ||
                    encounter.pairing.kind != encounter.kind || encounter.result.winner != record.results[index].winner ||
                    encounter.result.ticks != record.results[index].ticks)
                    throw std::runtime_error("Saved recap does not match its round");
                record.encounters.push_back(std::move(encounter));
            });
            if (record.pairs.size() != record.results.size()) throw std::runtime_error("Save round result count mismatch");
            if (record.encounters.size() != record.results.size()) throw std::runtime_error("Save recap count mismatch");
            for (int seat = 0; seat < 8; ++seat)
            {
                record.damage[seat] = in.Integer(0, 1000000); record.gold[seat] = in.Integer(0, 1000000);
                record.health[seat] = in.Integer(0, catalog_.rules.startingHealth); record.placement[seat] = in.Integer(0, 8);
                record.wins[seat] = in.Integer(0, catalog_.rules.maxRounds); record.pendingRewards[seat] = in.Integer(0, 1000000);
            }
            if (record.round != int(pending.records_.size()) + 1) throw std::runtime_error("Save round history is incomplete");
            pending.records_.push_back(std::move(record));
        });
        if (int(pending.records_.size()) != pending.round_ - 1 || in.offset != payload.size())
            throw std::runtime_error("Save history or payload length mismatch");
        pending.phase_ = Phase::Preparation;
        const auto issue = pending.InvariantError();
        if (!issue.empty()) throw std::runtime_error(issue);
        // A fresh transport namespace rejects commands from the process that wrote this save.
        // All logical RNG streams and pending decisions retain their exact state.
        *this = std::move(pending);
        return true;
    }
    catch (const std::exception &exception) { error = exception.what(); return false; }
}
} // namespace wc
