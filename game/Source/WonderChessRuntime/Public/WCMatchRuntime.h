#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "Simulation/WonderSimulation.h"
#include "WCMatchRuntime.generated.h"

class AWCBoardPresenter;
class FWCFrontEnd;
class UAudioComponent;
class USoundConcurrency;

UCLASS()
class WONDERCHESSRUNTIME_API AWCMatchState : public AGameStateBase {
  GENERATED_BODY()
public:
  UPROPERTY(Replicated) FString PublicJson;
  virtual void
  GetLifetimeReplicatedProps(TArray<FLifetimeProperty> &Out) const override;
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCMatchController : public APlayerController {
  GENERATED_BODY()
public:
  AWCMatchController();
  virtual void BeginPlay() override;
  virtual void Tick(float Delta) override;
  virtual void SetupInputComponent() override;
  UFUNCTION(Server, Reliable)
  void ServerIntent(int32 Type, int64 Request, int64 Sequence, int64 Revision,
                    int64 Unit, int32 Slot, bool ToBoard, int32 Column,
                    int32 Row);
  UFUNCTION(Server, Reliable) void ServerStart(int32 Humans, int32 Seed);
  UFUNCTION(Server, Reliable) void ServerPractice();
  UFUNCTION(Server, Reliable) void ServerCatalogReady(const FString& Schema, const FString& Digest, int32 Protocol);
  UFUNCTION(Server, Reliable) void ServerEntryReady(bool bSkip);
  UFUNCTION(Server, Reliable) void ServerCancelEntry();
  bool bCatalogReady = false, bEntryReady = false, bEntrySkip = false;
  UFUNCTION(Client, Reliable) void ClientPrivateState(const FString &Json);
  UFUNCTION(Client, Reliable)
  void ClientReply(bool Accepted, const FString &Reason, int64 Request = 0);
  UFUNCTION(Client, Reliable) void ClientRejectSession(const FString &Reason);
  void Intent(wc::CommandType Type, int64 Unit = 0, int32 Slot = -1,
              bool ToBoard = false, int32 Column = -1, int32 Row = -1);
  void Sound(const FString &Name);
  void Cancel();
  void Ready();
  void NextFocus();
  void UseFocus();
  void LowerFocusedVolume();
  void RaiseFocusedVolume();
  void CaptureScreenshot();
  void RefreshView();
  int32 AssignedSeat = -1;
  int32 ObservedSeat = 0;
  int64 SelectedUnit = 0;
  int32 InspectedDefinition = -1;
  int64 InspectedUnitId = 0;
  bool bInspectedCombat = false;
  bool bRecap = false;
  bool bOptions = false, bTutorial = false, bReducedMotion = false;
  FString Language = TEXT("en"), Message, PrivateJson, LastPublicJson;
  int64 LastRepliedRequest = 0;
  bool bLastReplyAccepted = false;
  FString JoinAddress = TEXT("127.0.0.1");
  float MasterVolume = .6f, MusicVolume = .25f, EffectsVolume = .6f;
  double MessageTime = 0;
  TSharedPtr<FJsonObject> Private, Public;
  UPROPERTY() TObjectPtr<AWCBoardPresenter> Presenter;
  UPROPERTY() TObjectPtr<UAudioComponent> Music;
  UPROPERTY() TObjectPtr<USoundConcurrency> EffectsConcurrency;
  void SaveOptions();

private:
  struct QueuedIntent {
    wc::CommandType Type;
    int64 Unit;
    int32 Slot;
    bool ToBoard;
    int32 Column, Row;
    int32 ExpectedDefinition = -1;
  };
  TArray<QueuedIntent> IntentQueue;
  bool bCommandPending = false;
  bool bPendingAccepted = false;
  bool bSentCatalogReady = false;
  int64 PendingSequence = 0, PendingRevision = 0, PendingRequest = 0, PendingUnit = 0;
  wc::CommandType PendingType = wc::CommandType::Ready;
  void SendNextIntent();
  void CompleteAcknowledgedIntent();
  int64 RequestId = 1;
  double NextMusic = 0;
  TMap<FString, double> LastSoundTimes;
  int32 LastPhase = -1;
  int32 LastCaptainHealth = -1;
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCMatchMode : public AGameModeBase {
  GENERATED_BODY()
public:
  AWCMatchMode();
  virtual void BeginPlay() override;
  virtual void Tick(float Delta) override;
  virtual void PostLogin(APlayerController *Player) override;
  virtual void Logout(AController *Exiting) override;
  void StartTournament(AWCMatchController *Requester, int32 Humans, int32 Seed);
  void RequestEntry(AWCMatchController* Requester, int32 Humans, int32 Seed);
  void CancelEntry(const FString& Reason);
  bool bEntryPending = false;
  FString EntryState;
  int32 EntrySeed = 0;
  double EntryDeadline = 0, IntroductionRemaining = 0;
  void Publish();
  void Regression(int32 Count);
  TUniquePtr<wc::Match> Match;
  wc::Catalog Catalog;
  FString LoadError;
  TArray<TWeakObjectPtr<AWCMatchController>> Controllers;
  int32 RequestedHumans = 1;
  double SnapshotClock = 0;
  double MillisecondCarry = 0;
  int32 Speed = 1;
  int32 LastLoggedRound = 0;
  TSharedPtr<FJsonObject> LastRecap;
  bool bPractice = false;
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCMatchHUD : public AHUD {
  GENERATED_BODY()
public:
  virtual void DrawHUD() override;
  virtual void EndPlay(const EEndPlayReason::Type Reason) override;
  virtual void NotifyHitBoxClick(FName Box) override;
  virtual void NotifyHitBoxRelease(FName Box) override;
  void CycleFocus();
  void ActivateFocus();
  void AdjustFocusedVolume(float Delta);
  bool BackFromFrontEnd();
  const TCHAR* FrontEndPageName() const;
  bool SelectPreviewForReview(const FString& Id, const FString& Clip);

private:
  TSharedPtr<FWCFrontEnd> FrontEnd;
  int32 PreviewOffer = -1;
  FString InspectedTrait;
  bool bPresentationOptionsRead = false;
  FString Focused;
  TArray<FString> Focusable;
  float Scale = 1, OffsetX = 0, OffsetY = 0;
  void Text(const FString &Value, float X, float Y, float Size = 1,
            FLinearColor Color = FLinearColor::White);
  void Box(float X, float Y, float W, float H, FLinearColor Color);
  void Button(const FString &Id, const FString &Label, float X, float Y,
              float W, float H, bool Enabled = true);
  void Wrap(const FString &Value, float X, float Y, float Width, float Size,
            FLinearColor Color);
  FString Label(const FString &Key) const;
  void Action(const FString &Id);
  FString Pressed;
  FVector2D PressLocation;
};

void WCTickSelectionAudit(AWCMatchController* Controller);
