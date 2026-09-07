#pragma once

#include "CoreMinimal.h"
#include "Engine/EngineBaseTypes.h"
#include "Engine/GameInstance.h"
#include "Net/Core/Connection/NetEnums.h"
#include "WCNetworkSession.generated.h"

class UNetDriver;
class APlayerController;

UCLASS()
class WONDERCHESSRUNTIME_API UWCNetworkSession : public UGameInstance {
  GENERATED_BODY()

public:
  virtual void Init() override;
  virtual void Shutdown() override;
  bool RouteStartup(APlayerController *Controller);
  bool IsStartupRouting() const { return bStartupRouting; }
  static bool NormalizeJoinAddress(const FString &Input, FString &Output);

  UPROPERTY(BlueprintReadOnly, Category = "WonderChess|Session")
  FString LastNetworkError;

  UPROPERTY(BlueprintReadOnly, Category = "WonderChess|Session")
  FString LastNetworkDetail;

  // Retained across travel so a failed connection can be edited and retried.
  FString LastJoinAddress, LastSessionAction;

  UPROPERTY(BlueprintReadOnly, Category = "WonderChess|Session")
  FName LastNetworkErrorKey = NAME_None;

  UPROPERTY(BlueprintReadOnly, Category = "WonderChess|Session")
  bool bMatchAborted = false;

  UPROPERTY(BlueprintReadOnly, Category = "WonderChess|Session")
  bool bHostDisconnected = false;

  // Called by an explicit new-session action, never by automatic failure
  // travel.
  UFUNCTION(BlueprintCallable, Category = "WonderChess|Session")
  void ClearNetworkFailure();

private:
  bool bStartupConsumed = false;
  bool bStartupRouting = false;
  FDelegateHandle NetworkFailureHandle;
  FDelegateHandle TravelFailureHandle;

  void HandleNetworkFailure(UWorld *FailureWorld, UNetDriver *NetDriver,
                            ENetworkFailure::Type FailureType,
                            const FString &ErrorString);
  void HandleTravelFailure(UWorld *FailureWorld,
                           ETravelFailure::Type FailureType,
                           const FString &ErrorString);
  void RecordFailure(UWorld *FailureWorld, bool HostDisconnected,
                     const FString &Message, FName MessageKey,
                     const FString &Detail);
};
