using UnrealBuildTool;
public class WonderChessTarget : TargetRules
{
    public WonderChessTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("WonderChessRuntime");
    }
}
