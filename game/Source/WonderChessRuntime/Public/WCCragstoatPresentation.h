#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Components/SceneComponent.h"
#include "WCBellbackPresentation.h"
#include "WCCragstoatPresentation.generated.h"

class UAnimSequence;
class USkeletalMeshComponent;
class USoundBase;
class USoundConcurrency;
class USoundAttenuation;
class UAudioComponent;
struct FPoseContext;

// Explicit candidate inputs, copied on the game thread before evaluation.
// Editor cold studies use these same inputs and BuildPose; no Bellback solver.
UCLASS(Transient)
class WONDERCHESSRUNTIME_API UWCCragstoatAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY() TObjectPtr<UAnimSequence> Current;
    UPROPERTY() TObjectPtr<UAnimSequence> Previous;
    UPROPERTY() TObjectPtr<UAnimSequence> HitReaction;
    UPROPERTY() TObjectPtr<UAnimSequence> GroundingReference;
    float Seconds=0, PreviousSeconds=0, Alpha=1, HitReactionSeconds=0;
    bool PoseValid=true;
    int CorrectedLegs=0;
    float MaximumFootCorrection=0;

    // No notifies, root-motion application, collision or simulation commands.
    // GroundingReference is this candidate's authored Idle sampled at zero.
    // An ankle baseline is not proof of sole/skin clearance: cold skin gates
    // still apply separately to every saved LOD and combined transition.
    // Interior crossfades preserve endpoint-blended component ankle/paw goals;
    // the local body blend and strict reach checks remain authoritative.
    static bool BuildPose(FPoseContext& Output, UAnimSequence* Current, float Seconds,
        UAnimSequence* Previous, float PreviousSeconds, float Alpha,
        UAnimSequence* HitReaction, float HitReactionSeconds,
        UAnimSequence* GroundingReference, int* CorrectedLegs=nullptr,
        float* MaximumFootCorrection=nullptr);
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};

UCLASS()
class WONDERCHESSRUNTIME_API UWCCragstoatPresentationComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    static bool CandidateEnabled();
    static bool ValidateAssets(FString& Error);
    bool InitializeCandidate(FString& Error);
    void Present(const FWCBellbackFrame& Frame);
    USkeletalMeshComponent* GetMesh() const { return Skeletal; }
    FVector CueLocation(FName Bone) const;
    bool IsDefeatFinished() const;
    FName ClipName() const { return CurrentClip; }
    float ClipSeconds() const { return CurrentSeconds; }
    float ClipDuration(FName Name) const;
    float MoveRate() const { return LastMoveRate; }
    bool HasHitOverlay() const { return HitOverlayActive; }
    float HitOverlaySeconds() const { return HitOverlayAge; }
    const TSet<FName>& SeenClips() const { return Seen; }
    int SoundCount() const { return SoundsPlayed; }
protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Skeletal;
    UPROPERTY() TMap<FName,TObjectPtr<UAnimSequence>> Clips;
    UPROPERTY() TMap<FName,TObjectPtr<USoundBase>> Sounds;
    UPROPERTY() TObjectPtr<USoundConcurrency> Concurrency;
    UPROPERTY() TObjectPtr<USoundAttenuation> Attenuation;
    UPROPERTY() TObjectPtr<UAudioComponent> ActiveTell;
    TArray<TWeakObjectPtr<UAudioComponent>> LiveCues;
    TSet<uint64> AttackTells, ChargeTells;
    uint64 ActiveTellAction=0;
    int SoundsPlayed=0, AttackVariant=0, ImpactVariant=0, HitVariant=0;
    uint64 Generation=MAX_uint64, CurrentAction=0;
    size_t EventCursor=0;
    double LastClock=0, LastPoseClock=0, BlendStarted=0;
    double TerminalStarted=-1, HitStarted=-100, TurnStarted=-100;
    float WalkPhase=0, MeshYaw=0, LastFacingYaw=0, LastMoveRate=0;
    float CurrentSeconds=0, OldSeconds=0, CurrentRate=0, OldRate=0;
    FVector PreviousLocation=FVector::ZeroVector;
    bool HasLocation=false, HitOverlayActive=false;
    float HitOverlayAge=0;
    int ReviewEffectSerial=-1;
    FName CurrentClip=NAME_None, OldClip=NAME_None, TerminalClip=NAME_None, TurnClip=NAME_None;
    TSet<FName> Seen;
    void SetPose(FName Name, float Seconds, double Clock, float Rate, uint64 Action=0);
    void PlayCue(FName Name, FVector Location, const FWCBellbackFrame& Frame);
    void StopActiveTell();
    void StopAllCues();
};
