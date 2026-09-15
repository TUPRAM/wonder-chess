#include "WCVNextLab.h"
#include "WCVNextArtStyle.h"
#include "Simulation/WonderSaveFile.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Notifications/SProgressBar.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SWrapBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SNullWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"
#include <algorithm>
#include <filesystem>

namespace
{
FString S(const std::string& Value) { return UTF8_TO_TCHAR(Value.c_str()); }
FText T(const FString& Value) { return FText::FromString(Value); }
const FLinearColor Ink(.018f,.032f,.042f,.98f), Paper(.89f,.92f,.85f), Gold(.98f,.75f,.34f);
wc::Id PublicIdentity(const std::vector<wc::PublicSeat>& Seats)
{
    wc::Id Hash=1469598103934665603ULL;
    const auto Add=[&](wc::Id Value){Hash^=Value;Hash*=1099511628211ULL;};
    for(const auto& Seat:Seats){
        Add(Seat.id);Add(Seat.health);Add(Seat.level);Add(Seat.placement);Add(Seat.wins);Add(Seat.ready);
        Add(Seat.deployment.size());
        for(const auto& Unit:Seat.deployment){Add(Unit.id);Add(Unit.definition);Add(Unit.star);Add(Unit.cell.column);Add(Unit.cell.row);Add(int(Unit.facing));Add(Unit.relic+1);}
    }
    return Hash;
}
const TCHAR* PhaseName(wc::Phase Phase)
{
    switch(Phase){case wc::Phase::Preparation:return TEXT("PREPARATION");case wc::Phase::Combat:return TEXT("COMBAT");
    case wc::Phase::Settlement:return TEXT("RECAP");case wc::Phase::Finished:return TEXT("RESULTS");default:return TEXT("ABORTED");}
}
class SWCSoloBoard : public SBorder
{
public:
    SLATE_BEGIN_ARGS(SWCSoloBoard) {} SLATE_ARGUMENT(TFunction<void()>, Click)
        SLATE_ARGUMENT(TFunction<FReply(const FKeyEvent&)>, Key) SLATE_END_ARGS()
    void Construct(const FArguments& Args)
    {
        Click=Args._Click;Key=Args._Key;
        SBorder::Construct(SBorder::FArguments().BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")))
            .BorderBackgroundColor(FLinearColor::Transparent));
    }
    virtual bool SupportsKeyboardFocus() const override { return true; }
    virtual FReply OnMouseButtonDown(const FGeometry&,const FPointerEvent& Event) override
    {
        if(Event.GetEffectingButton()!=EKeys::LeftMouseButton)return FReply::Unhandled();
        if(Click)Click();return FReply::Handled().SetUserFocus(AsShared(),EFocusCause::Mouse);
    }
    virtual FReply OnKeyDown(const FGeometry&,const FKeyEvent& Event) override
    { return Key?Key(Event):FReply::Unhandled(); }
private:
    TFunction<void()> Click;TFunction<FReply(const FKeyEvent&)> Key;
};
class SWCSoloModal : public SBorder
{
public:
    SLATE_BEGIN_ARGS(SWCSoloModal) {} SLATE_ARGUMENT(TFunction<bool()>,Active)
        SLATE_DEFAULT_SLOT(FArguments,Content) SLATE_END_ARGS()
    void Construct(const FArguments& Args)
    {
        Active=Args._Active;
        SetCanTick(true);
        SBorder::Construct(SBorder::FArguments().BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")))
            .BorderBackgroundColor(FLinearColor(.024f,.034f,.025f,.84f)).HAlign(HAlign_Center).VAlign(VAlign_Center)
            [Args._Content.Widget]);
    }
    void SynchronizeEnabledState() {SetEnabled(Active());}
    virtual bool SupportsKeyboardFocus() const override {return true;}
    virtual void Tick(const FGeometry&,double,float) override
    {
        if(Active()&&!HasKeyboardFocus()&&!HasFocusedDescendants()){
            FSlateApplication::Get().SetKeyboardFocus(AsShared(),EFocusCause::SetDirectly);
            int Visible=0,Enabled=0;
            if(const auto Parent=GetParentWidget())if(auto* Children=Parent->GetChildren())for(int Index=0;Index<Children->Num();++Index){
                const auto Child=Children->GetChildAt(Index);
                if(Child->GetTag().ToString().StartsWith(TEXT("WCModal."))){Visible+=Child->GetVisibility().IsVisible();Enabled+=Child->IsEnabled();}
            }
            UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_MODAL_FOCUS tag=%s owns_focus=%d visible_modals=%d enabled_modals=%d"),
                *GetTag().ToString(),HasKeyboardFocus(),Visible,Enabled);
            if(Visible!=1||Enabled!=1)UE_LOG(LogTemp,Error,TEXT("WC_STORYBOOK_MODAL_NONEXCLUSIVE"));
        }
    }
private:
    TFunction<bool()> Active;
};
class SWCSoloModalHost : public SOverlay
{
public:
    void Construct(const SOverlay::FArguments& Args) {SOverlay::Construct(Args);SetCanTick(true);}
    virtual void Tick(const FGeometry&,double,float) override
    {
        // Slate skips non-visibility attribute updates on collapsed children. Synchronize
        // these real enabled states from the host, including the state with no open modal.
        FChildren* ModalChildren=GetChildren();
        for(int Index=0;Index<ModalChildren->Num();++Index){
            const auto Child=ModalChildren->GetChildAt(Index);
            if(Child->GetTag().ToString().StartsWith(TEXT("WCModal.")))
                StaticCastSharedRef<SWCSoloModal>(Child)->SynchronizeEnabledState();
        }
    }
};
}

const wc::Combat* AWCVNextLab::CurrentCombat() const
{
    if(!SoloMode)return Fight.get();
    if(!SoloMatch||SoloMatch->CurrentPhase()==wc::Phase::Preparation)return nullptr;
    for(const auto& E:SoloMatch->Encounters())
        if(E.pairing.a==ViewedSeat || (E.kind==wc::EncounterKind::Pvp&&E.pairing.b==ViewedSeat))return &E.combat;
    return nullptr;
}

void AWCVNextLab::StartSolo()
{
    if(!LoadError.IsEmpty()||!Catalog.Validate().empty()){Message=TEXT("Cannot start: the requested content is invalid.");return;}
    ClearUpgradePresentation();
    SoloMatch=std::make_unique<wc::Match>(Catalog,uint64(Seed),1,false);
    SoloPaused=false;AwaitingSaveDecision=false;ViewedSeat=0;Selected=0;Accumulator=0;LastSoloRound=-1;LastSoloRecord=0;
    LastSoloPhase=wc::Phase::Aborted;LastSoloRevision=~wc::Id(0);SoloRecap=TEXT("Recruit a creature, select its bench card, then click a legal cell on the near half. Scout before changing your plan.");
    SavePath=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/
        (Catalog.rules.nearestReachableTarget?TEXT("WonderVNext/Solo/combat-clarity-preparation.wcsave"):
        Catalog.balanceVersion.find("+mana100_hit20_v1")!=std::string::npos?TEXT("WonderVNext/Solo/mana20-preparation.wcsave"):
        Catalog.balanceVersion.find("+mana100_v1")!=std::string::npos?TEXT("WonderVNext/Solo/mana100-preparation.wcsave"):TEXT("WonderVNext/Solo/preparation.wcsave")));
    FParse::Value(FCommandLine::Get(),TEXT("WCSavePath="),SavePath);
    Message=TEXT("One captain and seven bots. Independent shops. All battles use the same combat rules.");
    LastSoloRound=SoloMatch->Round();LastSoloPhase=SoloMatch->CurrentPhase();
    if(IFileManager::Get().FileExists(*SavePath)||IFileManager::Get().FileExists(*(SavePath+TEXT(".previous")))){
        SoloPaused=true;AwaitingSaveDecision=true;
        Message=TEXT("A saved preparation is available. Load it to continue, or choose New tournament. Your save has not been overwritten.");
    }
    SyncSoloFormation();
}

void AWCVNextLab::SyncSoloFormation()
{
    if(!SoloMatch)return;
    Formation[0].clear();Formation[1].clear();
    const auto Public=SoloMatch->PublicSeats();
    if(ViewedSeat<0||ViewedSeat>=int(Public.size()))ViewedSeat=0;
    Formation[0]=Public[ViewedSeat].deployment;
    for(const auto& Pair:SoloMatch->Pairings()){
        int Other=Pair.a==ViewedSeat?Pair.b:Pair.kind==wc::EncounterKind::Pvp&&Pair.b==ViewedSeat?Pair.a:-1;
        if(Other>=0&&Other<int(Public.size())){Formation[1]=Public[Other].deployment;break;}
    }
    PreparationDirty=true;
}

void AWCVNextLab::NewSolo()
{
    Seed=Seed==MAX_int32?1:Seed+1;StartSolo();AwaitingSaveDecision=false;SoloPaused=false;SaveSolo();
}

bool AWCVNextLab::SoloCommand(wc::Command Command)
{
    if(!SoloMatch)return false;
    if(AwaitingSaveDecision){Message=TEXT("Load the saved preparation or choose New tournament before giving orders.");return false;}
    if(ViewedSeat!=0){Message=TEXT("Scouting is read-only. Return to your board before giving an order.");return false;}
    const auto& Captain=SoloMatch->Seats()[0];
    const int GoldBefore=Captain.gold, LevelBefore=Captain.level;
    const auto RosterBefore=Command.type==wc::CommandType::Buy?Captain.roster:std::vector<wc::OwnedUnit>();
    FString Creature;int StarBefore=0, Definition=-1, MergedStar=0;
    for(const auto& Unit:Captain.roster)if(Unit.id==Command.unit){Creature=S(Catalog.units[Unit.definition].displayName);StarBefore=Unit.star;Definition=Unit.definition;break;}
    if(Command.type==wc::CommandType::Buy&&Command.slot>=0&&Command.slot<int(Captain.shop.size())){
        Definition=Captain.shop[Command.slot];if(Definition>=0)Creature=S(Catalog.units[Definition].displayName);
        const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Command);
        if(Preview.accepted)for(const auto& Merge:Preview.mergeSteps)MergedStar=FMath::Max(MergedStar,Merge.toStar);
    }
    Command.seat=0;Command.sequence=Captain.sequence+1;Command.revision=Captain.revision;Command.requestId=Command.sequence;
    const auto Reply=SoloMatch->Submit(0,Command);
    if(Reply.accepted&&Command.type==wc::CommandType::Buy)RecordRosterUpgrades(RosterBefore);
    if(!Reply.accepted)Message=TEXT("Order rejected: ")+S(Reply.reason);
    else switch(Command.type){
    case wc::CommandType::Buy:{
        Message=FString::Printf(TEXT("Recruited %s for %dg. Select its bench card, then a near-half cell to deploy."),*Creature,GoldBefore-Captain.gold);
        if(MergedStar>1)Message=FString::Printf(TEXT("Recruited %s for %dg; matching copies automatically merged to %d stars. Select the upgraded creature to position it."),*Creature,GoldBefore-Captain.gold,MergedStar);
        break;}
    case wc::CommandType::Sell:Message=FString::Printf(TEXT("Sold %s (%d stars) for %dg."),*Creature,StarBefore,Captain.gold-GoldBefore);Selected=0;break;
    case wc::CommandType::Move:Message=Command.toBoard?
        FString::Printf(TEXT("%s moved to %c%d. An occupied destination swaps the creatures."),*Creature,TCHAR('A'+Command.cell.column),Command.cell.row+1):
        FString::Printf(TEXT("%s returned to bench slot %d."),*Creature,Command.slot+1);break;
    case wc::CommandType::BuyXp:Message=FString::Printf(TEXT("Bought %d XP for %dg. Level %d, %d XP%s"),Catalog.rules.buyXpAmount,GoldBefore-Captain.gold,Captain.level,Captain.xp,
        Captain.level>LevelBefore?TEXT("; your deployment capacity increased."):TEXT("."));break;
    case wc::CommandType::Reroll:Message=FString::Printf(TEXT("Refreshed the shop for %dg. Gold remaining: %d."),GoldBefore-Captain.gold,Captain.gold);break;
    case wc::CommandType::ToggleLock:Message=Captain.shopLocked?TEXT("Shop locked. These offers stay for the next preparation."):TEXT("Shop unlocked. Offers refresh next preparation.");break;
    case wc::CommandType::Ready:Message=TEXT("Ready. Battle starts when every captain is ready or the preparation clock expires. Editing cancels your ready state.");break;
    case wc::CommandType::SetFacing:Message=Creature+TEXT(" rotated. Check the facing marker and ability coverage before readying.");break;
    case wc::CommandType::ChooseRelic:Message=TEXT("Relic drafted. Select a compatible owned creature, then use its Equip button in the inventory.");break;
    case wc::CommandType::EquipRelic:Message=Creature+TEXT(" equipped ")+S(Catalog.relics[Command.slot].name)+TEXT(". Inspect the changed ability and its tradeoff.");break;
    case wc::CommandType::UnequipRelic:Message=Creature+TEXT(" unequipped its relic. The relic is available in your inventory.");break;
    default:Message=TEXT("Order accepted.");break;
    }
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_COMMAND type=%d accepted=%d reason=%s sequence=%llu"),int(Command.type),Reply.accepted,*S(Reply.reason),Command.sequence);
    if(Reply.accepted){SyncSoloFormation();SaveSolo(true);}
    return Reply.accepted;
}

bool AWCVNextLab::SoloCell(wc::Cell Cell)
{
    if(!SoloMatch)return false;
    KeyboardColumn=Cell.column;KeyboardRow=Cell.row;
    if(const auto* Combat=CurrentCombat()){
        for(const auto& Unit:Combat->Units())if(Unit.health>0&&Unit.cell==Cell){Selected=Unit.id;return true;}
        return false;
    }
    if(ViewedSeat!=0){
        for(const auto& Unit:Formation[0])if(Unit.cell==Cell){Selected=Unit.id;Palette=Unit.definition;BrushStar=Unit.star;return true;}
        Message=TEXT("Viewing public formation. Return to your board to edit.");return false;
    }
    if(SoloMatch->CurrentPhase()!=wc::Phase::Preparation){Message=TEXT("Formation changes wait for preparation.");return false;}
    if(Cell.row>=Catalog.rules.deploymentRows){Message=FString::Printf(TEXT("Deploy on your near %d rows. Opponent cells are read-only."),Catalog.rules.deploymentRows);return false;}
    const auto& Roster=SoloMatch->Seats()[0].roster;
    const auto At=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return Unit.onBoard&&Unit.cell==Cell;});
    const auto SelectedUnit=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return Unit.id==Selected;});
    if(SelectedUnit!=Roster.end() && (At==Roster.end()||At->id!=Selected)){
        wc::Command Move;Move.type=wc::CommandType::Move;Move.unit=Selected;Move.toBoard=true;Move.cell=Cell;
        return SoloCommand(Move);
    }
    if(At!=Roster.end()){Selected=At->id;Palette=At->definition;BrushStar=At->star;PreparationDirty=true;
        Message=TEXT("Selected. Click another cell to move or swap, or a bench slot to return it. Escape clears selection.");return true;}
    Message=TEXT("Select an owned creature on the bench or board first.");return false;
}

void AWCVNextLab::SelectBench(int Slot)
{
    if(!SoloMatch||ViewedSeat!=0)return;
    const auto& Roster=SoloMatch->Seats()[0].roster;
    const auto At=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return !Unit.onBoard&&Unit.bench==Slot;});
    const auto Chosen=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return Unit.id==Selected;});
    if(Chosen!=Roster.end() && (At==Roster.end()||At->id!=Selected)){
        wc::Command Move;Move.type=wc::CommandType::Move;Move.unit=Selected;Move.slot=Slot;Move.toBoard=false;SoloCommand(Move);return;
    }
    if(At!=Roster.end()){Selected=At->id;Palette=At->definition;BrushStar=At->star;PreparationDirty=true;
        Message=TEXT("Bench creature selected. Click a near-half board cell to deploy it.");}
    else Message=TEXT("Empty bench slot. Select a deployed creature first to move it here.");
}

void AWCVNextLab::SaveSolo(bool Automatic)
{
    if(AwaitingSaveDecision){if(!Automatic)Message=TEXT("Load the saved preparation or choose New tournament first. Your saved game is preserved.");return;}
    if(!SoloMatch||SoloMatch->CurrentPhase()!=wc::Phase::Preparation)return;
    const auto Result=wc::SavePreparationFile(*SoloMatch,std::filesystem::path(*SavePath));
    if(!Automatic||!Result.Succeeded())Message=S(Result.message);
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_SAVE success=%d status=%d"),Result.Succeeded(),int(Result.status));
}

void AWCVNextLab::ResumeSolo()
{
    if(!SoloMatch)return;
    const auto Result=wc::LoadPreparationFile(*SoloMatch,std::filesystem::path(*SavePath));
    Message=S(Result.message);
    if(Result.Succeeded()){
        ClearUpgradePresentation();
        AwaitingSaveDecision=false;
        Seed=int(SoloMatch->Seed());ViewedSeat=0;Selected=0;SoloPaused=true;Accumulator=0;
        LastSoloRound=SoloMatch->Round();LastSoloPhase=SoloMatch->CurrentPhase();LastSoloRecord=0;
        SoloRecap=TEXT("No recorded battle for your captain in this saved tournament yet.");
        LastSoloRevision=~wc::Id(0);SyncSoloFormation();
        Message+=TEXT(" Preparation is paused; Resume clock when ready.");
    }
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_RESUME success=%d status=%d round=%d"),Result.Succeeded(),int(Result.status),SoloMatch->Round());
}

void AWCVNextLab::ScoutSolo(int Seat)
{
    ClearUpgradePresentation();
    ViewedSeat=FMath::Clamp(Seat,0,7);Selected=0;LastSoloRevision=~wc::Id(0);SyncSoloFormation();
    Message=ViewedSeat?TEXT("Live public view. Shops, benches and relic choices stay private."):TEXT("Your board. Select a creature to change your formation.");
}

void AWCVNextLab::EquipSolo(int Relic)
{
    wc::Command Equip;Equip.type=wc::CommandType::EquipRelic;Equip.unit=Selected;Equip.slot=Relic;SoloCommand(Equip);
}

FString AWCVNextLab::ShopText(int Slot) const
{
    if(!SoloMatch||ViewedSeat!=0)return TEXT("Private shop");
    const auto& Captain=SoloMatch->Seats()[0];
    if(Slot>=int(Captain.shop.size())||Captain.shop[Slot]<0)return TEXT("Purchased");
    const int Def=Captain.shop[Slot];const auto& Unit=Catalog.units[Def];int Copies=0;
    for(const auto& Owned:Captain.roster)if(Owned.definition==Def)Copies+=Owned.star==3?9:Owned.star==2?3:1;
    wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;
    const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Buy);
    const FString Hint=Preview.accepted&&!Preview.mergeSteps.empty()?TEXT(" · merges now"):FString();
    return FString::Printf(TEXT("%s  ·  %dg\nOwned copies: %d%s"),*S(Unit.displayName),Unit.cost,Copies,*Hint);
}
FString AWCVNextLab::BenchText(int Slot) const
{
    if(!SoloMatch||ViewedSeat!=0)return TEXT("Private");
    for(const auto& Unit:SoloMatch->Seats()[0].roster)if(!Unit.onBoard&&Unit.bench==Slot)
        return FString::Printf(TEXT("%d  %s%s *%d"),Slot+1,Selected==Unit.id?TEXT("> "):TEXT(""),*S(Catalog.units[Unit.definition].displayName),Unit.star);
    return FString::Printf(TEXT("%d  Empty"),Slot+1);
}
FString AWCVNextLab::RelicText(int Slot,bool Offer) const
{
    if(!SoloMatch||ViewedSeat!=0)return TEXT("Private");
    const auto& Captain=SoloMatch->Seats()[0];const auto& Items=Offer?Captain.relicOffers:Captain.ownedRelics;
    if(Slot>=int(Items.size()))return Offer?TEXT("No draft"):TEXT("No relic");
    const auto& Relic=Catalog.relics[Items[Slot]];
    const bool Compatible=std::any_of(Captain.roster.begin(),Captain.roster.end(),[&](const auto& Unit){return wc::RelicCompatible(Relic,Catalog.units[Unit.definition].ability.mechanic);});
    FString Fit=Compatible?TEXT(""):TEXT(" (future use)");
    if(!Offer){
        const auto Chosen=std::find_if(Captain.roster.begin(),Captain.roster.end(),[this](const auto& Unit){return Unit.id==Selected;});
        if(Chosen==Captain.roster.end())Fit=TEXT(" · select a creature");
        else if(Chosen->relic==Items[Slot])Fit=TEXT(" · equipped on selected");
        else Fit=wc::RelicCompatible(Relic,Catalog.units[Chosen->definition].ability.mechanic)?TEXT(" · fits selected"):TEXT(" · incompatible with selected");
    }
    return S(Relic.name)+Fit+TEXT("\n")+S(Relic.description);
}

FString AWCVNextLab::SoloStatusText() const
{
    if(!SoloMatch)return TEXT("No tournament.");
    const auto& Captain=SoloMatch->Seats()[0];
    const auto Public=SoloMatch->PublicSeats();const auto& View=Public[ViewedSeat];
    int Deployed=0;for(const auto& U:Captain.roster)Deployed+=U.onBoard;
    return FString::Printf(TEXT("Round %d · %s%s · %.1fs · Your HP %d · Gold %d · Level %d (%d XP) · Deployed %d/%d\nViewing %s%s · Keyboard cell %c%d"),
        SoloMatch->Round(),PhaseName(SoloMatch->CurrentPhase()),SoloPaused?TEXT(" / PAUSED"):TEXT(""),SoloMatch->RemainingMs()/1000.,Captain.health,Captain.gold,Captain.level,Captain.xp,Deployed,Captain.level,
        *S(View.label),ViewedSeat?TEXT(" / SCOUTING"):TEXT(" / YOUR BOARD"),TCHAR('A'+KeyboardColumn),KeyboardRow+1);
}
FString AWCVNextLab::SoloSummaryText() const
{
    if(!SoloMatch)return FString();
    FString Result;
    const auto Public=SoloMatch->PublicSeats();
    for(const auto& Seat:Public)Result+=FString::Printf(TEXT("%s %s · HP %d · Lv%d%s%s\n"),Seat.id==ViewedSeat?TEXT(">"):TEXT(" "),*S(Seat.label),Seat.health,Seat.level,Seat.health<=0?TEXT(" · OUT"):TEXT(""),Seat.ready?TEXT(" · Ready"):TEXT(""));
    Result+=FString::Printf(TEXT("\nPublic formation · round %d · revision %llu\nNext encounter: "),SoloMatch->Round(),LastSoloRevision);bool Found=false;
    for(const auto& Pair:SoloMatch->Pairings())if(Pair.a==ViewedSeat||(Pair.kind==wc::EncounterKind::Pvp&&Pair.b==ViewedSeat)){
        if(Pair.kind==wc::EncounterKind::Neutral)Result+=TEXT("Neutral wave ")+S(Pair.waveId);
        else{const int Other=Pair.a==ViewedSeat?Pair.b:Pair.a;Result+=S(Public[Other].label);if(Pair.ghost)Result+=TEXT(" (ghost copy)");}Found=true;break;
    }
    if(!Found)Result+=TEXT("No active encounter");
    for(const auto& Pair:SoloMatch->Pairings())if(Pair.a==ViewedSeat||(Pair.kind==wc::EncounterKind::Pvp&&Pair.b==ViewedSeat)){
        if(SoloMatch->CurrentPhase()==wc::Phase::Preparation)Result+=TEXT("\nNear A = viewed captain; far B = next opponent.");
        else Result+=TEXT("\nCombat A = ")+S(Public[Pair.a].label)+TEXT("; B = ")+(Pair.kind==wc::EncounterKind::Neutral?TEXT("neutral wave"):S(Public[Pair.b].label));
        break;
    }
    Result+=TEXT("\n\nTraits are inactive in this study candidate. Relics shown on inspected deployed creatures are public.");
    if(SoloMatch->CurrentPhase()==wc::Phase::Finished){Result+=TEXT("\n\nFINAL PLACEMENTS\n");for(int Place=1;Place<=8;++Place)for(const auto& Seat:Public)if(Seat.placement==Place)Result+=FString::Printf(TEXT("%d. %s\n"),Place,*S(Seat.label));}
    return Result;
}

void AWCVNextLab::TickSolo(float DeltaSeconds)
{
    if(!SoloMatch)return;
    if(SoloExercise){TickSoloExercise();}
    else if(!SoloPaused&&!AwaitingSaveDecision){
        Accumulator+=DeltaSeconds;
        for(int CatchUp=0;Accumulator>=.05&&CatchUp<20;++CatchUp){SoloMatch->Tick(50);Accumulator-=.05;}
    }
    const FString Invariant=S(SoloMatch->InvariantError());
    if(!Invariant.IsEmpty()){SoloPaused=true;Message=TEXT("Tournament stopped: ")+Invariant;UE_LOG(LogTemp,Error,TEXT("WC_SOLO_INVARIANT %s"),*Invariant);}
    const auto Phase=SoloMatch->CurrentPhase();const int Round=SoloMatch->Round();
    const auto Revision=PublicIdentity(SoloMatch->PublicSeats());
    if(Phase!=LastSoloPhase||Round!=LastSoloRound){
        Selected=0;SyncSoloFormation();
        UE_LOG(LogTemp,Display,TEXT("WC_SOLO_PHASE round=%d phase=%d remaining_ms=%d"),Round,int(Phase),SoloMatch->RemainingMs());
        if(Phase==wc::Phase::Preparation){SaveSolo(true);if(SoloMatch->Seats()[0].health<=0)Message=TEXT("You are eliminated. Scout surviving captains to spectate, restart, or exit.");}
        LastSoloRound=Round;LastSoloPhase=Phase;
    }
    if(Revision!=LastSoloRevision){if(Phase==wc::Phase::Preparation)SyncSoloFormation();LastSoloRevision=Revision;}
    if(int(SoloMatch->Records().size())>LastSoloRecord){
        bool Found=false;
        for(auto It=SoloMatch->Records().rbegin();It!=SoloMatch->Records().rend()&&!Found;++It){
        const auto& Record=*It;
        for(const auto& E:Record.encounters)if(E.pairing.a==0||(E.kind==wc::EncounterKind::Pvp&&E.pairing.b==0)){
            const int Side=E.pairing.a==0?0:1;const auto& R=E.result;
            SoloRecap=FString::Printf(TEXT("Your last battle · round %d: %s in %.2fs.\nCaptain HP lost: %d; HP remaining: %d.\nYou dealt %.0f creature health damage and received %.0f effective healing.\n%s\nSurvivors: you %d, opponent %d. Look at positioning and the recorded events before changing your plan."),Record.round,R.winner<0?TEXT("draw"):R.winner==Side?TEXT("you won"):TEXT("you lost"),R.ticks*Catalog.rules.tickMs/1000.,Record.damage[0],Record.health[0],E.healthLoss[1-Side]/100.,E.healing[Side]/100.,R.timeout?TEXT("Deadline fallback: summed remaining-health fractions decide the result; cost and stars do not weight that score."):TEXT("Combat resolved by elimination."),R.survivors[Side],R.survivors[1-Side]);
            Found=true;break;
        }
        }
        LastSoloRecord=int(SoloMatch->Records().size());
    }
    if(SoloSummaryBlock)SoloSummaryBlock->SetText(T(SoloSummaryText()));
}

void AWCVNextLab::BuildSoloInterface()
{
    if(FWCArtSlice::IsStorybook()){BuildStorybookInterface();return;}
    if(!GEngine||!GEngine->GameViewport)return;
    const auto Font=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),11);
    const auto CanEdit=[this]{return SoloMatch&&!AwaitingSaveDecision&&ViewedSeat==0&&SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0;};
    const auto Button=[Font](TFunction<FString()> Label,TFunction<void()> Action,TFunction<bool()> Enabled=[] {return true;}) -> TSharedRef<SWidget> {
        return SNew(SButton).ContentPadding(FMargin(7,5)).IsEnabled_Lambda([Enabled]{return Enabled();})
            .ToolTipText_Lambda([Label]{return T(Label());})
            .OnClicked_Lambda([Action]{Action();return FReply::Handled();})
            [SNew(STextBlock).Font(Font).AutoWrapText(true).Text_Lambda([Label]{return T(Label());})];
    };
    const auto Command=[this](wc::CommandType Type){wc::Command C;C.type=Type;C.unit=Selected;SoloCommand(C);};
    auto Actions=SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(4,4));
    Actions->AddSlot()[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].ready?TEXT("Ready · edit to cancel"):TEXT("Ready");},[Command]{Command(wc::CommandType::Ready);},[this,CanEdit]{return CanEdit()&&!SoloMatch->Seats()[0].ready;})];
    Actions->AddSlot()[Button([this]{return FString::Printf(TEXT("Reroll · %dg"),Catalog.rules.rerollCost);},[Command]{Command(wc::CommandType::Reroll);},CanEdit)];
    Actions->AddSlot()[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].shopLocked?TEXT("Unlock shop"):TEXT("Lock shop");},[Command]{Command(wc::CommandType::ToggleLock);},CanEdit)];
    Actions->AddSlot()[Button([this]{return FString::Printf(TEXT("Buy %d XP · %dg"),Catalog.rules.buyXpAmount,Catalog.rules.buyXpGold);},[Command]{Command(wc::CommandType::BuyXp);},CanEdit)];
    Actions->AddSlot()[Button([]{return TEXT("Sell selected");},[Command]{Command(wc::CommandType::Sell);},CanEdit)];
    Actions->AddSlot()[Button([]{return TEXT("Rotate selected");},[this]{
        if(!SoloMatch)return;for(const auto& U:SoloMatch->Seats()[0].roster)if(U.id==Selected){wc::Command C;C.type=wc::CommandType::SetFacing;C.unit=Selected;C.facing=wc::Facing((int(U.facing)+1)%4);SoloCommand(C);return;}Message=TEXT("Select an owned creature first.");},CanEdit)];
    Actions->AddSlot()[Button([]{return TEXT("Clear selection");},[this]{Selected=0;PreparationDirty=true;})];
    Actions->AddSlot()[Button([this]{return SoloPaused?TEXT("Resume clock"):TEXT("Pause");},[this]{SoloPaused=!SoloPaused;},[this]{return !AwaitingSaveDecision;})];
    Actions->AddSlot()[Button([]{return TEXT("Save preparation");},[this]{SaveSolo();},[this]{return SoloMatch&&SoloMatch->CurrentPhase()==wc::Phase::Preparation;})];
    Actions->AddSlot()[Button([]{return TEXT("Load saved preparation");},[this]{ResumeSolo();})];
    Actions->AddSlot()[Button([]{return TEXT("New tournament");},[this]{NewSolo();})];
    Actions->AddSlot()[Button([]{return TEXT("Exit");},[]{FPlatformMisc::RequestExit(false);})];
    const bool UseArtSlice=FWCArtSlice::IsEnabled();
    auto Shop=SNew(SHorizontalBox);
    for(int Slot=0;Slot<Catalog.rules.shopSlots;++Slot){
        const auto Buy=[this,Slot]{wc::Command C;C.type=wc::CommandType::Buy;C.slot=Slot;SoloCommand(C);};
        if(!UseArtSlice){Shop->AddSlot().FillWidth(1).Padding(2)[Button([this,Slot]{return ShopText(Slot);},Buy,CanEdit)];continue;}
        const auto CardData=[this,Slot]{
            FWCArtCardData Card;
            Card.Name=ShopText(Slot);Card.Tooltip=Card.Name;
            if(!SoloMatch||ViewedSeat!=0)return Card;
            const auto& Captain=SoloMatch->Seats()[0];
            if(Slot>=int(Captain.shop.size())||Captain.shop[Slot]<0)return Card;
            const int Definition=Captain.shop[Slot];const auto& Unit=Catalog.units[Definition];
            Card.UnitId=S(Unit.id);Card.Name=S(Unit.displayName);Card.Cost=Unit.cost;
            Card.Detail=S(Unit.unitClass)+TEXT(" · ")+(Unit.range<=1?TEXT("Melee"):TEXT("Ranged"))+TEXT("\n")+S(Unit.ability.name);
            int Copies=0;for(const auto& Owned:Captain.roster)if(Owned.definition==Definition)Copies+=Owned.star==3?9:Owned.star==2?3:1;
            wc::Command Command;Command.type=wc::CommandType::Buy;Command.slot=Slot;
            const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Command);
            Card.Footer=FString::Printf(TEXT("Owned: %d%s"),Copies,Preview.accepted&&!Preview.mergeSteps.empty()?TEXT(" · MERGE"):TEXT(""));
            if(!Preview.accepted)Card.Tooltip+=TEXT("\nUnavailable: ")+S(Preview.reason);
            if(Unit.id=="wc_vn_bellback")Card.Tooltip+=TEXT("\nBellback portrait study; the board uses a gameplay proxy.");
            return Card;
        };
        const auto CanBuy=[this,Slot,CanEdit]{
            if(!CanEdit())return false;
            const auto& Captain=SoloMatch->Seats()[0];
            if(Slot>=int(Captain.shop.size())||Captain.shop[Slot]<0)return false;
            wc::Command Command;Command.type=wc::CommandType::Buy;Command.slot=Slot;
            return wc::PreviewRosterCommand(Catalog,Captain,Command).accepted;
        };
        Shop->AddSlot().FillWidth(1).Padding(2)[FWCArtSlice::MakeShopCard(CardData,Buy,CanBuy)];
    }
    auto Bench=SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(3,3));
    for(int Slot=0;Slot<Catalog.rules.benchCapacity;++Slot)Bench->AddSlot()[Button([this,Slot]{return BenchText(Slot);},[this,Slot]{SelectBench(Slot);},CanEdit)];
    auto Scouting=SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(3,3));
    for(int Seat=0;Seat<8;++Seat)Scouting->AddSlot()[Button([Seat]{return Seat?FString::Printf(TEXT("Scout %d"),Seat+1):TEXT("Your board");},[this,Seat]{ScoutSolo(Seat);})];
    auto Relics=SNew(SVerticalBox);
    Relics->AddSlot().AutoHeight()[SNew(STextBlock).Font(Font).ColorAndOpacity(Gold).Text(T(TEXT("RELIC DRAFT / INVENTORY")))];
    const auto WithRelicIcon=[this,UseArtSlice](TSharedRef<SWidget> Content,int Slot,bool Offer)->TSharedRef<SWidget>{
        if(!UseArtSlice)return Content;
        return SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,5,0)[SNew(SBox).WidthOverride(36).HeightOverride(36)
                .Visibility_Lambda([this,Slot,Offer]{
                    if(!SoloMatch||ViewedSeat!=0)return EVisibility::Collapsed;
                    const auto& Captain=SoloMatch->Seats()[0];const auto& Items=Offer?Captain.relicOffers:Captain.ownedRelics;
                    return Slot<int(Items.size())&&Catalog.relics[Items[Slot]].id=="wc_vn_r_heavy_bloom"?EVisibility::Visible:EVisibility::Collapsed;
                })[SNew(SImage).Image(FWCArtSlice::HeavyBloomIcon())]]
            +SHorizontalBox::Slot().FillWidth(1)[Content];
    };
    for(int Slot=0;Slot<3;++Slot)Relics->AddSlot().AutoHeight().Padding(0,2)[WithRelicIcon(Button([this,Slot]{return TEXT("Draft: ")+RelicText(Slot,true);},[this,Slot]{wc::Command C;C.type=wc::CommandType::ChooseRelic;C.slot=Slot;SoloCommand(C);},[this,Slot,CanEdit]{return CanEdit()&&Slot<int(SoloMatch->Seats()[0].relicOffers.size());}),Slot,true)];
    for(int Slot=0;Slot<3;++Slot)Relics->AddSlot().AutoHeight().Padding(0,2)[WithRelicIcon(Button([this,Slot]{return TEXT("Equip: ")+RelicText(Slot,false);},[this,Slot]{if(Slot<int(SoloMatch->Seats()[0].ownedRelics.size()))EquipSolo(SoloMatch->Seats()[0].ownedRelics[Slot]);},[this,Slot,CanEdit]{return CanEdit()&&Slot<int(SoloMatch->Seats()[0].ownedRelics.size());}),Slot,false)];
    Relics->AddSlot().AutoHeight()[Button([]{return TEXT("Unequip selected");},[Command]{Command(wc::CommandType::UnequipRelic);},CanEdit)];
    const auto SelectedDefinition=[this]{
        if(const auto* Combat=CurrentCombat()){
            for(const auto& Unit:Combat->Units())if(Unit.id==Selected&&!Unit.neutral)return Unit.definition;
            return -1;
        }
        if(SoloMatch&&ViewedSeat==0)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(Unit.id==Selected)return Unit.definition;
        if(const auto* Unit=SelectedPiece())return Unit->definition;
        return -1;
    };
    auto Sidebar=SNew(SScrollBox)+SScrollBox::Slot().Padding(10)[SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Scouting]
        +SVerticalBox::Slot().AutoHeight().Padding(0,UseArtSlice?8:0)[UseArtSlice?FWCArtSlice::MakeStudyPanel([this,SelectedDefinition]{
            const int Definition=SelectedDefinition();return Definition>=0?S(Catalog.units[Definition].id):FString();
        },[this,SelectedDefinition]{const int Definition=SelectedDefinition();return Definition>=0?S(Catalog.units[Definition].displayName):FString();}):SNullWidget::NullWidget]
        +SVerticalBox::Slot().AutoHeight().Padding(0,8)[SAssignNew(SoloSummaryBlock,STextBlock).Font(Font).ColorAndOpacity(Paper).AutoWrapText(true)]
        +SVerticalBox::Slot().AutoHeight()[Relics]
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[SAssignNew(InspectorBlock,STextBlock).Font(Font).ColorAndOpacity(Paper).AutoWrapText(true)]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Font).ColorAndOpacity(Gold).Text(T(TEXT("BATTLE FACTS")))]
        +SVerticalBox::Slot().AutoHeight()[SAssignNew(EventBlock,STextBlock).Font(Font).ColorAndOpacity(Paper).AutoWrapText(true)]];
    BoardInput=SNew(SWCSoloBoard).Click([this]{BoardClick(false);}).Key([this](const FKeyEvent& Event){
        const auto Key=Event.GetKey();
        if(Key==EKeys::Left)KeyboardColumn=FMath::Max(0,KeyboardColumn-1);
        else if(Key==EKeys::Right)KeyboardColumn=FMath::Min(7,KeyboardColumn+1);
        else if(Key==EKeys::Up)KeyboardRow=FMath::Min(7,KeyboardRow+1);
        else if(Key==EKeys::Down)KeyboardRow=FMath::Max(0,KeyboardRow-1);
        else if(Key==EKeys::Enter||Key==EKeys::SpaceBar)SoloCell({KeyboardColumn,KeyboardRow});
        else if(Key==EKeys::Escape){Selected=0;PreparationDirty=true;}
        else return FReply::Unhandled();return FReply::Handled();});
    Interface=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(12)
            [SNew(SVerticalBox)+SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),19)).ColorAndOpacity(Gold).Text(T(UseArtSlice?TEXT("WONDER CHESS / 2D ART SLICE"):TEXT("WONDER CHESS / SOLO TOURNAMENT")))]
            +SVerticalBox::Slot().AutoHeight()[SAssignNew(StatusBlock,STextBlock).Font(Font).ColorAndOpacity(Paper).AutoWrapText(true)]
            +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Font).ColorAndOpacity(Paper).AutoWrapText(true).Text(T(TEXT("Six-creature study · gameplay proxy art · Click source, then destination. Board focus: arrows + Enter; Escape clears selection.")))]]]
        +SVerticalBox::Slot().FillHeight(1)[SNew(SHorizontalBox)+SHorizontalBox::Slot().FillWidth(1)[BoardInput.ToSharedRef()]
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(310)[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink)[Sidebar]]]]
        +SVerticalBox::Slot().AutoHeight()[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(8)
            [SNew(SVerticalBox)+SVerticalBox::Slot().AutoHeight()[Shop]+SVerticalBox::Slot().AutoHeight().Padding(0,4)[Bench]
            +SVerticalBox::Slot().AutoHeight()[Actions]
            +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SAssignNew(MessageBlock,STextBlock).Font(Font).ColorAndOpacity(Gold).AutoWrapText(true)]]];
    GEngine->GameViewport->AddViewportWidgetContent(Interface.ToSharedRef(),50);
    if(Controller){FInputModeGameAndUI Input;Input.SetWidgetToFocus(BoardInput);Input.SetHideCursorDuringCapture(false);Controller->SetInputMode(Input);}
    UpdateInterfaceText();
}

void AWCVNextLab::BuildStorybookInterface()
{
    if(!GEngine||!GEngine->GameViewport)return;
    const FLinearColor Parchment(.84f,.75f,.57f), Dark(.024f,.034f,.025f);
    const auto Small=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),10);
    const auto Regular=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),11);
    const auto Bold=FWCArtSlice::HeadingFont(12);
    const auto ViewSize=[] {FVector2D Size(1280,720);if(GEngine&&GEngine->GameViewport)GEngine->GameViewport->GetViewportSize(Size);return Size;};
    const auto Always=[] {return true;};
    const auto CanEdit=[this]{return SoloMatch&&LoadError.IsEmpty()&&!AwaitingSaveDecision&&ViewedSeat==0&&
        SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0;};
    const auto Command=[this](wc::CommandType Type){wc::Command C;C.type=Type;C.unit=Selected;SoloCommand(C);};
    const auto Button=[](TFunction<FString()> Label,TFunction<void()> Action,TFunction<bool()> Enabled)->TSharedRef<SWidget>{
        return FWCArtSlice::MakeButton(Label,Action,Enabled);
    };
    const auto Label=[Regular,Parchment](const FString& Value)->TSharedRef<SWidget>{
        return SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text(T(Value));
    };
    const auto SelectedDefinition=[this]{
        if(const auto* Combat=CurrentCombat()){
            for(const auto& Unit:Combat->Units())if(Unit.id==Selected&&!Unit.neutral)return Unit.definition;
            return -1;
        }
        if(SoloMatch&&ViewedSeat==0)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(Unit.id==Selected)return Unit.definition;
        if(const auto* Unit=SelectedPiece())return Unit->definition;
        return -1;
    };
    const auto SelectedId=[this,SelectedDefinition]{const int Def=SelectedDefinition();return Def>=0?S(Catalog.units[Def].id):FString();};
    const auto MenuOpen=MakeShared<bool>(false);
    const auto RecapOpen=MakeShared<bool>(false);
    const auto CollectionOpen=MakeShared<bool>(false);
    enum class EStoryModal {None,Recap,Menu,Collection,Draft,Results,Save};
    const auto TopModal=[this,CanEdit,MenuOpen,RecapOpen,CollectionOpen]{
        if(AwaitingSaveDecision)return EStoryModal::Save;
        if(SoloMatch&&SoloMatch->CurrentPhase()==wc::Phase::Finished)return EStoryModal::Results;
        if(CanEdit()&&!SoloMatch->Seats()[0].relicOffers.empty())return EStoryModal::Draft;
        if(*CollectionOpen)return EStoryModal::Collection;
        if(*MenuOpen)return EStoryModal::Menu;
        if(*RecapOpen)return EStoryModal::Recap;
        return EStoryModal::None;
    };
    auto OpenMenu=Button([]{return TEXT("Menu");},[MenuOpen]{*MenuOpen=true;},Always);
    OpenMenu->SetTag(TEXT("WC.OpenMenu"));
    const auto RelicId=[this](int Slot,bool Offer){
        if(!SoloMatch||ViewedSeat!=0)return FString();
        const auto& Captain=SoloMatch->Seats()[0];const auto& Items=Offer?Captain.relicOffers:Captain.ownedRelics;
        return Slot<int(Items.size())?S(Catalog.relics[Items[Slot]].id):FString();
    };
    auto Traits=SNew(SVerticalBox);
    Traits->AddSlot().AutoHeight().Padding(0,0,0,8)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Text(T(TEXT("TRAITS")))];
    Traits->AddSlot().AutoHeight().Padding(0,0,0,7)[Label(TEXT("Counts only\nBonuses are inactive"))];
    TArray<TPair<FString,bool>> Identities;
    for(const auto& Unit:Catalog.units){
        const auto Add=[&Identities](const FString& Id,bool Race){
            if(!Identities.ContainsByPredicate([&](const auto& Entry){return Entry.Key==Id&&Entry.Value==Race;}))Identities.Add({Id,Race});
        };
        Add(S(Unit.race),true);Add(S(Unit.unitClass),false);
    }
    for(const auto& Identity:Identities){
        const FString Name=Identity.Key.Replace(TEXT("_"),TEXT(" "));
        const auto Count=[this,Identity]{
            TSet<int> Distinct;
            if(SoloMatch){const auto Public=SoloMatch->PublicSeats();for(const auto& Unit:Public[ViewedSeat].deployment){
                const auto& Def=Catalog.units[Unit.definition];
                if(S(Identity.Value?Def.race:Def.unitClass)==Identity.Key)Distinct.Add(Unit.definition);
            }}
            return Distinct.Num();
        };
        Traits->AddSlot().AutoHeight().Padding(0,2)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[FWCArtSlice::MakeTraitGlyph(Identity.Key,29,[Count]{return Count()>0;})]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(6,0)[SNew(STextBlock).Font(Small).AutoWrapText(true)
                .ColorAndOpacity_Lambda([Count,Parchment]{return Count()>0?Parchment:FLinearColor(.34f,.37f,.30f);}).Text(T(Name))]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
                .Text_Lambda([Count]{return T(FString::FromInt(Count()));})]];
    }
    auto Inventory=SNew(SVerticalBox);
    Inventory->AddSlot().AutoHeight().Padding(0,10,0,5)[Label(TEXT("RELICS"))];
    for(int Slot=0;Slot<3;++Slot){
        const auto ItemId=[RelicId,Slot]{return RelicId(Slot,false);};
        Inventory->AddSlot().AutoHeight().Padding(0,2)[SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(3)
            .IsEnabled_Lambda([this,Slot,CanEdit]{
                if(!CanEdit()||Slot>=int(SoloMatch->Seats()[0].ownedRelics.size()))return false;
                const auto& Captain=SoloMatch->Seats()[0];for(const auto& Unit:Captain.roster)if(Unit.id==Selected)
                    return wc::RelicCompatible(Catalog.relics[Captain.ownedRelics[Slot]],Catalog.units[Unit.definition].ability.mechanic);
                return false;
            }).ToolTipText_Lambda([this,Slot]{return T(RelicText(Slot,false));})
            .OnClicked_Lambda([this,Slot]{if(SoloMatch&&Slot<int(SoloMatch->Seats()[0].ownedRelics.size()))EquipSolo(SoloMatch->Seats()[0].ownedRelics[Slot]);return FReply::Handled();})
            [SNew(SHorizontalBox)
                +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(34).HeightOverride(34)[SNew(SImage).Image_Lambda([ItemId]{return FWCArtSlice::RelicIcon(ItemId());})]]
                +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(5,0)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true)
                    .Text_Lambda([this,Slot]{if(!SoloMatch||ViewedSeat!=0)return T(TEXT("Private"));const auto& Items=SoloMatch->Seats()[0].ownedRelics;
                        return T(Slot<int(Items.size())?S(Catalog.relics[Items[Slot]].name):TEXT("Empty slot"));})]]];
    }
    Inventory->AddSlot().AutoHeight().Padding(0,4)[Button([]{return TEXT("Unequip selected");},[Command]{Command(wc::CommandType::UnequipRelic);},CanEdit)];
    auto Left=FWCArtSlice::MakePanel(SNew(SScrollBox)+SScrollBox::Slot()[SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Traits]+SVerticalBox::Slot().AutoHeight()[Inventory]],false,12);

    auto Standings=SNew(SVerticalBox);
    Standings->AddSlot().AutoHeight().Padding(0,0,0,5)[Label(TEXT("CAPTAINS  ·  CLICK TO SCOUT"))];
    for(int Seat=0;Seat<Catalog.rules.seatCount;++Seat){
        Standings->AddSlot().AutoHeight().Padding(0,1)[SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(FMargin(4,3))
            .ToolTipText_Lambda([this,Seat]{if(!SoloMatch)return T(TEXT("No tournament"));const auto Public=SoloMatch->PublicSeats();
                return T(S(Public[Seat].label)+TEXT(" · public formation\nHealth ")+FString::FromInt(Public[Seat].health)+TEXT(" · level ")+FString::FromInt(Public[Seat].level));})
            .OnClicked_Lambda([this,Seat]{ScoutSolo(Seat);return FReply::Handled();})
            [SNew(SHorizontalBox)
                +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(1,0,6,0)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
                    .Text_Lambda([this,Seat]{return T(Seat==ViewedSeat?TEXT("◆"):TEXT("◇"));})]
                +SHorizontalBox::Slot().FillWidth(1)[SNew(SVerticalBox)
                    +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment)
                        .Text_Lambda([this,Seat]{if(!SoloMatch)return T(TEXT("—"));const auto Public=SoloMatch->PublicSeats();
                            return T(Seat==0?TEXT("You"):S(Public[Seat].label));})]
                    +SVerticalBox::Slot().AutoHeight().Padding(0,3,0,0)[SNew(SBox).HeightOverride(5)[SNew(SProgressBar)
                        .BarFillStyle(EProgressBarFillStyle::Scale).FillImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")))
                        .BackgroundImage(FCoreStyle::Get().GetBrush(TEXT("BlackBrush")))
                        .BorderPadding(FVector2D::ZeroVector)
                        .Percent_Lambda([this,Seat]{if(!SoloMatch)return TOptional<float>(0.f);return TOptional<float>(FMath::Clamp(
                            float(SoloMatch->PublicSeats()[Seat].health)/FMath::Max(1,Catalog.rules.startingHealth),0.f,1.f));})
                        .FillColorAndOpacity(FLinearColor(.49f,.63f,.37f))]]]
                +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(8,0,0,0)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment)
                    .Text_Lambda([this,Seat]{if(!SoloMatch)return T(TEXT("—"));const auto Public=SoloMatch->PublicSeats();return T(Public[Seat].health>0?
                        FString::FromInt(Public[Seat].health):TEXT("OUT"));})]]];
    }
    auto Inspector=FWCArtSlice::MakePanel(SNew(SScrollBox)+SScrollBox::Slot()[SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(SBox).HeightOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().Y)*.11f,72.f,120.f));})
            .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SImage).Image_Lambda([SelectedId]{return FWCArtSlice::Portrait(SelectedId());})]]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,4)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Dark).AutoWrapText(true)
            .Text_Lambda([this,SelectedDefinition]{const int Def=SelectedDefinition();return T(Def>=0?S(Catalog.units[Def].displayName):TEXT("Select a creature"));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,2)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(38).HeightOverride(38)
                .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
                [SNew(SImage).Image_Lambda([SelectedId]{return FWCArtSlice::AbilityIcon(SelectedId());})]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(5,0)[SNew(STextBlock).Font(Small).ColorAndOpacity(Dark).AutoWrapText(true)
                .Text_Lambda([this,SelectedDefinition]{const int Def=SelectedDefinition();if(Def<0)return T(TEXT("Inspect a bench or board creature to see its ability and stats."));
                    const auto& Unit=Catalog.units[Def];return T(S(Unit.ability.name)+TEXT("\n")+(Unit.range<=1?TEXT("Melee"):TEXT("Ranged")));})]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SNew(STextBlock).Font(Small).ColorAndOpacity(Dark).AutoWrapText(true)
            .Text_Lambda([this]{return T(InspectorText().Replace(TEXT(" in this lab"),TEXT("")));})]],true,10);
    auto Right=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[FWCArtSlice::MakePanel(Standings,false,9)]
        +SVerticalBox::Slot().FillHeight(1).Padding(0,6,0,0)[Inspector];

    auto Bench=SNew(SHorizontalBox);
    for(int Slot=0;Slot<Catalog.rules.benchCapacity;++Slot){
        const auto Piece=[this,Slot]() -> const wc::OwnedUnit* {
            if(SoloMatch&&ViewedSeat==0)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(!Unit.onBoard&&Unit.bench==Slot)return &Unit;
            return nullptr;
        };
        Bench->AddSlot().FillWidth(1).Padding(2,0)[SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(2)
            .IsEnabled_Lambda(CanEdit).ToolTipText_Lambda([this,Slot]{return T(BenchText(Slot)+TEXT("\nSelect, then click a legal board tile. Click here with a selected unit to return or swap it."));})
            .OnClicked_Lambda([this,Slot]{SelectBench(Slot);return FReply::Handled();})
            [SNew(SBorder).BorderImage(FWCArtSlice::PanelBrush()).Padding(2)
                .BorderBackgroundColor_Lambda([this,Piece]{const auto* Unit=Piece();return Unit&&(Selected==Unit->id||UpgradePulse(Unit->id)>0)?FLinearColor(1.4f,1.15f,.65f):FLinearColor::White;})
                [SNew(SOverlay)
                    +SOverlay::Slot()[SNew(SBox).HeightOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().Y)*.05f,34.f,52.f));})
                        [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SImage).Image_Lambda([this,Piece]{const auto* Unit=Piece();return FWCArtSlice::Portrait(Unit?S(Catalog.units[Unit->definition].id):FString());})]]]
                    +SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).Text(T(FString::FromInt(Slot+1)))]
                    +SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Bottom)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment)
                        .Text_Lambda([Piece]{const auto* Unit=Piece();return T(Unit?FString::ChrN(Unit->star,TCHAR('*')):FString());})]]]];
    }
    auto Shop=SNew(SHorizontalBox);
    for(int Slot=0;Slot<Catalog.rules.shopSlots;++Slot){
        const auto Data=[this,Slot]{
            FWCArtCardData Card;Card.Name=ViewedSeat?TEXT("Private shop"):TEXT("Purchased");
            if(!SoloMatch||ViewedSeat!=0)return Card;
            const auto& Captain=SoloMatch->Seats()[0];if(Slot>=int(Captain.shop.size())||Captain.shop[Slot]<0)return Card;
            const int Def=Captain.shop[Slot];const auto& Unit=Catalog.units[Def];
            Card.UnitId=S(Unit.id);Card.Name=S(Unit.displayName);Card.Cost=Unit.cost;
            Card.Detail=S(Unit.race)+TEXT(" / ")+S(Unit.unitClass)+TEXT("\n")+S(Unit.ability.name);
            int Copies=0;for(const auto& Owned:Captain.roster)if(Owned.definition==Def)Copies+=Owned.star==3?9:Owned.star==2?3:1;
            wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;const auto Preview=wc::PreviewRosterCommand(Catalog,Captain,Buy);
            Card.Footer=FString::Printf(TEXT("Owned %d%s"),Copies,Preview.accepted&&!Preview.mergeSteps.empty()?TEXT(" · MERGE"):TEXT(""));
            if(!Preview.accepted)Card.Availability=Captain.gold<Unit.cost?FString::Printf(TEXT("NEED %d MORE GOLD"),Unit.cost-Captain.gold):TEXT("UNAVAILABLE");
            if(SoloMatch->CurrentPhase()!=wc::Phase::Preparation)Card.Availability=TEXT("NEXT PREPARATION");
            Card.Tooltip=Card.Name+TEXT(" · ")+FString::FromInt(Unit.cost)+TEXT(" gold\n")+Card.Detail+TEXT("\n")+Card.Footer;
            if(!Preview.accepted)Card.Tooltip+=TEXT("\n")+S(Preview.reason);
            return Card;
        };
        Shop->AddSlot().FillWidth(1).Padding(3,0)[FWCArtSlice::MakeShopCard(Data,[this,Slot]{wc::Command C;C.type=wc::CommandType::Buy;C.slot=Slot;SoloCommand(C);},[this,Slot,CanEdit]{
            if(!CanEdit())return false;wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;
            return wc::PreviewRosterCommand(Catalog,SoloMatch->Seats()[0],Buy).accepted;
        })];
    }
    const auto BuyXp=Button([this]{return FString::Printf(TEXT("+%d XP · %d g"),Catalog.rules.buyXpAmount,Catalog.rules.buyXpGold);},[Command]{Command(wc::CommandType::BuyXp);},CanEdit);
    auto Resources=FWCArtSlice::MakePanel(SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(20)).ColorAndOpacity(Parchment).Justification(ETextJustify::Center)
            .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("%d  GOLD"),SoloMatch->Seats()[0].gold):TEXT("—"));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,4)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Justification(ETextJustify::Center)
            .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("LEVEL %d"),SoloMatch->Seats()[0].level):TEXT("—"));})]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).Justification(ETextJustify::Center)
            .Text_Lambda([this]{if(!SoloMatch)return T(TEXT("—"));const auto& Captain=SoloMatch->Seats()[0];const auto Next=Catalog.rules.xpToNext.find(Captain.level);
                return T(Next==Catalog.rules.xpToNext.end()?TEXT("Maximum level"):FString::Printf(TEXT("%d / %d XP"),Captain.xp,Next->second));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,6,0,0)[BuyXp],false,10);
    auto ShopActions=FWCArtSlice::MakePanel(SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Button([this]{return FString::Printf(TEXT("REROLL · %d g"),Catalog.rules.rerollCost);},[Command]{Command(wc::CommandType::Reroll);},CanEdit)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5)[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].shopLocked?TEXT("UNLOCK SHOP"):TEXT("LOCK SHOP");},[Command]{Command(wc::CommandType::ToggleLock);},CanEdit)]
        +SVerticalBox::Slot().AutoHeight()[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].ready?TEXT("READY ✓"):TEXT("READY FOR BATTLE");},[Command]{Command(wc::CommandType::Ready);},[this,CanEdit]{return CanEdit()&&!SoloMatch->Seats()[0].ready;})],false,10);
    auto FormationActions=SNew(SHorizontalBox)
        +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment)
            .Text_Lambda([this]{if(!SoloMatch)return T(TEXT("BENCH"));int Deployed=0;for(const auto& Unit:SoloMatch->Seats()[0].roster)Deployed+=Unit.onBoard;
                return T(ViewedSeat?TEXT("SCOUTING · public board only"):FString::Printf(TEXT("BENCH    ·    DEPLOYED %d / %d"),Deployed,SoloMatch->Seats()[0].level));})]
        +SHorizontalBox::Slot().AutoWidth()[Button([]{return TEXT("Rotate");},[this]{
            if(SoloMatch)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(Unit.id==Selected){wc::Command C;C.type=wc::CommandType::SetFacing;C.unit=Selected;C.facing=wc::Facing((int(Unit.facing)+1)%4);SoloCommand(C);return;}
            Message=TEXT("Select one of your creatures first.");},CanEdit)]
        +SHorizontalBox::Slot().AutoWidth().Padding(4,0)[Button([]{return TEXT("Sell");},[Command]{Command(wc::CommandType::Sell);},CanEdit)]
        +SHorizontalBox::Slot().AutoWidth()[Button([]{return TEXT("Clear");},[this]{Selected=0;PreparationDirty=true;},Always)];
    const auto BenchWidth=[ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.74f,900.f,1420.f));};
    auto Bottom=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(4,2)[SNew(SBox).WidthOverride_Lambda(BenchWidth)[FormationActions]]
        +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,0,0,7)[SNew(SBox).WidthOverride_Lambda(BenchWidth)[Bench]]
        +SVerticalBox::Slot().AutoHeight()[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Fill).Padding(0,0,7,0)[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.13f,135.f,190.f));})[Resources]]
            +SHorizontalBox::Slot().FillWidth(1).HAlign(HAlign_Center)[SNew(SBox).WidthOverride_Lambda([]{return FOptionalSize(FMath::Clamp(float(FWCArtSlice::ViewportSlateSize().X)*.58f,740.f,960.f));})[Shop]]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Fill).Padding(7,0,0,0)[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.14f,145.f,210.f));})[ShopActions]]];

    BoardInput=SNew(SWCSoloBoard).IsEnabled_Lambda([this,TopModal]{return SoloMatch&&TopModal()==EStoryModal::None;})
        .Click([this]{BoardClick(false);}).Key([this](const FKeyEvent& Event){
        const auto Key=Event.GetKey();
        if(Key==EKeys::Left)KeyboardColumn=FMath::Max(0,KeyboardColumn-1);
        else if(Key==EKeys::Right)KeyboardColumn=FMath::Min(Catalog.rules.columns-1,KeyboardColumn+1);
        else if(Key==EKeys::Up)KeyboardRow=FMath::Min(Catalog.rules.rows-1,KeyboardRow+1);
        else if(Key==EKeys::Down)KeyboardRow=FMath::Max(0,KeyboardRow-1);
        else if(Key==EKeys::Enter||Key==EKeys::SpaceBar)SoloCell({KeyboardColumn,KeyboardRow});
        else if(Key==EKeys::Escape){Selected=0;PreparationDirty=true;}
        else return FReply::Unhandled();return FReply::Handled();});
    auto Header=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(SBorder).BorderImage(FWCArtSlice::PanelBrush(true)).Padding(FMargin(8,1))
            [SNew(STextBlock).Font(FWCArtSlice::HeadingFont(27)).ColorAndOpacity(Dark)
                .Justification(ETextJustify::Center).Text(T(TEXT("WONDER CHESS")))]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5)[FWCArtSlice::MakePanel(SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(5,0,15,0)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
                .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("ROUND %d"),SoloMatch->Round()):TEXT("ROUND —"));})]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Justification(ETextJustify::Center)
                .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("%s  ·  %d s%s"),PhaseName(SoloMatch->CurrentPhase()),FMath::CeilToInt(SoloMatch->RemainingMs()/1000.f),SoloPaused?TEXT("  ·  PAUSED"):TEXT("")):TEXT("Loading"));})]
            +SHorizontalBox::Slot().AutoWidth().Padding(0,0,5,0)[Button([this]{return SoloPaused?TEXT("Resume"):TEXT("Pause");},[this]{SoloPaused=!SoloPaused;},[this]{return !AwaitingSaveDecision;})]
            +SHorizontalBox::Slot().AutoWidth()[Button([]{return TEXT("Battle recap");},[RecapOpen]{*RecapOpen=true;},Always)]
            +SHorizontalBox::Slot().AutoWidth().Padding(5,0,0,0)[OpenMenu],false,5)];
    auto Main=SNew(SVerticalBox).IsEnabled_Lambda([TopModal]{return TopModal()==EStoryModal::None;})
        +SVerticalBox::Slot().AutoHeight().Padding(180,5,180,3)[Header]
        +SVerticalBox::Slot().FillHeight(1).Padding(10,0,10,5)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.13f,154.f,208.f));})[Left]]
            +SHorizontalBox::Slot().FillWidth(1).Padding(7,0)[BoardInput.ToSharedRef()]
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.175f,216.f,280.f));})[Right]]]
        +SVerticalBox::Slot().AutoHeight().Padding(10,0)[Bottom]
        +SVerticalBox::Slot().AutoHeight().Padding(10,6,10,7)[FWCArtSlice::MakePanel(SNew(SBox).HeightOverride(28)
            [SAssignNew(MessageBlock,STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true)
                .ToolTipText_Lambda([this]{return T(Message);})],false,6)];

    auto Menu=SNew(SVerticalBox);
    Menu->AddSlot().AutoHeight().Padding(0,0,0,12)[Label(TEXT("TOURNAMENT MENU"))];
    auto OpenCollection=Button([]{return TEXT("Creature & relic collection");},[MenuOpen,CollectionOpen]{*MenuOpen=false;*CollectionOpen=true;},Always);
    OpenCollection->SetTag(TEXT("WC.OpenCollection"));
    Menu->AddSlot().AutoHeight().Padding(0,0,0,8)[OpenCollection];
    Menu->AddSlot().AutoHeight()[Button([this]{return SoloPaused?TEXT("Resume clock"):TEXT("Pause clock");},[this]{SoloPaused=!SoloPaused;},[this]{return !AwaitingSaveDecision;})];
    Menu->AddSlot().AutoHeight().Padding(0,5)[Button([]{return TEXT("Save preparation");},[this]{SaveSolo();},[this]{return SoloMatch&&SoloMatch->CurrentPhase()==wc::Phase::Preparation&&!AwaitingSaveDecision;})];
    Menu->AddSlot().AutoHeight()[Button([]{return TEXT("Load saved preparation");},[this,MenuOpen]{ResumeSolo();*MenuOpen=false;},Always)];
    Menu->AddSlot().AutoHeight().Padding(0,5)[Button([]{return TEXT("New tournament");},[this,MenuOpen]{NewSolo();*MenuOpen=false;},Always)];
    Menu->AddSlot().AutoHeight()[Button([]{return TEXT("Exit game");},[]{FPlatformMisc::RequestExit(false);},Always)];
    Menu->AddSlot().AutoHeight().Padding(0,12)[Button([]{return TEXT("Return to board");},[MenuOpen]{*MenuOpen=false;},Always)];
    Menu->AddSlot().AutoHeight()[Label(TEXT("Choose a creature, then its destination. Arrow keys and Enter work while the board has focus. Escape clears selection. Portrait studies accompany the current gameplay figures."))];
    auto Collection=SNew(SVerticalBox);
    Collection->AddSlot().AutoHeight()[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(18)).ColorAndOpacity(Parchment).Text(T(TEXT("CREATURE & RELIC COLLECTION")))];
    Collection->AddSlot().AutoHeight().Padding(0,6)[Label(TEXT("Discover the six current creatures and twelve relics. This collection is read-only; recruit and equip during preparation."))];
    Collection->AddSlot().AutoHeight().Padding(0,0,0,12)[Button([]{return TEXT("Return to board");},[CollectionOpen]{*CollectionOpen=false;},Always)];
    for(const auto& Unit:Catalog.units){
        const FString Id=S(Unit.id);
        FString Description=S(Unit.race)+TEXT(" / ")+S(Unit.unitClass)+TEXT("  ·  ")+S(Unit.ability.name);
        if(const auto* Full=Metadata.Units.Find(Id);Full&&Full->IsValid()){
            const TSharedPtr<FJsonObject>* Ability=nullptr;FString Tooltip;
            if((*Full)->TryGetObjectField(TEXT("ability"),Ability)&&Ability&&(*Ability)->TryGetStringField(TEXT("tooltip_en"),Tooltip))Description+=TEXT("\n")+Tooltip;
        }
        Collection->AddSlot().AutoHeight().Padding(0,4)[FWCArtSlice::MakePanel(SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(80).HeightOverride(80)[SNew(SImage).Image(FWCArtSlice::Portrait(Id))]]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(7,0)[SNew(SBox).WidthOverride(64).HeightOverride(64)[SNew(SImage).Image(FWCArtSlice::AbilityIcon(Id))]]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,9,0)[SNew(SBox).WidthOverride(32).HeightOverride(32)[SNew(SImage).Image(FWCArtSlice::AbilityIcon(Id))]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Text(T(S(Unit.displayName)))]
                +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text(T(Description))]],false,8)];
    }
    Collection->AddSlot().AutoHeight().Padding(0,12,0,6)[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(17)).ColorAndOpacity(Parchment).Text(T(TEXT("THE TWELVE RELICS")))];
    for(const auto& Relic:Catalog.relics){
        const FString Id=S(Relic.id);
        Collection->AddSlot().AutoHeight().Padding(0,4)[FWCArtSlice::MakePanel(SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(64).HeightOverride(64)[SNew(SImage).Image(FWCArtSlice::RelicIcon(Id))]]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(8,0,12,0)[SNew(SBox).WidthOverride(32).HeightOverride(32)[SNew(SImage).Image(FWCArtSlice::RelicIcon(Id))]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Text(T(S(Relic.name)))]
                +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text(T(S(Relic.description)))]],false,8)];
    }
    Collection->AddSlot().AutoHeight().Padding(0,12,0,0)[Button([]{return TEXT("Return to board");},[CollectionOpen]{*CollectionOpen=false;},Always)];
    auto Draft=SNew(SVerticalBox);
    Draft->AddSlot().AutoHeight().Padding(0,0,0,12)[Label(TEXT("CHOOSE A RELIC\nOne permanent choice. Equip it on a compatible creature during preparation."))];
    for(int Slot=0;Slot<3;++Slot)Draft->AddSlot().AutoHeight().Padding(0,4)[SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(8)
        .IsEnabled_Lambda([this,Slot,CanEdit]{return CanEdit()&&Slot<int(SoloMatch->Seats()[0].relicOffers.size());})
        .OnClicked_Lambda([this,Slot]{wc::Command C;C.type=wc::CommandType::ChooseRelic;C.slot=Slot;SoloCommand(C);return FReply::Handled();})
        [SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(64).HeightOverride(64)[SNew(SImage).Image_Lambda([RelicId,Slot]{return FWCArtSlice::RelicIcon(RelicId(Slot,true));})]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(10,0)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true)
                .Text_Lambda([this,Slot]{return T(RelicText(Slot,true));})]]];
    auto SaveDecision=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,12)[Label(TEXT("CONTINUE YOUR JOURNEY\nA saved preparation is available. Choose how to begin."))]
        +SVerticalBox::Slot().AutoHeight()[Button([]{return TEXT("Load saved preparation");},[this]{ResumeSolo();},Always)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,6)[Button([]{return TEXT("Start a new tournament");},[this]{NewSolo();},Always)]
        +SVerticalBox::Slot().AutoHeight()[Button([]{return TEXT("Exit");},[]{FPlatformMisc::RequestExit(false);},Always)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,8)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{return T(Message);})];
    auto Results=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,10)[Label(TEXT("THE JOURNEY ENDS"))]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{
            FString Text;if(!SoloMatch)return T(Text);const auto Public=SoloMatch->PublicSeats();
            for(int Place=1;Place<=Catalog.rules.seatCount;++Place)for(const auto& Seat:Public)if(Seat.placement==Place)
                Text+=FString::Printf(TEXT("%d.  %s%s\n"),Place,*S(Seat.label),Seat.id==0?TEXT("  ·  YOU"):TEXT(""));
            return T(Text);
        })]
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[Button([]{return TEXT("New tournament");},[this]{NewSolo();},Always)]
        +SVerticalBox::Slot().AutoHeight()[Button([]{return TEXT("Exit game");},[]{FPlatformMisc::RequestExit(false);},Always)];
    const auto Modal=[TopModal](TSharedRef<SWidget> Content,EStoryModal Kind,float Width,FName Tag)->TSharedRef<SWidget>{
        auto Widget=SNew(SWCSoloModal).Active([TopModal,Kind]{return TopModal()==Kind;})
            .Visibility_Lambda([TopModal,Kind]{return TopModal()==Kind?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(SBox).WidthOverride(Width).MaxDesiredHeight(540)[FWCArtSlice::MakePanel(SNew(SScrollBox)+SScrollBox::Slot()[Content],false,22)]];
        Widget->SetTag(Tag);Widget->SynchronizeEnabledState();return Widget;
    };
    auto Recap=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Label(TEXT("BATTLE RECAP"))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,12)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{return T(SoloRecap);})]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{return T(EventText());})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[Button([]{return TEXT("Return to board");},[RecapOpen]{*RecapOpen=false;},Always)];
    Interface=SNew(SWCSoloModalHost)
        +SOverlay::Slot()[Main]
        +SOverlay::Slot()[Modal(Recap,EStoryModal::Recap,560,TEXT("WCModal.Recap"))]
        +SOverlay::Slot()[Modal(Menu,EStoryModal::Menu,440,TEXT("WCModal.Menu"))]
        +SOverlay::Slot()[Modal(Collection,EStoryModal::Collection,760,TEXT("WCModal.Collection"))]
        +SOverlay::Slot()[Modal(Draft,EStoryModal::Draft,570,TEXT("WCModal.Draft"))]
        +SOverlay::Slot()[Modal(Results,EStoryModal::Results,440,TEXT("WCModal.Results"))]
        +SOverlay::Slot()[Modal(SaveDecision,EStoryModal::Save,470,TEXT("WCModal.Save"))];
    GEngine->GameViewport->AddViewportWidgetContent(Interface.ToSharedRef(),50);
    if(Controller){FInputModeGameAndUI Input;Input.SetWidgetToFocus(BoardInput);Input.SetHideCursorDuringCapture(false);Controller->SetInputMode(Input);}
    UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_INTERFACE assets_ready=%d shop_slots=%d bench_slots=%d seats=%d"),
        FWCArtSlice::StorybookResourcesReady(),Catalog.rules.shopSlots,Catalog.rules.benchCapacity,Catalog.rules.seatCount);
    UpdateInterfaceText();
}

void AWCVNextLab::TickSoloExercise()
{
    // Candidate smoke path uses the same commands; real pointer/keyboard evidence is separate.
    if(ExerciseDone||!SoloMatch)return;
    if(!ExerciseChecks)ExerciseChecks=MakeShared<FJsonObject>();
    if(ExerciseStage==0){
        if(FWCArtSlice::IsEnabled())ExerciseChecks->SetBoolField(TEXT("art_slice_portrait_and_relic_loaded"),FWCArtSlice::ResourcesReady());
        if(FWCArtSlice::IsStorybook()){
            TSet<const UObject*> Portraits,Abilities,Relics;
            for(const auto& Unit:Catalog.units){
                Portraits.Add(FWCArtSlice::Portrait(S(Unit.id))->GetResourceObject());
                Abilities.Add(FWCArtSlice::AbilityIcon(S(Unit.id))->GetResourceObject());
            }
            for(const auto& Relic:Catalog.relics)Relics.Add(FWCArtSlice::RelicIcon(S(Relic.id))->GetResourceObject());
            ExerciseChecks->SetBoolField(TEXT("storybook_all_hero_portraits_and_abilities_mapped"),
                !Portraits.Contains(nullptr)&&!Abilities.Contains(nullptr)&&Portraits.Num()==int(Catalog.units.size())&&Abilities.Num()==int(Catalog.units.size()));
            ExerciseChecks->SetBoolField(TEXT("storybook_all_relics_mapped_to_distinct_art"),!Relics.Contains(nullptr)&&Relics.Num()==int(Catalog.relics.size()));
        }
        wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=0;
        if(AwaitingSaveDecision)ResumeSolo();
        const auto BeforeChoice=SoloMatch->SavePreparation();SaveSolo();StartSolo();
        ExerciseChecks->SetBoolField(TEXT("existing_save_blocks_orders"),AwaitingSaveDecision&&!SoloCommand(Buy));
        SaveSolo(true);ResumeSolo();
        ExerciseChecks->SetBoolField(TEXT("existing_save_choice_preserves_checkpoint"),!AwaitingSaveDecision&&SoloMatch->SavePreparation()==BeforeChoice);
        ExerciseChecks->SetBoolField(TEXT("unselected_inspector_requests_selection"),InspectorText().StartsWith(TEXT("Select a creature"))&&!InspectorText().Contains(TEXT("Relic: None")));
        ExerciseChecks->SetBoolField(TEXT("buy"),SoloCommand(Buy));
        ExerciseChecks->SetBoolField(TEXT("purchase_feedback"),Message.Contains(TEXT("Recruited")));
        if(!SoloMatch->Seats()[0].roster.empty()){
            Selected=SoloMatch->Seats()[0].roster.front().id;
            if(FWCArtSlice::IsEnabled()){
                ExerciseChecks->SetBoolField(TEXT("placement_preview_accepts_legal_solo_deployment"),PlacementState({2,2})==2);
                ExerciseChecks->SetBoolField(TEXT("placement_preview_rejects_opponent_half"),PlacementState({2,6})==3);
            }
            ExerciseChecks->SetBoolField(TEXT("deploy"),SoloCell({2,2}));
            const std::string Snapshot=SoloMatch->SavePreparation();SaveSolo();ResumeSolo();
            ExerciseChecks->SetBoolField(TEXT("disk_resume_exact"),SoloMatch->SavePreparation()==Snapshot);
            ScoutSolo(1);ExerciseChecks->SetBoolField(TEXT("scout_rejects_commands"),!SoloCommand(Buy));
            if(FWCArtSlice::IsEnabled())ExerciseChecks->SetBoolField(TEXT("placement_preview_scouts_without_edit_permission"),PlacementState({2,2})==1);
            ScoutSolo(0);
            wc::Command XP;XP.type=wc::CommandType::BuyXp;
            while(SoloMatch->Seats()[0].gold>=Catalog.rules.buyXpGold&&SoloMatch->Seats()[0].level<Catalog.rules.maximumLevel)if(!SoloCommand(XP))break;
            const auto BeforeReject=SoloMatch->SavePreparation();
            ExerciseChecks->SetBoolField(TEXT("insufficient_gold_rejection"),!SoloCommand(XP)&&SoloMatch->SavePreparation()==BeforeReject&&Message.Contains(TEXT("gold")));
        }
        SoloPaused=false;ExerciseStage=1;
    }
    if(SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0){
        if(!SoloMatch->Seats()[0].relicOffers.empty()){
            const auto& Captain=SoloMatch->Seats()[0];
            int Choice=0;
            if(!Captain.roster.empty())for(int I=0;I<int(Captain.relicOffers.size());++I)
                if(wc::RelicCompatible(Catalog.relics[Captain.relicOffers[I]],Catalog.units[Captain.roster.front().definition].ability.mechanic)){Choice=I;break;}
            const int Relic=Captain.relicOffers[Choice];
            wc::Command C;C.type=wc::CommandType::ChooseRelic;C.slot=Choice;
            const bool Drafted=SoloCommand(C);
            if(!ExerciseChecks->HasField(TEXT("relic_draft"))){
                ExerciseChecks->SetBoolField(TEXT("relic_draft"),Drafted&&Message.Contains(TEXT("Relic drafted")));
                Selected=Captain.roster.empty()?0:Captain.roster.front().id;
                C.type=wc::CommandType::EquipRelic;C.slot=Relic;C.unit=Selected;
                ExerciseChecks->SetBoolField(TEXT("relic_equip"),SoloCommand(C)&&Captain.roster.front().relic==Relic&&Message.Contains(TEXT("equipped")));
                ExerciseChecks->SetBoolField(TEXT("selected_inspector_includes_equipped_relic"),InspectorText().Contains(TEXT("Relic: ")+S(Catalog.relics[Relic].name)));
                const auto Snapshot=SoloMatch->SavePreparation();SaveSolo();ResumeSolo();
                ExerciseChecks->SetBoolField(TEXT("equipped_relic_disk_resume"),Snapshot==SoloMatch->SavePreparation());
                Selected=SoloMatch->Seats()[0].roster.front().id;C.type=wc::CommandType::UnequipRelic;C.unit=Selected;
                ExerciseChecks->SetBoolField(TEXT("relic_unequip"),SoloCommand(C)&&SoloMatch->Seats()[0].roster.front().relic<0&&Message.Contains(TEXT("unequipped")));
            }
        }
        if(!SoloMatch->Seats()[0].ready){wc::Command C;C.type=wc::CommandType::Ready;SoloCommand(C);}
    }
    for(int I=0;I<100&&SoloMatch->CurrentPhase()!=wc::Phase::Finished;++I)SoloMatch->Tick(50);
    if(SoloMatch->CurrentPhase()==wc::Phase::Combat&&!ExerciseChecks->HasField(TEXT("combat_cutoff_rejects_order"))){
        Selected=0;
        ExerciseChecks->SetBoolField(TEXT("combat_unselected_inspector_hides_palette"),InspectorText().StartsWith(TEXT("Select a creature"))&&!InspectorText().Contains(TEXT("Relic: None")));
        const auto Before=SoloMatch->Seats()[0];const auto PublicBefore=PublicIdentity(SoloMatch->PublicSeats());
        wc::Command C;C.type=wc::CommandType::Buy;C.slot=0;const bool Rejected=!SoloCommand(C);const auto& After=SoloMatch->Seats()[0];
        ExerciseChecks->SetBoolField(TEXT("combat_cutoff_rejects_order"),Rejected&&After.gold==Before.gold&&After.shop==Before.shop&&
            After.roster.size()==Before.roster.size()&&After.revision==Before.revision&&After.sequence==Before.sequence&&
            PublicIdentity(SoloMatch->PublicSeats())==PublicBefore&&Message.Contains(TEXT("Preparation is locked")));
    }
    if(SoloMatch->Seats()[0].health<=0&&!ExerciseChecks->HasField(TEXT("eliminated_spectating"))){
        for(const auto& Seat:SoloMatch->Seats())if(Seat.health>0){ScoutSolo(Seat.id);break;}
        ExerciseChecks->SetBoolField(TEXT("eliminated_spectating"),ViewedSeat!=0&&SoloMatch->Seats()[ViewedSeat].health>0);
    }
    if(SoloMatch->CurrentPhase()==wc::Phase::Finished){
        ExerciseChecks->SetBoolField(TEXT("finished"),true);ExerciseChecks->SetBoolField(TEXT("invariants"),SoloMatch->InvariantError().empty());
        ExerciseChecks->SetNumberField(TEXT("rounds"),SoloMatch->Round());
        ExerciseChecks->SetNumberField(TEXT("captain_placement"),SoloMatch->Seats()[0].placement);
        const auto Records=SoloMatch->Records().size();
        NewSolo();ExerciseChecks->SetBoolField(TEXT("restart_fresh"),Records>0&&SoloMatch->Records().empty()&&SoloMatch->Round()==1&&!AwaitingSaveDecision);
        ExerciseChecks->SetStringField(TEXT("boundary"),TEXT("Accelerated same-handler package smoke; not human or real input evidence."));
        FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(ExerciseChecks.ToSharedRef(),Writer);
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("solo-exercise.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
        ExerciseDone=true;SoloPaused=true;UE_LOG(LogTemp,Display,TEXT("WC_SOLO_EXERCISE_COMPLETE"));
    }
}
