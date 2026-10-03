#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Components/SceneComponent.h"
#include "Simulation/WonderSimulation.h"
#include "WCBellbackPresentation.generated.h"

class USkeletalMeshComponent;
class USkeletalMesh;
class UAnimSequence;
class USoundBase;
class USoundConcurrency;
class UMaterialInterface;

// Game-thread inputs are copied into the native proxy before any pose evaluation.
UCLASS(Transient)
class WONDERCHESSRUNTIME_API UWCBellbackAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY() TObjectPtr<UAnimSequence> Current;
    UPROPERTY() TObjectPtr<UAnimSequence> Previous;
    UPROPERTY() TObjectPtr<UAnimSequence> Overlay;
    float CurrentSeconds=0, PreviousSeconds=0, BlendAlpha=1;
    float OverlaySeconds=0,OverlayAlpha=0;
    FName OverlayBone=NAME_None;
    int CorrectedLegs=0;
    float MaximumFootCorrection=0;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};

struct FWCBellbackFrame
{
    uint64 Generation=0;
    const wc::Combat* Combat=nullptr;
    const wc::CombatUnit* Unit=nullptr;
    uint64 Id=0;
    int Side=0, Facing=0, TickMs=50;
    double Clock=0;
    float DeltaSeconds=0;
    bool Paused=false, AllowSound=true;
    // Explicit cosmetic review only; never used to update simulation.
    FName ReviewClip=NAME_None;
    float ReviewSeconds=0;
    bool ReviewTravel=false;
    int ReviewEffectSerial=-1;
};

UCLASS()
class WONDERCHESSRUNTIME_API UWCBellbackPresentationComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    static bool ValidateAssets(FString& Error);
    bool InitializeCandidate(FString& Error);
    void Present(const FWCBellbackFrame& Frame);
    FVector CueLocation(FName Socket) const;
    bool IsDefeatFinished() const;
    FName ClipName() const {return CurrentClip;}
    float ClipSeconds() const {return SampleSeconds;}
    float MoveRate() const {return LastMoveRate;}
    int SoundCount() const {return SoundsPlayed;}
    USkeletalMeshComponent* GetMesh() const {return Skeletal;}
    const TSet<FName>& SeenClips() const {return Seen;}
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Skeletal;
    UPROPERTY() TMap<FName,TObjectPtr<UAnimSequence>> Clips;
    UPROPERTY() TMap<FName,TObjectPtr<USoundBase>> Sounds;
    UPROPERTY() TObjectPtr<USoundConcurrency> Concurrency;
    uint64 Generation=MAX_uint64;
    size_t EventCursor=0;
    double LastClock=0, BlendStarted=0, OverrideStarted=-100, TerminalStarted=-1;
    float SampleSeconds=0, PreviousSeconds=0, LastMoveRate=0;
    float WalkPhase=0, LastYaw=0, MeshYaw=0;
    FVector LastLocation=FVector::ZeroVector;
    FName CurrentClip=NAME_None, PreviousClip=NAME_None, OverrideClip=NAME_None, TerminalClip=NAME_None;
    TSet<FName> Seen;
    int SoundsPlayed=0;
    int ReviewEffectSerial=-1;
    bool HasLocation=false;
    float GroundTravelCm=0;
    void PlayCue(FName Cue,FName Socket,const FWCBellbackFrame& Frame);
    void SetPose(FName Clip,float Seconds,double Clock);
};
