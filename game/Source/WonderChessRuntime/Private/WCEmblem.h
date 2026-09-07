#pragma once
#include "Rendering/DrawElementTypes.h"
#include "Widgets/SLeafWidget.h"

// Original Wonder Chess line emblems. Normalized paths render directly in Slate.
class SWCEmblem final : public SLeafWidget {
public:
  SLATE_BEGIN_ARGS(SWCEmblem) : _Size(28), _Color(FLinearColor(.92f, .72f, .37f)) {}
    SLATE_ARGUMENT(FString, Id)
    SLATE_ARGUMENT(float, Size)
    SLATE_ARGUMENT(FLinearColor, Color)
  SLATE_END_ARGS()
  void Construct(const FArguments& Args) { Id = Args._Id; Size = Args._Size; Color = Args._Color; }
  virtual FVector2D ComputeDesiredSize(float) const override { return FVector2D(Size, Size); }
  virtual int32 OnPaint(const FPaintArgs&, const FGeometry& Geometry, const FSlateRect&,
                        FSlateWindowElementList& Out, int32 Layer, const FWidgetStyle& Style, bool Enabled) const override {
    auto Line = [&](std::initializer_list<FVector2D> Points, FVector2D Offset = FVector2D::ZeroVector, float Scale = 1.f) {
      TArray<FVector2D> Path;
      for (const auto& P : Points) Path.Add((P * Scale + Offset) * Geometry.GetLocalSize());
      FSlateDrawElement::MakeLines(Out, Layer, Geometry.ToPaintGeometry(), Path, ESlateDrawEffect::None,
                                  Color * Style.GetColorAndOpacityTint() * (Enabled ? 1.f : .45f), true,
                                  FMath::Max(1.4f, float(Geometry.GetLocalSize().X) / 16));
    };
    auto Ring = [&](FVector2D Center, float Radius) {
      TArray<FVector2D> Path;
      for (int I = 0; I <= 20; ++I) {
        const float Angle = I * 2 * PI / 20;
        Path.Add((Center + FVector2D(FMath::Cos(Angle), FMath::Sin(Angle)) * Radius) * Geometry.GetLocalSize());
      }
      FSlateDrawElement::MakeLines(Out, Layer, Geometry.ToPaintGeometry(), Path, ESlateDrawEffect::None,
                                  Color * Style.GetColorAndOpacityTint(), true, FMath::Max(1.4f, Size / 16));
    };
    FString Motif = Id;
    if (Id.StartsWith(TEXT("wc_u_"))) {
      int Split = INDEX_NONE; Id.FindLastChar(TEXT('_'), Split);
      Motif = Id.Mid(Split + 1);
    }
    if (Motif == TEXT("human")) {
      Ring({.5,.5},.2); Line({{.5,.06},{.5,.2}}); Line({{.5,.8},{.5,.94}});
      Line({{.06,.5},{.2,.5}}); Line({{.8,.5},{.94,.5}});
      Line({{.18,.18},{.28,.28}}); Line({{.72,.72},{.82,.82}});
    } else if (Motif == TEXT("elf")) {
      Line({{.18,.85},{.5,.5},{.76,.12},{.8,.46},{.5,.74},{.18,.85}}); Line({{.33,.69},{.48,.3}});
    } else if (Motif == TEXT("dwarf")) {
      Line({{.12,.85},{.12,.36},{.32,.14},{.68,.14},{.88,.36},{.88,.85}});
      Line({{.34,.85},{.34,.43},{.5,.29},{.66,.43},{.66,.85}}); Line({{.05,.87},{.95,.87}});
    } else if (Motif == TEXT("orc")) {
      Line({{.18,.12},{.14,.58},{.34,.87},{.44,.7},{.34,.39}});
      Line({{.82,.12},{.86,.58},{.66,.87},{.56,.7},{.66,.39}});
    } else if (Motif == TEXT("halfling")) {
      Line({{.5,.91},{.5,.15}}); Line({{.5,.66},{.16,.54},{.18,.32},{.5,.5},{.81,.31},{.83,.54},{.5,.66}});
      Line({{.5,.37},{.34,.17},{.5,.05},{.66,.17},{.5,.37}});
    } else if (Motif == TEXT("dragonkin")) {
      Line({{.08,.12},{.24,.52},{.5,.87},{.76,.52},{.92,.12},{.62,.33},{.5,.12},{.38,.33},{.08,.12}});
      Line({{.37,.49},{.5,.65},{.63,.49}});
    } else if (Motif == TEXT("guardian")) {
      Line({{.12,.22},{.5,.07},{.88,.22},{.78,.65},{.5,.93},{.22,.65},{.12,.22}});
      Line({{.5,.18},{.5,.73}});
    } else if (Motif == TEXT("warrior")) {
      Line({{.2,.82},{.68,.16},{.87,.08},{.85,.28},{.38,.91},{.2,.82}}); Line({{.14,.65},{.54,.92}});
    } else if (Motif == TEXT("ranger")) {
      Line({{.28,.08},{.56,.3},{.65,.5},{.56,.7},{.28,.92},{.28,.08}});
      Line({{.1,.5},{.94,.5},{.77,.33}}); Line({{.94,.5},{.77,.67}});
    } else if (Motif == TEXT("mage")) {
      Line({{.5,.04},{.63,.36},{.94,.5},{.63,.64},{.5,.96},{.37,.64},{.06,.5},{.37,.36},{.5,.04}});
      Ring({.5,.5},.14);
    } else if (Motif == TEXT("priest")) {
      Line({{.28,.25},{.28,.71},{.5,.88},{.72,.71},{.72,.25},{.28,.25}});
      Line({{.38,.24},{.38,.1},{.62,.1},{.62,.24}}); Line({{.5,.38},{.5,.67},{.4,.55},{.6,.55}});
    } else if (Motif == TEXT("rogue")) {
      Line({{.14,.88},{.47,.45},{.59,.06},{.28,.34},{.14,.88}});
      Line({{.5,.87},{.77,.51},{.88,.2},{.6,.48},{.5,.87}});
    }
    if (Id.StartsWith(TEXT("wc_u_"))) {
      // Each authored hero combines its action symbol with a distinct identity seal.
      const FVector2D O(.59,.58); const float S = .4f;
      Line({{0,0},{1,0},{1,1},{0,1},{0,0}}, O, S);
      if (Id.Contains(TEXT("human"))) {
        Ring({.79,.78},.10);
        if (Motif == TEXT("guardian")) Line({{.79,.62},{.79,.68}});
        else if (Motif == TEXT("priest")) Line({{.68,.9},{.9,.9}});
        else if (Motif == TEXT("mage")) Line({{.63,.64},{.72,.71}});
        else Line({{.79,.67},{.79,.87}});
      } else if (Id.Contains(TEXT("elf")))
        Line({{.69,.9},{.71,.7},{.89,.64},{.88,.83},{.69,.9},{.83,.75}});
      else if (Id.Contains(TEXT("dwarf")))
        Line({{.68,.88},{.68,.73},{.79,.65},{.9,.73},{.9,.88},{.68,.88}});
      else if (Id.Contains(TEXT("orc")))
        Line({{.68,.66},{.71,.88},{.79,.81},{.86,.88},{.9,.66}});
      else if (Id.Contains(TEXT("halfling")))
        Line({{.67,.73},{.72,.67},{.79,.73},{.86,.67},{.91,.73},{.79,.9},{.67,.73}});
      else if (Id.Contains(TEXT("dragonkin")))
        Line({{.67,.73},{.79,.64},{.91,.73},{.91,.84},{.79,.92},{.67,.84},{.67,.73}});
    }
    return Layer;
  }
private:
  FString Id;
  float Size = 28;
  FLinearColor Color;
};
