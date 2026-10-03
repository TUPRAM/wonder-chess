#include "WCVNextArtStyle.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Engine/Texture2D.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/UserInterfaceSettings.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Fonts/CompositeFont.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "UObject/GCObject.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SLeafWidget.h"
#include "Widgets/Text/STextBlock.h"

namespace
{
const FLinearColor Ink(.009f,.024f,.028f), Paper(.89f,.86f,.75f), Bronze(.390f,.262f,.087f);
FText Text(const FString& Value) { return FText::FromString(Value); }

struct FArtResources : FGCObject
{
    TObjectPtr<UTexture2D> Portrait = nullptr;
    TObjectPtr<UTexture2D> Relic = nullptr;
    FSlateBrush PortraitBrush, RelicBrush;
    TMap<FString, TObjectPtr<UTexture2D>> Illustrations;
    TMap<FString, FSlateBrush> IllustrationBrushes;
    FSlateRoundedBoxBrush Panel{Ink, 9.f};
    // Slate panel with a thin brass edge: the castle-courtyard theme.
    FSlateRoundedBoxBrush StoryPanel{FLinearColor(.035f,.042f,.058f,.93f), 8.f,
        FLinearColor(.66f,.50f,.19f,.85f), 1.2f};
    FSlateRoundedBoxBrush Parchment{FLinearColor(.84f,.78f,.65f,.97f), 10.f,
        FLinearColor(.52f,.41f,.24f,.70f), 1.f};
    FSlateRoundedBoxBrush Focus{FLinearColor::Transparent, 9.f, Paper, 2.f};
    FButtonStyle Card;
    TSharedPtr<const FCompositeFont> HeadingFamily;
    bool FontsAvailable = false;

    FArtResources()
    {
        Card.SetNormal(FSlateRoundedBoxBrush(FLinearColor(.050f,.058f,.076f,.95f), 7.f,
                FLinearColor(.46f,.36f,.16f,.80f), 1.f))
            .SetHovered(FSlateRoundedBoxBrush(FLinearColor(.085f,.100f,.130f,.97f), 7.f, FLinearColor(.88f,.70f,.30f), 1.5f))
            .SetPressed(FSlateRoundedBoxBrush(FLinearColor(.030f,.035f,.046f,.98f), 7.f, FLinearColor(.88f,.70f,.30f), 1.5f))
            .SetDisabled(FSlateRoundedBoxBrush(FLinearColor(.040f,.045f,.055f,.85f), 7.f,
                FLinearColor(.22f,.22f,.22f,.70f), 1.f))
            .SetNormalPadding(FMargin(8,6)).SetPressedPadding(FMargin(9,7,7,5));
        if(FWCArtSlice::IsEnabled()){
            Portrait=LoadObject<UTexture2D>(nullptr,TEXT("/Game/WonderChess/VNext/ArtSliceR001/T_BellbackPortrait.T_BellbackPortrait"));
            Relic=LoadObject<UTexture2D>(nullptr,TEXT("/Game/WonderChess/VNext/ArtSliceR001/T_HeavyBloom.T_HeavyBloom"));
        }
        const auto Set=[](FSlateBrush& Brush,UTexture2D* Texture){
            Brush.DrawAs=ESlateBrushDrawType::Image;
            Brush.ImageSize=FVector2f(1024,1024);
            Brush.SetResourceObject(Texture);
        };
        Set(PortraitBrush,Portrait);Set(RelicBrush,Relic);
        if(FWCArtSlice::IsStorybook()){
            const FString FontDirectory=FPaths::ProjectContentDir()/TEXT("WonderChess/UIFonts");
            const FString RegularFont=FontDirectory/TEXT("Cinzel-Regular.ttf"),BoldFont=FontDirectory/TEXT("Cinzel-Bold.ttf");
            FontsAvailable=IFileManager::Get().FileExists(*RegularFont)&&IFileManager::Get().FileExists(*BoldFont);
            auto Font=MakeShared<FCompositeFont>(TEXT("Regular"),RegularFont,EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
            Font->DefaultTypeface.AppendFont(TEXT("Bold"),BoldFont,EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
            HeadingFamily=Font;
            UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_FONTS available=%d regular_bytes=%lld bold_bytes=%lld"),FontsAvailable,
                IFileManager::Get().FileSize(*RegularFont),IFileManager::Get().FileSize(*BoldFont));
            const auto Load=[&](const FString& Kind,const FString& Id){
                const FString Name=TEXT("T_")+Kind+TEXT("_")+Id;
                const FString Path=(Id==TEXT("silkmother")?TEXT("/Game/WonderChess/VNext/Characters/Silkmother_r003/UI/"):TEXT("/Game/WonderChess/VNext/ArtExpansionR001/"))+Name+TEXT(".")+Name;
                UTexture2D* Texture=LoadObject<UTexture2D>(nullptr,*Path);
                const FString Key=Kind+TEXT("_")+Id;
                Illustrations.Add(Key,Texture);
                FSlateBrush Brush;Set(Brush,Texture);IllustrationBrushes.Add(Key,Brush);
                UE_LOG(LogTemp,Display,TEXT("WC_STORYBOOK_UI asset=%s loaded=%d size=%dx%d"),*Key,Texture!=nullptr,
                    Texture?Texture->GetSizeX():0,Texture?Texture->GetSizeY():0);
            };
            for(const TCHAR* Id:{TEXT("bellback"),TEXT("cragstoat"),TEXT("grandmother_root"),TEXT("snapvine"),TEXT("prism_organ"),TEXT("reefglass"),TEXT("silkmother")}){
                if(FString(Id)!=TEXT("bellback"))Load(TEXT("Portrait"),Id);
                Load(TEXT("Ability"),Id);
            }
            for(const TCHAR* Id:{TEXT("quick_wick"),TEXT("long_lens"),TEXT("broad_canopy"),TEXT("close_focus"),TEXT("tight_choir"),TEXT("silk_trigger"),
                TEXT("patient_lantern"),TEXT("far_hourglass"),TEXT("wide_hourglass"),TEXT("narrow_metronome"),TEXT("urgent_shard")})Load(TEXT("Relic"),Id);
        }
        UE_LOG(LogTemp,Display,TEXT("WC_ART_SLICE_UI portrait=%d portrait_size=%dx%d heavy_bloom=%d heavy_bloom_size=%dx%d"),
            Portrait!=nullptr,Portrait?Portrait->GetSizeX():0,Portrait?Portrait->GetSizeY():0,
            Relic!=nullptr,Relic?Relic->GetSizeX():0,Relic?Relic->GetSizeY():0);
    }
    virtual void AddReferencedObjects(FReferenceCollector& Collector) override
    { Collector.AddReferencedObject(Portrait);Collector.AddReferencedObject(Relic);
        for(auto& Entry:Illustrations)Collector.AddReferencedObject(Entry.Value); }
    virtual FString GetReferencerName() const override { return TEXT("FWCArtSliceResources"); }
};
FArtResources& Resources() { static FArtResources Value;return Value; }

class SWCArtButton : public SButton
{
public:
    void Construct(const SButton::FArguments& Args) { SButton::Construct(Args); }
    virtual int32 OnPaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& Culling,
        FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& WidgetStyle,bool ParentEnabled) const override
    {
        const int32 Painted=SButton::OnPaint(Args,Geometry,Culling,Elements,Layer,WidgetStyle,ParentEnabled);
        if(HasKeyboardFocus()){
            const auto& FocusBrush=Resources().Focus;
            FSlateDrawElement::MakeBox(Elements,Painted+1,Geometry.ToPaintGeometry(),&FocusBrush,
                ESlateDrawEffect::None,FocusBrush.GetTint(WidgetStyle)*WidgetStyle.GetColorAndOpacityTint());
            return Painted+1;
        }
        return Painted;
    }
};

class SWCStoryPanel : public SBorder
{
public:
    SLATE_BEGIN_ARGS(SWCStoryPanel) {} SLATE_DEFAULT_SLOT(FArguments,Content)
        SLATE_ARGUMENT(bool,Parchment) SLATE_ARGUMENT(float,Padding) SLATE_END_ARGS()
    void Construct(const FArguments& Args)
    {
        SBorder::Construct(SBorder::FArguments().BorderImage(FWCArtSlice::PanelBrush(Args._Parchment))
            .Padding(Args._Padding)[Args._Content.Widget]);
    }
    virtual int32 OnPaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& Culling,
        FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& WidgetStyle,bool ParentEnabled) const override
    {
        // The panel silhouette and a fine border carry the visual hierarchy. Ornament at
        // every corner made small HUD regions compete with the board and creature art.
        return SBorder::OnPaint(Args,Geometry,Culling,Elements,Layer,WidgetStyle,ParentEnabled);
    }
};

// Only paints the passive card contents without the engine's grey wash. The owning button's
// enabled attribute and input handlers are unchanged; this widget has no interaction handlers.
class SWCReadableArt : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SWCReadableArt) {} SLATE_DEFAULT_SLOT(FArguments,Content) SLATE_END_ARGS()
    void Construct(const FArguments& Args) { ChildSlot[Args._Content.Widget]; }
    virtual int32 OnPaint(const FPaintArgs& Args,const FGeometry& Geometry,const FSlateRect& Culling,
        FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& WidgetStyle,bool ParentEnabled) const override
    { return SCompoundWidget::OnPaint(Args,Geometry,Culling,Elements,Layer,WidgetStyle,true); }
};

class SWCTraitGlyph : public SLeafWidget
{
public:
    SLATE_BEGIN_ARGS(SWCTraitGlyph) {} SLATE_ARGUMENT(FString,Id) SLATE_ARGUMENT(float,Size)
        SLATE_ARGUMENT(TFunction<bool()>,Active) SLATE_END_ARGS()
    void Construct(const FArguments& Args) { Id=Args._Id.ToLower();Size=Args._Size;Active=Args._Active; }
    virtual FVector2D ComputeDesiredSize(float) const override {return FVector2D(Size,Size);}
    virtual int32 OnPaint(const FPaintArgs&,const FGeometry& Geometry,const FSlateRect&,
        FSlateWindowElementList& Elements,int32 Layer,const FWidgetStyle& WidgetStyle,bool) const override
    {
        const FLinearColor Gold=(Active()?FLinearColor(.78f,.57f,.26f):FLinearColor(.36f,.31f,.20f))*WidgetStyle.GetColorAndOpacityTint();
        const FVector2f Scale=FVector2f(Geometry.GetLocalSize())/32.f;
        const auto Line=[&](TArray<FVector2f> Points,float Width=1.6f){for(auto& Point:Points)Point*=Scale;
            FSlateDrawElement::MakeLines(Elements,Layer,Geometry.ToPaintGeometry(),Points,ESlateDrawEffect::None,Gold,true,Width);};
        const auto Circle=[&](float X,float Y,float Radius,float Width=1.6f){TArray<FVector2f> Points;
            for(int Index=0;Index<=24;++Index){const float Angle=Index*2.f*PI/24.f;Points.Add({X+FMath::Cos(Angle)*Radius,Y+FMath::Sin(Angle)*Radius});}Line(Points,Width);};
        Circle(16,16,14.5f,1.f);
        if(Id==TEXT("beast")){
            Circle(9,11,2,3);Circle(15,8,2,3);Circle(22,10,2,3);Circle(25,16,1.5f,2.5f);
            Line({{10,22},{13,17},{17,16},{21,20},{20,24},{16,23},{12,25},{10,22}},3.f);
        }else if(Id==TEXT("guardian")){
            Line({{8,9},{16,6},{24,9},{23,19},{20,23},{16,27},{12,23},{9,19},{8,9}},2.8f);
            Line({{16,10},{16,21}},2.8f);Line({{12,14},{20,14}},2.8f);
        }else if(Id==TEXT("warrior")){
            Line({{9,26},{22,9},{24,7},{24,12},{11,28}},2.8f);Line({{7,8},{10,9},{23,25}},2.8f);
            Line({{7,22},{14,27}},2.5f);Line({{18,25},{25,20}},2.5f);
        }else if(Id==TEXT("plant")){
            Line({{16,26},{16,8}},2.4f);Line({{16,18},{8,15},{7,9},{13,11},{16,18}},2.4f);
            Line({{16,22},{22,20},{25,13},{19,15},{16,22}},2.4f);Line({{16,12},{13,8},{16,4},{19,8},{16,12}},2.f);
        }else if(Id==TEXT("healer")){
            for(int Index=0;Index<5;++Index){const float Angle=Index*2.f*PI/5.f-PI*.5f;Circle(16+FMath::Cos(Angle)*6,16+FMath::Sin(Angle)*6,3.3f,2.8f);}Circle(16,16,3,3.f);
        }else if(Id==TEXT("assassin")){
            Line({{10,27},{17,19},{15,16},{21,8},{24,5},{24,13},{20,20},{17,18},{11,27}},2.7f);
            Line({{10,18},{19,26}},2.4f);
        }else if(Id==TEXT("construct")){
            Circle(16,16,7,2.8f);Circle(16,16,2,2.4f);
            for(int Index=0;Index<8;++Index){const float A=Index*PI*.25f;Line({{16+FMath::Cos(A)*8,16+FMath::Sin(A)*8},{16+FMath::Cos(A)*12,16+FMath::Sin(A)*12}},2.5f);}
        }else if(Id==TEXT("mage")){
            Line({{16,4},{23,16},{16,28},{9,16},{16,4}},2.3f);Line({{9,16},{23,16}},1.7f);Line({{16,4},{16,28}},1.4f);
            Line({{5,11},{6,9},{8,8}},1.8f);Line({{24,24},{26,22},{27,20}},1.8f);
        }else if(Id==TEXT("tidekin")){
            for(float Y:{10.f,16.f,22.f})Line({{6,Y+2},{10,Y-1},{14,Y-2},{18,Y+1},{22,Y+2},{26,Y-1}},2.4f);
        }else if(Id==TEXT("controller")){
            TArray<FVector2f> Spiral;for(int Index=0;Index<=42;++Index){const float A=Index*.22f,R=1+Index*.20f;Spiral.Add({16+FMath::Cos(A)*R,16+FMath::Sin(A)*R});}Line(Spiral,2.2f);
            Circle(16,16,1,2.f);
        }
        return Layer;
    }
private:
    FString Id;float Size=28;TFunction<bool()> Active;
};
const FSlateBrush* Illustration(const FString& Kind,FString Id)
{
    Id.RemoveFromStart(TEXT("wc_vn_r_"));Id.RemoveFromStart(TEXT("wc_vn_"));Id.RemoveFromStart(TEXT("relic_"));
    // Placeholder art: the ported heroes borrow the retired creature illustrations until their own art exists.
    static const TMap<FString,FString> RetiredArt{{TEXT("shieldbearer"),TEXT("bellback")},{TEXT("boar_rusher"),TEXT("cragstoat")},
        {TEXT("grove_druid"),TEXT("grandmother_root")},{TEXT("hookjaw"),TEXT("snapvine")},{TEXT("prism_scholar"),TEXT("prism_organ")},
        {TEXT("tide_caller"),TEXT("reefglass")},{TEXT("soul_jailer"),TEXT("silkmother")}};
    if(const FString* Retired=RetiredArt.Find(Id))Id=*Retired;
    const FSlateBrush* Found=Resources().IllustrationBrushes.Find(Kind+TEXT("_")+Id);
    return Found&&Found->GetResourceObject()?Found:FCoreStyle::Get().GetBrush(TEXT("NoBrush"));
}
}

bool FWCArtSlice::IsEnabled() { return IsStorybook()||FParse::Param(FCommandLine::Get(),TEXT("WCArtSlice")); }
bool FWCArtSlice::IsStorybook() { return FParse::Param(FCommandLine::Get(),TEXT("WCStorybook")); }
bool FWCArtSlice::ResourcesReady() { return IsEnabled()&&Resources().Portrait&&Resources().Relic; }
bool FWCArtSlice::StorybookResourcesReady()
{
    if(!IsStorybook()||!ResourcesReady()||!Resources().FontsAvailable||Resources().Illustrations.Num()!=24)return false;
    for(const auto& Entry:Resources().Illustrations)if(!Entry.Value)return false;
    return true;
}
const FSlateBrush* FWCArtSlice::BellbackPortrait() { return &Resources().PortraitBrush; }
const FSlateBrush* FWCArtSlice::HeavyBloomIcon() { return &Resources().RelicBrush; }
TFunction<const FSlateBrush*(const FString&)> FWCArtSlice::LivePortrait;
const FSlateBrush* FWCArtSlice::Portrait(const FString& UnitId)
{ if(LivePortrait)if(const auto* Live=LivePortrait(UnitId))return Live;
  return UnitId==TEXT("wc_vn_shieldbearer")?BellbackPortrait():Illustration(TEXT("Portrait"),UnitId); }
const FSlateBrush* FWCArtSlice::AbilityIcon(const FString& UnitId) { return Illustration(TEXT("Ability"),UnitId); }
const FSlateBrush* FWCArtSlice::RelicIcon(const FString& RelicId)
{ return RelicId.EndsWith(TEXT("heavy_bloom"))?HeavyBloomIcon():Illustration(TEXT("Relic"),RelicId); }
const FSlateBrush* FWCArtSlice::PanelBrush(bool Parchment) { return Parchment?&Resources().Parchment:&Resources().StoryPanel; }
const FButtonStyle* FWCArtSlice::ButtonStyle() { return &Resources().Card; }
FSlateFontInfo FWCArtSlice::HeadingFont(int Size,bool Bold)
{
    if(IsStorybook()&&Resources().FontsAvailable)return FSlateFontInfo(Resources().HeadingFamily,float(Size),Bold?TEXT("Bold"):TEXT("Regular"));
    return FCoreStyle::GetDefaultFontStyle(Bold?TEXT("Bold"):TEXT("Regular"),Size);
}
FVector2D FWCArtSlice::ViewportSlateSize()
{
    FVector2D Size(1920,1080);
    if(GEngine&&GEngine->GameViewport)GEngine->GameViewport->GetViewportSize(Size);
    const float Scale=GetDefault<UUserInterfaceSettings>()->GetDPIScaleBasedOnSize(FIntPoint(FMath::RoundToInt(Size.X),FMath::RoundToInt(Size.Y)));
    return Size/FMath::Max(.1f,Scale);
}
TSharedRef<SWidget> FWCArtSlice::MakePanel(TSharedRef<SWidget> Content,bool Parchment,float Padding)
{ return SNew(SWCStoryPanel).Parchment(Parchment).Padding(Padding)[Content]; }
TSharedRef<SWidget> FWCArtSlice::MakeTraitGlyph(const FString& Id,float Size,TFunction<bool()> Active)
{ return SNew(SWCTraitGlyph).Id(Id).Size(Size).Active(Active); }
TSharedRef<SWidget> FWCArtSlice::MakeButton(TFunction<FString()> Label,TFunction<void()> Action,TFunction<bool()> Enabled,int FontSize)
{
    return SNew(SWCArtButton).ButtonStyle(ButtonStyle()).IsEnabled_Lambda([Enabled]{return Enabled();})
        .ToolTipText_Lambda([Label]{return Text(Label());}).OnClicked_Lambda([Action]{Action();return FReply::Handled();})
        [SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),FMath::Max(12,FontSize))).ColorAndOpacity(Paper)
            .Justification(ETextJustify::Center).AutoWrapText(true).Text_Lambda([Label]{return Text(Label());})];
}
FLinearColor FWCArtSlice::TierColor(int Cost)
{
    static const FLinearColor Colors[]={FLinearColor(.45f,.61f,.38f),FLinearColor(.22f,.64f,.59f),
        FLinearColor(.30f,.53f,.76f),FLinearColor(.64f,.46f,.76f),FLinearColor(.86f,.65f,.28f)};
    return Colors[FMath::Clamp(Cost,1,5)-1];
}

TSharedRef<SWidget> FWCArtSlice::MakeShopCard(TFunction<FWCArtCardData()> Data,
    TFunction<void()> Action,TFunction<bool()> Enabled)
{
    const auto Small=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),10);
    const auto Bold=HeadingFont(12);
    if(IsStorybook()){
        const auto CardSmall=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),12);
        const auto NameFont=HeadingFont(14);
        const auto CostFont=HeadingFont(13);
        const auto ArtHeight=[] {return FOptionalSize(FMath::Clamp(float(ViewportSlateSize().Y)*.15f,88.f,144.f));};
        return SNew(SWCArtButton).ButtonStyle(&Resources().Card).ContentPadding(FMargin(6,5))
            .IsEnabled_Lambda([Enabled]{return Enabled();}).ToolTipText_Lambda([Data]{return Text(Data().Tooltip+TEXT("\n")+Data().Detail);})
            .OnClicked_Lambda([Action]{Action();return FReply::Handled();})
            [SNew(SWCReadableArt)[SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,3)[SNew(SBox).HeightOverride(3)
                    [SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")))
                        .BorderBackgroundColor_Lambda([Data]{return TierColor(Data().Cost);})]]
                +SVerticalBox::Slot().AutoHeight()[SNew(SBox).HeightOverride(14)
                    [SNew(STextBlock).Font(CardSmall).ColorAndOpacity(FLinearColor(.96f,.58f,.45f))
                        .Justification(ETextJustify::Center).Text_Lambda([Data,Enabled]{const auto Card=Data();return Text(!Enabled()&&Card.Cost>0?
                            (Card.Availability.IsEmpty()?TEXT("UNAVAILABLE"):Card.Availability):FString());})]]
                +SVerticalBox::Slot().FillHeight(1)[SNew(SBox).HeightOverride_Lambda(ArtHeight)
                    [SNew(SOverlay)
                        +SOverlay::Slot()[SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SImage).Image_Lambda([Data]{return Portrait(Data().UnitId);})]]
                        +SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(STextBlock).Font(HeadingFont(46))
                            .ColorAndOpacity_Lambda([Data]{return TierColor(Data().Cost).CopyWithNewOpacity(.55f);})
                            .Text_Lambda([Data]{const auto Card=Data();
                                return Text(!Card.UnitId.IsEmpty()&&Portrait(Card.UnitId)->DrawAs==ESlateBrushDrawType::NoDrawType?Card.Name.Left(1).ToUpper():FString());})]]]
                +SVerticalBox::Slot().AutoHeight().Padding(0,4,0,0)[SNew(STextBlock).Font(NameFont)
                    .ColorAndOpacity_Lambda([Data]{return TierColor(Data().Cost);})
                    .Justification(ETextJustify::Center).AutoWrapText(true).Text_Lambda([Data]{return Text(Data().Name);})]
                +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(CardSmall).ColorAndOpacity(FLinearColor(.68f,.72f,.66f))
                    .Justification(ETextJustify::Center).AutoWrapText(true).Text_Lambda([Data]{
                        FString Detail=Data().Detail;const int Newline=Detail.Find(TEXT("\n"));
                        if(Newline>=0)Detail=Detail.Left(Newline);return Text(Detail);})]
                +SVerticalBox::Slot().AutoHeight().Padding(0,4,0,0)[SNew(SHorizontalBox)
                    +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[SNew(SBox).WidthOverride(24).HeightOverride(24)
                        [SNew(SImage).Image_Lambda([Data]{return AbilityIcon(Data().UnitId);})]]
                    +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(4,0)[SNew(STextBlock).Font(CardSmall).ColorAndOpacity(Paper)
                        .AutoWrapText(true).Text_Lambda([Data]{return Text(Data().Footer);})]
                    +SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[SNew(STextBlock).Font(CostFont).ColorAndOpacity(Paper)
                        .Text_Lambda([Data]{return Text(Data().Cost>0?FString::Printf(TEXT("%d g"),Data().Cost):TEXT("—"));})]]]];
    }
    return SNew(SWCArtButton).ButtonStyle(&Resources().Card).IsEnabled_Lambda([Enabled]{return Enabled();})
        .ToolTipText_Lambda([Data]{return Text(Data().Tooltip);})
        .OnClicked_Lambda([Action]{Action();return FReply::Handled();})
        [SNew(SBox).MinDesiredHeight(78)
            [SNew(SVerticalBox)
                +SVerticalBox::Slot().AutoHeight()[SNew(SHorizontalBox)
                    +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Bold)
                        .ColorAndOpacity(Paper).AutoWrapText(true).Text_Lambda([Data]{return Text(Data().Name);})]
                    +SHorizontalBox::Slot().AutoWidth().Padding(4,0,0,0)[SNew(SBorder)
                        .BorderImage(FCoreStyle::Get().GetBrush(TEXT("WhiteBrush")))
                        .BorderBackgroundColor_Lambda([Data]{return TierColor(Data().Cost);}).Padding(FMargin(5,2))
                        [SNew(STextBlock).Font(Bold).ColorAndOpacity(Ink)
                            .Text_Lambda([Data]{const int Cost=Data().Cost;return Text(Cost>0?FString::Printf(TEXT("%dg"),Cost):TEXT("—"));})]]]
                +SVerticalBox::Slot().FillHeight(1).Padding(0,4)[SNew(SHorizontalBox)
                    +SHorizontalBox::Slot().AutoWidth().Padding(0,0,7,0)[SNew(SBox).WidthOverride(44).HeightOverride(44)
                        .Visibility_Lambda([Data]{return Data().UnitId==TEXT("wc_vn_shieldbearer")?EVisibility::Visible:EVisibility::Collapsed;})
                        [SNew(SImage).Image(BellbackPortrait())]]
                    +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Small)
                        .ColorAndOpacity(Paper).AutoWrapText(true).Text_Lambda([Data]{return Text(Data().Detail);})]]
                +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Small).ColorAndOpacity(Paper)
                    .AutoWrapText(true).Text_Lambda([Data]{return Text(Data().Footer);})]]];
}

TSharedRef<SWidget> FWCArtSlice::MakeStudyPanel(TFunction<FString()> SelectedUnitId,
    TFunction<FString()> SelectedName)
{
    const auto Small=FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),10);
    const auto Bold=FCoreStyle::GetDefaultFontStyle(TEXT("Bold"),11);
    if(IsStorybook())return MakePanel(SNew(SVerticalBox)
        +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Bold).ColorAndOpacity(Paper).AutoWrapText(true).Text(Text(TEXT("PORTRAIT & ABILITY STUDIES")))]
        +SVerticalBox::Slot().AutoHeight().Padding(0,6)[SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(88).HeightOverride(88)[SNew(SImage)
                .Image_Lambda([SelectedUnitId]{const FString Id=SelectedUnitId();return Portrait(Id.IsEmpty()?TEXT("wc_vn_shieldbearer"):Id);})]]
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center).Padding(8,0)[SNew(STextBlock).Font(Small).ColorAndOpacity(Paper).AutoWrapText(true)
                .Text_Lambda([SelectedName]{return Text(SelectedName()+TEXT("\nSelect this creature on the board to inspect its attack, ability and current state."));})]]
        +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Left)[SNew(SBox).WidthOverride(44).HeightOverride(44)[SNew(SImage)
            .Image_Lambda([SelectedUnitId]{const FString Id=SelectedUnitId();return AbilityIcon(Id.IsEmpty()?TEXT("wc_vn_shieldbearer"):Id);})]]);
    const auto ShowPortrait=[SelectedUnitId]{const FString Id=SelectedUnitId();return Id.IsEmpty()||Id==TEXT("wc_vn_shieldbearer");};
    return SNew(SBorder).BorderImage(&Resources().Panel).Padding(8)
        [SNew(SVerticalBox)
            +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Font(Bold).ColorAndOpacity(Paper).AutoWrapText(true).Text(Text(TEXT("ART SLICE · PORTRAIT & RELIC STUDY")))]
            +SVerticalBox::Slot().AutoHeight().Padding(0,6)[SNew(SHorizontalBox)
                +SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)[SNew(SBox).WidthOverride(76).HeightOverride(76)
                    .Visibility_Lambda([ShowPortrait]{return ShowPortrait()?EVisibility::Visible:EVisibility::Collapsed;})
                    [SNew(SImage).Image(BellbackPortrait())]]
                +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Small).ColorAndOpacity(Paper).AutoWrapText(true)
                    .Text_Lambda([ShowPortrait,SelectedName]{return Text(ShowPortrait()?TEXT("Bellback\nPortrait study; the board creature is still a gameplay proxy."):
                        SelectedName()+TEXT("\nNo portrait in this first slice. Board identity remains the current proxy."));})]]
            +SVerticalBox::Slot().AutoHeight()[SNew(SHorizontalBox)
                +SHorizontalBox::Slot().AutoWidth().Padding(0,0,8,0)[SNew(SBox).WidthOverride(48).HeightOverride(48)[SNew(SImage).Image(HeavyBloomIcon())]]
                +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)[SNew(STextBlock).Font(Small).ColorAndOpacity(Paper).AutoWrapText(true)
                    .Text(Text(TEXT("Heavy Bloom · icon study\nReference only; does not equip a relic.")))]]];
}
