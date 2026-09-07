#pragma once
#include <array>
#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <utility>
#include <vector>

// The authoritative core has no renderer, clock, networking, or Python dependency.
namespace wc
{
using Int = std::int64_t;
using Id = std::uint64_t;
struct Cell
{
    int column = -1, row = -1;
    bool operator==(Cell b) const
    {
        return column == b.column && row == b.row;
    }
};
enum class DamageType
{
    Physical,
    Magic,
    True
};
enum class Effect
{
    Damage,
    Heal,
    Shield,
    Stun,
    Dash,
    StatModifier
};
enum class Selector
{
    Self,
    CurrentEnemy,
    AdjacentEnemies,
    AdjacentAllies,
    LowestHealthAlly,
    HighestAttackRateEnemy,
    CurrentEnemyArea,
    RetreatFromCurrentEnemy,
    CurrentEnemyAdjacent,
    FarthestEnemyAdjacent
};
enum class ActionState
{
    Idle,
    Seeking,
    Moving,
    AttackWindup,
    AttackRecovery,
    CastWindup,
    CastRecovery,
    Stunned,
    Defeated
};
enum class Phase
{
    Preparation,
    Combat,
    Settlement,
    Finished,
    Aborted
};
enum class CommandType
{
    Buy,
    Sell,
    Reroll,
    ToggleLock,
    BuyXp,
    Move,
    Ready
};
struct AbilityEffect
{
    Effect effect = Effect::Damage;
    DamageType damageType = DamageType::Physical;
    int durationMs = 0;
    std::array<Int, 3> magnitude{};
};
struct AbilityDef
{
    std::string id, name;
    Effect effect = Effect::Damage;
    Selector selector = Selector::CurrentEnemy;
    DamageType damageType = DamageType::Physical;
    int firstCastMs = 0, cooldownMs = 0, castMs = 0, recoveryMs = 0, durationMs = 0, travelMs = 0;
    int radius = 0, range = 0, maxTargets = 0, maxDash = 0;
    bool allowSelf = false;
    std::array<Int, 3> magnitude{};
    bool enabled = true;
    std::vector<AbilityEffect> effects;
};
struct UnitDef
{
    std::string id, name, race, unitClass;
    int cost = 0;
    Int health = 0, attackDamage = 0;
    int attackRate = 0, range = 0, armor = 0, resistance = 0, movementRate = 0, attackWindupMs = 0,
        projectileTravelMs = 0;
    DamageType damageType = DamageType::Physical;
    AbilityDef ability;
    std::string displayName;
    std::vector<std::string> roleTags;
};
struct TraitDef
{
    std::string id, stat;
    int threshold = 0, value = 0;
    int threshold4 = 4, value4 = 0;
};
int TraitValue(const TraitDef &trait, int distinctCount);
struct BotDef
{
    std::string id, label;
    double frontline = 0, damage = 0, support = 0, upgrade = 0, synergy = 0, level = 0, save = 0;
    int decisionIntervalMs = 0, observationMs = 0, maxCommands = 0, maxRerolls = 0, noiseBp = 0;
};
struct LossStage
{
    int start = 0, end = 0, damage = 0;
};
struct Rules
{
    int columns = 0, rows = 0, deploymentRows = 0, tileSizeCm = 0, tickMs = 0;
    int minAttackRate = 0, maxAttackRate = 0;
    Int maxHealth = 0, maxArmor = 0, maxRawDamage = 0;
    std::array<int, 3> starMultiplierBp{};
    int seatCount = 0, startingHealth = 0, maxRounds = 0, firstPreparationMs = 0, preparationMs = 0,
        combatTimeoutMs = 0, settlementMs = 0, drawDamage = 0;
    std::vector<LossStage> lossStages;
    int startingGold = 0, benchCapacity = 0, shopSlots = 0, rerollCost = 0, baseIncome = 0, winIncome = 0,
        interestDivisor = 0, interestCap = 0;
    int startingLevel = 0, maximumLevel = 0, buyXpGold = 0, buyXpAmount = 0, passiveXp = 0;
    std::map<int, int> xpToNext;
    std::map<int, std::array<int, 3>> shopWeights;
    int botObservationMs = 0, botRepositionCutoffMs = 0;
    int neutralOpeningRounds = 3, neutralEvery = 5, neutralWinIncome = 2,
        neutralLossDamage = 2, neutralOpeningDamage = 0;
};
struct NeutralSlot
{
    int definition = -1;
    Cell cell;
};
struct NeutralWave
{
    std::string id, name;
    int round = 0, hpScaleBp = 10000, damageScaleBp = 10000;
    std::vector<NeutralSlot> slots;
};
struct Catalog
{
    std::string schemaVersion, balanceVersion, contentDigest;
    Rules rules;
    std::vector<UnitDef> units;
    std::vector<TraitDef> traits;
    std::vector<BotDef> bots;
    std::vector<UnitDef> neutrals;
    std::vector<NeutralWave> waves;
    const UnitDef &Definition(int index, bool neutral = false) const;
    const NeutralWave *Wave(int round) const;
    std::string Validate() const;
};
bool IsNeutralRound(int round, const Rules &rules);
Int HalfUp(Int numerator, Int denominator);
Int ResolveDamage(Int raw, DamageType type, int armor, int resistance, int bonusBp = 0);
Int StarValue(Int base, int star, int bonusBp, const Rules &rules);
int AttackInterval(int baseRate, int bonusBp, const Rules &rules);
int MovementInterval(int baseRate, int bonusBp, const Rules &rules);
int Distance(Cell a, Cell b);
Cell EncounterCell(Cell local, int side, const Rules &rules);
struct Random
{
    Id state = 1;
    Id Next();
    int Below(int exclusive);
};
struct OwnedUnit
{
    Id id = 0;
    int definition = -1, star = 1;
    bool onBoard = false;
    Cell cell;
    int bench = -1;
    bool neutral = false;
    int hpScaleBp = 10000, damageScaleBp = 10000;
};
struct Command
{
    CommandType type = CommandType::Ready;
    int seat = -1;
    Id requestId = 0, sequence = 0, revision = 0, unit = 0;
    int slot = -1;
    bool toBoard = false;
    Cell cell;
};
struct Reply
{
    bool accepted = false;
    std::string reason;
    Id revision = 0, sequence = 0;
};
struct SeatState
{
    int id = -1, health = 0, gold = 0, xp = 0, level = 0, placement = 0, wins = 0, lockGold = 0, botIndex = 0;
    bool human = false, takeover = false, ready = false, shopLocked = false;
    std::string label;
    Id revision = 0, sequence = 0;
    std::vector<int> shop;
    std::vector<OwnedUnit> roster;
    Random shopRng, botRng;
    int neutralWins = 0, neutralLosses = 0, neutralDraws = 0;
};
struct PublicSeat
{
    int id = -1, health = 0, level = 0, placement = 0, wins = 0;
    bool human = false, ready = false, takeover = false;
    std::string label;
    std::vector<OwnedUnit> deployment;
};
struct MergeStep
{
    Id survivorId = 0;
    int fromStar = 1, toStar = 2;
    std::array<Id, 2> consumedIds{};
};
struct RosterPreview
{
    bool accepted = false;
    std::string reason;
    SeatState resulting;
    Id hypotheticalId = 0;
    std::vector<MergeStep> mergeSteps;
};
// Owner-state inventory projection only; authentication, phase and revision stay authoritative.
// A new unit ID is hypothetical. This never allocates a match namespace or advances RNG.
RosterPreview PreviewRosterCommand(const Catalog &catalog, const SeatState &owner, const Command &command);
enum class EncounterKind { Pvp, Ghost, Neutral };
struct EncounterSide
{
    std::optional<int> seat;
    std::string waveId;
};
struct Pairing
{
    int a = -1, b = -1;
    bool ghost = false;
    EncounterKind kind = EncounterKind::Pvp;
    std::string waveId;
};
struct Modifier
{
    std::string key;
    Int magnitude = 0;
    int expiry = 0;
};
struct CombatUnit
{
    Id id = 0, actionId = 0;
    // Presentation identity only; never consumed by combat decisions or effects.
    Id basicAttackOrdinal = 0;
    int definition = -1, side = 0, star = 1, initiative = 0, target = -1;
    Cell cell, destination;
    Int health = 0, maxHealth = 0, shield = 0, basicDamage = 0;
    int armor = 0, resistance = 0, basicBonus = 0, abilityBonus = 0, allBonus = 0, rateBonus = 0,
        supportBonus = 0;
    int shieldExpiry = 0, stunExpiry = 0, cooldownTick = 0, releaseTick = 0, recoveryTick = 0,
        movementTick = 0;
    Id shieldSource = 0;
    std::string shieldKey;
    ActionState state = ActionState::Idle;
    std::vector<Modifier> modifiers;
    bool neutral = false;
    int movementBonus = 0, hpScaleBp = 10000, damageScaleBp = 10000;
};
struct CombatEvent
{
    int tick = 0;
    Id source = 0, target = 0, action = 0;
    Effect effect = Effect::Damage;
    Int requested = 0, resolved = 0, absorbed = 0, healthLoss = 0, overkill = 0;
    Cell cell;
    Id absorbedFrom = 0;
    DamageType damageType = DamageType::Physical;
    bool basicAttack = false;
    int radius = 0;
};
struct CombatResult
{
    bool complete = false, timeout = false;
    int winner = -1, ticks = 0;
    std::array<int, 2> survivors{};
};
struct VisualAction
{
    Id source = 0, target = 0, action = 0;
    int definition = -1, radius = 0, releaseTick = 0, impactTick = 0;
    Cell origin, center;
    Effect effect = Effect::Damage;
    DamageType damageType = DamageType::Physical;
    bool neutral = false, basicAttack = false, released = false, provisional = true,
         recipientsProvisional = true, fixedArea = false;
    std::vector<Id> recipients;
};
class Combat
{
  public:
    Combat(const Catalog &catalog, const std::vector<OwnedUnit> &a, const std::vector<OwnedUnit> &b, Id seed,
           Id encounterId = 0);
    void Tick();
    const std::vector<CombatUnit> &Units() const
    {
        return units_;
    }
    const std::vector<CombatEvent> &Events() const
    {
        return events_;
    }
    const CombatResult &Result() const
    {
        return result_;
    }
    int CurrentTick() const
    {
        return tick_;
    }
    std::string InvariantError() const;
    std::vector<VisualAction> VisualActions() const;

  private:
    struct Packet
    {
        int due = 0, releasedAt = 0, source = -1, target = -1, radius = 0, duration = 0;
        Id action = 0;
        Effect effect = Effect::Damage;
        DamageType damageType = DamageType::Physical;
        Int magnitude = 0;
        int bonus = 0;
        Cell center, origin;
        bool area = false, basicAttack = false;
        std::string key;
        int effectOrder = 0, maxTargets = 12;
    };
    const Catalog *catalog_;
    std::vector<CombatUnit> units_;
    std::vector<Packet> packets_;
    std::vector<CombatEvent> events_;
    CombatResult result_;
    int tick_ = 0;
    Id nextAction_ = 1;
    bool draining_ = false;
    bool Free(Cell cell, int except = -1) const;
    void CancelReservation(int unit);
    std::vector<int> Select(int source, const AbilityDef &ability) const;
    bool DashLanding(int source, const AbilityDef &ability, int &target, Cell &cell) const;
    bool FindPath(int source, int target, Cell &next, int &length) const;
    int ChooseEnemy(int source, Cell &next, int &pathLength) const;
    bool CommitAbility(int source);
    void Release(int source);
    void Apply(const Packet &packet, int target);
    void Assess(bool timeout);
};
struct Encounter
{
    Pairing pairing;
    Combat combat;
    EncounterKind kind = EncounterKind::Pvp;
    std::array<EncounterSide, 2> sides;
    Encounter(Pairing p, Combat c) : pairing(p), combat(std::move(c)), kind(p.kind)
    {
        sides[0].seat = p.a;
        if (p.kind == EncounterKind::Neutral) sides[1].waveId = p.waveId;
        else sides[1].seat = p.b;
    }
};
struct BotDecision
{
    int round = 0, seat = -1;
    Id observationRevision = 0;
    std::string action;
    std::array<double, 8> features{};
    double score = 0;
    Reply reply;
    int goldAfter = 0;
};
struct EncounterSummary
{
    Pairing pairing;
    CombatResult result;
    std::array<Int, 2> healthLoss{}, absorbed{}, healing{};
    EncounterKind kind = EncounterKind::Pvp;
    std::array<EncounterSide, 2> sides;
};
struct RoundRecord
{
    int round = 0, pvpRoundIndex = 0;
    Id settlementId = 0, preHash = 0, postHash = 0;
    std::vector<Pairing> pairs;
    std::vector<CombatResult> results;
    std::vector<EncounterSummary> encounters;
    std::array<int, 8> damage{}, gold{}, health{}, placement{}, wins{};
    std::array<int, 8> pendingRewards{};
    bool neutral = false;
};
class Match
{
  public:
    Match(Catalog catalog, Id seed, int humans);
    void Restart(Id seed, int humans);
    void Tick(int elapsedMs);
    Reply Submit(int authenticatedSeat, const Command &command);
    void TakeOver(int seat);
    void Abort();
    const Catalog &Definitions() const
    {
        return catalog_;
    }
    const std::vector<SeatState> &Seats() const
    {
        return seats_;
    }
    const std::vector<Encounter> &Encounters() const
    {
        return encounters_;
    }
    const std::vector<Pairing> &Pairings() const
    {
        return pairs_;
    }
    std::vector<PublicSeat> PublicSeats() const;
    const std::vector<RoundRecord> &Records() const
    {
        return records_;
    }
    const std::vector<BotDecision> &BotLog() const
    {
        return botLog_;
    }
    Phase CurrentPhase() const
    {
        return phase_;
    }
    int Round() const
    {
        return round_;
    }
    int PvpRoundIndex() const { return pvpRoundIndex_; }
    bool NeutralRound() const { return IsNeutralRound(round_, catalog_.rules); }
    const NeutralWave *CurrentWave() const { return catalog_.Wave(round_); }
    int RemainingMs() const
    {
        return remainingMs_;
    }
    int ElapsedMs() const
    {
        return elapsedMs_;
    }
    bool Capped() const
    {
        return capped_;
    }
    Id Seed() const
    {
        return seed_;
    }
    Id Namespace() const
    {
        return matchNamespace_;
    }
    std::string InvariantError() const;

  private:
    struct CacheEntry
    {
        Command command;
        Reply reply;
    };
    Catalog catalog_;
    Id seed_ = 0, nextUnit_ = 1, nextRequest_ = 1, matchNamespace_ = 0;
    int round_ = 0, remainingMs_ = 0, elapsedMs_ = 0, accumulatorMs_ = 0, previousGhost_ = -1;
    int pvpRoundIndex_ = 0;
    Phase phase_ = Phase::Preparation;
    bool capped_ = false;
    std::vector<SeatState> seats_;
    std::vector<Pairing> pairs_;
    std::vector<Encounter> encounters_;
    std::vector<RoundRecord> records_;
    std::vector<BotDecision> botLog_;
    std::map<std::pair<int, Id>, CacheEntry> replies_;
    std::map<std::pair<int, int>, int> meetings_;
    std::vector<std::pair<int, int>> previousPairs_;
    std::array<int, 8> ghostCounts_{}, botCommands_{}, botRerolls_{}, botNextMs_{};
    std::array<int, 8> botObserveNextMs_{};
    std::array<Id, 8> botObservationRevision_{};
    std::array<std::vector<PublicSeat>, 8> botObservations_;
    std::array<bool, 8> lastWon_{};
    std::array<int, 8> pendingRewards_{};
    void Refresh(SeatState &seat);
    void GainXp(SeatState &seat, int xp);
    bool ApplyCommand(SeatState &seat, const Command &command, Id &nextUnit, std::string &reason);
    bool Legal(const SeatState &seat) const;
    void Prepare();
    void Pair();
    void Lock();
    void Settle();
    void BotTurn(int seat);
    double FormationScore(const SeatState &seat, const BotDef &bot) const;
    Cell FormationCell(const SeatState &seat, const OwnedUnit &unit) const;
    Id StateHash() const;
};
} // namespace wc
