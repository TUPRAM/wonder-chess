#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "WCDefinitionRegistry.h"
#include "Simulation/WonderScenario.h"
#include "Layout/SlateRect.h"
#include <memory>
#include "WCVNextLab.generated.h"

class ACameraActor;
class UMaterialInstanceDynamic;
class UMaterialInterface;
class UStaticMesh;
class UStaticMeshComponent;
class USkeletalMesh;
class USkeletalMeshComponent;
class UInstancedStaticMeshComponent;
class UTextRenderComponent;
class UWCBellbackPresentationComponent;
class UWCHeroPresentationComponent;
class UWCSilkmotherPresentationComponent;
class UWCCragstoatPresentationComponent;
class SWidget;
class STextBlock;
class SWrapBox;

UCLASS()
class WONDERCHESSRUNTIME_API AWCVNextLabMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AWCVNextLabMode();
    virtual void BeginPlay() override;
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCVNextLabController : public APlayerController
{
    GENERATED_BODY()
public:
    AWCVNextLabController();
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCVNextLab : public AActor
{
    GENERATED_BODY()
public:
    AWCVNextLab();
    virtual ~AWCVNextLab() override;
    void Initialize();
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
    struct FPieceView
    {
        TWeakObjectPtr<AActor> Actor;
        UStaticMeshComponent* Health = nullptr;
        UStaticMeshComponent* LabelBacking = nullptr;
        UTextRenderComponent* Label = nullptr;
        int Definition = -1, Side = 0;
        bool Neutral = false;
        // Shown body direction; it turns smoothly toward the piece's step or target during combat.
        float Yaw = 0;
        bool YawSet = false;
        UStaticMeshComponent* Mana = nullptr;
        UStaticMeshComponent* HealthTrack = nullptr;
        UStaticMeshComponent* ManaTrack = nullptr;
        TArray<UStaticMeshComponent*> TierPips;
        UWCBellbackPresentationComponent* Bellback = nullptr;
        UWCSilkmotherPresentationComponent* Silkmother = nullptr;
        UWCCragstoatPresentationComponent* Cragstoat = nullptr;
        USkeletalMeshComponent* CragstoatPreview = nullptr;
        UWCHeroPresentationComponent* Hero = nullptr;
    };
    wc::Catalog Catalog;
    std::unique_ptr<wc::Catalog> StatusTestCatalog;
    bool StatusTest=false,CueExercise=false;
    void StartStatusTest();
    TWeakObjectPtr<AActor> CueActor;
    TArray<UStaticMeshComponent*> CueMeshes;
    TArray<UTextRenderComponent*> CueTexts;
    TSet<FString> CueKindsSeen,CurrentCueKinds;
    int CueMeshUsed=0,CueTextUsed=0,PeakCueMeshes=0,PeakCueTexts=0;
    bool CueOverflow=false;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> SilkStrands;
    UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> SilkSparks;
    TArray<FTransform> SilkStrandTransforms,SilkSparkTransforms;
    void SilkLine(FVector A,FVector B,float Width);
    void SilkSpark(FVector P,float Radius);
    void FlushSilkEffects();
    void UpdateCombatCues();
    void CueMesh(const TCHAR* Shape,FVector Location,FVector Scale,FLinearColor Color,FRotator Rotation=FRotator::ZeroRotator);
    void CueLine(FVector A,FVector B,FLinearColor Color,float Width);
    void CueRing(FVector Center,float Radius,FLinearColor Color,float Width,float Arc=UE_TWO_PI,float Rotation=0);
    void CueText(FVector Location,const FString& Text,FLinearColor Color,float Size);
    void CueStar(FVector Center,float Radius,FLinearColor Color,float Width,float Rotation=0);
    void UpdatePlacementCue();
    int PlacementState(wc::Cell Cell) const;
    bool BellbackCandidate=false, BellbackExercise=false, BellbackPerformance=false;
    // -WCHeroReview: close-up screenshots of the first imported hero model playing each clip.
    bool HeroReview=false;
    // Stone castle courtyard around the board; -WCLegacyBoard keeps the earlier scene.
    bool Courtyard=true;
    void BuildCourtyard(AActor* Ground,class ADirectionalLight* Sun,class ASkyLight* Sky);
    // Press-and-hold on a piece lifts it; the hovered tile and the tiles in its attack range light up.
    bool Dragging=false,DragArmed=false;
    uint64 DragId=0;
    wc::Cell DragOrigin{-1,-1},DragHover{-1,-1};
    FVector DragGround=FVector::ZeroVector;
    double DragPressedAt=0;
    TSet<int> DragCells;
    void TickDrag();
    // The bench is a row of ten real tiles on the player's side of the board, as wide as the board itself;
    // cell row -1 addresses it and the column is the bench slot.
    static constexpr double BenchY=1070;
    static constexpr double BenchPitch=160;
    static constexpr int BenchSlots=10;
    static int BenchSlotAt(double X){return FMath::FloorToInt((X+BenchPitch*BenchSlots/2)/BenchPitch);}
    UStaticMeshComponent* BenchMark=nullptr;
    int BenchHover=-1;
    // One small off-board stage per modelled hero renders its idle animation for shop cards and portraits.
    UPROPERTY() TMap<FString,TObjectPtr<class UTextureRenderTarget2D>> HeroCardTargets;
    TMap<FString,TSharedPtr<FSlateBrush>> HeroCardBrushes;
    TMap<FString,UWCHeroPresentationComponent*> HeroCardHeroes;
    const FSlateBrush* HeroCardBrush(const FString& HeroId);
    // A bench piece has no model on the board, so a temporary one follows the cursor while it is dragged.
    bool DragFromBench=false;
    TWeakObjectPtr<AActor> DragGhost;
    UWCHeroPresentationComponent* DragGhostHero=nullptr;
    void BenchPressed(int Slot);
    void EndDrag();
    int HeroReviewStage=0;
    double HeroReviewAt=0;
    void TickHeroReview();
    bool SilkmotherCandidate=false;
    bool CragstoatCandidate=false,CragstoatExercise=false;
    int CragRouteStage=0,CragFloorSamples=0,CragPeakUnits=0,CragRealFightPeakUnits=0;
    TSet<FString> CragLoadedAssetsSeen;
    bool CragNativePoseValid=true;
    double CragRouteStarted=0,CragLastSurface=0,CragMinimumZ=MAX_dbl;
    double CragAudioStartWall=0,CragAudioStopWall=0;
    FString CragAudioStartUtc,CragAudioStopUtc;
    int CragCorrectedPoseSamples=0;
    float CragMaximumFootCorrection=0;
    FString CragFrameCsv;
    TSet<FName> CragClipsSeen;
    TSet<FString> CragShots;
    bool CragControlMatches=true;
    void TickCragstoatRoute(float DeltaSeconds);
    bool CragstoatPreview=false;
    bool SilkmotherExercise=false;
    int SilkRouteStage=0,SilkFloorSamples=0,SilkPeakUnits=0;
    double SilkRouteStarted=0,SilkLastSurface=0,SilkMinimumZ=MAX_dbl;
    FString SilkFrameCsv;
    TSet<FName> SilkClipsSeen;
    TSet<FString> SilkShots;
    TSet<FName> SilkHitOverlayBases;
    int SilkHitOverlaySamples=0;
    TArray<double> SilkFrameTimes;
    bool SilkControlMatches=true;
    void TickSilkmotherRoute(float DeltaSeconds);
    uint64 BellbackGeneration=0;
    const wc::Combat* BellbackCombat=nullptr;
    int BellbackPreviousTick=-1, BellbackRouteStage=0;
    double BellbackClock=0, BellbackRouteStarted=0, BellbackLastWall=0;
    FString BellbackFrameCsv;
    TSet<FName> BellbackSeenClips;
    TArray<double> BellbackFrameTimes;
    int BellbackPeakUnits=0, BellbackSoundCount=0;
    std::unique_ptr<wc::Combat> BellbackControl;
    FString BellbackControlSignature, BellbackActualSignature;
    int BellbackObservedGuard=0, BellbackObservedDamage=0;
    TSet<FString> BellbackShotsRequested;
    TArray<TSharedPtr<FJsonValue>> BellbackScreenshotRecords;
    TSharedPtr<FJsonObject> BellbackPendingScreenshot;
    FString BellbackScreenshotPath;
    double BellbackScreenshotRequestedAt=0, BellbackCaptureRecoveryUntil=0;
    int BellbackCaptureExcludedFrames=0;
    bool BellbackScreenshotFailure=false;
    TSharedPtr<FJsonObject> BellbackSelectionProbe;
    bool ProbeBellbackSelection();
    bool BellbackAudioRequested=false, BellbackAudioRecording=false, BellbackAudioExportPending=false;
    double BellbackAudioStartedAt=0, BellbackAudioStopRequestedAt=0, BellbackAudioNextPoll=0, BellbackAudioValidSeenAt=0;
    int64 BellbackAudioValidatedBytes=0;
    FString BellbackAudioPath, BellbackAudioFailure, BellbackAudioDeferredRouteFailure;
    TSharedPtr<FJsonObject> BellbackAudioMetadata;
    bool BeginBellbackAudioCapture(FString& Failure);
    bool FinishBellbackAudioCapture(const FString& RouteFailure);
    void PollBellbackAudioCapture(double Now);
    void QueueBellbackScreenshot(const FString& Name,double Age);
    void PollBellbackScreenshot(double Now);
    bool BellbackRouteDone=false;
    void TickBellbackRoute(float DeltaSeconds);
    void FinishBellbackRoute(const FString& Failure=FString());
    bool ArtSlice = false;
    bool Storybook = false;
    TMap<uint64, double> UpgradeStarted;
    void RecordRosterUpgrades(const std::vector<wc::OwnedUnit>& Before);
    void ClearUpgradePresentation();
    float UpgradePulse(uint64 Id) const;
    float DefeatAge(const wc::CombatUnit& Unit) const;
    const wc::Combat* DefeatClockCombat = nullptr;
    int DefeatClockTick = -1;
    double DefeatClockHeldAt = 0;
    int PlacementPreviewState = 0;
    wc::Cell PlacementPreviewCell{-1,-1};

    FWCDefinitionText Metadata;
    std::array<std::vector<wc::OwnedUnit>, 2> Formation, ReplayFormation;
    std::unique_ptr<wc::Combat> Fight, PreparationState;
    std::unique_ptr<wc::Match> SoloMatch;
    TMap<uint64, FPieceView> Pieces;
    TArray<UStaticMeshComponent*> Cells, Telegraphs;
    TSharedPtr<SWidget> Interface, BoardInput;
    TSharedPtr<STextBlock> InspectorBlock, EventBlock, StatusBlock, MessageBlock;
    UPROPERTY() TArray<TObjectPtr<AActor>> SceneActors;
    UPROPERTY() TMap<uint32, TObjectPtr<UMaterialInstanceDynamic>> Materials;
    UPROPERTY() TMap<FString, TObjectPtr<UStaticMesh>> ProxyMeshes;
    UPROPERTY() TObjectPtr<UMaterialInterface> ProxyMaterial;
    UPROPERTY() TObjectPtr<USkeletalMesh> CragstoatPreviewMesh;
    UPROPERTY() TObjectPtr<UMaterialInterface> CragstoatPreviewMaterial;
    UPROPERTY() TObjectPtr<UMaterialInterface> CombatCueMaterial;
    UPROPERTY() TObjectPtr<UMaterialInterface> QuietStoneMaterial;
    UPROPERTY() TObjectPtr<UMaterialInterface> SanctuaryMaterial;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> SanctuaryBackdrop;
    UPROPERTY() TMap<uint32,TObjectPtr<UMaterialInstanceDynamic>> StoneMaterials;
    UPROPERTY() TMap<uint32,TObjectPtr<UMaterialInstanceDynamic>> CueMaterials;
    UPROPERTY() TObjectPtr<ACameraActor> Camera;
    UPROPERTY() TObjectPtr<AWCVNextLabController> Controller;
    FString Message, LoadError, EvidenceDirectory;
    FString SavePath, SoloRecap;
    int ScenarioIndex = -1;
    bool ScenarioAlternative = false, ScenarioMirrored = false;
    FString ScenarioReport;
    FString ScenarioDescription;
    bool SoloMode = false, SoloPaused = false, SoloExercise = false;
    bool SoloVisualExercise = false;
    int SoloVisualOrders = 0;
    std::string SoloVisualSavedState;
    void TickSoloVisualExercise();
    void FinishSoloVisualExercise(const FString& Failure = FString());
    bool AwaitingSaveDecision = false;
    bool ShopOpen = false;
    int ShopDismissedRound = 0;
    // Session-only help preferences. These do not alter catalogue, save or combat state.
    bool SoloGuideOpen = false, SoloGuideWasPaused = false, SoloGuideReturnFocus = false;
    bool SoloBenchReturnFocus = false;
    bool SoloGuideIndonesian = false, CreatureSoundEnabled = true;
    int SoloGuidePage = 0;
    float SoloGuideTextScale = 1.f;
    void OpenSoloGuide();
    void CloseSoloGuide();
    FString SoloGuidePhrase(const TCHAR* English, const TCHAR* Indonesian) const;
    FString SoloGuideTitle() const;
    FString SoloGuideBody() const;
    int ViewedSeat = 0, LastSoloRound = -1, LastSoloRecord = 0, KeyboardColumn = 0, KeyboardRow = 0;
    wc::Phase LastSoloPhase = wc::Phase::Aborted;
    wc::Id LastSoloRevision = ~wc::Id(0);
    TSharedPtr<STextBlock> SoloSummaryBlock;
    int Palette = 0, BrushStar = 1, Seed = 314159, ReplaySeed = 314159;
    wc::Facing BrushFacing = wc::Facing::Forward;
    uint64 Selected = 0, NextId = 1;
    bool Paused = false, Exercise = false, ExerciseDone = false, CombatInvariantFailed = false;
    bool PreparationDirty = true;
    TSet<int> PreparationCells;
    uint64 PreparationRecipient = 0;
    FString PreparationHint;
    double Accumulator = 0, Elapsed = 0;
    int ExerciseStage = 0, FirstEventCount = 0;
    FString FirstSignature;
    TSharedPtr<FJsonObject> ExerciseChecks;
    enum class ECapturePhase { None, Settling, Requested, Processed };
    ECapturePhase CapturePhase = ECapturePhase::None;
    FString CaptureFilename;
    FDateTime CapturePreviousWrite;
    double CaptureQueuedAt = 0, CapturePresentedAt = -1, CaptureProcessedAt = 0;
    uint64 PresentationFrames = 0, CaptureFirstPresentedFrame = 0, CaptureSelected = 0;
    int CaptureResumeStage = 0, CaptureCombatTick = -1;
    int CaptureSoloRound = -1, CaptureSoloPhase = -1, CaptureSoloSeat = -1;
    bool CaptureStateStable = true;
    TSharedPtr<FJsonObject> CaptureRecord;
    TArray<TSharedPtr<FJsonValue>> CaptureRecords;

    UMaterialInstanceDynamic* Material(FLinearColor Color);
    UMaterialInstanceDynamic* StoneMaterial(FLinearColor Color);
    // Courtyard candidate textures (Courtyard_r001); null when the assets are absent so the plain blockout remains.
    UPROPERTY() TObjectPtr<UMaterialInterface> CourtyardStoneMaterial;
    UMaterialInstanceDynamic* CourtyardMaterial(const TCHAR* Texture,float TilingU,float TilingV,FLinearColor Tint=FLinearColor::White);
    UStaticMeshComponent* Mesh(AActor* ParentActor, const TCHAR* Shape, FVector Position,
        FVector Scale, FLinearColor Color, FRotator Rotation = FRotator::ZeroRotator);
    AActor* SceneActor(FVector Position = FVector::ZeroVector);
    FVector Position(wc::Cell Cell) const;
    void BuildScene();
    void BuildInterface();
    void UpdateInterfaceText();
    void UpdateCamera();
    float WorldUnitsPerPixel(FVector Location) const;
    bool CaptureBoardProjection(TSharedRef<FJsonObject> Record) const;
    FSlateRect BoardPixelBounds() const;
    void UpdatePreparationPreview();
    void UpdatePresentation(float DeltaSeconds);
    void AddPieceView(uint64 Id, int Definition, int Side, bool Neutral);
    bool EditCell(wc::Cell WorldCell, bool Remove);
    bool BoardClick(bool Remove);
    bool BoardRayClick(const FVector& Origin, const FVector& Direction, bool Remove);
    bool BellbackRayHit(const FVector& Origin, const FVector& Direction, uint64& Id, wc::Cell& Cell) const;
    static bool RayImportedBounds(const FBox& Bounds, const FTransform& Transform,
        const FVector& Origin, const FVector& Direction, double& Distance);
    wc::OwnedUnit* SelectedPiece();
    void ChooseHero(int Index);
    void ChangeStars();
    void ChangeFacing();
    bool EquipRelic(int Index);
    void CycleRelic();
    void UnequipRelic();
    void RemoveSelected();
    void ClearFormation();
    void Preset();
    bool Start(bool FromReplay = false);
    void TogglePause();
    void Step();
    void Reset();
    void Advance();
    FString StatusText() const;
    FString InspectorText() const;
    FString EventText() const;
    FString Signature() const;
    void TickExercise();
    void QueueCapture(const FString& Filename, int ResumeStage);
    void TickCapture();
    bool WriteEvidence(bool Passed);

    const wc::Combat* CurrentCombat() const;
    void BuildSoloInterface();
    void BuildStorybookInterface();
    void StartSolo();
    void NewSolo();
    void TickSolo(float DeltaSeconds);
    void SyncSoloFormation();
    bool SoloCommand(wc::Command Command);
    bool SoloCell(wc::Cell WorldCell);
    void SelectBench(int Slot);
    FString SoloKeyboardTargetText() const;
    void SaveSolo(bool Automatic = false);
    void ResumeSolo();
    void ScoutSolo(int Seat);
    void EquipSolo(int Relic);
    FString SoloStatusText() const;
    FString SoloSummaryText() const;
    FString ShopText(int Slot) const;
    FString BenchText(int Slot) const;
    FString RelicText(int Slot, bool Offer) const;
    void TickSoloExercise();
    void NextScenario();
    void LoadScenarioVariant(bool Alternative);
    void CompareScenario();
    void MirrorFormation();
    void SaveFormationScenario();
    void LoadFormationScenario();
    FString ScenarioText() const;
    bool ApplyFormationScenario(const wc::FormationScenario& Scenario, const FString& Success);
};
