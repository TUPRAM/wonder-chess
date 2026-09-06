#include "WCBoardPresenter.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "WCMatchRuntime.h"

AWCBoardPresenter::AWCBoardPresenter() { PrimaryActorTick.bCanEverTick = true; }
FVector AWCBoardPresenter::Position(int Column, int Row) const {
  return FVector((3.5 - Row) * 200, (3.5 - Column) * 200, 0);
}
UMaterialInstanceDynamic *AWCBoardPresenter::Material(FLinearColor Color) {
  const uint32 Key = Color.ToFColor(false).ToPackedRGBA();
  if (Materials.Contains(Key))
    return Materials[Key];
  auto *Base = LoadObject<UMaterialInterface>(
      nullptr, TEXT("/Game/WonderChess/Materials/M_WC_Surface.M_WC_Surface"));
  if (!Base)
    Base = LoadObject<UMaterialInterface>(
        nullptr,
        TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
  auto *M = UMaterialInstanceDynamic::Create(Base, this);
  M->SetVectorParameterValue(TEXT("Color"), Color);
  Materials.Add(Key, M);
  return M;
}
void AWCBoardPresenter::Prop(const FString &Asset, FVector Location,
                             FVector Scale, FLinearColor Color,
                             FRotator Rotation) {
  auto *A = GetWorld()->SpawnActor<AStaticMeshActor>(Location, Rotation);
  auto *C = A->GetStaticMeshComponent();
  C->SetMobility(EComponentMobility::Movable);
  auto *Mesh = LoadObject<UStaticMesh>(nullptr, *Asset);
  if (!Mesh)
    Mesh =
        LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
  C->SetStaticMesh(Mesh);
  C->SetMaterial(0, Material(Color));
  C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  A->SetActorScale3D(Scale);
}
void AWCBoardPresenter::Initialize() {
  FString Error;
  if (!wc::LoadCatalog(Definitions, Error, &Metadata)) {
    AssetStatus = Error;
    return;
  }
  for (const auto &Definition : Definitions.units) {
    FString Id = UTF8_TO_TCHAR(Definition.id.c_str());
    TArray<FString> Names = {TEXT("SK_") + Id,
                             TEXT("T_") + Id + TEXT("_Portrait")};
    for (const TCHAR *Clip :
         {TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Active"),
          TEXT("Hit"), TEXT("Defeat"), TEXT("Victory")})
      Names.Add(TEXT("AN_") + Id + TEXT("_") + Clip);
    for (const FString &Name : Names)
      if (auto *Asset = LoadObject<UObject>(
              nullptr, *(TEXT("/Game/WonderChess/Heroes/") + Id + TEXT("/") +
                         Name + TEXT(".") + Name)))
        ResidentAssets.Add(Asset);
  }
  for (const TCHAR *Name : {TEXT("SM_WC_ArrowGlyph"), TEXT("SM_WC_BoltGlyph")})
    if (auto *Asset = LoadObject<UStaticMesh>(
            nullptr, *(FString(TEXT("/Game/WonderChess/Effects/")) + Name +
                       TEXT(".") + Name)))
      ResidentAssets.Add(Asset);
  BuildArena();
  auto *Cam = GetWorld()->SpawnActor<ACameraActor>(FVector(2450, 0, 2800),
                                                   FRotator(-50, 180, 0));
  Cam->GetCameraComponent()->SetProjectionMode(
      ECameraProjectionMode::Orthographic);
  Cam->GetCameraComponent()->SetOrthoWidth(4300);
  Cam->GetCameraComponent()->bConstrainAspectRatio = false;
  Cam->GetCameraComponent()->bOverrideAspectRatioAxisConstraint = true;
  Cam->GetCameraComponent()->AspectRatioAxisConstraint =
      AspectRatio_MaintainXFOV;
  Camera = Cam;
  Controller->SetViewTarget(Cam);
  if (FParse::Param(FCommandLine::Get(), TEXT("WCArtReview"))) {
    Cam->SetActorLocation(FVector(2400, 0, 3100));
    Cam->SetActorRotation(FRotator(-52, 180, 0));
    Cam->GetCameraComponent()->SetOrthoWidth(2300);
  }
}
void AWCBoardPresenter::BuildArena() {
  auto *Sun = GetWorld()->SpawnActor<ADirectionalLight>(FVector(0, 0, 1000),
                                                        FRotator(-55, 148, 0));
  Sun->GetLightComponent()->SetIntensity(2.2);
  Cast<UDirectionalLightComponent>(Sun->GetLightComponent())
      ->SetForwardShadingPriority(1);
  Sun->GetLightComponent()->SetLightColor(FLinearColor(1, .92, .79));
  auto *Fill = GetWorld()->SpawnActor<ADirectionalLight>(FVector(0, 0, 1000),
                                                         FRotator(-35, -25, 0));
  Fill->GetLightComponent()->SetIntensity(.9);
  Fill->GetLightComponent()->SetLightColor(FLinearColor(.62, .77, 1));
  Fill->GetLightComponent()->SetCastShadows(false);
  auto *Sky = GetWorld()->SpawnActor<ASkyLight>();
  Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
  Sky->GetLightComponent()->SetIntensity(1.2);
  Sky->GetLightComponent()->SetLowerHemisphereColor(
      FLinearColor(.19, .26, .35));
  Prop(TEXT("/Engine/BasicShapes/Plane.Plane"), FVector(0, 0, -65),
       FVector(200, 200, 1), FLinearColor(.035, .07, .063));
  for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
    if (It->ActorHasTag(TEXT("WCArena")))
      return;
  const FString Cube = TEXT("/Engine/BasicShapes/Cube.Cube");
  Prop(Cube, FVector(0, 0, -100), FVector(23, 23, 1.3),
       FLinearColor(.12, .18, .17));
  Prop(Cube, FVector(0, 0, -28), FVector(17.1, 17.1, .5),
       FLinearColor(.53, .41, .23));
  for (int R = 0; R < 8; ++R)
    for (int C = 0; C < 8; ++C) {
      FLinearColor Color = (R + C) % 2 ? FLinearColor(.57, .52, .36)
                                       : FLinearColor(.72, .65, .46);
      Prop(Cube, Position(C, R) - FVector(0, 0, 18), FVector(1.97, 1.97, .20),
           Color);
    }
  for (int Side : {-1, 1}) {
    Prop(Cube, FVector(0, Side * 1040, 30), FVector(22, .65, .9),
         FLinearColor(.43, .43, .33));
    Prop(Cube, FVector(1040, 0, 30), FVector(.65, 22, .9),
         FLinearColor(.43, .43, .33));
    for (int X : {-900, -300, 300, 900}) {
      Prop(Cube, FVector(X, Side * 1040, 118), FVector(.9, .9, .32),
           FLinearColor(.65, .57, .34));
      Prop(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),
           FVector(X, Side * 1040, 190), FVector(.25, .25, 1.15),
           FLinearColor(.22, .16, .09));
      Prop(TEXT("/Engine/BasicShapes/Sphere.Sphere"),
           FVector(X, Side * 1040, 266), FVector(.44, .44, .56),
           FLinearColor(1, .59, .10));
    }
    for (int X : {-1100, 900}) {
      Prop(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),
           FVector(X, Side * 1280, 390), FVector(.12, .12, 7),
           FLinearColor(.39, .23, .1));
      Prop(Cube, FVector(X, Side * 1195, 570), FVector(.04, 1.6, 2.5),
           Side < 0 ? FLinearColor(.08, .32, .46) : FLinearColor(.5, .19, .10));
    }
  }
}
void AWCBoardPresenter::Tick(float Delta) {
  Super::Tick(Delta);
  Refresh(Delta);
  UpdateEffects(Delta);
}
void AWCBoardPresenter::Refresh(float Delta) {
  if (!Controller || !Controller->Public.IsValid() || Definitions.units.empty())
    return;
  auto Public = Controller->Public;
  int Phase = int(Public->GetNumberField(TEXT("phase")));
  int Observed = Controller->ObservedSeat;
  if (Phase == int(wc::Phase::Combat) || Phase == int(wc::Phase::Settlement)) {
    const auto &Encounters = Public->GetArrayField(TEXT("encounters"));
    const bool HasEncounter =
        Encounters.ContainsByPredicate([Observed](const auto &E) {
          const auto Encounter = E->AsObject();
          return int(Encounter->GetNumberField(TEXT("a"))) == Observed ||
                 (!Encounter->GetBoolField(TEXT("ghost")) &&
                  int(Encounter->GetNumberField(TEXT("b"))) == Observed);
        });
    if (!HasEncounter && Encounters.Num()) {
      Observed = int(Encounters[0]->AsObject()->GetNumberField(TEXT("a")));
      Controller->ObservedSeat = Observed;
      Controller->SelectedUnit = 0;
      Controller->InspectedUnitId = 0;
      Controller->InspectedDefinition = -1;
      Controller->bInspectedCombat = false;
    }
  }
  VisibleUnits.Reset();
  TArray<TSharedPtr<FJsonObject>> NewEvents;
  int WinningSide = -2;
  int Round = int(Public->GetNumberField(TEXT("round")));
  const bool Reconstructing = Round != LastRound || Observed != LastObserved;
  if (Reconstructing) {
    for (auto &Effect : Effects)
      if (IsValid(Effect.Actor))
        Effect.Actor->Destroy();
    Effects.Reset();
    Targets.Reset();
    for (auto &State : PreviousStates)
      State.Value = -1;
    for (auto &Action : PreviousActions)
      Action.Value = -1;
    LastObserved = Observed;
  }
  if (Round != LastRound || Phase != LastPhase) {
    if (Round != LastRound)
      bEncounterCompleted = false;
    LastEventTick = -1;
    LastRound = Round;
    LastPhase = Phase;
  }
  const bool Reviewing =
      FParse::Param(FCommandLine::Get(), TEXT("WCArtReview"));
  ReviewAge += Delta;
  const int ReviewStep = FMath::Clamp(int((ReviewAge - 5) / 1.5f), 0, 20);
  if (Phase == int(wc::Phase::Combat) || Phase == int(wc::Phase::Settlement)) {
    const auto &Encounters = Public->GetArrayField(TEXT("encounters"));
    int Index = 0;
    bool Found = false;
    for (const auto &E : Encounters) {
      auto P = E->AsObject();
      if (int(P->GetNumberField(TEXT("a"))) == Observed ||
          (!P->GetBoolField(TEXT("ghost")) &&
           int(P->GetNumberField(TEXT("b"))) == Observed)) {
        VisibleUnits = P->GetArrayField(TEXT("units"));
        Found = true;
        break;
      }
      ++Index;
    }
    if (!Found && Encounters.Num()) {
      Index = 0;
      VisibleUnits = Encounters[0]->AsObject()->GetArrayField(TEXT("units"));
    }
    if (Index != LastEncounter) {
      bEncounterCompleted = false;
      LastEncounter = Index;
      LastEventTick = -1;
    }
    if (Encounters.IsValidIndex(Index)) {
      auto P = Encounters[Index]->AsObject();
      if (!Reconstructing && !bEncounterCompleted &&
          P->GetBoolField(TEXT("complete")) &&
          int(P->GetNumberField(TEXT("winner"))) == -1)
        Controller->Sound(TEXT("draw"));
      bEncounterCompleted = P->GetBoolField(TEXT("complete"));
      WinningSide = P->GetBoolField(TEXT("complete"))
                        ? int(P->GetNumberField(TEXT("winner")))
                        : -2;
      const auto &Events = P->GetArrayField(TEXT("events"));
      int Newest = LastEventTick;
      for (const auto &E : Events) {
        auto V = E->AsObject();
        int Tick = int(V->GetNumberField(TEXT("tick")));
        if (Tick > LastEventTick) {
          Newest = FMath::Max(Newest, Tick);
          if (LastEventTick >= 0)
            NewEvents.Add(V);
        }
      }
      LastEventTick = Newest;
    }
  } else if (Phase >= 0) {
    const auto &Seats = Public->GetArrayField(TEXT("seats"));
    if (Seats.IsValidIndex(Observed))
      for (const auto &V :
           Seats[Observed]->AsObject()->GetArrayField(TEXT("units"))) {
        auto O = MakeShared<FJsonObject>(*V->AsObject());
        O->SetNumberField("side", 0);
        O->SetNumberField("state", int(wc::ActionState::Idle));
        O->SetNumberField("action", 0);
        O->SetNumberField("hp", 1);
        O->SetNumberField("maxHp", 1);
        O->SetNumberField("shield", 0);
        O->SetNumberField("stun", 0);
        VisibleUnits.Add(MakeShared<FJsonValueObject>(O));
      }
  } else {
    for (int I = 0; I < FMath::Min(6, int(Definitions.units.size())); ++I) {
      auto O = MakeShared<FJsonObject>();
      O->SetNumberField("id", 90000 + I);
      O->SetNumberField("def", I);
      O->SetNumberField("star", 1);
      O->SetNumberField("side", 0);
      O->SetNumberField("col", I + 1);
      O->SetNumberField("row", 3);
      O->SetNumberField("state", int(wc::ActionState::Idle));
      O->SetNumberField("action", 0);
      O->SetNumberField("hp", 1);
      O->SetNumberField("maxHp", 1);
      O->SetNumberField("shield", 0);
      O->SetNumberField("stun", 0);
      VisibleUnits.Add(MakeShared<FJsonValueObject>(O));
    }
  }
  if (Reviewing) {
    VisibleUnits.Reset();
    for (int I = 0; I < int(Definitions.units.size()); ++I) {
      auto O = MakeShared<FJsonObject>();
      O->SetNumberField("id", 90000 + I);
      O->SetNumberField("def", I);
      O->SetNumberField("star", 1);
      O->SetNumberField("side", 0);
      O->SetNumberField("col", 1 + (I % 4) * 2);
      O->SetNumberField("row", 1 + (I / 4) * 2);
      O->SetNumberField("state", 0);
      O->SetNumberField("action", ReviewStep + 1);
      O->SetNumberField("hp", 1);
      O->SetNumberField("maxHp", 1);
      O->SetNumberField("shield", 0);
      O->SetNumberField("stun", 0);
      VisibleUnits.Add(MakeShared<FJsonValueObject>(O));
    }
  }
  TSet<int64> Alive;
  for (const auto &V : VisibleUnits) {
    auto O = V->AsObject();
    int64 Id = int64(O->GetNumberField(TEXT("id")));
    int Def = int(O->GetNumberField(TEXT("def")));
    if (Def < 0 || Def >= int(Definitions.units.size()))
      continue;
    const FString UnitId = UTF8_TO_TCHAR(Definitions.units[Def].id.c_str());
    const int State = int(O->GetNumberField(TEXT("state")));
    Alive.Add(Id);
    int Side = int(O->GetNumberField(TEXT("side")));
    FVector Target = Position(int(O->GetNumberField(TEXT("col"))),
                              int(O->GetNumberField(TEXT("row"))));
    if (!Heroes.Contains(Id)) {
      auto *Actor =
          GetWorld()->SpawnActor<AActor>(Target, FRotator(0,
                                                          Phase < 0 ? 0
                                                          : Side    ? 0
                                                                    : 180,
                                                          0));
      auto *Root = NewObject<USceneComponent>(Actor);
      Actor->SetRootComponent(Root);
      Root->RegisterComponent();
      const FString Base =
          TEXT("/Game/WonderChess/Heroes/") + UnitId + TEXT("/SK_") + UnitId;
      auto *Mesh =
          LoadObject<USkeletalMesh>(nullptr, *(Base + TEXT(".SK_") + UnitId));
      if (Mesh) {
        auto *C = NewObject<USkeletalMeshComponent>(Actor);
        C->SetupAttachment(Root);
        C->RegisterComponent();
        C->SetSkeletalMesh(Mesh);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
      } else {
        auto *C = NewObject<UStaticMeshComponent>(Actor);
        C->SetupAttachment(Root);
        C->RegisterComponent();
        C->SetStaticMesh(LoadObject<UStaticMesh>(
            nullptr, TEXT("/Engine/BasicShapes/Cone.Cone")));
        C->SetRelativeScale3D(FVector(.6, .6, 1.7));
        C->SetRelativeLocation(FVector(0, 0, 85));
        C->SetMaterial(0, Material(FLinearColor(.45, .48, .51)));
        AssetStatus = TEXT("Internal graybox - hero assets incomplete");
      }
      auto *Disc = NewObject<UStaticMeshComponent>(Actor);
      Disc->SetupAttachment(Root);
      Disc->RegisterComponent();
      Disc->SetStaticMesh(LoadObject<UStaticMesh>(
          nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
      Disc->SetRelativeScale3D(FVector(.92, .92, .025));
      Disc->SetRelativeLocation(FVector(0, 0, 0));
      Disc->SetMaterial(0, Material(Side ? FLinearColor(.72, .22, .12)
                                         : FLinearColor(.06, .52, .67)));
      Disc->SetCollisionEnabled(ECollisionEnabled::NoCollision);
      Actor->SetActorLocation(Target);
      Heroes.Add(Id, Actor);
      PreviousStates.Add(Id, -1);
      PreviousActions.Add(Id, -1);
      auto *Highlight = NewObject<UStaticMeshComponent>(Actor);
      Highlight->SetupAttachment(Root);
      Highlight->RegisterComponent();
      Highlight->SetStaticMesh(LoadObject<UStaticMesh>(
          nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
      Highlight->SetRelativeScale3D(FVector(1.1, 1.1, .012));
      Highlight->SetRelativeLocation(FVector(0, 0, .5));
      Highlight->SetMaterial(0, Material(FLinearColor(1, .75, .17)));
      Highlight->SetCollisionEnabled(ECollisionEnabled::NoCollision);
      Highlight->SetCastShadow(false);
      Highlights.Add(Id, Highlight);
    }
    AActor *Actor = Heroes[Id];
    Targets.Add(Id, Actor->GetActorLocation());
    Actor->SetActorLocation(
        Controller->bReducedMotion
            ? Target
            : FMath::VInterpTo(Actor->GetActorLocation(), Target, Delta, 12));
    if (Highlights.Contains(Id))
      Highlights[Id]->SetVisibility(Id == Controller->SelectedUnit ||
                                    Id == Controller->InspectedUnitId);
    if (O->HasField(TEXT("target"))) {
      int64 TargetId = int64(O->GetNumberField(TEXT("target")));
      if (Heroes.Contains(TargetId)) {
        FVector Direction =
            Heroes[TargetId]->GetActorLocation() - Actor->GetActorLocation();
        Direction.Z = 0;
        if (!Direction.IsNearlyZero())
          Actor->SetActorRotation(FRotator(0, Direction.Rotation().Yaw, 0));
      }
    }
    const bool Victorious =
        WinningSide == Side && O->GetNumberField(TEXT("hp")) > 0;
    int64 Action = int64(O->GetNumberField(TEXT("action"))) +
                   (Victorious ? 1000000000 : 0);
    if (State != PreviousStates[Id] || Action != PreviousActions[Id]) {
      FString Clip = TEXT("Idle");
      bool Loop = true;
      if (State == int(wc::ActionState::Moving) ||
          State == int(wc::ActionState::Seeking)) {
        Clip = TEXT("Move");
        if (!Reconstructing && State == int(wc::ActionState::Moving))
          Controller->Sound(TEXT("movement"));
      }
      const bool Attacking = State == int(wc::ActionState::AttackWindup) ||
                             State == int(wc::ActionState::AttackRecovery);
      const bool Casting = State == int(wc::ActionState::CastWindup) ||
                           State == int(wc::ActionState::CastRecovery);
      if (Attacking) {
        Clip = TEXT("Attack");
        Loop = false;
      }
      if (Casting) {
        Clip = TEXT("Active");
        Loop = false;
      }
      if (!Reviewing && O->HasField(TEXT("releaseTick")) &&
          (State == int(wc::ActionState::AttackRecovery) ||
           State == int(wc::ActionState::CastRecovery))) {
        const auto &Definition = Definitions.units[Def];
        const int TravelMs = Attacking ? Definition.projectileTravelMs
                                       : Definition.ability.travelMs;
        const float ElapsedMs = (O->GetNumberField(TEXT("snapshotTick")) -
                                 O->GetNumberField(TEXT("releaseTick"))) *
                                Definitions.rules.tickMs;
        const float Remaining = (TravelMs - ElapsedMs) / 1000.f;
        const int64 TargetId = int64(O->GetNumberField(TEXT("target")));
        if (Remaining > 0 && Heroes.Contains(TargetId)) {
          if (!Reconstructing && Attacking)
            Controller->Sound(TEXT("ranged_launch"));
          const FVector End =
              Heroes[TargetId]->GetActorLocation() + FVector(0, 0, 110);
          const FVector Start =
              FMath::Lerp(Actor->GetActorLocation() + FVector(0, 0, 120), End,
                          FMath::Clamp(ElapsedMs / TravelMs, 0.f, 1.f));
          const auto DamageType =
              Casting ? Definition.ability.damageType : Definition.damageType;
          SpawnProjectile(
              Start, End, Remaining,
              DamageType == wc::DamageType::Magic  ? FLinearColor(.45, .6, 1)
              : DamageType == wc::DamageType::True ? FLinearColor::White
                                                   : FLinearColor(1, .8, .3),
              Definition.id == "wc_u_elf_ranger");
        }
      }
      if (State == int(wc::ActionState::Stunned)) {
        Clip = TEXT("Hit");
        Loop = false;
      }
      if (State == int(wc::ActionState::Defeated)) {
        Clip = TEXT("Defeat");
        Loop = false;
      }
      if (Victorious) {
        Clip = TEXT("Victory");
        Loop = true;
      }
      if (Reviewing) {
        static const TCHAR *Clips[] = {
            TEXT("Idle"), TEXT("Move"),   TEXT("Attack"), TEXT("Active"),
            TEXT("Hit"),  TEXT("Defeat"), TEXT("Victory")};
        Clip = Clips[ReviewStep / 3];
        Loop = false;
        AssetStatus = FString::Printf(
            TEXT("%s  |  pose %d of 3  |  Unreal skeletal assets"), *Clip,
            ReviewStep % 3 + 1);
      }
      {
        const FString Name = TEXT("AN_") + UnitId + TEXT("_") + Clip;
        const FString Path = TEXT("/Game/WonderChess/Heroes/") + UnitId +
                             TEXT("/") + Name + TEXT(".") + Name;
        if (auto *C = Actor->FindComponentByClass<USkeletalMeshComponent>())
          if (auto *Animation = LoadObject<UAnimSequence>(nullptr, *Path)) {
            C->PlayAnimation(Animation, Loop);
            if (!Reviewing && !Victorious && (Attacking || Casting) &&
                O->HasField(TEXT("snapshotTick"))) {
              const int WindupMs = Casting
                                       ? Definitions.units[Def].ability.castMs
                                       : Definitions.units[Def].attackWindupMs;
              const int WindupTicks =
                  (WindupMs + Definitions.rules.tickMs - 1) /
                  Definitions.rules.tickMs;
              const int StartTick =
                  int(O->GetNumberField(TEXT("releaseTick"))) - WindupTicks;
              const float Elapsed =
                  FMath::Max(0, int(O->GetNumberField(TEXT("snapshotTick"))) -
                                    StartTick) *
                  Definitions.rules.tickMs / 1000.f;
              C->SetPosition(FMath::Min(Elapsed, Animation->GetPlayLength()),
                             false);
            }
          }
      }
      PreviousStates[Id] = State;
      PreviousActions[Id] = Action;
    }
    if (Reviewing)
      if (auto *C = Actor->FindComponentByClass<USkeletalMeshComponent>())
        if (auto *Animation = C->GetSingleNodeInstance()) {
          Animation->SetPlaying(false);
          Animation->SetPosition(Animation->GetLength() *
                                     (ReviewStep % 3 == 0   ? .20f
                                      : ReviewStep % 3 == 1 ? .52f
                                                            : .88f),
                                 false);
        }
  }
  int Emitted = 0;
  for (const auto &V : NewEvents) {
    if (++Emitted > 8)
      break;
    int Kind = int(V->GetNumberField(TEXT("effect")));
    SpawnEffect(Kind, int64(V->GetNumberField(TEXT("source"))),
                int64(V->GetNumberField(TEXT("target"))),
                int(V->GetNumberField(TEXT("radius"))),
                int(V->GetNumberField(TEXT("col"))),
                int(V->GetNumberField(TEXT("row"))));
    if (Emitted <= 3) {
      static const TCHAR *Names[] = {TEXT("melee"),  TEXT("heal"),
                                     TEXT("shield"), TEXT("stun"),
                                     TEXT("dash"),   TEXT("magic_impact")};
      FString Cue = Names[FMath::Clamp(Kind, 0, 5)];
      if (Kind == 0) {
        for (const auto &Visible : VisibleUnits) {
          auto U = Visible->AsObject();
          if (U->GetNumberField(TEXT("id")) ==
              V->GetNumberField(TEXT("source"))) {
            const auto &Definition =
                Definitions.units[int(U->GetNumberField(TEXT("def")))];
            Cue = int(V->GetNumberField(TEXT("damageType"))) ==
                          int(wc::DamageType::Magic)
                      ? TEXT("magic_impact")
                  : Definition.projectileTravelMs > 0 ? TEXT("ranged_impact")
                                                      : TEXT("melee");
            break;
          }
        }
      }
      if (V->HasField(TEXT("basicAttack")) &&
          !V->GetBoolField(TEXT("basicAttack"))) {
        for (const auto &Visible : VisibleUnits) {
          const auto Source = Visible->AsObject();
          if (Source->GetNumberField(TEXT("id")) ==
              V->GetNumberField(TEXT("source"))) {
            Cue =
                FString(UTF8_TO_TCHAR(
                    Definitions.units[int(Source->GetNumberField(TEXT("def")))]
                        .id.c_str())) +
                TEXT("_active");
            break;
          }
        }
      }
      Controller->Sound(Cue);
    }
  }
  TArray<int64> Remove;
  for (const auto &Pair : Heroes)
    if (!Alive.Contains(Pair.Key)) {
      Pair.Value->Destroy();
      Remove.Add(Pair.Key);
    }
  for (int64 Id : Remove) {
    Heroes.Remove(Id);
    PreviousActions.Remove(Id);
    PreviousStates.Remove(Id);
    Highlights.Remove(Id);
    Targets.Remove(Id);
  }
  if (Reviewing && ReviewAge > 6 && ReviewCapture != ReviewStep &&
      FMath::Fmod(ReviewAge - 5, 1.5f) > .65f) {
    ReviewCapture = ReviewStep;
    FString Directory =
        FPaths::ProjectSavedDir() / TEXT("WonderChessEvidence/ArtReview");
    FParse::Value(FCommandLine::Get(), TEXT("WCArtReviewDir="), Directory);
    IFileManager::Get().MakeDirectory(*Directory, true);
    FScreenshotRequest::RequestScreenshot(
        Directory / FString::Printf(TEXT("pose-%02d.png"), ReviewStep), true,
        false);
    UE_LOG(LogTemp, Display,
           TEXT("WC_ART_REVIEW_CAPTURE step=%d heroes=%d label=%s"), ReviewStep,
           Heroes.Num(), *AssetStatus);
  }
}

void AWCBoardPresenter::SpawnEffect(int32 Kind, int64 Source, int64 Target,
                                    int32 Radius, int32 Column, int32 Row) {
  if (Controller->bReducedMotion || !Heroes.Contains(Target) ||
      Effects.Num() >= 48)
    return;
  FVector End = Heroes[Target]->GetActorLocation() + FVector(0, 0, 110);
  auto *A =
      GetWorld()->SpawnActor<AStaticMeshActor>(End, FRotator::ZeroRotator);
  auto *C = A->GetStaticMeshComponent();
  C->SetMobility(EComponentMobility::Movable);
  C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  C->SetCastShadow(false);
  C->SetStaticMesh(LoadObject<UStaticMesh>(
      nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")));
  static const FLinearColor Colors[] = {
      FLinearColor(1, .5, .12),  FLinearColor(.16, 1, .4),
      FLinearColor(1, .84, .23), FLinearColor(.9, .3, 1),
      FLinearColor(.2, .7, 1),   FLinearColor(.55, .4, 1)};
  C->SetMaterial(0, Material(Colors[FMath::Clamp(Kind, 0, 5)]));
  A->SetActorScale3D(Kind == 2 ? FVector(1.2, 1.2, .035)
                               : FVector(.14, .14, .14));
  Effects.Add({A, End, End, 0, .48f, Kind});
  if (Kind == int(wc::Effect::Dash) && Targets.Contains(Source)) {
    const FVector Origin = Targets[Source] + FVector(0, 0, 12);
    const FVector Landing = Position(Column, Row) + FVector(0, 0, 12);
    const FVector Direction = Landing - Origin;
    if (Direction.Size() > 30) {
      auto *Ribbon = GetWorld()->SpawnActor<AStaticMeshActor>(
          (Origin + Landing) / 2, Direction.Rotation());
      auto *Part = Ribbon->GetStaticMeshComponent();
      Part->SetMobility(EComponentMobility::Movable);
      Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
      Part->SetCastShadow(false);
      Part->SetStaticMesh(LoadObject<UStaticMesh>(
          nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
      Part->SetMaterial(0, Material(FLinearColor(.2, .7, 1)));
      Ribbon->SetActorScale3D(FVector(Direction.Size() / 100.f, .12, .02));
      Effects.Add({Ribbon, Ribbon->GetActorLocation(),
                   Ribbon->GetActorLocation(), 0, .3f, 6});
    }
  }
  if (Radius > 0 && Column >= 0 && Row >= 0) {
    FVector Center = Position(Column, Row) + FVector(0, 0, 3);
    for (int Edge = 0; Edge < 4 && Effects.Num() < 48; ++Edge) {
      auto *Line = GetWorld()->SpawnActor<AStaticMeshActor>(
          Center, FRotator::ZeroRotator);
      auto *Part = Line->GetStaticMeshComponent();
      Part->SetMobility(EComponentMobility::Movable);
      Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
      Part->SetCastShadow(false);
      Part->SetStaticMesh(LoadObject<UStaticMesh>(
          nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
      Part->SetMaterial(0, Material(Colors[FMath::Clamp(Kind, 0, 5)]));
      float Half = (Radius + .5f) * 200;
      FVector Point =
          Center + FVector(Edge < 2 ? (Edge ? Half : -Half) : 0,
                           Edge >= 2 ? (Edge == 2 ? Half : -Half) : 0, 0);
      Line->SetActorLocation(Point);
      Line->SetActorScale3D(Edge < 2 ? FVector(.035, Half * .02, .018)
                                     : FVector(Half * .02, .035, .018));
      Effects.Add({Line, Point, Point, 0, .5f, 6});
    }
  }
}
void AWCBoardPresenter::SpawnProjectile(FVector Start, FVector End,
                                        float Duration, FLinearColor Color,
                                        bool Arrow) {
  if (Controller->bReducedMotion || Effects.Num() >= 48)
    return;
  auto *Bolt =
      GetWorld()->SpawnActor<AStaticMeshActor>(Start, (End - Start).Rotation());
  auto *Mesh = Bolt->GetStaticMeshComponent();
  Mesh->SetMobility(EComponentMobility::Movable);
  Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  Mesh->SetCastShadow(false);
  const FString Name =
      Arrow ? TEXT("SM_WC_ArrowGlyph") : TEXT("SM_WC_BoltGlyph");
  Mesh->SetStaticMesh(LoadObject<UStaticMesh>(
      nullptr,
      *(TEXT("/Game/WonderChess/Effects/") + Name + TEXT(".") + Name)));
  Mesh->SetMaterial(0, Material(Color));
  Bolt->SetActorScale3D(FVector(.6));
  Effects.Add({Bolt, Start, End, 0, Duration, 7});
}
void AWCBoardPresenter::UpdateEffects(float Delta) {
  for (int I = Effects.Num() - 1; I >= 0; --I) {
    auto &E = Effects[I];
    E.Age += Delta;
    if (E.Age >= E.Duration) {
      E.Actor->Destroy();
      Effects.RemoveAtSwap(I);
      continue;
    }
    float T = E.Age / E.Duration;
    FVector Location = FMath::Lerp(E.Start, E.End, T);
    if (E.Kind == 1 || E.Kind == 3)
      Location.Z += T * 110;
    E.Actor->SetActorLocation(Location);
    if (E.Kind == 2)
      E.Actor->SetActorScale3D(FVector(1.2 + T * .8, 1.2 + T * .8, .035));
    else if (E.Kind != 6 && E.Start == E.End)
      E.Actor->SetActorScale3D(FVector(.08 + T * .3));
  }
}
