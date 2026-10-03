#include "WCVNextLab.h"
#include "Simulation/WonderScenarioFile.h"
#include "Misc/Paths.h"
#include <algorithm>
#include <exception>

namespace
{
FString ScenarioString(const std::string& Value) { return UTF8_TO_TCHAR(Value.c_str()); }
std::filesystem::path FormationSavePath()
{
    const FString Path = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("WonderVNext/Lab/formation.wcf"));
    return std::filesystem::path(*Path);
}
const TCHAR* ScenarioOutcome(const wc::ScenarioRun& Run)
{
    return Run.result.winner < 0 ? TEXT("tie") : Run.result.winner == 0 ? TEXT("teal wins") : TEXT("coral wins");
}
FString DescribePair(const wc::ScenarioPair& Pair)
{
    return ScenarioString(Pair.id)+TEXT(" · ")+ScenarioString(Pair.a.name)+TEXT("\n")+
        ScenarioString(Pair.question)+TEXT("\nDeclared change: ")+ScenarioString(Pair.a.intendedVariable);
}
}

bool AWCVNextLab::ApplyFormationScenario(const wc::FormationScenario& Scenario, const FString& Success)
{
    if (SoloMode || !LoadError.IsEmpty()) { Message=TEXT("Scenarios are available in the loaded formation lab."); return false; }
    std::string Error;
    if (!wc::ValidateScenario(Catalog,Scenario,Error)) { Message=TEXT("Formation rejected: ")+ScenarioString(Error); return false; }
    if (Scenario.seed < 1 || Scenario.seed > uint64(MAX_int32)) {
        Message=TEXT("This lab accepts seeds 1 through 2147483647. The current formation was preserved."); return false;
    }
    uint64 PendingNextId=1;
    for(const auto& Army:Scenario.armies)for(const auto& Unit:Army)PendingNextId=std::max(PendingNextId,Unit.id+1);
    if(PendingNextId>=(uint64(1)<<20)) {
        Message=TEXT("This formation leaves no identity for another recruit. The current formation was preserved."); return false;
    }
    Formation=Scenario.armies; Seed=int(Scenario.seed); NextId=PendingNextId;
    ReplayFormation=Formation; ReplaySeed=Seed;
    Fight.reset();PreparationState.reset();Selected=0;Paused=false;Accumulator=0;
    CombatInvariantFailed=false;PreparationDirty=true;PreparationCells.Reset();PreparationRecipient=0;
    PreparationHint.Empty();Message=Success;
    UE_LOG(LogTemp,Display,TEXT("WC_SCENARIO_APPLIED id=%s seed=%d units_a=%d units_b=%d"),
        *ScenarioString(Scenario.id),Seed,int(Formation[0].size()),int(Formation[1].size()));
    return true;
}

void AWCVNextLab::NextScenario()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    try {
        const auto Pairs=wc::BuiltinScenarioPairs(Catalog);
        const int Next=(ScenarioIndex+1)%int(Pairs.size());
        if(ApplyFormationScenario(Pairs[Next].a,TEXT("Formation A loaded. Predict the result, then press Start."))){
            ScenarioIndex=Next;ScenarioAlternative=false;ScenarioMirrored=false;ScenarioReport.Empty();
            ScenarioDescription=DescribePair(Pairs[Next]);
        }
    } catch(const std::exception& Error){Message=TEXT("Scenario unavailable: ")+ScenarioString(Error.what());}
}

void AWCVNextLab::LoadScenarioVariant(bool Alternative)
{
    if(SoloMode||!LoadError.IsEmpty())return;
    try {
        const auto Pairs=wc::BuiltinScenarioPairs(Catalog);
        const int Index=ScenarioIndex<0?0:ScenarioIndex;
        if(Index>=int(Pairs.size())){Message=TEXT("Select a scenario first.");return;}
        auto Pair=ScenarioMirrored?wc::MirrorScenarioPair(Pairs[Index]):Pairs[Index];
        if(ApplyFormationScenario(Alternative?Pair.b:Pair.a,Alternative?
            TEXT("Formation B loaded. The declared change is applied; press Start to observe it."):
            TEXT("Formation A loaded. Press Start to observe the original formation."))){
            ScenarioIndex=Index;ScenarioAlternative=Alternative;
            ScenarioDescription=DescribePair(Pairs[Index]);
        }
    } catch(const std::exception& Error){Message=TEXT("Scenario unavailable: ")+ScenarioString(Error.what());}
}

void AWCVNextLab::CompareScenario()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    try {
        const auto Pairs=wc::BuiltinScenarioPairs(Catalog);
        if(ScenarioIndex<0||ScenarioIndex>=int(Pairs.size())){Message=TEXT("Choose Next scenario before comparing its two formations.");return;}
        const auto Pair=ScenarioMirrored?wc::MirrorScenarioPair(Pairs[ScenarioIndex]):Pairs[ScenarioIndex];
        const auto A=wc::RunScenario(Catalog,Pair.a), B=wc::RunScenario(Catalog,Pair.b);
        const auto Sum=[](const wc::ScenarioRun& Run,auto Metric){return Metric(Run.sides[0])+Metric(Run.sides[1]);};
        ScenarioReport=FString::Printf(TEXT("Replayed built-in A / B\n%s at %.2fs / %s at %.2fs\n%s / %s\n"),
            ScenarioOutcome(A),A.result.ticks*Catalog.rules.tickMs/1000.,ScenarioOutcome(B),B.result.ticks*Catalog.rules.tickMs/1000.,
            A.result.timeout?TEXT("deadline"):TEXT("elimination"),B.result.timeout?TEXT("deadline"):TEXT("elimination"));
        FString Detail;
        switch(Pair.mechanic){
        case wc::AbilityMechanic::DirectionalGuard:
            Detail=FString::Printf(TEXT("Guard prevented: %.2f / %.2f health"),Sum(A,[](const auto& M){return M.guardPrevented;})/100.,Sum(B,[](const auto& M){return M.guardPrevented;})/100.);break;
        case wc::AbilityMechanic::MomentumCharge:
            Detail=FString::Printf(TEXT("Charge hits: %d / %d; moves: %d / %d"),Sum(A,[](const auto& M){return M.chargeHits;}),Sum(B,[](const auto& M){return M.chargeHits;}),Sum(A,[](const auto& M){return M.chargeLandings;}),Sum(B,[](const auto& M){return M.chargeLandings;}));break;
        case wc::AbilityMechanic::StationaryGrove:
            Detail=FString::Printf(TEXT("Effective healing: %.2f / %.2f health"),Sum(A,[](const auto& M){return M.healing;})/100.,Sum(B,[](const auto& M){return M.healing;})/100.);break;
        case wc::AbilityMechanic::ScreenedStrike:
        {
            const auto FirstTarget=[this](const wc::FormationScenario& Scenario,const wc::ScenarioRun& Run){
                for(const auto& Event:Run.events)if(Event.mechanic==wc::AbilityMechanic::ScreenedStrike&&Event.effect==wc::Effect::Damage){
                    const int Side=int((Event.target>>20)&1);const wc::Id Id=Event.target&((wc::Id(1)<<20)-1);
                    for(const auto& Unit:Scenario.armies[Side])if(Unit.id==Id)return ScenarioString(Catalog.units[Unit.definition].displayName);
                }
                return FString(TEXT("no hit"));
            };
            Detail=FString::Printf(TEXT("First strike: %s / %s\nStrike hits: %d / %d"),*FirstTarget(Pair.a,A),*FirstTarget(Pair.b,B),
                Sum(A,[](const auto& M){return M.strikeHits;}),Sum(B,[](const auto& M){return M.strikeHits;}));break;
        }
        case wc::AbilityMechanic::CrossingBeams:
            Detail=FString::Printf(TEXT("Beam-recipient hits: %d / %d"),Sum(A,[](const auto& M){return M.beamHits;}),Sum(B,[](const auto& M){return M.beamHits;}));break;
        case wc::AbilityMechanic::TidalPush:
            Detail=FString::Printf(TEXT("Tide hits: %d / %d; pushes: %d / %d"),Sum(A,[](const auto& M){return M.tideHits;}),Sum(B,[](const auto& M){return M.tideHits;}),Sum(A,[](const auto& M){return M.tidePushes;}),Sum(B,[](const auto& M){return M.tidePushes;}));break;
        case wc::AbilityMechanic::CocoonProjectile:
            Detail=FString::Printf(TEXT("Successful cocoons: %d / %d"),Sum(A,[](const auto& M){return M.cocoons;}),Sum(B,[](const auto& M){return M.cocoons;}));break;
        default:break;
        }
        ScenarioReport+=Detail+TEXT("\nBoth original fixtures were replayed. Board edits are not included in this comparison.");
        Message=TEXT("A/B comparison complete. The current board and playback were preserved.");
        UE_LOG(LogTemp,Display,TEXT("WC_SCENARIO_COMPARE id=%s mirrored=%d signature_a=%llu signature_b=%llu"),
            *ScenarioString(Pair.id),ScenarioMirrored,A.signature,B.signature);
    }catch(const std::exception& Error){Message=TEXT("Comparison failed: ")+ScenarioString(Error.what());}
}

void AWCVNextLab::MirrorFormation()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    auto Current=wc::MakeScenario(Catalog,"Current mirrored formation",Formation[0],Formation[1],uint64(Seed));
    if(ApplyFormationScenario(wc::MirrorScenario(Current),TEXT("Teams swapped and rotated. Press Start to test this orientation."))){
        ScenarioMirrored=!ScenarioMirrored;ScenarioReport.Empty();
    }
}

void AWCVNextLab::SaveFormationScenario()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    try {
        auto Scenario=wc::MakeScenario(Catalog,"Saved player formation",Formation[0],Formation[1],uint64(Seed));
        Scenario.intendedVariable="Player-edited starting formations; no causal comparison declaration";
        const auto Result=wc::SaveScenarioFile(Catalog,Scenario,FormationSavePath());
        Message=ScenarioString(Result.message);
        if(Result.succeeded)Message+=TEXT(" Saved both starting formations and the displayed seed.");
        UE_LOG(LogTemp,Display,TEXT("WC_SCENARIO_SAVE success=%d"),Result.succeeded);
    }catch(const std::exception& Error){Message=TEXT("Scenario save failed: ")+ScenarioString(Error.what());}
}

void AWCVNextLab::LoadFormationScenario()
{
    if(SoloMode||!LoadError.IsEmpty())return;
    wc::FormationScenario Pending;
    const auto Result=wc::LoadScenarioFile(Catalog,FormationSavePath(),Pending);
    if(!Result.succeeded){Message=ScenarioString(Result.message);return;}
    if(ApplyFormationScenario(Pending,ScenarioString(Result.message))){
        ScenarioIndex=-1;ScenarioAlternative=false;ScenarioMirrored=false;
        ScenarioDescription.Empty();
        ScenarioReport=TEXT("Loaded: ")+ScenarioString(Pending.name)+TEXT("\nIntended change: ")+ScenarioString(Pending.intendedVariable);
    }
}

FString AWCVNextLab::ScenarioText() const
{
    FString Text;
    if(ScenarioIndex>=0 && LoadError.IsEmpty())
        Text=ScenarioDescription+TEXT("\nSelected source: ")+(ScenarioAlternative?TEXT("B"):TEXT("A"))+
            (ScenarioMirrored?TEXT(" · mirrored"):TEXT(""));
    else Text=TEXT("Choose Next scenario to explore six formation relationships. A/B compares the original saved pair.");
    if(!ScenarioReport.IsEmpty())Text+=TEXT("\n\n")+ScenarioReport;
    return Text;
}
