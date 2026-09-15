#include "WCVNextLab.h"
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
            if(U.state==wc::ActionState::Stunned){
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
            if(U.shield>0){
                CueRing(P,78,Shield,5);CueRing(P+FVector(0,0,45),63,Shield,4);
                Mark(TEXT("active_shield"));
            }
            for(const auto& Modifier:U.modifiers){
                const float Sign=Modifier.magnitude>0?1.f:-1.f;
                const FVector C=P+FVector(65,0,55);
                CueLine(C+FVector(-12,0,-12*Sign),C+FVector(0,0,12*Sign),Sign>0?Heal:Stun,6);
                CueLine(C+FVector(12,0,-12*Sign),C+FVector(0,0,12*Sign),Sign>0?Heal:Stun,6);
                Mark(TEXT("stat_modifier"));
            }
        }
        for(const auto& Action:Combat->VisualActions()){
            const FVector From=Position(Action.origin)+FVector(0,0,75);
            const FVector To=At(Action.target,Action.center);
            const auto& Def=Catalog.Definition(Action.definition,Action.neutral);
            const FLinearColor Color=Action.basicAttack?(Def.ability.mechanic==wc::AbilityMechanic::Standard?Shot:SkillColor(Def.ability.mechanic)):SkillColor(Action.mechanic);
            const float Until=(Action.releaseTick-Combat->CurrentTick())*Catalog.rules.tickMs/1000.f;
            if(Action.basicAttack){
                if(Action.released){
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
                    Mark(TEXT("ranged_projectile"));
                }else if(Def.projectileTravelMs>0){
                    CueRing(From,22+14*FMath::Clamp(1-Until/.15f,0.f,1.f),Shot,4);
                    Mark(TEXT("ranged_windup"));
                }else{
                    const FVector Direction=(To-From).GetSafeNormal2D();
                    CueRing(From+Direction*45,55,Strike,7,1.8f,FMath::Atan2(Direction.Y,Direction.X)-.9f);
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
                for(int I=0;I<4;++I)CueLine(Corners[I],Corners[(I+1)%4],Heal,5);
                CueRing(Position(Action.center)+FVector(0,0,24),45+FMath::Fmod(Time*110,130.),Heal,4);
                Mark(TEXT("root_grove"));
            }else if(Action.mechanic==wc::AbilityMechanic::CrossingBeams){
                for(const auto& Cell:Action.cells){
                    const FVector P=Position(Cell)+FVector(0,0,30);
                    const bool AlongRow=Action.cells.front().row==Action.cells.back().row;
                    const FVector Axis=AlongRow?FVector(1,0,0):FVector(0,1,0);
                    CueLine(P-Axis*60,P+Axis*60,Prism,Action.released?7:4);
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
            const auto& E=*It;
            const float Age=(Combat->CurrentTick()-E.tick)*Catalog.rules.tickMs/1000.f;
            if(Age>.7f)break;
            const auto* Recipient=Find(E.target);
            const FVector From=Position(E.origin)+FVector(0,0,75),To=At(E.target,E.cell);
            const float Life=FMath::Max(.05f,1-Age/.7f);
            if(E.effect==wc::Effect::Heal&&E.resolved>0&&Recipient&&Recipient->health>0){
                const FVector P=To+FVector(80,0,25+Age*75);
                CueLine(P-FVector(15,0,0),P+FVector(15,0,0),Heal,8);
                CueLine(P-FVector(0,0,15),P+FVector(0,0,15),Heal,8);
                CueText(P+FVector(45,0,0),FString::Printf(TEXT("+%.0f"),E.resolved/100.),Heal,ArtSlice?32:25);
                Mark(TEXT("healing_plus"));
            }else if(E.effect==wc::Effect::Damage&&E.resolved>0){
                if(Age<.3f){
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
                if(E.prevented>0&&E.guardedBy){
                    const FVector Guard=At(E.guardedBy,E.origin);
                    CueLine(Guard,To,Strike,5*Life);
                    const FVector Incoming=(From-To).GetSafeNormal2D();
                    CueRing(To,85,Strike,7*Life,2.4f,Storybook?FMath::Atan2(Incoming.Y,Incoming.X)-1.2f:Time);
                    Mark(TEXT("bellback_guard"));
                }
            }else if(E.effect==wc::Effect::Dash&&Age<.4f){
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
    UpdatePlacementCue();
    for(int I=CueMeshUsed;I<CueMeshes.Num();++I)CueMeshes[I]->SetVisibility(false);
    for(int I=CueTextUsed;I<CueTexts.Num();++I)CueTexts[I]->SetVisibility(false);
    PeakCueMeshes=FMath::Max(PeakCueMeshes,CueMeshUsed);PeakCueTexts=FMath::Max(PeakCueTexts,CueTextUsed);
}
