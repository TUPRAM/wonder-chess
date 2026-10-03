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

// A grip bone bent by a fixed amount in every clip, so the hand stays closed around what it holds.
struct FWCBoneCurl
{
    FName Bone;
    // Rotation in the parent bone's space, applied in front of the bone's own rotation.
    FQuat ParentSpace = FQuat::Identity;
};

// A weapon held in a hand, treated as a rod from the grip to its far end for the body-clearance pass.
struct FWCGripItem
{
    TObjectPtr<UStaticMeshComponent> Item;
    FName Bone;
    // Placement relative to the hand bone before any clearance turn.
    FTransform Base;
    // Grip point and direction to the far end in the item's own space; length and thickness in centimetres.
    FVector Point = FVector::ZeroVector, Tip = FVector::ZAxisVector;
    float Length = 0, Radius = 6;
    // Current clearance turn about the grip point, in the hand bone's space.
    FQuat Clearance = FQuat::Identity;
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
    TArray<FWCBoneCurl> Curls;
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
    TArray<FWCBoneCurl> Curls;
    TArray<FWCGripItem> Grips;
    float BodyHeight = 180, BodyRadiusScale = 1;
    // Turns each held weapon about its grip just enough to stay outside the hero's own torso, head and legs.
    void ClearBody(float DeltaSeconds);
    FName Current = NAME_None, Before = NAME_None;
    uint64 PlayedAction = 0;
    bool Reviewing = false, Looping = true;
    float Height = 205, Seconds = 0, BeforeSeconds = 0, Blend = 1;
    // A hero without a skeleton ("static_mesh" in the config) is one solid model moved by code: it floats and
    // sways, surges forward to attack, swells to cast, shudders when stunned and collapses when defeated.
    UPROPERTY() TObjectPtr<UStaticMeshComponent> StaticBody;
    float StaticScale = 1, StaticYaw = 0, StaticLift = 0, Clock = 0, ActionAge = 10, DefeatAge = 0;
    bool StaticCasting = false;
    void PresentStatic(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds);
    void Play(FName Clip, bool Loop, bool Restart = false);
    void Advance(float DeltaSeconds);
};
