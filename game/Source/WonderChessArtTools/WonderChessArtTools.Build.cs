using UnrealBuildTool;
public class WonderChessArtTools : ModuleRules
{
    public WonderChessArtTools(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] {"Core", "CoreUObject", "Engine"});
        PrivateDependencyModuleNames.AddRange(new[] {"UnrealEd", "WonderChessRuntime", "Json", "RenderCore", "RHI", "ControlRig", "AssetRegistry", "MovieScene", "MovieSceneTracks"});
    }
}
