#include "WCVNextLab.h"
#include "AudioDeviceManager.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"

namespace {
constexpr double ExportTimeoutSeconds=30.;
constexpr double StableFileSeconds=.25;

struct FRecordedWaveInfo {
    int64 Bytes=0,DataBytes=0;
    uint16 Channels=0,Bits=0,BlockAlign=0;
    uint32 SampleRate=0;
};

// Read only the RIFF/chunk headers, not the entire recording on the game thread.
// An exact RIFF length and bounded chunks distinguish a completed asynchronous
// export from a file whose header exists while its audio data is still writing.
bool ReadCompletedWave(const FString& Path,FRecordedWaveInfo& Info)
{
    TUniquePtr<FArchive> Reader(IFileManager::Get().CreateFileReader(*Path,FILEREAD_Silent));
    if(!Reader)return false;
    Info.Bytes=Reader->TotalSize();
    if(Info.Bytes<44)return false;
    const auto LE16=[](const uint8* P){return uint16(uint16(P[0])|(uint16(P[1])<<8));};
    const auto LE32=[](const uint8* P){return uint32(P[0])|(uint32(P[1])<<8)|(uint32(P[2])<<16)|(uint32(P[3])<<24);};
    uint8 Header[12]={};Reader->Serialize(Header,12);
    if(Reader->IsError()||FMemory::Memcmp(Header,"RIFF",4)||FMemory::Memcmp(Header+8,"WAVE",4))return false;
    const int64 DeclaredBytes=int64(LE32(Header+4))+8;
    if(DeclaredBytes!=Info.Bytes)return false;
    bool HasFormat=false,HasData=false;
    int64 Position=12;int Chunks=0;
    while(Position+8<=DeclaredBytes&&++Chunks<=128){
        Reader->Seek(Position);uint8 Chunk[8]={};Reader->Serialize(Chunk,8);
        if(Reader->IsError())return false;
        const int64 Size=LE32(Chunk+4),Payload=Position+8,Next=Payload+Size+(Size&1);
        if(Next>DeclaredBytes)return false;
        if(!FMemory::Memcmp(Chunk,"fmt ",4)){
            if(Size<16||HasFormat)return false;
            uint8 Format[16]={};Reader->Serialize(Format,16);
            if(Reader->IsError()||LE16(Format)!=1)return false; // Engine writer exports PCM16.
            Info.Channels=LE16(Format+2);Info.SampleRate=LE32(Format+4);
            Info.BlockAlign=LE16(Format+12);Info.Bits=LE16(Format+14);
            if(!Info.Channels||Info.Channels>32||Info.Bits!=16||Info.SampleRate<8000||Info.SampleRate>384000||
               Info.BlockAlign!=Info.Channels*2||LE32(Format+8)!=Info.SampleRate*Info.BlockAlign)return false;
            HasFormat=true;
        }else if(!FMemory::Memcmp(Chunk,"data",4)){
            if(HasData||Size<=0)return false;
            Info.DataBytes=Size;HasData=true;
        }
        Position=Next;
    }
    return !Reader->IsError()&&Position==DeclaredBytes&&HasFormat&&HasData&&Info.DataBytes%Info.BlockAlign==0;
}
}

bool AWCVNextLab::BeginBellbackAudioCapture(FString& Failure)
{
    if(!BellbackAudioRequested)return true;
    BellbackAudioPath=FPaths::ConvertRelativePathToFull(EvidenceDirectory/TEXT("bellback-master-submix.wav"));
    const FString MetadataPath=FPaths::ChangeExtension(BellbackAudioPath,TEXT("json"));
    BellbackAudioMetadata=MakeShared<FJsonObject>();
    BellbackAudioMetadata->SetStringField(TEXT("status"),TEXT("NOT_STARTED"));
    BellbackAudioMetadata->SetStringField(TEXT("file"),BellbackAudioPath);
    BellbackAudioMetadata->SetStringField(TEXT("source"),TEXT("This game world's master submix via UAudioMixerBlueprintLibrary; no microphone or desktop capture."));
    BellbackAudioMetadata->SetStringField(TEXT("method"),TEXT("StartRecordingOutput(null submix), StopRecordingOutput(WavFile), then asynchronous tick polling for exact RIFF length, complete PCM chunks and stable valid file."));
    BellbackAudioMetadata->SetBoolField(TEXT("primary_performance_run"),false);
    BellbackAudioMetadata->SetBoolField(TEXT("human_listening_approval"),false);
    BellbackAudioMetadata->SetStringField(TEXT("clipping_and_mix_review"),TEXT("NOT_RUN; exported PCM requires independent sample analysis and listening."));
    if(IFileManager::Get().FileExists(*BellbackAudioPath)||IFileManager::Get().FileExists(*MetadataPath)){
        Failure=TEXT("Audio capture refuses to overwrite existing WAV or sidecar");
    }else if(!FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(this)){
        Failure=TEXT("Audio capture requires a live game audio mixer");
    }
    if(!Failure.IsEmpty()){
        BellbackAudioFailure=Failure;BellbackAudioMetadata->SetStringField(TEXT("failure"),Failure);return false;
    }
    BellbackAudioStartedAt=FPlatformTime::Seconds();
    BellbackAudioMetadata->SetStringField(TEXT("status"),TEXT("RECORDING_REQUESTED"));
    BellbackAudioMetadata->SetStringField(TEXT("started_utc"),FDateTime::UtcNow().ToIso8601());
    BellbackAudioMetadata->SetNumberField(TEXT("started_route_seconds"),BellbackAudioStartedAt-BellbackRouteStarted);
    UAudioMixerBlueprintLibrary::StartRecordingOutput(this,BellbackPerformance?135.f:105.f,nullptr);
    BellbackAudioRecording=true;
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_AUDIO_BEGIN master_submix=1 file=%s primary_performance=0"),*BellbackAudioPath);
    return true;
}

bool AWCVNextLab::FinishBellbackAudioCapture(const FString& RouteFailure)
{
    if(BellbackAudioExportPending)return false;
    if(!BellbackAudioRecording)return true;
    BellbackAudioDeferredRouteFailure=RouteFailure;
    BellbackAudioStopRequestedAt=FPlatformTime::Seconds();
    BellbackAudioRecording=false;BellbackAudioExportPending=true;
    BellbackAudioMetadata->SetStringField(TEXT("status"),TEXT("EXPORT_PENDING"));
    BellbackAudioMetadata->SetStringField(TEXT("stopped_utc"),FDateTime::UtcNow().ToIso8601());
    BellbackAudioMetadata->SetNumberField(TEXT("stopped_route_seconds"),BellbackAudioStopRequestedAt-BellbackRouteStarted);
    BellbackAudioMetadata->SetNumberField(TEXT("recording_wall_seconds"),BellbackAudioStopRequestedAt-BellbackAudioStartedAt);
    BellbackAudioMetadata->SetNumberField(TEXT("export_timeout_seconds"),ExportTimeoutSeconds);
    // WAV export intentionally returns no SoundWave. It finishes asynchronously;
    // FinishBellbackRoute must not request exit until Poll confirms completeness.
    UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,
        FPaths::GetBaseFilename(BellbackAudioPath),FPaths::GetPath(BellbackAudioPath),nullptr);
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_AUDIO_EXPORT_PENDING file=%s"),*BellbackAudioPath);
    return false;
}

void AWCVNextLab::PollBellbackAudioCapture(double Now)
{
    if(!BellbackAudioExportPending||Now<BellbackAudioNextPoll)return;
    BellbackAudioNextPoll=Now+.1;
    const bool TimedOut=Now-BellbackAudioStopRequestedAt>=ExportTimeoutSeconds;
    FRecordedWaveInfo Wave;
    const bool Valid=ReadCompletedWave(BellbackAudioPath,Wave);
    if(Valid){
        if(BellbackAudioValidSeenAt<=0||BellbackAudioValidatedBytes!=Wave.Bytes){
            BellbackAudioValidSeenAt=Now;BellbackAudioValidatedBytes=Wave.Bytes;
        }
    }else{
        BellbackAudioValidSeenAt=0;BellbackAudioValidatedBytes=0;
    }
    const bool Complete=Valid&&Now-BellbackAudioValidSeenAt>=StableFileSeconds;
    if(!Complete&&!TimedOut)return;
    BellbackAudioExportPending=false;
    if(!Complete)BellbackAudioFailure=TEXT("Master-submix WAV export did not become a complete stable PCM RIFF before timeout");
    BellbackAudioMetadata->SetStringField(TEXT("status"),Complete?TEXT("PASS_CAPTURE_ONLY"):TEXT("FAIL"));
    BellbackAudioMetadata->SetBoolField(TEXT("complete_valid_pcm_riff"),Complete);
    BellbackAudioMetadata->SetBoolField(TEXT("timed_out"),!Complete&&TimedOut);
    BellbackAudioMetadata->SetStringField(TEXT("failure"),BellbackAudioFailure);
    BellbackAudioMetadata->SetStringField(TEXT("completed_utc"),FDateTime::UtcNow().ToIso8601());
    BellbackAudioMetadata->SetNumberField(TEXT("export_wait_seconds"),Now-BellbackAudioStopRequestedAt);
    BellbackAudioMetadata->SetNumberField(TEXT("bytes"),IFileManager::Get().FileSize(*BellbackAudioPath));
    if(Complete){
        BellbackAudioMetadata->SetNumberField(TEXT("sample_rate_hz"),Wave.SampleRate);
        BellbackAudioMetadata->SetNumberField(TEXT("channels"),Wave.Channels);
        BellbackAudioMetadata->SetNumberField(TEXT("bits_per_sample"),Wave.Bits);
        BellbackAudioMetadata->SetNumberField(TEXT("data_bytes"),Wave.DataBytes);
        BellbackAudioMetadata->SetNumberField(TEXT("duration_seconds"),double(Wave.DataBytes)/(double(Wave.SampleRate)*Wave.BlockAlign));
        BellbackAudioMetadata->SetNumberField(TEXT("valid_file_stability_seconds"),Now-BellbackAudioValidSeenAt);
    }
    FString Json;FJsonSerializer::Serialize(BellbackAudioMetadata.ToSharedRef(),TJsonWriterFactory<>::Create(&Json));
    const bool Saved=FFileHelper::SaveStringToFile(Json,*FPaths::ChangeExtension(BellbackAudioPath,TEXT("json")));
    BellbackAudioMetadata->SetBoolField(TEXT("sidecar_saved"),Saved);
    if(!Saved){
        BellbackAudioFailure=TEXT("Master-submix capture metadata could not be saved");
        BellbackAudioMetadata->SetStringField(TEXT("status"),TEXT("FAIL"));
        BellbackAudioMetadata->SetStringField(TEXT("failure"),BellbackAudioFailure);
    }
    UE_LOG(LogTemp,Display,TEXT("WC_BELLBACK_AUDIO_COMPLETE valid=%d metadata=%d wait_seconds=%.3f file=%s"),Complete,Saved,Now-BellbackAudioStopRequestedAt,*BellbackAudioPath);
    FinishBellbackRoute(BellbackAudioDeferredRouteFailure);
}
