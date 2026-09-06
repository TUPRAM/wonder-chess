#include "WCFrontEnd.h"
#include "WCFrontEndScene.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "Animation/AnimSequence.h"
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
    if (!Clip.IsEmpty()) Scene->PlayClip(Clip, false);
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
    default:
      FinishAudit();
      break;
  }
}

void FWCFrontEnd::FinishAudit() {
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
