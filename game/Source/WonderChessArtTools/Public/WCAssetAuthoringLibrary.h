#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WCAssetAuthoringLibrary.generated.h"
class USkeletalMesh;
class USkeletalMeshComponent;
class UAnimSequence;
class UControlRig;
class USkeleton;
UCLASS()
class WONDERCHESSARTTOOLS_API UWCAssetAuthoringLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static USkeleton* CreateCreatureSkeleton(const FString& AssetPath, const TArray<FName>& Names,
        const TArray<int32>& Parents, const TArray<FTransform>& LocalTransforms);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool InitializeCreatureSkeleton(USkeleton* Skeleton, const TArray<FName>& Names,
        const TArray<int32>& Parents, const TArray<FTransform>& LocalTransforms);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool InitializeRig(UControlRig* Rig);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool EnsureMeshSocket(USkeletalMesh* Mesh, FName SocketName, FName BoneName, FTransform LocalTransform);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool SetBellbackPose(USkeletalMeshComponent* Mesh, UAnimSequence* Current, float CurrentTime,
        UAnimSequence* Previous, float PreviousTime, float BlendAlpha);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool ConfigureBellbackLOD(USkeletalMesh* Mesh, int32 Index);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString MeasureBellbackSurface(USkeletalMeshComponent* Mesh, int32 LOD);
    // Candidate-authored rest-space regions keep contact checks independent of anatomy.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString MeasureCreatureSurface(USkeletalMeshComponent* Mesh, int32 LOD,
        const TArray<FVector>& RegionMin, const TArray<FVector>& RegionMax);
    // Native controller finalization synchronizes authored and target sampling.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool FinalizeCreatureAnimationSampling(UAnimSequence* Sequence);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool SetCragstoatPose(USkeletalMeshComponent* Mesh, UAnimSequence* Current, float CurrentTime,
        UAnimSequence* Previous, float PreviousTime, float BlendAlpha,
        UAnimSequence* HitReaction, float HitReactionTime, UAnimSequence* GroundingReference);
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString CragstoatPoseAudit(USkeletalMeshComponent* Mesh);
    // Read the current Sequencer data-model interface, not deprecated raw-track storage.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString InspectCragstoatAnimationSource(UAnimSequence* Sequence);
};
