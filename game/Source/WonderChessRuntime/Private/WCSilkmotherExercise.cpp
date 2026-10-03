#include "WCVNextLab.h"
#include "WCSilkmotherPresentation.h"
#include "WCBellbackPresentation.h"
#include "Components/SkeletalMeshComponent.h"
#include "SkeletalRenderPublic.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Kismet/KismetSystemLibrary.h"

void AWCVNextLab::TickSilkmotherRoute(float DeltaSeconds)
{
    const auto Finish=[&](FString Error){
        auto R=MakeShared<FJsonObject>();
        R->SetStringField(TEXT("status"),Error.IsEmpty()?TEXT("PASS_RUNTIME_ROUTE_ONLY"):TEXT("FAIL"));R->SetStringField(TEXT("failure"),Error);
        R->SetNumberField(TEXT("minimum_skin_z_cm"),SilkMinimumZ);R->SetNumberField(TEXT("board_top_z_cm"),6);
        R->SetNumberField(TEXT("surface_samples"),SilkFloorSamples);R->SetNumberField(TEXT("peak_visible_skeletons"),SilkPeakUnits);
        R->SetBoolField(TEXT("control_combat_matches"),SilkControlMatches);R->SetBoolField(TEXT("cue_pool_overflow"),CueOverflow);
        R->SetBoolField(TEXT("motion_revision_20260930"),FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherMotionRevision20260930")));
        R->SetNumberField(TEXT("hit_overlay_requested_samples"),SilkHitOverlaySamples);
        R->SetStringField(TEXT("hit_overlay_sample_scope"),TEXT("Component requested state; cold native combined skin tests and viewed captures establish evaluated deformation separately."));
        R->SetStringField(TEXT("boundary"),TEXT("Real rendered combat plus separate twenty-unit cosmetic clip tour. Sparse CPU skin checks are diagnostic, not performance samples or full stance/transition certification. Owner review and audio-file audit remain separate."));
        R->SetStringField(TEXT("command_line"),FCommandLine::Get());R->SetStringField(TEXT("catalog_digest"),UTF8_TO_TCHAR(Catalog.contentDigest.c_str()));
        TArray<TSharedPtr<FJsonValue>> Names;for(auto N:SilkClipsSeen)Names.Add(MakeShared<FJsonValueString>(N.ToString()));R->SetArrayField(TEXT("clips_seen"),Names);
        Names.Reset();for(const auto& N:CueKindsSeen)Names.Add(MakeShared<FJsonValueString>(N));R->SetArrayField(TEXT("cue_kinds"),Names);
        Names.Reset();for(auto N:SilkHitOverlayBases)Names.Add(MakeShared<FJsonValueString>(N.ToString()));R->SetArrayField(TEXT("hit_overlay_base_clips"),Names);
        SilkFrameTimes.Sort();if(!SilkFrameTimes.IsEmpty())R->SetNumberField(TEXT("tour_frame_p95_ms"),SilkFrameTimes[FMath::Clamp(FMath::CeilToInt(SilkFrameTimes.Num()*.95)-1,0,SilkFrameTimes.Num()-1)]);
        FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));
        FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("silkmother-route.json")));
        FFileHelper::SaveStringToFile(SilkFrameCsv,*(EvidenceDirectory/TEXT("skin-samples.csv")));
        FPlatformMisc::RequestExitWithStatus(false,Error.IsEmpty()?0:1);
    };
    if(!LoadError.IsEmpty()){Finish(LoadError);return;}
    if(!SilkRouteStage){
        if(!SilkmotherCandidate||SoloMode){Finish(TEXT("Silkmother candidate arena required"));return;}
        if(IFileManager::Get().DirectoryExists(*EvidenceDirectory)){
            // Launcher creates the directory/log; refuse only previous task evidence.
            if(IFileManager::Get().FileExists(*(EvidenceDirectory/TEXT("silkmother-route.json")))){FPlatformMisc::RequestExitWithStatus(false,1);return;}
        }
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        SilkRouteStarted=Elapsed;SilkRouteStage=1;SilkFrameCsv=TEXT("age,stage,id,clip,clip_seconds,minimum_z_cm,vertices,hit_overlay_seconds,action_state,tick,generation\n");
        for(const auto& Pair:wc::BuiltinScenarioPairs(Catalog))if(Pair.mechanic==wc::AbilityMechanic::CocoonProjectile){Formation=Pair.a.armies;Seed=int(Pair.a.seed);}
        PreparationDirty=true;if(!Start()){Finish(TEXT("Arena combat rejected"));return;}
        BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
        if(FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherCaptureAudio"))){
            UKismetSystemLibrary::ExecuteConsoleCommand(this,TEXT("au.NeverDisableSubmixes 1"));
            UAudioMixerBlueprintLibrary::StartRecordingOutput(this,100,nullptr);
        }
    }
    const double Age=Elapsed-SilkRouteStarted;UpdateCamera();
    if(SilkRouteStage<=2){
        Accumulator+=DeltaSeconds;const double Step=Catalog.rules.tickMs/1000.;
        for(int I=0;I<20&&Accumulator>=Step&&Fight&&!Fight->Result().complete;++I){Advance();BellbackControl->Tick();Accumulator-=Step;}
        UpdatePresentation(DeltaSeconds);UpdateInterfaceText();
    }
    const auto Shot=[&](const FString& Name){
        if(SilkShots.Contains(Name)||FScreenshotRequest::IsScreenshotRequested())return;
        const FString Path=EvidenceDirectory/(Name+TEXT(".png"));
        if(IFileManager::Get().FileExists(*Path))return;
        SilkShots.Add(Name);FScreenshotRequest::RequestScreenshot(Path,true,false);
        UE_LOG(LogTemp,Display,TEXT("WC_SILKMOTHER_SCREENSHOT name=%s age=%.3f tick=%d"),*Name,Age,Fight?Fight->CurrentTick():-1);
    };
    if(CurrentCueKinds.Contains(TEXT("silkmother_dense_cocoon"))&&Fight){
        for(const auto& E:Fight->Events())if(E.mechanic==wc::AbilityMechanic::CocoonProjectile&&E.effect==wc::Effect::Stun&&E.resolved>0&&
            Fight->CurrentTick()-E.tick>=6&&Fight->CurrentTick()-E.tick<=12)Shot(TEXT("confirmed-cocoon"));
    }
    if(CurrentCueKinds.Contains(TEXT("silkmother_web_projectile")))Shot(TEXT("released-web"));
    if(SilkRouteStage<=2&&Age>=(SilkRouteStage==1?22:48)){
        SilkControlMatches&=Fight->CurrentTick()==BellbackControl->CurrentTick()&&Fight->Events().size()==BellbackControl->Events().size();
        for(size_t I=0;I<Fight->Events().size()&&I<BellbackControl->Events().size();++I){
            const auto& A=Fight->Events()[I];const auto& B=BellbackControl->Events()[I];
            SilkControlMatches&=A.tick==B.tick&&A.source==B.source&&A.target==B.target&&A.action==B.action&&A.effect==B.effect&&A.resolved==B.resolved&&A.healthLoss==B.healthLoss;
        }
        Reset();++BellbackGeneration;++SilkRouteStage;
        int Bell=-1,Silk=-1;for(int I=0;I<int(Catalog.units.size());++I){if(Catalog.units[I].id=="wc_vn_shieldbearer")Bell=I;if(Catalog.units[I].id=="wc_vn_soul_jailer")Silk=I;}
        Formation[0].clear();Formation[1].clear();NextId=1;
        for(int Side=0;Side<2;++Side)for(int I=0;I<(SilkRouteStage==2?4:10);++I){
            wc::OwnedUnit U;U.id=NextId++;U.definition=I%2?Bell:Silk;U.star=1;U.onBoard=true;U.cell={I%8,I/8};U.facing=wc::Facing::Forward;Formation[Side].push_back(U);
        }
        PreparationDirty=true;UpdatePresentation(0);
        if(SilkRouteStage==2){if(!Start()){Finish(TEXT("Second arena combat rejected"));return;}BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);}
    }
    if(SilkRouteStage==3){
        static const FName Clips[]={TEXT("Idle"),TEXT("Move"),TEXT("TurnLeft"),TEXT("TurnRight"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory")};
        static const float Lengths[]={2.4f,.8f,1.2f,1.2f,.8f,1.3f,.4f,2,2};
        const int Index=FMath::Clamp(int((Age-48)/3),0,8);const float Local=FMath::Fmod(float(Age-48),3.f);
        int Count=0;for(auto& Pair:Pieces){auto& V=Pair.Value;if(!V.Actor.IsValid())continue;
            V.Actor->SetActorLocation(FVector((Count%5-2)*290,(Count/5-1.5f)*340,0));++Count;
            FWCBellbackFrame F;F.Generation=BellbackGeneration;F.Id=Pair.Key;F.Side=V.Side;F.Facing=0;F.Clock=Age;F.DeltaSeconds=DeltaSeconds;F.AllowSound=false;
            F.ReviewClip=Clips[Index];F.ReviewSeconds=FMath::Fmod(Local,Lengths[Index]);
            if(V.Silkmother)V.Silkmother->Present(F);else if(V.Bellback)V.Bellback->Present(F);
        }
        if(Local>1)Shot(TEXT("tour-")+Clips[Index].ToString());
        if(!FScreenshotRequest::IsScreenshotRequested()&&Local>.4&&Local<.9)SilkFrameTimes.Add(DeltaSeconds*1000);
    }
    int Visible=0;const bool Sample=Age-SilkLastSurface>=.3&&Age>1&&SilkRouteStage<4;
    for(const auto& Pair:Pieces){const auto& V=Pair.Value;if(V.Bellback||V.Silkmother)++Visible;if(!V.Silkmother)continue;
        const FName Clip=V.Silkmother->ClipName();SilkClipsSeen.Add(Clip);
        if(V.Silkmother->HasHitOverlay()){
            ++SilkHitOverlaySamples;SilkHitOverlayBases.Add(Clip);
            if(V.Silkmother->HitOverlaySeconds()>.04f)Shot(TEXT("hit-overlay-")+Clip.ToString());
        }
        if(Clip==TEXT("Move")&&SilkRouteStage==2)Shot(TEXT("spider-moving"));
        if(Sample&&FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherContact"))){
            auto* M=V.Silkmother->GetMesh();TArray<FFinalSkinVertex> Vertices;M->GetCPUSkinnedVertices(Vertices,0);
            double Min=MAX_dbl;for(const auto& P:Vertices)Min=FMath::Min(Min,M->GetComponentTransform().TransformPosition(FVector(P.Position)).Z);
            SilkMinimumZ=FMath::Min(SilkMinimumZ,Min);++SilkFloorSamples;
            int State=-1;const int Tick=Fight?Fight->CurrentTick():-1;
            if(Fight)for(const auto& Unit:Fight->Units())if(Unit.id==Pair.Key){State=int(Unit.state);break;}
            SilkFrameCsv+=FString::Printf(TEXT("%.5f,%d,%llu,%s,%.5f,%.7f,%d,%.5f,%d,%d,%llu\n"),Age,SilkRouteStage,Pair.Key,*Clip.ToString(),V.Silkmother->ClipSeconds(),Min,Vertices.Num(),
                V.Silkmother->HasHitOverlay()?V.Silkmother->HitOverlaySeconds():-1.f,State,Tick,BellbackGeneration);
        }
    }
    if(Sample)SilkLastSurface=Age;SilkPeakUnits=FMath::Max(SilkPeakUnits,Visible);
    if(Age>=76&&SilkRouteStage==3){
        SilkRouteStage=4;
        if(FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherCaptureAudio")))
            UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("silkmother-master-submix"),FPaths::ConvertRelativePathToFull(EvidenceDirectory),nullptr,nullptr);
    }
    if(Age>=84){
        const bool ContactFailed=SilkFloorSamples&&SilkMinimumZ<5.95;
        const bool MissingRequestedContact=FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherContact"))&&SilkFloorSamples==0;
        const bool MissingRevisionOverlay=FParse::Param(FCommandLine::Get(),TEXT("WCSilkmotherMotionRevision20260930"))&&
            (SilkHitOverlaySamples==0||!SilkHitOverlayBases.Contains(TEXT("Attack")));
        Finish(!SilkControlMatches?TEXT("Combat mismatch"):CueOverflow?TEXT("Effect pool overflow"):ContactFailed?TEXT("Skin penetrates board"):
            MissingRequestedContact?TEXT("Requested contact samples missing"):MissingRevisionOverlay?TEXT("Damage-overlay attack coverage incomplete"):
            SilkClipsSeen.Num()!=9||SilkPeakUnits!=20||!SilkShots.Contains(TEXT("confirmed-cocoon"))?TEXT("Coverage incomplete"):FString());
    }
}
