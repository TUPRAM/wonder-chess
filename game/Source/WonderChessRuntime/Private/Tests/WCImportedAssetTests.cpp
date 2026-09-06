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
#include "Misc/EngineVersion.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Serialization/JsonSerializer.h"
#include "SkinnedAssetCompiler.h"
#include "WCDefinitionRegistry.h"

namespace {
using Object = TSharedPtr<FJsonObject>;
using Value = TSharedPtr<FJsonValue>;
FString AssetPath(const FString &Folder, const FString &Name) {
  return Folder / Name + TEXT(".") + Name;
}
Value JsonValue(const Object &Object) {
  return MakeShared<FJsonValueObject>(Object);
}
double ScaleError(const FTransform &Transform) {
  return (Transform.GetScale3D() - FVector::OneVector).GetAbsMax();
}
void WriteReport(const Object &Report) {
  FString Text;
  FJsonSerializer::Serialize(Report.ToSharedRef(),
                             TJsonWriterFactory<>::Create(&Text));
  FString Directory;
  if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory))
    Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence");
  IFileManager::Get().MakeDirectory(*Directory, true);
  FFileHelper::SaveStringToFile(Text,
                                *(Directory / TEXT("imported-assets.json")));
}
} // namespace

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCImportedAssetContracts,
                                 "WonderChess.Assets.ImportedAlphaContracts",
                                 EAutomationTestFlags::EditorContext |
                                     EAutomationTestFlags::EngineFilter)
bool FWCImportedAssetContracts::RunTest(const FString &Parameters) {
  FString OnlyUnit, FolderOverride;
  FParse::Value(FCommandLine::Get(), TEXT("WCAssetOnly="), OnlyUnit);
  FParse::Value(FCommandLine::Get(), TEXT("WCAssetFolder="), FolderOverride);
  if (!FolderOverride.IsEmpty() && OnlyUnit.IsEmpty()) {
    AddError(TEXT("WCAssetFolder requires WCAssetOnly so a probe cannot mix "
                  "multiple heroes in one folder."));
    return false;
  }
  wc::Catalog Catalog;
  FWCDefinitionText Text;
  FString Error;
  if (!TestTrue(TEXT("Load canonical asset and gameplay definitions"),
                wc::LoadCatalog(Catalog, Error, &Text))) {
    AddError(Error);
    return false;
  }
  const TArray<FName> RequiredBones = {
      TEXT("root"),       TEXT("pelvis"),      TEXT("spine_01"),
      TEXT("spine_02"),   TEXT("spine_03"),    TEXT("neck"),
      TEXT("head"),       TEXT("clavicle_l"),  TEXT("upperarm_l"),
      TEXT("lowerarm_l"), TEXT("hand_l"),      TEXT("thigh_l"),
      TEXT("calf_l"),     TEXT("foot_l"),      TEXT("toe_l"),
      TEXT("clavicle_r"), TEXT("upperarm_r"),  TEXT("lowerarm_r"),
      TEXT("hand_r"),     TEXT("thigh_r"),     TEXT("calf_r"),
      TEXT("foot_r"),     TEXT("toe_r"),       TEXT("weapon_r"),
      TEXT("weapon_l"),   TEXT("cast_origin"), TEXT("head_ui")};
  auto Report = MakeShared<FJsonObject>();
  Report->SetStringField(TEXT("only_unit"), OnlyUnit);
  Report->SetStringField(TEXT("folder_override"), FolderOverride);
  Report->SetStringField(
      TEXT("animation_sampling_boundary"),
      TEXT("runtime_root uses GetBoneTransform with bUseRawData=false, which "
           "requests compressed sampling but may fall back to raw data. "
           "raw_root explicitly requests raw sampling; compressed-data "
           "validity is recorded per clip."));
  Report->SetStringField(
      TEXT("texture_dimension_boundary"),
      TEXT("Editor imported FTextureSource dimensions are authoritative here; "
           "render dimensions are recorded separately and may be zero under "
           "NullRHI. This does not prove cooked texture residency."));
  Report->SetStringField(
      TEXT("root_basis_boundary"),
      TEXT("A fixed uniform positive reference-root scale is recorded, while "
           "every sampled root must preserve the reference transform and "
           "sampled bone scales must preserve reference scales. Physical "
           "height, feet and forward direction still need measured scene "
           "validation."));
  Report->SetStringField(TEXT("utc"), FDateTime::UtcNow().ToIso8601());
  Report->SetStringField(TEXT("engine"), FEngineVersion::Current().ToString());
  Report->SetStringField(TEXT("catalog_digest"),
                         UTF8_TO_TCHAR(Catalog.contentDigest.c_str()));
  Report->SetStringField(
      TEXT("boundary"),
      TEXT("Actual imported skeletal assets and sampled animation transforms. "
           "This does not verify feet contact, deformation quality, silhouette "
           "attractiveness, retarget compatibility, or visual release "
           "alignment."));
  Report->SetStringField(
      TEXT("animation_duration_policy"),
      TEXT("Idle2s, Move1s, Hit0.4s, Defeat1s, Victory1.5s; "
           "Attack uses current source export preset max(0.6s, authored "
           "windup+0.4s); Active max(0.5s, authored cast+recovery)."));
  TArray<Value> Heroes;
  TSet<FString> Families;
  TSet<UAnimSequence *> UniqueAnimations;
  int LoadedMeshes = 0, AnimationReferences = 0, TransformSamples = 0;
  for (const auto &Unit : Catalog.units) {
    const FString Id = UTF8_TO_TCHAR(Unit.id.c_str());
    if (!OnlyUnit.IsEmpty() && OnlyUnit != Id)
      continue;
    const auto *Definition = Text.Units.Find(Id);
    if (!TestTrue(Id + TEXT(" canonical text present"),
                  Definition && Definition->IsValid()))
      continue;
    const auto &DefinitionJson = *Definition;
    const auto Budget = DefinitionJson->GetObjectField(TEXT("art_budget"));
    const auto Contract =
        DefinitionJson->GetObjectField(TEXT("animation_contract"));
    const FString Family = DefinitionJson->GetStringField(TEXT("rig_family"));
    const FString Folder =
        FolderOverride.IsEmpty()
            ? DefinitionJson->GetObjectField(TEXT("asset_paths"))
                  ->GetStringField(TEXT("unreal_folder"))
            : FolderOverride;
    Families.Add(Family);
    auto Hero = MakeShared<FJsonObject>();
    Hero->SetStringField(TEXT("id"), Id);
    Hero->SetStringField(TEXT("authored_rig_family"), Family);
    Hero->SetNumberField(TEXT("authored_height_m"),
                         DefinitionJson->GetNumberField(TEXT("height_m")));
    auto *Mesh = LoadObject<USkeletalMesh>(
        nullptr, *AssetPath(Folder, TEXT("SK_") + Id));
    Hero->SetBoolField(TEXT("mesh_loaded"), Mesh != nullptr);
    Heroes.Add(JsonValue(Hero));
    if (!TestNotNull(Id + TEXT(" skeletal mesh"), Mesh))
      continue;
    ++LoadedMeshes;
    TArray<USkinnedAsset *> Pending{Mesh};
    FSkinnedAssetCompilingManager::Get().FinishCompilation(Pending);
    Hero->SetStringField(TEXT("mesh"), Mesh->GetPathName());
    auto *Skeleton = Mesh->GetSkeleton();
    if (!TestNotNull(Id + TEXT(" skeleton"), Skeleton))
      continue;
    Hero->SetStringField(TEXT("skeleton"), Skeleton->GetPathName());
    const auto &Ref = Mesh->GetRefSkeleton();
    Hero->SetNumberField(TEXT("bones"), Ref.GetNum());
    TestEqual(Id + TEXT(" current authored 27-bone rig"), Ref.GetNum(),
              RequiredBones.Num());
    TestTrue(Id + TEXT(" deform bone budget"),
             Ref.GetNum() <=
                 Budget->GetIntegerField(TEXT("deform_bones_target_max")));
    const FName RootName(*Contract->GetStringField(TEXT("root_bone")));
    const int RootIndex = Ref.FindBoneIndex(RootName);
    TestEqual(Id + TEXT(" root is first imported bone"), RootIndex, 0);
    int Parentless = 0;
    TArray<Value> BoneNames;
    for (int BoneIndex = 0; BoneIndex < Ref.GetNum(); ++BoneIndex) {
      if (Ref.GetParentIndex(BoneIndex) == INDEX_NONE)
        ++Parentless;
      BoneNames.Add(
          MakeShared<FJsonValueString>(Ref.GetBoneName(BoneIndex).ToString()));
      if (BoneIndex != RootIndex)
        TestTrue(Id + TEXT(" reference scale ") +
                     Ref.GetBoneName(BoneIndex).ToString(),
                 ScaleError(Ref.GetRefBonePose()[BoneIndex]) < .001);
    }
    Hero->SetArrayField(TEXT("bone_names"), BoneNames);
    TestEqual(Id + TEXT(" single root"), Parentless, 1);
    for (const FName Bone : RequiredBones)
      TestTrue(Id + TEXT(" required bone ") + Bone.ToString(),
               Ref.FindBoneIndex(Bone) != INDEX_NONE);
    if (RootIndex >= 0) {
      const auto &Root = Ref.GetRefBonePose()[RootIndex];
      Hero->SetStringField(TEXT("reference_root_transform"), Root.ToString());
      const FVector RootScale = Root.GetScale3D();
      Hero->SetBoolField(TEXT("reference_root_normalized"),
                         ScaleError(Root) < .001 &&
                             Root.GetRotation().Equals(FQuat::Identity, .001));
      TestTrue(Id + TEXT(" reference root has uniform positive basis scale"),
               RootScale.X > 0 &&
                   FMath::Abs(RootScale.X - RootScale.Y) < .001 &&
                   FMath::Abs(RootScale.X - RootScale.Z) < .001);
      TestTrue(Id + TEXT(" reference root at ground origin"),
               Root.GetTranslation().IsNearlyZero(.01));
      const int SkeletonRoot =
          Skeleton->GetReferenceSkeleton().FindBoneIndex(RootName);
      if (TestTrue(Id + TEXT(" persisted skeleton has authored root"),
                   SkeletonRoot != INDEX_NONE)) {
        const auto &SkeletonPose =
            Skeleton->GetReferenceSkeleton().GetRefBonePose()[SkeletonRoot];
        Hero->SetStringField(TEXT("skeleton_reference_root_transform"),
                             SkeletonPose.ToString());
        Hero->SetBoolField(TEXT("skeleton_root_matches_mesh_reference"),
                           SkeletonPose.Equals(Root, .001));
        TestTrue(Id + TEXT(" persisted skeleton root matches mesh reference"),
                 SkeletonPose.Equals(Root, .001));
      }
    }
    const auto Bounds = Mesh->GetBounds();
    Hero->SetStringField(TEXT("imported_bounds_origin_cm"),
                         Bounds.Origin.ToString());
    Hero->SetStringField(TEXT("imported_bounds_extent_cm"),
                         Bounds.BoxExtent.ToString());
    const auto &Materials = Mesh->GetMaterials();
    Hero->SetNumberField(TEXT("material_slots"), Materials.Num());
    TestTrue(Id + TEXT(" one or two material slots"),
             Materials.Num() > 0 &&
                 Materials.Num() <=
                     Budget->GetIntegerField(TEXT("material_slots_max")));
    for (int Slot = 0; Slot < Materials.Num(); ++Slot)
      TestNotNull(Id + FString::Printf(TEXT(" material slot%d"), Slot),
                  Materials[Slot].MaterialInterface.Get());
    TestEqual(Id + TEXT(" three imported LODs"), Mesh->GetLODNum(), 3);
    const auto *Render = Mesh->GetResourceForRendering();
    if (TestNotNull(Id + TEXT(" skeletal render data"), Render)) {
      TestEqual(Id + TEXT(" three actual rendered LODs"),
                Render->LODRenderData.Num(), 3);
      TArray<Value> Lods;
      int PreviousTriangles = INT32_MAX;
      for (int LodIndex = 0; LodIndex < Render->LODRenderData.Num();
           ++LodIndex) {
        const auto &Lod = Render->LODRenderData[LodIndex];
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("lod"), LodIndex);
        Row->SetNumberField(TEXT("vertices"), Lod.GetNumVertices());
        const int Triangles = Lod.GetTotalFaces();
        Row->SetNumberField(TEXT("triangles"), Triangles);
        TestTrue(Id + FString::Printf(TEXT(" LOD%d nonempty reduced geometry"),
                                      LodIndex),
                 Lod.GetNumVertices() > 0 && Triangles > 0 &&
                     Triangles < PreviousTriangles);
        if (LodIndex == 0)
          TestTrue(Id + TEXT(" LOD0 triangle budget"),
                   Triangles <=
                       Budget->GetIntegerField(TEXT("lod0_triangles_max")));
        PreviousTriangles = Triangles;
        Lods.Add(JsonValue(Row));
      }
      Hero->SetArrayField(TEXT("lods"), Lods);
    }
    TArray<Value> Textures;
    for (const FString Suffix :
         {TEXT("BaseColor"), TEXT("Normal"), TEXT("ORM"), TEXT("Portrait")}) {
      auto TextureReport = MakeShared<FJsonObject>();
      TextureReport->SetStringField(TEXT("kind"), Suffix);
      auto *Texture = LoadObject<UTexture2D>(
          nullptr, *AssetPath(Folder, TEXT("T_") + Id + TEXT("_") + Suffix));
      TextureReport->SetBoolField(TEXT("loaded"), Texture != nullptr);
      Textures.Add(JsonValue(TextureReport));
      if (!TestNotNull(Id + TEXT(" texture ") + Suffix, Texture))
        continue;
      TextureReport->SetStringField(TEXT("path"), Texture->GetPathName());
      TextureReport->SetBoolField(TEXT("srgb"), Texture->SRGB);
      const bool SourceValid = Texture->Source.IsValid();
      const int64 Width = SourceValid ? Texture->Source.GetSizeX() : 0;
      const int64 Height = SourceValid ? Texture->Source.GetSizeY() : 0;
      TextureReport->SetBoolField(TEXT("imported_source_valid"), SourceValid);
      TextureReport->SetNumberField(TEXT("size_x"), Width);
      TextureReport->SetNumberField(TEXT("size_y"), Height);
      TextureReport->SetNumberField(TEXT("render_size_x"), Texture->GetSizeX());
      TextureReport->SetNumberField(TEXT("render_size_y"), Texture->GetSizeY());
      const bool ExpectedSRGB =
          Suffix == TEXT("BaseColor") || Suffix == TEXT("Portrait");
      TestEqual(Id + TEXT(" texture color space ") + Suffix,
                bool(Texture->SRGB), ExpectedSRGB);
      TestTrue(Id + TEXT(" texture has dimensions ") + Suffix,
               SourceValid && Width > 0 && Height > 0);
      if (Suffix == TEXT("Normal"))
        TestEqual(Id + TEXT(" normal compression"),
                  int(Texture->CompressionSettings), int(TC_Normalmap));
      if (Suffix == TEXT("Portrait"))
        TestTrue(Id + TEXT(" portrait resolution512..1024"),
                 Width >= 512 && Width <= 1024 && Height >= 512 &&
                     Height <= 1024);
      else if (!Materials.IsEmpty() && Materials[0].MaterialInterface) {
        UTexture *Bound = nullptr;
        const bool Found =
            Materials[0].MaterialInterface->GetTextureParameterValue(
                FHashedMaterialParameterInfo(FName(*Suffix)), Bound);
        TestTrue(Id + TEXT(" material references texture ") + Suffix,
                 Found && Bound == Texture);
        TextureReport->SetBoolField(TEXT("bound_to_material"),
                                    Found && Bound == Texture);
      }
    }
    Hero->SetArrayField(TEXT("textures"), Textures);
    TArray<Value> Clips;
    const auto &RequiredClips = Contract->GetArrayField(TEXT("required_clips"));
    TestEqual(Id + TEXT(" seven authored clip references"), RequiredClips.Num(),
              7);
    for (const auto &ClipValue : RequiredClips) {
      const FString Clip = ClipValue->AsString();
      auto Row = MakeShared<FJsonObject>();
      Row->SetStringField(TEXT("clip"), Clip);
      auto *Animation = LoadObject<UAnimSequence>(
          nullptr, *AssetPath(Folder, TEXT("AN_") + Id + TEXT("_") + Clip));
      Row->SetBoolField(TEXT("loaded"), Animation != nullptr);
      Clips.Add(JsonValue(Row));
      if (!TestNotNull(Id + TEXT(" animation ") + Clip, Animation))
        continue;
      ++AnimationReferences;
      UniqueAnimations.Add(Animation);
      Animation->WaitOnExistingCompression();
      Row->SetBoolField(TEXT("compressed_data_valid"),
                        Animation->IsCompressedDataValid());
      Row->SetStringField(TEXT("path"), Animation->GetPathName());
      TestTrue(Id + TEXT(" same skeleton ") + Clip,
               Animation->GetSkeleton() == Skeleton);
      TestFalse(Id + TEXT(" root motion disabled ") + Clip,
                Animation->HasRootMotion());
      const double Length = Animation->GetPlayLength();
      double ExpectedLength = 0;
      if (Clip == TEXT("Idle"))
        ExpectedLength = 2;
      else if (Clip == TEXT("Move") || Clip == TEXT("Defeat"))
        ExpectedLength = 1;
      else if (Clip == TEXT("Hit"))
        ExpectedLength = .4;
      else if (Clip == TEXT("Victory"))
        ExpectedLength = 1.5;
      else if (Clip == TEXT("Attack"))
        ExpectedLength = FMath::Max(.6, Unit.attackWindupMs / 1000.0 + .4);
      else if (Clip == TEXT("Active"))
        ExpectedLength = FMath::Max(
            .5, (Unit.ability.castMs + Unit.ability.recoveryMs) / 1000.0);
      Row->SetNumberField(TEXT("duration_seconds"), Length);
      Row->SetNumberField(TEXT("expected_duration_seconds"), ExpectedLength);
      TestTrue(Id + TEXT(" authored/export duration ") + Clip,
               ExpectedLength > 0 &&
                   FMath::Abs(Length - ExpectedLength) < .0001);
      const auto *Model = Animation->GetDataModel();
      if (TestNotNull(Id + TEXT(" imported animation data model ") + Clip,
                      Model)) {
        Row->SetNumberField(TEXT("source_frames_per_second"),
                            Model->GetFrameRate().AsDecimal());
        Row->SetNumberField(TEXT("source_keys"), Model->GetNumberOfKeys());
        TestTrue(Id + TEXT(" authored60fps ") + Clip,
                 FMath::Abs(Model->GetFrameRate().AsDecimal() -
                            Contract->GetNumberField(TEXT("fps"))) < .001);
      }
      double MaxRootTranslation = 0, MaxRootRotation = 0, MaxScale = 0,
             MaxRootTranslationDelta = 0, MaxRootRotationDelta = 0,
             MaxScaleDelta = 0;
      TArray<Value> RootSamples;
      bool Finite = true;
      TArray<double> Times{0, Length * .25, Length * .5, Length * .75, Length};
      if (Clip == TEXT("Attack"))
        Times.Add(Unit.attackWindupMs / 1000.0);
      if (Clip == TEXT("Active"))
        Times.Add(Unit.ability.castMs / 1000.0);
      const auto &SkeletonRef = Skeleton->GetReferenceSkeleton();
      for (double Time : Times)
        for (int BoneIndex = 0; BoneIndex < SkeletonRef.GetNum(); ++BoneIndex) {
          FTransform Transform;
          Animation->GetBoneTransform(Transform,
                                      FSkeletonPoseBoneIndex(BoneIndex),
                                      FAnimExtractContext(Time), false);
          ++TransformSamples;
          Finite = Finite && !Transform.ContainsNaN();
          MaxScale = FMath::Max(MaxScale, ScaleError(Transform));
          const int MeshBoneIndex =
              Ref.FindBoneIndex(SkeletonRef.GetBoneName(BoneIndex));
          if (MeshBoneIndex != INDEX_NONE)
            MaxScaleDelta =
                FMath::Max(MaxScaleDelta,
                           (Transform.GetScale3D() -
                            Ref.GetRefBonePose()[MeshBoneIndex].GetScale3D())
                               .GetAbsMax());
          if (SkeletonRef.GetBoneName(BoneIndex) == RootName) {
            MaxRootTranslation = FMath::Max(MaxRootTranslation,
                                            Transform.GetTranslation().Size());
            MaxRootRotation = FMath::Max(
                MaxRootRotation,
                Transform.GetRotation().AngularDistance(FQuat::Identity));
            if (RootIndex >= 0) {
              const FTransform &ReferenceRoot = Ref.GetRefBonePose()[RootIndex];
              MaxRootTranslationDelta = FMath::Max(
                  MaxRootTranslationDelta,
                  (Transform.GetTranslation() - ReferenceRoot.GetTranslation())
                      .Size());
              MaxRootRotationDelta = FMath::Max(
                  MaxRootRotationDelta, Transform.GetRotation().AngularDistance(
                                            ReferenceRoot.GetRotation()));
            }
            FTransform RawRoot;
            Animation->GetBoneTransform(RawRoot,
                                        FSkeletonPoseBoneIndex(BoneIndex),
                                        FAnimExtractContext(Time), true);
            auto Sample = MakeShared<FJsonObject>();
            Sample->SetNumberField(TEXT("time_seconds"), Time);
            Sample->SetStringField(TEXT("runtime_root"), Transform.ToString());
            Sample->SetStringField(TEXT("raw_root"), RawRoot.ToString());
            RootSamples.Add(JsonValue(Sample));
          }
        }
      Row->SetNumberField(TEXT("sampled_times"), Times.Num());
      Row->SetNumberField(TEXT("max_root_translation_cm"), MaxRootTranslation);
      Row->SetNumberField(TEXT("max_root_rotation_radians"), MaxRootRotation);
      Row->SetNumberField(TEXT("max_bone_scale_error"), MaxScale);
      Row->SetNumberField(TEXT("max_bone_scale_delta_from_reference"),
                          MaxScaleDelta);
      Row->SetNumberField(TEXT("max_root_translation_delta_from_reference_cm"),
                          MaxRootTranslationDelta);
      Row->SetNumberField(
          TEXT("max_root_rotation_delta_from_reference_radians"),
          MaxRootRotationDelta);
      Row->SetArrayField(TEXT("root_samples"), RootSamples);
      TestTrue(Id + TEXT(" sampled finite pose ") + Clip, Finite);
      TestTrue(Id + TEXT(" sampled bone scales match reference ") + Clip,
               MaxScaleDelta < .001);
      TestTrue(Id + TEXT(" sampled root matches reference basis ") + Clip,
               MaxRootTranslationDelta < .01 && MaxRootRotationDelta < .001);
    }
    Hero->SetArrayField(TEXT("clips"), Clips);
  }
  const int ExpectedHeroes = OnlyUnit.IsEmpty() ? int(Catalog.units.size()) : 1;
  TestEqual(TEXT("All selected skeletal meshes loaded"), LoadedMeshes,
            ExpectedHeroes);
  TestEqual(TEXT("All selected hero animation references loaded"),
            AnimationReferences, ExpectedHeroes * 7);
  TestEqual(TEXT("Expected declared rig families"), Families.Num(),
            OnlyUnit.IsEmpty() ? 6 : 1);
  Report->SetNumberField(TEXT("loaded_meshes"), LoadedMeshes);
  Report->SetNumberField(TEXT("animation_references"), AnimationReferences);
  Report->SetNumberField(TEXT("unique_animation_assets"),
                         UniqueAnimations.Num());
  Report->SetNumberField(TEXT("sampled_bone_transforms"), TransformSamples);
  Report->SetArrayField(TEXT("heroes"), Heroes);
  Report->SetBoolField(TEXT("passed"), !HasAnyErrors());
  WriteReport(Report);
  return !HasAnyErrors();
}
#endif
