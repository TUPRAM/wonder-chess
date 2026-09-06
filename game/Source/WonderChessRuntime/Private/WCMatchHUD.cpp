#include "Components/AudioComponent.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "GameFramework/GameUserSettings.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "WCBoardPresenter.h"
#include "WCMatchRuntime.h"
#include "WCNetworkSession.h"

namespace {
const FLinearColor Navy(.018, .033, .047, .97), Panel(.038, .065, .080, .95),
    Gold(.91, .71, .33), Muted(.60, .69, .71), Teal(.12, .52, .54);

FString T(const AWCMatchController *P, const TCHAR *English,
          const TCHAR *Indonesian) {
  return P && P->Language == TEXT("id") ? Indonesian : English;
}

template <typename... Args>
FString LocalizedPrintf(
    const AWCMatchController *P,
    UE::Core::TCheckedFormatString<FString::FmtCharType, Args...> English,
    UE::Core::TCheckedFormatString<FString::FmtCharType, Args...> Indonesian,
    Args... Values) {
  return P && P->Language == TEXT("id") ? FString::Printf(Indonesian, Values...)
                                        : FString::Printf(English, Values...);
}

FString Token(const AWCMatchController *P, const FString &Id) {
  struct Translation {
    const TCHAR *Id;
    const TCHAR *English;
    const TCHAR *Indonesian;
  };
  static const Translation Values[] = {
      {TEXT("human"), TEXT("Human"), TEXT("Manusia")},
      {TEXT("elf"), TEXT("Elf"), TEXT("Elf")},
      {TEXT("dwarf"), TEXT("Dwarf"), TEXT("Kurcaci")},
      {TEXT("orc"), TEXT("Orc"), TEXT("Orc")},
      {TEXT("guardian"), TEXT("Guardian"), TEXT("Penjaga")},
      {TEXT("warrior"), TEXT("Warrior"), TEXT("Petarung")},
      {TEXT("ranger"), TEXT("Ranger"), TEXT("Pemanah")},
      {TEXT("rogue"), TEXT("Rogue"), TEXT("Penyelinap")},
      {TEXT("mage"), TEXT("Mage"), TEXT("Penyihir")},
      {TEXT("priest"), TEXT("Priest"), TEXT("Pendeta")},
      {TEXT("balanced"), TEXT("Balanced"), TEXT("Seimbang")},
      {TEXT("spells"), TEXT("Spells"), TEXT("Sihir")},
      {TEXT("sustain"), TEXT("Sustain"), TEXT("Pemulihan")},
      {TEXT("tempo"), TEXT("Tempo"), TEXT("Tempo")},
      {TEXT("upgrades"), TEXT("Upgrades"), TEXT("Peningkatan bintang")},
      {TEXT("leveling"), TEXT("Leveling"), TEXT("Peningkatan level")},
      {TEXT("adaptive"), TEXT("Adaptive"), TEXT("Adaptif")},
      {TEXT("melee"), TEXT("Melee"), TEXT("Jarak dekat")},
      {TEXT("ranged"), TEXT("Ranged"), TEXT("Jarak jauh")}};
  for (const auto &Value : Values)
    if (Id == Value.Id)
      return T(P, Value.English, Value.Indonesian);
  return Id;
}

FString DamageLabel(const AWCMatchController *P, wc::DamageType Type) {
  return Type == wc::DamageType::Physical
             ? T(P, TEXT("Physical"), TEXT("Fisik"))
         : Type == wc::DamageType::Magic ? T(P, TEXT("Magic"), TEXT("Sihir"))
                                         : T(P, TEXT("True"), TEXT("Murni"));
}

FString TraitBonus(const AWCMatchController *P, const wc::TraitDef &Trait) {
  FString Stat;
  if (Trait.stat == "max_health_bonus_bp")
    Stat = TEXT("HP");
  else if (Trait.stat == "attack_rate_bonus_bp")
    Stat = T(P, TEXT("atk/s"), TEXT("srgn/dtk"));
  else if (Trait.stat == "physical_armor_flat")
    Stat = T(P, TEXT("armor"), TEXT("fisik"));
  else if (Trait.stat == "magic_resistance_flat")
    Stat = T(P, TEXT("resist"), TEXT("resist"));
  else if (Trait.stat == "basic_damage_bonus_bp")
    Stat = T(P, TEXT("basic"), TEXT("dasar"));
  else if (Trait.stat == "ability_damage_bonus_bp")
    Stat = T(P, TEXT("skill dmg"), TEXT("dmg skill"));
  else if (Trait.stat == "all_damage_bonus_bp")
    Stat = T(P, TEXT("all dmg"), TEXT("semua dmg"));
  else if (Trait.stat == "support_power_bonus_bp")
    Stat = T(P, TEXT("support"), TEXT("bantuan"));
  const bool Percent = Trait.stat.find("_bp") != std::string::npos;
  return Percent ? FString::Printf(TEXT("+%g%% %s"), Trait.value / 100.0, *Stat)
                 : FString::Printf(TEXT("+%d %s"), Trait.value, *Stat);
}

FString ReplyText(const AWCMatchController *P, const FString &Reason) {
  struct KeyedReason {
    const TCHAR *Reason;
    const TCHAR *Key;
  };
  static const KeyedReason Keys[] = {
      {TEXT("Not enough gold"), TEXT("error.funds")},
      {TEXT("Bench full; purchase does not resolve into a legal merge"),
       TEXT("error.bench")},
      {TEXT("Preparation is locked"), TEXT("error.phase")},
      {TEXT("Invalid seat ownership"), TEXT("error.ownership")},
      {TEXT("Unit is not owned"), TEXT("error.ownership")}};
  if (P->Presenter)
    for (const auto &Entry : Keys)
      if (Reason == Entry.Reason)
        return P->Presenter->Metadata.Localized(Entry.Key, P->Language);
  struct LocalReason {
    const TCHAR *Reason;
    const TCHAR *English;
    const TCHAR *Indonesian;
  };
  static const LocalReason Messages[] = {
      {TEXT("Accepted"), TEXT("Confirmed."), TEXT("Dikonfirmasi.")},
      {TEXT("Offer is empty or unavailable"),
       TEXT("That offer is no longer available."),
       TEXT("Tawaran itu tidak tersedia lagi.")},
      {TEXT("Already at maximum level"), TEXT("Maximum level reached."),
       TEXT("Level maksimum tercapai.")},
      {TEXT("Destination is outside own deployment"),
       TEXT("Choose a cell on your half of the board."),
       TEXT("Pilih petak di bagian papanmu.")},
      {TEXT("Invalid bench slot"), TEXT("Choose a valid bench slot."),
       TEXT("Pilih slot bangku yang sah.")},
      {TEXT("Move exceeds deployment capacity"),
       TEXT("Your board is full. Return a hero to the bench or level up."),
       TEXT("Papanmu penuh. Kembalikan hero ke bangku atau naikkan level.")},
      {TEXT("Seat is eliminated"),
       TEXT("You are eliminated. Choose a captain to spectate."),
       TEXT("Kamu tersingkir. Pilih kapten untuk ditonton.")},
      {TEXT("Out-of-order command sequence"),
       TEXT("That request arrived out of order. Try again."),
       TEXT("Urutan permintaan tidak sesuai. Coba lagi.")},
      {TEXT("Stale seat revision"),
       TEXT("Your team changed. Select the current item and try again."),
       TEXT("Timmu berubah. Pilih item terbaru dan coba lagi.")},
      {TEXT("Request ID reused with different payload"),
       TEXT("That request conflicts with an earlier one. Try again."),
       TEXT(
           "Permintaan bertentangan dengan permintaan sebelumnya. Coba lagi.")},
      {TEXT("Unknown command"), TEXT("That action is unavailable."),
       TEXT("Tindakan itu tidak tersedia.")},
      {TEXT("Invalid command payload."),
       TEXT("That action could not be read. Try again."),
       TEXT("Tindakan tidak dapat dibaca. Coba lagi.")},
      {TEXT("This controller has no active human seat."),
       TEXT("No active human seat is assigned to this player."),
       TEXT("Pemain ini tidak memiliki kursi aktif.")},
      {TEXT("Only the host can start or restart."),
       TEXT("Only the host can start a tournament."),
       TEXT("Hanya host yang dapat memulai turnamen.")},
      {TEXT("Two connected humans require 2H6B."),
       TEXT("Use two human seats and six bots for this lobby."),
       TEXT("Gunakan dua kursi pemain dan enam bot di lobi ini.")},
      {TEXT("Two connected humans are required. Return to title to create a "
            "fresh lobby after a disconnect."),
       TEXT("Connect both players. After a disconnect, return to the title for "
            "a fresh lobby."),
       TEXT("Hubungkan kedua pemain. Setelah koneksi terputus, kembali ke "
            "judul untuk lobi baru.")},
      {TEXT("The guided practice fixture could not be prepared."),
       TEXT("Guided practice could not be prepared."),
       TEXT("Latihan terpandu tidak dapat disiapkan.")},
      {TEXT("Please wait for queued commands."),
       TEXT("Please wait for your queued actions."),
       TEXT("Tunggu tindakan dalam antrean selesai.")},
      {TEXT("That offer changed. Select a current shop card."),
       TEXT("That offer changed. Select a current shop card."),
       TEXT("Tawaran berubah. Pilih kartu toko terbaru.")}};
  for (const auto &Entry : Messages)
    if (Reason == Entry.Reason)
      return T(P, Entry.English, Entry.Indonesian);
  return Reason;
}

struct FConfirmedFeedback {
  int64 Namespace = -1, Revision = -1;
  int Gold = 0, Phase = -1;
  TMap<int64, wc::OwnedUnit> Units;
  TSet<FString> ActiveTraits;
  TSet<int64> HighlightedUnits;
  FString Transaction, NewTraits;
  double TransactionTime = 0, TraitTime = 0;
};

FString UnitLocation(const AWCMatchController *P, const wc::OwnedUnit &Unit) {
  return Unit.onBoard
             ? LocalizedPrintf(P, TEXT("board %c%d"), TEXT("papan %c%d"),
                               TCHAR('A' + Unit.cell.column), Unit.cell.row + 1)
             : LocalizedPrintf(P, TEXT("bench %d"), TEXT("bangku %d"),
                               Unit.bench + 1);
}

FConfirmedFeedback &UpdateConfirmedFeedback(AWCMatchHUD *HUD,
                                            AWCMatchController *P) {
  static TMap<TWeakObjectPtr<AWCMatchHUD>, FConfirmedFeedback> History;
  for (auto It = History.CreateIterator(); It; ++It)
    if (!It.Key().IsValid())
      It.RemoveCurrent();
  auto &Previous = History.FindOrAdd(TWeakObjectPtr<AWCMatchHUD>(HUD));
  if (!P->Public.IsValid() || !P->Private.IsValid() || !P->Presenter ||
      !P->Private->HasField(TEXT("revision")) ||
      !P->Private->HasField(TEXT("units")))
    return Previous;
  const int64 Namespace =
      int64(P->Public->GetNumberField(TEXT("matchNamespace")));
  const int64 Revision = int64(P->Private->GetNumberField(TEXT("revision")));
  if (Namespace != Previous.Namespace) {
    Previous = FConfirmedFeedback{};
    Previous.Namespace = Namespace;
  }
  if (Revision == Previous.Revision)
    return Previous;
  const int Phase = int(P->Public->GetNumberField(TEXT("phase")));
  const auto &Defs = P->Presenter->Definitions;
  TMap<int64, wc::OwnedUnit> Current;
  TMap<FString, TSet<int>> Distinct;
  for (const auto &V : P->Private->GetArrayField(TEXT("units"))) {
    const auto U = V->AsObject();
    wc::OwnedUnit Unit;
    Unit.id = wc::Id(U->GetNumberField(TEXT("id")));
    Unit.definition = int(U->GetNumberField(TEXT("def")));
    Unit.star = int(U->GetNumberField(TEXT("star")));
    Unit.onBoard = U->GetBoolField(TEXT("board"));
    Unit.bench = int(U->GetNumberField(TEXT("bench")));
    Unit.cell = {int(U->GetNumberField(TEXT("col"))),
                 int(U->GetNumberField(TEXT("row")))};
    if (Unit.definition < 0 || Unit.definition >= int(Defs.units.size()))
      continue;
    Current.Add(int64(Unit.id), Unit);
    if (Unit.onBoard) {
      const auto &Definition = Defs.units[Unit.definition];
      Distinct.FindOrAdd(UTF8_TO_TCHAR(Definition.race.c_str()))
          .Add(Unit.definition);
      Distinct.FindOrAdd(UTF8_TO_TCHAR(Definition.unitClass.c_str()))
          .Add(Unit.definition);
    }
  }
  TSet<FString> Active;
  TArray<FString> Activated;
  for (const auto &Trait : Defs.traits) {
    const FString Id = UTF8_TO_TCHAR(Trait.id.c_str());
    if (Distinct.FindRef(Id).Num() >= Trait.threshold) {
      Active.Add(Id);
      if (!Previous.ActiveTraits.Contains(Id))
        Activated.Add(Token(P, Id) + TEXT(" ") + TraitBonus(P, Trait));
    }
  }
  const int CurrentGold = int(P->Private->GetNumberField(TEXT("gold")));
  // Explain a transaction only when both adjacent authoritative revisions were
  // seen. A skipped snapshot can contain several actions, so never guess its
  // cause.
  if (Previous.Revision >= 0 && Revision == Previous.Revision + 1 &&
      Phase == 0 && Previous.Phase == 0) {
    const double Now = FPlatformTime::Seconds();
    TArray<wc::OwnedUnit> Added, Removed;
    const wc::OwnedUnit *Upgraded = nullptr;
    for (const auto &Pair : Current) {
      const auto *Before = Previous.Units.Find(Pair.Key);
      if (!Before)
        Added.Add(Pair.Value);
      else if (Pair.Value.star > Before->star)
        Upgraded = &Pair.Value;
    }
    for (const auto &Pair : Previous.Units)
      if (!Current.Contains(Pair.Key))
        Removed.Add(Pair.Value);
    FString Notice;
    if (Upgraded && CurrentGold < Previous.Gold) {
      int Consumed[] = {0, 0, 0};
      for (const auto &Unit : Removed)
        if (Unit.definition == Upgraded->definition && Unit.star >= 1 &&
            Unit.star <= 3)
          ++Consumed[Unit.star - 1];
      TArray<FString> Copies;
      for (int Star = 1; Star <= 3; ++Star)
        if (Consumed[Star - 1])
          Copies.Add(LocalizedPrintf(P, TEXT("%d x %d-star"),
                                     TEXT("%d x bintang %d"),
                                     Consumed[Star - 1], Star));
      Copies.Add(T(P, TEXT("purchased copy"), TEXT("salinan yang dibeli")));
      Notice = LocalizedPrintf(
          P, TEXT("%s -> %d stars at %s. Absorbed: %s."),
          TEXT("%s -> bintang %d di %s. Digabung: %s."),
          UTF8_TO_TCHAR(Defs.units[Upgraded->definition].name.c_str()),
          Upgraded->star, *UnitLocation(P, *Upgraded),
          *FString::Join(Copies, TEXT(" + ")));
      Previous.HighlightedUnits.Reset();
      Previous.HighlightedUnits.Add(int64(Upgraded->id));
    } else if (Added.Num() == 1 && Removed.IsEmpty() &&
               CurrentGold < Previous.Gold) {
      const auto &Unit = Added[0];
      Notice = LocalizedPrintf(
          P, TEXT("Recruited %s to %s | %d gold paid."),
          TEXT("%s direkrut ke %s | membayar %d emas."),
          UTF8_TO_TCHAR(Defs.units[Unit.definition].name.c_str()),
          *UnitLocation(P, Unit), Previous.Gold - CurrentGold);
      Previous.HighlightedUnits.Reset();
      Previous.HighlightedUnits.Add(int64(Unit.id));
    } else if (Removed.Num() == 1 && Added.IsEmpty() &&
               CurrentGold > Previous.Gold) {
      Notice = LocalizedPrintf(
          P, TEXT("Sold %s (%d stars) | %d gold received."),
          TEXT("%s (bintang %d) dijual | menerima %d emas."),
          UTF8_TO_TCHAR(Defs.units[Removed[0].definition].name.c_str()),
          Removed[0].star, CurrentGold - Previous.Gold);
      Previous.HighlightedUnits.Reset();
    }
    if (!Notice.IsEmpty()) {
      Previous.Transaction = Notice;
      Previous.TransactionTime = Now;
    }
    if (!Activated.IsEmpty()) {
      Previous.NewTraits =
          T(P, TEXT("Synergy activated: "), TEXT("Sinergi aktif: ")) +
          FString::Join(Activated, TEXT(" | "));
      Previous.TraitTime = Now;
    }
  }
  Previous.Units = MoveTemp(Current);
  Previous.ActiveTraits = MoveTemp(Active);
  Previous.Revision = Revision;
  Previous.Phase = Phase;
  Previous.Gold = CurrentGold;
  return Previous;
}

bool IsSlider(const FString &Id) {
  return Id == TEXT("master") || Id == TEXT("music") || Id == TEXT("effects");
}
void SetSlider(AWCMatchController *P, const FString &Id, float Value) {
  float &Volume = Id == TEXT("master")  ? P->MasterVolume
                  : Id == TEXT("music") ? P->MusicVolume
                                        : P->EffectsVolume;
  Volume = FMath::Clamp(Value, 0.f, 1.f);
  if (IsValid(P->Music))
    P->Music->SetVolumeMultiplier(P->MasterVolume * P->MusicVolume);
}

bool CanEdit(const AWCMatchController *P) {
  if (!P || !P->Public.IsValid() || !P->Private.IsValid())
    return false;
  if (const auto *Session = Cast<UWCNetworkSession>(P->GetGameInstance());
      Session && Session->bMatchAborted)
    return false;
  if (int(P->Public->GetNumberField(TEXT("phase"))) !=
          int(wc::Phase::Preparation) ||
      P->AssignedSeat != P->ObservedSeat)
    return false;
  const auto &Seats = P->Public->GetArrayField(TEXT("seats"));
  return Seats.IsValidIndex(P->AssignedSeat) &&
         Seats[P->AssignedSeat]->AsObject()->GetNumberField(TEXT("health")) > 0;
}

wc::OwnedUnit Owned(const TSharedPtr<FJsonObject> &Json) {
  wc::OwnedUnit Unit;
  Unit.id = wc::Id(Json->GetNumberField(TEXT("id")));
  Unit.definition = int(Json->GetNumberField(TEXT("def")));
  Unit.star = int(Json->GetNumberField(TEXT("star")));
  Unit.onBoard = Json->GetBoolField(TEXT("board"));
  Unit.cell = {int(Json->GetNumberField(TEXT("col"))),
               int(Json->GetNumberField(TEXT("row")))};
  return Unit;
}

bool Inspection(AWCMatchController *P, wc::CombatUnit &Unit, bool &IsCombat,
                bool &IsDeployed) {
  if (!P->Presenter || P->InspectedDefinition < 0 ||
      P->InspectedDefinition >= int(P->Presenter->Definitions.units.size()))
    return false;
  const auto &Defs = P->Presenter->Definitions;
  IsCombat = P->bInspectedCombat;
  IsDeployed = false;
  if (IsCombat) {
    const int Phase = int(P->Public->GetNumberField(TEXT("phase")));
    if (Phase != int(wc::Phase::Combat) && Phase != int(wc::Phase::Settlement))
      return false;
    for (const auto &V : P->Presenter->VisibleUnits) {
      const auto Json = V->AsObject();
      if (int64(Json->GetNumberField(TEXT("id"))) != P->InspectedUnitId)
        continue;
      Unit.id = wc::Id(P->InspectedUnitId);
      Unit.definition = int(Json->GetNumberField(TEXT("def")));
      Unit.star = int(Json->GetNumberField(TEXT("star")));
      Unit.health = wc::Int(Json->GetNumberField(TEXT("hp")));
      Unit.maxHealth = wc::Int(Json->GetNumberField(TEXT("maxHp")));
      Unit.shield = wc::Int(Json->GetNumberField(TEXT("shield")));
      Unit.basicDamage = wc::Int(Json->GetNumberField(TEXT("basicDamage")));
      Unit.armor = int(Json->GetNumberField(TEXT("armor")));
      Unit.resistance = int(Json->GetNumberField(TEXT("resistance")));
      Unit.basicBonus = int(Json->GetNumberField(TEXT("basicBonus")));
      Unit.abilityBonus = int(Json->GetNumberField(TEXT("abilityBonus")));
      Unit.allBonus = int(Json->GetNumberField(TEXT("allBonus")));
      Unit.supportBonus = int(Json->GetNumberField(TEXT("supportBonus")));
      Unit.rateBonus = int(Json->GetNumberField(TEXT("effectiveRateBonus")));
      IsDeployed = true;
      return Unit.definition >= 0 && Unit.definition < int(Defs.units.size()) &&
             Unit.star >= 1 && Unit.star <= 3;
    }
    return false;
  }

  std::vector<wc::OwnedUnit> Formation;
  if (P->InspectedUnitId) {
    const auto &Seats = P->Public->GetArrayField(TEXT("seats"));
    for (const auto &Seat : Seats) {
      const auto &Units = Seat->AsObject()->GetArrayField(TEXT("units"));
      bool Found = false;
      for (const auto &V : Units)
        if (int64(V->AsObject()->GetNumberField(TEXT("id"))) ==
            P->InspectedUnitId)
          Found = true;
      if (!Found)
        continue;
      for (const auto &V : Units)
        Formation.push_back(Owned(V->AsObject()));
      IsDeployed = true;
      break;
    }
    if (Formation.empty() && P->Private.IsValid() &&
        P->Private->HasField(TEXT("units")))
      for (const auto &V : P->Private->GetArrayField(TEXT("units")))
        if (int64(V->AsObject()->GetNumberField(TEXT("id"))) ==
            P->InspectedUnitId) {
          auto Selected = Owned(V->AsObject());
          Selected.onBoard = true;
          Selected.cell = {0, 0};
          Formation.push_back(Selected);
          break;
        }
    if (Formation.empty())
      return false;
  } else {
    wc::OwnedUnit Offer;
    Offer.id = 1;
    Offer.definition = P->InspectedDefinition;
    Offer.onBoard = true;
    Offer.cell = {0, 0};
    Formation.push_back(Offer);
  }
  // Use the same constructor that locks formations for combat, including star
  // and trait rounding.
  const wc::Combat Preview(Defs, Formation, {}, 1);
  for (const auto &Candidate : Preview.Units())
    if (!P->InspectedUnitId || Candidate.id == wc::Id(P->InspectedUnitId)) {
      Unit = Candidate;
      return true;
    }
  return false;
}
} // namespace
void AWCMatchHUD::Text(const FString &V, float X, float Y, float Size,
                       FLinearColor Color) {
  DrawText(V, Color, OffsetX + X * Scale, OffsetY + Y * Scale,
           GEngine->GetMediumFont(), FMath::Max(Size, 1.25f) * Scale);
}
void AWCMatchHUD::Box(float X, float Y, float W, float H, FLinearColor Color) {
  DrawRect(Color, OffsetX + X * Scale, OffsetY + Y * Scale, W * Scale,
           H * Scale);
}
void AWCMatchHUD::Button(const FString &Id, const FString &Value, float X,
                         float Y, float W, float H, bool Enabled) {
  auto *P = Cast<AWCMatchController>(PlayerOwner);
  float MX = 0, MY = 0;
  if (P)
    P->GetMousePosition(MX, MY);
  const bool Hover =
      Enabled && MX >= OffsetX + X * Scale && MX <= OffsetX + (X + W) * Scale &&
      MY >= OffsetY + Y * Scale && MY <= OffsetY + (Y + H) * Scale;
  Box(X, Y, W, H,
      Enabled ? (Hover ? FLinearColor(.16, .28, .29, .98) : Panel)
              : FLinearColor(.055, .065, .07, .9));
  Box(X, Y, W, 2, Enabled ? Gold : FLinearColor(.18, .22, .22));
  float TextW, TextH;
  GetTextSize(Value, TextW, TextH, GEngine->GetMediumFont(), 1.3f);
  const float FontScale = TextW > W - 28 ? 1.3f * (W - 28) / TextW : 1.3f;
  const float LabelY = Id.StartsWith(TEXT("scout_")) ? Y + 8 : Y + H / 2 - 10;
  DrawText(Value, Enabled ? FLinearColor::White : Muted,
           OffsetX + (X + 14) * Scale, OffsetY + LabelY * Scale,
           GEngine->GetMediumFont(), FontScale * Scale);
  const bool OptionButton = Id == TEXT("options") || Id == TEXT("language") ||
                            Id == TEXT("master") || Id == TEXT("music") ||
                            Id == TEXT("effects") || Id == TEXT("motion") ||
                            Id == TEXT("window") || Id == TEXT("quit");
  if (Enabled) {
    Focusable.AddUnique(Id);
    AddHitBox(FVector2D(OffsetX + X * Scale, OffsetY + Y * Scale),
              FVector2D(W * Scale, H * Scale), FName(*Id), true,
              P && P->bOptions && OptionButton ? 100 : 10);
  }
  if (Enabled && Focused == Id) {
    Box(X + 3, Y + 3, W - 6, 3, Gold);
    Box(X + 3, Y + H - 6, W - 6, 3, Gold);
    Box(X + 3, Y + 3, 3, H - 6, Gold);
    Box(X + W - 6, Y + 3, 3, H - 6, Gold);
  }
}
void AWCMatchHUD::CycleFocus() {
  if (Focusable.Num()) {
    const int Index = Focusable.IndexOfByKey(Focused);
    Focused = Focusable[(Index + 1) % Focusable.Num()];
  }
}
void AWCMatchHUD::ActivateFocus() {
  if (Focusable.Contains(Focused)) {
    if (IsSlider(Focused))
      AdjustFocusedVolume(.1f);
    else
      Action(Focused);
  }
}
void AWCMatchHUD::AdjustFocusedVolume(float Delta) {
  if (auto *P = Cast<AWCMatchController>(PlayerOwner))
    if (P->bOptions && IsSlider(Focused)) {
      const float Current = Focused == TEXT("master")  ? P->MasterVolume
                            : Focused == TEXT("music") ? P->MusicVolume
                                                       : P->EffectsVolume;
      SetSlider(P, Focused, Current + Delta);
      P->SaveOptions();
    }
}
void AWCMatchHUD::Wrap(const FString &Value, float X, float Y, float Width,
                       float Size, FLinearColor Color) {
  Size = FMath::Max(Size, 1.25f);
  TArray<FString> Paragraphs;
  Value.ParseIntoArray(Paragraphs, TEXT("\n"), false);
  float DY = 0;
  for (const auto &Paragraph : Paragraphs) {
    TArray<FString> Words;
    Paragraph.ParseIntoArrayWS(Words);
    FString Line;
    for (const auto &Word : Words) {
      FString Candidate = Line.IsEmpty() ? Word : Line + TEXT(" ") + Word;
      float W, H;
      GetTextSize(Candidate, W, H, GEngine->GetMediumFont(), Size);
      if (W > Width && !Line.IsEmpty()) {
        Text(Line, X, Y + DY, Size, Color);
        DY += 16 * Size;
        Line = Word;
      } else
        Line = Candidate;
    }
    if (!Line.IsEmpty())
      Text(Line, X, Y + DY, Size, Color);
    DY += 16 * Size;
  }
}
FString AWCMatchHUD::Label(const FString &Key) const {
  if (auto *P = Cast<AWCMatchController>(PlayerOwner))
    if (P->Presenter)
      return P->Presenter->Metadata.Localized(Key, P->Language);
  return Key;
}
void AWCMatchHUD::DrawHUD() {
  Super::DrawHUD();
  if (!Canvas)
    return;
  HitBoxMap.Reset();
  Focusable.Reset();
  Scale = FMath::Min(Canvas->SizeX / 1920.f, Canvas->SizeY / 1080.f);
  OffsetX = (Canvas->SizeX - 1920 * Scale) / 2;
  OffsetY = (Canvas->SizeY - 1080 * Scale) / 2;
  auto *P = Cast<AWCMatchController>(PlayerOwner);
  if (!P)
    return;
  P->RefreshView();
  auto State = P->Public;
  auto Private = P->Private;
  if (IsSlider(Pressed)) {
    if (P->bOptions && P->IsInputKeyDown(EKeys::LeftMouseButton)) {
      float MX, MY;
      if (P->GetMousePosition(MX, MY))
        SetSlider(P, Pressed, ((MX - OffsetX) / Scale - 865.f) / 440.f);
    } else {
      P->SaveOptions();
      Pressed.Reset();
    }
  }
  const auto *Session = Cast<UWCNetworkSession>(P->GetGameInstance());
  const bool Aborted = Session && Session->bMatchAborted;
  const bool StateAborted =
      State.IsValid() &&
      int(State->GetNumberField(TEXT("phase"))) == int(wc::Phase::Aborted);
  if (Aborted || StateAborted) {
    P->SelectedUnit = 0;
    P->bOptions = false;
    Box(0, 0, 1920, 1080, Navy);
    Box(365, 230, 1190, 575, Panel);
    Box(365, 230, 1190, 4, Gold);
    Text(T(P, TEXT("MATCH ABORTED"), TEXT("PERTANDINGAN DIHENTIKAN")), 425, 290,
         2.25, Gold);
    const FString Reason =
        Aborted ? (Session->LastNetworkErrorKey.IsNone() || !P->Presenter
                       ? Session->LastNetworkError
                       : Label(Session->LastNetworkErrorKey.ToString()))
                : TEXT("This session ended without a winner.");
    Wrap(Reason, 425, 395, 1060, 1.3, FLinearColor::White);
    Text(T(P, TEXT("Return to the title to start a new tournament."),
           TEXT("Kembali ke judul untuk memulai turnamen baru.")),
         425, 525, 1.05, Muted);
    Button(TEXT("menu"),
           T(P, TEXT("Return to title"), TEXT("Kembali ke judul")), 425, 650,
           705, 72);
    Button(TEXT("quit"), Label(TEXT("menu.quit")), 1160, 650, 330, 72);
    return;
  }
  if (FParse::Param(FCommandLine::Get(), TEXT("WCArtReview"))) {
    Box(0, 0, 1920, 84, Navy);
    Text(TEXT("Unreal asset review - 12 heroes / authored clips"), 40, 26, 1.25,
         Gold);
    if (P->Presenter) {
      Box(0, 1000, 1920, 80, Navy);
      Wrap(P->Presenter->AssetStatus, 40, 1020, 1840, .95, Gold);
    }
    return;
  }
  if (!State.IsValid() || !P->Presenter) {
    Box(0, 0, 1920, 1080, Navy);
    Text(TEXT("WONDER CHESS"), 120, 340, 2.2, Gold);
    Text(T(P, TEXT("Entering the Seven-Lantern Courtyard..."),
           TEXT("Memasuki Seven-Lantern Courtyard...")),
         120, 420, 1, Muted);
    return;
  }
  auto &Defs = P->Presenter->Definitions;
  const int Phase = int(State->GetNumberField(TEXT("phase")));
  if (Phase == int(wc::Phase::Finished))
    P->bRecap = false;
  const FString Error = State->GetStringField(TEXT("error"));
  if (!Error.IsEmpty()) {
    Box(160, 260, 1600, 400, Navy);
    Text(T(P, TEXT("Cannot start this build"),
           TEXT("Versi ini tidak dapat dimulai")),
         210, 310, 1.8, Gold);
    Wrap(Error, 210, 400, 1450, 1.1, Muted);
    return;
  }
  auto &ConfirmedFeedback = UpdateConfirmedFeedback(this, P);
  const double FeedbackNow = FPlatformTime::Seconds();
  const bool RecentTransaction =
      !ConfirmedFeedback.Transaction.IsEmpty() &&
      FeedbackNow - ConfirmedFeedback.TransactionTime < 5;
  if (Phase < 0) {
    Box(70, 120, 820, 820, Navy);
    Box(70, 120, 820, 4, Gold);
    Text(TEXT("WONDER"), 125, 175, 3.8, Gold);
    Text(TEXT("CHESS"), 125, 258, 3.8, Gold);
    Text(T(P, TEXT("A world of magic. A board of possibilities."),
           TEXT("Dunia penuh sihir. Papan penuh kemungkinan.")),
         130, 365, 1.2, Muted);
    Text(TEXT("THE SEVEN-LANTERN TRIALS"), 130, 430, .85, Gold);
    Wrap(T(P,
           TEXT("Recruit twelve champions. Discover their affinities. Arrange "
                "your company and face seven persistent rivals in an "
                "eight-seat tournament."),
           TEXT("Rekrut dua belas hero. Temukan sinergi mereka. Susun tim dan "
                "hadapi tujuh lawan tetap dalam turnamen delapan kursi.")),
         130, 472, 680, 1.1, FLinearColor::White);
    const bool Network = State->GetBoolField(TEXT("network"));
    Button(TEXT("start"),
           Network ? T(P, TEXT("Start 2 humans + 6 bots"),
                       TEXT("Mulai 2 pemain + 6 bot"))
                   : Label(TEXT("menu.play")),
           130, 590, 680, 64,
           P->AssignedSeat <= 0 && !P->bTutorial &&
               (!Network || State->GetNumberField(TEXT("connected")) == 2));
    Button(TEXT("host"),
           T(P, TEXT("Host LAN lobby | 2H6B"), TEXT("Buat lobi LAN | 2H6B")),
           130, 670, 330, 56, !Network);
    Button(TEXT("join"),
           T(P, TEXT("Join local host"), TEXT("Gabung host lokal")), 480, 670,
           330, 56, !Network);
    Text(T(P, TEXT("LAN: WonderChess.exe -WCJoin=<host IPv4>:7777"),
           TEXT("LAN: WonderChess.exe -WCJoin=<IPv4 host>:7777")),
         130, 746, .82, Muted);
    Button(TEXT("options"), Label(TEXT("menu.options")), 130, 800, 220, 56);
    Button(TEXT("tutorial"), T(P, TEXT("How to play"), TEXT("Cara bermain")),
           365, 800, 220, 56);
    Button(TEXT("quit"), Label(TEXT("menu.quit")), 600, 800, 210, 56);
    if (Network)
      Text(LocalizedPrintf(P, TEXT("Connected humans: %d / 2"),
                           TEXT("Pemain terhubung: %d / 2"),
                           int(State->GetNumberField(TEXT("connected")))),
           130, 884, 1, Gold);
    else
      Button(TEXT("practice"),
             T(P, TEXT("Guided practice | fixed shop seed"),
               TEXT("Latihan terpandu | seed toko tetap")),
             130, 877, 680, 46, !P->bTutorial);
    Box(955, 120, 865, 820, Navy);
    Box(955, 120, 865, 4, Gold);
    Text(T(P, TEXT("YOUR TOURNAMENT LOBBY"), TEXT("LOBI TURNAMENMU")), 995, 160,
         1.5, Gold);
    const int Humans = Network ? 2 : 1;
    const int Connected =
        Network ? int(State->GetNumberField(TEXT("connected"))) : 1;
    const auto &Profiles =
        P->Presenter->Metadata.Bots->GetArrayField(TEXT("bots"));
    for (int Seat = 0; Seat < Defs.rules.seatCount; ++Seat) {
      const float Y = 230 + Seat * 65;
      Box(992, Y, 790, 55, Panel);
      if (Seat < Humans) {
        Text(LocalizedPrintf(P, TEXT("%d  Captain %d"), TEXT("%d  Kapten %d"),
                             Seat + 1, Seat + 1),
             1012, Y + 9, .98, Gold);
        Text(Seat < Connected
                 ? T(P, TEXT("Human - connected"), TEXT("Pemain - terhubung"))
                 : T(P, TEXT("Human - waiting for LAN player"),
                     TEXT("Pemain - menunggu koneksi LAN")),
             1325, Y + 12, .82, Muted);
      } else {
        const int BotIndex = (Seat - Humans) % int(Defs.bots.size());
        const auto Profile = Profiles[BotIndex]->AsObject();
        Text(FString::Printf(TEXT("%d  %s"), Seat + 1,
                             UTF8_TO_TCHAR(Defs.bots[BotIndex].label.c_str())),
             1012, Y + 9, .98);
        Text(TEXT("BOT  |  ") +
                 Token(P, Profile->GetStringField(TEXT("focus"))),
             1325, Y + 12, .82, Muted);
      }
    }
    Wrap(T(P,
           TEXT("Policy: bots use the same commands and shop rules, and scout "
                "only public information. Their distinct preferences persist "
                "through the tournament."),
           TEXT("Kebijakan: bot memakai perintah dan aturan toko yang sama, "
                "serta hanya melihat informasi publik. Preferensi tiap bot "
                "tetap selama turnamen.")),
         995, 782, 775, 1, Muted);
    Text(LocalizedPrintf(P, TEXT("%d human + %d bots | Eight persistent seats"),
                         TEXT("%d pemain + %d bot | Delapan kursi tetap"),
                         Humans, Defs.rules.seatCount - Humans),
         995, 884, .9, Gold);
  } else {
    const int Round = int(State->GetNumberField(TEXT("round")));
    const int Remaining =
        FMath::CeilToInt(State->GetNumberField(TEXT("remaining")) / 1000.0);
    Box(0, 0, 1920, 110, Navy);
    Text(TEXT("WONDER CHESS"), 34, 24, 1.45, Gold);
    Text(TEXT("SEVEN-LANTERN COURTYARD"), 35, 63, .75, Muted);
    FString PhaseText = Phase == 0   ? Label(TEXT("match.preparation"))
                        : Phase == 1 ? Label(TEXT("match.combat"))
                        : Phase == 2
                            ? T(P, TEXT("Round recap"), TEXT("Ringkasan ronde"))
                        : Phase == 3 ? Label(TEXT("match.results"))
                                     : Label(TEXT("result.abort"));
    Text(LocalizedPrintf(P, TEXT("ROUND %02d / %s"), TEXT("RONDE %02d / %s"),
                         Round, *PhaseText),
         600, 24, 1.35, Gold);
    const bool PracticeWaiting =
        State->HasField(TEXT("practice")) &&
        State->GetBoolField(TEXT("practice")) && Round == 1 && Phase == 0 &&
        Private.IsValid() && !Private->GetBoolField(TEXT("ready"));
    Text(PracticeWaiting ? T(P, TEXT("Untimed practice - press Ready"),
                             TEXT("Latihan tanpa batas waktu - tekan Siap"))
                         : LocalizedPrintf(P, TEXT("%02d seconds"),
                                           TEXT("%02d detik"), Remaining),
         PracticeWaiting ? 600 : 820, 65, .9, Muted);
    Button(TEXT("home"), Label(TEXT("match.return")), 1160, 24, 260, 56);
    Button(TEXT("options"), Label(TEXT("menu.options")), 1750, 24, 140, 56);
    Button(TEXT("recap"), T(P, TEXT("Round recap"), TEXT("Ringkasan ronde")),
           1450, 24, 260, 56, State->HasField(TEXT("recap")));
    const auto &Seats = State->GetArrayField(TEXT("seats"));
    auto Own = Seats.IsValidIndex(P->AssignedSeat)
                   ? Seats[P->AssignedSeat]->AsObject()
                   : TSharedPtr<FJsonObject>();
    const bool Alive = Own.IsValid() && Own->GetNumberField(TEXT("health")) > 0;
    const bool Editable = CanEdit(P);
    Box(1580, 138, 310, 610, Navy);
    Text(T(P, TEXT("THE EIGHT CAPTAINS"), TEXT("DELAPAN KAPTEN")), 1598, 158,
         .9, Gold);
    for (int I = 0; I < Seats.Num(); ++I) {
      auto S = Seats[I]->AsObject();
      FString Name = S->GetStringField(TEXT("name"));
      int Hp = int(S->GetNumberField(TEXT("health")));
      int Place = int(S->GetNumberField(TEXT("place")));
      Button(TEXT("scout_") + FString::FromInt(I),
             FString::Printf(TEXT("%d  %s"), I + 1, *Name), 1595, 200 + I * 64,
             280, 54);
      Text(Hp > 0 ? FString::Printf(TEXT("%d HP | Lv %d %s"), Hp,
                                    int(S->GetNumberField(TEXT("level"))),
                                    *(S->GetBoolField(TEXT("human"))
                                          ? T(P, TEXT("HUMAN"), TEXT("PEMAIN"))
                                          : FString(TEXT("BOT"))))
                  : LocalizedPrintf(P, TEXT("Placed %d - eliminated"),
                                    TEXT("Peringkat %d - tersingkir"), Place),
           1610, 230 + I * 64, .70, Hp > 0 ? Muted : Gold);
    }
    int Opponent = -1;
    bool Ghost = false;
    for (const auto &Pair : State->GetArrayField(TEXT("pairs"))) {
      auto V = Pair->AsObject();
      int A = int(V->GetNumberField(TEXT("a"))),
          B = int(V->GetNumberField(TEXT("b")));
      if (A == P->ObservedSeat) {
        Opponent = B;
        Ghost = V->GetBoolField(TEXT("ghost"));
        break;
      }
      if (B == P->ObservedSeat && !V->GetBoolField(TEXT("ghost"))) {
        Opponent = A;
        break;
      }
    }
    if (Seats.IsValidIndex(P->ObservedSeat)) {
      Box(460, 124, 1080, 47, Navy);
      Text((P->ObservedSeat == P->AssignedSeat
                ? T(P, TEXT("VIEWING  "), TEXT("MELIHAT  "))
                : T(P, TEXT("SCOUTING  "), TEXT("MENGAMATI  "))) +
               Seats[P->ObservedSeat]->AsObject()->GetStringField(TEXT("name")),
           480, 135, 1, Muted);
      if (Seats.IsValidIndex(Opponent))
        Text((Ghost ? T(P, TEXT("GHOST OF  "), TEXT("SALINAN  "))
                    : T(P, TEXT("VERSUS  "), TEXT("MELAWAN  "))) +
                 Seats[Opponent]->AsObject()->GetStringField(TEXT("name")),
             980, 135, 1, Gold);
    }
    if (P->Presenter) {
      for (const auto &V : P->Presenter->VisibleUnits) {
        auto U = V->AsObject();
        int64 Id = int64(U->GetNumberField(TEXT("id")));
        if (!P->Presenter->Heroes.Contains(Id))
          continue;
        auto *A = P->Presenter->Heroes[Id];
        FVector2D Screen;
        P->ProjectWorldLocationToScreen(
            A->GetActorLocation() + FVector(0, 0, 205), Screen);
        float X = (Screen.X - OffsetX) / Scale,
              Y = (Screen.Y - OffsetY) / Scale;
        int D = int(U->GetNumberField(TEXT("def")));
        if (D < 0 || D >= int(Defs.units.size()))
          continue;
        if (U->GetNumberField(TEXT("hp")) > 0) {
          Box(X - 40, Y, 80, 5, FLinearColor(.06, .07, .07));
          Box(X - 40, Y,
              80 * U->GetNumberField(TEXT("hp")) /
                  FMath::Max(1.0, U->GetNumberField(TEXT("maxHp"))),
              5,
              U->GetNumberField(TEXT("side")) == 0
                  ? Teal
                  : FLinearColor(.82, .33, .17));
        }
        if (U->GetNumberField(TEXT("shield")) > 0)
          Text(LocalizedPrintf(P, TEXT("SHIELD %.0f"), TEXT("PERISAI %.0f"),
                               U->GetNumberField(TEXT("shield")) / 100),
               X - 40, Y - 17, .63, Gold);
        if (U->GetNumberField(TEXT("stun")) > 0)
          Text(T(P, TEXT("STUN"), TEXT("LUMPUH")), X - 20, Y + 10, .7, Gold);
        Text(FString::ChrN(int(U->GetNumberField(TEXT("star"))), TEXT('*')),
             X - 10, Y - 30, .8, Gold);
        if (P->SelectedUnit == Id) {
          Box(X - 46, Y + 10, 92, 3, Gold);
          Box(X - 46, Y + 92, 92, 3, Gold);
          Box(X - 46, Y + 10, 3, 85, Gold);
          Box(X + 43, Y + 10, 3, 85, Gold);
          Text(T(P, TEXT("SELECTED"), TEXT("TERPILIH")), X - 40, Y - 48, .62,
               Gold);
        }
        if (RecentTransaction &&
            ConfirmedFeedback.HighlightedUnits.Contains(Id))
          Box(X - 45, Y - 5, 90, 4, Teal);
        AddHitBox(FVector2D(Screen.X - 45 * Scale, Screen.Y + 10 * Scale),
                  FVector2D(90 * Scale, 85 * Scale),
                  FName(*((Editable ? TEXT("unit_") : TEXT("inspect_")) +
                          FString::Printf(TEXT("%lld"), Id))),
                  true, 20);
      }
      if (Editable)
        for (int R = 0; R < 4; ++R)
          for (int C = 0; C < 8; ++C) {
            FVector2D S;
            P->ProjectWorldLocationToScreen(P->Presenter->Position(C, R), S);
            AddHitBox(FVector2D(S.X - 50 * Scale, S.Y - 24 * Scale),
                      FVector2D(100 * Scale, 48 * Scale),
                      FName(*FString::Printf(TEXT("cell_%d_%d"), C, R)), true,
                      0);
          }
    }
    Box(25, 145, 290, 901, Navy);
    Text(Label(TEXT("ui.synergies")), 45, 164, 1.05, Gold);
    TMap<FString, TSet<int>> Counts;
    if (Seats.IsValidIndex(P->ObservedSeat))
      for (const auto &V :
           Seats[P->ObservedSeat]->AsObject()->GetArrayField(TEXT("units"))) {
        int D = int(V->AsObject()->GetNumberField(TEXT("def")));
        if (D < 0 || D >= int(Defs.units.size()))
          continue;
        Counts.FindOrAdd(UTF8_TO_TCHAR(Defs.units[D].race.c_str())).Add(D);
        Counts.FindOrAdd(UTF8_TO_TCHAR(Defs.units[D].unitClass.c_str())).Add(D);
      }
    int Line = 0;
    for (const auto &Trait : Defs.traits) {
      FString Id = UTF8_TO_TCHAR(Trait.id.c_str());
      int N = Counts.Contains(Id) ? Counts[Id].Num() : 0;
      if (N) {
        Text(FString::Printf(TEXT("%s %d/%d"), *Token(P, Id), N,
                             Trait.threshold),
             45, 203 + Line * 21, .69, N >= Trait.threshold ? Gold : Muted);
        Text(TraitBonus(P, Trait), 172, 203 + Line * 21, .62,
             N >= Trait.threshold ? Gold : Muted);
        ++Line;
      }
    }
    if (Line == 0)
      Wrap(T(P,
             TEXT("Two distinct deployed heroes activate a shared race or "
                  "class."),
             TEXT("Dua hero berbeda di papan mengaktifkan sinergi ras atau "
                  "kelas yang sama.")),
           45, 204, 245, .9, Muted);
    wc::CombatUnit Inspected;
    bool IsCombat = false, IsDeployed = false;
    if (Inspection(P, Inspected, IsCombat, IsDeployed)) {
      const auto &U = Defs.units[Inspected.definition];
      const auto &Skill = U.ability;
      FString Id = UTF8_TO_TCHAR(U.id.c_str());
      Text(UTF8_TO_TCHAR(U.name.c_str()), 45, 425, .96, Gold);
      const FString Portrait = TEXT("/Game/WonderChess/Heroes/") + Id +
                               TEXT("/T_") + Id + TEXT("_Portrait.T_") + Id +
                               TEXT("_Portrait");
      if (auto *Texture = LoadObject<UTexture2D>(nullptr, *Portrait))
        DrawTextureSimple(Texture, OffsetX + 45 * Scale, OffsetY + 459 * Scale,
                          (48.f / Texture->GetSizeX()) * Scale);
      Text(FString::Printf(TEXT("%s  |  %d %s"),
                           *FString::ChrN(Inspected.star, TEXT('*')), U.cost,
                           *Label(TEXT("ui.gold"))),
           104, 458, .76, Gold);
      Text(Token(P, UTF8_TO_TCHAR(U.race.c_str())) + TEXT(" / ") +
               Token(P, UTF8_TO_TCHAR(U.unitClass.c_str())),
           104, 483, .72, Muted);
      Text(IsCombat     ? T(P, TEXT("Live combat: traits + buffs"),
                            TEXT("Pertempuran: sinergi + efek"))
           : IsDeployed ? T(P, TEXT("Formation: star + active traits"),
                            TEXT("Formasi: bintang + sinergi aktif"))
                        : T(P, TEXT("Base star stats; no team traits"),
                            TEXT("Stat bintang; tanpa sinergi tim")),
           45, 516, .65, Muted);
      Text(FString::Printf(TEXT("HP %.2f / %.2f"), Inspected.health / 100.0,
                           Inspected.maxHealth / 100.0),
           45, 543, .8);
      const wc::Int Attack =
          wc::ResolveDamage(Inspected.basicDamage, wc::DamageType::True, 0, 0,
                            Inspected.basicBonus + Inspected.allBonus);
      Text(LocalizedPrintf(P, TEXT("ATK %.2f before defense"),
                           TEXT("ATK %.2f sebelum pertahanan"), Attack / 100.0),
           45, 568, .72);
      const auto *Authored = P->Presenter->Metadata.Units.Find(Id);
      const FString Delivery =
          Authored ? Token(P, (*Authored)
                                  ->GetObjectField(TEXT("stats"))
                                  ->GetStringField(TEXT("attack_delivery")))
                   : FString();
      Text(DamageLabel(P, U.damageType) + TEXT(" / ") + Delivery, 45, 591, .73,
           Gold);
      Text(LocalizedPrintf(P, TEXT("Armor %d / Magic resist %d"),
                           TEXT("Fisik %d / Resist sihir %d"), Inspected.armor,
                           Inspected.resistance),
           45, 615, .73, Muted);
      const int Interval =
          wc::AttackInterval(U.attackRate, Inspected.rateBonus, Defs.rules) *
          Defs.rules.tickMs;
      Text(LocalizedPrintf(P, TEXT("Range %d | %.2f attacks/s"),
                           TEXT("Jarak %d | %.2f serangan/dtk"), U.range,
                           1000.0 / Interval),
           45, 639, .7, Muted);
      Text(LocalizedPrintf(P, TEXT("Shield %.2f"), TEXT("Perisai %.2f"),
                           Inspected.shield / 100.0),
           45, 663, .73, Gold);
      Text(UTF8_TO_TCHAR(Skill.name.c_str()), 45, 696, .82, Gold);
      Wrap(P->Presenter->Metadata.AbilityTooltip(Id, P->Language), 45, 723, 247,
           .73, FLinearColor::White);
      wc::Int Power = Skill.magnitude[Inspected.star - 1];
      if (Skill.effect == wc::Effect::Damage)
        Power = wc::ResolveDamage(Power, wc::DamageType::True, 0, 0,
                                  Inspected.abilityBonus + Inspected.allBonus);
      else if (Skill.effect == wc::Effect::Heal ||
               Skill.effect == wc::Effect::Shield ||
               (Skill.effect == wc::Effect::StatModifier && Power > 0))
        Power = wc::HalfUp(Power * (10000 + Inspected.supportBonus), 10000);
      FString Magnitude;
      if (Skill.effect == wc::Effect::StatModifier)
        Magnitude =
            LocalizedPrintf(P, TEXT("Attack rate %+0.2f%%"),
                            TEXT("Laju serangan %+0.2f%%"), Power / 100.0);
      else if (Skill.effect == wc::Effect::Stun)
        Magnitude = T(P, TEXT("Stuns affected enemies"),
                      TEXT("Melumpuhkan musuh terkena"));
      else if (Skill.effect == wc::Effect::Dash)
        Magnitude =
            LocalizedPrintf(P, TEXT("Dash up to %d cells"),
                            TEXT("Lari cepat hingga %d petak"), Skill.maxDash);
      else
        Magnitude =
            FString::Printf(TEXT("%s %.2f"),
                            *(Skill.effect == wc::Effect::Damage
                                  ? DamageLabel(P, Skill.damageType)
                              : Skill.effect == wc::Effect::Heal
                                  ? T(P, TEXT("Heal"), TEXT("Pemulihan"))
                                  : T(P, TEXT("Shield"), TEXT("Perisai"))),
                            Power / 100.0);
      Text(Magnitude, 45, 799, .75, Gold);
      if (Skill.effect == wc::Effect::Damage)
        Text(T(P, TEXT("Skill damage before defense"),
               TEXT("Damage skill sebelum pertahanan")),
             45, 823, .64, Muted);
      Text(LocalizedPrintf(P, TEXT("Duration %.2fs | Range %d"),
                           TEXT("Durasi %.2fdtk | Jarak %d"),
                           Skill.durationMs / 1000.0, Skill.range),
           45, 847, .68, Muted);
      Text(LocalizedPrintf(P, TEXT("Radius %d | Max targets %d"),
                           TEXT("Radius %d | Maks target %d"), Skill.radius,
                           Skill.maxTargets),
           45, 870, .68, Muted);
      Text(LocalizedPrintf(P, TEXT("First %.2fs | Cooldown %.2fs"),
                           TEXT("Awal %.2fdtk | Jeda %.2fdtk"),
                           Skill.firstCastMs / 1000.0,
                           Skill.cooldownMs / 1000.0),
           45, 893, .65, Muted);
      Text(LocalizedPrintf(P, TEXT("Cast %.2fs | Recovery %.2fs"),
                           TEXT("Cast %.2fdtk | Pulih %.2fdtk"),
                           Skill.castMs / 1000.0, Skill.recoveryMs / 1000.0),
           45, 916, .65, Muted);
      Text(LocalizedPrintf(P, TEXT("Travel %.2fs"),
                           TEXT("Waktu proyektil %.2fdtk"),
                           Skill.travelMs / 1000.0),
           45, 939, .65, Muted);
    } else
      Wrap(T(P,
             TEXT("Select any visible champion to inspect its stats and active "
                  "skill. Select your bench hero, then a cell on your half to "
                  "deploy. Three identical copies upgrade automatically."),
             TEXT("Pilih hero yang terlihat untuk memeriksa statistik dan "
                  "skill. Pilih hero di bangku, lalu petak di bagian papanmu "
                  "untuk menempatkannya. Tiga salinan yang sama naik bintang "
                  "otomatis.")),
           45, 440, 245, .91, Muted);
    Box(335, 782, 1215, 285, Navy);
    if (Private.IsValid() && Private->HasField(TEXT("gold"))) {
      int GoldValue = int(Private->GetNumberField(TEXT("gold"))),
          Level = int(Private->GetNumberField(TEXT("level"))),
          Xp = int(Private->GetNumberField(TEXT("xp")));
      int Deployed = 0;
      for (const auto &V : Private->GetArrayField(TEXT("units")))
        if (V->AsObject()->GetBoolField(TEXT("board")))
          ++Deployed;
      const int BenchCount =
          Private->GetArrayField(TEXT("units")).Num() - Deployed;
      const FString Progress =
          Level >= Defs.rules.maximumLevel
              ? T(P, TEXT("MAX"), TEXT("MAKS"))
              : FString::Printf(TEXT("%d/%d"), Xp,
                                Defs.rules.xpToNext.at(Level));
      Text(LocalizedPrintf(
               P,
               TEXT("%d GOLD   /   LEVEL %d   /   XP %s   /   DEPLOYED %d/%d"),
               TEXT("%d EMAS   /   LEVEL %d   /   XP %s   /   DI PAPAN %d/%d"),
               GoldValue, Level, *Progress, Deployed, Level),
           355, 799, 1, Gold);
      for (int B = 0; B < 8; ++B) {
        TSharedPtr<FJsonObject> Found;
        for (const auto &V : Private->GetArrayField(TEXT("units"))) {
          auto U = V->AsObject();
          if (!U->GetBoolField(TEXT("board")) &&
              int(U->GetNumberField(TEXT("bench"))) == B) {
            Found = U;
            break;
          }
        }
        FString Caption = FString::Printf(TEXT("%d"), B + 1);
        if (Found) {
          int D = int(Found->GetNumberField(TEXT("def")));
          if (D >= 0 && D < int(Defs.units.size())) {
            Caption = UTF8_TO_TCHAR(Defs.units[D].name.c_str());
            int Space;
            if (Caption.FindChar(TEXT(' '), Space))
              Caption = Caption.Left(Space);
            Caption += FString::ChrN(int(Found->GetNumberField(TEXT("star"))),
                                     TEXT('*'));
          }
        }
        Button(TEXT("bench_") + FString::FromInt(B), Caption, 355 + B * 146,
               838, 135, 48, Editable || Found.IsValid());
        if (Found &&
            int64(Found->GetNumberField(TEXT("id"))) == P->SelectedUnit) {
          Box(355 + B * 146, 838, 135, 4, Gold);
          Box(355 + B * 146, 882, 135, 4, Gold);
        }
        if (Found && RecentTransaction &&
            ConfirmedFeedback.HighlightedUnits.Contains(
                int64(Found->GetNumberField(TEXT("id"))))) {
          Box(358 + B * 146, 843, 129, 3, Teal);
          Box(358 + B * 146, 878, 129, 3, Teal);
        }
      }
      const auto &Shop = Private->GetArrayField(TEXT("shop"));
      for (int I = 0; I < Shop.Num(); ++I) {
        const int D = int(Shop[I]->AsNumber());
        const float X = 355 + I * 234;
        Box(X, 905, 224, 146, Panel);
        if (D < 0 || D >= int(Defs.units.size())) {
          Text(T(P, TEXT("Recruited"), TEXT("Sudah direkrut")), X + 35, 965,
               .85, Muted);
          continue;
        }
        const auto &U = Defs.units[D];
        const FString Id = UTF8_TO_TCHAR(U.id.c_str());
        const FString Path = TEXT("/Game/WonderChess/Heroes/") + Id +
                             TEXT("/T_") + Id + TEXT("_Portrait.T_") + Id +
                             TEXT("_Portrait");
        if (auto *Texture = LoadObject<UTexture2D>(nullptr, *Path))
          DrawTextureSimple(Texture, OffsetX + (X + 5) * Scale,
                            OffsetY + 912 * Scale,
                            (62.f / Texture->GetSizeX()) * Scale);
        AddHitBox(FVector2D(OffsetX + X * Scale, OffsetY + 905 * Scale),
                  FVector2D(224 * Scale, 90 * Scale),
                  FName(*(TEXT("offer_") + FString::FromInt(I))), true, 10);
        Wrap(UTF8_TO_TCHAR(U.name.c_str()), X + 74, 912, 142, 1.25, Gold);
        Text(Token(P, UTF8_TO_TCHAR(U.race.c_str())) + TEXT(" / ") +
                 Token(P, UTF8_TO_TCHAR(U.unitClass.c_str())),
             X + 74, 966, .68, Muted);
        int Copies = 0, TwoStars = 0;
        for (const auto &V : Private->GetArrayField(TEXT("units"))) {
          const auto Unit = V->AsObject();
          if (int(Unit->GetNumberField(TEXT("def"))) == D) {
            if (Unit->GetNumberField(TEXT("star")) == 1)
              ++Copies;
            if (Unit->GetNumberField(TEXT("star")) == 2)
              ++TwoStars;
          }
        }
        const bool Merge = Copies >= 2,
                   Full = BenchCount >= Defs.rules.benchCapacity;
        FString Feedback = Merge ? LocalizedPrintf(P, TEXT("MERGE -> %d stars"),
                                                   TEXT("GABUNG -> %d bintang"),
                                                   TwoStars >= 2 ? 3 : 2)
                           : Full ? T(P, TEXT("Bench full - no merge"),
                                      TEXT("Bangku penuh - tak bergabung"))
                                  : FString();
        if (GoldValue < U.cost)
          Feedback =
              LocalizedPrintf(P, TEXT("Need %d more gold"),
                              TEXT("Perlu %d emas lagi"), U.cost - GoldValue);
        Text(Feedback, X + 7, 984, .65, Merge ? Gold : Muted);
        Button(TEXT("buy_") + FString::FromInt(I),
               FString::Printf(TEXT("%s - %d %s"), *Label(TEXT("shop.buy")),
                               U.cost, *Label(TEXT("ui.gold"))),
               X + 7, 1006, 210, 36,
               Editable && GoldValue >= U.cost && (!Full || Merge));
      }
      Button(TEXT("reroll"),
             Label(TEXT("shop.reroll"))
                 .Replace(TEXT("{cost}"),
                          *FString::FromInt(Defs.rules.rerollCost)),
             1585, 785, 290, 50, Editable);
      Button(
          TEXT("xp"),
          Label(TEXT("shop.xp"))
              .Replace(TEXT("{xp}"), *FString::FromInt(Defs.rules.buyXpAmount))
              .Replace(TEXT("{cost}"), *FString::FromInt(Defs.rules.buyXpGold)),
          1585, 846, 290, 50, Editable && Level < Defs.rules.maximumLevel);
      Button(TEXT("lock"),
             Private->GetBoolField(TEXT("locked"))
                 ? T(P, TEXT("Unlock shop"), TEXT("Buka kunci toko"))
                 : Label(TEXT("shop.lock")),
             1585, 907, 290, 50, Editable);
      Button(TEXT("ready"),
             Private->GetBoolField(TEXT("ready"))
                 ? T(P, TEXT("READY - waiting"), TEXT("SIAP - menunggu"))
                 : Label(TEXT("match.ready")),
             1585, 968, 290, 74,
             Phase == 0 && Alive && !Private->GetBoolField(TEXT("ready")));
    }
    if (P->SelectedUnit) {
      Button(TEXT("sell"),
             T(P, TEXT("Sell selected hero"), TEXT("Jual hero terpilih")), 34,
             982, 275, 52, Editable);
    }
    if (!Alive && Phase < 3) {
      Box(335, 782, 1215, 276, Navy);
      Text(LocalizedPrintf(
               P,
               TEXT("Placed %d. Select a captain to spectate; bots keep "
                    "playing."),
               TEXT("Peringkat %d. Pilih kapten untuk menonton; bot terus "
                    "bermain."),
               Own.IsValid() ? int(Own->GetNumberField(TEXT("place"))) : 0),
           382, 835, .91, Gold);
      Button(TEXT("menu"),
             T(P, TEXT("Return to title"), TEXT("Kembali ke judul")), 382, 890,
             350, 40);
      Button(TEXT("newsolo"),
             T(P, TEXT("New solo tournament"), TEXT("Turnamen solo baru")), 752,
             890, 360, 40);
    }
    if ((Phase == 2 || P->bRecap) && State->HasField(TEXT("recap")) &&
        Phase != 3) {
      const auto Rec = State->GetObjectField(TEXT("recap"));
      const auto &Fights = Rec->GetArrayField(TEXT("encounters"));
      int SelectedFight = 0;
      for (int I = 0; I < Fights.Num(); ++I) {
        const auto F = Fights[I]->AsObject();
        if (int(F->GetNumberField(TEXT("a"))) == P->ObservedSeat ||
            (!F->GetBoolField(TEXT("ghost")) &&
             int(F->GetNumberField(TEXT("b"))) == P->ObservedSeat)) {
          SelectedFight = I;
          break;
        }
      }
      HitBoxMap.Reset();
      Focusable.Reset();
      Box(390, 210, 1150, 530, Navy);
      Box(390, 210, 1150, 3, Gold);
      Text(LocalizedPrintf(P, TEXT("ROUND %d - ENCOUNTER RECAP"),
                           TEXT("RONDE %d - RINGKASAN PERTARUNGAN"),
                           int(Rec->GetNumberField(TEXT("round")))),
           425, 242, 1.3, Gold);
      auto SeatName = [&](int Seat) {
        return Seats.IsValidIndex(Seat)
                   ? Seats[Seat]->AsObject()->GetStringField(TEXT("name"))
                   : FString::Printf(TEXT("%d"), Seat + 1);
      };
      for (int I = 0; I < Fights.Num(); ++I) {
        const auto F = Fights[I]->AsObject();
        Button(TEXT("recapfight_") + FString::FromInt(I),
               FString::Printf(
                   TEXT("%d vs %d%s"), int(F->GetNumberField(TEXT("a"))) + 1,
                   int(F->GetNumberField(TEXT("b"))) + 1,
                   F->GetBoolField(TEXT("ghost")) ? TEXT(" [G]") : TEXT("")),
               425 + I * 270, 295, 250, 40);
      }
      if (Fights.IsValidIndex(SelectedFight)) {
        const auto F = Fights[SelectedFight]->AsObject();
        const bool Copy = F->GetBoolField(TEXT("ghost"));
        const int Winner = int(F->GetNumberField(TEXT("winner")));
        const int A = int(F->GetNumberField(TEXT("a"))),
                  B = int(F->GetNumberField(TEXT("b")));
        FString Outcome =
            Winner < 0 ? T(P, TEXT("Draw"), TEXT("Seri"))
                       : T(P, TEXT("Winner: "), TEXT("Pemenang: ")) +
                             (Winner == 1 && Copy
                                  ? T(P, TEXT("Ghost of "), TEXT("Salinan "))
                                  : FString()) +
                             SeatName(Winner == 0 ? A : B);
        if (F->GetBoolField(TEXT("timeout")))
          Outcome += T(P, TEXT(" | Timeout adjudication"),
                       TEXT(" | Penentuan saat batas waktu"));
        Text(Outcome, 425, 357, 1.05, Gold);
        const auto &Survivors = F->GetArrayField(TEXT("survivors"));
        const auto &Loss = F->GetArrayField(TEXT("healthLoss"));
        const auto &Absorbed = F->GetArrayField(TEXT("absorbed"));
        const auto &Healing = F->GetArrayField(TEXT("healing"));
        const auto &CaptainDamage = F->GetArrayField(TEXT("captainDamage"));
        for (int Side = 0; Side < 2; ++Side) {
          const float X = 425 + Side * 560;
          Text((Side == 1 && Copy ? T(P, TEXT("GHOST: "), TEXT("SALINAN: "))
                                  : FString()) +
                   SeatName(Side == 0 ? A : B),
               X, 397, 1, Muted);
          Text(LocalizedPrintf(P, TEXT("Survivors: %.0f"),
                               TEXT("Hero bertahan: %.0f"),
                               Survivors[Side]->AsNumber()),
               X, 434, .94);
          Text(LocalizedPrintf(P, TEXT("Hero HP lost: %.2f"),
                               TEXT("HP hero hilang: %.2f"),
                               Loss[Side]->AsNumber() / 100.0),
               X, 464, .92);
          Text(LocalizedPrintf(P, TEXT("Shield absorbed: %.2f"),
                               TEXT("Diserap perisai: %.2f"),
                               Absorbed[Side]->AsNumber() / 100.0),
               X, 494, .92);
          Text(LocalizedPrintf(P, TEXT("Effective healing: %.2f"),
                               TEXT("Pemulihan efektif: %.2f"),
                               Healing[Side]->AsNumber() / 100.0),
               X, 524, .92);
          FString Formula;
          if (Copy && Side == 1)
            Formula =
                T(P, TEXT("Donor unaffected by this copied fight."),
                  TEXT("Pemilik salinan tidak terpengaruh pertarungan ini."));
          else if (Winner < 0)
            Formula = LocalizedPrintf(
                P, TEXT("Captain loss: %.0f (draw rule: %d)"),
                TEXT("HP kapten hilang: %.0f (aturan seri: %d)"),
                CaptainDamage[Side]->AsNumber(), Defs.rules.drawDamage);
          else if (Winner == Side)
            Formula = T(P, TEXT("Captain loss: 0 (encounter won)"),
                        TEXT("HP kapten hilang: 0 (menang)"));
          else
            Formula = LocalizedPrintf(
                P, TEXT("Captain loss: %.0f = %d stage + %.0f enemy survivors"),
                TEXT("HP kapten hilang: %.0f = %d tahap + %.0f musuh bertahan"),
                CaptainDamage[Side]->AsNumber(),
                int(F->GetNumberField(TEXT("stageBase"))),
                Survivors[1 - Side]->AsNumber());
          Wrap(Formula, X, 575, 510, .89, Gold);
        }
      }
      Text(T(P,
             TEXT("Totals are measured from combat events; excess healing is "
                  "excluded."),
             TEXT("Total berasal dari peristiwa pertempuran; pemulihan "
                  "berlebih tidak dihitung.")),
           425, 640, .85, Muted);
      Button(TEXT("recap"),
             Phase == 2 ? T(P, TEXT("Next preparation begins shortly"),
                            TEXT("Persiapan berikutnya segera dimulai"))
                        : T(P, TEXT("Close recap"), TEXT("Tutup ringkasan")),
             425, 682, 530, 40, Phase != 2);
      if (!Alive)
        Button(TEXT("menu"),
               T(P, TEXT("Return to title"), TEXT("Kembali ke judul")), 985,
               682, 500, 40);
    }
    if (Phase == 3) {
      HitBoxMap.Reset();
      Focusable.Reset();
      Box(410, 200, 1090, 530, Navy);
      Text(T(P, TEXT("THE TRIALS CONCLUDE"), TEXT("TURNAMEN SELESAI")), 475,
           235, 2, Gold);
      Text(
          State->GetBoolField(TEXT("capped"))
              ? T(P,
                  TEXT("Round cap adjudication - shared placements are "
                       "possible"),
                  TEXT(
                      "Batas ronde tercapai - peringkat bersama dapat terjadi"))
              : T(P, TEXT("Final tournament standings"),
                  TEXT("Peringkat akhir turnamen")),
          475, 296, 1, Muted);
      for (int I = 0; I < Seats.Num(); ++I) {
        auto S = Seats[I]->AsObject();
        Text(LocalizedPrintf(P, TEXT("#%d  %s | %d wins"),
                             TEXT("#%d  %s | %d menang"),
                             int(S->GetNumberField(TEXT("place"))),
                             *S->GetStringField(TEXT("name")),
                             int(S->GetNumberField(TEXT("wins")))),
             490 + (I / 4) * 485, 355 + (I % 4) * 54, 1);
      }
      Button(TEXT("restart"), Label(TEXT("match.restart")), 475, 618, 430, 64,
             P->AssignedSeat <= 0);
      Button(TEXT("menu"),
             T(P, TEXT("Return to title"), TEXT("Kembali ke judul")), 940, 618,
             475, 64);
    }
  }
  if (!P->Presenter->AssetStatus.IsEmpty()) {
    Box(25, 1061, 1870, 19, Navy);
    Text(P->Presenter->AssetStatus, 35, 1062, .55, Gold);
  }
  if (State->HasField(TEXT("practice")) &&
      State->GetBoolField(TEXT("practice")) && Phase == 0 &&
      Private.IsValid() && Private->HasField(TEXT("units"))) {
    bool Ada = false, Placed = false, Partner = false, Merged = false;
    for (const auto &V : Private->GetArrayField(TEXT("units"))) {
      auto U = V->AsObject();
      int D = int(U->GetNumberField(TEXT("def")));
      if (D < 0 || D >= int(Defs.units.size()))
        continue;
      if (Defs.units[D].id == "wc_u_human_guardian") {
        Ada = true;
        Placed |= U->GetBoolField(TEXT("board"));
        Merged |= U->GetNumberField(TEXT("star")) >= 2;
      }
      if (Defs.units[D].id == "wc_u_human_priest")
        Partner |= U->GetBoolField(TEXT("board"));
    }
    FString Step =
        !Ada ? T(P, TEXT("Recruit Ada Brightshield from the shop."),
                 TEXT("Rekrut Ada Brightshield dari toko."))
        : !Placed
            ? T(P, TEXT("Select Ada on the bench, then a cell on your half."),
                TEXT("Pilih Ada di bangku, lalu sel di bagian papanmu."))
        : !Partner ? T(P,
                       TEXT("Recruit and deploy Mira beside Ada to activate "
                            "Human synergy."),
                       TEXT("Rekrut dan tempatkan Mira di dekat Ada untuk "
                            "sinergi Manusia."))
        : !Merged
            ? T(P,
                TEXT("Buy the two remaining Ada offers. Three copies merge "
                     "automatically."),
                TEXT("Beli dua Ada lainnya. Tiga salinan bergabung otomatis."))
            : T(P,
                TEXT("Your two-star Ada is ready. Inspect her shield, then "
                     "Ready to fight."),
                TEXT("Ada bintang dua siap. Periksa perisainya, lalu Siap "
                     "untuk bertarung."));
    Box(430, 683, 1100, 80, Navy);
    Text(T(P, TEXT("GUIDED PRACTICE - fixed shop; untimed first preparation"),
           TEXT("LATIHAN TERPANDU - toko tetap; persiapan awal tanpa batas "
                "waktu")),
         450, 694, 1.25, Gold);
    Wrap(Step, 450, 727, 1060, 1.25, FLinearColor::White);
  }
  if (Phase == 0 && !P->bRecap && !P->bOptions) {
    if (RecentTransaction) {
      Box(475, 174, 1070, 72, Navy);
      Wrap(ConfirmedFeedback.Transaction, 495, 185, 1030, 1.25, Gold);
    }
    if (!ConfirmedFeedback.NewTraits.IsEmpty() &&
        FeedbackNow - ConfirmedFeedback.TraitTime < 5) {
      Box(475, RecentTransaction ? 250 : 174, 1070, 53, Navy);
      Wrap(ConfirmedFeedback.NewTraits, 495, RecentTransaction ? 261 : 185,
           1030, 1.25, Gold);
    }
  }
  if (!P->Message.IsEmpty() && P->Message != TEXT("Accepted") &&
      FeedbackNow - P->MessageTime < 5) {
    Box(475, 110, 1070, 58, Navy);
    Wrap(ReplyText(P, P->Message), 495, 120, 1030, 1.25, Gold);
  }
  if (P->bTutorial && Phase < 0) {
    Box(955, 220, 865, 465, Navy);
    Text(T(P, TEXT("YOUR FIRST COMPANY"), TEXT("TIM PERTAMAMU")), 990, 252, 1.6,
         Gold);
    Wrap(
        T(P,
          TEXT("1. Recruit heroes from five shop offers.\n2. Select a bench "
               "hero, then click your half of the board.\n3. Deploy two "
               "different heroes with a shared race or class.\n4. Collect "
               "three identical copies for an automatic star upgrade.\n5. "
               "Ready your formation. Heroes fight automatically in all "
               "encounters.\n6. Scout rivals, earn gold, level up, and adapt."),
          TEXT("1. Rekrut hero dari lima tawaran toko.\n2. Pilih hero di "
               "bangku, lalu klik bagian papanmu.\n3. Tempatkan dua hero "
               "berbeda dengan ras atau kelas yang sama.\n4. Kumpulkan tiga "
               "salinan yang sama untuk naik bintang otomatis.\n5. Siapkan "
               "formasi. Hero bertarung otomatis di setiap pertarungan.\n6. "
               "Amati lawan, kumpulkan emas, naik level, dan sesuaikan tim.")),
        990, 322, 785, 1.14, FLinearColor::White);
    Button(
        TEXT("tutorial_close"),
        T(P, TEXT("Got it - review my lobby"), TEXT("Mengerti - lihat lobiku")),
        990, 593, 785, 55);
  }
  if (P->bOptions) {
    HitBoxMap.Reset();
    Focusable.Reset();
    Box(540, 170, 840, 710, Navy);
    Text(Label(TEXT("menu.options")), 585, 215, 1.8, Gold);
    Button(TEXT("language"),
           T(P, TEXT("Language: "), TEXT("Bahasa: ")) + P->Language +
               TEXT("  (EN / ID)"),
           585, 290, 750, 62);
    const TCHAR *Ids[] = {TEXT("master"), TEXT("music"), TEXT("effects")};
    const TCHAR *Keys[] = {TEXT("audio.master"), TEXT("audio.music"),
                           TEXT("audio.sfx")};
    const float Volumes[] = {P->MasterVolume, P->MusicVolume, P->EffectsVolume};
    for (int I = 0; I < 3; ++I) {
      const float Y = 376 + I * 72;
      Box(585, Y, 750, 58, Panel);
      Text(FString::Printf(TEXT("%s %d%%"), *Label(Keys[I]),
                           FMath::RoundToInt(Volumes[I] * 100)),
           599, Y + 16, 1.1);
      Box(865, Y + 26, 440, 7, Muted);
      Box(865, Y + 26, 440 * Volumes[I], 7, Teal);
      Box(860 + 440 * Volumes[I], Y + 17, 10, 25, Gold);
      Focusable.AddUnique(Ids[I]);
      AddHitBox(FVector2D(OffsetX + 585 * Scale, OffsetY + Y * Scale),
                FVector2D(750 * Scale, 58 * Scale), FName(Ids[I]), true, 100);
      if (Focused == Ids[I]) {
        Box(587, Y + 2, 746, 3, Gold);
        Box(587, Y + 53, 746, 3, Gold);
      }
    }
    Button(TEXT("motion"),
           Label(TEXT("access.motion")) + TEXT(": ") +
               (P->bReducedMotion ? T(P, TEXT("ON"), TEXT("AKTIF"))
                                  : T(P, TEXT("OFF"), TEXT("NONAKTIF"))),
           585, 592, 750, 58);
    Button(TEXT("window"),
           T(P, TEXT("Toggle window / fullscreen"),
             TEXT("Ganti jendela / layar penuh")),
           585, 664, 750, 58);
    Button(TEXT("options"), T(P, TEXT("Resume"), TEXT("Lanjutkan")), 585, 755,
           360, 62);
    Button(TEXT("quit"), Label(TEXT("menu.quit")), 975, 755, 360, 62);
  }
}
void AWCMatchHUD::NotifyHitBoxClick(FName BoxName) {
  Pressed = BoxName.ToString();
  if (PlayerOwner)
    PlayerOwner->GetMousePosition(PressLocation.X, PressLocation.Y);
  Action(Pressed);
}
void AWCMatchHUD::NotifyHitBoxRelease(FName) {
  auto *P = Cast<AWCMatchController>(PlayerOwner);
  if (P && IsSlider(Pressed)) {
    P->SaveOptions();
    Pressed.Reset();
    return;
  }
  if (!CanEdit(P) || P->bOptions || P->bRecap || !P->SelectedUnit ||
      (!Pressed.StartsWith(TEXT("unit_")) &&
       !Pressed.StartsWith(TEXT("bench_"))))
    return;
  FVector2D Now;
  P->GetMousePosition(Now.X, Now.Y);
  if ((Now - PressLocation).Size() < 12 * Scale)
    return;
  float X = (Now.X - OffsetX) / Scale, Y = (Now.Y - OffsetY) / Scale;
  if (Y >= 838 && Y <= 886 && X >= 355 && X < 1523) {
    P->Intent(wc::CommandType::Move, P->SelectedUnit,
              FMath::Clamp(int((X - 355) / 146), 0, 7), false);
    P->SelectedUnit = 0;
    return;
  }
  const auto &Rules = P->Presenter->Definitions.rules;
  FVector Origin, Direction;
  if (P->DeprojectMousePositionToWorld(Origin, Direction) &&
      FMath::Abs(Direction.Z) > .001) {
    FVector Point = Origin + Direction * ((0 - Origin.Z) / Direction.Z);
    int C = FMath::FloorToInt(Rules.columns / 2.0 - Point.Y / Rules.tileSizeCm),
        R = FMath::FloorToInt(Rules.rows / 2.0 - Point.X / Rules.tileSizeCm);
    if (C >= 0 && C < Rules.columns && R >= 0 && R < Rules.deploymentRows) {
      P->Intent(wc::CommandType::Move, P->SelectedUnit, -1, true, C, R);
      P->SelectedUnit = 0;
    }
  }
}
void AWCMatchHUD::Action(const FString &Id) {
  auto *P = Cast<AWCMatchController>(PlayerOwner);
  if (!P)
    return;
  auto *Session = Cast<UWCNetworkSession>(P->GetGameInstance());
  const bool Aborted =
      (Session && Session->bMatchAborted) ||
      (P->Public.IsValid() && int(P->Public->GetNumberField(TEXT("phase"))) ==
                                  int(wc::Phase::Aborted));
  if (Aborted && Id != TEXT("menu") && Id != TEXT("quit"))
    return;
  if (P->bOptions && Id != TEXT("options") && Id != TEXT("language") &&
      Id != TEXT("master") && Id != TEXT("music") && Id != TEXT("effects") &&
      Id != TEXT("motion") && Id != TEXT("window") && Id != TEXT("quit"))
    return;
  if (P->bRecap && Id != TEXT("recap") && !Id.StartsWith(TEXT("recapfight_")) &&
      Id != TEXT("menu") && Id != TEXT("options") && Id != TEXT("quit"))
    return;
  if (Id == TEXT("options")) {
    P->bOptions = !P->bOptions;
    return;
  }
  if (Id == TEXT("tutorial") || Id == TEXT("tutorial_close")) {
    P->bTutorial = Id == TEXT("tutorial_close") ? false : !P->bTutorial;
    return;
  }
  if (Id == TEXT("quit")) {
    UKismetSystemLibrary::QuitGame(this, P, EQuitPreference::Quit, false);
    return;
  }
  if (Id == TEXT("recap")) {
    P->bRecap = !P->bRecap;
    P->SelectedUnit = 0;
    return;
  }
  if (Id.StartsWith(TEXT("recapfight_"))) {
    if (P->Public.IsValid() && P->Public->HasField(TEXT("recap"))) {
      const auto &Fights = P->Public->GetObjectField(TEXT("recap"))
                               ->GetArrayField(TEXT("encounters"));
      const int Index = FCString::Atoi(*Id.Mid(10));
      if (Fights.IsValidIndex(Index)) {
        P->ObservedSeat =
            int(Fights[Index]->AsObject()->GetNumberField(TEXT("a")));
        P->SelectedUnit = 0;
        P->InspectedDefinition = -1;
        P->InspectedUnitId = 0;
      }
    }
    return;
  }
  const bool NewSession = Id == TEXT("host") || Id == TEXT("join") ||
                          Id == TEXT("menu") || Id == TEXT("start") ||
                          Id == TEXT("restart") || Id == TEXT("newsolo") ||
                          Id == TEXT("practice");
  if (NewSession) {
    if (Session)
      Session->ClearNetworkFailure();
    P->SelectedUnit = 0;
    P->InspectedUnitId = 0;
    P->InspectedDefinition = -1;
    P->bInspectedCombat = false;
    P->bRecap = false;
    P->bTutorial = false;
  }
  if (Id == TEXT("host")) {
    UGameplayStatics::OpenLevel(this,
                                TEXT("/Game/WonderChess/Maps/L_WC_Courtyard"),
                                true, TEXT("listen?WCHumans=2"));
    return;
  }
  if (Id == TEXT("join")) {
    P->ClientTravel(P->JoinAddress + TEXT(":7777"), TRAVEL_Absolute);
    return;
  }
  if (Id == TEXT("menu")) {
    UGameplayStatics::OpenLevel(this, TEXT("/Game/WonderChess/Maps/L_WC_Menu"));
    return;
  }
  if (Id == TEXT("newsolo")) {
    UGameplayStatics::OpenLevel(this,
                                TEXT("/Game/WonderChess/Maps/L_WC_Courtyard"),
                                true, TEXT("WCNewSolo=1"));
    return;
  }
  if (Id == TEXT("start") || Id == TEXT("restart")) {
    P->ServerStart(
        P->Public.IsValid() && P->Public->GetBoolField(TEXT("network")) ? 2 : 1,
        int32(FDateTime::UtcNow().GetTicks() & 0x7fffffff));
    return;
  }
  if (Id == TEXT("practice")) {
    P->bTutorial = true;
    P->ServerPractice();
    return;
  }
  if (Id == TEXT("home") || Id.StartsWith(TEXT("scout_"))) {
    P->ObservedSeat = Id == TEXT("home") ? FMath::Max(0, P->AssignedSeat)
                                         : FCString::Atoi(*Id.Mid(6));
    P->InspectedUnitId = 0;
    P->InspectedDefinition = -1;
    P->bInspectedCombat = false;
    return;
  }
  if (Id == TEXT("language")) {
    P->Language = P->Language == TEXT("en") ? TEXT("id") : TEXT("en");
    P->SaveOptions();
    return;
  }
  if (IsSlider(Id)) {
    float MX, MY;
    if (P->GetMousePosition(MX, MY))
      SetSlider(P, Id, ((MX - OffsetX) / Scale - 865.f) / 440.f);
    return;
  }
  if (Id == TEXT("motion")) {
    P->bReducedMotion = !P->bReducedMotion;
    P->SaveOptions();
    return;
  }
  if (Id == TEXT("window")) {
    auto *Settings = GEngine->GetGameUserSettings();
    Settings->SetFullscreenMode(Settings->GetFullscreenMode() ==
                                        EWindowMode::Windowed
                                    ? EWindowMode::WindowedFullscreen
                                    : EWindowMode::Windowed);
    Settings->ApplySettings(false);
    return;
  }
  if (Id.StartsWith(TEXT("inspect_"))) {
    P->SelectedUnit = 0;
    const int64 Selected = FCString::Atoi64(*Id.Mid(8));
    if (P->Presenter)
      for (const auto &V : P->Presenter->VisibleUnits) {
        auto U = V->AsObject();
        if (int64(U->GetNumberField(TEXT("id"))) == Selected) {
          P->InspectedUnitId = Selected;
          P->InspectedDefinition = int(U->GetNumberField(TEXT("def")));
          const int Phase = int(P->Public->GetNumberField(TEXT("phase")));
          P->bInspectedCombat = Phase == int(wc::Phase::Combat) ||
                                Phase == int(wc::Phase::Settlement);
          break;
        }
      }
    return;
  }
  if (!P->Private.IsValid() || !P->Private->HasField(TEXT("shop")))
    return;
  const bool Editable = CanEdit(P);
  if (Id.StartsWith(TEXT("offer_")) || Id.StartsWith(TEXT("buy_"))) {
    const bool Buy = Id.StartsWith(TEXT("buy_"));
    int Slot = FCString::Atoi(*Id.Mid(Buy ? 4 : 6));
    const auto &Shop = P->Private->GetArrayField(TEXT("shop"));
    if (Shop.IsValidIndex(Slot)) {
      P->InspectedDefinition = int(Shop[Slot]->AsNumber());
      P->InspectedUnitId = 0;
      P->bInspectedCombat = false;
      P->SelectedUnit = 0;
    }
    if (Buy && Editable)
      P->Intent(wc::CommandType::Buy, 0, Slot);
    return;
  }
  if (Id.StartsWith(TEXT("bench_")) && !Editable) {
    const int Slot = FCString::Atoi(*Id.Mid(6));
    P->SelectedUnit = 0;
    for (const auto &V : P->Private->GetArrayField(TEXT("units"))) {
      auto U = V->AsObject();
      if (!U->GetBoolField(TEXT("board")) &&
          int(U->GetNumberField(TEXT("bench"))) == Slot) {
        P->InspectedUnitId = int64(U->GetNumberField(TEXT("id")));
        P->InspectedDefinition = int(U->GetNumberField(TEXT("def")));
        P->bInspectedCombat = false;
        break;
      }
    }
    return;
  }
  if (Id == TEXT("ready")) {
    if (P->Public.IsValid() &&
        int(P->Public->GetNumberField(TEXT("phase"))) == 0 &&
        !P->Private->GetBoolField(TEXT("ready")))
      P->Ready();
    return;
  }
  if (!Editable)
    return;
  if (Id == TEXT("reroll")) {
    P->Intent(wc::CommandType::Reroll);
    return;
  }
  if (Id == TEXT("xp")) {
    P->Intent(wc::CommandType::BuyXp);
    return;
  }
  if (Id == TEXT("lock")) {
    P->Intent(wc::CommandType::ToggleLock);
    return;
  }
  if (Id == TEXT("sell")) {
    P->Intent(wc::CommandType::Sell, P->SelectedUnit);
    P->SelectedUnit = 0;
    return;
  }
  if (Id.StartsWith(TEXT("cell_"))) {
    TArray<FString> Fields;
    Id.ParseIntoArray(Fields, TEXT("_"));
    if (Fields.Num() == 3 && P->SelectedUnit) {
      P->Intent(wc::CommandType::Move, P->SelectedUnit, -1, true,
                FCString::Atoi(*Fields[1]), FCString::Atoi(*Fields[2]));
      P->SelectedUnit = 0;
    }
    return;
  }
  int64 Select = 0;
  if (Id.StartsWith(TEXT("unit_")))
    Select = FCString::Atoi64(*Id.Mid(5));
  if (Id.StartsWith(TEXT("bench_"))) {
    int B = FCString::Atoi(*Id.Mid(6));
    if (P->SelectedUnit) {
      P->Intent(wc::CommandType::Move, P->SelectedUnit, B, false);
      P->SelectedUnit = 0;
      return;
    }
    for (const auto &V : P->Private->GetArrayField(TEXT("units"))) {
      auto U = V->AsObject();
      if (!U->GetBoolField(TEXT("board")) &&
          int(U->GetNumberField(TEXT("bench"))) == B)
        Select = int64(U->GetNumberField(TEXT("id")));
    }
  }
  if (Select)
    for (const auto &V : P->Private->GetArrayField(TEXT("units"))) {
      auto U = V->AsObject();
      if (int64(U->GetNumberField(TEXT("id"))) == Select) {
        if (P->SelectedUnit && P->SelectedUnit != Select) {
          P->Intent(wc::CommandType::Move, P->SelectedUnit,
                    int(U->GetNumberField(TEXT("bench"))),
                    U->GetBoolField(TEXT("board")),
                    int(U->GetNumberField(TEXT("col"))),
                    int(U->GetNumberField(TEXT("row"))));
          P->SelectedUnit = 0;
        } else
          P->SelectedUnit = Select;
        P->InspectedDefinition = int(U->GetNumberField(TEXT("def")));
        P->InspectedUnitId = Select;
        P->bInspectedCombat = false;
      }
    }
}
