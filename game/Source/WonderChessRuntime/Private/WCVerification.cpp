#include "WCVerification.h"
#include "Components/AudioComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Containers/StringConv.h"
#include "DynamicRHI.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformProcess.h"
#include "Misc/CommandLine.h"
#include "Misc/EngineVersion.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "RHIGlobals.h"
#include "RenderTimer.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "WCNetworkSession.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace {
using Object = TSharedPtr<FJsonObject>;
using Value = TSharedPtr<FJsonValue>;
const double ProcessStart = FPlatformTime::Seconds();
struct Evidence {
  int64 Namespace = -1;
  TOptional<wc::Id> AuthoritySeed;
  double StartWall = 0, NextAction = 0, NextShot = 0, NextWrite = 0,
         NextSnapshot = 0, NextFrameFlush = 0, CompletedAt = 0;
  int Phase = -99, Round = -1, Rerolls = 0, Commands = 0, Accepted = 0,
      Rejected = 0;
  int MaxVisible = 0, MaxLogical = 0, MaxEncounters = 0;
  int FollowCandidates = 0, FollowEncounterA = -1, FollowEncounterB = -1,
      FollowAlive = 0;
  int64 FollowUnit = 0;
  bool FollowGhost = false;
  int PublicChars = 0, PublicUtf8Bytes = 0, MaxPublicChars = 0,
      MaxPublicUtf8Bytes = 0, PayloadSamples = 0;
  bool Complete = false, Aborted = false, Initialized = false,
       RestartRequested = false;
  uint64 PeakMemory = 0, ReplySerial = 0;
  bool LastReplyAccepted = false;
  FString LastReply, Directory, LatestPublic, LatestPrivate, FrameRows;
  FString SizedPublic;
  TArray<double> Frame, Game, Render, GPU, BusyFrame, BusyGame, BusyRender,
      BusyGPU;
  TSet<FString> ShotKeys, PrivacyViolations;
  TArray<Value> Transitions, ProbeResults, AuthorityTransitions;
  TArray<Value> ProjectedBoundsSamples;
  TArray<Object> PreviousAuthoritySeats;
  int AuthorityBotLogCount = 0, AuthorityRound = -1, AuthorityPhase = -1;
  bool ExitRequested = false;
  int ProbeStage = 0;
  int ProbePhase = -1, ProbeRound = 0, ForeignOwner = -1;
  bool CombatProbeSent = false, CombatProbeActive = false;
  double PhaseChangedAt = 0;
  int64 PriorNamespace = -1;
  FString ProbePrivateBefore;
  bool ProbeAwaiting = false, ProbeExpectedAccepted = false,
       ProbeExpectedLock = false;
  uint64 ProbeReplyAfter = 0;
  double ProbeStarted = 0;
  FString ProbeName, ProbeReason;
  int ProbeGold = 0;
  wc::Command OriginalProbe, PriorMatchProbe, Probe;
  bool NormalAwaiting = false;
  uint64 NormalReplyAfter = 0;
  int64 NormalExpectedSequence = 0;
};
TMap<TWeakObjectPtr<AWCMatchController>, Evidence> EvidenceStates;
TMap<TWeakObjectPtr<AWCMatchController>, int> RestartedControllers;
void CaptureAuthoritySeed(Evidence &E, int64 Namespace, wc::Id Seed) {
  if (E.Namespace > 0 && E.Namespace == Namespace && !E.AuthoritySeed.IsSet())
    E.AuthoritySeed = Seed;
}
void WriteAuthoritySeed(const Object &Json, const Evidence &E) {
  if (E.AuthoritySeed.IsSet())
    Json->SetNumberField(TEXT("match_seed_authority"), E.AuthoritySeed.GetValue());
  else
    Json->SetField(TEXT("match_seed_authority"), MakeShared<FJsonValueNull>());
}
struct VerificationOptions {
  FString RequestedSeed, RequestedHero;
  int32 Seed = 271828, Hero = -1;
  bool SeedSupplied = false, SeedValid = true, HeroSupplied = false,
       HeroValid = true;
};
bool BoundedDecimal(const FString &Text, int32 Minimum, int32 Maximum,
                    int32 &Result) {
  if (Text.IsEmpty() || Text.Len() > 10)
    return false;
  int64 Value = 0;
  for (TCHAR Character : Text) {
    if (Character < '0' || Character > '9')
      return false;
    Value = Value * 10 + (Character - '0');
    if (Value > Maximum)
      return false;
  }
  if (Value < Minimum)
    return false;
  Result = int32(Value);
  return true;
}
const VerificationOptions &Options() {
  static const VerificationOptions Parsed = [] {
    VerificationOptions Result;
    Result.SeedSupplied =
        FParse::Value(FCommandLine::Get(), TEXT("WCExerciseSeed="),
                      Result.RequestedSeed) ||
        FParse::Param(FCommandLine::Get(), TEXT("WCExerciseSeed"));
    if (Result.SeedSupplied)
      Result.SeedValid = BoundedDecimal(Result.RequestedSeed, 1, MAX_int32,
                                        Result.Seed);
    Result.HeroSupplied =
        FParse::Value(FCommandLine::Get(), TEXT("WCFollowHero="),
                      Result.RequestedHero) ||
        FParse::Param(FCommandLine::Get(), TEXT("WCFollowHero"));
    if (Result.HeroSupplied)
      Result.HeroValid =
          BoundedDecimal(Result.RequestedHero, 0, 11, Result.Hero);
    return Result;
  }();
  return Parsed;
}
bool AuthorityChecks() {
  return FParse::Param(FCommandLine::Get(), TEXT("WCAuthorityChecks"));
}
int PreparationProbeCount() { return AuthorityChecks() ? 6 : 4; }
double Number(const Object &Json, const TCHAR *Key, double Default = 0) {
  double Result = Default;
  if (Json.IsValid())
    Json->TryGetNumberField(Key, Result);
  return Result;
}
bool Boolean(const Object &Json, const TCHAR *Key, bool Default = false) {
  bool Result = Default;
  if (Json.IsValid())
    Json->TryGetBoolField(Key, Result);
  return Result;
}
FString Encode(const Object &Json) {
  FString Text;
  auto Writer =
      TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(
          &Text);
  FJsonSerializer::Serialize(Json.ToSharedRef(), Writer);
  return Text;
}
void Append(const FString &Path, const FString &Text) {
  if (!FFileHelper::SaveStringToFile(
          Text, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
          &IFileManager::Get(), FILEWRITE_Append))
    UE_LOG(LogTemp, Warning, TEXT("WC_EVIDENCE_WRITE_FAILED %s"), *Path);
}
FString Prefix(const Evidence &E, const AWCMatchController *P) {
  return FString::Printf(TEXT("match-%lld-seat-%d-pid-%u"), E.Namespace,
                         P->AssignedSeat,
                         FPlatformProcess::GetCurrentProcessId());
}
Object BaseRecord(const Evidence &E, const AWCMatchController *P) {
  auto Json = MakeShared<FJsonObject>();
  Json->SetStringField(TEXT("utc"), FDateTime::UtcNow().ToIso8601());
  Json->SetNumberField(TEXT("match_namespace"), E.Namespace);
  Json->SetNumberField(TEXT("process_id"),
                       FPlatformProcess::GetCurrentProcessId());
  Json->SetNumberField(TEXT("seat"), P->AssignedSeat);
  Json->SetNumberField(TEXT("observed_seat"), P->ObservedSeat);
  const auto &Configuration = Options();
  Json->SetStringField(TEXT("exercise_seed_requested"),
                       Configuration.RequestedSeed);
  Json->SetBoolField(TEXT("exercise_seed_override_present"),
                     Configuration.SeedSupplied);
  Json->SetBoolField(TEXT("exercise_seed_override_valid"),
                     Configuration.SeedValid);
  Json->SetNumberField(TEXT("exercise_seed_effective_initial"),
                       Configuration.Seed);
  Json->SetNumberField(TEXT("exercise_seed_restart"), 271828);
  WriteAuthoritySeed(Json, E);
  Json->SetStringField(
      TEXT("exercise_seed_boundary"),
      TEXT("Initial scripted ServerStart accepts decimal seeds 1-2147483647; "
           "absent or invalid values use271828. Actual match seed is recorded "
           "only where the authoritative Match is available and cached for "
           "that namespace. Restart retains "
           "the existing271828 seed."));
  Json->SetStringField(TEXT("follow_hero_requested"),
                       Configuration.RequestedHero);
  Json->SetBoolField(TEXT("follow_hero_override_present"),
                     Configuration.HeroSupplied);
  Json->SetBoolField(TEXT("follow_hero_override_valid"),
                     Configuration.HeroValid);
  Json->SetNumberField(TEXT("follow_hero_definition"), Configuration.Hero);
  Json->SetNumberField(TEXT("follow_hero_candidate_encounters"),
                       E.FollowCandidates);
  Json->SetNumberField(TEXT("follow_hero_selected_encounter_a"),
                       E.FollowEncounterA);
  Json->SetNumberField(TEXT("follow_hero_selected_encounter_b"),
                       E.FollowEncounterB);
  Json->SetBoolField(TEXT("follow_hero_selected_encounter_ghost"), E.FollowGhost);
  Json->SetNumberField(TEXT("follow_hero_selected_encounter_alive"),
                       E.FollowAlive);
  Json->SetNumberField(TEXT("follow_hero_selected_unit"), E.FollowUnit);
  bool TargetVisible = false;
  if (Configuration.Hero >= 0 && P->Presenter)
    for (const auto &Value : P->Presenter->VisibleUnits) {
      const auto Unit = Value->AsObject();
      TargetVisible |= Number(Unit, TEXT("def"), -1) == Configuration.Hero &&
                       Number(Unit, TEXT("hp")) > 0;
    }
  Json->SetBoolField(TEXT("follow_hero_actual_visible"), TargetVisible);
  Json->SetStringField(
      TEXT("follow_hero_boundary"),
      TEXT("Read-only public scouting selects an existing unfinished encounter "
           "containing a living requested definition. ObservedSeat changes only "
           "the viewport; the presenter may reflect that change on the next "
           "frame. Actual visible membership is recorded separately."));
  Json->SetNumberField(TEXT("elapsed_wall_seconds"),
                       FPlatformTime::Seconds() - E.StartWall);
  Json->SetNumberField(TEXT("phase"), E.Phase);
  Json->SetNumberField(TEXT("round"), E.Round);
  return Json;
}
void FollowHero(AWCMatchController *P, Evidence &E) {
  E.FollowCandidates = E.FollowAlive = 0;
  E.FollowEncounterA = E.FollowEncounterB = -1;
  E.FollowUnit = 0;
  E.FollowGhost = false;
  const auto &Configuration = Options();
  if (Configuration.Hero < 0 ||
      Number(P->Public, TEXT("phase"), -1) != int(wc::Phase::Combat) ||
      !P->Public->HasTypedField<EJson::Array>(TEXT("encounters")))
    return;
  Object Best;
  int BestAlive = -1;
  bool BestCurrent = false;
  int64 BestTarget = 0;
  for (const auto &Value : P->Public->GetArrayField(TEXT("encounters"))) {
    const auto Encounter = Value->AsObject();
    if (!Encounter.IsValid() || Boolean(Encounter, TEXT("complete")) ||
        !Encounter->HasTypedField<EJson::Array>(TEXT("units")))
      continue;
    int Alive = 0;
    int64 Target = 0;
    for (const auto &Entry : Encounter->GetArrayField(TEXT("units"))) {
      const auto Unit = Entry->AsObject();
      if (Number(Unit, TEXT("hp")) <= 0)
        continue;
      ++Alive;
      if (!Target && Number(Unit, TEXT("def"), -1) == Configuration.Hero)
        Target = int64(Number(Unit, TEXT("id")));
    }
    if (!Target)
      continue;
    ++E.FollowCandidates;
    const bool Current =
        Number(Encounter, TEXT("a"), -1) == P->ObservedSeat ||
        (!Boolean(Encounter, TEXT("ghost")) &&
         Number(Encounter, TEXT("b"), -1) == P->ObservedSeat);
    if (!Best.IsValid() || (Current && !BestCurrent) ||
        (Current == BestCurrent && Alive > BestAlive)) {
      Best = Encounter;
      BestAlive = Alive;
      BestCurrent = Current;
      BestTarget = Target;
    }
  }
  if (!Best.IsValid())
    return;
  E.FollowEncounterA = int(Number(Best, TEXT("a"), -1));
  E.FollowEncounterB = int(Number(Best, TEXT("b"), -1));
  E.FollowGhost = Boolean(Best, TEXT("ghost"));
  E.FollowAlive = BestAlive;
  E.FollowUnit = BestTarget;
  if (!BestCurrent && E.FollowEncounterA >= 0 && E.FollowEncounterA < 8)
    P->ObservedSeat = E.FollowEncounterA;
}
void MeasurePublicPayload(AWCMatchController *P, Evidence &E) {
  if (E.SizedPublic == P->LastPublicJson)
    return;
  E.SizedPublic = P->LastPublicJson;
  E.PublicChars = P->LastPublicJson.Len();
  const FTCHARToUTF8 Utf8(*P->LastPublicJson);
  E.PublicUtf8Bytes = Utf8.Length();
  E.MaxPublicChars = FMath::Max(E.MaxPublicChars, E.PublicChars);
  E.MaxPublicUtf8Bytes = FMath::Max(E.MaxPublicUtf8Bytes, E.PublicUtf8Bytes);
  ++E.PayloadSamples;
}
void SampleProjectedBounds(AWCMatchController *P, Evidence &E) {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCProjectedBounds")) ||
      E.Phase != int(wc::Phase::Combat) || !P->Presenter)
    return;
  int Width = 0, Height = 0;
  P->GetViewportSize(Width, Height);
  if (Width <= 0 || Height <= 0)
    return;
  const double Left = 335.0 * Width / 1920.0, Right = 1550.0 * Width / 1920.0,
               Top = 172.0 * Height / 1080.0, Bottom = 782.0 * Height / 1080.0;
  auto Sample = BaseRecord(E, P);
  Sample->SetNumberField(TEXT("viewport_width"), Width);
  Sample->SetNumberField(TEXT("viewport_height"), Height);
  auto Safe = MakeShared<FJsonObject>();
  Safe->SetNumberField(TEXT("left"), Left);
  Safe->SetNumberField(TEXT("right"), Right);
  Safe->SetNumberField(TEXT("top"), Top);
  Safe->SetNumberField(TEXT("bottom"), Bottom);
  Sample->SetObjectField(TEXT("board_safe_rectangle"), Safe);
  Sample->SetStringField(
      TEXT("boundary"),
      TEXT("Eight world-axis component-bounds corners projected using the "
           "current controller camera. Bounds crossing the reserved HUD "
           "rectangle are conservative geometry evidence, not pixel occlusion "
           "or visual-quality proof. No authored hero height is substituted."));
  TArray<Value> Units, Outside, Unprojectable, Missing;
  for (const auto &Entry : P->Presenter->VisibleUnits) {
    const auto Unit = Entry->AsObject();
    if (Number(Unit, TEXT("hp")) <= 0)
      continue;
    const int64 Id = int64(Number(Unit, TEXT("id")));
    AActor *const *Found = P->Presenter->Heroes.Find(Id);
    AActor *Actor = Found ? *Found : nullptr;
    auto *Component =
        IsValid(Actor) ? Actor->FindComponentByClass<USkeletalMeshComponent>()
                       : nullptr;
    if (!IsValid(Component) || !Component->IsVisible() || Actor->IsHidden()) {
      Missing.Add(MakeShared<FJsonValueNumber>(Id));
      continue;
    }
    const FBox Box = Component->Bounds.GetBox();
    auto Item = MakeShared<FJsonObject>();
    Item->SetNumberField(TEXT("id"), Id);
    Item->SetNumberField(TEXT("definition"), Number(Unit, TEXT("def")));
    Item->SetStringField(TEXT("component"), Component->GetPathName());
    Item->SetStringField(TEXT("world_bounds_min"), Box.Min.ToString());
    Item->SetStringField(TEXT("world_bounds_max"), Box.Max.ToString());
    FBox2D Screen(ForceInit);
    int Projected = 0;
    TArray<Value> Corners;
    for (int Corner = 0; Corner < 8; ++Corner) {
      const FVector World((Corner & 1) ? Box.Max.X : Box.Min.X,
                          (Corner & 2) ? Box.Max.Y : Box.Min.Y,
                          (Corner & 4) ? Box.Max.Z : Box.Min.Z);
      FVector2D Pixel;
      auto Point = MakeShared<FJsonObject>();
      const bool Valid =
          Box.IsValid && P->ProjectWorldLocationToScreen(World, Pixel, false);
      Point->SetBoolField(TEXT("projected"), Valid);
      if (Valid) {
        ++Projected;
        Screen += Pixel;
        Point->SetNumberField(TEXT("x"), Pixel.X);
        Point->SetNumberField(TEXT("y"), Pixel.Y);
      }
      Corners.Add(MakeShared<FJsonValueObject>(Point));
    }
    Item->SetArrayField(TEXT("projected_corners"), Corners);
    Item->SetNumberField(TEXT("projected_corner_count"), Projected);
    if (Projected > 0) {
      Item->SetNumberField(TEXT("screen_left"), Screen.Min.X);
      Item->SetNumberField(TEXT("screen_right"), Screen.Max.X);
      Item->SetNumberField(TEXT("screen_top"), Screen.Min.Y);
      Item->SetNumberField(TEXT("screen_bottom"), Screen.Max.Y);
    }
    if (Projected != 8)
      Unprojectable.Add(MakeShared<FJsonValueNumber>(Id));
    const bool Crosses =
        Projected > 0 && (Screen.Min.X < Left || Screen.Max.X > Right ||
                          Screen.Min.Y < Top || Screen.Max.Y > Bottom);
    Item->SetBoolField(TEXT("bounds_cross_board_safe_rectangle"), Crosses);
    if (Crosses)
      Outside.Add(MakeShared<FJsonValueNumber>(Id));
    Units.Add(MakeShared<FJsonValueObject>(Item));
  }
  Sample->SetArrayField(TEXT("units"), Units);
  Sample->SetArrayField(TEXT("bounds_outside_safe_ids"), Outside);
  Sample->SetArrayField(TEXT("unprojectable_ids"), Unprojectable);
  Sample->SetArrayField(TEXT("missing_or_invisible_component_ids"), Missing);
  E.ProjectedBoundsSamples.Add(MakeShared<FJsonValueObject>(Sample));
}
Object Metrics(TArray<double> Samples) {
  auto Json = MakeShared<FJsonObject>();
  Samples.Sort();
  Json->SetNumberField(TEXT("samples"), Samples.Num());
  Json->SetBoolField(TEXT("available"), !Samples.IsEmpty());
  if (!Samples.IsEmpty()) {
    Json->SetNumberField(TEXT("p50_ms"),
                         Samples[int((Samples.Num() - 1) * .50)]);
    Json->SetNumberField(TEXT("p95_ms"),
                         Samples[int((Samples.Num() - 1) * .95)]);
    Json->SetNumberField(TEXT("p99_ms"),
                         Samples[int((Samples.Num() - 1) * .99)]);
    Json->SetNumberField(TEXT("max_ms"), Samples.Last());
  }
  return Json;
}
void ScanPublic(const Value &Json, const FString &Path,
                TSet<FString> &Violations) {
  if (!Json.IsValid())
    return;
  if (Json->Type == EJson::Object) {
    for (const auto &Field : Json->AsObject()->Values) {
      const FString Child = Path + TEXT(".") + Field.Key;
      if (Field.Key == TEXT("gold") || Field.Key == TEXT("xp") ||
          Field.Key == TEXT("shop") || Field.Key == TEXT("bench") ||
          Field.Key == TEXT("sequence") || Field.Key == TEXT("revision") ||
          Field.Key == TEXT("shopRng") || Field.Key == TEXT("botRng"))
        Violations.Add(Child);
      ScanPublic(Field.Value, Child, Violations);
    }
  } else if (Json->Type == EJson::Array)
    for (int Index = 0; Index < Json->AsArray().Num(); ++Index)
      ScanPublic(Json->AsArray()[Index],
                 Path + FString::Printf(TEXT("[%d]"), Index), Violations);
}
void FlushFrames(AWCMatchController *P, Evidence &E) {
  if (E.FrameRows.IsEmpty())
    return;
  Append(E.Directory / (Prefix(E, P) + TEXT("-frames.csv")), E.FrameRows);
  E.FrameRows.Reset();
}
void Write(AWCMatchController *P, Evidence &E) {
  if (!E.Initialized)
    return;
  MeasurePublicPayload(P, E);
  SampleProjectedBounds(P, E);
  auto Json = BaseRecord(E, P);
  Json->SetNumberField(TEXT("public_json_chars_current"), E.PublicChars);
  Json->SetNumberField(TEXT("public_json_utf8_bytes_current"),
                       E.PublicUtf8Bytes);
  Json->SetNumberField(TEXT("public_json_chars_max"), E.MaxPublicChars);
  Json->SetNumberField(TEXT("public_json_utf8_bytes_max"),
                       E.MaxPublicUtf8Bytes);
  Json->SetNumberField(TEXT("distinct_public_payload_samples"),
                       E.PayloadSamples);
  Json->SetStringField(
      TEXT("public_payload_size_boundary"),
      TEXT("Actual received LastPublicJson TCHAR length and UTF8 conversion "
           "bytes; this excludes Unreal replication/bunch overhead and is not "
           "a captured packet size."));
  Json->SetBoolField(
      TEXT("projected_bounds_enabled"),
      FParse::Param(FCommandLine::Get(), TEXT("WCProjectedBounds")));
  Json->SetArrayField(TEXT("projected_hero_bounds_samples"),
                      E.ProjectedBoundsSamples);
  Json->SetStringField(TEXT("engine"), FEngineVersion::Current().ToString());
  Json->SetStringField(TEXT("cpu"), FPlatformMisc::GetCPUBrand());
  Json->SetStringField(TEXT("active_rhi_adapter"), GRHIAdapterName);
  Json->SetStringField(TEXT("primary_gpu_reported_by_os"),
                       FPlatformMisc::GetPrimaryGPUBrand());
  Json->SetStringField(TEXT("rhi"), GDynamicRHI ? GDynamicRHI->GetName()
                                                : TEXT("Unavailable"));
  Json->SetStringField(
      TEXT("gpu_timing_source"),
      TEXT("RHIGetGPUFrameCycles GPU0; zero samples excluded as unavailable"));
  Json->SetStringField(TEXT("profiling_boundary"),
                       TEXT("Instrumented observed viewport; busy subset "
                            "requires combat and twelve living visible units"));
  Json->SetNumberField(TEXT("network_mode"), int(P->GetNetMode()));
  Json->SetBoolField(TEXT("authority_process"), P->HasAuthority());
  Json->SetBoolField(TEXT("music_component_playing"),
                     IsValid(P->Music) && P->Music->IsPlaying());
  Json->SetNumberField(TEXT("master_volume"), P->MasterVolume);
  Json->SetNumberField(TEXT("music_volume"), P->MusicVolume);
  Json->SetNumberField(TEXT("effects_volume"), P->EffectsVolume);
  Json->SetStringField(TEXT("ui_language"), P->Language);
  Json->SetBoolField(TEXT("reduced_motion"), P->bReducedMotion);
  Json->SetBoolField(TEXT("scripted_client"),
                     FParse::Param(FCommandLine::Get(), TEXT("WCExercise")));
  Json->SetBoolField(TEXT("complete"), E.Complete);
  Json->SetBoolField(TEXT("aborted"), E.Aborted);
  Json->SetBoolField(TEXT("extended_authority_checks"), AuthorityChecks());
  Json->SetBoolField(TEXT("process_exit_requested"), E.ExitRequested);
  if (const auto *Network = P->GetGameInstance<UWCNetworkSession>()) {
    Json->SetBoolField(TEXT("host_disconnected"), Network->bHostDisconnected);
    Json->SetStringField(TEXT("network_error"), Network->LastNetworkError);
    Json->SetStringField(TEXT("network_error_detail"),
                         Network->LastNetworkDetail);
  }
  Json->SetNumberField(TEXT("prior_match_namespace"), E.PriorNamespace);
  Json->SetBoolField(TEXT("restart_requested_from_this_match"),
                     E.RestartRequested);
  Json->SetBoolField(TEXT("restart_once_enabled"),
                     FParse::Param(FCommandLine::Get(), TEXT("WCRestartOnce")));
  int SimulationSpeed = 1;
  FParse::Value(FCommandLine::Get(), TEXT("WCFast="), SimulationSpeed);
  Json->SetNumberField(TEXT("simulation_speed_multiplier"),
                       FMath::Clamp(SimulationSpeed, 1, 100));
  Json->SetNumberField(TEXT("intent_requests"), E.Commands);
  Json->SetNumberField(TEXT("actual_accepted_replies"), E.Accepted);
  Json->SetNumberField(TEXT("actual_rejected_replies"), E.Rejected);
  Json->SetNumberField(TEXT("peak_process_physical_bytes"), E.PeakMemory);
  Json->SetNumberField(TEXT("max_living_visible_units"), E.MaxVisible);
  Json->SetNumberField(TEXT("max_living_logical_units"), E.MaxLogical);
  Json->SetNumberField(TEXT("max_simultaneous_encounters"), E.MaxEncounters);
  Json->SetStringField(TEXT("public_snapshot"), E.LatestPublic);
  Json->SetStringField(TEXT("own_private_snapshot"), E.LatestPrivate);
  Json->SetObjectField(TEXT("frame_interval"), Metrics(E.Frame));
  Json->SetObjectField(TEXT("game_thread_active"), Metrics(E.Game));
  Json->SetObjectField(TEXT("render_thread_active"), Metrics(E.Render));
  Json->SetObjectField(TEXT("gpu"), Metrics(E.GPU));
  auto Busy = MakeShared<FJsonObject>();
  Busy->SetObjectField(TEXT("frame_interval"), Metrics(E.BusyFrame));
  Busy->SetObjectField(TEXT("game_thread_active"), Metrics(E.BusyGame));
  Busy->SetObjectField(TEXT("render_thread_active"), Metrics(E.BusyRender));
  Busy->SetObjectField(TEXT("gpu"), Metrics(E.BusyGPU));
  Json->SetObjectField(TEXT("twelve_unit_combat_subset"), Busy);
  Json->SetArrayField(TEXT("phase_round_transitions"), E.Transitions);
  Json->SetArrayField(TEXT("command_probes"), E.ProbeResults);
  Json->SetArrayField(TEXT("authority_takeover_transitions"),
                      E.AuthorityTransitions);
  TArray<Value> Violations;
  for (const FString &Violation : E.PrivacyViolations)
    Violations.Add(MakeShared<FJsonValueString>(Violation));
  Json->SetArrayField(TEXT("received_state_privacy_violations"), Violations);
  Json->SetStringField(TEXT("privacy_boundary"),
                       TEXT("Actual received GameState/client-RPC fields; "
                            "compare separate process audits. "
                            "This is not packet capture."));
  int X = 0, Y = 0;
  P->GetViewportSize(X, Y);
  Json->SetNumberField(TEXT("resolution_x"), X);
  Json->SetNumberField(TEXT("resolution_y"), Y);
  auto Settings = MakeShared<FJsonObject>();
  for (const TCHAR *Name :
       {TEXT("r.ScreenPercentage"),
        TEXT("r.SecondaryScreenPercentage.GameViewport"),
        TEXT("r.DynamicRes.OperationMode"), TEXT("r.VSync"), TEXT("t.MaxFPS"),
        TEXT("sg.ShadowQuality"), TEXT("sg.PostProcessQuality"),
        TEXT("r.AntiAliasingMethod"), TEXT("sg.AntiAliasingQuality"),
        TEXT("r.TSR.History.ScreenPercentage"), TEXT("r.ShadowQuality"),
        TEXT("r.DynamicGlobalIlluminationMethod"), TEXT("r.ReflectionMethod")})
    if (const auto *Variable = IConsoleManager::Get().FindConsoleVariable(Name))
      Settings->SetStringField(Name, Variable->GetString());
  Json->SetObjectField(TEXT("render_settings"), Settings);
  const FString Text = Encode(Json);
  FFileHelper::SaveStringToFile(Text, *(E.Directory / TEXT("session.json")));
  FFileHelper::SaveStringToFile(
      Text, *(E.Directory / (Prefix(E, P) + TEXT("-session.json"))));
  FlushFrames(P, E);
}
void CaptureAuthorityTakeover(AWCMatchController *P, Evidence &E) {
  if (!AuthorityChecks() || !P->HasAuthority())
    return;
  const auto *Mode = P->GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (!Mode || !Mode->Match)
    return;
  const auto &Match = *Mode->Match;
  const auto &Decisions = Match.BotLog();
  TArray<Object> Current;
  for (const auto &Seat : Match.Seats()) {
    auto State = MakeShared<FJsonObject>();
    State->SetNumberField(TEXT("seat"), Seat.id);
    State->SetBoolField(TEXT("human"), Seat.human);
    State->SetBoolField(TEXT("takeover"), Seat.takeover);
    State->SetNumberField(TEXT("health"), Seat.health);
    State->SetNumberField(TEXT("gold"), Seat.gold);
    State->SetNumberField(TEXT("xp"), Seat.xp);
    State->SetNumberField(TEXT("level"), Seat.level);
    State->SetNumberField(TEXT("revision"), Seat.revision);
    State->SetNumberField(TEXT("sequence"), Seat.sequence);
    State->SetBoolField(TEXT("locked"), Seat.shopLocked);
    State->SetStringField(TEXT("shop_rng"), LexToString(Seat.shopRng.state));
    TArray<Value> Roster, Offers;
    for (int Offer : Seat.shop)
      Offers.Add(MakeShared<FJsonValueNumber>(Offer));
    for (const auto &Unit : Seat.roster) {
      auto Item = MakeShared<FJsonObject>();
      Item->SetNumberField(TEXT("id"), Unit.id);
      Item->SetNumberField(TEXT("definition"), Unit.definition);
      Item->SetNumberField(TEXT("star"), Unit.star);
      Item->SetBoolField(TEXT("board"), Unit.onBoard);
      Item->SetNumberField(TEXT("column"), Unit.cell.column);
      Item->SetNumberField(TEXT("row"), Unit.cell.row);
      Item->SetNumberField(TEXT("bench"), Unit.bench);
      Roster.Add(MakeShared<FJsonValueObject>(Item));
    }
    State->SetArrayField(TEXT("roster"), Roster);
    State->SetArrayField(TEXT("shop"), Offers);
    Current.Add(State);
    if (E.PreviousAuthoritySeats.IsValidIndex(Seat.id) &&
        Boolean(E.PreviousAuthoritySeats[Seat.id], TEXT("human")) &&
        !Seat.human && Seat.takeover) {
      const auto Before = E.PreviousAuthoritySeats[Seat.id];
      bool InterveningCommands = false;
      for (int Index = E.AuthorityBotLogCount; Index < int(Decisions.size());
           ++Index)
        if (Decisions[Index].seat == Seat.id && Decisions[Index].reply.accepted)
          InterveningCommands = true;
      auto BeforeResources = MakeShared<FJsonObject>();
      auto AfterResources = MakeShared<FJsonObject>();
      BeforeResources->Values = Before->Values;
      AfterResources->Values = State->Values;
      for (const FString Key :
           {TEXT("human"), TEXT("takeover"), TEXT("revision")}) {
        BeforeResources->RemoveField(Key);
        AfterResources->RemoveField(Key);
      }
      const bool Comparable =
          !InterveningCommands &&
          Number(Before, TEXT("sequence")) == Number(State, TEXT("sequence")) &&
          E.AuthorityRound == Match.Round() &&
          E.AuthorityPhase == int(Match.CurrentPhase());
      const bool Preserved = Encode(BeforeResources) == Encode(AfterResources);
      auto Event = BaseRecord(E, P);
      Event->SetStringField(TEXT("event"),
                            TEXT("authority_takeover_transition"));
      Event->SetNumberField(TEXT("departed_seat"), Seat.id);
      Event->SetStringField(
          TEXT("status"), Comparable ? Preserved ? TEXT("PASS") : TEXT("FAILED")
                                     : TEXT("INCONCLUSIVE"));
      Event->SetStringField(
          TEXT("boundary"),
          TEXT("Host-only local verification record; never replicated to "
               "clients. Resource comparison is conclusive only without "
               "intervening commands or a phase/round boundary."));
      Event->SetBoolField(TEXT("intervening_bot_commands"),
                          InterveningCommands);
      Event->SetObjectField(TEXT("before"), Before);
      Event->SetObjectField(TEXT("after"), State);
      E.AuthorityTransitions.Add(MakeShared<FJsonValueObject>(Event));
      Append(E.Directory / (Prefix(E, P) + TEXT("-authority.jsonl")),
             Encode(Event) + TEXT("\n"));
    }
  }
  E.PreviousAuthoritySeats = MoveTemp(Current);
  E.AuthorityBotLogCount = int(Decisions.size());
  E.AuthorityRound = Match.Round();
  E.AuthorityPhase = int(Match.CurrentPhase());
}
void RecordSnapshot(AWCMatchController *P, Evidence &E) {
  CaptureAuthorityTakeover(P, E);
  E.LatestPublic = P->LastPublicJson;
  E.LatestPrivate = P->PrivateJson;
  ScanPublic(MakeShared<FJsonValueObject>(P->Public), TEXT("public"),
             E.PrivacyViolations);
  if (P->Private.IsValid() &&
      Number(P->Private, TEXT("seat"), -1) != P->AssignedSeat)
    E.PrivacyViolations.Add(
        TEXT("Owner-private seat differs from assigned controller"));
  const auto *Seats = P->Public->Values.Find(TEXT("seats"));
  if (Seats && (*Seats)->Type == EJson::Array &&
      (*Seats)->AsArray().IsValidIndex(P->AssignedSeat) &&
      P->Private.IsValid() && P->Private->HasField(TEXT("gold")) &&
      !Boolean((*Seats)->AsArray()[P->AssignedSeat]->AsObject(), TEXT("human")))
    E.PrivacyViolations.Add(
        TEXT("Bot-bound observer received private economy"));
  auto Json = BaseRecord(E, P);
  Json->SetObjectField(TEXT("public"), P->Public);
  if (P->Private.IsValid())
    Json->SetObjectField(TEXT("owner_private"), P->Private);
  Append(E.Directory / (Prefix(E, P) + TEXT("-snapshots.jsonl")),
         Encode(Json) + TEXT("\n"));
}
void ProbeResult(AWCMatchController *P, Evidence &E, const FString &Status,
                 const FString &Detail) {
  auto Json = BaseRecord(E, P);
  Json->SetStringField(TEXT("name"), E.ProbeName);
  Json->SetStringField(TEXT("status"), Status);
  Json->SetStringField(TEXT("detail"), Detail);
  Json->SetBoolField(TEXT("accepted"), E.LastReplyAccepted);
  Json->SetStringField(TEXT("reply"), E.LastReply);
  Json->SetNumberField(TEXT("request_id"), E.Probe.requestId);
  Json->SetNumberField(TEXT("unit"), E.Probe.unit);
  Json->SetNumberField(TEXT("observed_foreign_owner"), E.ForeignOwner);
  Json->SetStringField(TEXT("owner_private_before"), E.ProbePrivateBefore);
  Json->SetStringField(TEXT("owner_private_after"), Encode(P->Private));
  Json->SetNumberField(TEXT("sent_phase"), E.ProbePhase);
  Json->SetNumberField(TEXT("sent_round"), E.ProbeRound);
  E.ProbeResults.Add(MakeShared<FJsonValueObject>(Json));
  Append(E.Directory / (Prefix(E, P) + TEXT("-commands.jsonl")),
         Encode(Json) + TEXT("\n"));
  UE_LOG(LogTemp, Display, TEXT("WC_COMMAND_PROBE %s status=%s detail=%s"),
         *E.ProbeName, *Status, *Detail);
}
void SendProbe(AWCMatchController *P, Evidence &E) {
  const int64 Sequence = int64(Number(P->Private, TEXT("sequence")));
  const int64 Revision = int64(Number(P->Private, TEXT("revision")));
  wc::Command Command;
  Command.seat = P->AssignedSeat;
  Command.requestId = 90000000 + E.Namespace * 16 + E.ProbeStage;
  Command.sequence = Sequence + 1;
  Command.revision = Revision;
  E.ProbeGold = int(Number(P->Private, TEXT("gold")));
  E.ProbeExpectedLock = Boolean(P->Private, TEXT("locked"));
  E.ForeignOwner = -1;
  if (E.CombatProbeActive) {
    Command.requestId = 90000000 + E.Namespace * 16 + 10;
    Command.type = wc::CommandType::Buy;
    Command.slot = 0;
    E.ProbeName = TEXT("combat_phase_buy_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Preparation is locked");
  } else if (E.ProbeStage == -1) {
    Command = E.PriorMatchProbe;
    E.ProbeName = TEXT("previous_match_request_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Stale seat revision");
  } else if (E.ProbeStage == 0) {
    Command.type = wc::CommandType::Buy;
    Command.slot = 0;
    Command.sequence = Sequence + 777;
    E.ProbeName = TEXT("out_of_order_sequence_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Out-of-order command sequence");
  } else if (E.ProbeStage == 1) {
    Command.type = wc::CommandType::ToggleLock;
    E.OriginalProbe = Command;
    E.ProbeExpectedLock = !E.ProbeExpectedLock;
    E.ProbeName = TEXT("original_idempotent_lock_request");
    E.ProbeExpectedAccepted = true;
    E.ProbeReason = TEXT("Accepted");
  } else if (E.ProbeStage == 2) {
    Command = E.OriginalProbe;
    E.ProbeName = TEXT("duplicate_request_applies_once");
    E.ProbeExpectedAccepted = true;
    E.ProbeReason = TEXT("Accepted");
  } else if (E.ProbeStage == 3) {
    Command = E.OriginalProbe;
    Command.type = wc::CommandType::Reroll;
    E.ProbeName = TEXT("changed_payload_same_request_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Request ID reused with different payload");
  } else if (E.ProbeStage == 4) {
    Command.type = wc::CommandType::ToggleLock;
    Command.revision = E.OriginalProbe.revision;
    E.ProbeName = TEXT("stale_revision_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Stale seat revision");
  } else {
    Command.type = wc::CommandType::Sell;
    for (const auto &Entry : P->Public->GetArrayField(TEXT("seats"))) {
      const auto Seat = Entry->AsObject();
      if (int(Number(Seat, TEXT("id"))) == P->AssignedSeat)
        continue;
      const auto &Units = Seat->GetArrayField(TEXT("units"));
      if (!Units.IsEmpty()) {
        Command.unit = int64(Number(Units[0]->AsObject(), TEXT("id")));
        E.ForeignOwner = int(Number(Seat, TEXT("id")));
        break;
      }
    }
    if (Command.unit == 0)
      return;
    E.ProbeName = TEXT("foreign_unit_sale_rejected");
    E.ProbeExpectedAccepted = false;
    E.ProbeReason = TEXT("Unit is not owned");
  }
  E.Probe = Command;
  E.ProbeAwaiting = true;
  E.ProbeReplyAfter = E.ReplySerial;
  E.ProbeStarted = FPlatformTime::Seconds();
  E.ProbePhase = E.Phase;
  E.ProbeRound = E.Round;
  E.ProbePrivateBefore = Encode(P->Private);
  auto Json = BaseRecord(E, P);
  Json->SetStringField(TEXT("event"), TEXT("probe_sent"));
  Json->SetStringField(TEXT("name"), E.ProbeName);
  Json->SetNumberField(TEXT("request_id"), Command.requestId);
  Json->SetNumberField(TEXT("type"), int(Command.type));
  Json->SetNumberField(TEXT("sequence"), Command.sequence);
  Json->SetNumberField(TEXT("revision"), Command.revision);
  Json->SetNumberField(TEXT("unit"), Command.unit);
  Json->SetNumberField(TEXT("observed_foreign_owner"), E.ForeignOwner);
  Append(E.Directory / (Prefix(E, P) + TEXT("-commands.jsonl")),
         Encode(Json) + TEXT("\n"));
  ++E.Commands;
  P->ServerIntent(int(Command.type), int64(Command.requestId),
                  int64(Command.sequence), int64(Command.revision),
                  int64(Command.unit), Command.slot, Command.toBoard,
                  Command.cell.column, Command.cell.row);
}
bool AdvanceProbes(AWCMatchController *P, Evidence &E) {
  const int Count = PreparationProbeCount();
  if (E.ProbeStage >= Count && !E.CombatProbeActive)
    return false;
  if (E.ProbeAwaiting) {
    if (E.ReplySerial <= E.ProbeReplyAfter) {
      if (FPlatformTime::Seconds() - E.ProbeStarted > 5) {
        ProbeResult(P, E, TEXT("FAILED"),
                    TEXT("No actual reply within five wall seconds"));
        E.ProbeAwaiting = false;
        E.ProbeStage = Count;
        E.CombatProbeActive = false;
      }
      return true;
    }
    if (E.ProbeExpectedAccepted && E.LastReplyAccepted &&
        Number(P->Private, TEXT("sequence")) < double(E.Probe.sequence)) {
      if (FPlatformTime::Seconds() - E.ProbeStarted > 5) {
        ProbeResult(P, E, TEXT("FAILED"),
                    TEXT("Accepted reply without owner-private acknowledgement "
                         "within five wall seconds"));
        E.ProbeAwaiting = false;
        E.ProbeStage = Count;
        E.CombatProbeActive = false;
      }
      return true;
    }
    const bool Expected = E.LastReplyAccepted == E.ProbeExpectedAccepted &&
                          E.LastReply == E.ProbeReason;
    const bool SameBoundary =
        E.ProbePhase == E.Phase && E.ProbeRound == E.Round;
    const bool ExactState = E.ProbeExpectedAccepted && E.ProbeStage == 1
                                ? true
                                : E.ProbePrivateBefore == Encode(P->Private);
    const bool State =
        ExactState && int(Number(P->Private, TEXT("gold"))) == E.ProbeGold &&
        Boolean(P->Private, TEXT("locked")) == E.ProbeExpectedLock;
    ProbeResult(
        P, E,
        !SameBoundary       ? TEXT("NOT_RUN")
        : Expected && State ? TEXT("PASS")
                            : TEXT("FAILED"),
        !SameBoundary ? TEXT("Phase or round advanced while awaiting the "
                             "reply; state conservation is not comparable")
        : Expected && State
            ? TEXT("Actual reply and owner-private gold/lock state match "
                   "expectation")
            : TEXT("Actual reply or observed owner-private state differs"));
    E.ProbeAwaiting = false;
    if (E.CombatProbeActive) {
      E.CombatProbeActive = false;
      return false;
    }
    ++E.ProbeStage;
  }
  if (E.ProbeStage < Count) {
    if (E.Phase != int(wc::Phase::Preparation)) {
      E.ProbeName = TEXT("remaining_command_probes");
      ProbeResult(
          P, E, TEXT("NOT_RUN"),
          TEXT("Preparation ended before remaining probes could be sent"));
      E.ProbeStage = Count;
    } else
      SendProbe(P, E);
  }
  return E.ProbeStage < Count;
}
void DriverIntent(AWCMatchController *P, Evidence &E, wc::CommandType Type,
                  int64 Unit = 0, int Slot = -1, bool ToBoard = false,
                  int Column = -1, int Row = -1) {
  E.NormalAwaiting = true;
  E.NormalReplyAfter = E.ReplySerial;
  E.NormalExpectedSequence = int64(Number(P->Private, TEXT("sequence"))) + 1;
  ++E.Commands;
  auto Json = BaseRecord(E, P);
  Json->SetStringField(TEXT("event"), TEXT("normal_intent_requested"));
  Json->SetNumberField(TEXT("type"), int(Type));
  Json->SetNumberField(TEXT("unit"), Unit);
  Json->SetNumberField(TEXT("slot"), Slot);
  Json->SetBoolField(TEXT("to_board"), ToBoard);
  Json->SetNumberField(TEXT("column"), Column);
  Json->SetNumberField(TEXT("row"), Row);
  Append(E.Directory / (Prefix(E, P) + TEXT("-commands.jsonl")),
         Encode(Json) + TEXT("\n"));
  P->Intent(Type, Unit, Slot, ToBoard, Column, Row);
}
} // namespace

void WCRecordVerificationReply(AWCMatchController *P, bool Accepted,
                               const FString &Reason) {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCExercise")) &&
      !FParse::Param(FCommandLine::Get(), TEXT("WCProfile")) &&
      !FParse::Param(FCommandLine::Get(), TEXT("WCShots")))
    return;
  auto &E = EvidenceStates.FindOrAdd(P);
  ++E.ReplySerial;
  E.LastReplyAccepted = Accepted;
  E.LastReply = Reason;
  if (Accepted)
    ++E.Accepted;
  else
    ++E.Rejected;
  if (!E.Initialized)
    return;
  auto Json = BaseRecord(E, P);
  Json->SetStringField(TEXT("event"), TEXT("actual_client_reply"));
  Json->SetBoolField(TEXT("accepted"), Accepted);
  Json->SetStringField(TEXT("reason"), Reason);
  Json->SetNumberField(TEXT("reply_serial"), E.ReplySerial);
  Append(E.Directory / (Prefix(E, P) + TEXT("-commands.jsonl")),
         Encode(Json) + TEXT("\n"));
}

void WCTickVerification(AWCMatchController *P, float Delta) {
  const bool Exercise = FParse::Param(FCommandLine::Get(), TEXT("WCExercise"));
  const bool Profile = FParse::Param(FCommandLine::Get(), TEXT("WCProfile"));
  const bool Shots = FParse::Param(FCommandLine::Get(), TEXT("WCShots"));
  int ExitAfter = 0;
  const bool BoundedRun =
      FParse::Value(FCommandLine::Get(), TEXT("WCExitAfter="), ExitAfter);
  if (!Exercise && !Profile && !Shots && !BoundedRun && Options().Hero < 0)
    return;
  if (!P->Public.IsValid())
    return;
  auto &E = EvidenceStates.FindOrAdd(P);
  const double Now = FPlatformTime::Seconds();
  const int64 Namespace = int64(Number(P->Public, TEXT("matchNamespace")));
  if (!E.Initialized || E.Namespace != Namespace) {
    if (E.Initialized)
      Write(P, E);
    const wc::Command PreviousOriginal = E.Namespace > 0 ? E.OriginalProbe : E.PriorMatchProbe;
    const int64 PreviousNamespace = E.Namespace > 0 ? E.Namespace : E.PriorNamespace;
    E = Evidence{};
    if (AuthorityChecks() && PreviousOriginal.requestId && PreviousNamespace > 0) {
      E.PriorMatchProbe = PreviousOriginal;
      E.PriorNamespace = PreviousNamespace;
      if (Namespace > PreviousNamespace)
        E.ProbeStage = -1;
    }
    E.Initialized = true;
    E.Namespace = Namespace;
    const auto *Mode = P->GetWorld()->GetAuthGameMode<AWCMatchMode>();
    if (Mode && Mode->Match)
      CaptureAuthoritySeed(E, int64(Mode->Match->Namespace()),
                           Mode->Match->Seed());
    E.StartWall = Now;
    FString Directory;
    if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory))
      Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence") /
                  FString::Printf(TEXT("instance-%u"),
                                  FPlatformProcess::GetCurrentProcessId());
    E.Directory = FPaths::ConvertRelativePathToFull(Directory);
    IFileManager::Get().MakeDirectory(*E.Directory, true);
    Append(E.Directory / (Prefix(E, P) + TEXT("-frames.csv")),
           TEXT("wall_seconds,phase,round,visible_alive,logical_alive,"
                "encounters,frame_ms,game_ms,render_"
                "ms,gpu_ms,gpu_available,public_chars,public_utf8_bytes,neutral_round,neutral_live_encounters\n"));
    UE_LOG(LogTemp, Display,
           TEXT("WC_EVIDENCE_SESSION namespace=%lld directory=%s"), Namespace,
           *E.Directory);
  }
  const int Phase = int(Number(P->Public, TEXT("phase"), -1));
  const int Round = int(Number(P->Public, TEXT("round")));
  FollowHero(P, E);
  MeasurePublicPayload(P, E);
  if (E.Phase != Phase || E.Round != Round) {
    E.PhaseChangedAt = Now;
    E.Phase = Phase;
    E.Round = Round;
    E.Rerolls = 0;
    E.NextShot = Now + .3;
    E.NormalAwaiting = false;
    auto Transition = BaseRecord(E, P);
    Transition->SetObjectField(TEXT("public"), P->Public);
    if (P->Private.IsValid())
      Transition->SetObjectField(TEXT("owner_private"), P->Private);
    E.Transitions.Add(MakeShared<FJsonValueObject>(Transition));
    RecordSnapshot(P, E);
    Write(P, E);
  }
  E.LatestPublic = P->LastPublicJson;
  E.LatestPrivate = P->PrivateJson;
  const auto *Session = P->GetGameInstance<UWCNetworkSession>();
  const bool WasAborted = E.Aborted;
  E.Aborted =
      Phase == int(wc::Phase::Aborted) || (Session && Session->bMatchAborted);
  int Visible = 0, Logical = 0, Encounters = 0, NeutralEncounters = 0;
  if (P->Presenter)
    for (const auto &Unit : P->Presenter->VisibleUnits)
      if (Number(Unit->AsObject(), TEXT("hp")) > 0)
        ++Visible;
  if (P->Public->HasTypedField<EJson::Array>(TEXT("encounters"))) {
    for (const auto &Encounter : P->Public->GetArrayField(TEXT("encounters"))) {
      auto Item = Encounter->AsObject();
      if (!Boolean(Item, TEXT("complete"))) {
        ++Encounters;
        if (Boolean(Item, TEXT("neutral"))) ++NeutralEncounters;
      }
      for (const auto &Unit : Item->GetArrayField(TEXT("units")))
        if (Number(Unit->AsObject(), TEXT("hp")) > 0)
          ++Logical;
    }
  }
  E.MaxVisible = FMath::Max(E.MaxVisible, Visible);
  E.MaxLogical = FMath::Max(E.MaxLogical, Logical);
  E.MaxEncounters = FMath::Max(E.MaxEncounters, Encounters);
  if (Shots && Now > E.NextShot) {
    const FString Key =
        FString::Printf(TEXT("phase-%d-round-%d"), Phase, Round);
    if (!E.ShotKeys.Contains(Key)) {
      E.ShotKeys.Add(Key);
      FScreenshotRequest::RequestScreenshot(
          E.Directory / (Prefix(E, P) + TEXT("-") + Key + TEXT(".png")), true,
          false);
    }
  }
  if (Shots && Phase == int(wc::Phase::Combat) && P->Presenter &&
      !FScreenshotRequest::IsScreenshotRequested()) {
    for (const auto &Value : P->Presenter->VisibleUnits) {
      const auto Unit = Value->AsObject();
      if (Number(Unit, TEXT("hp")) <= 0 ||
          Number(Unit, TEXT("state")) != int(wc::ActionState::CastRecovery))
        continue;
      const FString Key = FString::Printf(TEXT("active-def-%d"),
                                          int(Number(Unit, TEXT("def"))));
      if (E.ShotKeys.Contains(Key))
        continue;
      E.ShotKeys.Add(Key);
      const FString Path =
          E.Directory / (Prefix(E, P) + TEXT("-") + Key + TEXT(".png"));
      auto Record = BaseRecord(E, P);
      Record->SetStringField(TEXT("capture"), Path);
      Record->SetStringField(
          TEXT("boundary"),
          TEXT("Screenshot requested on the first observed active-skill "
               "recovery for this definition. The next rendered frame supplies "
               "the image; this is not frame-exact video."));
      Record->SetObjectField(TEXT("observed_unit"), Unit);
      Append(E.Directory / (Prefix(E, P) + TEXT("-skill-shots.jsonl")),
             Encode(Record) + TEXT("\n"));
      FScreenshotRequest::RequestScreenshot(Path, true, false);
      break;
    }
  }
  if (Profile && Now - E.StartWall >= 5 && !E.Complete && !E.Aborted) {
    const double Frame = Delta * 1000,
                 Game = FPlatformTime::ToMilliseconds(GGameThreadTime),
                 Render = FPlatformTime::ToMilliseconds(GRenderThreadTime);
    const uint32 Cycles = GDynamicRHI ? RHIGetGPUFrameCycles() : 0;
    const double GPU = Cycles ? FPlatformTime::ToMilliseconds(Cycles) : 0;
    E.Frame.Add(Frame);
    E.Game.Add(Game);
    E.Render.Add(Render);
    if (Cycles)
      E.GPU.Add(GPU);
    const bool Busy = Phase == int(wc::Phase::Combat) && Visible >= 12;
    if (Busy) {
      E.BusyFrame.Add(Frame);
      E.BusyGame.Add(Game);
      E.BusyRender.Add(Render);
      if (Cycles)
        E.BusyGPU.Add(GPU);
    }
    E.PeakMemory = FMath::Max<uint64>(E.PeakMemory,
                                      FPlatformMemory::GetStats().UsedPhysical);
    E.FrameRows += FString::Printf(
        TEXT("%.6f,%d,%d,%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%d,%d,%d,%d,%d\n"),
        Now - E.StartWall, Phase, Round, Visible, Logical, Encounters, Frame,
        Game, Render, GPU, Cycles ? 1 : 0, E.PublicChars, E.PublicUtf8Bytes,
        Boolean(P->Public, TEXT("neutralRound")) ? 1 : 0, NeutralEncounters);
  }
  if (Now >= E.NextFrameFlush) {
    FlushFrames(P, E);
    E.NextFrameFlush = Now + 1;
  }
  if (Now >= E.NextSnapshot) {
    RecordSnapshot(P, E);
    E.NextSnapshot = Now + .5;
  }
  if (Phase == int(wc::Phase::Finished) && !E.Complete) {
    E.Complete = true;
    E.CompletedAt = Now;
    Write(P, E);
    UE_LOG(
        LogTemp, Display,
        TEXT("WC_SCRIPTED_SESSION_FINISHED namespace=%lld seat=%d commands=%d"),
        E.Namespace, P->AssignedSeat, E.Commands);
  }
  if (Now >= E.NextWrite || (E.Aborted && !WasAborted)) {
    Write(P, E);
    E.NextWrite = Now + 10;
  }
  if (BoundedRun && Now - ProcessStart > ExitAfter) {
    E.ExitRequested = true;
    Write(P, E);
    UE_LOG(LogTemp, Display,
           TEXT("WC_VERIFICATION_PROCESS_EXIT namespace=%lld phase=%d "
                "complete=%d wall_seconds=%.3f"),
           E.Namespace, E.Phase, E.Complete, Now - ProcessStart);
    FPlatformMisc::RequestExit(false);
    return;
  }
  if (!Exercise || E.Aborted || (Session && Session->IsStartupRouting()))
    return;
  if (E.Complete) {
    int RequestedRestarts = FParse::Param(FCommandLine::Get(), TEXT("WCRestartOnce")) ? 1 : 0;
    FParse::Value(FCommandLine::Get(), TEXT("WCRestartCount="), RequestedRestarts);
    RequestedRestarts = FMath::Clamp(RequestedRestarts, 0, 2);
    if (RestartedControllers.FindRef(P) < RequestedRestarts &&
        P->HasAuthority() && P->AssignedSeat == 0 &&
        Now - E.CompletedAt >= 2) {
      int Humans = 0;
      for (const auto &Seat : P->Public->GetArrayField(TEXT("seats")))
        if (Boolean(Seat->AsObject(), TEXT("human")))
          ++Humans;
      const int RestartIndex = ++RestartedControllers.FindOrAdd(P);
      E.RestartRequested = true;
      Write(P, E);
      UE_LOG(LogTemp, Display,
             TEXT("WC_SCRIPTED_RESTART_REQUEST namespace=%lld humans=%d"),
             E.Namespace, Humans);
      P->ServerStart(Humans, RestartIndex == 1 ? 271828 : 161803);
    }
    return;
  }
  if (E.ProbeAwaiting) {
    AdvanceProbes(P, E);
    return;
  }
  if (E.NormalAwaiting) {
    if (E.ReplySerial <= E.NormalReplyAfter)
      return;
    if (E.LastReplyAccepted &&
        Number(P->Private, TEXT("sequence")) < E.NormalExpectedSequence)
      return;
    E.NormalAwaiting = false;
  }
  if (AuthorityChecks() && Phase == int(wc::Phase::Combat) &&
      !E.CombatProbeSent && Round >= 4 && Now - E.PhaseChangedAt >= .05 &&
      P->Private.IsValid() && P->Private->HasField(TEXT("revision"))) {
    E.CombatProbeSent = true;
    E.CombatProbeActive = true;
    SendProbe(P, E);
    if (E.ReplySerial > E.ProbeReplyAfter)
      AdvanceProbes(P, E);
    return;
  }
  if (Now < E.NextAction)
    return;
  E.NextAction = Now + .18;
  if (Phase < 0 && P->AssignedSeat == 0) {
    const bool Network = Boolean(P->Public, TEXT("network"));
    if (!Network || Number(P->Public, TEXT("connected")) == 2)
      P->ServerStart(Network ? 2 : 1, Options().Seed);
    return;
  }
  if (Phase != int(wc::Phase::Preparation) || !P->Private.IsValid() ||
      !P->Private->HasField(TEXT("units")) || !P->Presenter)
    return;
  if ((int64(Number(P->Private, TEXT("revision"))) >> 32) != E.Namespace)
    return;
  const auto &Seats = P->Public->GetArrayField(TEXT("seats"));
  if (!Seats.IsValidIndex(P->AssignedSeat) ||
      Number(Seats[P->AssignedSeat]->AsObject(), TEXT("health")) <= 0 ||
      !Boolean(Seats[P->AssignedSeat]->AsObject(), TEXT("human")))
    return;
  if (Boolean(P->Private, TEXT("ready")))
    return;
  if (E.ProbeStage < PreparationProbeCount() && AdvanceProbes(P, E))
    return;
  if (Boolean(P->Private, TEXT("locked"))) {
    DriverIntent(P, E, wc::CommandType::ToggleLock);
    return;
  }
  const auto &Units = P->Private->GetArrayField(TEXT("units"));
  const int Level = int(Number(P->Private, TEXT("level"))),
            Gold = int(Number(P->Private, TEXT("gold")));
  int Deployed = 0;
  TSet<int> Cells;
  Object Bench;
  for (const auto &Entry : Units) {
    auto Unit = Entry->AsObject();
    if (Boolean(Unit, TEXT("board"))) {
      ++Deployed;
      Cells.Add(int(Number(Unit, TEXT("row"))) * 8 +
                int(Number(Unit, TEXT("col"))));
    } else if (!Bench.IsValid())
      Bench = Unit;
  }
  if (Bench.IsValid() && Deployed < Level) {
    const int Definition = int(Number(Bench, TEXT("def")));
    const bool Ranged = P->Presenter->Definitions.units[Definition].range > 1;
    const TArray<int> Rows =
        Ranged ? TArray<int>{0, 1, 2, 3} : TArray<int>{3, 2, 1, 0};
    for (int Row : Rows)
      for (int Column : {3, 4, 2, 5, 1, 6, 0, 7})
        if (!Cells.Contains(Row * 8 + Column)) {
          DriverIntent(P, E, wc::CommandType::Move,
                       int64(Number(Bench, TEXT("id"))), -1, true, Column, Row);
          return;
        }
  }
  const auto &Shop = P->Private->GetArrayField(TEXT("shop"));
  for (int Slot = 0; Slot < Shop.Num(); ++Slot) {
    const int Definition = int(Shop[Slot]->AsNumber());
    if (Definition < 0)
      continue;
    const auto &Unit = P->Presenter->Definitions.units[Definition];
    int Copies = 0;
    for (const auto &Entry : Units)
      if (int(Number(Entry->AsObject(), TEXT("def"))) == Definition &&
          Number(Entry->AsObject(), TEXT("star")) == 1)
        ++Copies;
    if (Gold >= Unit.cost && (Units.Num() < Level || Copies >= 2) &&
        Units.Num() < Level + 8) {
      DriverIntent(P, E, wc::CommandType::Buy, 0, Slot);
      return;
    }
  }
  if (Level < P->Presenter->Definitions.rules.maximumLevel &&
      Gold >= P->Presenter->Definitions.rules.buyXpGold && Deployed >= Level) {
    DriverIntent(P, E, wc::CommandType::BuyXp);
    return;
  }
  if (E.Rerolls < 1 && Gold >= P->Presenter->Definitions.rules.rerollCost) {
    ++E.Rerolls;
    DriverIntent(P, E, wc::CommandType::Reroll);
    return;
  }
  DriverIntent(P, E, wc::CommandType::Ready);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FWCVerificationNamespaceSeedTest,
    "WonderChess.Verification.NamespaceSeedIsolation",
    EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::EngineFilter)
bool FWCVerificationNamespaceSeedTest::RunTest(const FString &) {
  Evidence Previous;
  Previous.Namespace = 1;
  CaptureAuthoritySeed(Previous, 1, 314159);
  CaptureAuthoritySeed(Previous, 2, 271828);
  CaptureAuthoritySeed(Previous, 1, 999);
  auto Json = MakeShared<FJsonObject>();
  WriteAuthoritySeed(Json, Previous);
  TestEqual(TEXT("Old namespace retains original seed after replacement"),
            Json->GetNumberField(TEXT("match_seed_authority")), 314159.0);
  Evidence Next;
  Next.Namespace = 2;
  CaptureAuthoritySeed(Next, 1, 314159);
  WriteAuthoritySeed(Json, Next);
  TestTrue(TEXT("Mismatched namespace cannot supply an authority seed"),
           Json->HasTypedField<EJson::Null>(TEXT("match_seed_authority")));
  CaptureAuthoritySeed(Next, 2, 271828);
  WriteAuthoritySeed(Json, Next);
  TestEqual(TEXT("New namespace captures its own seed"),
            Json->GetNumberField(TEXT("match_seed_authority")), 271828.0);
  Evidence Client;
  Client.Namespace = 2;
  WriteAuthoritySeed(Json, Client);
  TestTrue(TEXT("Client without authority records an explicit null"),
           Json->HasTypedField<EJson::Null>(TEXT("match_seed_authority")));
  Evidence Menu;
  Menu.Namespace = 0;
  CaptureAuthoritySeed(Menu, 0, 123);
  WriteAuthoritySeed(Json, Menu);
  TestTrue(TEXT("Menu does not claim a match seed"),
           Json->HasTypedField<EJson::Null>(TEXT("match_seed_authority")));
  return true;
}
#endif
