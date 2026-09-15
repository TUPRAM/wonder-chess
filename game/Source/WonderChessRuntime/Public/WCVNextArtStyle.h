#pragma once

#include "CoreMinimal.h"

class SWidget;
struct FSlateBrush;
struct FButtonStyle;
struct FSlateFontInfo;

struct FWCArtCardData
{
    FString UnitId, Name, Detail, Footer, Tooltip, Availability;
    int Cost = 0;
};

// Presentation study only. All card content and actions come from the live caller.
struct WONDERCHESSRUNTIME_API FWCArtSlice
{
    static bool IsEnabled();
    static bool IsStorybook();
    static bool ResourcesReady();
    static bool StorybookResourcesReady();
    static const FSlateBrush* BellbackPortrait();
    static const FSlateBrush* HeavyBloomIcon();
    static const FSlateBrush* Portrait(const FString& UnitId);
    static const FSlateBrush* AbilityIcon(const FString& UnitId);
    static const FSlateBrush* RelicIcon(const FString& RelicId);
    static const FSlateBrush* PanelBrush(bool Parchment = false);
    static const FButtonStyle* ButtonStyle();
    static FSlateFontInfo HeadingFont(int Size, bool Bold = true);
    static FVector2D ViewportSlateSize();
    static TSharedRef<SWidget> MakePanel(TSharedRef<SWidget> Content, bool Parchment = false, float Padding = 8);
    static TSharedRef<SWidget> MakeTraitGlyph(const FString& Id, float Size, TFunction<bool()> Active);
    static TSharedRef<SWidget> MakeButton(TFunction<FString()> Label, TFunction<void()> Action,
        TFunction<bool()> Enabled, int FontSize = 11);
    static FLinearColor TierColor(int Cost);
    static TSharedRef<SWidget> MakeShopCard(TFunction<FWCArtCardData()> Data,
        TFunction<void()> Action, TFunction<bool()> Enabled);
    static TSharedRef<SWidget> MakeStudyPanel(TFunction<FString()> SelectedUnitId,
        TFunction<FString()> SelectedName);
};
