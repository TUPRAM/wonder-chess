using UnrealBuildTool;
public class WonderChessRuntime : ModuleRules
{
    public WonderChessRuntime(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;
        bEnableExceptions = true;
        PublicDependencyModuleNames.AddRange(new [] {"Core", "CoreUObject", "Engine", "InputCore", "Json", "JsonUtilities", "UMG", "Slate", "SlateCore", "NetCore", "RenderCore", "RHI"});
    }
}
