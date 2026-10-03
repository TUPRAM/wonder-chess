#pragma once

#include "CoreMinimal.h"
#include "Widgets/SLeafWidget.h"

struct FSlateBrush;

// A small, non-interactive Slate image whose actual textured geometry is circular.
// Rounded-box brushes round their background, but do not mask an opaque portrait.
class SWCCircularPortrait final : public SLeafWidget
{
public:
    SLATE_BEGIN_ARGS(SWCCircularPortrait) {}
        SLATE_ATTRIBUTE(const FSlateBrush*, Image)
    SLATE_END_ARGS()

    void Construct(const FArguments& Args);

    virtual FVector2D ComputeDesiredSize(float LayoutScaleMultiplier) const override;
    virtual int32 OnPaint(const FPaintArgs& Args, const FGeometry& Geometry,
        const FSlateRect& CullingRect, FSlateWindowElementList& OutDrawElements,
        int32 LayerId, const FWidgetStyle& WidgetStyle, bool bParentEnabled) const override;

private:
    TAttribute<const FSlateBrush*> Image;
};
