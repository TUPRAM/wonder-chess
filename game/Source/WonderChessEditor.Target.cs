using UnrealBuildTool;
public class WonderChessEditorTarget : TargetRules
{
    public WonderChessEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_7;
        ExtraModuleNames.Add("WonderChessRuntime");
    }
}
