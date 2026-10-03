#include "WCAssetAuthoringLibrary.h"
#include "ControlRig.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Modules/ModuleManager.h"
#include "WCBellbackPresentation.h"
#include "WCCragstoatPresentation.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimData/IAnimationDataController.h"
#include "Animation/AnimData/IAnimationDataModel.h"
#include "Animation/Skeleton.h"
#include "ReferenceSkeleton.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "SkeletalRenderPublic.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, WonderChessArtTools)
FString UWCAssetAuthoringLibrary::InspectCragstoatAnimationSource(UAnimSequence* Sequence)
{
    auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("valid"),false);
    if(Sequence&&Sequence->GetPathName().StartsWith(TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Animations/"))){
        const auto* Model=Sequence->GetDataModel();
        R->SetStringField(TEXT("asset"),Sequence->GetPathName());
        R->SetBoolField(TEXT("compressed_data_valid"),Sequence->IsCompressedDataValid());
        if(Model){
            R->SetStringField(TEXT("model_object"),Sequence->GetDataModelInterface().GetObject()->GetPathName());
            R->SetNumberField(TEXT("keys"),Model->GetNumberOfKeys());R->SetNumberField(TEXT("frames"),Model->GetNumberOfFrames());
            const auto Rate=Model->GetFrameRate();R->SetNumberField(TEXT("rate_numerator"),Rate.Numerator);R->SetNumberField(TEXT("rate_denominator"),Rate.Denominator);
            TArray<FName> Names;Model->GetBoneTrackNames(Names);auto Tracks=MakeShared<FJsonObject>();
            bool Valid=!Names.IsEmpty();
            const auto Numbers=[](const TArray<double>& Values){TArray<TSharedPtr<FJsonValue>> A;for(double V:Values)A.Add(MakeShared<FJsonValueNumber>(V));return A;};
            for(FName Name:Names){
                TArray<FTransform> Keys;Model->GetBoneTrackTransforms(Name,Keys);
                Valid&=Keys.Num()==Model->GetNumberOfKeys();TArray<TSharedPtr<FJsonValue>> Encoded;
                for(const auto& Key:Keys){
                    const FVector T=Key.GetTranslation(),S=Key.GetScale3D();const FQuat Q=Key.GetRotation();
                    Valid&=!Key.ContainsNaN()&&FMath::IsFinite(Q.SizeSquared());auto K=MakeShared<FJsonObject>();
                    K->SetArrayField(TEXT("translation"),Numbers({T.X,T.Y,T.Z}));K->SetArrayField(TEXT("rotation"),Numbers({Q.X,Q.Y,Q.Z,Q.W}));K->SetArrayField(TEXT("scale"),Numbers({S.X,S.Y,S.Z}));
                    Encoded.Add(MakeShared<FJsonValueObject>(K));
                }
                Tracks->SetArrayField(Name.ToString(),Encoded);
            }
            R->SetNumberField(TEXT("bone_tracks"),Names.Num());R->SetObjectField(TEXT("tracks"),Tracks);R->SetBoolField(TEXT("valid"),Valid);
        }
    }
    R->SetStringField(TEXT("scope"),TEXT("Read-only native Sequencer model key extraction and loaded-platform compressed validity. Exact JSON comparison and compressed playback are separate checks."));
    FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));return Json;
}
bool UWCAssetAuthoringLibrary::SetCragstoatPose(USkeletalMeshComponent* Mesh,UAnimSequence* Current,float CurrentTime,
    UAnimSequence* Previous,float PreviousTime,float BlendAlpha,UAnimSequence* HitReaction,float HitReactionTime,UAnimSequence* GroundingReference)
{
    if(!Mesh||!Mesh->GetSkeletalMeshAsset()||!Current||!GroundingReference)return false;
    const auto ValidClip=[&](const UAnimSequence* Clip){return !Clip||Clip->GetPathName().StartsWith(TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/"));};
    const FString MeshPath=Mesh->GetSkeletalMeshAsset()->GetPathName();
    const bool AllowedMesh=MeshPath.StartsWith(TEXT("/Game/WonderChess/Diagnostics/CragstoatRevision20260930/SageTail_r003/"))||
        MeshPath==TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r001.SK_Cragstoat_BodySkin_r001")||
        MeshPath==TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r002.SK_Cragstoat_BodySkin_r002")||
        MeshPath==TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r003.SK_Cragstoat_BodySkin_r003")||
        MeshPath==TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20261001_r001/Mesh/SK_Cragstoat_BodySkin_r001.SK_Cragstoat_BodySkin_r001");
    if(!AllowedMesh||
        !ValidClip(Current)||!ValidClip(Previous)||!ValidClip(HitReaction)||!ValidClip(GroundingReference))return false;
    if(!FMath::IsFinite(CurrentTime)||!FMath::IsFinite(PreviousTime)||!FMath::IsFinite(BlendAlpha)||!FMath::IsFinite(HitReactionTime))return false;
    if(Mesh->GetAnimationMode()!=EAnimationMode::AnimationBlueprint||
        Mesh->GetAnimClass()!=UWCCragstoatAnimInstance::StaticClass()||
        !Cast<UWCCragstoatAnimInstance>(Mesh->GetAnimInstance())){
        Mesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);Mesh->SetAnimInstanceClass(UWCCragstoatAnimInstance::StaticClass());
    }
    auto* A=Cast<UWCCragstoatAnimInstance>(Mesh->GetAnimInstance());if(!A)return false;
    A->Current=Current;A->Seconds=CurrentTime;A->Previous=Previous;A->PreviousSeconds=PreviousTime;A->Alpha=BlendAlpha;
    A->HitReaction=HitReaction;A->HitReactionSeconds=HitReactionTime;A->GroundingReference=GroundingReference;
    Mesh->TickAnimation(0,false);Mesh->RefreshBoneTransforms();
    return A->PoseValid;
}
FString UWCAssetAuthoringLibrary::CragstoatPoseAudit(USkeletalMeshComponent* Mesh)
{
    auto* A=Mesh?Cast<UWCCragstoatAnimInstance>(Mesh->GetAnimInstance()):nullptr;
    auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("valid"),A&&A->PoseValid);
    if(A){R->SetNumberField(TEXT("corrected_legs"),A->CorrectedLegs);R->SetNumberField(TEXT("maximum_foot_correction_cm"),A->MaximumFootCorrection);}
    FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));return Json;
}
bool UWCAssetAuthoringLibrary::FinalizeCreatureAnimationSampling(UAnimSequence* Sequence)
{
    if(!Sequence)return false;
    const FString Path=Sequence->GetPathName();
    if(!Path.StartsWith(TEXT("/Game/WonderChess/VNext/Characters/SilkmotherMotionRevision20260930_"))&&
       !Path.StartsWith(TEXT("/Game/WonderChess/Diagnostics/SilkmotherMotionRevision20260930_"))&&
       !Path.StartsWith(TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/"))&&
       !Path.StartsWith(TEXT("/Game/WonderChess/Diagnostics/CragstoatProduction20260930_r001/")))return false;
    const auto* Model=Sequence->GetDataModel();if(!Model||Model->GetFrameRate()!=FFrameRate(60,1))return false;
    Sequence->GetController().NotifyPopulated();
    Sequence->MarkPackageDirty();
    return Sequence->GetSamplingFrameRate()==Model->GetFrameRate();
}
USkeleton* UWCAssetAuthoringLibrary::CreateCreatureSkeleton(const FString& AssetPath, const TArray<FName>& Names,
    const TArray<int32>& Parents, const TArray<FTransform>& LocalTransforms)
{
    if(!AssetPath.StartsWith(TEXT("/Game/WonderChess/Diagnostics/")) || !FPackageName::IsValidLongPackageName(AssetPath) ||
       FPackageName::DoesPackageExist(AssetPath)) return nullptr;
    UPackage* Package=CreatePackage(*AssetPath);if(!Package)return nullptr;
    const FString Name=FPackageName::GetLongPackageAssetName(AssetPath);
    if(FindObject<UObject>(Package,*Name))return nullptr;
    USkeleton* Result=NewObject<USkeleton>(Package,*Name,RF_Public|RF_Standalone|RF_Transactional);
    if(!InitializeCreatureSkeleton(Result,Names,Parents,LocalTransforms))return nullptr;
    FAssetRegistryModule::AssetCreated(Result);Package->MarkPackageDirty();return Result;
}
bool UWCAssetAuthoringLibrary::InitializeCreatureSkeleton(USkeleton* Skeleton, const TArray<FName>& Names,
    const TArray<int32>& Parents, const TArray<FTransform>& LocalTransforms)
{
    if(!Skeleton || Skeleton->GetReferenceSkeleton().GetNum()!=0 || Names.IsEmpty() ||
        Names.Num()!=Parents.Num() || Names.Num()!=LocalTransforms.Num()) return false;
    TSet<FName> Seen;
    for(int32 I=0;I<Names.Num();++I)
    {
        if(Names[I].IsNone() || Seen.Contains(Names[I]) || LocalTransforms[I].ContainsNaN() ||
           !LocalTransforms[I].GetRotation().IsNormalized() ||
           (I==0 ? Parents[I]!=INDEX_NONE : (Parents[I]<0 || Parents[I]>=I))) return false;
        Seen.Add(Names[I]);
    }
    Skeleton->Modify();
    {FReferenceSkeletonModifier Modifier(Skeleton);
     for(int32 I=0;I<Names.Num();++I)Modifier.Add(FMeshBoneInfo(Names[I],Names[I].ToString(),Parents[I]),LocalTransforms[I]);}
    Skeleton->MarkPackageDirty();return Skeleton->GetReferenceSkeleton().GetNum()==Names.Num();
}
FString UWCAssetAuthoringLibrary::MeasureCreatureSurface(USkeletalMeshComponent* Mesh, int32 LOD,
    const TArray<FVector>& RegionMin, const TArray<FVector>& RegionMax)
{
    if (!Mesh || RegionMin.Num()!=RegionMax.Num() || !Mesh->GetSkeletalMeshRenderData() ||
        !Mesh->GetSkeletalMeshRenderData()->LODRenderData.IsValidIndex(LOD)) return TEXT("{}");
    TArray<FFinalSkinVertex> Vertices; Mesh->GetCPUSkinnedVertices(Vertices,LOD);
    const auto& Rest=Mesh->GetSkeletalMeshRenderData()->LODRenderData[LOD].StaticVertexBuffers.PositionVertexBuffer;
    if (Vertices.Num()!=int32(Rest.GetNumVertices())) return TEXT("{}");
    TArray<double> Minimum; Minimum.Init(MAX_dbl,RegionMin.Num());
    TArray<int32> Count; Count.Init(0,RegionMin.Num());
    TArray<FVector> Sum; Sum.Init(FVector::ZeroVector,RegionMin.Num());
    double GlobalMin=MAX_dbl; int32 Below=0; FBox Bounds(ForceInit); FVector LowestRest=FVector::ZeroVector;
    const FTransform World=Mesh->GetComponentTransform();
    for(int32 I=0;I<Vertices.Num();++I)
    {
        const FVector P=World.TransformPosition(FVector(Vertices[I].Position));
        if(P.ContainsNaN()) return TEXT("{}");
        if(P.Z<GlobalMin){GlobalMin=P.Z;LowestRest=FVector(Rest.VertexPosition(I));}
        Below+=P.Z<-.05; Bounds+=P;
        const FVector R(Rest.VertexPosition(I));
        for(int32 J=0;J<RegionMin.Num();++J)
            if(FBox(RegionMin[J],RegionMax[J]).IsInsideOrOn(R))
            {Minimum[J]=FMath::Min(Minimum[J],P.Z);Sum[J]+=P;++Count[J];}
    }
    auto Obj=MakeShared<FJsonObject>();Obj->SetNumberField(TEXT("vertices"),Vertices.Num());
    Obj->SetNumberField(TEXT("minimum_z_cm"),GlobalMin);Obj->SetNumberField(TEXT("below_tolerance_count"),Below);
    TArray<TSharedPtr<FJsonValue>> Lowest;
    for(double V:{LowestRest.X,LowestRest.Y,LowestRest.Z})Lowest.Add(MakeShared<FJsonValueNumber>(V));
    Obj->SetArrayField(TEXT("lowest_vertex_rest_cm"),Lowest);
    TArray<TSharedPtr<FJsonValue>> Regions;
    for(int32 J=0;J<Count.Num();++J)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("vertices"),Count[J]);
        if(Count[J])
        {O->SetNumberField(TEXT("minimum_z_cm"),Minimum[J]);TArray<TSharedPtr<FJsonValue>> V;
         const FVector C=Sum[J]/Count[J];for(double X:{C.X,C.Y,C.Z})V.Add(MakeShared<FJsonValueNumber>(X));O->SetArrayField(TEXT("centroid"),V);}
        Regions.Add(MakeShared<FJsonValueObject>(O));
    }
    Obj->SetArrayField(TEXT("regions"),Regions);
    FString Json;FJsonSerializer::Serialize(Obj,TJsonWriterFactory<>::Create(&Json));return Json;
}
bool UWCAssetAuthoringLibrary::InitializeRig(UControlRig* Rig)
{
    if(!Rig)return false;
    Rig->Initialize(true);Rig->Evaluate_AnyThread();
    return Rig->GetHierarchy()&&Rig->GetHierarchy()->Num()>0;
}
bool UWCAssetAuthoringLibrary::EnsureMeshSocket(USkeletalMesh* Mesh, FName SocketName, FName BoneName, FTransform LocalTransform)
{
    if (!Mesh || SocketName.IsNone() || Mesh->GetRefSkeleton().FindBoneIndex(BoneName)==INDEX_NONE) return false;
    Mesh->Modify();
    USkeletalMeshSocket* Socket=Mesh->FindSocket(SocketName);
    if (!Socket)
    {
        Socket=NewObject<USkeletalMeshSocket>(Mesh,NAME_None,RF_Transactional);
        Socket->SocketName=SocketName;
        Mesh->AddSocket(Socket,false);
    }
    Socket->Modify();
    Socket->BoneName=BoneName;
    Socket->SetSocketLocalTransform(LocalTransform);
    Mesh->MarkPackageDirty();
    return true;
}
bool UWCAssetAuthoringLibrary::SetBellbackPose(USkeletalMeshComponent* Mesh,UAnimSequence* Current,float CurrentTime,UAnimSequence* Previous,float PreviousTime,float BlendAlpha)
{
    if(!Mesh||!Current)return false;
    if(!Cast<UWCBellbackAnimInstance>(Mesh->GetAnimInstance()))
    {
        Mesh->SetAnimationMode(EAnimationMode::AnimationBlueprint);
        Mesh->SetAnimInstanceClass(UWCBellbackAnimInstance::StaticClass());
        Mesh->InitAnim(true);
    }
    auto* Anim=Cast<UWCBellbackAnimInstance>(Mesh->GetAnimInstance());
    if(!Anim)return false;
    Anim->Current=Current;Anim->CurrentSeconds=CurrentTime;
    Anim->Previous=Previous;Anim->PreviousSeconds=PreviousTime;Anim->BlendAlpha=BlendAlpha;
    Mesh->TickAnimation(0,false);Mesh->RefreshBoneTransforms();
    return true;
}
bool UWCAssetAuthoringLibrary::ConfigureBellbackLOD(USkeletalMesh* Mesh,int32 Index)
{
    if(!Mesh||!Mesh->GetLODInfo(0)||Index<1||Index>2)return false;
    Mesh->Modify();
    {
        if(!Mesh->GetLODInfo(Index))Mesh->AddLODInfo();
        auto* Info=Mesh->GetLODInfo(Index);if(!Info)return false;
        Info->ReductionSettings.NumOfTrianglesPercentage=Index==1?.40f:.15f;
        Info->ReductionSettings.TerminationCriterion=SMTC_NumOfTriangles;
        Info->ReductionSettings.MaxBonesPerVertex=8;
        Info->ReductionSettings.BaseLOD=0;
        Info->ReductionSettings.bMergeCoincidentVertBones=true;
        Info->ScreenSize=FPerPlatformFloat(Index==1?.24f:.10f);
    }
    Mesh->MarkPackageDirty();return true;
}
FString UWCAssetAuthoringLibrary::MeasureBellbackSurface(USkeletalMeshComponent* Mesh,int32 LOD)
{
    if(!Mesh||!Mesh->GetSkeletalMeshRenderData()||!Mesh->GetSkeletalMeshRenderData()->LODRenderData.IsValidIndex(LOD))return TEXT("{}");
    TArray<FFinalSkinVertex> Vertices;Mesh->GetCPUSkinnedVertices(Vertices,LOD);
    const auto& Rest=Mesh->GetSkeletalMeshRenderData()->LODRenderData[LOD].StaticVertexBuffers.PositionVertexBuffer;
    if(Vertices.Num()!=int32(Rest.GetNumVertices()))return TEXT("{}");
    const FTransform World=Mesh->GetComponentTransform();double Minimum=MAX_dbl;int32 Below=0;
    double FootMin[4]={MAX_dbl,MAX_dbl,MAX_dbl,MAX_dbl};FVector Sum[4]={};int32 Count[4]={};
    FBox Bounds(ForceInit);
    for(int32 I=0;I<Vertices.Num();++I)
    {
        const FVector P=World.TransformPosition(FVector(Vertices[I].Position));Bounds+=P;
        Minimum=FMath::Min(Minimum,P.Z);Below+=P.Z<-.01;
        const FVector R(Rest.VertexPosition(I));const int32 F=(R.Y<0?2:0)+(R.X<0?1:0);
        if(R.Z<24)FootMin[F]=FMath::Min(FootMin[F],P.Z);
        if(R.Z<2){Sum[F]+=P;++Count[F];}
    }
    auto Obj=MakeShared<FJsonObject>();Obj->SetNumberField(TEXT("vertices"),Vertices.Num());Obj->SetNumberField(TEXT("minimum_z_cm"),Minimum);Obj->SetNumberField(TEXT("below_zero_count"),Below);
    TArray<TSharedPtr<FJsonValue>> Feet;
    for(int32 F=0;F<4;++F){auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("minimum_z_cm"),FootMin[F]);O->SetNumberField(TEXT("sole_vertices"),Count[F]);
        const FVector C=Count[F]?Sum[F]/Count[F]:FVector::ZeroVector;TArray<TSharedPtr<FJsonValue>> Values;
        for(double V:{C.X,C.Y,C.Z})Values.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("sole_centroid"),Values);Feet.Add(MakeShared<FJsonValueObject>(O));}
    Obj->SetArrayField(TEXT("feet_fr_fl_br_bl"),Feet);
    TArray<TSharedPtr<FJsonValue>> Min,Max;
    for(double V:{Bounds.Min.X,Bounds.Min.Y,Bounds.Min.Z})Min.Add(MakeShared<FJsonValueNumber>(V));
    for(double V:{Bounds.Max.X,Bounds.Max.Y,Bounds.Max.Z})Max.Add(MakeShared<FJsonValueNumber>(V));
    Obj->SetArrayField(TEXT("bounds_min"),Min);Obj->SetArrayField(TEXT("bounds_max"),Max);
    FString Json;FJsonSerializer::Serialize(Obj,TJsonWriterFactory<>::Create(&Json));return Json;
}
