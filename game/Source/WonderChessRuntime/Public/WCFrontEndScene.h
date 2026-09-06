#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WCFrontEndScene.generated.h"

class AWCMatchController;
class UCameraComponent;
class USkeletalMeshComponent;
class UStaticMeshComponent;
class FJsonObject;

// A local presentation scene. It never creates owned units or advances combat.
UCLASS()
class WONDERCHESSRUNTIME_API AWCFrontEndScene : public AActor {
  GENERATED_BODY()
public:
  AWCFrontEndScene();
  void Initialize(AWCMatchController* OwnerController);
  void ShowHero(const FString& UnitId, int32 Star, bool ReducedMotion);
  bool PlayClip(const FString& Clip, bool ReducedMotion);
  void RotateHero(float Degrees);
  void ResetView();
  void SetTurntable(bool Enabled);
  void TransitionToArena(float Duration, bool ReducedMotion);
  void RestoreCamera();
  void RestorePreview();
  TSharedPtr<FJsonObject> MeasureGrounding() const;
  virtual void Tick(float DeltaSeconds) override;
  FString AssetMessage;
  FString SelectedClip = TEXT("Idle");
  bool bApproachImported = false;

private:
  UStaticMeshComponent* AddProp(const TCHAR* Name, FVector Position, FVector Scale = FVector(1),
               FRotator Rotation = FRotator::ZeroRotator, const TCHAR* Folder = TEXT("Arena"));
  UPROPERTY() TObjectPtr<UCameraComponent> Camera;
  UPROPERTY() TObjectPtr<USkeletalMeshComponent> Hero;
  UPROPERTY() TObjectPtr<UStaticMeshComponent> Floor;
  UPROPERTY() TArray<TObjectPtr<UObject>> ResidentAssets;
  TWeakObjectPtr<AWCMatchController> Controller;
  TWeakObjectPtr<AActor> PreviousCamera;
  TArray<TWeakObjectPtr<AActor>> HiddenArenaActors;
  FString HeroId;
  float Rotation = -45.f;
  bool bTurntable = false;
  int32 FramingFrames = 0;
  int32 TransitionStage = 0;
  float TransitionClock = 0, FadeSeconds = .18f;
  void FitPreview();
  void SetArenaVisible(bool Visible);
};
