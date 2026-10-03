#include "WCCragstoatMeshAuditLibrary.h"

#include "Engine/SkeletalMesh.h"
#include "ReferenceSkeleton.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshModel.h"
#include "Rendering/SkeletalMeshLODModel.h"
#include "Rendering/SkinWeightVertexBuffer.h"
#include "RawIndexBuffer.h"
#include "Misc/SecureHash.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const TCHAR* SourcePath=TEXT("/Game/WonderChess/Diagnostics/CragstoatRevision20260930/SageTail_r003/SK_Cragstoat.SK_Cragstoat");
const TCHAR* CandidatePath=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r001.SK_Cragstoat_BodySkin_r001");
const TCHAR* CandidatePath2=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r002.SK_Cragstoat_BodySkin_r002");
const TCHAR* CandidatePath3=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20260930_r001/Mesh/SK_Cragstoat_BodySkin_r003.SK_Cragstoat_BodySkin_r003");
const TCHAR* ParentTransitionPath=TEXT("/Game/WonderChess/VNext/Characters/CragstoatProduction20261001_r001/Mesh/SK_Cragstoat_BodySkin_r001.SK_Cragstoat_BodySkin_r001");
const FName TailNames[]={TEXT("Tail01"),TEXT("Tail02"),TEXT("Tail03"),TEXT("Tail04"),TEXT("Tail05"),TEXT("Tail06"),TEXT("Tail07"),TEXT("Tail08")};
struct FNamedWeight { FName Name; uint32 Value; };
using FWeights=TArray<FNamedWeight,TInlineAllocator<8>>;
struct FSnapshot
{
    const FSkeletalMeshLODRenderData* LOD=nullptr;
    TArray<uint32> Indices;
    TArray<FWeights> Weights;
    TSharedPtr<FJsonObject> Json=MakeShared<FJsonObject>();
    uint32 NormalizationFailures=0;
};
FString FinishHash(FSHA1& Hash)
{
    Hash.Final();uint8 Bytes[FSHA1::DigestSize];Hash.GetHash(Bytes);
    return BytesToHex(Bytes,FSHA1::DigestSize).ToLower();
}
template<class T>void HashValue(FSHA1& Hash,const T& Value){Hash.Update(reinterpret_cast<const uint8*>(&Value),sizeof(T));}
void HashName(FSHA1& Hash,FName Name)
{
    const FTCHARToUTF8 Text(*Name.ToString().ToLower());const uint32 Size=Text.Length();
    HashValue(Hash,Size);Hash.Update(reinterpret_cast<const uint8*>(Text.Get()),Size);
}
uint32 WeightFor(const FWeights& Weights,FName Name)
{
    const auto* Found=Weights.FindByPredicate([&](const FNamedWeight& W){return W.Name==Name;});
    return Found?Found->Value:0;
}
bool SameWeights(const FWeights& A,const FWeights& B)
{
    if(A.Num()!=B.Num())return false;
    for(int32 I=0;I<A.Num();++I)if(A[I].Name!=B[I].Name||A[I].Value!=B[I].Value)return false;
    return true;
}
template<class T>TArray<TSharedPtr<FJsonValue>> MatrixValues(const T& Matrix)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    for(int32 Row=0;Row<4;++Row)for(int32 Column=0;Column<4;++Column)Values.Add(MakeShared<FJsonValueNumber>(Matrix.M[Row][Column]));
    return Values;
}
bool Capture(USkeletalMesh* Mesh,FSnapshot& Out,FString& Error)
{
    const auto* Render=Mesh->GetResourceForRendering();
    if(!Render||Render->LODRenderData.IsEmpty()){Error=TEXT("LOD0 render data unavailable");return false;}
    Out.LOD=&Render->LODRenderData[0];const auto& LOD=*Out.LOD;
    const auto& Positions=LOD.StaticVertexBuffers.PositionVertexBuffer;
    const auto& Attributes=LOD.StaticVertexBuffers.StaticMeshVertexBuffer;
    const auto& Colors=LOD.StaticVertexBuffers.ColorVertexBuffer;
    const auto* Skin=LOD.GetSkinWeightVertexBuffer();const auto* Index=LOD.MultiSizeIndexContainer.GetIndexBuffer();
    const uint32 N=Positions.GetNumVertices(),UVs=Attributes.GetNumTexCoords();
    const bool WeightCPU=Skin&&Skin->GetDataVertexBuffer()->GetWeightData()&&
        (!Skin->GetVariableBonesPerVertex()||Skin->GetLookupVertexBuffer()->GetLookupData());
    const bool IndexCPU=Index&&Index->Num()>0&&Index->GetResourceDataSize()>0&&
        (LOD.MultiSizeIndexContainer.GetDataTypeSize()==2||LOD.MultiSizeIndexContainer.GetDataTypeSize()==4)&&
        uint64(Index->GetResourceDataSize())>=uint64(Index->Num())*LOD.MultiSizeIndexContainer.GetDataTypeSize();
    const bool CPU=N>0&&Positions.GetVertexData()&&Attributes.GetTangentData()&&Attributes.GetTexCoordData()&&
        (Colors.GetNumVertices()==0||Colors.GetVertexData())&&WeightCPU&&IndexCPU;
    Out.Json->SetBoolField(TEXT("cpu_data_available"),CPU);
    Out.Json->SetNumberField(TEXT("render_vertices"),N);Out.Json->SetNumberField(TEXT("uv_channels"),UVs);
    Out.Json->SetNumberField(TEXT("color_vertices"),Colors.GetNumVertices());Out.Json->SetNumberField(TEXT("saved_lods"),Render->LODRenderData.Num());
    if(const auto* Info=Mesh->GetLODInfo(0)){
        auto Build=MakeShared<FJsonObject>();Build->SetBoolField(TEXT("use_high_precision_skin_weights"),Info->BuildSettings.bUseHighPrecisionSkinWeights);
        Build->SetBoolField(TEXT("recompute_normals"),Info->BuildSettings.bRecomputeNormals);Build->SetBoolField(TEXT("recompute_tangents"),Info->BuildSettings.bRecomputeTangents);
        Out.Json->SetObjectField(TEXT("saved_lod0_build_settings"),Build);
    }
    if(!CPU){Error=TEXT("Actual CPU buffer data unavailable; audit never changes CPU access flags");return false;}
    if(Attributes.GetNumVertices()!=N||Skin->GetNumVertices()!=N||UVs==0||UVs>8||
        (Colors.GetNumVertices()!=0&&Colors.GetNumVertices()!=N)||Index->Num()%3!=0||Skin->GetMaxBoneInfluences()>64){
        Error=TEXT("Render buffer metadata inconsistent");return false;
    }
    const auto& Ref=Mesh->GetRefSkeleton();
    if(Ref.GetNum()!=33){Error=TEXT("Expected exact33bone anatomy");return false;}
    const auto& Inverse=Mesh->GetRefBasesInvMatrix();
    if(Inverse.Num()!=Ref.GetNum()){Error=TEXT("Actual inverse reference bases missing/inconsistent");return false;}
    TArray<TSharedPtr<FJsonValue>> RefBones;
    for(int32 I=0;I<Ref.GetNum();++I){
        const auto Local=Ref.GetRefBonePose()[I].ToMatrixWithScale();
        for(int32 Row=0;Row<4;++Row)for(int32 Column=0;Column<4;++Column)
            if(!FMath::IsFinite(Local.M[Row][Column])||!FMath::IsFinite(Inverse[I].M[Row][Column])){
                Error=TEXT("Nonfinite actual mesh reference/local inverse matrix");return false;
            }
        auto Bone=MakeShared<FJsonObject>();Bone->SetStringField(TEXT("name"),Ref.GetBoneName(I).ToString());
        Bone->SetNumberField(TEXT("parent_index"),Ref.GetParentIndex(I));Bone->SetArrayField(TEXT("local_pose_matrix_row_major"),MatrixValues(Local));
        Bone->SetArrayField(TEXT("actual_inverse_reference_matrix_row_major"),MatrixValues(Inverse[I]));RefBones.Add(MakeShared<FJsonValueObject>(Bone));
    }
    Out.Json->SetArrayField(TEXT("actual_mesh_reference_bones"),RefBones);
    for(FName Name:TailNames)if(Ref.FindBoneIndex(Name)<0){Error=TEXT("Required Tail01-08 reference bone missing");return false;}
    TArray<int32> SectionFor;SectionFor.Init(INDEX_NONE,N);
    for(int32 S=0;S<LOD.RenderSections.Num();++S){
        const auto& Section=LOD.RenderSections[S];
        if(uint64(Section.BaseVertexIndex)+Section.NumVertices>N||Section.BoneMap.IsEmpty()){
            Error=TEXT("Invalid render section vertex range/bone map");return false;
        }
        for(uint32 V=Section.BaseVertexIndex;V<Section.BaseVertexIndex+Section.NumVertices;++V){
            if(SectionFor[V]!=INDEX_NONE){Error=TEXT("Overlapping render section vertex ranges");return false;}SectionFor[V]=S;
        }
    }
    FSHA1 PositionHash,TangentHash,UVHash,ColorHash,IndexHash,WeightHash,TailHash[8];
    const uint32 ColorCount=Colors.GetNumVertices();HashValue(ColorHash,ColorCount);HashValue(UVHash,UVs);
    uint64 TailMass[8]={};uint32 TailVertices[8]={};Out.Weights.SetNum(N);
    for(uint32 V=0;V<N;++V){
        const auto P=Positions.VertexPosition(V);const auto X=Attributes.VertexTangentX(V);
        const auto Y=Attributes.VertexTangentY(V);const auto Z=Attributes.VertexTangentZ(V);
        if(P.ContainsNaN()||X.ContainsNaN()||Y.ContainsNaN()||Z.ContainsNaN()){
            Error=TEXT("Nonfinite rest position/tangent");return false;
        }
        HashValue(PositionHash,P);HashValue(TangentHash,X);HashValue(TangentHash,Y);HashValue(TangentHash,Z);
        for(uint32 U=0;U<UVs;++U){const auto UV=Attributes.GetVertexUV(V,U);if(UV.ContainsNaN()){Error=TEXT("Nonfinite UV");return false;}HashValue(UVHash,UV);}
        if(ColorCount)HashValue(ColorHash,Colors.VertexColor(V));
        if(SectionFor[V]<0){Error=TEXT("Unmapped render vertex section");return false;}
        const auto& BoneMap=LOD.RenderSections[SectionFor[V]].BoneMap;
        uint32 Offset=0,Count=0;Skin->GetVertexInfluenceOffsetCount(V,Offset,Count);
        if(Count>64||uint64(Offset)+uint64(Count)*Skin->GetBoneIndexAndWeightByteSize()>Skin->GetDataVertexBuffer()->GetVertexDataSize()){
            Error=TEXT("Skin influence range exceeds available CPU data");return false;
        }
        auto& Weights=Out.Weights[V];uint32 Sum=0;
        for(uint32 I=0;I<Count;++I){
            const uint32 Value=Skin->GetBoneWeight(V,I);if(Value==0)continue;
            const uint32 Slot=Skin->GetBoneIndex(V,I);
            if(!BoneMap.IsValidIndex(Slot)||!Ref.IsValidIndex(BoneMap[Slot])){Error=TEXT("Positive skin weight has invalid section/reference bone");return false;}
            const FName Name=Ref.GetBoneName(BoneMap[Slot]);Sum+=Value;
            if(auto* Existing=Weights.FindByPredicate([&](const FNamedWeight& W){return W.Name==Name;}))Existing->Value+=Value;
            else Weights.Add({Name,Value});
        }
        Out.NormalizationFailures+=Sum!=65535;
        Weights.Sort([](const FNamedWeight& A,const FNamedWeight& B){return A.Name.LexicalLess(B.Name);});
        const uint32 Entries=Weights.Num();HashValue(WeightHash,Entries);
        for(const auto& W:Weights){HashName(WeightHash,W.Name);HashValue(WeightHash,W.Value);}
        for(int32 T=0;T<8;++T){const uint32 W=WeightFor(Weights,TailNames[T]);TailMass[T]+=W;TailVertices[T]+=W>0;HashValue(TailHash[T],W);}
    }
    Out.Indices.Reserve(Index->Num());
    for(int32 I=0;I<Index->Num();++I){const uint32 V=Index->Get(I);if(V>=N){Error=TEXT("Render triangle index out of bounds");return false;}Out.Indices.Add(V);HashValue(IndexHash,V);}
    auto Signatures=MakeShared<FJsonObject>();
    Signatures->SetStringField(TEXT("algorithm"),TEXT("SHA1 nativeCPU value stream; comparison counters are direct, not digest-only"));
    Signatures->SetStringField(TEXT("rest_positions"),FinishHash(PositionHash));Signatures->SetStringField(TEXT("normal_and_tangents"),FinishHash(TangentHash));
    Signatures->SetStringField(TEXT("uv"),FinishHash(UVHash));Signatures->SetStringField(TEXT("color"),FinishHash(ColorHash));
    Signatures->SetStringField(TEXT("indices"),FinishHash(IndexHash));Signatures->SetStringField(TEXT("semantic_packed_weights"),FinishHash(WeightHash));
    Out.Json->SetObjectField(TEXT("signatures"),Signatures);
    auto Tail=MakeShared<FJsonObject>();
    for(int32 T=0;T<8;++T){auto Bone=MakeShared<FJsonObject>();Bone->SetStringField(TEXT("per_vertex_signature"),FinishHash(TailHash[T]));
        Bone->SetNumberField(TEXT("weighted_render_vertices"),TailVertices[T]);Bone->SetNumberField(TEXT("expanded_uint16_mass"),double(TailMass[T]));
        Bone->SetNumberField(TEXT("normalized_mass"),double(TailMass[T])/65535.);Tail->SetObjectField(TailNames[T].ToString(),Bone);}
    Out.Json->SetObjectField(TEXT("tail_weights"),Tail);Out.Json->SetNumberField(TEXT("render_indices"),Index->Num());
    Out.Json->SetNumberField(TEXT("render_triangles"),Index->Num()/3);Out.Json->SetNumberField(TEXT("render_sections"),LOD.RenderSections.Num());
    Out.Json->SetNumberField(TEXT("storage_weight_bits"),Skin->GetBoneWeightByteSize()*8);Out.Json->SetNumberField(TEXT("storage_bone_index_bits"),Skin->GetBoneIndexByteSize()*8);
    Out.Json->SetBoolField(TEXT("unified_bone_map"),LOD.HasUnifiedBoneMap());Out.Json->SetNumberField(TEXT("normalization_mismatches"),Out.NormalizationFailures);
    Out.Json->SetStringField(TEXT("weight_encoding"),TEXT("GetBoneWeight uint16; native8bit expands w8*257, native16bit retains value. Not authoring/DynamicMesh packed16 identity."));
    return true;
}
}

FString UWCCragstoatMeshAuditLibrary::CompareCragstoatBodySkin(USkeletalMesh* Source,USkeletalMesh* Candidate)
{
    auto Result=MakeShared<FJsonObject>();Result->SetBoolField(TEXT("valid"),false);Result->SetBoolField(TEXT("comparable_order"),false);
    Result->SetField(TEXT("tail_weight_equivalence"),MakeShared<FJsonValueNull>());
    Result->SetStringField(TEXT("scope"),TEXT("Read-only exact two-asset LOD0 CPU render-data audit. No source/seam/face remapping, bone-rest/motion/skin/appearance acceptance or asset mutation."));
    const auto Encode=[&](){FString Json;FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Json));return Json;};
    if(!IsInGameThread()||!Source||!Candidate||Source->GetPathName()!=SourcePath||
        (Candidate->GetPathName()!=CandidatePath&&Candidate->GetPathName()!=CandidatePath2&&Candidate->GetPathName()!=CandidatePath3&&Candidate->GetPathName()!=ParentTransitionPath)){
        Result->SetStringField(TEXT("failure"),TEXT("Requires game-thread exact approved source and an explicitly allowed private BodySkin mesh"));return Encode();
    }
    if(Source->IsCompiling()||Candidate->IsCompiling()){Result->SetStringField(TEXT("failure"),TEXT("Mesh render-data compilation active; no waits/rebuilds performed"));return Encode();}
    FSnapshot A,B;FString Error;Result->SetStringField(TEXT("source_asset"),Source->GetPathName());Result->SetStringField(TEXT("candidate_asset"),Candidate->GetPathName());
    Result->SetObjectField(TEXT("source"),A.Json);Result->SetObjectField(TEXT("candidate"),B.Json);
    if(!Capture(Source,A,Error)||!Capture(Candidate,B,Error)){Result->SetStringField(TEXT("failure"),Error);return Encode();}
    const auto& AR=Source->GetRefSkeleton();const auto& BR=Candidate->GetRefSkeleton();
    const auto& AI=Source->GetRefBasesInvMatrix();const auto& BI=Candidate->GetRefBasesInvMatrix();
    uint32 NameChanges=0,ParentChanges=0,LocalChanges=0,InverseChanges=0;double MaximumLocal=0.,MaximumInverse=0.;
    for(int32 I=0;I<33;++I){
        NameChanges+=AR.GetBoneName(I)!=BR.GetBoneName(I);ParentChanges+=AR.GetParentIndex(I)!=BR.GetParentIndex(I);
        const auto AL=AR.GetRefBonePose()[I].ToMatrixWithScale(),BL=BR.GetRefBonePose()[I].ToMatrixWithScale();bool LocalDifferent=false,InverseDifferent=false;
        for(int32 Row=0;Row<4;++Row)for(int32 Column=0;Column<4;++Column){
            LocalDifferent|=AL.M[Row][Column]!=BL.M[Row][Column];InverseDifferent|=AI[I].M[Row][Column]!=BI[I].M[Row][Column];
            MaximumLocal=FMath::Max(MaximumLocal,FMath::Abs(AL.M[Row][Column]-BL.M[Row][Column]));
            MaximumInverse=FMath::Max(MaximumInverse,double(FMath::Abs(AI[I].M[Row][Column]-BI[I].M[Row][Column])));
        }
        LocalChanges+=LocalDifferent;InverseChanges+=InverseDifferent;
    }
    auto Ref=MakeShared<FJsonObject>();Ref->SetBoolField(TEXT("same_skeleton_object"),Source->GetSkeleton()==Candidate->GetSkeleton());
    Ref->SetNumberField(TEXT("bone_name_order_differences"),NameChanges);Ref->SetNumberField(TEXT("parent_index_differences"),ParentChanges);
    Ref->SetNumberField(TEXT("local_pose_matrix_rows_different"),LocalChanges);Ref->SetNumberField(TEXT("inverse_reference_matrix_rows_different"),InverseChanges);
    Ref->SetNumberField(TEXT("maximum_local_matrix_element_difference"),MaximumLocal);Ref->SetNumberField(TEXT("maximum_inverse_matrix_element_difference"),MaximumInverse);
    Ref->SetBoolField(TEXT("actual_reference_basis_direct_equal"),NameChanges==0&&ParentChanges==0&&LocalChanges==0&&InverseChanges==0);
    Result->SetObjectField(TEXT("actual_reference_basis_comparison"),Ref);
    const auto& AP=A.LOD->StaticVertexBuffers.PositionVertexBuffer;const auto& BP=B.LOD->StaticVertexBuffers.PositionVertexBuffer;
    const auto& AV=A.LOD->StaticVertexBuffers.StaticMeshVertexBuffer;const auto& BV=B.LOD->StaticVertexBuffers.StaticMeshVertexBuffer;
    const auto& AC=A.LOD->StaticVertexBuffers.ColorVertexBuffer;const auto& BC=B.LOD->StaticVertexBuffers.ColorVertexBuffer;
    const bool VertexCount=AP.GetNumVertices()==BP.GetNumVertices(),UVCount=AV.GetNumTexCoords()==BV.GetNumTexCoords(),ColorCount=AC.GetNumVertices()==BC.GetNumVertices();
    uint32 Positions=0,Tangents=0,UVs=0,Colors=0,IndexChanges=0;const uint32 N=FMath::Min(AP.GetNumVertices(),BP.GetNumVertices());
    for(uint32 V=0;V<N;++V){
        const auto P=AP.VertexPosition(V),Q=BP.VertexPosition(V);Positions+=FMemory::Memcmp(&P,&Q,sizeof(P))!=0;
        const auto AX=AV.VertexTangentX(V),BX=BV.VertexTangentX(V),AZ=AV.VertexTangentZ(V),BZ=BV.VertexTangentZ(V);
        const auto AY=AV.VertexTangentY(V),BY=BV.VertexTangentY(V);
        Tangents+=FMemory::Memcmp(&AX,&BX,sizeof(AX))||FMemory::Memcmp(&AY,&BY,sizeof(AY))||FMemory::Memcmp(&AZ,&BZ,sizeof(AZ));
        for(uint32 U=0;U<FMath::Min(AV.GetNumTexCoords(),BV.GetNumTexCoords());++U){const auto X=AV.GetVertexUV(V,U),Y=BV.GetVertexUV(V,U);UVs+=FMemory::Memcmp(&X,&Y,sizeof(X))!=0;}
        if(ColorCount&&AC.GetNumVertices())Colors+=AC.VertexColor(V)!=BC.VertexColor(V);
    }
    for(int32 I=0;I<FMath::Min(A.Indices.Num(),B.Indices.Num());++I)IndexChanges+=A.Indices[I]!=B.Indices[I];
    const bool IndexEqual=A.Indices.Num()==B.Indices.Num()&&IndexChanges==0;
    const bool Comparable=VertexCount&&UVCount&&ColorCount&&IndexEqual&&Positions==0&&Tangents==0&&UVs==0&&Colors==0;
    auto Geometry=MakeShared<FJsonObject>();Geometry->SetBoolField(TEXT("vertex_count_equal"),VertexCount);Geometry->SetBoolField(TEXT("index_direct_equal"),IndexEqual);
    Geometry->SetBoolField(TEXT("rest_positions_direct_equal"),VertexCount&&Positions==0);Geometry->SetBoolField(TEXT("normal_tangent_direct_equal"),VertexCount&&Tangents==0);
    Geometry->SetBoolField(TEXT("uv_direct_equal"),VertexCount&&UVCount&&UVs==0);Geometry->SetBoolField(TEXT("color_direct_equal"),VertexCount&&ColorCount&&Colors==0);
    Geometry->SetNumberField(TEXT("position_rows_different"),Positions);Geometry->SetNumberField(TEXT("normal_tangent_rows_different"),Tangents);
    Geometry->SetNumberField(TEXT("uv_values_different"),UVs);Geometry->SetNumberField(TEXT("color_rows_different"),Colors);Geometry->SetNumberField(TEXT("index_values_different"),IndexChanges);
    Result->SetObjectField(TEXT("direct_geometry"),Geometry);Result->SetBoolField(TEXT("comparable_order"),Comparable);
    const bool SameIndexDiagnostic=VertexCount&&IndexEqual&&Positions==0;
    if(SameIndexDiagnostic){
        uint32 Changed=0,Inside=0,Outside=0,TailChanged[8]={};
        uint32 MaximumWeightDelta=0;TArray<TSharedPtr<FJsonValue>> Examples;
        for(uint32 V=0;V<N;++V){
            if(!SameWeights(A.Weights[V],B.Weights[V])){++Changed;const auto P=AP.VertexPosition(V);
                const bool In=P.X>=-66.f&&P.X<=-35.f&&FMath::Abs(P.Y)<=8.f&&P.Z>=12.f&&P.Z<=24.f;Inside+=In;Outside+=!In;
                for(const auto& W:A.Weights[V])MaximumWeightDelta=FMath::Max(MaximumWeightDelta,uint32(FMath::Abs(int64(W.Value)-int64(WeightFor(B.Weights[V],W.Name)))));
                for(const auto& W:B.Weights[V])MaximumWeightDelta=FMath::Max(MaximumWeightDelta,uint32(FMath::Abs(int64(W.Value)-int64(WeightFor(A.Weights[V],W.Name)))));
                if(Examples.Num()<64){auto Example=MakeShared<FJsonObject>();Example->SetNumberField(TEXT("render_vertex"),V);Example->SetBoolField(TEXT("inside_filter"),In);
                    TArray<TSharedPtr<FJsonValue>> Position;for(double C:{double(P.X),double(P.Y),double(P.Z)})Position.Add(MakeShared<FJsonValueNumber>(C));Example->SetArrayField(TEXT("source_rest_cm"),Position);
                    auto Before=MakeShared<FJsonObject>(),After=MakeShared<FJsonObject>();for(const auto& W:A.Weights[V])Before->SetNumberField(W.Name.ToString(),W.Value);
                    for(const auto& W:B.Weights[V])After->SetNumberField(W.Name.ToString(),W.Value);Example->SetObjectField(TEXT("source_expanded_uint16"),Before);Example->SetObjectField(TEXT("candidate_expanded_uint16"),After);Examples.Add(MakeShared<FJsonValueObject>(Example));}
            }
            for(int32 T=0;T<8;++T)TailChanged[T]+=WeightFor(A.Weights[V],TailNames[T])!=WeightFor(B.Weights[V],TailNames[T]);
        }
        auto Diagnostic=MakeShared<FJsonObject>();Diagnostic->SetNumberField(TEXT("changed_weight_render_vertices"),Changed);
        Diagnostic->SetNumberField(TEXT("changed_weights_inside_coordinate_filter"),Inside);Diagnostic->SetNumberField(TEXT("changed_weights_outside_coordinate_filter"),Outside);
        Diagnostic->SetNumberField(TEXT("maximum_semantic_weight_delta_expanded_uint16"),MaximumWeightDelta);Diagnostic->SetArrayField(TEXT("first64_changed_weight_examples"),Examples);
        Diagnostic->SetStringField(TEXT("coordinate_filter"),TEXT("Source rest x[-66,-35], abs(y)<=8, z[12,24] cm; inclusive; render vertices, not DynamicMesh source ids."));
        Diagnostic->SetStringField(TEXT("interpretation"),TEXT("Same vertex count/index stream/position bits only. Diagnostic same-index counts do not certify seam correspondence or tail preservation when other attributes differ."));
        auto Tail=MakeShared<FJsonObject>();bool AllTail=true;
        for(int32 T=0;T<8;++T){Tail->SetNumberField(TailNames[T].ToString(),TailChanged[T]);AllTail&=TailChanged[T]==0;}
        Diagnostic->SetObjectField(TEXT("same_index_tail_weight_differences"),Tail);Result->SetObjectField(TEXT("diagnostic_same_index_weights"),Diagnostic);
        if(Comparable){
            Result->SetBoolField(TEXT("semantic_packed_weights_direct_equal"),Changed==0);
            Result->SetBoolField(TEXT("tail_weight_equivalence"),AllTail);
        }
    }
    if(!Comparable){
        Result->SetField(TEXT("semantic_packed_weights_direct_equal"),MakeShared<FJsonValueNull>());
        Result->SetStringField(TEXT("comparison_limit"),TEXT("Render order/attributes not identical: per-vertex weight/tail preservation cannot be inferred. No seam/face mapping attempted."));
    }
    Result->SetBoolField(TEXT("valid"),true);
    Result->SetBoolField(TEXT("packed_weight_normalization_exact"),A.NormalizationFailures==0&&B.NormalizationFailures==0);
    return Encode();
}

FString UWCCragstoatMeshAuditLibrary::ExportCragstoatSourceRenderWeights(USkeletalMesh* Source)
{
    auto Result=MakeShared<FJsonObject>();Result->SetBoolField(TEXT("valid"),false);
    Result->SetStringField(TEXT("status"),TEXT("EXACT_MESH_RENDER_WEIGHT_EXPORT_REJECTED"));
    Result->SetBoolField(TEXT("asset_mutations"),false);
    Result->SetStringField(TEXT("scope"),TEXT("Read-only exact Sage or private BodySkin_r002/r003 LOD0 actual 8-bit render weights grouped by MeshToImportVertexMap. Not original MeshDescription uint16 identity. External import-id/DynamicMesh position verification is required before an import-id preservation comparison or private rebase."));
    const auto Encode=[&](){FString Json;FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Json));return Json;};
    const auto Fail=[&](const TCHAR* Reason){Result->SetStringField(TEXT("failure"),Reason);return Encode();};
    if(!IsInGameThread()||!Source||(Source->GetPathName()!=SourcePath&&Source->GetPathName()!=CandidatePath2&&Source->GetPathName()!=CandidatePath3&&Source->GetPathName()!=ParentTransitionPath))return Fail(TEXT("Requires game-thread exact approved Sage or an explicitly allowed private BodySkin mesh"));
    Result->SetStringField(TEXT("source_asset"),Source->GetPathName());
    if(Source->IsCompiling())return Fail(TEXT("Source render-data compilation active; no wait/rebuild performed"));
    FSnapshot Snapshot;FString Error;Result->SetObjectField(TEXT("source"),Snapshot.Json);
    if(!Capture(Source,Snapshot,Error)){Result->SetStringField(TEXT("failure"),Error);return Encode();}
    const auto* Skin=Snapshot.LOD->GetSkinWeightVertexBuffer();
    if(Skin->GetBoneWeightByteSize()!=1||Snapshot.NormalizationFailures!=0)return Fail(TEXT("Source must have actual normalized 8-bit renderer weights"));
    const auto* Imported=Source->GetImportedModel();
    if(!Imported||Imported->LODModels.IsEmpty())return Fail(TEXT("Editor imported LOD0 model unavailable"));
    const auto& Model=Imported->LODModels[0];const auto& Map=Model.MeshToImportVertexMap;
    const auto& Positions=Snapshot.LOD->StaticVertexBuffers.PositionVertexBuffer;const uint32 N=Positions.GetNumVertices();
    Result->SetNumberField(TEXT("render_vertices"),N);Result->SetNumberField(TEXT("import_map_entries"),Map.Num());
    Result->SetNumberField(TEXT("imported_model_max_import_vertex"),Model.MaxImportVertex);
    if(Map.Num()!=int32(N)||Model.NumVertices!=N)return Fail(TEXT("Imported map/model vertex count differs from actual render vertex count"));
    TMap<int32,uint32> Representative,Multiplicity;
    for(uint32 V=0;V<N;++V){
        const int32 Import=Map[V];if(Import<0){Result->SetNumberField(TEXT("rejected_render_vertex"),V);return Fail(TEXT("Negative import vertex id"));}
        const auto& Weights=Snapshot.Weights[V];uint32 Sum=0,ByteSum=0;
        for(const auto& Weight:Weights){
            if(Weight.Value==0||Weight.Value>65535||Weight.Value%257!=0){Result->SetNumberField(TEXT("rejected_render_vertex"),V);return Fail(TEXT("Actual weight is not a positive expanded 8-bit value"));}
            Sum+=Weight.Value;ByteSum+=Weight.Value/257;
        }
        if(Sum!=65535||ByteSum!=255){Result->SetNumberField(TEXT("rejected_render_vertex"),V);return Fail(TEXT("Expanded/byte weight normalization is not exact"));}
        if(const uint32* First=Representative.Find(Import)){
            const auto P=Positions.VertexPosition(V),Q=Positions.VertexPosition(*First);
            if(P.X!=Q.X||P.Y!=Q.Y||P.Z!=Q.Z||!SameWeights(Weights,Snapshot.Weights[*First])){
                Result->SetNumberField(TEXT("ambiguous_import_id"),Import);Result->SetNumberField(TEXT("first_render_vertex"),*First);Result->SetNumberField(TEXT("conflicting_render_vertex"),V);
                return Fail(TEXT("Duplicate import id has different actual rest coordinates or semantic render weights"));
            }
            ++Multiplicity.FindChecked(Import);
        }else{Representative.Add(Import,V);Multiplicity.Add(Import,1);}
    }
    TArray<int32> ImportIds;Representative.GetKeys(ImportIds);ImportIds.Sort();TArray<TSharedPtr<FJsonValue>> Rows;Rows.Reserve(ImportIds.Num());
    for(int32 Import:ImportIds){
        const uint32 V=Representative.FindChecked(Import);const auto P=Positions.VertexPosition(V);auto Row=MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("import_id"),Import);Row->SetNumberField(TEXT("first_render_vertex"),V);Row->SetNumberField(TEXT("render_vertex_count"),Multiplicity.FindChecked(Import));
        TArray<TSharedPtr<FJsonValue>> Coordinates;for(double C:{double(P.X),double(P.Y),double(P.Z)})Coordinates.Add(MakeShared<FJsonValueNumber>(C));Row->SetArrayField(TEXT("rest_cm"),Coordinates);
        auto Expanded=MakeShared<FJsonObject>(),Bytes=MakeShared<FJsonObject>();
        for(const auto& Weight:Snapshot.Weights[V]){Expanded->SetNumberField(Weight.Name.ToString(),Weight.Value);Bytes->SetNumberField(Weight.Name.ToString(),Weight.Value/257);}
        Row->SetObjectField(TEXT("expanded_uint16_by_bone"),Expanded);Row->SetObjectField(TEXT("byte_weights_by_bone"),Bytes);Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Result->SetNumberField(TEXT("unique_import_rows"),ImportIds.Num());Result->SetNumberField(TEXT("duplicate_render_vertices"),N-ImportIds.Num());
    Result->SetBoolField(TEXT("duplicate_import_positions_and_weights_exact"),true);Result->SetBoolField(TEXT("expanded_weights_multiple_of_257"),true);
    Result->SetBoolField(TEXT("expanded_and_byte_normalization_exact"),true);Result->SetBoolField(TEXT("requires_external_dynamic_mesh_position_verification"),true);
    Result->SetArrayField(TEXT("rows"),Rows);Result->SetStringField(TEXT("status"),TEXT("READONLY_EXACT_MESH_RENDER_BYTE_WEIGHTS_EXPORTED_REQUIRES_IMPORT_ID_POSITION_VERIFICATION"));
    Result->SetBoolField(TEXT("valid"),true);return Encode();
}
