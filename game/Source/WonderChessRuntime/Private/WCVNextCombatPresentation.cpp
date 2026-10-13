#include "WCVNextLab.h"
#include "WCHeroPresentation.h"
#include "Components/PointLightComponent.h"
#include "Dom/JsonObject.h"
#include "Misc/Paths.h"
#include "WCSilkmotherPresentation.h"
#include "WCBellbackPresentation.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Widgets/SWidget.h"
#include <algorithm>

namespace
{
const FLinearColor Strike(1,.65f,.22f), Shot(1,.9f,.55f), Heal(.2f,1,.4f), Shield(.3f,.8f,1),
    Stun(.95f,.7f,1), Hurt(1,.3f,.22f), Vine(1,.25f,.6f), Prism(.7f,.4f,1), Tide(.1f,.95f,1);
FLinearColor SliceInk(FLinearColor Color)
{
    // The pale stone needs saturated inks rather than emissive pastel strokes.
    if(Color==Heal)return FLinearColor(.008f,.24f,.045f);
    if(Color==Stun)return FLinearColor(.22f,.025f,.40f);
    if(Color==Shield)return FLinearColor(.015f,.15f,.42f);
    if(Color==Hurt)return FLinearColor(.42f,.035f,.015f);
    if(Color==Vine)return FLinearColor(.42f,.012f,.16f);
    if(Color==Prism)return FLinearColor(.22f,.035f,.42f);
    if(Color==Tide)return FLinearColor(.006f,.30f,.35f);
    if(Color==Strike)return FLinearColor(.48f,.22f,.018f);
    if(Color==Shot)return FLinearColor(.58f,.38f,.08f);
    return Color;
}
FLinearColor SkillColor(wc::AbilityMechanic Mechanic)
{
    switch(Mechanic){
    case wc::AbilityMechanic::DirectionalGuard:return Strike;
    case wc::AbilityMechanic::MomentumCharge:return Strike;
    case wc::AbilityMechanic::StationaryGrove:return Heal;
    case wc::AbilityMechanic::ScreenedStrike:return Vine;
    case wc::AbilityMechanic::CrossingBeams:return Prism;
    case wc::AbilityMechanic::TidalPush:return Tide;
    default:return Shot;
    }
}
}

void AWCVNextLab::SilkLine(FVector A,FVector B,float Width)
{
    if(SilkStrandTransforms.Num()>=8192){CueOverflow=true;return;}
    const FVector D=B-A;if(D.SizeSquared()<.01f)return;
    SilkStrandTransforms.Emplace(D.Rotation(),(A+B)*.5,FVector(D.Size(),Width,Width)/100);
}
void AWCVNextLab::SilkSpark(FVector P,float Radius)
{
    if(SilkSparkTransforms.Num()>=512){CueOverflow=true;return;}
    SilkSparkTransforms.Emplace(FQuat::Identity,P,FVector(Radius/50));
}
void AWCVNextLab::FlushSilkEffects()
{
    const auto Flush=[&](TObjectPtr<UInstancedStaticMeshComponent>& Component,const TCHAR* Shape,
        const TArray<FTransform>& Transforms,FLinearColor Color){
        if(!Component&&Transforms.IsEmpty())return;
        if(!Component){
            Component=NewObject<UInstancedStaticMeshComponent>(this);AddInstanceComponent(Component);
            auto* EffectMesh=LoadObject<UStaticMesh>(nullptr,*(FString(TEXT("/Game/WonderChess/VNext/Characters/Silkmother_r003/Effects/SM_Silk_"))+Shape));
            Component->SetStaticMesh(EffectMesh);Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Component->SetCastShadow(false);Component->SetCanEverAffectNavigation(false);
            auto* SilkMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WonderChess/VNext/Characters/Silkmother_r003/Effects/M_SilkEffects"));
            auto* Material=UMaterialInstanceDynamic::Create(SilkMaterial?SilkMaterial:CombatCueMaterial.Get(),this);
            Material->SetVectorParameterValue(TEXT("Color"),Color);Component->SetMaterial(0,Material);
            Component->RegisterComponent();
        }
        // A bounded instanced batch keeps dense silk separate from the general cue component pool.
        Component->ClearInstances();if(!Transforms.IsEmpty())Component->AddInstances(Transforms,false,true,false);
    };
    Flush(SilkStrands,TEXT("Cube"),SilkStrandTransforms,FLinearColor(.86f,.73f,.48f));
    Flush(SilkSparks,TEXT("Sphere"),SilkSparkTransforms,FLinearColor(1.f,.64f,.19f));
    if(SilkStrands&&SilkStrandTransforms.Num()>=384&&!CueKindsSeen.Contains(TEXT("silk_instance_batch_verified"))){
        CueKindsSeen.Add(TEXT("silk_instance_batch_verified"));
        UE_LOG(LogTemp,Display,TEXT("WC_SILK_BATCH instances=%d mesh=%s material=%s visible=%d registered=%d owner_hidden=%d bounds=%s"),
            SilkStrands->GetInstanceCount(),*GetNameSafe(SilkStrands->GetStaticMesh()),*GetPathNameSafe(SilkStrands->GetMaterial(0)),
            SilkStrands->IsVisible(),SilkStrands->IsRegistered(),IsHidden(),*SilkStrands->Bounds.ToString());
    }
}

void AWCVNextLab::CueMesh(const TCHAR* Shape,FVector Location,FVector Scale,FLinearColor Color,FRotator Rotation)
{
    if(ArtSlice)Color=SliceInk(Color);
    // Reused components are cosmetic. Neither their transforms nor visibility feed combat.
    if(CueMeshUsed>=1024){CueOverflow=true;return;}
    if(!CueActor.IsValid())CueActor=SceneActor();
    if(CueMeshUsed==CueMeshes.Num()){
        auto* Component=Mesh(CueActor.Get(),Shape,Location,Scale,Color,Rotation);
        Component->SetCastShadow(false);CueMeshes.Add(Component);
    }
    auto* Component=CueMeshes[CueMeshUsed++];
    Component->SetStaticMesh(ProxyMeshes.FindChecked(Shape));
    Component->SetWorldLocationAndRotation(Location,Rotation);
    const uint32 Key=Color.ToFColor(false).ToPackedRGBA();
    if(!CueMaterials.Contains(Key)){
        auto* Instance=UMaterialInstanceDynamic::Create(CombatCueMaterial,this);
        Instance->SetVectorParameterValue(TEXT("Color"),Color);CueMaterials.Add(Key,Instance);
    }
    Component->SetWorldScale3D(Scale);Component->SetMaterial(0,CueMaterials.FindChecked(Key));Component->SetVisibility(true);
}

void AWCVNextLab::CueLine(FVector A,FVector B,FLinearColor Color,float Width)
{
    if(ArtSlice&&Camera&&Controller){
        Width=FMath::Max(Width,WorldUnitsPerPixel((A+B)*.5)*1.6f);
    }
    const FVector Delta=B-A;
    if(Delta.SizeSquared()<.01)return;
    CueMesh(TEXT("Cube"),(A+B)*.5,FVector(Delta.Size()/100,Width/100,Width/100),Color,Delta.Rotation());
}

void AWCVNextLab::CueRing(FVector Center,float Radius,FLinearColor Color,float Width,float Arc,float Rotation)
{
    constexpr int Segments=16;
    for(int I=0;I<Segments;++I){
        const float A=Rotation+Arc*I/Segments,B=Rotation+Arc*(I+1)/Segments;
        CueLine(Center+FVector(FMath::Cos(A)*Radius,FMath::Sin(A)*Radius,0),
                Center+FVector(FMath::Cos(B)*Radius,FMath::Sin(B)*Radius,0),Color,Width);
    }
}

void AWCVNextLab::CueStar(FVector Center,float Radius,FLinearColor Color,float Width,float Rotation)
{
    // A five-point vector outline; pooled segments stay legible without an opaque sprite quad.
    for(int I=0;I<10;++I){
        const float A=Rotation+I*UE_TWO_PI/10,B=Rotation+(I+1)*UE_TWO_PI/10;
        const float R=I%2?Radius*.43f:Radius,S=(I+1)%2?Radius*.43f:Radius;
        CueLine(Center+FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,0),
            Center+FVector(FMath::Cos(B)*S,FMath::Sin(B)*S,0),Color,Width);
    }
}

int AWCVNextLab::PlacementState(wc::Cell Cell) const
{
    // 0: no destination; 1: inspection; 2: accepted placement; 3: rejected placement.
    if(!LoadError.IsEmpty()||Cell.column<0||Cell.column>=Catalog.rules.columns||Cell.row<0||Cell.row>=Catalog.rules.rows)return 0;
    if(const auto* Combat=CurrentCombat()){
        for(const auto& Unit:Combat->Units())if(Unit.cell==Cell)return 1;
        return 3;
    }
    if(SoloMode){
        if(!SoloMatch)return 0;
        if(ViewedSeat!=0)return 1;
        if(AwaitingSaveDecision||SoloMatch->CurrentPhase()!=wc::Phase::Preparation||Cell.row>=Catalog.rules.deploymentRows)return 3;
        const auto& PlayerSeat=SoloMatch->Seats()[0];
        if(PlayerSeat.health<=0)return 3;
        const auto At=std::find_if(PlayerSeat.roster.begin(),PlayerSeat.roster.end(),[&](const auto& Unit){return Unit.onBoard&&Unit.cell==Cell;});
        const auto Chosen=std::find_if(PlayerSeat.roster.begin(),PlayerSeat.roster.end(),[&](const auto& Unit){return Unit.id==Selected;});
        if(Chosen!=PlayerSeat.roster.end()&&(At==PlayerSeat.roster.end()||At->id!=Selected)){
            wc::Command Move;Move.type=wc::CommandType::Move;Move.unit=Selected;Move.toBoard=true;Move.cell=Cell;
            return wc::PreviewRosterCommand(Catalog,PlayerSeat,Move).accepted?2:3;
        }
        return At!=PlayerSeat.roster.end()?1:3;
    }
    const int Side=Cell.row<Catalog.rules.deploymentRows?0:1;
    for(const auto& Unit:Formation[Side])if(wc::EncounterCell(Unit.cell,Side,Catalog.rules)==Cell)return 1;
    for(int Team=0;Team<2;++Team)for(const auto& Unit:Formation[Team])if(Unit.id==Selected)return Team==Side?2:3;
    return Formation[Side].size()<10?2:3;
}

void AWCVNextLab::UpdatePlacementCue()
{
    PlacementPreviewState=0;PlacementPreviewCell={-1,-1};
    if(!ArtSlice||!Controller||!BoardInput||!BoardInput->IsEnabled())return;
    if(CurrentCombat()||(SoloMode&&SoloMatch&&SoloMatch->CurrentPhase()!=wc::Phase::Preparation))return;
    wc::Cell Cell{-1,-1};
    if(BoardInput->IsHovered()){
        FVector Origin,Direction;
        if(Controller->DeprojectMousePositionToWorld(Origin,Direction)&&FMath::Abs(Direction.Z)>.0001f){
            const double T=-Origin.Z/Direction.Z;
            if(T>=0){const FVector P=Origin+Direction*T;Cell={FMath::FloorToInt32((P.X+800)/200),FMath::FloorToInt32((800-P.Y)/200)};}
        }
    }else if(SoloMode&&BoardInput->HasKeyboardFocus())Cell={KeyboardColumn,KeyboardRow};
    PlacementPreviewState=PlacementState(Cell);PlacementPreviewCell=Cell;
    if(!PlacementPreviewState)return;
    const FVector Center=Position(Cell)+FVector(0,0,17);
    const FLinearColor Color=PlacementPreviewState==2?FLinearColor(.008f,.24f,.045f):PlacementPreviewState==3?FLinearColor(.42f,.025f,.015f):FLinearColor(.38f,.24f,.055f);
    // Only the pointed destination is evaluated. Existing units show a neutral inspection diamond.
    if(PlacementPreviewState==1){
        const FVector P=Center+FVector(66,-66,0);
        CueLine(P+FVector(0,12,0),P+FVector(12,0,0),Color,3);CueLine(P+FVector(12,0,0),P-FVector(0,12,0),Color,3);
        CueLine(P-FVector(0,12,0),P-FVector(12,0,0),Color,3);CueLine(P-FVector(12,0,0),P+FVector(0,12,0),Color,3);
        return;
    }
    const FVector Corners[]={Center+FVector(-91,-91,0),Center+FVector(91,-91,0),Center+FVector(91,91,0),Center+FVector(-91,91,0)};
    for(int I=0;I<4;++I)CueLine(Corners[I],Corners[(I+1)%4],Color,4);
    const FVector P=Center+FVector(55,-50,0);
    if(PlacementPreviewState==2){
        CueLine(P+FVector(-18,0,0),P+FVector(-5,-12,0),Color,6);CueLine(P+FVector(-5,-12,0),P+FVector(22,22,0),Color,6);
    }else{
        CueLine(P-FVector(16,16,0),P+FVector(16,16,0),Color,6);CueLine(P+FVector(-16,16,0),P+FVector(16,-16,0),Color,6);
        for(int I=-1;I<=1;++I)CueLine(Center+FVector(-75+I*23,65,0),Center+FVector(-57+I*23,83,0),Color,3);
    }
}

void AWCVNextLab::CueText(FVector Location,const FString& Text,FLinearColor Color,float Size)
{
    if(ArtSlice)Color=SliceInk(Color);
    if(CueTextUsed>=64){CueOverflow=true;return;}
    if(!CueActor.IsValid())CueActor=SceneActor();
    if(CueTextUsed==CueTexts.Num()){
        auto* Component=NewObject<UTextRenderComponent>(CueActor.Get());
        CueActor->AddInstanceComponent(Component);Component->SetupAttachment(CueActor->GetRootComponent());
        Component->SetHorizontalAlignment(EHTA_Center);Component->SetVerticalAlignment(EVRTA_TextCenter);
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);Component->RegisterComponent();CueTexts.Add(Component);
    }
    auto* Component=CueTexts[CueTextUsed++];
    Component->SetWorldLocation(Location);Component->SetWorldSize(Size);
    Component->SetText(FText::FromString(Text));Component->SetTextRenderColor(Color.ToFColor(false));
    if(Camera)Component->SetWorldRotation((-Camera->GetActorForwardVector()).Rotation());
    Component->SetVisibility(true);
}

void AWCVNextLab::RecordRosterUpgrades(const std::vector<wc::OwnedUnit>& Before)
{
    if(!Storybook||!SoloMatch||ViewedSeat!=0||SoloMatch->CurrentPhase()!=wc::Phase::Preparation)return;
    for(const auto& Unit:SoloMatch->Seats()[0].roster){
        const auto Previous=std::find_if(Before.begin(),Before.end(),[&](const auto& Old){return Old.id==Unit.id;});
        if(Previous!=Before.end()&&Previous->definition==Unit.definition&&Unit.star>Previous->star){
            UpgradeStarted.Add(Unit.id,Elapsed);
            CueKindsSeen.Add(TEXT("completed_roster_upgrade"));
            UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_UPGRADE owned=%llu from=%d to=%d"),Unit.id,Previous->star,Unit.star);
        }
    }
}

void AWCVNextLab::ClearUpgradePresentation()
{
    UpgradeStarted.Reset();
}

float AWCVNextLab::UpgradePulse(uint64 Id) const
{
    if(!Storybook||!SoloMatch||ViewedSeat!=0||SoloMatch->CurrentPhase()!=wc::Phase::Preparation)return 0;
    const auto* Started=UpgradeStarted.Find(Id);
    const double Time=SoloVisualExercise&&CapturePhase!=ECapturePhase::None?CaptureQueuedAt:Elapsed;
    return Started?FMath::Clamp(float(1-(Time-*Started)/1.1),0.f,1.f):0;
}

float AWCVNextLab::DefeatAge(const wc::CombatUnit& Unit) const
{
    const auto* Combat=CurrentCombat();
    if(!Combat||Unit.health>0)return -1;
    for(auto It=Combat->Events().rbegin();It!=Combat->Events().rend();++It){
        if(It->target==Unit.id&&It->effect==wc::Effect::Damage&&It->healthLoss>0)
            return FMath::Max(0.f,(Combat->CurrentTick()-It->tick)*Catalog.rules.tickMs/1000.f+
                (Combat->Result().complete&&Combat==DefeatClockCombat?float(Elapsed-DefeatClockHeldAt):0.f));
    }
    return 1;
}

void AWCVNextLab::UpdateCombatCues()
{
    CueMeshUsed=CueTextUsed=0;CurrentCueKinds.Reset();
    FxLive=Courtyard&&!SoloVisualExercise&&!SoloExercise&&!Exercise;
    SilkStrandTransforms.Reset();SilkSparkTransforms.Reset();
    const auto* Combat=CurrentCombat();
    if(Combat){
        const double Time=Combat->CurrentTick()*Catalog.rules.tickMs/1000.;
        const auto Find=[&](wc::Id Id)->const wc::CombatUnit*{
            for(const auto& U:Combat->Units())if(U.id==Id)return &U;return nullptr;
        };
        const auto At=[&](wc::Id Id,wc::Cell Fallback,float Z=75.f){
            if(const auto* View=Pieces.Find(Id);View&&View->Actor.IsValid()){
                FVector P=View->Actor->GetActorLocation();P.Z=Z;return P;
            }
            return Position(Fallback)+FVector(0,0,Z);
        };
        const auto Mark=[&](const TCHAR* Kind){CueKindsSeen.Add(Kind);CurrentCueKinds.Add(Kind);};
        const auto Poisoned=Combat->PeriodicTargets();
        const FLinearColor TypeTone[]={FLinearColor(.95f,.60f,.22f),FLinearColor(.36f,.58f,1.f),FLinearColor(.96f,.96f,.92f)};
        for(const auto& U:Combat->Units()){
            if(U.health<=0){
                const float Age=DefeatAge(U);
                if(Storybook&&Age>=0&&Age<.72f){
                    const FVector P=At(U.id,U.cell,35);
                    const float Phase=Age/.72f;
                    const FLinearColor Ash(.22f,.21f,.14f);
                    // Detached leaf shapes make defeat distinct from a healing blossom or tier star.
                    for(int I=0;I<5;++I){
                        const float Angle=I*UE_TWO_PI/5+float(U.id%7);
                        const FVector D(FMath::Cos(Angle),FMath::Sin(Angle),0);
                        const FVector Cross(-D.Y,D.X,0);
                        const FVector Center=P+D*(18+Phase*48)+FVector(0,0,Phase*90);
                        const float Size=9*(1-Phase);
                        CueLine(Center-D*Size,Center+Cross*Size*.45f,Ash,2);
                        CueLine(Center+Cross*Size*.45f,Center+D*Size,Ash,2);
                        CueLine(Center+D*Size,Center-Cross*Size*.45f,Ash,2);
                        CueLine(Center-Cross*Size*.45f,Center-D*Size,Ash,2);
                    }
                    Mark(TEXT("storybook_defeat_leaves"));
                }
                continue;
            }
            const FVector P=At(U.id,U.cell);
            if(U.id==Selected){
                CueRing(P-FVector(0,0,56),87,Shot,3);
                if(U.target>=0&&U.target<int(Combat->Units().size())){
                    const auto& Target=Combat->Units()[U.target];
                    if(Target.health>0){
                        const FVector T=At(Target.id,Target.cell,30);
                        CueLine(P-FVector(0,0,45),T,Shot,2);CueRing(T,70,Shot,3);
                        Mark(TEXT("selected_target"));
                    }
                }
            }
            if(U.cocoonExpiry>Combat->CurrentTick()){
                FVector Center=P+FVector(0,0,30),Extent(72,72,105);
                if(const auto* View=Pieces.Find(U.id)){
                    auto* Mesh=View->Bellback?View->Bellback->GetMesh():View->Silkmother?View->Silkmother->GetMesh():nullptr;
                    if(Mesh){Center=Mesh->Bounds.Origin;Extent=Mesh->Bounds.BoxExtent;}
                }
                Extent.X+=9;Extent.Y+=9;Extent.Z+=7;
                // Crossed twelve-turn silk bands enclose the target; the health/name markers remain unobstructed.
                for(int Hand:{-1,1})for(int I=0;I<192;++I){
                    const auto Point=[&](float T){
                        const float A=Hand*T*UE_TWO_PI*12+float(U.id%11),Z=(T*2-1)*.96f;
                        const float R=FMath::Sqrt(FMath::Max(.02f,1-Z*Z));
                        return Center+FVector(FMath::Cos(A)*Extent.X*R,FMath::Sin(A)*Extent.Y*R,Z*Extent.Z);
                    };
                    SilkLine(Point(I/192.f),Point((I+1)/192.f),5.5f);
                }
                for(int I=0;I<10;++I){
                    const float A=Time*2+I*UE_TWO_PI/10;
                    SilkSpark(Center+FVector(FMath::Cos(A)*(Extent.X+10),FMath::Sin(A)*(Extent.Y+10),FMath::Sin(A*2)*Extent.Z*.7f),2.4f);
                }
                Mark(TEXT("silkmother_dense_cocoon"));
            }else if(U.state==wc::ActionState::Stunned){
                // A continuous spiral and orbiting stars exist only while the actual stun is active.
                const FVector Center=P+FVector(0,0,ArtSlice?242:245);
                const int SpiralSegments=ArtSlice?18:24;
                for(int I=0;I<SpiralSegments;++I){
                    const float A=I*.38f+Time*3,B=(I+1)*.38f+Time*3;
                    const float R=ArtSlice?8+I*1.45f:12+I*1.7f,S=ArtSlice?8+(I+1)*1.45f:12+(I+1)*1.7f;
                    CueLine(Center+FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,I*.5f),
                            Center+FVector(FMath::Cos(B)*S,FMath::Sin(B)*S,(I+1)*.5f),Stun,ArtSlice?3.5f:5);
                }
                for(int I=0;I<3;++I){
                    const float A=Time*3+I*UE_TWO_PI/3;
                    const FVector Star=Center+FVector(FMath::Cos(A)*(ArtSlice?44:58),FMath::Sin(A)*(ArtSlice?44:58),15);
                    if(ArtSlice)CueStar(Star,11,Stun,3,A*.3f);
                    else{
                        CueLine(Star-FVector(9,0,0),Star+FVector(9,0,0),Stun,5);
                        CueLine(Star-FVector(0,9,0),Star+FVector(0,9,0),Stun,5);
                    }
                }
                Mark(TEXT("stun_swirl"));
                if(ArtSlice)Mark(TEXT("art_slice_stun_stars"));
            }
            {
                // Statuses. Hexed: a turning violet ring and a star overhead. Silenced: a blue cross beside the unit.
                // Taunted: a red ring and a line to the unit it must attack. Under damage over time: three falling drops.
                const int Now=Combat->CurrentTick();
                const FLinearColor Violet(.62f,.35f,.95f),Crimson(.95f,.22f,.18f),Mute(.45f,.62f,.95f),Venom(.45f,.85f,.30f);
                if(U.statuses[int(wc::UnitStatus::Hex)].expiry>Now){
                    CueRing(P-FVector(0,0,50),70,Violet,4,UE_TWO_PI,float(Time)*2);
                    CueStar(P+FVector(0,0,165),16,Violet,3,float(Time));
                    Mark(TEXT("status_hex"));
                }
                if(U.statuses[int(wc::UnitStatus::Silence)].expiry>Now){
                    const FVector C=P+FVector(-65,0,70);
                    CueLine(C+FVector(-12,0,-12),C+FVector(12,0,12),Mute,5);CueLine(C+FVector(-12,0,12),C+FVector(12,0,-12),Mute,5);
                    Mark(TEXT("status_silence"));
                }
                const auto& Taunt=U.statuses[int(wc::UnitStatus::Taunt)];
                if(Taunt.expiry>Now&&Taunt.source>=0&&Taunt.source<int(Combat->Units().size())&&Combat->Units()[Taunt.source].health>0){
                    const auto& By=Combat->Units()[Taunt.source];
                    CueLine(P-FVector(0,0,30),At(By.id,By.cell,45),Crimson,3);
                    CueRing(P-FVector(0,0,52),64,Crimson,3);
                    Mark(TEXT("status_taunt"));
                }
                if(Poisoned.end()!=std::find(Poisoned.begin(),Poisoned.end(),int(&U-Combat->Units().data()))){
                    for(int Drop=0;Drop<3;++Drop){
                        const float Fall=FMath::Fmod(float(Time)*1.4f+Drop*.33f,1.f);
                        const FVector C=P+FVector(-45+Drop*18,0,95-Fall*45);
                        CueLine(C,C-FVector(0,0,9),Venom,4);
                    }
                    Mark(TEXT("damage_over_time"));
                }
            }
            if(U.shield>0){
                CueRing(P,78,Shield,5);CueRing(P+FVector(0,0,45),63,Shield,4);
                Mark(TEXT("active_shield"));
            }
            int ModifierIndex=0;
            for(const auto& Modifier:U.modifiers){
                // One arrow per modifier, stacked upward: green up for a buff, red down for a debuff.
                const float Sign=Modifier.magnitude>0?1.f:-1.f;
                const FVector C=P+FVector(65,0,55+30*ModifierIndex++);
                CueLine(C+FVector(-12,0,-12*Sign),C+FVector(0,0,12*Sign),Sign>0?Heal:Stun,6);
                CueLine(C+FVector(12,0,-12*Sign),C+FVector(0,0,12*Sign),Sign>0?Heal:Stun,6);
                Mark(TEXT("stat_modifier"));
            }
        }
        {
            // Ground zones and auras: the outline of the affected ground, for as long as hits are still due.
            const FVector Ax=Position({1,0})-Position({0,0}),Ay=Position({0,1})-Position({0,0});
            for(const auto& Zone:Combat->Zones()){
                const float Reach=Zone.radius+.5f,Pulse=.75f+.25f*FMath::Sin(float(Time)*5);
                const FVector C=Position(Zone.center)+FVector(0,0,6);
                const FLinearColor Tone=TypeTone[FMath::Clamp(int(Zone.damageType),0,2)]*Pulse;
                const FVector Corner[]={C-Ax*Reach-Ay*Reach,C+Ax*Reach-Ay*Reach,C+Ax*Reach+Ay*Reach,C-Ax*Reach+Ay*Reach};
                for(int I=0;I<4;++I)CueLine(Corner[I],Corner[(I+1)%4],Tone,5);
                Mark(TEXT("ground_zone"));
            }
        }
        for(const auto& Action:Combat->VisualActions()){
            FVector From=Position(Action.origin)+FVector(0,0,75);
            const FVector To=At(Action.target,Action.center);
            const auto& Def=Catalog.Definition(Action.definition,Action.neutral);
            // A modelled hero's shots leave its staff tip, crystal or hand rather than the middle of its tile.
            if(Def.projectileTravelMs>0)if(const auto* Shooter=Pieces.Find(Action.source);Shooter&&Shooter->Hero)From=Shooter->Hero->MuzzleLocation(int(Action.action));
            if(Def.id=="wc_vn_soul_jailer"&&!(FxLive&&Action.basicAttack&&ShotLook(Def.id,true))){
                if(const auto* View=Pieces.Find(Action.source);View&&View->Silkmother)From=View->Silkmother->CueLocation(TEXT("mouth"));
                const float Span=FMath::Max(1,Action.impactTick-Action.releaseTick);
                const float T=FMath::Clamp((Combat->CurrentTick()-Action.releaseTick)/Span,0.f,1.f);
                if(Action.released){
                    const FVector Tip=FMath::Lerp(From,To,T),D=(To-From).GetSafeNormal();
                    const FVector Across=FVector::CrossProduct(D,FVector::UpVector).GetSafeNormal();
                    const float Size=Action.basicAttack?4.f:11.f;
                    for(int I=0;I<(Action.basicAttack?2:6);++I){
                        const float Angle=I*UE_TWO_PI/6;
                        const FVector Offset=(Across*FMath::Cos(Angle)+FVector::UpVector*FMath::Sin(Angle))*Size;
                        SilkLine(FMath::Lerp(From,To,FMath::Max(0.f,T-.13f))+Offset,Tip,Action.basicAttack?2.2f:3.5f);
                    }
                    SilkSpark(Tip,Action.basicAttack?3:8);
                    Mark(Action.basicAttack?TEXT("silkmother_silk_shot"):TEXT("silkmother_web_projectile"));
                }else if(!Action.basicAttack){
                    const auto* Source=Find(Action.source);
                    const float CastMs=Source?FMath::Max(1,Source->ability.castMs):FMath::Max(1,Def.ability.castMs);
                    const float Age=FMath::Clamp(1-(Action.releaseTick-Combat->CurrentTick())*Catalog.rules.tickMs/CastMs,0.f,1.f);
                    for(int I=0;I<6;++I){const float A=Time*8+I*UE_TWO_PI/6;
                        SilkSpark(From+FVector(FMath::Cos(A),FMath::Sin(A),.3f)*18*(1-Age),2+Age*2);}
                    Mark(TEXT("silkmother_weave_windup"));
                }
                continue;
            }
            const FLinearColor Color=Action.basicAttack?(Def.ability.mechanic==wc::AbilityMechanic::Standard?Shot:SkillColor(Def.ability.mechanic)):SkillColor(Action.mechanic);
            const float Until=(Action.releaseTick-Combat->CurrentTick())*Catalog.rules.tickMs/1000.f;
            if(Action.basicAttack){
                if(Action.released){
                    // A hero with a modelled shot draws it in DrawFeedback; the plain line cue would double it.
                    if(FxLive&&ShotLook(Def.id,true)){Mark(TEXT("ranged_projectile"));continue;}
                    const float Span=FMath::Max(1,Action.impactTick-Action.releaseTick);
                    const float T=FMath::Clamp((Combat->CurrentTick()-Action.releaseTick)/Span,0.f,1.f);
                    const FVector Tip=FMath::Lerp(From,To,T);
                    if(ArtSlice){
                        const FVector D=(To-From).GetSafeNormal(),Across=FVector(-D.Y,D.X,0).GetSafeNormal();
                        for(int I=0;I<3;++I){
                            const FVector A=FMath::Lerp(From,To,FMath::Max(0.f,T-.16f+I*.04f));
                            const FVector B=FMath::Lerp(From,To,FMath::Max(0.f,T-.12f+I*.04f));
                            CueLine(A,B,Color,2+I*2);
                        }
                        const FVector Nose=Tip+D*16,Back=Tip-D*14,Left=Tip+Across*8,Right=Tip-Across*8;
                        if(Storybook&&Def.ability.mechanic==wc::AbilityMechanic::StationaryGrove){
                            CueMesh(TEXT("Sphere"),Tip,FVector(.10f,.18f,.10f),Heal,D.Rotation());
                            CueLine(Tip-D*9,Tip-D*17+Across*10,Heal,3);
                            CueLine(Tip-D*9,Tip-D*17-Across*10,Heal,3);
                            Mark(TEXT("root_seed_projectile"));
                        }else if(Storybook&&Def.ability.mechanic==wc::AbilityMechanic::TidalPush){
                            const FVector Center=Tip-D*8;
                            for(int I=0;I<6;++I){
                                const float A=-1.15f+I*2.3f/6,B=-1.15f+(I+1)*2.3f/6;
                                CueLine(Center+D*FMath::Cos(A)*18+Across*FMath::Sin(A)*18,
                                    Center+D*FMath::Cos(B)*18+Across*FMath::Sin(B)*18,Tide,4);
                            }
                            Mark(TEXT("reefglass_crescent_projectile"));
                        }else{
                            CueLine(Nose,Left,Color,3);CueLine(Left,Back,Color,3);CueLine(Back,Right,Color,3);CueLine(Right,Nose,Color,3);
                            CueLine(Tip-D*6,Tip+D*7,Shot,4);
                            if(Storybook&&Def.ability.mechanic==wc::AbilityMechanic::ScreenedStrike){
                                CueLine(Back,Back-D*10+Across*11,Vine,3);
                                CueLine(Back,Back-D*10-Across*11,Vine,3);
                                Mark(TEXT("snapvine_barbed_projectile"));
                            }else if(Storybook&&Def.ability.mechanic==wc::AbilityMechanic::CrossingBeams){
                                CueLine(Left-FVector(0,0,9),Tip+FVector(0,0,9),Prism,3);
                                CueLine(Tip+FVector(0,0,9),Right-FVector(0,0,9),Prism,3);
                                Mark(TEXT("prism_glass_projectile"));
                            }
                            Mark(TEXT("art_slice_kite_projectile"));
                        }
                    }else{
                        CueLine(FMath::Lerp(From,To,FMath::Max(0.f,T-.22f)),Tip,Color,8);
                        CueMesh(Def.ability.mechanic==wc::AbilityMechanic::CrossingBeams?TEXT("Cube"):Def.ability.mechanic==wc::AbilityMechanic::ScreenedStrike?TEXT("Cone"):TEXT("Sphere"),Tip,FVector(.18),Color,(To-From).Rotation());
                    }
                    if(Courtyard&&!SoloVisualExercise&&!Exercise&&!ShotLook(Def.id,true)){
                        // A bright core that sheds a fading trail makes the shot read at board distance.
                        const bool Sprout=Def.ability.mechanic==wc::AbilityMechanic::StationaryGrove,Wet=Def.ability.mechanic==wc::AbilityMechanic::TidalPush;
                        const FLinearColor Core=Sprout?FLinearColor(.6f,2.4f,.5f):Wet?FLinearColor(.4f,1.1f,2.6f):FLinearColor(1.5f,2.3f,3.f);
                        FxEmit(0,Tip,FVector::ZeroVector,Core,54,54,0);
                        FxEmit(0,Tip,FVector::ZeroVector,FLinearColor(3.f,3.f,3.f),20,20,0);
                        if(!(SoloMode?SoloPaused:Paused)){
                            FxEmit(0,Tip,FVector(FMath::FRandRange(-25.f,25.f),FMath::FRandRange(-25.f,25.f),FMath::FRandRange(-10.f,30.f)),Core,26,4,.32f);
                            if(Wet)FxEmit(1,Tip,FVector(0,0,-30),FLinearColor(.75f,.88f,1.f,.5f),24,60,.35f);
                            if(Sprout&&FMath::FRand()<.5f)FxEmit(3,Tip,FVector(FMath::FRandRange(-60.f,60.f),FMath::FRandRange(-60.f,60.f),40),Core,7,2,.4f,200,1,0,3);
                        }
                    }
                    Mark(TEXT("ranged_projectile"));
                }else if(Def.projectileTravelMs>0){
                    CueRing(From,22+14*FMath::Clamp(1-Until/.15f,0.f,1.f),Shot,4);
                    Mark(TEXT("ranged_windup"));
                }else{
                    const FVector Direction=(To-From).GetSafeNormal2D();
                    if(!FxLive)CueRing(From+Direction*45,55,Strike,7,1.8f,FMath::Atan2(Direction.Y,Direction.X)-.9f);
                    Mark(TEXT("melee_windup"));
                }
                continue;
            }
            Mark(TEXT("skill_telegraph"));
            if(Action.mechanic==wc::AbilityMechanic::StationaryGrove){
                const int Left=FMath::Max(0,Action.center.column-Action.radius),Right=FMath::Min(Catalog.rules.columns-1,Action.center.column+Action.radius);
                const int Top=FMath::Max(0,Action.center.row-Action.radius),Bottom=FMath::Min(Catalog.rules.rows-1,Action.center.row+Action.radius);
                const FVector Corners[]={Position({Left,Top})+FVector(-95,95,22),Position({Right,Top})+FVector(95,95,22),
                    Position({Right,Bottom})+FVector(95,-95,22),Position({Left,Bottom})+FVector(-95,-95,22)};
                if(!FxLive){for(int I=0;I<4;++I)CueLine(Corners[I],Corners[(I+1)%4],Heal,5);
                CueRing(Position(Action.center)+FVector(0,0,24),45+FMath::Fmod(Time*110,130.),Heal,4);}
                else for(int I=0;I<4;++I){
                    // The grove's edge is a soft band of green light instead of a drawn box.
                    const FVector A=Corners[I],B=Corners[(I+1)%4];
                    FxEmit(3,(A+B)*.5,(B-A).GetSafeNormal()*.01,FLinearColor(.25f,1.3f,.3f)*(.55f+.15f*FMath::Sin(float(Time)*3+I)),16,0,0,0,0,0,float(FVector::Dist(A,B))/16);
                }
                Mark(TEXT("root_grove"));
            }else if(Action.mechanic==wc::AbilityMechanic::CrossingBeams){
                for(const auto& Cell:Action.cells){
                    const FVector P=Position(Cell)+FVector(0,0,30);
                    const bool AlongRow=Action.cells.front().row==Action.cells.back().row;
                    const FVector Axis=AlongRow?FVector(1,0,0):FVector(0,1,0);
                    if(!FxLive)CueLine(P-Axis*60,P+Axis*60,Prism,Action.released?7:4);
                    else FxEmit(3,P,Axis*.01,FLinearColor(.8f,1.5f,2.2f)*(Action.released?1.4f:.45f+.2f*FMath::Sin(float(Time)*18)),Action.released?34:18,0,0,0,0,0,Action.released?6.5f:12);
                }
                Mark(TEXT("prism_cross"));
            }else{
                const FVector Aim=Position({FMath::Clamp(Action.center.column,0,Catalog.rules.columns-1),
                    FMath::Clamp(Action.center.row,0,Catalog.rules.rows-1)})+FVector(0,0,32);
                const FVector Start=From-FVector(0,0,43);
                const FVector D=(Aim-Start).GetSafeNormal();
                for(float T=0;T<1;T+=.12f)CueLine(FMath::Lerp(Start,Aim,T),FMath::Lerp(Start,Aim,FMath::Min(T+.07f,1.f)),Color,5);
                CueLine(Aim-D*35+FVector(-D.Y,D.X,0)*20,Aim,Color,6);
                CueLine(Aim-D*35-FVector(-D.Y,D.X,0)*20,Aim,Color,6);
                if(Action.mechanic==wc::AbilityMechanic::ScreenedStrike)Mark(TEXT("snapvine_aim"));
                if(Action.mechanic==wc::AbilityMechanic::TidalPush)Mark(TEXT("reefglass_lane"));
                if(Action.mechanic==wc::AbilityMechanic::MomentumCharge)Mark(TEXT("cragstoat_charge_aim"));
            }
        }
        // Read a bounded recent interval directly: pause, replay and observer changes need no event playback queue.
        const auto& Events=Combat->Events();
        for(auto It=Events.rbegin();It!=Events.rend();++It){
            const float Age=(Combat->CurrentTick()-It->tick)*Catalog.rules.tickMs/1000.f;
            if(Age>10.7f)break;
            if(It->mechanic!=wc::AbilityMechanic::CocoonProjectile||It->effect!=wc::Effect::Stun||It->resolved<=0)continue;
            const float ReleaseAge=Age-It->resolved/1000.f;
            const auto* Target=Find(It->target);
            if(ReleaseAge<0||ReleaseAge>.35f||!Target||Target->health<=0||Target->cocoonExpiry>Combat->CurrentTick())continue;
            const FVector Center=At(Target->id,Target->cell);const float Life=1-ReleaseAge/.35f;
            for(int I=0;I<12;++I){
                const float A=I*UE_TWO_PI/12;
                const FVector D(FMath::Cos(A),FMath::Sin(A),.35f);
                SilkLine(Center+D*(65+ReleaseAge*50),Center+D*(78+ReleaseAge*90),2.5f*Life);
                SilkSpark(Center+D*(78+ReleaseAge*90),3*Life);
            }
            Mark(TEXT("silkmother_cocoon_release"));
        }
        for(auto It=Events.rbegin();It!=Events.rend();++It){
            const auto& E=*It;
            const float Age=(Combat->CurrentTick()-E.tick)*Catalog.rules.tickMs/1000.f;
            if(Age>.7f)break;
            const auto* Recipient=Find(E.target);
            const FVector From=Position(E.origin)+FVector(0,0,75),To=At(E.target,E.cell);
            const float Life=FMath::Max(.05f,1-Age/.7f);
            if(E.mechanic==wc::AbilityMechanic::CocoonProjectile&&E.effect==wc::Effect::Stun&&E.resolved>0&&Recipient&&Recipient->health>0){
                for(int I=0;I<14;++I){
                    const float A=I*UE_TWO_PI/14;const FVector D(FMath::Cos(A),FMath::Sin(A),FMath::Sin(A*3)*.5f);
                    SilkLine(To+D*(10+Age*75),To+D*(23+Age*110),3*Life);
                    SilkSpark(To+D*(23+Age*110),4*Life);
                }
                Mark(TEXT("silkmother_confirmed_catch"));
            }else if(E.effect==wc::Effect::Heal&&E.resolved>0&&Recipient&&Recipient->health>0){
                const FVector P=To+FVector(80,0,25+Age*75);
                CueLine(P-FVector(15,0,0),P+FVector(15,0,0),Heal,8);
                CueLine(P-FVector(0,0,15),P+FVector(0,0,15),Heal,8);
                CueText(P+FVector(45,0,0),FString::Printf(TEXT("+%.0f"),E.resolved/100.),Heal,ArtSlice?32:25);
                Mark(TEXT("healing_plus"));
            }else if(E.effect==wc::Effect::Damage&&E.resolved>0){
                if(Age<.3f&&!FxLive){
                    const float Size=20+Age*65;
                    if(ArtSlice){
                        const FRotator Facing=Camera?(-Camera->GetActorForwardVector()).Rotation():FRotator::ZeroRotator;
                        const auto Color=E.basicAttack?Hurt:SkillColor(E.mechanic);
                        for(int I=0;I<6;++I){
                            const float Angle=I*UE_TWO_PI/6;
                            const FVector D=Facing.RotateVector(FVector(0,FMath::Cos(Angle),FMath::Sin(Angle)));
                            CueLine(To+D*(7+Age*35),To+D*(18+Age*45),Color,3*Life);
                        }
                        Mark(TEXT("art_slice_six_ray_impact"));
                    }else{
                        CueLine(To-FVector(Size,0,Size),To+FVector(Size,0,Size),E.basicAttack?Hurt:SkillColor(E.mechanic),5*Life);
                        CueLine(To+FVector(Size,0,-Size),To+FVector(-Size,0,Size),E.basicAttack?Hurt:SkillColor(E.mechanic),5*Life);
                    }
                    Mark(TEXT("damage_impact"));
                    if(E.basicAttack){
                        const auto* Source=Find(E.source);
                        if(Source&&Catalog.Definition(Source->definition,Source->neutral).projectileTravelMs==0){
                            const FVector D=(To-From).GetSafeNormal2D();
                            CueRing(From+D*70,65,Strike,7*Life,2.1f,FMath::Atan2(D.Y,D.X)-1.05f+Age*3);
                            Mark(TEXT("melee_strike"));
                        }
                    }else{
                        const auto Color=SkillColor(E.mechanic);
                        if(E.mechanic==wc::AbilityMechanic::ScreenedStrike){
                            CueLine(From,To,Color,10*Life);
                            if(Storybook){
                                const FVector Direction=(To-From).GetSafeNormal2D(),Across(-Direction.Y,Direction.X,0);
                                for(int I=1;I<=3;++I){
                                    const FVector P=FMath::Lerp(From,To,I*.23f);
                                    CueLine(P-Direction*12,P+Across*(I%2?17:-17),Color,3*Life);
                                    CueLine(P+Across*(I%2?17:-17),P+Direction*12,Color,3*Life);
                                }
                            }
                            Mark(TEXT("snapvine_lash"));
                        }
                        if(E.mechanic==wc::AbilityMechanic::CrossingBeams){
                            if(!E.visualCells.empty())CueLine(Position(E.visualCells.front())+FVector(0,0,70),
                                Position(E.visualCells.back())+FVector(0,0,70),Color,11*Life);
                            Mark(TEXT("prism_beam"));
                        }
                        if(E.mechanic==wc::AbilityMechanic::TidalPush){
                            const FVector Direction=(To-From).GetSafeNormal2D();
                            CueRing(To,65+Age*180,Color,8*Life,2.4f,Storybook?FMath::Atan2(Direction.Y,Direction.X)-1.2f:Time*2);
                            Mark(TEXT("reefglass_wave"));
                        }
                    }
                }
                if(E.prevented>0&&E.guardedBy&&!FxLive){
                    const FVector Guard=At(E.guardedBy,E.origin);
                    CueLine(Guard,To,Strike,5*Life);
                    const FVector Incoming=(From-To).GetSafeNormal2D();
                    CueRing(To,85,Strike,7*Life,2.4f,Storybook?FMath::Atan2(Incoming.Y,Incoming.X)-1.2f:Time);
                    Mark(TEXT("bellback_guard"));
                }
            }else if((E.effect==wc::Effect::Dash||E.effect==wc::Effect::Blink)&&Age<.4f&&!FxLive){
                const auto Color=SkillColor(E.mechanic);
                CueLine(From,Position(E.cell)+FVector(0,0,75),Color,(E.mechanic==wc::AbilityMechanic::Standard?3:12)*Life);
                if(E.mechanic==wc::AbilityMechanic::TidalPush){CueText(To+FVector(0,0,90+Age*80),TEXT("PUSH"),Tide,26);Mark(TEXT("push_trail"));}
                else if(E.mechanic==wc::AbilityMechanic::MomentumCharge){
                    Mark(TEXT("charge_trail"));CueRing(To,65+Age*70,Color,5*Life);
                    if(Storybook){
                        const FVector End=Position(E.cell)+FVector(0,0,23),Begin=Position(E.origin)+FVector(0,0,23);
                        const FVector D=(End-Begin).GetSafeNormal2D(),Across(-D.Y,D.X,0);
                        for(int I=1;I<=4;++I){
                            const FVector P=FMath::Lerp(Begin,End,I*.18f)+Across*(I%2?18:-18);
                            CueLine(P-D*7,P+D*7,Color,5*Life);
                        }
                        Mark(TEXT("cragstoat_charge_footfalls"));
                    }
                }
                else Mark(TEXT("movement_trail"));
            }
        }
    }
    if(Storybook){
        const double UpgradeTime=SoloVisualExercise&&CapturePhase!=ECapturePhase::None?CaptureQueuedAt:Elapsed;
        for(auto It=UpgradeStarted.CreateIterator();It;++It)if(UpgradeTime-It.Value()>1.1)It.RemoveCurrent();
        if(!Combat&&SoloMatch&&ViewedSeat==0&&SoloMatch->CurrentPhase()==wc::Phase::Preparation){
            for(const auto& Unit:Formation[0]){
                const float Life=UpgradePulse(Unit.id);
                if(Life<=0)continue;
                const FVector P=Position(Unit.cell)+FVector(0,0,23);
                CueRing(P,57+(1-Life)*31,Strike,4*Life);
                CueStar(P+FVector(0,0,148+(1-Life)*45),19*Life,Strike,3,UE_PI*.5f);
                CueKindsSeen.Add(TEXT("storybook_upgrade_crown"));
                CurrentCueKinds.Add(TEXT("storybook_upgrade_crown"));
            }
        }
    }
    DrawFeedback(Combat);
    UpdatePlacementCue();
    FlushSilkEffects();
    for(int I=CueMeshUsed;I<CueMeshes.Num();++I)CueMeshes[I]->SetVisibility(false);
    for(int I=CueTextUsed;I<CueTexts.Num();++I)CueTexts[I]->SetVisibility(false);
    PeakCueMeshes=FMath::Max(PeakCueMeshes,CueMeshUsed);PeakCueTexts=FMath::Max(PeakCueTexts,CueTextUsed);
}

// ---------------------------------------------------------------------------------------------------------------
// Particle effects. A small CPU particle system drawn as instanced quads: soft glows, smoke, ground rings, streaks
// and tumbling stone shards, plus a pool of short light flashes. Cosmetic only; it reads combat, never changes it.
namespace { enum : uint8 { FxGlow, FxSmoke, FxRing, FxStreak, FxShard }; }

void AWCVNextLab::FxEmit(uint8 Kind,FVector P,FVector V,FLinearColor Color,float Size0,float Size1,float Life,float Gravity,float Drag,float Delay,float Stretch)
{
    if(Fx.Num()>=2200)return;
    FFx New;New.Kind=Kind;New.P=P;New.V=V;New.Color=Color;New.Size0=Size0;New.Size1=Size1;New.Life=Life;New.Gravity=Gravity;
    New.Drag=Drag;New.Age=-Delay;New.Stretch=Stretch;New.Spin=FMath::FRandRange(-6.f,6.f);
    Fx.Add(New);
}
void AWCVNextLab::FxFlash(FVector P,FLinearColor Color,float Intensity,float Life)
{
    if(FxLights.IsEmpty())return;
    int Oldest=0;
    for(int I=1;I<FxLights.Num();++I)if(FxLightAt[I]<FxLightAt[Oldest])Oldest=I;
    FxLights[Oldest]->SetWorldLocation(P);FxLights[Oldest]->SetLightColor(Color);
    FxLightAt[Oldest]=Elapsed;FxLightLife[Oldest]=Life;FxLightPower[Oldest]=Intensity;
}
void AWCVNextLab::TickFx(float Dt)
{
    if(!Camera)return;
    if(!FxBatches[0]){
        auto* Host=SceneActor();
        const TCHAR* Names[]={TEXT("M_FxGlow"),TEXT("M_FxSmoke"),TEXT("M_FxRing"),TEXT("M_FxStreak")};
        for(int Kind=0;Kind<5;++Kind){
            auto* Batch=NewObject<UInstancedStaticMeshComponent>(Host);
            Host->AddInstanceComponent(Batch);Batch->SetupAttachment(Host->GetRootComponent());
            Batch->SetStaticMesh(ProxyMeshes.FindChecked(Kind==FxShard?TEXT("Cube"):TEXT("Plane")));
            Batch->SetMobility(EComponentMobility::Movable);Batch->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Batch->SetCastShadow(Kind==FxShard);Batch->NumCustomDataFloats=Kind==FxShard?0:4;
            UMaterialInterface* Look=Kind==FxShard?nullptr:LoadObject<UMaterialInterface>(nullptr,
                *FString::Printf(TEXT("/Game/WonderChess/VNext/Effects/%s.%s"),Names[Kind],Names[Kind]));
            Batch->SetMaterial(0,Look?Look:Kind==FxShard?static_cast<UMaterialInterface*>(Material(FLinearColor(.28f,.26f,.23f))):CombatCueMaterial.Get());
            // Glows and streaks draw over smoke.
            Batch->SetTranslucentSortPriority(Kind==FxSmoke?0:Kind==FxRing?1:2);
            Batch->RegisterComponent();FxBatches[Kind]=Batch;
        }
        for(int I=0;I<6;++I){
            auto* Light=NewObject<UPointLightComponent>(Host);
            Host->AddInstanceComponent(Light);Light->SetupAttachment(Host->GetRootComponent());
            Light->bUseInverseSquaredFalloff=false;Light->SetLightFalloffExponent(2);Light->SetAttenuationRadius(520);
            Light->SetIntensity(0);Light->SetCastShadows(false);Light->RegisterComponent();
            FxLights.Add(Light);FxLightAt.Add(-100);FxLightLife.Add(.2f);FxLightPower.Add(0);
        }
    }
    const FVector Forward=Camera->GetActorForwardVector(),Side=Camera->GetActorRightVector();
    TArray<FTransform> Transforms[5];TArray<float> Data[4];
    for(int I=Fx.Num()-1;I>=0;--I){
        auto& P=Fx[I];
        const bool Instant=P.Life<=0;
        if(!Instant){
            P.Age+=Dt;
            if(P.Age>=P.Life){Fx.RemoveAtSwap(I,1,EAllowShrinking::No);continue;}
            if(P.Age<0)continue;
            P.V.Z-=P.Gravity*Dt;P.V*=FMath::Max(0.f,1-P.Drag*Dt);P.P+=P.V*Dt;
            if(P.Kind==FxShard&&P.P.Z<9&&P.V.Z<0){P.P.Z=9;P.V=FVector(P.V.X*.5,P.V.Y*.5,-P.V.Z*.35);}
        }
        const float T=Instant?0:P.Age/P.Life;
        const float Size=FMath::Lerp(P.Size0,P.Size1,T);
        const float Alpha=Instant?1:FMath::Min(1.f,P.Age/(.1f*P.Life+.001f))*FMath::Pow(1-T,1.4f);
        FTransform Place;
        if(P.Kind==FxRing)Place=FTransform(FRotator(0,P.Spin*20,0),P.P,FVector(Size/100));
        else if(P.Kind==FxShard)Place=FTransform(FRotator(P.Age*P.Spin*90,P.Spin*40,P.Age*P.Spin*60),P.P,FVector(Size/100));
        else if(P.Kind==FxStreak){
            FVector Along=P.V.GetSafeNormal();
            if(Along.IsNearlyZero())Along=Side;
            Place=FTransform(FRotationMatrix::MakeFromXZ(Along,-Forward).Rotator(),P.P,FVector(Size*P.Stretch/100,Size/100,1));
        }else Place=FTransform((FRotationMatrix::MakeFromZX(-Forward,Side).ToQuat()*FQuat(FVector::ZAxisVector,P.Spin*(1+P.Age))).Rotator(),P.P,FVector(Size/100));
        Transforms[P.Kind].Add(Place);
        if(P.Kind!=FxShard)Data[P.Kind].Append({P.Color.R,P.Color.G,P.Color.B,Alpha*P.Color.A});
        if(Instant)Fx.RemoveAtSwap(I,1,EAllowShrinking::No);
    }
    for(int Kind=0;Kind<5;++Kind){
        auto* Batch=FxBatches[Kind];
        Batch->ClearInstances();
        if(Transforms[Kind].IsEmpty())continue;
        Batch->AddInstances(Transforms[Kind],false,true,false);
        if(Kind!=FxShard&&Batch->PerInstanceSMCustomData.Num()==Data[Kind].Num())Batch->PerInstanceSMCustomData=Data[Kind];
        Batch->MarkRenderStateDirty();
    }
    for(int I=0;I<FxLights.Num();++I){
        const float T=float(Elapsed-FxLightAt[I])/FxLightLife[I];
        FxLights[I]->SetIntensity(T>=0&&T<1?FxLightPower[I]*FMath::Square(1-T):0);
    }
}

// Fight feel layered over the rule-driven cues: team rings, star glow, the draining health segment, hit sparks,
// knocks and numbers, shot trails and each modelled hero's own skill effect. Evidence runs keep the plain cue set,
// so their captures stay comparable.
void AWCVNextLab::DrawFeedback(const wc::Combat* Combat)
{
    for(const auto& Ghost:GhostBars)CueMesh(TEXT("Cube"),Ghost.Location,Ghost.Scale,FLinearColor(1.f,.93f,.72f),Ghost.Rotation);
    GhostBars.Reset();KnockOffsets.Reset();
    const bool Live=Courtyard&&!SoloVisualExercise&&!SoloExercise&&!Exercise;
    const bool Held=SoloMode?SoloPaused:Paused;
    if(Live){TickFx(Held?0.f:GetWorld()->GetDeltaSeconds());TickProps(Held?0.f:GetWorld()->GetDeltaSeconds());}
    if(Live&&!Combat&&SoloMode&&SoloMatch&&ViewedSeat==0&&SoloMatch->CurrentPhase()==wc::Phase::Preparation){
        const auto& Captain=SoloMatch->Seats()[0];
        if(Dragging){
            // While a hero is held, the tiles it may stand on glow green and the far half glows red.
            for(int Row=0;Row<8;++Row)for(int Column=0;Column<8;++Column)
                FxEmit(FxGlow,Position({Column,Row})+FVector(0,0,9),FVector::ZeroVector,Row<Catalog.rules.deploymentRows?FLinearColor(.10f,.55f,.16f):FLinearColor(.50f,.06f,.04f),250,250,0);
        }
        // Heroes that a shop offer would upgrade stand in a gold ring.
        for(int Slot=0;Slot<int(Captain.shop.size());++Slot){
            if(Captain.shop[Slot]<0)continue;
            wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;
            const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Buy);
            if(!Preview.accepted||Preview.mergeSteps.empty())continue;
            for(const auto& Unit:Captain.roster)if(Unit.definition==Captain.shop[Slot])
                FxEmit(FxRing,Position(Unit.onBoard?Unit.cell:wc::Cell{Unit.bench,-1})+FVector(0,0,8),FVector::ZeroVector,FLinearColor(2.4f,1.7f,.5f)*(.7f+.3f*FMath::Sin(float(Elapsed)*5)),150,150,0);
        }
        // The guided match points into the yard itself when a step is about the bench or about rows of the board.
        if(GuideStage>=0&&GuideStage<int(GuideScript.stages.size())&&GuideStep<int(GuideScript.stages[GuideStage].steps.size())){
            const auto& Step=GuideScript.stages[GuideStage].steps[GuideStep];
            const FLinearColor Point=FLinearColor(2.6f,2.2f,1.f)*(.6f+.4f*FMath::Sin(float(Elapsed)*6));
            if(Step.highlight=="WC.Bench")for(const auto& Unit:Captain.roster)if(!Unit.onBoard)
                FxEmit(FxRing,Position(wc::Cell{Unit.bench,-1})+FVector(0,0,8),FVector::ZeroVector,Point,175,175,0);
            if(Step.highlight=="WC.Board"){
                const int From=Step.done=="row_at_least"?Step.value:0,To=Step.done=="row_at_most"?Step.value:Catalog.rules.deploymentRows-1;
                for(int Row=From;Row<=To;++Row)for(int Column=0;Column<Catalog.rules.columns;++Column)
                    FxEmit(FxRing,Position({Column,Row})+FVector(0,0,8),FVector::ZeroVector,Point,150,150,0);
            }
        }
    }
    if(!Combat||!Live){FeedbackCombat=nullptr;return;}
    if(Combat!=FeedbackCombat||Combat->CurrentTick()<FeedbackTick){FeedbackCombat=Combat;FeedbackTick=-1;FeedbackFallen=0;ShotLaunched.Reset();}
    const float TickSeconds=Catalog.rules.tickMs/1000.f;
    const float Smooth=Held?0.f:float(FMath::Clamp(Accumulator/TickSeconds,0.,1.));
    const float Time=float(Elapsed);
    const auto Unit=[&](wc::Id Id)->const wc::CombatUnit*{for(const auto& U:Combat->Units())if(U.id==Id)return &U;return nullptr;};
    const auto Where=[&](wc::Id Id,wc::Cell Fallback,float Z){
        if(const auto* View=Pieces.Find(Id);View&&View->Actor.IsValid()){FVector P=View->Actor->GetActorLocation();P.Z=Z;return P;}
        return Position(Fallback)+FVector(0,0,Z);
    };
    const auto Muzzle=[&](wc::Id Id,wc::Cell Fallback,int Index){
        if(const auto* View=Pieces.Find(Id);View&&View->Hero)return View->Hero->MuzzleLocation(Index);
        return Where(Id,Fallback,95);
    };
    const auto Around=[](float Speed,float Up){
        const float A=FMath::FRandRange(0.f,UE_TWO_PI);
        return FVector(FMath::Cos(A),FMath::Sin(A),0)*Speed*FMath::FRandRange(.55f,1.f)+FVector(0,0,Up*FMath::FRandRange(.5f,1.f));
    };
    const FLinearColor Side[]={FLinearColor(0.f,1.25f,1.1f),FLinearColor(1.9f,.22f,.08f)};
    const FLinearColor Dust(.30f,.26f,.20f,.6f),Warm(2.6f,1.7f,.7f),Cold(.7f,1.5f,2.8f),Water(.35f,.9f,2.2f),Foam(.75f,.88f,1.f,.6f),
        Leaf(.5f,2.2f,.45f),Light(1.5f,2.4f,3.f),Golden(2.6f,1.9f,.6f),Silver(.80f,.84f,.90f),Iron(.38f,.38f,.42f),Dark(.07f,.06f,.05f);
    // Modelled shots in flight: the piece itself, tumbling along its arc, with its own trail. The throw may begin a
    // little before the rules release the attack so the arc can be seen; it always lands on the rules' impact tick.
    for(const auto& Action:Combat->VisualActions()){
        if(Action.impactTick<=Action.releaseTick)continue;
        const FShotLook* Look=ShotLook(Catalog.Definition(Action.definition,Action.neutral).id,Action.basicAttack);
        if(!Look)continue;
        const float Begin=Action.releaseTick-Look->LeadMs/float(Catalog.rules.tickMs);
        const float Span=Action.impactTick-Begin;
        const float T=(Combat->CurrentTick()+Smooth-Begin)/Span;
        if(T<0||T>=1)continue;
        FVector Start=Muzzle(Action.source,Action.origin,int(Action.action));
        const auto* Shooter=Pieces.Find(Action.source);
        if(Shooter&&Shooter->Hero&&Shooter->Hero->GetMesh()&&!Look->FromBone.IsEmpty())Start=Shooter->Hero->GetMesh()->GetSocketLocation(FName(*Look->FromBone));
        const FVector End=Where(Action.target,Action.center,Action.basicAttack?80:30);
        if(Shooter&&Shooter->Hero&&Look->FromItem>=0){
            const FVector Mount=Shooter->Hero->ItemLocation(Look->FromItem);
            // Shots alternate between the left and right side of the mount (a rack on each side).
            const FVector Ahead=(End-Mount).GetSafeNormal2D();
            Start=Mount+Ahead*Look->FromForward+FVector(Ahead.Y,-Ahead.X,0)*Look->FromSide*(Action.action%2?1.f:-1.f)+FVector(0,0,Look->FromUp);
        }
        if(!ShotLaunched.Contains(Action.action)){
            ShotLaunched.Add(Action.action);
            const FVector Out=(End-Start).GetSafeNormal();
            if(Look->Launch==TEXT("cannon")){
                // The cannon speaks: a flash at the mouth and smoke rolling forward.
                PropEmit(TEXT("BlastStar"),Start+Out*20,FVector::ZeroVector,FQuat(FRotator(FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f),0)),FVector(0,0,300),.15f,.6f,.14f);
                for(int I=0;I<5;++I)PropEmit(TEXT("SmokeBall"),Start+Out*30,Out*FMath::FRandRange(60.f,220.f)+Around(50,60),FQuat::Identity,FVector(20,30,40),.2f,.75f+I*.08f,FMath::FRandRange(.6f,1.f),-40,false,I*.03f);
                FxFlash(Start,FLinearColor(1.f,.7f,.3f),10,.18f);CamShake=FMath::Max(CamShake,.35f);
                if(Shooter&&Shooter->Hero&&Look->FromItem>=0)Shooter->Hero->KickItem(Look->FromItem,34);
            }else if(Look->Launch==TEXT("gun")){
                PropEmit(TEXT("BlastStar"),Start+Out*12,FVector::ZeroVector,FQuat(FRotator(FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f),0)),FVector(0,0,300),.08f,.3f,.1f);
                for(int I=0;I<3;++I)PropEmit(TEXT("SmokeBall"),Start+Out*18,Out*FMath::FRandRange(40.f,130.f)+Around(30,40),FQuat::Identity,FVector(20,30,40),.1f,.36f+I*.06f,FMath::FRandRange(.5f,.8f),-40,false,I*.03f);
                FxFlash(Start,FLinearColor(1.f,.8f,.5f),7,.12f);
            }
        }
        const auto Path=[&](float K){return FMath::Lerp(Start,End,K)+FVector(0,0,Look->Arc*4*K*(1-K));};
        const FVector At=Path(T),Heading=(Path(FMath::Min(1.f,T+.03f))-Path(FMath::Max(0.f,T-.03f))).GetSafeNormal();
        const float Flown=T*Span*TickSeconds;
        const FQuat Tumble(FRotator(Look->Spin.Y*Flown,Look->Spin.Z*Flown,Look->Spin.X*Flown));
        const float Size=Look->Scale*FMath::Lerp(1.f,Look->Grow,T);
        PropEmit(Look->Mesh,At,FVector::ZeroVector,FRotationMatrix::MakeFromY(Heading).ToQuat()*Tumble,FVector::ZeroVector,Size,Size,0);
        const FVector Tail=At-Heading*18*Look->Scale;
        if(Look->Trail==TEXT("ember")){
            FxEmit(FxGlow,At,FVector::ZeroVector,FLinearColor(3.f,1.3f,.3f),46,46,0);
            if(!Held&&FMath::FRand()<.8f)PropEmit(TEXT("Ember"),Tail+Around(8,8),Around(40,30)-Heading*40,FQuat::Identity,FVector::ZeroVector,1.f,.3f,.45f,420);
        }else if(Look->Trail==TEXT("rocket")){
            FxEmit(FxGlow,Tail,FVector::ZeroVector,FLinearColor(3.f,1.6f,.4f),34,34,0);
            PropEmit(TEXT("FlameDrop"),Tail,FVector::ZeroVector,FRotationMatrix::MakeFromY(-Heading).ToQuat(),FVector::ZeroVector,.9f,.9f,0);
            if(!Held&&FMath::FRand()<.8f)PropEmit(TEXT("SmokeBall"),Tail,Around(20,20),FQuat::Identity,FVector(0,0,60),.10f,.34f,.5f,-30);
        }else if(Look->Trail==TEXT("wisp")){
            FxEmit(FxGlow,At,FVector::ZeroVector,FLinearColor(.6f,2.6f,.9f),50,50,0);
            if(!Held&&FMath::FRand()<.6f)FxEmit(FxGlow,Tail+Around(10,10),Around(20,30),FLinearColor(.5f,2.2f,.8f),12,2,.4f);
        }else if(Look->Trail==TEXT("glint")){
            FxEmit(FxGlow,Tail,FVector::ZeroVector,FLinearColor(.5f,.9f,1.2f),30,30,0);
            if(!Held&&FMath::FRand()<.5f)PropEmit(TEXT("CrystalSplinter"),Tail,Around(40,40),FQuat(FRotator(FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f),0)),FVector(300,200,100),.7f,.2f,.35f,300);
        }else if(Look->Trail==TEXT("holy")){
            FxEmit(FxGlow,At,FVector::ZeroVector,FLinearColor(3.f,2.2f,.8f),44,44,0);
            if(!Held&&FMath::FRand()<.5f)FxEmit(FxGlow,Tail,Around(15,25),FLinearColor(3.f,2.2f,.8f),9,2,.35f);
        }else if(Look->Trail==TEXT("drip")){
            if(!Held&&FMath::FRand()<.8f)PropEmit(TEXT("Droplet"),Tail+Around(6,6),Around(25,10),FQuat::Identity,FVector::ZeroVector,.8f,.4f,.4f,900);
        }else if(Look->Trail==TEXT("leaf")){
            if(!Held&&FMath::FRand()<.35f)PropEmit(TEXT("LeafScrap"),Tail,Around(30,20),FQuat(FRotator(FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f),0)),FVector(300,200,260),.8f,.5f,.6f,160);
        }else if(Look->Trail==TEXT("tracer")){
            const FVector Back=At-Heading*110;
            FxEmit(FxStreak,(At+Back)*.5,Heading*.01,FLinearColor(3.f,2.6f,1.6f),5,5,0,0,0,0,24);
        }else if(Look->Trail==TEXT("chain")){
            // The chain pays out behind the hook, link after link, back to the hand.
            const float Reach=float(FVector::Dist(Start,At));
            const FVector Along=(At-Start).GetSafeNormal();
            const FQuat Lie=FRotationMatrix::MakeFromY(Along).ToQuat();
            const int Links=FMath::Min(60,int(Reach/12));
            for(int I=0;I<Links;++I){
                const float K=(I+.5f)/Links;
                PropEmit(TEXT("ChainLink"),FMath::Lerp(Start,At,K)-FVector(0,0,FMath::Sin(K*UE_PI)*10),FVector::ZeroVector,Lie*FQuat(FRotator(I%2?90.f:0.f,0,0)),FVector::ZeroVector,1,1,0);
            }
        }
        if(Look->Trail==TEXT("fuse")){
            // A lit fuse: a bright point at the tail, sparks falling away and small puffs of smoke left behind.
            FxEmit(FxGlow,At-Heading*20*Look->Scale,FVector::ZeroVector,FLinearColor(3.f,2.f,.6f),18,18,0);
            if(!Held&&FMath::FRand()<.7f)PropEmit(TEXT("SmokeBall"),At-Heading*20,FVector(FMath::FRandRange(-15.f,15.f),FMath::FRandRange(-15.f,15.f),30),FQuat::Identity,FVector(0,0,60),.10f,.26f,.4f,-30);
            if(!Held&&FMath::FRand()<.6f)FxEmit(FxStreak,At-Heading*20,-Heading*120+Around(90,60),FLinearColor(3.f,1.8f,.5f),5,1,.2f,300,1,0,3);
        }
        if(Shooter&&Shooter->Hero&&Look->HideItem>=0)Shooter->Hero->HideItemFor(Look->HideItem,(1-T)*Span*TickSeconds+.35f);
    }
    int Fallen=0;
    for(const auto& U:Combat->Units()){
        if(U.health<=0){++Fallen;continue;}
        const FVector Foot=Where(U.id,U.cell,6);
        // The skill's name floats over the caster while it winds up.
        if(U.state==wc::ActionState::CastWindup)CueText(Where(U.id,U.cell,250),FString(UTF8_TO_TCHAR(U.ability.name.c_str())),FLinearColor(1.f,.86f,.45f),24);
        // Whose piece this is: a soft ring in the team colour, only while fighting. Stars add silver or gold.
        FxEmit(FxRing,Foot,FVector::ZeroVector,Side[U.side?1:0],118,118,0);
        if(U.star>=3){
            FxEmit(FxRing,Foot+FVector(0,0,1),FVector::ZeroVector,Golden*(.8f+.25f*FMath::Sin(Time*3+U.id)),150,150,0);
            FxEmit(FxGlow,Foot+FVector(0,0,4),FVector::ZeroVector,Golden*.35f,210,210,0);
            if(!Held&&FMath::FRand()<.12f)FxEmit(FxGlow,Foot+Around(45,0),FVector(0,0,70),Golden,9,2,1.1f,-10);
        }else if(U.star==2)FxEmit(FxRing,Foot+FVector(0,0,1),FVector::ZeroVector,Silver,138,138,0);
    }
    bool HitSound=false,SkillSound=false;
    TSet<uint64> Drawn,ShotDrawn,ShapeDrawn;
    TMap<uint64,TArray<FVector>> Chains;
    const FVector HalfX=(Position({1,0})-Position({0,0}))*.45f,HalfY=(Position({0,1})-Position({0,0}))*.45f;
    const auto& Events=Combat->Events();
    for(auto It=Events.rbegin();It!=Events.rend();++It){
        const auto& E=*It;
        const float Age=(Combat->CurrentTick()+Smooth-E.tick)*TickSeconds;
        if(Age>.9f)break;
        const bool New=E.tick>FeedbackTick;
        const auto* Source=Unit(E.source);const auto* Target=Unit(E.target);
        const std::string Hero=Source?Catalog.Definition(Source->definition,Source->neutral).id:std::string();
        const FVector To=Where(E.target,E.cell,80),Ground=Where(E.target,E.cell,8);
        const FVector From=Source?Where(E.source,E.origin,80):Position(E.origin)+FVector(0,0,80);
        const FVector Line=(To-From).GetSafeNormal2D();
        if(E.effect==wc::Effect::Damage&&E.evaded&&Age<.75f)
            CueText(To+FVector(0,0,95+Age*85),FString(SoloGuideIndonesian?TEXT("Meleset"):TEXT("Miss")),FLinearColor(.72f,.72f,.72f),28);
        if(wc::IsStatusEffect(E.effect)&&E.resolved>0&&Age<.9f)
            CueText(To+FVector(0,0,110+Age*70),FString(E.effect==wc::Effect::Hex?(SoloGuideIndonesian?TEXT("Terkutuk"):TEXT("Hexed")):
                E.effect==wc::Effect::Silence?(SoloGuideIndonesian?TEXT("Bungkam"):TEXT("Silenced")):
                (SoloGuideIndonesian?TEXT("Terpancing"):TEXT("Taunted"))),FLinearColor(.78f,.55f,.95f),28);
        if(E.effect==wc::Effect::ManaDrain&&E.resolved>0&&Age<.75f)
            CueText(To+FVector(0,0,120+Age*60),FString::Printf(TEXT("-%.0f mana"),E.resolved/100.),FLinearColor(.45f,.62f,1.f),24);
        if(E.effect==wc::Effect::Blink){
            // A blink: a fading trail between the two cells, a glow where the unit left and a ring where it lands.
            const FVector Left=Position(E.origin)+FVector(0,0,70),Lands=Position(E.cell)+FVector(0,0,70);
            if(Age<.3f)CueLine(Left,Lands,FLinearColor(.75f,.9f,1.f),5*(1-Age/.3f));
            if(New){
                FxEmit(FxGlow,Left,FVector::ZeroVector,Cold,130,20,.25f);
                FxEmit(FxGlow,Lands,FVector::ZeroVector,Cold,40,170,.3f);
                FxEmit(FxRing,Position(E.cell)+FVector(0,0,8),FVector::ZeroVector,Cold,40,230,.3f);
            }
        }
        if(E.effect==wc::Effect::Summon&&New){
            // A summon arrives in a green ring of light; one whose time is up leaves in dust.
            const FVector Spot=Position(E.cell);
            if(E.source!=E.target){
                FxEmit(FxRing,Spot+FVector(0,0,8),FVector::ZeroVector,Leaf,30,250,.4f);
                FxEmit(FxGlow,Spot+FVector(0,0,60),FVector::ZeroVector,Leaf,60,210,.35f);
                for(int I=0;I<8;++I)FxEmit(FxStreak,Spot+Around(30,0),FVector(0,0,FMath::FRandRange(180.f,320.f)),Leaf,7,2,FMath::FRandRange(.25f,.45f),0,1,0,4);
            }else for(int I=0;I<8;++I)FxEmit(FxSmoke,Spot+FVector(0,0,30)+Around(20,15),Around(90,70),Dust,40,120,FMath::FRandRange(.5f,.9f),-15,2);
        }
        if(E.effect==wc::Effect::Damage&&!E.basicAttack&&E.mechanic==wc::AbilityMechanic::Standard&&!E.visualCells.empty()&&Age<.35f&&!ShapeDrawn.Contains(E.action)){
            // A line or a cone: the cells it covers light up for a moment.
            ShapeDrawn.Add(E.action);
            const FLinearColor Tone=(E.damageType==wc::DamageType::Physical?FLinearColor(.95f,.60f,.22f):FLinearColor(.36f,.58f,1.f))*(1-Age/.35f);
            for(const auto Covered:E.visualCells){
                const FVector C=Position(Covered)+FVector(0,0,6);
                const FVector Corner[]={C-HalfX-HalfY,C+HalfX-HalfY,C+HalfX+HalfY,C-HalfX+HalfY};
                for(int I=0;I<4;++I)CueLine(Corner[I],Corner[(I+1)%4],Tone,4);
            }
        }
        if(E.effect==wc::Effect::Damage&&!E.basicAttack&&Age<.45f&&Source&&Source->ability.selector==wc::Selector::ChainFromCurrentEnemy)
            Chains.FindOrAdd(E.action).Add(To);
        if(E.effect==wc::Effect::Damage&&E.resolved>0){
            const bool Heavy=(Target&&E.healthLoss*4>Target->maxHealth)||E.critical;
            const bool Magic=E.damageType!=wc::DamageType::Physical;
            if(Age<.2f)KnockOffsets.FindOrAdd(E.target)+=Line*(E.basicAttack?7.f:13.f)*FMath::Sin(Age/.2f*UE_PI);
            if((!E.basicAttack||Heavy)&&Age<.75f)
                // Cream for physical, blue for magic, white for true damage. A critical hit carries a mark; hits that
                // follow another hit (reflect, bonus true damage) and damage over time are written smaller.
                CueText(To+FVector(float(int(E.source%3)-1)*28,0,95+Age*85),E.critical?FString::Printf(TEXT("%.0f!"),E.resolved/100.):FString::Printf(TEXT("%.0f"),E.resolved/100.),
                    E.damageType==wc::DamageType::True?FLinearColor(1.f,1.f,1.f):Magic?FLinearColor(.50f,.76f,1.f):FLinearColor(1.f,.95f,.85f),
                    Heavy?40:E.secondary||E.periodic?23:30);
            if(New){
                // Every hit: a flash at the point of contact and sparks thrown along the blow.
                const FLinearColor Tone=Magic?Cold:Warm;
                FxEmit(FxGlow,To,FVector::ZeroVector,Tone,E.basicAttack?70:130,E.basicAttack?20:40,.14f);
                for(int I=0;I<(E.basicAttack?5:10);++I)
                    FxEmit(FxStreak,To,(Line*FMath::FRandRange(120.f,330.f)+Around(170,150)),Tone,7,2,FMath::FRandRange(.18f,.34f),520,2,0,4);
                if(Heavy){FxEmit(FxRing,Ground,FVector::ZeroVector,Tone,60,300,.3f);FxFlash(To,Tone,7,.2f);CamShake=FMath::Max(CamShake,.6f);}
                if(const FShotLook* Blow=E.basicAttack&&Source&&Catalog.Definition(Source->definition,Source->neutral).projectileTravelMs==0?MeleeLook(Hero):nullptr){
                    ShotImpact(*Blow,To,Ground,Line);
                }else if(E.basicAttack&&Source&&Catalog.Definition(Source->definition,Source->neutral).projectileTravelMs==0){
                    // A melee blow leaves a bright arc swept through the air in front of the attacker.
                    const FVector Across(-Line.Y,Line.X,0);
                    for(int I=0;I<7;++I){
                        const float A=(I-3)*.33f;
                        const FVector At=From+Line*(62+18*FMath::Cos(A))+Across*FMath::Sin(A)*62+FVector(0,0,18-I*5);
                        FxEmit(FxStreak,At,(Across*FMath::Cos(A)-Line*FMath::Sin(A))*90,FLinearColor(2.6f,2.3f,1.6f),13-FMath::Abs(I-3)*2.5f,2,.2f,0,3,I*.012f,4.5f);
                    }
                }
                if(E.basicAttack&&Source&&Source->neutral&&Catalog.Definition(Source->definition,true).id=="wc_vn_n_slate_ram"){
                    // Slate Ram: stone meets armour. Chips fly, dust rolls off its shoulders and the ground shakes a little.
                    for(int I=0;I<7;++I)FxEmit(FxShard,To-Line*20,-Line*120+Around(200,330),FLinearColor::White,FMath::FRandRange(5.f,10.f),3,FMath::FRandRange(.6f,1.f),1100,.4f);
                    for(int I=0;I<9;++I)FxEmit(FxSmoke,From+Line*70+Around(25,20),Line*90+Around(110,60),Dust,30,120,FMath::FRandRange(.5f,.9f),-15,2.5f);
                    FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(1.2f,1.3f,1.5f),50,260,.3f);
                    CamShake=FMath::Max(CamShake,.45f);
                }
                if(const FShotLook* Landed=ShotLook(Hero,E.basicAttack);Landed&&!Landed->Impact.IsEmpty()&&(E.basicAttack||!ShotDrawn.Contains(E.action))){
                    ShotDrawn.Add(E.action);ShotImpact(*Landed,E.basicAttack?To:Ground+FVector(0,0,40),Ground,Line);
                }
                HitSound|=E.basicAttack;SkillSound|=!E.basicAttack;
            }
        }
        if(E.prevented>0&&E.guardedBy&&New){
            // The Shieldbearer's guard: the shield flares gold, then blue, and throws sparks back at the attacker.
            const FVector Guard=Where(E.guardedBy,E.origin,105);
            FxEmit(FxGlow,Guard,FVector::ZeroVector,Golden,60,230,.22f);
            FxEmit(FxGlow,Guard,FVector::ZeroVector,Cold,150,260,.4f,0,0,.08f);
            FxEmit(FxRing,Guard-FVector(0,0,97),FVector::ZeroVector,Golden,120,330,.4f);
            for(int I=0;I<12;++I)FxEmit(FxStreak,Guard,Around(260,220),Golden,8,2,FMath::FRandRange(.2f,.4f),600,2,0,4);
            FxFlash(Guard,FLinearColor(1.f,.85f,.5f),9,.25f);
        }
        if(E.basicAttack)continue;
        if(E.mechanic==wc::AbilityMechanic::ScreenedStrike&&E.effect==wc::Effect::Damage&&Age<.4f){
            // Hookjaw: a chain of links from the hand to the target, slack as it flies and taut as it bites.
            const FVector Hand=Muzzle(E.source,E.origin,0);
            const float Sag=45*FMath::Max(0.f,1-Age/.14f),Reach=FMath::Min(1.f,Age/.1f);
            FVector Last=Hand;
            for(int I=1;I<=14;++I){
                const float K=I/14.f*Reach;
                const FVector Link=FMath::Lerp(Hand,To,K)-FVector(0,0,Sag*FMath::Sin(K*UE_PI));
                CueLine(Last,Link,Iron,I%2?4.f:2.5f);Last=Link;
            }
            FxEmit(FxGlow,Last,FVector::ZeroVector,Warm*.6f,26,26,0);
        }
        if(E.mechanic==wc::AbilityMechanic::CrossingBeams&&E.effect==wc::Effect::Damage&&Age<.3f){
            // Prism Scholar: a beam of light from a crystal to each target, held for a moment and fading.
            const FVector Crystal=Muzzle(E.source,E.origin,int(E.target%3));
            const float Fade=1-Age/.3f;
            FLinearColor Beam=Light*Fade;
            FxEmit(FxStreak,(Crystal+To)*.5,(To-Crystal).GetSafeNormal()*.01,Beam,26*Fade+6,0,0,0,0,0,float(FVector::Dist(Crystal,To))/(26*Fade+6)*1.15f);
            FxEmit(FxGlow,Crystal,FVector::ZeroVector,Beam,70,70,0);
        }
        if(!New)continue;
        if(E.mechanic==wc::AbilityMechanic::MomentumCharge&&E.effect==wc::Effect::Damage){
            // Tusk Charge: dust kicked up along the dash, then a burst of dust, sparks and a shockwave at contact.
            const FVector Begin=Position(E.origin)+FVector(0,0,14);
            for(int I=0;I<16;++I){
                const float K=I/16.f;
                FxEmit(FxSmoke,FMath::Lerp(Begin,Ground,K)+Around(22,0),Around(40,60),Dust,34,120,FMath::FRandRange(.5f,.85f),-30,1.5f,K*.1f);
            }
            for(int I=0;I<18;++I)FxEmit(FxSmoke,Ground+Around(20,10),Around(300,110),Dust,40,150,FMath::FRandRange(.5f,.9f),-20,3,.1f);
            for(int I=0;I<16;++I)FxEmit(FxStreak,To,Line*220+Around(300,260),Warm,9,2,FMath::FRandRange(.2f,.45f),650,2,.1f,4);
            FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(1.8f,1.5f,1.1f),70,460,.38f,0,0,.1f);
            FxEmit(FxGlow,To,FVector::ZeroVector,Warm,170,60,.18f,0,0,.1f);
            FxFlash(To,FLinearColor(1.f,.8f,.5f),10,.25f);CamShake=FMath::Max(CamShake,.85f);
        }else if(E.mechanic==wc::AbilityMechanic::ScreenedStrike&&E.effect==wc::Effect::Damage){
            for(int I=0;I<12;++I)FxEmit(FxStreak,To,-Line*200+Around(220,200),Warm,8,2,FMath::FRandRange(.2f,.4f),600,2,.1f,4);
        }else if(E.mechanic==wc::AbilityMechanic::TidalPush&&(E.effect==wc::Effect::Dash||E.effect==wc::Effect::Damage)){
            // Tide Caller: a foaming crest rolls down the lane and breaks into spray on what it hits.
            const FVector Start=Position(E.origin)+FVector(0,0,26),D=(Ground-Start).GetSafeNormal2D(),Across(-D.Y,D.X,0);
            const float Reach=float(FVector::Dist2D(Start,Ground));
            for(int I=0;I<26;++I){
                const float Spread=FMath::FRandRange(-1.f,1.f);
                FxEmit(I%3?FxSmoke:FxGlow,Start+Across*Spread*70+FVector(0,0,FMath::FRandRange(0.f,40.f)),D*(Reach/.34f)*FMath::FRandRange(.85f,1.05f),
                    I%3?Foam:Water,I%3?70:46,I%3?130:20,.4f,0,.6f,FMath::FRandRange(0.f,.06f));
            }
            for(int I=0;I<20;++I)FxEmit(FxGlow,Ground+FVector(0,0,50),D*120+Around(230,420),Water,15,5,FMath::FRandRange(.45f,.8f),900,.6f,.3f);
            FxEmit(FxRing,Ground,FVector::ZeroVector,Water,80,420,.45f,0,0,.3f);
            FxFlash(Ground+FVector(0,0,80),FLinearColor(.5f,.75f,1.f),7,.3f);
        }else if(E.mechanic==wc::AbilityMechanic::StationaryGrove&&E.effect==wc::Effect::Heal&&E.resolved>0){
            // Grove Druid: green motes spiral up from each ally the grove heals.
            for(int I=0;I<9;++I)FxEmit(FxGlow,Ground+Around(42,20),FVector(0,0,FMath::FRandRange(90.f,170.f)),Leaf,14,3,FMath::FRandRange(.6f,1.f),-20,0,I*.03f);
            FxEmit(FxGlow,Ground+FVector(0,0,60),FVector::ZeroVector,Leaf*.5f,60,190,.45f);
        }else if(E.mechanic==wc::AbilityMechanic::CrossingBeams&&E.effect==wc::Effect::Damage){
            for(int I=0;I<10;++I)FxEmit(FxStreak,To,Around(280,220),Light,8,2,FMath::FRandRange(.18f,.35f),450,2,0,4);
            FxEmit(FxRing,Ground,FVector::ZeroVector,Light,50,260,.3f);
            FxFlash(To,FLinearColor(.6f,.9f,1.f),9,.22f);
        }else if(Hero=="wc_vn_hammerer"&&(E.effect==wc::Effect::Stun||E.effect==wc::Effect::Damage)&&!Drawn.Contains(E.action)){
            // Hammerer: two shockwave rings, a roll of dust and stone chips where the hammer lands.
            Drawn.Add(E.action);
            FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(2.2f,1.9f,1.4f),60,520,.4f);
            FxEmit(FxRing,Ground,FVector::ZeroVector,Warm*.6f,40,340,.5f,0,0,.06f);
            for(int I=0;I<16;++I)FxEmit(FxSmoke,Ground+Around(25,5),Around(330,70),Dust,40,150,FMath::FRandRange(.5f,.9f),-15,3);
            for(int I=0;I<10;++I)FxEmit(FxShard,Ground+FVector(0,0,12),Around(260,430),FLinearColor::White,FMath::FRandRange(7.f,14.f),4,FMath::FRandRange(.8f,1.2f),1100,.4f);
            for(int I=0;I<12;++I)FxEmit(FxStreak,Ground+FVector(0,0,20),Around(300,330),Warm,8,2,FMath::FRandRange(.2f,.4f),700,2,0,4);
            FxEmit(FxGlow,Ground+FVector(0,0,30),FVector::ZeroVector,Warm,220,70,.16f);
            FxFlash(Ground+FVector(0,0,60),FLinearColor(1.f,.85f,.55f),12,.25f);CamShake=FMath::Max(CamShake,.8f);
        }else if(Hero=="wc_vn_earthbreaker"&&!Drawn.Contains(E.action)){
            // Earthbreaker: the ground heaves. Dust rolls out low in every direction, stones are thrown up, rings run out.
            Drawn.Add(E.action);
            const FVector Centre=Position(E.origin)+FVector(0,0,10);
            EarthCracks.Add({Centre,Elapsed});
            for(int I=0;I<34;++I)FxEmit(FxSmoke,Centre+Around(40,8),Around(460,60),Dust,50,190,FMath::FRandRange(.7f,1.2f),-12,2.6f);
            for(int I=0;I<16;++I)FxEmit(FxShard,Centre+Around(90,0)+FVector(0,0,8),Around(170,520),FLinearColor::White,FMath::FRandRange(9.f,19.f),5,FMath::FRandRange(.9f,1.4f),1200,.3f);
            FxEmit(FxRing,Centre,FVector::ZeroVector,FLinearColor(2.f,1.5f,.9f),90,760,.5f);
            FxEmit(FxRing,Centre,FVector::ZeroVector,Warm*.5f,60,520,.65f,0,0,.08f);
            FxEmit(FxGlow,Centre+FVector(0,0,20),FVector::ZeroVector,FLinearColor(2.4f,1.3f,.4f),330,120,.22f);
            FxFlash(Centre+FVector(0,0,70),FLinearColor(1.f,.7f,.35f),14,.3f);CamShake=FMath::Max(CamShake,1.f);
        }else if(!Hero.empty()&&E.mechanic==wc::AbilityMechanic::Standard){
            // Standard-ability heroes: each has its own look for the moment the skill lands.
            const FLinearColor Fire(3.f,1.4f,.35f),Soot(.10f,.09f,.08f,.7f),Venom(.55f,2.4f,.35f),Hex(1.9f,.6f,2.6f),Moon(1.5f,1.6f,2.8f),
                Bark(.42f,.30f,.16f,.8f),Steel(1.1f,1.5f,2.2f),Blood(2.6f,.25f,.2f),Bone(.9f,2.2f,.7f);
            const FVector Across(-Line.Y,Line.X,0);
            const float Reach=float(FVector::Dist(From,To));
            const auto Tracer=[&](FVector A,FVector B,FLinearColor Tone,float Width,float Life){
                FxEmit(FxStreak,(A+B)*.5,(B-A).GetSafeNormal()*.01,Tone,Width,Width*.3f,Life,0,0,0,float(FVector::Dist(A,B))/Width*1.1f);
            };
            const auto Blast=[&](FVector At,float Scale,float Delay){
                FxEmit(FxGlow,At+FVector(0,0,40),FVector::ZeroVector,Fire,200*Scale,60*Scale,.2f,0,0,Delay);
                FxEmit(FxRing,At,FVector::ZeroVector,Fire,60*Scale,430*Scale,.4f,0,0,Delay);
                for(int I=0;I<int(14*Scale);++I)FxEmit(FxSmoke,At+Around(30,30),Around(170*Scale,190),Soot,50*Scale,170*Scale,FMath::FRandRange(.7f,1.2f),-40,2,Delay+.04f);
                for(int I=0;I<int(14*Scale);++I)FxEmit(FxStreak,At+FVector(0,0,25),Around(380*Scale,380),Fire,9,2,FMath::FRandRange(.25f,.5f),800,2,Delay,4);
                for(int I=0;I<int(7*Scale);++I)FxEmit(FxShard,At+FVector(0,0,12),Around(230,430),FLinearColor::White,FMath::FRandRange(6.f,12.f),4,FMath::FRandRange(.8f,1.1f),1100,.4f,Delay);
            };
            const bool First=!Drawn.Contains(E.action);
            Drawn.Add(E.action);
            if(Hero=="wc_vn_siege_master"&&First){
                // Siege Master: smoke and fire at the cannon's mouth, then the shell bursts on the ground.
                const FVector Mouth=From+Line*95-Across*70-FVector(0,0,25);
                FxEmit(FxGlow,Mouth,FVector::ZeroVector,Fire,150,40,.14f);
                for(int I=0;I<10;++I)FxEmit(FxSmoke,Mouth,Line*FMath::FRandRange(80.f,260.f)+Around(60,70),Soot,35,150,FMath::FRandRange(.7f,1.2f),-30,2.5f);
                Blast(Ground,1.25f,0);FxFlash(Ground+FVector(0,0,70),FLinearColor(1.f,.6f,.25f),16,.3f);CamShake=FMath::Max(CamShake,1.f);
            }else if(Hero=="wc_vn_forge_king"&&First){
                // Forge King: a volley of rockets comes down one after another around the target.
                for(int Rocket=0;Rocket<5;++Rocket){
                    const FVector At=Ground+(Rocket?Around(150,0):FVector::ZeroVector);
                    const float Delay=Rocket*.09f;
                    FxEmit(FxStreak,At+FVector(0,0,330)-Line*170,(Line*170-FVector(0,0,330))/.12f,Fire,16,6,.12f,0,0,Delay,5);
                    Blast(At,.62f,Delay+.1f);
                }
                FxFlash(Ground+FVector(0,0,80),FLinearColor(1.f,.55f,.2f),15,.5f);CamShake=FMath::Max(CamShake,1.f);
            }else if(Hero=="wc_vn_bomber"&&First&&!ShotLook(Hero,false)){
                Blast(Ground,.9f,0);FxFlash(Ground+FVector(0,0,60),FLinearColor(1.f,.6f,.25f),11,.25f);CamShake=FMath::Max(CamShake,.7f);
            }else if(Hero=="wc_vn_longbow_scout"){
                // Longbow Scout: a long bright arrow trail that punches through in a spray of light.
                Tracer(From+FVector(0,0,30),To,FLinearColor(2.4f,2.6f,1.6f),9,.22f);
                for(int I=0;I<14;++I)FxEmit(FxStreak,To,Line*FMath::FRandRange(260.f,520.f)+Around(110,110),FLinearColor(2.2f,2.4f,1.4f),8,2,FMath::FRandRange(.2f,.4f),300,2,0,5);
                FxEmit(FxRing,Ground,FVector::ZeroVector,Leaf,50,260,.3f);
            }else if(Hero=="wc_vn_rifleman"){
                // Rifleman: muzzle flash and powder smoke, a hard tracer, and a heavy spark burst on the target.
                const FVector Mouth=Muzzle(E.source,E.origin,0);
                FxEmit(FxGlow,Mouth,FVector::ZeroVector,Fire,120,30,.1f);
                for(int I=0;I<8;++I)FxEmit(FxSmoke,Mouth,Line*FMath::FRandRange(40.f,160.f)+Around(40,50),FLinearColor(.5f,.5f,.5f,.5f),26,110,FMath::FRandRange(.6f,1.f),-25,2.5f);
                Tracer(Mouth,To,FLinearColor(3.f,2.6f,1.6f),6,.1f);
                for(int I=0;I<18;++I)FxEmit(FxStreak,To,-Line*120+Around(320,280),Warm,9,2,FMath::FRandRange(.2f,.45f),700,2,0,4);
                FxEmit(FxGlow,To,FVector::ZeroVector,Warm,190,50,.15f);
                FxFlash(Mouth,FLinearColor(1.f,.8f,.5f),12,.12f);CamShake=FMath::Max(CamShake,.75f);
            }else if(Hero=="wc_vn_dartblower"){
                // Dartblower: a thin green dart line, then a cloud of poison that hangs on the target.
                Tracer(From+FVector(0,0,25),To,Venom,4,.16f);
                for(int I=0;I<16;++I)FxEmit(FxSmoke,To+Around(25,25),Around(45,40),FLinearColor(.25f,.75f,.2f,.55f),40,120,FMath::FRandRange(1.1f,1.9f),-12,1.2f,I*.02f);
                for(int I=0;I<8;++I)FxEmit(FxGlow,To+Around(40,40),FVector(0,0,FMath::FRandRange(20.f,60.f)),Venom,10,2,FMath::FRandRange(.6f,1.2f));
            }else if(Hero=="wc_vn_moonblade"){
                // Moonblade: two crossing crescents of moonlight cut through the target.
                for(int Cut=0;Cut<2;++Cut)for(int I=0;I<9;++I){
                    const float A=(I-4)*.3f,Sign=Cut?1.f:-1.f;
                    const FVector At=To+Across*FMath::Sin(A)*70*Sign+FVector(0,0,(I-4)*14.f*Sign)-Line*(18*FMath::Cos(A));
                    FxEmit(FxStreak,At,(Across*Sign+FVector(0,0,.6f*Sign))*120,Moon,16-FMath::Abs(I-4)*3,2,.24f,0,3,Cut*.08f+I*.01f,5);
                }
                FxEmit(FxGlow,To,FVector::ZeroVector,Moon,150,40,.2f);FxFlash(To,FLinearColor(.6f,.65f,1.f),9,.2f);
            }else if(Hero=="wc_vn_foxclaw"){
                // Foxclaw: three parallel claw marks torn across the target and dust where it landed.
                for(int Claw=-1;Claw<=1;++Claw)for(int I=0;I<7;++I){
                    const float K=(I-3)/3.f;
                    FxEmit(FxStreak,To+Across*(K*55)+FVector(0,0,Claw*22-K*30),(Across-FVector(0,0,.55f))*150,FLinearColor(3.f,1.5f,.5f),13-FMath::Abs(I-3)*3,2,.22f,0,3,I*.012f,5);
                }
                for(int I=0;I<10;++I)FxEmit(FxSmoke,Ground+Around(25,5),Around(200,50),Dust,34,120,FMath::FRandRange(.4f,.8f),-15,3);
            }else if(Hero=="wc_vn_bearguard"&&First){
                // Bearguard: one wide sweep of the claws all the way round him.
                const FVector Centre=Position(E.origin)+FVector(0,0,70);
                for(int I=0;I<26;++I){
                    const float A=I/26.f*UE_TWO_PI;
                    const FVector Out(FMath::Cos(A),FMath::Sin(A),0);
                    FxEmit(FxStreak,Centre+Out*120,FVector(-Out.Y,Out.X,0)*260,FLinearColor(2.6f,2.f,1.2f),15,3,.22f,0,2,I*.006f,5);
                }
                FxEmit(FxRing,Centre-FVector(0,0,62),FVector::ZeroVector,Warm,90,520,.35f);
                for(int I=0;I<14;++I)FxEmit(FxSmoke,Centre-FVector(0,0,55)+Around(60,5),Around(280,50),Dust,40,140,FMath::FRandRange(.5f,.9f),-15,3);
                CamShake=FMath::Max(CamShake,.7f);
            }else if(Hero=="wc_vn_jinxer"&&First){
                // Jinxer: a purple hex pops on the target with rattling sparks and drifting feathers of smoke.
                FxEmit(FxRing,Ground,FVector::ZeroVector,Hex,40,300,.45f);
                FxEmit(FxGlow,To,FVector::ZeroVector,Hex,160,50,.25f);
                for(int I=0;I<14;++I)FxEmit(FxSmoke,To+Around(30,30),Around(70,90),FLinearColor(.45f,.15f,.6f,.6f),30,110,FMath::FRandRange(.7f,1.3f),-25,1.5f);
                for(int I=0;I<12;++I)FxEmit(FxStreak,To,Around(240,240),Hex,7,2,FMath::FRandRange(.2f,.4f),300,2,0,4);
                FxFlash(To,FLinearColor(.8f,.4f,1.f),8,.25f);
            }else if(Hero=="wc_vn_bonechanter"&&First){
                // Bonechanter: a sickly green chain snaps to the target, bursts, and motes of life drift back to him.
                Tracer(From+FVector(0,0,60),To,Bone,10,.3f);
                FxEmit(FxRing,Ground,FVector::ZeroVector,Bone,60,440,.45f);
                FxEmit(FxGlow,To,FVector::ZeroVector,Bone,190,60,.25f);
                for(int I=0;I<14;++I)FxEmit(FxGlow,To+Around(90,50),(From-To)/.7f+Around(40,40),Bone,14,4,.7f,0,0,.1f+I*.02f);
                FxFlash(To,FLinearColor(.5f,1.f,.4f),10,.3f);
            }else if(Hero=="wc_vn_treant_caller"&&E.effect==wc::Effect::Shield){
                // Treant Caller: bark and leaves whirl up around the ally he protects.
                FxEmit(FxRing,Ground,FVector::ZeroVector,Leaf,150,70,.5f);
                for(int I=0;I<16;++I){
                    const float A=I/16.f*UE_TWO_PI;
                    FxEmit(I%2?FxShard:FxGlow,Ground+FVector(FMath::Cos(A),FMath::Sin(A),0)*70,FVector(-FMath::Sin(A)*120,FMath::Cos(A)*120,FMath::FRandRange(120.f,220.f)),I%2?FLinearColor(.5f,.36f,.2f):Leaf,I%2?8.f:13.f,3,FMath::FRandRange(.6f,1.f),I%2?200.f:-10.f,.6f,I*.02f);
                }
                FxEmit(FxGlow,To,FVector::ZeroVector,Leaf*.6f,90,230,.5f);
            }else if(Hero=="wc_vn_ironwall"&&E.effect==wc::Effect::Shield){
                // Ironwall: the shields ring like a bell: a steel-blue wall of light and a shower of sparks.
                const FVector Centre=Position(E.origin)+FVector(0,0,8);
                FxEmit(FxRing,Centre,FVector::ZeroVector,Steel,60,300,.35f);
                FxEmit(FxRing,Centre,FVector::ZeroVector,Steel*.6f,140,150,.9f);
                FxEmit(FxGlow,Centre+FVector(0,0,80),FVector::ZeroVector,Steel,120,260,.4f);
                for(int I=0;I<14;++I)FxEmit(FxStreak,Centre+FVector(0,0,90),Around(260,260),Steel,8,2,FMath::FRandRange(.2f,.4f),600,2,0,4);
                FxFlash(Centre+FVector(0,0,90),FLinearColor(.6f,.8f,1.f),9,.25f);
            }else if(Hero=="wc_vn_ember_wisp"&&E.effect==wc::Effect::Shield){
                // Ember Wisp: a ring of small flames settles round the ally it shields.
                for(int I=0;I<14;++I){
                    const float A=I/14.f*UE_TWO_PI;
                    FxEmit(FxGlow,Ground+FVector(FMath::Cos(A),FMath::Sin(A),0)*75,FVector(0,0,FMath::FRandRange(70.f,150.f)),Fire,18,3,FMath::FRandRange(.6f,1.f),-20,0,I*.02f);
                }
                FxEmit(FxRing,Ground,FVector::ZeroVector,Fire,150,90,.5f);FxEmit(FxGlow,To,FVector::ZeroVector,Fire*.4f,90,220,.45f);
            }else if(Hero=="wc_vn_chapel_healer"&&E.effect==wc::Effect::Heal){
                // Chapel Healer: a column of warm light and rising golden motes on the healed ally.
                FxEmit(FxStreak,To+FVector(0,0,90),FVector(0,0,.01f),Golden*.7f,60,30,.45f,0,0,0,5);
                for(int I=0;I<12;++I)FxEmit(FxGlow,Ground+Around(45,20),FVector(0,0,FMath::FRandRange(100.f,190.f)),Golden,13,3,FMath::FRandRange(.6f,1.f),-20,0,I*.03f);
                FxEmit(FxRing,Ground,FVector::ZeroVector,Golden,60,220,.4f);
            }else if(Hero=="wc_vn_n_hollow_bellkeeper"&&First){
                // The Bellkeeper's toll: three slow bronze rings roll out across the stone and the whole yard shakes.
                const FVector Centre=Position(E.origin)+FVector(0,0,8);
                for(int Ring=0;Ring<3;++Ring)FxEmit(FxRing,Centre,FVector::ZeroVector,FLinearColor(2.6f,1.7f,.5f)*(1-Ring*.22f),80,1000,.7f,0,0,Ring*.14f);
                FxEmit(FxGlow,Centre+FVector(0,0,170),FVector::ZeroVector,FLinearColor(2.6f,1.8f,.6f),320,90,.3f);
                for(int I=0;I<20;++I)FxEmit(FxSmoke,Centre+Around(60,5),Around(520,40),Dust,50,170,FMath::FRandRange(.7f,1.1f),-12,2.4f);
                FxFlash(Centre+FVector(0,0,170),FLinearColor(1.f,.8f,.4f),18,.35f);CamShake=FMath::Max(CamShake,1.2f);
            }else if(Hero=="wc_vn_n_root_sentinel"&&First){
                // Root Sentinel: both clubs hit the ground. Dust, bark and stones jump and a ring runs out.
                const FVector Centre=Position(E.origin)+FVector(0,0,10);
                for(int I=0;I<24;++I)FxEmit(FxSmoke,Centre+Around(40,8),Around(380,60),Dust,46,170,FMath::FRandRange(.6f,1.1f),-12,2.6f);
                for(int I=0;I<12;++I)FxEmit(FxShard,Centre+Around(70,0)+FVector(0,0,8),Around(170,480),FLinearColor::White,FMath::FRandRange(8.f,16.f),5,FMath::FRandRange(.8f,1.3f),1200,.3f);
                FxEmit(FxRing,Centre,FVector::ZeroVector,FLinearColor(1.4f,1.8f,.8f),80,620,.45f);
                CamShake=FMath::Max(CamShake,.9f);
            }else if(Hero=="wc_vn_n_bog_toad"&&First){
                // Bog Toad: a glob of mud bursts and spatters.
                for(int I=0;I<16;++I)FxEmit(FxSmoke,Ground+Around(25,20),Around(190,150),FLinearColor(.16f,.11f,.05f,.8f),40,130,FMath::FRandRange(.5f,.9f),300,2.4f);
                for(int I=0;I<12;++I)FxEmit(FxShard,Ground+FVector(0,0,14),Around(240,360),FLinearColor(.35f,.25f,.12f),FMath::FRandRange(5.f,10.f),3,FMath::FRandRange(.6f,1.f),1100,.4f);
                FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(.6f,.45f,.2f),50,330,.35f);
            }else if(Hero=="wc_vn_n_spore_cap"&&E.effect==wc::Effect::Heal){
                // Spore Cap: pale green spores drift up round the monster it mends.
                for(int I=0;I<16;++I)FxEmit(FxGlow,Ground+Around(50,30),FVector(FMath::FRandRange(-20.f,20.f),0,FMath::FRandRange(60.f,140.f)),FLinearColor(.9f,2.2f,1.1f),11,3,FMath::FRandRange(.8f,1.4f),-10,0,I*.03f);
                FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(.7f,1.8f,.9f),60,200,.4f);
            }else if(Hero=="wc_vn_n_lantern_bulb"&&E.effect==wc::Effect::Shield){
                // Lantern Bulb: a warm ring of lamplight settles on the monster it shields.
                FxEmit(FxRing,Ground,FVector::ZeroVector,FLinearColor(2.6f,1.9f,.6f),150,80,.5f);
                FxEmit(FxGlow,To,FVector::ZeroVector,FLinearColor(2.6f,1.9f,.6f)*.5f,90,220,.45f);
            }else if(Hero=="wc_vn_blood_drummer"&&First){
                // Blood Drummer: each cast sends red rings out from the drum like a heartbeat.
                const FVector Centre=Position(E.origin)+FVector(0,0,8);
                for(int Beat=0;Beat<3;++Beat)FxEmit(FxRing,Centre,FVector::ZeroVector,Blood,60,420,.45f,0,0,Beat*.16f);
                FxEmit(FxGlow,Centre+FVector(0,0,110),FVector::ZeroVector,Blood,150,60,.2f);
            }
        }
    }
    // Earthbreaker's cracks stay in the stone for a moment, glowing faintly from within before they fade.
    for(int I=EarthCracks.Num()-1;I>=0;--I){
        const float Age=float(Elapsed-EarthCracks[I].At);
        if(Age>1.6f){EarthCracks.RemoveAtSwap(I);continue;}
        const float Grow=FMath::Min(1.f,Age/.14f),Fade=FMath::Clamp((1.6f-Age)/.6f,0.f,1.f);
        for(int Crack=0;Crack<9;++Crack){
            const float A=Crack*UE_TWO_PI/9+.2f;
            FVector At=EarthCracks[I].Where+FVector(FMath::Cos(A),FMath::Sin(A),0)*30;
            for(int Piece=0;Piece<5;++Piece){
                const float Bend=A+((Crack*7+Piece*3)%5-2)*.24f;
                const FVector Next=At+FVector(FMath::Cos(Bend),FMath::Sin(Bend),0)*56*Grow;
                CueLine(At,Next,Dark,(8-Piece*1.4f)*Fade);
                FxEmit(FxStreak,(At+Next)*.5+FVector(0,0,2),(Next-At).GetSafeNormal()*.01,FLinearColor(2.2f,.9f,.2f)*Fade*(1-Age/1.6f),5,0,0,0,0,0,13);
                At=Next;
            }
        }
    }
    for(const auto& Action:Combat->VisualActions()){
        if(Action.basicAttack)continue;
        if(Action.mechanic==wc::AbilityMechanic::StationaryGrove&&Action.released){
            // Grove Druid: grass and flowers stand on every tile of an active grove, with fireflies drifting up.
            const float Grown=FMath::Clamp((Combat->CurrentTick()+Smooth-Action.releaseTick)*TickSeconds/.7f,0.f,1.f);
            for(int Row=Action.center.row-Action.radius;Row<=Action.center.row+Action.radius;++Row)
                for(int Column=Action.center.column-Action.radius;Column<=Action.center.column+Action.radius;++Column){
                    if(Row<0||Row>7||Column<0||Column>7)continue;
                    const FVector Tile=Position({Column,Row})+FVector(0,0,9);
                    FxEmit(FxGlow,Tile+FVector(0,0,3),FVector::ZeroVector,Leaf*(.10f+.03f*FMath::Sin(Time*2+Row+Column)),230,230,0);
                    for(int Tuft=0;Tuft<5;++Tuft){
                        const float A=Tuft*1.7f+Row*2.1f+Column*1.3f;
                        const FVector Root=Tile+FVector(FMath::Cos(A)*58,FMath::Sin(A)*58,0);
                        const float Sway=FMath::Sin(Time*1.6f+A)*4;
                        CueLine(Root,Root+FVector(Sway,0,26*Grown),FLinearColor(.25f,.62f,.22f),2.5f);
                        if(Tuft%2==0)FxEmit(FxGlow,Root+FVector(Sway,0,29*Grown),FVector::ZeroVector,Tuft?FLinearColor(2.4f,.8f,1.4f):FLinearColor(2.4f,2.f,.6f),13*Grown,13,0);
                    }
                    if(!Held&&FMath::FRand()<.05f)FxEmit(FxGlow,Tile+Around(80,10),FVector(FMath::FRandRange(-12.f,12.f),0,FMath::FRandRange(35.f,70.f)),Leaf,9,2,FMath::FRandRange(1.f,1.8f));
                }
        }else if(Action.mechanic==wc::AbilityMechanic::CrossingBeams&&!Action.released){
            // Prism Scholar: the crystals gather light while Crossfire charges.
            for(int Crystal=0;Crystal<3;++Crystal){
                const FVector At=Muzzle(Action.source,Action.origin,Crystal);
                FxEmit(FxGlow,At,FVector::ZeroVector,Light*(.8f+.3f*FMath::Sin(Time*16+Crystal)),70,70,0);
                if(!Held&&FMath::FRand()<.4f){const FVector Out=Around(70,40);FxEmit(FxStreak,At+Out,-Out*3,Light,6,2,.3f,0,0,0,3);}
            }
        }
    }
    // A chain: a bright line from each target to the next one it jumped to.
    for(const auto& Chain:Chains)for(int I=0;I+1<Chain.Value.Num();++I)CueLine(Chain.Value[I],Chain.Value[I+1],FLinearColor(.75f,.9f,1.f),5);
    if(Fallen>FeedbackFallen){
        // A fallen piece goes down in a cloud of dust.
        for(const auto& U:Combat->Units())if(U.health<=0&&DefeatAge(U)>=0&&DefeatAge(U)<.2f){
            const FVector At=Where(U.id,U.cell,30);
            for(int I=0;I<12;++I)FxEmit(FxSmoke,At+Around(25,20),Around(120,90),Dust,40,130,FMath::FRandRange(.6f,1.f),-15,2);
        }
        PlayCue(TEXT("fall"),.5f);
    }
    FeedbackFallen=Fallen;
    if(SkillSound)PlayCue(TEXT("skill"),.5f);else if(HitSound)PlayCue(TEXT("hit"),.35f);
    FeedbackTick=Combat->CurrentTick();
}

// ---------------------------------------------------------------------------------------------------------------
// Handmade effect pieces. Modelled props (see tools/blender/build_effect_props.py) are thrown, spun, bounced and
// scaled like particles, but each one is a real mesh with its own painted colour. Cosmetic only.
void AWCVNextLab::PropEmit(const FString& Mesh,FVector P,FVector V,FQuat R,FVector Spin,float Scale0,float Scale1,float Life,float Gravity,bool Bounce,float Delay)
{
    if(Props.Num()>=700)return;
    FProp New;New.Mesh=Mesh;New.P=P;New.V=V;New.R=R;New.Spin=Spin;New.Scale0=Scale0;New.Scale1=Scale1;New.Life=Life;New.Gravity=Gravity;New.Bounce=Bounce;New.Age=-Delay;
    Props.Add(New);
}
void AWCVNextLab::TickProps(float Dt)
{
    TMap<FString,TArray<FTransform>> Placed;
    for(int I=Props.Num()-1;I>=0;--I){
        auto& P=Props[I];
        const bool Instant=P.Life<=0;
        float T=0;
        if(!Instant){
            P.Age+=Dt;
            if(P.Age>=P.Life){Props.RemoveAtSwap(I,1,EAllowShrinking::No);continue;}
            if(P.Age<0)continue;
            P.V.Z-=P.Gravity*Dt;P.P+=P.V*Dt;
            if(P.Bounce&&P.P.Z<10&&P.V.Z<0){P.P.Z=10;P.V=FVector(P.V.X*.45,P.V.Y*.45,-P.V.Z*.3);P.Spin*=.4;}
            const FVector Turn=P.Spin*Dt;
            P.R=(FQuat(FRotator(Turn.Y,Turn.Z,Turn.X))*P.R).GetNormalized();
            T=P.Age/P.Life;
        }
        // Pieces shrink away over their last fifth instead of popping out.
        const float Scale=FMath::Lerp(P.Scale0,P.Scale1,T)*(T>.8f?(1-T)/.2f:1.f);
        Placed.FindOrAdd(P.Mesh).Add(FTransform(P.R,P.P,FVector(FMath::Max(.001f,Scale))));
        if(Instant)Props.RemoveAtSwap(I,1,EAllowShrinking::No);
    }
    for(auto& Batch:PropBatches)if(!Placed.Contains(Batch.Key)&&Batch.Value->GetInstanceCount()>0){Batch.Value->ClearInstances();Batch.Value->MarkRenderStateDirty();}
    for(auto& Entry:Placed){
        UInstancedStaticMeshComponent* Batch=PropBatches.FindRef(Entry.Key);
        if(!Batch){
            // A short name is a prop from the effects folder; a full path is any other mesh, such as a hero's own item.
            const FString Path=Entry.Key.StartsWith(TEXT("/"))?Entry.Key+TEXT(".")+FPaths::GetBaseFilename(Entry.Key):
                FString::Printf(TEXT("/Game/WonderChess/VNext/Effects/Props/%s/SM_%s.SM_%s"),*Entry.Key,*Entry.Key,*Entry.Key);
            auto* Model=LoadObject<UStaticMesh>(nullptr,*Path);
            if(!Model){UE_LOG(LogTemp,Warning,TEXT("WC_PROP_MISSING %s"),*Path);Model=ProxyMeshes.FindChecked(TEXT("Cube"));}
            auto* Host=SceneActor();
            Batch=NewObject<UInstancedStaticMeshComponent>(Host);
            Host->AddInstanceComponent(Batch);Batch->SetupAttachment(Host->GetRootComponent());
            Batch->SetStaticMesh(Model);Batch->SetMobility(EComponentMobility::Movable);Batch->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Batch->SetCastShadow(false);Batch->RegisterComponent();
            PropBatches.Add(Entry.Key,Batch);
        }
        Batch->ClearInstances();
        Batch->AddInstances(Entry.Value,false,true,false);
        Batch->MarkRenderStateDirty();
    }
}
const AWCVNextLab::FShotLook* AWCVNextLab::ShotLook(const std::string& Id,bool Basic)
{
    const FString Key=UTF8_TO_TCHAR(Id.c_str());
    auto* Found=ShotLooks.Find(Key);
    if(!Found){
        TPair<FShotLook,FShotLook> Pair;
        const TSharedPtr<FJsonObject> Config=UWCHeroPresentationComponent::Config(Key);
        const TSharedPtr<FJsonObject>* Shots=nullptr;
        if(Config&&Config->TryGetObjectField(TEXT("shots"),Shots))for(int Kind=0;Kind<2;++Kind){
            const TSharedPtr<FJsonObject>* Entry=nullptr;
            if(!(*Shots)->TryGetObjectField(Kind?TEXT("skill"):TEXT("basic"),Entry))continue;
            FShotLook& Look=Kind?Pair.Value:Pair.Key;
            Look.Mesh=(*Entry)->GetStringField(TEXT("mesh"));
            (*Entry)->TryGetStringField(TEXT("trail"),Look.Trail);(*Entry)->TryGetStringField(TEXT("impact"),Look.Impact);
            (*Entry)->TryGetStringField(TEXT("from_bone"),Look.FromBone);
            double Number=0;
            if((*Entry)->TryGetNumberField(TEXT("scale"),Number))Look.Scale=Number;
            if((*Entry)->TryGetNumberField(TEXT("arc"),Number))Look.Arc=Number;
            if((*Entry)->TryGetNumberField(TEXT("impact_scale"),Number))Look.ImpactScale=Number;
            if((*Entry)->TryGetNumberField(TEXT("lead_ms"),Number))Look.LeadMs=Number;
            if((*Entry)->TryGetNumberField(TEXT("hide_item"),Number))Look.HideItem=int(Number);
            if((*Entry)->TryGetNumberField(TEXT("from_item"),Number))Look.FromItem=int(Number);
            if((*Entry)->TryGetNumberField(TEXT("from_forward"),Number))Look.FromForward=Number;
            if((*Entry)->TryGetNumberField(TEXT("from_up"),Number))Look.FromUp=Number;
            if((*Entry)->TryGetNumberField(TEXT("from_side"),Number))Look.FromSide=Number;
            if((*Entry)->TryGetNumberField(TEXT("grow"),Number))Look.Grow=Number;
            (*Entry)->TryGetStringField(TEXT("launch"),Look.Launch);
            const TArray<TSharedPtr<FJsonValue>>* Turn=nullptr;
            if((*Entry)->TryGetArrayField(TEXT("spin"),Turn)&&Turn->Num()==3)Look.Spin=FVector((*Turn)[0]->AsNumber(),(*Turn)[1]->AsNumber(),(*Turn)[2]->AsNumber());
            Look.Valid=!Look.Mesh.IsEmpty();
        }
        Found=&ShotLooks.Add(Key,Pair);
    }
    const FShotLook& Look=Basic?Found->Key:Found->Value;
    return Look.Valid?&Look:nullptr;
}
const AWCVNextLab::FShotLook* AWCVNextLab::MeleeLook(const std::string& Id)
{
    const FString Key=UTF8_TO_TCHAR(Id.c_str());
    auto* Found=MeleeLooks.Find(Key);
    if(!Found){
        FShotLook Look;
        const TSharedPtr<FJsonObject> Config=UWCHeroPresentationComponent::Config(Key);
        const TSharedPtr<FJsonObject>* Shots=nullptr;const TSharedPtr<FJsonObject>* Entry=nullptr;
        if(Config&&Config->TryGetObjectField(TEXT("shots"),Shots)&&(*Shots)->TryGetObjectField(TEXT("melee"),Entry)){
            (*Entry)->TryGetStringField(TEXT("impact"),Look.Impact);
            double Number=0;
            if((*Entry)->TryGetNumberField(TEXT("item"),Number))Look.FromItem=int(Number);
            if((*Entry)->TryGetNumberField(TEXT("width"),Number))Look.Scale=Number;
            if((*Entry)->TryGetNumberField(TEXT("impact_scale"),Number))Look.ImpactScale=Number;
            const TArray<TSharedPtr<FJsonValue>>* Tint=nullptr;
            if((*Entry)->TryGetArrayField(TEXT("color"),Tint)&&Tint->Num()==3)Look.Spin=FVector((*Tint)[0]->AsNumber(),(*Tint)[1]->AsNumber(),(*Tint)[2]->AsNumber());
            Look.Valid=true;
        }
        Found=&MeleeLooks.Add(Key,Look);
    }
    return Found->Valid?Found:nullptr;
}
void AWCVNextLab::ShotImpact(const FShotLook& Look,FVector At,FVector Ground,FVector Line)
{
    const float S=Look.ImpactScale;
    const auto Any=[]{return FQuat(FRotator(FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f),FMath::FRandRange(0.f,360.f)));};
    const auto Out=[](float Speed,float Up){
        const float A=FMath::FRandRange(0.f,UE_TWO_PI);
        return FVector(FMath::Cos(A),FMath::Sin(A),0)*Speed*FMath::FRandRange(.5f,1.f)+FVector(0,0,Up*FMath::FRandRange(.5f,1.f));
    };
    if(Look.Impact==TEXT("bomb")){
        // The blast as shapes: a spiked flash that snaps out and is gone, smoke balls that swell and drift up,
        // torn casing thrown wide and bouncing, and a burn left on the stone.
        PropEmit(TEXT("BlastStar"),At,FVector::ZeroVector,Any(),FVector(0,0,400),.25f*S,1.5f*S,.2f);
        PropEmit(TEXT("BlastStar"),At,FVector::ZeroVector,Any(),FVector(0,0,-300),.2f*S,1.f*S,.14f,0,false,.05f);
        for(int I=0;I<5;++I)PropEmit(TEXT("SmokeBall"),At+Out(30*S,20),Out(70*S,120),Any(),FVector(20,30,40),.35f*S,(1.1f+I*.12f)*S,FMath::FRandRange(.7f,1.1f),-60,false,.06f+I*.03f);
        for(int I=0;I<int(9*S);++I)PropEmit(I%3?TEXT("ShardRed"):TEXT("ShardIron"),At,Out(420,520),Any(),
            FVector(FMath::FRandRange(-900.f,900.f),FMath::FRandRange(-900.f,900.f),FMath::FRandRange(-900.f,900.f)),1.4f,1.4f,FMath::FRandRange(.9f,1.4f),1500,true);
        PropEmit(TEXT("Scorch"),FVector(Ground.X,Ground.Y,Ground.Z+1),FVector::ZeroVector,FQuat(FRotator(0,FMath::FRandRange(0.f,360.f),0)),FVector::ZeroVector,.9f*S,S,3.5f);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(3.f,1.6f,.5f),190*S,60*S,.16f);
        FxFlash(At,FLinearColor(1.f,.6f,.25f),12*S,.25f);CamShake=FMath::Max(CamShake,.6f*S);
        return;
    }
    // Throws Count pieces of one model outward from the point of impact.
    const auto Burst=[&](const TCHAR* Mesh,int Count,float Speed,float Up,float Size,float Life,float Gravity,bool Bounce){
        for(int I=0;I<Count;++I)PropEmit(Mesh,At,Out(Speed,Up),Any(),FVector(FMath::FRandRange(-700.f,700.f),FMath::FRandRange(-700.f,700.f),FMath::FRandRange(-700.f,700.f)),
            Size*S,Size*S,FMath::FRandRange(Life*.7f,Life),Gravity,Bounce);
    };
    if(Look.Impact==TEXT("leaf")){
        Burst(TEXT("LeafScrap"),8,170,200,1.f,1.2f,300,false);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(.6f,2.4f,.5f),110*S,30*S,.18f);
    }else if(Look.Impact==TEXT("sparks")){
        Burst(TEXT("ShardIron"),4,300,320,.6f,.7f,1500,true);
        for(int I=0;I<9;++I)FxEmit(3,At,-Line*120+Out(300,260),FLinearColor(2.6f,1.7f,.7f),7,2,FMath::FRandRange(.18f,.35f),600,2,0,4);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(2.6f,1.7f,.7f),100*S,30*S,.12f);
    }else if(Look.Impact==TEXT("crystal")){
        Burst(TEXT("CrystalSplinter"),9,330,320,1.f,.75f,1000,true);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(1.2f,2.2f,3.f),150*S,40*S,.16f);FxFlash(At,FLinearColor(.6f,.9f,1.f),7,.18f);
    }else if(Look.Impact==TEXT("splash")){
        Burst(TEXT("Droplet"),14,260,400,1.f,.75f,1400,false);
        FxEmit(2,Ground,FVector::ZeroVector,FLinearColor(.35f,.9f,2.2f),40,300*S,.4f);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(.35f,.9f,2.2f),120*S,40*S,.14f);
    }else if(Look.Impact==TEXT("soul")){
        for(int I=0;I<5;++I)PropEmit(TEXT("SoulWisp"),At+Out(20,10),Out(60,180),FRotationMatrix::MakeFromY(FVector(0,0,1)).ToQuat(),FVector(0,0,200),.32f*S,.12f*S,FMath::FRandRange(.5f,.8f),-120,false,I*.03f);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(.6f,2.6f,.9f),140*S,40*S,.2f);
    }else if(Look.Impact==TEXT("flame")){
        for(int I=0;I<7;++I)PropEmit(TEXT("FlameDrop"),At+Out(14,10),Out(110,260),FRotationMatrix::MakeFromY(FVector(0,0,-1)).ToQuat(),FVector::ZeroVector,.7f*S,.2f*S,FMath::FRandRange(.35f,.55f),-220,false,I*.02f);
        Burst(TEXT("Ember"),8,220,300,1.f,.6f,700,false);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(3.f,1.4f,.35f),150*S,40*S,.16f);FxFlash(At,FLinearColor(1.f,.6f,.25f),8,.2f);
    }else if(Look.Impact==TEXT("thump")){
        const FQuat Face=FRotationMatrix::MakeFromY(Line).ToQuat();
        for(int I=0;I<3;++I)PropEmit(TEXT("SoundRing"),At,FVector::ZeroVector,Face,FVector::ZeroVector,1.2f*S,(2.4f+I*.7f)*S,.26f,0,false,I*.05f);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(2.6f,.3f,.2f),110*S,30*S,.14f);
    }else if(Look.Impact==TEXT("rock")){
        Burst(TEXT("RockChunk"),8,320,440,1.f,1.1f,1500,true);
        for(int I=0;I<4;++I)PropEmit(TEXT("SmokeBall"),At+Out(24,10),Out(60,90),Any(),FVector(20,30,40),.25f*S,(.8f+I*.1f)*S,FMath::FRandRange(.6f,.9f),-40,false,I*.03f);
        FxEmit(2,Ground,FVector::ZeroVector,FLinearColor(1.8f,1.5f,1.1f),50,320*S,.3f);CamShake=FMath::Max(CamShake,.5f*S);
    }else if(Look.Impact==TEXT("stick")){
        // The shaft stays planted in the target for a moment.
        PropEmit(Look.Mesh,At-Line*14,FVector::ZeroVector,FRotationMatrix::MakeFromY(Line).ToQuat(),FVector::ZeroVector,Look.Scale,Look.Scale,.9f);
        Burst(TEXT("Splinter"),4,200,260,1.f,.7f,1300,true);
    }else if(Look.Impact==TEXT("hammer")){
        // A hammer blow: a ring of light slams out along the ground, cracks open in the stone, chips and sparks fly, dust rolls.
        PropEmit(TEXT("ShockRing"),Ground+FVector(0,0,4),FVector::ZeroVector,FQuat::Identity,FVector::ZeroVector,.5f*S,4.2f*S,.3f);
        PropEmit(TEXT("ShockRing"),Ground+FVector(0,0,4),FVector::ZeroVector,FQuat::Identity,FVector::ZeroVector,.3f*S,2.8f*S,.42f,0,false,.06f);
        PropEmit(TEXT("CrackMark"),Ground+FVector(0,0,1.5f),FVector::ZeroVector,FQuat(FRotator(0,FMath::FRandRange(0.f,360.f),0)),FVector::ZeroVector,.9f*S,1.f*S,2.6f);
        Burst(TEXT("RockChunk"),7,300,420,.9f,1.f,1500,true);
        Burst(TEXT("ShardIron"),5,360,380,.6f,.6f,1500,true);
        for(int I=0;I<5;++I)PropEmit(TEXT("SmokeBall"),Ground+Out(26,6),Out(110,50),Any(),FVector(20,30,40),.22f*S,(.7f+I*.08f)*S,FMath::FRandRange(.5f,.8f),-30,false,I*.03f);
        for(int I=0;I<10;++I)FxEmit(3,At,Out(300,330),FLinearColor(2.6f,1.9f,.9f),8,2,FMath::FRandRange(.2f,.4f),700,2,0,4);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(2.6f,2.1f,1.4f),170*S,50*S,.14f);
        FxFlash(At,FLinearColor(1.f,.85f,.6f),9*S,.2f);CamShake=FMath::Max(CamShake,.55f*S);
    }else if(Look.Impact==TEXT("hex")){
        Burst(TEXT("BoneChip"),6,230,320,1.f,.8f,1300,true);
        FxEmit(2,Ground,FVector::ZeroVector,FLinearColor(1.9f,.6f,2.6f),40,240*S,.35f);
        FxEmit(0,At,FVector::ZeroVector,FLinearColor(1.9f,.6f,2.6f),130*S,40*S,.18f);
    }
}
