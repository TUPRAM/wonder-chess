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
class UTextRenderComponent;
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
        UStaticMeshComponent* Mana = nullptr;
        UStaticMeshComponent* HealthTrack = nullptr;
        UStaticMeshComponent* ManaTrack = nullptr;
        TArray<UStaticMeshComponent*> TierPips;
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
    void UpdateCombatCues();
    void CueMesh(const TCHAR* Shape,FVector Location,FVector Scale,FLinearColor Color,FRotator Rotation=FRotator::ZeroRotator);
    void CueLine(FVector A,FVector B,FLinearColor Color,float Width);
    void CueRing(FVector Center,float Radius,FLinearColor Color,float Width,float Arc=UE_TWO_PI,float Rotation=0);
    void CueText(FVector Location,const FString& Text,FLinearColor Color,float Size);
    void CueStar(FVector Center,float Radius,FLinearColor Color,float Width,float Rotation=0);
    void UpdatePlacementCue();
    int PlacementState(wc::Cell Cell) const;
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
    void AddPieceView(uint64 Id, int Definition, int Side);
    bool EditCell(wc::Cell WorldCell, bool Remove);
    bool BoardClick(bool Remove);
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
