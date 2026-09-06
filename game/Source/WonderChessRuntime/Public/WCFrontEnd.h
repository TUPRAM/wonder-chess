#pragma once

#include "CoreMinimal.h"
#include "UObject/GCObject.h"

class AWCMatchController;
class AWCFrontEndScene;
class SWidget;
class SVerticalBox;
class SScrollBox;
class SBorder;
class FJsonObject;
struct FSlateBrush;

// Native Slate front end backed by the same immutable catalog as combat.
class WONDERCHESSRUNTIME_API FWCFrontEnd : public FGCObject {
public:
  ~FWCFrontEnd();
  bool Update(AWCMatchController* Player, TFunction<void(const FString&)> OnAction);
  bool Back();
  void Remove();
  virtual void AddReferencedObjects(FReferenceCollector& Collector) override;
  virtual FString GetReferencerName() const override { return TEXT("WonderChessFrontEnd"); }

private:
  enum class EPage { Lobby, Mode, Gallery, Detail, Settings };
  EPage Page = EPage::Lobby;
  TWeakObjectPtr<AWCMatchController> Controller;
  TWeakObjectPtr<AWCFrontEndScene> Scene;
  TSharedPtr<SWidget> Root;
  TSharedPtr<SBorder> Body;
  TSharedPtr<SVerticalBox> Grid;
  TSharedPtr<SScrollBox> GalleryScroll;
  TFunction<void(const FString&)> Action;
  TArray<TObjectPtr<UObject>> Assets;
  TMap<FString, TSharedPtr<FSlateBrush>> Portraits;
  TMap<FString, TWeakPtr<SWidget>> Buttons;
  TMap<FString, TSet<FString>> Filters;
  TArray<int32> Results;
  FString Search, SelectedId, Sort = TEXT("Cost"), DetailTab = TEXT("Skill"), EntryState, PreviousLanguage, PendingAction, ParticipantSignature;
  int32 Star = 1, Columns = 6, PreviousConnected = -1;
  float ScrollOffset = 0;
  double PendingAt = 0;
  bool bPending = false, bShowcase = false, bTurntable = false;
  bool bAdvanced = false;
  bool bAuditInitialized = false, bAudit = false, bAuditFinished = false;
  int32 AuditStage = 0;
  int32 AuditRosterStage = 0;
  uint64 AuditFrameAt = 0;
  double AuditAt = 0;
  double AuditEntryDeadline = 0, AuditIntroObservedAt = 0;
  FString AuditDirectory, AuditPrefix, AuditOriginalHero;
  TSharedPtr<FJsonObject> AuditReport;

  void Rebuild();
  void RefreshResults();
  void RefreshGrid();
  void OpenHero(int32 Index);
  void ShiftHero(int32 Delta);
  void SetPage(EPage Value);
  void Dispatch(const FString& Id);
  void SaveShowcase();
  int32 SelectedIndex() const;
  bool IsEntry() const;
  TSharedRef<SWidget> Lobby();
  TSharedRef<SWidget> Mode();
  TSharedRef<SWidget> Gallery();
  TSharedRef<SWidget> Detail();
  TSharedRef<SWidget> Settings();
  TSharedRef<SWidget> Header();
  TSharedRef<SWidget> Card(int32 Index, float Width);
  TSharedRef<SWidget> DetailBody();
  TSharedRef<SWidget> PreviewControls();
  TSharedRef<SWidget> Button(const FString& Label, TFunction<void()> Handler, bool Enabled = true, bool Accent = false);
  TSharedRef<SWidget> Copy(const FString& Value, int32 Size = 18, bool Gold = false);
  const FSlateBrush* Portrait(const FString& UnitId);
  FString Local(const TCHAR* English, const TCHAR* Indonesian) const;
  void InitializeAudit();
  void TickAudit();
  bool AuditKey(const FString& ButtonLabel);
  void AuditCheck(const FString& Name, bool Pass, const FString& Detail = FString());
  void AuditCatalog();
  void AuditCapture(const FString& Name);
  void FinishAudit();
};
