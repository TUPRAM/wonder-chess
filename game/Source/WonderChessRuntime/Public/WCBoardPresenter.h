#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WCDefinitionRegistry.h"
#include "WCAttackPresentation.h"
#include "WCBoardPresenter.generated.h"
class AWCMatchController;
class USkeletalMeshComponent;
class UStaticMeshComponent;
class UMaterialInstanceDynamic;
UCLASS()
class WONDERCHESSRUNTIME_API AWCBoardPresenter : public AActor {
  GENERATED_BODY()
public:
  AWCBoardPresenter();
  virtual void Tick(float Delta) override;
  void Initialize();
  void Refresh(float Delta);
  FVector Position(int Column, int Row) const;
  TArray<TSharedPtr<FJsonValue>> VisibleUnits;
  TMap<int64, AActor *> Heroes;
  wc::Catalog Definitions;
  FWCDefinitionText Metadata;
  AWCMatchController *Controller = nullptr;
  FString AssetStatus;

private:
  TMap<int64, int32> PreviousStates;
  TMap<int64, int64> PreviousActions;
  struct FAttackWindows {
    EWCAttackWindowStatus Status = EWCAttackWindowStatus::Absent;
    wc::presentation::AttackWindows Windows;
    FString Error;
  };
  TMap<FString, FAttackWindows> AttackWindows;
  TMap<int64, wc::presentation::AttackClock> AttackClocks;
  TMap<int64, FVector> Targets;
  TMap<int64, UStaticMeshComponent *> Highlights;
  TMap<FString, AActor*> StatusMarkers, Telegraphs;
  TSet<FString> HeardActions, KnownProjectiles;
  UPROPERTY() TMap<uint32, TObjectPtr<UMaterialInstanceDynamic>> Materials;
  UPROPERTY() TArray<TObjectPtr<UObject>> ResidentAssets;
  UPROPERTY() TObjectPtr<AActor> Camera;
  UMaterialInstanceDynamic *Material(FLinearColor Color);
  void Prop(const FString &Asset, FVector Location, FVector Scale,
            FLinearColor Color, FRotator Rotation = FRotator::ZeroRotator);
  void BuildArena();
  struct VisualEffect {
    AActor *Actor;
    FVector Start, End;
    float Age = 0, Duration = .4f;
    int32 Kind = 0;
  };
  TArray<VisualEffect> Effects;
  void SpawnEffect(int32 Kind, int64 Source, int64 Target, int32 Radius = 0,
                   int32 Column = -1, int32 Row = -1, const FString& UnitId = FString(), bool Basic = false);
  AActor* CreateGlyph(int32 Kind, FVector Center, FLinearColor Color, float Duration = 0,
                      FVector Extent = FVector(24,24,24));
  AActor* CreateBoundary(int32 Column, int32 Row, int32 Radius, FLinearColor Color, float Duration = 0);
  void PresentActions(const TArray<TSharedPtr<FJsonValue>>& Actions, int32 Tick);
  float HeroHeight(int64 Id) const;
  void UpdateEffects(float Delta);
  void SpawnProjectile(FVector Start, FVector End, float Duration,
                       FLinearColor Color, bool Arrow);
  bool bEncounterCompleted = false;
  int32 LastEncounter = -1;
  int32 LastEventTick = -1;
  int32 LastRound = -1, LastPhase = -99;
  int32 LastObserved = -1;
  int64 LastMatchNamespace = -1;
  float ReviewAge = 0;
  int32 ReviewCapture = -1;
};
