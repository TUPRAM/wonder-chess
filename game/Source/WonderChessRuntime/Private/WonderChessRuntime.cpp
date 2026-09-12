#include "Modules/ModuleManager.h"
#include "GameMapsSettings.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

class FWonderChessRuntimeModule : public FDefaultGameModuleImpl
{
public:
    virtual void StartupModule() override
    {
        if (FParse::Param(FCommandLine::Get(), TEXT("WCLab")))
        {
            UGameMapsSettings::SetGlobalDefaultGameMode(TEXT("/Script/WonderChessRuntime.WCVNextLabMode"));
            UGameMapsSettings::SetGameDefaultMap(TEXT("/Engine/Maps/Entry"));
        }
    }
};
IMPLEMENT_PRIMARY_GAME_MODULE(FWonderChessRuntimeModule, WonderChessRuntime, "WonderChess");
