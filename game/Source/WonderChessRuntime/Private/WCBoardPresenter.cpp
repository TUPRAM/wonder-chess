#include "WCBoardPresenter.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
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

namespace {
FString ActionKey(int64 Source, int64 Action) {
  return FString::Printf(TEXT("%lld:%lld"), Source, Action);
}
FLinearColor SkillColor(const FString& Id) {
  static const TMap<FString,FLinearColor> Colors = {
    {TEXT("wc_u_human_guardian"),{1,.72f,.25f}},{TEXT("wc_u_human_priest"),{1,.82f,.42f}},
    {TEXT("wc_u_human_mage"),{1,.30f,.08f}},{TEXT("wc_u_elf_ranger"),{.38f,.88f,.61f}},
    {TEXT("wc_u_elf_priest"),{.16f,.76f,.69f}},{TEXT("wc_u_elf_rogue"),{.26f,.43f,.93f}},
    {TEXT("wc_u_dwarf_guardian"),{.95f,.61f,.19f}},{TEXT("wc_u_dwarf_ranger"),{.94f,.79f,.42f}},
    {TEXT("wc_u_dwarf_warrior"),{1,.83f,.54f}},{TEXT("wc_u_orc_warrior"),{.95f,.53f,.12f}},
    {TEXT("wc_u_orc_mage"),{.25f,.48f,.92f}},{TEXT("wc_u_orc_rogue"),{.45f,.86f,.92f}},
    {TEXT("wc_u_human_warrior"),{1,.93f,.79f}},{TEXT("wc_u_elf_mage"),{.71f,.52f,1}},
    {TEXT("wc_u_dwarf_priest"),{1,.67f,.24f}},{TEXT("wc_u_orc_guardian"),{.70f,.85f,.53f}},
    {TEXT("wc_u_halfling_warrior"),{.61f,.84f,.30f}},{TEXT("wc_u_halfling_ranger"),{.28f,.62f,.99f}},
    {TEXT("wc_u_halfling_rogue"),{1,.81f,.33f}},{TEXT("wc_u_halfling_mage"),{.65f,.85f,1}},
    {TEXT("wc_u_dragonkin_guardian"),{1,.87f,.50f}},{TEXT("wc_u_dragonkin_ranger"),{.22f,.86f,1}},
    {TEXT("wc_u_dragonkin_rogue"),{.89f,.76f,1}},{TEXT("wc_u_dragonkin_priest"),{.86f,.93f,.59f}},
    {TEXT("wc_n_sprout"),{.52f,.73f,.28f}},{TEXT("wc_n_thorn"),{.70f,.65f,.31f}},
    {TEXT("wc_n_wisp"),{.45f,.92f,.83f}},{TEXT("wc_n_stoneback"),{.62f,.73f,.66f}},
    {TEXT("wc_n_prowler"),{.35f,.84f,.85f}},{TEXT("wc_n_sentinel"),{.94f,.72f,.29f}},
    {TEXT("wc_n_warden"),{.71f,.93f,.85f}}
  };
  if(const auto* Color=Colors.Find(Id)) return *Color;
  return FLinearColor(.8f,.8f,.8f);
}
}

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
  A->Tags.Add(TEXT("WCBoardEnvironment"));
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
  for (int Kind = 0; Kind < 2; ++Kind) {
    const auto& List = Kind ? Definitions.neutrals : Definitions.units;
    for (const auto& Definition : List) {
      const FString Id = UTF8_TO_TCHAR(Definition.id.c_str());
      const FString Folder = FString(Kind ? TEXT("/Game/WonderChess/Neutrals/") : TEXT("/Game/WonderChess/Heroes/")) + Id + TEXT("/");
      TArray<FString> Names = {TEXT("SK_") + Id, TEXT("T_") + Id + TEXT("_Portrait")};
      for (const TCHAR* Clip : {TEXT("Idle"),TEXT("Move"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory")}) {
        if (Kind && (FCString::Strcmp(Clip,TEXT("Victory")) == 0 || (!Definition.ability.enabled && FCString::Strcmp(Clip,TEXT("Active")) == 0))) continue;
        Names.Add(TEXT("AN_") + Id + TEXT("_") + Clip);
      }
      for (const auto& Name : Names)
        if (auto* Asset = LoadObject<UObject>(nullptr, *(Folder + Name + TEXT(".") + Name))) ResidentAssets.Add(Asset);
    }
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
  TArray<TSharedPtr<FJsonValue>> VisualActions;
  int32 SnapshotTick=0;
  int WinningSide = -2;
  int Round = int(Public->GetNumberField(TEXT("round")));
  const bool Reconstructing = Round != LastRound || Observed != LastObserved;
  if (Reconstructing) {
    for (auto &Effect : Effects)
      if (IsValid(Effect.Actor))
        Effect.Actor->Destroy();
    Effects.Reset();
    for(auto& Pair:Telegraphs) if(IsValid(Pair.Value)) Pair.Value->Destroy();
    for(auto& Pair:StatusMarkers) if(IsValid(Pair.Value)) Pair.Value->Destroy();
    Telegraphs.Reset(); StatusMarkers.Reset(); HeardActions.Reset(); KnownProjectiles.Reset();
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
      if(P->HasField(TEXT("visualActions"))) VisualActions=P->GetArrayField(TEXT("visualActions"));
      if(VisibleUnits.Num()) SnapshotTick=int(VisibleUnits[0]->AsObject()->GetNumberField(TEXT("snapshotTick")));
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
  }
  if (Reviewing) {
    VisibleUnits.Reset();
    int ReviewPage = 0; FParse::Value(FCommandLine::Get(), TEXT("WCArtPage="), ReviewPage);
    for (int I = FMath::Clamp(ReviewPage,0,1)*12; I < FMath::Min(int(Definitions.units.size()),(FMath::Clamp(ReviewPage,0,1)+1)*12); ++I) {
      auto O = MakeShared<FJsonObject>();
      O->SetNumberField("id", 90000 + I);
      O->SetNumberField("def", I);
      O->SetNumberField("star", 1);
      O->SetNumberField("side", 0);
      O->SetNumberField("col", 1 + (I % 4) * 2);
      O->SetNumberField("row", 1 + ((I % 12) / 4) * 2);
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
  TSet<FString> LiveStatuses;
  for (const auto &V : VisibleUnits) {
    auto O = V->AsObject();
    int64 Id = int64(O->GetNumberField(TEXT("id")));
    int Def = int(O->GetNumberField(TEXT("def")));
    const bool Neutral = O->HasField(TEXT("neutral")) && O->GetBoolField(TEXT("neutral"));
    const auto& List = Neutral ? Definitions.neutrals : Definitions.units;
    if (Def < 0 || Def >= int(List.size())) continue;
    const FString UnitId = UTF8_TO_TCHAR(Definitions.Definition(Def, Neutral).id.c_str());
    const FString AssetFolder = FString(Neutral ? TEXT("/Game/WonderChess/Neutrals/") : TEXT("/Game/WonderChess/Heroes/")) + UnitId + TEXT("/");
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
          AssetFolder + TEXT("SK_") + UnitId;
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
    auto Status=[&](const TCHAR* Name,bool Active,int Glyph,FLinearColor Color,float Height) {
      const FString Key=FString::Printf(TEXT("%lld:%s"),Id,Name);
      if(!Active || O->GetNumberField(TEXT("hp"))<=0) return;
      LiveStatuses.Add(Key);
      if(!StatusMarkers.Contains(Key)) StatusMarkers.Add(Key,CreateGlyph(Glyph,Target,Color,0,FVector(30,30,30)));
      if(IsValid(StatusMarkers[Key])) StatusMarkers[Key]->SetActorLocation(Actor->GetActorLocation()+FVector(0,0,Height));
    };
    Status(TEXT("shield"),O->GetNumberField(TEXT("shield"))>0,2,FLinearColor(.95f,.78f,.31f),38);
    Status(TEXT("stun"),O->GetNumberField(TEXT("stun"))>0,3,FLinearColor(.80f,.65f,1),HeroHeight(Id)+13);
    const int RateDelta=O->HasField(TEXT("effectiveRateBonus")) && O->HasField(TEXT("rateBonus"))
      ? int(O->GetNumberField(TEXT("effectiveRateBonus"))-O->GetNumberField(TEXT("rateBonus"))) : 0;
    Status(TEXT("tempo_up"),RateDelta>0,5,FLinearColor(.24f,.80f,.67f),HeroHeight(Id)+16);
    Status(TEXT("tempo_down"),RateDelta<0,10,FLinearColor(.30f,.58f,.94f),HeroHeight(Id)+16);
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
      if (State == int(wc::ActionState::Stunned)) {
        Clip = TEXT("Hit");
        Loop = false;
      }
      if (State == int(wc::ActionState::Defeated)) {
        Clip = TEXT("Defeat");
        Loop = false;
      }
      if (Victorious) {
        Clip = Neutral ? TEXT("Idle") : TEXT("Victory");
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
        const FString Path = AssetFolder + Name + TEXT(".") + Name;
        if (auto *C = Actor->FindComponentByClass<USkeletalMeshComponent>())
          if (auto *Animation = LoadObject<UAnimSequence>(nullptr, *Path)) {
            C->PlayAnimation(Animation, Loop);
            if (!Reviewing && !Victorious && (Attacking || Casting) &&
                O->HasField(TEXT("snapshotTick"))) {
              const int WindupMs = Casting
                                       ? Definitions.Definition(Def, Neutral).ability.castMs
                                       : Definitions.Definition(Def, Neutral).attackWindupMs;
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
  PresentActions(VisualActions,SnapshotTick);
  TSet<FString> AreaEmitted;
  for (const auto &V : NewEvents) {
    int Kind = int(V->GetNumberField(TEXT("effect")));
    const int64 SourceId=int64(V->GetNumberField(TEXT("source")));
    const int64 ActionId=V->HasField(TEXT("action"))?int64(V->GetNumberField(TEXT("action"))):0;
    const FString Key=ActionKey(SourceId,ActionId);
    const bool Basic=V->GetBoolField(TEXT("basicAttack"));
    FString UnitId;
    const wc::UnitDef* SourceDefinition=nullptr;
    for(const auto& Visible:VisibleUnits) {
      const auto Source=Visible->AsObject();
      if(int64(Source->GetNumberField(TEXT("id")))!=SourceId) continue;
      SourceDefinition=&Definitions.Definition(int(Source->GetNumberField(TEXT("def"))),Source->HasField(TEXT("neutral")) && Source->GetBoolField(TEXT("neutral")));
      UnitId=UTF8_TO_TCHAR(SourceDefinition->id.c_str()); break;
    }
    SpawnEffect(Kind, int64(V->GetNumberField(TEXT("source"))),
                int64(V->GetNumberField(TEXT("target"))),
                AreaEmitted.Contains(Key)?0:int(V->GetNumberField(TEXT("radius"))),
                int(V->GetNumberField(TEXT("col"))),
                int(V->GetNumberField(TEXT("row"))),UnitId,Basic);
    AreaEmitted.Add(Key);
    if (!HeardActions.Contains(Key)) {
      HeardActions.Add(Key);
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
                Definitions.Definition(int(U->GetNumberField(TEXT("def"))), U->HasField(TEXT("neutral")) && U->GetBoolField(TEXT("neutral")));
            Cue = int(V->GetNumberField(TEXT("damageType"))) ==
                          int(wc::DamageType::Magic)
                      ? TEXT("magic_impact")
                  : Definition.projectileTravelMs > 0 ? TEXT("ranged_impact")
                                                      : TEXT("melee");
            break;
          }
        }
      }
      if (!Basic) {
        for (const auto &Visible : VisibleUnits) {
          const auto Source = Visible->AsObject();
          if (Source->GetNumberField(TEXT("id")) ==
              V->GetNumberField(TEXT("source"))) {
            Cue =
                FString(UTF8_TO_TCHAR(
                    Definitions.Definition(int(Source->GetNumberField(TEXT("def"))), Source->HasField(TEXT("neutral")) && Source->GetBoolField(TEXT("neutral")))
                        .id.c_str())) +
                TEXT("_active");
            break;
          }
        }
      }
      if(Basic && UnitId.StartsWith(TEXT("wc_n_"))) Cue=UnitId+TEXT("_basic");
      Controller->Sound(Cue);
    }
  }
  for(auto It=StatusMarkers.CreateIterator();It;++It) if(!LiveStatuses.Contains(It.Key())) {
    if(IsValid(It.Value())) It.Value()->Destroy(); It.RemoveCurrent();
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

float AWCBoardPresenter::HeroHeight(int64 Id) const {
  if(!Heroes.Contains(Id) || !IsValid(Heroes[Id])) return 140;
  return FMath::Clamp(float(Heroes[Id]->GetComponentsBoundingBox(true).Max.Z-Heroes[Id]->GetActorLocation().Z),60.f,240.f);
}

AActor* AWCBoardPresenter::CreateGlyph(int32 Kind,FVector Center,FLinearColor Color,float Duration,FVector Extent) {
  if(Duration>0 && Effects.Num()>=96) return nullptr;
  auto* Actor=GetWorld()->SpawnActor<AActor>(Center,FRotator::ZeroRotator);
  auto* Root=NewObject<USceneComponent>(Actor);Actor->SetRootComponent(Root);Root->RegisterComponent();
  auto* Parts=NewObject<UInstancedStaticMeshComponent>(Actor);
  Parts->SetupAttachment(Root);Parts->SetMobility(EComponentMobility::Movable);
  Parts->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
  Parts->SetMaterial(0,Material(Color));Parts->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  Parts->SetCastShadow(false);Parts->RegisterComponent();
  auto Line=[&](FVector A,FVector B,float Width=3.f) {
    const FVector Direction=B-A;
    Parts->AddInstance(FTransform(Direction.Rotation(),(A+B)*.5,FVector(Direction.Size()/100.,Width/100.,Width/100.)));
  };
  const float R=float(Extent.X);
  if(Kind==7) {
    const float X=float(Extent.X)*.5f,Y=float(Extent.Y)*.5f;
    Line({-X,-Y,0},{X,-Y,0});Line({X,-Y,0},{X,Y,0});Line({X,Y,0},{-X,Y,0});Line({-X,Y,0},{-X,-Y,0});
  } else if(Kind==6 || Kind==2) {
    const int Segments=Kind==2?6:12;
    for(int I=0;I<Segments;++I) {
      const float A=2*PI*I/Segments,B=2*PI*(I+1)/Segments;
      if(Kind==2) Line({0,FMath::Cos(A)*R,FMath::Sin(A)*R*1.3f},{0,FMath::Cos(B)*R,FMath::Sin(B)*R*1.3f},3.5f);
      else Line({FMath::Cos(A)*R,FMath::Sin(A)*R,0},{FMath::Cos(B)*R,FMath::Sin(B)*R,0});
    }
  } else if(Kind==5 || Kind==10) {
    const float Sign=Kind==5?1.f:-1.f;
    for(int I=0;I<2;++I) { const float Z=I*14.f;Line({0,-13,Z},{0,0,Z+Sign*10});Line({0,0,Z+Sign*10},{0,13,Z}); }
  } else if(Kind==12) {
    Line({0,-R,-R*.4f},{0,0,-R});Line({0,0,-R},{0,R,0});Line({0,R,0},{0,R*.3f,R});
  } else if(Kind==13 || Kind==14 || Kind==17) {
    for(int I=-1;I<=1;++I) {
      const float Y=I*R*.65f;
      if(Kind==14) { Line({0,Y,0},{0,Y+7,R});Line({0,Y+7,R},{0,Y,R*1.7f}); }
      else {Line({0,Y-R*.3f,0},{0,Y,R*(Kind==13?1.4f:.5f)});Line({0,Y,R*(Kind==13?1.4f:.5f)},{0,Y+R*.3f,0});}
    }
  } else if(Kind==15) {
    Line({0,-R,-R*.6f},{0,R,R*.6f},5);
  } else if(Kind==16) {
    Line({0,0,-R},{0,-R*.55f,0});Line({0,-R*.55f,0},{0,0,R});
    Line({0,0,R},{0,R*.55f,0});Line({0,R*.55f,0},{0,0,-R});
  } else if(Kind==1) {
    for(int Sign:{-1,1}) { Line({0,0,0},{0,Sign*15.f,18});Line({0,Sign*15.f,18},{0,Sign*8.f,35}); }
  } else if(Kind==3) {
    for(int I=0;I<5;++I) {
      const float A=2*PI*I/5.f,B=A+4*PI/5.f;
      Line({FMath::Cos(A)*R,FMath::Sin(A)*R,0},{FMath::Cos(B)*R,FMath::Sin(B)*R,0},3.f);
    }
  } else {
    Line({0,-R,0},{0,R,0});Line({0,0,-R},{0,0,R});
    if(Kind==11) {Line({0,-R*.7f,-R*.7f},{0,R*.7f,R*.7f});Line({0,-R*.7f,R*.7f},{0,R*.7f,-R*.7f});}
  }
  if(Duration>0) Effects.Add({Actor,Center,Center,0,Duration,8});
  return Actor;
}

AActor* AWCBoardPresenter::CreateBoundary(int32 Column,int32 Row,int32 Radius,FLinearColor Color,float Duration) {
  if(Column<0 || Column>=Definitions.rules.columns || Row<0 || Row>=Definitions.rules.rows) return nullptr;
  const int LoC=FMath::Max(0,Column-Radius),HiC=FMath::Min(Definitions.rules.columns-1,Column+Radius);
  const int LoR=FMath::Max(0,Row-Radius),HiR=FMath::Min(Definitions.rules.rows-1,Row+Radius);
  const FVector Center=(Position(LoC,LoR)+Position(HiC,HiR))*.5+FVector(0,0,4);
  return CreateGlyph(7,Center,Color,Duration,FVector((HiR-LoR+1)*200,(HiC-LoC+1)*200,1));
}

void AWCBoardPresenter::PresentActions(const TArray<TSharedPtr<FJsonValue>>& Actions,int32 Tick) {
  TSet<FString> Live;
  for(const auto& Value:Actions) {
    const auto Action=Value->AsObject();
    const int64 Source=int64(Action->GetNumberField(TEXT("source"))),Id=int64(Action->GetNumberField(TEXT("action")));
    const int DefinitionIndex=int(Action->GetNumberField(TEXT("definition")));
    const bool Neutral=Action->GetBoolField(TEXT("neutral")),Basic=Action->GetBoolField(TEXT("basicAttack"));
    const auto& List=Neutral?Definitions.neutrals:Definitions.units;
    if(DefinitionIndex<0 || DefinitionIndex>=int(List.size())) continue;
    const auto& Definition=List[DefinitionIndex];const FString UnitId=UTF8_TO_TCHAR(Definition.id.c_str());
    const auto Color=SkillColor(UnitId);const FString Key=ActionKey(Source,Id);
    const bool Released=Action->GetBoolField(TEXT("released"));
    const int Release=int(Action->GetNumberField(TEXT("releaseTick"))),Impact=int(Action->GetNumberField(TEXT("impactTick")));
    const int Column=int(Action->GetNumberField(TEXT("col"))),Row=int(Action->GetNumberField(TEXT("row")));
    const int Radius=int(Action->GetNumberField(TEXT("radius"))),Kind=int(Action->GetNumberField(TEXT("effect")));
    const int64 Target=int64(Action->GetNumberField(TEXT("target")));
    const bool Fixed=Action->GetBoolField(TEXT("fixedArea"));
    if(Released && Impact>Tick && Impact>Release && !KnownProjectiles.Contains(Key)) {
      KnownProjectiles.Add(Key);
      FVector Origin=Position(int(Action->GetNumberField(TEXT("originCol"))),int(Action->GetNumberField(TEXT("originRow"))))+FVector(0,0,HeroHeight(Source)*.65f);
      if(Heroes.Contains(Source)) if(auto* Mesh=Heroes[Source]->FindComponentByClass<USkeletalMeshComponent>())
        if(Mesh->DoesSocketExist(TEXT("cast_origin"))) Origin=Mesh->GetSocketLocation(TEXT("cast_origin"));
      FVector End=Fixed?Position(Column,Row)+FVector(0,0,18):Origin;
      if(!Fixed && Heroes.Contains(Target)) End=Heroes[Target]->GetActorLocation()+FVector(0,0,HeroHeight(Target)*.55f);
      const float Elapsed=FMath::Clamp(float(Tick-Release)/(Impact-Release),0.f,1.f);
      SpawnProjectile(FMath::Lerp(Origin,End,Elapsed),End,(Impact-Tick)*Definitions.rules.tickMs/1000.f,Color,
        Definition.damageType==wc::DamageType::Physical && (Definition.id=="wc_u_elf_ranger" || Definition.id=="wc_u_halfling_ranger" || Definition.id=="wc_n_thorn"));
      if(Basic && !Neutral) Controller->Sound(TEXT("ranged_launch"));
    }
    if(Basic) continue;
    FString MarkerKey=Key+FString::Printf(TEXT(":%d:%d:%d"),Column,Row,Released?1:0);
    AActor* Marker=nullptr;
    if(Telegraphs.Contains(MarkerKey)) Marker=Telegraphs[MarkerKey];
    else if(Radius>0) Marker=CreateBoundary(Column,Row,Radius,Color*(Released?.70f:.38f));
    else if(Kind==int(wc::Effect::Dash)) Marker=CreateBoundary(Column,Row,0,Color*.55f);
    else if(Heroes.Contains(Target)) Marker=CreateGlyph(Kind==int(wc::Effect::Heal)?1:Kind==int(wc::Effect::Shield)?2:0,
      Heroes[Target]->GetActorLocation()+FVector(0,0,HeroHeight(Target)+12),Color*.45f,0,FVector(13));
    if(Marker) {
      Telegraphs.Add(MarkerKey,Marker);Live.Add(MarkerKey);
      if(Radius==0 && Kind!=int(wc::Effect::Dash) && Heroes.Contains(Target))
        Marker->SetActorLocation(Heroes[Target]->GetActorLocation()+FVector(0,0,HeroHeight(Target)+12));
    }
    if(Action->HasField(TEXT("recipients")) && (Radius>0 || Kind==int(wc::Effect::Heal) || Kind==int(wc::Effect::Shield)))
      for(const auto& Recipient:Action->GetArrayField(TEXT("recipients"))) {
        const int64 RecipientId=int64(Recipient->AsNumber());if(!Heroes.Contains(RecipientId)) continue;
        const FString RecipientKey=Key+FString::Printf(TEXT(":recipient:%lld"),RecipientId);
        Live.Add(RecipientKey);
        if(!Telegraphs.Contains(RecipientKey)) Telegraphs.Add(RecipientKey,CreateGlyph(0,FVector::ZeroVector,Color*.45f,0,FVector(9)));
        if(IsValid(Telegraphs[RecipientKey])) Telegraphs[RecipientKey]->SetActorLocation(Heroes[RecipientId]->GetActorLocation()+FVector(0,0,HeroHeight(RecipientId)+10));
      }
  }
  for(auto It=Telegraphs.CreateIterator();It;++It) if(!Live.Contains(It.Key())) {
    if(IsValid(It.Value())) It.Value()->Destroy(); It.RemoveCurrent();
  }
}

void AWCBoardPresenter::SpawnEffect(int32 Kind,int64 Source,int64 Target,int32 Radius,int32 Column,int32 Row,const FString& UnitId,bool Basic) {
  const auto Color=SkillColor(UnitId);
  if(Radius>0) CreateBoundary(Column,Row,Radius,Color*.75f,Controller->bReducedMotion?.16f:.38f);
  if(!Heroes.Contains(Target)) return;
  const FVector PositionNow=Heroes[Target]->GetActorLocation();
  if(Kind==int(wc::Effect::Dash)) {
    CreateGlyph(6,PositionNow+FVector(0,0,5),Color,.25f,FVector(36));
    if(!Controller->bReducedMotion && Targets.Contains(Source)) {
      const FVector From=Targets[Source]+FVector(0,0,7),To=Position(Column,Row)+FVector(0,0,7);
      const FVector Direction=To-From;
      if(Direction.Size()>20) {
        auto* Trail=GetWorld()->SpawnActor<AStaticMeshActor>((From+To)*.5,Direction.Rotation());
        auto* Mesh=Trail->GetStaticMeshComponent();Mesh->SetMobility(EComponentMobility::Movable);
        Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
        Mesh->SetMaterial(0,Material(Color));Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetCastShadow(false);
        Trail->SetActorScale3D(FVector(Direction.Size()/100.,.065,.018));Effects.Add({Trail,Trail->GetActorLocation(),Trail->GetActorLocation(),0,.22f,8});
      }
    }
    return;
  }
  int Glyph=Kind==int(wc::Effect::Heal)?1:Kind==int(wc::Effect::Shield)?2:Kind==int(wc::Effect::Stun)?3:
    Kind==int(wc::Effect::StatModifier)?(UnitId==TEXT("wc_u_halfling_ranger")?10:5):Basic?0:11;
  if(!Basic && Kind==int(wc::Effect::Damage)) {
    if(UnitId==TEXT("wc_u_human_mage")) Glyph=13;
    else if(UnitId==TEXT("wc_u_orc_mage")) Glyph=14;
    else if(UnitId==TEXT("wc_u_halfling_mage")) Glyph=17;
    else if(UnitId==TEXT("wc_u_human_warrior")) Glyph=15;
    else if(UnitId==TEXT("wc_u_dragonkin_rogue") || UnitId==TEXT("wc_u_dwarf_warrior")) Glyph=12;
    else if(UnitId==TEXT("wc_u_dwarf_ranger") || UnitId==TEXT("wc_u_dragonkin_ranger") || UnitId==TEXT("wc_n_warden")) Glyph=16;
  }
  const float Height=Kind==int(wc::Effect::Stun)?HeroHeight(Target)+14:HeroHeight(Target)*.48f;
  CreateGlyph(Glyph,PositionNow+FVector(0,0,Height),Color,Controller->bReducedMotion?.16f:.32f,FVector(Basic?9:20));
  if(!Basic && Heroes.Contains(Source) && (Kind==int(wc::Effect::Heal) || Kind==int(wc::Effect::Shield)) && Source!=Target) {
    const FVector Start=Heroes[Source]->GetActorLocation()+FVector(0,0,HeroHeight(Source)*.6f);
    if(!Controller->bReducedMotion) SpawnProjectile(Start,PositionNow+FVector(0,0,Height),.18f,Color,false);
  }
  if(!Basic && UnitId==TEXT("wc_u_orc_mage") && !Controller->bReducedMotion)
    CreateGlyph(0,PositionNow+FVector(0,0,40),Color,.24f,FVector(18,18,18));
}

void AWCBoardPresenter::SpawnProjectile(FVector Start, FVector End,
                                        float Duration, FLinearColor Color,
                                        bool Arrow) {
  if (Controller->bReducedMotion || Effects.Num() >= 96)
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
    else if (E.Kind != 6 && E.Kind != 8 && E.Start == E.End)
      E.Actor->SetActorScale3D(FVector(.08 + T * .3));
  }
}
