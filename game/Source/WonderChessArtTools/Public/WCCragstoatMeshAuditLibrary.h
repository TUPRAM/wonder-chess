#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WCCragstoatMeshAuditLibrary.generated.h"

class USkeletalMesh;

UCLASS()
class WONDERCHESSARTTOOLS_API UWCCragstoatMeshAuditLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Read-only LOD0 render-buffer comparison of the exact source/private pilot.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString CompareCragstoatBodySkin(USkeletalMesh* Source, USkeletalMesh* Candidate);

    // Read-only exact-source render-byte weights grouped by imported vertex id.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static FString ExportCragstoatSourceRenderWeights(USkeletalMesh* Source);
};
