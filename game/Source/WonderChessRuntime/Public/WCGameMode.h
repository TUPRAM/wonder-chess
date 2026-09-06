#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "WCGameMode.generated.h"

UCLASS()
class WONDERCHESSRUNTIME_API AWCGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AWCGameMode();
};

UCLASS()
class WONDERCHESSRUNTIME_API AWCHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
