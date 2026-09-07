#include "WCFrontEndScene.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/PointLightComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "EngineUtils.h"
#include "Dom/JsonObject.h"
#include "SkeletalRenderPublic.h"
#include "WCMatchRuntime.h"

AWCFrontEndScene::AWCFrontEndScene() {
  PrimaryActorTick.bCanEverTick = true;
  RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("PresentationRoot"));
  Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("ShowcaseCamera"));
  Camera->SetupAttachment(RootComponent);
  Camera->SetFieldOfView(35);
  Camera->bConstrainAspectRatio = false;
  Camera->bOverrideAspectRatioAxisConstraint = true;
  Camera->AspectRatioAxisConstraint = AspectRatio_MaintainYFOV;
  Hero = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("ShowcaseHero"));
  Hero->SetupAttachment(RootComponent);
  Hero->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  Hero->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
  SetActorEnableCollision(false);
}

UStaticMeshComponent* AWCFrontEndScene::AddProp(const TCHAR* Name, FVector Position,
                              FVector Scale, FRotator RotationValue, const TCHAR* Folder) {
  const FString Path = FString(TEXT("/Game/WonderChess/")) + Folder + TEXT("/") + Name + TEXT(".") + Name;
  auto* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
  if (!Mesh) {
    AssetMessage += FString::Printf(TEXT("Missing courtyard asset: %s. "), Name);
    return nullptr;
  }
  auto* Component = NewObject<UStaticMeshComponent>(this);
  Component->SetupAttachment(RootComponent);
  Component->SetStaticMesh(Mesh);
  Component->SetRelativeLocation(Position);
  Component->SetRelativeRotation(RotationValue);
  Component->SetRelativeScale3D(Scale);
  Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  Component->RegisterComponent();
  return Component;
}

void AWCFrontEndScene::Initialize(AWCMatchController* OwnerController) {
  Controller = OwnerController;
  PreviousCamera = OwnerController->GetViewTarget();
  SetArenaVisible(false);
  // Separate from the active arena; previews cannot overlap selectable cells.
  SetActorLocation(FVector(3400, 0, 0));
  bApproachImported = LoadObject<UStaticMesh>(nullptr,
      TEXT("/Game/WonderChess/Lobby/SM_WC_BrighthavenApproach.SM_WC_BrighthavenApproach")) != nullptr;
  if (bApproachImported) {
    const FVector VillageOffset(-640, 640, -40);
    for (const TCHAR* Module : {TEXT("SM_WC_ApproachWestHouse"), TEXT("SM_WC_ApproachEastHouse"),
         TEXT("SM_WC_ApproachGardenArch"), TEXT("SM_WC_ApproachBeacon"), TEXT("SM_WC_ApproachGardenWalls")})
      AddProp(Module, VillageOffset, FVector(.5f), FRotator(0, -45, 0), TEXT("Lobby"));
    AddProp(TEXT("SM_WC_ApproachPlatform"), FVector::ZeroVector, FVector(1.6f, 1.6f, 1), FRotator(0, -45, 0), TEXT("Lobby"));
    Floor = AddProp(TEXT("SM_WC_Tile"), FVector::ZeroVector);
  } else {
  AddProp(TEXT("SM_WC_CourtyardFoundation"), FVector(0, 0, 23), FVector(.6f, .6f, 1));
  for (int Row = -1; Row <= 1; ++Row) for (int Column = -1; Column <= 1; ++Column) {
    auto* Tile = AddProp((Row + Column) % 2 ? TEXT("SM_WC_TileAlt") : TEXT("SM_WC_Tile"), FVector(Row * 200, Column * 200, 0));
    if (Row == 0 && Column == 0) Floor = Tile;
  }
  AddProp(TEXT("SM_WC_Stairs"), FVector(170, -520, -15), FVector(1.5f));
  for (int32 Index = -2; Index <= 2; ++Index) {
    AddProp(TEXT("SM_WC_DistantFacade"), FVector(-1450, Index * 530, -15), FVector(.8f), FRotator(0, 90, 0));
    AddProp(TEXT("SM_WC_LowWall"), FVector(-350, Index * 240, 0), FVector(1), FRotator(0, 90, 0));
  }
  for (int32 Index = 0; Index < 7; ++Index)
    AddProp(TEXT("SM_WC_Lantern"), FVector(-320, (Index - 3) * 145, 75));
  for (int32 Side : {-1, 1}) {
    AddProp(TEXT("SM_WC_Planter"), FVector(-240, Side * 480, 0), FVector(.8f));
    AddProp(TEXT("SM_WC_Flagpole"), FVector(-370, Side * 560, 0), FVector(1.1f));
    AddProp(TEXT("SM_WC_Banner"), FVector(-370, Side * 560, 0), FVector(1.1f));
  }
  }
  auto* SkyMaterial = LoadObject<UMaterialInterface>(nullptr,
      TEXT("/Game/WonderChess/Lobby/M_WC_BrighthavenSky.M_WC_BrighthavenSky"));
  auto* SkyMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
  if (SkyMaterial && SkyMesh) {
    auto* Sky = NewObject<UStaticMeshComponent>(this);
    Sky->SetupAttachment(RootComponent);
    Sky->SetStaticMesh(SkyMesh);
    Sky->SetMaterial(0, SkyMaterial);
    Sky->SetRelativeScale3D(FVector(180));
    Sky->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Sky->SetCastShadow(false);
    Sky->RegisterComponent();
  } else AssetMessage += TEXT("The original Brighthaven sky material is missing. ");
  auto* Fill = NewObject<UPointLightComponent>(this);
  Fill->SetupAttachment(RootComponent);
  Fill->SetRelativeLocation(FVector(150, -160, 280));
  Fill->SetIntensity(3500);
  Fill->SetLightColor(FLinearColor(1, .87f, .66f));
  Fill->SetAttenuationRadius(900);
  Fill->SetCastShadows(false);
  Fill->RegisterComponent();
  auto* Atmosphere = NewObject<USkyAtmosphereComponent>(this);
  Atmosphere->SetupAttachment(RootComponent);
  Atmosphere->SetRayleighScatteringScale(.8f);
  Atmosphere->SetMieScatteringScale(.2f);
  Atmosphere->RegisterComponent();
  auto* SkySun = NewObject<UDirectionalLightComponent>(this);
  SkySun->SetupAttachment(RootComponent);
  SkySun->SetRelativeRotation(FRotator(-32, 148, 0));
  SkySun->SetIntensity(.8f);
  SkySun->SetLightColor(FLinearColor(1, .91f, .77f));
  SkySun->SetAtmosphereSunLight(true);
  SkySun->SetCastShadows(true);
  SkySun->SetDynamicShadowDistanceMovableLight(2400.f);
  SkySun->RegisterComponent();
  ResetView();
  OwnerController->SetViewTarget(this);
}

void AWCFrontEndScene::ShowHero(const FString& UnitId, int32 Star, bool ReducedMotion) {
  if (HeroId != UnitId) {
    HeroId = UnitId;
    ResidentAssets.Reset();
    const FString Name = TEXT("SK_") + UnitId;
    const FString Path = TEXT("/Game/WonderChess/Heroes/") + UnitId + TEXT("/") + Name + TEXT(".") + Name;
    auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *Path);
    Hero->SetSkeletalMesh(Mesh);
    AssetMessage = Mesh ? FString() : TEXT("This hero's skeletal mesh is not present in this build.");
    SelectedClip = TEXT("Idle");
    ResetView();
  }
  // Stars remain a gallery preview; this restrained size accent never changes combat.
  Hero->SetRelativeScale3D(FVector(1.f + .035f * (FMath::Clamp(Star, 1, 3) - 1)));
  if (Floor && Hero->GetSkeletalMeshAsset()) {
    const auto Ground = Floor->CalcBounds(Floor->GetComponentTransform());
    const auto Reference = Hero->GetSkeletalMeshAsset()->GetBounds();
    FVector Location = Hero->GetRelativeLocation();
    Location.Z = Ground.Origin.Z + Ground.BoxExtent.Z - GetActorLocation().Z -
                 (Reference.Origin.Z - Reference.BoxExtent.Z) * Hero->GetRelativeScale3D().Z;
    Hero->SetRelativeLocation(Location);
  }
  FramingFrames = 5;
  PlayClip(SelectedClip, ReducedMotion);
}

bool AWCFrontEndScene::PlayClip(const FString& Clip, bool ReducedMotion) {
  SelectedClip = Clip;
  const FString Name = TEXT("AN_") + HeroId + TEXT("_") + Clip;
  const FString Path = TEXT("/Game/WonderChess/Heroes/") + HeroId + TEXT("/") + Name + TEXT(".") + Name;
  auto* Animation = LoadObject<UAnimSequence>(nullptr, *Path);
  if (!Animation || !Hero->GetSkeletalMeshAsset()) {
    AssetMessage = FString::Printf(TEXT("Preview unavailable: %s / %s. Imported content is required."), *HeroId, *Clip);
    return false;
  }
  ResidentAssets.AddUnique(Animation);
  AssetMessage.Reset();
  Hero->PlayAnimation(Animation, true);
  FramingFrames = 5;
  Hero->bPauseAnims = ReducedMotion;
  if (ReducedMotion)
    Hero->SetPosition(0, false);
  return true;
}

void AWCFrontEndScene::RotateHero(float Degrees) {
  Rotation = FMath::Fmod(Rotation + Degrees, 360.f);
  Hero->SetRelativeRotation(FRotator(0, Rotation, 0));
}

void AWCFrontEndScene::ResetView() {
  Rotation = -45;
  Hero->SetRelativeRotation(FRotator(0, Rotation, 0));
  const float Height = Hero->GetSkeletalMeshAsset()
                           ? FMath::Max(180.f, Hero->GetSkeletalMeshAsset()->GetBounds().BoxExtent.Z * 2)
                           : 200.f;
  const float Distance = FMath::Clamp(Height * 4.6f, 850.f, 1600.f);
  const FVector Target(120, 120, Height * .32f);
  const FVector Position = Target + FVector(Distance * .78f, -Distance * .78f, Distance * .24f);
  Camera->SetRelativeLocation(Position);
  Camera->SetRelativeRotation((Target - Position).Rotation());
  FramingFrames = 5;
}

void AWCFrontEndScene::FitPreview() {
  if (!Controller.IsValid() || Controller->GetViewTarget() != this || !Hero->GetSkeletalMeshAsset() ||
      !GEngine || !GEngine->GameViewport) return;
  FVector2D Viewport;
  GEngine->GameViewport->GetViewportSize(Viewport);
  if (Viewport.X < 1 || Viewport.Y < 1) return;
  const auto Bounds = Hero->CalcBounds(Hero->GetComponentTransform());
  FVector2D Minimum(DBL_MAX, DBL_MAX), Maximum(-DBL_MAX, -DBL_MAX), Center, RightPoint, UpPoint;
  for (int X : {-1, 1}) for (int Y : {-1, 1}) for (int Z : {-1, 1}) {
    FVector2D Point;
    if (!Controller->ProjectWorldLocationToScreen(Bounds.Origin + Bounds.BoxExtent * FVector(X, Y, Z), Point)) return;
    Minimum.X = FMath::Min(Minimum.X, Point.X); Minimum.Y = FMath::Min(Minimum.Y, Point.Y);
    Maximum.X = FMath::Max(Maximum.X, Point.X); Maximum.Y = FMath::Max(Maximum.Y, Point.Y);
  }
  if (!Controller->ProjectWorldLocationToScreen(Bounds.Origin, Center) ||
      !Controller->ProjectWorldLocationToScreen(Bounds.Origin + Camera->GetRightVector() * 100, RightPoint) ||
      !Controller->ProjectWorldLocationToScreen(Bounds.Origin + Camera->GetUpVector() * 100, UpPoint)) return;
  const double PixelsPerCmX = FMath::Abs(RightPoint.X - Center.X) / 100;
  const double PixelsPerCmY = FMath::Abs(UpPoint.Y - Center.Y) / 100;
  if (PixelsPerCmX < .01 || PixelsPerCmY < .01) return;
  const FVector2D ProjectedCenter = (Minimum + Maximum) * .5;
  const FVector Correction = -Camera->GetRightVector() * ((Viewport.X * .77 - ProjectedCenter.X) / PixelsPerCmX) +
                              Camera->GetUpVector() * ((Viewport.Y * .435 - ProjectedCenter.Y) / PixelsPerCmY);
  Camera->AddWorldOffset(Correction.GetClampedToMaxSize(400));
  const double Fit = FMath::Max((Maximum.X - Minimum.X) / (Viewport.X * .34), (Maximum.Y - Minimum.Y) / (Viewport.Y * .54));
  if (Fit > 1.02)
    Camera->AddWorldOffset(-Camera->GetForwardVector() * FMath::Min(500.0, FVector::Distance(Camera->GetComponentLocation(), Bounds.Origin) * (Fit - 1)));
  else if (Fit < .95)
    Camera->AddWorldOffset(Camera->GetForwardVector() * FMath::Min(350.0, FVector::Distance(Camera->GetComponentLocation(), Bounds.Origin) * (1 - Fit)));
}

void AWCFrontEndScene::SetTurntable(bool Enabled) { bTurntable = Enabled; }
void AWCFrontEndScene::SetArenaVisible(bool Visible) {
  if (!Controller.IsValid()) return;
  if (Visible) {
    for (const auto& Actor : HiddenArenaActors)
      if (Actor.IsValid()) Controller->HiddenActors.Remove(Actor.Get());
    HiddenArenaActors.Reset();
  } else {
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
      if ((It->ActorHasTag(TEXT("WCArena")) || It->ActorHasTag(TEXT("WCBoardEnvironment"))) &&
          !Controller->HiddenActors.Contains(*It)) {
        Controller->HiddenActors.Add(*It);
        HiddenArenaActors.Add(*It);
      }
  }
}
void AWCFrontEndScene::TransitionToArena(float Duration, bool ReducedMotion) {
  if (!Controller.IsValid() || !PreviousCamera.IsValid()) return;
  bTurntable = false;
  // The two cameras use different projections. Cover that cut instead of flying
  // a perspective camera through the roofs between the approach and the board.
  FadeSeconds = FMath::Clamp(Duration * .1f, .05f, ReducedMotion ? .15f : .18f);
  TransitionClock = 0; TransitionStage = 1;
  if (Controller->PlayerCameraManager)
    Controller->PlayerCameraManager->StartCameraFade(0.f, 1.f, FadeSeconds, FLinearColor::Black, false, true);
}
void AWCFrontEndScene::Tick(float DeltaSeconds) {
  Super::Tick(DeltaSeconds);
  if (TransitionStage && Controller.IsValid()) {
    TransitionClock += DeltaSeconds;
    if (TransitionStage == 1 && TransitionClock >= FadeSeconds) {
      SetArenaVisible(true);
      if (PreviousCamera.IsValid()) Controller->SetViewTarget(PreviousCamera.Get());
      if (Controller->PlayerCameraManager)
        Controller->PlayerCameraManager->StartCameraFade(1.f, 0.f, FadeSeconds, FLinearColor::Black, false, false);
      TransitionStage = 2; TransitionClock = 0;
    } else if (TransitionStage == 2 && TransitionClock >= FadeSeconds) TransitionStage = 0;
  }
  if (FramingFrames > 0) { --FramingFrames; FitPreview(); }
  if (bTurntable && Controller.IsValid() && !Controller->bReducedMotion)
    RotateHero(DeltaSeconds * 18.f);
}
void AWCFrontEndScene::RestoreCamera() {
  SetArenaVisible(true);
  if (!Controller.IsValid()) return;
  if (Controller->PlayerCameraManager) Controller->PlayerCameraManager->StopCameraFade();
  if (PreviousCamera.IsValid() && (Controller->GetViewTarget() == this || TransitionStage)) Controller->SetViewTarget(PreviousCamera.Get());
  TransitionStage = 0;
}
void AWCFrontEndScene::RestorePreview() {
  SetArenaVisible(false);
  TransitionStage = 0;
  if (!Controller.IsValid()) return;
  if (Controller->PlayerCameraManager) Controller->PlayerCameraManager->StopCameraFade();
  Controller->SetViewTarget(this);
}
TSharedPtr<FJsonObject> AWCFrontEndScene::MeasureGrounding() const {
  auto Report = MakeShared<FJsonObject>();
  Report->SetStringField(TEXT("hero"), HeroId);
  Report->SetStringField(TEXT("clip"), SelectedClip);
  Report->SetStringField(TEXT("method"), TEXT("Actual CPU-skinned LOD0 vertices and transformed floor bounds. Render-thread flush; audit only, excluded from performance evidence."));
  if (!Floor || !Hero->GetSkeletalMeshAsset()) { Report->SetBoolField(TEXT("available"), false); return Report; }
  const auto Ground = Floor->CalcBounds(Floor->GetComponentTransform());
  const double GroundZ = Ground.Origin.Z + Ground.BoxExtent.Z;
  TArray<FFinalSkinVertex> Vertices;
  Hero->GetCPUSkinnedVertices(Vertices, 0);
  double Minimum = DBL_MAX;
  for (const auto& Vertex : Vertices)
    Minimum = FMath::Min(Minimum, Hero->GetComponentTransform().TransformPosition(FVector(Vertex.Position)).Z);
  Report->SetBoolField(TEXT("available"), !Vertices.IsEmpty());
  Report->SetNumberField(TEXT("vertices"), Vertices.Num());
  Report->SetNumberField(TEXT("floor_world_z_cm"), GroundZ);
  Report->SetNumberField(TEXT("hero_component_z_cm"), Hero->GetComponentLocation().Z);
  Report->SetNumberField(TEXT("left_foot_bone_world_z_cm"), Hero->GetBoneLocation(TEXT("foot_l")).Z);
  Report->SetNumberField(TEXT("right_foot_bone_world_z_cm"), Hero->GetBoneLocation(TEXT("foot_r")).Z);
  if (!Vertices.IsEmpty()) {
    Report->SetNumberField(TEXT("lowest_skinned_vertex_world_z_cm"), Minimum);
    Report->SetNumberField(TEXT("lowest_vertex_gap_cm"), Minimum - GroundZ);
  }
  return Report;
}
