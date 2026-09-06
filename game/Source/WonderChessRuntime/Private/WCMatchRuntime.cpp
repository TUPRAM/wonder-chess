#include "WCMatchRuntime.h"
#include "Components/AudioComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/PlatformProcess.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Net/UnrealNetwork.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "Serialization/JsonSerializer.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundConcurrency.h"
#include "Sound/SoundWave.h"
#include "TimerManager.h"
#include "UnrealClient.h"
#include "WCBoardPresenter.h"
#include "WCDefinitionRegistry.h"
#include "WCNetworkSession.h"
#include "WCVerification.h"

namespace {
using Obj = TSharedPtr<FJsonObject>;
using Val = TSharedPtr<FJsonValue>;
FString Str(const std::string &S) { return UTF8_TO_TCHAR(S.c_str()); }
Obj NewObj() { return MakeShared<FJsonObject>(); }
Val J(Obj O) { return MakeShared<FJsonValueObject>(O); }
FString Encode(Obj O) {
  FString S;
  auto W =
      TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&S);
  FJsonSerializer::Serialize(O.ToSharedRef(), W);
  return S;
}
Obj Decode(const FString &S) {
  Obj O;
  FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(S), O);
  return O;
}
Obj Owned(const wc::OwnedUnit &U) {
  auto O = NewObj();
  O->SetNumberField("id", U.id);
  O->SetNumberField("def", U.definition);
  O->SetBoolField("neutral", U.neutral);
  O->SetNumberField("star", U.star);
  O->SetBoolField("board", U.onBoard);
  O->SetNumberField("col", U.cell.column);
  O->SetNumberField("row", U.cell.row);
  O->SetNumberField("bench", U.bench);
  return O;
}
Obj Pair(const wc::Pairing &P) {
  auto O = NewObj();
  O->SetNumberField("a", P.a);
  O->SetNumberField("b", P.b);
  O->SetBoolField("ghost", P.ghost);
  O->SetBoolField("neutral", P.kind == wc::EncounterKind::Neutral);
  O->SetStringField("kind", P.kind == wc::EncounterKind::Neutral ? TEXT("neutral") : P.ghost ? TEXT("ghost") : TEXT("pvp"));
  O->SetStringField("waveId", Str(P.waveId));
  TArray<Val> Sides;
  for (int Side = 0; Side < 2; ++Side) {
    auto Owner = NewObj();
    const bool Neutral = Side == 1 && P.kind == wc::EncounterKind::Neutral;
    if (Neutral) Owner->SetField("seat", MakeShared<FJsonValueNull>());
    else Owner->SetNumberField("seat", Side == 0 ? P.a : P.b);
    Owner->SetStringField("waveId", Neutral ? Str(P.waveId) : FString());
    Sides.Add(J(Owner));
  }
  O->SetArrayField("sides", Sides);
  return O;
}
} // namespace

void AWCMatchState::GetLifetimeReplicatedProps(
    TArray<FLifetimeProperty> &OutLifetimeProps) const {
  Super::GetLifetimeReplicatedProps(OutLifetimeProps);
  DOREPLIFETIME(AWCMatchState, PublicJson);
}

AWCMatchMode::AWCMatchMode() {
  PrimaryActorTick.bCanEverTick = true;
  GameStateClass = AWCMatchState::StaticClass();
  PlayerControllerClass = AWCMatchController::StaticClass();
  HUDClass = AWCMatchHUD::StaticClass();
  DefaultPawnClass = nullptr;
}
void AWCMatchMode::BeginPlay() {
  Super::BeginPlay();
  if (GEngine)
    GEngine->SetMaxFPS(60);
  if (!wc::LoadCatalog(Catalog, LoadError)) {
    UE_LOG(LogTemp, Error, TEXT("WC_CATALOG_REJECTED %s"), *LoadError);
    Publish();
    return;
  }
  UE_LOG(LogTemp, Display, TEXT("WC_CATALOG_LOADED units=%d digest=%s"),
         int(Catalog.units.size()), *Str(Catalog.contentDigest));
  const FString Humans =
      UGameplayStatics::ParseOption(OptionsString, TEXT("WCHumans"));
  if (!Humans.IsEmpty())
    RequestedHumans = FCString::Atoi(*Humans);
  FParse::Value(FCommandLine::Get(), TEXT("WCFast="), Speed);
  Speed = FMath::Clamp(Speed, 1, 100);
  int32 Count = 0;
  if (FParse::Value(FCommandLine::Get(), TEXT("WCRegression="), Count)) {
    Regression(FMath::Clamp(Count, 1, 1000));
    return;
  }
  const auto *Session = Cast<UWCNetworkSession>(GetGameInstance());
  if ((FParse::Param(FCommandLine::Get(), TEXT("WCAutoStart")) ||
       UGameplayStatics::HasOption(OptionsString, TEXT("WCNewSolo"))) &&
      !(Session && Session->bMatchAborted))
    GetWorldTimerManager().SetTimerForNextTick([this]() {
      RequestEntry(Controllers.Num() ? Controllers[0].Get() : nullptr,
                      RequestedHumans, 314159);
    });
  Publish();
}
void AWCMatchMode::PostLogin(APlayerController *Player) {
  Super::PostLogin(Player);
  if (auto *P = Cast<AWCMatchController>(Player)) {
    if (Match || Controllers.Num() >= 2 ||
        (bEntryPending && Controllers.Num() >= RequestedHumans)) {
      P->ClientRejectSession(TEXT("This session has no open human seat. Create a fresh lobby to join."));
      return;
    }
    P->AssignedSeat = Controllers.Num();
    Controllers.Add(P);
    Publish();
  }
}
void AWCMatchMode::Logout(AController *Exiting) {
  if (auto *P = Cast<AWCMatchController>(Exiting)) {
    if (Match && P->AssignedSeat >= 0) {
      Match->TakeOver(P->AssignedSeat);
      UE_LOG(LogTemp, Display, TEXT("WC_BOT_TAKEOVER seat=%d"),
             P->AssignedSeat);
    }
    if (!Match) {
      Controllers.Remove(P);
      for (int32 Index = 0; Index < Controllers.Num(); ++Index)
        if (Controllers[Index].IsValid()) Controllers[Index]->AssignedSeat = Index;
      if (bEntryPending) CancelEntry(TEXT("A participant disconnected. Start a fresh session."));
    }
  }
  Super::Logout(Exiting);
}
void AWCMatchMode::RequestEntry(AWCMatchController* Requester, int32 Humans, int32 Seed) {
  if (bEntryPending) return;
  if ((!Controllers.IsEmpty() && Requester != Controllers[0].Get()) || Humans < 0 || Humans > 2 || !LoadError.IsEmpty()) return;
  if (Match && Match->CurrentPhase() != wc::Phase::Finished && Match->CurrentPhase() != wc::Phase::Aborted) {
    if (Requester) Requester->ClientReply(false, TEXT("Finish the current tournament before restarting."));
    return;
  }
  if (Humans < Controllers.Num() && GetNetMode() != NM_Standalone) return;
  Match.Reset(); LastRecap.Reset(); bPractice = false;
  RequestedHumans = Humans; EntrySeed = Seed; bEntryPending = true;
  EntryState = Humans == 2 && Controllers.Num() < 2 ? TEXT("WaitingForPlayers") : TEXT("Loading");
  EntryDeadline = FPlatformTime::Seconds() + 30.0; IntroductionRemaining = 0;
  for (auto Weak : Controllers) if (auto* P = Weak.Get()) {
    P->bEntryReady = Humans <= 1 && P->bCatalogReady;
    P->bEntrySkip = false;
  }
  UE_LOG(LogTemp, Display, TEXT("WC_ENTRY_REQUEST humans=%d seed=%d preparation_started=false"), Humans, Seed);
  Publish();
}
void AWCMatchMode::CancelEntry(const FString& Reason) {
  bEntryPending = false; EntryState.Reset(); IntroductionRemaining = 0;
  for (auto Weak : Controllers) if (auto* P = Weak.Get()) {
    P->bEntryReady = false; P->bEntrySkip = false;
    if (!Reason.IsEmpty()) P->ClientReply(false, Reason);
  }
  UE_LOG(LogTemp, Display, TEXT("WC_ENTRY_CANCEL reason=%s"), *Reason);
  Publish();
}
void AWCMatchMode::StartTournament(AWCMatchController *Requester, int32 Humans,
                                   int32 Seed) {
  if (Controllers.Num() && Requester != Controllers[0].Get()) {
    if (Requester)
      Requester->ClientReply(false,
                             TEXT("Only the host can start or restart."));
    return;
  }
  if (!LoadError.IsEmpty() || (Humans != 0 && Humans != 1 && Humans != 2))
    return;
  int32 Connected = 0;
  for (auto Weak : Controllers)
    if (Weak.IsValid())
      ++Connected;
  if (Humans == 2 && Connected != 2) {
    if (Requester)
      Requester->ClientReply(
          false, TEXT("Two connected humans are required. Return to title to "
                      "create a fresh lobby after a disconnect."));
    return;
  }
  if (Humans < Controllers.Num() && GetNetMode() != NM_Standalone) {
    if (Requester)
      Requester->ClientReply(false, TEXT("Two connected humans require 2H6B."));
    return;
  }
  try {
    Match = MakeUnique<wc::Match>(Catalog, uint64(uint32(Seed)), Humans);
  } catch (const std::exception &E) {
    LoadError = Str(E.what());
    UE_LOG(LogTemp, Error, TEXT("WC_START_FAILED %s"), *LoadError);
    return;
  }
  bEntryPending = false; EntryState.Reset(); IntroductionRemaining = 0;
  LastLoggedRound = 0;
  MillisecondCarry = 0;
  LastRecap.Reset();
  bPractice = false;
  for (auto Weak : Controllers)
    if (auto *P = Weak.Get()) {
      P->SelectedUnit = 0;
      P->ObservedSeat = FMath::Max(0, P->AssignedSeat);
    }
  UE_LOG(LogTemp, Display, TEXT("WC_MATCH_START seed=%d humans=%d bots=%d"),
         Seed, Humans, 8 - Humans);
  Publish();
}
void AWCMatchMode::Tick(float Delta) {
  Super::Tick(Delta);
  if (bEntryPending) {
    int32 Connected = 0; bool Loaded = true, Ready = true, Skip = true;
    for (auto Weak : Controllers) if (auto* P = Weak.Get()) {
      ++Connected; Loaded &= P->bCatalogReady;
      Ready &= P->bEntryReady; Skip &= P->bEntrySkip;
    }
    const bool Enough = Connected >= RequestedHumans;
    if (FPlatformTime::Seconds() >= EntryDeadline) {
      CancelEntry(TEXT("Session preparation timed out. Check the connection and try again."));
    } else if (!Enough || !Loaded || !Ready) {
      IntroductionRemaining = 0;
      EntryState = !Enough ? TEXT("WaitingForPlayers") : !Loaded ? TEXT("Loading") : TEXT("Ready");
    } else if (EntryState == TEXT("Introduction")) {
      IntroductionRemaining -= Delta;
      if (Skip || IntroductionRemaining <= 0) {
        StartTournament(Controllers.Num() ? Controllers[0].Get() : nullptr, RequestedHumans, EntrySeed);
        if (Match) {
          UE_LOG(LogTemp, Display, TEXT("WC_ENTRY_COMPLETE all_catalogs_ready=true preparation_elapsed_ms=0"));
        } else {
          CancelEntry(TEXT("The session could not start. Return to the lobby and try again."));
        }
        return;
      }
    } else { EntryState = TEXT("Introduction"); IntroductionRemaining = 3.0; Publish(); }
  }
  bool Paused = false;
  if (GetNetMode() == NM_Standalone && Controllers.Num() &&
      Controllers[0].IsValid())
    Paused = Controllers[0]->bOptions;
  if (bPractice && Match && Match->Round() == 1 &&
      Match->CurrentPhase() == wc::Phase::Preparation &&
      !Match->Seats()[0].ready)
    Paused = true;
  if (Match && !Paused) {
    MillisecondCarry += double(Delta) * 1000 * Speed;
    const int Ms = int(MillisecondCarry);
    MillisecondCarry -= Ms;
    try {
      Match->Tick(Ms);
    } catch (const std::exception &E) {
      UE_LOG(LogTemp, Error, TEXT("WC_RUNTIME_FAILED %s"), *Str(E.what()));
      LoadError = Str(E.what());
      Match->Abort();
    }
    if (Match->Records().size() > size_t(LastLoggedRound)) {
      LastLoggedRound = int(Match->Records().size());
      const auto &R = Match->Records().back();
      UE_LOG(LogTemp, Display,
             TEXT("WC_ROUND_SETTLED round=%d seat0_hp=%d records=%d"), R.round,
             R.health[0], LastLoggedRound);
      if (Match->CurrentPhase() == wc::Phase::Finished)
        UE_LOG(LogTemp, Display,
               TEXT("WC_MATCH_FINISHED seed=%llu rounds=%d capped=%d"),
               Match->Seed(), Match->Round(), Match->Capped());
    }
  }
  SnapshotClock += Delta;
  const double SnapshotInterval =
      Match && Match->CurrentPhase() == wc::Phase::Combat ? .10 : .25;
  if (SnapshotClock >= SnapshotInterval) {
    SnapshotClock = 0;
    Publish();
  }
}
void AWCMatchMode::Publish() {
  auto O = NewObj();
  O->SetBoolField("practice", bPractice);
  O->SetStringField("entryState", EntryState);
  O->SetNumberField("entryRemainingMs", bEntryPending ? FMath::Max(0.0, (EntryState == TEXT("Introduction") ? IntroductionRemaining : EntryDeadline-FPlatformTime::Seconds()) * 1000.0) : 0);
  O->SetStringField("schemaVersion", Str(Catalog.schemaVersion));
  O->SetStringField("contentDigest", Str(Catalog.contentDigest));
  O->SetNumberField("protocolVersion", 4);
  TArray<Val> Participants;
  for (int32 Seat = 0; Seat < 8; ++Seat) {
    auto Participant = NewObj();
    const bool Human = Seat < RequestedHumans;
    auto* Controller = Controllers.IsValidIndex(Seat) ? Controllers[Seat].Get() : nullptr;
    Participant->SetNumberField("seat", Seat);
    Participant->SetBoolField("bot", !Human);
    Participant->SetBoolField("ready", !Human || (Controller && Controller->bCatalogReady && Controller->bEntryReady));
    Participant->SetStringField("name", Human ? FString::Printf(TEXT("Player %d"), Seat+1) : !Catalog.bots.empty() ? Str(Catalog.bots[(Seat-RequestedHumans)%Catalog.bots.size()].label) : TEXT("Bot"));
    Participants.Add(J(Participant));
  }
  O->SetArrayField("entryParticipants", Participants);
  O->SetNumberField("matchNamespace", Match ? Match->Namespace() : 0);
  O->SetStringField("error", LoadError);
  int Connected = 0;
  for (auto Weak : Controllers)
    if (Weak.IsValid())
      ++Connected;
  O->SetNumberField("connected", Connected);
  O->SetNumberField("requestedHumans", RequestedHumans);
  O->SetBoolField("network", GetNetMode() != NM_Standalone);
  O->SetNumberField("phase", Match ? int(Match->CurrentPhase()) : -1);
  O->SetNumberField("round", Match ? Match->Round() : 0);
  O->SetNumberField("pvpRoundIndex", Match ? Match->PvpRoundIndex() : 0);
  O->SetBoolField("neutralRound", Match && Match->NeutralRound());
  if (Match && Match->CurrentWave()) {
    const auto& Wave = *Match->CurrentWave(); auto Preview = NewObj();
    Preview->SetStringField("id", Str(Wave.id)); Preview->SetStringField("name", Str(Wave.name));
    Preview->SetNumberField("hpScaleBp", Wave.hpScaleBp); Preview->SetNumberField("damageScaleBp", Wave.damageScaleBp);
    TArray<Val> Creatures;
    for (const auto& Slot : Wave.slots) {
      auto Creature = NewObj(); Creature->SetNumberField("def", Slot.definition);
      Creature->SetStringField("name", Str(Catalog.neutrals[Slot.definition].displayName));
      Creature->SetNumberField("col", Slot.cell.column); Creature->SetNumberField("row", Slot.cell.row);
      Creatures.Add(J(Creature));
    }
    Preview->SetArrayField("creatures", Creatures); O->SetObjectField("wavePreview", Preview);
  }
  O->SetNumberField("remaining", Match ? Match->RemainingMs() : 0);
  O->SetBoolField("capped", Match && Match->Capped());
  TArray<Val> Seats, Pairs, Encounters;
  if (Match) {
    for (const auto &S : Match->PublicSeats()) {
      auto P = NewObj();
      P->SetNumberField("id", S.id);
      P->SetStringField("name", Str(S.label));
      P->SetBoolField("human", S.human);
      P->SetBoolField("ready", S.ready);
      P->SetBoolField("takeover", S.takeover);
      P->SetNumberField("health", S.health);
      P->SetNumberField("level", S.level);
      P->SetNumberField("place", S.placement);
      P->SetNumberField("wins", S.wins);
      TArray<Val> Deployment;
      for (const auto &U : S.deployment) {
        auto PublicUnit = Owned(U);
        PublicUnit->RemoveField(TEXT("bench"));
        Deployment.Add(J(PublicUnit));
      }
      P->SetArrayField("units", Deployment);
      Seats.Add(J(P));
    }
    for (const auto &P : Match->Pairings())
      Pairs.Add(J(Pair(P)));
    for (const auto &E : Match->Encounters()) {
      auto P = Pair(E.pairing);
      P->SetNumberField("tick", E.combat.CurrentTick());
      P->SetBoolField("complete", E.combat.Result().complete);
      P->SetBoolField("timeout", E.combat.Result().timeout);
      P->SetNumberField("winner", E.combat.Result().winner);
      TArray<Val> Units;
      for (const auto &U : E.combat.Units()) {
        auto V = NewObj();
        V->SetNumberField("id", U.id);
        V->SetNumberField("def", U.definition);
        V->SetBoolField("neutral", U.neutral);
        V->SetNumberField("movementBonus", U.movementBonus);
        V->SetNumberField("star", U.star);
        V->SetNumberField("side", U.side);
        V->SetNumberField("col", U.cell.column);
        V->SetNumberField("row", U.cell.row);
        V->SetNumberField("destCol", U.destination.column);
        V->SetNumberField("destRow", U.destination.row);
        V->SetNumberField("state", int(U.state));
        V->SetNumberField("hp", U.health);
        V->SetNumberField("maxHp", U.maxHealth);
        V->SetNumberField("attack", U.basicDamage);
        V->SetNumberField("basicDamage", U.basicDamage);
        V->SetNumberField("basicBonus", U.basicBonus);
        V->SetNumberField("abilityBonus", U.abilityBonus);
        V->SetNumberField("allBonus", U.allBonus);
        V->SetNumberField("supportBonus", U.supportBonus);
        V->SetNumberField("armor", U.armor);
        V->SetNumberField("resistance", U.resistance);
        V->SetNumberField("rateBonus", U.rateBonus);
        int EffectiveRate = U.rateBonus;
        for (const auto &Modifier : U.modifiers)
          EffectiveRate += int(Modifier.magnitude);
        V->SetNumberField("effectiveRateBonus", EffectiveRate);
        V->SetNumberField(
            "target", U.target >= 0 && U.target < int(E.combat.Units().size())
                          ? E.combat.Units()[U.target].id
                          : 0);
        V->SetNumberField("shield", U.shield);
        V->SetNumberField("action", U.actionId);
        V->SetNumberField("snapshotTick", E.combat.CurrentTick());
        V->SetNumberField("releaseTick", U.releaseTick);
        V->SetNumberField("stun",
                          U.stunExpiry > E.combat.CurrentTick() ? 1 : 0);
        Units.Add(J(V));
      }
      P->SetArrayField("units", Units);
      TArray<Val> VisualActions;
      for (const auto &Action : E.combat.VisualActions()) {
        auto V = NewObj();
        V->SetNumberField("source", Action.source);
        V->SetNumberField("target", Action.target);
        V->SetNumberField("action", Action.action);
        V->SetNumberField("definition", Action.definition);
        V->SetNumberField("radius", Action.radius);
        V->SetNumberField("releaseTick", Action.releaseTick);
        V->SetNumberField("impactTick", Action.impactTick);
        V->SetNumberField("originCol", Action.origin.column);
        V->SetNumberField("originRow", Action.origin.row);
        V->SetNumberField("col", Action.center.column);
        V->SetNumberField("row", Action.center.row);
        V->SetNumberField("effect", int(Action.effect));
        V->SetNumberField("damageType", int(Action.damageType));
        V->SetBoolField("neutral", Action.neutral);
        V->SetBoolField("basicAttack", Action.basicAttack);
        V->SetBoolField("released", Action.released);
        V->SetBoolField("provisional", Action.provisional);
        V->SetBoolField("recipientsProvisional", Action.recipientsProvisional);
        V->SetBoolField("fixedArea", Action.fixedArea);
        TArray<Val> Recipients;
        for (const auto Recipient : Action.recipients)
          Recipients.Add(MakeShared<FJsonValueNumber>(double(Recipient)));
        V->SetArrayField("recipients", Recipients);
        VisualActions.Add(J(V));
      }
      P->SetArrayField("visualActions", VisualActions);
      TArray<Val> Survivors, HealthLoss, Absorbed, Healing, CaptainDamage;
      int64 Loss[2] = {0, 0}, Shield[2] = {0, 0}, Heal[2] = {0, 0};
      TMap<int64, int> Sides;
      for (const auto &U : E.combat.Units())
        Sides.Add(U.id, U.side);
      for (const auto &Event : E.combat.Events())
        if (Sides.Contains(Event.target)) {
          int Side = Sides[Event.target];
          Loss[Side] += Event.healthLoss;
          Shield[Side] += Event.absorbed;
          if (Event.effect == wc::Effect::Heal)
            Heal[Side] += Event.resolved;
        }
      int StageBase = 0;
      for (const auto &Stage : Catalog.rules.lossStages)
        if (Match->PvpRoundIndex() >= Stage.start && Match->PvpRoundIndex() <= Stage.end)
          StageBase = Stage.damage;
      for (int Side = 0; Side < 2; ++Side) {
        Survivors.Add(
            MakeShared<FJsonValueNumber>(E.combat.Result().survivors[Side]));
        HealthLoss.Add(MakeShared<FJsonValueNumber>(Loss[Side]));
        Absorbed.Add(MakeShared<FJsonValueNumber>(Shield[Side]));
        Healing.Add(MakeShared<FJsonValueNumber>(Heal[Side]));
        int Damage = 0;
        if (!Match->Records().empty() &&
            Match->Records().back().round == Match->Round() &&
            !(Side == 1 && (E.pairing.ghost || E.kind == wc::EncounterKind::Neutral)))
          Damage = Match->Records().back().damage[Side == 0 ? E.pairing.a
                                                            : E.pairing.b];
        CaptainDamage.Add(MakeShared<FJsonValueNumber>(Damage));
      }
      P->SetArrayField("survivors", Survivors);
      P->SetArrayField("healthLoss", HealthLoss);
      P->SetArrayField("absorbed", Absorbed);
      P->SetArrayField("healing", Healing);
      P->SetArrayField("captainDamage", CaptainDamage);
      P->SetNumberField("stageBase", StageBase);
      TArray<Val> Events;
      const auto &All = E.combat.Events();
      const int EventWindowTicks = FMath::DivideAndRoundUp(2000, Catalog.rules.tickMs);
      const int EarliestEventTick = E.combat.CurrentTick() - EventWindowTicks;
      size_t FirstEvent = 0;
      while (FirstEvent < All.size() && All[FirstEvent].tick < EarliestEventTick) ++FirstEvent;
      P->SetNumberField("eventWindowStartTick", EarliestEventTick);
      for (size_t I = FirstEvent; I < All.size();
           ++I) {
        const auto &V = All[I];
        auto VJ = NewObj();
        VJ->SetNumberField("tick", V.tick);
        VJ->SetNumberField("action", V.action);
        VJ->SetNumberField("effect", int(V.effect));
        VJ->SetNumberField("damageType", int(V.damageType));
        VJ->SetBoolField("basicAttack", V.basicAttack);
        VJ->SetNumberField("radius", V.radius);
        VJ->SetNumberField("col", V.cell.column);
        VJ->SetNumberField("row", V.cell.row);
        VJ->SetNumberField("source", V.source);
        VJ->SetNumberField("target", V.target);
        VJ->SetNumberField("loss", V.healthLoss);
        VJ->SetNumberField("absorbed", V.absorbed);
        VJ->SetNumberField("resolved", V.resolved);
        Events.Add(J(VJ));
      }
      P->SetArrayField("events", Events);
      Encounters.Add(J(P));
    }
    if (!Match->Records().empty() &&
        (!LastRecap.IsValid() || LastRecap->GetNumberField(TEXT("round")) !=
                                     Match->Records().back().round)) {
      const auto &R = Match->Records().back();
      auto Rec = NewObj();
      Rec->SetNumberField("round", R.round);
      Rec->SetBoolField("neutral", R.neutral);
      Rec->SetNumberField("pvpRoundIndex", R.pvpRoundIndex);
      auto Numbers = [](const auto &Values) {
        TArray<Val> Result;
        for (auto Value : Values)
          Result.Add(MakeShared<FJsonValueNumber>(Value));
        return Result;
      };
      Rec->SetArrayField("damage", Numbers(R.damage));
      Rec->SetArrayField("health", Numbers(R.health));
      Rec->SetArrayField("pendingRewards", Numbers(R.pendingRewards));
      int StageBase = 0;
      for (const auto &Stage : Catalog.rules.lossStages)
        if (R.pvpRoundIndex >= Stage.start && R.pvpRoundIndex <= Stage.end)
          StageBase = Stage.damage;
      TArray<Val> RecapEncounters;
      for (const auto &Encounter : R.encounters) {
        auto Summary = Pair(Encounter.pairing);
        Summary->SetBoolField("complete", Encounter.result.complete);
        Summary->SetBoolField("timeout", Encounter.result.timeout);
        Summary->SetNumberField("winner", Encounter.result.winner);
        Summary->SetArrayField("survivors",
                               Numbers(Encounter.result.survivors));
        Summary->SetArrayField("healthLoss", Numbers(Encounter.healthLoss));
        Summary->SetArrayField("absorbed", Numbers(Encounter.absorbed));
        Summary->SetArrayField("healing", Numbers(Encounter.healing));
        const std::array<int, 2> CaptainDamage = {
            R.damage[Encounter.pairing.a],
            (Encounter.pairing.ghost || Encounter.kind == wc::EncounterKind::Neutral) ? 0 : R.damage[Encounter.pairing.b]};
        Summary->SetArrayField("captainDamage", Numbers(CaptainDamage));
        Summary->SetNumberField("stageBase", StageBase);
        RecapEncounters.Add(J(Summary));
      }
      Rec->SetArrayField("encounters", RecapEncounters);
      LastRecap = Rec;
    }
    if (LastRecap.IsValid())
      O->SetObjectField("recap", LastRecap);
  }
  O->SetArrayField("seats", Seats);
  O->SetArrayField("pairs", Pairs);
  O->SetArrayField("encounters", Encounters);
  if (auto *S = GetGameState<AWCMatchState>())
    S->PublicJson = Encode(O);
  for (auto Weak : Controllers)
    if (auto *P = Weak.Get()) {
      auto Private = NewObj();
      Private->SetNumberField("seat", P->AssignedSeat);
      if (Match && P->AssignedSeat >= 0 &&
          P->AssignedSeat < int(Match->Seats().size()) &&
          Match->Seats()[P->AssignedSeat].human) {
        const auto &S = Match->Seats()[P->AssignedSeat];
        Private->SetNumberField("gold", S.gold);
        Private->SetNumberField("xp", S.xp);
        Private->SetNumberField("level", S.level);
        Private->SetNumberField("revision", S.revision);
        Private->SetNumberField("sequence", S.sequence);
        Private->SetBoolField("locked", S.shopLocked);
        Private->SetBoolField("ready", S.ready);
        TArray<Val> Shop, Units;
        for (int U : S.shop)
          Shop.Add(MakeShared<FJsonValueNumber>(U));
        for (const auto &U : S.roster)
          Units.Add(J(Owned(U)));
        Private->SetArrayField("shop", Shop);
        Private->SetArrayField("units", Units);
      }
      P->ClientPrivateState(Encode(Private));
    }
}

void AWCMatchMode::Regression(int32 Count) {
  FString Directory = FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence");
  FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory);
  Directory = FPaths::ConvertRelativePathToFull(Directory);
  IFileManager::Get().MakeDirectory(*Directory, true);
  auto Report = NewObj();
  Report->SetNumberField("requested", Count);
  Report->SetNumberField("attempted", 0);
  Report->SetBoolField("complete", false);
  Report->SetStringField("start_utc", FDateTime::UtcNow().ToIso8601());
  Report->SetStringField("engine", FEngineVersion::Current().ToString());
  Report->SetStringField("digest", Str(Catalog.contentDigest));
  Report->SetStringField("schema_version", Str(Catalog.schemaVersion));
  Report->SetStringField("balance_version", Str(Catalog.balanceVersion));
  Report->SetNumberField("tick_ms", Catalog.rules.tickMs);
  Report->SetStringField("cpu", FPlatformMisc::GetCPUBrand());
  Report->SetStringField("executable_path", FPlatformProcess::ExecutablePath());
  Report->SetStringField("translation_unit_build_date", TEXT(__DATE__));
  Report->SetStringField("translation_unit_build_time", TEXT(__TIME__));
#if defined(_MSC_VER)
  Report->SetStringField("compiler", TEXT("MSVC"));
  Report->SetNumberField("compiler_version", _MSC_VER);
  Report->SetNumberField("compiler_full_version", _MSC_FULL_VER);
#endif
  Report->SetStringField(
      "provenance_boundary",
      TEXT("SHA1 values are calculated from files read by this process. "
           "SHA256 values come from staged manifest entries only when their "
           "SHA1 matches the loaded file. Current source files are "
           "observations, "
           "not a compiled-artifact manifest. Record delivered executable and "
           "source snapshot SHA256 externally. This is simulation timing, "
           "not rendered frame performance."));
  const FString DataDirectory =
      FPaths::ProjectContentDir() / TEXT("WonderChess/SourceData");
  FString ManifestText;
  Obj Manifest;
  if (FFileHelper::LoadFileToString(
          ManifestText, *(DataDirectory / TEXT("runtime_stage_manifest.json"))))
    Manifest = Decode(ManifestText);
  const Obj ManifestFiles =
      Manifest.IsValid() &&
              Manifest->HasTypedField<EJson::Object>(TEXT("files"))
          ? Manifest->GetObjectField(TEXT("files"))
          : Obj();
  auto Inputs = NewObj();
  auto RecordFile = [&](const FString &Key, const FString &Path) {
    auto Item = NewObj();
    Item->SetStringField("path", FPaths::ConvertRelativePathToFull(Path));
    TArray<uint8> Bytes;
    const bool Available = FFileHelper::LoadFileToArray(Bytes, *Path);
    Item->SetBoolField("available", Available);
    if (Available) {
      const FString Actual =
          FSHA1::HashBuffer(Bytes.GetData(), Bytes.Num()).ToString().ToLower();
      Item->SetStringField("sha1_actual", Actual);
      Item->SetNumberField("bytes", Bytes.Num());
      if (ManifestFiles.IsValid() &&
          ManifestFiles->HasTypedField<EJson::Object>(Key)) {
        const auto Expected = ManifestFiles->GetObjectField(Key);
        FString ExpectedSha1, ExpectedSha256;
        const bool Verified =
            Expected->TryGetStringField(TEXT("sha1"), ExpectedSha1) &&
            ExpectedSha1.Equals(Actual, ESearchCase::IgnoreCase);
        Item->SetBoolField("staged_manifest_sha1_matches", Verified);
        if (Verified &&
            Expected->TryGetStringField(TEXT("sha256"), ExpectedSha256))
          Item->SetStringField("sha256_staged_manifest", ExpectedSha256);
      }
    }
    Inputs->SetObjectField(Key, Item);
  };
  for (const FString Name :
       {TEXT("rules.alpha.json"), TEXT("units.json"), TEXT("traits.json"),
        TEXT("bots.json"), TEXT("world.json"), TEXT("neutrals.json")})
    RecordFile(Name, DataDirectory / Name);
  RecordFile(TEXT("runtime_stage_manifest.json"),
             DataDirectory / TEXT("runtime_stage_manifest.json"));
  const FString CurrentSource = TEXT(__FILE__);
  RecordFile(TEXT("observed_WCMatchRuntime.cpp"), CurrentSource);
  for (const FString Name :
       {TEXT("WonderSimulation.cpp"), TEXT("WonderTournament.cpp")})
    RecordFile(TEXT("observed_") + Name,
               FPaths::GetPath(CurrentSource) / TEXT("Simulation") / Name);
  Report->SetObjectField("input_files", Inputs);
  FString ProfileText;
  if (FFileHelper::LoadFileToString(
          ProfileText, *(DataDirectory / TEXT("rules.alpha.json")))) {
    const auto Profile = Decode(ProfileText);
    FString ProfileId;
    if (Profile.IsValid() &&
        Profile->TryGetStringField(TEXT("profile_id"), ProfileId))
      Report->SetStringField("profile_id", ProfileId);
  }
  TArray<Val> Trials;
  int Failures = 0;
  bool WriteFailed = false;
  const double BatchStart = FPlatformTime::Seconds();
  auto SaveReport = [&]() {
    if (!FFileHelper::SaveStringToFile(
            Encode(Report), *(Directory / TEXT("regression.json")))) {
      WriteFailed = true;
      UE_LOG(LogTemp, Error,
             TEXT("WC_REGRESSION_EVIDENCE_WRITE_FAILED path=%s"), *Directory);
    }
  };
  SaveReport();
  for (int Seed = 1; Seed <= Count; ++Seed) {
    auto Trial = NewObj();
    Trial->SetNumberField("seed", Seed);
    Trial->SetStringField("start_utc", FDateTime::UtcNow().ToIso8601());
    const double Start = FPlatformTime::Seconds();
    try {
      wc::Match M(Catalog, Seed, 0);
      Trial->SetNumberField("match_namespace", double(M.Namespace()));
      int Steps = 0, InvariantChecks = 0, LastDeploymentRound = -1;
      struct FUse {
        int UnitRounds = 0, Rounds = 0, MaxStar = 0;
        TSet<uint64> Ids;
      };
      TArray<TArray<FUse>> Uses;
      Uses.SetNum(Catalog.rules.seatCount);
      for (auto &SeatUses : Uses)
        SeatUses.SetNum(int(Catalog.units.size()));
      TArray<Val> Deployments;
      std::string Error;
      const int Limit =
          (Catalog.rules.firstPreparationMs +
           Catalog.rules.maxRounds *
               (Catalog.rules.preparationMs + Catalog.rules.combatTimeoutMs +
                Catalog.rules.settlementMs)) /
              Catalog.rules.tickMs +
          100;
      while (M.CurrentPhase() != wc::Phase::Finished && Steps < Limit) {
        M.Tick(Catalog.rules.tickMs);
        ++Steps;
        if (M.CurrentPhase() == wc::Phase::Combat &&
            LastDeploymentRound != M.Round()) {
          LastDeploymentRound = M.Round();
          auto Deployment = NewObj();
          Deployment->SetNumberField("round", M.Round());
          TArray<Val> DeployedSeats;
          for (const auto &Seat : M.Seats()) {
            auto DeployedSeat = NewObj();
            DeployedSeat->SetNumberField("seat", Seat.id);
            TArray<Val> Units;
            TSet<int> Seen;
            if (Seat.health > 0)
              for (const auto &Unit : Seat.roster)
                if (Unit.onBoard) {
                  Units.Add(J(Owned(Unit)));
                  auto &Use = Uses[Seat.id][Unit.definition];
                  ++Use.UnitRounds;
                  Use.MaxStar = FMath::Max(Use.MaxStar, Unit.star);
                  Use.Ids.Add(Unit.id);
                  if (!Seen.Contains(Unit.definition)) {
                    ++Use.Rounds;
                    Seen.Add(Unit.definition);
                  }
                }
            DeployedSeat->SetArrayField("units", Units);
            DeployedSeats.Add(J(DeployedSeat));
          }
          Deployment->SetArrayField("seats", DeployedSeats);
          Deployments.Add(J(Deployment));
        }
        if (Steps % 20 == 0) {
          ++InvariantChecks;
          if (!(Error = M.InvariantError()).empty())
            break;
        }
      }
      if (Error.empty()) {
        ++InvariantChecks;
        Error = M.InvariantError();
      }
      if (M.CurrentPhase() != wc::Phase::Finished && Error.empty())
        Error = "match did not finish";
      Trial->SetNumberField("steps", Steps);
      Trial->SetNumberField("invariant_checks", InvariantChecks);
      Trial->SetNumberField("phase", int(M.CurrentPhase()));
      Trial->SetBoolField("capped", M.Capped());
      Trial->SetArrayField("combat_lock_deployments", Deployments);
      int Fights = 0, Timeouts = 0, Ghosts = 0, Rejects = 0, Unresolved = 0;
      TArray<Val> Rejections;
      for (const auto &Decision : M.BotLog())
        if (!Decision.reply.accepted) {
          ++Rejects;
          auto Rejection = NewObj();
          Rejection->SetNumberField("round", Decision.round);
          Rejection->SetNumberField("seat", Decision.seat);
          Rejection->SetStringField("action", Str(Decision.action));
          Rejection->SetStringField("reason", Str(Decision.reply.reason));
          Rejections.Add(J(Rejection));
        }
      for (const auto &Encounter : M.Encounters())
        if (!Encounter.combat.Result().complete)
          ++Unresolved;
      Trial->SetNumberField("commands", int(M.BotLog().size()));
      Trial->SetNumberField("command_rejects", Rejects);
      Trial->SetArrayField("rejected_commands", Rejections);
      Trial->SetNumberField("unresolved_encounters", Unresolved);
      if (Error.empty() && Rejects > 0)
        Error = "bot command rejected";
      if (Error.empty() && Unresolved > 0)
        Error = "unresolved encounter at end of regression";
      TArray<Val> Rounds;
      for (const auto &R : M.Records()) {
        auto RJ = NewObj();
        RJ->SetNumberField("round", R.round);
        RJ->SetStringField("settlement_id", LexToString(R.settlementId));
        RJ->SetStringField("pre_hash", LexToString(R.preHash));
        RJ->SetStringField("post_hash", LexToString(R.postHash));
        TArray<Val> Outcomes;
        for (size_t I = 0; I < R.results.size(); ++I) {
          auto E = Pair(R.pairs[I]);
          E->SetNumberField("winner", R.results[I].winner);
          E->SetBoolField("timeout", R.results[I].timeout);
          E->SetBoolField("complete", R.results[I].complete);
          E->SetNumberField("ticks", R.results[I].ticks);
          E->SetNumberField("simulated_ms",
                            R.results[I].ticks * Catalog.rules.tickMs);
          E->SetNumberField("survivors_a", R.results[I].survivors[0]);
          E->SetNumberField("survivors_b", R.results[I].survivors[1]);
          Outcomes.Add(J(E));
          ++Fights;
          if (R.results[I].timeout)
            ++Timeouts;
          if (R.pairs[I].ghost)
            ++Ghosts;
        }
        RJ->SetArrayField("encounters", Outcomes);
        TArray<Val> SettledSeats;
        for (int Seat = 0; Seat < Catalog.rules.seatCount; ++Seat) {
          auto State = NewObj();
          State->SetNumberField("seat", Seat);
          State->SetNumberField("health", R.health[Seat]);
          State->SetNumberField("gold", R.gold[Seat]);
          State->SetNumberField("damage", R.damage[Seat]);
          State->SetNumberField("wins", R.wins[Seat]);
          State->SetNumberField("placement", R.placement[Seat]);
          SettledSeats.Add(J(State));
        }
        RJ->SetArrayField("seats", SettledSeats);
        Rounds.Add(J(RJ));
      }
      Trial->SetArrayField("rounds", Rounds);
      Trial->SetNumberField("fights", Fights);
      Trial->SetNumberField("timeouts", Timeouts);
      Trial->SetNumberField("ghosts", Ghosts);
      Trial->SetNumberField("simulated_ms", M.ElapsedMs());
      Trial->SetStringField("error", Str(Error));
      Trial->SetBoolField("pass", Error.empty());
      if (!Error.empty())
        ++Failures;
      TArray<Val> Places;
      TArray<Val> HeroUse;
      for (const auto &S : M.Seats()) {
        auto P = NewObj();
        P->SetNumberField("seat", S.id);
        P->SetNumberField("placement", S.placement);
        P->SetNumberField("health", S.health);
        Places.Add(J(P));
        for (int Definition = 0; Definition < int(Catalog.units.size());
             ++Definition) {
          const auto &Use = Uses[S.id][Definition];
          auto Item = NewObj();
          Item->SetNumberField("seat", S.id);
          Item->SetStringField("unit_id", Str(Catalog.units[Definition].id));
          Item->SetNumberField("final_placement", S.placement);
          Item->SetNumberField("deployed_unit_rounds", Use.UnitRounds);
          Item->SetNumberField("rounds_deployed", Use.Rounds);
          Item->SetNumberField("distinct_owned_instances", Use.Ids.Num());
          Item->SetNumberField("maximum_deployed_star", Use.MaxStar);
          HeroUse.Add(J(Item));
        }
      }
      Trial->SetArrayField("placements", Places);
      Trial->SetArrayField("hero_use_by_seat", HeroUse);
      Trial->SetStringField(
          "hero_use_boundary",
          TEXT(
              "Living seat deployments observed once at each real combat lock. "
              "Unit-rounds include duplicate copies; rounds count a hero once "
              "per seat; ghosts do not add ownership. These are usage and "
              "placement associations, not causal hero strength estimates."));
      UE_LOG(
          LogTemp, Display,
          TEXT("WC_REGRESSION seed=%d status=%s fights=%d rounds=%d error=%s"),
          Seed, Error.empty() ? TEXT("PASS") : TEXT("FAIL"), Fights, M.Round(),
          *Str(Error));
    } catch (const std::exception &E) {
      ++Failures;
      Trial->SetBoolField("pass", false);
      Trial->SetStringField("error", Str(E.what()));
    }
    Trial->SetNumberField("wall_seconds", FPlatformTime::Seconds() - Start);
    Trial->SetStringField("end_utc", FDateTime::UtcNow().ToIso8601());
    Trials.Add(J(Trial));
    Report->SetArrayField("trials", Trials);
    Report->SetNumberField("attempted", Trials.Num());
    Report->SetNumberField("failed", Failures);
    SaveReport();
  }
  Report->SetBoolField("complete", Trials.Num() == Count);
  Report->SetBoolField("evidence_write_failed", WriteFailed);
  Report->SetStringField("end_utc", FDateTime::UtcNow().ToIso8601());
  Report->SetNumberField("batch_wall_seconds",
                         FPlatformTime::Seconds() - BatchStart);
  SaveReport();
  UE_LOG(LogTemp, Display,
         TEXT("WC_REGRESSION_DONE attempted=%d failed=%d path=%s"), Count,
         Failures, *Directory);
  FPlatformMisc::RequestExitWithStatus(false, WriteFailed ? 2
                                              : Failures  ? 1
                                                          : 0);
}

AWCMatchController::AWCMatchController() {
  PrimaryActorTick.bCanEverTick = true;
  bShowMouseCursor = true;
  bEnableClickEvents = true;
}
void AWCMatchController::BeginPlay() {
  Super::BeginPlay();
  if (!IsLocalController())
    return;
  if (auto *Session = GetGameInstance<UWCNetworkSession>())
    if (Session->RouteStartup(this))
      return;
  bShowMouseCursor = true;
  FInputModeGameAndUI Mode;
  Mode.SetHideCursorDuringCapture(false);
  SetInputMode(Mode);
  GConfig->GetString(TEXT("WonderChess"), TEXT("Language"), Language,
                     GGameUserSettingsIni);
  GConfig->GetFloat(TEXT("WonderChess"), TEXT("Master"), MasterVolume,
                    GGameUserSettingsIni);
  GConfig->GetFloat(TEXT("WonderChess"), TEXT("Music"), MusicVolume,
                    GGameUserSettingsIni);
  GConfig->GetFloat(TEXT("WonderChess"), TEXT("Effects"), EffectsVolume,
                    GGameUserSettingsIni);
  GConfig->GetBool(TEXT("WonderChess"), TEXT("ReducedMotion"), bReducedMotion,
                   GGameUserSettingsIni);
  Presenter = GetWorld()->SpawnActor<AWCBoardPresenter>();
  Presenter->Controller = this;
  Presenter->Initialize();

}
void AWCMatchController::SetupInputComponent() {
  Super::SetupInputComponent();
  InputComponent->BindKey(EKeys::Escape, IE_Pressed, this,
                          &AWCMatchController::Cancel);
  InputComponent->BindKey(EKeys::RightMouseButton, IE_Pressed, this,
                          &AWCMatchController::Cancel);
  InputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this,
                          &AWCMatchController::Ready);
  InputComponent->BindKey(EKeys::Tab, IE_Pressed, this,
                          &AWCMatchController::NextFocus);
  InputComponent->BindKey(EKeys::Enter, IE_Pressed, this,
                          &AWCMatchController::UseFocus);
  InputComponent->BindKey(EKeys::Left, IE_Pressed, this,
                          &AWCMatchController::LowerFocusedVolume);
  InputComponent->BindKey(EKeys::Right, IE_Pressed, this,
                          &AWCMatchController::RaiseFocusedVolume);
  InputComponent->BindKey(EKeys::F9, IE_Pressed, this,
                          &AWCMatchController::CaptureScreenshot);
}
void AWCMatchController::CaptureScreenshot() {
  FString Directory = FPaths::ScreenShotDir();
  FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), Directory);
  IFileManager::Get().MakeDirectory(*Directory, true);
  FScreenshotRequest::RequestScreenshot(
      Directory / FString::Printf(TEXT("manual-%lld.png"),
                                  FDateTime::UtcNow().GetTicks()),
      true, false);
}
void AWCMatchController::NextFocus() {
  if (auto *H = Cast<AWCMatchHUD>(GetHUD()))
    H->CycleFocus();
}
void AWCMatchController::UseFocus() {
  if (auto *H = Cast<AWCMatchHUD>(GetHUD()))
    H->ActivateFocus();
}
void AWCMatchController::LowerFocusedVolume() {
  if (auto *H = Cast<AWCMatchHUD>(GetHUD()))
    H->AdjustFocusedVolume(-.1f);
}
void AWCMatchController::RaiseFocusedVolume() {
  if (auto *H = Cast<AWCMatchHUD>(GetHUD()))
    H->AdjustFocusedVolume(.1f);
}

void AWCMatchController::Cancel() {
  if (auto* H = Cast<AWCMatchHUD>(GetHUD()); H && H->BackFromFrontEnd()) return;
  if (SelectedUnit)
    SelectedUnit = 0;
  else
    bOptions = !bOptions;
}
void AWCMatchController::Ready() {
  if (bOptions || !Public.IsValid() ||
      int(Public->GetNumberField(TEXT("phase"))) !=
          int(wc::Phase::Preparation) ||
      !Private.IsValid() || !Private->HasField(TEXT("ready")) ||
      Private->GetBoolField(TEXT("ready")))
    return;
  if (auto *Session = GetGameInstance<UWCNetworkSession>();
      Session && Session->bMatchAborted)
    return;
  const auto &Seats = Public->GetArrayField(TEXT("seats"));
  if (!Seats.IsValidIndex(AssignedSeat) ||
      Seats[AssignedSeat]->AsObject()->GetNumberField(TEXT("health")) <= 0)
    return;
  Intent(wc::CommandType::Ready);
}
void AWCMatchController::ClientRejectSession_Implementation(
    const FString &Reason) {
  if (auto *Session = GetGameInstance<UWCNetworkSession>()) {
    Session->bMatchAborted = true;
    Session->LastNetworkError = Reason;
  }
  ClientTravel(TEXT("/Game/WonderChess/Maps/L_WC_Menu"), TRAVEL_Absolute);
}
void AWCMatchController::ClientPrivateState_Implementation(
    const FString &Json) {
  TMap<int64, int> PreviousStars;
  if (Private.IsValid() && Private->HasField(TEXT("units")))
    for (const auto &V : Private->GetArrayField(TEXT("units"))) {
      auto U = V->AsObject();
      int64 UnitId = int64(U->GetNumberField(TEXT("id")));
      PreviousStars.Add(UnitId, int(U->GetNumberField(TEXT("star"))));
    }
  PrivateJson = Json;
  Private = Decode(Json);
  if (Private.IsValid()) {
    if (Private->HasField(TEXT("units")))
      for (const auto &V : Private->GetArrayField(TEXT("units"))) {
        auto U = V->AsObject();
        int Star = int(U->GetNumberField(TEXT("star")));
        int64 UnitId = int64(U->GetNumberField(TEXT("id")));
        if (Star > 1 && PreviousStars.Contains(UnitId) &&
            Star > PreviousStars[UnitId]) {
          Sound(TEXT("merge"));
          break;
        }
      }
    const int PreviousSeat = AssignedSeat;
    AssignedSeat = int(Private->GetNumberField(TEXT("seat")));
    if (PreviousSeat != AssignedSeat)
      ObservedSeat = FMath::Max(0, AssignedSeat);
    if (Private->HasField(TEXT("revision")) && bCommandPending) {
      int64 Revision = int64(Private->GetNumberField(TEXT("revision")));
      int64 Sequence = int64(Private->GetNumberField(TEXT("sequence")));
      if (Revision > PendingRevision && Sequence >= PendingSequence)
        bCommandPending = false;
    }
  }
}
void AWCMatchController::ClientReply_Implementation(bool Accepted,
                                                    const FString &Reason) {
  WCRecordVerificationReply(this, Accepted, Reason);
  Message = Reason;
  MessageTime = FPlatformTime::Seconds();
  UE_LOG(LogTemp, Display,
         TEXT("WC_COMMAND_REPLY seat=%d accepted=%d reason=%s"), AssignedSeat,
         Accepted, *Reason);
  if (!Accepted) {
    bCommandPending = false;
    Sound(TEXT("draw"));
  } else {
    static const TCHAR *Names[] = {
        TEXT("buy"), TEXT("sell"),     TEXT("reroll"), TEXT("ready"),
        TEXT("buy"), TEXT("movement"), TEXT("ready")};
    Sound(Names[int(PendingType)]);
  }
}
void AWCMatchController::ServerStart_Implementation(int32 Humans, int32 Seed) {
  if (auto *M = GetWorld()->GetAuthGameMode<AWCMatchMode>())
    M->RequestEntry(this, Humans, Seed);
}
void AWCMatchController::ServerCatalogReady_Implementation(const FString& Schema, const FString& Digest, int32 Protocol) {
  auto* M = GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (!M || !M->Controllers.Contains(this)) return;
  if (Protocol != 4 || Schema != Str(M->Catalog.schemaVersion) || Digest != Str(M->Catalog.contentDigest)) {
    bCatalogReady = false;
    ClientRejectSession(TEXT("Game data or protocol differs from the host. Use the same Wonder Chess package."));
    return;
  }
  bCatalogReady = true;
  if (M->bEntryPending && M->RequestedHumans <= 1) bEntryReady = true;
  M->Publish();
}
void AWCMatchController::ServerEntryReady_Implementation(bool bSkip) {
  auto* M = GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (!M || !M->bEntryPending || !bCatalogReady || !M->Controllers.Contains(this)) return;
  bEntryReady = true; bEntrySkip |= bSkip; M->Publish();
}
void AWCMatchController::ServerCancelEntry_Implementation() {
  auto* M = GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (M && M->bEntryPending && M->Controllers.Contains(this)) M->CancelEntry(TEXT("Session preparation cancelled."));
}
void AWCMatchController::ServerPractice_Implementation() {
  auto *M = GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (!M || GetNetMode() != NM_Standalone || AssignedSeat != 0 ||
      !M->LoadError.IsEmpty())
    return;
  int Ada = -1, Mira = -1;
  for (int I = 0; I < int(M->Catalog.units.size()); ++I) {
    if (M->Catalog.units[I].id == "wc_u_human_guardian")
      Ada = I;
    if (M->Catalog.units[I].id == "wc_u_human_priest")
      Mira = I;
  }
  for (int Seed = 1; Seed <= 10000; ++Seed) {
    wc::Match Fixture(M->Catalog, Seed, 1);
    int Copies = 0, Partners = 0;
    for (int Offer : Fixture.Seats()[0].shop) {
      Copies += Offer == Ada;
      Partners += Offer == Mira;
    }
    if (Copies >= 3 && Partners) {
      M->StartTournament(this, 1, Seed);
      M->bPractice = true;
      M->Publish();
      UE_LOG(LogTemp, Display,
             TEXT("WC_GUIDED_PRACTICE fixed_seed=%d normal_rules=true"), Seed);
      return;
    }
  }
  ClientReply(false,
              TEXT("The guided practice fixture could not be prepared."));
}
void AWCMatchController::ServerIntent_Implementation(int32 Type, int64 Request,
                                                     int64 Sequence,
                                                     int64 Revision, int64 Unit,
                                                     int32 Slot, bool ToBoard,
                                                     int32 Column, int32 Row) {
  auto *M = GetWorld()->GetAuthGameMode<AWCMatchMode>();
  if (!M || !M->Match)
    return;
  if (AssignedSeat < 0 || AssignedSeat >= int(M->Match->Seats().size()) ||
      !M->Match->Seats()[AssignedSeat].human) {
    ClientReply(false, TEXT("This controller has no active human seat."));
    return;
  }
  if (Type < 0 || Type > int(wc::CommandType::Ready) || Request <= 0 ||
      Sequence < 0 || Revision < 0 || Unit < 0) {
    ClientReply(false, TEXT("Invalid command payload."));
    return;
  }
  wc::Command C;
  C.type = wc::CommandType(Type);
  C.seat = AssignedSeat;
  C.requestId = Request;
  C.sequence = Sequence;
  C.revision = Revision;
  C.unit = Unit;
  C.slot = Slot;
  C.toBoard = ToBoard;
  C.cell = {Column, Row};
  const auto Reply = M->Match->Submit(AssignedSeat, C);
  ClientReply(Reply.accepted, Str(Reply.reason));
  M->Publish();
}
void AWCMatchController::Intent(wc::CommandType Type, int64 Unit, int32 Slot,
                                bool ToBoard, int32 Column, int32 Row) {
  if (!Private.IsValid() || !Private->HasField(TEXT("revision")))
    return;
  if (IntentQueue.Num() >= 8) {
    Message = TEXT("Please wait for queued commands.");
    MessageTime = FPlatformTime::Seconds();
    return;
  }
  int Expected = -1;
  if (Type == wc::CommandType::Buy) {
    const auto &Shop = Private->GetArrayField(TEXT("shop"));
    if (!Shop.IsValidIndex(Slot))
      return;
    Expected = int(Shop[Slot]->AsNumber());
  }
  IntentQueue.Add({Type, Unit, Slot, ToBoard, Column, Row, Expected});
  SendNextIntent();
}
void AWCMatchController::SendNextIntent() {
  if (bCommandPending || IntentQueue.IsEmpty() || !Private.IsValid() ||
      !Private->HasField(TEXT("revision")))
    return;
  auto C = IntentQueue[0];
  IntentQueue.RemoveAt(0);
  if (C.Type == wc::CommandType::Buy) {
    const auto &Shop = Private->GetArrayField(TEXT("shop"));
    if (!Shop.IsValidIndex(C.Slot) ||
        int(Shop[C.Slot]->AsNumber()) != C.ExpectedDefinition) {
      Message = TEXT("That offer changed. Select a current shop card.");
      MessageTime = FPlatformTime::Seconds();
      return;
    }
  }
  PendingSequence = int64(Private->GetNumberField(TEXT("sequence"))) + 1;
  PendingRevision = int64(Private->GetNumberField(TEXT("revision")));
  PendingType = C.Type;
  bCommandPending = true;
  ServerIntent(int(C.Type), RequestId++, PendingSequence, PendingRevision,
               C.Unit, C.Slot, C.ToBoard, C.Column, C.Row);
}
void AWCMatchController::RefreshView() {
  if (auto *S = GetWorld()->GetGameState<AWCMatchState>())
    if (S->PublicJson != LastPublicJson) {
      const double OldNamespace =
          Public.IsValid() ? Public->GetNumberField(TEXT("matchNamespace")) : 0;
      LastPublicJson = S->PublicJson;
      Public = Decode(LastPublicJson);
      if (Public.IsValid() &&
          Public->GetNumberField(TEXT("matchNamespace")) != OldNamespace) {
        ObservedSeat = FMath::Max(0, AssignedSeat);
        SelectedUnit = 0;
        InspectedDefinition = -1;
        InspectedUnitId = 0;
        bInspectedCombat = false;
        bRecap = false;
        LastCaptainHealth = -1;
        if (Music)
          Music->Stop();
        NextMusic = 0;
        IntentQueue.Reset();
        bCommandPending = false;
      }
      if (Public.IsValid()) {
        int Phase = int(Public->GetNumberField(TEXT("phase")));
        if (Phase != LastPhase) {
          SelectedUnit = 0;
          IntentQueue.Reset();
          bCommandPending = false;
          if (Phase >= 0) {
            const auto &Seats = Public->GetArrayField(TEXT("seats"));
            int Place =
                Seats.IsValidIndex(AssignedSeat)
                    ? int(Seats[AssignedSeat]->AsObject()->GetNumberField(
                          TEXT("place")))
                    : 0;
            Sound(Phase == int(wc::Phase::Finished)
                      ? (Place == 1 ? TEXT("victory") : TEXT("defeat"))
                      : TEXT("phase"));
          }
          LastPhase = Phase;
        }
        const auto &Seats = Public->GetArrayField(TEXT("seats"));
        if (Seats.IsValidIndex(AssignedSeat)) {
          int Health = int(
              Seats[AssignedSeat]->AsObject()->GetNumberField(TEXT("health")));
          if (LastCaptainHealth > Health)
            Sound(Health <= 0 ? TEXT("defeat") : TEXT("health_loss"));
          LastCaptainHealth = Health;
        }
      }
    }
}
void AWCMatchController::Tick(float Delta) {
  Super::Tick(Delta);
  if (!IsLocalController())
    return;
  RefreshView();
  if (!bSentCatalogReady && Presenter && !Presenter->Definitions.units.empty() && Public.IsValid() && Public->HasField(TEXT("contentDigest")) && !Public->GetStringField(TEXT("contentDigest")).IsEmpty()) {
    bSentCatalogReady = true;
    ServerCatalogReady(Str(Presenter->Definitions.schemaVersion), Str(Presenter->Definitions.contentDigest), 4);
  }
  SendNextIntent();
  if (Public.IsValid() && Public->HasField(TEXT("entryState")) &&
      !Public->GetStringField(TEXT("entryState")).IsEmpty() &&
      FParse::Param(FCommandLine::Get(), TEXT("WCExercise")))
    ServerEntryReady(false);
  WCTickVerification(this, Delta);
  if (FPlatformTime::Seconds() > NextMusic &&
      (!IsValid(Music) || !Music->IsPlaying())) {
    NextMusic = FPlatformTime::Seconds() + 24;
    if (auto *S = LoadObject<USoundWave>(
            nullptr,
            TEXT("/Game/WonderChess/Audio/S_WC_courtyard.S_WC_courtyard"))) {
      S->bLooping = true;
      Music =
          UGameplayStatics::SpawnSound2D(this, S, MasterVolume * MusicVolume);
    }
  }
}
void AWCMatchController::Sound(const FString &Name) {
  const double Now = FPlatformTime::Seconds();
  if (LastSoundTimes.Contains(Name) && Now - LastSoundTimes[Name] < .08)
    return;
  LastSoundTimes.Add(Name, Now);
  if (!EffectsConcurrency) {
    EffectsConcurrency = NewObject<USoundConcurrency>(this);
    EffectsConcurrency->Concurrency.MaxCount = 12;
    EffectsConcurrency->Concurrency.ResolutionRule =
        EMaxConcurrentResolutionRule::StopOldest;
    EffectsConcurrency->Concurrency.VoiceStealReleaseTime = .025f;
  }
  const FString Path =
      TEXT("/Game/WonderChess/Audio/S_WC_") + Name + TEXT(".S_WC_") + Name;
  if (auto *S = LoadObject<USoundBase>(nullptr, *Path))
    UGameplayStatics::PlaySound2D(this, S, MasterVolume * EffectsVolume, 1, 0,
                                  EffectsConcurrency, this);
}
void AWCMatchController::SaveOptions() {
  GConfig->SetString(TEXT("WonderChess"), TEXT("Language"), *Language,
                     GGameUserSettingsIni);
  GConfig->SetFloat(TEXT("WonderChess"), TEXT("Master"), MasterVolume,
                    GGameUserSettingsIni);
  GConfig->SetFloat(TEXT("WonderChess"), TEXT("Music"), MusicVolume,
                    GGameUserSettingsIni);
  GConfig->SetFloat(TEXT("WonderChess"), TEXT("Effects"), EffectsVolume,
                    GGameUserSettingsIni);
  GConfig->SetBool(TEXT("WonderChess"), TEXT("ReducedMotion"), bReducedMotion,
                   GGameUserSettingsIni);
  GConfig->Flush(false, GGameUserSettingsIni);
  if (Music)
    Music->SetVolumeMultiplier(MasterVolume * MusicVolume);
}
