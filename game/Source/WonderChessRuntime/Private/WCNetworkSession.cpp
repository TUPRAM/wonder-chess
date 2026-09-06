#include "WCNetworkSession.h"

#include "Engine/Engine.h"
#include "Engine/NetDriver.h"
#include "Engine/PendingNetGame.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "WCMatchRuntime.h"

namespace {
bool Decimal(const FString &Text, int Maximum, int &Value) {
  if (Text.IsEmpty() || Text.Len() > 5)
    return false;
  for (TCHAR Character : Text)
    if (Character < '0' || Character > '9')
      return false;
  Value = FCString::Atoi(*Text);
  return Value <= Maximum;
}
} // namespace

bool UWCNetworkSession::NormalizeJoinAddress(const FString &Input,
                                             FString &Output) {
  Output.Reset();
  TArray<FString> Endpoint;
  Input.ParseIntoArray(Endpoint, TEXT(":"), false);
  if (Endpoint.Num() < 1 || Endpoint.Num() > 2)
    return false;
  int Port = 7777;
  if (Endpoint.Num() == 2 && (!Decimal(Endpoint[1], 65535, Port) || Port == 0))
    return false;
  TArray<FString> Parts;
  Endpoint[0].ParseIntoArray(Parts, TEXT("."), false);
  if (Parts.Num() != 4)
    return false;
  int Octets[4];
  for (int Index = 0; Index < 4; ++Index)
    if (Parts[Index].Len() > 3 || !Decimal(Parts[Index], 255, Octets[Index]))
      return false;
  Output = FString::Printf(TEXT("%d.%d.%d.%d:%d"), Octets[0], Octets[1],
                           Octets[2], Octets[3], Port);
  return true;
}

bool UWCNetworkSession::RouteStartup(APlayerController *Controller) {
  if (bStartupConsumed) {
    bStartupRouting = false;
    return false;
  }
  bStartupConsumed = true;
  const bool Host = FParse::Param(FCommandLine::Get(), TEXT("WCHost"));
  FString Join;
  const bool Joining =
      FParse::Value(FCommandLine::Get(), TEXT("WCJoin="), Join) ||
      FParse::Param(FCommandLine::Get(), TEXT("WCJoin"));
  if (!Host && !Joining)
    return false;
  FString Address, PortText;
  int Port = 7777;
  const bool HasPort =
      FParse::Value(FCommandLine::Get(), TEXT("Port="), PortText);
  if (!Controller || Host == Joining ||
      (Host && HasPort && (!Decimal(PortText, 65535, Port) || Port == 0)) ||
      (Joining && !NormalizeJoinAddress(Join, Address))) {
    RecordFailure(Controller ? Controller->GetWorld() : nullptr, false,
                  TEXT("Invalid network launch options. Use -WCHost -Port=7777 "
                       "or -WCJoin=127.0.0.1:7777."),
                  NAME_None,
                  TEXT("Host and join are mutually exclusive; joining requires "
                       "a literal IPv4 address and port 1-65535."));
    return false;
  }
  if (Host) {
    FURL URL(nullptr, TEXT("/Game/WonderChess/Maps/L_WC_Courtyard"),
             TRAVEL_Absolute);
    URL.Port = Port;
    URL.AddOption(TEXT("listen"));
    URL.AddOption(TEXT("WCHumans=2"));
    Address = URL.ToString();
  }
  bStartupRouting = true;
  const TWeakObjectPtr<APlayerController> Player(Controller);
  Controller->GetWorldTimerManager().SetTimerForNextTick([Player, Address,
                                                          Host]() {
    if (!Player.IsValid())
      return;
    if (Host && GEngine)
      GEngine->SetClientTravel(Player->GetWorld(), *Address, TRAVEL_Absolute);
    else
      Player->ClientTravel(Address, TRAVEL_Absolute);
  });
  return true;
}

void UWCNetworkSession::Init() {
  Super::Init();
  if (GEngine) {
    NetworkFailureHandle = GEngine->OnNetworkFailure().AddUObject(
        this, &UWCNetworkSession::HandleNetworkFailure);
    TravelFailureHandle = GEngine->OnTravelFailure().AddUObject(
        this, &UWCNetworkSession::HandleTravelFailure);
  }
}

void UWCNetworkSession::Shutdown() {
  if (GEngine) {
    GEngine->OnNetworkFailure().Remove(NetworkFailureHandle);
    GEngine->OnTravelFailure().Remove(TravelFailureHandle);
  }
  NetworkFailureHandle.Reset();
  TravelFailureHandle.Reset();
  Super::Shutdown();
}

void UWCNetworkSession::ClearNetworkFailure() {
  LastNetworkError.Reset();
  LastNetworkDetail.Reset();
  LastNetworkErrorKey = NAME_None;
  bMatchAborted = false;
  bHostDisconnected = false;
}

void UWCNetworkSession::RecordFailure(UWorld *FailureWorld,
                                      bool HostDisconnected,
                                      const FString &Message, FName MessageKey,
                                      const FString &Detail) {
  // A secondary travel failure must not erase the original host-loss diagnosis.
  if (bHostDisconnected)
    return;
  bStartupRouting = false;
  bMatchAborted = true;
  bHostDisconnected = HostDisconnected;
  LastNetworkError = Message;
  LastNetworkErrorKey = MessageKey;
  LastNetworkDetail = Detail;

  if (FailureWorld) {
    if (auto *Mode = FailureWorld->GetAuthGameMode<AWCMatchMode>()) {
      if (Mode->Match) {
        Mode->Match->Abort();
        Mode->Publish();
      }
    }
  }
  UE_LOG(LogTemp, Warning,
         TEXT("WC_SESSION_ABORTED host_disconnected=%d winner=none message=%s "
              "detail=%s"),
         bHostDisconnected, *LastNetworkError, *LastNetworkDetail);
}

void UWCNetworkSession::HandleNetworkFailure(UWorld *FailureWorld,
                                             UNetDriver *NetDriver,
                                             ENetworkFailure::Type FailureType,
                                             const FString &ErrorString) {
  if (NetDriver && NetDriver->NetDriverName != NAME_GameNetDriver &&
      NetDriver->NetDriverName != NAME_PendingNetDriver)
    return;
  if (!FailureWorld && NetDriver)
    FailureWorld = NetDriver->GetWorld();
  if (!FailureWorld && NetDriver && GEngine) {
    for (const FWorldContext &Context : GEngine->GetWorldContexts()) {
      if (Context.OwningGameInstance == this && Context.PendingNetGame &&
          Context.PendingNetGame->NetDriver == NetDriver) {
        FailureWorld = Context.World();
        break;
      }
    }
  }
  if (!FailureWorld || FailureWorld->GetGameInstance() != this)
    return;

  const bool IsClient = FailureWorld->GetNetMode() == NM_Client ||
                        (NetDriver && (NetDriver->GetNetMode() == NM_Client ||
                                       NetDriver->ServerConnection != nullptr));
  const bool ConnectionEnded =
      FailureType == ENetworkFailure::ConnectionLost ||
      FailureType == ENetworkFailure::ConnectionTimeout;
  const bool HostingFailure =
      FailureType == ENetworkFailure::NetDriverAlreadyExists ||
      FailureType == ENetworkFailure::NetDriverCreateFailure ||
      FailureType == ENetworkFailure::NetDriverListenFailure;
  const ENetMode NetMode = FailureWorld->GetNetMode();

  if (!IsClient &&
      (NetMode == NM_ListenServer || NetMode == NM_DedicatedServer) &&
      !HostingFailure) {
    // The authority's Logout handler preserves the departed seat and installs
    // its bot.
    UE_LOG(
        LogTemp, Display,
        TEXT("WC_REMOTE_CONNECTION_FAILURE tournament_continues=true type=%s"),
        ENetworkFailure::ToString(FailureType));
    return;
  }

  const FString Detail = FString(ENetworkFailure::ToString(FailureType)) +
                         TEXT(": ") + ErrorString;
  if (IsClient && ConnectionEnded) {
    RecordFailure(
        FailureWorld, true,
        TEXT("The host disconnected. This match ended without a winner."),
        TEXT("result.abort"), Detail);
  } else {
    RecordFailure(FailureWorld, false,
                  HostingFailure ? TEXT("The local network host could not "
                                        "start. No winner was declared.")
                                 : TEXT("The network connection failed. This "
                                        "session ended without a winner."),
                  NAME_None, Detail);
  }
}

void UWCNetworkSession::HandleTravelFailure(UWorld *FailureWorld,
                                            ETravelFailure::Type FailureType,
                                            const FString &ErrorString) {
  if (!FailureWorld || FailureWorld->GetGameInstance() != this)
    return;
  RecordFailure(FailureWorld, false,
                TEXT("The game could not load the requested session. No winner "
                     "was declared."),
                NAME_None,
                FString(ETravelFailure::ToString(FailureType)) + TEXT(": ") +
                    ErrorString);
}
