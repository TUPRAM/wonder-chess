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
    StatModifier,
    // Statuses: a hexed unit can only walk, a silenced unit cannot cast, a taunted unit must
    // attack whoever taunted it. Their magnitude is the duration in milliseconds at each star.
    Hex,
    Silence,
    Taunt,
    // Removes mana (centimana) from the target, never below zero.
    ManaDrain,
    // The caster moves at once to a cell chosen by a cell selector, relative to the ability's target.
    Blink,
    // Adds units to the caster's side at the start of the next tick. In events: a summon arriving
    // (source is its owner, resolved its health) or leaving when its time is up (source is itself).
    Summon
};
inline bool IsStatusEffect(Effect effect)
{
    return effect == Effect::Hex || effect == Effect::Silence || effect == Effect::Taunt;
}
enum class AbilityMechanic
{
    Standard,
    DirectionalGuard,
    MomentumCharge,
    StationaryGrove,
    ScreenedStrike,
    CrossingBeams,
    TidalPush,
    CocoonProjectile
};
// Preparation orientation is local; the opposing formation is rotated by 180 degrees.
enum class Facing { Forward, Right, Backward, Left };
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
    FarthestEnemyAdjacent,
    // One enemy: the farthest in range, or the one with the lowest share of health.
    FarthestEnemy,
    LowestHealthEnemy,
    // Every ally, anywhere on the board.
    AllAllies,
    // An area centred on the cell that covers the most enemies.
    DensestEnemyArea,
    // maxTargets separate areas, each on the cell of a randomly chosen enemy.
    RandomEnemyAreas,
    // Every enemy on the line through the current enemy to the board edge, or in a cone toward it.
    EnemyLine,
    EnemyCone,
    // The current enemy, then the nearest enemy to each one hit, up to maxTargets.
    ChainFromCurrentEnemy,
    // Cell selectors, for a blink only: the free cell next to the target nearest the caster; the
    // free cell next to the target farthest past it; the farthest free cell on the line through
    // the target, within maxDash cells.
    CellBesideTarget,
    CellBehindTarget,
    CellThroughTarget,
    // For a summon only: the cells where units have fallen in this fight, newest first.
    FallenUnits
};
inline bool IsCellSelector(Selector selector)
{
    return selector == Selector::CellBesideTarget || selector == Selector::CellBehindTarget ||
           selector == Selector::CellThroughTarget;
}
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
    Ready,
    ChooseRelic,
    EquipRelic,
    UnequipRelic,
    SetFacing
};
// The stat a timed modifier changes. Attack rate, attack damage, damage dealt, damage taken and
// movement are in basis points; armour and resistance are flat points. Negative values are debuffs.
enum class ModifierStat
{
    AttackRate,
    AttackDamage,
    Armor,
    Resistance,
    DamageDealt,
    DamageTaken,
    Movement,
    // Share of health lost that is returned to the attacker as true damage.
    Reflect
};
struct AbilityEffect
{
    Effect effect = Effect::Damage;
    DamageType damageType = DamageType::Physical;
    int durationMs = 0;
    std::array<Int, 3> magnitude{};
    // Chain fields. An effect lands delayMs after the ability's own impact time, and either
    // reuses the ability's targets or picks its own with `selector` when the ability releases.
    int delayMs = 0;
    bool ownSelector = false;
    Selector selector = Selector::CurrentEnemy;
    // Which stat a StatModifier effect changes.
    ModifierStat stat = ModifierStat::AttackRate;
    // A repeating effect lands every repeatMs for durationMs (damage over time on a unit, or a
    // zone when the selector is an area). A following zone stays centred on its caster.
    int repeatMs = 0;
    bool follow = false;
    // A direct hit that is always a critical hit.
    bool critical = false;
    // A summon effect: which definition in the catalogue's neutral list, and how many. Its
    // durationMs is how long each unit stays (zero: until it falls).
    int summon = -1, count = 1;
};
struct ManaDef
{
    // Centimana: 10000 is 100 displayed mana; zero maximum keeps existing activation.
    int maximum = 0, starting = 0, basicAttackGain = 0, damageGainAtFullHealth = 0,
        damageEventCap = 0, damageWindowCap = 0, damageWindowMs = 1000, gainDivisorBp = 10000;
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
    AbilityMechanic mechanic = AbilityMechanic::Standard;
    ManaDef mana;
    int guardReductionBp = 0, momentumPerStepBp = 0, maxMomentumSteps = 0,
        stationaryMs = 0, pulseMs = 0, displacementCells = 0, secondaryDelayMs = 0;
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
    // Never moves, attacks or casts, and alone does not keep a fight going (a wall).
    bool inert = false;
};
struct RelicDef
{
    std::string id, name, description;
    // An empty list fits every hero; a listed relic fits only those mechanics.
    std::vector<AbilityMechanic> compatibleMechanics;
    int magnitudeBp = 10000, rangeDelta = 0, radiusDelta = 0, durationBp = 10000,
        castBp = 10000, cooldownBp = 10000;
    // Holder stat benefits, applied once when combat starts.
    int healthBp = 0, attackDamageBp = 0, attackRateBp = 0, skillPowerBp = 0, allDamageBp = 0,
        armorFlat = 0, resistanceFlat = 0;
};
bool RelicCompatible(const RelicDef &relic, AbilityMechanic mechanic);
struct TraitDef
{
    std::string id, stat;
    int threshold = 0, value = 0;
    int threshold4 = 4, value4 = 0;
    std::vector<std::pair<int, int>> tiers;
    // Team traits reach every recruited ally once the members meet a tier.
    bool team = false;
    // How long a status given by the trait lasts; zero for every other trait.
    int durationMs = 0;
};
int TraitValue(const TraitDef &trait, int distinctCount);
// Bot hints for one class: how a bot values the class and where it stands. Empty in
// catalogues that still rely on the legacy class names.
enum class BotRole
{
    Frontline,
    Damage,
    Support
};
struct ClassRole
{
    std::string id;
    BotRole role = BotRole::Damage;
    // Preferred deployment row, 3 = front. Flanking classes fill columns from the edges.
    int row = 0;
    bool flank = false;
};
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
// Preparation time for rounds start..end.
struct PreparationStage
{
    int start = 0, end = 0, ms = 0;
};
// A run of this many player-fight wins, or losses, in a row pays this much extra gold each round.
struct StreakStep
{
    int length = 0, gold = 0;
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
    // Round 1 uses firstPreparationMs; a later round uses its stage, or preparationMs when no stage covers it.
    std::vector<PreparationStage> preparationStages;
    // The longest step reached pays; an empty list pays nothing.
    std::vector<StreakStep> streakIncome;
    // When preparation ends, benched units fill free board places, lowest bench slot first.
    bool autoDeploy = false;
    int startingGold = 0, benchCapacity = 0, shopSlots = 0, rerollCost = 0, baseIncome = 0, winIncome = 0,
        interestDivisor = 0, interestCap = 0;
    int startingLevel = 0, maximumLevel = 0, buyXpGold = 0, buyXpAmount = 0, passiveXp = 0;
    std::map<int, int> xpToNext;
    std::map<int, std::array<int, 5>> shopWeights;
    int botObservationMs = 0, botRepositionCutoffMs = 0;
    int neutralOpeningRounds = 3, neutralEvery = 5, neutralWinIncome = 2,
        neutralLossDamage = 2, neutralOpeningDamage = 0;
    std::vector<int> relicRounds;
    int maximumRelics = 3;
    bool nearestReachableTarget = false, mobileAttackRecovery = false;
    // Units step straight at their target, diagonally past neighbours when that is the direct way.
    bool directMovement = false;
    // A momentum charge strikes along its line and the charger ends on the cell it started from.
    bool chargeReturns = false;
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
    std::vector<ClassRole> classRoles;
    // Bots treat gold above the interest cap as free to spend on experience and rerolls.
    bool botSpendsSurplus = false;
    std::vector<UnitDef> neutrals;
    // How many summoned units one side may have alive at once.
    int summonLimit = 0;
    std::vector<NeutralWave> waves;
    std::string profileId = "alpha_24";
    std::vector<RelicDef> relics;
    bool ownedTeamRelicOffers = false;
    const UnitDef &Definition(int index, bool neutral = false) const;
    const NeutralWave *Wave(int round) const;
    std::string Validate() const;
};
AbilityDef EffectiveAbility(const Catalog &catalog, const UnitDef &unit, int relic = -1);
struct SeatState;
// What a bot thinks a seat's best line-up is worth: unit budget, role cover and traits.
double BotLineupValue(const SeatState &seat, const Catalog &catalog, const BotDef &bot);
// Extra gold a seat's fielded traits pay for a won player fight.
int TraitWinGold(const SeatState &seat, const Catalog &catalog);
bool IsNeutralRound(int round, const Rules &rules);
int PreparationMs(const Rules &rules, int round);
// Gold for a streak of the given signed length (wins positive, losses negative).
int StreakIncome(const Rules &rules, int streak);
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
    Facing facing = Facing::Forward;
    int relic = -1;
};
struct Command
{
    CommandType type = CommandType::Ready;
    int seat = -1;
    Id requestId = 0, sequence = 0, revision = 0, unit = 0;
    int slot = -1;
    bool toBoard = false;
    Cell cell;
    Facing facing = Facing::Forward;
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
    // Player fights won in a row (positive) or lost in a row (negative). A draw resets it; monster rounds leave it.
    int streak = 0;
    std::vector<int> ownedRelics, relicOffers;
    Random relicRng;
    int pendingRelicDrafts = 0;
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
// The guided first match. A stage is a prepared position for the captain against one fixed opponent, with the
// steps the captain is walked through. Authored in the catalogue under "tutorial".
struct GuidedUnit
{
    int definition = -1, star = 1;
    Cell cell;
};
struct GuidedStep
{
    std::string textEn, textId;
    // The screen control to point at, by its tag; may be empty.
    std::string highlight;
    // What completes the step, and what it refers to: a hero, a trait, a number.
    std::string done, trait;
    int definition = -1, value = 0;
    // The orders the captain may give meanwhile.
    std::vector<CommandType> allow;
};
struct GuidedStage
{
    std::string id, titleEn, titleId;
    int round = 4, gold = 0, level = 3, streak = 0;
    bool fight = true, relicDraft = false;
    std::vector<GuidedUnit> board, bench, opponent;
    std::vector<int> shop;
    std::vector<GuidedStep> steps;
};
struct Tutorial
{
    std::vector<GuidedStage> stages;
};
// What the screen knows that the match does not.
struct GuidedView
{
    bool shopOpen = false;
    std::string traitFocus;
};
inline bool GuidedAllows(const GuidedStep &step, CommandType type)
{
    for (const auto allowed : step.allow) if (allowed == type) return true;
    return false;
}
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
// Statuses of the same kind do not stack: the one that ends later stays.
enum class UnitStatus
{
    Hex,
    Silence,
    Taunt
};
struct StatusState
{
    int expiry = 0;
    // Index of the unit that caused it, or -1 for a trait.
    int source = -1;
};
struct Modifier
{
    std::string key;
    Int magnitude = 0;
    int expiry = 0;
    ModifierStat stat = ModifierStat::AttackRate;
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
        movementTick = 0, basicReadyTick = 0;
    Id shieldSource = 0;
    // Separate from generic stun so targeting can skip only existing cocoons.
    int cocoonExpiry = 0;
    Id cocoonSource = 0;
    std::string shieldKey;
    ActionState state = ActionState::Idle;
    std::vector<Modifier> modifiers;
    bool neutral = false;
    int movementBonus = 0, hpScaleBp = 10000, damageScaleBp = 10000;
    Facing facing = Facing::Forward;
    int momentumSteps = 0, lastMovementTick = 0, positionEpoch = 0;
    int mana = 0, manaResumeTick = 0, manaWindowStart = 0, manaWindowGained = 0;
    Id lastManaAttackAction = 0;
    int castsCommitted = 0, firstCastTick = -1, manaBlockedAttempts = 0, manaOnDeath = 0;
    Int manaFromAttacks = 0, manaFromDamage = 0, manaSpent = 0;
    Cell abilityAim;
    int relic = -1;
    AbilityDef ability;
    // Fight-start values from traits: extra attack reach, health regenerated per second (basis
    // points of maximum health), mana per second (centimana) and ability damage shrugged off.
    int rangeBonus = 0, regenBp = 0, manaPerSecond = 0, abilityReductionBp = 0;
    Int manaFromRegen = 0;
    // Chance to dodge a basic attack, chance to crit with one, share of damage dealt healed back,
    // and share of damage dealt again as true damage. All in basis points.
    int evasionBp = 0, critChanceBp = 0, lifestealBp = 0, bonusTrueDamageBp = 0;
    std::array<StatusState, 3> statuses{};
    Int manaDrained = 0;
    // A unit added during the fight: who summoned it, and the tick it leaves (zero: never).
    bool summoned = false;
    int owner = -1, expiryTick = 0;
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
    AbilityMechanic mechanic = AbilityMechanic::Standard;
    Cell origin;
    Id guardedBy = 0;
    Int prevented = 0;
    std::vector<Cell> visualCells;
    // For StatModifier events: the stat that changed.
    ModifierStat stat = ModifierStat::AttackRate;
    // A dodged basic attack; a critical hit; an effect caused by another hit (lifesteal, bonus
    // true damage, reflect) rather than by an attack or ability directly.
    bool evaded = false, critical = false, secondary = false;
    // A hit from a repeating effect: damage over time, a ground zone or an aura.
    bool periodic = false;
};
struct CombatResult
{
    bool complete = false, timeout = false;
    int winner = -1, ticks = 0;
    std::array<int, 2> survivors{};
};
enum class MechanicPhase { Attempt, Committed, Released, Cancelled, Impact };
enum class MechanicReason
{
    Ready, NoLivingTarget, TargetOutOfRange, DashTooLong, NoMomentum,
    PathOccupied, CornerOccupied, NotEstablished, NoInjuredAlly,
    TargetMoved, SourceMoved, SourceStunned, SourceDefeated,
    TetherInvalidated, CombatEnded, TargetDefeated, Resolved, TargetAlreadyCocooned
};
const char *MechanicPhaseName(MechanicPhase phase);
const char *MechanicReasonName(MechanicReason reason);
struct MechanicTrace
{
    int tick = 0;
    Id source = 0, target = 0, action = 0;
    AbilityMechanic mechanic = AbilityMechanic::Standard;
    MechanicPhase phase = MechanicPhase::Attempt;
    MechanicReason reason = MechanicReason::Ready;
    Cell origin, aim, landing;
    int momentumSteps = 0, recipients = 0, fullHealthAllies = 0;
    Int requested = 0, resolved = 0;
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
    AbilityMechanic mechanic = AbilityMechanic::Standard;
    std::vector<Cell> cells;
};
// A repeating area effect that still has hits to land. For presentation only.
struct ZoneView
{
    Id source = 0, action = 0;
    Cell center;
    int radius = 0, side = 0, untilTick = 0;
    DamageType damageType = DamageType::Physical;
    bool follow = false;
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
    int ChanceDraws() const { return chanceDraws_; }
    // Summons that were dropped because the side was at its limit or no cell was free.
    int SummonsRefused() const { return summonsRefused_; }
    // Presentation helpers: ground zones and auras still running, and the units still under damage over time.
    std::vector<ZoneView> Zones() const;
    std::vector<int> PeriodicTargets() const;
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
    // Optional observer, enabled only before the first tick. Not gameplay events or saved state.
    bool EnableDiagnostics();
    const std::vector<MechanicTrace> &Diagnostics() const { return diagnostics_; }

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
        AbilityMechanic mechanic = AbilityMechanic::Standard;
        std::vector<Cell> cells;
        bool allied = false, allowSelf = false, tethered = false;
        int positionEpoch = 0, displacementCells = 0;
        ModifierStat stat = ModifierStat::AttackRate;
        bool secondary = false;
        bool periodic = false, follow = false;
        bool critical = false;
    };
    const Catalog *catalog_;
    std::vector<CombatUnit> units_;
    std::vector<Packet> packets_;
    std::vector<CombatEvent> events_;
    bool diagnosticsEnabled_ = false;
    std::vector<MechanicTrace> diagnostics_;
    CombatResult result_;
    int tick_ = 0;
    Id nextAction_ = 1;
    bool draining_ = false;
    // One stream for every chance roll in the fight, seeded with the fight, drawn only when a
    // unit actually has a chance-based rule. The same seed replays the same rolls.
    Random chance_;
    int chanceDraws_ = 0;
    bool Roll(int chanceBp);
    struct Spawn
    {
        int owner = -1, definition = -1, star = 1, lifetime = 0;
        Cell anchor, toward;
        Id action = 0;
    };
    // Summons wait here until the start of the next tick; fallen units leave their cell here.
    std::vector<Spawn> spawns_;
    std::vector<Cell> graves_;
    std::array<int, 2> summonBonusBp_{};
    Id encounterId_ = 0, nextSummon_ = 0;
    int summonsRefused_ = 0;
    void ServeSpawns();
    int LivingSummons(int side) const;
    bool Inert(const CombatUnit &unit) const;
    bool Afflicted(const CombatUnit &unit, UnitStatus status) const;
    bool Free(Cell cell, int except = -1) const;
    void CancelReservation(int unit);
    std::vector<int> Select(int source, const AbilityDef &ability) const;
    bool DashLanding(int source, const AbilityDef &ability, int &target, Cell &cell) const;
    bool Blink(int source, int target, Selector rule, Id action);
    bool FindPath(int source, int target, Cell &next, int &length) const;
    int ChooseEnemy(int source, Cell &next, int &pathLength) const;
    bool CommitAbility(int source);
    void RecordCommit(int source);
    void GainMana(int unit, Int amount, bool incoming, Id action);
    bool CommitMechanic(int source, const AbilityDef &ability);
    void ReleaseMechanic(int source, const AbilityDef &ability);
    void MoveUnit(int unit, Cell cell, AbilityMechanic mechanic, Id action, int source);
    bool ChargeLanding(int source, const AbilityDef &ability, int target, Cell &landing,
                       MechanicReason *reason = nullptr) const;
    void TraceMechanic(int source, MechanicPhase phase, MechanicReason reason,
                       const Packet *packet = nullptr, int recipients = 0, int fullHealth = 0,
                       Int requested = 0, Int resolved = 0);
    MechanicReason TetherReason(const Packet &packet) const;
    void TraceCompletion();
    std::vector<int> PacketTargets(const Packet &packet) const;
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
    Match(Catalog catalog, Id seed, int humans, bool networked = false);
    void Restart(Id seed, int humans, bool networked = false);
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
    // Units placed from the bench for this seat when the current round's preparation ended.
    const std::vector<Id> &AutoDeployed(int seat) const { return autoDeployed_[seat]; }
    // Guided first match: seat 0 against one fixed opponent in seat 1; the other seats sit out. The preparation
    // clock is held, nothing is saved, and after the fight the match waits for the next stage.
    void BeginGuidedStage(const GuidedStage &stage);
    bool Guided() const { return guided_; }
    bool GuidedStepDone(const GuidedStep &step, const GuidedView &view) const;

    std::string SavePreparation() const;
    bool RestorePreparation(const std::string &saved, std::string &error);

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
    int originalHumans_ = 0;
    bool networked_ = false;
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
    std::array<std::vector<Id>, 8> autoDeployed_;
    bool guided_ = false;
    void AutoDeploy(SeatState &seat);
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
