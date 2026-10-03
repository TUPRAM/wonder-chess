#include "WCVNextLab.h"
#include "WCVNextArtStyle.h"
#include "WCCircularPortrait.h"
#include "Simulation/WonderSaveFile.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
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
TSharedRef<SWidget> SoloTagged(TSharedRef<SWidget> Widget,FName Tag)
{
    Widget->SetTag(Tag);return Widget;
}
TSharedPtr<SWidget> SoloFindTag(const TSharedRef<SWidget>& Widget,FName Tag,bool VisibleOnly=true)
{
    if(VisibleOnly&&!Widget->GetVisibility().IsVisible())return nullptr;
    if(Widget->GetTag()==Tag)return Widget;
    if(auto* Children=Widget->GetChildren())for(int Index=0;Index<Children->Num();++Index)
        if(auto Found=SoloFindTag(Children->GetChildAt(Index),Tag,VisibleOnly))return Found;
    return nullptr;
}
const FButtonStyle* BenchSocketStyle()
{
    static const FButtonStyle Style=[] {
        FButtonStyle Result;
        Result.SetNormal(FSlateRoundedBoxBrush(FLinearColor(.022f,.048f,.049f,.93f),39.f,
                FLinearColor(.42f,.40f,.29f),1.5f))
            .SetHovered(FSlateRoundedBoxBrush(FLinearColor(.050f,.095f,.093f,.97f),39.f,
                FLinearColor(.87f,.75f,.48f),2.f))
            .SetPressed(FSlateRoundedBoxBrush(FLinearColor(.015f,.037f,.038f,.98f),39.f,
                FLinearColor(.94f,.82f,.55f),2.f))
            .SetDisabled(FSlateRoundedBoxBrush(FLinearColor(.026f,.038f,.038f,.76f),39.f,
                FLinearColor(.31f,.34f,.29f),1.f))
            .SetNormalPadding(FMargin(2)).SetPressedPadding(FMargin(2));
        return Result;
    }();
    return &Style;
}
const FSlateBrush* BenchFace(bool Selected)
{
    static const FSlateRoundedBoxBrush Normal(FLinearColor(.024f,.054f,.055f,.92f),39.f,
        FLinearColor(.36f,.41f,.31f),1.f);
    static const FSlateRoundedBoxBrush Active(FLinearColor(.066f,.098f,.087f,.96f),39.f,
        FLinearColor(.94f,.76f,.35f),2.f);
    return Selected?&Active:&Normal;
}
const FSlateBrush* CaptainBadge(bool Active)
{
    static const FSlateRoundedBoxBrush Normal(FLinearColor(.065f,.13f,.14f,.95f),12.f,
        FLinearColor(.39f,.43f,.35f),1.f);
    static const FSlateRoundedBoxBrush Selected(FLinearColor(.13f,.36f,.33f,.98f),12.f,
        FLinearColor(.93f,.75f,.36f),1.5f);
    return Active?&Selected:&Normal;
}
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
    void SetKeyHandler(TFunction<FReply(const FKeyEvent&)> Handler) {KeyHandler=MoveTemp(Handler);}
    void SetAfterSynchronize(TFunction<void()> Handler) {AfterSynchronize=MoveTemp(Handler);}
    virtual FReply OnKeyDown(const FGeometry&,const FKeyEvent& Event) override
    {return KeyHandler?KeyHandler(Event):FReply::Unhandled();}
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
        if(AfterSynchronize)AfterSynchronize();
    }
private:
    TFunction<FReply(const FKeyEvent&)> KeyHandler;
    TFunction<void()> AfterSynchronize;
};
}

FString AWCVNextLab::SoloGuidePhrase(const TCHAR* English,const TCHAR* Indonesian) const
{
    return SoloGuideIndonesian?Indonesian:English;
}

FString AWCVNextLab::SoloGuideTitle() const
{
    switch(SoloGuidePage){
    case 0:return SoloGuidePhrase(TEXT("1. Recruit and upgrade"),TEXT("1. Rekrut dan tingkatkan"));
    case 1:return SoloGuidePhrase(TEXT("2. Place and face"),TEXT("2. Tempatkan dan arahkan"));
    case 2:return SoloGuidePhrase(TEXT("3. Scout and learn from combat"),TEXT("3. Amati lawan dan pelajari pertempuran"));
    case 3:return SoloGuidePhrase(TEXT("4. Relics, saves and results"),TEXT("4. Relik, penyimpanan dan hasil"));
    default:return SoloGuidePhrase(TEXT("5. Keyboard and guide settings"),TEXT("5. Papan ketik dan pengaturan panduan"));
    }
}

FString AWCVNextLab::SoloGuideBody() const
{
    switch(SoloGuidePage){
    case 0:
        if(SoloGuideIndonesian)return FString::Printf(
            TEXT("Saat persiapan, buka Shop untuk melihat %d tawaran milik Anda. Setiap kapten memiliki toko sendiri. Kartu menunjukkan harga saat ini dan jumlah salinan yang dimiliki.\n\nBeli makhluk, lalu pilih slot bangku yang ditempatinya. Tiga salinan setara bergabung otomatis; bintang lebih tinggi mewakili lebih banyak salinan. Bangku memiliki %d slot. Pembelian saat bangku penuh masih bisa berhasil jika penggabungan menyediakan ruang. Pembelian yang tidak tersedia menjelaskan alasannya.\n\nReroll menghabiskan emas yang ditampilkan. Lock mempertahankan tawaran. Membeli XP mengubah level dan peluang toko; periksa nilai saat ini sebelum membeli."),
            Catalog.rules.shopSlots,Catalog.rules.benchCapacity);
        return FString::Printf(
            TEXT("During preparation, open Shop to see your %d offers. Each captain has an independent shop. The card shows its live cost and owned copies.\n\nBuy a creature, then select its occupied bench socket. Three equal copies merge automatically; higher stars represent more copies. The bench has %d slots. A purchase may still work with a full bench if the actual merge makes space. An unavailable purchase explains its reason.\n\nReroll spends the displayed gold. Lock retains your offers. Buying XP changes your level and shop odds; inspect the live values before spending."),
            Catalog.rules.shopSlots,Catalog.rules.benchCapacity);
    case 1:
        return SoloGuidePhrase(
            TEXT("Select an occupied bench socket, then click a legal cell on the near half of your own board. Legal destinations and the selected ability preview explain placement. Deployment is limited by your current level.\n\nClick a deployed creature to select it. Click another destination to move it; an occupied board destination can swap creatures. A successful move clears selection. To return a creature to the bench, select it on the board and click an empty bench socket. Clicking an occupied bench socket selects its occupant.\n\nUse Rotate selected to change facing. Inspect the preview before committing: protection, lanes and charge paths depend on the actual ability. Placement and purchases are locked during combat."),
            TEXT("Pilih slot bangku yang berisi makhluk, lalu klik petak yang sah di bagian dekat papan Anda. Tujuan yang sah dan pratinjau kemampuan makhluk terpilih membantu penempatan. Jumlah makhluk di papan dibatasi oleh level Anda.\n\nKlik makhluk di papan untuk memilihnya. Klik tujuan lain untuk memindahkannya; tujuan yang sudah terisi dapat menukar makhluk. Pemindahan yang berhasil menghapus pilihan. Untuk mengembalikan makhluk ke bangku, pilih di papan lalu klik slot bangku kosong. Klik slot bangku yang terisi untuk memilih penghuninya.\n\nGunakan Rotate selected untuk mengubah arah. Periksa pratinjau sebelum menetapkan posisi: perlindungan, jalur dan lintasan serbuan mengikuti kemampuan yang sebenarnya. Penempatan dan pembelian terkunci saat pertempuran."));
    case 2:
        return SoloGuidePhrase(
            TEXT("Click a captain in the standings to scout that public formation. Check whose board is shown. Opponent shops, benches and draft choices stay private. Return to Your board before issuing your orders.\n\nReady ends your preparation decision when the round is ready to proceed; editing cancels your readiness. The shared preparation clock also ends the phase. Combat then runs automatically.\n\nWatch who acts, where the ability commits, and which creature is actually affected. Healing shows effective restoration; a push requires a changed position. Recap records battle facts and captain health lost. Use those facts to choose a practical formation or recruitment change after a loss. Trait counts are visible, but trait bonuses are inactive in this candidate."),
            TEXT("Klik kapten pada daftar peringkat untuk mengamati formasi publiknya. Periksa papan siapa yang sedang ditampilkan. Toko, bangku dan pilihan draf lawan tetap pribadi. Kembali ke Your board sebelum memberi perintah.\n\nReady menyelesaikan keputusan persiapan saat ronde siap berlanjut; perubahan membatalkan kesiapan Anda. Waktu persiapan bersama juga mengakhiri fase. Pertempuran kemudian berjalan otomatis.\n\nAmati siapa yang bertindak, tempat kemampuan ditetapkan dan makhluk yang benar-benar terkena. Penyembuhan menunjukkan pemulihan efektif; dorongan harus mengubah posisi. Recap mencatat fakta pertempuran dan kesehatan kapten yang hilang. Gunakan fakta tersebut untuk mengubah formasi atau rekrutmen setelah kalah. Jumlah trait ditampilkan, tetapi bonus trait belum aktif pada kandidat ini."));
    case 3:
        if(SoloGuideIndonesian)return FString::Printf(
            TEXT("Saat draf relik muncul, pilih salah satu tawaran yang tersedia. Baca efek, kekurangan dan kecocokannya. Pilih makhluk milik Anda, lalu pilih relik dalam inventaris untuk memasangnya saat persiapan. Satu tim dapat memasang paling banyak %d relik, satu pada setiap makhluk. Unequip selected melepas relik makhluk terpilih.\n\nGunakan Menu > Save preparation pada fase persiapan yang sah. Memuat memulihkan persiapan tersimpan, bukan pertempuran setelahnya. Simpanan yang sudah ada meminta pilihan untuk memuat atau memulai turnamen baru. Baca pesan pemulihan sebelum mencoba lagi; simpanan yang sah harus dipertahankan.\n\nTersingkirnya Anda berbeda dari penentuan pemenang akhir. Anda dapat mengamati kapten yang masih hidup selama turnamen berlanjut. Hasil akhir menunjukkan peringkat; New tournament memulai dari awal."),
            Catalog.rules.maximumRelics);
        return FString::Printf(
            TEXT("When a relic draft appears, choose one of the real offers. Read its effect, drawback and compatibility. Select an owned creature, then choose an inventory relic to equip it during preparation. A team may equip at most %d relics, with one per creature. Unequip selected removes the selected creature's relic.\n\nUse Menu > Save preparation at a valid preparation boundary. Loading restores that saved preparation, not a later combat. Existing saved games ask whether to load or start a new tournament. Read a recovery error before retrying; the valid checkpoint must be preserved.\n\nPersonal elimination is different from the final winner. You can inspect living captains while the tournament continues. Final results show placements; New tournament starts fresh."),
            Catalog.rules.maximumRelics);
    default:
        return SoloGuidePhrase(
            TEXT("Tab / Shift+Tab moves focus between enabled controls. Enter or Space activates a focused button.\n\nWhen the board has focus, arrow keys move the cell cursor; Enter or Space selects a creature or places the selection. Escape clears a board selection. F1 opens this guide; F1 or Escape closes it. Return restores board focus when no other modal is required.\n\nThe solo clock pauses while this guide is open and returns to its earlier pause state when you close it. Guide language and Guide text size affect this guide only. Creature sounds controls the current Bellback and Silkmother presentation audio. These choices last for this game session."),
            TEXT("Tab / Shift+Tab memindahkan fokus antar kontrol yang aktif. Enter atau Spasi mengaktifkan tombol yang memiliki fokus.\n\nSaat papan memiliki fokus, tombol panah memindahkan kursor petak; Enter atau Spasi memilih makhluk atau menempatkan pilihan. Escape menghapus pilihan pada papan. F1 membuka panduan ini; F1 atau Escape menutupnya. Kembali memulihkan fokus papan jika tidak ada dialog lain yang wajib dibuka.\n\nWaktu solo berhenti sementara saat panduan dibuka dan kembali ke keadaan jeda sebelumnya saat ditutup. Bahasa panduan dan Ukuran teks panduan hanya memengaruhi panduan ini. Suara makhluk mengatur audio presentasi Bellback dan Silkmother saat ini. Pilihan ini berlaku selama sesi permainan ini."));
    }
}

void AWCVNextLab::OpenSoloGuide()
{
    if(!SoloMode||!Storybook||SoloGuideOpen||AwaitingSaveDecision||!SoloMatch||
        SoloMatch->CurrentPhase()==wc::Phase::Finished||
        (SoloMatch->CurrentPhase()==wc::Phase::Preparation&&ViewedSeat==0&&!SoloMatch->Seats()[0].relicOffers.empty()))return;
    SoloGuideWasPaused=SoloPaused;SoloPaused=true;SoloGuideOpen=true;SoloGuideReturnFocus=false;
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_GUIDE_OPEN page=%d language=%s previous_paused=%d"),
        SoloGuidePage,SoloGuideIndonesian?TEXT("id"):TEXT("en"),SoloGuideWasPaused);
}

void AWCVNextLab::CloseSoloGuide()
{
    if(!SoloGuideOpen)return;
    SoloGuideOpen=false;SoloPaused=SoloGuideWasPaused;SoloGuideReturnFocus=true;
    UE_LOG(LogTemp,Display,TEXT("WC_SOLO_GUIDE_CLOSE restored_paused=%d"),SoloPaused);
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
    SoloGuideOpen=false;SoloGuideReturnFocus=false;SoloBenchReturnFocus=false;
    ClearUpgradePresentation();
    SoloMatch=std::make_unique<wc::Match>(Catalog,uint64(Seed),1,false);
    SoloPaused=false;AwaitingSaveDecision=false;ViewedSeat=0;Selected=0;ShopOpen=false;ShopDismissedRound=0;Accumulator=0;LastSoloRound=-1;LastSoloRecord=0;
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
    if(Reply.accepted){
        if(Command.type==wc::CommandType::Move){Selected=0;PreparationDirty=true;}
        SyncSoloFormation();SaveSolo(true);
    }
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
        Message=TEXT("Selected. Click another board cell to move or swap, or an empty bench slot to return it. Escape clears selection.");return true;}
    Message=TEXT("Select an owned creature on the bench or board first.");return false;
}

void AWCVNextLab::SelectBench(int Slot)
{
    if(!SoloMatch||ViewedSeat!=0||AwaitingSaveDecision||SoloGuideOpen||
        SoloMatch->CurrentPhase()!=wc::Phase::Preparation||SoloMatch->Seats()[0].health<=0||
        !SoloMatch->Seats()[0].relicOffers.empty())return;
    const auto& Roster=SoloMatch->Seats()[0].roster;
    const auto At=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return !Unit.onBoard&&Unit.bench==Slot;});
    const auto Chosen=std::find_if(Roster.begin(),Roster.end(),[&](const auto& Unit){return Unit.id==Selected;});
    if(At!=Roster.end()){
        Selected=At->id;Palette=At->definition;BrushStar=At->star;PreparationDirty=true;
        KeyboardColumn=FMath::Clamp(KeyboardColumn,0,Catalog.rules.columns-1);
        KeyboardRow=FMath::Clamp(KeyboardRow,0,Catalog.rules.deploymentRows-1);
        Message=SoloKeyboardTargetText();
        // Apply after the button click and modal synchronization, so mandatory
        // choices keep focus and the bench button cannot recapture Enter.
        if(Storybook)SoloBenchReturnFocus=true;
        else if(BoardInput.IsValid())FSlateApplication::Get().SetKeyboardFocus(BoardInput,EFocusCause::SetDirectly);
        return;
    }
    if(Chosen!=Roster.end()){
        wc::Command Move;Move.type=wc::CommandType::Move;Move.unit=Selected;Move.slot=Slot;Move.toBoard=false;SoloCommand(Move);return;
    }
    Message=TEXT("Empty bench slot. Select a deployed creature first to move it here.");
}

FString AWCVNextLab::SoloKeyboardTargetText() const
{
    const FString Cell=FString::Printf(TEXT("%c%d"),TCHAR('A'+KeyboardColumn),KeyboardRow+1);
    const FString Target=TEXT("Keyboard target ")+Cell;
    if(!SoloMatch||ViewedSeat!=0||SoloMatch->CurrentPhase()!=wc::Phase::Preparation)
        return Target+TEXT(" · Enter: inspect; arrows: target.");
    if(KeyboardRow>=Catalog.rules.deploymentRows)
        return Target+TEXT(" · Opponent cell. Choose a near-half tile.");
    for(const auto& Unit:SoloMatch->Seats()[0].roster)if(Unit.id==Selected)
        return Target+TEXT(" · ")+S(Catalog.units[Unit.definition].name)+
            (Unit.onBoard?TEXT(" · Enter: move; arrows: target."):TEXT(" · Enter: deploy; arrows: target. Click also works."));
    return Target+TEXT(" · Enter: select; arrows: target.");
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
        Seed=int(SoloMatch->Seed());ViewedSeat=0;Selected=0;ShopOpen=false;ShopDismissedRound=0;SoloPaused=true;Accumulator=0;
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
    Result+=Catalog.traits.empty()?TEXT("\n\nTraits are inactive in this study candidate."):TEXT("\n\nHuman, Orc, Beastkin, Dragonkin, Tank, Fighter and Mage bonuses are active at 2 / 4 distinct heroes.");
    Result+=TEXT(" Relics shown on inspected deployed creatures are public.");
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
            if(Unit.id=="wc_vn_shieldbearer")Card.Tooltip+=TEXT("\nBellback portrait study; the board uses a gameplay proxy.");
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
        else return FReply::Unhandled();
        if(Key==EKeys::Left||Key==EKeys::Right||Key==EKeys::Up||Key==EKeys::Down)Message=SoloKeyboardTargetText();
        return FReply::Handled();});
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
    enum class EStoryModal {None,Shop,Recap,Menu,Collection,Guide,Draft,Results,Save};
    const auto TopModal=[this,CanEdit,MenuOpen,RecapOpen,CollectionOpen]{
        if(AwaitingSaveDecision)return EStoryModal::Save;
        if(SoloMatch&&SoloMatch->CurrentPhase()==wc::Phase::Finished)return EStoryModal::Results;
        if(CanEdit()&&!SoloMatch->Seats()[0].relicOffers.empty())return EStoryModal::Draft;
        if(SoloGuideOpen)return EStoryModal::Guide;
        if(*CollectionOpen)return EStoryModal::Collection;
        if(*MenuOpen)return EStoryModal::Menu;
        if(*RecapOpen)return EStoryModal::Recap;
        if(CanEdit()&&(ShopOpen||SoloMatch->Round()>ShopDismissedRound))return EStoryModal::Shop;
        return EStoryModal::None;
    };
    auto OpenMenu=Button([]{return TEXT("Menu");},[MenuOpen]{*MenuOpen=true;},Always);
    OpenMenu->SetTag(TEXT("WC.OpenMenu"));
    const auto GuideAvailable=[this,TopModal]{const auto Kind=TopModal();return SoloMatch&&LoadError.IsEmpty()&&Kind!=EStoryModal::Save&&Kind!=EStoryModal::Draft&&Kind!=EStoryModal::Results;};
    const auto OpenGuide=[this,MenuOpen,RecapOpen,CollectionOpen]{
        OpenSoloGuide();
        if(SoloGuideOpen){*MenuOpen=false;*RecapOpen=false;*CollectionOpen=false;}
    };
    const auto RelicId=[this](int Slot,bool Offer){
        if(!SoloMatch||ViewedSeat!=0)return FString();
        const auto& Captain=SoloMatch->Seats()[0];const auto& Items=Offer?Captain.relicOffers:Captain.ownedRelics;
        return Slot<int(Items.size())?S(Catalog.relics[Items[Slot]].id):FString();
    };
    auto Traits=SNew(SVerticalBox);
    Traits->AddSlot().AutoHeight().Padding(0,0,0,8)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Text(T(TEXT("TRAITS")))];
    Traits->AddSlot().AutoHeight().Padding(0,0,0,7)[Label(Catalog.traits.empty()?TEXT("Deployed counts · bonuses inactive"):TEXT("Deployed counts · stat bonuses active at 2 / 4"))];
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
        Traits->AddSlot().AutoHeight().Padding(0,2)[SNew(SBox)
            .Visibility_Lambda([Count]{return Count()>0?EVisibility::Visible:EVisibility::Collapsed;})[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[FWCArtSlice::MakeTraitGlyph(Identity.Key,29,[Count]{return Count()>0;})]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(6,0)[SNew(STextBlock).Font(Small).AutoWrapText(true)
                .ColorAndOpacity_Lambda([Count,Parchment]{return Count()>0?Parchment:FLinearColor(.34f,.37f,.30f);}).Text(T(Name))]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
                .Text_Lambda([Count]{return T(FString::FromInt(Count()));})]]];
    }
    auto Inventory=SNew(SVerticalBox);
    Inventory->AddSlot().AutoHeight().Padding(0,10,0,5)[Label(TEXT("RELICS"))];
    Inventory->AddSlot().AutoHeight().Padding(0,0,0,3)[SNew(SBox)
        .Visibility_Lambda([this]{return !SoloMatch||ViewedSeat!=0||SoloMatch->Seats()[0].ownedRelics.empty()?EVisibility::Visible:EVisibility::Collapsed;})
        [Label(TEXT("No relics owned"))]];
    for(int Slot=0;Slot<3;++Slot){
        const auto ItemId=[RelicId,Slot]{return RelicId(Slot,false);};
        Inventory->AddSlot().AutoHeight().Padding(0,2)[SNew(SBox)
            .Visibility_Lambda([this,Slot]{return SoloMatch&&ViewedSeat==0&&Slot<int(SoloMatch->Seats()[0].ownedRelics.size())?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(3)
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
                        return T(Slot<int(Items.size())?S(Catalog.relics[Items[Slot]].name):TEXT("Empty slot"));})]]]];
    }
    Inventory->AddSlot().AutoHeight().Padding(0,4)[SNew(SBox)
        .Visibility_Lambda([this]{return SoloMatch&&ViewedSeat==0&&!SoloMatch->Seats()[0].ownedRelics.empty()?EVisibility::Visible:EVisibility::Collapsed;})
        [Button([]{return TEXT("Unequip selected");},[Command]{Command(wc::CommandType::UnequipRelic);},CanEdit)]];
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
                +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(1,0,6,0)[SNew(SBox).WidthOverride(24).HeightOverride(24)
                    [SNew(SBorder).BorderImage_Lambda([this,Seat]{return CaptainBadge(Seat==ViewedSeat);}).Padding(0)
                        .HAlign(HAlign_Center).VAlign(VAlign_Center)
                        [SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
                            .Text_Lambda([this,Seat]{
                                if(!SoloMatch)return T(TEXT("?"));
                                const FString Name=Seat==0?TEXT("You"):S(SoloMatch->PublicSeats()[Seat].label);
                                return T(Name.IsEmpty()?TEXT("?"):Name.Left(1).ToUpper());})]]]
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
    auto Inspector=SNew(SBox).Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
        .HeightOverride_Lambda([ViewSize,SelectedDefinition]{return FOptionalSize(
        SelectedDefinition()>=0?FMath::Clamp(float(ViewSize().Y)*.33f,210.f,340.f):44.f);})
        [FWCArtSlice::MakePanel(SNew(SScrollBox)+SScrollBox::Slot()[SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(SBox).HeightOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().Y)*.11f,72.f,120.f));})
            .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SImage).Image_Lambda([SelectedId]{return FWCArtSlice::Portrait(SelectedId());})]]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,4)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Dark).AutoWrapText(true)
            .Text_Lambda([this,SelectedDefinition]{const int Def=SelectedDefinition();return T(Def>=0?S(Catalog.units[Def].displayName):TEXT("Select a creature"));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,2)[SNew(SBox)
            .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(38).HeightOverride(38)
                .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
                [SNew(SImage).Image_Lambda([SelectedId]{return FWCArtSlice::AbilityIcon(SelectedId());})]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(5,0)[SNew(STextBlock).Font(Small).ColorAndOpacity(Dark).AutoWrapText(true)
                .Text_Lambda([this,SelectedDefinition]{const int Def=SelectedDefinition();if(Def<0)return T(TEXT("Inspect a bench or board creature to see its ability and stats."));
                    const auto& Unit=Catalog.units[Def];return T(S(Unit.ability.name)+TEXT("\n")+(Unit.range<=1?TEXT("Melee"):TEXT("Ranged")));})]]]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5)[SNew(SBox)
            .Visibility_Lambda([SelectedDefinition]{return SelectedDefinition()>=0?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(STextBlock).Font(Small).ColorAndOpacity(Dark).AutoWrapText(true)
                .Text_Lambda([this]{return T(InspectorText().Replace(TEXT(" in this lab"),TEXT("")));})]]],true,10)];
    auto Right=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[FWCArtSlice::MakePanel(Standings,false,9)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,6,0,0)[Inspector];

    auto Bench=SNew(SHorizontalBox);
    for(int Slot=0;Slot<Catalog.rules.benchCapacity;++Slot){
        const auto Piece=[this,Slot]() -> const wc::OwnedUnit* {
            if(SoloMatch&&ViewedSeat==0)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(!Unit.onBoard&&Unit.bench==Slot)return &Unit;
            return nullptr;
        };
        const auto SocketSize=[ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().Y)*.078f,78.f,90.f));};
        const auto PortraitSize=[ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().Y)*.067f,68.f,78.f));};
        Bench->AddSlot().FillWidth(1).HAlign(HAlign_Center).Padding(2,0)[SNew(SBox)
            .WidthOverride_Lambda(SocketSize).HeightOverride_Lambda(SocketSize)
            [SNew(SButton).ButtonStyle(BenchSocketStyle()).ContentPadding(2)
                .IsEnabled_Lambda(CanEdit).ToolTipText_Lambda([this,Slot,Piece]{return T(BenchText(Slot)+(Piece()?TEXT("\nClick to select this creature; then choose a legal board tile."):TEXT("\nClick with a selected creature to move it into this empty slot.")));})
                .OnPressed_Lambda([this,Slot]{BenchPressed(Slot);})
                .OnClicked_Lambda([this,Slot]{SelectBench(Slot);return FReply::Handled();})
                [SNew(SBorder).BorderImage_Lambda([this,Piece]{const auto* Unit=Piece();
                        return BenchFace(Unit&&(Selected==Unit->id||UpgradePulse(Unit->id)>0));}).Padding(2)
                    [SNew(SOverlay)
                        +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(SBox)
                            .WidthOverride_Lambda(PortraitSize).HeightOverride_Lambda(PortraitSize)
                            [SNew(SWCCircularPortrait).Image_Lambda([this,Piece]{const auto* Unit=Piece();
                                return Unit?FWCArtSlice::Portrait(S(Catalog.units[Unit->definition].id)):nullptr;})]]
                        +SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).Text(T(FString::FromInt(Slot+1)))]
                        +SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Bottom)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment)
                            .Text_Lambda([Piece]{const auto* Unit=Piece();return T(Unit?FString::ChrN(Unit->star,TCHAR('*')):FString());})]]]]];
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
        Shop->AddSlot().FillWidth(1).Padding(3,0)[SoloTagged(FWCArtSlice::MakeShopCard(Data,[this,Slot]{wc::Command C;C.type=wc::CommandType::Buy;C.slot=Slot;SoloCommand(C);},[this,Slot,CanEdit]{
            if(!CanEdit())return false;wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Slot;
            return wc::PreviewRosterCommand(Catalog,SoloMatch->Seats()[0],Buy).accepted;
        }),FName(*FString::Printf(TEXT("WC.Shop.Slot%d"),Slot)))];
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
    auto ShopActions=SNew(SHorizontalBox)
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,5,0)[Button([this]{return FString::Printf(TEXT("REROLL · %d g"),Catalog.rules.rerollCost);},[Command]{Command(wc::CommandType::Reroll);},CanEdit)]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,7,0)[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].shopLocked?TEXT("UNLOCK SHOP"):TEXT("LOCK SHOP");},[Command]{Command(wc::CommandType::ToggleLock);},CanEdit)];
    auto FormationActions=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().VAlign(VAlign_Center)[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment)
            .Text_Lambda([this]{if(!SoloMatch)return T(TEXT("BENCH"));int Deployed=0;for(const auto& Unit:SoloMatch->Seats()[0].roster)Deployed+=Unit.onBoard;
                return T(ViewedSeat?TEXT("SCOUTING · public board only"):FString::Printf(TEXT("DEPLOYED %d / %d"),Deployed,SoloMatch->Seats()[0].level));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,5,0,0)[SNew(SHorizontalBox)
        +SHorizontalBox::Slot().FillWidth(1)[Button([]{return TEXT("Rotate");},[this]{
            if(SoloMatch)for(const auto& Unit:SoloMatch->Seats()[0].roster)if(Unit.id==Selected){wc::Command C;C.type=wc::CommandType::SetFacing;C.unit=Selected;C.facing=wc::Facing((int(Unit.facing)+1)%4);SoloCommand(C);return;}
            Message=TEXT("Select one of your creatures first.");},CanEdit)]
        +SHorizontalBox::Slot().FillWidth(1).Padding(4,0)[SoloTagged(Button([]{return TEXT("Sell");},[Command]{Command(wc::CommandType::Sell);},CanEdit),TEXT("WC.Sell"))]
        +SHorizontalBox::Slot().FillWidth(1)[Button([]{return TEXT("Clear");},[this]{Selected=0;PreparationDirty=true;},Always)]];
    Right->AddSlot().AutoHeight().Padding(0,6,0,0)[FWCArtSlice::MakePanel(FormationActions,false,7)];
    const auto BenchWidth=[ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.74f,900.f,1420.f));};
    auto Bottom=SNew(SBox).HAlign(HAlign_Center).Padding(FMargin(0,0,0,4))
        [SNew(SBox).WidthOverride_Lambda(BenchWidth)[Bench]];
    auto LeftRail=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Left]
        +SVerticalBox::Slot().AutoHeight().Padding(0,6,0,0)[Resources];
    auto ShopPanel=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,10)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(19)).ColorAndOpacity(Parchment)
                .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("ROUND %d  ·  RECRUIT"),SoloMatch->Round()):TEXT("RECRUIT"));})]
            +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[ShopActions]
            +SHorizontalBox::Slot().AutoWidth().Padding(4,0)[Button([]{return TEXT("How to play / Cara bermain");},OpenGuide,GuideAvailable)]
            +SHorizontalBox::Slot().AutoWidth()[SoloTagged(Button([]{return TEXT("Close shop");},[this]{
                if(SoloMatch)ShopDismissedRound=SoloMatch->Round();ShopOpen=false;
            },Always),TEXT("WC.Shop.Close"))]]
        +SVerticalBox::Slot().AutoHeight()[Shop]
        +SVerticalBox::Slot().AutoHeight().Padding(3,10,3,0)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),13)).ColorAndOpacity(Parchment)
            .Text_Lambda([this]{
                if(!SoloMatch)return T(TEXT(""));
                const auto& Captain=SoloMatch->Seats()[0];
                FString Odds=FString::Printf(TEXT("%d gold  ·  Level %d shop odds"),Captain.gold,Captain.level);
                const auto It=Catalog.rules.shopWeights.find(Captain.level);
                if(It!=Catalog.rules.shopWeights.end())for(int Tier=0;Tier<5;++Tier)
                    Odds+=FString::Printf(TEXT("     %d-cost %d%%"),Tier+1,It->second[Tier]/100);
                return T(Odds);
            })];

    BoardInput=SNew(SWCSoloBoard).IsEnabled_Lambda([this,TopModal]{return SoloMatch&&TopModal()==EStoryModal::None;})
        .Click([this]{BoardClick(false);}).Key([this](const FKeyEvent& Event){
        const auto Key=Event.GetKey();
        if(Key==EKeys::Left)KeyboardColumn=FMath::Max(0,KeyboardColumn-1);
        else if(Key==EKeys::Right)KeyboardColumn=FMath::Min(Catalog.rules.columns-1,KeyboardColumn+1);
        else if(Key==EKeys::Up)KeyboardRow=FMath::Min(Catalog.rules.rows-1,KeyboardRow+1);
        else if(Key==EKeys::Down)KeyboardRow=FMath::Max(0,KeyboardRow-1);
        else if(Key==EKeys::Enter||Key==EKeys::SpaceBar)SoloCell({KeyboardColumn,KeyboardRow});
        else if(Key==EKeys::Escape){Selected=0;PreparationDirty=true;}
        else return FReply::Unhandled();
        if(Key==EKeys::Left||Key==EKeys::Right||Key==EKeys::Up||Key==EKeys::Down)Message=SoloKeyboardTargetText();
        return FReply::Handled();});
    auto Header=FWCArtSlice::MakePanel(SNew(SHorizontalBox)
        +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(4,0,16,0)[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(17)).ColorAndOpacity(Parchment).Text(T(TEXT("WONDER CHESS")))]
        +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0,0,12,0)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
            .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("ROUND %d"),SoloMatch->Round()):TEXT("ROUND —"));})]
        +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment).Justification(ETextJustify::Center)
            .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("%s  ·  %d s%s"),PhaseName(SoloMatch->CurrentPhase()),FMath::CeilToInt(SoloMatch->RemainingMs()/1000.f),SoloPaused?TEXT("  ·  PAUSED"):TEXT("")):TEXT("Loading"));})]
        +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(12,0)[SNew(STextBlock).Font(Bold).ColorAndOpacity(Parchment)
            .Text_Lambda([this]{return T(SoloMatch?FString::Printf(TEXT("%d g  ·  Lv %d"),SoloMatch->Seats()[0].gold,SoloMatch->Seats()[0].level):TEXT(""));})]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,4,0)[SoloTagged(Button([]{return TEXT("Shop");},[this]{ShopOpen=true;},CanEdit),TEXT("WC.OpenShop"))]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,4,0)[Button([this]{return SoloMatch&&SoloMatch->Seats()[0].ready?TEXT("Ready ✓"):TEXT("Ready");},[Command]{Command(wc::CommandType::Ready);},[this,CanEdit]{return CanEdit()&&!SoloMatch->Seats()[0].ready;})]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,4,0)[Button([this]{return SoloPaused?TEXT("Resume"):TEXT("Pause");},[this]{SoloPaused=!SoloPaused;},[this]{return !AwaitingSaveDecision;})]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,4,0)[SoloTagged(Button([]{return TEXT("Recap");},[RecapOpen]{*RecapOpen=true;},Always),TEXT("WC.OpenRecap"))]
        +SHorizontalBox::Slot().AutoWidth().Padding(0,0,4,0)[Button([]{return TEXT("Help · F1");},OpenGuide,GuideAvailable)]
        +SHorizontalBox::Slot().AutoWidth()[OpenMenu],false,4);
    auto Main=SNew(SVerticalBox).IsEnabled_Lambda([TopModal]{return TopModal()==EStoryModal::None;})
        +SVerticalBox::Slot().AutoHeight().Padding(7,5,7,3)[Header]
        +SVerticalBox::Slot().FillHeight(1).Padding(7,0,7,4)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.115f,140.f,190.f));})[LeftRail]]
            +SHorizontalBox::Slot().FillWidth(1).Padding(5,0)[BoardInput.ToSharedRef()]
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride_Lambda([ViewSize]{return FOptionalSize(FMath::Clamp(float(ViewSize().X)*.16f,190.f,255.f));})[Right]]]
        +SVerticalBox::Slot().AutoHeight().Padding(7,0)[Bottom]
        +SVerticalBox::Slot().AutoHeight().Padding(7,3,7,5)[FWCArtSlice::MakePanel(SNew(SBox).HeightOverride(25)
            [SAssignNew(MessageBlock,STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true)
                .ToolTipText_Lambda([this]{return T(Message);})],false,6)];

    auto Menu=SNew(SVerticalBox);
    Menu->AddSlot().AutoHeight().Padding(0,0,0,12)[Label(TEXT("TOURNAMENT MENU"))];
    auto OpenCollection=Button([]{return TEXT("Creature & relic collection");},[MenuOpen,CollectionOpen]{*MenuOpen=false;*CollectionOpen=true;},Always);
    OpenCollection->SetTag(TEXT("WC.OpenCollection"));
    Menu->AddSlot().AutoHeight().Padding(0,0,0,8)[OpenCollection];
    Menu->AddSlot().AutoHeight().Padding(0,0,0,8)[Button([]{return TEXT("How to play / Guide settings · F1");},OpenGuide,GuideAvailable)];
    Menu->AddSlot().AutoHeight()[Button([this]{return SoloPaused?TEXT("Resume clock"):TEXT("Pause clock");},[this]{SoloPaused=!SoloPaused;},[this]{return !AwaitingSaveDecision;})];
    Menu->AddSlot().AutoHeight().Padding(0,5)[Button([]{return TEXT("Save preparation");},[this]{SaveSolo();},[this]{return SoloMatch&&SoloMatch->CurrentPhase()==wc::Phase::Preparation&&!AwaitingSaveDecision;})];
    Menu->AddSlot().AutoHeight()[SoloTagged(Button([]{return TEXT("Load saved preparation");},[this,MenuOpen]{ResumeSolo();*MenuOpen=false;},Always),TEXT("WC.Menu.Load"))];
    Menu->AddSlot().AutoHeight().Padding(0,5)[SoloTagged(Button([]{return TEXT("New tournament");},[this,MenuOpen]{NewSolo();*MenuOpen=false;},Always),TEXT("WC.Menu.New"))];
    Menu->AddSlot().AutoHeight()[Button([]{return TEXT("Exit game");},[]{FPlatformMisc::RequestExit(false);},Always)];
    Menu->AddSlot().AutoHeight().Padding(0,12)[SoloTagged(Button([]{return TEXT("Return to board");},[MenuOpen]{*MenuOpen=false;},Always),TEXT("WC.Menu.Return"))];
    Menu->AddSlot().AutoHeight()[Label(TEXT("Choose a creature, then its destination. Arrow keys and Enter work while the board has focus. Escape clears selection. Portrait studies accompany the current gameplay figures."))];
    auto Collection=SNew(SVerticalBox);
    Collection->AddSlot().AutoHeight()[SNew(STextBlock).Font(FWCArtSlice::HeadingFont(18)).ColorAndOpacity(Parchment).Text(T(TEXT("CREATURE & RELIC COLLECTION")))];
    Collection->AddSlot().AutoHeight().Padding(0,6)[Label(FString::Printf(TEXT("Discover %d current creatures and %d relics. This collection is read-only; recruit and equip during preparation."),int(Catalog.units.size()),int(Catalog.relics.size())))];
    Collection->AddSlot().AutoHeight().Padding(0,0,0,12)[SoloTagged(Button([]{return TEXT("Return to board");},[CollectionOpen]{*CollectionOpen=false;},Always),TEXT("WC.Collection.Return"))];
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
        +SVerticalBox::Slot().AutoHeight()[SoloTagged(Button([]{return TEXT("Load saved preparation");},[this]{ResumeSolo();},Always),TEXT("WC.Save.Load"))]
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
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[SoloTagged(Button([]{return TEXT("New tournament");},[this]{NewSolo();},Always),TEXT("WC.Results.New"))]
        +SVerticalBox::Slot().AutoHeight()[Button([]{return TEXT("Exit game");},[]{FPlatformMisc::RequestExit(false);},Always)];
    const auto Modal=[TopModal](TSharedRef<SWidget> Content,EStoryModal Kind,float Width,FName Tag)->TSharedRef<SWidget>{
        auto Widget=SNew(SWCSoloModal).Active([TopModal,Kind]{return TopModal()==Kind;})
            .Visibility_Lambda([TopModal,Kind]{return TopModal()==Kind?EVisibility::Visible:EVisibility::Collapsed;})
            [SNew(SBox).WidthOverride(Width).MaxDesiredHeight(540)[FWCArtSlice::MakePanel(SNew(SScrollBox)
                // Tab focus must reveal wrapped guide controls at enlarged text sizes.
                .ScrollWhenFocusChanges(Kind==EStoryModal::Guide?EScrollWhenFocusChanges::InstantScroll:EScrollWhenFocusChanges::NoScroll)
                .NavigationDestination(EDescendantScrollDestination::IntoView)
                .NavigationScrollPadding(Kind==EStoryModal::Guide?12.f:0.f)
                +SScrollBox::Slot()[Content],false,22)]];
        Widget->SetTag(Tag);Widget->SynchronizeEnabledState();return Widget;
    };
    auto Recap=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[Label(TEXT("BATTLE RECAP"))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,12)[SNew(STextBlock).Font(Regular).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{return T(SoloRecap);})]
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Small).ColorAndOpacity(Parchment).AutoWrapText(true).Text_Lambda([this]{return T(EventText());})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[SoloTagged(Button([]{return TEXT("Return to board");},[RecapOpen]{*RecapOpen=false;},Always),TEXT("WC.Recap.Return"))];
    const auto GuideLabel=[this,Parchment](TFunction<FString()> Value,bool Heading=false)->TSharedRef<SWidget>{
        return SNew(STextBlock).ColorAndOpacity(Parchment).AutoWrapText(true)
            .Font_Lambda([this,Heading]{return FCoreStyle::GetDefaultFontStyle(Heading?TEXT("Bold"):TEXT("Regular"),
                FMath::RoundToInt((Heading?17.f:14.f)*SoloGuideTextScale));})
            .Text_Lambda([Value]{return T(Value());});
    };
    const auto GuideButton=[this,Parchment](TFunction<FString()> Value,TFunction<void()> Action,TFunction<bool()> Enabled,FName Tag)->TSharedRef<SWidget>{
        auto Widget=SNew(SButton).ButtonStyle(FWCArtSlice::ButtonStyle()).ContentPadding(FMargin(12,9))
            .IsEnabled_Lambda([Enabled]{return Enabled();})
            .OnClicked_Lambda([Action]{Action();return FReply::Handled();})
            [SNew(STextBlock).ColorAndOpacity(Parchment).AutoWrapText(true)
                .Font_Lambda([this]{return FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),FMath::RoundToInt(14.f*SoloGuideTextScale));})
                .Text_Lambda([Value]{return T(Value());})];
        Widget->SetTag(Tag);return Widget;
    };
    auto GuideSettings=SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(7,7));
    GuideSettings->AddSlot()[GuideButton([this]{return SoloGuidePhrase(TEXT("Guide language: English"),TEXT("Bahasa panduan: Indonesia"));},
        [this]{SoloGuideIndonesian=!SoloGuideIndonesian;},Always,TEXT("WC.Guide.Language"))];
    GuideSettings->AddSlot()[GuideButton([this]{
        const int Percent=FMath::RoundToInt(SoloGuideTextScale*100);
        if(SoloGuideIndonesian)return FString::Printf(TEXT("Ukuran teks panduan: %d%%"),Percent);
        return FString::Printf(TEXT("Guide text size: %d%%"),Percent);
    },
        [this]{SoloGuideTextScale=SoloGuideTextScale<1.25f?1.25f:SoloGuideTextScale<1.5f?1.5f:SoloGuideTextScale<2.f?2.f:1.f;},Always,TEXT("WC.Guide.TextSize"))];
    GuideSettings->AddSlot()[GuideButton([this]{return SoloGuidePhrase(TEXT("Creature sounds: "),TEXT("Suara makhluk: "))+
            SoloGuidePhrase(CreatureSoundEnabled?TEXT("On"):TEXT("Off"),CreatureSoundEnabled?TEXT("Aktif"):TEXT("Nonaktif"));},
        [this]{CreatureSoundEnabled=!CreatureSoundEnabled;},Always,TEXT("WC.Guide.Sound"))];
    auto GuidePages=SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(7,7));
    GuidePages->AddSlot()[GuideButton([this]{return SoloGuidePhrase(TEXT("Previous"),TEXT("Sebelumnya"));},
        [this]{SoloGuidePage=FMath::Max(0,SoloGuidePage-1);},[this]{return SoloGuidePage>0;},TEXT("WC.Guide.Previous"))];
    GuidePages->AddSlot()[GuideButton([this]{return SoloGuidePhrase(TEXT("Next"),TEXT("Berikutnya"));},
        [this]{SoloGuidePage=FMath::Min(4,SoloGuidePage+1);},[this]{return SoloGuidePage<4;},TEXT("WC.Guide.Next"))];
    GuidePages->AddSlot()[GuideButton([this]{return SoloGuidePhrase(TEXT("Return to game · Esc"),TEXT("Kembali ke permainan · Esc"));},
        [this]{CloseSoloGuide();},Always,TEXT("WC.Guide.Close"))];
    auto Guide=SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)[GuideLabel([this]{return SoloGuidePhrase(TEXT("HOW TO PLAY / GUIDE SETTINGS"),TEXT("CARA BERMAIN / PENGATURAN PANDUAN"));},true)]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)[GuideLabel([this]{return SoloGuidePhrase(TEXT("Solo clock paused while this guide is open."),TEXT("Waktu solo dijeda selama panduan ini terbuka."));})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,12)[GuideSettings]
        +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,8)[GuidePages]
        +SVerticalBox::Slot().AutoHeight().Padding(0,10)[GuideLabel([this]{return SoloGuideTitle();},true)]
        +SVerticalBox::Slot().AutoHeight()[GuideLabel([this]{return SoloGuideBody();})]
        +SVerticalBox::Slot().AutoHeight().Padding(0,12,0,0)[GuideButton([this]{return SoloGuidePhrase(TEXT("Return to game · Esc"),TEXT("Kembali ke permainan · Esc"));},
            [this]{CloseSoloGuide();},Always,TEXT("WC.Guide.CloseBottom"))];
    auto ModalHost=SNew(SWCSoloModalHost)
        +SOverlay::Slot()[Main]
        +SOverlay::Slot()[Modal(ShopPanel,EStoryModal::Shop,1060,TEXT("WCModal.Shop"))]
        +SOverlay::Slot()[Modal(Recap,EStoryModal::Recap,560,TEXT("WCModal.Recap"))]
        +SOverlay::Slot()[Modal(Menu,EStoryModal::Menu,440,TEXT("WCModal.Menu"))]
        +SOverlay::Slot()[Modal(Collection,EStoryModal::Collection,760,TEXT("WCModal.Collection"))]
        +SOverlay::Slot()[Modal(Guide,EStoryModal::Guide,660,TEXT("WCModal.Guide"))]
        +SOverlay::Slot()[Modal(Draft,EStoryModal::Draft,570,TEXT("WCModal.Draft"))]
        +SOverlay::Slot()[Modal(Results,EStoryModal::Results,440,TEXT("WCModal.Results"))]
        +SOverlay::Slot()[Modal(SaveDecision,EStoryModal::Save,470,TEXT("WCModal.Save"))];
    ModalHost->SetKeyHandler([this,OpenGuide,GuideAvailable](const FKeyEvent& Event){
        if(Event.GetKey()==EKeys::F1){
            if(SoloGuideOpen)CloseSoloGuide();else if(GuideAvailable())OpenGuide();
            return FReply::Handled();
        }
        if(Event.GetKey()==EKeys::Escape&&SoloGuideOpen){CloseSoloGuide();return FReply::Handled();}
        return FReply::Unhandled();
    });
    const auto PreviousModal=MakeShared<EStoryModal>(EStoryModal::None);
    ModalHost->SetAfterSynchronize([this,TopModal,PreviousModal]{
        const auto CurrentModal=TopModal();
        // A closed button may retain Slate focus after its ancestor collapses. Give
        // arrows/Enter back to the board only when every modal has actually closed.
        // The diagnostic bypass preserves all earlier guide/bench focus behavior.
        const bool LegacyProbe=SoloExercise&&FParse::Param(FCommandLine::Get(),TEXT("WCSoloRecoveryExercise"))&&
            FParse::Param(FCommandLine::Get(),TEXT("WCSoloRecoveryLegacyFocus"));
        if(*PreviousModal!=EStoryModal::None&&CurrentModal==EStoryModal::None&&!LegacyProbe&&BoardInput.IsValid()){
            FSlateApplication::Get().SetKeyboardFocus(BoardInput,EFocusCause::SetDirectly);
            UE_LOG(LogTemp,Display,TEXT("WC_SOLO_MODAL_BOARD_FOCUS_RESTORE previous_modal=%d board_focus=%d"),
                int(*PreviousModal),BoardInput->HasKeyboardFocus());
        }
        *PreviousModal=CurrentModal;
        if(SoloBenchReturnFocus){
            if(TopModal()==EStoryModal::None&&BoardInput.IsValid()&&SoloMatch&&Selected&&ViewedSeat==0&&
                SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0)
                FSlateApplication::Get().SetKeyboardFocus(BoardInput,EFocusCause::SetDirectly);
            SoloBenchReturnFocus=false;
        }
        if(SoloGuideReturnFocus&&!SoloGuideOpen){
            // Required shop/draft/save modals retain their own focus. Focus the board
            // only after the modal host has synchronized its actual enabled states.
            if(TopModal()==EStoryModal::None&&BoardInput.IsValid())
                FSlateApplication::Get().SetKeyboardFocus(BoardInput,EFocusCause::SetDirectly);
            SoloGuideReturnFocus=false;
        }
    });
    Interface=ModalHost;
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
    if(FParse::Param(FCommandLine::Get(),TEXT("WCSoloRecoveryExercise"))){
        // Synthetic Slate events test native focus/routing and real command authority.
        // They are neither OS device input nor unfamiliar-player study evidence.
        TSharedPtr<FJsonObject> Checks;
        const TSharedPtr<FJsonObject>* Existing=nullptr;
        if(ExerciseChecks->TryGetObjectField(TEXT("recovery_checks"),Existing))Checks=*Existing;
        else {Checks=MakeShared<FJsonObject>();ExerciseChecks->SetObjectField(TEXT("recovery_checks"),Checks);}
        FString Mode=TEXT("journey"),ExpectedPath;
        FParse::Value(FCommandLine::Get(),TEXT("WCSoloRecoveryMode="),Mode);
        FParse::Value(FCommandLine::Get(),TEXT("WCSoloExpectedPath="),ExpectedPath);
        const bool Cold=Mode==TEXT("cold")||Mode==TEXT("backup")||Mode==TEXT("invalid");
        const auto Check=[Checks](const TCHAR* Name,bool Value){Checks->SetBoolField(Name,Value);};
        const auto SetStage=[this](int Stage){ExerciseStage=Stage;ExerciseChecks->SetNumberField(TEXT("stage_started"),Elapsed);};
        const auto Finish=[this,Checks,Mode](const FString& Failure=FString()){
            bool Passed=Failure.IsEmpty();
            for(const auto& Row:Checks->Values)if(Row.Value->Type==EJson::Boolean)Passed&=Row.Value->AsBool();
            auto Report=MakeShared<FJsonObject>();
            Report->SetStringField(TEXT("schema"),TEXT("wonder_vnext.synthetic_slate_recovery.2"));
            Report->SetStringField(TEXT("status"),Passed?TEXT("PASS_NATIVE_SYNTHETIC_SLATE_RECOVERY"):TEXT("FAILED_NATIVE_SYNTHETIC_SLATE_RECOVERY"));
            Report->SetBoolField(TEXT("passed"),Passed);Report->SetStringField(TEXT("failure"),Failure);
            Report->SetStringField(TEXT("utc"),FDateTime::UtcNow().ToIso8601());Report->SetStringField(TEXT("mode"),Mode);
            Report->SetBoolField(TEXT("legacy_new_focus_bypass"),FParse::Param(FCommandLine::Get(),TEXT("WCSoloRecoveryLegacyFocus")));
            Report->SetStringField(TEXT("catalog_digest"),S(Catalog.contentDigest));
            Report->SetStringField(TEXT("balance_version"),S(Catalog.balanceVersion));
            Report->SetStringField(TEXT("save_path"),SavePath);Report->SetNumberField(TEXT("wall_seconds"),Elapsed);
            Report->SetNumberField(TEXT("seed"),Seed);Report->SetNumberField(TEXT("last_stage"),ExerciseStage);
            FVector2D Size=FVector2D::ZeroVector;if(GEngine&&GEngine->GameViewport)GEngine->GameViewport->GetViewportSize(Size);
            Report->SetNumberField(TEXT("viewport_width"),Size.X);Report->SetNumberField(TEXT("viewport_height"),Size.Y);
            Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("observations"),ExerciseChecks);
            Report->SetStringField(TEXT("boundary"),TEXT("Engine-local synthetic Slate key down/up through ProcessKeyDownEvent/ProcessKeyUpEvent; explicit focus only for tagged button activation. Bench uses its actual shared handler. Board focus is observed, never forced by this harness. Accelerated real combat, no physical mouse/keyboard, pacing, human study or package promotion claim."));
            FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Report,Writer);
            IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
            const bool Written=FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("solo-recovery-exercise.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
            ExerciseDone=true;SoloPaused=true;
            UE_LOG(LogTemp,Display,TEXT("WC_SOLO_RECOVERY_COMPLETE passed=%d written=%d mode=%s"),Passed,Written,*Mode);
            FPlatformMisc::RequestExit(false);
        };
        const auto Key=[](FKey Value){
            const FKeyEvent Event(Value,FModifierKeysState(),uint32(0),false,uint32(0),uint32(0));
            FSlateApplication::Get().ProcessKeyDownEvent(Event);FSlateApplication::Get().ProcessKeyUpEvent(Event);
        };
        const auto Activate=[this,Key](FName Tag){
            auto Widget=Interface.IsValid()?SoloFindTag(Interface.ToSharedRef(),Tag):nullptr;
            if(!Widget.IsValid()||!Widget->IsEnabled()||!Widget->SupportsKeyboardFocus())return false;
            FSlateApplication::Get().SetKeyboardFocus(Widget,EFocusCause::SetDirectly);
            if(!Widget->HasKeyboardFocus())return false;
            Key(EKeys::Enter);return true;
        };
        const auto FocusAndArrow=[this,Check,Key](const TCHAR* FocusName,const TCHAR* ArrowName,FKey Arrow){
            Check(FocusName,BoardInput.IsValid()&&BoardInput->HasKeyboardFocus());
            const int Before=KeyboardColumn;
            Key(Arrow);Check(ArrowName,KeyboardColumn==Before+(Arrow==EKeys::Right?1:-1));
        };
        const auto UnitAt=[this](wc::Id Id)->const wc::OwnedUnit*{
            const auto& Roster=SoloMatch->Seats()[0].roster;
            const auto At=std::find_if(Roster.begin(),Roster.end(),[Id](const auto& Unit){return Unit.id==Id;});
            return At==Roster.end()?nullptr:&*At;
        };
        const auto BinaryHex=[](const TArray64<uint8>& Bytes){return BytesToHex(Bytes.GetData(),int32(Bytes.Num()));};
        if(Elapsed>180){Finish(TEXT("Recovery exercise exceeded its 180 second limit."));return;}
        if(!SoloMatch->InvariantError().empty()){Finish(S(SoloMatch->InvariantError()));return;}
        if(ExerciseStage==0){
            FString ExplicitSave;
            const bool Explicit=FParse::Value(FCommandLine::Get(),TEXT("WCSavePath="),ExplicitSave);
            const auto Parent=FPaths::GetPath(FPaths::ConvertRelativePathToFull(EvidenceDirectory));
            const bool Scoped=Explicit&&FPaths::IsUnderDirectory(FPaths::ConvertRelativePathToFull(SavePath),Parent)&&
                !FPaths::IsUnderDirectory(Parent,FPaths::ConvertRelativePathToFull(SavePath));
            Check(TEXT("explicit_diagnostic_save_path_is_scoped"),Scoped);
            Check(TEXT("storybook_native_interface_ready"),Storybook&&Interface.IsValid()&&BoardInput.IsValid()&&FWCArtSlice::StorybookResourcesReady());
            Check(TEXT("development_seed_not_reserved"),Seed<900001||Seed>900250);
            if(Seed>=900001&&Seed<=900250){Finish(TEXT("Reserved holdout seeds cannot be used by this diagnostic."));return;}
            if(!Scoped||!Storybook||!Interface.IsValid()||!BoardInput.IsValid()){
                Finish(TEXT("Recovery requires Storybook, an explicit scoped diagnostic save and native Slate."));return;
            }
            const bool Recognized=Mode==TEXT("journey")||Mode==TEXT("checkpoint")||Cold;
            if(!Recognized){Finish(TEXT("Unknown recovery mode."));return;}
            SoloPaused=true;
            if(!Cold&&(IFileManager::Get().FileExists(*SavePath)||IFileManager::Get().FileExists(*(SavePath+TEXT(".previous"))))){
                Finish(TEXT("Fresh journey/checkpoint mode cannot overwrite an existing diagnostic save."));return;
            }
            SetStage(1);return;
        }
        if(Elapsed-ExerciseChecks->GetNumberField(TEXT("stage_started"))<.15)return;
        if(ExerciseStage==1){
            if(Cold){
                Check(TEXT("cold_start_save_choice_blocks_clock_and_orders"),AwaitingSaveDecision&&SoloPaused);
                const auto Before=SoloMatch->SavePreparation();
                wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=0;
                Check(TEXT("startup_order_rejected_without_state_mutation"),!SoloCommand(Buy)&&Before==SoloMatch->SavePreparation());
                OpenSoloGuide();Check(TEXT("startup_required_save_modal_retains_priority"),!SoloGuideOpen&&AwaitingSaveDecision);
                TArray64<uint8> PrimaryBefore,PreviousBefore;
                const bool PrimaryRead=FFileHelper::LoadFileToArray(PrimaryBefore,*SavePath);
                const bool PreviousRead=FFileHelper::LoadFileToArray(PreviousBefore,*(SavePath+TEXT(".previous")));
                ExerciseChecks->SetBoolField(TEXT("primary_read_before_load"),PrimaryRead);
                ExerciseChecks->SetBoolField(TEXT("previous_read_before_load"),PreviousRead);
                ExerciseChecks->SetStringField(TEXT("primary_before_load_hex"),BinaryHex(PrimaryBefore));
                ExerciseChecks->SetStringField(TEXT("previous_before_load_hex"),BinaryHex(PreviousBefore));
                Check(TEXT("startup_load_button_activated"),Activate(TEXT("WC.Save.Load")));
                SetStage(2);return;
            }
            for(int Count=0;Count<2;++Count){
                int Slot=-1;const auto& Captain=SoloMatch->Seats()[0];
                for(int Index=0;Index<int(Captain.shop.size());++Index){
                    wc::Command Buy;Buy.type=wc::CommandType::Buy;Buy.slot=Index;
                    if(wc::PreviewRosterCommand(Catalog,Captain,Buy).accepted){Slot=Index;break;}
                }
                if(Slot<0||!Activate(FName(*FString::Printf(TEXT("WC.Shop.Slot%d"),Slot)))){
                    Finish(TEXT("Could not activate two real affordable shop offers."));return;
                }
            }
            const auto& Roster=SoloMatch->Seats()[0].roster;
            Check(TEXT("two_real_shop_purchases_accepted"),Roster.size()==2&&Message.Contains(TEXT("Recruited")));
            if(Roster.size()!=2){Finish(TEXT("Diagnostic shop purchases did not yield two owned creatures."));return;}
            ExerciseChecks->SetNumberField(TEXT("first_unit"),Roster[0].id);ExerciseChecks->SetNumberField(TEXT("second_unit"),Roster[1].id);
            Check(TEXT("shop_close_button_activated"),Activate(TEXT("WC.Shop.Close")));SetStage(3);return;
        }
        if(ExerciseStage==2){
            TArray64<uint8> PrimaryAfter,PreviousAfter;
            const bool PrimaryRead=FFileHelper::LoadFileToArray(PrimaryAfter,*SavePath);
            const bool PreviousRead=FFileHelper::LoadFileToArray(PreviousAfter,*(SavePath+TEXT(".previous")));
            Check(TEXT("load_preserves_existing_primary_and_previous_files"),
                PrimaryRead==ExerciseChecks->GetBoolField(TEXT("primary_read_before_load"))&&
                PreviousRead==ExerciseChecks->GetBoolField(TEXT("previous_read_before_load"))&&
                BinaryHex(PrimaryAfter)==ExerciseChecks->GetStringField(TEXT("primary_before_load_hex"))&&
                BinaryHex(PreviousAfter)==ExerciseChecks->GetStringField(TEXT("previous_before_load_hex")));
            ExerciseChecks->SetStringField(TEXT("load_message"),Message);
            if(Mode==TEXT("invalid")){
                Check(TEXT("invalid_save_keeps_required_choice_and_pause"),AwaitingSaveDecision&&SoloPaused);
                Check(TEXT("invalid_save_explains_both_restore_failures"),Message.Contains(TEXT("No valid preparation"))&&Message.Contains(TEXT("Previous:")));
                const auto Modal=SoloFindTag(Interface.ToSharedRef(),TEXT("WCModal.Save"));
                Check(TEXT("failed_load_does_not_restore_board_focus"),Modal.IsValid()&&(Modal->HasKeyboardFocus()||Modal->HasFocusedDescendants())&&!BoardInput->HasKeyboardFocus());
                Finish();return;
            }
            TArray64<uint8> Expected;
            const bool ReadExpected=!ExpectedPath.IsEmpty()&&FFileHelper::LoadFileToArray(Expected,*ExpectedPath);
            const std::string ExpectedSnapshot=ReadExpected&&Expected.Num()>0?
                std::string(reinterpret_cast<const char*>(Expected.GetData()),size_t(Expected.Num())):std::string();
            Check(TEXT("cold_resume_restores_exact_frozen_preparation"),ReadExpected&&Expected.Num()>=8&&ExpectedSnapshot==SoloMatch->SavePreparation()&&!AwaitingSaveDecision);
            ExerciseChecks->SetNumberField(TEXT("expected_binary_snapshot_bytes"),Expected.Num());
            Check(TEXT("cold_resume_starts_paused_without_clock_jump"),SoloPaused);
            if(Mode==TEXT("backup"))Check(TEXT("corrupt_primary_reports_previous_recovery"),Message.Contains(TEXT("Recovered previous preparation")));
            const int Time=SoloMatch->RemainingMs();const auto Before=SoloMatch->SavePreparation();
            SoloExercise=false;TickSolo(.25f);SoloExercise=true;
            Check(TEXT("paused_cold_resume_retains_remaining_clock_and_state"),Time==SoloMatch->RemainingMs()&&Before==SoloMatch->SavePreparation());
            if(AwaitingSaveDecision||SoloMatch->Seats()[0].roster.empty()){Finish(TEXT("Cold checkpoint did not restore the expected owned creature."));return;}
            ExerciseChecks->SetNumberField(TEXT("first_unit"),SoloMatch->Seats()[0].roster.front().id);
            Check(TEXT("cold_shop_modal_keeps_focus_until_dismissed"),!BoardInput->HasKeyboardFocus()&&SoloFindTag(Interface.ToSharedRef(),TEXT("WCModal.Shop")).IsValid());
            Check(TEXT("shop_close_button_activated"),Activate(TEXT("WC.Shop.Close")));SetStage(3);return;
        }
        const wc::Id First=wc::Id(ExerciseChecks->GetNumberField(TEXT("first_unit")));
        if(ExerciseStage==3){
            Check(TEXT("shop_close_restores_actual_board_focus"),BoardInput->HasKeyboardFocus());
            const auto* Unit=UnitAt(First);
            if(!Unit||Unit->onBoard){Finish(TEXT("Expected first creature on the bench."));return;}
            KeyboardColumn=2;KeyboardRow=2;SelectBench(Unit->bench);SetStage(4);return;
        }
        if(ExerciseStage==4){
            Check(TEXT("bench_selection_restores_actual_board_focus"),BoardInput->HasKeyboardFocus());
            Key(EKeys::Enter);const auto* Unit=UnitAt(First);
            Check(TEXT("slate_enter_deploys_actual_selected_creature"),Unit&&Unit->onBoard&&Unit->cell==wc::Cell{2,2}&&Selected==0);
            if(Cold){Check(TEXT("cold_recovered_match_has_no_invariant_error"),SoloMatch->InvariantError().empty());Finish();return;}
            Key(EKeys::Enter);Key(EKeys::Right);Key(EKeys::Enter);Unit=UnitAt(First);
            Check(TEXT("slate_arrow_enter_rearranges_owned_creature"),Unit&&Unit->cell==wc::Cell{3,2}&&Selected==0);
            const wc::Id Second=wc::Id(ExerciseChecks->GetNumberField(TEXT("second_unit")));
            Unit=UnitAt(Second);if(!Unit){Finish(TEXT("Second purchased creature is missing."));return;}
            KeyboardColumn=2;KeyboardRow=2;SelectBench(Unit->bench);SetStage(5);return;
        }
        if(ExerciseStage==5){
            Key(EKeys::Enter);Key(EKeys::Right);Key(EKeys::Enter);Key(EKeys::Left);Key(EKeys::Enter);
            const wc::Id Second=wc::Id(ExerciseChecks->GetNumberField(TEXT("second_unit")));
            const auto* A=UnitAt(First);const auto* B=UnitAt(Second);
            Check(TEXT("occupied_board_swap_uses_authority_and_clears_selection"),A&&B&&A->cell==wc::Cell{2,2}&&B->cell==wc::Cell{3,2}&&Selected==0);
            Key(EKeys::Enter);
            int Empty=0;for(;Empty<Catalog.rules.benchCapacity;++Empty){bool Occupied=false;
                for(const auto& Unit:SoloMatch->Seats()[0].roster)Occupied|=!Unit.onBoard&&Unit.bench==Empty;
                if(!Occupied)break;
            }
            SelectBench(Empty);A=UnitAt(First);Check(TEXT("empty_bench_return_uses_shared_handler"),A&&!A->onBoard&&Selected==0);
            Key(EKeys::Right);Key(EKeys::Enter);
            const int GoldBefore=SoloMatch->Seats()[0].gold;
            Check(TEXT("sell_selected_button_activated"),Activate(TEXT("WC.Sell")));
            Check(TEXT("sale_removes_selected_creature_and_returns_real_gold"),!UnitAt(Second)&&SoloMatch->Seats()[0].gold>GoldBefore&&Selected==0&&Message.Contains(TEXT("Sold")));
            ExerciseChecks->SetNumberField(TEXT("sale_gold_returned"),SoloMatch->Seats()[0].gold-GoldBefore);
            Check(TEXT("formation_journey_invariants"),SoloMatch->InvariantError().empty());
            Check(TEXT("menu_open_button_activated"),Activate(TEXT("WC.OpenMenu")));SetStage(6);return;
        }
        if(ExerciseStage==6){Check(TEXT("menu_return_button_activated"),Activate(TEXT("WC.Menu.Return")));SetStage(7);return;}
        if(ExerciseStage==7){
            FocusAndArrow(TEXT("menu_close_restores_actual_board_focus"),TEXT("arrow_routes_to_board_after_menu_close"),EKeys::Right);
            Check(TEXT("recap_open_button_activated"),Activate(TEXT("WC.OpenRecap")));SetStage(8);return;
        }
        if(ExerciseStage==8){Check(TEXT("recap_return_button_activated"),Activate(TEXT("WC.Recap.Return")));SetStage(9);return;}
        if(ExerciseStage==9){
            FocusAndArrow(TEXT("recap_close_restores_actual_board_focus"),TEXT("arrow_routes_to_board_after_recap_close"),EKeys::Left);
            Check(TEXT("collection_menu_open_button_activated"),Activate(TEXT("WC.OpenMenu")));SetStage(10);return;
        }
        if(ExerciseStage==10){Check(TEXT("collection_open_button_activated"),Activate(TEXT("WC.OpenCollection")));SetStage(11);return;}
        if(ExerciseStage==11){Check(TEXT("collection_return_button_activated"),Activate(TEXT("WC.Collection.Return")));SetStage(12);return;}
        if(ExerciseStage==12){
            FocusAndArrow(TEXT("collection_close_restores_actual_board_focus"),TEXT("arrow_routes_to_board_after_collection_close"),EKeys::Right);
            SaveSolo();
            const auto Snapshot=SoloMatch->SavePreparation();TArray64<uint8> SnapshotBytes;
            SnapshotBytes.Append(reinterpret_cast<const uint8*>(Snapshot.data()),int64(Snapshot.size()));
            const auto CheckpointPath=EvidenceDirectory/TEXT("checkpoint-expected.wcsave");
            const bool Written=FFileHelper::SaveArrayToFile(SnapshotBytes,*CheckpointPath);
            TArray64<uint8> Stored,Primary;const bool ReadStored=FFileHelper::LoadFileToArray(Stored,*CheckpointPath);
            const bool ReadPrimary=FFileHelper::LoadFileToArray(Primary,*SavePath);
            Check(TEXT("exact_checkpoint_reference_written"),Written&&ReadStored&&SnapshotBytes==Stored&&SnapshotBytes.Num()>=8);
            Check(TEXT("checkpoint_binary_bytes_match_real_saved_primary"),ReadPrimary&&Primary==SnapshotBytes);
            wc::Match Validation(Catalog,1,0);const auto Validated=wc::LoadPreparationFile(Validation,std::filesystem::path(*CheckpointPath));
            Check(TEXT("checkpoint_reference_validated_by_native_loader"),Validated.Succeeded()&&Validation.SavePreparation()==Snapshot);
            Check(TEXT("checkpoint_preserves_embedded_null_bytes"),Snapshot.find('\0')!=std::string::npos);
            ExerciseChecks->SetNumberField(TEXT("checkpoint_binary_snapshot_bytes"),SnapshotBytes.Num());
            ExerciseChecks->SetNumberField(TEXT("checkpoint_remaining_ms"),SoloMatch->RemainingMs());
            if(Mode==TEXT("checkpoint")){Finish();return;}
            SetStage(13);return;
        }
        if(ExerciseStage==13){
            if(SoloMatch->CurrentPhase()==wc::Phase::Preparation&&SoloMatch->Seats()[0].health>0){
                if(!SoloMatch->Seats()[0].relicOffers.empty()){wc::Command C;C.type=wc::CommandType::ChooseRelic;C.slot=0;SoloCommand(C);}
                if(!SoloMatch->Seats()[0].ready){wc::Command C;C.type=wc::CommandType::Ready;SoloCommand(C);}
            }
            for(int Tick=0;Tick<100&&SoloMatch->CurrentPhase()!=wc::Phase::Finished;++Tick)SoloMatch->Tick(50);
            SoloExercise=false;TickSolo(0);SoloExercise=true;
            if(!Checks->HasField(TEXT("actual_loss_recap_reports_captain_health"))&&SoloRecap.Contains(TEXT("you lost"))){
                Check(TEXT("actual_loss_recap_reports_captain_health"),SoloRecap.Contains(TEXT("Captain HP lost:"))&&SoloRecap.Contains(TEXT("HP remaining:")));
                ExerciseChecks->SetStringField(TEXT("loss_recap"),SoloRecap);
            }
            if(SoloMatch->Seats()[0].health<=0&&!Checks->HasField(TEXT("personal_elimination_allows_read_only_spectating"))){
                int Living=-1;for(const auto& Seat:SoloMatch->Seats())if(Seat.health>0){Living=Seat.id;break;}
                if(Living>=0){ScoutSolo(Living);Check(TEXT("personal_elimination_allows_read_only_spectating"),ViewedSeat!=0&&SoloMatch->Seats()[ViewedSeat].health>0);
                    const auto Before=PublicIdentity(SoloMatch->PublicSeats());wc::Command C;C.type=wc::CommandType::Buy;C.slot=0;
                    Check(TEXT("spectating_rejects_purchase_without_public_mutation"),!SoloCommand(C)&&Before==PublicIdentity(SoloMatch->PublicSeats()));}
            }
            if(SoloMatch->CurrentPhase()!=wc::Phase::Finished)return;
            Check(TEXT("tournament_finished_after_personal_loss"),SoloMatch->Seats()[0].placement>1&&SoloMatch->InvariantError().empty());
            ExerciseChecks->SetNumberField(TEXT("finished_rounds"),SoloMatch->Round());ExerciseChecks->SetNumberField(TEXT("captain_placement"),SoloMatch->Seats()[0].placement);
            Check(TEXT("loss_recap_was_observed"),Checks->HasField(TEXT("actual_loss_recap_reports_captain_health")));
            Check(TEXT("eliminated_spectating_was_observed"),Checks->HasField(TEXT("personal_elimination_allows_read_only_spectating")));
            SetStage(14);return;
        }
        if(ExerciseStage==14){Check(TEXT("results_restart_button_activated"),Activate(TEXT("WC.Results.New")));SetStage(15);return;}
        if(ExerciseStage==15){
            Check(TEXT("results_restart_resets_round_records_selection_and_save_choice"),SoloMatch->Round()==1&&SoloMatch->Records().empty()&&Selected==0&&!AwaitingSaveDecision);
            Check(TEXT("restart_shop_priority_not_overridden_by_board_focus"),SoloFindTag(Interface.ToSharedRef(),TEXT("WCModal.Shop")).IsValid()&&!BoardInput->HasKeyboardFocus());
            Check(TEXT("restart_shop_close_button_activated"),Activate(TEXT("WC.Shop.Close")));SetStage(16);return;
        }
        if(ExerciseStage==16){Check(TEXT("restart_shop_close_restores_actual_board_focus"),BoardInput->HasKeyboardFocus());Finish();return;}
        return;
    }
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
        if(Storybook){OpenSoloGuide();ExerciseChecks->SetBoolField(TEXT("guide_preserves_startup_save_priority"),AwaitingSaveDecision&&!SoloGuideOpen);}
        ExerciseChecks->SetBoolField(TEXT("existing_save_blocks_orders"),AwaitingSaveDecision&&!SoloCommand(Buy));
        SaveSolo(true);ResumeSolo();
        ExerciseChecks->SetBoolField(TEXT("existing_save_choice_preserves_checkpoint"),!AwaitingSaveDecision&&SoloMatch->SavePreparation()==BeforeChoice);
        if(Storybook){
            SoloPaused=false;
            const auto BeforeGuide=SoloMatch->SavePreparation();const int TimeBefore=SoloMatch->RemainingMs();
            const bool PreviousShopOpen=ShopOpen;const int PreviousDismissedRound=ShopDismissedRound;
            OpenSoloGuide();
            // Exercise the real clock path without recursively entering this harness.
            SoloExercise=false;TickSolo(.25f);SoloExercise=true;
            ExerciseChecks->SetBoolField(TEXT("guide_pauses_clock_without_changing_match_or_shop"),SoloGuideOpen&&SoloPaused&&
                SoloMatch->RemainingMs()==TimeBefore&&SoloMatch->SavePreparation()==BeforeGuide&&
                ShopOpen==PreviousShopOpen&&ShopDismissedRound==PreviousDismissedRound);
            CloseSoloGuide();ExerciseChecks->SetBoolField(TEXT("guide_restores_running_clock"),!SoloGuideOpen&&!SoloPaused);
            SoloPaused=true;OpenSoloGuide();CloseSoloGuide();
            ExerciseChecks->SetBoolField(TEXT("guide_preserves_existing_pause"),!SoloGuideOpen&&SoloPaused);
            bool Bilingual=true;
            for(int Page=0;Page<5;++Page){
                SoloGuidePage=Page;SoloGuideIndonesian=false;const FString English=SoloGuideBody();
                SoloGuideIndonesian=true;Bilingual&=!English.IsEmpty()&&!SoloGuideBody().IsEmpty()&&English!=SoloGuideBody();
            }
            ExerciseChecks->SetBoolField(TEXT("guide_has_five_bilingual_pages"),Bilingual);
            SoloGuidePage=0;SoloGuideIndonesian=false;SoloGuideReturnFocus=false;SoloPaused=false;
        }
        ExerciseChecks->SetBoolField(TEXT("unselected_inspector_requests_selection"),InspectorText().StartsWith(TEXT("Select a creature"))&&!InspectorText().Contains(TEXT("Relic: None")));
        ExerciseChecks->SetBoolField(TEXT("buy"),SoloCommand(Buy));
        ExerciseChecks->SetBoolField(TEXT("purchase_feedback"),Message.Contains(TEXT("Recruited")));
        if(!SoloMatch->Seats()[0].roster.empty()){
            const auto& BenchUnit=SoloMatch->Seats()[0].roster.front();
            SelectBench(BenchUnit.bench);
            ExerciseChecks->SetBoolField(TEXT("bench_selection_describes_keyboard_deployment"),Selected==BenchUnit.id&&
                Message.Contains(TEXT("Keyboard target"))&&Message.Contains(TEXT("Enter: deploy")));
            SoloBenchReturnFocus=false;
            Selected=SoloMatch->Seats()[0].roster.front().id;
            if(FWCArtSlice::IsEnabled()){
                ExerciseChecks->SetBoolField(TEXT("placement_preview_accepts_legal_solo_deployment"),PlacementState({2,2})==2);
                ExerciseChecks->SetBoolField(TEXT("placement_preview_rejects_opponent_half"),PlacementState({2,6})==3);
            }
            const bool Deployed=SoloCell({2,2});
            ExerciseChecks->SetBoolField(TEXT("deploy"),Deployed);
            ExerciseChecks->SetBoolField(TEXT("selection_clears_after_accepted_deploy"),Deployed&&Selected==0);
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
            if(Storybook&&!ExerciseChecks->HasField(TEXT("guide_preserves_relic_draft_priority"))){
                OpenSoloGuide();ExerciseChecks->SetBoolField(TEXT("guide_preserves_relic_draft_priority"),!SoloGuideOpen);
            }
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
        if(Storybook){OpenSoloGuide();ExerciseChecks->SetBoolField(TEXT("guide_preserves_results_priority"),!SoloGuideOpen);}
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
