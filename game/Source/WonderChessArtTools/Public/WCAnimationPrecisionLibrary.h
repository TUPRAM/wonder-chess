#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "WCAnimationPrecisionLibrary.generated.h"

class UAnimSequence;

// Private candidate authoring only; never used by the gameplay runtime.
UCLASS()
class WONDERCHESSARTTOOLS_API UWCAnimationPrecisionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // Replace one existing Running_r005 bone's rotation channels after a complete
    // 37-key preflight. Translation, scale, source assets and finalization are separate.
    UFUNCTION(BlueprintCallable, Category="Wonder Chess|Editor Art")
    static bool SetCragstoatPreciseRotationKeys(UAnimSequence* Sequence, FName Bone,
        const TArray<FQuat>& SourceKeys);
};
