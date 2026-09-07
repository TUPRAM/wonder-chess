#include "WCFrontEnd.h"
#include "WCDefinitionRegistry.h"
#include "WCFrontEndScene.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "WCNetworkSession.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Text/STextBlock.h"
#include "ContentStreaming.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#include "ShaderCompiler.h"
#endif

void FWCFrontEnd::InitializeAudit() {
  if (bAuditInitialized) return;
  bAuditInitialized = true;
  FString TargetPage, TargetHero, Clip;
  FParse::Value(FCommandLine::Get(), TEXT("WCFrontEndPage="), TargetPage);
  FParse::Value(FCommandLine::Get(), TEXT("WCFrontEndHero="), TargetHero);
  FParse::Value(FCommandLine::Get(), TEXT("WCFrontEndClip="), Clip);
  bAudit = FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndAudit"));
  AuditOriginalHero = SelectedId;
  if (!TargetHero.IsEmpty()) {
    const FString Previous = SelectedId;
    SelectedId = TargetHero;
    if (SelectedIndex() < 0) SelectedId = Previous;
  }
  if (TargetPage.Equals(TEXT("Gallery"), ESearchCase::IgnoreCase)) Page = EPage::Gallery;
  if (TargetPage.Equals(TEXT("Detail"), ESearchCase::IgnoreCase)) Page = EPage::Detail;
  if (TargetPage.Equals(TEXT("Mode"), ESearchCase::IgnoreCase)) Page = EPage::Mode;
  if (TargetPage.Equals(TEXT("Settings"), ESearchCase::IgnoreCase)) Page = EPage::Settings;
  FParse::Value(FCommandLine::Get(), TEXT("WCFrontEndStar="), Star);
  Star = FMath::Clamp(Star, 1, 3);
  if (Scene.IsValid()) {
    Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
    if (!Clip.IsEmpty()) Scene->PlayClip(Clip, Controller->bReducedMotion);
  }
  if (!bAudit) return;
  AuditAt = FPlatformTime::Seconds() + 4;
  AuditPrefix = FDateTime::UtcNow().ToString(TEXT("%Y%m%dT%H%M%S"));
  if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), AuditDirectory))
    AuditDirectory = FPaths::ProjectSavedDir() / TEXT("FrontEndAudit") / AuditPrefix;
  AuditDirectory = FPaths::ConvertRelativePathToFull(AuditDirectory);
  IFileManager::Get().MakeDirectory(*AuditDirectory, true);
  AuditReport = MakeShared<FJsonObject>();
  AuditReport->SetStringField(TEXT("status"), TEXT("RUNNING"));
  AuditReport->SetStringField(TEXT("started_utc"), FDateTime::UtcNow().ToIso8601());
  AuditReport->SetStringField(TEXT("method"), TEXT("Real native Slate viewport. Selected navigation uses focused Slate Enter down/up events; exhaustive filter and catalog coverage uses the same view-model methods. Asset presence is not continuous animation review. No physical human input or two-machine LAN claim."));
  AuditReport->SetStringField(TEXT("balance_version"), UTF8_TO_TCHAR(Controller->Presenter->Definitions.balanceVersion.c_str()));
  AuditReport->SetStringField(TEXT("content_digest"), UTF8_TO_TCHAR(Controller->Presenter->Definitions.contentDigest.c_str()));
  AuditReport->SetArrayField(TEXT("checks"), {});
  AuditReport->SetArrayField(TEXT("screenshots"), {});
  AuditReport->SetBoolField(TEXT("original_reduced_motion"), Controller->bReducedMotion);
  UE_LOG(LogTemp, Display, TEXT("WC_FRONTEND_AUDIT_STARTED directory=%s"), *AuditDirectory);
}

void FWCFrontEnd::AuditCheck(const FString& Name, bool Pass, const FString& Detail) {
  auto Checks = AuditReport->GetArrayField(TEXT("checks"));
  auto Item = MakeShared<FJsonObject>();
  Item->SetStringField(TEXT("name"), Name);
  Item->SetBoolField(TEXT("pass"), Pass);
  Item->SetStringField(TEXT("detail"), Detail);
  Checks.Add(MakeShared<FJsonValueObject>(Item));
  AuditReport->SetArrayField(TEXT("checks"), Checks);
  UE_LOG(LogTemp, Display, TEXT("WC_FRONTEND_CHECK %s %s %s"), Pass ? TEXT("PASS") : TEXT("FAIL"), *Name, *Detail);
}

bool FWCFrontEnd::AuditKey(const FString& ButtonLabel) {
  const auto Target = Buttons.FindRef(ButtonLabel).Pin();
  if (!Target || !Target->IsEnabled()) return false;
  auto& Slate = FSlateApplication::Get();
  Slate.SetKeyboardFocus(Target, EFocusCause::SetDirectly);
  const FKeyEvent Down(EKeys::Enter, FModifierKeysState(), 0, false, 0, 0);
  const FKeyEvent Up(EKeys::Enter, FModifierKeysState(), 0, false, 0, 0);
  Slate.ProcessKeyDownEvent(Down);
  Slate.ProcessKeyUpEvent(Up);
  return true;
}

void FWCFrontEnd::AuditCatalog() {
  const auto& Catalog = Controller->Presenter->Definitions;
  AuditCheck(TEXT("24 runtime heroes"), Catalog.units.size() == 24);
  TSet<FString> Names;
  int StarRows = 0, EffectRows = 0, Clips = 0, Meshes = 0, PortraitCount = 0;
  for (const auto& Unit : Catalog.units) {
    const FString Id = UTF8_TO_TCHAR(Unit.id.c_str());
    const auto Text = Controller->Presenter->Metadata.Units.FindRef(Id);
    if (!Text) { AuditCheck(Id + TEXT(" metadata"), false); continue; }
    const FString DisplayName = Text->GetStringField(TEXT("display_name"));
    AuditCheck(Id + TEXT(" short name"), !DisplayName.IsEmpty() && !Names.Contains(DisplayName));
    Names.Add(DisplayName);
    const auto Stats = Text->GetObjectField(TEXT("stats"));
    const auto& Effects = Text->GetObjectField(TEXT("ability"))->GetArrayField(TEXT("effects"));
    AuditCheck(Id + TEXT(" effect count"), Effects.Num() == int(Unit.ability.effects.size()));
    for (int SelectedStar = 1; SelectedStar <= 3; ++SelectedStar) {
      ++StarRows;
      const auto Health = wc::StarValue(Unit.health, SelectedStar, 0, Catalog.rules);
      const auto Damage = wc::StarValue(Unit.attackDamage, SelectedStar, 0, Catalog.rules);
      const auto AuthoredHealth = wc::StarValue(wc::Int(Stats->GetNumberField(TEXT("health_cp"))), SelectedStar, 0, Catalog.rules);
      const auto AuthoredDamage = wc::StarValue(wc::Int(Stats->GetNumberField(TEXT("attack_damage_cp"))), SelectedStar, 0, Catalog.rules);
      AuditCheck(FString::Printf(TEXT("%s star %d stats"), *Id, SelectedStar), Health == AuthoredHealth && Damage == AuthoredDamage,
          FString::Printf(TEXT("health_cp=%lld basic_cp=%lld"), Health, Damage));
      for (int EffectIndex = 0; EffectIndex < Effects.Num() && EffectIndex < int(Unit.ability.effects.size()); ++EffectIndex) {
        ++EffectRows;
        const auto Value = wc::Int(Effects[EffectIndex]->AsObject()->GetArrayField(TEXT("magnitude_by_star"))[SelectedStar - 1]->AsNumber());
        AuditCheck(FString::Printf(TEXT("%s star %d effect %d magnitude"), *Id, SelectedStar, EffectIndex),
                   Value == Unit.ability.effects[EffectIndex].magnitude[SelectedStar - 1]);
      }
    }
    auto AssetPath = [&Id](const FString& Name) { return TEXT("/Game/WonderChess/Heroes/") + Id + TEXT("/") + Name + TEXT(".") + Name; };
    auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *AssetPath(TEXT("SK_") + Id));
    if (Mesh) { Assets.Add(Mesh); ++Meshes; }
    AuditCheck(Id + TEXT(" skeletal mesh present"), Mesh != nullptr);
    auto* PortraitAsset = LoadObject<UTexture2D>(nullptr, *AssetPath(TEXT("T_") + Id + TEXT("_Portrait")));
    if (PortraitAsset) { Assets.Add(PortraitAsset); ++PortraitCount; }
    AuditCheck(Id + TEXT(" portrait present"), PortraitAsset != nullptr);
    for (const TCHAR* Clip : {TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Active"), TEXT("Hit"), TEXT("Defeat"), TEXT("Victory")}) {
      auto* Animation = LoadObject<UAnimSequence>(nullptr, *AssetPath(TEXT("AN_") + Id + TEXT("_") + Clip));
      if (Animation) { Assets.Add(Animation); ++Clips; }
      AuditCheck(Id + TEXT(" / ") + Clip + TEXT(" imported clip"), Animation && Animation->GetPlayLength() > 0,
                 TEXT("Presence and positive duration only; not continuous motion acceptance."));
    }
  }
  AuditReport->SetNumberField(TEXT("star_rows_checked"), StarRows);
  AuditReport->SetNumberField(TEXT("effect_star_rows_checked"), EffectRows);
  AuditReport->SetNumberField(TEXT("meshes_present"), Meshes);
  AuditReport->SetNumberField(TEXT("portraits_present"), PortraitCount);
  AuditReport->SetNumberField(TEXT("clips_present"), Clips);
  Filters.Reset(); Search.Reset(); RefreshResults();
  AuditCheck(TEXT("Unfiltered gallery returns 24"), Results.Num() == 24);
  Search = TEXT("aDa BRIGHTSHIELD"); RefreshResults();
  AuditCheck(TEXT("Full name search ignores case"), Results.Num() == 1 && Catalog.units[Results[0]].id == "wc_u_human_guardian");
  Search = TEXT("ada"); RefreshResults();
  AuditCheck(TEXT("Short name search"), Results.Num() == 1 && Catalog.units[Results[0]].id == "wc_u_human_guardian");
  Search.Reset();
  Filters.FindOrAdd(TEXT("race")) = {TEXT("human"), TEXT("dwarf")};
  Filters.FindOrAdd(TEXT("unit_class")) = {TEXT("guardian"), TEXT("priest")};
  RefreshResults();
  TSet<FString> Found;
  for (int Index : Results) Found.Add(UTF8_TO_TCHAR(Catalog.units[Index].id.c_str()));
  AuditCheck(TEXT("Race OR and class OR combine with AND"), Found.Num() == 4 &&
      Found.Contains(TEXT("wc_u_human_guardian")) && Found.Contains(TEXT("wc_u_human_priest")) &&
      Found.Contains(TEXT("wc_u_dwarf_guardian")) && Found.Contains(TEXT("wc_u_dwarf_priest")));
  Filters.Reset();
  Filters.FindOrAdd(TEXT("role")) = {TEXT("healer"), TEXT("tank")};
  Filters.FindOrAdd(TEXT("cost")) = {TEXT("1"), TEXT("3")};
  Filters.FindOrAdd(TEXT("race")) = {TEXT("human"), TEXT("dwarf")};
  RefreshResults(); Found.Reset();
  for (int Index : Results) Found.Add(UTF8_TO_TCHAR(Catalog.units[Index].id.c_str()));
  AuditCheck(TEXT("Role OR, cost OR and race OR combine with AND"), Found.Num() == 3 &&
      Found.Contains(TEXT("wc_u_human_guardian")) && Found.Contains(TEXT("wc_u_human_priest")) && Found.Contains(TEXT("wc_u_dwarf_guardian")));
  Filters.Reset(); Search = TEXT("no-such-hero-unique-audit-query"); RefreshResults();
  AuditCheck(TEXT("Empty search result"), Results.IsEmpty());
  Filters.Reset(); Search.Reset(); RefreshResults();
}

void FWCFrontEnd::AuditCapture(const FString& Name) {
  const FString Path = AuditDirectory / (AuditPrefix + TEXT("-") + Name + TEXT(".png"));
  FScreenshotRequest::RequestScreenshot(Path, true, false);
  auto Shots = AuditReport->GetArrayField(TEXT("screenshots"));
  auto Shot = MakeShared<FJsonObject>();
  Shot->SetStringField(TEXT("path"), Path);
  Shot->SetStringField(TEXT("screen"), Name);
  Shot->SetStringField(TEXT("method"), TEXT("FScreenshotRequest with Slate UI, actual rendered viewport"));
  Shot->SetStringField(TEXT("requested_utc"), FDateTime::UtcNow().ToIso8601());
  if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport) {
    const FIntPoint Size = GEngine->GameViewport->Viewport->GetSizeXY();
    Shot->SetNumberField(TEXT("viewport_width"), Size.X);
    Shot->SetNumberField(TEXT("viewport_height"), Size.Y);
  }
  if (Name.StartsWith(TEXT("roster-"))) {
    Shot->SetStringField(TEXT("hero_id"), SelectedId);
    Shot->SetStringField(TEXT("clip"), Scene.IsValid() ? Scene->SelectedClip : TEXT("missing scene"));
    Shot->SetStringField(TEXT("selection_method"), TEXT("Hero: native view model; clip: focused Slate Enter"));
    Shot->SetStringField(TEXT("review_boundary"), TEXT("Single actual rendered pose; not continuous clip review"));
  }
  if (Name.StartsWith(TEXT("seat-introduction")))
    Shot->SetNumberField(TEXT("seconds_after_introduction_observed"), FPlatformTime::Seconds() - AuditIntroObservedAt);
  else if (Scene.IsValid() && (Name == TEXT("lobby") || Name.StartsWith(TEXT("ada-"))))
    Shot->SetObjectField(TEXT("grounding_probe"), Scene->MeasureGrounding());
  Shots.Add(MakeShared<FJsonValueObject>(Shot));
  AuditReport->SetArrayField(TEXT("screenshots"), Shots);
}

void FWCFrontEnd::TickAudit() {
  if (!bAudit || bAuditFinished || !Controller.IsValid() || FPlatformTime::Seconds() < AuditAt || GFrameCounter < AuditFrameAt) return;
  auto Preview = [this]() -> USkeletalMeshComponent* {
    return Scene.IsValid() ? Scene->FindComponentByClass<USkeletalMeshComponent>() : nullptr;
  };
  auto ReducedLabel = [this]() {
    return Local(Controller->bReducedMotion ? TEXT("Reduced motion: on") : TEXT("Reduced motion: off"),
                 Controller->bReducedMotion ? TEXT("Gerakan terbatas: aktif") : TEXT("Gerakan terbatas: nonaktif"));
  };
  if ((AuditStage >= 25 && AuditStage <= 38) || (AuditStage >= 40 && AuditStage <= 53)) {
    const bool Reduced = AuditStage < 40;
    const int32 Step = AuditStage++ - (Reduced ? 25 : 40);
    const TCHAR* Clips[] = {TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Active"), TEXT("Hit"), TEXT("Defeat"), TEXT("Victory")};
    const FString Clip = Clips[Step / 2];
    const auto Motion = AuditReport->GetObjectField(TEXT("reduced_motion_audit"));
    if (Step % 2 == 0) {
      const bool Activated = AuditKey(Clip == TEXT("Active") ? Local(TEXT("Skill"), TEXT("Skill")) : Clip);
      auto* Mesh = Preview();
      auto* Instance = Mesh ? Mesh->GetSingleNodeInstance() : nullptr;
      auto* Asset = Instance ? Instance->GetCurrentAsset() : nullptr;
      const FString ExpectedAsset = TEXT("AN_wc_u_human_guardian_") + Clip;
      AuditCheck(Clip + (Reduced ? TEXT(" reduced Slate selection") : TEXT(" playback Slate selection")),
          Activated && Asset && Asset->GetName() == ExpectedAsset && Scene->SelectedClip == Clip &&
          Controller->bReducedMotion == Reduced && Mesh->bPauseAnims == Reduced,
          TEXT("Focused native Slate Enter; actual single-node asset and pause state inspected."));
      Motion->SetNumberField(TEXT("sample_position"), Mesh ? Mesh->GetPosition() : -1);
      Motion->SetNumberField(TEXT("sample_yaw"), Mesh ? Mesh->GetRelativeRotation().Yaw : 0);
      Motion->SetNumberField(TEXT("sample_started"), FPlatformTime::Seconds());
      AuditAt = FPlatformTime::Seconds() + (Reduced ? .25 : .137);
      AuditFrameAt = GFrameCounter + 3;
    } else {
      const auto* Mesh = Preview();
      const double Start = Motion->GetNumberField(TEXT("sample_position"));
      const double Position = Mesh ? Mesh->GetPosition() : -1;
      const double Elapsed = FPlatformTime::Seconds() - Motion->GetNumberField(TEXT("sample_started"));
      const double YawDelta = Mesh ? FMath::Abs(FMath::FindDeltaAngleDegrees(
          float(Motion->GetNumberField(TEXT("sample_yaw"))), Mesh->GetRelativeRotation().Yaw)) : 360;
      const bool PositionPass = Reduced ? FMath::Abs(Position - Start) < .0001 && FMath::Abs(Position) < .0001 : FMath::Abs(Position - Start) > .0001;
      AuditCheck(Clip + (Reduced ? TEXT(" holds first pose across ticks") : TEXT(" advances across ticks")),
          Mesh && Mesh->GetSingleNodeInstance() && Mesh->bPauseAnims == Reduced && Start >= 0 && PositionPass,
          FString::Printf(TEXT("position_before=%.6f position_after=%.6f elapsed_seconds=%.3f"), Start, Position, Elapsed));
      AuditCheck(Clip + (Reduced ? TEXT(" reduced rotation stable") : TEXT(" playback leaves turntable off")),
          Mesh && !bTurntable && YawDelta < .001,
          FString::Printf(TEXT("yaw_delta_degrees=%.6f elapsed_seconds=%.3f"), YawDelta, Elapsed));
      AuditAt = FPlatformTime::Seconds() + .03;
    }
    return;
  }
  if (AuditStage == 17 && FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndAllHeroes"))) {
    const auto& Roster = Controller->Presenter->Definitions.units;
    if (AuditRosterStage < int32(Roster.size()) * 4) {
      const int32 Hero = AuditRosterStage / 4, Step = AuditRosterStage++ % 4;
      const FString Id = UTF8_TO_TCHAR(Roster[Hero].id.c_str());
      if (Step == 0) {
        OpenHero(Hero);
        AuditCheck(Id + TEXT(" Slate Idle"), AuditKey(TEXT("Idle")) && Scene.IsValid() && Scene->SelectedClip == TEXT("Idle"));
      } else if (Step == 2) {
        AuditCheck(Id + TEXT(" Slate Active"), AuditKey(Local(TEXT("Skill"), TEXT("Skill"))) && Scene.IsValid() && Scene->SelectedClip == TEXT("Active"));
      } else {
        AuditCapture(TEXT("roster-") + Id + (Step == 1 ? TEXT("-Idle") : TEXT("-Active")));
      }
      AuditAt = FPlatformTime::Seconds() + ((Step % 2) == 0 ? .4 : .15);
      AuditFrameAt = GFrameCounter + ((Step % 2) == 0 ? 5 : 1);
      return;
    }
  }
  AuditAt = FPlatformTime::Seconds() + 2.5;
  auto Select = [this](const TCHAR* Id) {
    SelectedId = Id;
    if (SelectedIndex() >= 0) OpenHero(SelectedIndex());
  };
  switch (AuditStage++) {
    case 0:
      AuditCatalog();
      Page = EPage::Lobby; Rebuild();
      break;
    case 1:
      AuditCheck(TEXT("Original Brighthaven approach mesh loaded"), Scene.IsValid() && Scene->bApproachImported);
      AuditCapture(TEXT("lobby"));
      break;
    case 2:
      AuditCheck(TEXT("Slate Enter opens Heroes"), AuditKey(Local(TEXT("Heroes"), TEXT("Hero"))) && Page == EPage::Gallery);
      break;
    case 3:
      AuditCapture(TEXT("gallery"));
      break;
    case 4:
      Search = TEXT("no-such-hero-unique-audit-query"); RefreshGrid();
      break;
    case 5:
      AuditCapture(TEXT("no-results"));
      break;
    case 6:
      AuditCheck(TEXT("Slate Enter clears empty-state filters"), AuditKey(Local(TEXT("Clear filters"), TEXT("Hapus filter"))) && Search.IsEmpty() && Results.Num() == 24);
      Select(TEXT("wc_u_human_guardian"));
      break;
    case 7:
      AuditCheck(TEXT("Slate star button selects 2"), AuditKey(TEXT("2 ★")) && Star == 2);
      AuditCheck(TEXT("Slate Skill button plays Active"), AuditKey(Local(TEXT("Skill"), TEXT("Skill"))) && Scene.IsValid() && Scene->SelectedClip == TEXT("Active"));
      break;
    case 8:
      AuditCapture(TEXT("ada-star2-active"));
      break;
    case 9:
      AuditCheck(TEXT("Slate Synergies tab"), AuditKey(TEXT("Synergies")) && DetailTab == TEXT("Synergies"));
      break;
    case 10:
      AuditCapture(TEXT("ada-synergies"));
      break;
    case 11:
      Select(TEXT("wc_u_halfling_warrior")); DetailTab = TEXT("Story"); Rebuild();
      break;
    case 12:
      AuditCapture(TEXT("halfling-story"));
      break;
    case 13:
      Select(TEXT("wc_u_dragonkin_guardian")); DetailTab = TEXT("Skill"); Rebuild();
      break;
    case 14:
      AuditCapture(TEXT("dragonkin-skill"));
      break;
    case 15:
      Select(TEXT("wc_u_human_guardian"));
      AuditCheck(TEXT("Slate Move preview"), AuditKey(TEXT("Move")) && Scene.IsValid() && Scene->SelectedClip == TEXT("Move"));
      break;
    case 16:
      AuditCapture(TEXT("ada-move"));
      break;
    case 17:
      if (auto* Mode = Controller->GetWorld()->GetAuthGameMode<AWCMatchMode>(); Mode && !Mode->Match && Controller->GetNetMode() == NM_Standalone) {
        Controller->ServerStart(1, 41031);
        AuditCheck(TEXT("Entry creates no running match"), Mode->bEntryPending && !Mode->Match);
        Controller->ServerStart(1, 41032);
        AuditCheck(TEXT("Duplicate start preserves first request"), Mode->bEntryPending && Mode->EntrySeed == 41031 && !Mode->Match);
        Controller->ServerCancelEntry();
        AuditCheck(TEXT("Cancel before introduction"), !Mode->bEntryPending && !Mode->Match && Mode->EntryState.IsEmpty());
        Controller->ServerStart(1, 41033);
        Page = EPage::Mode; Rebuild();
        AuditAt = FPlatformTime::Seconds() + .05;
        AuditEntryDeadline = FPlatformTime::Seconds() + 2;
      } else {
        AuditReport->SetStringField(TEXT("entry_fixture"), TEXT("NOT RUN: requires a standalone idle host; no LAN participants synthesized."));
        AuditStage = 23;
      }
      break;
    case 18:
      if (auto* Mode = Controller->GetWorld()->GetAuthGameMode<AWCMatchMode>()) {
        if (Mode->EntryState != TEXT("Introduction") && FPlatformTime::Seconds() < AuditEntryDeadline) {
          --AuditStage; AuditAt = FPlatformTime::Seconds() + .03; break;
        }
        AuditCheck(TEXT("Introduction precedes match clock"), Mode->EntryState == TEXT("Introduction") && !Mode->Match);
        AuditIntroObservedAt = FPlatformTime::Seconds();
        AuditCapture(TEXT("seat-introduction-0ms"));
      }
      AuditAt = FPlatformTime::Seconds() + .5;
      break;
    case 19:
      AuditCapture(TEXT("seat-introduction-500ms"));
      AuditAt = FPlatformTime::Seconds() + 1;
      break;
    case 20:
      AuditCapture(TEXT("seat-introduction-1500ms"));
      AuditAt = FPlatformTime::Seconds() + 1;
      break;
    case 21:
      AuditCapture(TEXT("seat-introduction-2500ms"));
      AuditAt = FPlatformTime::Seconds() + .05;
      break;
    case 22:
      Controller->ServerCancelEntry();
      if (auto* Mode = Controller->GetWorld()->GetAuthGameMode<AWCMatchMode>())
        AuditCheck(TEXT("Cancel introduction leaves no match"), !Mode->bEntryPending && !Mode->Match);
      break;
    case 23: {
      const auto Motion = MakeShared<FJsonObject>();
      Motion->SetStringField(TEXT("method"), TEXT("Settings and clip controls: focused Slate Enter. Actual skeletal single-node position and component yaw sampled across rendered ticks. Hero selection uses the existing view model."));
      AuditReport->SetObjectField(TEXT("reduced_motion_audit"), Motion);
      Select(TEXT("wc_u_human_guardian"));
      AuditCheck(TEXT("Slate opens Settings for motion audit"), AuditKey(Local(TEXT("Settings"), TEXT("Pengaturan"))) && Page == EPage::Settings);
      if (Controller->bReducedMotion)
        AuditCheck(TEXT("Slate prepares unrestricted motion"), AuditKey(ReducedLabel()) && !Controller->bReducedMotion);
      Select(TEXT("wc_u_human_guardian"));
      if (bTurntable) AuditKey(Local(TEXT("Stop rotation"), TEXT("Hentikan rotasi")));
      AuditCheck(TEXT("Slate enables turntable before reduced motion"), AuditKey(Local(TEXT("Turntable"), TEXT("Putar model"))) && bTurntable);
      const auto* Mesh = Preview();
      Motion->SetNumberField(TEXT("rotation_started_yaw"), Mesh ? Mesh->GetRelativeRotation().Yaw : 0);
      Motion->SetNumberField(TEXT("rotation_started_at"), FPlatformTime::Seconds());
      AuditAt = FPlatformTime::Seconds() + .5;
      AuditFrameAt = GFrameCounter + 3;
      break;
    }
    case 24: {
      const auto Motion = AuditReport->GetObjectField(TEXT("reduced_motion_audit"));
      const auto* Mesh = Preview();
      const double Delta = Mesh ? FMath::Abs(FMath::FindDeltaAngleDegrees(float(Motion->GetNumberField(TEXT("rotation_started_yaw"))), Mesh->GetRelativeRotation().Yaw)) : 0;
      AuditCheck(TEXT("Enabled turntable actually rotates"), Mesh && Delta > .1,
          FString::Printf(TEXT("yaw_delta_degrees=%.6f elapsed_seconds=%.3f"), Delta, FPlatformTime::Seconds() - Motion->GetNumberField(TEXT("rotation_started_at"))));
      AuditCheck(TEXT("Slate enables reduced motion in Settings"), AuditKey(Local(TEXT("Settings"), TEXT("Pengaturan"))) &&
          Page == EPage::Settings && AuditKey(ReducedLabel()) && Controller->bReducedMotion && !bTurntable);
      Select(TEXT("wc_u_human_guardian"));
      const auto Rotation = Buttons.FindRef(Local(TEXT("Rotation off"), TEXT("Rotasi mati"))).Pin();
      AuditCheck(TEXT("Reduced turntable control disabled"), Rotation && !Rotation->IsEnabled() &&
          !AuditKey(Local(TEXT("Rotation off"), TEXT("Rotasi mati"))) && !bTurntable);
      AuditAt = FPlatformTime::Seconds() + .03;
      break;
    }
    case 39:
      AuditCheck(TEXT("Slate disables reduced motion in Settings"), AuditKey(Local(TEXT("Settings"), TEXT("Pengaturan"))) &&
          Page == EPage::Settings && AuditKey(ReducedLabel()) && !Controller->bReducedMotion && !bTurntable);
      Select(TEXT("wc_u_human_guardian"));
      AuditAt = FPlatformTime::Seconds() + .03;
      break;
    case 54: {
      const auto* Mesh = Preview();
      const auto Motion = AuditReport->GetObjectField(TEXT("reduced_motion_audit"));
      Motion->SetNumberField(TEXT("rotation_stopped_yaw"), Mesh ? Mesh->GetRelativeRotation().Yaw : 0);
      Motion->SetNumberField(TEXT("rotation_stopped_at"), FPlatformTime::Seconds());
      AuditAt = FPlatformTime::Seconds() + .5;
      AuditFrameAt = GFrameCounter + 3;
      break;
    }
    case 55: {
      const auto* Mesh = Preview();
      const auto Motion = AuditReport->GetObjectField(TEXT("reduced_motion_audit"));
      const double Delta = Mesh ? FMath::Abs(FMath::FindDeltaAngleDegrees(float(Motion->GetNumberField(TEXT("rotation_stopped_yaw"))), Mesh->GetRelativeRotation().Yaw)) : 360;
      AuditCheck(TEXT("Turntable remains off after motion is restored"), Mesh && !bTurntable && Delta < .001,
          FString::Printf(TEXT("yaw_delta_degrees=%.6f elapsed_seconds=%.3f"), Delta, FPlatformTime::Seconds() - Motion->GetNumberField(TEXT("rotation_stopped_at"))));
      const bool Original = AuditReport->GetBoolField(TEXT("original_reduced_motion"));
      const bool Opened = AuditKey(Local(TEXT("Settings"), TEXT("Pengaturan"))) && Page == EPage::Settings;
      const bool Restored = Controller->bReducedMotion == Original || (Opened && AuditKey(ReducedLabel()) && Controller->bReducedMotion == Original);
      AuditCheck(TEXT("Original reduced-motion preference restored through Slate"), Opened && Restored);
      Motion->SetBoolField(TEXT("original_preference_restored"), Restored);
      AuditAt = FPlatformTime::Seconds() + .03;
      break;
    }
    case 56:
      AuditCheck(TEXT("Slate opens gallery for retention check"), AuditKey(Local(TEXT("Heroes"), TEXT("Hero"))) && Page == EPage::Gallery);
      break;
    case 57:
      if (GalleryScroll) GalleryScroll->SetScrollOffset(180);
      AuditAt = FPlatformTime::Seconds() + .2;
      break;
    case 58:
      AuditReport->SetNumberField(TEXT("retained_scroll_expected"), GalleryScroll ? GalleryScroll->GetScrollOffset() : -1);
      Select(TEXT("wc_u_human_guardian"));
      break;
    case 59:
      AuditCheck(TEXT("Slate Back returns detail to gallery"), AuditKey(Local(TEXT("Back"), TEXT("Kembali"))) && Page == EPage::Gallery);
      AuditAt = FPlatformTime::Seconds() + .2;
      break;
    case 60:
      AuditCheck(TEXT("Actual gallery offset and selected hero survive detail/back"), GalleryScroll &&
          AuditReport->GetNumberField(TEXT("retained_scroll_expected")) > 0 &&
          FMath::IsNearlyEqual(double(GalleryScroll->GetScrollOffset()), AuditReport->GetNumberField(TEXT("retained_scroll_expected")), .5) && SelectedId == TEXT("wc_u_human_guardian"));
      break;
    default:
      FinishAudit();
      break;
  }
}

void FWCFrontEnd::FinishAudit() {
  const bool OriginalMotion = AuditReport->GetBoolField(TEXT("original_reduced_motion"));
  if (Controller->bReducedMotion != OriginalMotion) {
    AuditCheck(TEXT("Original motion preference needed fallback restoration"), false,
        TEXT("Slate restoration did not complete; restoring the saved option directly to avoid leaving audit changes."));
    Controller->bReducedMotion = OriginalMotion;
    Controller->SaveOptions();
  }
  int Failures = 0;
  for (const auto& Check : AuditReport->GetArrayField(TEXT("checks")))
    if (!Check->AsObject()->GetBoolField(TEXT("pass"))) ++Failures;
  for (const auto& Shot : AuditReport->GetArrayField(TEXT("screenshots"))) {
    const bool Exists = IFileManager::Get().FileSize(*Shot->AsObject()->GetStringField(TEXT("path"))) > 0;
    Shot->AsObject()->SetBoolField(TEXT("file_written"), Exists);
    if (!Exists) ++Failures;
  }
  AuditReport->SetNumberField(TEXT("failed_checks_or_captures"), Failures);
  AuditReport->SetNumberField(TEXT("checks_executed"), AuditReport->GetArrayField(TEXT("checks")).Num());
  AuditReport->SetStringField(TEXT("status"), Failures ? TEXT("FAIL") : TEXT("PASS"));
  AuditReport->SetStringField(TEXT("ended_utc"), FDateTime::UtcNow().ToIso8601());
  FString Json;
  FJsonSerializer::Serialize(AuditReport.ToSharedRef(), TJsonWriterFactory<>::Create(&Json));
  const FString Path = AuditDirectory / (AuditPrefix + TEXT("-frontend-audit.json"));
  const bool Written = FFileHelper::SaveStringToFile(Json, *Path, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
  UE_LOG(LogTemp, Display, TEXT("WC_FRONTEND_AUDIT_DONE checks=%d failed=%d written=%d path=%s"),
         AuditReport->GetArrayField(TEXT("checks")).Num(), Failures, Written, *Path);
  bAuditFinished = true;
  bAudit = false;
  SelectedId = AuditOriginalHero; Star = 1;
  if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
  Page = EPage::Lobby; Filters.Reset(); Search.Reset(); DetailTab = TEXT("Skill"); Rebuild();
  if (FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndAuditExit")))
    FPlatformMisc::RequestExitWithStatus(false, !Written ? 2 : Failures ? 1 : 0);
}

namespace {
int CountVisibleText(const TSharedRef<SWidget>& Widget, const FString& Text) {
  if (!Widget->GetVisibility().IsVisible()) return 0;
  int Count = 0;
  if (Widget->GetType() == FName(TEXT("STextBlock")) &&
      StaticCastSharedRef<STextBlock>(Widget)->GetText().ToString().Contains(Text)) ++Count;
  FChildren* Children = Widget->GetChildren();
  for (int Index = 0; Index < Children->Num(); ++Index) Count += CountVisibleText(Children->GetChildAt(Index), Text);
  return Count;
}
struct FWCInteractionTrial {
  TSharedPtr<FJsonObject> Report;
  FString Directory, Name;
  int Stage = 0, Failures = 0;
  double Started = FPlatformTime::Seconds();
  uint64 FinishFrame = 0;
  bool Finished = false;
  int64 Unit = 0, Reply = 0, Revision = 0;
  int Gold = 0, Cost = 0;
  TArray<TSharedPtr<FJsonValue>> PresentationSamples;
  FString SettlingStage;
  double StableSince = 0;
  int StableFrames = 0;
  void Begin(const TCHAR* Label, AWCMatchController* Player) {
    Name = Label;
    if (!FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory))
      Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence") / FDateTime::UtcNow().ToString(TEXT("%Y%m%dT%H%M%S"));
    IFileManager::Get().MakeDirectory(*Directory, true);
    Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("status"), TEXT("RUNNING"));
    Report->SetStringField(TEXT("started_utc"), FDateTime::UtcNow().ToIso8601());
    Report->SetStringField(TEXT("method"), TEXT("Opt-in actual native HUD/Slate controls, real server command authority or Unreal network failure callback. Software-driven fixture; no physical human play or two-machine LAN claim."));
    Report->SetStringField(TEXT("content_digest"), UTF8_TO_TCHAR(Player->Presenter->Definitions.contentDigest.c_str()));
    Report->SetArrayField(TEXT("checks"), {});
    Report->SetArrayField(TEXT("screenshots"), {});
    Save();
  }
  void Save() {
    Report->SetArrayField(TEXT("presentation_samples"), PresentationSamples);
    FString Json;
    FJsonSerializer::Serialize(Report.ToSharedRef(), TJsonWriterFactory<>::Create(&Json));
    if (!FFileHelper::SaveStringToFile(Json, *(Directory / (Name + TEXT(".json"))), FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)) {
      UE_LOG(LogTemp, Error, TEXT("WC_UI_TRIAL_WRITE_FAILED %s"), *Directory); ++Failures;
    }
  }
  void Check(const FString& NameValue, bool Passed, const FString& Detail = FString()) {
    auto Checks = Report->GetArrayField(TEXT("checks"));
    auto Check = MakeShared<FJsonObject>();
    Check->SetStringField(TEXT("name"), NameValue); Check->SetBoolField(TEXT("pass"), Passed);
    Check->SetStringField(TEXT("detail"), Detail); Checks.Add(MakeShared<FJsonValueObject>(Check));
    Report->SetArrayField(TEXT("checks"), Checks); if (!Passed) ++Failures;
    UE_LOG(LogTemp, Display, TEXT("WC_UI_TRIAL_CHECK %s %s %s"), Passed ? TEXT("PASS") : TEXT("FAIL"), *NameValue, *Detail);
    Save();
  }
  void Capture(const TCHAR* Label) {
    const FString Path = Directory / (Name + TEXT("-") + Label + TEXT(".png"));
    FScreenshotRequest::RequestScreenshot(Path, true, false);
    auto Shots = Report->GetArrayField(TEXT("screenshots")); Shots.Add(MakeShared<FJsonValueString>(Path));
    Report->SetArrayField(TEXT("screenshots"), Shots);
  }
  bool PreviewSettled(const TCHAR* Label, AWCMatchController* Player, AWCFrontEndScene* Preview) {
    if (SettlingStage != Label) { SettlingStage = Label; StableSince = 0; StableFrames = 0; }
    const bool CameraMatches = Preview && Player->GetViewTarget() == Preview;
    int AssetsRemaining = 0, ShaderJobs = 0;
    bool ShaderCompiling = false;
#if WITH_EDITOR
    AssetsRemaining = FAssetCompilingManager::Get().GetNumRemainingAssets();
    if (GShaderCompilingManager) {
      ShaderJobs = GShaderCompilingManager->GetNumRemainingJobs();
      ShaderCompiling = GShaderCompilingManager->IsCompiling();
    }
#endif
    const int Streaming = IStreamingManager::Get().GetNumWantingResources();
    const bool Ready = CameraMatches && AssetsRemaining == 0 && !ShaderCompiling && Streaming == 0;
    if (Ready) {
      if (!StableFrames) StableSince = FPlatformTime::Seconds();
      ++StableFrames;
    } else { StableFrames = 0; StableSince = 0; }
    auto Sample = MakeShared<FJsonObject>();
    Sample->SetStringField(TEXT("stage"), SettlingStage);
    Sample->SetNumberField(TEXT("frame"), double(GFrameCounter));
    Sample->SetNumberField(TEXT("wall_seconds"), FPlatformTime::Seconds() - Started);
    Sample->SetStringField(TEXT("actual_view_target"), GetPathNameSafe(Player->GetViewTarget()));
    Sample->SetStringField(TEXT("expected_scene"), GetPathNameSafe(Preview));
    Sample->SetBoolField(TEXT("view_target_is_scene"), CameraMatches);
    Sample->SetBoolField(TEXT("automatic_camera_management"), Player->bAutoManageActiveCameraTarget);
    Sample->SetBoolField(TEXT("editor_compilation_counters_available"), WITH_EDITOR != 0);
    Sample->SetNumberField(TEXT("assets_compiling"), AssetsRemaining);
    Sample->SetNumberField(TEXT("shader_jobs_remaining"), ShaderJobs);
    Sample->SetBoolField(TEXT("shader_compiling"), ShaderCompiling);
    Sample->SetNumberField(TEXT("streaming_resources_pending"), Streaming);
    Sample->SetNumberField(TEXT("stable_frames"), StableFrames);
    PresentationSamples.Add(MakeShared<FJsonValueObject>(Sample));
    if (PresentationSamples.Num() % 60 == 0) Save();
    return Ready && StableFrames >= 12 && FPlatformTime::Seconds() - StableSince >= .5;
  }
  void CheckPreview(const TCHAR* Label, AWCMatchController* Player, AWCFrontEndScene* Preview) {
    auto* Hero = Preview ? Preview->FindComponentByClass<USkeletalMeshComponent>() : nullptr;
    const bool Ready = Preview && Player->GetViewTarget() == Preview && Preview->bApproachImported &&
                       Hero && Hero->GetSkeletalMeshAsset() && Hero->GetSingleNodeInstance() && Hero->GetSingleNodeInstance()->GetCurrentAsset();
    Check(Label, Ready, FString::Printf(TEXT("view=%s scene=%s stable_frames=%d auto_camera=%d approach=%d mesh=%s"),
      *GetPathNameSafe(Player->GetViewTarget()), *GetPathNameSafe(Preview), StableFrames, Player->bAutoManageActiveCameraTarget,
      Preview && Preview->bApproachImported, *GetPathNameSafe(Hero ? Hero->GetSkeletalMeshAsset() : nullptr)));
  }
  void Finish() {
    if (!FinishFrame) { FinishFrame = GFrameCounter + 4; return; }
    if (GFrameCounter < FinishFrame || Finished) return;
    for (const auto& Shot : Report->GetArrayField(TEXT("screenshots")))
      if (IFileManager::Get().FileSize(*Shot->AsString()) <= 0) ++Failures;
    Report->SetStringField(TEXT("status"), Failures ? TEXT("FAIL") : TEXT("PASS"));
    Report->SetNumberField(TEXT("failed_checks_or_captures"), Failures);
    Report->SetStringField(TEXT("ended_utc"), FDateTime::UtcNow().ToIso8601());
    Report->SetNumberField(TEXT("elapsed_seconds"), FPlatformTime::Seconds() - Started);
    Save(); Finished = true;
    FPlatformMisc::RequestExitWithStatus(false, Failures ? 1 : 0);
  }
};
}

void FWCFrontEnd::TickRecoveryAudit() {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndRecoveryAudit")) || !Controller.IsValid() || !Root) return;
  auto* Session = Controller->GetGameInstance<UWCNetworkSession>();
  if (!Session) return;
  static TMap<TWeakObjectPtr<UWCNetworkSession>, FWCInteractionTrial> Trials;
  auto& Trial = Trials.FindOrAdd(TWeakObjectPtr<UWCNetworkSession>(Session));
  if (!Trial.Report) Trial.Begin(TEXT("network-recovery-audit"), Controller.Get());
  if (Trial.Finished) return;
  if (Trial.Stage == 7) { Trial.Finish(); return; }
  if (FPlatformTime::Seconds() - Trial.Started > 100) {
    Trial.Check(TEXT("Bounded recovery completed"), false, TEXT("Actual callback/connection/title transition did not complete within 100 seconds."));
    Trial.Stage = 7; Trial.FinishFrame = 0; Trial.Finish(); return;
  }
  if (Trial.Stage == 0) {
    if (!Session->bMatchAborted || Session->LastNetworkError.IsEmpty()) return;
    Trial.Check(TEXT("Real network failure is visible in native Mode"), Page == EPage::Mode && NetworkError == Session->LastNetworkError && !bPending && !IsEntry(), Session->LastNetworkError + TEXT(" | ") + Session->LastNetworkDetail);
    const auto Join = Buttons.FindRef(Local(TEXT("Join LAN"), TEXT("Gabung LAN"))).Pin();
    Trial.Check(TEXT("Join retry is enabled after real failure"), Join && Join->IsEnabled());
    Trial.Report->SetStringField(TEXT("failed_endpoint"), Session->LastJoinAddress);
    Trial.Stage = 1; return;
  }
  if (Trial.Stage == 1) {
    if (!Trial.PreviewSettled(TEXT("failed_connection"), Controller.Get(), Scene.Get())) return;
    Trial.CheckPreview(TEXT("Original scene restored after failed connection"), Controller.Get(), Scene.Get());
    Trial.Capture(TEXT("failed-connection")); Trial.Stage = 2; Trial.FinishFrame = GFrameCounter + 4; return;
  }
  if (Trial.Stage == 2) {
    if (GFrameCounter < Trial.FinishFrame) return;
    FString Target, Address;
    FParse::Value(FCommandLine::Get(), TEXT("WCRecoveryTarget="), Target);
    if (!UWCNetworkSession::NormalizeJoinAddress(Target, Address)) {
      Trial.Check(TEXT("A valid actual retry host was supplied"), false, Target);
      Trial.Stage = 7; Trial.FinishFrame = 0; return;
    }
    Controller->JoinAddress = Address;
    Trial.Report->SetStringField(TEXT("retry_endpoint"), Address);
    Rebuild(); Trial.Stage = 3; Trial.FinishFrame = 0;
    Trial.Check(TEXT("Slate Join retries the declared endpoint"), AuditKey(Local(TEXT("Join LAN"), TEXT("Gabung LAN"))));
    return;
  }
  if (Trial.Stage == 3) {
    if (Session->bMatchAborted) return;
    if (!Controller->Public->GetBoolField(TEXT("network")) || Controller->Public->GetNumberField(TEXT("connected")) != 2 || Controller->AssignedSeat != 1) return;
    Trial.Check(TEXT("Retry connected to a real two-controller host"), true,
                FString::Printf(TEXT("assigned_seat=%d protocol=%g digest=%s"), Controller->AssignedSeat,
                  Controller->Public->GetNumberField(TEXT("protocolVersion")), *Controller->Public->GetStringField(TEXT("contentDigest"))));
    Trial.Check(TEXT("Retry catalog and protocol agree"), Controller->Public->GetNumberField(TEXT("protocolVersion")) == wc::NetworkProtocolVersion &&
                Controller->Public->GetStringField(TEXT("contentDigest")) == UTF8_TO_TCHAR(Controller->Presenter->Definitions.contentDigest.c_str()));
    Page = EPage::Mode; Rebuild(); Trial.Stage = 4; return;
  }
  if (Trial.Stage == 4) {
    if (!Trial.PreviewSettled(TEXT("connected_lobby"), Controller.Get(), Scene.Get())) return;
    Trial.CheckPreview(TEXT("Original scene restored after actual LAN retry"), Controller.Get(), Scene.Get());
    Trial.Check(TEXT("Idle connected captains display waiting for start"), !IsEntry() &&
        CountVisibleText(Root.ToSharedRef(), Local(TEXT("Waiting for start"), TEXT("Menunggu mulai"))) == 2 &&
        CountVisibleText(Root.ToSharedRef(), Local(TEXT("Open LAN seat"), TEXT("Kursi LAN terbuka"))) == 0);
    Trial.Capture(TEXT("connected-lobby")); Trial.Stage = 5; Trial.FinishFrame = GFrameCounter + 4; return;
  }
  if (Trial.Stage == 5) {
    if (GFrameCounter < Trial.FinishFrame) return;
    Trial.Stage = 6; Trial.FinishFrame = 0;
    Trial.Check(TEXT("Slate leaves the actual LAN lobby"), AuditKey(Local(TEXT("Leave LAN lobby"), TEXT("Tinggalkan lobi LAN"))));
    return;
  }
  if (Trial.Stage == 6) {
    if (Controller->Public->GetBoolField(TEXT("network"))) return;
    if (!Trial.PreviewSettled(TEXT("returned_title"), Controller.Get(), Scene.Get())) return;
    Trial.Check(TEXT("Return to local title has no running tournament"), Controller->Public->GetNumberField(TEXT("phase")) < 0 && !Session->bMatchAborted);
    Trial.CheckPreview(TEXT("Original scene restored on return to title"), Controller.Get(), Scene.Get());
    Trial.Capture(TEXT("returned-title")); Trial.Stage = 7; Trial.FinishFrame = 0;
  }
}

void WCTickSelectionAudit(AWCMatchController* Player) {
  if (!FParse::Param(FCommandLine::Get(), TEXT("WCSelectionAudit")) || !Player || !Player->Presenter || !Player->Public.IsValid() || !Player->Private.IsValid()) return;
  static TMap<TWeakObjectPtr<AWCMatchController>, FWCInteractionTrial> Trials;
  auto& Trial = Trials.FindOrAdd(TWeakObjectPtr<AWCMatchController>(Player));
  if (!Trial.Report) Trial.Begin(TEXT("selection-rejection-audit"), Player);
  if (Trial.Finished) return;
  if (Trial.Stage == 9) { Trial.Finish(); return; }
  if (FPlatformTime::Seconds() - Trial.Started > 35) {
    Trial.Check(TEXT("Bounded selection scenario completed"), false, TEXT("Actual first-preparation action/reply did not complete within 35 seconds.")); Trial.Stage = 9; Trial.Finish(); return;
  }
  if (Player->Public->GetNumberField(TEXT("phase")) != 0 || !Player->Private->HasField(TEXT("units"))) return;
  auto* HUD = Cast<AWCMatchHUD>(Player->GetHUD()); if (!HUD) return;
  const auto& Units = Player->Private->GetArrayField(TEXT("units"));
  TSharedPtr<FJsonObject> Owned;
  for (const auto& Value : Units) if (int64(Value->AsObject()->GetNumberField(TEXT("id"))) == Trial.Unit) Owned = Value->AsObject();
  const FString ReplyDetail = FString::Printf(TEXT("request=%lld accepted=%d selected=%lld revision=%g sequence=%g gold=%g reason=%s"),
    Player->LastRepliedRequest, Player->bLastReplyAccepted, Player->SelectedUnit,
    Player->Private->GetNumberField(TEXT("revision")), Player->Private->GetNumberField(TEXT("sequence")),
    Player->Private->GetNumberField(TEXT("gold")), *Player->Message);
  if (Trial.Stage == 0) {
    const auto& Shop = Player->Private->GetArrayField(TEXT("shop"));
    for (int Slot = 0; Slot < Shop.Num(); ++Slot) {
      const int Def = int(Shop[Slot]->AsNumber());
      if (Def >= 0 && Player->Presenter->Definitions.units[Def].cost <= Player->Private->GetNumberField(TEXT("gold"))) {
        Trial.Reply = Player->LastRepliedRequest; Trial.Stage = 1;
        HUD->NotifyHitBoxClick(FName(*(TEXT("buy_") + FString::FromInt(Slot)))); return;
      }
    }
  } else if (Trial.Stage == 1) {
    if (Player->LastRepliedRequest <= Trial.Reply || !Player->bLastReplyAccepted || Units.Num() != 1) return;
    Owned = Units[0]->AsObject(); Trial.Unit = int64(Owned->GetNumberField(TEXT("id")));
    Trial.Cost = Player->Presenter->Definitions.units[int(Owned->GetNumberField(TEXT("def")))].cost;
    Trial.Check(TEXT("HUD purchase produced an authoritative owned copy"), true, ReplyDetail);
    HUD->NotifyHitBoxClick(FName(*(TEXT("bench_") + FString::FromInt(int(Owned->GetNumberField(TEXT("bench")))))));
    Trial.Check(TEXT("HUD selects the real owned bench copy"), Player->SelectedUnit == Trial.Unit);
    Trial.Gold = int(Player->Private->GetNumberField(TEXT("gold")));
    Trial.Revision = int64(Player->Private->GetNumberField(TEXT("revision")));
    Trial.Reply = Player->LastRepliedRequest; Trial.Stage = 2;
    HUD->NotifyHitBoxClick(FName(TEXT("cell_-1_0")));
  } else if (Trial.Stage == 2) {
    if (Player->LastRepliedRequest <= Trial.Reply) return;
    Trial.Check(TEXT("Actual invalid move preserves useful selection and owner state"), !Player->bLastReplyAccepted &&
      Player->Message == TEXT("Destination is outside own deployment") && Player->SelectedUnit == Trial.Unit && Owned && !Owned->GetBoolField(TEXT("board")) &&
      Player->Private->GetNumberField(TEXT("gold")) == Trial.Gold && Player->Private->GetNumberField(TEXT("revision")) == Trial.Revision, ReplyDetail);
    Trial.Capture(TEXT("rejected-move")); Trial.Stage = 3; Trial.FinishFrame = GFrameCounter + 4;
  } else if (Trial.Stage == 3) {
    if (GFrameCounter < Trial.FinishFrame) return;
    Trial.Reply = Player->LastRepliedRequest; Trial.Stage = 4; Trial.FinishFrame = 0;
    HUD->NotifyHitBoxClick(FName(TEXT("cell_0_0")));
  } else if (Trial.Stage == 4) {
    if (Player->LastRepliedRequest <= Trial.Reply || !Owned || !Owned->GetBoolField(TEXT("board"))) return;
    Trial.Check(TEXT("Matching accepted move clears selection after actual placement"), Player->bLastReplyAccepted && Player->SelectedUnit == 0 &&
      Owned->GetNumberField(TEXT("col")) == 0 && Owned->GetNumberField(TEXT("row")) == 0, ReplyDetail);
    HUD->NotifyHitBoxClick(FName(*(TEXT("unit_") + FString::Printf(TEXT("%lld"), Trial.Unit))));
    Trial.Reply = Player->LastRepliedRequest; Trial.Stage = 5;
    Player->Intent(wc::CommandType::Sell, 0);
  } else if (Trial.Stage == 5) {
    if (Player->LastRepliedRequest <= Trial.Reply) return;
    Trial.Check(TEXT("Actual unowned sale rejection retains the useful owned selection"), !Player->bLastReplyAccepted &&
      Player->Message == TEXT("Unit is not owned") && Player->SelectedUnit == Trial.Unit && Owned &&
      Player->Private->GetNumberField(TEXT("gold")) == Trial.Gold, ReplyDetail);
    Trial.Capture(TEXT("rejected-sale")); Trial.Stage = 6; Trial.FinishFrame = GFrameCounter + 4;
  } else if (Trial.Stage == 6) {
    if (GFrameCounter < Trial.FinishFrame) return;
    Trial.Reply = Player->LastRepliedRequest; Trial.Stage = 7; Trial.FinishFrame = 0;
    HUD->NotifyHitBoxClick(FName(TEXT("sell")));
  } else if (Trial.Stage == 7) {
    if (Player->LastRepliedRequest <= Trial.Reply || Owned) return;
    Trial.Check(TEXT("Matching accepted sale clears selection and pays canonical copy value"), Player->bLastReplyAccepted && Player->SelectedUnit == 0 &&
      Player->Private->GetNumberField(TEXT("gold")) == Trial.Gold + Trial.Cost, ReplyDetail);
    Trial.Capture(TEXT("accepted-sale")); Trial.Stage = 9; Trial.FinishFrame = 0;
  }
}
