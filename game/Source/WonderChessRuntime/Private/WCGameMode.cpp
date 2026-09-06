#include "WCGameMode.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"

AWCGameMode::AWCGameMode()
{
    HUDClass = AWCHUD::StaticClass();
    DefaultPawnClass = nullptr;
}

void AWCHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas) return;
    DrawRect(FLinearColor(0.018f, 0.035f, 0.05f), 0, 0, Canvas->SizeX, Canvas->SizeY);
    DrawText(TEXT("WONDER CHESS"), FLinearColor(1.f, .78f, .36f), Canvas->SizeX*.20f, Canvas->SizeY*.30f, GEngine->GetLargeFont(), 2.4f);
    DrawText(TEXT("A world of magic. A board of possibilities."), FLinearColor::White, Canvas->SizeX*.20f, Canvas->SizeY*.46f, GEngine->GetMediumFont(), 1.2f);
    DrawText(TEXT("WC-300 - executable toolchain checkpoint"), FLinearColor(.6f,.75f,.8f), Canvas->SizeX*.20f, Canvas->SizeY*.59f, GEngine->GetMediumFont());
}
