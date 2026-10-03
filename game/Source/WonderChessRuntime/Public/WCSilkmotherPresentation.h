#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Components/SceneComponent.h"
#include "WCBellbackPresentation.h"
#include "WCSilkmotherPresentation.generated.h"
class USkeletalMeshComponent;
class UAnimSequence;
class USoundBase;
class USoundConcurrency;
class USoundAttenuation;

UCLASS(Transient)
class WONDERCHESSRUNTIME_API UWCSilkmotherAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY() TObjectPtr<UAnimSequence> Current;
    UPROPERTY() TObjectPtr<UAnimSequence> Previous;
    UPROPERTY() TObjectPtr<UAnimSequence> HitReaction;
    float Seconds=0,PreviousSeconds=0,Alpha=1;
    float HitReactionSeconds=0;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};

UCLASS()
class WONDERCHESSRUNTIME_API UWCSilkmotherPresentationComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    static bool ValidateAssets(FString& Error);
    bool InitializeCandidate(FString& Error);
    void Present(const FWCBellbackFrame& Frame);
    USkeletalMeshComponent* GetMesh() const { return Skeletal; }
    FVector CueLocation(FName Socket) const;
    bool IsDefeatFinished() const;
    FName ClipName() const {return CurrentClip;}
    float ClipSeconds() const {return CurrentSeconds;}
    int SoundCount() const {return SoundsPlayed;}
    bool HasHitOverlay() const {return HitOverlayActive;}
    float HitOverlaySeconds() const {return HitOverlayAge;}
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Skeletal;
    UPROPERTY() TMap<FName,TObjectPtr<UAnimSequence>> Clips;
    UPROPERTY() TMap<FName,TObjectPtr<USoundBase>> Sounds;
    UPROPERTY() TObjectPtr<USoundConcurrency> Concurrency;
    UPROPERTY() TObjectPtr<USoundAttenuation> Attenuation;
    TSet<uint64> ReleasedActions,WeavingActions;
    TMap<uint64,TPair<int,FVector>> CaughtTargets;
    int SoundsPlayed=0,StepVariant=0;
    float MeshYaw=0;
    uint64 Generation=MAX_uint64;
    double LastClock=0,BlendStarted=0,TerminalStarted=-1,HitStarted=-100;
    size_t EventCursor=0;
    float WalkPhase=0,CurrentSeconds=0,OldSeconds=0;
    FVector PreviousLocation=FVector::ZeroVector;
    bool HasLocation=false;
    bool HitOverlayActive=false;
    float HitOverlayAge=0;
    FName CurrentClip=NAME_None,OldClip=NAME_None,TerminalClip=NAME_None;
    void SetPose(FName Name,float Seconds,double Clock);
    void PlayCue(FName Name,FVector Location,const FWCBellbackFrame& Frame);
};
