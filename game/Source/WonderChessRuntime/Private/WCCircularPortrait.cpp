#include "WCCircularPortrait.h"

#include "Rendering/DrawElements.h"
#include "Rendering/RenderingCommon.h"
#include "Styling/SlateBrush.h"
#include "Textures/SlateShaderResource.h"

void SWCCircularPortrait::Construct(const FArguments& Args)
{
    Image = Args._Image;
}

FVector2D SWCCircularPortrait::ComputeDesiredSize(float) const
{
    return FVector2D(78.f, 78.f);
}

int32 SWCCircularPortrait::OnPaint(const FPaintArgs&, const FGeometry& Geometry,
    const FSlateRect&, FSlateWindowElementList& OutDrawElements, int32 LayerId,
    const FWidgetStyle& WidgetStyle, bool bParentEnabled) const
{
    const FSlateBrush* Brush = Image.Get();
    if (!Brush || Brush->DrawAs == ESlateBrushDrawType::NoDrawType || !Brush->GetResourceObject())
        return LayerId;

    const FSlateResourceHandle Handle = Brush->GetRenderingResource();
    const FSlateShaderResourceProxy* Proxy = Handle.GetResourceProxy();
    if (!Proxy)
        return LayerId;

    const FVector2f Size(Geometry.GetLocalSize());
    const float OuterRadius = 0.5f * FMath::Min(Size.X, Size.Y) - 0.5f;
    if (OuterRadius <= 1.5f)
        return LayerId;
    const float InnerRadius = OuterRadius - 1.25f;
    const FVector2f Center = Size * 0.5f;
    const FVector2f UVCenter = Proxy->StartUV + Proxy->SizeUV * 0.5f;
    const FVector2f UVRadius = Proxy->SizeUV * 0.5f;
    const FLinearColor Tint = Brush->GetTint(WidgetStyle) * WidgetStyle.GetColorAndOpacityTint();
    const FColor Solid = Tint.ToFColor(true);
    const FColor Feather = FLinearColor(Tint.R, Tint.G, Tint.B, 0.f).ToFColor(true);
    const FSlateRenderTransform& Transform = Geometry.GetAccumulatedRenderTransform();

    constexpr int32 Segments = 64;
    TArray<FSlateVertex> Vertices;
    TArray<SlateIndex> Indices;
    Vertices.Reserve(1 + 2 * Segments);
    Indices.Reserve(9 * Segments);
    const auto Vertex = [&](const FVector2f& Position, const FVector2f& UV, const FColor Color)
    {
        return FSlateVertex::Make<ESlateVertexRounding::Disabled>(Transform, Position, UV, Color);
    };
    Vertices.Add(Vertex(Center, UVCenter, Solid));
    for (int32 Index = 0; Index < Segments; ++Index)
    {
        const float Angle = 2.f * PI * float(Index) / float(Segments);
        const FVector2f Direction(FMath::Cos(Angle), FMath::Sin(Angle));
        const FVector2f InnerPosition = Center + Direction * InnerRadius;
        const FVector2f OuterPosition = Center + Direction * OuterRadius;
        Vertices.Add(Vertex(InnerPosition, UVCenter + UVRadius * (Direction * (InnerRadius / OuterRadius)), Solid));
        Vertices.Add(Vertex(OuterPosition, UVCenter + UVRadius * Direction, Feather));
    }
    for (int32 Index = 0; Index < Segments; ++Index)
    {
        const SlateIndex Inner = SlateIndex(1 + 2 * Index);
        const SlateIndex Outer = SlateIndex(Inner + 1);
        const SlateIndex NextInner = SlateIndex(1 + 2 * ((Index + 1) % Segments));
        const SlateIndex NextOuter = SlateIndex(NextInner + 1);
        Indices.Append({0, Inner, NextInner, Inner, Outer, NextInner, NextInner, Outer, NextOuter});
    }

    FSlateDrawElement::MakeCustomVerts(OutDrawElements, LayerId, Handle, Vertices, Indices,
        nullptr, 0, 0, ShouldBeEnabled(bParentEnabled) ? ESlateDrawEffect::None : ESlateDrawEffect::DisabledEffect);
    return LayerId;
}
