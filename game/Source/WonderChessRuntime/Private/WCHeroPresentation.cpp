#include "WCHeroPresentation.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "AnimationRuntime.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace {
const float BlendSeconds = .15f;

// Placement of each imported hero is data so it can be adjusted without rebuilding.
TSharedPtr<FJsonObject> HeroConfig(const FString& HeroId)
{
    static TSharedPtr<FJsonObject> Root;
    static bool Loaded = false;
    if (!Loaded)
    {
        Loaded = true;
        FString Text;
        const FString Path = FPaths::ProjectContentDir() / TEXT("WonderChess/VNextData/hero_presentation.json");
        if (FFileHelper::LoadFileToString(Text, *Path))
        {
            const auto Reader = TJsonReaderFactory<>::Create(Text);
            FJsonSerializer::Deserialize(Reader, Root);
        }
    }
    const TSharedPtr<FJsonObject>* Hero = nullptr;
    return Root && Root->TryGetObjectField(HeroId, Hero) ? *Hero : nullptr;
}
FVector Vector(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, FVector Default = FVector::ZeroVector)
{
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || Values->Num() != 3) return Default;
    return FVector((*Values)[0]->AsNumber(), (*Values)[1]->AsNumber(), (*Values)[2]->AsNumber());
}
template <class T> T* LoadAsset(const FString& Path)
{
    // "/Game/Folder/Name" -> "/Game/Folder/Name.Name"
    return LoadObject<T>(nullptr, *(Path + TEXT(".") + FPaths::GetBaseFilename(Path)));
}
// Reference-pose transform of a bone in mesh space.
FTransform ReferenceTransform(const FReferenceSkeleton& Skeleton, int32 Bone)
{
    FTransform Result = FTransform::Identity;
    for (; Bone != INDEX_NONE; Bone = Skeleton.GetParentIndex(Bone)) Result = Result * Skeleton.GetRefBonePose()[Bone];
    return Result;
}

struct FHeroAnimProxy : FAnimInstanceProxy
{
    UAnimSequence* Current = nullptr; UAnimSequence* Previous = nullptr;
    float Time = 0, PreviousTime = 0, Alpha = 1;
    FWCHeldArm Arm; bool bHold = false;
    explicit FHeroAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance) {}
    virtual void PreUpdate(UAnimInstance* Instance, float Delta) override
    {
        FAnimInstanceProxy::PreUpdate(Instance, Delta);
        const auto* A = CastChecked<UWCHeroAnimInstance>(Instance);
        Current = A->Current; Previous = A->Previous; Time = A->CurrentSeconds; PreviousTime = A->PreviousSeconds;
        Alpha = A->BlendAlpha; Arm = A->HeldArm; bHold = A->bHoldArm && A->HeldArm.bValid;
    }
    virtual bool Evaluate(FPoseContext& Output) override
    {
        Output.ResetToRefPose();
        if (!Current) return true;
        FAnimationPoseData OutData(Output);
        Current->GetAnimationPose(OutData, FAnimExtractContext(double(Time), false));
        if (Previous && Alpha < 1)
        {
            FPoseContext Old(Output); Old.ResetToRefPose();
            FAnimationPoseData OldData(Old);
            Previous->GetAnimationPose(OldData, FAnimExtractContext(double(PreviousTime), false));
            FAnimationRuntime::BlendTwoPosesTogetherInPlace(OutData, OldData, Alpha);
        }
        if (bHold) HoldArm(Output.Pose);
        Output.Pose.NormalizeRotations();
        return true;
    }
    // Replaces the animated arm with the held pose, turned with the chest so it follows leans and twists.
    void HoldArm(FCompactPose& Pose) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        const auto Index = [&](FName Name) {
            const int32 Mesh = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
            return Mesh < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(Mesh));
        };
        const auto Chest = Index(Arm.Chest), Upper = Index(Arm.Upper), Lower = Index(Arm.Lower);
        if (Chest.GetInt() < 0 || Upper.GetInt() < 0 || Lower.GetInt() < 0) return;
        const auto World = [&](FCompactPoseBoneIndex Bone) {
            FTransform Result = FTransform::Identity;
            for (; Bone.GetInt() != INDEX_NONE; Bone = Pose.GetParentBoneIndex(Bone)) Result = Result * Pose[Bone];
            return Result;
        };
        const FQuat Turn = World(Chest).GetRotation() * Arm.ChestReference.Inverse();
        const FTransform Parent = World(Pose.GetParentBoneIndex(Upper));
        FTransform UpperWorld = Pose[Upper] * Parent;
        UpperWorld.SetRotation((Turn * Arm.UpperHeld).GetNormalized());
        FTransform LowerWorld = Pose[Lower] * UpperWorld;
        LowerWorld.SetRotation((Turn * Arm.LowerHeld).GetNormalized());
        Pose[Upper] = UpperWorld.GetRelativeTransform(Parent);
        Pose[Lower] = LowerWorld.GetRelativeTransform(UpperWorld);
    }
};
}

FAnimInstanceProxy* UWCHeroAnimInstance::CreateAnimInstanceProxy() { return new FHeroAnimProxy(this); }
void UWCHeroAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) { delete Proxy; }

bool UWCHeroPresentationComponent::HasModel(const FString& HeroId) { return HeroConfig(HeroId).IsValid(); }

bool UWCHeroPresentationComponent::InitializeHero(const FString& HeroId, FString& Error)
{
    const auto Config = HeroConfig(HeroId);
    if (!Config) { Error = TEXT("No hero presentation entry for ") + HeroId; return false; }
    auto* Mesh = LoadAsset<USkeletalMesh>(Config->GetStringField(TEXT("mesh")));
    if (!Mesh) { Error = TEXT("Hero mesh is missing for ") + HeroId; return false; }
    Height = Config->GetNumberField(TEXT("label_height"));
    for (const auto& Clip : Config->GetObjectField(TEXT("clips"))->Values)
    {
        if (auto* Sequence = LoadAsset<UAnimSequence>(Clip.Value->AsString())) Clips.Add(FName(*Clip.Key), Sequence);
        else UE_LOG(LogTemp, Warning, TEXT("WC_HERO_CLIP_MISSING hero=%s clip=%s"), *HeroId, *Clip.Key);
    }
    if (!Clips.Contains(TEXT("Idle"))) { Error = TEXT("Hero has no Idle clip: ") + HeroId; return false; }
    const TSharedPtr<FJsonObject>* RateObject = nullptr;
    if (Config->TryGetObjectField(TEXT("rates"), RateObject))
        for (const auto& Rate : (*RateObject)->Values) Rates.Add(FName(*Rate.Key), float(Rate.Value->AsNumber()));

    const auto& Skeleton = Mesh->GetRefSkeleton();
    FTransform HeldLower = FTransform::Identity;
    FVector HeldDirection = FVector::ForwardVector;
    const TSharedPtr<FJsonObject>* Held = nullptr;
    if (Config->TryGetObjectField(TEXT("held_arm"), Held))
    {
        HeldArm.Chest = FName(*(*Held)->GetStringField(TEXT("chest")));
        HeldArm.Upper = FName(*(*Held)->GetStringField(TEXT("upper")));
        HeldArm.Lower = FName(*(*Held)->GetStringField(TEXT("lower")));
        const int32 Chest = Skeleton.FindBoneIndex(HeldArm.Chest), Upper = Skeleton.FindBoneIndex(HeldArm.Upper),
            Lower = Skeleton.FindBoneIndex(HeldArm.Lower), Hand = Skeleton.FindBoneIndex(FName(*(*Held)->GetStringField(TEXT("hand"))));
        if (Chest < 0 || Upper < 0 || Lower < 0 || Hand < 0) { Error = TEXT("Held-arm bones are missing for ") + HeroId; return false; }
        // Directions are in mesh space for the reference pose: the hero faces +Y and its left is +X.
        const FTransform UpperRef = ReferenceTransform(Skeleton, Upper), LowerRef = ReferenceTransform(Skeleton, Lower),
            HandRef = ReferenceTransform(Skeleton, Hand);
        const FVector UpperWanted = Vector(*Held, TEXT("upper_direction")).GetSafeNormal(),
            LowerWanted = Vector(*Held, TEXT("lower_direction")).GetSafeNormal();
        const FQuat UpperTurn = FQuat::FindBetweenNormals((LowerRef.GetLocation() - UpperRef.GetLocation()).GetSafeNormal(), UpperWanted);
        const FVector LowerAfterUpper = UpperTurn.RotateVector((HandRef.GetLocation() - LowerRef.GetLocation()).GetSafeNormal());
        const FQuat LowerTurn = FQuat::FindBetweenNormals(LowerAfterUpper, LowerWanted);
        HeldArm.ChestReference = ReferenceTransform(Skeleton, Chest).GetRotation();
        HeldArm.UpperHeld = UpperTurn * UpperRef.GetRotation();
        HeldArm.LowerHeld = LowerTurn * UpperTurn * LowerRef.GetRotation();
        HeldArm.bValid = true;
        const double UpperLength = FVector::Distance(UpperRef.GetLocation(), LowerRef.GetLocation());
        HeldLower = FTransform(HeldArm.LowerHeld, UpperRef.GetLocation() + UpperWanted * UpperLength);
        HeldDirection = LowerWanted;
        const TArray<TSharedPtr<FJsonValue>>* Free = nullptr;
        if ((*Held)->TryGetArrayField(TEXT("free_clips"), Free)) for (const auto& Name : *Free) FreeArmClips.Add(FName(*Name->AsString()));
    }

    Skeletal = NewObject<USkeletalMeshComponent>(GetOwner());
    GetOwner()->AddInstanceComponent(Skeletal);
    Skeletal->SetupAttachment(this);
    Skeletal->SetSkeletalMeshAsset(Mesh);
    Skeletal->SetRelativeScale3D(FVector(Config->GetNumberField(TEXT("scale"))));
    Skeletal->SetRelativeRotation(FRotator(0, Config->GetNumberField(TEXT("yaw")), 0));
    Skeletal->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Skeletal->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Skeletal->bEnableUpdateRateOptimizations = false;
    Skeletal->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    Skeletal->SetAnimInstanceClass(UWCHeroAnimInstance::StaticClass());
    Skeletal->RegisterComponent();

    const TArray<TSharedPtr<FJsonValue>>* ItemList = nullptr;
    if (Config->TryGetArrayField(TEXT("items"), ItemList))
        for (const auto& Value : *ItemList)
        {
            const auto Entry = Value->AsObject();
            auto* ItemMesh = LoadAsset<UStaticMesh>(Entry->GetStringField(TEXT("mesh")));
            if (!ItemMesh) { Error = TEXT("Hero item mesh is missing for ") + HeroId; return false; }
            auto* Item = NewObject<UStaticMeshComponent>(GetOwner());
            GetOwner()->AddInstanceComponent(Item);
            Item->SetStaticMesh(ItemMesh);
            Item->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            const FName Bone(*Entry->GetStringField(TEXT("bone")));
            Item->SetupAttachment(Skeletal, Bone);
            const FVector Rotation = Vector(Entry, TEXT("rotation"));
            FTransform Offset(FRotator(Rotation.X, Rotation.Y, Rotation.Z), Vector(Entry, TEXT("location")),
                FVector(Entry->GetNumberField(TEXT("scale"))));
            // "held_pose" items are placed in mesh space for the held arm, then follow that forearm rigidly.
            bool bHeldPose = false;
            if (Entry->TryGetBoolField(TEXT("held_pose"), bHeldPose) && bHeldPose && HeldArm.bValid && Bone == HeldArm.Lower)
            {
                Offset.SetLocation(HeldLower.GetLocation() + HeldDirection * Entry->GetNumberField(TEXT("along_forearm")) + Offset.GetLocation());
                Offset = Offset.GetRelativeTransform(HeldLower);
            }
            Item->SetRelativeTransform(Offset);
            Item->RegisterComponent();
            Items.Add(Item);
        }
    Play(TEXT("Idle"), true);
    Advance(0);
    UE_LOG(LogTemp, Display, TEXT("WC_HERO_MODEL hero=%s clips=%d items=%d held_arm=%d"), *HeroId, Clips.Num(), Items.Num(), int(HeldArm.bValid));
    return true;
}

void UWCHeroPresentationComponent::Play(FName Clip, bool Loop, bool Restart)
{
    if (!Clips.Contains(Clip)) Clip = TEXT("Idle");
    if (Clip == Current && !Restart) return;
    Before = Current; BeforeSeconds = Seconds; Blend = Before.IsNone() ? 1 : 0;
    Current = Clip; Looping = Loop; Seconds = 0;
}

void UWCHeroPresentationComponent::Advance(float DeltaSeconds)
{
    auto* Sequence = Clips.FindChecked(Current).Get();
    const float Length = Sequence->GetPlayLength();
    const float* Rate = Rates.Find(Current);
    Seconds += DeltaSeconds * (Rate ? *Rate : 1);
    Seconds = Looping ? FMath::Fmod(Seconds, Length) : FMath::Min(Seconds, Length - .001f);
    Blend = FMath::Min(1.f, Blend + DeltaSeconds / BlendSeconds);
    if (auto* Instance = Cast<UWCHeroAnimInstance>(Skeletal->GetAnimInstance()))
    {
        Instance->Current = Sequence; Instance->CurrentSeconds = Seconds;
        Instance->Previous = Before.IsNone() ? nullptr : Clips.FindChecked(Before).Get();
        Instance->PreviousSeconds = BeforeSeconds; Instance->BlendAlpha = Blend;
        Instance->HeldArm = HeldArm; Instance->bHoldArm = !FreeArmClips.Contains(Current);
    }
}

void UWCHeroPresentationComponent::ReviewClip(FName Clip, bool Loop)
{
    Reviewing = !Clip.IsNone();
    if (Skeletal && Reviewing) Play(Clip, Loop, true);
}

void UWCHeroPresentationComponent::Present(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds)
{
    if (!Skeletal) return;
    if (!Reviewing)
    {
        if (!Unit) { PlayedAction = 0; Play(TEXT("Idle"), true); }
        else if (Unit->health <= 0 || Unit->state == wc::ActionState::Defeated) Play(TEXT("Defeat"), false);
        else switch (Unit->state)
        {
        case wc::ActionState::Moving: Play(TEXT("Move"), true); break;
        case wc::ActionState::Stunned: Play(TEXT("Hit"), false); break;
        case wc::ActionState::AttackWindup:
        case wc::ActionState::AttackRecovery:
            // One swing per simulated attack, restarted when the next attack begins.
            Play(TEXT("Attack"), false, Unit->actionId != PlayedAction);
            PlayedAction = Unit->actionId;
            break;
        case wc::ActionState::CastWindup:
        case wc::ActionState::CastRecovery:
            Play(TEXT("Cast"), false, Unit->actionId != PlayedAction);
            PlayedAction = Unit->actionId;
            break;
        default: Play(TEXT("Idle"), true); break;
        }
    }
    Advance(Paused && !Reviewing ? 0 : DeltaSeconds);
}
