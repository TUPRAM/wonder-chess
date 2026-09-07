#include "WCFrontEnd.h"
#include "WCFrontEndScene.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "WCVerification.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "ContentStreaming.h"
#include "Dom/JsonObject.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/WorldSettings.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#include "ShaderCompiler.h"
#endif

namespace {
FString ProfileAssetPath(const FString& Id, const FString& Name) {
  return TEXT("/Game/WonderChess/Heroes/") + Id + TEXT("/") + Name + TEXT(".") + Name;
}
FString ProfileEncode(const TSharedRef<FJsonObject>& Value) {
  FString Text;
  FJsonSerializer::Serialize(Value, TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Text));
  return Text;
}
TSharedRef<FJsonObject> ResidentState(const FString& Id, const FString& Clip) {
  auto Value = MakeShared<FJsonObject>();
  const FString MeshPath = ProfileAssetPath(Id, TEXT("SK_") + Id);
  const FString ClipPath = ProfileAssetPath(Id, TEXT("AN_") + Id + TEXT("_") + Clip);
  Value->SetStringField(TEXT("mesh_path"), MeshPath);
  Value->SetStringField(TEXT("clip_path"), ClipPath);
  Value->SetBoolField(TEXT("mesh_object_resident"), FindObject<USkeletalMesh>(nullptr, *MeshPath) != nullptr);
  Value->SetBoolField(TEXT("clip_object_resident"), FindObject<UAnimSequence>(nullptr, *ClipPath) != nullptr);
  return Value;
}
struct FProfileStep {
  FString Label, Page, Hero, Clip, Visit;
  TArray<FString> Buttons;
  double Dwell = 10;
};
}

struct FWCFrontEndProfileState {
  double Started = FPlatformTime::Seconds(), ActionAt = 0, StableAt = 0, MeasureAt = 0, ExitAt = 0;
  int32 Index = -1, StableFrames = 0, CompletedStages = 0;
  uint64 MeasureFrame = 0;
  bool Initialized = false, Measuring = false, Finished = false, Failed = false, FileError = false;
  FString Directory, ReportPath, MarkersPath, FrameCsv, OriginalHero, Language;
  bool ReducedMotion = false;
  float Master = 0, Music = 0, Effects = 0;
  TArray<FString> SavedSection;
  TArray<FProfileStep> Steps;
  TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();

  bool Save() {
    if (ReportPath.IsEmpty()) return false;
    Report->SetNumberField(TEXT("completed_stages"), CompletedStages);
    const bool Written = FFileHelper::SaveStringToFile(ProfileEncode(Report), *ReportPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    FileError |= !Written;
    return Written;
  }
  bool Mark(const TCHAR* Event, AWCMatchController* Player, const FProfileStep* Step = nullptr) {
    double Wall = 0; FString Csv;
    if (!WCReadVerificationClock(Player, Wall, Csv)) { FileError = true; return false; }
    auto Value = MakeShared<FJsonObject>();
    Value->SetStringField(TEXT("event"), Event);
    Value->SetStringField(TEXT("utc"), FDateTime::UtcNow().ToIso8601());
    Value->SetNumberField(TEXT("wall_seconds"), Wall);
    Value->SetNumberField(TEXT("process_monotonic_seconds"), FPlatformTime::Seconds());
    Value->SetNumberField(TEXT("frame_counter"), double(GFrameCounter));
    Value->SetStringField(TEXT("actual_frontend_page"), Cast<AWCMatchHUD>(Player->GetHUD()) ? Cast<AWCMatchHUD>(Player->GetHUD())->FrontEndPageName() : TEXT("closed"));
    Value->SetNumberField(TEXT("stage_index"), Index);
    if (Step) {
      Value->SetStringField(TEXT("stage"), Step->Label);
      Value->SetStringField(TEXT("frontend_page"), Step->Page);
      Value->SetStringField(TEXT("hero_id"), Step->Hero);
      Value->SetStringField(TEXT("clip"), Step->Clip);
      Value->SetStringField(TEXT("visit"), Step->Visit);
      Value->SetNumberField(TEXT("requested_dwell_seconds"), Step->Dwell);
      TArray<TSharedPtr<FJsonValue>> Keys;
      for (const auto& Key : Step->Buttons) Keys.Add(MakeShared<FJsonValueString>(Key));
      Value->SetArrayField(TEXT("native_slate_buttons"), Keys);
      Value->SetObjectField(TEXT("object_residency_at_marker"), ResidentState(Step->Hero, Step->Clip));
    }
    const bool Written = FFileHelper::SaveStringToFile(ProfileEncode(Value) + TEXT("\n"), *MarkersPath,
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append);
    FileError |= !Written;
    return Written;
  }
  void Finish(AWCMatchController* Player, const FString& Failure = FString()) {
    if (Finished) return;
    const bool MarkerWritten = Mark(TEXT("route_end"), Player);
    Failed = !Failure.IsEmpty() || FileError || !MarkerWritten;
    Report->SetStringField(TEXT("status"), Failed ? TEXT("FAIL") : TEXT("PASS_ROUTE_EXECUTION_ONLY"));
    Report->SetStringField(TEXT("failure"), Failure);
    Report->SetStringField(TEXT("ended_utc"), FDateTime::UtcNow().ToIso8601());
    Report->SetNumberField(TEXT("elapsed_seconds"), FPlatformTime::Seconds() - Started);
    Report->SetBoolField(TEXT("no_screenshot_requests_by_route"), true);
    if (!Save()) Failed = true;
    Finished = true;
    ExitAt = FPlatformTime::Seconds() + 2;
    UE_LOG(LogTemp, Display, TEXT("WC_FRONTEND_PROFILE_FINISHED status=%s stages=%d reason=%s"),
           Failed ? TEXT("FAIL") : TEXT("PASS_ROUTE_EXECUTION_ONLY"), CompletedStages, *Failure);
  }
};

void FWCFrontEnd::TickProfile() {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndProfile"))) return;
  auto* Player = Controller.Get();
  if (!Player || !Player->Public || !Player->Presenter) return;
  if (!ProfileState) ProfileState = MakeShared<FWCFrontEndProfileState>();
  auto& State = *ProfileState;
  const double Now = FPlatformTime::Seconds();
  if (State.Finished) {
    if (Now >= State.ExitAt) FPlatformMisc::RequestExitWithStatus(false, State.Failed ? 1 : 0);
    return;
  }
  if (!State.Initialized) {
    State.Initialized = true;
    FString Directory;
    const bool ExplicitDirectory = FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory);
    if (!ExplicitDirectory || Directory.IsEmpty()) {
      UE_LOG(LogTemp, Error, TEXT("WC_FRONTEND_PROFILE_REFUSED explicit fresh WCEvidenceDir is required"));
      State.Failed = State.Finished = true; State.ExitAt = Now;
      return;
    }
    State.Directory = FPaths::ConvertRelativePathToFull(Directory);
    State.ReportPath = State.Directory / TEXT("frontend-profile.json");
    State.MarkersPath = State.Directory / TEXT("frontend-profile-markers.jsonl");
    if (IFileManager::Get().FileExists(*State.ReportPath) || IFileManager::Get().FileExists(*State.MarkersPath)) {
      UE_LOG(LogTemp, Error, TEXT("WC_FRONTEND_PROFILE_REFUSED existing profile evidence will not be overwritten: %s"), *State.Directory);
      State.ReportPath.Reset(); State.MarkersPath.Reset();
      State.Failed = State.Finished = true; State.ExitAt = Now;
      return;
    }
    IFileManager::Get().MakeDirectory(*State.Directory, true);
    State.Report->SetStringField(TEXT("status"), TEXT("STARTED"));
    State.Report->SetStringField(TEXT("started_utc"), FDateTime::UtcNow().ToIso8601());
    State.Report->SetStringField(TEXT("method"), TEXT("Native Slate focused Enter key down/up on visible Heroes, Back, Meet this hero, Next, Idle and Skill buttons. Normal world clock, no screenshots, no entry or roster commands. Boundary marker writes and ordinary WCProfile sampling remain instrumentation."));
    State.Report->SetStringField(TEXT("load_scope"), TEXT("First UI presentation and warm revisit only. BoardPresenter initializes and retains catalog assets before this route. FindObject residency is object presence, not disk/cache/texture-mip residency. No forced garbage collection, cache eviction or cold-load claim."));
    State.Report->SetStringField(TEXT("frame_join"), TEXT("CSV is sampled in controller Tick before HUD navigation. Action costs can appear in following frame rows. For settled dwell use frame_counter > measure_begin frame + 1 and <= measure_end frame, plus the matching frontend_page. The first post-marker row is retained in CSV but separated as boundary instrumentation. Keep action_begin/action_return/measure_begin transition intervals separate; do not discard their hitches."));
    State.Report->SetStringField(TEXT("acceptance_boundary"), TEXT("Route completion is instrumentation evidence only: no manual UI, screenshot, visual, continuous animation, gameplay, network or performance acceptance. GPU absence remains unavailable, not zero. External competing workloads must be recorded by the launcher."));
    State.Report->SetNumberField(TEXT("csv_initial_seconds_excluded"), 5);
    State.Report->SetBoolField(TEXT("pre_frontend_startup_measured"), false);
    State.Report->SetBoolField(TEXT("editor_compilation_counters_available"), WITH_EDITOR != 0);
    State.Report->SetNumberField(TEXT("hard_timeout_seconds"), 1800);
    State.Report->SetNumberField(TEXT("pid"), FPlatformProcess::GetCurrentProcessId());
    State.Report->SetStringField(TEXT("balance_version"), UTF8_TO_TCHAR(Player->Presenter->Definitions.balanceVersion.c_str()));
    State.Report->SetStringField(TEXT("content_digest"), UTF8_TO_TCHAR(Player->Presenter->Definitions.contentDigest.c_str()));
    State.Report->SetStringField(TEXT("schema_version"), Player->Public->GetStringField(TEXT("schemaVersion")));
    State.Report->SetNumberField(TEXT("protocol_version"), Player->Public->GetNumberField(TEXT("protocolVersion")));
    State.Language = Player->Language; State.ReducedMotion = Player->bReducedMotion;
    State.Master = Player->MasterVolume; State.Music = Player->MusicVolume; State.Effects = Player->EffectsVolume;
    GConfig->GetSection(TEXT("WonderChess"), State.SavedSection, GGameUserSettingsIni);
    State.Report->SetStringField(TEXT("language"), State.Language);
    State.Report->SetBoolField(TEXT("reduced_motion"), State.ReducedMotion);
    State.Report->SetStringField(TEXT("animation_workload"), State.ReducedMotion ? TEXT("Saved reduced motion: preview clips held at pose zero") : TEXT("Saved ordinary motion: preview clips play normally"));
    State.Report->SetNumberField(TEXT("master_volume"), State.Master);
    State.Report->SetNumberField(TEXT("music_volume"), State.Music);
    State.Report->SetNumberField(TEXT("effects_volume"), State.Effects);
    State.Save();
    FString Failure;
    if (!FParse::Param(FCommandLine::Get(), TEXT("WCProfile"))) Failure = TEXT("WCProfile is required for frame evidence");
    for (const TCHAR* Flag : {TEXT("WCFrontEndAudit"), TEXT("WCFrontEndAllHeroes"), TEXT("WCShots"), TEXT("WCReviewMotion"),
         TEXT("WCSelectionAudit"), TEXT("WCFrontEndRecoveryAudit"), TEXT("WCExercise"), TEXT("WCAutoStart"), TEXT("WCHost"), TEXT("NullRHI"), TEXT("WCArtReview"), TEXT("WCProjectedBounds"), TEXT("WCFollowHero")})
      if (FParse::Param(FCommandLine::Get(), Flag)) Failure = FString(TEXT("Conflicting option: ")) + Flag;
    for (const TCHAR* Flag : {TEXT("WCJoin="), TEXT("WCFrontEndPage="), TEXT("WCFrontEndHero="), TEXT("WCFrontEndClip="), TEXT("WCFrontEndStar="), TEXT("WCReviewHero="), TEXT("WCFollowHero=")}) {
      FString Value;
      if (FParse::Value(FCommandLine::Get(), Flag, Value)) Failure = FString(TEXT("Conflicting option: ")) + Flag;
    }
    float Speed = 1; FParse::Value(FCommandLine::Get(), TEXT("WCFast="), Speed);
    if (Speed != 1 || FApp::UseFixedTimeStep()) Failure = TEXT("Normal 1x variable-step clock is required");
    int ExitAfter = 0;
    if (FParse::Value(FCommandLine::Get(), TEXT("WCExitAfter="), ExitAfter) && ExitAfter < 1810)
      Failure = TEXT("WCExitAfter must be omitted or at least 1810 seconds; this route has its own 1800-second bound");
    if (!Failure.IsEmpty()) { State.Finish(Player, Failure); return; }
  }
  if (State.FileError) { State.Finish(Player, TEXT("Evidence file write or verification clock failed")); return; }
  if (Now - State.Started > 1800) { State.Finish(Player, TEXT("1800-second profile timeout")); return; }
  if (Player->Public->GetNumberField(TEXT("phase")) >= 0 || Player->Public->GetNumberField(TEXT("matchNamespace")) != 0 ||
      !Player->Public->GetStringField(TEXT("entryState")).IsEmpty() || Player->Public->GetBoolField(TEXT("network")) || Player->bTutorial) {
    State.Finish(Player, TEXT("Profiling requires an idle standalone lobby with no match or entry")); return;
  }
  bool SavedUnchanged = true;
  if (!State.Measuring || Now - State.MeasureAt >= State.Steps[State.Index].Dwell) {
    TArray<FString> CurrentSaved;
    GConfig->GetSection(TEXT("WonderChess"), CurrentSaved, GGameUserSettingsIni);
    SavedUnchanged = CurrentSaved == State.SavedSection;
  }
  const bool SettingsUnchanged = SavedUnchanged && Player->Language == State.Language &&
      Player->bReducedMotion == State.ReducedMotion && Player->MasterVolume == State.Master &&
      Player->MusicVolume == State.Music && Player->EffectsVolume == State.Effects && !bReviewPreview;
  if (!SettingsUnchanged) { State.Report->SetBoolField(TEXT("saved_preferences_unchanged"), false); State.Finish(Player, TEXT("Saved or runtime preferences changed during profile")); return; }
  if (FScreenshotRequest::IsScreenshotRequested()) { State.Finish(Player, TEXT("Screenshot request would contaminate profile")); return; }
  if (FApp::UseFixedTimeStep() || !FMath::IsNearlyEqual(Player->GetWorld()->GetWorldSettings()->GetEffectiveTimeDilation(), 1.f)) {
    State.Finish(Player, TEXT("World clock changed from normal 1x")); return;
  }
  double VerificationWall = 0; FString Csv;
  if (!WCReadVerificationClock(Player, VerificationWall, Csv)) {
    if (Now - State.Started > 10) State.Finish(Player, TEXT("Verification clock not initialized"));
    return;
  }
  if (!Root || !Scene.IsValid()) {
    if (Now - State.Started > 30) State.Finish(Player, TEXT("Native front end failed to appear"));
    return;
  }
  if (State.Steps.IsEmpty()) {
    RefreshResults();
    if (Page != EPage::Lobby || Results.Num() != 24 || !Search.IsEmpty() || !Filters.IsEmpty()) {
      State.Finish(Player, TEXT("Expected unfiltered 24-hero initial lobby")); return;
    }
    State.OriginalHero = SelectedId; State.FrameCsv = Csv;
    State.Report->SetStringField(TEXT("original_showcase_hero"), SelectedId);
    State.Report->SetStringField(TEXT("frame_csv"), Csv);
    State.Report->SetStringField(TEXT("markers_jsonl"), State.MarkersPath);
    TArray<TSharedPtr<FJsonValue>> Resident;
    for (const auto Index : Results) {
      const FString Id = UTF8_TO_TCHAR(Player->Presenter->Definitions.units[Index].id.c_str());
      auto Item = MakeShared<FJsonObject>(); Item->SetStringField(TEXT("hero_id"), Id);
      Item->SetObjectField(TEXT("idle"), ResidentState(Id, TEXT("Idle")));
      Item->SetObjectField(TEXT("active"), ResidentState(Id, TEXT("Active")));
      Resident.Add(MakeShared<FJsonValueObject>(Item));
    }
    State.Report->SetArrayField(TEXT("initial_object_residency"), Resident);
    auto Add = [&](const FString& Label, const FString& PageValue, const FString& Hero, const FString& Clip,
                   const FString& Visit, const TArray<FString>& Keys, double Dwell = 10) {
      State.Steps.Add({Label, PageValue, Hero, Clip, Visit, Keys, Dwell});
    };
    const FString Heroes = Local(TEXT("Heroes"), TEXT("Hero")), BackKey = Local(TEXT("Back"), TEXT("Kembali"));
    const FString Meet = Local(TEXT("Meet this hero"), TEXT("Kenali hero ini")), Next = Local(TEXT("Next"), TEXT("Berikutnya"));
    // No direct page, hero, animation or settings writes: the route dispatches real registered Slate buttons.
    Add(TEXT("lobby-first-presentation"), TEXT("lobby"), SelectedId, TEXT("Idle"), TEXT("first_ui_presentation"), {}, 20);
    Add(TEXT("gallery-first-presentation"), TEXT("gallery"), SelectedId, TEXT("Idle"), TEXT("first_ui_presentation"), {Heroes}, 20);
    Add(TEXT("lobby-warm-1"), TEXT("lobby"), SelectedId, TEXT("Idle"), TEXT("warm_revisit"), {BackKey}, 20);
    int32 RosterAt = Results.IndexOfByKey(SelectedIndex());
    if (RosterAt < 0) { State.Finish(Player, TEXT("Initial showcase hero absent from gallery results")); return; }
    FString LastHero;
    for (int Pass = 0; Pass < 2; ++Pass) {
      const FString Visit = Pass ? TEXT("warm_revisit") : TEXT("first_detail_presentation");
      for (int Hero = 0; Hero < 24; ++Hero) {
        const FString Id = UTF8_TO_TCHAR(Player->Presenter->Definitions.units[Results[(RosterAt + Hero) % 24]].id.c_str());
        const FString Prefix = FString::Printf(TEXT("pass-%d-%s"), Pass + 1, *Id);
        Add(Prefix + TEXT("-idle"), TEXT("detail"), Id, TEXT("Idle"), Visit, {Hero ? Next : Meet, TEXT("Idle")});
        Add(Prefix + TEXT("-active"), TEXT("detail"), Id, TEXT("Active"), Visit, {TEXT("Skill")});
        LastHero = Id;
      }
      Add(FString::Printf(TEXT("gallery-warm-%d"), Pass + 1), TEXT("gallery"), LastHero, TEXT("Active"), TEXT("warm_revisit"), {BackKey}, 20);
      Add(FString::Printf(TEXT("lobby-warm-%d"), Pass + 2), TEXT("lobby"), LastHero, TEXT("Active"), TEXT("warm_revisit"), {BackKey}, 20);
      RosterAt = (RosterAt + 23) % 24;
    }
    State.Report->SetNumberField(TEXT("expected_stages"), State.Steps.Num());
    State.Report->SetNumberField(TEXT("hero_detail_stages"), 96);
    State.Report->SetNumberField(TEXT("hero_idle_active_passes"), 2);
    State.Report->SetBoolField(TEXT("saved_preferences_unchanged"), true);
    State.Save(); State.Mark(TEXT("route_ready"), Player);
  }
  // Startup exclusions remain explicit; do not quietly turn eager startup into a cold-load benchmark.
  if (State.Index < 0 && VerificationWall < 10) return;
  if (State.Index < 0 || (!State.Measuring && State.ActionAt == 0)) {
    ++State.Index;
    if (State.Index >= State.Steps.Num()) { State.Finish(Player); return; }
    const auto& Step = State.Steps[State.Index];
    if (!State.Mark(TEXT("action_begin"), Player, &Step)) { State.Finish(Player, TEXT("Cannot write action marker")); return; }
    for (const auto& Key : Step.Buttons)
      if (!AuditKey(Key)) { State.Finish(Player, FString(TEXT("Native Slate button unavailable: ")) + Key); return; }
    State.Mark(TEXT("action_return"), Player, &Step);
    State.ActionAt = FPlatformTime::Seconds(); State.StableAt = 0; State.StableFrames = 0;
    return;
  }
  const auto& Step = State.Steps[State.Index];
  if (FString(PageName()) != Step.Page || SelectedId != Step.Hero || Scene->SelectedClip != Step.Clip || Star != 1) {
    State.Finish(Player, FString(TEXT("Actual native page/hero/clip/star differs from stage: ")) + Step.Label); return;
  }
  auto* Hero = Scene->FindComponentByClass<USkeletalMeshComponent>();
  auto* Animation = Hero ? Hero->GetSingleNodeInstance() : nullptr;
  const FString ExpectedMesh = ProfileAssetPath(Step.Hero, TEXT("SK_") + Step.Hero);
  const FString ExpectedClip = ProfileAssetPath(Step.Hero, TEXT("AN_") + Step.Hero + TEXT("_") + Step.Clip);
  if (!Hero || GetPathNameSafe(Hero->GetSkeletalMeshAsset()) != ExpectedMesh || !Animation ||
      GetPathNameSafe(Animation->GetCurrentAsset()) != ExpectedClip || !Scene->AssetMessage.IsEmpty()) {
    State.Finish(Player, FString(TEXT("Actual preview mesh or animation unavailable: ")) + Step.Hero + TEXT("/") + Step.Clip); return;
  }
  if (Hero->bPauseAnims != State.ReducedMotion) { State.Finish(Player, TEXT("Preview playback differs from saved reduced-motion preference")); return; }
  if (State.Measuring) {
    if (Player->GetViewTarget() != Scene.Get()) { State.Finish(Player, TEXT("Preview camera changed during dwell")); return; }
    if (Now - State.MeasureAt >= Step.Dwell) {
      State.Mark(TEXT("measure_end"), Player, &Step);
      auto Stages = State.Report->HasField(TEXT("stages")) ? State.Report->GetArrayField(TEXT("stages")) : TArray<TSharedPtr<FJsonValue>>();
      auto Complete = MakeShared<FJsonObject>();
      Complete->SetStringField(TEXT("stage"), Step.Label); Complete->SetStringField(TEXT("hero_id"), Step.Hero);
      Complete->SetNumberField(TEXT("elapsed_dwell_seconds"), Now - State.MeasureAt);
      Complete->SetNumberField(TEXT("render_tick_span"), double(GFrameCounter - State.MeasureFrame));
      Complete->SetNumberField(TEXT("settling_seconds"), State.MeasureAt - State.ActionAt);
      Stages.Add(MakeShared<FJsonValueObject>(Complete)); State.Report->SetArrayField(TEXT("stages"), Stages);
      ++State.CompletedStages; State.Measuring = false; State.ActionAt = 0;
      State.Save();
    }
    return;
  }
  int AssetsRemaining = 0;
  bool ShaderCompiling = false;
#if WITH_EDITOR
  AssetsRemaining = FAssetCompilingManager::Get().GetNumRemainingAssets();
  ShaderCompiling = GShaderCompilingManager && GShaderCompilingManager->IsCompiling();
#endif
  const int Streaming = IStreamingManager::Get().GetNumWantingResources();
  const bool Ready = Player->GetViewTarget() == Scene.Get() && Scene->bApproachImported && AssetsRemaining == 0 && !ShaderCompiling && Streaming == 0;
  if (Ready) {
    if (!State.StableFrames) State.StableAt = Now;
    ++State.StableFrames;
  } else { State.StableFrames = 0; State.StableAt = 0; }
  if (State.StableFrames >= 30 && Now - State.StableAt >= .5) {
    State.Measuring = true; State.MeasureAt = Now; State.MeasureFrame = GFrameCounter;
    State.Mark(TEXT("measure_begin"), Player, &Step);
  } else if (Now - State.ActionAt > 60) {
    State.Finish(Player, FString::Printf(TEXT("Preview settling timeout: %s assets=%d shader=%d streaming=%d view=%s"),
        *Step.Label, AssetsRemaining, ShaderCompiling, Streaming, *GetPathNameSafe(Player->GetViewTarget())));
  }
}
