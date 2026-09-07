#include "WCFrontEnd.h"
#include "WCFrontEndScene.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "WCNetworkSession.h"
#include "WCEmblem.h"
#include "Components/AudioComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "GameFramework/GameUserSettings.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Styling/AppStyle.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SEditableTextBox.h"
#include "Widgets/Input/SSlider.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Layout/SSeparator.h"
#include "Widgets/Layout/SWrapBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

namespace {
const FLinearColor Ink(.022f, .037f, .052f, .96f);
const FLinearColor Paper(.9f, .91f, .85f);
const FLinearColor Gold(.92f, .72f, .37f);
const FLinearColor Teal(.065f, .28f, .31f);
FString String(const std::string& Value) { return UTF8_TO_TCHAR(Value.c_str()); }
FString Humanize(FString Value) {
  Value.ReplaceInline(TEXT("_"), TEXT(" "));
  if (!Value.IsEmpty()) Value[0] = FChar::ToUpper(Value[0]);
  return Value;
}
FString TraitStat(const FString& Value, bool Indonesian) {
  struct Entry { const TCHAR* Id; const TCHAR* English; const TCHAR* Indonesian; };
  static const Entry Entries[] = {
    {TEXT("max_health_bonus_bp"), TEXT("maximum health"), TEXT("kesehatan maksimum")},
    {TEXT("attack_rate_bonus_bp"), TEXT("attack speed"), TEXT("kecepatan serang")},
    {TEXT("physical_armor_flat"), TEXT("armor points"), TEXT("poin armor")},
    {TEXT("magic_resistance_flat"), TEXT("magic resistance points"), TEXT("poin resistansi sihir")},
    {TEXT("basic_damage_bonus_bp"), TEXT("basic attack damage"), TEXT("damage serangan biasa")},
    {TEXT("ability_damage_bonus_bp"), TEXT("skill damage"), TEXT("damage skill")},
    {TEXT("all_damage_bonus_bp"), TEXT("attack and skill damage"), TEXT("damage serangan dan skill")},
    {TEXT("support_power_bonus_bp"), TEXT("healing and shields"), TEXT("pemulihan dan perisai")},
    {TEXT("movement_bonus_bp"), TEXT("movement speed"), TEXT("kecepatan gerak")}};
  for (const auto& Entry : Entries) if (Value == Entry.Id) return Indonesian ? Entry.Indonesian : Entry.English;
  return Humanize(Value);
}
FString Field(const TSharedPtr<FJsonObject>& Object, const TCHAR* Key) {
  FString Value;
  if (Object) Object->TryGetStringField(Key, Value);
  return Value;
}
double Number(const TSharedPtr<FJsonObject>& Object, const TCHAR* Key) {
  double Value = 0;
  if (Object) Object->TryGetNumberField(Key, Value);
  return Value;
}
FString ShortName(const TSharedPtr<FJsonObject>& Object) {
  const FString Name = Field(Object, TEXT("display_name"));
  return Name.IsEmpty() ? Field(Object, TEXT("name")) : Name;
}
TArray<FString> Roles(const TSharedPtr<FJsonObject>& Object) {
  TArray<FString> Output;
  const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
  if (Object && Object->TryGetArrayField(TEXT("role_tags"), Values))
    for (const auto& Value : *Values) Output.Add(Value->AsString());
  if (Output.IsEmpty()) Output.Add(Field(Object, TEXT("role")));
  return Output;
}
class SWCFrontEndRoot : public SCompoundWidget {
public:
  SLATE_BEGIN_ARGS(SWCFrontEndRoot) {}
    SLATE_DEFAULT_SLOT(FArguments, Content)
    SLATE_ARGUMENT(TFunction<bool()>, Back)
    SLATE_ARGUMENT(TFunction<void()>, Screenshot)
  SLATE_END_ARGS()
  void Construct(const FArguments& Args) {
    Back = Args._Back;
    Screenshot = Args._Screenshot;
    ChildSlot[Args._Content.Widget];
  }
  bool SupportsKeyboardFocus() const override { return true; }
  FReply OnKeyDown(const FGeometry&, const FKeyEvent& Event) override {
    if (Event.GetKey() == EKeys::Escape && Back && Back()) return FReply::Handled();
    if (Event.GetKey() == EKeys::F9 && Screenshot) { Screenshot(); return FReply::Handled(); }
    return FReply::Unhandled();
  }
private:
  TFunction<bool()> Back;
  TFunction<void()> Screenshot;
};
}

FWCFrontEnd::~FWCFrontEnd() { Remove(); }
void FWCFrontEnd::AddReferencedObjects(FReferenceCollector& Collector) {
  Collector.AddReferencedObjects(Assets);
}
FString FWCFrontEnd::Local(const TCHAR* English, const TCHAR* Indonesian) const {
  return Controller.IsValid() && Controller->Language == TEXT("id") ? Indonesian : English;
}
TSharedRef<SWidget> FWCFrontEnd::Copy(const FString& Value, int32 Size, bool IsGold) {
  return SNew(STextBlock).Text(FText::FromString(Value))
      .Font(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), Size))
      .ColorAndOpacity(IsGold ? Gold : Paper).AutoWrapText(true);
}
TSharedRef<SWidget> FWCFrontEnd::Button(const FString& Label, TFunction<void()> Handler, bool Enabled, bool Accent) {
  auto Widget = SNew(SButton).IsEnabled(Enabled).ContentPadding(FMargin(15, 9))
      .ButtonColorAndOpacity(Accent ? Teal : FLinearColor(.06f, .09f, .11f))
      .ForegroundColor(Paper)
      .OnClicked_Lambda([Handler = MoveTemp(Handler)] { Handler(); return FReply::Handled(); })
      [Copy(Label, 16, Accent)];
  Buttons.Add(Label, Widget);
  return Widget;
}
bool FWCFrontEnd::IsEntry() const { return !EntryState.IsEmpty() && EntryState != TEXT("Lobby"); }
bool FWCFrontEnd::Update(AWCMatchController* Player, TFunction<void(const FString&)> OnAction) {
  if (!Player || !Player->Presenter || !Player->Public || !GEngine || !GEngine->GameViewport) {
    Remove(); return false;
  }
  if (FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndProfile"))) {
    Controller = Player;
    TickProfile();
  }
  if (bAudit && Root) TickAudit();
  const int Phase = int(Number(Player->Public, TEXT("phase")));
  const auto* Session = Player->GetGameInstance<UWCNetworkSession>();
  if (Phase >= 0 ||
      !Field(Player->Public, TEXT("error")).IsEmpty() || Player->bTutorial) {
    Remove(); return false;
  }
  Controller = Player;
  Action = MoveTemp(OnAction);
  FString NextEntry = Field(Player->Public, TEXT("entryState"));
  const int Connected = int(Number(Player->Public, TEXT("connected")));
  FVector2D Size;
  GEngine->GameViewport->GetViewportSize(Size);
  const int NextColumns = Size.X < 1500 ? 4 : 6;
  const FString NextError = Session && Session->bMatchAborted ? Session->LastNetworkError : FString();
  const FString NextDetail = Session && Session->bMatchAborted ? Session->LastNetworkDetail : FString();
  if (!NextError.IsEmpty()) NextEntry.Reset();
  const bool ErrorChanged = NextError != NetworkError || NextDetail != NetworkDetail;
  const bool MessageChanged = PreviousMessage != Player->Message;
  NetworkError = NextError; NetworkDetail = NextDetail;
  PreviousMessage = Player->Message;
  if (ErrorChanged && !NetworkError.IsEmpty()) {
    bPending = false;
    Page = EPage::Mode;
    if (Session && !Session->LastJoinAddress.IsEmpty()) Player->JoinAddress = Session->LastJoinAddress;
  }
  if (MessageChanged && Player->Message != TEXT("Accepted") && !Player->Message.IsEmpty() && NextEntry.IsEmpty())
    bPending = false;
  FString NextParticipants;
  const TArray<TSharedPtr<FJsonValue>>* Participants = nullptr;
  if (Player->Public->TryGetArrayField(TEXT("entryParticipants"), Participants))
    for (const auto& Participant : *Participants) {
      const auto Person = Participant->AsObject();
      NextParticipants += Field(Person, TEXT("name")) + (Person->GetBoolField(TEXT("ready")) ? TEXT("/ready;") : TEXT("/waiting;"));
    }
  const bool Changed = EntryState != NextEntry || Connected != PreviousConnected ||
                       Columns != NextColumns || PreviousLanguage != Player->Language || ParticipantSignature != NextParticipants || ErrorChanged || MessageChanged;
  EntryState = NextEntry;
  PreviousConnected = Connected;
  Columns = NextColumns;
  PreviousLanguage = Player->Language;
  ParticipantSignature = NextParticipants;
  if (!Root) {
    GConfig->GetString(TEXT("WonderChess"), TEXT("ShowcaseHero"), SelectedId, GGameUserSettingsIni);
    if (SelectedIndex() < 0 && !Player->Presenter->Definitions.units.empty())
      SelectedId = String(Player->Presenter->Definitions.units[0].id);
    Scene = Player->GetWorld()->SpawnActor<AWCFrontEndScene>();
    Scene->Initialize(Player);
    Scene->ShowHero(SelectedId, Star, Player->bReducedMotion);
    Root = SNew(SWCFrontEndRoot)
        .Back([this] { return Back(); })
        .Screenshot([this] { if (Controller.IsValid()) Controller->CaptureScreenshot(); })
        [SAssignNew(Body, SBorder).BorderImage(FAppStyle::GetBrush(TEXT("NoBorder"))).Padding(FMargin(28, 20))];
    GEngine->GameViewport->AddViewportWidgetContent(Root.ToSharedRef(), 30);
    FInputModeGameAndUI Input;
    Input.SetWidgetToFocus(Root);
    Input.SetHideCursorDuringCapture(false);
    Player->SetInputMode(Input);
    InitializeAudit();
    Rebuild();
  } else if (Changed) {
    if (EntryState == TEXT("Introduction") && Scene.IsValid())
      Scene->TransitionToArena(float(Number(Player->Public, TEXT("entryRemainingMs")) / 1000), Player->bReducedMotion);
    else if (EntryState.IsEmpty() && Scene.IsValid())
      Scene->RestorePreview();
    Rebuild();
  }
  if (bPending && PendingAction == TEXT("start") && !IsEntry() && FPlatformTime::Seconds() - PendingAt > 3) {
    bPending = false;
    Rebuild();
  }
  TickRecoveryAudit();
  return true;
}
void FWCFrontEnd::Remove() {
  if (Root && GEngine && GEngine->GameViewport)
    GEngine->GameViewport->RemoveViewportWidgetContent(Root.ToSharedRef());
  Root.Reset(); Body.Reset(); Grid.Reset(); GalleryScroll.Reset();
  if (Scene.IsValid()) { Scene->RestoreCamera(); Scene->Destroy(); }
  Scene.Reset();
  Portraits.Reset(); Assets.Reset();
  bPending = false;
}
const TCHAR* FWCFrontEnd::PageName() const {
  if (!Root) return TEXT("closed");
  switch (Page) {
    case EPage::Lobby: return TEXT("lobby");
    case EPage::Mode: return TEXT("mode");
    case EPage::Gallery: return TEXT("gallery");
    case EPage::Detail: return TEXT("detail");
    case EPage::Settings: return TEXT("settings");
  }
  return TEXT("unknown");
}
bool FWCFrontEnd::Back() {
  if (!Root) return false;
  if (IsEntry()) { Dispatch(TEXT("entrycancel")); return true; }
  if (Page == EPage::Detail) SetPage(EPage::Gallery);
  else if (Page != EPage::Lobby) SetPage(EPage::Lobby);
  return true;
}
void FWCFrontEnd::SetPage(EPage Value) {
  if (GalleryScroll) ScrollOffset = GalleryScroll->GetScrollOffset();
  Page = Value;
  if (Controller.IsValid()) Controller->Sound(TEXT("ready"));
  Rebuild();
}
void FWCFrontEnd::Dispatch(const FString& Id) {
  if ((bPending || IsEntry()) && (Id == TEXT("start") || Id == TEXT("host") || Id == TEXT("join"))) return;
  if (Id == TEXT("start") || Id == TEXT("host") || Id == TEXT("join")) {
    bPending = true;
    PendingAction = Id;
    PendingAt = FPlatformTime::Seconds();
  }
  if (Action) Action(Id);
  Rebuild();
}
void FWCFrontEnd::SaveShowcase() {
  if (bAudit || FParse::Param(FCommandLine::Get(), TEXT("WCFrontEndProfile"))) return;
  GConfig->SetString(TEXT("WonderChess"), TEXT("ShowcaseHero"), *SelectedId, GGameUserSettingsIni);
  GConfig->Flush(false, GGameUserSettingsIni);
}
int32 FWCFrontEnd::SelectedIndex() const {
  if (!Controller.IsValid() || !Controller->Presenter) return -1;
  const auto& Definitions = Controller->Presenter->Definitions.units;
  for (int32 Index = 0; Index < int32(Definitions.size()); ++Index)
    if (String(Definitions[Index].id) == SelectedId) return Index;
  return -1;
}
void FWCFrontEnd::OpenHero(int32 Index) {
  if (!Controller.IsValid()) return;
  const auto& Definitions = Controller->Presenter->Definitions.units;
  if (Index < 0 || Index >= int32(Definitions.size())) return;
  SelectedId = String(Definitions[Index].id);
  Star = 1;
  if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
  SaveShowcase(); SetPage(EPage::Detail);
}
bool FWCFrontEnd::SelectPreviewForReview(const FString& Id, const FString& Clip) {
  if (!Controller.IsValid() || !Controller->Presenter || !Scene.IsValid() || IsEntry()) return false;
  const auto& Definitions = Controller->Presenter->Definitions.units;
  bool Found = false;
  for (const auto& Definition : Definitions) if (String(Definition.id) == Id) { Found = true; break; }
  if (!Found) return false;
  SelectedId = Id;
  Star = 1;
  DetailTab = TEXT("Skill");
  Page = EPage::Detail;
  bReviewPreview = true;
  bTurntable = false;
  Scene->RestorePreview();
  Scene->ShowHero(SelectedId, Star, false);
  Scene->SetTurntable(false);
  const bool Loaded = Scene->PlayClip(Clip, false);
  Rebuild();
  return Loaded;
}
bool FWCFrontEnd::ReducePreviewMotion() const {
  return Controller.IsValid() && Controller->bReducedMotion && !bReviewPreview;
}
void FWCFrontEnd::ShiftHero(int32 Delta) {
  RefreshResults();
  if (Results.IsEmpty()) return;
  const int32 Current = Results.IndexOfByKey(SelectedIndex());
  OpenHero(Results[(FMath::Max(0, Current) + Delta + Results.Num()) % Results.Num()]);
}
TSharedRef<SWidget> FWCFrontEnd::Header() {
  const bool Home = Page == EPage::Lobby;
  return SNew(SHorizontalBox)
      + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
        [Copy(Home ? TEXT("WONDER CHESS") : Local(TEXT("THE SEVEN-LANTERN TRIALS"), TEXT("UJIAN TUJUH LENTERA")), Home ? 32 : 21, true)]
      + SHorizontalBox::Slot().AutoWidth().Padding(8, 0)
        [Button(Local(TEXT("Heroes"), TEXT("Hero")), [this] { SetPage(EPage::Gallery); }, !IsEntry())]
      + SHorizontalBox::Slot().AutoWidth().Padding(8, 0)
        [Button(Local(TEXT("Settings"), TEXT("Pengaturan")), [this] { SetPage(EPage::Settings); }, !IsEntry())]
      + SHorizontalBox::Slot().AutoWidth()
        [Button(Local(Home ? TEXT("Quit") : TEXT("Back"), Home ? TEXT("Keluar") : TEXT("Kembali")),
                [this, Home] { if (Home) Dispatch(TEXT("quit")); else Back(); })];
}
void FWCFrontEnd::Rebuild() {
  if (!Body || !Controller.IsValid()) return;
  Buttons.Reset();
  Grid.Reset(); GalleryScroll.Reset();
  TSharedRef<SWidget> Content = IsEntry() ? Mode() :
      Page == EPage::Lobby ? Lobby() : Page == EPage::Mode ? Mode() :
      Page == EPage::Gallery ? Gallery() : Page == EPage::Detail ? Detail() : Settings();
  auto Panel = SNew(SVerticalBox)
      + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 16)[Header()]
      + SVerticalBox::Slot().FillHeight(1)[Content]
      + SVerticalBox::Slot().AutoHeight().Padding(0, 12, 0, 0)
        [Copy(Local(TEXT("Brighthaven • Aurelune     |     Tab: focus   Enter: select   Esc: back   F9: capture"),
                    TEXT("Brighthaven • Aurelune     |     Tab: fokus   Enter: pilih   Esc: kembali   F9: tangkapan")), 13)];
  Body->SetContent(Panel);
}
TSharedRef<SWidget> FWCFrontEnd::Lobby() {
  const auto& Text = Controller->Presenter->Metadata.Units.FindRef(SelectedId);
  return SNew(SHorizontalBox)
      + SHorizontalBox::Slot().FillWidth(.43f).VAlign(VAlign_Center)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(28)
        [SNew(SVerticalBox)
          + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 16)[Copy(Local(TEXT("Your company.\nYour next adventure."), TEXT("Pasukanmu.\nPetualangan berikutnya.")), 36, true)]
          + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 22)[Copy(Local(TEXT("Recruit 24 champions, discover their bonds, and face seven persistent rivals in the Seven-Lantern Courtyard."), TEXT("Rekrut 24 hero, temukan sinergi mereka, dan hadapi tujuh lawan tetap di Seven-Lantern Courtyard.")), 20)]
          + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 12)[Button(Local(TEXT("Play"), TEXT("Main")), [this] { SetPage(EPage::Mode); }, true, true)]
          + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 12)[Button(Local(TEXT("Explore the heroes"), TEXT("Jelajahi para hero")), [this] { SetPage(EPage::Gallery); })]
          + SVerticalBox::Slot().AutoHeight()[Button(Local(TEXT("Guided practice"), TEXT("Latihan terpandu")), [this] { Dispatch(TEXT("practice")); })]
        ]]
      + SHorizontalBox::Slot().FillWidth(.57f).VAlign(VAlign_Bottom).Padding(40, 0, 0, 20)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(18)
        [SNew(SVerticalBox)
          + SVerticalBox::Slot().AutoHeight()[Copy(ShortName(Text), 29, true)]
          + SVerticalBox::Slot().AutoHeight().Padding(0, 8)[Copy(Field(Text, TEXT("title")), 18)]
          + SVerticalBox::Slot().AutoHeight()[Button(Local(TEXT("Meet this hero"), TEXT("Kenali hero ini")), [this] { OpenHero(SelectedIndex()); })]
          + SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Text_Lambda([this] { return FText::FromString(Scene.IsValid() ? Scene->AssetMessage : FString()); }).ColorAndOpacity(Gold).AutoWrapText(true)]
        ]];
}

TSharedRef<SWidget> FWCFrontEnd::Mode() {
  const bool Network = NetworkError.IsEmpty() && Controller->Public->GetBoolField(TEXT("network"));
  const int Humans = Network ? 2 : 1;
  const bool CanHost = !NetworkError.IsEmpty() || Controller->AssignedSeat == 0;
  auto Rows = SNew(SVerticalBox);
  const TArray<TSharedPtr<FJsonValue>>* Participants = nullptr;
  if (Controller->Public->TryGetArrayField(TEXT("entryParticipants"), Participants) && !Participants->IsEmpty()) {
    for (const auto& Value : *Participants) {
      const auto Person = Value->AsObject();
      const bool Bot = Person->GetBoolField(TEXT("bot"));
      const bool Ready = Person->GetBoolField(TEXT("ready"));
      const int Seat = int(Number(Person, TEXT("seat")));
      const bool OpenSeat = !Bot && Network && Seat >= int(Number(Controller->Public, TEXT("connected")));
      const FString Kind = Bot ? TEXT("BOT") : Local(TEXT("Human"), TEXT("Pemain"));
      const FString Name = OpenSeat ? Local(TEXT("Open LAN seat"), TEXT("Kursi LAN terbuka")) : Field(Person, TEXT("name"));
      const FString Readiness = !Bot && !IsEntry()
          ? (OpenSeat ? Local(TEXT("Waiting for connection"), TEXT("Menunggu koneksi"))
                      : Local(TEXT("Waiting for start"), TEXT("Menunggu mulai")))
          : Local(Ready ? TEXT("Ready") : TEXT("Loading"), Ready ? TEXT("Siap") : TEXT("Memuat"));
      Rows->AddSlot().AutoHeight().Padding(0, 5)
        [Copy(FString::Printf(TEXT("%d  %s   ·   %s   ·   %s"), Seat + 1, *Name, *Kind, *Readiness), 18)];
    }
  } else {
    for (int Seat = 0; Seat < 8; ++Seat) {
      FString Label;
      if (Seat < Humans) {
        const bool OpenSeat = Network && Seat >= int(Number(Controller->Public, TEXT("connected")));
        const FString Name = OpenSeat ? Local(TEXT("Open LAN seat"), TEXT("Kursi LAN terbuka"))
            : FString::Printf(TEXT("%s %d"), *Local(TEXT("Captain"), TEXT("Kapten")), Seat + 1);
        Label = FString::Printf(TEXT("%d  %s   ·   %s"), Seat + 1, *Name,
            *Local(OpenSeat ? TEXT("Waiting for connection") : TEXT("Waiting for start"),
                   OpenSeat ? TEXT("Menunggu koneksi") : TEXT("Menunggu mulai")));
      } else {
        const auto& Bots = Controller->Presenter->Definitions.bots;
        const auto& Bot = Bots[(Seat - Humans) % Bots.size()];
        Label = FString::Printf(TEXT("%d  %s   ·   BOT"), Seat + 1, *String(Bot.label));
        const TArray<TSharedPtr<FJsonValue>>* Profiles = nullptr;
        if (Controller->Presenter->Metadata.Bots->TryGetArrayField(TEXT("bots"), Profiles) && Profiles->IsValidIndex((Seat - Humans) % Bots.size()))
          Label += TEXT(" · ") + Humanize(Field((*Profiles)[(Seat - Humans) % Bots.size()]->AsObject(), TEXT("focus")));
      }
      Rows->AddSlot().AutoHeight().Padding(0, 5)[Copy(Label, 18)];
    }
  }
  auto Controls = SNew(SVerticalBox);
  FString Status;
  if (EntryState == TEXT("WaitingForPlayers")) Status = Local(TEXT("Waiting for player 2"), TEXT("Menunggu pemain 2"));
  if (EntryState == TEXT("Loading")) Status = Local(TEXT("Preparing the courtyard"), TEXT("Menyiapkan halaman"));
  if (EntryState == TEXT("Ready")) Status = Local(TEXT("Ready for the trials"), TEXT("Siap mengikuti ujian"));
  if (EntryState == TEXT("Introduction")) Status = Local(TEXT("Meet your rivals"), TEXT("Kenali para rivalmu"));
  const FString Heading = IsEntry() ? Status :
      Network ? Local(TEXT("LAN gathering · two captains"), TEXT("Lobi LAN · dua kapten")) :
                Local(TEXT("Choose your tournament"), TEXT("Pilih turnamenmu"));
  Controls->AddSlot().AutoHeight().Padding(0, 0, 0, 15)[Copy(Heading, 27, true)];
  if (!NetworkError.IsEmpty()) {
    Controls->AddSlot().AutoHeight().Padding(0, 5)[Copy(Local(TEXT("Connection unavailable"), TEXT("Koneksi tidak tersedia")), 22, true)];
    FString Guidance = NetworkError;
    if (NetworkError.StartsWith(TEXT("Could not reach the LAN host.")))
      Guidance = Local(TEXT("The LAN host did not respond. Check its address and make sure its lobby is open."),
                       TEXT("Host LAN tidak merespons. Periksa alamat dan pastikan lobinya terbuka."));
    else if (NetworkError.StartsWith(TEXT("The local network host could not start.")))
      Guidance = Local(TEXT("The LAN host could not start. Try hosting again or choose Solo."),
                       TEXT("Host LAN belum dapat dimulai. Coba buat lobi lagi atau pilih Solo."));
    else if (NetworkError.StartsWith(TEXT("The game could not load the requested session.")))
      Guidance = Local(TEXT("The session could not load. Try joining again or return to Solo."),
                       TEXT("Sesi belum dapat dimuat. Coba gabung lagi atau kembali ke Solo."));
    Controls->AddSlot().AutoHeight().Padding(0, 5)[Copy(Guidance, 18)];
    Controls->AddSlot().AutoHeight().Padding(0, 12)[Copy(Local(TEXT("Edit the address and join again, host a new LAN session, or choose Solo. No tournament is running here."), TEXT("Ubah alamat lalu gabung lagi, buat sesi LAN baru, atau pilih Solo. Tidak ada turnamen aktif di sini.")), 18)];
  }
  if (IsEntry()) {
    Controls->AddSlot().AutoHeight().Padding(0, 0, 0, 18)[Copy(Local(TEXT("These are the actual participants. Your first preparation begins after the host completes entry."), TEXT("Inilah peserta sebenarnya. Persiapan pertama dimulai setelah host menyelesaikan proses masuk.")), 19)];
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Ready to enter"), TEXT("Siap masuk")), [this] { Dispatch(TEXT("entryready")); }, EntryState == TEXT("Ready") || EntryState == TEXT("Loading"), true)];
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Skip introduction"), TEXT("Lewati perkenalan")), [this] { Dispatch(TEXT("entryskip")); })];
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Cancel entry"), TEXT("Batalkan")), [this] { Dispatch(TEXT("entrycancel")); })];
    Controls->AddSlot().AutoHeight()[SNew(STextBlock).Text_Lambda([this] {
      return FText::FromString(Local(TEXT("First preparation timer has not started."), TEXT("Waktu persiapan pertama belum dimulai.")));
    }).ColorAndOpacity(Paper).AutoWrapText(true)];
  } else {
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Network ? Local(TEXT("Start · 2 humans + 6 bots"), TEXT("Mulai · 2 pemain + 6 bot")) : Local(TEXT("Solo · you + 7 bots"), TEXT("Solo · kamu + 7 bot")), [this] { Dispatch(TEXT("start")); }, CanHost && !bPending && (!Network || PreviousConnected == 2), true)];
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Host LAN · 2 humans + 6 bots"), TEXT("Buat LAN · 2 pemain + 6 bot")), [this] { Dispatch(TEXT("host")); }, !Network && !bPending)];
    Controls->AddSlot().AutoHeight().Padding(0, 12, 0, 6)[Copy(Local(TEXT("Join a host by IPv4 address"), TEXT("Gabung lewat alamat IPv4")), 17)];
    Controls->AddSlot().AutoHeight()[SNew(SEditableTextBox)
      .Font(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 16))
      .Text(FText::FromString(Controller->JoinAddress)).HintText(FText::FromString(TEXT("192.168.1.20:7777")))
      .IsEnabled(!Network && !bPending)
      .OnTextChanged_Lambda([this](const FText& Value) { Controller->JoinAddress = Value.ToString(); })];
    Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Join LAN"), TEXT("Gabung LAN")), [this] {
      FString Address;
      if (!UWCNetworkSession::NormalizeJoinAddress(Controller->JoinAddress, Address)) {
        Controller->Message = Local(TEXT("Enter a valid host address and optional port."), TEXT("Masukkan alamat host dan port yang sah."));
        Rebuild(); return;
      }
      Controller->JoinAddress = Address;
      Dispatch(TEXT("join"));
    }, !Network && !bPending)];
    if (Network)
      Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Leave LAN lobby"), TEXT("Tinggalkan lobi LAN")), [this] { Dispatch(TEXT("menu")); })];
    if (bPending) {
      Controls->AddSlot().AutoHeight()[Copy(PendingAction == TEXT("join") ? Local(TEXT("Connecting to the host…"), TEXT("Menghubungkan ke host…")) : Local(TEXT("Preparing session…"), TEXT("Menyiapkan sesi…")), 18, true)];
      Controls->AddSlot().AutoHeight().Padding(0, 8)[Button(Local(TEXT("Cancel connection"), TEXT("Batalkan koneksi")), [this] { Dispatch(TEXT("menu")); })];
    }
  }
  if (!Controller->Message.IsEmpty())
    Controls->AddSlot().AutoHeight().Padding(0, 15)[Copy(Controller->Message, 17, true)];
  if (EntryState == TEXT("Introduction")) {
    return SNew(SVerticalBox)
      + SVerticalBox::Slot().FillHeight(1)[SNew(SBox)]
      + SVerticalBox::Slot().AutoHeight()
        [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(20)
          [SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(.45f)
              [SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight()[Copy(Status, 27, true)]
                + SVerticalBox::Slot().AutoHeight().Padding(0, 14)[Copy(Local(TEXT("Round 1 · Monster encounter\nYour preparation begins after this introduction."), TEXT("Ronde 1 · Pertemuan monster\nPersiapan dimulai setelah perkenalan ini.")), 19)]
                + SVerticalBox::Slot().AutoHeight()[Button(Local(TEXT("Skip introduction"), TEXT("Lewati perkenalan")), [this] { Dispatch(TEXT("entryskip")); })]]
            + SHorizontalBox::Slot().FillWidth(.55f)[Rows]]];
  }
  return SNew(SHorizontalBox)
    + SHorizontalBox::Slot().FillWidth(.5f).Padding(0, 0, 14, 0)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(24)
        [SNew(SScrollBox) + SScrollBox::Slot()[Controls]]]
    + SHorizontalBox::Slot().FillWidth(.5f).Padding(14, 0, 0, 0)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(24)
        [SNew(SScrollBox) + SScrollBox::Slot()
          [SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 20)[Copy(Local(TEXT("Eight persistent seats"), TEXT("Delapan kursi tetap")), 26, true)]
            + SVerticalBox::Slot().AutoHeight()[Rows]
            + SVerticalBox::Slot().AutoHeight().Padding(0, 22)[Copy(Local(TEXT("Bots use the same shop, gold, placement and combat rules. Their preferences persist throughout the match."), TEXT("Bot memakai aturan toko, emas, penempatan, dan pertempuran yang sama. Preferensi mereka tetap sepanjang pertandingan.")), 18)]
          ]]];
}

const FSlateBrush* FWCFrontEnd::Portrait(const FString& UnitId) {
  if (const auto* Existing = Portraits.Find(UnitId)) return Existing->Get();
  const FString Name = TEXT("T_") + UnitId + TEXT("_Portrait");
  const FString Path = TEXT("/Game/WonderChess/Heroes/") + UnitId + TEXT("/") + Name + TEXT(".") + Name;
  auto Brush = MakeShared<FSlateBrush>();
  auto* Texture = LoadObject<UTexture2D>(nullptr, *Path);
  if (Texture) { Assets.Add(Texture); Brush->SetResourceObject(Texture); }
  Brush->ImageSize = FVector2D(160, 160);
  Brush->DrawAs = Texture ? ESlateBrushDrawType::Image : ESlateBrushDrawType::NoDrawType;
  Portraits.Add(UnitId, Brush);
  return &Brush.Get();
}
void FWCFrontEnd::RefreshResults() {
  Results.Reset();
  if (!Controller.IsValid()) return;
  const auto& Defs = Controller->Presenter->Definitions.units;
  const auto& Metadata = Controller->Presenter->Metadata.Units;
  for (int Index = 0; Index < int(Defs.size()); ++Index) {
    const auto Text = Metadata.FindRef(String(Defs[Index].id));
    if (!Text) continue;
    if (!Search.IsEmpty() && !ShortName(Text).Contains(Search, ESearchCase::IgnoreCase) &&
        !Field(Text, TEXT("name")).Contains(Search, ESearchCase::IgnoreCase)) continue;
    bool Match = true;
    for (const auto& Pair : Filters) {
      if (Pair.Value.IsEmpty()) continue;
      if (Pair.Key == TEXT("role")) {
        bool RoleMatch = false;
        for (const auto& Role : Roles(Text)) RoleMatch |= Pair.Value.Contains(Role);
        Match &= RoleMatch;
      } else {
        const FString Value = Pair.Key == TEXT("cost") ? FString::FromInt(Defs[Index].cost) : Field(Text, *Pair.Key);
        Match &= Pair.Value.Contains(Value);
      }
    }
    if (Match) Results.Add(Index);
  }
  Results.Sort([this, &Defs, &Metadata](int A, int B) {
    if (Sort == TEXT("Cost") && Defs[A].cost != Defs[B].cost) return Defs[A].cost < Defs[B].cost;
    if (Sort == TEXT("Race") && Defs[A].race != Defs[B].race) return Defs[A].race < Defs[B].race;
    if (Sort == TEXT("Class") && Defs[A].unitClass != Defs[B].unitClass) return Defs[A].unitClass < Defs[B].unitClass;
    return ShortName(Metadata.FindRef(String(Defs[A].id))) < ShortName(Metadata.FindRef(String(Defs[B].id)));
  });
}
TSharedRef<SWidget> FWCFrontEnd::Card(int32 Index, float Width) {
  const auto& Definition = Controller->Presenter->Definitions.units[Index];
  const FString Id = String(Definition.id);
  const auto Text = Controller->Presenter->Metadata.Units.FindRef(Id);
  const FString Description = Controller->Presenter->Metadata.AbilityTooltip(Id, Controller->Language);
  return SNew(SBox).WidthOverride(Width).Padding(5)
    [SNew(SButton).ContentPadding(12).ButtonColorAndOpacity(Id == SelectedId ? Teal : Ink)
      .ToolTipText(FText::FromString(Description)).OnClicked_Lambda([this, Index] { OpenHero(Index); return FReply::Handled(); })
      [SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)
          [SNew(SBox).WidthOverride(146).HeightOverride(146)
            [SNew(SImage).Image(Portrait(Id))]]
        + SVerticalBox::Slot().AutoHeight()[Copy(ShortName(Text), 20, true)]
        + SVerticalBox::Slot().AutoHeight().Padding(0, 4)[Copy(FString::Printf(TEXT("%d %s · %s"), Definition.cost, *Local(TEXT("gold"), TEXT("emas")), *FString::Join(Roles(Text), TEXT(" / "))), 14)]
        + SVerticalBox::Slot().AutoHeight().Padding(0, 4)
          [SNew(SHorizontalBox)
            + SHorizontalBox::Slot().FillWidth(1)[EmblemLabel(String(Definition.race), Humanize(String(Definition.race)), 14)]
            + SHorizontalBox::Slot().FillWidth(1)[EmblemLabel(String(Definition.unitClass), Humanize(String(Definition.unitClass)), 14)]]
        + SVerticalBox::Slot().AutoHeight().Padding(0, 7, 0, 0)
          [EmblemLabel(Id, Field(Text->GetObjectField(TEXT("ability")), TEXT("name")), 15)]
        + SVerticalBox::Slot().AutoHeight().Padding(0, 4, 0, 0)[Copy(Description, 14)]
      ]];
}
TSharedRef<SWidget> FWCFrontEnd::EmblemLabel(const FString& Id, const FString& Label, int32 FontSize) {
  return SNew(SHorizontalBox)
    + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 7, 0)
      [SNew(SBox).ToolTipText(FText::FromString(Label))[SNew(SWCEmblem).Id(Id).Size(26)]]
    + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[Copy(Label, FontSize)];
}
void FWCFrontEnd::RefreshGrid() {
  if (!Grid) return;
  RefreshResults();
  Grid->ClearChildren();
  Grid->AddSlot().AutoHeight().Padding(5, 12)
    [Copy(FString::Printf(TEXT("%d / %d %s"), Results.Num(), int(Controller->Presenter->Definitions.units.size()),
                        *Local(TEXT("heroes"), TEXT("hero"))), 17, true)];
  if (Results.IsEmpty()) {
    Grid->AddSlot().AutoHeight().Padding(6, 20)[Copy(Local(TEXT("No heroes match these filters."), TEXT("Tidak ada hero yang cocok dengan filter ini.")), 22)];
    Grid->AddSlot().AutoHeight()[Button(Local(TEXT("Clear filters"), TEXT("Hapus filter")), [this] { Search.Reset(); Filters.Reset(); Rebuild(); })];
    return;
  }
  FVector2D Size;
  GEngine->GameViewport->GetViewportSize(Size);
  const float Width = (Size.X - 110) / Columns;
  if (bShowcase) {
    const int Current = FMath::Max(0, Results.IndexOfByKey(SelectedIndex()));
    auto Row = SNew(SHorizontalBox);
    for (int Offset : {-1, 0, 1}) {
      const int Index = Results[(Current + Offset + Results.Num()) % Results.Num()];
      Row->AddSlot().FillWidth(1).HAlign(HAlign_Center)[Card(Index, FMath::Min(360.f, (Size.X - 140) / 3))];
    }
    Grid->AddSlot().AutoHeight()[Row];
    auto Navigation = SNew(SHorizontalBox);
    Navigation->AddSlot().FillWidth(1)[Button(Local(TEXT("Previous hero"), TEXT("Hero sebelumnya")), [this] {
      const int Current = FMath::Max(0, Results.IndexOfByKey(SelectedIndex()));
      SelectedId = String(Controller->Presenter->Definitions.units[Results[(Current + Results.Num() - 1) % Results.Num()]].id);
      if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
      SaveShowcase();
      RefreshGrid();
    })];
    Navigation->AddSlot().FillWidth(1)[Button(Local(TEXT("Next hero"), TEXT("Hero berikutnya")), [this] {
      const int Current = FMath::Max(0, Results.IndexOfByKey(SelectedIndex()));
      SelectedId = String(Controller->Presenter->Definitions.units[Results[(Current + 1) % Results.Num()]].id);
      if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
      SaveShowcase();
      RefreshGrid();
    })];
    Grid->AddSlot().AutoHeight().Padding(8, 12)[Navigation];
  } else {
    for (int Offset = 0; Offset < Results.Num(); Offset += Columns) {
      auto Row = SNew(SHorizontalBox);
      for (int Column = 0; Column < Columns && Offset + Column < Results.Num(); ++Column)
        Row->AddSlot().FillWidth(1)[Card(Results[Offset + Column], Width)];
      Grid->AddSlot().AutoHeight()[Row];
    }
  }
}
TSharedRef<SWidget> FWCFrontEnd::Gallery() {
  auto FilterRows = SNew(SVerticalBox);
  for (const FString Group : {TEXT("race"), TEXT("unit_class"), TEXT("cost"), TEXT("role")}) {
    TSet<FString> Unique;
    for (const auto& Pair : Controller->Presenter->Metadata.Units) {
      if (Group == TEXT("role")) for (const auto& Role : Roles(Pair.Value)) Unique.Add(Role);
      else Unique.Add(Group == TEXT("cost") ? FString::FromInt(int(Number(Pair.Value, TEXT("cost")))) : Field(Pair.Value, *Group));
    }
    auto Values = Unique.Array(); Values.Sort();
    auto Row = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5, 4));
    Row->AddSlot().VAlign(VAlign_Center)[Copy(Group == TEXT("unit_class") ? Local(TEXT("Class"), TEXT("Kelas")) : Humanize(Group), 16, true)];
    for (const auto& Value : Values) {
      const bool Active = Filters.FindOrAdd(Group).Contains(Value);
      Row->AddSlot()[Button((Active ? TEXT("✓ ") : TEXT("")) + Humanize(Value), [this, Group, Value] {
        auto& Choices = Filters.FindOrAdd(Group);
        if (Choices.Contains(Value)) Choices.Remove(Value); else Choices.Add(Value);
        ScrollOffset = 0; Rebuild();
      }, true, Active)];
    }
    FilterRows->AddSlot().AutoHeight().Padding(0, 3)[Row];
  }
  auto Top = SNew(SHorizontalBox)
    + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(0, 0, 25, 0)
      [Copy(FString::Printf(TEXT("%s · %d"), *Local(TEXT("Heroes"), TEXT("Hero")), int(Controller->Presenter->Definitions.units.size())), 28, true)]
    + SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
      [SNew(SEditableTextBox).Text(FText::FromString(Search)).HintText(FText::FromString(Local(TEXT("Search short or full name"), TEXT("Cari nama singkat atau lengkap"))))
        .Font(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 16))
        .OnTextChanged_Lambda([this](const FText& Value) { Search = Value.ToString(); ScrollOffset = 0; RefreshGrid(); if (GalleryScroll) GalleryScroll->ScrollToStart(); })]
    + SHorizontalBox::Slot().AutoWidth().Padding(12, 0)[Button(Local(bShowcase ? TEXT("Grid") : TEXT("Showcase"), bShowcase ? TEXT("Kisi") : TEXT("Pameran")), [this] { bShowcase = !bShowcase; ScrollOffset = 0; Rebuild(); })]
    + SHorizontalBox::Slot().AutoWidth()[Button(Local(TEXT("Clear"), TEXT("Hapus")), [this] { Filters.Reset(); Search.Reset(); ScrollOffset = 0; Rebuild(); })];
  auto Sorts = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(6, 4));
  Sorts->AddSlot().VAlign(VAlign_Center)[Copy(Local(TEXT("Sort"), TEXT("Urutkan")), 16)];
  for (const FString Value : {TEXT("Cost"), TEXT("Name"), TEXT("Race"), TEXT("Class")})
    Sorts->AddSlot()[Button(Value, [this, Value] { Sort = Value; ScrollOffset = 0; Rebuild(); }, true, Value == Sort)];
  auto Panel = SNew(SVerticalBox)
    + SVerticalBox::Slot().AutoHeight().Padding(0, 0, 0, 12)[Top]
    + SVerticalBox::Slot().AutoHeight()[FilterRows]
    + SVerticalBox::Slot().AutoHeight().Padding(0, 8)[Sorts]
    + SVerticalBox::Slot().FillHeight(1)
      [SAssignNew(GalleryScroll, SScrollBox).ScrollBarAlwaysVisible(true)
        + SScrollBox::Slot()[SAssignNew(Grid, SVerticalBox)]];
  RefreshGrid();
  GalleryScroll->SetScrollOffset(ScrollOffset);
  return SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(18)[Panel];
}

TSharedRef<SWidget> FWCFrontEnd::PreviewControls() {
  auto Clips = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5, 5));
  for (const FString Clip : {TEXT("Idle"), TEXT("Move"), TEXT("Attack"), TEXT("Active"), TEXT("Hit"), TEXT("Defeat"), TEXT("Victory")})
    Clips->AddSlot()[Button(Clip == TEXT("Active") ? Local(TEXT("Skill"), TEXT("Skill")) : Clip,
        [this, Clip] { if (Scene.IsValid() && Controller.IsValid()) { Scene->PlayClip(Clip, ReducePreviewMotion()); Scene->SetTurntable(false); bTurntable = false; Rebuild(); } }, true,
        Scene.IsValid() && Scene->SelectedClip == Clip)];
  auto Rotation = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5, 5));
  Rotation->AddSlot()[Button(TEXT("↶ 30°"), [this] { if (Scene.IsValid()) Scene->RotateHero(-30); })];
  Rotation->AddSlot()[Button(TEXT("↷ 30°"), [this] { if (Scene.IsValid()) Scene->RotateHero(30); })];
  Rotation->AddSlot()[Button(Local(TEXT("Reset view"), TEXT("Atur ulang")), [this] { if (Scene.IsValid()) Scene->ResetView(); })];
  Rotation->AddSlot()[Button(ReducePreviewMotion() ? Local(TEXT("Rotation off"), TEXT("Rotasi mati")) :
      Local(bTurntable ? TEXT("Stop rotation") : TEXT("Turntable"), bTurntable ? TEXT("Hentikan rotasi") : TEXT("Putar model")), [this] {
    bTurntable = Controller.IsValid() && !ReducePreviewMotion() && !bTurntable;
    if (Scene.IsValid()) Scene->SetTurntable(bTurntable); Rebuild();
  }, !ReducePreviewMotion())];
  return SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(14)
    [SNew(SVerticalBox)
      + SVerticalBox::Slot().AutoHeight()[Copy(ReducePreviewMotion() ?
          Local(TEXT("Reduced motion · choose a still pose"), TEXT("Gerakan terbatas · pilih pose diam")) :
          Local(TEXT("Model preview · no match changes"), TEXT("Pratinjau model · tidak mengubah pertandingan")), 16, true)]
      + SVerticalBox::Slot().AutoHeight().Padding(0, 8)[Clips]
      + SVerticalBox::Slot().AutoHeight()[Rotation]
      + SVerticalBox::Slot().AutoHeight().Padding(0, 8, 0, 0)[SNew(STextBlock)
        .Text_Lambda([this] { return FText::FromString(Scene.IsValid() ? Scene->AssetMessage : FString()); }).ColorAndOpacity(Gold).AutoWrapText(true)]
    ];
}

TSharedRef<SWidget> FWCFrontEnd::Detail() {
  const int Index = SelectedIndex();
  if (Index < 0) return Copy(Local(TEXT("Hero data is unavailable."), TEXT("Data hero tidak tersedia.")), 22, true);
  const auto& Definition = Controller->Presenter->Definitions.units[Index];
  const auto Text = Controller->Presenter->Metadata.Units.FindRef(SelectedId);
  auto Stars = SNew(SHorizontalBox);
  for (int Value : {1, 2, 3})
    Stars->AddSlot().FillWidth(1).Padding(3, 0)[Button(FString::Printf(TEXT("%d ★"), Value), [this, Value] {
      Star = Value; if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion); Rebuild();
    }, true, Value == Star)];
  auto Tabs = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5, 5));
  for (const FString Tab : {TEXT("Skill"), TEXT("Synergies"), TEXT("Tactics"), TEXT("Story")})
    Tabs->AddSlot()[Button(Tab, [this, Tab] { DetailTab = Tab; Rebuild(); }, true, DetailTab == Tab)];
  auto Information = SNew(SVerticalBox)
    + SVerticalBox::Slot().AutoHeight()[Copy(ShortName(Text), 31, true)]
    + SVerticalBox::Slot().AutoHeight().Padding(0, 6)[Copy(Field(Text, TEXT("name")) + TEXT(" · ") + Field(Text, TEXT("title")), 18)]
    + SVerticalBox::Slot().AutoHeight().Padding(0, 3)[Copy(FString::Printf(TEXT("%s · %s · %s · %d %s"),
        *Humanize(String(Definition.race)), *Humanize(String(Definition.unitClass)), *FString::Join(Roles(Text), TEXT(" / ")),
        Definition.cost, *Local(TEXT("gold"), TEXT("emas"))), 16)]
    + SVerticalBox::Slot().AutoHeight().Padding(0, 12)[Stars]
    + SVerticalBox::Slot().AutoHeight()[Tabs]
    + SVerticalBox::Slot().FillHeight(1).Padding(0, 12, 0, 0)
      [SNew(SScrollBox).ScrollBarAlwaysVisible(true) + SScrollBox::Slot()[DetailBody()]];
  auto Navigate = SNew(SHorizontalBox)
    + SHorizontalBox::Slot().FillWidth(1).Padding(0, 0, 5, 0)[Button(Local(TEXT("Previous"), TEXT("Sebelumnya")), [this] { ShiftHero(-1); })]
    + SHorizontalBox::Slot().FillWidth(1).Padding(5, 0, 0, 0)[Button(Local(TEXT("Next"), TEXT("Berikutnya")), [this] { ShiftHero(1); })];
  return SNew(SHorizontalBox)
    + SHorizontalBox::Slot().FillWidth(.55f)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(22)[Information]]
    + SHorizontalBox::Slot().FillWidth(.45f).Padding(22, 0, 0, 0)
      [SNew(SVerticalBox)
        + SVerticalBox::Slot().AutoHeight()[Navigate]
        + SVerticalBox::Slot().FillHeight(1)[SNew(SBox)]
        + SVerticalBox::Slot().AutoHeight()[PreviewControls()]];
}

TSharedRef<SWidget> FWCFrontEnd::DetailBody() {
  const auto& Catalog = Controller->Presenter->Definitions;
  const auto& Definition = Catalog.units[SelectedIndex()];
  const auto Text = Controller->Presenter->Metadata.Units.FindRef(SelectedId);
  auto Lines = SNew(SVerticalBox);
  auto Add = [this, &Lines](const FString& Value, bool Accent = false) {
    Lines->AddSlot().AutoHeight().Padding(0, 0, 8, 13)[Copy(Value, 17, Accent)];
  };
  if (DetailTab == TEXT("Skill")) {
    Add(Local(TEXT("Base stats · selected star"), TEXT("Stat dasar · bintang terpilih")), true);
    Add(FString::Printf(TEXT("%s %g     %s %g\n%s %.2f/s     %s %d %s\n%s %d %s     %s %d %s"),
        *Local(TEXT("Health"), TEXT("Kesehatan")), wc::StarValue(Definition.health, Star, 0, Catalog.rules) / 100.0,
        *Local(TEXT("Attack"), TEXT("Serangan")), wc::StarValue(Definition.attackDamage, Star, 0, Catalog.rules) / 100.0,
        *Local(TEXT("Attack speed"), TEXT("Kecepatan serang")), Definition.attackRate / 1000.0,
        *Local(TEXT("Range"), TEXT("Jangkauan")), Definition.range, *Local(TEXT("tiles"), TEXT("petak")),
        *Local(TEXT("Armor"), TEXT("Armor")), Definition.armor, *Local(TEXT("points"), TEXT("poin")),
        *Local(TEXT("Magic resistance"), TEXT("Resistansi sihir")), Definition.resistance, *Local(TEXT("points"), TEXT("poin"))));
    const auto SummaryAbility = Text->GetObjectField(TEXT("ability"));
    Lines->AddSlot().AutoHeight().Padding(0, 0, 8, 13)[EmblemLabel(SelectedId, Field(SummaryAbility, TEXT("name")), 20)];
    Add(Controller->Presenter->Metadata.AbilityTooltip(SelectedId, Controller->Language));
    for (const auto& Value : SummaryAbility->GetArrayField(TEXT("effects"))) {
      const auto Effect = Value->AsObject();
      const FString Kind = Field(Effect, TEXT("effect"));
      const double Magnitude = Effect->GetArrayField(TEXT("magnitude_by_star"))[Star - 1]->AsNumber();
      const double Duration = Number(Effect, TEXT("duration_ms")) / 1000;
      FString Summary;
      if (Kind == TEXT("damage"))
        Summary = FString::Printf(TEXT("%s: %g %s"), *Local(TEXT("Damage"), TEXT("Damage")), Magnitude / 100, *Humanize(Field(Effect, TEXT("damage_type"))));
      else if (Kind == TEXT("heal"))
        Summary = FString::Printf(TEXT("%s: %g HP"), *Local(TEXT("Healing"), TEXT("Pemulihan")), Magnitude / 100);
      else if (Kind == TEXT("shield"))
        Summary = FString::Printf(TEXT("%s: %g · %.2f s"), *Local(TEXT("Shield"), TEXT("Perisai")), Magnitude / 100, Duration);
      else if (Kind == TEXT("stun"))
        Summary = FString::Printf(TEXT("%s: %.2f s"), *Local(TEXT("Stun"), TEXT("Lumpuh")), Duration);
      else if (Kind == TEXT("dash"))
        Summary = FString::Printf(TEXT("%s: %g %s"), *Local(TEXT("Dash distance"), TEXT("Jarak lompatan")), Number(SummaryAbility, TEXT("max_dash_tiles")), *Local(TEXT("tiles"), TEXT("petak")));
      else if (Kind == TEXT("stat_modifier"))
        Summary = FString::Printf(TEXT("%s: %+.1f%% · %.2f s"), *Local(TEXT("Attack speed"), TEXT("Kecepatan serang")), Magnitude / 100, Duration);
      Add(Summary, true);
    }
    Add(FString::Printf(TEXT("%s %.2f s  ·  %s %.2f s"),
        *Local(TEXT("Cooldown"), TEXT("Jeda skill")), Number(SummaryAbility, TEXT("cooldown_ms")) / 1000,
        *Local(TEXT("First cast"), TEXT("Skill pertama")), Number(SummaryAbility, TEXT("first_cast_ms")) / 1000));
    Lines->AddSlot().AutoHeight().Padding(0, 0, 10, 16)
      [Button(Local(bAdvanced ? TEXT("Hide advanced details") : TEXT("Advanced details"), bAdvanced ? TEXT("Sembunyikan rincian lanjutan") : TEXT("Rincian lanjutan")),
              [this] { bAdvanced = !bAdvanced; Rebuild(); })];
    if (bAdvanced) {
    Add(Local(TEXT("Timing and targeting details"), TEXT("Rincian waktu dan target")), true);
    const auto& Rules = Catalog.rules;
    const auto Health = wc::StarValue(Definition.health, Star, 0, Rules);
    const auto Basic = wc::StarValue(Definition.attackDamage, Star, 0, Rules);
    const int AttackMs = wc::AttackInterval(Definition.attackRate, 0, Rules) * Rules.tickMs;
    Add(FString::Printf(TEXT("%s  %g     %s  %g\n%s  %.3f/s   (%d ms %s)\n%s  %d %s · %s\n%s  %d     %s  %d"),
        *Local(TEXT("Health"), TEXT("Kesehatan")), Health / 100.0,
        *Local(TEXT("Basic damage"), TEXT("Damage dasar")), Basic / 100.0,
        *Local(TEXT("Attack speed"), TEXT("Kecepatan serang")), Definition.attackRate / 1000.0, AttackMs,
        *Local(TEXT("effective interval"), TEXT("interval efektif")),
        *Local(TEXT("Range"), TEXT("Jangkauan")), Definition.range, *Local(TEXT("tiles"), TEXT("petak")),
        *Field(Text->GetObjectField(TEXT("stats")), TEXT("attack_delivery")),
        *Local(TEXT("Armor points"), TEXT("Poin armor")), Definition.armor,
        *Local(TEXT("Magic resistance points"), TEXT("Poin resistansi sihir")), Definition.resistance));
    const int MoveTicks = wc::MovementInterval(Definition.movementRate, 0, Rules);
    Add(FString::Printf(TEXT("%s %.3f %s/s · %.3f %s/s (%d ms)"),
        *Local(TEXT("Movement"), TEXT("Gerak")), Definition.movementRate / 1000.0,
        *Local(TEXT("nominal tiles"), TEXT("petak nominal")), 1000.0 / (MoveTicks * Rules.tickMs),
        *Local(TEXT("effective tiles"), TEXT("petak efektif")), MoveTicks * Rules.tickMs));
    const auto Ability = Text->GetObjectField(TEXT("ability"));
    Add(Field(Ability, TEXT("name")), true);
    Add(Controller->Presenter->Metadata.AbilityTooltip(SelectedId, Controller->Language));
    Add(FString::Printf(TEXT("%s %.2fs   ·   %s %.2fs\n%s %.2fs   ·   %s %.2fs   ·   %s %.2fs"),
        *Local(TEXT("First cast"), TEXT("Skill pertama")), Number(Ability, TEXT("first_cast_ms")) / 1000,
        *Local(TEXT("Cooldown"), TEXT("Jeda skill")), Number(Ability, TEXT("cooldown_ms")) / 1000,
        *Local(TEXT("Windup"), TEXT("Persiapan")), Number(Ability, TEXT("cast_ms")) / 1000,
        *Local(TEXT("Travel"), TEXT("Waktu lintas")), Number(Ability, TEXT("travel_ms")) / 1000,
        *Local(TEXT("Recovery"), TEXT("Pemulihan")), Number(Ability, TEXT("recovery_ms")) / 1000));
    Add(Local(TEXT("Effects in execution order"), TEXT("Efek sesuai urutan eksekusi")), true);
    const TArray<TSharedPtr<FJsonValue>>* Effects = nullptr;
    TArray<TSharedPtr<FJsonObject>> Ordered;
    if (Ability->TryGetArrayField(TEXT("effects"), Effects))
      for (const auto& Effect : *Effects) Ordered.Add(Effect->AsObject());
    else Ordered.Add(Ability);
    for (int Index = 0; Index < Ordered.Num(); ++Index) {
      const auto Effect = Ordered[Index];
      const TArray<TSharedPtr<FJsonValue>>* Magnitudes = nullptr;
      double Magnitude = 0;
      if (Effect->TryGetArrayField(TEXT("magnitude_by_star"), Magnitudes) && Magnitudes->IsValidIndex(Star - 1))
        Magnitude = (*Magnitudes)[Star - 1]->AsNumber();
      FString Unit = Field(Effect, TEXT("magnitude_unit"));
      if (Unit == TEXT("centipoints")) { Magnitude /= 100; Unit = Local(TEXT("points"), TEXT("poin")); }
      else if (Unit == TEXT("basis_points")) { Magnitude /= 100; Unit = TEXT("%"); }
      Add(FString::Printf(TEXT("%d. %s · %g %s\n%s · %s\n%s %g · %s %g · %s %g\n%s %.2fs"), Index + 1,
          *Humanize(Field(Effect, TEXT("effect"))), Magnitude, *Unit,
          *Humanize(Field(Ability, TEXT("target_rule"))), *Humanize(Field(Effect, TEXT("damage_type"))),
          *Local(TEXT("Range"), TEXT("Jangkauan")), Number(Ability, TEXT("range_tiles")),
          *Local(TEXT("Radius"), TEXT("Radius")), Number(Ability, TEXT("radius_tiles")),
          *Local(TEXT("Maximum targets"), TEXT("Target maksimum")), Number(Ability, TEXT("max_targets")),
          *Local(TEXT("Duration"), TEXT("Durasi")), Number(Effect, TEXT("duration_ms")) / 1000));
    }
    }
  } else if (DetailTab == TEXT("Synergies")) {
    Add(Local(TEXT("Count distinct deployed heroes. A 4-hero tier replaces the 2-hero tier. Bench copies and extra stars do not add contributors."), TEXT("Hitung jenis hero berbeda di papan. Tingkat 4 menggantikan tingkat 2. Salinan di bangku dan bintang tambahan tidak menambah hitungan.")), true);
    const auto& Traits = Controller->Presenter->Metadata.Traits->GetArrayField(TEXT("traits"));
    for (const FString Id : {String(Definition.race), String(Definition.unitClass)}) {
      for (const auto& Value : Traits) {
        const auto Trait = Value->AsObject();
        if (Field(Trait, TEXT("id")) != Id) continue;
        Lines->AddSlot().AutoHeight().Padding(0, 0, 8, 13)
          [EmblemLabel(Id, Humanize(Id) + TEXT(" · ") + Field(Trait, TEXT("name")), 19)];
        Add(Field(Trait, TEXT("description")));
        for (const auto& Level : Trait->GetArrayField(TEXT("tiers"))) {
          const auto Tier = Level->AsObject();
          const bool Percent = Field(Trait, TEXT("magnitude_unit")) == TEXT("basis_points");
          Add(FString::Printf(TEXT("%d %s → +%g%s %s\n%s"), int(Number(Tier, TEXT("count"))),
              *Local(TEXT("distinct heroes"), TEXT("jenis hero")), Number(Tier, TEXT("value")) / (Percent ? 100 : 1), Percent ? TEXT("%") : TEXT(""),
              *TraitStat(Field(Trait, TEXT("stat")), Controller->Language == TEXT("id")),
              *Local(TEXT("Recipients: matching deployed heroes only, locked at combat start."), TEXT("Penerima: hero terkait di papan, ditetapkan saat awal pertempuran."))));
        }
        auto Partners = SNew(SWrapBox).UseAllottedSize(true).InnerSlotPadding(FVector2D(5, 6));
        for (int Index = 0; Index < int(Catalog.units.size()); ++Index) {
          const auto& Partner = Catalog.units[Index];
          if (String(Partner.id) == SelectedId || (String(Partner.race) != Id && String(Partner.unitClass) != Id)) continue;
          const auto PartnerText = Controller->Presenter->Metadata.Units.FindRef(String(Partner.id));
          Partners->AddSlot()
            [SNew(SButton).ContentPadding(7).ButtonColorAndOpacity(Teal)
              .ToolTipText(FText::FromString(ShortName(PartnerText) + TEXT(" · ") + Humanize(Id)))
              .OnClicked_Lambda([this, Index] { OpenHero(Index); return FReply::Handled(); })
              [SNew(SHorizontalBox)
                + SHorizontalBox::Slot().AutoWidth().Padding(0, 0, 8, 0)
                  [SNew(SBox).WidthOverride(44).HeightOverride(44)[SNew(SImage).Image(Portrait(String(Partner.id)))]]
                + SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[Copy(ShortName(PartnerText), 16)]]];
        }
        Lines->AddSlot().AutoHeight().Padding(0, 0, 0, 20)[Partners];
      }
    }
  } else if (DetailTab == TEXT("Tactics")) {
    const auto Tactics = Text->GetObjectField(TEXT("tactics"));
    for (const TCHAR* Key : {TEXT("placement"), TEXT("partner"), TEXT("counter"), TEXT("weakness"), TEXT("contrast")}) {
      Add(Humanize(Key), true); Add(Field(Tactics, Key));
    }
    Add(Local(TEXT("Weapons and armor are part of this hero's appearance. They do not add item slots or separate equipment stats."), TEXT("Senjata dan armor merupakan bagian penampilan hero ini. Tidak ada slot item atau stat perlengkapan terpisah.")));
  } else {
    Add(Field(Text, TEXT("name")) + TEXT(" · ") + Field(Text, TEXT("title")), true);
    Add(Humanize(Field(Text, TEXT("region"))) + TEXT(" · ") + Humanize(Field(Text, TEXT("faction"))));
    Add(Field(Text, TEXT("biography")));
  }
  return Lines;
}

TSharedRef<SWidget> FWCFrontEnd::Settings() {
  auto Content = SNew(SVerticalBox);
  Content->AddSlot().AutoHeight().Padding(0, 0, 0, 22)[Copy(Local(TEXT("Settings"), TEXT("Pengaturan")), 30, true)];
  for (const FString Type : {TEXT("Master"), TEXT("Music"), TEXT("Effects")}) {
    Content->AddSlot().AutoHeight().Padding(0, 12)[Copy(Type, 20)];
    Content->AddSlot().AutoHeight()[SNew(SSlider)
      .Value_Lambda([this, Type] { return Type == TEXT("Master") ? Controller->MasterVolume : Type == TEXT("Music") ? Controller->MusicVolume : Controller->EffectsVolume; })
      .OnValueChanged_Lambda([this, Type](float Value) {
        if (Type == TEXT("Master")) Controller->MasterVolume = Value;
        else if (Type == TEXT("Music")) Controller->MusicVolume = Value;
        else Controller->EffectsVolume = Value;
        if (Controller->Music) Controller->Music->SetVolumeMultiplier(Controller->MasterVolume * Controller->MusicVolume);
        Controller->SaveOptions();
      })];
  }
  Content->AddSlot().AutoHeight().Padding(0, 22, 0, 10)[Button(Controller->Language == TEXT("en") ? TEXT("Language: English") : TEXT("Bahasa: Indonesia"), [this] {
    Controller->Language = Controller->Language == TEXT("en") ? TEXT("id") : TEXT("en"); Controller->SaveOptions(); Rebuild();
  })];
  Content->AddSlot().AutoHeight().Padding(0, 10)[Button(Local(Controller->bReducedMotion ? TEXT("Reduced motion: on") : TEXT("Reduced motion: off"),
      Controller->bReducedMotion ? TEXT("Gerakan terbatas: aktif") : TEXT("Gerakan terbatas: nonaktif")), [this] {
    Controller->bReducedMotion = !Controller->bReducedMotion;
    Controller->SaveOptions();
    if (Controller->bReducedMotion) {
      bTurntable = false;
      if (Scene.IsValid()) Scene->SetTurntable(false);
    }
    if (Scene.IsValid()) Scene->ShowHero(SelectedId, Star, Controller->bReducedMotion);
    Rebuild();
  })];
  Content->AddSlot().AutoHeight().Padding(0, 10)[Button(Local(TEXT("Toggle window / fullscreen"), TEXT("Ubah jendela / layar penuh")), [this] { Dispatch(TEXT("window")); })];
  Content->AddSlot().AutoHeight().Padding(0, 15)[Copy(Local(TEXT("Settings are saved locally. Reduced motion holds each selected animation at its first pose and disables automatic rotation. Step rotation and reset remain available."), TEXT("Pengaturan disimpan lokal. Gerakan terbatas menahan setiap animasi pada pose awal dan menonaktifkan rotasi otomatis. Rotasi bertahap dan atur ulang tetap tersedia.")), 18)];
  return SNew(SHorizontalBox)
    + SHorizontalBox::Slot().FillWidth(.5f)
      [SNew(SBorder).BorderImage(FAppStyle::GetBrush(TEXT("WhiteBrush"))).BorderBackgroundColor(Ink).Padding(30)
        [SNew(SScrollBox) + SScrollBox::Slot()[Content]]]
    + SHorizontalBox::Slot().FillWidth(.5f)[SNew(SBox)];
}
