#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Components/SceneComponent.h"
#include "Simulation/WonderSimulation.h"
#include "WCHeroPresentation.generated.h"

class USkeletalMeshComponent;
class UStaticMeshComponent;
class UAnimSequence;

// An arm held in one fixed pose relative to the chest, so a strapped item reads as worn in every clip.
struct FWCHeldArm
{
    FName Chest, Upper, Lower;
    // Component-space rotations of the chest in the reference pose and of the two arm bones in the held pose.
    FQuat ChestReference = FQuat::Identity, UpperHeld = FQuat::Identity, LowerHeld = FQuat::Identity;
    bool bValid = false;
};

// Game-thread inputs are copied into the native proxy before any pose evaluation.
UCLASS(Transient)
class WONDERCHESSRUNTIME_API UWCHeroAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY() TObjectPtr<UAnimSequence> Current;
    UPROPERTY() TObjectPtr<UAnimSequence> Previous;
    float CurrentSeconds = 0, PreviousSeconds = 0, BlendAlpha = 1;
    FWCHeldArm HeldArm;
    bool bHoldArm = false;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};

// Shows one rigged hero model on the board and picks its clip from the unit's combat state.
// Purely cosmetic: it reads the simulation and never changes it.
UCLASS()
class WONDERCHESSRUNTIME_API UWCHeroPresentationComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    // True when Content/WonderChess/VNextData/hero_presentation.json lists this hero.
    static bool HasModel(const FString& HeroId);
    bool InitializeHero(const FString& HeroId, FString& Error);
    // Unit is null outside combat; the hero then idles.
    void Present(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds);
    // Cosmetic review only: holds one named clip regardless of combat state until cleared with NAME_None.
    void ReviewClip(FName Clip, bool Loop);
    USkeletalMeshComponent* GetMesh() const { return Skeletal; }
    FName ClipName() const { return Current; }
    float LabelHeight() const { return Height; }
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Skeletal;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Items;
    UPROPERTY() TMap<FName, TObjectPtr<UAnimSequence>> Clips;
    TMap<FName, float> Rates;
    TSet<FName> FreeArmClips;
    FWCHeldArm HeldArm;
    FName Current = NAME_None, Before = NAME_None;
    uint64 PlayedAction = 0;
    bool Reviewing = false, Looping = true;
    float Height = 205, Seconds = 0, BeforeSeconds = 0, Blend = 1;
    void Play(FName Clip, bool Loop, bool Restart = false);
    void Advance(float DeltaSeconds);
};
