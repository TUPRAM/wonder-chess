#include "WCAnimationPrecisionLibrary.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimData/IAnimationDataModel.h"
#include "Animation/Skeleton.h"
#include "Channels/MovieSceneFloatChannel.h"
#include "MovieScene.h"
#include "MovieSceneSequence.h"
#include "MovieSceneTrack.h"
#include "Rigs/FKControlRig.h"
#include "Rigs/RigHierarchy.h"
#include "Sections/MovieSceneParameterSection.h"
#include "Sequencer/MovieSceneControlRigParameterSection.h"

namespace
{
constexpr double RotationGateDegrees=.001;
constexpr int32 KeyCount=37;
const TCHAR* CandidateAsset=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Animations/Running_r005/AS_Cragstoat_Move.AS_Cragstoat_Move");
const TCHAR* AcceptedSkeleton=TEXT("/Game/WonderChess/Diagnostics/CragstoatRevision20260930/SageTail_r003/SKEL_Cragstoat.SKEL_Cragstoat");

double RotationErrorDegrees(const FQuat& A,const FQuat& B)
{
    const double Dot=FMath::Abs(A.X*B.X+A.Y*B.Y+A.Z*B.Z+A.W*B.W);
    return FMath::RadiansToDegrees(2.*FMath::Acos(FMath::Clamp(Dot,0.,1.)));
}

bool ExactPrincipalEuler(const FQuat& Q,FVector& Euler)
{
    // FVector Euler order is Roll,Pitch,Yaw. The installed FQuat::Euler path
    // deliberately snaps near +/-90 degrees; use the double identities instead.
    const double Singularity=Q.Z*Q.X-Q.W*Q.Y;
    const double YawY=2.*(Q.W*Q.Z+Q.X*Q.Y);
    const double YawX=1.-2.*(Q.Y*Q.Y+Q.Z*Q.Z);
    const double RollY=-2.*(Q.W*Q.X+Q.Y*Q.Z);
    const double RollX=1.-2.*(Q.X*Q.X+Q.Y*Q.Y);
    const double SinPitch=FMath::Clamp(2.*Singularity,-1.,1.);
    if(FMath::Abs(YawX)+FMath::Abs(YawY)+FMath::Abs(RollX)+FMath::Abs(RollY)<1.e-14){
        // At the actual singularity only, yaw/roll are coupled. This exact
        // representative is verified against Q before any channel is touched.
        const double Sign=SinPitch<0.?-1.:1.;
        Euler=FVector(0.,Sign*90.,FMath::RadiansToDegrees(Sign*2.*FMath::Atan2(Q.X,Q.W)));
    }else{
        Euler=FVector(FMath::RadiansToDegrees(FMath::Atan2(RollY,RollX)),
            FMath::RadiansToDegrees(FMath::Asin(SinPitch)),
            FMath::RadiansToDegrees(FMath::Atan2(YawY,YawX)));
    }
    return !Euler.ContainsNaN()&&RotationErrorDegrees(Q,FQuat::MakeFromEuler(Euler).GetNormalized())<RotationGateDegrees;
}

FVector UnwrapNear(const FVector& Value,const FVector& Previous)
{
    return FVector(Previous.X+FMath::FindDeltaAngleDegrees(Previous.X,Value.X),
        Previous.Y+FMath::FindDeltaAngleDegrees(Previous.Y,Value.Y),
        Previous.Z+FMath::FindDeltaAngleDegrees(Previous.Z,Value.Z));
}
}

bool UWCAnimationPrecisionLibrary::SetCragstoatPreciseRotationKeys(UAnimSequence* Sequence,
    FName Bone,const TArray<FQuat>& SourceKeys)
{
    if(!IsInGameThread()||!Sequence||Sequence->GetPathName()!=CandidateAsset||Bone.IsNone()||
        SourceKeys.Num()!=KeyCount||!Sequence->GetSkeleton()||
        Sequence->GetSkeleton()->GetPathName()!=AcceptedSkeleton||
        Sequence->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Bone)<0)return false;

    const auto ModelInterface=Sequence->GetDataModelInterface();
    IAnimationDataModel* Model=ModelInterface.GetInterface();
    auto* MovieSequence=Cast<UMovieSceneSequence>(ModelInterface.GetObject());
    if(!Model||!MovieSequence||!MovieSequence->GetMovieScene()||
        MovieSequence->GetOutermost()!=Sequence->GetOutermost()||
        MovieSequence->GetMovieScene()->GetOutermost()!=Sequence->GetOutermost())return false;
    IAnimationDataModel::FEvaluationAndModificationLock Lock(*Model);
    if(Model->GetFrameRate()!=FFrameRate(60,1)||Model->GetNumberOfKeys()!=KeyCount||
        Model->GetNumberOfFrames()!=KeyCount-1||FMath::Abs(Model->GetPlayLength()-.6)>.000001)return false;
    TArray<FName> BoneTracks;Model->GetBoneTrackNames(BoneTracks);
    if(BoneTracks.Num()!=33)return false;
    TSet<FName> SeenBones;
    for(FName Name:BoneTracks){
        if(SeenBones.Contains(Name)||Sequence->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Name)<0)return false;
        SeenBones.Add(Name);
    }
    if(!SeenBones.Contains(Bone))return false;

    UMovieSceneControlRigParameterSection* Section=nullptr;
    for(auto* Track:MovieSequence->GetMovieScene()->GetTracks()){
        if(!Track)return false;
        for(auto* Candidate:Track->GetAllSections()){
            auto* RigSection=Cast<UMovieSceneControlRigParameterSection>(Candidate);
            if(!RigSection)continue;
            if(Section)return false; // Never guess between multiple rigs/sections.
            Section=RigSection;
        }
    }
    if(!Section||Section->GetOutermost()!=Sequence->GetOutermost()||
        Section->IsReadOnly()||Section->IsLocked()||!Section->GetControlRig()||
        !Section->GetControlRig()->IsA<UFKControlRig>()||!Section->GetControlRig()->GetHierarchy())return false;
    const FName ControlName=UFKControlRig::GetControlName(URigHierarchy::GetSanitizedName(Bone),ERigElementType::Bone);
    if(!Section->GetControlRig()->GetHierarchy()->Contains(FRigElementKey(ControlName,ERigElementType::Control)))return false;
    auto& Parameters=Section->GetTransformParameterNamesAndCurves();
    FTransformParameterNameAndCurves* Curves=nullptr;
    for(auto& Parameter:Parameters)if(Parameter.ParameterName==ControlName){
        if(Curves)return false;
        Curves=&Parameter;
    }
    if(!Curves)return false;

    TArray<FFrameNumber> Frames;Frames.Reserve(KeyCount);
    TArray<FMovieSceneFloatValue> Values[3];
    for(auto& Channel:Values)Channel.Reserve(KeyCount);
    FVector Previous=FVector::ZeroVector;double MaximumError=0.;
    for(int32 Index=0;Index<KeyCount;++Index){
        const FQuat Input=SourceKeys[Index];
        if(Input.ContainsNaN()||!FMath::IsFinite(Input.SizeSquared())||
            FMath::Abs(Input.SizeSquared()-1.)>.0001)return false;
        const FQuat Q=Input.GetNormalized();FVector Euler;
        if(!ExactPrincipalEuler(Q,Euler))return false;
        if(Index>0){
            const FVector Principal=UnwrapNear(Euler,Previous);
            const FVector Equivalent=UnwrapNear(FVector(Euler.X+180.,
                Euler.Y>=0.?180.-Euler.Y:-180.-Euler.Y,Euler.Z+180.),Previous);
            if(RotationErrorDegrees(Q,FQuat::MakeFromEuler(Equivalent).GetNormalized())>=RotationGateDegrees)return false;
            Euler=(Equivalent-Previous).SizeSquared()<(Principal-Previous).SizeSquared()?Equivalent:Principal;
        }
        // Validate the exact float values that will enter the saved channels.
        const FVector Stored(float(Euler.X),float(Euler.Y),float(Euler.Z));
        const double Error=RotationErrorDegrees(Q,FQuat::MakeFromEuler(Stored).GetNormalized());
        if(Stored.ContainsNaN()||!FMath::IsFinite(Error)||Error>=RotationGateDegrees)return false;
        MaximumError=FMath::Max(MaximumError,Error);Previous=Stored;
        Frames.Add(FFrameNumber(Index));
        for(int32 Axis=0;Axis<3;++Axis){
            FMovieSceneFloatValue Value;Value.Value=float(Stored[Axis]);
            Value.InterpMode=ERichCurveInterpMode::RCIM_Linear;Values[Axis].Add(Value);
        }
    }

    // All namespace, model, target and 37-key rotation checks precede mutation.
    // NotifyPopulated/finalization is the caller's separate complete-stage step.
    if(!Section->TryModify())return false;
    for(int32 Axis=0;Axis<3;++Axis)Curves->Rotation[Axis].SetKeysOnly(Frames,Values[Axis]);
    Sequence->MarkPackageDirty();
    UE_LOG(LogTemp,Display,TEXT("WC_CRAGSTOAT_PRECISE_ROTATION asset=%s bone=%s keys=%d maximum_float_roundtrip_degrees=%.9f"),
        *Sequence->GetPathName(),*Bone.ToString(),KeyCount,MaximumError);
    return true;
}
