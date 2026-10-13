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
// A small light that rides on a bone: glowing eyes, a lantern seed, the light inside a split seed.
struct FWCGlow
{
    FName Bone;
    FVector At = FVector::ZeroVector;
    FLinearColor Color = FLinearColor::White;
    float Size = 20;
};

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
    // A walking staff: whatever the hand does, the item stays upright, pivoting about the grip.
    bool bUpright = false;
    // Something carried on a chain: it hangs straight down from the hand and swings behind the hand's motion.
    bool bHang = false;
    FVector Swing = FVector(0, 0, -1), LastGrip = FVector::ZeroVector;
    // A rifle or blowpipe: during these clips the item points straight ahead of the hero, whatever the hand does.
    TSet<FName> AimClips;
    // A linstock or tool: during these clips its tip is brought to a point on another listed item (item space).
    TSet<FName> TouchClips;
    int TouchItem = -1;
    FVector TouchAt = FVector::ZeroVector;
    // A small fire burning on the item (item space), such as a lit match cord.
    bool bFlame = false;
    FVector Flame = FVector::ZeroVector;
    float FlameSize = 1;
    // Current clearance turn about the grip point, in the hand bone's space.
    FQuat Clearance = FQuat::Identity;
};

// An item that hovers beside the hero instead of being held: it rides one bone, bobs and turns slowly.
struct FWCFloatItem
{
    TObjectPtr<UStaticMeshComponent> Item;
    FTransform Base;
    // World-up expressed in the bone's space, so the bob stays vertical.
    FVector Up = FVector::ZAxisVector;
    float Bob = 4, Spin = 25, Phase = 0;
    // An item that stands on the ground beside the hero; it rolls while the hero walks.
    bool bGround = false;
    float Roll = 0, RollRate = 0;
    // Recoil: centimetres the item has been knocked straight back; it rolls forward again by itself.
    float Kick = 0;
};

// The off hand reaching for a second point on a held weapon, so a long weapon is swung with both hands.
struct FWCSecondHand
{
    FName Upper, Lower, Hand, Carrier;
    // Where the off hand grips, in the carrying hand bone's space.
    FVector Target = FVector::ZeroVector;
    float Weight = 0;
    bool bValid = false;
    // A repeated strike: the target rises and falls along Axis (carrier space) by Beat centimetres, Rate times a
    // second, as when drumming.
    FVector Axis = FVector::ZAxisVector;
    float Beat = 0, Rate = 0, Phase = 0;
    TSet<FName> Clips;
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
    FWCSecondHand SecondHand;
    TArray<FWCSecondHand> Reaches;
    float ReachTime = 0;
    TArray<FName> StraightBones;
    float StraightWeight = 0;
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
    // The hero's whole presentation entry, for readers outside this component (shot looks).
    static TSharedPtr<class FJsonObject> Config(const FString& HeroId);
    // Hides one listed item for a moment, as when a held bomb has just been thrown.
    void HideItemFor(int Index, float HideSeconds);
    // Where a listed item is in the world, for shots that leave an item rather than a hand (a cannon).
    FVector ItemLocation(int Index) const;
    // The far end of a gripped item (the hammer's head, the tip of a blade), for swing trails.
    FVector ItemTip(int Index) const;
    // Knocks a ground item straight back, as a cannon recoils when it fires.
    void KickItem(int Index, float Centimetres);
    // Calls Each(world position, size) for every fire burning on a held item.
    void FlamePoints(TFunctionRef<void(const FVector&, float)> Each) const;
    bool InitializeHero(const FString& HeroId, FString& Error);
    // Unit is null outside combat; the hero then idles.
    void Present(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds);
    // Cosmetic review only: holds one named clip regardless of combat state until cleared with NAME_None.
    void ReviewClip(FName Clip, bool Loop);
    USkeletalMeshComponent* GetMesh() const { return Skeletal; }
    // Calls Each(world position, colour, size in cm) for every glow listed for this model.
    void GlowPoints(TFunctionRef<void(const FVector&, const FLinearColor&, float)> Each) const;
    FName ClipName() const { return Current; }
    float LabelHeight() const { return Height; }
    // Where this hero's shots and beams start: a floating item, the far end of an upright staff, or the hand.
    FVector MuzzleLocation(int Index) const;
    // A JSON fragment of this frame's clip, feet, hands and held items, for the frame recorder.
    FString Describe() const;
    // Set while the hero stands alive in a finished fight; it then plays its Taunt clip if it has one.
    bool bCelebrate = false;
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Skeletal;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Items;
    UPROPERTY() TMap<FName, TObjectPtr<UAnimSequence>> Clips;
    TMap<FName, float> Rates;
    TSet<FName> FreeArmClips;
    TMap<int32, float> HiddenItems;
    TArray<FWCGlow> Glows;
    FWCHeldArm HeldArm;
    // Other held-arm poses used during particular clips (upper-arm and forearm rotations), such as raising a pipe to the mouth.
    TMap<FName, TPair<FQuat, FQuat>> ArmPoses;
    TArray<FWCBoneCurl> Curls;
    TArray<FWCGripItem> Grips;
    TArray<FWCFloatItem> Floats;
    FWCSecondHand SecondHand;
    TSet<FName> SecondHandClips;
    TArray<FWCSecondHand> Reaches;
    TArray<FName> StraightBones;
    TSet<FName> StraightClips;
    float StraightAmount = 0, StraightNow = 0;
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
    // How an unrigged model moves: 0 drifts like water, 1 walks on heavy legs, 2 flickers like a flame.
    int StaticMotion = 0;
    void PresentStatic(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds);
    void Play(FName Clip, bool Loop, bool Restart = false);
    void Advance(float DeltaSeconds);
};
