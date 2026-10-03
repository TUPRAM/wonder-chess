#include "WCCragstoatPresentation.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimationPoseData.h"
#include "Animation/AnimSequence.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundConcurrency.h"
#include "Sound/SoundAttenuation.h"

namespace
{
const TCHAR* AcceptedRoot=TEXT("/Game/WonderChess/Diagnostics/CragstoatRevision20260930/SageTail_r003/");
const TCHAR* AnimationRoot=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Animations/Combat_r003/");
const TCHAR* RunningRoot=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Animations/Running_r004/");
const TCHAR* AudioRoot=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Audio/");
const FName Names[]={TEXT("Idle"),TEXT("Move"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory"),TEXT("TurnLeft"),TEXT("TurnRight")};
const FName SoundNames[]={TEXT("Footstep1"),TEXT("Footstep2"),TEXT("Footstep3"),TEXT("Footstep4"),
    TEXT("Attack1"),TEXT("Attack2"),TEXT("Impact1"),TEXT("Impact2"),TEXT("Impact3"),
    TEXT("Hit1"),TEXT("Hit2"),TEXT("Active"),TEXT("Dash"),TEXT("Defeat"),TEXT("Victory")};
const float Lengths[]={2.4f,.6f,.8f,.65f,.4f,1.6f,2.4f,.6f,.6f};
// Saved Running_r004 Move: 30cm stance travel / .25 duty, scale1, +X forward.
// Diagonal pairs touch down at0/.5; explicit flights occupy .25-.5/.75-1.
// This is a cosmetic phase mapping, never a movement-rate override.
constexpr float TravelPerCycle=120.f, CrossfadeSeconds=.12f;
constexpr float AttackRelease=.15f, ActiveRelease=.35f;

template<class T>T* LoadAccepted(const TCHAR* Name)
{
    return LoadObject<T>(nullptr,*(FString(AcceptedRoot)+Name));
}
UAnimSequence* LoadClip(FName Name)
{
    const TCHAR* Root=Name==TEXT("Move")?RunningRoot:AnimationRoot;
    return LoadObject<UAnimSequence>(nullptr,*(FString(Root)+TEXT("AS_Cragstoat_")+Name.ToString()));
}
USoundBase* LoadSound(FName Name)
{
    return LoadObject<USoundBase>(nullptr,*(FString(AudioRoot)+TEXT("S_Cragstoat_")+Name.ToString()));
}
bool FiniteTransform(const FTransform& T)
{
    const FQuat Q=T.GetRotation();
    return !T.ContainsNaN()&&FMath::IsFinite(Q.SizeSquared())&&Q.SizeSquared()>.000001;
}
bool FinitePose(const FCompactPose& Pose)
{
    for(auto I:Pose.ForEachBoneIndex())if(!FiniteTransform(Pose[I]))return false;
    return true;
}
using FCragWorldPose=TArray<FTransform,TInlineAllocator<64>>;
bool ComponentPose(const FCompactPose& Pose,FCragWorldPose& World)
{
    World.SetNum(Pose.GetNumBones());
    for(auto I:Pose.ForEachBoneIndex()){
        if(!FiniteTransform(Pose[I]))return false;
        World[I.GetInt()]=Pose[I];const auto P=Pose.GetParentBoneIndex(I);
        if(P.GetInt()!=INDEX_NONE)World[I.GetInt()]=World[I.GetInt()]*World[P.GetInt()];
        if(!FiniteTransform(World[I.GetInt()]))return false;
    }
    return true;
}
struct FCragLeg { const TCHAR* Upper; const TCHAR* Lower; const TCHAR* Ankle; const TCHAR* Paw; };
// Exact accepted 33-bone anatomy from sage-keymotion_r004/controls.json.
const FCragLeg Legs[]={
    {TEXT("Front_Left_00"),TEXT("Front_Left_01"),TEXT("Front_Left_02"),TEXT("Front_Left_03")},
    {TEXT("Front_Right_00"),TEXT("Front_Right_01"),TEXT("Front_Right_02"),TEXT("Front_Right_03")},
    {TEXT("Rear_Left_00"),TEXT("Rear_Left_01"),TEXT("Rear_Left_02"),TEXT("Rear_Left_03")},
    {TEXT("Rear_Right_00"),TEXT("Rear_Right_01"),TEXT("Rear_Right_02"),TEXT("Rear_Right_03")}};

// Baseline mode raises only below-neutral ankles after a local crossfade.
// Recoil mode preserves each pre-overlay ankle/paw world transform, including
// the Move swing trajectory. No borrowed sole constants or whole-body lift.
enum class ECragFeetMode { NeutralGround, PreserveHitTargets, BlendEndpointTargets };
bool SolveFeet(FCompactPose& Pose,const FCragWorldPose& Targets,ECragFeetMode Mode,
    int& Corrected,float& Maximum)
{
    const bool PreserveTargets=Mode!=ECragFeetMode::NeutralGround;
    const bool UseHitSource=Mode==ECragFeetMode::PreserveHitTargets;
    const TCHAR* ModeName=UseHitSource?TEXT("hit-preserve"):
        Mode==ECragFeetMode::BlendEndpointTargets?TEXT("blend-endpoints"):TEXT("neutral-ground");
    FCragWorldPose World;if(!ComponentPose(Pose,World)||Targets.Num()!=World.Num())return false;
    const auto& Bones=Pose.GetBoneContainer();
    const auto Index=[&](const TCHAR* Name){
        const int MeshIndex=Bones.GetReferenceSkeleton().FindBoneIndex(Name);
        return MeshIndex<0?FCompactPoseBoneIndex(INDEX_NONE):Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
    };
    for(const FCragLeg& Leg:Legs){
        const auto U=Index(Leg.Upper),L=Index(Leg.Lower),A=Index(Leg.Ankle),Paw=Index(Leg.Paw);
        if(U.GetInt()<0||L.GetInt()<0||A.GetInt()<0||Paw.GetInt()<0)return false;
        if(Pose.GetParentBoneIndex(L)!=U||Pose.GetParentBoneIndex(A)!=L||Pose.GetParentBoneIndex(Paw)!=A)return false;
        const FTransform BU=World[U.GetInt()],BL=World[L.GetInt()],BA=World[A.GetInt()];
        FTransform GoalAnkle=PreserveTargets?Targets[A.GetInt()]:BA;
        if(!PreserveTargets)GoalAnkle.SetLocation(FVector(BA.GetLocation().X,BA.GetLocation().Y,
            FMath::Max(BA.GetLocation().Z,Targets[A.GetInt()].GetLocation().Z)));
        const FVector Hip=BU.GetLocation(),Knee=BL.GetLocation(),Foot=BA.GetLocation(),Goal=GoalAnkle.GetLocation();
        const double Correction=FVector::Distance(Foot,Goal);
        const bool RotationChanged=!BA.GetRotation().Equals(GoalAnkle.GetRotation(),.000001);
        const bool EndpointPawChanged=Mode==ECragFeetMode::BlendEndpointTargets&&
            (!World[Paw.GetInt()].GetLocation().Equals(Targets[Paw.GetInt()].GetLocation(),.000001)||
             !World[Paw.GetInt()].GetRotation().Equals(Targets[Paw.GetInt()].GetRotation(),.000001));
        if(Correction<.000001&&!RotationChanged&&!EndpointPawChanged)continue;
        // Endpoint mode keeps the actual locally blended limb lengths, bend
        // plane and source orientations. Only ankle/paw goals are interpolated.
        // Hit mode retains its established before-overlay source geometry.
        const FTransform SourceUpper=UseHitSource?Targets[U.GetInt()]:BU;
        const FTransform SourceLower=UseHitSource?Targets[L.GetInt()]:BL;
        const FTransform SourceAnkle=UseHitSource?Targets[A.GetInt()]:BA;
        const FVector SourceHip=SourceUpper.GetLocation(),SourceKnee=SourceLower.GetLocation(),SourceFoot=SourceAnkle.GetLocation();
        const double UL=FVector::Distance(SourceHip,SourceKnee),LL=FVector::Distance(SourceKnee,SourceFoot),D=FVector::Distance(Hip,Goal);
        if(!FMath::IsFinite(UL)||!FMath::IsFinite(LL)||!FMath::IsFinite(D)||UL<=.001||LL<=.001||D<=.001)return false;
        const FVector Axis=(Goal-Hip)/D;
        const double Low=FMath::Abs(UL-LL)+.0001,High=UL+LL-.0001;
        if(Low>High)return false;
        constexpr double ReachTolerance=.0001; // cm; numerical allowance, never a shortened target.
        if(D<Low-ReachTolerance||D>High+ReachTolerance){
            UE_LOG(LogTemp,Warning,TEXT("WC_CRAGSTOAT_POSE_REJECT leg=%s mode=%s reason=unreachable d=%.9f low=%.9f high=%.9f tolerance=%.9f"),
                Leg.Ankle,ModeName,D,Low,High,ReachTolerance);
            return false;
        }
        const double Reach=FMath::Clamp(D,Low,High);
        FVector Pole=SourceKnee-SourceHip;Pole-=Axis*FVector::DotProduct(Pole,Axis);
        if(!Pole.Normalize()){
            Pole=Targets[L.GetInt()].GetLocation()-Targets[U.GetInt()].GetLocation();
            Pole-=Axis*FVector::DotProduct(Pole,Axis);
            if(!Pole.Normalize()){
                Pole=FVector::CrossProduct(Axis,FVector::UpVector);
                if(!Pole.Normalize()){Pole=FVector::CrossProduct(Axis,FVector::RightVector);if(!Pole.Normalize())return false;}
            }
        }
        const double Along=(UL*UL+Reach*Reach-LL*LL)/(2*Reach);
        const FVector NewKnee=Hip+Axis*Along+Pole*FMath::Sqrt(FMath::Max(0.,UL*UL-Along*Along));
        const FVector NewFoot=Hip+Axis*Reach;
        FTransform Upper=BU,Lower=BL,Ankle=GoalAnkle;
        Upper.SetRotation((FQuat::FindBetweenNormals((SourceKnee-SourceHip).GetSafeNormal(),(NewKnee-Hip).GetSafeNormal())*SourceUpper.GetRotation()).GetNormalized());
        Lower.SetRotation((FQuat::FindBetweenNormals((SourceFoot-SourceKnee).GetSafeNormal(),(NewFoot-NewKnee).GetSafeNormal())*SourceLower.GetRotation()).GetNormalized());
        Lower.SetLocation(NewKnee);Ankle.SetLocation(NewFoot);
        if(!FiniteTransform(Upper)||!FiniteTransform(Lower)||!FiniteTransform(Ankle))return false;
        const auto Parent=Pose.GetParentBoneIndex(U);
        Pose[U]=Parent.GetInt()<0?Upper:Upper.GetRelativeTransform(World[Parent.GetInt()]);
        Pose[L]=Lower.GetRelativeTransform(Upper);Pose[A]=Ankle.GetRelativeTransform(Lower);
        if(PreserveTargets){
            FTransform PawWorld=Targets[Paw.GetInt()];
            PawWorld.AddToTranslation(NewFoot-Goal);Pose[Paw]=PawWorld.GetRelativeTransform(Ankle);
        }
        ++Corrected;Maximum=FMath::Max(Maximum,float(FVector::Distance(Foot,NewFoot)));
        // Rebuild before the next chain so its parent is the actual solved pose.
        if(!ComponentPose(Pose,World))return false;
        const double AnkleError=FVector::Distance(World[A.GetInt()].GetLocation(),Goal);
        const double PawError=PreserveTargets?FVector::Distance(World[Paw.GetInt()].GetLocation(),Targets[Paw.GetInt()].GetLocation()):0.;
        if(!FMath::IsFinite(AnkleError)||!FMath::IsFinite(PawError)||AnkleError>ReachTolerance||PawError>ReachTolerance){
            UE_LOG(LogTemp,Warning,TEXT("WC_CRAGSTOAT_POSE_REJECT leg=%s mode=%s reason=fk-target-residual ankle=%.9f paw=%.9f tolerance=%.9f"),
                Leg.Ankle,ModeName,AnkleError,PawError,ReachTolerance);
            return false;
        }
    }
    return true;
}

struct FCragstoatProxy : FAnimInstanceProxy
{
    UAnimSequence* Current=nullptr;UAnimSequence* Previous=nullptr;UAnimSequence* HitReaction=nullptr;UAnimSequence* GroundingReference=nullptr;
    float Seconds=0,PreviousSeconds=0,Alpha=1,HitReactionSeconds=0,MaximumCorrection=0;
    int Corrected=0;bool Valid=true;
    explicit FCragstoatProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
    virtual void PreUpdate(UAnimInstance* Instance,float Delta) override {
        FAnimInstanceProxy::PreUpdate(Instance,Delta);const auto* A=CastChecked<UWCCragstoatAnimInstance>(Instance);
        Current=A->Current;Previous=A->Previous;HitReaction=A->HitReaction;GroundingReference=A->GroundingReference;
        Seconds=A->Seconds;PreviousSeconds=A->PreviousSeconds;Alpha=A->Alpha;HitReactionSeconds=A->HitReactionSeconds;
    }
    virtual bool Evaluate(FPoseContext& Output) override {
        Valid=UWCCragstoatAnimInstance::BuildPose(Output,Current,Seconds,Previous,PreviousSeconds,Alpha,
            HitReaction,HitReactionSeconds,GroundingReference,&Corrected,&MaximumCorrection);return true;
    }
    virtual void PostEvaluate(UAnimInstance* Instance) override {
        FAnimInstanceProxy::PostEvaluate(Instance);auto* A=CastChecked<UWCCragstoatAnimInstance>(Instance);
        A->PoseValid=Valid;A->CorrectedLegs=Corrected;A->MaximumFootCorrection=MaximumCorrection;
    }
};
bool Loops(FName Name){return Name==TEXT("Idle")||Name==TEXT("Move")||Name==TEXT("Victory");}
float ClipTime(float Seconds,UAnimSequence* Clip,bool Loop=false)
{
    if(!Clip||!FMath::IsFinite(Seconds)||Clip->GetPlayLength()<=0)return 0;
    return Loop?FMath::Fmod(FMath::Max(0.f,Seconds),Clip->GetPlayLength()):FMath::Clamp(Seconds,0.f,Clip->GetPlayLength());
}
}

bool UWCCragstoatAnimInstance::BuildPose(FPoseContext& Output,UAnimSequence* Current,float Seconds,
    UAnimSequence* Previous,float PreviousSeconds,float Alpha,UAnimSequence* HitReaction,
    float HitReactionSeconds,UAnimSequence* GroundingReference,int* CorrectedLegs,float* MaximumFootCorrection)
{
    int Corrected=0;float Maximum=0;Output.ResetToRefPose();
    if(CorrectedLegs)*CorrectedLegs=0;if(MaximumFootCorrection)*MaximumFootCorrection=0;
    const auto Fail=[&](){Output.ResetToRefPose();return false;};
    if(!Current||!GroundingReference||!FMath::IsFinite(Seconds)||!FMath::IsFinite(PreviousSeconds)||
        !FMath::IsFinite(Alpha)||!FMath::IsFinite(HitReactionSeconds))return Fail();
    if(Current->GetSkeleton()!=GroundingReference->GetSkeleton()||
        (Previous&&Previous->GetSkeleton()!=Current->GetSkeleton())||
        (HitReaction&&HitReaction->GetSkeleton()!=Current->GetSkeleton()))return Fail();
    FAnimationPoseData Data(Output);Current->GetAnimationPose(Data,FAnimExtractContext(ClipTime(Seconds,Current),false));
    if(!FinitePose(Output.Pose))return Fail();
    Alpha=FMath::Clamp(Alpha,0.f,1.f);
    FCragWorldPose CurrentEndpoint,PreviousEndpoint;
    const bool CorrectBlendEndpoints=Previous&&Alpha>0.f&&Alpha<1.f;
    if(CorrectBlendEndpoints&&!ComponentPose(Output.Pose,CurrentEndpoint))return Fail();
    if(Previous&&Alpha<1){
        FPoseContext Old(Output);Old.ResetToRefPose();FAnimationPoseData OldData(Old);
        Previous->GetAnimationPose(OldData,FAnimExtractContext(ClipTime(PreviousSeconds,Previous),false));
        if(!FinitePose(Old.Pose))return Fail();
        if(CorrectBlendEndpoints&&!ComponentPose(Old.Pose,PreviousEndpoint))return Fail();
        FAnimationRuntime::BlendTwoPosesTogetherInPlace(Data,OldData,Alpha);
    }
    if(CorrectBlendEndpoints){
        FCragWorldPose Targets;
        if(!ComponentPose(Output.Pose,Targets)||Targets.Num()!=CurrentEndpoint.Num()||Targets.Num()!=PreviousEndpoint.Num())return Fail();
        const auto& Bones=Output.Pose.GetBoneContainer();
        for(const FCragLeg& Leg:Legs)for(const TCHAR* Name:{Leg.Ankle,Leg.Paw}){
            const int MeshIndex=Bones.GetReferenceSkeleton().FindBoneIndex(Name);
            if(MeshIndex<0)return Fail();
            const auto Index=Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
            if(Index.GetInt()<0)return Fail();
            const auto& Old=PreviousEndpoint[Index.GetInt()];const auto& Now=CurrentEndpoint[Index.GetInt()];
            FTransform Goal=Targets[Index.GetInt()];
            Goal.SetLocation(FMath::Lerp(Old.GetLocation(),Now.GetLocation(),Alpha));
            Goal.SetRotation(FQuat::Slerp(Old.GetRotation(),Now.GetRotation(),Alpha).GetNormalized());
            Goal.SetScale3D(FMath::Lerp(Old.GetScale3D(),Now.GetScale3D(),Alpha));
            if(!FiniteTransform(Goal))return Fail();Targets[Index.GetInt()]=Goal;
        }
        if(!SolveFeet(Output.Pose,Targets,ECragFeetMode::BlendEndpointTargets,Corrected,Maximum))return Fail();
    }
    FPoseContext Ground(Output);Ground.ResetToRefPose();FAnimationPoseData GroundData(Ground);
    GroundingReference->GetAnimationPose(GroundData,FAnimExtractContext(0.f,false));
    FCragWorldPose Neutral;if(!ComponentPose(Ground.Pose,Neutral)||!SolveFeet(Output.Pose,Neutral,ECragFeetMode::NeutralGround,Corrected,Maximum))return Fail();
    if(HitReaction){
        FCragWorldPose Before;if(!ComponentPose(Output.Pose,Before))return Fail();
        FPoseContext Reaction(Output),HitNeutral(Output);Reaction.ResetToRefPose();HitNeutral.ResetToRefPose();
        FAnimationPoseData ReactionData(Reaction),HitNeutralData(HitNeutral);
        HitReaction->GetAnimationPose(ReactionData,FAnimExtractContext(ClipTime(HitReactionSeconds,HitReaction),false));
        HitReaction->GetAnimationPose(HitNeutralData,FAnimExtractContext(0.f,false));
        if(!FinitePose(Reaction.Pose)||!FinitePose(HitNeutral.Pose))return Fail();
        FAnimationRuntime::ConvertPoseToAdditive(Reaction.Pose,HitNeutral.Pose);
        Reaction.Curve.Empty();Reaction.CustomAttributes.Empty();
        FAnimationRuntime::AccumulateAdditivePose(Data,ReactionData,1.f,AAT_LocalSpaceBase);
        if(!SolveFeet(Output.Pose,Before,ECragFeetMode::PreserveHitTargets,Corrected,Maximum)||
           !SolveFeet(Output.Pose,Neutral,ECragFeetMode::NeutralGround,Corrected,Maximum))return Fail();
    }
    if(!FinitePose(Output.Pose))return Fail();Output.Pose.NormalizeRotations();
    if(CorrectedLegs)*CorrectedLegs=Corrected;if(MaximumFootCorrection)*MaximumFootCorrection=Maximum;
    return true;
}
FAnimInstanceProxy* UWCCragstoatAnimInstance::CreateAnimInstanceProxy(){return new FCragstoatProxy(this);}
void UWCCragstoatAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}
bool UWCCragstoatPresentationComponent::CandidateEnabled()
{
    return FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatCandidate"));
}
bool UWCCragstoatPresentationComponent::ValidateAssets(FString& Error)
{
    auto* Mesh=LoadAccepted<USkeletalMesh>(TEXT("SK_Cragstoat"));
    if(!Mesh||!Mesh->GetSkeleton()||Mesh->GetRefSkeleton().GetNum()!=33){Error=TEXT("Cragstoat accepted33bone mesh/skeleton missing");return false;}
    for(const auto& Leg:Legs)for(const TCHAR* Name:{Leg.Upper,Leg.Lower,Leg.Ankle,Leg.Paw})
        if(Mesh->GetRefSkeleton().FindBoneIndex(Name)<0){Error=FString(TEXT("Cragstoat measured leg bone missing: "))+Name;return false;}
    if(!LoadAccepted<UMaterialInterface>(TEXT("M_CragstoatSage"))){Error=TEXT("Cragstoat accepted sage material missing");return false;}
    for(int I=0;I<UE_ARRAY_COUNT(Names);++I){
        auto* Clip=LoadClip(Names[I]);
        if(!Clip||Clip->GetSkeleton()!=Mesh->GetSkeleton()||!FMath::IsFinite(Clip->GetPlayLength())||
            FMath::Abs(Clip->GetPlayLength()-Lengths[I])>.001){
            Error=TEXT("Cragstoat clip missing, skeleton mismatch or authored duration mismatch: ")+Names[I].ToString();return false;
        }
    }
    for(FName Name:SoundNames)if(!LoadSound(Name)){
        Error=TEXT("Cragstoat candidate sound missing: ")+Name.ToString();return false;
    }
    return true;
}
bool UWCCragstoatPresentationComponent::InitializeCandidate(FString& Error)
{
    if(!CandidateEnabled()){Error=TEXT("Cragstoat production candidate requires explicit opt-in flag");return false;}
    if(!ValidateAssets(Error))return false;
    Skeletal=NewObject<USkeletalMeshComponent>(GetOwner());GetOwner()->AddInstanceComponent(Skeletal);
    Skeletal->SetupAttachment(this);Skeletal->SetSkeletalMeshAsset(LoadAccepted<USkeletalMesh>(TEXT("SK_Cragstoat")));
    Skeletal->SetMaterial(0,LoadAccepted<UMaterialInterface>(TEXT("M_CragstoatSage")));
    // Candidate scale1/+X forward. The owning presentation component carries
    // the board/clearance offset; applying it again here would float the mesh.
    Skeletal->SetRelativeLocation(FVector::ZeroVector);
    Skeletal->SetCollisionEnabled(ECollisionEnabled::NoCollision);Skeletal->SetCastShadow(false);
    Skeletal->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Skeletal->SetAnimationMode(EAnimationMode::AnimationBlueprint);Skeletal->SetAnimInstanceClass(UWCCragstoatAnimInstance::StaticClass());
    Skeletal->RegisterComponent();for(FName Name:Names)Clips.Add(Name,LoadClip(Name));
    for(FName Name:SoundNames)Sounds.Add(Name,LoadSound(Name));
    static TWeakObjectPtr<USoundConcurrency> Shared;
    if(!Shared.IsValid()){Shared=NewObject<USoundConcurrency>();Shared->Concurrency.MaxCount=12;}
    Concurrency=Shared.Get();Attenuation=NewObject<USoundAttenuation>(this);
    Attenuation->Attenuation.bAttenuate=true;Attenuation->Attenuation.bSpatialize=true;
    Attenuation->Attenuation.AttenuationShapeExtents=FVector(1400);Attenuation->Attenuation.FalloffDistance=3600;
    SetPose(TEXT("Idle"),0,0,1);return true;
}
void UWCCragstoatPresentationComponent::PlayCue(FName Name,FVector Location,const FWCBellbackFrame& F)
{
    if(!F.AllowSound||F.Paused||!Sounds.Contains(Name)||Location.ContainsNaN())return;
    const bool Step=Name.ToString().StartsWith(TEXT("Footstep"));
    const float Gain=Step?.055f:Name==TEXT("Active")?.10f:Name==TEXT("Defeat")||Name==TEXT("Victory")?.16f:.12f;
    UAudioComponent* Audio=UGameplayStatics::SpawnSoundAtLocation(this,Sounds.FindChecked(Name),Location,
        FRotator::ZeroRotator,Gain,1.f,0.f,Attenuation,Concurrency,true);
    if(!Audio)return;
    LiveCues.RemoveAll([](const TWeakObjectPtr<UAudioComponent>& A){return !A.IsValid();});
    LiveCues.Add(Audio);++SoundsPlayed;
    if(Name==TEXT("Active")){ActiveTell=Audio;}
    UE_LOG(LogTemp,Display,TEXT("WC_CRAGSTOAT_SOUND unit=%llu cue=%s tick=%d"),F.Id,*Name.ToString(),F.Combat?F.Combat->CurrentTick():-1);
}
void UWCCragstoatPresentationComponent::StopActiveTell()
{
    if(IsValid(ActiveTell))ActiveTell->FadeOut(.03f,0.f);
    ActiveTell=nullptr;ActiveTellAction=0;
}
void UWCCragstoatPresentationComponent::StopAllCues()
{
    for(const auto& A:LiveCues)if(A.IsValid())A->Stop();
    LiveCues.Reset();ActiveTell=nullptr;ActiveTellAction=0;
}
void UWCCragstoatPresentationComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    StopAllCues();Super::EndPlay(Reason);
}
FVector UWCCragstoatPresentationComponent::CueLocation(FName Bone) const
{
    return Skeletal?Skeletal->GetSocketLocation(Bone):GetComponentLocation();
}
bool UWCCragstoatPresentationComponent::IsDefeatFinished() const
{
    UAnimSequence* Clip=Clips.FindRef(TEXT("Defeat"));return Clip&&CurrentClip==TEXT("Defeat")&&CurrentSeconds>=Clip->GetPlayLength()-.01f;
}
float UWCCragstoatPresentationComponent::ClipDuration(FName Name) const
{
    UAnimSequence* Clip=Clips.FindRef(Name);return Clip?Clip->GetPlayLength():0;
}
void UWCCragstoatPresentationComponent::SetPose(FName Name,float Seconds,double Clock,float Rate,uint64 Action)
{
    if(!Skeletal||!Clips.Contains(Name)||!FMath::IsFinite(Seconds)||!FMath::IsFinite(Clock)||!FMath::IsFinite(Rate))return;
    const float Dt=FMath::Max(0.f,float(Clock-LastPoseClock));LastPoseClock=Clock;
    if(CurrentClip!=Name||CurrentAction!=Action){
        OldClip=CurrentClip;OldSeconds=CurrentSeconds;OldRate=CurrentRate;
        CurrentClip=Name;CurrentAction=Action;BlendStarted=Clock;Seen.Add(Name);
    }else if(UAnimSequence* Old=Clips.FindRef(OldClip))OldSeconds=ClipTime(OldSeconds+Dt*OldRate,Old,Loops(OldClip));
    CurrentSeconds=ClipTime(Seconds,Clips.FindChecked(Name));CurrentRate=Rate;
    if(auto* A=Cast<UWCCragstoatAnimInstance>(Skeletal->GetAnimInstance())){
        A->Current=Clips.FindChecked(Name);A->Seconds=CurrentSeconds;
        A->Previous=Clips.FindRef(OldClip);A->PreviousSeconds=OldSeconds;
        A->Alpha=A->Previous?FMath::Clamp(float((Clock-BlendStarted)/CrossfadeSeconds),0.f,1.f):1.f;
        A->HitReaction=HitOverlayActive?Clips.FindChecked(TEXT("Hit")):nullptr;A->HitReactionSeconds=HitOverlayAge;
        A->GroundingReference=Clips.FindChecked(TEXT("Idle"));
    }
}
void UWCCragstoatPresentationComponent::Present(const FWCBellbackFrame& F)
{
    if(!Skeletal||!FMath::IsFinite(F.Clock)||F.TickMs<=0)return;
    if(Generation!=F.Generation||F.Clock<LastClock){
        StopAllCues();AttackTells.Reset();ChargeTells.Reset();SoundsPlayed=AttackVariant=ImpactVariant=HitVariant=0;
        Generation=F.Generation;EventCursor=0;HasLocation=false;WalkPhase=0;
        TerminalClip=TurnClip=CurrentClip=OldClip=NAME_None;CurrentAction=0;
        TerminalStarted=-1;HitStarted=TurnStarted=-100;LastClock=LastPoseClock=BlendStarted=F.Clock;
        CurrentSeconds=OldSeconds=CurrentRate=OldRate=LastMoveRate=0;ReviewEffectSerial=-1;
        // FacingStep Forward is row+1, which projects to world-Y. This
        // source faces +X, unlike the older Bellback/Silkmother source basis.
        MeshYaw=LastFacingYaw=F.Facing*90-90;Seen.Reset();
    }
    const float Dt=F.Paused?0.f:FMath::Max(0.f,float(F.Clock-LastClock));LastClock=F.Clock;
    const FVector Location=GetOwner()->GetActorLocation();if(Location.ContainsNaN())return;
    const FVector Travel=HasLocation?Location-PreviousLocation:FVector::ZeroVector;PreviousLocation=Location;HasLocation=true;
    LiveCues.RemoveAll([](const TWeakObjectPtr<UAudioComponent>& A){return !A.IsValid();});
    for(const auto& A:LiveCues)if(A.IsValid())A->SetPaused(F.Paused||!F.AllowSound);
    const auto* U=F.Unit;
    const bool ChargeWindup=U&&U->health>0&&U->state==wc::ActionState::CastWindup&&U->ability.mechanic==wc::AbilityMechanic::MomentumCharge;
    if(!ChargeWindup||U->actionId!=ActiveTellAction)StopActiveTell();
    if(U&&U->health>0&&U->state==wc::ActionState::AttackWindup&&!AttackTells.Contains(U->actionId)){
        AttackTells.Add(U->actionId);PlayCue(SoundNames[4+(AttackVariant++)%2],CueLocation(TEXT("Muzzle")),F);
    }
    if(ChargeWindup&&!ChargeTells.Contains(U->actionId)){
        ChargeTells.Add(U->actionId);ActiveTellAction=U->actionId;PlayCue(TEXT("Active"),CueLocation(TEXT("Chest")),F);
    }
    double DefeatClock=-1;
    if(F.Combat){
        const auto& Events=F.Combat->Events();if(EventCursor>Events.size())EventCursor=Events.size();
        for(;EventCursor<Events.size();++EventCursor){const auto& E=Events[EventCursor];
            if(E.effect==wc::Effect::Damage&&E.target==F.Id&&E.healthLoss>0){
                HitStarted=E.tick*F.TickMs/1000.;DefeatClock=HitStarted;
                PlayCue(SoundNames[9+(HitVariant++)%2],CueLocation(TEXT("Chest")),F);
            }
            if(E.effect==wc::Effect::Damage&&E.source==F.Id&&E.healthLoss>0){
                const FVector Impact((E.cell.column-3.5)*200,(3.5-E.cell.row)*200,65);
                PlayCue(SoundNames[6+(ImpactVariant++)%3],Impact,F);
            }
            // MoveUnit's authoritative Dash has resolved=0; changed cells,
            // correct mechanic and source/target identify the actual charge.
            if(E.effect==wc::Effect::Dash&&E.mechanic==wc::AbilityMechanic::MomentumCharge&&
                E.source==F.Id&&E.target==F.Id&&!(E.origin==E.cell)){
                PlayCue(TEXT("Dash"),CueLocation(TEXT("Chest")),F);
            }
        }
    }
    if(U&&U->health<=0&&TerminalClip!=TEXT("Defeat")){
        TerminalClip=TEXT("Defeat");TerminalStarted=DefeatClock>=0?DefeatClock:F.Clock;StopActiveTell();
        PlayCue(TEXT("Defeat"),CueLocation(TEXT("Head")),F);
    }
    else if(U&&U->health>0&&F.Combat&&F.Combat->Result().complete&&F.Combat->Result().winner==F.Side&&TerminalClip.IsNone()){
        TerminalClip=TEXT("Victory");TerminalStarted=F.Clock;StopActiveTell();PlayCue(TEXT("Victory"),CueLocation(TEXT("Head")),F);
    }
    // Explicit review trigger is cosmetic; it never enters Combat::Events.
    if(!F.ReviewClip.IsNone()&&F.ReviewEffectSerial>=0&&F.ReviewEffectSerial!=ReviewEffectSerial){
        ReviewEffectSerial=F.ReviewEffectSerial;HitStarted=F.Clock;
    }
    const double Age=F.Clock-HitStarted;HitOverlayActive=TerminalClip.IsNone()&&(!U||U->health>0)&&Age>=0&&Age<.4;
    HitOverlayAge=HitOverlayActive?float(Age):0;
    const float FacingYaw=F.Facing*90-90;
    if(!F.ReviewClip.IsNone()){
        MeshYaw=FacingYaw;SetWorldRotation(FRotator(0,MeshYaw,0));
        SetPose(F.ReviewClip,F.ReviewSeconds,F.Clock,0);return;
    }
    if(!U&&FMath::Abs(FMath::FindDeltaAngleDegrees(LastFacingYaw,FacingYaw))>.01){
        TurnClip=FMath::FindDeltaAngleDegrees(LastFacingYaw,FacingYaw)>0?TEXT("TurnRight"):TEXT("TurnLeft");TurnStarted=F.Clock;
    }
    LastFacingYaw=FacingYaw;
    LastMoveRate=0;
    FName Name=TEXT("Idle");float Seconds=ClipTime(float(F.Clock),Clips.FindChecked(Name),true),Rate=1;uint64 Action=0;
    if(!TerminalClip.IsNone()){Name=TerminalClip;Seconds=float(F.Clock-TerminalStarted);Rate=1;}
    else if(U&&U->state==wc::ActionState::Stunned){Seconds=0;Rate=0;}
    else if(U&&(U->state==wc::ActionState::CastWindup||U->state==wc::ActionState::CastRecovery)){
        Name=TEXT("Active");Seconds=ActiveRelease+float(F.Clock-U->releaseTick*F.TickMs/1000.);Action=U->actionId;
    }
    else if(U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::AttackRecovery)){
        Name=TEXT("Attack");Seconds=AttackRelease+float(F.Clock-U->releaseTick*F.TickMs/1000.);Action=U->actionId;
    }
    else if(U&&U->state==wc::ActionState::Moving){
        Name=TEXT("Move");
        if(Dt>0){
            const float Before=WalkPhase,After=Before+Travel.Size2D()/TravelPerCycle;
            const float Offsets[]={0.f,.5f,.5f,0.f}; // FL,FR,RL,RR: saved diagonal-pair touchdowns.
            for(int I=0;I<4;++I)if(FMath::FloorToInt(After+Offsets[I])>FMath::FloorToInt(Before+Offsets[I]))
                PlayCue(SoundNames[I],CueLocation(Legs[I].Paw),F);
            // Render stalls emit at most one recent contact per paw; old audio
            // is not replayed in an unbounded catch-up burst.
            WalkPhase=FMath::Fmod(After,1.f);
        }
        Seconds=WalkPhase*Clips.FindChecked(Name)->GetPlayLength();
        LastMoveRate=Dt>0?Travel.Size2D()/TravelPerCycle*Clips.FindChecked(Name)->GetPlayLength()/Dt:0;Rate=LastMoveRate;
    }
    else if(!U&&!TurnClip.IsNone()&&F.Clock-TurnStarted<Clips.FindChecked(TurnClip)->GetPlayLength()){
        Name=TurnClip;Seconds=float(F.Clock-TurnStarted);
    }
    const bool HoldYaw=!TerminalClip.IsNone()||(U&&U->state==wc::ActionState::Stunned);
    float Desired=HoldYaw?MeshYaw:U&&U->state==wc::ActionState::Moving&&Travel.SizeSquared2D()>.001?Travel.Rotation().Yaw:FacingYaw;
    const bool Casting=U&&(U->state==wc::ActionState::CastWindup||U->state==wc::ActionState::CastRecovery);
    const bool Attacking=U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::AttackRecovery);
    if(!HoldYaw&&U&&(Casting||Attacking)){
        wc::Cell Aim=U->cell;bool HasAim=false;
        if(Casting){Aim=U->abilityAim;HasAim=Aim.column>=0&&Aim.row>=0;}
        else if(F.Combat&&U->target>=0&&U->target<int(F.Combat->Units().size())){
            const auto& Target=F.Combat->Units()[U->target];
            if(Target.health>0){Aim=Target.cell;HasAim=true;}
        }
        const FVector Direction(Aim.column-U->cell.column,U->cell.row-Aim.row,0);
        if(HasAim&&Direction.SizeSquared2D()>0)Desired=Direction.Rotation().Yaw;
    }
    float TurnRate=420;
    if(!HoldYaw&&U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::CastWindup)){
        const double Remaining=U->releaseTick*F.TickMs/1000.-F.Clock;
        if(Remaining>0)TurnRate=FMath::Max(TurnRate,float(FMath::Abs(FMath::FindDeltaAngleDegrees(MeshYaw,Desired))/Remaining));
    }
    MeshYaw=FMath::FixedTurn(MeshYaw,Desired,Dt*TurnRate);SetWorldRotation(FRotator(0,MeshYaw,0));
    SetPose(Name,Seconds,F.Clock,Rate,Action);
}
