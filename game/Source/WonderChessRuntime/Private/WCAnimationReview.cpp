#include "WCAnimationReview.h"
#include "WCMatchRuntime.h"
#include "WCFrontEndScene.h"
#include "WCBoardPresenter.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "ContentStreaming.h"
#include "Engine/Texture.h"
#include "HAL/FileManager.h"
#include "Materials/MaterialInterface.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace {
using Object = TSharedPtr<FJsonObject>;
struct MotionCapture {
  bool Started = false, Finished = false, Pending = false, Failed = false;
  bool PreviousFixed = false;
  double PreviousDelta = 0, StartWall = 0, TextureWaitStart = 0;
  int Index = 0, Frame = 0, FramesRequired = 0, Warmup = 0;
  FString Directory, PendingPath, ClipDirectory;
  TArray<TPair<FString, FString>> Jobs;
  TArray<TSharedPtr<FJsonValue>> Clips;
  TWeakObjectPtr<USkeletalMeshComponent> Mesh;
  Object Report, Current;
  FDelegateHandle ProcessedHandle;
};
MotionCapture Capture;
constexpr double CaptureStep = 1.0 / 20.0;

void WriteReport() {
  FString Json;
  Capture.Report->SetArrayField(TEXT("clips"), Capture.Clips);
  FJsonSerializer::Serialize(Capture.Report.ToSharedRef(), TJsonWriterFactory<>::Create(&Json));
  FFileHelper::SaveStringToFile(Json, *(Capture.Directory / TEXT("engine-motion.json")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
void Finish(const FString& Status) {
  Capture.Finished = true;
  Capture.Report->SetStringField(TEXT("status"), Status);
  Capture.Report->SetNumberField(TEXT("elapsed_wall_seconds"), FPlatformTime::Seconds() - Capture.StartWall);
  Capture.Report->SetStringField(TEXT("finished_utc"), FDateTime::UtcNow().ToIso8601());
  WriteReport();
  FScreenshotRequest::OnScreenshotRequestProcessed().Remove(Capture.ProcessedHandle);
  FApp::SetUseFixedTimeStep(Capture.PreviousFixed);
  FApp::SetFixedDeltaTime(Capture.PreviousDelta);
  FPlatformMisc::RequestExitWithStatus(false, Capture.Failed ? 2 : 0);
}
void ScreenshotProcessed() {
  if (!Capture.Pending || Capture.Finished) return;
  Capture.Pending = false;
  const auto* Mesh = Capture.Mesh.Get();
  const auto* Animation = Mesh ? Mesh->GetSingleNodeInstance() : nullptr;
  const int64 Bytes = IFileManager::Get().FileSize(*Capture.PendingPath);
  if (!Animation || Bytes <= 0) {
    Capture.Failed = true;
    Capture.Current->SetStringField(TEXT("status"), TEXT("FAIL_SCREENSHOT_OR_ANIMATION"));
  }
  const FString Row = FString::Printf(TEXT("%d,%.9f,%.9f,%lld,%s\n"), Capture.Frame,
      Animation ? Animation->GetCurrentTime() : -1.f, FPlatformTime::Seconds(), Bytes,
      *FPaths::GetCleanFilename(Capture.PendingPath));
  FFileHelper::SaveStringToFile(Row, *(Capture.ClipDirectory / TEXT("frames.csv")),
      FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append);
  ++Capture.Frame;
}
}

void WCTickAnimationReview(AWCMatchController* Player) {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCReviewMotion")) || Capture.Finished ||
      !Player || !Player->IsLocalController() || !Player->Presenter) return;
  auto* HUD = Cast<AWCMatchHUD>(Player->GetHUD());
  auto* Scene = Cast<AWCFrontEndScene>(Player->GetViewTarget());
  if (!Capture.Started) {
    if (!HUD || !Scene || Player->Presenter->Definitions.units.empty()) return;
    Capture.Started = true;
    Capture.StartWall = FPlatformTime::Seconds();
    Capture.Report = MakeShared<FJsonObject>();
    Capture.Report->SetStringField(TEXT("status"), TEXT("RECORDING"));
    Capture.Report->SetStringField(TEXT("started_utc"), FDateTime::UtcNow().ToIso8601());
    Capture.Report->SetStringField(TEXT("content_digest"), UTF8_TO_TCHAR(Player->Presenter->Definitions.contentDigest.c_str()));
    Capture.Report->SetStringField(TEXT("method"), TEXT("Actual Unreal gallery viewport, all rendered frames over a clip cycle at fixed 20Hz game steps. Movie playback at20fps restores authored timeline speed. Offline capture, not wall-clock performance, manual input, audiovisual approval or continuous human review."));
    Capture.Report->SetNumberField(TEXT("playback_fps"), 20);
    if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Capture.Directory)) {
      Capture.Directory = FPaths::ProjectSavedDir() / TEXT("AnimationReview") / FDateTime::UtcNow().ToString(TEXT("%Y%m%dT%H%M%S"));
    }
    Capture.Directory = FPaths::ConvertRelativePathToFull(Capture.Directory);
    IFileManager::Get().MakeDirectory(*Capture.Directory, true);
    if (IFileManager::Get().FileExists(*(Capture.Directory / TEXT("engine-motion.json"))) ||
        FParse::Param(FCommandLine::Get(), TEXT("WCExercise")) || FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndAudit")) ||
        FParse::Param(FCommandLine::Get(), TEXT("WCProfile")) || FParse::Param(FCommandLine::Get(), TEXT("WCAutoStart"))) {
      Capture.Failed = Capture.Finished = true;
      UE_LOG(LogTemp, Error, TEXT("Motion review requires fresh evidence and no match, profiling or other audit."));
      FPlatformMisc::RequestExitWithStatus(false, 2); return;
    }
    FString RequestedHero, RequestedClip;
    FParse::Value(FCommandLine::Get(), TEXT("WCReviewHero="), RequestedHero);
    FParse::Value(FCommandLine::Get(), TEXT("WCReviewClip="), RequestedClip);
    for (const auto& Unit : Player->Presenter->Definitions.units) {
      const FString Id = UTF8_TO_TCHAR(Unit.id.c_str());
      if (!RequestedHero.IsEmpty() && RequestedHero != Id) continue;
      for (const FString Clip : {TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Active"), TEXT("Hit"), TEXT("Defeat"), TEXT("Victory")})
        if (RequestedClip.IsEmpty() || RequestedClip == Clip) Capture.Jobs.Add({Id, Clip});
    }
    Capture.Report->SetNumberField(TEXT("requested_clips"), Capture.Jobs.Num());
    Capture.PreviousFixed = FApp::UseFixedTimeStep(); Capture.PreviousDelta = FApp::GetFixedDeltaTime();
    FApp::SetFixedDeltaTime(CaptureStep); FApp::SetUseFixedTimeStep(true);
    Capture.ProcessedHandle = FScreenshotRequest::OnScreenshotRequestProcessed().AddStatic(&ScreenshotProcessed);
    if (Capture.Jobs.IsEmpty()) { Capture.Failed = true; Finish(TEXT("FAIL_EMPTY_SELECTION")); return; }
    WriteReport();
  }
  if (FPlatformTime::Seconds() - Capture.StartWall > 3600) { Capture.Failed = true; Finish(TEXT("FAIL_TIMEOUT")); return; }
  if (Capture.Pending || FScreenshotRequest::IsScreenshotRequested()) return;
  if (Capture.Current.IsValid() && Capture.Frame >= Capture.FramesRequired && Capture.Warmup == 0) {
    Capture.Current->SetNumberField(TEXT("captured_frames"), Capture.Frame);
    if (!Capture.Current->HasField(TEXT("status"))) Capture.Current->SetStringField(TEXT("status"), TEXT("CAPTURED_REVIEW_PENDING"));
    Capture.Current.Reset(); Capture.Mesh.Reset(); ++Capture.Index; WriteReport();
  }
  if (Capture.Index >= Capture.Jobs.Num()) { Finish(Capture.Failed ? TEXT("PARTIAL_CAPTURE_FAILURE") : TEXT("CAPTURED_REVIEW_PENDING")); return; }
  if (!Capture.Current.IsValid()) {
    const auto& Job = Capture.Jobs[Capture.Index];
    Capture.Current = MakeShared<FJsonObject>(); Capture.Clips.Add(MakeShared<FJsonValueObject>(Capture.Current));
    Capture.Current->SetStringField(TEXT("hero"), Job.Key); Capture.Current->SetStringField(TEXT("clip"), Job.Value);
    Capture.ClipDirectory = Capture.Directory / Job.Key / Job.Value;
    Capture.Current->SetStringField(TEXT("frames_directory"), Capture.ClipDirectory);
    Capture.Frame = Capture.FramesRequired = Capture.Warmup = 0;
    if (!HUD || !HUD->SelectPreviewForReview(Job.Key, Job.Value)) {
      Capture.Current->SetStringField(TEXT("status"), TEXT("MISSING_PREVIEW_ASSET")); Capture.Failed = true; return;
    }
    Scene = Cast<AWCFrontEndScene>(Player->GetViewTarget());
    Capture.Mesh = Scene ? Scene->FindComponentByClass<USkeletalMeshComponent>() : nullptr;
    auto* Instance = Capture.Mesh.IsValid() ? Capture.Mesh->GetSingleNodeInstance() : nullptr;
    const auto* Animation = Instance ? Cast<UAnimSequence>(Instance->GetCurrentAsset()) : nullptr;
    if (!Animation || Animation->GetPlayLength() <= 0) {
      Capture.Current->SetStringField(TEXT("status"), TEXT("MISSING_ANIMATION")); Capture.Failed = true; return;
    }
    Capture.Current->SetStringField(TEXT("animation_asset"), Animation->GetPathName());
    Capture.Current->SetNumberField(TEXT("clip_seconds"), Animation->GetPlayLength());
    Capture.FramesRequired = FMath::CeilToInt(Animation->GetPlayLength() / CaptureStep) + 1;
    Capture.Current->SetNumberField(TEXT("required_frames"), Capture.FramesRequired);
    TArray<FString> Existing;
    IFileManager::Get().FindFiles(Existing, *(Capture.ClipDirectory / TEXT("*")), true, false);
    if (!Existing.IsEmpty()) {
      Capture.Current->SetStringField(TEXT("status"), TEXT("FAIL_EXISTING_CLIP_EVIDENCE"));
      Capture.Failed = true; Capture.FramesRequired = 0; return;
    }
    IFileManager::Get().MakeDirectory(*Capture.ClipDirectory, true);
    FFileHelper::SaveStringToFile(TEXT("frame,animation_seconds,wall_seconds,bytes,file\n"), *(Capture.ClipDirectory / TEXT("frames.csv")), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    Capture.Mesh->PrestreamTextures(60.f, true);
    Capture.TextureWaitStart = FPlatformTime::Seconds();
    Capture.Warmup = 6; return;
  }
  if (Capture.Warmup > 0) {
    if (Capture.Warmup == 6 && Capture.Mesh.IsValid()) {
      IStreamingManager::Get().StreamAllResources(.01f);
      TArray<UTexture*> Textures;
      for (auto* Material : Capture.Mesh->GetMaterials()) if (Material) {
        TArray<UTexture*> MaterialTextures;
        Material->GetUsedTextures(MaterialTextures);
        for (auto* Texture : MaterialTextures) Textures.AddUnique(Texture);
      }
      TArray<FString> PendingTextures, TexturePaths;
      for (auto* Texture : Textures) {
        const FString Path = Texture ? Texture->GetPathName() : TEXT("<null>");
        TexturePaths.AddUnique(Path);
        bool Ready = Texture && Texture->GetResource() && Texture->IsFullyStreamedIn();
#if WITH_EDITOR
        Ready = Ready && !Texture->IsCompiling();
#endif
        if (!Ready) PendingTextures.AddUnique(Path);
      }
      const double WaitSeconds = FPlatformTime::Seconds() - Capture.TextureWaitStart;
      Capture.Current->SetNumberField(TEXT("texture_ready_wait_seconds"), WaitSeconds);
      Capture.Current->SetStringField(TEXT("used_textures"), FString::Join(TexturePaths, TEXT(";")));
      if (Textures.IsEmpty() || !PendingTextures.IsEmpty()) {
        Capture.Current->SetStringField(TEXT("pending_textures"), FString::Join(PendingTextures, TEXT(";")));
        if (WaitSeconds >= 30) {
          Capture.Current->SetStringField(TEXT("status"), TEXT("FAIL_TEXTURE_STREAMING_TIMEOUT"));
          Capture.Failed = true; Finish(TEXT("FAIL_TEXTURE_STREAMING_TIMEOUT"));
        }
        return;
      }
      Capture.Current->RemoveField(TEXT("pending_textures"));
      Capture.Current->SetBoolField(TEXT("textures_fully_streamed_before_capture"), true);
    }
    if (--Capture.Warmup == 0 && Capture.Mesh.IsValid()) Capture.Mesh->SetPosition(0, false);
    return;
  }
  Capture.PendingPath = Capture.ClipDirectory / FString::Printf(TEXT("frame-%05d.png"), Capture.Frame);
  Capture.Pending = true;
  FScreenshotRequest::RequestScreenshot(Capture.PendingPath, true, false);
}
