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
    TArray<FWCBoneCurl> Curls;
    explicit FHeroAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance) {}
    virtual void PreUpdate(UAnimInstance* Instance, float Delta) override
    {
        FAnimInstanceProxy::PreUpdate(Instance, Delta);
        const auto* A = CastChecked<UWCHeroAnimInstance>(Instance);
        Current = A->Current; Previous = A->Previous; Time = A->CurrentSeconds; PreviousTime = A->PreviousSeconds;
        Alpha = A->BlendAlpha; Arm = A->HeldArm; bHold = A->bHoldArm && A->HeldArm.bValid;
        if (Curls.Num() != A->Curls.Num()) Curls = A->Curls;
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
        // The clips carry no finger motion, so the grip bones take their fixed curl here.
        for (const auto& Curl : Curls)
        {
            const auto& Bones = Output.Pose.GetBoneContainer();
            const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Curl.Bone);
            const FCompactPoseBoneIndex Bone = MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
            if (Bone.GetInt() >= 0) Output.Pose[Bone].SetRotation(Curl.ParentSpace * Output.Pose[Bone].GetRotation());
        }
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
    FString StaticPath;
    if (Config->TryGetStringField(TEXT("static_mesh"), StaticPath))
    {
        auto* Model = LoadAsset<UStaticMesh>(StaticPath);
        if (!Model) { Error = TEXT("Hero model is missing for ") + HeroId; return false; }
        Height = Config->GetNumberField(TEXT("label_height"));
        StaticScale = Config->GetNumberField(TEXT("scale"));
        StaticYaw = Config->GetNumberField(TEXT("yaw"));
        // The model's lowest point rests on the tile whatever its pivot is.
        const FBoxSphereBounds ModelBounds = Model->GetBounds();
        StaticLift = -(ModelBounds.Origin.Z - ModelBounds.BoxExtent.Z) * StaticScale;
        StaticBody = NewObject<UStaticMeshComponent>(GetOwner());
        GetOwner()->AddInstanceComponent(StaticBody);
        StaticBody->SetupAttachment(this);
        StaticBody->SetStaticMesh(Model);
        StaticBody->SetMobility(EComponentMobility::Movable);
        StaticBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        StaticBody->RegisterComponent();
        PresentStatic(nullptr, true, 0);
        return true;
    }
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

    // "curls": grip bones bent about a mesh-space axis of the reference pose.
    const TArray<TSharedPtr<FJsonValue>>* CurlList = nullptr;
    if (Config->TryGetArrayField(TEXT("curls"), CurlList))
        for (const auto& Value : *CurlList)
        {
            const auto Entry = Value->AsObject();
            FWCBoneCurl Curl;
            Curl.Bone = FName(*Entry->GetStringField(TEXT("bone")));
            const FReferenceSkeleton& Reference = Mesh->GetRefSkeleton();
            const int32 Bone = Reference.FindBoneIndex(Curl.Bone);
            if (Bone == INDEX_NONE) { UE_LOG(LogTemp, Warning, TEXT("WC_HERO_CURL_BONE_MISSING hero=%s bone=%s"), *HeroId, *Curl.Bone.ToString()); continue; }
            const FQuat Parent = ReferenceTransform(Reference, Reference.GetParentIndex(Bone)).GetRotation();
            const FQuat Bend(Vector(Entry, TEXT("axis"), FVector::XAxisVector).GetSafeNormal(), FMath::DegreesToRadians(Entry->GetNumberField(TEXT("angle"))));
            Curl.ParentSpace = Parent.Inverse() * Bend * Parent;
            Curls.Add(Curl);
        }
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
            // "grip" items are held in a hand. The weapon is laid out in mesh space for the reference pose (which way
            // its business end points, which point of the handle sits in the palm) and then follows the hand rigidly.
            const TSharedPtr<FJsonObject>* Grip = nullptr;
            const FReferenceSkeleton& Bones = Mesh->GetRefSkeleton();
            const int32 Hand = Bones.FindBoneIndex(Bone);
            if (Entry->TryGetObjectField(TEXT("grip"), Grip) && Hand != INDEX_NONE)
            {
                const FTransform HandReference = ReferenceTransform(Bones, Hand);
                const FTransform ArmReference = ReferenceTransform(Bones, Bones.GetParentIndex(Hand));
                const float ItemScale = Entry->GetNumberField(TEXT("scale"));
                const FVector Tip = Vector(*Grip, TEXT("tip_axis"), FVector::ZAxisVector).GetSafeNormal();
                const FVector Direction = Vector(*Grip, TEXT("rest_direction"), FVector::YAxisVector).GetSafeNormal();
                double Roll = 0, Reach = 8;
                (*Grip)->TryGetNumberField(TEXT("roll"), Roll);
                (*Grip)->TryGetNumberField(TEXT("reach"), Reach);
                const FQuat Aim = FQuat(Direction, FMath::DegreesToRadians(Roll)) * FQuat::FindBetweenNormals(Tip, Direction);
                // The hand bone sits at the wrist; the palm is a little further along the forearm's line.
                const FVector Palm = HandReference.GetLocation() +
                    (HandReference.GetLocation() - ArmReference.GetLocation()).GetSafeNormal() * Reach + Vector(*Grip, TEXT("palm"));
                Offset = FTransform(Aim, Palm - Aim.RotateVector(Vector(*Grip, TEXT("point")) * ItemScale), FVector(ItemScale))
                    .GetRelativeTransform(HandReference);
                FWCGripItem Rod;
                Rod.Item = Item; Rod.Bone = Bone; Rod.Base = Offset; Rod.Point = Vector(*Grip, TEXT("point")); Rod.Tip = Tip;
                // The rod runs from the grip to the far end of the model along the tip direction.
                const FBoxSphereBounds ItemBounds = ItemMesh->GetBounds();
                const float Far = FVector::DotProduct(ItemBounds.Origin, Tip) + FVector::DotProduct(ItemBounds.BoxExtent, Tip.GetAbs());
                Rod.Length = FMath::Max(1.f, (Far - FVector::DotProduct(Rod.Point, Tip)) * ItemScale);
                double Thickness = 6;
                (*Grip)->TryGetNumberField(TEXT("radius"), Thickness);
                Rod.Radius = Thickness;
                Grips.Add(Rod);
            }
            Item->SetRelativeTransform(Offset);
            Item->RegisterComponent();
            Items.Add(Item);
        }
    const int32 HeadBone = Mesh->GetRefSkeleton().FindBoneIndex(TEXT("Head"));
    if (HeadBone != INDEX_NONE) BodyHeight = ReferenceTransform(Mesh->GetRefSkeleton(), HeadBone).GetLocation().Z * 1.1f;
    double RadiusScale = 1;
    if (Config->TryGetNumberField(TEXT("body_radius_scale"), RadiusScale)) BodyRadiusScale = RadiusScale;
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
        Instance->Curls = Curls;
    }
    ClearBody(DeltaSeconds);
}

void UWCHeroPresentationComponent::ClearBody(float DeltaSeconds)
{
    if (Grips.IsEmpty()) return;
    // The hero's body as rounded rods between joints, sized from its height. Poses are those of the last drawn frame.
    struct FRod { const TCHAR* From; const TCHAR* To; float Radius; };
    static const FRod Body[] = {
        {TEXT("Hips"), TEXT("Spine"), .135f}, {TEXT("Spine"), TEXT("Head"), .10f}, {TEXT("Head"), TEXT("head_end"), .085f},
        {TEXT("LeftUpLeg"), TEXT("LeftLeg"), .08f}, {TEXT("LeftLeg"), TEXT("LeftFoot"), .06f},
        {TEXT("RightUpLeg"), TEXT("RightLeg"), .08f}, {TEXT("RightLeg"), TEXT("RightFoot"), .06f}};
    const auto Joint = [this](const TCHAR* Name) { return Skeletal->GetSocketTransform(Name, RTS_Component).GetLocation(); };
    for (auto& Held : Grips)
    {
        const FTransform Hand = Skeletal->GetSocketTransform(Held.Bone, RTS_Component);
        const FTransform Rest = Held.Base * Hand;
        const FVector Grip = Rest.TransformPosition(Held.Point);
        const FVector Along = Rest.TransformVectorNoScale(Held.Tip).GetSafeNormal();
        FQuat Turn = FQuat::Identity;
        for (int Pass = 0; Pass < 3; ++Pass)
            for (const auto& Rod : Body)
            {
                const FVector End = Grip + Turn.RotateVector(Along) * Held.Length;
                FVector OnWeapon, OnBody;
                FMath::SegmentDistToSegmentSafe(Grip, End, Joint(Rod.From), Joint(Rod.To), OnWeapon, OnBody);
                const float Clear = Held.Radius + Rod.Radius * BodyHeight * BodyRadiusScale;
                const FVector Away = OnWeapon - OnBody;
                const float Lever = FVector::Dist(OnWeapon, Grip);
                // A weapon touching the body right at the hand cannot be turned clear; the hand itself is there.
                if (Away.SizeSquared() >= Clear * Clear || Lever < 8) continue;
                const FVector Axis = FVector::CrossProduct(OnWeapon - Grip, Away.GetSafeNormal()).GetSafeNormal();
                if (Axis.IsNearlyZero()) continue;
                Turn = FQuat(Axis, FMath::Min(FMath::Atan2(Clear - Away.Size(), Lever), .5f)) * Turn;
            }
        // Kept in the hand's space so the turn rides with the arm, and eased so it never snaps.
        const FQuat Wanted = Hand.GetRotation().Inverse() * Turn * Hand.GetRotation();
        Held.Clearance = FQuat::Slerp(Held.Clearance, Wanted, FMath::Clamp(DeltaSeconds * 14, 0.f, 1.f)).GetNormalized();
        const FQuat Applied = Hand.GetRotation() * Held.Clearance * Hand.GetRotation().Inverse();
        FTransform Placed = Rest;
        Placed.SetRotation(Applied * Rest.GetRotation());
        Placed.SetLocation(Grip + Applied.RotateVector(Rest.GetLocation() - Grip));
        Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
    }
}

void UWCHeroPresentationComponent::ReviewClip(FName Clip, bool Loop)
{
    Reviewing = !Clip.IsNone();
    if (Skeletal && Reviewing) Play(Clip, Loop, true);
}

void UWCHeroPresentationComponent::PresentStatic(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds)
{
    const float Step = Paused ? 0 : DeltaSeconds;
    Clock += Step; ActionAge += Step;
    const bool Defeated = Unit && (Unit->health <= 0 || Unit->state == wc::ActionState::Defeated);
    DefeatAge = Defeated ? DefeatAge + Step : 0;
    const auto State = Unit ? Unit->state : wc::ActionState::Idle;
    const bool Casting = State == wc::ActionState::CastWindup || State == wc::ActionState::CastRecovery;
    const bool Acting = Casting || State == wc::ActionState::AttackWindup || State == wc::ActionState::AttackRecovery;
    if (!Unit) PlayedAction = 0;
    else if (Acting && !Defeated && Unit->actionId != PlayedAction) { PlayedAction = Unit->actionId; ActionAge = 0; StaticCasting = Casting; }
    // One surge per action: out and back over 0.45 s for an attack, a slower swell for a cast.
    const float Length = StaticCasting ? .7f : .45f;
    const float Pulse = ActionAge < Length ? FMath::Sin(ActionAge / Length * UE_PI) : 0;
    FVector Offset(0, 0, StaticLift + 7 + FMath::Sin(Clock * 2.1f) * 5);
    FVector Scale(StaticScale);
    // The model faces the actor's +Y. Positive lean tips its top that way.
    float Lean = FMath::Sin(Clock * 1.3f) * 1.5f, Side = FMath::Sin(Clock * .9f + 1) * 2.5f;
    if (State == wc::ActionState::Moving) Lean += 9;
    if (State == wc::ActionState::Stunned) Offset.X += FMath::Sin(Clock * 42) * 3.5f;
    if (StaticCasting) { Offset.Z += Pulse * 26; Scale *= FVector(1 + Pulse * .14f, 1 + Pulse * .14f, 1 + Pulse * .06f); }
    else { Offset.Y += Pulse * 48; Lean += Pulse * 14; }
    if (Defeated)
    {
        // The body loses its shape and settles into a low pool.
        const float Fall = FMath::Clamp(DefeatAge / .8f, 0.f, 1.f);
        Scale *= FVector(1 + Fall * .35f, 1 + Fall * .35f, FMath::Lerp(1.f, .07f, Fall));
        Offset.Z = StaticLift * FMath::Lerp(1.f, .07f, Fall);
        Lean = Side = 0;
    }
    StaticBody->SetRelativeLocation(Offset);
    StaticBody->SetRelativeRotation(FQuat(FVector::XAxisVector, FMath::DegreesToRadians(-Lean)) *
        FQuat(FVector::YAxisVector, FMath::DegreesToRadians(Side)) * FRotator(0, StaticYaw, 0).Quaternion());
    StaticBody->SetRelativeScale3D(Scale);
}

void UWCHeroPresentationComponent::Present(const wc::CombatUnit* Unit, bool Paused, float DeltaSeconds)
{
    if (StaticBody) { PresentStatic(Unit, Paused, DeltaSeconds); return; }
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
