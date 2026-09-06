#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Animation/AnimData/IAnimationDataModel.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Texture2D.h"
#include "HAL/FileManager.h"
#include "Materials/MaterialInterface.h"
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Serialization/JsonSerializer.h"
#include "SkinnedAssetCompiler.h"
#include "WCDefinitionRegistry.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCNeutralAssetContracts,
    "WonderChess.Assets.ImportedNeutralContracts",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FWCNeutralAssetContracts::RunTest(const FString &) {
  wc::Catalog Catalog;
  FString Error;
  if (!TestTrue(TEXT("Load canonical neutral catalog"), wc::LoadCatalog(Catalog, Error))) {
    AddError(Error);
    return false;
  }
  auto Report = MakeShared<FJsonObject>();
  Report->SetStringField(TEXT("utc"), FDateTime::UtcNow().ToIso8601());
  Report->SetStringField(TEXT("digest"), UTF8_TO_TCHAR(Catalog.contentDigest.c_str()));
  Report->SetStringField(TEXT("boundary"), TEXT("Cold editor import and every authored frame transform sampled; this does not certify continuous visual playback or cooked residency."));
  TArray<TSharedPtr<FJsonValue>> Entries;
  int MeshCount = 0, ClipCount = 0, PoseSamples = 0;
  for (const auto &Unit : Catalog.neutrals) {
    const FString Id = UTF8_TO_TCHAR(Unit.id.c_str());
    const FString Folder = TEXT("/Game/WonderChess/Neutrals/") + Id;
    auto Path = [&](const FString &Name) { return Folder / Name + TEXT(".") + Name; };
    auto Entry = MakeShared<FJsonObject>();
    Entry->SetStringField(TEXT("id"), Id);
    Entries.Add(MakeShared<FJsonValueObject>(Entry));
    FString ManifestText;
    TSharedPtr<FJsonObject> Manifest;
    const FString ManifestPath = FPaths::ProjectDir() / TEXT("../exports/neutrals/") / Id / TEXT("export_manifest.json");
    if (!TestTrue(Id + TEXT(" source manifest readable"), FFileHelper::LoadFileToString(ManifestText, *ManifestPath)
        && FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ManifestText), Manifest))) continue;
    auto *Mesh = LoadObject<USkeletalMesh>(nullptr, *Path(TEXT("SK_") + Id));
    if (!TestNotNull(Id + TEXT(" skeletal mesh"), Mesh)) continue;
    ++MeshCount;
    TArray<USkinnedAsset *> Pending{Mesh};
    FSkinnedAssetCompilingManager::Get().FinishCompilation(Pending);
    auto *Skeleton = Mesh->GetSkeleton();
    if (!TestNotNull(Id + TEXT(" mechanical skeleton"), Skeleton)) continue;
    const auto &Ref = Mesh->GetRefSkeleton();
    TestEqual(Id + TEXT(" authored bone count"), Ref.GetNum(), Manifest->GetIntegerField(TEXT("bones")));
    for (const auto &Bone : Manifest->GetArrayField(TEXT("rig_bones")))
      TestTrue(Id + TEXT(" authored bone ") + Bone->AsString(), Ref.FindBoneIndex(FName(*Bone->AsString())) >= 0);
    TestEqual(Id + TEXT(" root at index zero"), Ref.FindBoneIndex(TEXT("root")), 0);
    TestTrue(Id + TEXT(" skeleton root agrees with mesh"), Ref.GetNum() > 0 && Skeleton->GetReferenceSkeleton().GetNum() > 0
        && Ref.GetRefBonePose()[0].Equals(Skeleton->GetReferenceSkeleton().GetRefBonePose()[0], .001));
    TestEqual(Id + TEXT(" three LODs"), Mesh->GetLODNum(), 3);
    const auto *Render = Mesh->GetResourceForRendering();
    if (TestNotNull(Id + TEXT(" rendered geometry"), Render)) {
      int Last = MAX_int32;
      for (const auto &Lod : Render->LODRenderData) {
        TestTrue(Id + TEXT(" LOD geometry strictly reduces"), Lod.GetTotalFaces() > 0 && Lod.GetTotalFaces() < Last);
        Last = Lod.GetTotalFaces();
      }
    }
    const double SourceHeight = Manifest->GetArrayField(TEXT("measured_rest_dimensions_m"))[2]->AsNumber() * 100;
    const double ImportedHeight = Mesh->GetBounds().BoxExtent.Z * 2;
    Entry->SetNumberField(TEXT("height_cm"), ImportedHeight);
    TestTrue(Id + TEXT(" physical height agrees with Blender"), FMath::Abs(ImportedHeight - SourceHeight) < 1.0);
    TestTrue(Id + TEXT(" material assigned"), Mesh->GetMaterials().Num() == 1 && Mesh->GetMaterials()[0].MaterialInterface);
    for (const FString Kind : {TEXT("BaseColor"), TEXT("Normal"), TEXT("ORM"), TEXT("Portrait")}) {
      auto *Texture = LoadObject<UTexture2D>(nullptr, *Path(TEXT("T_") + Id + TEXT("_") + Kind));
      if (!TestNotNull(Id + TEXT(" texture ") + Kind, Texture)) continue;
      const int ExpectedSize = Kind == TEXT("Portrait") ? 640 : 1024;
      TestTrue(Id + TEXT(" source texture dimensions ") + Kind, Texture->Source.IsValid()
          && Texture->Source.GetSizeX() == ExpectedSize && Texture->Source.GetSizeY() == ExpectedSize);
      TestEqual(Id + TEXT(" texture color space ") + Kind, bool(Texture->SRGB), Kind == TEXT("BaseColor") || Kind == TEXT("Portrait"));
      if (Kind == TEXT("Normal")) TestEqual(Id + TEXT(" normal compression"), int(Texture->CompressionSettings), int(TC_Normalmap));
      if (Kind != TEXT("Portrait") && !Mesh->GetMaterials().IsEmpty() && Mesh->GetMaterials()[0].MaterialInterface) {
        UTexture *Bound = nullptr;
        TestTrue(Id + TEXT(" material texture binding ") + Kind,
            Mesh->GetMaterials()[0].MaterialInterface->GetTextureParameterValue(FHashedMaterialParameterInfo(FName(*Kind)), Bound) && Bound == Texture);
      }
    }
    TArray<FString> Required{TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Hit"), TEXT("Defeat")};
    if (!Unit.ability.effects.empty()) Required.Add(TEXT("Active"));
    TArray<TSharedPtr<FJsonValue>> Clips;
    for (const FString &Clip : Required) {
      auto *Animation = LoadObject<UAnimSequence>(nullptr, *Path(TEXT("AN_") + Id + TEXT("_") + Clip));
      if (!TestNotNull(Id + TEXT(" clip ") + Clip, Animation)) continue;
      ++ClipCount;
      Animation->WaitOnExistingCompression();
      TestTrue(Id + TEXT(" clip skeleton ") + Clip, Animation->GetSkeleton() == Skeleton);
      TestFalse(Id + TEXT(" no root motion ") + Clip, Animation->HasRootMotion());
      const auto SourceClip = Manifest->GetObjectField(TEXT("clips"))->GetObjectField(Clip);
      const auto Frames = SourceClip->GetArrayField(TEXT("frames"));
      const double Length = (Frames[1]->AsNumber() - Frames[0]->AsNumber()) / SourceClip->GetNumberField(TEXT("fps"));
      TestTrue(Id + TEXT(" clip duration ") + Clip, FMath::Abs(Animation->GetPlayLength() - Length) < .0001);
      const auto *Model = Animation->GetDataModel();
      if (!TestNotNull(Id + TEXT(" authored animation data ") + Clip, Model)) continue;
      TestTrue(Id + TEXT(" clip authored60fps ") + Clip, FMath::Abs(Model->GetFrameRate().AsDecimal() - 60) < .001);
      bool Finite = true;
      double MaxScale = 0, RootTranslation = 0, RootRotation = 0;
      for (int Frame = 0; Frame < Model->GetNumberOfKeys(); ++Frame) {
        const double Time = FMath::Min(Length, Frame / 60.0);
        for (int Bone = 0; Bone < Ref.GetNum(); ++Bone) {
          FTransform Pose;
          Animation->GetBoneTransform(Pose, FSkeletonPoseBoneIndex(Bone), FAnimExtractContext(Time), false);
          ++PoseSamples;
          Finite &= !Pose.ContainsNaN();
          MaxScale = FMath::Max(MaxScale, (Pose.GetScale3D() - Ref.GetRefBonePose()[Bone].GetScale3D()).GetAbsMax());
          if (Bone == 0) {
            RootTranslation = FMath::Max(RootTranslation, (Pose.GetTranslation() - Ref.GetRefBonePose()[0].GetTranslation()).Size());
            RootRotation = FMath::Max(RootRotation, Pose.GetRotation().AngularDistance(Ref.GetRefBonePose()[0].GetRotation()));
          }
        }
      }
      TestTrue(Id + TEXT(" all frames finite ") + Clip, Finite);
      TestTrue(Id + TEXT(" all frames preserve bone scale ") + Clip, MaxScale < .001);
      TestTrue(Id + TEXT(" all frames preserve root basis ") + Clip, RootTranslation < .01 && RootRotation < .001);
      auto Row = MakeShared<FJsonObject>();
      Row->SetStringField(TEXT("clip"), Clip);
      Row->SetNumberField(TEXT("keys"), Model->GetNumberOfKeys());
      Row->SetNumberField(TEXT("duration_seconds"), Length);
      Row->SetNumberField(TEXT("max_scale_delta"), MaxScale);
      Row->SetNumberField(TEXT("max_root_translation_cm"), RootTranslation);
      Row->SetNumberField(TEXT("max_root_rotation_radians"), RootRotation);
      Row->SetBoolField(TEXT("compressed_data_valid"), Animation->IsCompressedDataValid());
      Clips.Add(MakeShared<FJsonValueObject>(Row));
    }
    Entry->SetArrayField(TEXT("clips"), Clips);
  }
  TestEqual(TEXT("All seven neutral meshes"), MeshCount, 7);
  TestEqual(TEXT("Forty authored neutral clips"), ClipCount, 40);
  Report->SetArrayField(TEXT("neutrals"), Entries);
  Report->SetNumberField(TEXT("meshes"), MeshCount);
  Report->SetNumberField(TEXT("clips"), ClipCount);
  Report->SetNumberField(TEXT("sampled_bone_transforms"), PoseSamples);
  Report->SetBoolField(TEXT("passed"), !HasAnyErrors());
  FString Directory, Json;
  if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory)) Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence");
  IFileManager::Get().MakeDirectory(*Directory, true);
  FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Json));
  TestTrue(TEXT("Write neutral evidence"), FFileHelper::SaveStringToFile(Json, *(Directory / TEXT("imported-neutrals.json"))));
  return !HasAnyErrors();
}
#endif
