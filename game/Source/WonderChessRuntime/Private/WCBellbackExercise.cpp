#include "WCVNextLab.h"
#include "WCBellbackPresentation.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Dom/JsonObject.h"
#include "DynamicRHI.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/SkeletalMesh.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "Misc/SecureHash.h"
#include "RHI.h"
#include "RHIGlobals.h"
#include "RenderTimer.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include <algorithm>

namespace {
FString CombatSignature(const wc::Combat& C){
    FString S;
    for(const auto& E:C.Events())S+=FString::Printf(TEXT("%d,%llu,%llu,%llu,%d,%lld,%lld,%lld,%lld,%d,%d,%d,%llu,%lld;"),E.tick,E.source,E.target,E.action,int(E.effect),E.requested,E.resolved,E.absorbed,E.healthLoss,E.cell.column,E.cell.row,int(E.mechanic),E.guardedBy,E.prevented);
    for(const auto& U:C.Units())S+=FString::Printf(TEXT("%llu,%lld,%lld,%d,%d,%d,%d,%d;"),U.id,U.health,U.shield,U.cell.column,U.cell.row,int(U.state),int(U.facing),U.relic);
    const auto& R=C.Result();S+=FString::Printf(TEXT("%d,%d,%d,%d,%d"),R.winner,R.timeout,R.ticks,R.survivors[0],R.survivors[1]);
    const FTCHARToUTF8 Utf8(*S);return FSHA1::HashBuffer(Utf8.Get(),Utf8.Length()).ToString();
}
double Percentile(TArray<double> Values,double Q){if(Values.IsEmpty())return 0;Values.Sort();return Values[FMath::Clamp(FMath::CeilToInt(Q*Values.Num())-1,0,Values.Num()-1)];}
}

bool AWCVNextLab::ProbeBellbackSelection()
{
    BellbackSelectionProbe=MakeShared<FJsonObject>();auto& R=BellbackSelectionProbe;
    R->SetStringField(TEXT("boundary"),TEXT("Synthetic world rays through the same BoardRayClick dispatch as mouse deprojection. Loaded skeletal asset and live component transforms; not real mouse, Slate routing, pixel-accurate silhouette or human usability evidence."));
    if(Pieces.Num()!=1||Formation[0].size()!=1){R->SetBoolField(TEXT("passed"),false);return false;}
    auto& View=Pieces.CreateIterator().Value();
    if(!View.Bellback||!View.Actor.IsValid()||!View.Bellback->GetMesh()->GetSkeletalMeshAsset()){R->SetBoolField(TEXT("passed"),false);return false;}
    auto* Mesh=View.Bellback->GetMesh();auto* Actor=View.Actor.Get();
    const FBox Box=Mesh->GetSkeletalMeshAsset()->GetImportedBounds().GetBox();
    const FVector Center=Box.GetCenter(),Extent=Box.GetExtent();
    const FTransform Original=Actor->GetActorTransform();
    const uint64 Expected=Formation[0][0].id;const wc::Cell ExpectedCell=wc::EncounterCell(Formation[0][0].cell,0,Catalog.rules);
    R->SetStringField(TEXT("mesh"),Mesh->GetSkeletalMeshAsset()->GetPathName());
    R->SetStringField(TEXT("imported_bounds_min"),Box.Min.ToString());R->SetStringField(TEXT("imported_bounds_max"),Box.Max.ToString());
    R->SetNumberField(TEXT("single_scene_unit_id"),double(Expected));
    bool Passed=true;TArray<TSharedPtr<FJsonValue>> Cases;
    for(double Yaw:{0.,45.,90.,135.}){
        Actor->SetActorRotation(FRotator(0,Yaw,0));const FTransform Transform=Mesh->GetComponentTransform();
        const FVector LocalOrigin=Center-FVector(0,Extent.Y+100,0);
        const FVector Origin=Transform.TransformPosition(LocalOrigin);
        const FVector Direction=Transform.TransformVector(FVector(0,1,0)).GetSafeNormal();
        const FVector Entry=Transform.TransformPosition(Center-FVector(0,Extent.Y,0));
        double Distance=0;uint64 Id=0;wc::Cell Cell{-1,-1};
        const bool Geometric=RayImportedBounds(Box,Transform,Origin,Direction,Distance)&&FMath::Abs(Distance-FVector::Distance(Origin,Entry))<.01;
        const bool SceneHit=BellbackRayHit(Origin,Direction,Id,Cell)&&Id==Expected&&Cell==ExpectedCell;
        Selected=0;const bool SelectedCorrect=BoardRayClick(Origin,Direction,false)&&Selected==Expected;
        const FVector MissOrigin=Transform.TransformPosition(Center+FVector(Extent.X+10,-Extent.Y-100,0));
        double MissDistance=0;const bool Miss=!RayImportedBounds(Box,Transform,MissOrigin,Direction,MissDistance)&&!BellbackRayHit(MissOrigin,Direction,Id,Cell);
        // A farther copy of the actual imported box must have a larger parameter.
        FTransform Farther=Transform;Farther.AddToTranslation(Direction*1000);
        double FarDistance=0;const bool Ordered=RayImportedBounds(Box,Farther,Origin,Direction,FarDistance)&&FarDistance>Distance+999;
        const bool ThisPass=Geometric&&SceneHit&&SelectedCorrect&&Miss&&Ordered;Passed&=ThisPass;
        auto C=MakeShared<FJsonObject>();C->SetNumberField(TEXT("actor_yaw"),Yaw);C->SetNumberField(TEXT("entry_distance_cm"),Distance);
        C->SetStringField(TEXT("component_transform"),Transform.ToHumanReadableString());
        C->SetBoolField(TEXT("entry_distance_matches_transformed_face"),Geometric);C->SetBoolField(TEXT("single_scene_hit_and_cell"),SceneHit);
        C->SetBoolField(TEXT("dispatch_selected_exact_id"),SelectedCorrect);C->SetBoolField(TEXT("parallel_outside_box_misses"),Miss);
        C->SetBoolField(TEXT("farther_transformed_box_orders_after_near_box"),Ordered);Cases.Add(MakeShared<FJsonValueObject>(C));
    }
    Actor->SetActorTransform(Original);
    const FVector Upper=Mesh->GetComponentTransform().TransformPosition(Center+FVector(0,0,Extent.Z*.6));
    const FVector Direction=FVector(0,1,-.5).GetSafeNormal(),Origin=Upper-Direction*1000;
    const FVector Ground=Origin-Direction*(Origin.Z/Direction.Z);
    const wc::Cell GroundCell{FMath::FloorToInt((Ground.X+800)/200),FMath::FloorToInt((800-Ground.Y)/200)};
    Selected=0;const bool TallClick=GroundCell!=ExpectedCell&&BoardRayClick(Origin,Direction,false)&&Selected==Expected;
    R->SetBoolField(TEXT("upper_body_selects_creature_despite_ground_ray_hitting_different_cell"),TallClick);
    R->SetNumberField(TEXT("old_ground_column"),GroundCell.column);R->SetNumberField(TEXT("old_ground_row"),GroundCell.row);
    R->SetArrayField(TEXT("rotated_asset_cases"),Cases);Passed&=TallClick;
    // An empty board cell retains the existing preparation placement authority.
    const wc::Cell Empty{0,0};Selected=0;
    const bool Fallback=BoardRayClick(Position(Empty)+FVector(0,0,1000),FVector(0,0,-1),false)&&SelectedPiece()&&SelectedPiece()->cell==Empty;
    R->SetBoolField(TEXT("empty_cell_ground_fallback_uses_preparation_handler"),Fallback);Passed&=Fallback;
    bool NearestScene=false;
    if(Fallback){
        const uint64 SecondId=Selected;UpdatePresentation(0);
        auto* FirstActor=Pieces.FindChecked(Expected).Actor.Get();auto* SecondActor=Pieces.FindChecked(SecondId).Actor.Get();
        const FTransform SecondOriginal=SecondActor->GetActorTransform();
        SecondActor->SetActorTransform(FirstActor->GetActorTransform());SecondActor->AddActorWorldOffset(FVector(0,400,0));
        const auto* FirstMesh=Pieces.FindChecked(Expected).Bellback->GetMesh();
        const FVector Mid=FirstMesh->GetComponentTransform().TransformPosition(Center);
        uint64 Id=0;wc::Cell Cell{-1,-1};
        const bool NearFirst=BellbackRayHit(Mid-FVector(0,1000,0),FVector(0,1,0),Id,Cell)&&Id==Expected;
        const bool NearSecond=BellbackRayHit(Mid+FVector(0,1400,0),FVector(0,-1,0),Id,Cell)&&Id==SecondId;
        NearestScene=NearFirst&&NearSecond;SecondActor->SetActorTransform(SecondOriginal);
    }
    R->SetBoolField(TEXT("two_live_components_choose_nearest_from_both_directions"),NearestScene);Passed&=NearestScene;
    // This temporary test placement is discarded before the guard fixture starts.
    R->SetBoolField(TEXT("passed"),Passed);return Passed;
}

void AWCVNextLab::QueueBellbackScreenshot(const FString& Name,double Age)
{
    if(BellbackPendingScreenshot||BellbackShotsRequested.Contains(Name)||FScreenshotRequest::IsScreenshotRequested())return;
    BellbackScreenshotPath=FPaths::ConvertRelativePathToFull(EvidenceDirectory/(Name+TEXT(".png")));
    if(IFileManager::Get().FileExists(*BellbackScreenshotPath)||IFileManager::Get().FileExists(*FPaths::ChangeExtension(BellbackScreenshotPath,TEXT("json")))){
        BellbackScreenshotFailure=true;FinishBellbackRoute(TEXT("Existing screenshot would be overwritten: ")+Name);return;
    }
    BellbackShotsRequested.Add(Name);BellbackScreenshotRequestedAt=FPlatformTime::Seconds();
    BellbackCaptureRecoveryUntil=BellbackScreenshotRequestedAt+1;
    BellbackPendingScreenshot=MakeShared<FJsonObject>();auto& R=BellbackPendingScreenshot;
    R->SetStringField(TEXT("name"),Name);R->SetStringField(TEXT("file"),BellbackScreenshotPath);
    R->SetStringField(TEXT("method"),TEXT("Native viewport PNG without Slate UI; request-state metadata, rendered asynchronously without pausing gameplay. Request-to-completion frame interval is recorded; not a claim of exact pose/tick synchronization."));
    R->SetNumberField(TEXT("requested_wall_seconds"),Age);R->SetNumberField(TEXT("requested_frame"),double(GFrameCounter));
    R->SetStringField(TEXT("requested_utc"),FDateTime::UtcNow().ToIso8601());R->SetNumberField(TEXT("route_stage"),BellbackRouteStage);
    R->SetNumberField(TEXT("combat_tick_at_request"),Fight?Fight->CurrentTick():-1);
    R->SetNumberField(TEXT("cue_meshes_at_request"),CueMeshUsed);
    R->SetBoolField(TEXT("actual_guard_cue_visible_at_request"),CurrentCueKinds.Contains(TEXT("bellback_guard")));
    CaptureBoardProjection(R.ToSharedRef());
    if(Controller){int W=0,H=0;Controller->GetViewportSize(W,H);R->SetNumberField(TEXT("viewport_width"),W);R->SetNumberField(TEXT("viewport_height"),H);}
    TArray<TSharedPtr<FJsonValue>> Units;
    for(const auto& Pair:Pieces)if(Pair.Value.Bellback){
        auto U=MakeShared<FJsonObject>();U->SetNumberField(TEXT("id"),double(Pair.Key));
        U->SetStringField(TEXT("base_clip"),Pair.Value.Bellback->ClipName().ToString());
        U->SetNumberField(TEXT("base_clip_seconds"),Pair.Value.Bellback->ClipSeconds());
        U->SetNumberField(TEXT("move_play_rate"),Pair.Value.Bellback->MoveRate());
        if(Pair.Value.Actor.IsValid()){const FVector P=Pair.Value.Actor->GetActorLocation();U->SetNumberField(TEXT("x"),P.X);U->SetNumberField(TEXT("y"),P.Y);U->SetNumberField(TEXT("z"),P.Z);}
        Units.Add(MakeShared<FJsonValueObject>(U));
    }
    R->SetArrayField(TEXT("requested_unit_states"),Units);
    BellbackScreenshotRecords.Add(MakeShared<FJsonValueObject>(R));
    FScreenshotRequest::RequestScreenshot(BellbackScreenshotPath,false,false);
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_CAPTURE_REQUEST name=%s frame=%llu age=%.3f"),*Name,GFrameCounter,Age);
}

void AWCVNextLab::PollBellbackScreenshot(double Now)
{
    if(!BellbackPendingScreenshot)return;
    const bool TimedOut=Now-BellbackScreenshotRequestedAt>15;
    if(FScreenshotRequest::IsScreenshotRequested()&&!TimedOut)return;
    const int64 Bytes=IFileManager::Get().FileSize(*BellbackScreenshotPath);
    bool ValidPng=false;int Width=0,Height=0;
    if(!TimedOut&&Bytes>=24){
        TUniquePtr<FArchive> Reader(IFileManager::Get().CreateFileReader(*BellbackScreenshotPath));
        if(Reader){uint8 Header[24]={};Reader->Serialize(Header,24);
            ValidPng=!Reader->IsError()&&Header[0]==137&&Header[1]=='P'&&Header[2]=='N'&&Header[3]=='G';
            const auto IntAt=[&](int I){return int((uint32(Header[I])<<24)|(uint32(Header[I+1])<<16)|(uint32(Header[I+2])<<8)|Header[I+3]);};
            Width=IntAt(16);Height=IntAt(20);ValidPng=ValidPng&&Width>0&&Height>0;
        }
    }
    auto& R=BellbackPendingScreenshot;
    R->SetBoolField(TEXT("saved_valid_png"),ValidPng);R->SetBoolField(TEXT("timed_out"),TimedOut);
    R->SetNumberField(TEXT("bytes"),Bytes);R->SetNumberField(TEXT("png_width"),Width);R->SetNumberField(TEXT("png_height"),Height);
    R->SetNumberField(TEXT("completed_frame"),double(GFrameCounter));R->SetNumberField(TEXT("completed_wall_seconds"),Now-BellbackRouteStarted);
    BellbackCaptureRecoveryUntil=Now+1;R->SetNumberField(TEXT("summary_exclusion_ends_wall_seconds"),BellbackCaptureRecoveryUntil-BellbackRouteStarted);
    FString Sidecar;FJsonSerializer::Serialize(R.ToSharedRef(),TJsonWriterFactory<>::Create(&Sidecar));
    const bool MetadataSaved=FFileHelper::SaveStringToFile(Sidecar,*FPaths::ChangeExtension(BellbackScreenshotPath,TEXT("json")));
    BellbackScreenshotFailure|=!ValidPng||!MetadataSaved;BellbackPendingScreenshot.Reset();
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_CAPTURE_COMPLETE valid=%d file=%s"),ValidPng,*BellbackScreenshotPath);
}

void AWCVNextLab::TickBellbackRoute(float DeltaSeconds)
{
    if(BellbackRouteDone)return;
    BellbackAudioRequested=FParse::Param(FCommandLine::Get(),TEXT("WCBellbackCaptureAudio"));
    if(BellbackAudioExportPending){PollBellbackAudioCapture(FPlatformTime::Seconds());return;}
    if(!LoadError.IsEmpty()){FinishBellbackRoute(LoadError);return;}
    const double Now=FPlatformTime::Seconds();
    PollBellbackScreenshot(Now);
    if(!BellbackRouteStage){
        if(!BellbackCandidate||SoloMode){FinishBellbackRoute(TEXT("Candidate laboratory required"));return;}
        for(const TCHAR* Flag:{TEXT("NullRHI"),TEXT("benchmark"),TEXT("UseFixedTimeStep"),TEXT("nosound")})
            if(FParse::Param(FCommandLine::Get(),Flag)){FinishBellbackRoute(FString(TEXT("Route requires rendered normal-time audiovisual execution; conflicting flag: "))+Flag);return;}
        const FString Report=EvidenceDirectory/TEXT("bellback-route.json");
        if(IFileManager::Get().FileExists(*Report)){UE_LOG(LogTemp,Error,TEXT("WC_BELLBACK_ROUTE existing evidence refused"));BellbackRouteDone=true;FPlatformMisc::RequestExitWithStatus(false,1);return;}
        IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
        BellbackRouteStarted=BellbackLastWall=Now;BellbackRouteStage=1;BellbackFrameCsv=TEXT("frame,wall_seconds,workload,frame_ms,game_ms,render_ms,gpu_ms,visible_skeletons,cue_meshes,lod0,lod1,lod2,sounds,visible_triangles,visible_vertices,visible_bones,material_sections,ik_corrected_legs,ik_max_correction_source_cm,capture_affected\n");
        FString AudioFailure;if(!BeginBellbackAudioCapture(AudioFailure)){FinishBellbackRoute(AudioFailure);return;}
        Formation[0].clear();Formation[1].clear();NextId=1;
        int Bell=-1,Root=-1,Prism=-1;
        for(int I=0;I<int(Catalog.units.size());++I){const auto& Id=Catalog.units[I].id;if(Id=="wc_vn_shieldbearer")Bell=I;if(Id=="wc_vn_grove_druid")Root=I;if(Id=="wc_vn_prism_scholar")Prism=I;}
        if(Bell<0||Root<0||Prism<0){FinishBellbackRoute(TEXT("Required pilot IDs missing"));return;}
        wc::OwnedUnit SelectionUnit;SelectionUnit.id=NextId++;SelectionUnit.definition=Bell;SelectionUnit.star=1;SelectionUnit.onBoard=true;SelectionUnit.cell={3,2};SelectionUnit.facing=wc::Facing::Forward;
        Formation[0].push_back(SelectionUnit);PreparationDirty=true;UpdatePresentation(0);
        if(!ProbeBellbackSelection()){FinishBellbackRoute(TEXT("Bellback imported-bounds selection probe failed"));return;}
        Selected=0;
        // Existing F01 fixture exercises the exact directional guard mechanic.
        const auto Guard=wc::BuiltinScenarioPairs(Catalog).front().a;
        Formation=Guard.armies;Seed=int(Guard.seed);
        PreparationDirty=true;
        if(!Start()){FinishBellbackRoute(TEXT("Combat fixture refused"));return;}
        BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
        UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_ROUTE_BEGIN route=%s resolution=%s"),BellbackPerformance?TEXT("performance"):TEXT("exercise"),GEngine&&GEngine->GameViewport?*GEngine->GameViewport->Viewport->GetSizeXY().ToString():TEXT("unavailable"));
    }
    const double Age=Now-BellbackRouteStarted;
    UpdateCamera();
    if(BellbackRouteStage<=2){
        Accumulator+=DeltaSeconds;const double Step=Catalog.rules.tickMs/1000.;
        for(int N=0;Accumulator>=Step&&N<20&&Fight&&!Fight->Result().complete;++N){Advance();BellbackControl->Tick();Accumulator-=Step;}
        UpdatePresentation(DeltaSeconds);UpdateInterfaceText();
        if(BellbackSelectionProbe&&!BellbackSelectionProbe->HasField(TEXT("combat_exact_visible_id"))){
            bool Exact=false;
            for(const auto& Pair:Pieces)if(Pair.Value.Bellback&&Pair.Value.Actor.IsValid()){
                const auto* Mesh=Pair.Value.Bellback->GetMesh();
                const FVector Center=Mesh->GetComponentTransform().TransformPosition(Mesh->GetSkeletalMeshAsset()->GetImportedBounds().Origin);
                const FVector Origin=Center+FVector(0,0,1000),Direction(0,0,-1);uint64 Id=0;wc::Cell Cell{-1,-1};
                if(BellbackRayHit(Origin,Direction,Id,Cell)){
                    const FString Before=CombatSignature(*Fight);Selected=0;
                    Exact=BoardRayClick(Origin,Direction,false)&&Selected==Id&&CombatSignature(*Fight)==Before;
                    const bool RemovalLocked=!BoardRayClick(Origin,Direction,true)&&Selected==Id&&CombatSignature(*Fight)==Before;
                    BellbackSelectionProbe->SetBoolField(TEXT("combat_remove_still_locked"),RemovalLocked);Exact&=RemovalLocked;
                    BellbackSelectionProbe->SetNumberField(TEXT("combat_selected_id"),double(Selected));break;
                }
            }
            BellbackSelectionProbe->SetBoolField(TEXT("combat_exact_visible_id"),Exact);Selected=0;
            if(!Exact){FinishBellbackRoute(TEXT("Bellback exact combat selection probe failed"));return;}
        }
        if(CombatInvariantFailed){FinishBellbackRoute(TEXT("Combat invariant failed"));return;}
        if(Age>=(BellbackRouteStage==1?35:70)){
            BellbackActualSignature+=CombatSignature(*Fight)+TEXT(";");BellbackControlSignature+=CombatSignature(*BellbackControl)+TEXT(";");
            for(const auto& E:Fight->Events()){if(E.guardedBy&&E.prevented>0)++BellbackObservedGuard;if(E.healthLoss>0)++BellbackObservedDamage;}
            if(BellbackActualSignature!=BellbackControlSignature){FinishBellbackRoute(TEXT("Presentation/control combat signatures differ"));return;}
            Reset();++BellbackGeneration;
            int Bell=-1,Root=-1,Prism=-1;
            for(int I=0;I<int(Catalog.units.size());++I){const auto& Id=Catalog.units[I].id;if(Id=="wc_vn_shieldbearer")Bell=I;if(Id=="wc_vn_grove_druid")Root=I;if(Id=="wc_vn_prism_scholar")Prism=I;}
            if(BellbackRouteStage==1){
                BellbackRouteStage=2;Formation[0].clear();Formation[1].clear();NextId=1;
                for(int Side=0;Side<2;++Side)for(int I=0;I<10;++I){
                    wc::OwnedUnit U;U.id=NextId++;U.definition=I<6?Bell:I<8?Root:Prism;U.star=1;U.onBoard=true;
                    U.cell={I<6?I+1:(I-6)*2+1,I<6?3:2};U.facing=wc::Facing::Forward;Formation[Side].push_back(U);
                }
                if(!Start()){FinishBellbackRoute(TEXT("Twenty-unit mixed combat fixture refused"));return;}
                BellbackControl=std::make_unique<wc::Combat>(Catalog,Formation[0],Formation[1],uint64(Seed),1);
            }else{
                BellbackRouteStage=3;
                for(auto& Team:Formation)for(auto& U:Team)U.definition=Bell;
                UpdatePresentation(0);
            }
        }
    }
    if(BellbackRouteStage==3){
        // Synthetic animation load, explicitly distinct from the authoritative battle above.
        // All twenty skeletons stay visible; no health or simulation state is rewritten.
        static const FName Names[]={TEXT("Idle"),TEXT("Move"),TEXT("TurnLeft"),TEXT("TurnRight"),TEXT("Attack"),TEXT("Active"),TEXT("Hit"),TEXT("Defeat"),TEXT("Victory")};
        static const float Lengths[]={3,2.4f,.6f,.6f,.8f,1.2f,14.f/30,1.6f,2.4f};
        const double TourAge=Age-70;
        for(auto& Pair:Pieces){auto& View=Pair.Value;if(!View.Bellback||!View.Actor.IsValid())continue;
            const int Index=FMath::Clamp(int(TourAge/3),0,8);
            const float Local=FMath::Fmod(float(TourAge),3.f);
            FWCBellbackFrame F;F.Generation=BellbackGeneration;F.Id=Pair.Key;F.Side=View.Side;F.Facing=View.Side?2:0;
            F.Clock=Age;F.DeltaSeconds=DeltaSeconds;F.AllowSound=false;F.ReviewClip=Names[Index];F.ReviewSeconds=FMath::Fmod(Local,Lengths[Index]);
            View.Bellback->Present(F);
        }
        UpdateInterfaceText();
        if(Age>=97){
            if(BellbackPerformance){BellbackRouteStage=4;++BellbackGeneration;}
            else{FinishBellbackRoute();return;}
        }
    }
    if(BellbackRouteStage==4){
        // Worst-case cosmetic load: twenty independently skinned moving actors,
        // continuous pooled guard/impact effects and shared-concurrency sounds.
        // No synthetic event is inserted into the authoritative combat stream.
        CueMeshUsed=CueTextUsed=0;int Index=0;
        const double StressAge=Age-97;
        const float Phase=FMath::Fmod(float(StressAge),1.6f);
        const float Offset=Phase<.8f?-80+Phase*200:80-(Phase-.8f)*200;
        for(auto& Pair:Pieces){auto& View=Pair.Value;if(!View.Bellback||!View.Actor.IsValid())continue;
            View.Actor->SetActorLocation(FVector((Index%5-2)*280+Offset,(Index/5-1.5f)*320,0));
            FWCBellbackFrame F;F.Generation=BellbackGeneration;F.Id=Pair.Key;F.Side=View.Side;F.Facing=View.Side?2:0;
            F.Clock=Age;F.DeltaSeconds=DeltaSeconds;F.AllowSound=true;F.ReviewClip=TEXT("Move");F.ReviewTravel=true;
            F.ReviewEffectSerial=FMath::FloorToInt(StressAge*.75+Index*.1);View.Bellback->Present(F);
            const float Pulse=FMath::Fmod(float(StressAge)+Index*.07f,.8f)/.8f;
            const FVector Bell=View.Bellback->CueLocation(TEXT("bell")),Mouth=View.Bellback->CueLocation(TEXT("mouth"));
            CueRing(Bell,24+Pulse*50,FLinearColor(.85f,.51f,.08f),3*(1-Pulse)+1);
            for(int Ray=0;Ray<4;++Ray){const float Angle=Ray*UE_HALF_PI;const FVector D(0,FMath::Cos(Angle),FMath::Sin(Angle));CueLine(Mouth+D*(7+Pulse*15),Mouth+D*(18+Pulse*28),FLinearColor(.85f,.25f,.08f),3);}
            ++Index;
        }
        for(int I=CueMeshUsed;I<CueMeshes.Num();++I)CueMeshes[I]->SetVisibility(false);
        for(int I=CueTextUsed;I<CueTexts.Num();++I)CueTexts[I]->SetVisibility(false);
        PeakCueMeshes=FMath::Max(PeakCueMeshes,CueMeshUsed);
        if(Age>=127){FinishBellbackRoute();return;}
    }
    int Visible=0,Sounds=0,Lods[3]={0,0,0},Triangles=0,Vertices=0,Bones=0,Sections=0,CorrectedLegs=0;
    float MaximumCorrection=0;
    for(const auto& Pair:Pieces)if(Pair.Value.Bellback){
        auto* B=Pair.Value.Bellback;BellbackSeenClips.Append(B->SeenClips());Sounds+=B->SoundCount();
        if(auto* M=B->GetMesh();M&&M->IsVisible()&&!M->GetOwner()->IsHidden()){
            ++Visible;++Lods[FMath::Clamp(M->GetPredictedLODLevel(),0,2)];Bones+=M->GetNumBones();
            if(const auto* A=Cast<UWCBellbackAnimInstance>(M->GetAnimInstance())){CorrectedLegs+=A->CorrectedLegs;MaximumCorrection=FMath::Max(MaximumCorrection,A->MaximumFootCorrection);}
            if(const auto* Data=M->GetSkeletalMeshRenderData();Data&&Data->LODRenderData.IsValidIndex(M->GetPredictedLODLevel())){
                const auto& LOD=Data->LODRenderData[M->GetPredictedLODLevel()];Vertices+=LOD.GetNumVertices();
                for(const auto& Section:LOD.RenderSections)if(!Section.bDisabled){Triangles+=Section.NumTriangles;++Sections;}
            }
        }
    }
    BellbackPeakUnits=FMath::Max(BellbackPeakUnits,Visible);BellbackSoundCount=FMath::Max(BellbackSoundCount,Sounds);
    if(BellbackRouteStage==1&&CurrentCueKinds.Contains(TEXT("bellback_guard")))QueueBellbackScreenshot(TEXT("guard-event"),Age);
    if(BellbackRouteStage==2&&Age>=38)QueueBellbackScreenshot(TEXT("mixed-combat"),Age);
    if(BellbackRouteStage==3){
        if(Age>=74&&Age<76)QueueBellbackScreenshot(TEXT("twenty-move"),Age);
        if(Age>=85.4&&Age<87)QueueBellbackScreenshot(TEXT("twenty-active"),Age);
        if(Age>=92.1&&Age<93.8)QueueBellbackScreenshot(TEXT("twenty-defeat"),Age);
        if(Age>=95.1&&Age<96.8)QueueBellbackScreenshot(TEXT("twenty-victory"),Age);
    }
    if(BellbackRouteStage==4&&Age>=109)QueueBellbackScreenshot(TEXT("twenty-moving-effects"),Age);
    if(BellbackRouteDone)return;
    const bool CaptureAffected=BellbackPendingScreenshot.IsValid()||Now<=BellbackCaptureRecoveryUntil;
    if(CaptureAffected)++BellbackCaptureExcludedFrames;
    const double WallMs=(Now-BellbackLastWall)*1000;BellbackLastWall=Now;
    if(Age>=5){
        const uint32 GPUCycles=GDynamicRHI?RHIGetGPUFrameCycles():0;
        const FString GPU=GPUCycles?FString::Printf(TEXT("%.5f"),FPlatformTime::ToMilliseconds(GPUCycles)):FString();
        BellbackFrameCsv+=FString::Printf(TEXT("%llu,%.6f,%s,%.5f,%.5f,%.5f,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%.5f,%d\n"),GFrameCounter,Age,
            BellbackRouteStage==1?TEXT("authoritative_guard_fixture"):BellbackRouteStage==2?TEXT("authoritative_mixed_twenty_start"):BellbackRouteStage==3?TEXT("synthetic_twenty_clip_tour"):TEXT("synthetic_twenty_moving_with_effects"),WallMs,
            FPlatformTime::ToMilliseconds(GGameThreadTime),FPlatformTime::ToMilliseconds(GRenderThreadTime),*GPU,Visible,CueMeshUsed,Lods[0],Lods[1],Lods[2],Sounds,Triangles,Vertices,Bones,Sections,CorrectedLegs,MaximumCorrection,CaptureAffected?1:0);
        if(BellbackRouteStage==(BellbackPerformance?4:3)&&Visible==20&&!CaptureAffected)BellbackFrameTimes.Add(WallMs);
    }
}

void AWCVNextLab::FinishBellbackRoute(const FString& Failure)
{
    if(BellbackRouteDone)return;
    if(!FinishBellbackAudioCapture(Failure))return;
    BellbackRouteDone=true;
    if(IFileManager::Get().FileExists(*(EvidenceDirectory/TEXT("bellback-route.json")))){
        UE_LOG(LogTemp,Error,TEXT("WC_BELLBACK_ROUTE refusing to overwrite existing report"));FPlatformMisc::RequestExitWithStatus(false,1);return;
    }
    FString Error=Failure.IsEmpty()?BellbackAudioFailure:Failure;
    if(Error.IsEmpty()&&(BellbackActualSignature.IsEmpty()||BellbackActualSignature!=BellbackControlSignature))Error=TEXT("Missing or mismatched control combat signature");
    if(Error.IsEmpty()&&(BellbackPeakUnits!=20||BellbackSeenClips.Num()!=9||BellbackObservedGuard==0||BellbackObservedDamage==0))Error=TEXT("Required clip/20-unit/actual guard/damage coverage incomplete");
    if(Error.IsEmpty()&&BellbackFrameTimes.Num()<120)Error=TEXT("Insufficient twenty-unit rendered frame samples");
    if(Error.IsEmpty()&&(BellbackScreenshotFailure||BellbackPendingScreenshot.IsValid()||BellbackScreenshotRecords.Num()!=(BellbackPerformance?7:6)))Error=TEXT("Required route screenshots incomplete or invalid");
    if(Error.IsEmpty()&&(!BellbackSelectionProbe||!BellbackSelectionProbe->GetBoolField(TEXT("passed"))||!BellbackSelectionProbe->GetBoolField(TEXT("combat_exact_visible_id"))))Error=TEXT("Selection probe incomplete or failed");
    auto R=MakeShared<FJsonObject>();
    R->SetStringField(TEXT("status"),Error.IsEmpty()?TEXT("PASS_EXECUTION_ONLY"):TEXT("FAIL"));R->SetStringField(TEXT("failure"),Error);
    R->SetStringField(TEXT("route"),BellbackPerformance?TEXT("performance"):TEXT("exercise"));
    R->SetBoolField(TEXT("audio_capture_requested"),BellbackAudioRequested);
    R->SetBoolField(TEXT("timing_eligible_as_primary_performance"),!BellbackAudioRequested);
    R->SetStringField(TEXT("audio_capture_timing_policy"),TEXT("Optional master-submix recording is a separate audio diagnostic run. Its frame timings must not replace the unrecorded primary performance run. Export waiting happens after route sampling ends."));
    if(BellbackAudioMetadata)R->SetObjectField(TEXT("audio_capture"),BellbackAudioMetadata);
    if(BellbackSelectionProbe)R->SetObjectField(TEXT("selection_probe"),BellbackSelectionProbe);
    R->SetStringField(TEXT("boundary"),TEXT("Real battle signatures compare presentation-enabled and independent control simulations at the same observed tick. Twenty-unit clip tour and moving/effect stress are synthetic cosmetic workloads, not twenty surviving combatants. Synthetic rings, impacts and sounds never enter simulation. Timing describes this route/hardware only; no human visual/audio/release approval."));
    R->SetStringField(TEXT("twenty_unit_summary_workload"),BellbackPerformance?TEXT("synthetic_twenty_moving_with_effects at 200 world cm/s; 30 seconds"):TEXT("synthetic_twenty_clip_tour; 27 seconds"));
    R->SetNumberField(TEXT("peak_cue_meshes"),PeakCueMeshes);
    R->SetArrayField(TEXT("screenshots"),BellbackScreenshotRecords);
    R->SetNumberField(TEXT("capture_affected_frames_retained_in_csv"),BellbackCaptureExcludedFrames);
    R->SetStringField(TEXT("capture_timing_policy"),TEXT("CSV retains every sampled row. capture_affected=1 marks screenshot request through processed-file verification plus one second of recovery. Twenty-unit percentile summaries exclude these rows; screenshot work never pauses simulation."));
    R->SetStringField(TEXT("actual_signature"),BellbackActualSignature);R->SetStringField(TEXT("control_signature"),BellbackControlSignature);
    R->SetStringField(TEXT("cpu"),FPlatformMisc::GetCPUBrand());R->SetStringField(TEXT("gpu"),GRHIAdapterName);
    R->SetStringField(TEXT("command_line"),FCommandLine::Get());R->SetStringField(TEXT("catalog_digest"),UTF8_TO_TCHAR(Catalog.contentDigest.c_str()));
    R->SetNumberField(TEXT("seed"),Seed);R->SetNumberField(TEXT("peak_visible_skeletons"),BellbackPeakUnits);
    R->SetNumberField(TEXT("observed_guard_events"),BellbackObservedGuard);R->SetNumberField(TEXT("observed_health_damage_events"),BellbackObservedDamage);
    R->SetNumberField(TEXT("sound_triggers"),BellbackSoundCount);R->SetNumberField(TEXT("twenty_unit_frame_samples"),BellbackFrameTimes.Num());
    R->SetNumberField(TEXT("twenty_unit_frame_p50_ms"),Percentile(BellbackFrameTimes,.5));R->SetNumberField(TEXT("twenty_unit_frame_p95_ms"),Percentile(BellbackFrameTimes,.95));R->SetNumberField(TEXT("twenty_unit_frame_p99_ms"),Percentile(BellbackFrameTimes,.99));
    R->SetStringField(TEXT("gpu_timing"),TEXT("RHIGetGPUFrameCycles; blank CSV fields mean unavailable"));
    TArray<TSharedPtr<FJsonValue>> Names;for(FName N:BellbackSeenClips)Names.Add(MakeShared<FJsonValueString>(N.ToString()));R->SetArrayField(TEXT("sampled_clips"),Names);
    if(Controller){int W=0,H=0;Controller->GetViewportSize(W,H);R->SetNumberField(TEXT("viewport_width"),W);R->SetNumberField(TEXT("viewport_height"),H);}
    FString Json;FJsonSerializer::Serialize(R, TJsonWriterFactory<>::Create(&Json));
    IFileManager::Get().MakeDirectory(*EvidenceDirectory,true);
    const bool Written=FFileHelper::SaveStringToFile(Json,*(EvidenceDirectory/TEXT("bellback-route.json")))&&FFileHelper::SaveStringToFile(BellbackFrameCsv,*(EvidenceDirectory/TEXT("bellback-frames.csv")));
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_ROUTE_END status=%s reason=%s written=%d"),Error.IsEmpty()?TEXT("PASS_EXECUTION_ONLY"):TEXT("FAIL"),*Error,Written);
    FPlatformMisc::RequestExitWithStatus(false,Error.IsEmpty()&&Written?0:1);
}
