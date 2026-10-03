#include "WCSilkmotherPresentation.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundConcurrency.h"
#include "Sound/SoundAttenuation.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include <algorithm>

namespace
{
constexpr float SourceScale=.6666997156f;
constexpr float TravelPerCycle=28.f/.75f*SourceScale;
const TCHAR* Root=TEXT("/Game/WonderChess/VNext/Characters/Silkmother_r003/");
const TCHAR* MotionRevisionRoot=TEXT("/Game/WonderChess/VNext/Characters/SilkmotherMotionRevision20260930_r003/");
bool MotionRevisionEnabled(){return FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherMotionRevision20260930"));}
const FName Names[]={TEXT("Idle"),TEXT("Move"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory"),TEXT("TurnLeft"),TEXT("TurnRight")};
const FName SoundNames[]={TEXT("Footstep1"),TEXT("Footstep2"),TEXT("Footstep3"),TEXT("Shot"),TEXT("Weave"),TEXT("Catch"),TEXT("Release"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory")};
template<class T>T* Load(const FString& Relative){
    const bool Revised=MotionRevisionEnabled()&&(Relative==TEXT("Animations/AS_Silkmother_Attack")||Relative==TEXT("Animations/AS_Silkmother_Hit"));
    return LoadObject<T>(nullptr,*(FString(Revised?MotionRevisionRoot:Root)+Relative));
}
using FSilkWorldPose=TArray<FTransform,TInlineAllocator<96>>;
void ComponentPose(const FCompactPose& Pose,FSilkWorldPose& World){
    World.SetNum(Pose.GetNumBones());
    for(auto I:Pose.ForEachBoneIndex()){
        World[I.GetInt()]=Pose[I];const auto P=Pose.GetParentBoneIndex(I);
        if(P.GetInt()!=INDEX_NONE)World[I.GetInt()]=World[I.GetInt()]*World[P.GetInt()];
    }
}
void PreserveRecoilFootTrajectories(FCompactPose& Pose,const FSilkWorldPose& Base){
    // Measured Silkmother bone-map, not Bellback's skeleton or sole constants.
    // Keep the current gait's ankle targets, including swing arcs, while the
    // recoiling body bends the eight walking legs toward those targets.
    const TCHAR* Chains[][3]={
        {TEXT("Bone_050"),TEXT("Bone_049"),TEXT("Bone_048")},
        {TEXT("Bone_032"),TEXT("Bone_031"),TEXT("Bone_030")},
        {TEXT("Bone_014"),TEXT("Bone_013"),TEXT("Bone_012")},
        {TEXT("Bone_038"),TEXT("Bone_037"),TEXT("Bone_036")},
        {TEXT("Bone_056"),TEXT("Bone_055"),TEXT("Bone_054")},
        {TEXT("Bone_026"),TEXT("Bone_025"),TEXT("Bone_024")},
        {TEXT("Bone_020"),TEXT("Bone_019"),TEXT("Bone_018")},
        {TEXT("Bone_044"),TEXT("Bone_043"),TEXT("Bone_042")}};
    FSilkWorldPose World;ComponentPose(Pose,World);const auto& Bones=Pose.GetBoneContainer();
    const auto Index=[&](const TCHAR* Name){return Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(Bones.GetReferenceSkeleton().FindBoneIndex(Name)));};
    for(const auto& Chain:Chains){
        const auto U=Index(Chain[0]),L=Index(Chain[1]),A=Index(Chain[2]);
        if(U.GetInt()<0||L.GetInt()<0||A.GetInt()<0)continue;
        const FTransform& BU=Base[U.GetInt()];const FTransform& BL=Base[L.GetInt()];const FTransform& BA=Base[A.GetInt()];
        const FVector Hip=World[U.GetInt()].GetLocation(),Goal=BA.GetLocation();
        const double UL=FVector::Distance(BU.GetLocation(),BL.GetLocation()),LL=FVector::Distance(BL.GetLocation(),Goal);
        const double D=FVector::Distance(Hip,Goal);if(UL<.001||LL<.001||D<.001)continue;
        const FVector Axis=(Goal-Hip)/D;
        const double Reach=FMath::Clamp(D,FMath::Abs(UL-LL)+.0001,UL+LL-.0001);
        FVector Pole=BL.GetLocation()-BU.GetLocation();Pole-=Axis*FVector::DotProduct(Pole,Axis);
        if(!Pole.Normalize())Pole=FVector::CrossProduct(Axis,FVector::UpVector).GetSafeNormal();
        const double Along=(UL*UL+Reach*Reach-LL*LL)/(2*Reach);
        const FVector Knee=Hip+Axis*Along+Pole*FMath::Sqrt(FMath::Max(0.,UL*UL-Along*Along));
        const FVector Foot=Hip+Axis*Reach;
        FTransform Upper=BU,Lower=BL,Ankle=BA;Upper.SetLocation(Hip);Lower.SetLocation(Knee);Ankle.SetLocation(Foot);
        Upper.SetRotation((FQuat::FindBetweenNormals((BL.GetLocation()-BU.GetLocation()).GetSafeNormal(),(Knee-Hip).GetSafeNormal())*BU.GetRotation()).GetNormalized());
        Lower.SetRotation((FQuat::FindBetweenNormals((Goal-BL.GetLocation()).GetSafeNormal(),(Foot-Knee).GetSafeNormal())*BL.GetRotation()).GetNormalized());
        const auto Parent=Pose.GetParentBoneIndex(U);
        Pose[U]=Parent.GetInt()<0?Upper:Upper.GetRelativeTransform(World[Parent.GetInt()]);
        Pose[L]=Lower.GetRelativeTransform(Upper);Pose[A]=Ankle.GetRelativeTransform(Lower);
    }
}
struct FSilkmotherProxy : FAnimInstanceProxy
{
    UAnimSequence* Current=nullptr;UAnimSequence* Previous=nullptr;UAnimSequence* HitReaction=nullptr;
    float Seconds=0,PreviousSeconds=0,Alpha=1;
    float HitReactionSeconds=0;
    explicit FSilkmotherProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
    virtual void PreUpdate(UAnimInstance* Instance,float Delta) override {
        FAnimInstanceProxy::PreUpdate(Instance,Delta);
        const auto* A=CastChecked<UWCSilkmotherAnimInstance>(Instance);
        Current=A->Current;Previous=A->Previous;Seconds=A->Seconds;PreviousSeconds=A->PreviousSeconds;Alpha=A->Alpha;
        HitReaction=A->HitReaction;HitReactionSeconds=A->HitReactionSeconds;
    }
    virtual bool Evaluate(FPoseContext& Output) override {
        Output.ResetToRefPose();if(!Current)return true;
        FAnimationPoseData Data(Output);Current->GetAnimationPose(Data,FAnimExtractContext(Seconds,false));
        if(Previous&&Alpha<1){
            FPoseContext Old(Output);Old.ResetToRefPose();FAnimationPoseData OldData(Old);
            Previous->GetAnimationPose(OldData,FAnimExtractContext(PreviousSeconds,false));
            FAnimationRuntime::BlendTwoPosesTogetherInPlace(Data,OldData,Alpha);
        }
        if(HitReaction){
            // Apply the latest damage reaction without changing the authoritative
            // attack/cast clock or the distance-driven walking phase.
            FSilkWorldPose BeforeRecoil;ComponentPose(Output.Pose,BeforeRecoil);
            FPoseContext Reaction(Output),Neutral(Output);
            Reaction.ResetToRefPose();Neutral.ResetToRefPose();
            FAnimationPoseData ReactionData(Reaction),NeutralData(Neutral);
            HitReaction->GetAnimationPose(ReactionData,FAnimExtractContext(HitReactionSeconds,false));
            HitReaction->GetAnimationPose(NeutralData,FAnimExtractContext(0.f,false));
            FAnimationRuntime::ConvertPoseToAdditive(Reaction.Pose,Neutral.Pose);
            Reaction.Curve.Empty();Reaction.CustomAttributes.Empty();
            FAnimationRuntime::AccumulateAdditivePose(Data,ReactionData,1.f,AAT_LocalSpaceBase);
            PreserveRecoilFootTrajectories(Output.Pose,BeforeRecoil);
        }
        Output.Pose.NormalizeRotations();return true;
    }
};
}
FAnimInstanceProxy* UWCSilkmotherAnimInstance::CreateAnimInstanceProxy(){return new FSilkmotherProxy(this);}
void UWCSilkmotherAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}
bool UWCSilkmotherPresentationComponent::ValidateAssets(FString& Error)
{
    auto* Mesh=Load<USkeletalMesh>(TEXT("SK_Silkmother"));
    if(!Mesh||!Mesh->GetSkeleton()){Error=TEXT("Silkmother mesh/skeleton missing");return false;}
    for(FName Name:Names)if(!Load<UAnimSequence>(TEXT("Animations/AS_Silkmother_")+Name.ToString())){
        Error=TEXT("Silkmother clip missing: ")+Name.ToString();return false;
    }
    if(Mesh->GetMaterials().IsEmpty()||!Mesh->GetMaterials()[0].MaterialInterface){Error=TEXT("Silkmother original material missing");return false;}
    for(FName Name:SoundNames)if(!Load<USoundBase>(TEXT("Audio/S_Silkmother_")+Name.ToString())){
        Error=TEXT("Silkmother sound missing: ")+Name.ToString();return false;
    }
    return true;
}
bool UWCSilkmotherPresentationComponent::InitializeCandidate(FString& Error)
{
    if(!ValidateAssets(Error))return false;
    Skeletal=NewObject<USkeletalMeshComponent>(GetOwner());GetOwner()->AddInstanceComponent(Skeletal);
    Skeletal->SetupAttachment(this);Skeletal->SetSkeletalMeshAsset(Load<USkeletalMesh>(TEXT("SK_Silkmother")));
    Skeletal->SetRelativeScale3D(FVector(SourceScale));
    Skeletal->SetRelativeLocation(FVector(-.0814386,5.4510549,.5000033));
    Skeletal->SetCollisionEnabled(ECollisionEnabled::NoCollision);Skeletal->SetCastShadow(false);
    Skeletal->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Skeletal->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    Skeletal->SetAnimInstanceClass(UWCSilkmotherAnimInstance::StaticClass());Skeletal->RegisterComponent();
    for(FName Name:Names)Clips.Add(Name,Load<UAnimSequence>(TEXT("Animations/AS_Silkmother_")+Name.ToString()));
    for(FName Name:SoundNames)Sounds.Add(Name,Load<USoundBase>(TEXT("Audio/S_Silkmother_")+Name.ToString()));
    static TWeakObjectPtr<USoundConcurrency> Shared;
    if(!Shared.IsValid()){Shared=NewObject<USoundConcurrency>();Shared->Concurrency.MaxCount=12;}
    Concurrency=Shared.Get();Attenuation=NewObject<USoundAttenuation>(this);
    Attenuation->Attenuation.bAttenuate=true;Attenuation->Attenuation.bSpatialize=true;
    Attenuation->Attenuation.AttenuationShapeExtents=FVector(1400);Attenuation->Attenuation.FalloffDistance=3600;
    SetPose(TEXT("Idle"),0,0);return true;
}
void UWCSilkmotherPresentationComponent::PlayCue(FName Name,FVector Location,const FWCBellbackFrame& F)
{
    if(!F.AllowSound||F.Paused||!Sounds.Contains(Name))return;
    const float Gain=Name.ToString().StartsWith(TEXT("Footstep"))?.055f:Name==TEXT("Weave")?.08f:.14f;
    UGameplayStatics::PlaySoundAtLocation(this,Sounds.FindChecked(Name),Location,Gain,1,0,Attenuation,Concurrency);
    ++SoundsPlayed;
    UE_LOG(LogTemp,Display,TEXT("WC_SILKMOTHER_SOUND unit=%llu cue=%s tick=%d"),F.Id,*Name.ToString(),F.Combat?F.Combat->CurrentTick():-1);
}
FVector UWCSilkmotherPresentationComponent::CueLocation(FName Socket) const
{
    return Skeletal?Skeletal->GetSocketLocation(Socket):GetComponentLocation();
}
bool UWCSilkmotherPresentationComponent::IsDefeatFinished() const
{
    return CurrentClip==TEXT("Defeat")&&CurrentSeconds>=Clips.FindChecked(TEXT("Defeat"))->GetPlayLength()-.01f;
}
void UWCSilkmotherPresentationComponent::SetPose(FName Name,float Seconds,double Clock)
{
    if(!Clips.Contains(Name))return;
    if(CurrentClip!=Name){OldClip=CurrentClip;OldSeconds=CurrentSeconds;CurrentClip=Name;BlendStarted=Clock;}
    CurrentSeconds=FMath::Clamp(Seconds,0.f,Clips.FindChecked(Name)->GetPlayLength());
    if(auto* A=Cast<UWCSilkmotherAnimInstance>(Skeletal->GetAnimInstance())){
        A->Current=Clips.FindChecked(Name);A->Seconds=CurrentSeconds;
        A->Previous=Clips.FindRef(OldClip);A->PreviousSeconds=OldSeconds;
        A->Alpha=FMath::Clamp(float((Clock-BlendStarted)/.12),0.f,1.f);
        A->HitReaction=HitOverlayActive?Clips.FindChecked(TEXT("Hit")):nullptr;
        A->HitReactionSeconds=HitOverlayAge;
    }
}
void UWCSilkmotherPresentationComponent::Present(const FWCBellbackFrame& F)
{
    if(!Skeletal)return;
    HitOverlayActive=false;HitOverlayAge=0;
    if(Generation!=F.Generation){Generation=F.Generation;EventCursor=0;HasLocation=false;WalkPhase=0;TerminalClip=NAME_None;TerminalStarted=-1;HitStarted=-100;LastClock=F.Clock;
        ReleasedActions.Reset();WeavingActions.Reset();CaughtTargets.Reset();MeshYaw=F.Facing*90+180;}
    const float Dt=FMath::Max(0.f,float(F.Clock-LastClock));LastClock=F.Clock;
    const FVector Location=GetOwner()->GetActorLocation();
    const FVector Travel=HasLocation?Location-PreviousLocation:FVector::ZeroVector;
    PreviousLocation=Location;HasLocation=true;
    double DefeatClock=-1;
    if(F.Combat){
        for(const auto& Action:F.Combat->VisualActions())if(Action.source==F.Id){
            if(Action.released&&!ReleasedActions.Contains(Action.action)){
                ReleasedActions.Add(Action.action);PlayCue(TEXT("Shot"),CueLocation(TEXT("mouth")),F);
            }else if(!Action.released&&!Action.basicAttack&&!WeavingActions.Contains(Action.action)){
                WeavingActions.Add(Action.action);PlayCue(TEXT("Weave"),CueLocation(TEXT("mouth")),F);
            }
        }
        const auto& Events=F.Combat->Events();if(EventCursor>Events.size())EventCursor=Events.size();
        for(;EventCursor<Events.size();++EventCursor){const auto& E=Events[EventCursor];
            if(E.effect==wc::Effect::Damage&&E.target==F.Id&&E.healthLoss>0){
                HitStarted=MotionRevisionEnabled()?E.tick*F.TickMs/1000.:
                    F.Clock-(F.Combat->CurrentTick()-E.tick)*F.TickMs/1000.;DefeatClock=HitStarted;
                PlayCue(TEXT("Hit"),CueLocation(TEXT("impact_center")),F);
            }
            if(E.source==F.Id&&E.mechanic==wc::AbilityMechanic::CocoonProjectile&&E.effect==wc::Effect::Stun&&E.resolved>0){
                // Position uses the same current eight-cell board mapping as the lab presentation.
                const FVector P((E.cell.column-3.5)*200,(3.5-E.cell.row)*200,75);
                PlayCue(TEXT("Catch"),P,F);
                for(const auto& Target:F.Combat->Units())if(Target.id==E.target)CaughtTargets.Add(E.target,{Target.cocoonExpiry,P});
            }
        }
        for(auto It=CaughtTargets.CreateIterator();It;++It){
            const auto Target=std::find_if(F.Combat->Units().begin(),F.Combat->Units().end(),[&](const auto& U){return U.id==It.Key();});
            if(Target==F.Combat->Units().end()||Target->health<=0||F.Combat->Result().complete){It.RemoveCurrent();continue;}
            if(F.Combat->CurrentTick()>=It.Value().Key){PlayCue(TEXT("Release"),It.Value().Value,F);It.RemoveCurrent();}
        }
    }
    const auto* U=F.Unit;
    if(U&&U->health<=0&&TerminalClip!=TEXT("Defeat")){TerminalClip=TEXT("Defeat");TerminalStarted=DefeatClock>=0?DefeatClock:F.Clock;PlayCue(TEXT("Defeat"),CueLocation(TEXT("lantern")),F);}
    else if(U&&U->health>0&&F.Combat&&F.Combat->Result().complete&&F.Combat->Result().winner==F.Side&&TerminalClip.IsNone()){
        TerminalClip=TEXT("Victory");TerminalStarted=F.Clock;PlayCue(TEXT("Victory"),CueLocation(TEXT("lantern")),F);
    }
    FName Name=TEXT("Idle");float Seconds=FMath::Fmod(float(F.Clock),Clips.FindChecked(Name)->GetPlayLength());
    if(!F.ReviewClip.IsNone()){SetPose(F.ReviewClip,F.ReviewSeconds,F.Clock);return;}
    if(!TerminalClip.IsNone()){Name=TerminalClip;Seconds=float(F.Clock-TerminalStarted);}
    else if(U&&U->state==wc::ActionState::Stunned){Name=TEXT("Idle");Seconds=0;}
    else if(U&&(U->state==wc::ActionState::CastWindup||U->state==wc::ActionState::CastRecovery)){
        Name=TEXT("Active");const float Release=float(F.Clock-U->releaseTick*F.TickMs/1000.);
        Seconds=Release<0?.65f*FMath::Clamp(1.f+Release/FMath::Max(.001f,U->ability.castMs/1000.f),0.f,1.f):
            .65f+FMath::Clamp(Release/FMath::Max(.001f,U->ability.recoveryMs/1000.f),0.f,1.f)*.65f;
    }
    else if(U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::AttackRecovery)){
        Name=TEXT("Attack");const float Release=float(F.Clock-U->releaseTick*F.TickMs/1000.);
        Seconds=Release<0?FMath::Max(0.f,.15f+Release):.15f+Release;
    }
    if(TerminalClip.IsNone()&&U&&U->state==wc::ActionState::Moving){
        Name=TEXT("Move");const float Before=WalkPhase;if(Dt>0)WalkPhase+=Travel.Size2D()/TravelPerCycle;
        // Group contacts into four quiet accents, rather than eight loud clicks per cycle.
        for(float Offset:{0.f,.5f,1.f/12.f,7.f/12.f})
            if(FMath::FloorToInt(WalkPhase+Offset)>FMath::FloorToInt(Before+Offset))
                PlayCue(SoundNames[(StepVariant++)%3],CueLocation(TEXT("impact_center")),F);
        Seconds=FMath::Fmod(WalkPhase,1.f)*Clips.FindChecked(Name)->GetPlayLength();
    }
    else if(!MotionRevisionEnabled()&&TerminalClip.IsNone()&&Name==TEXT("Idle")&&F.Clock-HitStarted<.4&&!(U&&U->state==wc::ActionState::Stunned)){
        Name=TEXT("Hit");Seconds=float(F.Clock-HitStarted);
    }
    const double HitAge=F.Clock-HitStarted;
    if(MotionRevisionEnabled()&&TerminalClip.IsNone()&&U&&U->health>0&&HitAge>=0&&HitAge<.4){
        HitOverlayActive=true;HitOverlayAge=float(HitAge);
    }
    const float Desired=U&&U->state==wc::ActionState::Moving&&Travel.SizeSquared2D()>.001?Travel.Rotation().Yaw-90:F.Facing*90+180;
    MeshYaw=FMath::FixedTurn(MeshYaw,Desired,Dt*420);
    SetWorldRotation(FRotator(0,MeshYaw,0));
    SetPose(Name,Seconds,F.Clock);
}
