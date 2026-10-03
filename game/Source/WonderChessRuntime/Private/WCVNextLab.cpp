#include "WCVNextLab.h"
#include "WCBellbackPresentation.h"
#include "WCHeroPresentation.h"
#include "WCSilkmotherPresentation.h"
#include "WCCragstoatPresentation.h"
#include "Engine/TextureCube.h"
#include "WCVNextArtStyle.h"
#include "Simulation/WonderCombatClarityTests.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Framework/Application/SlateApplication.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/SkyLight.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Serialization/JsonSerializer.h"
#include "Styling/CoreStyle.h"
#include "UnrealClient.h"
#include "UObject/ConstructorHelpers.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SSpinBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SWrapBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SNullWidget.h"
#include "Widgets/SViewport.h"
#include "Widgets/Text/STextBlock.h"
#include <algorithm>
#include <tuple>

namespace
{
const FLinearColor Ink(.018f, .032f, .042f, .97f), Paper(.89f, .92f, .85f), Gold(.98f, .75f, .34f);
const FLinearColor Teams[] = {{.13f,.72f,.68f}, {.92f,.36f,.24f}};
const FLinearColor HeroColors[] = {{.64f,.56f,.28f}, {.42f,.55f,.64f}, {.35f,.55f,.22f}, {.56f,.26f,.34f}, {.42f,.38f,.75f}, {.22f,.70f,.69f}};
const TCHAR* CragstoatPreviewMeshPath=TEXT("/Game/WonderChess/Diagnostics/CragstoatProduction20260921/AnimationReady_r002/SK_Cragstoat.SK_Cragstoat");
const TCHAR* CragstoatPreviewMaterialPath=TEXT("/Game/WonderChess/Diagnostics/CragstoatProduction20260921/Color_r002/M_CragstoatPBR.M_CragstoatPBR");
FString Str(const std::string& Value) { return UTF8_TO_TCHAR(Value.c_str()); }
FText Txt(const FString& Value) { return FText::FromString(Value); }
wc::Id OwnedId(wc::Id CombatId) { return CombatId & ((wc::Id(1)<<20)-1); }
const TCHAR* FacingName(wc::Facing Facing)
{
    static const TCHAR* Names[] = {TEXT("Forward"), TEXT("Right"), TEXT("Backward"), TEXT("Left")};
    return Names[FMath::Clamp(int(Facing), 0, 3)];
}
const TCHAR* EffectName(wc::Effect Effect)
{
    switch (Effect) {
    case wc::Effect::Damage: return TEXT("damage"); case wc::Effect::Heal: return TEXT("heal");
    case wc::Effect::Shield: return TEXT("shield"); case wc::Effect::Stun: return TEXT("stun");
    case wc::Effect::Dash: return TEXT("move"); case wc::Effect::StatModifier: return TEXT("modifier");
    }
    return TEXT("effect");
}
FString Hash(const FString& Value)
{
    const FTCHARToUTF8 Utf8(*Value);
    return FSHA1::HashBuffer(Utf8.Get(), Utf8.Length()).ToString().ToLower();
}
}

AWCVNextLabMode::AWCVNextLabMode()
{
    PlayerControllerClass = AWCVNextLabController::StaticClass();
    DefaultPawnClass = nullptr;
    HUDClass = nullptr;
}
void AWCVNextLabMode::BeginPlay()
{
    Super::BeginPlay();
    GetWorld()->SpawnActor<AWCVNextLab>()->Initialize();
}
AWCVNextLabController::AWCVNextLabController()
{
    bAutoManageActiveCameraTarget = false;
    bShowMouseCursor = true;
    bEnableClickEvents = true;
}
AWCVNextLab::AWCVNextLab()
{
    PrimaryActorTick.bCanEverTick = true;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cone(TEXT("/Engine/BasicShapes/Cone.Cone"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Plane(TEXT("/Engine/BasicShapes/Plane.Plane"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Surface(TEXT("/Game/WonderChess/Materials/M_WC_Surface.M_WC_Surface"));
    ProxyMeshes.Add(TEXT("Cube"),Cube.Object);ProxyMeshes.Add(TEXT("Sphere"),Sphere.Object);
    ProxyMeshes.Add(TEXT("Cylinder"),Cylinder.Object);ProxyMeshes.Add(TEXT("Cone"),Cone.Object);
    ProxyMeshes.Add(TEXT("Plane"),Plane.Object);
    ProxyMaterial=Surface.Object;
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> CueSurface(TEXT("/Game/WonderChess/VNext/M_CombatCue.M_CombatCue"));
    CombatCueMaterial=CueSurface.Object;
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> CragMesh(CragstoatPreviewMeshPath);
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> CragMaterial(CragstoatPreviewMaterialPath);
    CragstoatPreviewMesh=CragMesh.Object;
    CragstoatPreviewMaterial=CragMaterial.Object;
}
AWCVNextLab::~AWCVNextLab() = default;

void AWCVNextLab::Initialize()
{
    BellbackCandidate=FParse::Param(FCommandLine::Get(),TEXT("WCBellbackCandidate"));
    HeroReview=FParse::Param(FCommandLine::Get(),TEXT("WCHeroReview"));
    Courtyard=!FParse::Param(FCommandLine::Get(),TEXT("WCLegacyBoard"));
    SilkmotherCandidate=FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherCandidate"));
    CragstoatCandidate=FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatCandidate"));
    CragstoatExercise=FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatExercise"));
    CragstoatPreview=FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatPreview"))&&!CragstoatCandidate;
    if(SilkmotherCandidate||CragstoatCandidate)BellbackCandidate=true;
    BellbackExercise=FParse::Param(FCommandLine::Get(),TEXT("WCBellbackExercise"));
    SilkmotherExercise=FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherExercise"));
    BellbackPerformance=FParse::Param(FCommandLine::Get(),TEXT("WCBellbackPerformance"));
    ArtSlice = FWCArtSlice::IsEnabled();
    Storybook = FWCArtSlice::IsStorybook();
    if(Storybook){
        SanctuaryMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WonderChess/VNext/ArtExpansionR001/M_SanctuaryBackground.M_SanctuaryBackground"));
        UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_SANCTUARY material=%d"),SanctuaryMaterial!=nullptr);
    }
    if(ArtSlice){
        QuietStoneMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WonderChess/VNext/ArtSliceR001/M_QuietStone.M_QuietStone"));
        const auto* StoneTexture=LoadObject<UTexture2D>(nullptr,TEXT("/Game/WonderChess/VNext/ArtSliceR001/T_QuietStone.T_QuietStone"));
        UE_LOG(LogTemp,Display,TEXT("WC_ART_SLICE_STONE texture=%d size=%dx%d material=%d"),StoneTexture!=nullptr,
            StoneTexture?StoneTexture->GetSizeX():0,StoneTexture?StoneTexture->GetSizeY():0,QuietStoneMaterial!=nullptr);
    }
    Controller = Cast<AWCVNextLabController>(GetWorld()->GetFirstPlayerController());
    Exercise = FParse::Param(FCommandLine::Get(), TEXT("WCLabExercise"));
    CueExercise=FParse::Param(FCommandLine::Get(), TEXT("WCCueExercise"));
    if(CueExercise){Exercise=true;ExerciseStage=100;}
    SoloMode = FParse::Param(FCommandLine::Get(), TEXT("WCSolo"));
    SoloExercise = SoloMode && FParse::Param(FCommandLine::Get(), TEXT("WCSoloExercise"));
    SoloVisualExercise=SoloMode&&Storybook&&FParse::Param(FCommandLine::Get(),TEXT("WCSoloVisualExercise"));
    if(SoloVisualExercise){SoloExercise=false;Exercise=true;ExerciseStage=200;}
    EvidenceDirectory = FPaths::ProjectSavedDir() / TEXT("WonderVNext/Lab");
    FParse::Value(FCommandLine::Get(), TEXT("WCEvidenceDir="), EvidenceDirectory);
    FParse::Value(FCommandLine::Get(), TEXT("WCSeed="), Seed);
    Seed = FMath::Max(1, Seed);
    FString Profile;
    FParse::Value(FCommandLine::Get(), TEXT("WCProfileName="), Profile);
    if (Profile != TEXT("wonder_vnext"))
        LoadError = TEXT("The lab requires -WCProfileName=wonder_vnext. Legacy data is never substituted.");
    else if (!wc::LoadCatalog(Catalog, LoadError, &Metadata)) {}
    else if (Catalog.units.size() < 6 || Catalog.rules.columns != 8 || Catalog.rules.rows != 8 || Catalog.rules.deploymentRows != 4)
        LoadError = TEXT("The vNext lab needs its six pilot definitions and an 8 by 8 board with four deployment rows.");
    if(LoadError.IsEmpty()){
        if(CragstoatPreview&&(!SoloMode||!Storybook))
            LoadError=TEXT("Cragstoat rest-pose preview requires solo storybook mode.");
        if(CragstoatPreview&&LoadError.IsEmpty()){
            auto* PreviewMesh=CragstoatPreviewMesh.Get();
            auto* PreviewMaterial=CragstoatPreviewMaterial.Get();
            if(!PreviewMesh||!PreviewMesh->GetSkeleton()||!PreviewMaterial)
                LoadError=TEXT("Cragstoat preview mesh, skeleton or preserved PBR material is missing.");
            else UE_LOG(LogTemp,Display,TEXT("WC_CRAGSTOAT_PREVIEW_ASSETS mesh=%s material=%s box_extent=%s"),
                CragstoatPreviewMeshPath,CragstoatPreviewMaterialPath,*PreviewMesh->GetBounds().BoxExtent.ToString());
        }
        if((BellbackExercise||BellbackPerformance)&&(!BellbackCandidate||SoloMode||Exercise||SoloExercise||BellbackExercise==BellbackPerformance))
            LoadError=TEXT("Bellback routes require candidate laboratory, one route and no other exercise flags.");
        if(BellbackCandidate&&LoadError.IsEmpty())UWCBellbackPresentationComponent::ValidateAssets(LoadError);
        if(SilkmotherCandidate&&LoadError.IsEmpty())UWCSilkmotherPresentationComponent::ValidateAssets(LoadError);
        if(CragstoatCandidate&&LoadError.IsEmpty())UWCCragstoatPresentationComponent::ValidateAssets(LoadError);
        if(CragstoatExercise&&(!CragstoatCandidate||SoloMode||SilkmotherExercise||BellbackExercise||BellbackPerformance))
            LoadError=TEXT("Cragstoat exercise requires its candidate laboratory and one exercise route.");
        if(ArtSlice&&(!QuietStoneMaterial||!FWCArtSlice::ResourcesReady()))LoadError=TEXT("The 2D art slice requires its stone material and UI artwork in this package.");
        if(Storybook&&!SanctuaryMaterial)LoadError=TEXT("The storybook sanctuary material is missing from this package.");
        if(Storybook&&!FWCArtSlice::StorybookResourcesReady())LoadError=TEXT("The storybook portraits, ability icons or relic artwork are missing from this package.");
        if(!CombatCueMaterial)LoadError=TEXT("Combat cue material is missing.");
        if(!ProxyMaterial)LoadError=TEXT("The lab's engine proxy material is missing from this build.");
        for(const auto& Entry:ProxyMeshes)if(!Entry.Value)LoadError=TEXT("A required engine proxy mesh is missing from this build: ")+Entry.Key;
    }
    if (LoadError.IsEmpty()) {
        BuildScene();
        if (SoloMode) StartSolo(); else Preset();
        if(!SoloMode&&SilkmotherCandidate&&FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherArena"))){
            const auto Pairs=wc::BuiltinScenarioPairs(Catalog);
            for(size_t I=0;I<Pairs.size();++I)if(Pairs[I].mechanic==wc::AbilityMechanic::CocoonProjectile){
                ScenarioIndex=int(I);ApplyFormationScenario(Pairs[I].a,TEXT("Silkmother + Bellback arena. Press Start to test their abilities."));break;
            }
        }
        UE_LOG(LogTemp, Display, TEXT("WC_VNEXT_LAB_READY profile=wonder_vnext units=%d digest=%s proxy_art=UNAPPROVED"), int(Catalog.units.size()), *Str(Catalog.contentDigest));
    } else {
        Message = LoadError;
        UE_LOG(LogTemp, Error, TEXT("WC_VNEXT_LAB_REJECTED %s"), *LoadError);
    }
    if (SoloMode) BuildSoloInterface(); else BuildInterface();
    if (Exercise) {
        ExerciseChecks = MakeShared<FJsonObject>();
        ExerciseChecks->SetBoolField(TEXT("native_slate_created"), Interface.IsValid());
        ExerciseChecks->SetBoolField(TEXT("vnext_profile_loaded"), LoadError.IsEmpty());
        if(ArtSlice){
            ExerciseChecks->SetBoolField(TEXT("art_slice_resources_loaded"),QuietStoneMaterial&&FWCArtSlice::ResourcesReady());
            bool StoneApplied=Cells.Num()==64;
            for(const auto* Cell:Cells)StoneApplied&=Cell&&Cell->GetMaterial(0)&&Cell->GetMaterial(0)->GetMaterial()==QuietStoneMaterial->GetMaterial();
            ExerciseChecks->SetBoolField(TEXT("quiet_stone_applied_to_64_cells"),StoneApplied);
        }
        if(Storybook){
            ExerciseChecks->SetBoolField(TEXT("storybook_sanctuary_backdrop_loaded"),SanctuaryBackdrop&&SanctuaryMaterial);
            ExerciseChecks->SetBoolField(TEXT("storybook_expanded_illustrations_loaded"),FWCArtSlice::StorybookResourcesReady());
        }
        if (!LoadError.IsEmpty()) {
            if(SoloVisualExercise)FinishSoloVisualExercise(LoadError);else WriteEvidence(false);
            ExerciseDone = true;
        }
    }
}

AActor* AWCVNextLab::SceneActor(FVector Location)
{
    auto* Actor = GetWorld()->SpawnActor<AActor>(Location, FRotator::ZeroRotator);
    auto* Root = NewObject<USceneComponent>(Actor);
    Actor->SetRootComponent(Root);
    Actor->AddInstanceComponent(Root);
    Root->RegisterComponent();
    Actor->SetActorLocation(Location);
    SceneActors.Add(Actor);
    return Actor;
}
UMaterialInstanceDynamic* AWCVNextLab::Material(FLinearColor Color)
{
    const uint32 Key = Color.ToFColor(false).ToPackedRGBA();
    if (auto* Existing = Materials.Find(Key)) return *Existing;
    auto* Result = UMaterialInstanceDynamic::Create(ProxyMaterial, this);
    Result->SetVectorParameterValue(TEXT("Color"), Color);
    Materials.Add(Key, Result);
    return Result;
}
UMaterialInstanceDynamic* AWCVNextLab::StoneMaterial(FLinearColor Color)
{
    const uint32 Key=Color.ToFColor(false).ToPackedRGBA();
    if(auto* Existing=StoneMaterials.Find(Key))return *Existing;
    auto* Result=UMaterialInstanceDynamic::Create(QuietStoneMaterial,this);
    Result->SetVectorParameterValue(TEXT("Color"),Color);
    StoneMaterials.Add(Key,Result);
    return Result;
}
UStaticMeshComponent* AWCVNextLab::Mesh(AActor* ParentActor, const TCHAR* Shape, FVector Location, FVector Scale, FLinearColor Color, FRotator Rotation)
{
    auto* Component = NewObject<UStaticMeshComponent>(ParentActor);
    ParentActor->AddInstanceComponent(Component);
    Component->SetupAttachment(ParentActor->GetRootComponent());
    Component->SetStaticMesh(ProxyMeshes.FindChecked(Shape));
    Component->SetMobility(EComponentMobility::Movable);
    Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Component->SetMaterial(0, Material(Color));
    Component->SetRelativeLocation(Location);
    Component->SetRelativeRotation(Rotation);
    Component->SetRelativeScale3D(Scale);
    Component->RegisterComponent();
    return Component;
}
FVector AWCVNextLab::Position(wc::Cell Cell) const
{
    return FVector((Cell.column - 3.5) * 200, (3.5 - Cell.row) * 200, 0);
}
void AWCVNextLab::BuildScene()
{
    auto* Ground = SceneActor();
    auto* Foundation=Mesh(Ground, TEXT("Cube"), FVector(0,0,-45), FVector(17.2,17.2,.7), FLinearColor(.10f,.16f,.14f));
    if(Storybook){
        Foundation->SetRelativeLocation(FVector(0,0,-19));
        Foundation->SetRelativeScale3D(FVector(17.45,17.45,.28));
        auto* FoundationInk=UMaterialInstanceDynamic::Create(CombatCueMaterial,this);
        FoundationInk->SetVectorParameterValue(TEXT("Color"),FLinearColor(.20f,.17f,.105f));
        Foundation->SetMaterial(0,FoundationInk);
        Foundation->SetCastShadow(false);
        for(int Edge=0;Edge<4;++Edge){
            const bool Vertical=Edge>1;
            const FVector P=Vertical?FVector(Edge==2?-842:842,0,-2):FVector(0,Edge==0?-842:842,-2);
            auto* Rim=Mesh(Ground,TEXT("Cube"),P,Vertical?FVector(.46,17.5,.18):FVector(17.5,.46,.18),Paper);
            Rim->SetMaterial(0,StoneMaterial(FLinearColor(.58f,.59f,.52f)));
            auto* Inlay=Mesh(Ground,TEXT("Cube"),P+FVector(0,0,13),Vertical?FVector(.04,17.4,.025):FVector(17.4,.04,.025),FLinearColor(.38f,.29f,.12f));
            Inlay->SetCastShadow(false);
        }
        // A single instanced mesh draws the quiet etched corner medallions.
        auto* Etch=NewObject<UInstancedStaticMeshComponent>(Ground);
        Ground->AddInstanceComponent(Etch);Etch->SetupAttachment(Ground->GetRootComponent());
        Etch->SetStaticMesh(ProxyMeshes.FindChecked(TEXT("Cube")));Etch->SetMobility(EComponentMobility::Movable);
        Etch->SetCollisionEnabled(ECollisionEnabled::NoCollision);Etch->SetCastShadow(false);
        Etch->SetMaterial(0,Material(FLinearColor(.54f,.47f,.30f)));Etch->RegisterComponent();
        const auto Engrave=[Etch](FVector A,FVector B){
            const FVector Delta=B-A;
            Etch->AddInstance(FTransform(Delta.Rotation(),(A+B)*.5,FVector(Delta.Size()/100,.024,.008)));
        };
        for(int Row:{0,7})for(int Column:{0,7}){
            const FVector Center=Position({Column,Row})+FVector(0,0,7.2);
            for(int I=0;I<16;++I){
                const float A=I*UE_TWO_PI/16,B=(I+1)*UE_TWO_PI/16;
                Engrave(Center+FVector(FMath::Cos(A)*64,FMath::Sin(A)*64,0),Center+FVector(FMath::Cos(B)*64,FMath::Sin(B)*64,0));
            }
            Engrave(Center+FVector(0,-33,0),Center+FVector(0,36,0));
            for(int Side:{-1,1})for(int Leaf=0;Leaf<2;++Leaf){
                const FVector Stem=Center+FVector(0,-15+Leaf*22,0),Tip=Stem+FVector(Side*27,21,0);
                Engrave(Stem,Stem+FVector(Side*18,1,0));Engrave(Stem+FVector(Side*18,1,0),Tip);
                Engrave(Tip,Stem+FVector(Side*7,23,0));Engrave(Stem+FVector(Side*7,23,0),Stem);
            }
        }
        auto* BackdropActor=SceneActor();
        SanctuaryBackdrop=Mesh(BackdropActor,TEXT("Plane"),FVector(0,0,-2000),FVector(100),FLinearColor::White);
        SanctuaryBackdrop->SetMaterial(0,SanctuaryMaterial);
        SanctuaryBackdrop->SetCastShadow(false);
        if(Courtyard){SanctuaryBackdrop->SetVisibility(false);Foundation->SetVisibility(false);}
    }
    for (int Row = 0; Row < 8; ++Row) for (int Column = 0; Column < 8; ++Column) {
        const FVector P = Position({Column, Row});
        const FLinearColor Color = Courtyard ? ((Row+Column)%2 ? FLinearColor(.33f,.32f,.30f) : FLinearColor(.47f,.45f,.41f)) :
            (Row+Column)%2 ? FLinearColor(.23f,.30f,.25f) : FLinearColor(.32f,.39f,.31f);
        auto* Tile=Mesh(Ground, TEXT("Cube"), P, FVector(Storybook?1.985:1.94,Storybook?1.985:1.94,.12), Color);
        if(ArtSlice)Tile->SetMaterial(0,StoneMaterial(Courtyard?Color:Storybook?
            ((Row+Column)%2?FLinearColor(.61f,.65f,.60f):FLinearColor(.82f,.83f,.77f)):
            ((Row+Column)%2?FLinearColor(.69f,.74f,.67f):FLinearColor(.87f,.89f,.80f))));
        Cells.Add(Tile);
        for (int Edge = 0; Edge < 4; ++Edge) {
            const bool Vertical = Edge > 1;
            const FVector Offset = Vertical ? FVector(Edge == 2 ? -89 : 89,0,10) : FVector(0,Edge == 0 ? -89 : 89,10);
            auto* Mark = Mesh(Ground, TEXT("Cube"), P+Offset, Vertical ? FVector(.035,1.78,.035) : FVector(1.78,.035,.035), Gold);
            Mark->SetVisibility(false);
            Mark->SetCastShadow(false);
            Telegraphs.Add(Mark);
        }
    }
    for (int Side=0; Side<2; ++Side)
        Mesh(Ground, TEXT("Cube"), FVector(0, Side ? -826 : 826, Storybook?13:8), FVector(Storybook?2.2:16.8,.12,.1), Teams[Side]);
    auto* Light = GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,1000), FRotator(-55,-35,0));
    Light->GetLightComponent()->SetIntensity(Storybook?3.2f:4.f);
    if(Storybook)Light->GetLightComponent()->SetLightColor(FLinearColor(1.f,.96f,.89f));
    SceneActors.Add(Light);
    auto* Sky = GetWorld()->SpawnActor<ASkyLight>();
    Sky->GetLightComponent()->SetIntensity(Storybook?.92f:.75f);
    Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Sky->GetLightComponent()->bRealTimeCapture = true;
    if(SilkmotherCandidate){
        Light->GetLightComponent()->SetIntensity(2.5);Light->GetLightComponent()->SetCastShadows(false);
        auto* Fill=Sky->GetLightComponent();Fill->bRealTimeCapture=false;Fill->SourceType=SLS_SpecifiedCubemap;
        Fill->SetCubemap(LoadObject<UTextureCube>(nullptr,TEXT("/Game/WonderChess/VNext/Characters/Silkmother_r003/Environment/T_NeutralLightCube")));
        Fill->SetIntensity(1.5);Fill->SetCastShadows(false);
    }
    SceneActors.Add(Sky);
    if(Courtyard)BuildCourtyard(Ground,Light,Sky);
    Camera = GetWorld()->SpawnActor<ACameraActor>();
    Camera->GetCameraComponent()->SetProjectionMode(Storybook?ECameraProjectionMode::Perspective:ECameraProjectionMode::Orthographic);
    if(Storybook)Camera->GetCameraComponent()->SetFieldOfView(34);
    auto& Exposure=Camera->GetCameraComponent()->PostProcessSettings;
    Exposure.bOverride_AutoExposureMethod=true;Exposure.AutoExposureMethod=EAutoExposureMethod::AEM_Manual;
    Exposure.bOverride_AutoExposureApplyPhysicalCameraExposure=true;Exposure.AutoExposureApplyPhysicalCameraExposure=false;
    Exposure.bOverride_AutoExposureBias=true;Exposure.AutoExposureBias=0;
    if(SilkmotherCandidate){Exposure.bOverride_AmbientOcclusionIntensity=true;Exposure.AmbientOcclusionIntensity=0;Exposure.bOverride_BloomIntensity=true;Exposure.BloomIntensity=0;}
    Camera->GetCameraComponent()->PostProcessBlendWeight=1;
    Camera->GetCameraComponent()->bConstrainAspectRatio = false;
    Camera->GetCameraComponent()->bOverrideAspectRatioAxisConstraint = true;
    Camera->GetCameraComponent()->SetAspectRatioAxisConstraint(AspectRatio_MaintainXFOV);
    SceneActors.Add(Camera);
    if (Controller) Controller->SetViewTarget(Camera);
    UpdateCamera();
}

FSlateRect AWCVNextLab::BoardPixelBounds() const
{
    int Width=0, Height=0;
    if(Controller)Controller->GetViewportSize(Width,Height);
    if(BoardInput&&GEngine&&GEngine->GameViewport){
        const auto Viewport=GEngine->GameViewport->GetGameViewportWidget();
        if(Viewport){
            const auto& V=Viewport->GetCachedGeometry();const auto& B=BoardInput->GetCachedGeometry();
            const FVector2D Size=V.GetLocalSize();
            if(Size.X>1&&Size.Y>1&&B.GetLocalSize().X>1){
                const FVector2D Min=V.AbsoluteToLocal(B.LocalToAbsolute(FVector2D::ZeroVector));
                const FVector2D Max=V.AbsoluteToLocal(B.LocalToAbsolute(B.GetLocalSize()));
                return FSlateRect(Min.X*Width/Size.X,Min.Y*Height/Size.Y,Max.X*Width/Size.X,Max.Y*Height/Size.Y);
            }
        }
    }
    return FSlateRect(0,95,FMath::Max(350,Width-320),FMath::Max(395,Height-105));
}
// Builds the courtyard from the basic shapes the lab already uses: paving, three curtain walls with battlements,
// corner towers, a gate, banners and braziers. The side nearest the camera stays open.
void AWCVNextLab::BuildCourtyard(AActor* Ground,ADirectionalLight* Sun,ASkyLight* Sky)
{
    const FLinearColor Wall(.36f,.34f,.31f),WallShade(.27f,.26f,.24f),Roof(.30f,.14f,.11f),
        Cloth(.09f,.19f,.46f),Brass(.60f,.45f,.16f),Soot(.05f,.045f,.04f);
    const auto Block=[&](FVector P,FVector Scale,FLinearColor Color,FRotator R=FRotator::ZeroRotator,const TCHAR* Shape=TEXT("Cube")){
        auto* Part=Mesh(Ground,Shape,P,Scale,Color,R);
        if(QuietStoneMaterial&&(Color==Wall||Color==WallShade))Part->SetMaterial(0,StoneMaterial(Color));
        return Part;
    };
    // Paving: large flagstones in three close greys so the yard does not read as one flat plane.
    Block(FVector(0,0,-36),FVector(70,70,.5),Soot)->SetCastShadow(false);
    const FLinearColor Flags[]={FLinearColor(.30f,.29f,.27f),FLinearColor(.34f,.33f,.30f),FLinearColor(.26f,.25f,.24f)};
    for(int Tint=0;Tint<3;++Tint){
        auto* Slabs=NewObject<UInstancedStaticMeshComponent>(Ground);
        Ground->AddInstanceComponent(Slabs);Slabs->SetupAttachment(Ground->GetRootComponent());
        Slabs->SetStaticMesh(ProxyMeshes.FindChecked(TEXT("Cube")));Slabs->SetMobility(EComponentMobility::Movable);
        Slabs->SetCollisionEnabled(ECollisionEnabled::NoCollision);Slabs->SetCastShadow(false);
        Slabs->SetMaterial(0,QuietStoneMaterial?StoneMaterial(Flags[Tint]):Material(Flags[Tint]));Slabs->RegisterComponent();
        for(int X=-10;X<=10;++X)for(int Y=-10;Y<=10;++Y){
            if(FMath::Abs(X)<=2&&FMath::Abs(Y)<=2)continue; // the board and its rim sit here
            if(((X*7+Y*13)%3+3)%3!=Tint)continue;
            Slabs->AddInstance(FTransform(FRotator::ZeroRotator,FVector(X*360,Y*360,-12),FVector(3.5,3.5,.2)));
        }
    }
    // Curtain walls on the far side and both flanks; +Y is the camera side.
    // Close enough that the far wall and both flanks show at the edges of the game camera.
    const double Far=-1180,Flank=1500,Height=900,Base=-10;
    const auto Curtain=[&](FVector Center,bool AlongX,double Length){
        Block(Center+FVector(0,0,Height/2+Base),AlongX?FVector(Length/100,2.6,Height/100):FVector(2.6,Length/100,Height/100),Wall);
        Block(Center+FVector(0,0,Base+70),AlongX?FVector(Length/100,3.1,1.4):FVector(3.1,Length/100,1.4),WallShade);
        const int Count=FMath::FloorToInt(Length/260);
        for(int I=0;I<Count;++I){
            const double Along=-Length/2+130+I*260;
            Block(Center+(AlongX?FVector(Along,0,0):FVector(0,Along,0))+FVector(0,0,Height+Base+55),
                AlongX?FVector(1.3,2.9,1.1):FVector(2.9,1.3,1.1),Wall);
        }
    };
    Curtain(FVector(0,Far,0),true,2*Flank);
    Curtain(FVector(-Flank,(Far+1500)/2,0),false,1500-Far);
    Curtain(FVector(Flank,(Far+1500)/2,0),false,1500-Far);
    // Round corner towers with slate roofs.
    for(int Side:{-1,1}){
        const FVector At(Side*Flank,Far,Base);
        Block(At+FVector(0,0,Height*.68),FVector(6.4,6.4,Height*1.36/100),Wall,FRotator::ZeroRotator,TEXT("Cylinder"));
        Block(At+FVector(0,0,Height*1.36+40),FVector(7.4,7.4,.8),WallShade,FRotator::ZeroRotator,TEXT("Cylinder"));
        Block(At+FVector(0,0,Height*1.36+330),FVector(7.8,7.8,5.4),Roof,FRotator::ZeroRotator,TEXT("Cone"));
    }
    // Gatehouse in the far wall: a proud block, a dark arch and a portcullis hint.
    Block(FVector(0,Far+60,Base+Height*.56),FVector(8.4,3.6,Height*1.12/100),Wall);
    Block(FVector(0,Far+245,Base+250),FVector(4.4,.3,5),Soot)->SetCastShadow(false);
    Block(FVector(0,Far+245,Base+500),FVector(4.4,.3,4.4),Soot,FRotator(0,0,90),TEXT("Cylinder"))->SetCastShadow(false);
    for(int Bar=-2;Bar<=2;++Bar)Block(FVector(Bar*70,Far+262,Base+300),FVector(.12,.12,6),WallShade)->SetCastShadow(false);
    // Banners in the Shieldbearer's blue and brass hang on the far wall and the flanks.
    const auto Banner=[&](FVector P,bool FacesY){
        Block(P,FacesY?FVector(1.9,.06,4.6):FVector(.06,1.9,4.6),Cloth)->SetCastShadow(false);
        Block(P+FVector(0,0,-205),FacesY?FVector(1.9,.07,.5):FVector(.07,1.9,.5),Brass)->SetCastShadow(false);
        Block(P+FVector(0,0,238),FacesY?FVector(2.3,.1,.14):FVector(.1,2.3,.14),Brass)->SetCastShadow(false);
    };
    for(int X:{-1050,-560,560,1050})Banner(FVector(X,Far+140,Base+420),true);
    for(int Side:{-1,1})for(int Y:{-700,0,700})Banner(FVector(Side*(Flank-140),Y,Base+420),false);
    // Braziers at the yard corners give warm local light.
    for(int X:{-1,1})for(int Y:{-1,1}){
        const FVector At(X*1180,Y*1020,Base);
        Block(At+FVector(0,0,70),FVector(.5,.5,1.4),Soot,FRotator::ZeroRotator,TEXT("Cylinder"));
        Block(At+FVector(0,0,150),FVector(1.1,1.1,.3),WallShade,FRotator::ZeroRotator,TEXT("Cylinder"));
        Block(At+FVector(0,0,190),FVector(.7,.7,.5),FLinearColor(1.f,.42f,.08f),FRotator::ZeroRotator,TEXT("Cone"))->SetCastShadow(false);
        auto* Fire=NewObject<UPointLightComponent>(Ground);
        Ground->AddInstanceComponent(Fire);Fire->SetupAttachment(Ground->GetRootComponent());
        Fire->SetRelativeLocation(At+FVector(0,0,260));Fire->bUseInverseSquaredFalloff=false;Fire->SetLightFalloffExponent(2);
        Fire->SetIntensity(2.2f);Fire->SetAttenuationRadius(1500);Fire->SetLightColor(FLinearColor(1.f,.62f,.30f));
        Fire->SetCastShadows(false);Fire->RegisterComponent();
    }
    // Late-afternoon sun with a soft opposite fill so armour and faces do not fall into black.
    Sun->SetActorRotation(FRotator(-46,-128,0));
    Sun->GetLightComponent()->SetIntensity(4.4f);Sun->GetLightComponent()->SetLightColor(FLinearColor(1.f,.93f,.82f));
    Sky->GetLightComponent()->SetIntensity(1.9f);
    // One directional light only: a second one competes with it for forward shading.
    SceneActors.Add(GetWorld()->SpawnActor<ASkyAtmosphere>());
}
// Mouse dragging during preparation. A press that selects a piece (on its board tile or in its bench slot) arms
// the drag; holding or moving away lifts the piece. Releasing over a board tile issues the same move a second
// click would.
void AWCVNextLab::EndDrag()
{
    Dragging=DragArmed=DragFromBench=false;DragCells.Reset();DragHover={-1,-1};DragGhostHero=nullptr;
    if(auto* Ghost=DragGhost.Get()){SceneActors.Remove(Ghost);Ghost->Destroy();}
    DragGhost.Reset();
}
void AWCVNextLab::BenchPressed(int Slot)
{
    if(!SoloMatch||ViewedSeat!=0||CurrentCombat()||SoloMatch->CurrentPhase()!=wc::Phase::Preparation)return;
    for(const auto& Unit:SoloMatch->Seats()[0].roster)if(!Unit.onBoard&&Unit.bench==Slot){
        SelectBench(Slot);
        if(Selected==Unit.id){DragArmed=true;DragFromBench=true;DragId=Unit.id;DragOrigin={-1,-1};DragPressedAt=Elapsed;}
        return;
    }
}
void AWCVNextLab::TickDrag()
{
    const bool Down=FSlateApplication::Get().GetPressedMouseButtons().Contains(EKeys::LeftMouseButton);
    FVector Origin,Direction;
    bool OnBoard=false;wc::Cell Hover{-1,-1};
    if(Controller&&Controller->DeprojectMousePositionToWorld(Origin,Direction)&&FMath::Abs(Direction.Z)>.0001f&&-Origin.Z/Direction.Z>0){
        DragGround=Origin+Direction*(-Origin.Z/Direction.Z);
        Hover={int(FMath::FloorToInt((DragGround.X+800)/200)),int(FMath::FloorToInt((800-DragGround.Y)/200))};
        OnBoard=Hover.column>=0&&Hover.column<8&&Hover.row>=0&&Hover.row<8;
    }
    if((Dragging||DragArmed)&&(CurrentCombat()||Selected!=DragId)){EndDrag();return;}
    if(!Dragging){
        if(DragArmed&&Down&&((OnBoard&&!(Hover==DragOrigin))||Elapsed-DragPressedAt>.18))Dragging=true;
        if(!Down)DragArmed=DragFromBench=false;
    }
    DragCells.Reset();DragHover={-1,-1};
    if(!Dragging)return;
    int Definition=-1;
    for(int Side=0;Side<2;++Side)for(const auto& Owned:Formation[Side])if(Owned.id==DragId)Definition=Owned.definition;
    if(SoloMatch)for(const auto& Owned:SoloMatch->Seats()[0].roster)if(Owned.id==DragId)Definition=Owned.definition;
    if(OnBoard&&Definition>=0){
        DragHover=Hover;
        const int Range=Catalog.units[Definition].range;
        for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column)
            if(wc::Distance({Column,Row},Hover)<=Range)DragCells.Add(Row*8+Column);
    }
    if(DragFromBench&&Definition>=0){
        if(!DragGhost.IsValid()){
            auto* Ghost=SceneActor();
            Mesh(Ghost,TEXT("Cylinder"),FVector(0,0,-58),FVector(1.16,1.16,.02),Teams[0])->SetCastShadow(false);
            const FString HeroId=Str(Catalog.units[Definition].id);
            FString Error;
            if(UWCHeroPresentationComponent::HasModel(HeroId)){
                DragGhostHero=NewObject<UWCHeroPresentationComponent>(Ghost);
                Ghost->AddInstanceComponent(DragGhostHero);DragGhostHero->SetupAttachment(Ghost->GetRootComponent());DragGhostHero->RegisterComponent();
                if(!DragGhostHero->InitializeHero(HeroId,Error)){DragGhostHero->DestroyComponent();DragGhostHero=nullptr;}
            }
            if(!DragGhostHero)Mesh(Ghost,TEXT("Sphere"),FVector(0,0,70),FVector(1.,1.,1.3),HeroColors[Definition%6]);
            Ghost->SetActorRotation(FRotator(0,180,0));
            DragGhost=Ghost;
        }
        DragGhost->SetActorLocation(FVector(DragGround.X,DragGround.Y,70));
        if(DragGhostHero)DragGhostHero->Present(nullptr,false,GetWorld()->GetDeltaSeconds());
    }
    if(!Down){
        const bool Drop=OnBoard&&!(Hover==DragOrigin);
        EndDrag();
        if(Drop){if(SoloMode)SoloCell(Hover);else EditCell(Hover,false);}
    }
}
void AWCVNextLab::UpdateCamera()
{
    if(!Camera||!Controller)return;
    int Width=0,Height=0;Controller->GetViewportSize(Width,Height);if(Width<=0||Height<=0)return;
    const FSlateRect Bounds=BoardPixelBounds();
    const FVector2D BoardSize(Bounds.Right-Bounds.Left,Bounds.Bottom-Bounds.Top);
    const FVector2D BoardCenter((Bounds.Left+Bounds.Right)*.5,(Bounds.Top+Bounds.Bottom)*.5);
    if(Storybook){
        const FVector Forward=FVector(0,-2400,Courtyard?-1650:-2200).GetSafeNormal(),Right(1,0,0),Up=FVector::CrossProduct(Forward,Right).GetSafeNormal();
        const double Tangent=FMath::Tan(FMath::DegreesToRadians(17.)),Focal=Width/(2*Tangent);
        const FVector2D DesiredCenter(BoardCenter.X,BoardCenter.Y+BoardSize.Y*.035);
        const auto CameraAt=[&](double Distance){
            const double Near=Distance+Forward.Y*800,Far=Distance-Forward.Y*800;
            const double ShiftX=(Width*.5-DesiredCenter.X)*Near/Focal;
            const double UnshiftedMid=Height*.5-Focal*.5*(Up.Y*800/Near-Up.Y*800/Far);
            const double ShiftY=(DesiredCenter.Y-UnshiftedMid)/(Focal*.5*(1/Near+1/Far));
            return -Forward*Distance+Right*ShiftX+Up*ShiftY;
        };
        const auto Project=[&](FVector Point,FVector Location){
            const FVector Relative=Point-Location;
            const double Depth=FVector::DotProduct(Relative,Forward);
            return FVector2D(Width*.5+Focal*FVector::DotProduct(Relative,Right)/Depth,
                Height*.5-Focal*FVector::DotProduct(Relative,Up)/Depth);
        };
        const auto Fits=[&](double Distance){
            const FVector Location=CameraAt(Distance);
            FVector2D Minimum(MAX_dbl,MAX_dbl),Maximum(-MAX_dbl,-MAX_dbl);
            for(int X:{-1,1})for(int Y:{-1,1}){
                const auto P=Project(FVector(X*800,Y*800,0),Location);
                Minimum.X=FMath::Min(Minimum.X,P.X);Minimum.Y=FMath::Min(Minimum.Y,P.Y);
                Maximum.X=FMath::Max(Maximum.X,P.X);Maximum.Y=FMath::Max(Maximum.Y,P.Y);
                const auto Rim=Project(FVector(X*880,Y*880,14),Location);
                if(Rim.X<Bounds.Left+4||Rim.X>Bounds.Right-4||Rim.Y<Bounds.Top+4||Rim.Y>Bounds.Bottom-4)return false;
                const auto Headroom=Project(FVector(X*780,Y*700,320),Location);
                if(Headroom.X<Bounds.Left+3||Headroom.X>Bounds.Right-3||Headroom.Y<Bounds.Top+3||Headroom.Y>Bounds.Bottom-3)return false;
            }
            return Maximum.X-Minimum.X<=BoardSize.X*.97&&Maximum.Y-Minimum.Y<=BoardSize.Y*.90;
        };
        double Low=1800,High=30000;
        for(int I=0;I<24;++I){
            const double Mid=(Low+High)*.5;
            if(Fits(Mid))High=Mid;else Low=Mid;
        }
        const FVector Location=CameraAt(High);
        Camera->SetActorLocation(Location);Camera->SetActorRotation(Forward.Rotation());
        Camera->GetCameraComponent()->SetOrthoWidth(2*High*Tangent);
        if(SanctuaryBackdrop){
            const double Depth=High+5000,PlateWidth=2*Depth*Tangent;
            SanctuaryBackdrop->SetWorldLocation(Location+Forward*Depth);
            SanctuaryBackdrop->SetWorldRotation(FRotationMatrix::MakeFromXY(Right,-Up).Rotator());
            SanctuaryBackdrop->SetWorldScale3D(FVector(PlateWidth/100,PlateWidth*Height/Width/100,1));
        }
        return;
    }
    const float WorldPerPixel=FMath::Max(1740.f/FMath::Max(1.f,float(BoardSize.X)),1640.f/FMath::Max(1.f,float(BoardSize.Y)));
    Camera->GetCameraComponent()->SetOrthoWidth(WorldPerPixel*Width);
    const FVector2D Offset=BoardCenter-FVector2D(Width,Height)*.5f;
    const FVector Target(-Offset.X*WorldPerPixel,-Offset.Y*WorldPerPixel/.818f,0);
    const FVector Location=Target+FVector(0,1900,2700);
    Camera->SetActorLocation(Location);
    Camera->SetActorRotation((Target-Location).Rotation());
}

float AWCVNextLab::WorldUnitsPerPixel(FVector Location) const
{
    int Width=0,Height=0;if(Controller)Controller->GetViewportSize(Width,Height);
    if(!Camera||Width<=0)return 2;
    const auto* View=Camera->GetCameraComponent();
    if(View->ProjectionMode==ECameraProjectionMode::Orthographic)return View->OrthoWidth/Width;
    const double Depth=FMath::Max(1.,FVector::DotProduct(Location-Camera->GetActorLocation(),Camera->GetActorForwardVector()));
    return 2*Depth*FMath::Tan(FMath::DegreesToRadians(View->FieldOfView*.5f))/Width;
}

bool AWCVNextLab::CaptureBoardProjection(TSharedRef<FJsonObject> Record) const
{
    if(!Controller||!Camera)return false;
    const auto Bounds=BoardPixelBounds();
    int Visible=0,RoundTrips=0,Corners=0;
    const auto Inside=[Bounds](FVector2D Pixel){
        return Pixel.X>Bounds.Left&&Pixel.X<Bounds.Right&&Pixel.Y>Bounds.Top&&Pixel.Y<Bounds.Bottom;
    };
    for(int Row=0;Row<Catalog.rules.rows;++Row)for(int Column=0;Column<Catalog.rules.columns;++Column){
        FVector2D Pixel;
        if(Controller->ProjectWorldLocationToScreen(Position({Column,Row}),Pixel)){
            Visible+=Inside(Pixel);
            FVector Origin,Direction;
            if(Controller->DeprojectScreenPositionToWorld(Pixel.X,Pixel.Y,Origin,Direction)&&FMath::Abs(Direction.Z)>.0001){
                const FVector Point=Origin-Direction*(Origin.Z/Direction.Z);
                RoundTrips+=FMath::FloorToInt((Point.X+800)/200)==Column&&FMath::FloorToInt((800-Point.Y)/200)==Row;
            }
        }
    }
    for(int X:{-1,1})for(int Y:{-1,1}){
        FVector2D Pixel;
        Corners+=Controller->ProjectWorldLocationToScreen(FVector(X*800,Y*800,0),Pixel)&&Inside(Pixel);
    }
    Record->SetStringField(TEXT("camera_projection"),Storybook?TEXT("perspective_34_degrees"):TEXT("orthographic"));
    Record->SetNumberField(TEXT("board_centers_visible"),Visible);
    Record->SetNumberField(TEXT("board_click_roundtrips"),RoundTrips);
    Record->SetNumberField(TEXT("board_corners_visible"),Corners);
    const bool Passed=Visible==64&&RoundTrips==64&&Corners==4;
    Record->SetBoolField(TEXT("board_projection_verified"),Passed);
    return Passed;
}

void AWCVNextLab::BuildInterface()
{
    if (!GEngine || !GEngine->GameViewport) return;
    const FSlateFontInfo BodyFont = FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 12);
    const FSlateFontInfo SmallFont = FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 10);
    const auto Button = [this, BodyFont](const FString& Label, TFunction<void()> Action) -> TSharedRef<SWidget> {
        return SNew(SButton).ContentPadding(FMargin(10,7))
            .OnClicked_Lambda([Action] { Action(); return FReply::Handled(); })
            [SNew(STextBlock).Font(BodyFont).Text(Txt(Label))];
    };
    auto PaletteBox = SNew(SVerticalBox);
    for (int Index=0; Index<FMath::Min(6, int(Catalog.units.size())); ++Index) {
        const auto& Def = Catalog.units[Index];
        if(ArtSlice&&(Storybook||Def.id=="wc_vn_shieldbearer")){
            PaletteBox->AddSlot().AutoHeight().Padding(0,2)[FWCArtSlice::MakeShopCard([this,Index]{
                const auto& Unit=Catalog.units[Index];FWCArtCardData Data;
                Data.UnitId=Str(Unit.id);Data.Name=Str(Unit.displayName);Data.Cost=Unit.cost;
                Data.Detail=Str(Unit.race)+TEXT(" / ")+Str(Unit.unitClass);
                Data.Footer=Palette==Index?TEXT("SELECTED · click an empty cell"):TEXT("LAB PALETTE · choose to place");Data.Tooltip=TEXT("Reusable shop card study. This lab palette places a test creature; it does not spend gold.");
                return Data;
            },[this,Index]{ChooseHero(Index);},[this]{return !Fight&&LoadError.IsEmpty();})];
            continue;
        }
        PaletteBox->AddSlot().AutoHeight().Padding(0,2)
        [SNew(SButton).ContentPadding(FMargin(9,7))
            .IsEnabled_Lambda([this]{ return !Fight; })
            .ButtonColorAndOpacity_Lambda([this,Index]{return Palette==Index?FLinearColor(.26f,.42f,.34f):FLinearColor(.10f,.15f,.16f);})
            .OnClicked_Lambda([this,Index]{ChooseHero(Index);return FReply::Handled();})
            [SNew(STextBlock).Font(BodyFont).ColorAndOpacity(Paper)
                .Text(Txt(FString::Printf(TEXT("%d  %s"),Index+1,*Str(Def.displayName.empty()?Def.name:Def.displayName))))]];
    }
    auto Controls = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5,5));
    Controls->AddSlot()[Button(TEXT("Start"), [this]{Start();})];
    Controls->AddSlot()[Button(TEXT("Pause / Resume"), [this]{TogglePause();})];
    Controls->AddSlot()[Button(TEXT("Step 1 tick"), [this]{Step();})];
    Controls->AddSlot()[Button(TEXT("Reset to formation"), [this]{Reset();})];
    Controls->AddSlot()[Button(TEXT("Replay same seed"), [this]{Start(true);})];
    Controls->AddSlot()[Button(TEXT("Status effect test"), [this]{StartStatusTest();})];
    auto Scenarios = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(4,4));
    Scenarios->AddSlot()[Button(TEXT("Next scenario"),[this]{NextScenario();})];
    Scenarios->AddSlot()[Button(TEXT("Formation A"),[this]{LoadScenarioVariant(false);})];
    Scenarios->AddSlot()[Button(TEXT("Formation B"),[this]{LoadScenarioVariant(true);})];
    Scenarios->AddSlot()[Button(TEXT("Compare A/B"),[this]{CompareScenario();})];
    Scenarios->AddSlot()[Button(TEXT("Mirror current"),[this]{MirrorFormation();})];
    Scenarios->AddSlot()[Button(TEXT("Save formation"),[this]{SaveFormationScenario();})];
    Scenarios->AddSlot()[Button(TEXT("Load formation"),[this]{LoadFormationScenario();})];
    const auto EditEnabled = [this]{return !Fight && LoadError.IsEmpty();};
    auto Sidebar = SNew(SScrollBox)
    +SScrollBox::Slot().Padding(12,10)
    [SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,7)
        [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),17)).ColorAndOpacity(Gold).Text(Txt(TEXT("FORMATION WORKBENCH")))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,7)
        [ArtSlice?FWCArtSlice::MakeStudyPanel([this]{
            int Definition=Palette;
            if(const auto* Combat=CurrentCombat()){for(const auto& Unit:Combat->Units())if(Unit.id==Selected&&!Unit.neutral){Definition=Unit.definition;break;}}
            else if(const auto* Unit=SelectedPiece())Definition=Unit->definition;
            return Definition>=0&&Definition<int(Catalog.units.size())?Str(Catalog.units[Definition].id):FString();
        },[this]{
            int Definition=Palette;
            if(const auto* Combat=CurrentCombat()){for(const auto& Unit:Combat->Units())if(Unit.id==Selected&&!Unit.neutral){Definition=Unit.definition;break;}}
            else if(const auto* Unit=SelectedPiece())Definition=Unit->definition;
            return Definition>=0&&Definition<int(Catalog.units.size())?Str(Catalog.units[Definition].displayName):FString();
        }):SNullWidget::NullWidget]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(SmallFont).ColorAndOpacity(Paper).AutoWrapText(true)
            .Text(Txt(TEXT("COMBAT KEY\nMelee: amber slash | Ranged: traveling shot\nHeal: green + | Shield: blue shell\nStun: violet swirl | Push: cyan trail\nSelect a creature to see its target and action.")))]
        +SVerticalBox::Slot().AutoHeight()[Scenarios]
        +SVerticalBox::Slot().AutoHeight().Padding(0,7)[SNew(STextBlock).Font(SmallFont).ColorAndOpacity(Paper).AutoWrapText(true).Text_Lambda([this]{return Txt(ScenarioText());})]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(BodyFont).ColorAndOpacity(Paper).AutoWrapText(true)
            .Text(Txt(TEXT("Choose a creature, then click an empty cell. Teal half = A; coral half = B. Click a piece to inspect. Right-click removes. Ten pieces per side.")))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,8)[PaletteBox]
        +SVerticalBox::Slot().AutoHeight()[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1)[SNew(SButton).IsEnabled_Lambda(EditEnabled).OnClicked_Lambda([this]{ChangeStars();return FReply::Handled();})
                [SNew(STextBlock).Font(BodyFont).Text_Lambda([this]{return Txt(FString::Printf(TEXT("Stars: %d / 3"),BrushStar));})]]
            +SHorizontalBox::Slot().FillWidth(1).Padding(5,0)[SNew(SButton).IsEnabled_Lambda(EditEnabled).OnClicked_Lambda([this]{ChangeFacing();return FReply::Handled();})
                [SNew(STextBlock).Font(BodyFont).Text_Lambda([this]{return Txt(FString(TEXT("Face: "))+FacingName(BrushFacing));})]]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,8)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[SNew(STextBlock).Font(BodyFont).ColorAndOpacity(Paper).Text(Txt(TEXT("Seed  ")))]
            +SHorizontalBox::Slot().FillWidth(1)[SNew(SSpinBox<int32>).MinValue(1).MaxValue(MAX_int32).MinSliderValue(1).MaxSliderValue(1000000)
                .IsEnabled_Lambda(EditEnabled).Value_Lambda([this]{return Seed;}).OnValueChanged_Lambda([this](int32 Value){if(!Fight){Seed=Value;PreparationDirty=true;}})]]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(SmallFont).ColorAndOpacity(Gold).AutoWrapText(true)
            .Text(Txt(TEXT("RELIC FIXTURE · Equip directly for testing; this lab does not award or acquire relics.")))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1)[SNew(SButton).ContentPadding(FMargin(10,7)).IsEnabled_Lambda(EditEnabled)
                .ToolTipText_Lambda([this]{
                    FString Help=TEXT("Lab fixture: one relic per creature, three per team, no duplicate relic within a team.\n");
                    if(const auto* Piece=SelectedPiece())for(const auto& Relic:Catalog.relics)
                        if(wc::RelicCompatible(Relic,Catalog.units[Piece->definition].ability.mechanic))Help+=TEXT("\n")+Str(Relic.name)+TEXT(": ")+Str(Relic.description);
                    return Txt(Help);
                })
                .OnClicked_Lambda([this]{CycleRelic();return FReply::Handled();})
                [SNew(STextBlock).Font(BodyFont).Text(Txt(TEXT("Next relic")))]]
            +SHorizontalBox::Slot().AutoWidth().Padding(4,0)[Button(TEXT("Unequip"),[this]{UnequipRelic();})]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,5)[Button(TEXT("Remove selected"),[this]{RemoveSelected();})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,5)[Button(TEXT("Clear both formations"),[this]{ClearFormation();})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,10)[Button(TEXT("Six-creature mirror preset"),[this]{Preset();})]
        +SVerticalBox::Slot().AutoHeight()[SAssignNew(InspectorBlock,STextBlock).Font(BodyFont).ColorAndOpacity(Paper).AutoWrapText(true)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,12,0,4)[SNew(STextBlock).Font(BodyFont).ColorAndOpacity(Gold).Text(Txt(TEXT("LATEST AUTHORITATIVE EVENTS")))]
        +SVerticalBox::Slot().AutoHeight()[SAssignNew(EventBlock,STextBlock).Font(SmallFont).ColorAndOpacity(Paper).AutoWrapText(true)]
    ];
    BoardInput = SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(FLinearColor::Transparent)
        .OnMouseButtonDown_Lambda([this](const FGeometry&,const FPointerEvent& Event){
            if(Event.GetEffectingButton()==EKeys::LeftMouseButton || Event.GetEffectingButton()==EKeys::RightMouseButton){
                BoardClick(Event.GetEffectingButton()==EKeys::RightMouseButton);return FReply::Handled();}
            return FReply::Unhandled();});
    Interface = SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()
        [SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(FMargin(18,10))
            [SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),21)).ColorAndOpacity(Gold).Text(Txt(TEXT("WONDER CHESS  /  TACTICAL LAB")))]
                +SVerticalBox::Slot().AutoHeight().Padding(0,3)[SNew(STextBlock).Font(SmallFont).ColorAndOpacity(Paper).AutoWrapText(true)
                    .Text(Txt(SilkmotherCandidate?TEXT("Silkmother & Bellback  ·  Creature test arena  ·  Place units, start combat and compare formations."):TEXT("wonder_vnext  ·  UNAPPROVED GAMEPLAY PROXIES  ·  Formation and combat experiment; not the finished art or full tournament.")))]
                +SVerticalBox::Slot().AutoHeight()[SAssignNew(StatusBlock,STextBlock).Font(BodyFont).ColorAndOpacity(Paper).AutoWrapText(true)]]]
        +SVerticalBox::Slot().FillHeight(1)
        [SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1)
            [BoardInput.ToSharedRef()]
            +SHorizontalBox::Slot().AutoWidth()
            [SNew(SBox).WidthOverride(320)[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(0)[Sidebar]]]]
        +SVerticalBox::Slot().AutoHeight()
        [SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(FMargin(14,8))
            [SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight()[Controls]
                +SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[SAssignNew(MessageBlock,STextBlock).Font(BodyFont).ColorAndOpacity(Gold).AutoWrapText(true)]]];
    UpdateInterfaceText();
    GEngine->GameViewport->AddViewportWidgetContent(Interface.ToSharedRef(),50);
    if(Controller){FInputModeGameAndUI Input;Input.SetWidgetToFocus(Interface);Input.SetHideCursorDuringCapture(false);Controller->SetInputMode(Input);}
}

void AWCVNextLab::UpdateInterfaceText()
{
    bool Changed=false;
    const auto Assign=[&Changed](const TSharedPtr<STextBlock>& Block,const FString& Value){
        if(Block&&Block->GetText().ToString()!=Value){
            // Keep the same FText while its content is unchanged; rebuild wrapped layout only at a real update.
            Block->SetText(Txt(Value));
            Block->Invalidate(EInvalidateWidgetReason::Layout);
            Changed=true;
        }
    };
    Assign(InspectorBlock,InspectorText());Assign(EventBlock,EventText());
    Assign(StatusBlock,StatusText());Assign(MessageBlock,Message);
    if(Changed&&Interface)Interface->Invalidate(EInvalidateWidgetReason::Layout);
}

wc::OwnedUnit* AWCVNextLab::SelectedPiece()
{
    for(auto& Side:Formation)for(auto& Piece:Side)if(Piece.id==Selected)return &Piece;
    return nullptr;
}
void AWCVNextLab::ChooseHero(int Index)
{
    if(Fight)return;
    Palette=Index;Selected=0;
    Message=TEXT("Creature selected. Click an empty cell on either team's half.");
}
bool AWCVNextLab::BoardClick(bool Remove)
{
    if(!Controller||!LoadError.IsEmpty())return false;
    FVector Origin,Direction;
    if(!Controller->DeprojectMousePositionToWorld(Origin,Direction))return false;
    return BoardRayClick(Origin,Direction,Remove);
}
bool AWCVNextLab::RayImportedBounds(const FBox& Bounds,const FTransform& Transform,
    const FVector& Origin,const FVector& Direction,double& Distance)
{
    if(!Bounds.IsValid||Direction.IsNearlyZero()||Transform.GetScale3D().GetAbsMin()<UE_SMALL_NUMBER)return false;
    const FVector O=Transform.InverseTransformPosition(Origin);
    // Keep the original ray parameter through scale/rotation; do not normalize D.
    const FVector D=Transform.InverseTransformVector(Direction);
    double Near=0,Far=TNumericLimits<double>::Max();
    for(int Axis=0;Axis<3;++Axis){
        if(FMath::Abs(D[Axis])<1.e-12){if(O[Axis]<Bounds.Min[Axis]||O[Axis]>Bounds.Max[Axis])return false;continue;}
        double A=(Bounds.Min[Axis]-O[Axis])/D[Axis],B=(Bounds.Max[Axis]-O[Axis])/D[Axis];
        if(A>B)Swap(A,B);
        Near=FMath::Max(Near,A);Far=FMath::Min(Far,B);if(Near>Far)return false;
    }
    Distance=Near;return true;
}
bool AWCVNextLab::BellbackRayHit(const FVector& Origin,const FVector& Direction,uint64& Id,wc::Cell& Cell) const
{
    if(!BellbackCandidate)return false;
    const auto* Combat=CurrentCombat();
    double Nearest=TNumericLimits<double>::Max();bool Hit=false;
    for(const auto& Pair:Pieces){
        const auto& View=Pair.Value;const auto* Actor=View.Actor.Get();
        if((!View.Bellback&&!View.Silkmother&&!View.Cragstoat)||!Actor||Actor->IsHidden())continue;
        const auto* Mesh=View.Bellback?View.Bellback->GetMesh():View.Silkmother?View.Silkmother->GetMesh():View.Cragstoat->GetMesh();
        if(!Mesh||!Mesh->IsVisible()||!Mesh->GetSkeletalMeshAsset())continue;
        wc::Cell Resolved{-1,-1};bool Found=false;
        if(Combat){for(const auto& U:Combat->Units())if(U.id==Pair.Key){Resolved=U.cell;Found=true;break;}}
        else for(int Side=0;Side<2;++Side)for(const auto& U:Formation[Side])if(U.id==Pair.Key){Resolved=wc::EncounterCell(U.cell,Side,Catalog.rules);Found=true;break;}
        if(!Found)continue;
        double T=0;
        // Imported geometry bounds exclude animation padding, labels and FX.
        // Inverse-transforming the ray retains an oriented box during turns.
        if(RayImportedBounds(Mesh->GetSkeletalMeshAsset()->GetImportedBounds().GetBox(),Mesh->GetComponentTransform(),Origin,Direction,T)&&
            (T<Nearest||(T==Nearest&&Pair.Key<Id))){Nearest=T;Id=Pair.Key;Cell=Resolved;Hit=true;}
    }
    return Hit;
}
bool AWCVNextLab::BoardRayClick(const FVector& Origin,const FVector& Direction,bool Remove)
{
    if(!LoadError.IsEmpty())return false;
    uint64 HitId=0;wc::Cell HitCell{-1,-1};
    if(BellbackRayHit(Origin,Direction,HitId,HitCell)){
        if(CurrentCombat()){
            if(Remove&&!SoloMode){Message=TEXT("Combat is locked. Reset to edit the formation.");return false;}
            Selected=HitId;return true;
        }
        return SoloMode?SoloCell(HitCell):EditCell(HitCell,Remove);
    }
    if(FMath::Abs(Direction.Z)<.0001f)return false;
    const double T=-Origin.Z/Direction.Z;
    if(T<0)return false;
    const FVector P=Origin+Direction*T;
    const wc::Cell Cell{FMath::FloorToInt((P.X+800)/200),FMath::FloorToInt((800-P.Y)/200)};
    if(Cell.column<0||Cell.column>=8||Cell.row<0||Cell.row>=8)return false;
    const bool Handled=SoloMode ? SoloCell(Cell) : EditCell(Cell,Remove);
    if(Handled&&!Remove&&!CurrentCombat()&&Selected)
        for(int Side=0;Side<2;++Side)for(const auto& Owned:Formation[Side])
            if(Owned.id==Selected&&wc::EncounterCell(Owned.cell,Side,Catalog.rules)==Cell){
                DragArmed=true;DragId=Selected;DragOrigin=Cell;DragPressedAt=Elapsed;
            }
    return Handled;
}
bool AWCVNextLab::EditCell(wc::Cell Cell,bool Remove)
{
    if(Cell.column<0||Cell.column>=8||Cell.row<0||Cell.row>=8||!LoadError.IsEmpty())return false;
    if(Fight){
        if(Remove){Message=TEXT("Combat is locked. Reset to edit the formation.");return false;}
        for(const auto& Piece:Fight->Units())if(Piece.cell==Cell&&Piece.health>0){Selected=Piece.id;return true;}
        for(const auto& Piece:Fight->Units())if(Piece.cell==Cell){Selected=Piece.id;return true;}
        return false;
    }
    const int Side=Cell.row<4?0:1;
    auto& Roster=Formation[Side];
    for(auto It=Roster.begin();It!=Roster.end();++It)if(wc::EncounterCell(It->cell,Side,Catalog.rules)==Cell){
        Selected=It->id;
        if(Remove){Roster.erase(It);Selected=0;PreparationDirty=true;Message=TEXT("Piece removed.");}
        else{Palette=It->definition;BrushStar=It->star;BrushFacing=It->facing;Message=TEXT("Piece selected. Click an empty cell on its half to move; stars and facing edit it. Choose a palette entry to place another.");}
        return true;
    }
    if(Remove)return false;
    if(auto* Existing=SelectedPiece()){
        for(const auto& U:Roster)if(U.id==Existing->id){Existing->cell=wc::EncounterCell(Cell,Side,Catalog.rules);PreparationDirty=true;Message=TEXT("Formation position updated.");return true;}
        Message=TEXT("A piece stays on its own team. Choose a palette entry to place a creature on the other team.");return false;
    }
    if(Roster.size()>=10){Message=TEXT("This lab allows ten pieces per side. Remove a piece first.");return false;}
    wc::OwnedUnit Piece;
    Piece.id=NextId++;Piece.definition=Palette;Piece.star=BrushStar;Piece.facing=BrushFacing;Piece.onBoard=true;
    Piece.cell=wc::EncounterCell(Cell,Side,Catalog.rules);
    Roster.push_back(Piece);Selected=Piece.id;PreparationDirty=true;
    Message=FString::Printf(TEXT("Placed %s on team %s."),*Str(Catalog.units[Palette].displayName),Side?TEXT("B"):TEXT("A"));
    return true;
}
void AWCVNextLab::ChangeStars()
{
    if(Fight)return;
    BrushStar=BrushStar%3+1;
    if(auto* Piece=SelectedPiece())Piece->star=BrushStar;
    PreparationDirty=true;
}
void AWCVNextLab::ChangeFacing()
{
    if(Fight)return;
    BrushFacing=static_cast<wc::Facing>((int(BrushFacing)+1)%4);
    if(auto* Piece=SelectedPiece())Piece->facing=BrushFacing;
    PreparationDirty=true;
}
bool AWCVNextLab::EquipRelic(int Index)
{
    if(Fight){Message=TEXT("Relic edits are locked during combat. Reset to preparation first.");return false;}
    auto* SelectedUnit=SelectedPiece();
    if(!SelectedUnit){Message=TEXT("Select a placed creature before equipping a test relic.");return false;}
    if(Index<0||Index>=int(Catalog.relics.size())||!wc::RelicCompatible(Catalog.relics[Index],Catalog.units[SelectedUnit->definition].ability.mechanic)){
        Message=TEXT("That relic is incompatible with this creature.");return false;
    }
    for(auto& Side:Formation)for(const auto& OwnerPiece:Side)if(OwnerPiece.id==SelectedUnit->id){
        int OtherEquipped=0;
        for(const auto& Piece:Side)if(Piece.id!=SelectedUnit->id&&Piece.relic>=0){
            ++OtherEquipped;
            if(Piece.relic==Index){Message=TEXT("A relic can appear only once on each team in this fixture.");return false;}
        }
        if(OtherEquipped>=Catalog.rules.maximumRelics){Message=TEXT("Three relics are already equipped on this team. Unequip one first.");return false;}
        SelectedUnit->relic=Index;PreparationDirty=true;
        Message=TEXT("Equipped ")+Str(Catalog.relics[Index].name)+TEXT(". ")+Str(Catalog.relics[Index].description);
        return true;
    }
    return false;
}
void AWCVNextLab::CycleRelic()
{
    if(Fight){Message=TEXT("Relic edits are locked during combat.");return;}
    auto* Unit=SelectedPiece();if(!Unit){Message=TEXT("Select a placed creature to choose a compatible test relic.");return;}
    const int Current=Unit->relic;
    for(int Offset=1;Offset<=int(Catalog.relics.size());++Offset){
        const int Index=(Current+Offset)%Catalog.relics.size();
        if(wc::RelicCompatible(Catalog.relics[Index],Catalog.units[Unit->definition].ability.mechanic)&&EquipRelic(Index))return;
    }
    Message=TEXT("No compatible free relic slot. Maximum three equipped per team, one per creature, no duplicate relic on a team.");
}
void AWCVNextLab::UnequipRelic()
{
    if(Fight){Message=TEXT("Relic edits are locked during combat.");return;}
    if(auto* Piece=SelectedPiece()){Piece->relic=-1;PreparationDirty=true;Message=TEXT("Test relic unequipped. Base ability restored.");}
    else Message=TEXT("Select a placed creature first.");
}
void AWCVNextLab::RemoveSelected()
{
    if(Fight){Message=TEXT("Reset to preparation before changing either team.");return;}
    for(auto& Side:Formation)for(auto It=Side.begin();It!=Side.end();++It)if(It->id==Selected){Side.erase(It);Selected=0;PreparationDirty=true;return;}
    Message=TEXT("Click a piece before removing it.");
}
void AWCVNextLab::ClearFormation()
{
    if(Fight){Message=TEXT("Reset to preparation before clearing either team.");return;}
    Formation[0].clear();Formation[1].clear();Selected=0;PreparationDirty=true;
    Message=TEXT("Empty formation. Choose a creature and place at least one on each side.");
}
void AWCVNextLab::Preset()
{
    if(Fight||!LoadError.IsEmpty()||Catalog.units.size()<6)return;
    ClearFormation();BrushStar=1;BrushFacing=wc::Facing::Forward;
    const wc::Cell Layout[]={{1,2},{3,1},{1,1},{2,3},{5,0},{5,3}};
    for(int Side=0;Side<2;++Side)for(int Hero=0;Hero<6;++Hero){ChooseHero(Hero);EditCell(wc::EncounterCell(Layout[Hero],Side,Catalog.rules),false);}
    Selected=Formation[0][0].id;Palette=0;
    Message=TEXT("Six distinct pilot creatures per team. Edit freely before Start; no combat commands are accepted during a fight.");
}
bool AWCVNextLab::Start(bool FromReplay)
{
    if(StatusTest){Reset();FromReplay=false;}
    if(!LoadError.IsEmpty())return false;
    if(FromReplay){
        if(ReplayFormation[0].empty()||ReplayFormation[1].empty()){Message=TEXT("Start a battle first to record its replay inputs.");return false;}
        Formation=ReplayFormation;Seed=ReplaySeed;
    }else{
        if(Fight){Message=TEXT("Reset to edit, or use Replay for the identical starting formation and seed.");return false;}
        if(Formation[0].empty()||Formation[1].empty()){Message=TEXT("Place at least one creature on each side before Start.");return false;}
        ReplayFormation=Formation;ReplaySeed=Seed;
    }
    ++BellbackGeneration;
    Fight=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
    Paused=false;Accumulator=0;Selected=0;CombatInvariantFailed=false;
    Message=FromReplay?TEXT("Replaying the exact saved formation and seed through authoritative combat."):TEXT("Combat running. Gold outlines show the core's actual pending skill cells. Formation is locked.");
    UE_LOG(LogTemp,Display,TEXT("WC_VNEXT_LAB_START seed=%d a=%d b=%d replay=%d"),Seed,int(Formation[0].size()),int(Formation[1].size()),FromReplay);
    return true;
}
void AWCVNextLab::TogglePause(){if(Fight&&!Fight->Result().complete&&!CombatInvariantFailed){Paused=!Paused;Message=Paused?TEXT("Paused. Step advances exactly one authoritative tick."):TEXT("Combat resumed.");}}
void AWCVNextLab::Step(){if(!Fight&&!Start())return;Paused=true;Advance();}
void AWCVNextLab::Reset(){Fight.reset();StatusTest=false;StatusTestCatalog.reset();Paused=false;Accumulator=0;Selected=0;CombatInvariantFailed=false;PreparationDirty=true;ClearUpgradePresentation();Message=TEXT("Preparation restored. Both original formations are editable.");}
void AWCVNextLab::Advance()
{
    if(!Fight||Fight->Result().complete||CombatInvariantFailed)return;
    Fight->Tick();
    const FString Error=Str(Fight->InvariantError());
    if(!Error.IsEmpty()){
        Paused=true;CombatInvariantFailed=true;Message=TEXT("Combat invariant failed: ")+Error;
        UE_LOG(LogTemp,Error,TEXT("WC_VNEXT_LAB_INVARIANT %s"),*Error);
        if(Exercise&&ExerciseChecks){ExerciseChecks->SetBoolField(TEXT("every_observed_tick_invariants"),false);ExerciseChecks->SetStringField(TEXT("first_invariant_error"),Error);WriteEvidence(false);ExerciseDone=true;}
        return;
    }
    if(Fight->Result().complete){
        const auto& R=Fight->Result();
        Message=FString::Printf(TEXT("%s%s. %d ticks, %d authoritative events. Reset to change your plan; Replay repeats it."),R.winner<0?TEXT("Draw"):R.winner?TEXT("Team B wins"):TEXT("Team A wins"),R.timeout?TEXT(" · timeout adjudication"):TEXT(""),R.ticks,int(Fight->Events().size()));
        UE_LOG(LogTemp,Display,TEXT("WC_VNEXT_LAB_RESULT winner=%d timeout=%d ticks=%d events=%d signature=%s"),R.winner,R.timeout,R.ticks,int(Fight->Events().size()),*Signature());
    }
}

void AWCVNextLab::AddPieceView(uint64 Id,int Definition,int Side,bool Neutral)
{
    auto* Actor=SceneActor();
    const FLinearColor Color=HeroColors[Definition%6];
    auto* TeamBase=Mesh(Actor,TEXT("Cylinder"),FVector(0,0,13),FVector(1.16,1.16,.13),Teams[Side]);
    Mesh(Actor,TEXT("Cone"),FVector(0,54,27),FVector(.20,.20,.44),Paper,FRotator(0,0,-90));
    const auto Part=[&](const TCHAR* Shape,FVector P,FVector Scale,FLinearColor C,FRotator R=FRotator::ZeroRotator){return Mesh(Actor,Shape,P,Scale,C,R);};
    UWCBellbackPresentationComponent* Bellback=nullptr;
    UWCSilkmotherPresentationComponent* Silkmother=nullptr;
    UWCCragstoatPresentationComponent* CragProduction=nullptr;
    USkeletalMeshComponent* Cragstoat=nullptr;
    // Imported race/class hero models replace the proxy shapes wherever one is listed.
    UWCHeroPresentationComponent* Hero=nullptr;
    const FString HeroId=Str(Catalog.Definition(Definition,Neutral).id);
    if(!Neutral&&!BellbackCandidate&&UWCHeroPresentationComponent::HasModel(HeroId)){
        Hero=NewObject<UWCHeroPresentationComponent>(Actor);
        Actor->AddInstanceComponent(Hero);Hero->SetupAttachment(Actor->GetRootComponent());Hero->RegisterComponent();
        Hero->SetRelativeLocation(FVector(0,0,6));
        FString Error;
        if(Hero->InitializeHero(HeroId,Error)){
            TeamBase->SetRelativeLocation(FVector(0,0,6.1));TeamBase->SetRelativeScale3D(FVector(1.16,1.16,.001));
            Hero->GetMesh()->AddTickPrerequisiteActor(this);
        }else{UE_LOG(LogTemp,Warning,TEXT("WC_HERO_MODEL_REJECTED %s"),*Error);Hero->DestroyComponent();Hero=nullptr;}
    }
    if(BellbackCandidate&&!Neutral&&Catalog.Definition(Definition,false).id=="wc_vn_shieldbearer"){
        Bellback=NewObject<UWCBellbackPresentationComponent>(Actor);
        Actor->AddInstanceComponent(Bellback);Bellback->SetupAttachment(Actor->GetRootComponent());Bellback->RegisterComponent();
        Bellback->SetRelativeLocation(FVector(0,0,6));
        TeamBase->SetRelativeLocation(FVector(0,0,6.1));TeamBase->SetRelativeScale3D(FVector(1.16,1.16,.001));
        FString Error;if(!Bellback->InitializeCandidate(Error)){LoadError=Error;UE_LOG(LogTemp,Error,TEXT("WC_BELLBACK_REJECTED %s"),*Error);return;}
        Bellback->GetMesh()->AddTickPrerequisiteActor(this);
    }
    if(SilkmotherCandidate&&!Neutral&&Catalog.Definition(Definition,false).id=="wc_vn_soul_jailer"){
        Silkmother=NewObject<UWCSilkmotherPresentationComponent>(Actor);
        Actor->AddInstanceComponent(Silkmother);Silkmother->SetupAttachment(Actor->GetRootComponent());Silkmother->RegisterComponent();
        Silkmother->SetRelativeLocation(FVector(0,0,6));
        TeamBase->SetRelativeLocation(FVector(0,0,6.1));TeamBase->SetRelativeScale3D(FVector(1.16,1.16,.001));
        FString Error;if(!Silkmother->InitializeCandidate(Error)){LoadError=Error;UE_LOG(LogTemp,Error,TEXT("WC_SILKMOTHER_REJECTED %s"),*Error);return;}
        Silkmother->GetMesh()->AddTickPrerequisiteActor(this);
    }
    if(CragstoatPreview&&!Neutral&&Catalog.Definition(Definition,false).id=="wc_vn_boar_rusher"){
        Cragstoat=NewObject<USkeletalMeshComponent>(Actor);
        Actor->AddInstanceComponent(Cragstoat);Cragstoat->SetupAttachment(Actor->GetRootComponent());
        Cragstoat->SetSkeletalMeshAsset(CragstoatPreviewMesh);
        Cragstoat->SetMaterial(0,CragstoatPreviewMaterial);
        Cragstoat->SetRelativeLocation(FVector(0,0,6.3)); // Bind-pose minimum Z is 0; tile surface is Z 6.
        Cragstoat->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Cragstoat->SetCastShadow(false);
        Cragstoat->RegisterComponent();
        TeamBase->SetRelativeLocation(FVector(0,0,6.1));TeamBase->SetRelativeScale3D(FVector(1.16,1.16,.001));
        UE_LOG(LogTemp,Display,TEXT("WC_CRAGSTOAT_PREVIEW_SPAWN unit=%llu skeletal=1 rest_pose=1"),Id);
    }
    if(CragstoatCandidate&&!Neutral&&Catalog.Definition(Definition,false).id=="wc_vn_boar_rusher"){
        CragProduction=NewObject<UWCCragstoatPresentationComponent>(Actor);
        Actor->AddInstanceComponent(CragProduction);CragProduction->SetupAttachment(Actor->GetRootComponent());CragProduction->RegisterComponent();
        CragProduction->SetRelativeLocation(FVector(0,0,6.3));
        TeamBase->SetRelativeLocation(FVector(0,0,6.1));TeamBase->SetRelativeScale3D(FVector(1.16,1.16,.001));
        FString Error;if(!CragProduction->InitializeCandidate(Error)){LoadError=Error;UE_LOG(LogTemp,Error,TEXT("WC_CRAGSTOAT_REJECTED %s"),*Error);return;}
        CragProduction->GetMesh()->AddTickPrerequisiteActor(this);
    }
    if(!Bellback&&!Silkmother&&!Cragstoat&&!CragProduction&&!Hero)switch(Definition%6){
    case 0:
        Part(TEXT("Sphere"),FVector(0,0,62),FVector(1.18,1.35,.78),Color);
        Part(TEXT("Cylinder"),FVector(0,0,111),FVector(.40,.40,.15),Gold);
        Part(TEXT("Sphere"),FVector(0,57,46),FVector(.48,.55,.40),Color*.75f);
        for(int X:{-1,1})for(int Y:{-1,1})Part(TEXT("Cube"),FVector(X*38,Y*38,28),FVector(.25,.32,.36),Color*.65f);
        break;
    case 1:
        Part(TEXT("Sphere"),FVector(0,0,53),FVector(.68,1.37,.58),Color);
        Part(TEXT("Sphere"),FVector(0,66,66),FVector(.58,.61,.54),Color);
        for(int X:{-1,1})for(int Y:{-1,1})Part(TEXT("Cube"),FVector(X*24,Y*43,31),FVector(.17,.21,.45),Color*.7f);
        Part(TEXT("Cone"),FVector(0,-79,49),FVector(.32,.32,.90),Color,FRotator(-75,0,0));
        Part(TEXT("Cone"),FVector(-20,66,105),FVector(.22,.22,.35),Gold);
        Part(TEXT("Cone"),FVector(20,66,105),FVector(.22,.22,.35),Gold);
        break;
    case 2:
        Part(TEXT("Cone"),FVector(0,0,59),FVector(.85,.85,1.1),FLinearColor(.34f,.23f,.14f));
        for(int I=0;I<5;++I){const float Angle=I*2*PI/5;Part(TEXT("Sphere"),FVector(FMath::Cos(Angle)*40,FMath::Sin(Angle)*40,105),FVector(.75,.75,.60),Color);}
        Part(TEXT("Sphere"),FVector(0,0,142),FVector(.65,.65,.65),Color*1.1f);
        break;
    case 3:
        for(int I=0;I<5;++I){const float A=I*.95f;Part(TEXT("Sphere"),FVector(FMath::Cos(A)*30,FMath::Sin(A)*30,28+I*15),FVector(.44,.44,.46),Color);}
        Part(TEXT("Cone"),FVector(0,38,108),FVector(.76,.92,.43),Color,FRotator(35,0,0));
        Part(TEXT("Cone"),FVector(0,50,97),FVector(.60,.74,.22),Gold,FRotator(-25,0,180));
        break;
    case 4:
        for(int I=-1;I<=1;++I)Part(TEXT("Cube"),FVector(I*36,0,92+FMath::Abs(I)*14),FVector(.34,.34,.85),Color,FRotator(0,45,0));
        Part(TEXT("Sphere"),FVector(0,0,43),FVector(.48,.48,.32),Gold);
        Part(TEXT("Cone"),FVector(0,0,146),FVector(.43,.43,.53),Color);
        break;
    case 5:
        Part(TEXT("Sphere"),FVector(0,0,111),FVector(1.10,1.05,.65),Color);
        for(int I=0;I<6;++I){const float Angle=I*PI/3;Part(TEXT("Cylinder"),FVector(FMath::Cos(Angle)*34,FMath::Sin(Angle)*34,62),FVector(.12,.12,.71),Color*.75f,FRotator(10*FMath::Cos(Angle),0,10*FMath::Sin(Angle)));}
        Part(TEXT("Sphere"),FVector(0,40,110),FVector(.19,.19,.19),Gold);
        break;
    }
    const float Lift=Hero?Hero->LabelHeight()-205:0; // Taller imported heroes push their bars and label up.
    auto* Bar=Mesh(Actor,TEXT("Cube"),FVector(0,0,Cragstoat?137:176+Lift),FVector(1.12,.065,.065),Teams[Side]);
    Bar->SetCastShadow(false);
    auto* Backing=Mesh(Actor,TEXT("Cube"),FVector(0,0,Cragstoat?181:220+Lift),FVector(.03,1.4,.5),FLinearColor(.015f,.022f,.026f));
    Backing->SetCastShadow(false);
    auto* Label=NewObject<UTextRenderComponent>(Actor);
    Actor->AddInstanceComponent(Label);Label->SetupAttachment(Actor->GetRootComponent());
    // The candidate's measured posed crown reaches 212 cm including board height.
    // Leave space for the label's lower half instead of covering the bell crown.
    Label->SetRelativeLocation(FVector(0,0,Bellback?250:Cragstoat?175:Silkmother?170:205+Lift));Label->SetHorizontalAlignment(EHTA_Center);Label->SetVerticalAlignment(EVRTA_TextCenter);Label->SetWorldSize(32);
    Label->SetTextRenderColor(FColor(236,242,217));Label->SetCastShadow(false);Label->RegisterComponent();
    auto* ManaBar=Mesh(Actor,TEXT("Cube"),FVector(0,0,Cragstoat?125:164+Lift),FVector(.001,.045,.045),FLinearColor(.15,.55,1.0));
    ManaBar->SetCastShadow(false);ManaBar->SetVisibility(false);
    Pieces.Add(Id,FPieceView{Actor,Bar,Backing,Label,Definition,Side});
    Pieces.FindChecked(Id).Mana=ManaBar;
    Pieces.FindChecked(Id).Bellback=Bellback;
    Pieces.FindChecked(Id).Hero=Hero;
    Pieces.FindChecked(Id).Silkmother=Silkmother;
    Pieces.FindChecked(Id).Cragstoat=CragProduction;
    Pieces.FindChecked(Id).CragstoatPreview=Cragstoat;
    if(ArtSlice){
        auto& View=Pieces.FindChecked(Id);
        const auto Unlit=[this](UStaticMeshComponent* Component,FLinearColor Tint){
            auto* Instance=UMaterialInstanceDynamic::Create(CombatCueMaterial,this);
            Instance->SetVectorParameterValue(TEXT("Color"),Tint);Component->SetMaterial(0,Instance);
            Component->SetCastShadow(false);
        };
        View.HealthTrack=Part(TEXT("Cube"),FVector::ZeroVector,FVector(.02),Ink);
        View.ManaTrack=Part(TEXT("Cube"),FVector::ZeroVector,FVector(.02),Ink);
        Unlit(View.HealthTrack,FLinearColor(.035f,.055f,.05f));Unlit(View.ManaTrack,FLinearColor(.035f,.055f,.05f));
        Unlit(Bar,Teams[Side]);Unlit(ManaBar,FLinearColor(.22f,.62f,.83f));
        Unlit(Backing,FLinearColor(.035f,.055f,.05f));
        for(int I=0;I<3;++I){
            auto* Pip=Part(TEXT("Cube"),FVector::ZeroVector,FVector(.02),Gold);
            Unlit(Pip,FLinearColor(.78f,.61f,.32f));View.TierPips.Add(Pip);
        }
    }
}

void AWCVNextLab::UpdatePreparationPreview()
{
    PreparationCells.Reset();PreparationRecipient=0;PreparationHint.Empty();
    if(CurrentCombat())return;
    if(PreparationDirty){
        PreparationState=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
        PreparationDirty=false;
    }
    if(!PreparationState||!Selected)return;
    const wc::CombatUnit* Source=nullptr;
    for(const auto& Unit:PreparationState->Units())if(OwnedId(Unit.id)==Selected){Source=&Unit;break;}
    if(!Source)return;
    const wc::Cell Directions[]={{0,1},{1,0},{0,-1},{-1,0}};
    const wc::Cell Direction=Directions[int(Source->facing)];
    const auto& Ability=Source->ability;
    if(Ability.mechanic==wc::AbilityMechanic::DirectionalGuard){
        for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column){
            const int X=Column-Source->cell.column,Y=Row-Source->cell.row;
            const int Behind=-(X*Direction.column+Y*Direction.row);
            if(Behind>0&&FMath::Abs(X*Direction.row-Y*Direction.column)<=Behind&&wc::Distance({Column,Row},Source->cell)<=Ability.radius)
                PreparationCells.Add(Row*8+Column);
        }
        const wc::CombatUnit* Recipient=nullptr;
        int NearestDistance=MAX_int32,NearestCount=0;
        for(const auto& Unit:PreparationState->Units())if(Unit.side==Source->side&&Unit.id!=Source->id&&PreparationCells.Contains(Unit.cell.row*8+Unit.cell.column)){
            const int Distance=wc::Distance(Source->cell,Unit.cell);
            if(Distance<NearestDistance){NearestDistance=Distance;NearestCount=1;}
            else if(Distance==NearestDistance)++NearestCount;
            if(!Recipient||std::make_tuple(wc::Distance(Source->cell,Unit.cell),Unit.initiative)<std::make_tuple(wc::Distance(Source->cell,Recipient->cell),Recipient->initiative))Recipient=&Unit;
        }
        const bool UnresolvedTie=SoloMode&&NearestCount>1;
        if(UnresolvedTie)Recipient=nullptr;
        PreparationRecipient=Recipient?OwnedId(Recipient->id):0;
        PreparationHint=TEXT("Spatial intent: teal = eligible rear cells. ");
        PreparationHint+=UnresolvedTie?TEXT("Several allies share the nearest distance. Actual encounter initiative resolves that tie at combat start. "):
            Recipient?TEXT("Gold = current eligible ally, ")+Str(Catalog.units[Recipient->definition].displayName)+TEXT(". "):TEXT("No ally currently occupies them. ");
        PreparationHint+=TEXT("Protection still requires damage arriving from the front at resolution; movement can change the recipient.");
    }else if(Ability.mechanic==wc::AbilityMechanic::TidalPush){
        for(int Distance=1;Distance<=Ability.range;++Distance){
            const wc::Cell Cell{Source->cell.column+Direction.column*Distance,Source->cell.row+Direction.row*Distance};
            if(Cell.column<0||Cell.column>=8||Cell.row<0||Cell.row>=8)break;
            PreparationCells.Add(Cell.row*8+Cell.column);
        }
        PreparationHint=TEXT("Spatial intent: the facing lane at this position. A future cast commits its actual cells; it is not a predicted hit or winner.");
    }
}

void AWCVNextLab::UpdatePresentation(float DeltaSeconds)
{
    const auto* Combat = CurrentCombat();
    if(BellbackCandidate){
        if(Combat!=BellbackCombat||(Combat&&Combat->CurrentTick()<BellbackPreviousTick)){
            ++BellbackGeneration;BellbackCombat=Combat;BellbackClock=Combat?Combat->CurrentTick()*Catalog.rules.tickMs/1000.:0;
        }
        BellbackPreviousTick=Combat?Combat->CurrentTick():-1;
        if(Combat&&!Combat->Result().complete)BellbackClock=Combat->CurrentTick()*Catalog.rules.tickMs/1000.+
            ((SoloMode?SoloPaused:Paused)||CapturePhase!=ECapturePhase::None?0:FMath::Clamp(Accumulator,0.,Catalog.rules.tickMs/1000.));
        else if(CapturePhase==ECapturePhase::None)BellbackClock+=DeltaSeconds;
    }
    if(Combat!=DefeatClockCombat||(Combat&&Combat->CurrentTick()!=DefeatClockTick)){
        DefeatClockCombat=Combat;
        DefeatClockTick=Combat?Combat->CurrentTick():-1;
        DefeatClockHeldAt=Elapsed;
    }
    UpdatePreparationPreview();
    TSet<uint64> Alive;
    const auto Present=[&](uint64 Id,int Def,int Side,int Star,wc::Cell Cell,wc::Facing Facing,wc::Int Health,wc::Int MaxHealth,wc::ActionState State,bool Neutral){
        const float PixelWorld=WorldUnitsPerPixel(Position(Cell)+FVector(0,0,220));
        Alive.Add(Id);
        if(const auto* Existing=Pieces.Find(Id);Existing&&(Existing->Definition!=Def||Existing->Side!=Side||Existing->Neutral!=Neutral)){
            if(auto* OldActor=Existing->Actor.Get()){SceneActors.Remove(OldActor);OldActor->Destroy();}
            Pieces.Remove(Id);
        }
        if(!Pieces.Contains(Id))AddPieceView(Id,Def,Side,Neutral);
        if(!Pieces.Contains(Id))return;
        auto& View=Pieces.FindChecked(Id);
        const bool Imported=View.Bellback||View.Silkmother||View.Cragstoat||View.CragstoatPreview||View.Hero;
        View.Neutral=Neutral;
        auto* Actor=View.Actor.Get();if(!Actor)return;
        float DefeatProgress=0;
        if(Storybook&&Combat&&Health<=0&&!Imported){
            const auto Defeated=std::find_if(Combat->Units().begin(),Combat->Units().end(),[&](const auto& Unit){return Unit.id==Id;});
            if(Defeated!=Combat->Units().end())DefeatProgress=FMath::Clamp(DefeatAge(*Defeated)/.72f,0.f,1.f);
        }
        Actor->SetActorHiddenInGame((!Imported&&Storybook&&Health<=0&&DefeatProgress>=1)||
            (View.CragstoatPreview&&Combat&&Health<=0));
        FVector Target=Position(Cell);
        // A dragged piece follows the cursor, lifted off the board.
        if(Dragging&&!Combat&&Id==DragId)Target=FVector(DragGround.X,DragGround.Y,70);
        if(Combat&&Health>0){
            const auto Found=std::find_if(Combat->Units().begin(),Combat->Units().end(),[&](const wc::CombatUnit& U){return U.id==Id;});
            if(Found!=Combat->Units().end()){
                const auto& U=*Found;const auto& D=Catalog.Definition(Def,Neutral);
                if(State==wc::ActionState::Moving&&U.destination.column>=0){
                    const int Duration=wc::MovementInterval(D.movementRate,U.movementBonus,Catalog.rules);
                    const double FractionalTick=Imported&&!(SoloMode?SoloPaused:Paused)&&CapturePhase==ECapturePhase::None?
                        FMath::Clamp(Accumulator*1000/Catalog.rules.tickMs,0.,1.):0;
                    const float Progress=FMath::Clamp(1.f-float(U.movementTick-Combat->CurrentTick()-FractionalTick)/Duration,0.f,1.f);
                    Target=FMath::Lerp(Target,Position(U.destination),Progress);
                }
                if(!Imported&&(State==wc::ActionState::AttackWindup||State==wc::ActionState::AttackRecovery)&&U.target>=0){
                    const auto& Enemy=Combat->Units()[U.target];
                    const float SinceRelease=(Combat->CurrentTick()-U.releaseTick)*Catalog.rules.tickMs/1000.f;
                    const float Motion=SinceRelease<0?-10.f:FMath::Max(0.f,1-SinceRelease/.22f)*22;
                    Target+=(Position(Enemy.cell)-Position(Cell)).GetSafeNormal2D()*Motion;
                }
                if(Def%6==4||Def%6==5)Target.Z=FMath::Sin(Combat->CurrentTick()*.1+Id)*5;
            }
        }
        const FVector Location=Combat&&!Imported?FMath::VInterpTo(Actor->GetActorLocation(),Target,DeltaSeconds,18):Target;
        Actor->SetActorLocation(Location);
        Actor->SetActorRotation(FRotator(0,int(Facing)*90+180,!Imported&&Storybook&&Health<=0?DefeatProgress*22:0));
        const float Remaining=FMath::Max(.001f,1-DefeatProgress*DefeatProgress);
        Actor->SetActorScale3D(Health>0||Imported?FVector(1):Storybook?
            FVector(Remaining,Remaining,Remaining*FMath::Lerp(1.f,.18f,DefeatProgress)):FVector(1,1,.22));
        if(Imported){
            FWCBellbackFrame Frame;Frame.Generation=BellbackGeneration;Frame.Combat=Combat;Frame.Id=Id;Frame.Side=Side;
            Frame.Facing=int(Facing);Frame.TickMs=Catalog.rules.tickMs;Frame.Clock=BellbackClock;Frame.DeltaSeconds=DeltaSeconds;
            Frame.Paused=SoloMode?SoloPaused:Paused;Frame.AllowSound=CreatureSoundEnabled&&CapturePhase==ECapturePhase::None;
            if(Combat)for(const auto& U:Combat->Units())if(U.id==Id){Frame.Unit=&U;break;}
            if(View.Hero)View.Hero->Present(Frame.Unit,Frame.Paused,DeltaSeconds);
            else if(View.Bellback)View.Bellback->Present(Frame);
            else if(View.Silkmother)View.Silkmother->Present(Frame);
            else if(View.Cragstoat)View.Cragstoat->Present(Frame);
        }
        const float Fraction=MaxHealth>0?FMath::Clamp(float(double(Health)/MaxHealth),0.f,1.f):1;
        View.Health->SetRelativeScale3D(FVector(Fraction*1.12,.065,.065));
        View.Health->SetWorldRotation(FRotator::ZeroRotator);
        View.Health->SetVisibility(Health>0);
        int Mana=0,MaximumMana=0;
        if(Combat){for(const auto& U:Combat->Units())if(U.id==Id){Mana=U.mana;MaximumMana=U.ability.mana.maximum;break;}}
        else if(!Neutral){MaximumMana=Catalog.units[Def].ability.mana.maximum;Mana=Catalog.units[Def].ability.mana.starting;}
        View.Mana->SetVisibility(Health>0&&MaximumMana>0);
        View.Mana->SetRelativeScale3D(FVector(FMath::Max(.015f,MaximumMana>0?float(Mana)/MaximumMana*1.12f:0.f),.045,.045));
        View.Mana->SetWorldRotation(FRotator::ZeroRotator);
        const auto& Definition = Catalog.Definition(Def, Neutral);
        FString Name=Str(Definition.displayName.empty()?Definition.name:Definition.displayName);
        if(Definition.id=="wc_vn_grove_druid")Name=TEXT("Druid");
        if(Definition.id=="wc_vn_prism_scholar")Name=TEXT("Scholar");
        const TCHAR* Reach=Definition.projectileTravelMs>0?TEXT("Ranged"):TEXT("Melee");
        const FString ManaLabel=!ArtSlice&&MaximumMana>0?FString::Printf(TEXT("\nMana %.0f/100"),Mana/100.):FString();
        View.Label->SetText(Txt(ArtSlice?Name:
            FString::Printf(TEXT("%s\n%s *%d %s%s"),*Name,Side?TEXT("B"):TEXT("A"),Star,Reach,*ManaLabel)));
        View.Label->SetWorldSize(PixelWorld*(ArtSlice?14:18));
        const float LabelWidth=View.Label->GetTextLocalSize().Y;
        const float MaximumLabelWidth=Catalog.rules.tileSizeCm*(ArtSlice?.78f:.90f);
        if(LabelWidth>MaximumLabelWidth)View.Label->SetWorldSize(PixelWorld*(ArtSlice?14:18)*(MaximumLabelWidth/LabelWidth));
        View.Label->SetVisibility(Health>0);
        View.LabelBacking->SetVisibility(Health>0);
        if(Camera){
            const FRotator Rotation=(-Camera->GetActorForwardVector()).Rotation();
            View.Label->SetWorldRotation(Rotation);
            const FVector Size=View.Label->GetTextLocalSize();
            View.LabelBacking->SetWorldRotation(Rotation);
            View.LabelBacking->SetWorldLocation(View.Label->GetComponentLocation()-Rotation.Vector()*3);
            View.LabelBacking->SetWorldScale3D(FVector(.03,(Size.Y+PixelWorld*8)/100,(Size.Z+PixelWorld*4)/100));
            if(MaximumMana>0){
                View.Mana->SetWorldRotation(Rotation);
                View.Mana->SetWorldLocation(View.Label->GetComponentLocation()+Rotation.RotateVector(FVector(2,0,Size.Z*.5f+PixelWorld*5)));
                View.Mana->SetWorldScale3D(FVector(.02,FMath::Max(.015f,float(Mana)/MaximumMana)*MaximumLabelWidth/100,PixelWorld*4/100));
            }
            if(ArtSlice){
                const float BarWidth=FMath::Min(MaximumLabelWidth,PixelWorld*66);
                const FVector LabelPosition=View.Label->GetComponentLocation();
                const float Top=Size.Z*.5f+PixelWorld*8;
                const auto Bar=[&](UStaticMeshComponent* Fill,UStaticMeshComponent* Track,float Value,float Z,float Pixels,bool Visible){
                    Value=FMath::Clamp(Value,0.f,1.f);
                    Track->SetWorldRotation(Rotation);
                    Track->SetWorldLocation(LabelPosition+Rotation.RotateVector(FVector(1,0,Z)));
                    Track->SetWorldScale3D(FVector(.018,(BarWidth+PixelWorld*3)/100,PixelWorld*(Pixels+2)/100));
                    Track->SetVisibility(Visible);
                    Fill->SetWorldRotation(Rotation);
                    Fill->SetWorldLocation(LabelPosition+Rotation.RotateVector(FVector(3,(Value-1)*BarWidth*.5f,Z)));
                    Fill->SetWorldScale3D(FVector(.012,FMath::Max(.0001f,Value)*BarWidth/100,PixelWorld*Pixels/100));
                    Fill->SetVisibility(Visible&&Value>0);
                };
                Bar(View.Health,View.HealthTrack,Fraction,Top,5,Health>0);
                Bar(View.Mana,View.ManaTrack,MaximumMana>0?float(Mana)/MaximumMana:0,Top+PixelWorld*8,3,Health>0&&MaximumMana>0);
                for(int I=0;I<View.TierPips.Num();++I){
                    auto* Pip=View.TierPips[I];
                    Pip->SetWorldRotation((Rotation.Quaternion()*FRotator(0,0,45).Quaternion()).Rotator());
                    Pip->SetWorldLocation(LabelPosition+Rotation.RotateVector(FVector(4,(I-(Star-1)*.5f)*PixelWorld*9,-Size.Z*.5f-PixelWorld*5)));
                    Pip->SetWorldScale3D(FVector(.012,PixelWorld*4/100,PixelWorld*4/100));
                    Pip->SetVisibility(Health>0&&I<Star);
                }
            }
        }
    };
    if(Combat){
        for(const auto& U:Combat->Units())Present(U.id,U.definition,U.side,U.star,U.cell,U.facing,U.health,U.maxHealth,U.state,U.neutral);
    }else{
        for(int Side=0;Side<2;++Side)for(const auto& U:Formation[Side]){
            const auto Facing=static_cast<wc::Facing>((int(U.facing)+Side*2)%4);
            const auto HP=wc::StarValue(Catalog.units[U.definition].health,U.star,0,Catalog.rules);
            Present(U.id,U.definition,Side,U.star,wc::EncounterCell(U.cell,Side,Catalog.rules),Facing,HP,HP,wc::ActionState::Idle,false);
        }
    }
    for(auto It=Pieces.CreateIterator();It;++It)if(!Alive.Contains(It.Key())){
        if(auto* Actor=It.Value().Actor.Get()){SceneActors.Remove(Actor);Actor->Destroy();}
        It.RemoveCurrent();
    }
    TSet<int> Marked;
    int RecipientCell=-1;
    if(Combat)for(const auto& Action:Combat->VisualActions())if(!Action.basicAttack){
        // Grove's exact green perimeter already communicates its cells without inset tile frames.
        if(Storybook&&Action.mechanic==wc::AbilityMechanic::StationaryGrove)continue;
        for(const auto& Cell:Action.cells)if(Cell.column>=0&&Cell.column<8&&Cell.row>=0&&Cell.row<8)Marked.Add(Cell.row*8+Cell.column);
        if(Action.cells.empty()&&Action.center.column>=0&&Action.center.column<8&&Action.center.row>=0&&Action.center.row<8)
            for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column)
                if(wc::Distance({Column,Row},Action.center)<=Action.radius)Marked.Add(Row*8+Column);
    }
    if(!Combat){
        Marked=PreparationCells;
        for(int Side=0;Side<2;++Side)for(const auto& Owned:Formation[Side]){
            const auto Cell=wc::EncounterCell(Owned.cell,Side,Catalog.rules);
            if(Owned.id==Selected)Marked.Add(Cell.row*8+Cell.column);
            if(Owned.id==PreparationRecipient)RecipientCell=Cell.row*8+Cell.column;
        }
        Marked.Append(DragCells);
    }
    for(int Index=0;Index<Telegraphs.Num();++Index){
        const bool KeyboardCell=SoloMode&&BoardInput.IsValid()&&BoardInput->HasKeyboardFocus()&&Index/4==KeyboardRow*8+KeyboardColumn;
        Telegraphs[Index]->SetVisibility(Marked.Contains(Index/4)||KeyboardCell);
        // While dragging: the hovered tile is gold, the rest of the attack range is the team colour.
        const bool RangeCell=!Combat&&Dragging&&DragCells.Contains(Index/4)&&Index/4!=DragHover.row*8+DragHover.column;
        const auto Color=KeyboardCell?Paper:RangeCell||(!Combat&&PreparationCells.Contains(Index/4)&&RecipientCell!=Index/4)?Teams[0]:Gold;
        if(Storybook){
            const FLinearColor Tint=Color==Teams[0]?FLinearColor(.008f,.24f,.22f):
                KeyboardCell?FLinearColor(.56f,.43f,.18f):FLinearColor(.43f,.28f,.08f);
            const uint32 Key=Tint.ToFColor(false).ToPackedRGBA();
            if(!CueMaterials.Contains(Key)){
                auto* Instance=UMaterialInstanceDynamic::Create(CombatCueMaterial,this);
                Instance->SetVectorParameterValue(TEXT("Color"),Tint);CueMaterials.Add(Key,Instance);
            }
            Telegraphs[Index]->SetMaterial(0,CueMaterials.FindChecked(Key));
            const float Width=FMath::Max(3.5f,WorldUnitsPerPixel(Telegraphs[Index]->GetComponentLocation())*1.6f)/100;
            Telegraphs[Index]->SetRelativeScale3D(Index%4>1?FVector(Width,1.78,.008):FVector(1.78,Width,.008));
        }else Telegraphs[Index]->SetMaterial(0,Material(Color));
    }
    UpdateCombatCues();
    ++PresentationFrames;
}

FString AWCVNextLab::StatusText() const
{
    if(!LoadError.IsEmpty())return TEXT("PROFILE REJECTED: ")+LoadError;
    if(StatusTest)return TEXT("STATUS EFFECT TEST · Synthetic abilities for this demonstration only · Reset returns to your formation");
    const FString Variant=Catalog.rules.nearestReachableTarget?TEXT("COMBAT CLARITY · MANA 20/HIT · "):
        Catalog.balanceVersion.find("+mana100_hit20_v1")!=std::string::npos?TEXT("MANA 20/HIT EXPERIMENT · "):
        Catalog.balanceVersion.find("+mana100_v1")!=std::string::npos?TEXT("MANA EXPERIMENT · "):TEXT("COOLDOWN CONTROL · ");
    if(SoloMode)return Variant+SoloStatusText();
    if(!Fight)return Variant+FString::Printf(TEXT("PREPARATION  ·  A %d/10  |  B %d/10  ·  Seed %d  ·  Choose positions and facing before combat"),int(Formation[0].size()),int(Formation[1].size()),Seed);
    return Variant+FString::Printf(TEXT("%s  ·  %.2fs  ·  Tick %d  ·  Events %d  ·  Seed %d"),Fight->Result().complete?TEXT("RESOLVED"):Paused?TEXT("PAUSED"):TEXT("COMBAT"),Fight->CurrentTick()*Catalog.rules.tickMs/1000.,Fight->CurrentTick(),int(Fight->Events().size()),Seed);
}
FString AWCVNextLab::InspectorText() const
{
    const auto* Combat = CurrentCombat();
    if(!LoadError.IsEmpty())return LoadError;
    int Def=Palette,Star=BrushStar,Relic=-1;
    bool HasSelection=false;
    const wc::CombatUnit* CombatPiece=nullptr;
    if(Combat)for(const auto& U:Combat->Units())if(U.id==Selected){HasSelection=true;CombatPiece=&U;Def=U.definition;Star=U.star;Relic=U.relic;}
    if(!Combat)for(const auto& Side:Formation)for(const auto& U:Side)if(U.id==Selected){HasSelection=true;Def=U.definition;Star=U.star;Relic=U.relic;}
    if(!Combat&&SoloMode&&SoloMatch&&ViewedSeat==0)for(const auto& U:SoloMatch->Seats()[0].roster)if(U.id==Selected){HasSelection=true;Def=U.definition;Star=U.star;Relic=U.relic;}
    if(SoloMode&&!HasSelection)return TEXT("Select a creature to inspect its stats, ability and equipped relic.");
    if(Def<0||Def>=int(CombatPiece&&CombatPiece->neutral?Catalog.neutrals.size():Catalog.units.size()))return FString();
    const auto& D=Catalog.Definition(Def,CombatPiece&&CombatPiece->neutral);
    const auto HP=CombatPiece?CombatPiece->health:wc::StarValue(D.health,Star,0,Catalog.rules);
    const auto Maximum=CombatPiece?CombatPiece->maxHealth:HP;
    const auto Damage=CombatPiece?CombatPiece->basicDamage:wc::StarValue(D.attackDamage,Star,0,Catalog.rules);
    FString Result=FString::Printf(TEXT("%s  ·  %d star\n%s / %s\n%s\nHealth %.0f / %.0f   Basic %.0f\nArmor %d   Resist %d   Range %d\n\n%s\n"),*Str(D.name),Star,*Str(D.race),*Str(D.unitClass),CombatPiece?TEXT("Current battle stats"):TEXT("Base stats; trait bonuses inactive in this lab"),HP/100.,Maximum/100.,Damage/100.,CombatPiece?CombatPiece->armor:D.armor,CombatPiece?CombatPiece->resistance:D.resistance,D.range,*Str(D.ability.name));
    if(const auto* Full=Metadata.Units.Find(Str(D.id));Full&&Full->IsValid()){
        const TSharedPtr<FJsonObject>* Ability=nullptr;
        FString Tooltip;
        if((*Full)->TryGetObjectField(TEXT("ability"),Ability)&&Ability&&(*Ability)->TryGetStringField(TEXT("tooltip_en"),Tooltip))Result+=Tooltip+TEXT("\n");
    }
    Result+=FString::Printf(TEXT("%s basic attack · %.2fs between attacks\n"),D.projectileTravelMs>0?TEXT("Ranged projectile"):TEXT("Melee strike"),wc::AttackInterval(D.attackRate,CombatPiece?CombatPiece->rateBonus:0,Catalog.rules)*Catalog.rules.tickMs/1000.);
    if(CombatPiece){
        const TCHAR* State=CombatPiece->state==wc::ActionState::Moving?TEXT("Moving to attack range"):
            CombatPiece->state==wc::ActionState::AttackWindup?TEXT("Basic attack windup"):
            CombatPiece->state==wc::ActionState::AttackRecovery?TEXT("Recovering from own attack"):
            CombatPiece->state==wc::ActionState::CastWindup?TEXT("Casting skill"):
            CombatPiece->state==wc::ActionState::CastRecovery?TEXT("Recovering from skill"):
            CombatPiece->state==wc::ActionState::Stunned?(CombatPiece->cocoonExpiry>Combat->CurrentTick()?TEXT("Cocooned: cannot move, attack or cast"):TEXT("Stunned")):
            CombatPiece->health<=0?TEXT("Defeated"):TEXT("Seeking an enemy");
        Result+=FString(TEXT("State: "))+State+TEXT("\n");
        if(CombatPiece->target>=0){const auto& T=Combat->Units()[CombatPiece->target];Result+=FString(TEXT("Target: "))+Str(Catalog.Definition(T.definition,T.neutral).displayName)+TEXT("\n");}
    }
    switch(D.ability.mechanic){
    case wc::AbilityMechanic::DirectionalGuard:Result+=TEXT("Visual: gold arc and ally link show damage prevented.\n");break;
    case wc::AbilityMechanic::MomentumCharge:Result+=TEXT("Visual: amber arrow aims the charge; a trail shows movement.\n");break;
    case wc::AbilityMechanic::StationaryGrove:Result+=TEXT("Visual: green ring marks the grove; + numbers show health restored.\n");break;
    case wc::AbilityMechanic::ScreenedStrike:Result+=TEXT("Visual: pink aim line becomes a lash to the first enemy hit.\n");break;
    case wc::AbilityMechanic::CrossingBeams:Result+=TEXT("Visual: violet lane markings precede crossing beam impacts.\n");break;
    case wc::AbilityMechanic::TidalPush:Result+=TEXT("Visual: cyan lane and wave; PUSH appears only on displacement.\n");break;
    case wc::AbilityMechanic::CocoonProjectile:Result+=TEXT("Visual: mouth-fired web wraps one enemy in cream silk.\n");break;
    default:break;
    }
    const auto A=CombatPiece?CombatPiece->ability:wc::EffectiveAbility(Catalog,D,Relic);
    if(A.mechanic==wc::AbilityMechanic::DirectionalGuard)
        Result+=FString::Printf(TEXT("Passive guard · no activation timer\nPrevents %.1f%% damage from frontal sources\nRear radius %d · nearest eligible ally"),A.guardReductionBp/100.,A.radius);
    else{
        if(A.mana.maximum>0){
            const int Mana=CombatPiece?CombatPiece->mana:A.mana.starting;
            const TCHAR* Readiness=CombatPiece&&CombatPiece->state==wc::ActionState::CastWindup?TEXT("Casting"):
                CombatPiece&&Combat->CurrentTick()<CombatPiece->manaResumeTick?TEXT("Recovering; gain paused"):
                Mana>=A.mana.maximum?TEXT("Ready; waiting for action / valid target"):TEXT("Charging");
            Result+=FString::Printf(TEXT("Mana %.1f / %.0f · %s\nGain %.1f per basic hit; HP loss also charges\nWindup %.2fs | Reach %d | Effect %.2f | Radius %d"),
                Mana/100.,A.mana.maximum/100.,Readiness,A.mana.basicAttackGain*100./A.mana.gainDivisorBp,
                A.castMs/1000.,A.range,A.magnitude[Star-1]/100.,A.radius);
        }else
        Result+=FString::Printf(TEXT("First %.2fs  |  Cooldown %.2fs\nWindup %.2fs  |  Reach %d\n%s %.2f  |  Radius %d"),A.firstCastMs/1000.,A.cooldownMs/1000.,A.castMs/1000.,A.range,A.mechanic==wc::AbilityMechanic::StationaryGrove?TEXT("Heal per pulse"):A.effect==wc::Effect::Heal?TEXT("Heal"):TEXT("Base effect"),A.magnitude[Star-1]/100.,A.radius);
        if(A.mechanic==wc::AbilityMechanic::StationaryGrove)
            Result+=FString::Printf(TEXT("\nPulse interval %.2fs  |  Area duration %.2fs"),A.pulseMs/1000.,A.durationMs/1000.);
        if(A.mechanic==wc::AbilityMechanic::CocoonProjectile)
            Result+=FString::Printf(TEXT("\nCocoon %.2fs: cannot move, attack or cast.\nNo skill damage. Chooses nearest enemy not already trapped.\nTravel %.2fs; canceled casts create no cocoon."),A.durationMs/1000.,A.travelMs/1000.);
        if(CombatPiece&&A.mana.maximum==0)Result+=FString::Printf(TEXT("\nNext readiness in %.2fs"),FMath::Max(0,CombatPiece->cooldownTick-Combat->CurrentTick())*Catalog.rules.tickMs/1000.);
    }
    if(CombatPiece)Result+=FString::Printf(TEXT("\nShield %.0f  |  Facing %s"),CombatPiece->shield/100.,FacingName(CombatPiece->facing));
    if(CombatPiece&&A.mechanic==wc::AbilityMechanic::MomentumCharge)
        Result+=FString::Printf(TEXT("\nApproach steps: %d / %d\nA released charge consumes its stored steps."),CombatPiece->momentumSteps,A.maxMomentumSteps);
    if(CombatPiece&&A.mechanic==wc::AbilityMechanic::StationaryGrove)
        Result+=FString::Printf(TEXT("\nEstablishment: %.2f / %.2fs\nMovement and stun reset establishment; live pulses require the source to remain valid."),
            FMath::Min(A.stationaryMs,(Combat->CurrentTick()-CombatPiece->lastMovementTick)*Catalog.rules.tickMs)/1000.,A.stationaryMs/1000.);
    if(CombatPiece)for(const auto& Action:Combat->VisualActions())if(Action.source==CombatPiece->id&&!Action.basicAttack){
        Result+=FString::Printf(TEXT("\n%s effect at %c%d · %d marked cells"),Action.released?TEXT("Released"):TEXT("Preparing"),
            TCHAR('A'+Action.center.column),Action.center.row+1,int(Action.cells.size()));
        break;
    }
    if(A.mana.maximum>0&&Relic>=0)Result+=TEXT("\nRelic timing adjusts mana gain; mana cost stays 100.");
    Result+=TEXT("\n\nRelic: ");
    if(Relic>=0&&Relic<int(Catalog.relics.size()))Result+=Str(Catalog.relics[Relic].name)+TEXT("\n")+Str(Catalog.relics[Relic].description)+TEXT("\nValues above include its actual transforms.");
    else Result+=TEXT("None");
    if(!Combat&&!PreparationHint.IsEmpty())Result+=TEXT("\n\n")+PreparationHint;
    return Result;
}
FString AWCVNextLab::EventText() const
{
    const auto* Combat = CurrentCombat();
    if(SoloMode&&SoloMatch&&(SoloMatch->CurrentPhase()==wc::Phase::Settlement||SoloMatch->CurrentPhase()==wc::Phase::Finished))return SoloRecap;
    if(SoloMode&&!Combat)return SoloRecap;
    if(!Combat)return TEXT("Start or Step to inspect real combat events. No predicted winner is substituted.");
    const auto& Events=Combat->Events();
    const auto Name=[this,Combat](wc::Id Id){
        for(const auto& Unit:Combat->Units())if(Unit.id==Id)
            return Str(Catalog.Definition(Unit.definition,Unit.neutral).displayName)+FString(Unit.side?TEXT(" B"):TEXT(" A"));
        return FString(TEXT("effect"));
    };
    FString Result;
    const int StartIndex=FMath::Max(0,int(Events.size())-8);
    for(int Index=int(Events.size())-1;Index>=StartIndex;--Index){
        const auto& E=Events[Index];
        Result+=FString::Printf(TEXT("%.2fs  %s → %s\n%s %.2f at %c%d"),E.tick*Catalog.rules.tickMs/1000.,*Name(E.source),*Name(E.target),EffectName(E.effect),E.resolved/100.,TCHAR('A'+E.cell.column),E.cell.row+1);
        if(E.absorbed)Result+=FString::Printf(TEXT("  absorbed %.2f"),E.absorbed/100.);
        if(E.prevented)Result+=FString::Printf(TEXT("  %s prevented %.2f"),*Name(E.guardedBy),E.prevented/100.);
        Result+=TEXT("\n\n");
    }
    return Result.IsEmpty()?TEXT("No effect has resolved yet."):Result;
}
FString AWCVNextLab::Signature() const
{
    if(!Fight)return FString();
    FString Data;
    for(const auto& E:Fight->Events())Data+=FString::Printf(TEXT("%d,%llu,%llu,%llu,%d,%lld,%lld,%lld,%lld,%d,%d,%d,%llu,%lld;"),E.tick,E.source,E.target,E.action,int(E.effect),E.requested,E.resolved,E.absorbed,E.healthLoss,E.cell.column,E.cell.row,int(E.mechanic),E.guardedBy,E.prevented);
    for(const auto& U:Fight->Units())Data+=FString::Printf(TEXT("u%llu,%lld,%lld,%d,%d,%d,%d,%d;"),U.id,U.health,U.shield,U.cell.column,U.cell.row,int(U.state),int(U.facing),U.relic);
    const auto& R=Fight->Result();Data+=FString::Printf(TEXT("r%d,%d,%d,%d,%d"),R.winner,R.timeout,R.ticks,R.survivors[0],R.survivors[1]);
    return Hash(Data);
}
// Review-only route: no simulation input. Each stage holds one clip, waits for it to play, then saves a
// screenshot without the interface. Two camera sides are used for the idle pose.
void AWCVNextLab::TickHeroReview()
{
    struct FShot{const TCHAR* Clip;bool Loop;float Wait;float Side;const TCHAR* File;};
    static const FShot Shots[]={
        {TEXT("Idle"),true,1.2f,35,TEXT("hero-idle-front.png")},{TEXT("Idle"),true,.6f,215,TEXT("hero-idle-back.png")},
        {TEXT("Idle"),true,.6f,-55,TEXT("hero-idle-shield-side.png")},
        {TEXT("Move"),true,.45f,35,TEXT("hero-walk.png")},{TEXT("Attack"),false,1.1f,35,TEXT("hero-attack.png")},
        {TEXT("Cast"),false,1.2f,35,TEXT("hero-block.png")},{TEXT("Hit"),false,.5f,35,TEXT("hero-hit.png")},
        {TEXT("Defeat"),false,2.6f,35,TEXT("hero-defeat.png")}};
    const FPieceView* Found=nullptr;
    for(const auto& Entry:Pieces)if(Entry.Value.Hero&&Entry.Value.Side==0&&Entry.Value.Actor.IsValid()){Found=&Entry.Value;break;}
    if(!Found||!Camera)return;
    const int Index=HeroReviewStage/2;
    static bool Captured=false;
    if(Index>=int(UE_ARRAY_COUNT(Shots))){
        // After the screenshots the route keeps cycling so the clips can be watched live.
        if(!Captured){Captured=true;UE_LOG(LogTemp,Display,TEXT("WC_HERO_REVIEW_COMPLETE"));}
        HeroReviewStage=0;return;
    }
    const auto& Shot=Shots[Index];
    // The hero's own front is local +Y; Side turns the camera around it from that front.
    const FVector At=Found->Actor->GetActorLocation();
    const FVector Front=Found->Actor->GetActorRotation().RotateVector(FVector(0,1,0));
    const FVector Direction=FRotator(0,Shot.Side,0).RotateVector(Front);
    const FVector Eye=At+Direction*780+FVector(0,0,260);
    auto* View=Camera->GetCameraComponent();
    View->SetProjectionMode(ECameraProjectionMode::Perspective);View->SetFieldOfView(32);
    Camera->SetActorLocation(Eye);Camera->SetActorRotation((At+FVector(0,0,105)-Eye).Rotation());
    if(HeroReviewStage==0&&!Captured){
        // The lab's single top light leaves the camera side in shadow; a fill light on the camera shows the model.
        auto* Fill=NewObject<UPointLightComponent>(Camera);
        Fill->SetupAttachment(Camera->GetRootComponent());
        Fill->bUseInverseSquaredFalloff=false;Fill->SetLightFalloffExponent(1);Fill->SetIntensity(5);
        Fill->SetAttenuationRadius(4000);Fill->SetCastShadows(false);Fill->RegisterComponent();
    }
    if(HeroReviewStage%2==0){
        Found->Hero->ReviewClip(Shot.Clip,Shot.Loop);HeroReviewAt=Elapsed;++HeroReviewStage;
    }else if(Captured){
        // Watching: give each clip time to play through before moving on.
        if(Elapsed-HeroReviewAt>=FMath::Max(3.f,Shot.Wait+1.5f))++HeroReviewStage;
    }else if(Elapsed-HeroReviewAt>=Shot.Wait&&!FScreenshotRequest::IsScreenshotRequested()){
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        FScreenshotRequest::RequestScreenshot(EvidenceDirectory/Shot.File,false,false);
        ++HeroReviewStage;
    }
}
void AWCVNextLab::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);Elapsed+=DeltaSeconds;
    if(CragstoatExercise){TickCragstoatRoute(DeltaSeconds);return;}
    if(SilkmotherExercise){TickSilkmotherRoute(DeltaSeconds);return;}
    if(BellbackExercise||BellbackPerformance){TickBellbackRoute(DeltaSeconds);return;}
    if(!LoadError.IsEmpty())return;
    UpdateCamera();
    if(HeroReview)TickHeroReview();
    TickDrag();
    if(SoloMode){
        if(SoloVisualExercise){
            if(CapturePhase==ECapturePhase::None&&!ExerciseDone)TickSoloVisualExercise();
            SoloPaused=true;TickSolo(0);
            UpdatePresentation(DeltaSeconds);UpdateInterfaceText();TickCapture();return;
        }
        TickSolo(DeltaSeconds);UpdatePresentation(DeltaSeconds);UpdateInterfaceText();return;
    }
    if(Exercise&&!ExerciseDone){if(CapturePhase==ECapturePhase::None)TickExercise();}
    else if(CapturePhase==ECapturePhase::None&&Fight&&!Paused&&!Fight->Result().complete){
        Accumulator+=DeltaSeconds;
        const double TickSeconds=Catalog.rules.tickMs/1000.;
        int CatchUp=0;
        while(Accumulator>=TickSeconds&&CatchUp++<20&&!Fight->Result().complete&&!Paused){Advance();Accumulator-=TickSeconds;}
    }
    UpdatePresentation(DeltaSeconds);
    UpdateInterfaceText();
    TickCapture();
}
void AWCVNextLab::EndPlay(const EEndPlayReason::Type Reason)
{
    if(Interface&&GEngine&&GEngine->GameViewport)GEngine->GameViewport->RemoveViewportWidgetContent(Interface.ToSharedRef());
    Interface.Reset();BoardInput.Reset();
    InspectorBlock.Reset();EventBlock.Reset();StatusBlock.Reset();MessageBlock.Reset();
    for(AActor* Actor:SceneActors)if(IsValid(Actor))Actor->Destroy();
    SceneActors.Empty();
    Super::EndPlay(Reason);
}

void AWCVNextLab::QueueCapture(const FString& Filename,int ResumeStage)
{
    CaptureFilename=EvidenceDirectory/Filename;
    CapturePreviousWrite=IFileManager::Get().GetTimeStamp(*CaptureFilename);
    CaptureQueuedAt=Elapsed;CapturePresentedAt=-1;
    CaptureSelected=Selected;CaptureCombatTick=CurrentCombat()?CurrentCombat()->CurrentTick():-1;
    CaptureSoloRound=SoloMatch?SoloMatch->Round():-1;
    CaptureSoloPhase=SoloMatch?int(SoloMatch->CurrentPhase()):-1;
    CaptureSoloSeat=SoloMatch?ViewedSeat:-1;
    CaptureResumeStage=ResumeStage;CaptureStateStable=true;
    CapturePhase=ECapturePhase::Settling;
    CaptureRecord=MakeShared<FJsonObject>();
    CaptureRecord->SetStringField(TEXT("file"),Filename);
    CaptureRecord->SetNumberField(TEXT("queued_at_seconds"),Elapsed);
    CaptureRecord->SetNumberField(TEXT("selected_id"),Selected);
    CaptureRecord->SetNumberField(TEXT("combat_tick"),CaptureCombatTick);
    if(SoloMode){
        CaptureRecord->SetNumberField(TEXT("round"),CaptureSoloRound);
        CaptureRecord->SetNumberField(TEXT("phase"),CaptureSoloPhase);
        CaptureRecord->SetNumberField(TEXT("viewed_seat"),CaptureSoloSeat);
        CaptureRecord->SetBoolField(TEXT("cosmetic_upgrade_time_held"),SoloVisualExercise);
    }
    CaptureRecords.Add(MakeShared<FJsonValueObject>(CaptureRecord));
}
void AWCVNextLab::TickCapture()
{
    if(CapturePhase==ECapturePhase::None)return;
    CaptureStateStable&=Selected==CaptureSelected&&(CurrentCombat()?CurrentCombat()->CurrentTick():-1)==CaptureCombatTick;
    if(SoloMatch)CaptureStateStable&=SoloMatch->Round()==CaptureSoloRound&&int(SoloMatch->CurrentPhase())==CaptureSoloPhase&&ViewedSeat==CaptureSoloSeat;
    if(Elapsed-CaptureQueuedAt>15){
        CaptureRecord->SetBoolField(TEXT("completed"),false);
        ExerciseChecks->SetBoolField(TEXT("all_captures_completed"),false);
        CapturePhase=ECapturePhase::None;ExerciseDone=true;Paused=true;
        Message=TEXT("Screenshot processing timed out. Capture evidence failed; inspect lab-exercise.json.");
        if(SoloVisualExercise)FinishSoloVisualExercise(TEXT("Screenshot processing timed out."));else WriteEvidence(false);
        return;
    }
    if(CapturePhase==ECapturePhase::Settling){
        if(CapturePresentedAt<0){
            CapturePresentedAt=Elapsed;CaptureFirstPresentedFrame=PresentationFrames;
            return;
        }
        // A UI screenshot may read the previous window backbuffer. Let the new state reach it first.
        if(Elapsed-CapturePresentedAt<.15||PresentationFrames-CaptureFirstPresentedFrame<2||FScreenshotRequest::IsScreenshotRequested())return;
        CaptureRecord->SetNumberField(TEXT("presentation_ticks_before_request"),PresentationFrames-CaptureFirstPresentedFrame);
        CaptureRecord->SetNumberField(TEXT("settled_seconds_before_request"),Elapsed-CapturePresentedAt);
        CaptureBoardProjection(CaptureRecord.ToSharedRef());
        int MarkedCells=0;
        for(int Index=0;Index<Telegraphs.Num();Index+=4)if(Telegraphs[Index]->IsVisible())++MarkedCells;
        CaptureRecord->SetNumberField(TEXT("presented_marked_cells"),MarkedCells);
        TArray<TSharedPtr<FJsonValue>> PreviewCells;
        for(int Cell=0;Cell<64;++Cell)if(PreparationCells.Contains(Cell))PreviewCells.Add(MakeShared<FJsonValueNumber>(Cell));
        CaptureRecord->SetArrayField(TEXT("preparation_cells"),PreviewCells);
        const FString InspectorSource=InspectorText();
        CaptureRecord->SetStringField(TEXT("inspector_source_text"),InspectorSource);
        CaptureRecord->SetStringField(TEXT("inspector_widget_text"),InspectorBlock?InspectorBlock->GetText().ToString():FString());
        CaptureRecord->SetStringField(TEXT("status_widget_text"),StatusBlock?StatusBlock->GetText().ToString():FString());
        CaptureRecord->SetStringField(TEXT("event_widget_text"),EventBlock?EventBlock->GetText().ToString():FString());
        CaptureRecord->SetBoolField(TEXT("text_widgets_match_current_sources"),SoloMode?
            MessageBlock&&MessageBlock->GetText().ToString()==Message:
            InspectorBlock&&InspectorBlock->GetText().ToString()==InspectorSource&&
            EventBlock&&EventBlock->GetText().ToString()==EventText()&&
            StatusBlock&&StatusBlock->GetText().ToString()==StatusText()&&
            MessageBlock&&MessageBlock->GetText().ToString()==Message);
        if(SoloMode){
            CaptureRecord->SetStringField(TEXT("text_verification_scope"),TEXT("Message widget read back; other Storybook fields use live Slate attributes and need visual review."));
            CaptureRecord->SetStringField(TEXT("solo_status_source"),SoloStatusText());
            CaptureRecord->SetStringField(TEXT("solo_summary_source"),SoloSummaryText());
        }
        FScreenshotRequest::RequestScreenshot(CaptureFilename,true,false);
        CaptureRecord->SetNumberField(TEXT("requested_at_seconds"),Elapsed);
        CapturePhase=ECapturePhase::Requested;
    }else if(CapturePhase==ECapturePhase::Requested&&!FScreenshotRequest::IsScreenshotRequested()){
        const int64 Bytes=IFileManager::Get().FileSize(*CaptureFilename);
        const bool Saved=Bytes>0&&IFileManager::Get().GetTimeStamp(*CaptureFilename)!=CapturePreviousWrite;
        CaptureRecord->SetBoolField(TEXT("new_file_saved"),Saved);
        CaptureRecord->SetNumberField(TEXT("bytes"),Bytes);
        CaptureRecord->SetNumberField(TEXT("processed_at_seconds"),Elapsed);
        CaptureProcessedAt=Elapsed;CapturePhase=ECapturePhase::Processed;
    }else if(CapturePhase==ECapturePhase::Processed&&Elapsed-CaptureProcessedAt>=.15){
        CaptureRecord->SetBoolField(TEXT("state_stable_through_capture"),CaptureStateStable);
        CaptureRecord->SetBoolField(TEXT("completed"),true);
        CaptureRecord->SetNumberField(TEXT("settled_seconds_after_processing"),Elapsed-CaptureProcessedAt);
        ExerciseStage=CaptureResumeStage;CapturePhase=ECapturePhase::None;
    }
}

void AWCVNextLab::FinishSoloVisualExercise(const FString& Failure)
{
    if(!ExerciseChecks)ExerciseChecks=MakeShared<FJsonObject>();
    if(!Failure.IsEmpty())ExerciseChecks->SetBoolField(TEXT("completed_without_error"),false);
    bool Passed=Failure.IsEmpty();
    for(const auto& Check:ExerciseChecks->Values)if(Check.Value->Type==EJson::Boolean)Passed&=Check.Value->AsBool();
    auto Report=MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("schema"),TEXT("wonder_vnext.solo_visual_exercise.1"));
    Report->SetBoolField(TEXT("passed"),Passed);
    Report->SetStringField(TEXT("failure"),Failure);
    Report->SetStringField(TEXT("utc"),FDateTime::UtcNow().ToIso8601());
    Report->SetStringField(TEXT("boundary"),TEXT("Native packaged UI captures from real local command handlers; accelerated tournament. Not physical input or human art acceptance."));
    Report->SetStringField(TEXT("save_path"),SavePath);
    Report->SetStringField(TEXT("catalog_digest"),Str(Catalog.contentDigest));
    Report->SetNumberField(TEXT("wall_seconds"),Elapsed);
    Report->SetObjectField(TEXT("checks"),ExerciseChecks);
    Report->SetArrayField(TEXT("captures"),CaptureRecords);
    FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);
    IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
    const bool Written=FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("solo-visual-exercise.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    ExerciseDone=true;SoloPaused=true;
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_VISUAL_EXERCISE_COMPLETE passed=%d report_written=%d captures=%d"),Passed,Written,CaptureRecords.Num());
    FPlatformMisc::RequestExit(false);
}

void AWCVNextLab::TickSoloVisualExercise()
{
    if(ExerciseDone||!SoloMatch)return;
    if(Elapsed>180){FinishSoloVisualExercise(TEXT("Visual exercise exceeded 180 seconds."));return;}
    if(!SoloMatch->InvariantError().empty()){FinishSoloVisualExercise(Str(SoloMatch->InvariantError()));return;}
    const auto Check=[this](const TCHAR* Name,bool Value){ExerciseChecks->SetBoolField(Name,Value);};
    const auto CaptureUpgrade=[this](int Resume){
        if(ExerciseChecks->HasField(TEXT("actual_merge_captured")))return false;
        for(const auto& Entry:UpgradeStarted)if(UpgradePulse(Entry.Key)>0){
            Selected=Entry.Key;
            ExerciseChecks->SetBoolField(TEXT("actual_merge_captured"),true);
            QueueCapture(TEXT("solo-upgrade.png"),Resume);
            return true;
        }
        return false;
    };
    const auto BuyOne=[this]{
        if(ViewedSeat!=0||SoloMatch->Seats()[0].health<=0)return false;
        const auto& Captain=SoloMatch->Seats()[0];
        int Best=-1,BestScore=-1;
        for(int Slot=0;Slot<int(Captain.shop.size());++Slot){
            wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;
            const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Buy);
            if(!Preview.accepted)continue;
            int Score=Preview.mergeSteps.empty()?0:100;
            for(const auto& Unit:Captain.roster)if(Unit.definition==Captain.shop[Slot]&&Unit.star==1)Score+=10;
            if(Score>BestScore){Best=Slot;BestScore=Score;}
        }
        if(Best<0)return false;
        wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Best;
        return SoloCommand(Buy);
    };
    const auto Deploy=[this]{
        const auto& Captain=SoloMatch->Seats()[0];
        std::vector<wc::Id> Bench;
        int Count=0;for(const auto& Unit:Captain.roster){if(Unit.onBoard)++Count;else Bench.push_back(Unit.id);}
        for(const auto Id:Bench){
            if(Count>=FMath::Min(2,Captain.level))break;
            Selected=Id;
            if(SoloCell({Count?4:2,2}))++Count;
        }
    };
    if(ExerciseStage==200){
        FString ExplicitSave;
        const bool Fresh=FParse::Value(FCommandLine::Get(),TEXT("WCSavePath="),ExplicitSave)&&
            FPaths::IsUnderDirectory(FPaths::ConvertRelativePathToFull(SavePath),FPaths::ConvertRelativePathToFull(EvidenceDirectory))&&
            !IFileManager::Get().FileExists(*SavePath)&&!IFileManager::Get().FileExists(*(SavePath+TEXT(".previous")));
        if(!Fresh){FinishSoloVisualExercise(TEXT("Visual exercise requires a fresh explicit WCSavePath inside its evidence directory."));return;}
        Check(TEXT("storybook_resources_ready"),FWCArtSlice::StorybookResourcesReady()&&SanctuaryBackdrop);
        SoloVisualSavedState=SoloMatch->SavePreparation();
        SaveSolo();StartSolo();
        Check(TEXT("saved_preparation_opens_choice"),AwaitingSaveDecision);
        QueueCapture(TEXT("solo-save-choice.png"),201);
        return;
    }
    if(ExerciseStage==201){
        ResumeSolo();Check(TEXT("resume_restores_exact_preparation"),!AwaitingSaveDecision&&SoloMatch->SavePreparation()==SoloVisualSavedState);
        Check(TEXT("resume_does_not_trigger_upgrade"),UpgradeStarted.IsEmpty());
        QueueCapture(TEXT("solo-loaded-preparation.png"),202);return;
    }
    if(ExerciseStage==202){
        if(SoloVisualOrders<10&&BuyOne()){
            ++SoloVisualOrders;Deploy();
            if(CaptureUpgrade(202))return;
            return;
        }
        if(SoloVisualOrders<10&&SoloMatch->Seats()[0].gold>=Catalog.rules.rerollCost+1){
            wc::Command Reroll;Reroll.type=wc::CommandType::Reroll;
            if(SoloCommand(Reroll)){++SoloVisualOrders;return;}
        }
        Deploy();
        int Deployed=0,Benched=0;for(const auto& Unit:SoloMatch->Seats()[0].roster){if(Unit.onBoard)++Deployed;else ++Benched;}
        Check(TEXT("preparation_has_real_deployed_and_bench_units"),Deployed>=2&&Benched>=1);
        ExerciseChecks->SetNumberField(TEXT("preparation_deployed"),Deployed);
        ExerciseChecks->SetNumberField(TEXT("preparation_benched"),Benched);
        const auto& Roster=SoloMatch->Seats()[0].roster;
        const auto BoardUnit=std::find_if(Roster.begin(),Roster.end(),[](const auto& Unit){return Unit.onBoard;});
        const auto BenchUnit=std::find_if(Roster.begin(),Roster.end(),[](const auto& Unit){return !Unit.onBoard;});
        if(BoardUnit!=Roster.end()&&BenchUnit!=Roster.end()){
            const std::string BeforeClick=SoloMatch->SavePreparation();
            Selected=BoardUnit->id;
            SelectBench(BenchUnit->bench);
            Check(TEXT("occupied_bench_click_selects_without_swapping"),
                Selected==BenchUnit->id&&SoloMatch->SavePreparation()==BeforeClick);
            Selected=0;
        }else Check(TEXT("occupied_bench_click_selects_without_swapping"),false);
        // The prior preparation capture records the automatic shop popup. Show the
        // unobscured board and bench for the formation capture after that review.
        ShopOpen=false;ShopDismissedRound=SoloMatch->Round();
        SoloPaused=true;QueueCapture(TEXT("solo-recruited-preparation.png"),204);return;
    }
    if(ExerciseStage==204){
        ScoutSolo(1);Check(TEXT("scouting_clears_upgrade"),UpgradeStarted.IsEmpty());
        const auto Before=SoloMatch->SavePreparation();
        wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=0;
        Check(TEXT("scouting_rejects_orders_without_mutation"),!SoloCommand(Buy)&&Before==SoloMatch->SavePreparation());
        QueueCapture(TEXT("solo-scouting.png"),205);return;
    }
    if(ExerciseStage==206){
        const auto& Captain=SoloMatch->Seats()[0];
        int Choice=-1;wc::Id Recipient=0;
        for(int Slot=0;Slot<int(Captain.relicOffers.size())&&Choice<0;++Slot)for(const auto& Unit:Captain.roster)
            if(wc::RelicCompatible(Catalog.relics[Captain.relicOffers[Slot]],Catalog.units[Unit.definition].ability.mechanic)){Choice=Slot;Recipient=Unit.id;break;}
        if(Choice<0){FinishSoloVisualExercise(TEXT("No first-draft relic fits the actually recruited roster."));return;}
        const int Relic=Captain.relicOffers[Choice];
        wc::Command Draft;Draft.type=wc::CommandType::ChooseRelic;Draft.slot=Choice;
        const bool Drafted=SoloCommand(Draft);Selected=Recipient;
        wc::Command Equip;Equip.type=wc::CommandType::EquipRelic;Equip.slot=Relic;Equip.unit=Recipient;
        Check(TEXT("real_draft_and_equipment_accepted"),Drafted&&SoloCommand(Equip));
        Check(TEXT("equipped_relic_in_live_inspector"),InspectorText().Contains(TEXT("Relic: ")+Str(Catalog.relics[Relic].name)));
        QueueCapture(TEXT("solo-equipped-relic.png"),205);return;
    }
    if(ExerciseStage==208){
        const auto Records=SoloMatch->Records().size();NewSolo();
        Check(TEXT("restart_clears_results_and_upgrade"),Records>0&&SoloMatch->Round()==1&&SoloMatch->Records().empty()&&!AwaitingSaveDecision&&UpgradeStarted.IsEmpty());
        QueueCapture(TEXT("solo-restarted.png"),209);return;
    }
    if(ExerciseStage==209){
        bool Complete=CaptureRecords.Num()==9;
        for(const auto& Value:CaptureRecords){
            const auto Record=Value->AsObject();
            Complete&=Record->GetBoolField(TEXT("completed"))&&Record->GetBoolField(TEXT("new_file_saved"))&&
                Record->GetBoolField(TEXT("state_stable_through_capture"))&&Record->GetBoolField(TEXT("text_widgets_match_current_sources"))&&
                Record->GetBoolField(TEXT("board_projection_verified"))&&
                Record->GetNumberField(TEXT("presentation_ticks_before_request"))>=2;
        }
        Check(TEXT("nine_stable_native_ui_captures_written"),Complete);
        Check(TEXT("actual_merge_captured"),ExerciseChecks->HasField(TEXT("actual_merge_captured")));
        FinishSoloVisualExercise();return;
    }
    if(ExerciseStage!=205)return;
    if(ViewedSeat!=0&&SoloMatch->Seats()[0].health>0)ScoutSolo(0);
    if(SoloMatch->CurrentPhase()==wc::Phase::Finished){
        Check(TEXT("actual_tournament_finished"),SoloMatch->InvariantError().empty()&&SoloMatch->Seats()[0].placement>0);
        ExerciseChecks->SetNumberField(TEXT("completed_rounds"),SoloMatch->Round());
        QueueCapture(TEXT("solo-results.png"),208);return;
    }
    if(SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0){
        if(!SoloMatch->Seats()[0].relicOffers.empty()){
            if(!ExerciseChecks->HasField(TEXT("real_relic_draft_captured"))){
                Check(TEXT("real_relic_draft_captured"),true);QueueCapture(TEXT("solo-relic-draft.png"),206);return;
            }
            wc::Command Draft;Draft.type=wc::CommandType::ChooseRelic;Draft.slot=0;SoloCommand(Draft);
        }
        if(!ExerciseChecks->HasField(TEXT("actual_merge_captured"))&&BuyOne()){
            Deploy();if(CaptureUpgrade(205))return;
        }
        if(!SoloMatch->Seats()[0].ready){wc::Command Ready;Ready.type=wc::CommandType::Ready;SoloCommand(Ready);}
    }
    const auto Phase=SoloMatch->CurrentPhase();const int Round=SoloMatch->Round();
    for(int I=0;I<200&&SoloMatch->CurrentPhase()==Phase&&SoloMatch->Round()==Round;++I)SoloMatch->Tick(50);
    // Refresh the public presentation state before requesting any next-frame capture.
    SoloPaused=true;TickSolo(0);
}

void AWCVNextLab::TickExercise()
{
    if(CombatInvariantFailed)return;
    if(Elapsed>90){ExerciseChecks->SetBoolField(TEXT("completed_within_exercise_limit"),false);WriteEvidence(false);ExerciseDone=true;Paused=true;return;}
    if(ExerciseStage==100){
        StartStatusTest();ExerciseStage=101;
    }else if(ExerciseStage==101){
        if(Fight&&Fight->CurrentTick()<27)Advance();
        else {Paused=true;QueueCapture(TEXT("status-effects-active.png"),102);}
    }else if(ExerciseStage==102){
        ExerciseChecks->SetBoolField(TEXT("actual_stun_swirl_drawn"),CueKindsSeen.Contains(TEXT("stun_swirl")));
        ExerciseChecks->SetBoolField(TEXT("actual_shield_drawn"),CueKindsSeen.Contains(TEXT("active_shield")));
        ExerciseChecks->SetBoolField(TEXT("effective_healing_plus_drawn"),CueKindsSeen.Contains(TEXT("healing_plus")));
        ExerciseChecks->SetBoolField(TEXT("actual_modifier_drawn"),CueKindsSeen.Contains(TEXT("stat_modifier")));
        if(ArtSlice)ExerciseChecks->SetBoolField(TEXT("art_slice_five_point_stun_stars_drawn"),CueKindsSeen.Contains(TEXT("art_slice_stun_stars")));
        for(int I=0;I<8&&Fight->CurrentTick()<150;++I)Advance();
        if(Fight->CurrentTick()>=150){Paused=true;QueueCapture(TEXT("status-effects-expired.png"),103);}
    }else if(ExerciseStage==103){
        bool Expired=true;for(const auto& U:Fight->Units())Expired&=U.state!=wc::ActionState::Stunned&&U.shield==0&&U.modifiers.empty();
        ExerciseChecks->SetBoolField(TEXT("actual_statuses_expired"),Expired);
        ExerciseChecks->SetBoolField(TEXT("expired_status_geometry_hidden"),!CurrentCueKinds.Contains(TEXT("stun_swirl"))&&!CurrentCueKinds.Contains(TEXT("active_shield"))&&!CurrentCueKinds.Contains(TEXT("stat_modifier")));
        ExerciseChecks->SetBoolField(TEXT("cue_pool_bounded"),!CueOverflow);
        bool Passed=true;for(const auto& E:ExerciseChecks->Values)if(E.Value->Type==EJson::Boolean)Passed&=E.Value->AsBool();
        WriteEvidence(Passed);ExerciseDone=true;Paused=true;
    }else if(ExerciseStage==0){
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        QueueCapture(TEXT("lab-preparation.png"),1);
    }else if(ExerciseStage==1){
        if(ArtSlice){
            // The first capture has now settled; stage zero precedes the first presentation tick.
            bool Hud=!Pieces.IsEmpty();
            for(const auto& Pair:Pieces){
                const auto& View=Pair.Value;const int Maximum=Catalog.units[View.Definition].ability.mana.maximum;
                Hud&=View.HealthTrack&&View.ManaTrack&&View.HealthTrack->IsVisible()&&View.ManaTrack->IsVisible()==(Maximum>0)&&View.TierPips.Num()==3;
                if(Maximum==0)Hud&=!View.Mana->IsVisible();
            }
            ExerciseChecks->SetBoolField(TEXT("art_slice_hud_tracks_and_passive_mana_visibility"),Hud);
        }
        ClearFormation();
        ExerciseChecks->SetBoolField(TEXT("empty_start_rejected"),!Start());
        ChooseHero(0);EditCell({0,0},false);
        if(ArtSlice){
            ExerciseChecks->SetBoolField(TEXT("placement_preview_inspects_occupied_cell"),PlacementState({0,0})==1);
            ExerciseChecks->SetBoolField(TEXT("placement_preview_accepts_same_team_empty_cell"),PlacementState({1,0})==2);
            ExerciseChecks->SetBoolField(TEXT("placement_preview_rejects_cross_team_move"),PlacementState({0,7})==3);
            ExerciseChecks->SetBoolField(TEXT("placement_preview_ignores_off_board"),PlacementState({-1,0})==0);
        }
        const uint64 TestPiece=Selected;
        ChangeStars();ChangeFacing();
        ExerciseChecks->SetBoolField(TEXT("stars_and_facing_edit_selected_piece"),SelectedPiece()&&SelectedPiece()->star==2&&SelectedPiece()->facing==wc::Facing::Right);
        EditCell({1,0},false);
        ExerciseChecks->SetBoolField(TEXT("move_preserves_piece_and_star"),SelectedPiece()&&SelectedPiece()->id==TestPiece&&SelectedPiece()->cell==wc::Cell{1,0}&&SelectedPiece()->star==2&&Formation[0].size()==1);
        RemoveSelected();
        ExerciseChecks->SetBoolField(TEXT("remove_selected"),Formation[0].empty()&&TestPiece!=0);
        BrushStar=1;BrushFacing=wc::Facing::Forward;
        for(int Index=0;Index<10;++Index){ChooseHero(0);EditCell({Index%8,Index/8},false);}
        ChooseHero(0);
        if(ArtSlice)ExerciseChecks->SetBoolField(TEXT("placement_preview_rejects_full_team"),PlacementState({2,1})==3);
        ExerciseChecks->SetBoolField(TEXT("ten_per_side_limit"),Formation[0].size()==10&&!EditCell({2,1},false));
        Preset();
        ExerciseChecks->SetBoolField(TEXT("six_hero_palette_and_both_formations"),Formation[0].size()==6&&Formation[1].size()==6);
        UpdatePreparationPreview();
        const int BaseGuardCells=PreparationCells.Num();
        ExerciseChecks->SetBoolField(TEXT("guard_preparation_recipient_visible"),PreparationRecipient==Formation[0][2].id&&BaseGuardCells>0);
        ExerciseChecks->SetBoolField(TEXT("passive_guard_hides_unused_cast_timers"),!InspectorText().Contains(TEXT("First "))&&!InspectorText().Contains(TEXT("Cooldown")));
        CycleRelic();
        const int GuardRelic=SelectedPiece()->relic;
        const auto BaseGuard=Catalog.units[0].ability;
        const auto ChangedGuard=wc::EffectiveAbility(Catalog,Catalog.units[0],GuardRelic);
        UpdatePreparationPreview();
        ExerciseChecks->SetBoolField(TEXT("compatible_relic_changes_actual_guard_geometry"),GuardRelic>=0&&ChangedGuard.radius>BaseGuard.radius&&ChangedGuard.guardReductionBp<BaseGuard.guardReductionBp&&PreparationCells.Num()>BaseGuardCells);
        UnequipRelic();
        ExerciseChecks->SetBoolField(TEXT("unequip_restores_base_ability"),SelectedPiece()->relic==-1&&wc::EffectiveAbility(Catalog,Catalog.units[0],SelectedPiece()->relic).guardReductionBp==BaseGuard.guardReductionBp);
        CycleRelic();
        ChooseHero(0);EditCell({0,0},false);
        ExerciseChecks->SetBoolField(TEXT("duplicate_team_relic_rejected"),!EquipRelic(GuardRelic));
        RemoveSelected();
        Selected=Formation[0][1].id;CycleRelic();
        Selected=Formation[0][2].id;CycleRelic();
        Selected=Formation[0][3].id;CycleRelic();
        ExerciseChecks->SetBoolField(TEXT("maximum_three_relics_per_team"),Formation[0][0].relic>=0&&Formation[0][1].relic>=0&&Formation[0][2].relic>=0&&Formation[0][3].relic==-1);
        Selected=Formation[0][1].id;
        const int BeforeReplace=SelectedPiece()->relic;CycleRelic();
        ExerciseChecks->SetBoolField(TEXT("one_relic_per_hero_replacement"),SelectedPiece()->relic>=0&&SelectedPiece()->relic!=BeforeReplace&&Formation[0][3].relic==-1);
        Selected=Formation[1][0].id;
        ExerciseChecks->SetBoolField(TEXT("same_relic_allowed_on_opposing_team"),EquipRelic(GuardRelic));
        Selected=Formation[0][0].id;UpdatePreparationPreview();
        ExerciseChecks->SetNumberField(TEXT("guard_preview_cells_with_relic"),PreparationCells.Num());
        QueueCapture(TEXT("lab-guard-relic-preparation.png"),10);
    }else if(ExerciseStage==10){
        EditCell(wc::EncounterCell(Formation[0][5].cell,0,Catalog.rules),false);UpdatePreparationPreview();
        const int ForwardCells=PreparationCells.Num();
        bool InForwardLane=ForwardCells>0;
        for(const int Cell:PreparationCells)InForwardLane&=Cell%8==Formation[0][5].cell.column&&Cell/8>Formation[0][5].cell.row;
        ChangeFacing();UpdatePreparationPreview();
        bool InRightLane=PreparationCells.Num()>0;
        for(const int Cell:PreparationCells)InRightLane&=Cell/8==Formation[0][5].cell.row&&Cell%8>Formation[0][5].cell.column;
        ExerciseChecks->SetBoolField(TEXT("tidal_preparation_lane_rotates_with_facing"),InForwardLane&&InRightLane);
        ChangeFacing();ChangeFacing();ChangeFacing();UpdatePreparationPreview();
        ExerciseChecks->SetNumberField(TEXT("tidal_forward_preview_cells"),PreparationCells.Num());
        QueueCapture(TEXT("lab-tidal-preparation.png"),11);
    }else if(ExerciseStage==11){
        const bool Began=Start();TogglePause();
        bool FacingCorrect=Fight!=nullptr;
        if(Fight)for(const auto& Unit:Fight->Units())FacingCorrect&=Unit.facing==(Unit.side?wc::Facing::Backward:wc::Facing::Forward);
        ExerciseChecks->SetBoolField(TEXT("opponent_local_facing_rotates_into_world"),FacingCorrect);
        const int Before=Fight?Fight->CurrentTick():-1;
        Step();if(ExerciseDone)return;
        ExerciseChecks->SetBoolField(TEXT("pause_and_single_tick_step"),Began&&Paused&&Fight&&Fight->CurrentTick()==Before+1);
        const auto SizeBefore=Formation[0].size();
        const bool Removed=EditCell(wc::EncounterCell(Formation[0][0].cell,0,Catalog.rules),true);
        ExerciseChecks->SetBoolField(TEXT("combat_rejects_formation_edits"),!Removed&&Formation[0].size()==SizeBefore);
        Selected=Formation[0][0].id;const int BeforeRelic=SelectedPiece()->relic;
        const bool EquippedDuringCombat=EquipRelic(BeforeRelic);UnequipRelic();
        ExerciseChecks->SetBoolField(TEXT("combat_rejects_relic_edits"),!EquippedDuringCombat&&SelectedPiece()->relic==BeforeRelic);
        TogglePause();ExerciseStage=2;
    }else if(ExerciseStage==2){
        for(int I=0;I<8&&Fight&&!Fight->Result().complete&&!CombatInvariantFailed;++I)Advance();
        if(ExerciseDone)return;
        if(Fight&&Fight->CurrentTick()>=60&&ExerciseChecks&&!ExerciseChecks->HasField(TEXT("combat_capture_requested"))){
            if(Catalog.units[4].ability.mana.maximum>0){
                const wc::CombatUnit* Inspected=nullptr;
                for(const auto& U:Fight->Units())if(U.side==0&&OwnedId(U.id)==Formation[0][4].id){Inspected=&U;Selected=U.id;break;}
                const FString Inspection=InspectorText();
                ExerciseChecks->SetBoolField(TEXT("mana_inspector_uses_resource_not_cooldown"),Inspected&&
                    Inspection.StartsWith(Str(Catalog.units[4].name))&&Inspection.Contains(TEXT("Current battle stats"))&&
                    Inspection.Contains(FString::Printf(TEXT("Mana %.1f / 100"),Inspected->mana/100.))&&!Inspection.Contains(TEXT("Cooldown")));
                bool ManaBars=true;for(const auto& U:Fight->Units()){
                    const auto* View=Pieces.Find(U.id);
                    ManaBars&=View&&View->Mana&&View->Mana->IsVisible()==(U.health>0&&U.ability.mana.maximum>0&&(!ArtSlice||U.mana>0));
                    if(ArtSlice)ManaBars&=View&&View->ManaTrack&&View->ManaTrack->IsVisible()==(U.health>0&&U.ability.mana.maximum>0);
                }
                ExerciseChecks->SetBoolField(TEXT("mana_bars_match_live_resource_users"),ManaBars);
            }
            QueueCapture(TEXT("lab-combat.png"),2);
            ExerciseChecks->SetBoolField(TEXT("combat_capture_requested"),true);
            return;
        }
        if(Storybook&&Fight&&!ExerciseChecks->HasField(TEXT("storybook_defeat_capture_requested"))){
            const auto Defeated=std::find_if(Fight->Units().begin(),Fight->Units().end(),[](const auto& Unit){return Unit.health<=0;});
            if(Defeated!=Fight->Units().end()){
                Selected=Defeated->id;
                ExerciseChecks->SetBoolField(TEXT("storybook_defeat_capture_requested"),true);
                QueueCapture(TEXT("lab-defeat.png"),2);
                return;
            }
        }
        if(Fight&&Fight->Result().complete){
            FirstSignature=Signature();FirstEventCount=int(Fight->Events().size());
            ExerciseChecks->SetBoolField(TEXT("actual_combat_completed"),FirstEventCount>0);
            ExerciseChecks->SetBoolField(TEXT("first_combat_invariants"),Fight->InvariantError().empty());
            const auto OriginalSeed=Seed;
            Reset();Seed=OriginalSeed==MAX_int32?1:OriginalSeed+1;
            Start(true);
            ExerciseChecks->SetBoolField(TEXT("replay_restores_original_seed"),Seed==OriginalSeed);
            bool RelicsRestored=Fight!=nullptr;
            if(Fight)for(const auto& Unit:Fight->Units()){
                const auto& Roster=ReplayFormation[Unit.side];
                const auto Initial=std::find_if(Roster.begin(),Roster.end(),[&Unit](const wc::OwnedUnit& Owned){return Owned.id==OwnedId(Unit.id);});
                RelicsRestored&=Initial!=Roster.end()&&Initial->relic==Unit.relic;
            }
            ExerciseChecks->SetBoolField(TEXT("replay_restores_equipped_relics"),RelicsRestored);
            ExerciseStage=3;
        }
    }else if(ExerciseStage==3){
        for(int I=0;I<8&&Fight&&!Fight->Result().complete&&!CombatInvariantFailed;++I)Advance();
        if(ExerciseDone)return;
        if(Fight&&Fight->Result().complete){
            ExerciseChecks->SetBoolField(TEXT("replay_exact_event_and_final_state_signature"),Signature()==FirstSignature&&int(Fight->Events().size())==FirstEventCount);
            ExerciseChecks->SetBoolField(TEXT("replay_combat_invariants"),Fight->InvariantError().empty());
            ExerciseChecks->SetBoolField(TEXT("every_observed_tick_invariants"),!CombatInvariantFailed);
            ExerciseChecks->SetBoolField(TEXT("completed_within_exercise_limit"),true);
            Paused=true;
            Message=TEXT("Combat and replay resolved. Holding the final state while capture evidence finishes.");
            QueueCapture(TEXT("lab-replay-result.png"),4);
        }
    }else if(ExerciseStage==4){
        if(Storybook){
            bool DefeatedHidden=true;
            int ExpiredDefeats=0;
            if(Fight)for(const auto& Unit:Fight->Units())if(Unit.health<=0&&DefeatAge(Unit)>=.72f){
                ++ExpiredDefeats;
                const auto* View=Pieces.Find(Unit.id);
                DefeatedHidden&=View&&View->Actor.IsValid()&&View->Actor->IsHidden();
            }
            ExerciseChecks->SetBoolField(TEXT("storybook_actual_defeat_leaves_drawn"),CueKindsSeen.Contains(TEXT("storybook_defeat_leaves")));
            ExerciseChecks->SetBoolField(TEXT("storybook_expired_defeated_proxies_hidden"),ExpiredDefeats>0&&DefeatedHidden);
            ExerciseChecks->SetNumberField(TEXT("storybook_expired_defeat_count"),ExpiredDefeats);
            ExerciseChecks->SetBoolField(TEXT("storybook_cues_pool_bounded"),!CueOverflow);
            ExerciseChecks->SetBoolField(TEXT("storybook_four_ranged_identities_drawn"),
                CueKindsSeen.Contains(TEXT("root_seed_projectile"))&&CueKindsSeen.Contains(TEXT("snapvine_barbed_projectile"))&&
                CueKindsSeen.Contains(TEXT("prism_glass_projectile"))&&CueKindsSeen.Contains(TEXT("reefglass_crescent_projectile")));
        }
        bool CapturesComplete=CaptureRecords.Num()==(Storybook?6:5),CapturesSaved=CapturesComplete,CapturesStable=CapturesComplete,CapturesSettled=CapturesComplete,CaptureTextExact=CapturesComplete;
        bool BellbackText=false,ReefglassText=false;
        for(const auto& Value:CaptureRecords){
            const auto Record=Value->AsObject();
            CapturesComplete&=Record->GetBoolField(TEXT("completed"));
            CapturesSaved&=Record->GetBoolField(TEXT("new_file_saved"));
            CapturesStable&=Record->GetBoolField(TEXT("state_stable_through_capture"));
            CaptureTextExact&=Record->GetBoolField(TEXT("text_widgets_match_current_sources"));
            const FString CapturedInspector=Record->GetStringField(TEXT("inspector_widget_text"));
            if(Record->GetStringField(TEXT("file"))==TEXT("lab-preparation.png"))BellbackText=CapturedInspector.StartsWith(Str(Catalog.units[0].name)+TEXT("  ·  1 star\n"));
            if(Record->GetStringField(TEXT("file"))==TEXT("lab-tidal-preparation.png"))ReefglassText=CapturedInspector.StartsWith(Str(Catalog.units[5].name)+TEXT("  ·  1 star\n"))&&CapturedInspector.Contains(TEXT("\nHealth "))&&CapturedInspector.Contains(TEXT("\nArmor "))&&CapturedInspector.Contains(TEXT("Base stats; trait bonuses inactive in this lab"));
            CapturesSettled&=Record->GetNumberField(TEXT("presentation_ticks_before_request"))>=2&&Record->GetNumberField(TEXT("settled_seconds_before_request"))>=.15&&Record->GetNumberField(TEXT("settled_seconds_after_processing"))>=.15;
        }
        ExerciseChecks->SetBoolField(TEXT("all_captures_completed"),CapturesComplete);
        ExerciseChecks->SetBoolField(TEXT("all_captures_saved_new_files"),CapturesSaved);
        ExerciseChecks->SetBoolField(TEXT("capture_selection_and_combat_ticks_held"),CapturesStable);
        ExerciseChecks->SetBoolField(TEXT("captured_text_widgets_match_exact_current_sources"),CaptureTextExact);
        ExerciseChecks->SetBoolField(TEXT("inspector_updates_from_bellback_to_full_reefglass_text"),BellbackText&&ReefglassText);
        ExerciseChecks->SetBoolField(TEXT("captures_settled_before_request_and_after_processing"),CapturesSettled);
        bool Passed=true;
        for(const auto& Check:ExerciseChecks->Values)if(Check.Value->Type==EJson::Boolean)Passed&=Check.Value->AsBool();
        Passed=WriteEvidence(Passed);ExerciseDone=true;Paused=true;
        Message=Passed?TEXT("Local lab exercise passed: editing, relics, one-tick step, locked combat, identical replay and completed captures. Scripted coverage is not human play or art acceptance."):TEXT("Lab exercise failed. Inspect lab-exercise.json and the game log.");
    }
}
bool AWCVNextLab::WriteEvidence(bool Passed)
{
    auto Root=MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("schema"),TEXT("wonder_vnext.lab_exercise.1"));
    Root->SetStringField(TEXT("utc"),FDateTime::UtcNow().ToIso8601());
    Root->SetBoolField(TEXT("passed"),Passed);
    Root->SetStringField(TEXT("input_boundary"),TEXT("Native Unreal Slate constructed; scripted calls exercise the same handlers as its buttons. Physical pointer hit testing and human usability are not certified."));
    Root->SetStringField(TEXT("art_status"),TEXT("UNAPPROVED_GAMEPLAY_PROXIES"));
    Root->SetBoolField(TEXT("art_slice_enabled"),ArtSlice);
    Root->SetBoolField(TEXT("storybook_enabled"),Storybook);
    if(Storybook){
        Root->SetBoolField(TEXT("sanctuary_world_material_loaded"),SanctuaryMaterial!=nullptr);
        Root->SetBoolField(TEXT("sanctuary_world_backdrop_loaded"),SanctuaryBackdrop!=nullptr);
        Root->SetStringField(TEXT("storybook_art_status"),TEXT("EXPANDED_ASSET_CANDIDATE_PENDING_OWNER_REVIEW"));
    }
    if(ArtSlice){
        Root->SetBoolField(TEXT("art_slice_ui_resources_ready"),FWCArtSlice::ResourcesReady());
        Root->SetBoolField(TEXT("quiet_stone_material_loaded"),QuietStoneMaterial!=nullptr);
        Root->SetNumberField(TEXT("placement_preview_state"),PlacementPreviewState);
        Root->SetStringField(TEXT("art_slice_status"),TEXT("IN_GAME_STUDY_CANDIDATE_PENDING_OWNER_REVIEW"));
    }
    TArray<TSharedPtr<FJsonValue>> CueKinds;for(const auto& Kind:CueKindsSeen)CueKinds.Add(MakeShared<FJsonValueString>(Kind));
    Root->SetArrayField(TEXT("rendered_cue_kinds"),CueKinds);
    Root->SetNumberField(TEXT("peak_cue_meshes"),PeakCueMeshes);Root->SetNumberField(TEXT("peak_cue_texts"),PeakCueTexts);
    Root->SetBoolField(TEXT("cue_pool_overflow"),CueOverflow);
    Root->SetStringField(TEXT("profile"),TEXT("wonder_vnext"));
    Root->SetStringField(TEXT("catalog_digest"),Str(Catalog.contentDigest));
    Root->SetArrayField(TEXT("captures"),CaptureRecords);
    Root->SetStringField(TEXT("load_error"),LoadError);
    Root->SetNumberField(TEXT("seed"),ReplaySeed);
    Root->SetNumberField(TEXT("wall_seconds"),Elapsed);
    if(Controller&&Interface&&BoardInput){
        int Width=0,Height=0;Controller->GetViewportSize(Width,Height);
        Root->SetNumberField(TEXT("viewport_width"),Width);Root->SetNumberField(TEXT("viewport_height"),Height);
        const FSlateRect BoardBounds=BoardPixelBounds();
        auto Bounds=MakeShared<FJsonObject>();
        Bounds->SetNumberField(TEXT("left"),BoardBounds.Left);Bounds->SetNumberField(TEXT("top"),BoardBounds.Top);Bounds->SetNumberField(TEXT("right"),BoardBounds.Right);Bounds->SetNumberField(TEXT("bottom"),BoardBounds.Bottom);
        Root->SetObjectField(TEXT("board_pixel_bounds"),Bounds);
        int Inside=0,RoundTrips=0;
        for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column){
            FVector2D Screen;
            if(Width>0&&Height>0&&Controller->ProjectWorldLocationToScreen(Position({Column,Row}),Screen)){
                if(Screen.X>BoardBounds.Left&&Screen.X<BoardBounds.Right&&Screen.Y>BoardBounds.Top&&Screen.Y<BoardBounds.Bottom)++Inside;
                FVector Origin,Direction;
                if(Controller->DeprojectScreenPositionToWorld(Screen.X,Screen.Y,Origin,Direction)&&FMath::Abs(Direction.Z)>.0001f){
                    const FVector P=Origin-Direction*(Origin.Z/Direction.Z);
                    if(FMath::FloorToInt((P.X+800)/200)==Column&&FMath::FloorToInt((800-P.Y)/200)==Row)++RoundTrips;
                }
            }
        }
        Root->SetNumberField(TEXT("cell_centers_inside_unobstructed_board"),Inside);
        Root->SetNumberField(TEXT("project_deproject_cell_roundtrips"),RoundTrips);
        FVector2D ProjectedMin(MAX_flt,MAX_flt),ProjectedMax(-MAX_flt,-MAX_flt);
        int CornersInside=0;
        for(int X:{-1,1})for(int Y:{-1,1}){
            FVector2D Screen;
            if(Controller->ProjectWorldLocationToScreen(FVector(X*800,Y*800,0),Screen)){
                ProjectedMin.X=FMath::Min(ProjectedMin.X,Screen.X);ProjectedMin.Y=FMath::Min(ProjectedMin.Y,Screen.Y);
                ProjectedMax.X=FMath::Max(ProjectedMax.X,Screen.X);ProjectedMax.Y=FMath::Max(ProjectedMax.Y,Screen.Y);
                if(Screen.X>BoardBounds.Left&&Screen.X<BoardBounds.Right&&Screen.Y>BoardBounds.Top&&Screen.Y<BoardBounds.Bottom)++CornersInside;
            }
        }
        auto Projected=MakeShared<FJsonObject>();
        Projected->SetNumberField(TEXT("left"),ProjectedMin.X);Projected->SetNumberField(TEXT("top"),ProjectedMin.Y);
        Projected->SetNumberField(TEXT("right"),ProjectedMax.X);Projected->SetNumberField(TEXT("bottom"),ProjectedMax.Y);
        Root->SetObjectField(TEXT("projected_board_pixel_bounds"),Projected);
        const double BoardWidth=FMath::Max(1.f,BoardBounds.Right-BoardBounds.Left),BoardHeight=FMath::Max(1.f,BoardBounds.Bottom-BoardBounds.Top);
        const double HeightFraction=(ProjectedMax.Y-ProjectedMin.Y)/BoardHeight,WidthFraction=(ProjectedMax.X-ProjectedMin.X)/BoardWidth;
        Root->SetNumberField(TEXT("board_height_fraction_of_pane"),HeightFraction);
        Root->SetNumberField(TEXT("board_width_fraction_of_pane"),WidthFraction);
        const bool Fitted=CornersInside==4&&WidthFraction<=.95&&HeightFraction<=.88&&(HeightFraction>=.72||WidthFraction>=.88);
        if(ExerciseChecks){ExerciseChecks->SetBoolField(TEXT("all_64_cell_centers_visible"),Inside==64);ExerciseChecks->SetBoolField(TEXT("all_64_click_projection_roundtrips"),RoundTrips==64);}
        if(ExerciseChecks)ExerciseChecks->SetBoolField(TEXT("board_fills_available_pane_without_clipping"),Fitted);
        Passed&=Inside==64&&RoundTrips==64&&Fitted;
        Root->SetBoolField(TEXT("passed"),Passed);
    }
    Root->SetObjectField(TEXT("checks"),ExerciseChecks.IsValid()?ExerciseChecks:MakeShared<FJsonObject>());
    TArray<TSharedPtr<FJsonValue>> Rosters;
    for(int Side=0;Side<2;++Side)for(const auto& U:ReplayFormation[Side]){
        auto Row=MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("side"),Side);Row->SetNumberField(TEXT("id"),U.id);
        Row->SetStringField(TEXT("hero_id"),Str(Catalog.units[U.definition].id));
        Row->SetNumberField(TEXT("star"),U.star);Row->SetNumberField(TEXT("column"),U.cell.column);Row->SetNumberField(TEXT("row"),U.cell.row);Row->SetNumberField(TEXT("facing"),int(U.facing));
        Row->SetNumberField(TEXT("relic_index"),U.relic);
        Row->SetStringField(TEXT("relic_id"),U.relic>=0&&U.relic<int(Catalog.relics.size())?Str(Catalog.relics[U.relic].id):TEXT(""));
        Rosters.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("initial_formations"),Rosters);
    Root->SetStringField(TEXT("first_signature"),FirstSignature);
    Root->SetStringField(TEXT("replay_signature"),Signature());
    if(Fight){
        Root->SetNumberField(TEXT("event_count"),Fight->Events().size());
        Root->SetNumberField(TEXT("ticks"),Fight->CurrentTick());
        Root->SetNumberField(TEXT("winner"),Fight->Result().winner);
        Root->SetBoolField(TEXT("timeout"),Fight->Result().timeout);
        TArray<TSharedPtr<FJsonValue>> Events;
        auto Counts=MakeShared<FJsonObject>();TMap<int,int> MechanicCounts;
        for(const auto& E:Fight->Events()){
            MechanicCounts.FindOrAdd(int(E.mechanic))++;
            auto Row=MakeShared<FJsonObject>();
            Row->SetNumberField(TEXT("tick"),E.tick);Row->SetNumberField(TEXT("source"),E.source);Row->SetNumberField(TEXT("target"),E.target);Row->SetNumberField(TEXT("action"),E.action);
            Row->SetStringField(TEXT("effect"),EffectName(E.effect));Row->SetNumberField(TEXT("mechanic"),int(E.mechanic));
            Row->SetBoolField(TEXT("basic_attack"),E.basicAttack);
            Row->SetNumberField(TEXT("resolved_cp"),E.resolved);Row->SetNumberField(TEXT("health_loss_cp"),E.healthLoss);Row->SetNumberField(TEXT("absorbed_cp"),E.absorbed);Row->SetNumberField(TEXT("prevented_cp"),E.prevented);
            Row->SetNumberField(TEXT("column"),E.cell.column);Row->SetNumberField(TEXT("row"),E.cell.row);
            Events.Add(MakeShared<FJsonValueObject>(Row));
        }
        for(const auto& Pair:MechanicCounts)Counts->SetNumberField(FString::FromInt(Pair.Key),Pair.Value);
        Root->SetObjectField(TEXT("observed_event_mechanic_counts"),Counts);
        Root->SetArrayField(TEXT("events"),Events);
    }
    FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Root,Writer);
    IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
    const bool Saved=FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("lab-exercise.json")));
    UE_LOG(LogTemp,Display,TEXT("WC_VNEXT_LAB_EXERCISE passed=%d saved=%d path=%s"),Passed,Saved,*(EvidenceDirectory/TEXT("lab-exercise.json")));
    return Passed&&Saved;
}

void AWCVNextLab::StartStatusTest()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    Fight.reset();StatusTestCatalog=std::make_unique<wc::Catalog>(wctest::StatusCueCatalog(Catalog));
    wc::OwnedUnit A;A.id=900;A.definition=0;A.onBoard=true;A.cell={3,3};
    wc::OwnedUnit B=A;B.id=901;B.definition=1;B.cell={4,3};
    Fight=std::make_unique<wc::Combat>(*StatusTestCatalog,std::vector<wc::OwnedUnit>{A},std::vector<wc::OwnedUnit>{B},Seed);
    StatusTest=true;Paused=false;Accumulator=0;Selected=Fight->Units().back().id;
    Message=TEXT("Synthetic status test: damage, effective heal, shield, stun and slow. These are test effects, not Bellback or Cragstoat abilities. Reset restores your real formation.");
}
