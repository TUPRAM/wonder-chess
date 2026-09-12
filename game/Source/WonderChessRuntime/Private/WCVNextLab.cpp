#include "WCVNextLab.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "Materials/MaterialInstanceDynamic.h"
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
#include "Widgets/SViewport.h"
#include "Widgets/Text/STextBlock.h"
#include <algorithm>
#include <tuple>

namespace
{
const FLinearColor Ink(.018f, .032f, .042f, .97f), Paper(.89f, .92f, .85f), Gold(.98f, .75f, .34f);
const FLinearColor Teams[] = {{.13f,.72f,.68f}, {.92f,.36f,.24f}};
const FLinearColor HeroColors[] = {{.64f,.56f,.28f}, {.42f,.55f,.64f}, {.35f,.55f,.22f}, {.56f,.26f,.34f}, {.42f,.38f,.75f}, {.22f,.70f,.69f}};
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
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Surface(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    ProxyMeshes.Add(TEXT("Cube"),Cube.Object);ProxyMeshes.Add(TEXT("Sphere"),Sphere.Object);
    ProxyMeshes.Add(TEXT("Cylinder"),Cylinder.Object);ProxyMeshes.Add(TEXT("Cone"),Cone.Object);
    ProxyMaterial=Surface.Object;
}
AWCVNextLab::~AWCVNextLab() = default;

void AWCVNextLab::Initialize()
{
    Controller = Cast<AWCVNextLabController>(GetWorld()->GetFirstPlayerController());
    Exercise = FParse::Param(FCommandLine::Get(), TEXT("WCLabExercise"));
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
        if(!ProxyMaterial)LoadError=TEXT("The lab's engine proxy material is missing from this build.");
        for(const auto& Entry:ProxyMeshes)if(!Entry.Value)LoadError=TEXT("A required engine proxy mesh is missing from this build: ")+Entry.Key;
    }
    if (LoadError.IsEmpty()) {
        BuildScene();
        Preset();
        UE_LOG(LogTemp, Display, TEXT("WC_VNEXT_LAB_READY profile=wonder_vnext units=%d digest=%s proxy_art=UNAPPROVED"), int(Catalog.units.size()), *Str(Catalog.contentDigest));
    } else {
        Message = LoadError;
        UE_LOG(LogTemp, Error, TEXT("WC_VNEXT_LAB_REJECTED %s"), *LoadError);
    }
    BuildInterface();
    if (Exercise) {
        ExerciseChecks = MakeShared<FJsonObject>();
        ExerciseChecks->SetBoolField(TEXT("native_slate_created"), Interface.IsValid());
        ExerciseChecks->SetBoolField(TEXT("vnext_profile_loaded"), LoadError.IsEmpty());
        if (!LoadError.IsEmpty()) { WriteEvidence(false); ExerciseDone = true; }
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
    Mesh(Ground, TEXT("Cube"), FVector(0,0,-45), FVector(17.2,17.2,.7), FLinearColor(.10f,.16f,.14f));
    for (int Row = 0; Row < 8; ++Row) for (int Column = 0; Column < 8; ++Column) {
        const FVector P = Position({Column, Row});
        const FLinearColor Color = (Row+Column)%2 ? FLinearColor(.23f,.30f,.25f) : FLinearColor(.32f,.39f,.31f);
        Cells.Add(Mesh(Ground, TEXT("Cube"), P, FVector(1.94,1.94,.12), Color));
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
        Mesh(Ground, TEXT("Cube"), FVector(0, Side ? -826 : 826, 8), FVector(16.8,.12,.1), Teams[Side]);
    auto* Light = GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,1000), FRotator(-55,-35,0));
    Light->GetLightComponent()->SetIntensity(4);
    SceneActors.Add(Light);
    auto* Sky = GetWorld()->SpawnActor<ASkyLight>();
    Sky->GetLightComponent()->SetIntensity(.75f);
    Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Sky->GetLightComponent()->bRealTimeCapture = true;
    SceneActors.Add(Sky);
    Camera = GetWorld()->SpawnActor<ACameraActor>();
    Camera->GetCameraComponent()->SetProjectionMode(ECameraProjectionMode::Orthographic);
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
void AWCVNextLab::UpdateCamera()
{
    if(!Camera||!Controller)return;
    int Width=0,Height=0;Controller->GetViewportSize(Width,Height);if(Width<=0||Height<=0)return;
    const FSlateRect Bounds=BoardPixelBounds();
    const FVector2D BoardSize(Bounds.Right-Bounds.Left,Bounds.Bottom-Bounds.Top);
    const FVector2D BoardCenter((Bounds.Left+Bounds.Right)*.5,(Bounds.Top+Bounds.Bottom)*.5);
    const float WorldPerPixel=FMath::Max(1740.f/FMath::Max(1.f,float(BoardSize.X)),1640.f/FMath::Max(1.f,float(BoardSize.Y)));
    Camera->GetCameraComponent()->SetOrthoWidth(WorldPerPixel*Width);
    const FVector2D Offset=BoardCenter-FVector2D(Width,Height)*.5f;
    const FVector Target(-Offset.X*WorldPerPixel,-Offset.Y*WorldPerPixel/.818f,0);
    const FVector Location=Target+FVector(0,1900,2700);
    Camera->SetActorLocation(Location);
    Camera->SetActorRotation((Target-Location).Rotation());
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
    const auto EditEnabled = [this]{return !Fight && LoadError.IsEmpty();};
    auto Sidebar = SNew(SScrollBox)
    +SScrollBox::Slot().Padding(12,10)
    [SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,7)
        [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),17)).ColorAndOpacity(Gold).Text(Txt(TEXT("FORMATION WORKBENCH")))]
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
                    .Text(Txt(TEXT("wonder_vnext  ·  UNAPPROVED GAMEPLAY PROXIES  ·  Formation and combat experiment; not the finished art or full tournament.")))]
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
    if(!Controller->DeprojectMousePositionToWorld(Origin,Direction)||FMath::Abs(Direction.Z)<.0001f)return false;
    const double T=-Origin.Z/Direction.Z;
    if(T<0)return false;
    const FVector P=Origin+Direction*T;
    const wc::Cell Cell{FMath::FloorToInt((P.X+800)/200),FMath::FloorToInt((800-P.Y)/200)};
    if(Cell.column<0||Cell.column>=8||Cell.row<0||Cell.row>=8)return false;
    return EditCell(Cell,Remove);
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
    if(!LoadError.IsEmpty())return false;
    if(FromReplay){
        if(ReplayFormation[0].empty()||ReplayFormation[1].empty()){Message=TEXT("Start a battle first to record its replay inputs.");return false;}
        Formation=ReplayFormation;Seed=ReplaySeed;
    }else{
        if(Fight){Message=TEXT("Reset to edit, or use Replay for the identical starting formation and seed.");return false;}
        if(Formation[0].empty()||Formation[1].empty()){Message=TEXT("Place at least one creature on each side before Start.");return false;}
        ReplayFormation=Formation;ReplaySeed=Seed;
    }
    Fight=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
    Paused=false;Accumulator=0;Selected=0;CombatInvariantFailed=false;
    Message=FromReplay?TEXT("Replaying the exact saved formation and seed through authoritative combat."):TEXT("Combat running. Gold outlines show the core's actual pending skill cells. Formation is locked.");
    UE_LOG(LogTemp,Display,TEXT("WC_VNEXT_LAB_START seed=%d a=%d b=%d replay=%d"),Seed,int(Formation[0].size()),int(Formation[1].size()),FromReplay);
    return true;
}
void AWCVNextLab::TogglePause(){if(Fight&&!Fight->Result().complete&&!CombatInvariantFailed){Paused=!Paused;Message=Paused?TEXT("Paused. Step advances exactly one authoritative tick."):TEXT("Combat resumed.");}}
void AWCVNextLab::Step(){if(!Fight&&!Start())return;Paused=true;Advance();}
void AWCVNextLab::Reset(){Fight.reset();Paused=false;Accumulator=0;Selected=0;CombatInvariantFailed=false;PreparationDirty=true;Message=TEXT("Preparation restored. Both original formations are editable.");}
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

void AWCVNextLab::AddPieceView(uint64 Id,int Definition,int Side)
{
    auto* Actor=SceneActor();
    const FLinearColor Color=HeroColors[Definition%6];
    Mesh(Actor,TEXT("Cylinder"),FVector(0,0,13),FVector(1.16,1.16,.13),Teams[Side]);
    Mesh(Actor,TEXT("Cone"),FVector(0,54,27),FVector(.20,.20,.44),Paper,FRotator(0,0,-90));
    const auto Part=[&](const TCHAR* Shape,FVector P,FVector Scale,FLinearColor C,FRotator R=FRotator::ZeroRotator){return Mesh(Actor,Shape,P,Scale,C,R);};
    switch(Definition%6){
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
    auto* Bar=Mesh(Actor,TEXT("Cube"),FVector(0,0,176),FVector(1.12,.065,.065),Teams[Side]);
    Bar->SetCastShadow(false);
    auto* Backing=Mesh(Actor,TEXT("Cube"),FVector(0,0,220),FVector(.03,1.4,.5),FLinearColor(.015f,.022f,.026f));
    Backing->SetCastShadow(false);
    auto* Label=NewObject<UTextRenderComponent>(Actor);
    Actor->AddInstanceComponent(Label);Label->SetupAttachment(Actor->GetRootComponent());
    Label->SetRelativeLocation(FVector(0,0,220));Label->SetHorizontalAlignment(EHTA_Center);Label->SetVerticalAlignment(EVRTA_TextCenter);Label->SetWorldSize(32);
    Label->SetTextRenderColor(FColor(236,242,217));Label->SetCastShadow(false);Label->RegisterComponent();
    Pieces.Add(Id,FPieceView{Actor,Bar,Backing,Label,Definition,Side});
}

void AWCVNextLab::UpdatePreparationPreview()
{
    PreparationCells.Reset();PreparationRecipient=0;PreparationHint.Empty();
    if(Fight)return;
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
        for(const auto& Unit:PreparationState->Units())if(Unit.side==Source->side&&Unit.id!=Source->id&&PreparationCells.Contains(Unit.cell.row*8+Unit.cell.column)){
            if(!Recipient||std::make_tuple(wc::Distance(Source->cell,Unit.cell),Unit.initiative)<std::make_tuple(wc::Distance(Source->cell,Recipient->cell),Recipient->initiative))Recipient=&Unit;
        }
        PreparationRecipient=Recipient?OwnedId(Recipient->id):0;
        PreparationHint=TEXT("Spatial intent: teal = eligible rear cells. ");
        PreparationHint+=Recipient?TEXT("Gold = current eligible ally, ")+Str(Catalog.units[Recipient->definition].displayName)+TEXT(". "):TEXT("No ally currently occupies them. ");
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
    UpdatePreparationPreview();
    int Width=0,Height=0;if(Controller)Controller->GetViewportSize(Width,Height);
    const float PixelWorld=Camera&&Width>0?Camera->GetCameraComponent()->OrthoWidth/Width:2;
    TSet<uint64> Alive;
    const auto Present=[&](uint64 Id,int Def,int Side,int Star,wc::Cell Cell,wc::Facing Facing,wc::Int Health,wc::Int MaxHealth,wc::ActionState State){
        Alive.Add(Id);
        if(!Pieces.Contains(Id))AddPieceView(Id,Def,Side);
        auto& View=Pieces.FindChecked(Id);
        auto* Actor=View.Actor.Get();if(!Actor)return;
        FVector Target=Position(Cell);
        if(Fight&&Health>0)Target.Z=(Def%6==4||Def%6==5)?FMath::Sin(Elapsed*2+Id)*5:0;
        const FVector Location=Fight?FMath::VInterpTo(Actor->GetActorLocation(),Target,DeltaSeconds,18):Target;
        Actor->SetActorLocation(Location);
        Actor->SetActorRotation(FRotator(0,int(Facing)*90+180,0));
        Actor->SetActorScale3D(Health>0?FVector(1):FVector(1,1,.22));
        const float Fraction=MaxHealth>0?FMath::Clamp(float(double(Health)/MaxHealth),0.f,1.f):1;
        View.Health->SetRelativeScale3D(FVector(Fraction*1.12,.065,.065));
        View.Health->SetWorldRotation(FRotator::ZeroRotator);
        View.Health->SetVisibility(Health>0);
        const FString Name=Str(Catalog.units[Def].displayName);
        const TCHAR* Mark=State==wc::ActionState::CastWindup?TEXT("  CAST"):State==wc::ActionState::Stunned?TEXT("  STUN"):TEXT("");
        View.Label->SetText(Txt(FString::Printf(TEXT("%s\n%s *%d%s"),*Name,Side?TEXT("B"):TEXT("A"),Star,Mark)));
        View.Label->SetWorldSize(PixelWorld*18);
        const float LabelWidth=View.Label->GetTextLocalSize().Y;
        if(LabelWidth>PixelWorld*130)View.Label->SetWorldSize(PixelWorld*18*(PixelWorld*130/LabelWidth));
        View.Label->SetVisibility(Health>0);
        View.LabelBacking->SetVisibility(Health>0);
        if(Camera){
            const FRotator Rotation=(-Camera->GetActorForwardVector()).Rotation();
            View.Label->SetWorldRotation(Rotation);
            const FVector Size=View.Label->GetTextLocalSize();
            View.LabelBacking->SetWorldRotation(Rotation);
            View.LabelBacking->SetWorldLocation(View.Label->GetComponentLocation()-Rotation.Vector()*3);
            View.LabelBacking->SetWorldScale3D(FVector(.03,(Size.Y+PixelWorld*8)/100,(Size.Z+PixelWorld*4)/100));
        }
    };
    if(Fight){
        for(const auto& U:Fight->Units())Present(U.id,U.definition,U.side,U.star,U.cell,U.facing,U.health,U.maxHealth,U.state);
    }else{
        for(int Side=0;Side<2;++Side)for(const auto& U:Formation[Side]){
            const auto Facing=static_cast<wc::Facing>((int(U.facing)+Side*2)%4);
            const auto HP=wc::StarValue(Catalog.units[U.definition].health,U.star,0,Catalog.rules);
            Present(U.id,U.definition,Side,U.star,wc::EncounterCell(U.cell,Side,Catalog.rules),Facing,HP,HP,wc::ActionState::Idle);
        }
    }
    for(auto It=Pieces.CreateIterator();It;++It)if(!Alive.Contains(It.Key())){
        if(auto* Actor=It.Value().Actor.Get()){SceneActors.Remove(Actor);Actor->Destroy();}
        It.RemoveCurrent();
    }
    TSet<int> Marked;
    int RecipientCell=-1;
    if(Fight)for(const auto& Action:Fight->VisualActions())if(!Action.basicAttack){
        for(const auto& Cell:Action.cells)if(Cell.column>=0&&Cell.column<8&&Cell.row>=0&&Cell.row<8)Marked.Add(Cell.row*8+Cell.column);
        if(Action.cells.empty()&&Action.center.column>=0&&Action.center.column<8&&Action.center.row>=0&&Action.center.row<8)
            for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column)
                if(wc::Distance({Column,Row},Action.center)<=Action.radius)Marked.Add(Row*8+Column);
    }
    if(!Fight){
        Marked=PreparationCells;
        for(int Side=0;Side<2;++Side)for(const auto& Owned:Formation[Side]){
            const auto Cell=wc::EncounterCell(Owned.cell,Side,Catalog.rules);
            if(Owned.id==Selected)Marked.Add(Cell.row*8+Cell.column);
            if(Owned.id==PreparationRecipient)RecipientCell=Cell.row*8+Cell.column;
        }
    }
    for(int Index=0;Index<Telegraphs.Num();++Index){
        Telegraphs[Index]->SetVisibility(Marked.Contains(Index/4));
        const auto Color=!Fight&&PreparationCells.Contains(Index/4)&&RecipientCell!=Index/4?Teams[0]:Gold;
        Telegraphs[Index]->SetMaterial(0,Material(Color));
    }
    ++PresentationFrames;
}

FString AWCVNextLab::StatusText() const
{
    if(!LoadError.IsEmpty())return TEXT("PROFILE REJECTED: ")+LoadError;
    if(!Fight)return FString::Printf(TEXT("PREPARATION  ·  A %d/10  |  B %d/10  ·  Seed %d  ·  Choose positions and facing before combat"),int(Formation[0].size()),int(Formation[1].size()),Seed);
    return FString::Printf(TEXT("%s  ·  %.2fs  ·  Tick %d  ·  Events %d  ·  Seed %d"),Fight->Result().complete?TEXT("RESOLVED"):Paused?TEXT("PAUSED"):TEXT("COMBAT"),Fight->CurrentTick()*Catalog.rules.tickMs/1000.,Fight->CurrentTick(),int(Fight->Events().size()),Seed);
}
FString AWCVNextLab::InspectorText() const
{
    if(!LoadError.IsEmpty())return LoadError;
    int Def=Palette,Star=BrushStar,Relic=-1;
    const wc::CombatUnit* CombatPiece=nullptr;
    if(Fight)for(const auto& U:Fight->Units())if(U.id==Selected){CombatPiece=&U;Def=U.definition;Star=U.star;Relic=U.relic;}
    if(!Fight)for(const auto& Side:Formation)for(const auto& U:Side)if(U.id==Selected){Def=U.definition;Star=U.star;Relic=U.relic;}
    if(Def<0||Def>=int(Catalog.units.size()))return FString();
    const auto& D=Catalog.units[Def];
    const auto HP=CombatPiece?CombatPiece->health:wc::StarValue(D.health,Star,0,Catalog.rules);
    const auto Maximum=CombatPiece?CombatPiece->maxHealth:HP;
    const auto Damage=CombatPiece?CombatPiece->basicDamage:wc::StarValue(D.attackDamage,Star,0,Catalog.rules);
    FString Result=FString::Printf(TEXT("%s  ·  %d star\n%s / %s\n%s\nHealth %.0f / %.0f   Basic %.0f\nArmor %d   Resist %d   Range %d\n\n%s\n"),*Str(D.name),Star,*Str(D.race),*Str(D.unitClass),CombatPiece?TEXT("Current battle stats"):TEXT("Base stats; trait bonuses inactive in this lab"),HP/100.,Maximum/100.,Damage/100.,CombatPiece?CombatPiece->armor:D.armor,CombatPiece?CombatPiece->resistance:D.resistance,D.range,*Str(D.ability.name));
    if(const auto* Full=Metadata.Units.Find(Str(D.id));Full&&Full->IsValid()){
        const TSharedPtr<FJsonObject>* Ability=nullptr;
        FString Tooltip;
        if((*Full)->TryGetObjectField(TEXT("ability"),Ability)&&Ability&&(*Ability)->TryGetStringField(TEXT("tooltip_en"),Tooltip))Result+=Tooltip+TEXT("\n");
    }
    const auto A=CombatPiece?CombatPiece->ability:wc::EffectiveAbility(Catalog,D,Relic);
    if(A.mechanic==wc::AbilityMechanic::DirectionalGuard)
        Result+=FString::Printf(TEXT("Passive guard · no activation timer\nPrevents %.1f%% damage from frontal sources\nRear radius %d · nearest eligible ally"),A.guardReductionBp/100.,A.radius);
    else{
        Result+=FString::Printf(TEXT("First %.2fs  |  Cooldown %.2fs\nWindup %.2fs  |  Reach %d\n%s %.2f  |  Radius %d"),A.firstCastMs/1000.,A.cooldownMs/1000.,A.castMs/1000.,A.range,A.mechanic==wc::AbilityMechanic::StationaryGrove?TEXT("Heal per pulse"):A.effect==wc::Effect::Heal?TEXT("Heal"):TEXT("Base effect"),A.magnitude[Star-1]/100.,A.radius);
        if(A.mechanic==wc::AbilityMechanic::StationaryGrove)
            Result+=FString::Printf(TEXT("\nPulse interval %.2fs  |  Area duration %.2fs"),A.pulseMs/1000.,A.durationMs/1000.);
        if(CombatPiece)Result+=FString::Printf(TEXT("\nNext readiness in %.2fs"),FMath::Max(0,CombatPiece->cooldownTick-Fight->CurrentTick())*Catalog.rules.tickMs/1000.);
    }
    if(CombatPiece)Result+=FString::Printf(TEXT("\nShield %.0f  |  Facing %s"),CombatPiece->shield/100.,FacingName(CombatPiece->facing));
    Result+=TEXT("\n\nRelic: ");
    if(Relic>=0&&Relic<int(Catalog.relics.size()))Result+=Str(Catalog.relics[Relic].name)+TEXT("\n")+Str(Catalog.relics[Relic].description)+TEXT("\nValues above include its actual transforms.");
    else Result+=TEXT("None");
    if(!Fight&&!PreparationHint.IsEmpty())Result+=TEXT("\n\n")+PreparationHint;
    return Result;
}
FString AWCVNextLab::EventText() const
{
    if(!Fight)return TEXT("Start or Step to inspect real combat events. No predicted winner is substituted.");
    const auto& Events=Fight->Events();
    FString Result;
    const int StartIndex=FMath::Max(0,int(Events.size())-8);
    for(int Index=int(Events.size())-1;Index>=StartIndex;--Index){
        const auto& E=Events[Index];
        Result+=FString::Printf(TEXT("t%d  #%llu → #%llu  %s  %.2f"),E.tick,E.source,E.target,EffectName(E.effect),E.resolved/100.);
        if(E.absorbed)Result+=FString::Printf(TEXT("  absorbed %.2f"),E.absorbed/100.);
        if(E.prevented)Result+=FString::Printf(TEXT("  guarded %.2f"),E.prevented/100.);
        Result+=TEXT("\n");
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
void AWCVNextLab::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);Elapsed+=DeltaSeconds;
    if(!LoadError.IsEmpty())return;
    UpdateCamera();
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
    CaptureSelected=Selected;CaptureCombatTick=Fight?Fight->CurrentTick():-1;
    CaptureResumeStage=ResumeStage;CaptureStateStable=true;
    CapturePhase=ECapturePhase::Settling;
    CaptureRecord=MakeShared<FJsonObject>();
    CaptureRecord->SetStringField(TEXT("file"),Filename);
    CaptureRecord->SetNumberField(TEXT("queued_at_seconds"),Elapsed);
    CaptureRecord->SetNumberField(TEXT("selected_id"),Selected);
    CaptureRecord->SetNumberField(TEXT("combat_tick"),CaptureCombatTick);
    CaptureRecords.Add(MakeShared<FJsonValueObject>(CaptureRecord));
}
void AWCVNextLab::TickCapture()
{
    if(CapturePhase==ECapturePhase::None)return;
    CaptureStateStable&=Selected==CaptureSelected&&(Fight?Fight->CurrentTick():-1)==CaptureCombatTick;
    if(Elapsed-CaptureQueuedAt>15){
        CaptureRecord->SetBoolField(TEXT("completed"),false);
        ExerciseChecks->SetBoolField(TEXT("all_captures_completed"),false);
        CapturePhase=ECapturePhase::None;ExerciseDone=true;Paused=true;
        Message=TEXT("Screenshot processing timed out. Capture evidence failed; inspect lab-exercise.json.");
        WriteEvidence(false);return;
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
        CaptureRecord->SetBoolField(TEXT("text_widgets_match_current_sources"),
            InspectorBlock&&InspectorBlock->GetText().ToString()==InspectorSource&&
            EventBlock&&EventBlock->GetText().ToString()==EventText()&&
            StatusBlock&&StatusBlock->GetText().ToString()==StatusText()&&
            MessageBlock&&MessageBlock->GetText().ToString()==Message);
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

void AWCVNextLab::TickExercise()
{
    if(CombatInvariantFailed)return;
    if(Elapsed>90){ExerciseChecks->SetBoolField(TEXT("completed_within_exercise_limit"),false);WriteEvidence(false);ExerciseDone=true;Paused=true;return;}
    if(ExerciseStage==0){
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        QueueCapture(TEXT("lab-preparation.png"),1);
    }else if(ExerciseStage==1){
        ClearFormation();
        ExerciseChecks->SetBoolField(TEXT("empty_start_rejected"),!Start());
        ChooseHero(0);EditCell({0,0},false);
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
            QueueCapture(TEXT("lab-combat.png"),2);
            ExerciseChecks->SetBoolField(TEXT("combat_capture_requested"),true);
            return;
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
        bool CapturesComplete=CaptureRecords.Num()==5,CapturesSaved=CapturesComplete,CapturesStable=CapturesComplete,CapturesSettled=CapturesComplete,CaptureTextExact=CapturesComplete;
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
