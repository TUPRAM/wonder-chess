#include "WCDefinitionRegistry.h"

#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include <cmath>
#include <set>
#include <stdexcept>

namespace
{
struct FDataError { FString Message; };
void Require(bool Condition, const FString& Message)
{
    if (!Condition) throw FDataError{Message};
}
std::string Utf8(const FString& Value) { return std::string(TCHAR_TO_UTF8(*Value)); }

struct FObject
{
    TSharedPtr<FJsonObject> Value;
    FString Path;

    FObject(TSharedPtr<FJsonObject> InValue, FString InPath) : Value(MoveTemp(InValue)), Path(MoveTemp(InPath))
    {
        Require(Value.IsValid(), Path + TEXT(": expected object"));
    }
    TSharedPtr<FJsonValue> Field(const FString& Key) const
    {
        const auto* Found = Value->Values.Find(Key);
        Require(Found && Found->IsValid(), Path + TEXT(".") + Key + TEXT(": missing field"));
        return *Found;
    }
    FString String(const FString& Key, bool Nullable = false) const
    {
        const auto Item = Field(Key);
        if (Nullable && Item->Type == EJson::Null) return FString();
        Require(Item->Type == EJson::String && !Item->AsString().IsEmpty(), Path + TEXT(".") + Key + TEXT(": expected nonempty string"));
        return Item->AsString();
    }
    double Number(const FString& Key, double Minimum = 0, double Maximum = 100000000) const
    {
        const auto Item = Field(Key);
        Require(Item->Type == EJson::Number, Path + TEXT(".") + Key + TEXT(": expected number"));
        const double NumberValue = Item->AsNumber();
        Require(std::isfinite(NumberValue) && NumberValue >= Minimum && NumberValue <= Maximum, Path + TEXT(".") + Key + TEXT(": number outside supported bounds"));
        return NumberValue;
    }
    int64 Integer(const FString& Key, int64 Minimum = 0, int64 Maximum = 100000000) const
    {
        const double NumberValue = Number(Key, static_cast<double>(Minimum), static_cast<double>(Maximum));
        Require(std::floor(NumberValue) == NumberValue, Path + TEXT(".") + Key + TEXT(": expected integer"));
        return static_cast<int64>(NumberValue);
    }
    bool Boolean(const FString& Key) const
    {
        const auto Item = Field(Key);
        Require(Item->Type == EJson::Boolean, Path + TEXT(".") + Key + TEXT(": expected boolean"));
        return Item->AsBool();
    }
    FObject Object(const FString& Key) const
    {
        const auto Item = Field(Key);
        Require(Item->Type == EJson::Object, Path + TEXT(".") + Key + TEXT(": expected object"));
        return FObject(Item->AsObject(), Path + TEXT(".") + Key);
    }
    const TArray<TSharedPtr<FJsonValue>>& Array(const FString& Key) const
    {
        const auto Item = Field(Key);
        Require(Item->Type == EJson::Array, Path + TEXT(".") + Key + TEXT(": expected array"));
        return Item->AsArray();
    }
    void Expect(const FString& Key, const FString& Expected) const
    {
        Require(String(Key) == Expected, Path + TEXT(".") + Key + TEXT(": unsupported value; expected ") + Expected);
    }
};

FObject AsObject(const TSharedPtr<FJsonValue>& Value, const FString& Path)
{
    Require(Value.IsValid() && Value->Type == EJson::Object, Path + TEXT(": expected object"));
    return FObject(Value->AsObject(), Path);
}

FObject ReadObject(const FString& Path)
{
    FString Source;
    Require(FFileHelper::LoadFileToString(Source, *Path), TEXT("Cannot read runtime data: ") + Path);
    TSharedPtr<FJsonObject> Object;
    const auto Reader = TJsonReaderFactory<>::Create(Source);
    Require(FJsonSerializer::Deserialize(Reader, Object) && Object.IsValid(), Path + TEXT(": invalid JSON object: ") + Reader->GetErrorMessage());
    return FObject(Object, Path);
}

TArray<TSharedPtr<FJsonValue>> ReadArray(const FString& Path)
{
    FString Source;
    Require(FFileHelper::LoadFileToString(Source, *Path), TEXT("Cannot read runtime rows: ") + Path);
    TArray<TSharedPtr<FJsonValue>> Rows;
    const auto Reader = TJsonReaderFactory<>::Create(Source);
    Require(FJsonSerializer::Deserialize(Reader, Rows), Path + TEXT(": invalid JSON row array"));
    return Rows;
}

void ExactKeys(const FObject& Object, std::initializer_list<const TCHAR*> Keys)
{
    Require(Object.Value->Values.Num() == static_cast<int32>(Keys.size()), Object.Path + TEXT(": unexpected or missing fields"));
    for (const TCHAR* Key : Keys) Object.Field(Key);
}

template<typename T>
T EnumValue(const FString& Value, std::initializer_list<std::pair<const TCHAR*, T>> Values, const FString& Path)
{
    for (const auto& Item : Values) if (Value == Item.first) return Item.second;
    throw FDataError{Path + TEXT(": unsupported enum ") + Value};
}

wc::DamageType DamageType(const FString& Value, const FString& Path)
{
    return EnumValue<wc::DamageType>(Value, {{TEXT("physical"),wc::DamageType::Physical},{TEXT("magic"),wc::DamageType::Magic},{TEXT("true"),wc::DamageType::True}}, Path);
}

void VerifyStage(const FString& Directory, const FObject& Manifest, const FObject& Digest)
{
    Manifest.Expect(TEXT("schema_version"), TEXT("3.1.0"));
    Digest.Expect(TEXT("schema_version"), TEXT("3.1.0"));
    Require(Manifest.String(TEXT("catalog_digest")) == Digest.String(TEXT("combined_sha256")), TEXT("Runtime manifest/catalog digest mismatch"));
    const FObject Files = Manifest.Object(TEXT("files"));
    ExactKeys(Files, {TEXT("asset_manifest.json"),TEXT("neutrals.json"),TEXT("bots.json"),TEXT("rules.alpha.json"),TEXT("traits.json"),TEXT("units.json"),TEXT("world.json"),TEXT("locales/en.json"),TEXT("locales/id.json"),TEXT("generated/catalog_digest.json"),TEXT("generated/unreal/DT_Units_Alpha.json"),TEXT("generated/unreal/DT_Abilities_Alpha.json")});
    for (const auto& Entry : Files.Value->Values)
    {
        const FObject Metadata = Files.Object(Entry.Key);
        ExactKeys(Metadata, {TEXT("source"), TEXT("bytes"), TEXT("sha256"), TEXT("sha1")});
        TArray<uint8> Bytes;
        Require(FFileHelper::LoadFileToArray(Bytes, *(Directory / Entry.Key)), TEXT("Missing staged file: ") + Entry.Key);
        Require(Bytes.Num() == Metadata.Integer(TEXT("bytes"), 1), TEXT("Staged size mismatch: ") + Entry.Key);
        const FString Sha1 = FSHA1::HashBuffer(Bytes.GetData(), Bytes.Num()).ToString().ToLower();
        Require(Sha1 == Metadata.String(TEXT("sha1")), TEXT("Staged content hash mismatch: ") + Entry.Key);
        Require(Metadata.String(TEXT("sha256")).Len() == 64, TEXT("Invalid provenance SHA-256: ") + Entry.Key);
    }
    const FObject SourceHashes = Digest.Object(TEXT("source_sha256"));
    Require(SourceHashes.Value->Values.Num() == 7, TEXT("Catalog must cover seven canonical source files"));
    for (const auto& Entry : SourceHashes.Value->Values)
    {
        Require(Entry.Key.StartsWith(TEXT("data/")), TEXT("Unexpected canonical digest source"));
        const FObject Metadata = Files.Object(Entry.Key.Mid(5));
        Require(Metadata.String(TEXT("source")) == Entry.Key && Metadata.String(TEXT("sha256")) == SourceHashes.String(Entry.Key), TEXT("Catalog/source provenance mismatch: ") + Entry.Key);
    }
}

void ParseRules(const FObject& Root, wc::Rules& R)
{
    ExactKeys(Root, {TEXT("schema_version"),TEXT("balance_version"),TEXT("profile_id"),TEXT("design_status"),TEXT("board"),TEXT("simulation"),TEXT("tournament"),TEXT("economy"),TEXT("alpha_unit_ids"),TEXT("active_trait_thresholds"),TEXT("future_profile"),TEXT("runtime_llm_calls"),TEXT("website_blocks_alpha"),TEXT("status_policies"),TEXT("network")});
    Root.Expect(TEXT("schema_version"), TEXT("3.1.0"));
    Root.Expect(TEXT("profile_id"), TEXT("alpha_24"));
    Require(!Root.Boolean(TEXT("runtime_llm_calls")) && !Root.Boolean(TEXT("website_blocks_alpha")), TEXT("Unsupported external runtime dependency"));
    const auto& Thresholds = Root.Array(TEXT("active_trait_thresholds"));
    Require(Thresholds.Num() == 2 && Thresholds[0]->Type == EJson::Number && Thresholds[0]->AsNumber() == 2 && Thresholds[1]->Type == EJson::Number && Thresholds[1]->AsNumber() == 4, TEXT("Expected highest eligible 2/4 trait tiers"));
    const FObject Board = Root.Object(TEXT("board"));
    ExactKeys(Board, {TEXT("columns"),TEXT("rows"),TEXT("deployment_rows_per_side"),TEXT("tile_size_cm"),TEXT("neighbor_mode"),TEXT("distance_metric"),TEXT("diagonal_corner_policy")});
    Board.Expect(TEXT("neighbor_mode"), TEXT("eight"));
    Board.Expect(TEXT("distance_metric"), TEXT("chebyshev"));
    Board.Expect(TEXT("diagonal_corner_policy"), TEXT("block_if_either_orthogonal_blocked"));
    R.columns = Board.Integer(TEXT("columns"), 1, 8);
    R.rows = Board.Integer(TEXT("rows"), 1, 8);
    R.deploymentRows = Board.Integer(TEXT("deployment_rows_per_side"), 1, 4);
    R.tileSizeCm = Board.Integer(TEXT("tile_size_cm"), 1, 10000);
    const FObject Sim = Root.Object(TEXT("simulation"));
    ExactKeys(Sim, {TEXT("tick_ms"),TEXT("health_scale"),TEXT("basis_scale"),TEXT("rate_scale"),TEXT("rounding"),TEXT("star_multiplier_bp"),TEXT("min_attack_rate_milli"),TEXT("max_attack_rate_milli"),TEXT("max_health_cp"),TEXT("max_armor"),TEXT("max_raw_damage_cp"),TEXT("simultaneous_semantics")});
    Sim.Expect(TEXT("rounding"), TEXT("round_half_up_nonnegative"));
    Sim.Expect(TEXT("simultaneous_semantics"), TEXT("released_due_packets_survive_source_defeat_target_defeat_immediate"));
    Require(Sim.Integer(TEXT("health_scale")) == 100 && Sim.Integer(TEXT("basis_scale")) == 10000 && Sim.Integer(TEXT("rate_scale")) == 1000, TEXT("Unsupported numeric scales"));
    R.tickMs = Sim.Integer(TEXT("tick_ms"), 1, 1000);
    R.minAttackRate = Sim.Integer(TEXT("min_attack_rate_milli"), 1);
    R.maxAttackRate = Sim.Integer(TEXT("max_attack_rate_milli"), 1);
    R.maxHealth = Sim.Integer(TEXT("max_health_cp"), 1);
    R.maxArmor = Sim.Integer(TEXT("max_armor"));
    R.maxRawDamage = Sim.Integer(TEXT("max_raw_damage_cp"));
    const auto& Stars = Sim.Array(TEXT("star_multiplier_bp"));
    Require(Stars.Num() == 3, TEXT("Exactly three star multipliers required"));
    for (int32 Index = 0; Index < Stars.Num(); ++Index)
    {
        Require(Stars[Index]->Type == EJson::Number && Stars[Index]->AsNumber() >= 1 && Stars[Index]->AsNumber() <= 1000000 && std::floor(Stars[Index]->AsNumber()) == Stars[Index]->AsNumber(), TEXT("Invalid star multiplier"));
        R.starMultiplierBp[Index] = static_cast<int>(Stars[Index]->AsNumber());
    }
    const FObject Tournament = Root.Object(TEXT("tournament"));
    ExactKeys(Tournament, {TEXT("seats"),TEXT("default_humans"),TEXT("starting_health"),TEXT("max_rounds"),TEXT("first_preparation_ms"),TEXT("preparation_ms"),TEXT("combat_timeout_ms"),TEXT("settlement_ms"),TEXT("draw_damage"),TEXT("loss_base_by_stage"),TEXT("ghost_wins_count_for_cap"),TEXT("timeout_score"),TEXT("rank_ties"),TEXT("neutral_opening_rounds"),TEXT("neutral_every_rounds"),TEXT("neutral_opening_failure_damage"),TEXT("neutral_failure_damage")});
    Tournament.Expect(TEXT("timeout_score"), TEXT("sum_survivor_health_fractions"));
    Tournament.Expect(TEXT("rank_ties"), TEXT("competition_ranking_same_placement"));
    Require(Tournament.Boolean(TEXT("ghost_wins_count_for_cap")), TEXT("Unsupported ghost win policy"));
    Tournament.Integer(TEXT("default_humans"), 0, 2);
    R.seatCount = Tournament.Integer(TEXT("seats"), 8, 8);
    R.startingHealth = Tournament.Integer(TEXT("starting_health"), 1, 10000);
    R.maxRounds = Tournament.Integer(TEXT("max_rounds"), 1, 1000);
    R.firstPreparationMs = Tournament.Integer(TEXT("first_preparation_ms"), 1);
    R.preparationMs = Tournament.Integer(TEXT("preparation_ms"), 1);
    R.combatTimeoutMs = Tournament.Integer(TEXT("combat_timeout_ms"), 1);
    R.settlementMs = Tournament.Integer(TEXT("settlement_ms"), 1);
    R.drawDamage = Tournament.Integer(TEXT("draw_damage"), 0, 10000);
    R.neutralOpeningRounds = Tournament.Integer(TEXT("neutral_opening_rounds"), 0, 40);
    R.neutralEvery = Tournament.Integer(TEXT("neutral_every_rounds"), 1, 40);
    R.neutralOpeningDamage = Tournament.Integer(TEXT("neutral_opening_failure_damage"), 0, 10000);
    R.neutralLossDamage = Tournament.Integer(TEXT("neutral_failure_damage"), 0, 10000);
    for (const auto& Item : Tournament.Array(TEXT("loss_base_by_stage")))
    {
        const FObject Stage = AsObject(Item, TEXT("loss_base_by_stage"));
        ExactKeys(Stage, {TEXT("start"),TEXT("end"),TEXT("damage")});
        R.lossStages.push_back({static_cast<int>(Stage.Integer(TEXT("start"), 1)),static_cast<int>(Stage.Integer(TEXT("end"), 1)),static_cast<int>(Stage.Integer(TEXT("damage")))});
    }
    const FObject Economy = Root.Object(TEXT("economy"));
    ExactKeys(Economy, {TEXT("starting_gold"),TEXT("bench_capacity"),TEXT("shop_slots"),TEXT("reroll_cost"),TEXT("base_income"),TEXT("win_income"),TEXT("neutral_win_income"),TEXT("interest_divisor"),TEXT("interest_cap"),TEXT("interest_snapshot"),TEXT("pool"),TEXT("starting_level"),TEXT("maximum_level"),TEXT("buy_xp_gold"),TEXT("buy_xp_amount"),TEXT("passive_xp"),TEXT("xp_to_next"),TEXT("sell_formula"),TEXT("shop_weights_by_level")});
    Economy.Expect(TEXT("interest_snapshot"), TEXT("preparation_lock"));
    Economy.Expect(TEXT("pool"), TEXT("independent_with_replacement"));
    Economy.Expect(TEXT("sell_formula"), TEXT("cost_times_3_power_star_minus_1"));
    R.startingGold = Economy.Integer(TEXT("starting_gold"));
    R.benchCapacity = Economy.Integer(TEXT("bench_capacity"), 1, 8);
    R.shopSlots = Economy.Integer(TEXT("shop_slots"), 1, 5);
    R.rerollCost = Economy.Integer(TEXT("reroll_cost"), 1);
    R.baseIncome = Economy.Integer(TEXT("base_income"));
    R.winIncome = Economy.Integer(TEXT("win_income"));
    R.neutralWinIncome = Economy.Integer(TEXT("neutral_win_income"));
    R.interestDivisor = Economy.Integer(TEXT("interest_divisor"), 1);
    R.interestCap = Economy.Integer(TEXT("interest_cap"));
    R.startingLevel = Economy.Integer(TEXT("starting_level"), 1, 6);
    R.maximumLevel = Economy.Integer(TEXT("maximum_level"), R.startingLevel, 6);
    R.buyXpGold = Economy.Integer(TEXT("buy_xp_gold"), 1);
    R.buyXpAmount = Economy.Integer(TEXT("buy_xp_amount"), 1);
    R.passiveXp = Economy.Integer(TEXT("passive_xp"));
    const FObject Xp = Economy.Object(TEXT("xp_to_next"));
    const FObject Weights = Economy.Object(TEXT("shop_weights_by_level"));
    Require(Xp.Value->Values.Num() == R.maximumLevel - R.startingLevel && Weights.Value->Values.Num() == R.maximumLevel - R.startingLevel + 1, TEXT("Missing or unexpected economy levels"));
    for (int Level = R.startingLevel; Level <= R.maximumLevel; ++Level)
    {
        const FString Key = FString::FromInt(Level);
        if (Level < R.maximumLevel) R.xpToNext[Level] = Xp.Integer(Key, 1);
        const FObject LevelWeights = Weights.Object(Key);
        ExactKeys(LevelWeights, {TEXT("1"),TEXT("2"),TEXT("3")});
        R.shopWeights[Level] = {static_cast<int>(LevelWeights.Integer(TEXT("1"))),static_cast<int>(LevelWeights.Integer(TEXT("2"))),static_cast<int>(LevelWeights.Integer(TEXT("3")))};
    }
    const FObject Status = Root.Object(TEXT("status_policies"));
    ExactKeys(Status, {TEXT("shield"),TEXT("stun"),TEXT("buff"),TEXT("debuff"),TEXT("support_power")});
    Status.Expect(TEXT("shield"), TEXT("stronger_replaces_equal_refreshes_weaker_ignored"));
    Status.Expect(TEXT("stun"), TEXT("max_expiry_no_duration_sum"));
    Status.Expect(TEXT("buff"), TEXT("same_key_strongest_refresh_distinct_keys_add"));
    Status.Expect(TEXT("debuff"), TEXT("same_key_strongest_refresh_attack_rate_only"));
    Status.Expect(TEXT("support_power"), TEXT("heal_shield_and_positive_active_attack_rate_only"));
    const FObject Network = Root.Object(TEXT("network"));
    ExactKeys(Network, {TEXT("protocol_version"),TEXT("release_test_modes"),TEXT("future_mode"),TEXT("disconnect_policy"),TEXT("host_disconnect"),TEXT("public_snapshot_cadence_ms"),TEXT("bot_public_observation_ms"),TEXT("bot_final_reposition_cutoff_ms")});
    Require(Network.Integer(TEXT("protocol_version")) == 4, TEXT("Unsupported network protocol version"));
    const auto& Modes = Network.Array(TEXT("release_test_modes"));
    Require(Modes.Num() == 3 && Modes[0]->Type == EJson::String && Modes[1]->Type == EJson::String && Modes[2]->Type == EJson::String && Modes[0]->AsString() == TEXT("1H7B") && Modes[1]->AsString() == TEXT("0H8B") && Modes[2]->AsString() == TEXT("2H6B"), TEXT("Release modes must retain 1H7B, 0H8B and 2H6B"));
    Network.Expect(TEXT("disconnect_policy"), TEXT("bot_takeover_until_match_end_no_rejoin_alpha"));
    Network.Expect(TEXT("host_disconnect"), TEXT("abort_explicitly_no_host_migration"));
    Network.Integer(TEXT("public_snapshot_cadence_ms"), 1);
    R.botObservationMs = Network.Integer(TEXT("bot_public_observation_ms"), 1);
    R.botRepositionCutoffMs = Network.Integer(TEXT("bot_final_reposition_cutoff_ms"));
}

wc::UnitDef ParseUnit(const FObject& Unit, const wc::Rules& Rules, bool Neutral = false)
{
    wc::UnitDef U;
    U.id = Utf8(Unit.String(TEXT("id")));
    U.displayName = Utf8(Unit.String(TEXT("display_name")));
    U.name = Neutral ? U.displayName : Utf8(Unit.String(TEXT("name")));
    if (!Neutral)
    {
        U.race = Utf8(Unit.String(TEXT("race")));
        U.unitClass = Utf8(Unit.String(TEXT("unit_class")));
        U.cost = Unit.Integer(TEXT("cost"), 1, 3);
        Unit.Expect(TEXT("production_phase"), TEXT("alpha"));
        for (const auto& Role : Unit.Array(TEXT("role_tags")))
        {
            Require(Role->Type == EJson::String, TEXT("Role tag must be a string"));
            U.roleTags.push_back(Utf8(Role->AsString()));
        }
    }
    else Require(Unit.Integer(TEXT("footprint_cells")) == 1, TEXT("Neutral footprint must be one cell"));
    const FObject Stats = Unit.Object(TEXT("stats"));
    ExactKeys(Stats, {TEXT("health_cp"),TEXT("attack_damage_cp"),TEXT("attack_rate_milli"),TEXT("attack_range_tiles"),TEXT("physical_armor"),TEXT("magic_resistance"),TEXT("movement_rate_milli"),TEXT("attack_delivery"),TEXT("attack_damage_type"),TEXT("attack_windup_ms"),TEXT("projectile_travel_ms")});
    U.health = Stats.Integer(TEXT("health_cp"), 1, Rules.maxHealth);
    U.attackDamage = Stats.Integer(TEXT("attack_damage_cp"), 0, Rules.maxRawDamage);
    U.attackRate = Stats.Integer(TEXT("attack_rate_milli"), Rules.minAttackRate, Rules.maxAttackRate);
    U.range = Stats.Integer(TEXT("attack_range_tiles"), 1, Rules.columns);
    U.armor = Stats.Integer(TEXT("physical_armor"), 0, Rules.maxArmor);
    U.resistance = Stats.Integer(TEXT("magic_resistance"), 0, Rules.maxArmor);
    U.movementRate = Stats.Integer(TEXT("movement_rate_milli"), 1, 100000);
    U.attackWindupMs = Stats.Integer(TEXT("attack_windup_ms"), 1);
    U.projectileTravelMs = Stats.Integer(TEXT("projectile_travel_ms"));
    U.damageType = DamageType(Stats.String(TEXT("attack_damage_type")), Stats.Path);
    const FString AttackDelivery = Stats.String(TEXT("attack_delivery"));
    Require(AttackDelivery == TEXT("melee") || AttackDelivery == TEXT("ranged"), Stats.Path + TEXT(": unsupported attack delivery"));
    Require(AttackDelivery != TEXT("melee") || U.projectileTravelMs == 0, Stats.Path + TEXT(": melee cannot travel as projectile"));
    if (Neutral && Unit.Field(TEXT("ability"))->Type == EJson::Null)
    {
        U.ability.enabled = false;
        return U;
    }
    const FObject Ability = Unit.Object(TEXT("ability"));
    ExactKeys(Ability, {TEXT("id"),TEXT("name"),TEXT("tooltip_en"),TEXT("tooltip_id"),TEXT("effects"),TEXT("target_rule"),TEXT("first_cast_ms"),TEXT("cooldown_ms"),TEXT("cast_ms"),TEXT("radius_tiles"),TEXT("range_tiles"),TEXT("allow_self"),TEXT("recovery_ms"),TEXT("max_targets"),TEXT("max_dash_tiles"),TEXT("travel_ms"),TEXT("interrupt_policy"),TEXT("no_target_policy"),TEXT("effect_snapshot"),TEXT("delivery")});
    auto& A = U.ability;
    A.id = Utf8(Ability.String(TEXT("id")));
    A.name = Utf8(Ability.String(TEXT("name")));
    Ability.String(TEXT("tooltip_en"));
    Ability.String(TEXT("tooltip_id"));
    A.selector = EnumValue<wc::Selector>(Ability.String(TEXT("target_rule")), {{TEXT("self"),wc::Selector::Self},{TEXT("current_enemy"),wc::Selector::CurrentEnemy},{TEXT("adjacent_enemies"),wc::Selector::AdjacentEnemies},{TEXT("adjacent_allies"),wc::Selector::AdjacentAllies},{TEXT("lowest_health_ally"),wc::Selector::LowestHealthAlly},{TEXT("highest_attack_rate_enemy"),wc::Selector::HighestAttackRateEnemy},{TEXT("current_enemy_area"),wc::Selector::CurrentEnemyArea},{TEXT("retreat_from_current_enemy"),wc::Selector::RetreatFromCurrentEnemy},{TEXT("current_enemy_adjacent"),wc::Selector::CurrentEnemyAdjacent},{TEXT("farthest_enemy_adjacent"),wc::Selector::FarthestEnemyAdjacent}}, Ability.Path);
    A.firstCastMs = Ability.Integer(TEXT("first_cast_ms"));
    A.cooldownMs = Ability.Integer(TEXT("cooldown_ms"), Rules.tickMs);
    A.castMs = Ability.Integer(TEXT("cast_ms"), Rules.tickMs);
    A.recoveryMs = Ability.Integer(TEXT("recovery_ms"));
    A.travelMs = Ability.Integer(TEXT("travel_ms"));
    A.radius = Ability.Integer(TEXT("radius_tiles"), 0, Rules.columns);
    A.range = Ability.Integer(TEXT("range_tiles"), 0, Rules.columns);
    A.maxTargets = Ability.Integer(TEXT("max_targets"), 0, 48);
    A.maxDash = Ability.Integer(TEXT("max_dash_tiles"), 0, Rules.columns);
    A.allowSelf = Ability.Boolean(TEXT("allow_self"));
    Ability.Expect(TEXT("interrupt_policy"), TEXT("consume_committed_cooldown_cancel_unreleased_effect"));
    Ability.Expect(TEXT("no_target_policy"), TEXT("remain_ready_continue_basics"));
    Ability.Expect(TEXT("effect_snapshot"), TEXT("capture_at_release_except_reserved_dash_destination"));
    const FString Delivery = Ability.String(TEXT("delivery"));
    Require(Delivery == TEXT("instant") || Delivery == TEXT("projectile"), Ability.Path + TEXT(": unsupported ability delivery"));
    Require(Delivery != TEXT("instant") || A.travelMs == 0, Ability.Path + TEXT(": instant delivery cannot have projectile travel"));
    const auto& Effects = Ability.Array(TEXT("effects"));
    Require(Effects.Num() >= 1 && Effects.Num() <= 2, Ability.Path + TEXT(": expected one or two ordered effects"));
    for (const auto& Value : Effects)
    {
        const FObject Source = AsObject(Value, Ability.Path + TEXT(".effects"));
        ExactKeys(Source, {TEXT("effect"),TEXT("damage_type"),TEXT("magnitude_unit"),TEXT("magnitude_by_star"),TEXT("stat"),TEXT("duration_ms")});
        wc::AbilityEffect Effect;
        Effect.effect = EnumValue<wc::Effect>(Source.String(TEXT("effect")), {{TEXT("damage"),wc::Effect::Damage},{TEXT("heal"),wc::Effect::Heal},{TEXT("shield"),wc::Effect::Shield},{TEXT("stun"),wc::Effect::Stun},{TEXT("dash"),wc::Effect::Dash},{TEXT("stat_modifier"),wc::Effect::StatModifier}}, Source.Path);
        const FString Type = Source.String(TEXT("damage_type"), true);
        Require((Effect.effect == wc::Effect::Damage) == !Type.IsEmpty(), Source.Path + TEXT(": damage type/effect mismatch"));
        if (!Type.IsEmpty()) Effect.damageType = DamageType(Type, Source.Path);
        Effect.durationMs = Source.Integer(TEXT("duration_ms"));
        const FString Stat = Source.String(TEXT("stat"), true);
        Require(Stat == (Effect.effect == wc::Effect::StatModifier ? TEXT("attack_rate") : TEXT("")), Source.Path + TEXT(": unsupported stat modifier"));
        const FString Expected = Effect.effect == wc::Effect::StatModifier ? TEXT("basis_points") : (Effect.effect == wc::Effect::Stun || Effect.effect == wc::Effect::Dash ? TEXT("") : TEXT("centipoints"));
        Require(Source.String(TEXT("magnitude_unit"), true) == Expected, Source.Path + TEXT(": magnitude unit/effect mismatch"));
        const auto& Magnitudes = Source.Array(TEXT("magnitude_by_star"));
        Require(Magnitudes.Num() == 3, Source.Path + TEXT(": exactly three authored magnitudes required"));
        for (int Index = 0; Index < 3; ++Index)
        {
            Require(Magnitudes[Index]->Type == EJson::Number, Source.Path + TEXT(": numeric magnitude required"));
            const double Magnitude = Magnitudes[Index]->AsNumber();
            Require(std::isfinite(Magnitude) && std::floor(Magnitude) == Magnitude && Magnitude >= -10000 && Magnitude <= Rules.maxRawDamage, Source.Path + TEXT(": invalid magnitude"));
            Require(Effect.effect == wc::Effect::StatModifier || Magnitude >= 0, Source.Path + TEXT(": negative non-modifier"));
            Require((Effect.effect != wc::Effect::Dash && Effect.effect != wc::Effect::Stun) || Magnitude == 0, Source.Path + TEXT(": hidden dash/stun magnitude"));
            Effect.magnitude[Index] = static_cast<wc::Int>(Magnitude);
        }
        A.effects.push_back(Effect);
    }
    A.effect = A.effects.front().effect;
    A.damageType = A.effects.front().damageType;
    A.durationMs = A.effects.front().durationMs;
    A.magnitude = A.effects.front().magnitude;
    return U;
}

void SameString(const FObject& Row, const FString& RowKey, const FObject& Source, const FString& SourceKey, bool Nullable = false)
{
    FString Expected = Source.String(SourceKey, Nullable);
    if (Nullable && Expected.IsEmpty()) Expected = TEXT("none");
    Require(Row.String(RowKey) == Expected, Row.Path + TEXT(".") + RowKey + TEXT(": generated row differs from canonical source"));
}
void SameNumber(const FObject& Row, const FString& RowKey, const FObject& Source, const FString& SourceKey)
{
    Require(Row.Integer(RowKey, -10000) == Source.Integer(SourceKey, -10000), Row.Path + TEXT(".") + RowKey + TEXT(": generated row differs from canonical source"));
}

void VerifyRows(const FString& Directory, const TArray<FObject>& Units)
{
    const auto UnitRows = ReadArray(Directory / TEXT("generated/unreal/DT_Units_Alpha.json"));
    const auto AbilityRows = ReadArray(Directory / TEXT("generated/unreal/DT_Abilities_Alpha.json"));
    Require(UnitRows.Num() == Units.Num() && AbilityRows.Num() == Units.Num(), TEXT("Generated alpha row count mismatch"));
    TMap<FString, FObject> ById;
    for (const FObject& Unit : Units) ById.Add(Unit.String(TEXT("id")), Unit);
    TSet<FString> SeenUnits, SeenAbilities;
    for (int32 Index = 0; Index < UnitRows.Num(); ++Index)
    {
        const FObject Row = AsObject(UnitRows[Index], TEXT("DT_Units_Alpha"));
        const FString Id = Row.String(TEXT("UnitId"));
        Require(ById.Contains(Id) && !SeenUnits.Contains(Id), TEXT("Unknown/duplicate alpha unit row: ") + Id);
        SeenUnits.Add(Id);
        const FObject& Unit = ById.FindChecked(Id);
        const FObject Stats = Unit.Object(TEXT("stats"));
        ExactKeys(Row, {TEXT("Name"),TEXT("UnitId"),TEXT("DisplayName"),TEXT("LoreName"),TEXT("RoleTags"),TEXT("RaceId"),TEXT("ClassId"),TEXT("AbilityId"),TEXT("Cost"),TEXT("HealthCp"),TEXT("AttackDamageCp"),TEXT("AttackRateMilli"),TEXT("AttackRangeTiles"),TEXT("PhysicalArmor"),TEXT("MagicResistance"),TEXT("MovementRateMilli"),TEXT("AttackDelivery"),TEXT("AttackDamageType"),TEXT("AttackWindupMs"),TEXT("ProjectileTravelMs"),TEXT("ProductionPhase")});
        for (const auto& Key : {std::pair{TEXT("Name"),TEXT("id")}, {TEXT("UnitId"),TEXT("id")}, {TEXT("DisplayName"),TEXT("display_name")}, {TEXT("LoreName"),TEXT("name")}, {TEXT("RaceId"),TEXT("race")}, {TEXT("ClassId"),TEXT("unit_class")}, {TEXT("ProductionPhase"),TEXT("production_phase")}}) SameString(Row, Key.first, Unit, Key.second);
        const auto& RoleRows = Row.Array(TEXT("RoleTags"));
        const auto& RoleSource = Unit.Array(TEXT("role_tags"));
        Require(RoleRows.Num() == RoleSource.Num(), TEXT("Generated role count mismatch"));
        for (int32 Role = 0; Role < RoleRows.Num(); ++Role)
            Require(RoleRows[Role]->Type == EJson::String && RoleRows[Role]->AsString() == RoleSource[Role]->AsString(), TEXT("Generated role differs from source"));
        SameString(Row,TEXT("AbilityId"),Unit.Object(TEXT("ability")),TEXT("id"));
        SameNumber(Row,TEXT("Cost"),Unit,TEXT("cost"));
        for (const auto& Key : {std::pair{TEXT("HealthCp"),TEXT("health_cp")}, {TEXT("AttackDamageCp"),TEXT("attack_damage_cp")}, {TEXT("AttackRateMilli"),TEXT("attack_rate_milli")}, {TEXT("AttackRangeTiles"),TEXT("attack_range_tiles")}, {TEXT("PhysicalArmor"),TEXT("physical_armor")}, {TEXT("MagicResistance"),TEXT("magic_resistance")}, {TEXT("MovementRateMilli"),TEXT("movement_rate_milli")}, {TEXT("AttackWindupMs"),TEXT("attack_windup_ms")}, {TEXT("ProjectileTravelMs"),TEXT("projectile_travel_ms")}}) SameNumber(Row,Key.first,Stats,Key.second);
        SameString(Row,TEXT("AttackDelivery"),Stats,TEXT("attack_delivery"));
        SameString(Row,TEXT("AttackDamageType"),Stats,TEXT("attack_damage_type"));
    }
    for (const auto& Value : AbilityRows)
    {
        const FObject Row = AsObject(Value, TEXT("DT_Abilities_Alpha"));
        const FString Id = Row.String(TEXT("AbilityId"));
        const FObject* Unit = Units.FindByPredicate([&Id](const FObject& Candidate){return Candidate.Object(TEXT("ability")).String(TEXT("id")) == Id;});
        Require(Unit && !SeenAbilities.Contains(Id), TEXT("Unknown/duplicate alpha ability row: ") + Id);
        SeenAbilities.Add(Id);
        const FObject Ability = Unit->Object(TEXT("ability"));
        ExactKeys(Row, {TEXT("Name"),TEXT("AbilityId"),TEXT("DisplayName"),TEXT("Effects"),TEXT("TargetRule"),TEXT("FirstCastMs"),TEXT("CooldownMs"),TEXT("CastMs"),TEXT("RecoveryMs"),TEXT("RangeTiles"),TEXT("RadiusTiles"),TEXT("MaxTargets"),TEXT("MaxDashTiles"),TEXT("TravelMs"),TEXT("AllowSelf"),TEXT("TooltipEn"),TEXT("TooltipId")});
        for (const auto& Key : {std::pair{TEXT("Name"),TEXT("id")},{TEXT("AbilityId"),TEXT("id")},{TEXT("DisplayName"),TEXT("name")},{TEXT("TargetRule"),TEXT("target_rule")},{TEXT("TooltipEn"),TEXT("tooltip_en")},{TEXT("TooltipId"),TEXT("tooltip_id")}}) SameString(Row,Key.first,Ability,Key.second);
        for (const auto& Key : {std::pair{TEXT("FirstCastMs"),TEXT("first_cast_ms")},{TEXT("CooldownMs"),TEXT("cooldown_ms")},{TEXT("CastMs"),TEXT("cast_ms")},{TEXT("RecoveryMs"),TEXT("recovery_ms")},{TEXT("RangeTiles"),TEXT("range_tiles")},{TEXT("RadiusTiles"),TEXT("radius_tiles")},{TEXT("MaxTargets"),TEXT("max_targets")},{TEXT("MaxDashTiles"),TEXT("max_dash_tiles")},{TEXT("TravelMs"),TEXT("travel_ms")}}) SameNumber(Row,Key.first,Ability,Key.second);
        Require(Row.Boolean(TEXT("AllowSelf")) == Ability.Boolean(TEXT("allow_self")), TEXT("Generated allow_self mismatch"));
        const auto& Effects = Ability.Array(TEXT("effects"));
        const auto& Rows = Row.Array(TEXT("Effects"));
        Require(Effects.Num() == Rows.Num(), TEXT("Generated effect count mismatch"));
        for (int32 Index = 0; Index < Effects.Num(); ++Index)
        {
            const FObject Source = AsObject(Effects[Index], TEXT("source_effect"));
            const FObject Effect = AsObject(Rows[Index], TEXT("generated_effect"));
            ExactKeys(Effect, {TEXT("EffectId"),TEXT("DamageType"),TEXT("MagnitudeUnit"),TEXT("Magnitude1"),TEXT("Magnitude2"),TEXT("Magnitude3"),TEXT("DurationMs"),TEXT("StatId")});
            SameString(Effect,TEXT("EffectId"),Source,TEXT("effect"));
            for (const auto& Key : {std::pair{TEXT("DamageType"),TEXT("damage_type")},{TEXT("MagnitudeUnit"),TEXT("magnitude_unit")},{TEXT("StatId"),TEXT("stat")}}) SameString(Effect,Key.first,Source,Key.second,true);
            SameNumber(Effect,TEXT("DurationMs"),Source,TEXT("duration_ms"));
            for (int32 Star = 0; Star < 3; ++Star) Require(Effect.Integer(TEXT("Magnitude") + FString::FromInt(Star+1), -10000) == Source.Array(TEXT("magnitude_by_star"))[Star]->AsNumber(), TEXT("Generated effect magnitude mismatch"));
        }
    }
}
}

FString FWCDefinitionText::Localized(const FString& Key, const FString& Language) const
{
    const auto* Locale = Locales.Find(Language);
    if (!Locale) Locale = Locales.Find(TEXT("en"));
    if (Locale) if (const FString* Result = Locale->Find(Key)) return *Result;
    return Key;
}

FString FWCDefinitionText::AbilityTooltip(const FString& UnitId, const FString& Language) const
{
    const auto* Unit = Units.Find(UnitId);
    if (!Unit) Unit = NeutralUnits.Find(UnitId);
    if (!Unit) return FString();
    const TSharedPtr<FJsonObject>* AbilityValue = nullptr;
    if (!(*Unit)->TryGetObjectField(TEXT("ability"), AbilityValue)) return Language == TEXT("id") ? TEXT("Serangan biasa saja.") : TEXT("Basic attacks only.");
    const auto Ability = *AbilityValue;
    return Ability->GetStringField(Language == TEXT("id") ? TEXT("tooltip_id") : TEXT("tooltip_en"));
}

bool wc::LoadCatalog(Catalog& OutCatalog, FString& Error, FWCDefinitionText* Text)
{
    Error.Reset();
    try
    {
        const FString Directory = FPaths::ProjectContentDir() / TEXT("WonderChess/SourceData");
        const FObject Manifest = ReadObject(Directory / TEXT("runtime_stage_manifest.json"));
        const FObject Digest = ReadObject(Directory / TEXT("generated/catalog_digest.json"));
        VerifyStage(Directory, Manifest, Digest);
        const FObject RulesSource = ReadObject(Directory / TEXT("rules.alpha.json"));
        const FObject UnitsSource = ReadObject(Directory / TEXT("units.json"));
        const FObject TraitsSource = ReadObject(Directory / TEXT("traits.json"));
        const FObject BotsSource = ReadObject(Directory / TEXT("bots.json"));
        Catalog Next;
        FWCDefinitionText NextText;
        NextText.Rules = RulesSource.Value;
        NextText.Traits = TraitsSource.Value;
        NextText.Bots = BotsSource.Value;
        Next.schemaVersion = Utf8(RulesSource.String(TEXT("schema_version")));
        Next.balanceVersion = Utf8(RulesSource.String(TEXT("balance_version")));
        Next.contentDigest = Utf8(Digest.String(TEXT("combined_sha256")));
        UnitsSource.Expect(TEXT("schema_version"), UTF8_TO_TCHAR(Next.schemaVersion.c_str()));
        UnitsSource.Expect(TEXT("balance_version"), UTF8_TO_TCHAR(Next.balanceVersion.c_str()));
        Manifest.Expect(TEXT("balance_version"), UTF8_TO_TCHAR(Next.balanceVersion.c_str()));
        TraitsSource.Expect(TEXT("schema_version"), UTF8_TO_TCHAR(Next.schemaVersion.c_str()));
        BotsSource.Expect(TEXT("schema_version"), UTF8_TO_TCHAR(Next.schemaVersion.c_str()));
        ParseRules(RulesSource, Next.rules);
        const auto& AllUnits = UnitsSource.Array(TEXT("units"));
        const auto& AlphaIds = RulesSource.Array(TEXT("alpha_unit_ids"));
        const auto& ManifestIds = Manifest.Array(TEXT("alpha_unit_ids"));
        Require(AllUnits.Num() == 24 && AlphaIds.Num() == 24 && ManifestIds.Num() == 24, TEXT("Expected exact 24-hero playable catalog"));
        TMap<FString, FObject> UnitsById;
        TSet<FString> AbilityIds, SelectedIds;
        for (const auto& Value : AllUnits)
        {
            const FObject Unit = AsObject(Value, TEXT("units"));
            const FString Id = Unit.String(TEXT("id"));
            const FString AbilityId = Unit.Object(TEXT("ability")).String(TEXT("id"));
            Require(!UnitsById.Contains(Id) && !AbilityIds.Contains(AbilityId), TEXT("Duplicate unit or ability ID"));
            UnitsById.Add(Id, Unit);
            AbilityIds.Add(AbilityId);
        }
        TArray<FObject> Selected;
        for (int32 Index = 0; Index < AlphaIds.Num(); ++Index)
        {
            Require(AlphaIds[Index]->Type == EJson::String && ManifestIds[Index]->Type == EJson::String, TEXT("Expected alpha ID string"));
            const FString Id = AlphaIds[Index]->AsString();
            Require(ManifestIds[Index]->AsString() == Id && UnitsById.Contains(Id) && !SelectedIds.Contains(Id), TEXT("Invalid, missing or reordered alpha ID: ") + Id);
            SelectedIds.Add(Id);
            const FObject& Unit = UnitsById.FindChecked(Id);
            Selected.Add(Unit);
            Next.units.push_back(ParseUnit(Unit, Next.rules));
            NextText.Units.Add(Id, Unit.Value);
        }
        for (const auto& Entry : UnitsById) Require((Entry.Value.String(TEXT("production_phase")) == TEXT("alpha")) == SelectedIds.Contains(Entry.Key), TEXT("Production phase disagrees with alpha list"));
        VerifyRows(Directory, Selected);
        const FObject NeutralsSource = ReadObject(Directory / TEXT("neutrals.json"));
        NeutralsSource.Expect(TEXT("schema_version"), UTF8_TO_TCHAR(Next.schemaVersion.c_str()));
        NeutralsSource.Expect(TEXT("balance_version"), UTF8_TO_TCHAR(Next.balanceVersion.c_str()));
        NextText.Neutrals = NeutralsSource.Value;
        TMap<FString,int32> NeutralIndices;
        for (const auto& Value : NeutralsSource.Array(TEXT("creatures")))
        {
            const FObject Creature = AsObject(Value, TEXT("neutral_creature"));
            const FString Id = Creature.String(TEXT("id"));
            Require(Id.StartsWith(TEXT("wc_n_")) && !NeutralIndices.Contains(Id) && !UnitsById.Contains(Id), TEXT("Invalid/duplicate neutral ID"));
            NeutralIndices.Add(Id, static_cast<int32>(Next.neutrals.size()));
            Next.neutrals.push_back(ParseUnit(Creature, Next.rules, true));
            NextText.NeutralUnits.Add(Id, Creature.Value);
        }
        Require(Next.neutrals.size() == 7, TEXT("Expected seven authored neutral archetypes"));
        TSet<FString> WaveIds;
        TSet<int32> WaveRounds;
        for (const auto& Value : NeutralsSource.Array(TEXT("waves")))
        {
            const FObject Source = AsObject(Value, TEXT("neutral_wave"));
            ExactKeys(Source, {TEXT("id"),TEXT("round"),TEXT("display_name"),TEXT("hp_scale_bp"),TEXT("damage_scale_bp"),TEXT("reward_policy"),TEXT("slots")});
            Source.Expect(TEXT("reward_policy"), TEXT("neutral_standard"));
            const FString Id = Source.String(TEXT("id"));
            const int32 Round = Source.Integer(TEXT("round"), 1, Next.rules.maxRounds);
            Require(!WaveIds.Contains(Id) && !WaveRounds.Contains(Round), TEXT("Duplicate wave ID or round"));
            WaveIds.Add(Id); WaveRounds.Add(Round);
            NeutralWave Wave;
            Wave.id = Utf8(Id); Wave.name = Utf8(Source.String(TEXT("display_name"))); Wave.round = Round;
            Wave.hpScaleBp = Source.Integer(TEXT("hp_scale_bp"), 1, 100000);
            Wave.damageScaleBp = Source.Integer(TEXT("damage_scale_bp"), 1, 100000);
            const auto& Slots = Source.Array(TEXT("slots"));
            Require(Slots.Num() > 0 && Slots.Num() <= 6, TEXT("Neutral wave requires one to six creatures"));
            TSet<int32> Cells;
            for (const auto& SlotValue : Slots)
            {
                const FObject Slot = AsObject(SlotValue, TEXT("neutral_slot"));
                ExactKeys(Slot, {TEXT("creature_id"),TEXT("column"),TEXT("row")});
                const FString CreatureId = Slot.String(TEXT("creature_id"));
                Require(NeutralIndices.Contains(CreatureId), TEXT("Wave refers to unknown neutral"));
                const int32 Column = Slot.Integer(TEXT("column"), 0, Next.rules.columns-1);
                const int32 Row = Slot.Integer(TEXT("row"), 0, Next.rules.deploymentRows-1);
                Require(!Cells.Contains(Row*Next.rules.columns+Column), TEXT("Duplicate neutral cell"));
                Cells.Add(Row*Next.rules.columns+Column);
                Wave.slots.push_back({NeutralIndices.FindChecked(CreatureId), {Column,Row}});
            }
            Next.waves.push_back(Wave);
        }

        TSet<FString> TraitIds;
        for (const auto& Value : TraitsSource.Array(TEXT("traits")))
        {
            const FObject Trait = AsObject(Value, TEXT("traits"));
            ExactKeys(Trait, {TEXT("id"),TEXT("kind"),TEXT("name"),TEXT("stat"),TEXT("magnitude_unit"),TEXT("tiers"),TEXT("recipients"),TEXT("count_rule"),TEXT("higher_tier"),TEXT("activation"),TEXT("description"),TEXT("alpha_enabled")});
            const FString Id = Trait.String(TEXT("id"));
            Require(!TraitIds.Contains(Id), TEXT("Duplicate trait ID"));
            TraitIds.Add(Id);
            Trait.Expect(TEXT("recipients"), TEXT("matching_units"));
            Trait.Expect(TEXT("count_rule"), TEXT("distinct_deployed_types"));
            Trait.Expect(TEXT("higher_tier"), TEXT("replaces"));
            Trait.Expect(TEXT("activation"), TEXT("combat_snapshot"));
            const FString Kind = Trait.String(TEXT("kind"));
            Require(Kind == TEXT("race") || Kind == TEXT("class"), TEXT("Unknown trait kind"));
            if (!Trait.Boolean(TEXT("alpha_enabled"))) continue;
            TraitDef T;
            T.id = Utf8(Id);
            T.stat = Utf8(Trait.String(TEXT("stat")));
            const std::set<std::string> SupportedStats = {"max_health_bonus_bp","attack_rate_bonus_bp","physical_armor_flat","all_damage_bonus_bp","basic_damage_bonus_bp","ability_damage_bonus_bp","support_power_bonus_bp","movement_bonus_bp","magic_resistance_flat"};
            Require(SupportedStats.count(T.stat) != 0, TEXT("Unsupported alpha trait statistic"));
            const auto& Tiers = Trait.Array(TEXT("tiers"));
            bool FoundTier = false, FoundFourth = false;
            for (const auto& TierValue : Tiers)
            {
                const FObject Tier = AsObject(TierValue, Trait.Path + TEXT(".tiers"));
                const int Count = Tier.Integer(TEXT("count"), 1);
                const int ValueInt = Tier.Integer(TEXT("value"));
                if (Count == 2)
                {
                    Require(!FoundTier, TEXT("Duplicate active trait threshold"));
                    FoundTier = true;
                    T.threshold = Count;
                    T.value = ValueInt;
                }
                else if (Count == 4)
                {
                    Require(!FoundFourth, TEXT("Duplicate fourth trait threshold"));
                    FoundFourth = true; T.threshold4 = Count; T.value4 = ValueInt;
                }
                else Require(false, TEXT("Unsupported trait threshold"));
            }
            Require(FoundTier && FoundFourth, TEXT("Missing active trait threshold"));
            Next.traits.push_back(T);
        }
        Require(TraitIds.Num() == 12 && Next.traits.size() == 12, TEXT("Expected twelve active race/class traits"));
        TSet<FString> BotIds;
        for (const auto& Value : BotsSource.Array(TEXT("bots")))
        {
            const FObject Bot = AsObject(Value, TEXT("bots"));
            ExactKeys(Bot, {TEXT("id"),TEXT("label"),TEXT("focus"),TEXT("weights"),TEXT("decision_interval_ms"),TEXT("public_observation_ms"),TEXT("max_commands_per_preparation"),TEXT("max_paid_rerolls_per_preparation"),TEXT("noise_bp"),TEXT("honesty")});
            BotDef B;
            B.id = Utf8(Bot.String(TEXT("id")));
            B.label = Utf8(Bot.String(TEXT("label")));
            Require(!BotIds.Contains(UTF8_TO_TCHAR(B.id.c_str())), TEXT("Duplicate bot persona ID"));
            BotIds.Add(UTF8_TO_TCHAR(B.id.c_str()));
            Bot.String(TEXT("focus"));
            Bot.Expect(TEXT("honesty"), TEXT("same_commands_same_information_same_shop_rules"));
            const FObject Weights = Bot.Object(TEXT("weights"));
            ExactKeys(Weights, {TEXT("frontline"),TEXT("damage"),TEXT("support"),TEXT("upgrade"),TEXT("synergy"),TEXT("level"),TEXT("save")});
            B.frontline = Weights.Number(TEXT("frontline"), 0, 10);
            B.damage = Weights.Number(TEXT("damage"), 0, 10);
            B.support = Weights.Number(TEXT("support"), 0, 10);
            B.upgrade = Weights.Number(TEXT("upgrade"), 0, 10);
            B.synergy = Weights.Number(TEXT("synergy"), 0, 10);
            B.level = Weights.Number(TEXT("level"), 0, 10);
            B.save = Weights.Number(TEXT("save"), 0, 10);
            B.decisionIntervalMs = Bot.Integer(TEXT("decision_interval_ms"), 1);
            B.observationMs = Bot.Integer(TEXT("public_observation_ms"), 1);
            B.maxCommands = Bot.Integer(TEXT("max_commands_per_preparation"), 1, 1000);
            B.maxRerolls = Bot.Integer(TEXT("max_paid_rerolls_per_preparation"), 0, 1000);
            B.noiseBp = Bot.Integer(TEXT("noise_bp"), 0, 10000);
            Next.bots.push_back(B);
        }
        Require(Next.bots.size() == 7, TEXT("Exactly seven authored bot personas required"));
        for (const FString Language : {FString(TEXT("en")),FString(TEXT("id"))})
        {
            const FObject Locale = ReadObject(Directory / TEXT("locales") / (Language + TEXT(".json")));
            TMap<FString,FString>& Strings = NextText.Locales.Add(Language);
            for (const auto& Entry : Locale.Value->Values) Strings.Add(Entry.Key, Locale.String(Entry.Key));
        }
        const auto& English = NextText.Locales.FindChecked(TEXT("en"));
        const auto& Indonesian = NextText.Locales.FindChecked(TEXT("id"));
        Require(English.Num() == Indonesian.Num(), TEXT("Locale key count mismatch"));
        for (const auto& Entry : English) Require(Indonesian.Contains(Entry.Key), TEXT("Missing Indonesian locale key: ") + Entry.Key);
        NextText.World = ReadObject(Directory / TEXT("world.json")).Value;
        const std::string Failure = Next.Validate();
        Require(Failure.empty(), FString(TEXT("Catalog invariant: ")) + UTF8_TO_TCHAR(Failure.c_str()));
        OutCatalog = std::move(Next);
        if (Text) *Text = MoveTemp(NextText);
        return true;
    }
    catch (const FDataError& Failure)
    {
        Error = Failure.Message;
    }
    catch (const std::exception& Failure)
    {
        Error = FString(TEXT("Runtime catalog exception: ")) + UTF8_TO_TCHAR(Failure.what());
    }
    return false;
}

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCCatalogLoadTest, "WonderChess.Data.CanonicalCatalog", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FWCCatalogLoadTest::RunTest(const FString& Parameters)
{
    wc::Catalog Catalog;
    FWCDefinitionText Text;
    FString Error;
    if (!wc::LoadCatalog(Catalog, Error, &Text))
    {
        AddError(Error);
        return false;
    }
    TestEqual(TEXT("Playable alpha definitions"), static_cast<int32>(Catalog.units.size()), 24);
    TestEqual(TEXT("Active alpha traits"), static_cast<int32>(Catalog.traits.size()), 12);
    TestEqual(TEXT("Neutral archetypes"), static_cast<int32>(Catalog.neutrals.size()), 7);
    TestEqual(TEXT("Authored waves"), static_cast<int32>(Catalog.waves.size()), 11);
    TestEqual(TEXT("Authored bot personas"), static_cast<int32>(Catalog.bots.size()), 7);
    TestEqual(TEXT("Localized English title"), Text.Localized(TEXT("game.title")), FString(TEXT("Wonder Chess")));
    TestTrue(TEXT("Authored metadata retained for every alpha hero"), Text.Units.Num() == 24);
    for (const auto& Unit : Catalog.units)
    {
        TestFalse(TEXT("English tooltip retained"), Text.AbilityTooltip(UTF8_TO_TCHAR(Unit.id.c_str())).IsEmpty());
        TestFalse(TEXT("Indonesian tooltip retained"), Text.AbilityTooltip(UTF8_TO_TCHAR(Unit.id.c_str()), TEXT("id")).IsEmpty());
    }
    return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCCatalogValidationTest, "WonderChess.Data.RejectInvalidNumericTypes", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FWCCatalogValidationTest::RunTest(const FString& Parameters)
{
    const auto Json = MakeShared<FJsonObject>();
    const FObject Record(Json, TEXT("validation_fixture"));
    const auto Rejected = [&Record]()
    {
        try { Record.Integer(TEXT("value"), 0, 100); }
        catch (const FDataError&) { return true; }
        return false;
    };
    TestTrue(TEXT("Missing required numeric value rejected"), Rejected());
    Json->SetStringField(TEXT("value"), TEXT("50"));
    TestTrue(TEXT("Numeric string rejected"), Rejected());
    Json->SetNumberField(TEXT("value"), 50.5);
    TestTrue(TEXT("Fractional centipoint rejected"), Rejected());
    Json->SetNumberField(TEXT("value"), 101);
    TestTrue(TEXT("Out-of-bounds integer rejected"), Rejected());
    Json->SetBoolField(TEXT("value"), true);
    TestTrue(TEXT("Boolean masquerading as integer rejected"), Rejected());
    Json->SetNumberField(TEXT("value"), 50);
    TestFalse(TEXT("Valid integer accepted"), Rejected());
    return !HasAnyErrors();
}
#endif
