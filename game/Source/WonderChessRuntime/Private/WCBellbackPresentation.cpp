#include "WCBellbackPresentation.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimationPoseData.h"
#include "Animation/AnimSequence.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundConcurrency.h"
#include <algorithm>

namespace {
const TCHAR* Root=TEXT("/Game/WonderChess/VNext/Characters/Bellback_r001/");
const TCHAR* ClipNames[]={TEXT("Idle"),TEXT("Move"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory"),TEXT("TurnLeft"),TEXT("TurnRight")};
const TCHAR* SoundNames[]={TEXT("Footstep"),TEXT("Bell"),TEXT("Impact"),TEXT("Hit"),TEXT("Defeat")};
FString AssetPath(const FString& Folder,const FString& Name){return FString(Root)+Folder+Name+TEXT(".")+Name;}
template<class T>T* Load(const FString& Folder,const FString& Name){return LoadObject<T>(nullptr,*AssetPath(Folder,Name));}

struct FGroundLeg {const TCHAR* Upper;const TCHAR* Lower;const TCHAR* Ankle;const TCHAR* Toe;double RestSole[3];};
// Measured from each saved candidate LOD's rest surface. Reduction changes the
// lowest sole vertex; using LOD0's clearance for every LOD buried the reduced paws.
// Provenance: reports/bellback-production-20260920/rig-lod-probe.json.
const FGroundLeg Legs[]={
    {TEXT("Bone_020"),TEXT("Bone_019"),TEXT("Bone_018"),TEXT("Bone_017"),{.01960703,-.18014381,-.52039660}},
    {TEXT("Bone_025"),TEXT("Bone_024"),TEXT("Bone_023"),TEXT("Bone_022"),{.00932036,-2.17353035,-.24429201}},
    {TEXT("Bone_008"),TEXT("Bone_007"),TEXT("Bone_006"),TEXT("Bone_005"),{.01774862,-.11284633,-.69997752}},
    {TEXT("Bone_012"),TEXT("Bone_011"),TEXT("Bone_010"),TEXT("Bone_009"),{.00001014,-.00641626,-.24624321}}};

// Candidate-specific fixed-board contact correction. All calculations include the
// source root's reference scale. Preserve limb lengths and the existing knee pole;
// only an ankle below its measured sole clearance is raised. No whole-body lift.
void GroundFeet(FCompactPose& Pose,int& Corrected,float& Maximum,int LOD)
{
    Corrected=0;Maximum=0;
    const auto& Bones=Pose.GetBoneContainer();
    TArray<FTransform,TInlineAllocator<128>> World,Reference;
    World.SetNum(Pose.GetNumBones());Reference.SetNum(Pose.GetNumBones());
    for(auto I:Pose.ForEachBoneIndex()){
        const auto P=Pose.GetParentBoneIndex(I);World[I.GetInt()]=Pose[I];Reference[I.GetInt()]=Bones.GetRefPoseTransform(I);
        if(P.GetInt()!=INDEX_NONE){World[I.GetInt()]=World[I.GetInt()]*World[P.GetInt()];Reference[I.GetInt()]=Reference[I.GetInt()]*Reference[P.GetInt()];}
    }
    const auto Index=[&](const TCHAR* Name){return Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(Bones.GetReferenceSkeleton().FindBoneIndex(Name)));};
    for(const auto& Leg:Legs){
        const auto U=Index(Leg.Upper),L=Index(Leg.Lower),A=Index(Leg.Ankle),T=Index(Leg.Toe);
        if(U.GetInt()<0||L.GetInt()<0||A.GetInt()<0||T.GetInt()<0)continue;
        FTransform Upper=World[U.GetInt()],Lower=World[L.GetInt()],Ankle=World[A.GetInt()];
        const FVector Hip=Upper.GetLocation(),Knee=Lower.GetLocation(),Foot=Ankle.GetLocation();
        const double Floor=Reference[A.GetInt()].GetLocation().Z-Leg.RestSole[FMath::Clamp(LOD,0,2)]+.5;
        FVector Goal=Foot;Goal.Z=FMath::Max(Goal.Z,Floor);
        const bool Raised=Goal.Z>Foot.Z+.0001;
        const bool Rotated=!Ankle.GetRotation().Equals(Reference[A.GetInt()].GetRotation(),.0001);
        if(Raised){
            const double UpperLength=FVector::Distance(Hip,Knee),LowerLength=FVector::Distance(Knee,Foot);
            const double Distance=FVector::Distance(Hip,Goal);
            if(UpperLength>.001&&LowerLength>.001&&Distance>.001){
                const FVector Axis=(Goal-Hip)/Distance;
                const double Reach=FMath::Clamp(Distance,FMath::Abs(UpperLength-LowerLength)+.0001,UpperLength+LowerLength-.0001);
                FVector Pole=(Knee-Hip)-Axis*FVector::DotProduct(Knee-Hip,Axis);
                if(!Pole.Normalize()){
                    Pole=Reference[L.GetInt()].GetLocation()-Reference[U.GetInt()].GetLocation();
                    Pole-=Axis*FVector::DotProduct(Pole,Axis);
                    if(!Pole.Normalize())Pole=FVector::CrossProduct(Axis,FVector::RightVector).GetSafeNormal();
                }
                const double Along=(UpperLength*UpperLength+Reach*Reach-LowerLength*LowerLength)/(2*Reach);
                const FVector NewKnee=Hip+Axis*Along+Pole*FMath::Sqrt(FMath::Max(0.,UpperLength*UpperLength-Along*Along));
                Goal=Hip+Axis*Reach;
                Upper.SetRotation((FQuat::FindBetweenNormals((Knee-Hip).GetSafeNormal(),(NewKnee-Hip).GetSafeNormal())*Upper.GetRotation()).GetNormalized());
                Lower.SetRotation((FQuat::FindBetweenNormals((Foot-Knee).GetSafeNormal(),(Goal-NewKnee).GetSafeNormal())*Lower.GetRotation()).GetNormalized());
                Lower.SetLocation(NewKnee);Ankle.SetLocation(Goal);
                Maximum=FMath::Max(Maximum,float(FVector::Distance(Foot,Goal)));
            }
        }
        Ankle.SetRotation(Reference[A.GetInt()].GetRotation());
        if(Raised||Rotated)++Corrected;
        const auto Parent=Pose.GetParentBoneIndex(U);
        Pose[U]=Parent.GetInt()<0?Upper:Upper.GetRelativeTransform(World[Parent.GetInt()]);
        Pose[L]=Lower.GetRelativeTransform(Upper);Pose[A]=Ankle.GetRelativeTransform(Lower);
        Pose[T]=Bones.GetRefPoseTransform(T);
    }
}

// Engine-only pose extraction avoids an animation blueprint or additional module.
// No animation notifies/root-motion processing can issue game commands.
struct FBellbackAnimProxy : FAnimInstanceProxy {
    UAnimSequence* Current=nullptr;UAnimSequence* Previous=nullptr;UAnimSequence* Overlay=nullptr;
    float Time=0,PreviousTime=0,Alpha=1;
    float OverlayTime=0,OverlayAlpha=0;FName OverlayBone=NAME_None;
    int Corrected=0;float MaximumCorrection=0;
    explicit FBellbackAnimProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance){}
    virtual void PreUpdate(UAnimInstance* Instance,float Delta) override {
        FAnimInstanceProxy::PreUpdate(Instance,Delta);
        const auto* A=CastChecked<UWCBellbackAnimInstance>(Instance);
        Current=A->Current;Previous=A->Previous;Time=A->CurrentSeconds;PreviousTime=A->PreviousSeconds;Alpha=A->BlendAlpha;
        Overlay=A->Overlay;OverlayTime=A->OverlaySeconds;OverlayAlpha=A->OverlayAlpha;OverlayBone=A->OverlayBone;
    }
    virtual bool Evaluate(FPoseContext& Output) override {
        Output.ResetToRefPose();
        if(!Current)return true;
        FAnimationPoseData OutData(Output);
        Current->GetAnimationPose(OutData,FAnimExtractContext(Time,false));
        if(Previous&&Alpha<1){
            FPoseContext Old(Output);Old.ResetToRefPose();
            FAnimationPoseData OldData(Old);
            Previous->GetAnimationPose(OldData,FAnimExtractContext(PreviousTime,false));
            FAnimationRuntime::BlendTwoPosesTogetherInPlace(OutData,OldData,Alpha);
        }
        if(Overlay&&OverlayAlpha>0&&!OverlayBone.IsNone()){
            const auto& Bones=Output.Pose.GetBoneContainer();
            const int MeshIndex=Bones.GetReferenceSkeleton().FindBoneIndex(OverlayBone);
            if(MeshIndex>=0){
                const auto Index=Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
                if(Index.GetInt()>=0){
                    FPoseContext Layer(Output);Layer.ResetToRefPose();FAnimationPoseData LayerData(Layer);
                    Overlay->GetAnimationPose(LayerData,FAnimExtractContext(OverlayTime,false));
                    FTransform Blended;Blended.Blend(Output.Pose[Index],Layer.Pose[Index],OverlayAlpha);Output.Pose[Index]=Blended;
                }
            }
        }
        GroundFeet(Output.Pose,Corrected,MaximumCorrection,GetLODLevel());
        Output.Pose.NormalizeRotations();
        return true;
    }
    virtual void PostEvaluate(UAnimInstance* Instance) override {
        FAnimInstanceProxy::PostEvaluate(Instance);
        auto* A=CastChecked<UWCBellbackAnimInstance>(Instance);A->CorrectedLegs=Corrected;A->MaximumFootCorrection=MaximumCorrection;
    }
};
}
FAnimInstanceProxy* UWCBellbackAnimInstance::CreateAnimInstanceProxy(){return new FBellbackAnimProxy(this);}
void UWCBellbackAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy){delete Proxy;}

bool UWCBellbackPresentationComponent::ValidateAssets(FString& Error)
{
    auto* Mesh=Load<USkeletalMesh>(TEXT(""),TEXT("SK_Bellback"));
    if(!Mesh||!Mesh->GetSkeleton()){Error=TEXT("Bellback candidate skeletal mesh/skeleton missing");return false;}
    for(const auto& Leg:Legs)for(const TCHAR* Bone:{Leg.Upper,Leg.Lower,Leg.Ankle,Leg.Toe})
        if(Mesh->GetRefSkeleton().FindBoneIndex(Bone)<0){Error=FString(TEXT("Bellback floor solver bone missing: "))+Bone;return false;}
    for(const TCHAR* Bone:{TEXT("MainBell"),TEXT("Head")})
        if(Mesh->GetRefSkeleton().FindBoneIndex(Bone)<0){Error=FString(TEXT("Bellback reaction overlay bone missing: "))+Bone;return false;}
    if(!Load<UMaterialInterface>(TEXT(""),TEXT("M_Bellback"))){Error=TEXT("Bellback material missing");return false;}
    for(const TCHAR* Name:ClipNames){
        auto* Clip=Load<UAnimSequence>(TEXT("Animations/"),FString(TEXT("AS_Bellback_"))+Name);
        if(!Clip||Clip->GetSkeleton()!=Mesh->GetSkeleton()||Clip->GetPlayLength()<=0){Error=FString(TEXT("Bellback clip missing, empty or skeleton mismatch: "))+Name;return false;}
    }
    if(Load<UAnimSequence>(TEXT("Animations/"),TEXT("AS_Bellback_Move"))->EvaluateCurveData(FName(TEXT("GroundTravelCm")),FAnimExtractContext(0))<=0){Error=TEXT("Bellback Move GroundTravelCm curve missing or nonpositive");return false;}
    for(const TCHAR* Name:SoundNames)if(!Load<USoundBase>(TEXT("Audio/"),FString(TEXT("S_Bellback_"))+Name)){Error=FString(TEXT("Bellback sound missing: "))+Name;return false;}
    for(const TCHAR* Socket:{TEXT("bell"),TEXT("mouth"),TEXT("foot_fl"),TEXT("foot_fr"),TEXT("foot_bl"),TEXT("foot_br"),TEXT("impact_center")})
        if(!Mesh->FindSocket(Socket)){Error=FString(TEXT("Bellback socket missing: "))+Socket;return false;}
    return true;
}

bool UWCBellbackPresentationComponent::InitializeCandidate(FString& Error)
{
    if(!ValidateAssets(Error))return false;
    for(const TCHAR* Name:ClipNames)Clips.Add(Name,Load<UAnimSequence>(TEXT("Animations/"),FString(TEXT("AS_Bellback_"))+Name));
    for(const TCHAR* Name:SoundNames)Sounds.Add(Name,Load<USoundBase>(TEXT("Audio/"),FString(TEXT("S_Bellback_"))+Name));
    // Runtime-safe authored metric stored as a constant float curve on Move.
    const auto* Move=Clips.FindChecked(TEXT("Move")).Get();
    GroundTravelCm=Move->EvaluateCurveData(FName(TEXT("GroundTravelCm")),FAnimExtractContext(0));
    if(!FMath::IsFinite(GroundTravelCm)||GroundTravelCm<=0){Error=TEXT("Bellback Move requires positive GroundTravelCm animation curve (source centimeters/cycle)");return false;}
    Skeletal=NewObject<USkeletalMeshComponent>(GetOwner());GetOwner()->AddInstanceComponent(Skeletal);
    Skeletal->SetupAttachment(this);Skeletal->SetSkeletalMeshAsset(Load<USkeletalMesh>(TEXT(""),TEXT("SK_Bellback")));
    Skeletal->SetMaterial(0,Load<UMaterialInterface>(TEXT(""),TEXT("M_Bellback")));
    Skeletal->SetRelativeScale3D(FVector(2.2/1.7));
    Skeletal->SetCollisionEnabled(ECollisionEnabled::NoCollision);Skeletal->SetGenerateOverlapEvents(false);
    Skeletal->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Skeletal->bEnableUpdateRateOptimizations=false;
    Skeletal->SetAnimationMode(EAnimationMode::AnimationBlueprint);Skeletal->SetAnimInstanceClass(UWCBellbackAnimInstance::StaticClass());
    Skeletal->RegisterComponent();
    static TWeakObjectPtr<USoundConcurrency> SharedConcurrency;
    if(!SharedConcurrency.IsValid()){SharedConcurrency=NewObject<USoundConcurrency>();SharedConcurrency->Concurrency.MaxCount=16;}
    Concurrency=SharedConcurrency.Get();
    SetPose(TEXT("Idle"),0,0);
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_READY ground_travel_source_cm=%.3f world_cm=%.3f scale=%.6f"),GroundTravelCm,GroundTravelCm*2.2/1.7,2.2/1.7);
    return true;
}
FVector UWCBellbackPresentationComponent::CueLocation(FName Socket)const{return Skeletal?Skeletal->GetSocketLocation(Socket):GetComponentLocation();}
bool UWCBellbackPresentationComponent::IsDefeatFinished()const{return TerminalClip==TEXT("Defeat")&&SampleSeconds>=Clips.FindChecked(TEXT("Defeat"))->GetPlayLength()-.001f;}
void UWCBellbackPresentationComponent::PlayCue(FName Cue,FName Socket,const FWCBellbackFrame& Frame)
{
    if(!Frame.AllowSound)return;
    // Measured crowded-board capture clipped at the PCM export ceiling with .42.
    // Keep footfalls below the bell/impact accents and preserve mix headroom.
    const float Gain=Cue==TEXT("Footstep")?.105f:.21f;
    UGameplayStatics::PlaySoundAtLocation(this,Sounds.FindChecked(Cue),CueLocation(Socket),Gain,1,0,nullptr,Concurrency);
    ++SoundsPlayed;
    UE_LOG(LogTemp,VeryVerbose,TEXT("WC_BELLBACK_SOUND unit=%llu cue=%s tick=%d"),Frame.Id,*Cue.ToString(),Frame.Combat?Frame.Combat->CurrentTick():-1);
}
void UWCBellbackPresentationComponent::SetPose(FName Clip,float Seconds,double Clock)
{
    if(!Skeletal)return;
    if(Clip!=CurrentClip){PreviousClip=CurrentClip;PreviousSeconds=SampleSeconds;CurrentClip=Clip;BlendStarted=Clock;Seen.Add(Clip);}
    SampleSeconds=FMath::Clamp(Seconds,0.f,Clips.FindChecked(Clip)->GetPlayLength());
    if(auto* A=Cast<UWCBellbackAnimInstance>(Skeletal->GetAnimInstance())){
        A->Current=Clips.FindChecked(CurrentClip);A->Previous=PreviousClip.IsNone()?nullptr:Clips.FindChecked(PreviousClip);
        A->CurrentSeconds=SampleSeconds;A->PreviousSeconds=PreviousSeconds;
        A->Overlay=nullptr;A->OverlayAlpha=0;
        const float T=FMath::Clamp(float((Clock-BlendStarted)/.12),0.f,1.f);A->BlendAlpha=T*T*(3-2*T);
    }
}
void UWCBellbackPresentationComponent::Present(const FWCBellbackFrame& F)
{
    if(!Skeletal)return;
    if(Generation!=F.Generation){
        Generation=F.Generation;EventCursor=F.Combat&&F.Combat->CurrentTick()>1?F.Combat->Events().size():0;
        HasLocation=false;TerminalClip=OverrideClip=NAME_None;TerminalStarted=-1;OverrideStarted=-100;WalkPhase=0;
        LastClock=F.Clock;LastYaw=MeshYaw=F.Facing*90+180;
    }
    const float Dt=FMath::Max(0.f,float(F.Clock-LastClock));LastClock=F.Clock;
    const FVector Location=GetOwner()->GetActorLocation();
    const FVector Travel=HasLocation?Location-LastLocation:FVector::ZeroVector;
    const float Distance=Dt>0?Travel.Size2D():0;LastLocation=Location;HasLocation=true;
    if(!F.ReviewClip.IsNone()){
        float Seconds=F.ReviewSeconds;
        if(F.ReviewTravel&&F.ReviewClip==TEXT("Move")){
            const float Before=WalkPhase;WalkPhase+=Distance/(GroundTravelCm*2.2/1.7);
            const float Length=Clips.FindChecked(TEXT("Move"))->GetPlayLength();Seconds=FMath::Fmod(WalkPhase,1.f)*Length;
            LastMoveRate=Dt>0?(WalkPhase-Before)*Length/Dt:0;
            for(int Step=FMath::FloorToInt(Before*4)+1;Step<=FMath::FloorToInt(WalkPhase*4)&&Step<=FMath::FloorToInt(Before*4)+4;++Step){
                const FName Feet[]={TEXT("foot_fr"),TEXT("foot_br"),TEXT("foot_fl"),TEXT("foot_bl")};PlayCue(TEXT("Footstep"),Feet[Step%4],F);
            }
            if(Travel.SizeSquared2D()>.001)Skeletal->SetWorldRotation(FRotator(0,Travel.Rotation().Yaw-90,0));
        }
        if(F.ReviewEffectSerial>=0&&F.ReviewEffectSerial!=ReviewEffectSerial){ReviewEffectSerial=F.ReviewEffectSerial;PlayCue(TEXT("Bell"),TEXT("bell"),F);PlayCue(TEXT("Impact"),TEXT("mouth"),F);}
        SetPose(F.ReviewClip,Seconds,F.Clock);return;
    }
    if(!OverrideClip.IsNone()&&F.Clock-OverrideStarted>=Clips.FindChecked(OverrideClip)->GetPlayLength())OverrideClip=NAME_None;
    double DefeatEventClock=-1;
    if(F.Combat){
        const auto& Events=F.Combat->Events();
        if(EventCursor>Events.size())EventCursor=Events.size();
        for(;EventCursor<Events.size();++EventCursor){const auto& E=Events[EventCursor];
            const double EventClock=F.Clock-(F.Combat->CurrentTick()-E.tick)*F.TickMs/1000.;
            if(E.effect==wc::Effect::Damage&&E.guardedBy==F.Id&&E.prevented>0){OverrideClip=TEXT("Active");OverrideStarted=EventClock;PlayCue(TEXT("Bell"),TEXT("bell"),F);}
            if(E.effect==wc::Effect::Damage&&E.source==F.Id&&E.basicAttack&&E.resolved>0)PlayCue(TEXT("Impact"),TEXT("mouth"),F);
            if(E.effect==wc::Effect::Damage&&E.target==F.Id&&E.healthLoss>0){
                if(OverrideClip!=TEXT("Active")){OverrideClip=TEXT("Hit");OverrideStarted=EventClock;}
                PlayCue(TEXT("Hit"),TEXT("impact_center"),F);
                DefeatEventClock=EventClock;
            }
        }
    }
    const auto* U=F.Unit;
    if(U&&U->health<=0&&TerminalClip!=TEXT("Defeat")){TerminalClip=TEXT("Defeat");TerminalStarted=DefeatEventClock>=0?DefeatEventClock:F.Clock;PlayCue(TEXT("Defeat"),TEXT("bell"),F);}
    if(U&&U->health>0&&F.Combat->Result().complete&&F.Combat->Result().winner==F.Side&&TerminalClip.IsNone()){TerminalClip=TEXT("Victory");TerminalStarted=F.Clock;}
    FName Clip=TEXT("Idle");float Time=FMath::Fmod(float(F.Clock),Clips.FindChecked(Clip)->GetPlayLength());LastMoveRate=0;
    if(!TerminalClip.IsNone()){Clip=TerminalClip;Time=float(F.Clock-TerminalStarted);}
    else if(!OverrideClip.IsNone()&&F.Clock-OverrideStarted<Clips.FindChecked(OverrideClip)->GetPlayLength()&&
        !(U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::AttackRecovery||U->state==wc::ActionState::Moving))){
        Clip=OverrideClip;Time=float(F.Clock-OverrideStarted);
    }else if(U&&(U->state==wc::ActionState::AttackWindup||U->state==wc::ActionState::AttackRecovery)){
        Clip=TEXT("Attack");const float Release=float(F.Clock-U->releaseTick*F.TickMs/1000.);
        const float Recovery=FMath::Max(.001f,(U->recoveryTick-U->releaseTick)*F.TickMs/1000.f);
        Time=Release<0?FMath::Max(0.f,.15f+Release):.15f+FMath::Clamp(Release/Recovery,0.f,1.f)*(Clips.FindChecked(Clip)->GetPlayLength()-.15f);
    }else if(U&&U->state==wc::ActionState::Moving){
        Clip=TEXT("Move");const float Length=Clips.FindChecked(Clip)->GetPlayLength();
        const float PreviousPhase=WalkPhase;WalkPhase+=Distance/(GroundTravelCm*2.2/1.7);
        LastMoveRate=Dt>0?(WalkPhase-PreviousPhase)*Length/Dt:0;Time=FMath::Fmod(WalkPhase,1.f)*Length;
        for(int Step=FMath::FloorToInt(PreviousPhase*4)+1;Step<=FMath::FloorToInt(WalkPhase*4)&&Step<=FMath::FloorToInt(PreviousPhase*4)+4;++Step){
            const FName Feet[]={TEXT("foot_fr"),TEXT("foot_br"),TEXT("foot_fl"),TEXT("foot_bl")};PlayCue(TEXT("Footstep"),Feet[Step%4],F);
        }
    }else if(!U&&F.Facing*90+180!=LastYaw){
        OverrideClip=FMath::FindDeltaAngleDegrees(LastYaw,float(F.Facing*90+180))>0?TEXT("TurnRight"):TEXT("TurnLeft");OverrideStarted=F.Clock;
        Clip=OverrideClip;Time=0;
    }
    LastYaw=F.Facing*90+180;
    // Mesh yaw eases relative to the always-exact authored facing marker on the parent.
    const float DesiredYaw=U&&U->state==wc::ActionState::Moving&&Travel.SizeSquared2D()>.001?Travel.Rotation().Yaw-90:LastYaw;
    MeshYaw=FMath::FixedTurn(MeshYaw,DesiredYaw,Dt*300);
    Skeletal->SetRelativeRotation(FRotator(0,FMath::FindDeltaAngleDegrees(LastYaw,MeshYaw),0));
    SetPose(Clip,Time,F.Clock);
    // Reactions cannot replace a committed attack or stop the grounded gait.
    // The independently rigged bell may react above either base motion; a head
    // flinch layers over locomotion only, preserving the authored attack contact.
    if(TerminalClip.IsNone()&&!OverrideClip.IsNone()&&OverrideClip!=Clip&&
        (OverrideClip==TEXT("Active")||(OverrideClip==TEXT("Hit")&&Clip==TEXT("Move")))){
        const float Age=float(F.Clock-OverrideStarted),Length=Clips.FindChecked(OverrideClip)->GetPlayLength();
        if(Age>=0&&Age<Length)if(auto* A=Cast<UWCBellbackAnimInstance>(Skeletal->GetAnimInstance())){
            A->Overlay=Clips.FindChecked(OverrideClip);A->OverlaySeconds=Age;
            A->OverlayBone=OverrideClip==TEXT("Active")?TEXT("MainBell"):TEXT("Head");
            A->OverlayAlpha=FMath::Clamp(FMath::Min(Age/.08f,(Length-Age)/.12f),0.f,1.f);Seen.Add(OverrideClip);
        }
    }
}
