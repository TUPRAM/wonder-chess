#include "WCVNextLab.h"
#include "WCCragstoatPresentation.h"
#include "WCBellbackPresentation.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "SkeletalRenderPublic.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Kismet/KismetSystemLibrary.h"

namespace {
FString CragCombatSignature(const wc::Combat& C)
{
    FString S;
    for(const auto& E:C.Events())S+=FString::Printf(TEXT("%d,%llu,%llu,%llu,%d,%lld,%lld,%lld,%lld,%d,%d,%d,%llu,%lld;"),E.tick,E.source,E.target,E.action,int(E.effect),E.requested,E.resolved,E.absorbed,E.healthLoss,E.cell.column,E.cell.row,int(E.mechanic),E.guardedBy,E.prevented);
    for(const auto& U:C.Units())S+=FString::Printf(TEXT("%llu,%lld,%lld,%d,%d,%d,%d,%d;"),U.id,U.health,U.shield,U.cell.column,U.cell.row,int(U.state),int(U.facing),U.relic);
    const auto& R=C.Result();S+=FString::Printf(TEXT("%d,%d,%d,%d,%d"),R.winner,R.timeout,R.ticks,R.survivors[0],R.survivors[1]);
    const FTCHARToUTF8 Utf8(*S);return FSHA1::HashBuffer(Utf8.Get(),Utf8.Length()).ToString();
}
}

void AWCVNextLab::TickCragstoatRoute(float DeltaSeconds)
{
    const bool Audio20=FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatAudio20"));
    const auto Finish=[&](FString Error){
        auto R=MakeShared<FJsonObject>();
        R->SetStringField(TEXT("status"),Error.IsEmpty()?TEXT("PASS_SCOPED_RUNTIME_ROUTE"):TEXT("FAIL"));
        R->SetStringField(TEXT("failure"),Error);
        R->SetNumberField(TEXT("minimum_skin_z_cm"),CragMinimumZ);
        R->SetNumberField(TEXT("board_top_z_cm"),6);
        R->SetNumberField(TEXT("surface_samples"),CragFloorSamples);
        R->SetNumberField(TEXT("corrected_pose_samples"),CragCorrectedPoseSamples);
        R->SetNumberField(TEXT("maximum_foot_correction_cm"),CragMaximumFootCorrection);
        R->SetBoolField(TEXT("sampled_native_pose_valid"),CragFloorSamples>0&&CragNativePoseValid);
        R->SetNumberField(TEXT("peak_visible_cragstoats"),CragPeakUnits);
        R->SetNumberField(TEXT("peak_real_fight_cragstoats"),CragRealFightPeakUnits);
        R->SetBoolField(TEXT("twenty_cragstoat_audio_diagnostic"),Audio20);
        R->SetBoolField(TEXT("control_combat_matches"),CragControlMatches);
        R->SetBoolField(TEXT("cue_pool_overflow"),CueOverflow);
        R->SetStringField(TEXT("catalog_digest"),UTF8_TO_TCHAR(Catalog.contentDigest.c_str()));
        R->SetBoolField(TEXT("storybook_visuals"),Storybook);
        R->SetStringField(TEXT("audio_recording_api_start_utc"),CragAudioStartUtc);
        R->SetStringField(TEXT("audio_recording_api_stop_utc"),CragAudioStopUtc);
        R->SetNumberField(TEXT("audio_recording_api_wall_seconds"),CragAudioStopWall>CragAudioStartWall?CragAudioStopWall-CragAudioStartWall:0);
        R->SetStringField(TEXT("audio_timing_scope"),TEXT("Wall-clock StartRecordingOutput to StopRecordingOutput API window; mixer callback sample boundaries are not independently timestamped."));
        R->SetStringField(TEXT("rule_scope"),TEXT("Baseline catalog cooldown rules. This exercise constructs control Combat from the same loaded Catalog; Storybook flag selects visual cues only."));
        R->SetStringField(TEXT("command_line"),FCommandLine::Get());
        R->SetStringField(TEXT("boundary"),Audio20?
            TEXT("Canonical charge fight then twenty real canonical Cragstoats in authoritative combat with audio, followed by a distinct muted twenty-Cragstoat nine-clip cosmetic tour. Sparse CPU skin/contact and requested clip counters do not establish full pose/transition/LOD, performance, listening or human motion/release acceptance."):
            TEXT("Two rendered authoritative fights and a separate twenty-Cragstoat nine-clip cosmetic tour. Sparse CPU skin/contact and requested clip counters do not establish full pose/transition/LOD, performance, listening or human motion/release acceptance."));
        TArray<TSharedPtr<FJsonValue>> Names;
        for(auto N:CragClipsSeen)Names.Add(MakeShared<FJsonValueString>(N.ToString()));R->SetArrayField(TEXT("clips_seen"),Names);
        Names.Reset();for(const auto& N:CueKindsSeen)Names.Add(MakeShared<FJsonValueString>(N));R->SetArrayField(TEXT("cue_kinds"),Names);
        TArray<FString> AssetPaths=CragLoadedAssetsSeen.Array();AssetPaths.Sort();Names.Reset();
        for(const auto& Path:AssetPaths)Names.Add(MakeShared<FJsonValueString>(Path));R->SetArrayField(TEXT("observed_loaded_mesh_and_animation_assets"),Names);
        FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));
        FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("cragstoat-route.json")));
        FFileHelper::SaveStringToFile(CragFrameCsv,*(EvidenceDirectory/TEXT("skin-samples.csv")));
        FPlatformMisc::RequestExitWithStatus(false,Error.IsEmpty()?0:1);
    };
    if(!LoadError.IsEmpty()){Finish(LoadError);return;}
    if(!CragRouteStage){
        if(!CragstoatCandidate||SoloMode){Finish(TEXT("Cragstoat candidate laboratory required"));return;}
        if(IFileManager::Get().FileExists(*(EvidenceDirectory/TEXT("cragstoat-route.json")))){FPlatformMisc::RequestExitWithStatus(false,1);return;}
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        CragRouteStarted=Elapsed;CragRouteStage=1;
        CragFrameCsv=TEXT("age,stage,id,requested_clip,requested_seconds,minimum_z_cm,vertices,corrected_legs,maximum_foot_correction_cm,move_clip_rate,spawned_sound_count,hit_overlay,world_x_cm,world_y_cm,mesh_world_yaw\n");
        bool Found=false;
        for(const auto& Pair:wc::BuiltinScenarioPairs(Catalog))if(Pair.mechanic==wc::AbilityMechanic::MomentumCharge){Formation=Pair.a.armies;Seed=int(Pair.a.seed);Found=true;break;}
        if(!Found){Finish(TEXT("Canonical charge fixture absent"));return;}
        PreparationDirty=true;if(!Start()){Finish(TEXT("Charge fixture rejected"));return;}
        BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
        if(FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatCaptureAudio"))){
            UKismetSystemLibrary::ExecuteConsoleCommand(this,TEXT("au.NeverDisableSubmixes 1"));
            CragAudioStartWall=FPlatformTime::Seconds();CragAudioStartUtc=FDateTime::UtcNow().ToIso8601();
            UAudioMixerBlueprintLibrary::StartRecordingOutput(this,100,nullptr);
        }
    }
    const double Age=Elapsed-CragRouteStarted;UpdateCamera();
    if(CragRouteStage<=2){
        Accumulator+=DeltaSeconds;const double Step=Catalog.rules.tickMs/1000.;
        for(int I=0;I<20&&Accumulator>=Step&&Fight&&!Fight->Result().complete;++I){
            Advance();BellbackControl->Tick();Accumulator-=Step;
            CragControlMatches&=CragCombatSignature(*Fight)==CragCombatSignature(*BellbackControl);
        }
        UpdatePresentation(DeltaSeconds);UpdateInterfaceText();
    }
    const auto Shot=[&](const FString& Name){
        if(CragShots.Contains(Name)||FScreenshotRequest::IsScreenshotRequested())return;
        const FString Path=EvidenceDirectory/(Name+TEXT(".png"));
        if(IFileManager::Get().FileExists(*Path))return;
        CragShots.Add(Name);FScreenshotRequest::RequestScreenshot(Path,true,false);
    };
    if(CurrentCueKinds.Contains(TEXT("cragstoat_charge_aim")))Shot(TEXT("charge-aim"));
    if(CurrentCueKinds.Contains(TEXT("cragstoat_charge_footfalls")))Shot(TEXT("charge-footfalls"));
    if(CragRouteStage<=2&&Age>=(CragRouteStage==1?22:48)){
        CragControlMatches&=CragCombatSignature(*Fight)==CragCombatSignature(*BellbackControl);
        Reset();++BellbackGeneration;++CragRouteStage;
        int Crag=-1,Bell=-1;for(int I=0;I<int(Catalog.units.size());++I){if(Catalog.units[I].id=="wc_vn_boar_rusher")Crag=I;if(Catalog.units[I].id=="wc_vn_shieldbearer")Bell=I;}
        if(Crag<0||Bell<0){Finish(TEXT("Required enabled heroes absent"));return;}
        Formation[0].clear();Formation[1].clear();NextId=1;
        for(int Side=0;Side<2;++Side)for(int I=0;I<(CragRouteStage==2&&!Audio20?4:10);++I){
            wc::OwnedUnit U;U.id=NextId++;U.definition=CragRouteStage==2&&!Audio20&&I%2?Bell:Crag;U.star=1;U.onBoard=true;U.cell={I%8,I/8};U.facing=wc::Facing::Forward;Formation[Side].push_back(U);
        }
        PreparationDirty=true;UpdatePresentation(0);
        if(CragRouteStage==2){if(!Start()){Finish(Audio20?TEXT("Twenty-Cragstoat fight rejected"):TEXT("Mixed charge fight rejected"));return;}BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);}
    }
    if(CragRouteStage==3){
        static const FName Clips[]={TEXT("Idle"),TEXT("Move"),TEXT("TurnLeft"),TEXT("TurnRight"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory")};
        const int Index=FMath::Clamp(int((Age-48)/3),0,8);const float Local=FMath::Fmod(float(Age-48),3.f);
        int Count=0;
        for(auto& Pair:Pieces){auto& V=Pair.Value;if(!V.Actor.IsValid()||!V.Cragstoat)continue;
            V.Actor->SetActorLocation(FVector((Count%5-2)*290,(Count/5-1.5f)*340,0));++Count;
            FWCBellbackFrame F;F.Generation=BellbackGeneration;F.Id=Pair.Key;F.Side=V.Side;F.Facing=0;F.Clock=Age;F.DeltaSeconds=DeltaSeconds;F.AllowSound=false;
            F.ReviewClip=Clips[Index];F.ReviewSeconds=FMath::Fmod(Local,FMath::Max(.001f,V.Cragstoat->ClipDuration(Clips[Index])));
            V.Cragstoat->Present(F);
        }
        if(Local>1)Shot(TEXT("tour-")+Clips[Index].ToString());
    }
    int Visible=0;const bool Sample=Age-CragLastSurface>=.3&&Age>1&&CragRouteStage<4;
    for(const auto& Pair:Pieces){const auto& V=Pair.Value;if(!V.Cragstoat)continue;++Visible;
        if(auto* LoadedMesh=V.Cragstoat->GetMesh()){
            if(LoadedMesh->GetSkeletalMeshAsset())CragLoadedAssetsSeen.Add(LoadedMesh->GetSkeletalMeshAsset()->GetPathName());
            if(const auto* LoadedPose=Cast<UWCCragstoatAnimInstance>(LoadedMesh->GetAnimInstance())){
                for(const auto* LoadedClip:{LoadedPose->Current.Get(),LoadedPose->Previous.Get(),LoadedPose->HitReaction.Get(),LoadedPose->GroundingReference.Get()})
                    if(LoadedClip)CragLoadedAssetsSeen.Add(LoadedClip->GetPathName());
            }
        }
        const FName Clip=V.Cragstoat->ClipName();if(!Clip.IsNone())CragClipsSeen.Add(Clip);
        if(Sample&&FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatContact"))){
            auto* M=V.Cragstoat->GetMesh();TArray<FFinalSkinVertex> Vertices;M->GetCPUSkinnedVertices(Vertices,0);
            if(Vertices.IsEmpty()){CragNativePoseValid=false;Finish(TEXT("Native CPU skin samples missing"));return;}
            const auto* Pose=Cast<UWCCragstoatAnimInstance>(M->GetAnimInstance());
            if(!Pose||!Pose->PoseValid||!FMath::IsFinite(Pose->MaximumFootCorrection)){
                CragNativePoseValid=false;Finish(TEXT("Native Cragstoat pose evaluation rejected; reference fallback is not a contact pass"));return;
            }
            if(Pose->CorrectedLegs>0)++CragCorrectedPoseSamples;
            CragMaximumFootCorrection=FMath::Max(CragMaximumFootCorrection,Pose->MaximumFootCorrection);
            double Min=MAX_dbl;for(const auto& P:Vertices)Min=FMath::Min(Min,M->GetComponentTransform().TransformPosition(FVector(P.Position)).Z);
            CragMinimumZ=FMath::Min(CragMinimumZ,Min);++CragFloorSamples;
            const FVector Location=M->GetComponentLocation();
            CragFrameCsv+=FString::Printf(TEXT("%.5f,%d,%llu,%s,%.5f,%.7f,%d,%d,%.7f,%.7f,%d,%d,%.7f,%.7f,%.7f\n"),Age,CragRouteStage,Pair.Key,*Clip.ToString(),V.Cragstoat->ClipSeconds(),Min,Vertices.Num(),Pose->CorrectedLegs,Pose->MaximumFootCorrection,V.Cragstoat->MoveRate(),V.Cragstoat->SoundCount(),int(V.Cragstoat->HasHitOverlay()),Location.X,Location.Y,M->GetComponentRotation().Yaw);
        }
    }
    if(Sample)CragLastSurface=Age;CragPeakUnits=FMath::Max(CragPeakUnits,Visible);
    if(CragRouteStage<=2)CragRealFightPeakUnits=FMath::Max(CragRealFightPeakUnits,Visible);
    if(Age>=76&&CragRouteStage==3){
        CragRouteStage=4;
        if(FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatCaptureAudio"))){
            CragAudioStopWall=FPlatformTime::Seconds();CragAudioStopUtc=FDateTime::UtcNow().ToIso8601();
            UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("cragstoat-master-submix"),FPaths::ConvertRelativePathToFull(EvidenceDirectory),nullptr,nullptr);
        }
    }
    if(Age>=84){
        const bool RequestedContact=FParse::Param(FCommandLine::Get(),TEXT("WCCragstoatContact"));
        Finish(!CragControlMatches?TEXT("Presentation/control combat signatures differ"):CueOverflow?TEXT("Cue pool overflow"):
            RequestedContact&&(!CragFloorSamples||CragMinimumZ<5.95)?TEXT("Requested board contact missing or penetrating"):
            CragClipsSeen.Num()!=9||CragPeakUnits!=20?TEXT("Nine-clip/twenty-creature coverage incomplete"):
            Audio20&&CragRealFightPeakUnits!=20?TEXT("Twenty real Cragstoat audio-fight coverage incomplete"):
            !CragShots.Contains(TEXT("charge-aim"))||!(Storybook?CragShots.Contains(TEXT("charge-footfalls")):CueKindsSeen.Contains(TEXT("charge_trail")))?TEXT("Charge cue coverage incomplete"):FString());
    }
}
