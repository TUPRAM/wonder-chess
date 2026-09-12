#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "WCDefinitionRegistry.h"
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
    };
    wc::Catalog Catalog;
    FWCDefinitionText Metadata;
    std::array<std::vector<wc::OwnedUnit>, 2> Formation, ReplayFormation;
    std::unique_ptr<wc::Combat> Fight, PreparationState;
    TMap<uint64, FPieceView> Pieces;
    TArray<UStaticMeshComponent*> Cells, Telegraphs;
    TSharedPtr<SWidget> Interface, BoardInput;
    TSharedPtr<STextBlock> InspectorBlock, EventBlock, StatusBlock, MessageBlock;
    UPROPERTY() TArray<TObjectPtr<AActor>> SceneActors;
    UPROPERTY() TMap<uint32, TObjectPtr<UMaterialInstanceDynamic>> Materials;
    UPROPERTY() TMap<FString, TObjectPtr<UStaticMesh>> ProxyMeshes;
    UPROPERTY() TObjectPtr<UMaterialInterface> ProxyMaterial;
    UPROPERTY() TObjectPtr<ACameraActor> Camera;
    UPROPERTY() TObjectPtr<AWCVNextLabController> Controller;
    FString Message, LoadError, EvidenceDirectory;
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
    bool CaptureStateStable = true;
    TSharedPtr<FJsonObject> CaptureRecord;
    TArray<TSharedPtr<FJsonValue>> CaptureRecords;

    UMaterialInstanceDynamic* Material(FLinearColor Color);
    UStaticMeshComponent* Mesh(AActor* ParentActor, const TCHAR* Shape, FVector Position,
        FVector Scale, FLinearColor Color, FRotator Rotation = FRotator::ZeroRotator);
    AActor* SceneActor(FVector Position = FVector::ZeroVector);
    FVector Position(wc::Cell Cell) const;
    void BuildScene();
    void BuildInterface();
    void UpdateInterfaceText();
    void UpdateCamera();
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
};
