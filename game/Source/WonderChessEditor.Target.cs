using UnrealBuildTool;
public class WonderChessEditorTarget : TargetRules
{
    public WonderChessEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("WonderChessRuntime");
    }
}
