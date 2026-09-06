// GENERATED CANDIDATE: not Unreal-compiled by the kit. Verify in the installed engine.
#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "WCDataRows.generated.h"

USTRUCT(BlueprintType)
struct FWCAbilityEffect
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName EffectId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName DamageType = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName MagnitudeUnit = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int64 Magnitude1 = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int64 Magnitude2 = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int64 Magnitude3 = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 DurationMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName StatId = NAME_None;
};

USTRUCT(BlueprintType)
struct FWCUnitRow : public FTableRowBase
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName UnitId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FString DisplayName = TEXT("");
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FString LoreName = TEXT("");
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    TArray<FName> RoleTags = {};
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName RaceId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName ClassId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName AbilityId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 Cost = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int64 HealthCp = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int64 AttackDamageCp = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 AttackRateMilli = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 AttackRangeTiles = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 PhysicalArmor = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 MagicResistance = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 MovementRateMilli = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName AttackDelivery = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName AttackDamageType = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 AttackWindupMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 ProjectileTravelMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName ProductionPhase = NAME_None;
};

USTRUCT(BlueprintType)
struct FWCAbilityRow : public FTableRowBase
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName AbilityId = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FString DisplayName = TEXT("");
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    TArray<FWCAbilityEffect> Effects = {};
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FName TargetRule = NAME_None;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 FirstCastMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 CooldownMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 CastMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 RecoveryMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 RangeTiles = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 RadiusTiles = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 MaxTargets = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 MaxDashTiles = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    int32 TravelMs = 0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    bool AllowSelf = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FString TooltipEn = TEXT("");
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="WonderChess")
    FString TooltipId = TEXT("");
};

