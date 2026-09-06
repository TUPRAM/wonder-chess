#pragma once

#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "Simulation/WonderSimulation.h"

struct FWCDefinitionText
{
    TMap<FString, TMap<FString, FString>> Locales;
    TMap<FString, TSharedPtr<FJsonObject>> Units;
    TMap<FString, TSharedPtr<FJsonObject>> NeutralUnits;
    TSharedPtr<FJsonObject> World, Rules, Traits, Bots, Neutrals;
    FString Localized(const FString& Key, const FString& Language = TEXT("en")) const;
    FString AbilityTooltip(const FString& UnitId, const FString& Language = TEXT("en")) const;
};

namespace wc
{
    WONDERCHESSRUNTIME_API bool LoadCatalog(Catalog& OutCatalog, FString& Error, FWCDefinitionText* Text = nullptr);
}
