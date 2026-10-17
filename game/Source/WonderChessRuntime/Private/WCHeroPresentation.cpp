#include "WCHeroPresentation.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "AnimationRuntime.h"
#include "Components/PointLightComponent.h"
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

// How far, and which way, a point must move to leave a solid cylinder (zero when it is already outside).
FVector OutOfSolid(const FVector& Point, const FVector& Base, const FVector& Axis, double Height, double Radius)
{
    const FVector Offset = Point - Base;
    const double Along = FVector::DotProduct(Offset, Axis);
    if (Along <= 0 || Along >= Height) return FVector::ZeroVector;
    const FVector Radial = Offset - Axis * Along;
    const double Distance = Radial.Size();
    if (Distance >= Radius) return FVector::ZeroVector;
    FVector Best = (Distance > 1e-3 ? Radial / Distance : FVector::CrossProduct(Axis, FVector::YAxisVector).GetSafeNormal()) * (Radius - Distance);
    const FVector Top = Axis * (Height - Along), Bottom = -Axis * Along;
    if (Top.SizeSquared() < Best.SizeSquared()) Best = Top;
    if (Bottom.SizeSquared() < Best.SizeSquared()) Best = Bottom;
    return Best;
}
// A turn shortened to at most MaxDegrees about the same axis.
FQuat Capped(const FQuat& Turn, float MaxDegrees)
{
    FVector Axis; float Angle;
    Turn.ToAxisAndAngle(Axis, Angle);
    if (Angle > UE_PI) { Angle = UE_TWO_PI - Angle; Axis = -Axis; }
    const float Max = FMath::DegreesToRadians(MaxDegrees);
    return Angle <= Max ? Turn : FQuat(Axis, Max);
}

struct FHeroAnimProxy : FAnimInstanceProxy
{
    UAnimSequence* Current = nullptr; UAnimSequence* Previous = nullptr;
    float Time = 0, PreviousTime = 0, Alpha = 1;
    FWCHeldArm Arm; bool bHold = false;
    TArray<FWCBoneCurl> Curls;
    FWCSecondHand Second;
    TArray<FWCSecondHand> Reaches;
    float ReachTime = 0;
    TArray<FName> StraightBones;
    float StraightWeight = 0;
    TArray<FWCStanceBend> Stance;
    float StanceWeight = 0, StanceRate = 0, StanceLower = 0;
    bool bStancePlant = false;
    TArray<FWCSolid> Solids;
    TArray<FWCWristAim> Wrists;
    explicit FHeroAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance) {}
    virtual void PreUpdate(UAnimInstance* Instance, float Delta) override
    {
        FAnimInstanceProxy::PreUpdate(Instance, Delta);
        const auto* A = CastChecked<UWCHeroAnimInstance>(Instance);
        Current = A->Current; Previous = A->Previous; Time = A->CurrentSeconds; PreviousTime = A->PreviousSeconds;
        Alpha = A->BlendAlpha; Arm = A->HeldArm; bHold = A->bHoldArm && A->HeldArm.bValid;
        if (Curls.Num() != A->Curls.Num()) Curls = A->Curls;
        Second = A->SecondHand;
        Reaches = A->Reaches; ReachTime = A->ReachTime;
        StraightWeight = A->StraightWeight;
        if (StraightBones.Num() != A->StraightBones.Num()) StraightBones = A->StraightBones;
        if (Stance.Num() != A->Stance.Num()) Stance = A->Stance;
        StanceWeight = A->StanceWeight; StanceRate = A->StanceRate; StanceLower = A->StanceLower; bStancePlant = A->bStancePlant;
        if (Solids.Num() != A->Solids.Num()) Solids = A->Solids;
        Wrists = A->Wrists;
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
        if (StraightWeight > .01f) Straighten(Output.Pose);
        if (bHold) HoldArm(Output.Pose);
        if (StanceWeight > .01f) Stand(Output.Pose);
        LockRoot(Output.Pose);
        if (Second.bValid && Second.Weight > .01f) ReachSecondHand(Output.Pose, Second);
        for (const auto& Reach : Reaches) if (Reach.Weight > .01f) ReachSecondHand(Output.Pose, Reach);
        if (Solids.Num()) KeepArmsOut(Output.Pose);
        for (const auto& Wrist : Wrists) if (Wrist.RestWeight > .01f || Wrist.StrikeWeight > .01f) AimWrist(Output.Pose, Wrist);
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
    // Library clips carry their travel in the hips (a charge runs 2.6 m forward and snaps back). The game moves
    // the piece itself, so the hips are held over the tile: sideways and forward travel is removed, height is kept.
    void LockRoot(FCompactPose& Pose) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(TEXT("Hips"));
        if (MeshBone < 0) return;
        const FCompactPoseBoneIndex Hips = Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
        if (Hips.GetInt() < 0) return;
        FTransform Parent = FTransform::Identity, Rest = FTransform::Identity;
        for (FCompactPoseBoneIndex Bone = Pose.GetParentBoneIndex(Hips); Bone.GetInt() != INDEX_NONE; Bone = Pose.GetParentBoneIndex(Bone))
        { Parent = Parent * Pose[Bone]; Rest = Rest * Bones.GetRefPoseTransform(Bone); }
        const FVector Home = (Bones.GetRefPoseTransform(Hips) * Rest).GetLocation();
        FTransform World = Pose[Hips] * Parent;
        World.SetLocation(FVector(Home.X, Home.Y, World.GetLocation().Z));
        Pose[Hips] = World.GetRelativeTransform(Parent);
    }
    // Bends the off arm so its hand meets the weapon: a two-bone reach that keeps the elbow on its animated side.
    void ReachSecondHand(FCompactPose& Pose, const FWCSecondHand& Limb) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        const auto Index = [&](FName Name) {
            const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
            return MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
        };
        const auto Upper = Index(Limb.Upper), Lower = Index(Limb.Lower), Hand = Index(Limb.Hand), Carrier = Index(Limb.Carrier);
        if (Upper.GetInt() < 0 || Lower.GetInt() < 0 || Hand.GetInt() < 0 || Carrier.GetInt() < 0) return;
        const auto World = [&](FCompactPoseBoneIndex Bone) {
            FTransform Result = FTransform::Identity;
            for (; Bone.GetInt() != INDEX_NONE; Bone = Pose.GetParentBoneIndex(Bone)) Result = Result * Pose[Bone];
            return Result;
        };
        const FVector C = (Pose[Hand] * Pose[Lower] * Pose[Upper] * World(Pose.GetParentBoneIndex(Upper))).GetLocation();
        const float Lift = Limb.Beat * FMath::Max(0.f, FMath::Sin(ReachTime * Limb.Rate * UE_TWO_PI + Limb.Phase));
        SolveArm(Pose, Upper, Lower, Hand, FMath::Lerp(C, World(Carrier).TransformPosition(Limb.Target + Limb.Axis * Lift), Limb.Weight));
    }
    FCompactPoseBoneIndex Find(const FCompactPose& Pose, FName Name) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
        return MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
    }
    static FTransform WorldOf(const FCompactPose& Pose, FCompactPoseBoneIndex Bone)
    {
        FTransform Result = FTransform::Identity;
        for (; Bone.GetInt() != INDEX_NONE; Bone = Pose.GetParentBoneIndex(Bone)) Result = Result * Pose[Bone];
        return Result;
    }
    // Two-bone reach of the hand to Wanted (component space), keeping the elbow on its present side.
    void SolveArm(FCompactPose& Pose, FCompactPoseBoneIndex Upper, FCompactPoseBoneIndex Lower, FCompactPoseBoneIndex Hand, const FVector& Wanted) const
    {
        const FTransform Parent = WorldOf(Pose, Pose.GetParentBoneIndex(Upper));
        FTransform UpperWorld = Pose[Upper] * Parent, LowerWorld = Pose[Lower] * UpperWorld;
        const FTransform HandWorld = Pose[Hand] * LowerWorld;
        const FVector A = UpperWorld.GetLocation(), B = LowerWorld.GetLocation(), C = HandWorld.GetLocation();
        const double First = FVector::Dist(A, B), Next = FVector::Dist(B, C);
        const double Reach = FMath::Clamp(FVector::Dist(A, Wanted), FMath::Abs(First - Next) + .5, First + Next - .5);
        const FVector Line = (Wanted - A).GetSafeNormal();
        const double Along = (First * First + Reach * Reach - Next * Next) / (2 * Reach);
        const double Out = FMath::Sqrt(FMath::Max(0., First * First - Along * Along));
        FVector Pole = (B - A) - Line * FVector::DotProduct(B - A, Line);
        if (!Pole.Normalize()) Pole = FVector::CrossProduct(Line, FVector::UpVector).GetSafeNormal();
        const FVector Elbow = A + Line * Along + Pole * Out, Palm = A + Line * Reach;
        const FQuat TurnUpper = FQuat::FindBetweenVectors(B - A, Elbow - A);
        UpperWorld.SetRotation((TurnUpper * UpperWorld.GetRotation()).GetNormalized());
        const FQuat TurnLower = FQuat::FindBetweenVectors(TurnUpper.RotateVector(C - B), Palm - Elbow);
        LowerWorld.SetRotation((TurnLower * TurnUpper * LowerWorld.GetRotation()).GetNormalized());
        LowerWorld.SetLocation(Elbow);
        Pose[Upper] = UpperWorld.GetRelativeTransform(Parent);
        Pose[Lower] = LowerWorld.GetRelativeTransform(UpperWorld);
    }
    // Pulls the listed bones most of the way back to the reference pose, so a clip's slouch or hip shift becomes
    // an upright stand that still breathes a little.
    void Straighten(FCompactPose& Pose) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        for (const FName Name : StraightBones)
        {
            const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
            const FCompactPoseBoneIndex Bone = MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
            if (Bone.GetInt() < 0) continue;
            const FTransform& Rest = Bones.GetRefPoseTransform(Bone);
            Pose[Bone].SetRotation(FQuat::Slerp(Pose[Bone].GetRotation(), Rest.GetRotation(), StraightWeight));
            Pose[Bone].SetLocation(FMath::Lerp(Pose[Bone].GetLocation(), Rest.GetLocation(), StraightWeight));
        }
    }
    // Lays the stance over the clip: each listed bone turns about its axis, swinging slowly with the breath.
    void Stand(FCompactPose& Pose) const
    {
        const auto& Bones = Pose.GetBoneContainer();
        const auto Index = [&](const TCHAR* Name) {
            const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Name);
            return MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
        };
        const auto World = [&](FCompactPoseBoneIndex Bone) {
            FTransform Result = FTransform::Identity;
            for (; Bone.GetInt() != INDEX_NONE; Bone = Pose.GetParentBoneIndex(Bone)) Result = Result * Pose[Bone];
            return Result;
        };
        // "plant_feet": the lower foot stays at the height the clip gave it, however the stance bends the legs.
        const FCompactPoseBoneIndex LeftFoot = Index(TEXT("LeftFoot")), RightFoot = Index(TEXT("RightFoot"));
        const bool bPlant = bStancePlant && LeftFoot.GetInt() >= 0 && RightFoot.GetInt() >= 0;
        const auto Lowest = [&] { return FMath::Min(World(LeftFoot).GetLocation().Z, World(RightFoot).GetLocation().Z); };
        const double Planted = bPlant ? Lowest() : 0;
        const float Breath = FMath::Sin(ReachTime * StanceRate * UE_TWO_PI);
        for (const auto& Bend : Stance)
        {
            const int32 MeshBone = Bones.GetReferenceSkeleton().FindBoneIndex(Bend.Bone);
            const FCompactPoseBoneIndex Bone = MeshBone < 0 ? FCompactPoseBoneIndex(INDEX_NONE) : Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshBone));
            if (Bone.GetInt() < 0) continue;
            const float Degrees = (Bend.Angle + Bend.Breathe * Breath) * StanceWeight;
            Pose[Bone].SetRotation((FQuat(Bend.Axis, FMath::DegreesToRadians(Degrees)) * Pose[Bone].GetRotation()).GetNormalized());
        }
        // A crouch: the hips come straight down by "lower", and by however far bent knees lifted the planted foot.
        const FCompactPoseBoneIndex Hips = Index(TEXT("Hips"));
        const double Drop = StanceLower * StanceWeight + (bPlant ? Lowest() - Planted : 0);
        if (Drop == 0 || Hips.GetInt() < 0) return;
        const FTransform Parent = World(Pose.GetParentBoneIndex(Hips));
        FTransform Lowered = Pose[Hips] * Parent;
        Lowered.AddToTranslation(FVector(0, 0, -Drop));
        Pose[Hips] = Lowered.GetRelativeTransform(Parent);
    }
    // Hands and forearms are pushed out of solid items (a drum): the hand moves just far enough for the palm, wrist
    // and middle of the forearm to clear it, and the arm reaches there.
    void KeepArmsOut(FCompactPose& Pose) const
    {
        for (const auto& Limb : Reaches)
        {
            const auto Upper = Find(Pose, Limb.Upper), Lower = Find(Pose, Limb.Lower), Hand = Find(Pose, Limb.Hand);
            if (Upper.GetInt() < 0 || Lower.GetInt() < 0 || Hand.GetInt() < 0) continue;
            for (int Pass = 0; Pass < 2; ++Pass)
            {
                const FVector Elbow = WorldOf(Pose, Lower).GetLocation(), Wrist = WorldOf(Pose, Hand).GetLocation();
                const FVector Palm = Wrist + (Wrist - Elbow).GetSafeNormal() * 10;
                FVector Push = FVector::ZeroVector;
                for (const auto& Solid : Solids)
                {
                    const auto Carrier = Find(Pose, Solid.Carrier);
                    if (Carrier.GetInt() < 0) continue;
                    const FTransform Body = WorldOf(Pose, Carrier);
                    const FVector Axis = Body.TransformVectorNoScale(Solid.Axis).GetSafeNormal();
                    const FVector Base = Body.TransformPosition(Solid.Base) - Axis * Solid.LimbMargin;
                    for (const FVector& Point : {Palm, Wrist, (Elbow + Wrist) * .5})
                    {
                        const FVector Out = OutOfSolid(Point, Base, Axis, Solid.Height + 2 * Solid.LimbMargin, Solid.Radius + Solid.LimbMargin);
                        if (Out.SizeSquared() > Push.SizeSquared()) Push = Out;
                    }
                }
                if (Push.SizeSquared() < .01) break;
                SolveArm(Pose, Upper, Lower, Hand, Wrist + Push);
            }
        }
    }
    // Turns the hand so its stick points along the forearm plus the rest bend, or at the strike spot while drumming,
    // each turn capped like a wrist; the fingers stay closed round the handle.
    void AimWrist(FCompactPose& Pose, const FWCWristAim& Wrist) const
    {
        const auto Hand = Find(Pose, Wrist.Hand);
        if (Hand.GetInt() < 0) return;
        const auto Lower = Pose.GetParentBoneIndex(Hand);
        const FTransform Parent = WorldOf(Pose, Lower);
        FTransform HandWorld = Pose[Hand] * Parent;
        // While striking, the wrist starts from straight (its rest on the forearm) rather than whatever the clip does
        // with it, so a stomping or twisting clip cannot leave the stick pointing far from the drum.
        if (Wrist.StrikeWeight > .01f)
            HandWorld.SetRotation(FQuat::Slerp(HandWorld.GetRotation(), Parent.GetRotation() * Pose.GetBoneContainer().GetRefPoseTransform(Hand).GetRotation(), Wrist.StrikeWeight).GetNormalized());
        const FVector Along = HandWorld.TransformVectorNoScale(Wrist.Tip).GetSafeNormal();
        const FVector Forearm = (HandWorld.GetLocation() - Parent.GetLocation()).GetSafeNormal();
        FQuat Turn = FQuat::Slerp(FQuat::Identity, Capped(FQuat::FindBetweenNormals(Along, (Forearm + Wrist.RestBend).GetSafeNormal()), Wrist.RestMax), Wrist.RestWeight);
        const auto Carrier = Find(Pose, Wrist.Carrier);
        if (Wrist.StrikeWeight > .01f && Carrier.GetInt() >= 0)
        {
            float Lift = 0;
            for (const auto& Reach : Reaches)
                if (Reach.Hand == Wrist.Hand) Lift = Reach.Weight * Reach.Beat * FMath::Max(0.f, FMath::Sin(ReachTime * Reach.Rate * UE_TWO_PI + Reach.Phase));
            const FVector Spot = WorldOf(Pose, Carrier).TransformPosition(Wrist.Spot) + FVector(0, 0, Lift * Wrist.Snap);
            const FQuat Strike = Capped(FQuat::FindBetweenNormals(Along, (Spot - HandWorld.TransformPosition(Wrist.Grip)).GetSafeNormal()), Wrist.StrikeMax);
            Turn = FQuat::Slerp(Turn, Strike, Wrist.StrikeWeight);
        }
        HandWorld.SetRotation((Turn * HandWorld.GetRotation()).GetNormalized());
        Pose[Hand] = HandWorld.GetRelativeTransform(Parent);
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
TSharedPtr<FJsonObject> UWCHeroPresentationComponent::Config(const FString& HeroId) { return HeroConfig(HeroId); }
FVector UWCHeroPresentationComponent::ItemLocation(int Index) const
{
    return Items.IsValidIndex(Index) ? Items[Index]->GetComponentLocation() : GetComponentLocation();
}
FVector UWCHeroPresentationComponent::ItemTip(int Index) const
{
    if (!Items.IsValidIndex(Index)) return GetComponentLocation();
    for (const auto& Held : Grips) if (Held.Item == Items[Index])
    {
        const FTransform Placed = Held.Item->GetComponentTransform();
        return Placed.TransformPosition(Held.Point) + Placed.TransformVectorNoScale(Held.Tip).GetSafeNormal() * Held.Length * .9f;
    }
    return Items[Index]->GetComponentLocation();
}
void UWCHeroPresentationComponent::KickItem(int Index, float Centimetres)
{
    if (!Items.IsValidIndex(Index)) return;
    for (auto& Standing : Floats) if (Standing.Item == Items[Index]) Standing.Kick = Centimetres;
}
void UWCHeroPresentationComponent::FlamePoints(TFunctionRef<void(const FVector&, float)> Each) const
{
    for (const auto& Held : Grips) if (Held.bFlame && Held.Item && Held.Item->IsVisible())
        Each(Held.Item->GetComponentTransform().TransformPosition(Held.Flame), Held.FlameSize);
}
void UWCHeroPresentationComponent::HideItemFor(int Index, float HideSeconds)
{
    if (!Items.IsValidIndex(Index)) return;
    HiddenItems.Add(Index, HideSeconds);
    Items[Index]->SetVisibility(false, true);
}

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
        FString Motion;
        if (Config->TryGetStringField(TEXT("motion"), Motion)) StaticMotion = Motion == TEXT("walker") ? 1 : Motion == TEXT("flame") ? 2 : 0;
        const TSharedPtr<FJsonObject>* BodyLamp = nullptr;
        if (Config->TryGetObjectField(TEXT("light"), BodyLamp))
        {
            auto* Glow = NewObject<UPointLightComponent>(GetOwner());
            GetOwner()->AddInstanceComponent(Glow);
            Glow->SetupAttachment(StaticBody);
            Glow->SetRelativeLocation(Vector(*BodyLamp, TEXT("at")));
            const FVector Tint = Vector(*BodyLamp, TEXT("color"), FVector(1, .8f, .5f));
            Glow->SetLightColor(FLinearColor(Tint.X, Tint.Y, Tint.Z));
            Glow->bUseInverseSquaredFalloff = false; Glow->SetLightFalloffExponent(2);
            Glow->SetIntensity((*BodyLamp)->GetNumberField(TEXT("intensity")));
            Glow->SetAttenuationRadius((*BodyLamp)->GetNumberField(TEXT("radius")));
            Glow->SetCastShadows(false);
            Glow->RegisterComponent();
        }
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
    // "glows": lights that ride on a bone, placed by where they sit on the standing model (left +X, forward +Y).
    const TArray<TSharedPtr<FJsonValue>>* GlowList = nullptr;
    if (Config->TryGetArrayField(TEXT("glows"), GlowList))
        for (const auto& Value : *GlowList)
        {
            const TSharedPtr<FJsonObject> Entry = Value->AsObject();
            if (!Entry) continue;
            FWCGlow Glow;
            Glow.Bone = FName(*Entry->GetStringField(TEXT("bone")));
            const int32 GlowBone = Skeleton.FindBoneIndex(Glow.Bone);
            if (GlowBone < 0) continue;
            Glow.At = ReferenceTransform(Skeleton, GlowBone).InverseTransformPosition(Vector(Entry, TEXT("at")));
            const FVector Tint = Vector(Entry, TEXT("color"), FVector(1, 1, 1));
            Glow.Color = FLinearColor(Tint.X, Tint.Y, Tint.Z);
            Glow.Size = Entry->GetNumberField(TEXT("size"));
            Glows.Add(Glow);
        }
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
        // "clip_poses": {clip: {upper_direction, lower_direction}} holds the arm differently during those clips.
        const TSharedPtr<FJsonObject>* Poses = nullptr;
        if ((*Held)->TryGetObjectField(TEXT("clip_poses"), Poses))
            for (const auto& Pose : (*Poses)->Values)
            {
                const TSharedPtr<FJsonObject> Entry = Pose.Value->AsObject();
                if (!Entry) continue;
                const FVector UpperAim = Vector(Entry, TEXT("upper_direction")).GetSafeNormal(), LowerAim = Vector(Entry, TEXT("lower_direction")).GetSafeNormal();
                const FQuat UpperAimTurn = FQuat::FindBetweenNormals((LowerRef.GetLocation() - UpperRef.GetLocation()).GetSafeNormal(), UpperAim);
                const FQuat LowerAimTurn = FQuat::FindBetweenNormals(UpperAimTurn.RotateVector((HandRef.GetLocation() - LowerRef.GetLocation()).GetSafeNormal()), LowerAim);
                ArmPoses.Add(FName(*Pose.Key), TPair<FQuat, FQuat>(UpperAimTurn * UpperRef.GetRotation(), LowerAimTurn * UpperAimTurn * LowerRef.GetRotation()));
            }
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
    // "straighten": bones pulled toward the reference pose during the listed clips.
    const TSharedPtr<FJsonObject>* Stand = nullptr;
    if (Config->TryGetObjectField(TEXT("straighten"), Stand))
    {
        const TArray<TSharedPtr<FJsonValue>>* Names = nullptr;
        if ((*Stand)->TryGetArrayField(TEXT("bones"), Names)) for (const auto& Name : *Names) StraightBones.Add(FName(*Name->AsString()));
        if ((*Stand)->TryGetArrayField(TEXT("clips"), Names)) for (const auto& Name : *Names) StraightClips.Add(FName(*Name->AsString()));
        StraightAmount = (*Stand)->GetNumberField(TEXT("weight"));
    }
    // "stance": {"clips", "breathe_rate", "lower", "plant_feet", "bones": [{bone, axis, angle, breathe}]}, a pose laid over those clips
    // before arm reaches are solved, such as arms held out from the body. Axes are mesh space on the standing body.
    const TSharedPtr<FJsonObject>* Pose = nullptr;
    if (Config->TryGetObjectField(TEXT("stance"), Pose))
    {
        const FReferenceSkeleton& Reference = Mesh->GetRefSkeleton();
        const TArray<TSharedPtr<FJsonValue>>* Names = nullptr;
        if ((*Pose)->TryGetArrayField(TEXT("clips"), Names)) for (const auto& Name : *Names) StanceClips.Add(FName(*Name->AsString()));
        double Rate = 0;
        if ((*Pose)->TryGetNumberField(TEXT("breathe_rate"), Rate)) StanceRate = Rate;
        if ((*Pose)->TryGetNumberField(TEXT("lower"), Rate)) StanceLower = Rate;
        (*Pose)->TryGetBoolField(TEXT("plant_feet"), bStancePlant);
        if ((*Pose)->TryGetArrayField(TEXT("bones"), Names))
            for (const auto& Value : *Names)
            {
                const auto Entry = Value->AsObject();
                FWCStanceBend Bend;
                Bend.Bone = FName(*Entry->GetStringField(TEXT("bone")));
                const int32 Bone = Reference.FindBoneIndex(Bend.Bone);
                if (Bone == INDEX_NONE) { UE_LOG(LogTemp, Warning, TEXT("WC_HERO_STANCE_BONE_MISSING hero=%s bone=%s"), *HeroId, *Bend.Bone.ToString()); continue; }
                const FQuat Parent = ReferenceTransform(Reference, Reference.GetParentIndex(Bone)).GetRotation();
                Bend.Axis = Parent.Inverse().RotateVector(Vector(Entry, TEXT("axis"), FVector::XAxisVector).GetSafeNormal());
                Bend.Angle = Entry->GetNumberField(TEXT("angle"));
                double Breathe = 0;
                if (Entry->TryGetNumberField(TEXT("breathe"), Breathe)) Bend.Breathe = Breathe;
                Stance.Add(Bend);
            }
    }
    // "reaches": arms bent so a hand meets a point on the body or on something it carries, optionally beating.
    const TArray<TSharedPtr<FJsonValue>>* ReachList = nullptr;
    if (Config->TryGetArrayField(TEXT("reaches"), ReachList))
        for (const auto& Value : *ReachList)
        {
            const auto Entry = Value->AsObject();
            FWCSecondHand Reach;
            Reach.Upper = FName(*Entry->GetStringField(TEXT("upper")));
            Reach.Lower = FName(*Entry->GetStringField(TEXT("lower")));
            Reach.Hand = FName(*Entry->GetStringField(TEXT("hand")));
            Reach.Carrier = FName(*Entry->GetStringField(TEXT("carrier")));
            const FReferenceSkeleton& Reference = Mesh->GetRefSkeleton();
            const int32 Carrier = Reference.FindBoneIndex(Reach.Carrier);
            if (Carrier == INDEX_NONE) continue;
            // The point and the beat direction are given on the standing body and carried by the bone.
            const FTransform Carried = ReferenceTransform(Reference, Carrier);
            Reach.Target = Carried.InverseTransformPosition(Vector(Entry, TEXT("point")));
            Reach.Axis = Carried.InverseTransformVectorNoScale(Vector(Entry, TEXT("beat_axis"), FVector::ZAxisVector).GetSafeNormal());
            double Number = 0;
            if (Entry->TryGetNumberField(TEXT("beat"), Number)) Reach.Beat = Number;
            if (Entry->TryGetNumberField(TEXT("rate"), Number)) Reach.Rate = Number;
            if (Entry->TryGetNumberField(TEXT("phase"), Number)) Reach.Phase = Number;
            const TArray<TSharedPtr<FJsonValue>>* Names = nullptr;
            if (Entry->TryGetArrayField(TEXT("clips"), Names)) for (const auto& Name : *Names) Reach.Clips.Add(FName(*Name->AsString()));
            Reach.bValid = true;
            Reaches.Add(Reach);
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
                FVector Direction = Vector(*Grip, TEXT("rest_direction"), FVector::YAxisVector).GetSafeNormal();
                // "rest_forearm": the item continues the forearm's line in the reference pose, bent by this mesh-space
                // offset, so it hangs down beside a lowered arm the way a club or mallet is carried.
                if ((*Grip)->HasField(TEXT("rest_forearm")))
                    Direction = ((HandReference.GetLocation() - ArmReference.GetLocation()).GetSafeNormal() + Vector(*Grip, TEXT("rest_forearm"))).GetSafeNormal();
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
                (*Grip)->TryGetBoolField(TEXT("upright"), Rod.bUpright);
                (*Grip)->TryGetBoolField(TEXT("hang"), Rod.bHang);
                const TArray<TSharedPtr<FJsonValue>>* Aimed = nullptr;
                if ((*Grip)->TryGetArrayField(TEXT("aim_clips"), Aimed)) for (const auto& Name : *Aimed) Rod.AimClips.Add(FName(*Name->AsString()));
                const TSharedPtr<FJsonObject>* Touch = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("touch"), Touch))
                {
                    Rod.TouchItem = int((*Touch)->GetNumberField(TEXT("item")));
                    Rod.TouchAt = Vector(*Touch, TEXT("at"));
                    const TArray<TSharedPtr<FJsonValue>>* During = nullptr;
                    if ((*Touch)->TryGetArrayField(TEXT("clips"), During)) for (const auto& Name : *During) Rod.TouchClips.Add(FName(*Name->AsString()));
                }
                // "wrap": {"radius"}: the hand's fingers bend round the handle (see WrapFingers).
                const TSharedPtr<FJsonObject>* Wrap = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("wrap"), Wrap))
                {
                    Rod.WrapRadius = (*Wrap)->GetNumberField(TEXT("radius"));
                    const TArray<TSharedPtr<FJsonValue>>* Seat = nullptr;
                    if ((*Wrap)->TryGetArrayField(TEXT("seat"), Seat) && Seat->Num() == 2) Rod.WrapSeat = FVector2D((*Seat)[0]->AsNumber(), (*Seat)[1]->AsNumber());
                }
                // "wrist": {"rest_bend", "rest_max", "strike_max", "rest_clips"}: the hand turns to point the item.
                const TSharedPtr<FJsonObject>* Hold = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("wrist"), Hold))
                {
                    Rod.bWrist = true;
                    Rod.WristBend = Vector(*Hold, TEXT("rest_bend"));
                    double Degrees = 0;
                    if ((*Hold)->TryGetNumberField(TEXT("rest_max"), Degrees)) Rod.WristRestMax = Degrees;
                    if ((*Hold)->TryGetNumberField(TEXT("strike_max"), Degrees)) Rod.WristStrikeMax = Degrees;
                    const TArray<TSharedPtr<FJsonValue>>* During = nullptr;
                    if ((*Hold)->TryGetArrayField(TEXT("rest_clips"), During)) for (const auto& Name : *During) Rod.WristRestClips.Add(FName(*Name->AsString()));
                }
                const TSharedPtr<FJsonObject>* Strike = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("strike"), Strike))
                {
                    Rod.StrikeItem = int((*Strike)->GetNumberField(TEXT("item")));
                    Rod.StrikeAt = Vector(*Strike, TEXT("at"));
                    double Snap = 0;
                    if ((*Strike)->TryGetNumberField(TEXT("snap"), Snap)) Rod.StrikeSnap = Snap;
                    const TArray<TSharedPtr<FJsonValue>>* During = nullptr;
                    if ((*Strike)->TryGetArrayField(TEXT("clips"), During)) for (const auto& Name : *During) Rod.StrikeClips.Add(FName(*Name->AsString()));
                }
                const TSharedPtr<FJsonObject>* Fire = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("flame"), Fire))
                {
                    Rod.bFlame = true; Rod.Flame = Vector(*Fire, TEXT("at"));
                    double Big = 1;
                    if ((*Fire)->TryGetNumberField(TEXT("size"), Big)) Rod.FlameSize = Big;
                }
                // "second_hand": the other arm reaches a second point on this weapon during the listed clips.
                const TSharedPtr<FJsonObject>* Other = nullptr;
                if ((*Grip)->TryGetObjectField(TEXT("second_hand"), Other))
                {
                    SecondHand.Upper = FName(*(*Other)->GetStringField(TEXT("upper")));
                    SecondHand.Lower = FName(*(*Other)->GetStringField(TEXT("lower")));
                    SecondHand.Hand = FName(*(*Other)->GetStringField(TEXT("hand")));
                    SecondHand.Carrier = Bone;
                    SecondHand.Target = Offset.TransformPosition(Vector(*Other, TEXT("point")));
                    SecondHand.bValid = true;
                    const TArray<TSharedPtr<FJsonValue>>* Names = nullptr;
                    if ((*Other)->TryGetArrayField(TEXT("clips"), Names)) for (const auto& Name : *Names) SecondHandClips.Add(FName(*Name->AsString()));
                }
                Grips.Add(Rod);
            }
            // "float" items hover at a mesh-space spot of the reference pose and ride the named bone.
            const TSharedPtr<FJsonObject>* Hover = nullptr;
            if (Entry->TryGetObjectField(TEXT("float"), Hover) && Hand != INDEX_NONE)
            {
                // It rides the hero as a whole rather than a bone, so body motion does not swing it around.
                Item->SetupAttachment(Skeletal);
                const FTransform Carrier = FTransform::Identity;
                Offset = FTransform(FQuat::Identity, Vector(*Hover, TEXT("at")), FVector(Entry->GetNumberField(TEXT("scale"))));
                FWCFloatItem Drift;
                Drift.Item = Item; Drift.Base = Offset; Drift.Up = Carrier.InverseTransformVector(FVector::ZAxisVector);
                double Number = 0;
                if ((*Hover)->TryGetNumberField(TEXT("bob"), Number)) Drift.Bob = Number;
                if ((*Hover)->TryGetNumberField(TEXT("spin"), Number)) Drift.Spin = Number;
                if ((*Hover)->TryGetNumberField(TEXT("phase"), Number)) Drift.Phase = Number;
                Floats.Add(Drift);
            }
            // "ground" items stand on the floor beside the hero and travel with it; a round one rolls as it goes.
            const TSharedPtr<FJsonObject>* Floor = nullptr;
            if (Entry->TryGetObjectField(TEXT("ground"), Floor))
            {
                Item->SetupAttachment(Skeletal);
                Offset = FTransform(FRotator(Rotation.X, Rotation.Y, Rotation.Z), Vector(*Floor, TEXT("at")), FVector(Entry->GetNumberField(TEXT("scale"))));
                FWCFloatItem Standing;
                Standing.Item = Item; Standing.Base = Offset; Standing.Bob = 0; Standing.Spin = 0; Standing.bGround = true;
                double Number = 0;
                if ((*Floor)->TryGetNumberField(TEXT("roll_rate"), Number)) Standing.RollRate = Number;
                Floats.Add(Standing);
            }
            // "mesh_space" items are fixed to a bone but placed by where they sit on the standing body.
            bool bMeshSpace = false;
            if (Entry->TryGetBoolField(TEXT("mesh_space"), bMeshSpace) && bMeshSpace && Hand != INDEX_NONE)
                Offset = Offset.GetRelativeTransform(ReferenceTransform(Bones, Hand));
            Item->SetRelativeTransform(Offset);
            // "solid": {"from", "to", "radius", "limb_margin"}, a cylinder in item space that arms and held items keep out of.
            const TSharedPtr<FJsonObject>* Solid = nullptr;
            if (Entry->TryGetObjectField(TEXT("solid"), Solid) && Hand != INDEX_NONE)
            {
                FWCSolid Shape;
                Shape.Carrier = Bone;
                Shape.Base = Offset.TransformPosition(Vector(*Solid, TEXT("from")));
                const FVector Top = Offset.TransformPosition(Vector(*Solid, TEXT("to")));
                Shape.Axis = (Top - Shape.Base).GetSafeNormal();
                Shape.Height = FVector::Dist(Top, Shape.Base);
                Shape.Radius = (*Solid)->GetNumberField(TEXT("radius")) * Offset.GetScale3D().X;
                double Margin = 0;
                if ((*Solid)->TryGetNumberField(TEXT("limb_margin"), Margin)) Shape.LimbMargin = Margin;
                Solids.Add(Shape);
            }
            // "light": a small lamp carried by the item, such as a lantern's flame.
            const TSharedPtr<FJsonObject>* Lamp = nullptr;
            if (Entry->TryGetObjectField(TEXT("light"), Lamp))
            {
                auto* Glow = NewObject<UPointLightComponent>(GetOwner());
                GetOwner()->AddInstanceComponent(Glow);
                Glow->SetupAttachment(Item);
                Glow->SetRelativeLocation(Vector(*Lamp, TEXT("at")));
                const FVector Tint = Vector(*Lamp, TEXT("color"), FVector(1, .8f, .5f));
                Glow->SetLightColor(FLinearColor(Tint.X, Tint.Y, Tint.Z));
                Glow->bUseInverseSquaredFalloff = false; Glow->SetLightFalloffExponent(2);
                Glow->SetIntensity((*Lamp)->GetNumberField(TEXT("intensity")));
                Glow->SetAttenuationRadius((*Lamp)->GetNumberField(TEXT("radius")));
                Glow->SetCastShadows(false);
                Glow->RegisterComponent();
            }
            Item->RegisterComponent();
            Items.Add(Item);
        }
    // Fingers that wrap the handle. On the standing body, each joint of each finger of the hand (a chain of curled
    // bones starting at a child of the hand) bends from straight until the next joint, or the fingertip for the last
    // one, touches a cylinder of the wrap radius round the stick's axis; a joint whose finger never reaches the
    // handle keeps its configured curl. The bends replace that hand's curls.
    const TArray<TSharedPtr<FJsonValue>>* CurlConfig = nullptr;
    if (Config->TryGetArrayField(TEXT("curls"), CurlConfig))
        for (auto& Holding : Grips)
        {
            if (Holding.WrapRadius <= 0) continue;
            const FReferenceSkeleton& Reference = Mesh->GetRefSkeleton();
            const int32 HandBone = Reference.FindBoneIndex(Holding.Bone);
            if (HandBone == INDEX_NONE) continue;
            TMap<int32, TPair<FVector, float>> Bendable;
            for (const auto& Value : *CurlConfig)
            {
                const auto Entry = Value->AsObject();
                const int32 Bone = Reference.FindBoneIndex(FName(*Entry->GetStringField(TEXT("bone"))));
                if (Bone != INDEX_NONE) Bendable.Add(Bone, {Vector(Entry, TEXT("axis"), FVector::XAxisVector).GetSafeNormal(), float(Entry->GetNumberField(TEXT("angle")))});
            }
            const FTransform HandReference = ReferenceTransform(Reference, HandBone);
            if (!Holding.WrapSeat.IsZero())
            {
                // Seat the handle in the fist: along the line from the little finger's knuckle to the index finger's,
                // out from the knuckles the way the fingers curl and back towards the wrist.
                FVector Knuckles = FVector::ZeroVector, Fingers = FVector::ZeroVector, Curl = FVector::ZeroVector, IndexKnuckle, PinkyKnuckle;
                int32 Count = 0;
                bool bIndex = false, bPinky = false;
                for (const auto& First : Bendable)
                {
                    const FString Name = Reference.GetBoneName(First.Key).ToString();
                    if (Reference.GetParentIndex(First.Key) != HandBone || Name.Contains(TEXT("Thumb"))) continue;
                    int32 Child = INDEX_NONE;
                    for (const auto& Next : Bendable) if (Reference.GetParentIndex(Next.Key) == First.Key) Child = Next.Key;
                    if (Child == INDEX_NONE) continue;
                    const FVector Knuckle = ReferenceTransform(Reference, First.Key).GetLocation();
                    const FVector Finger = (ReferenceTransform(Reference, Child).GetLocation() - Knuckle).GetSafeNormal();
                    Knuckles += Knuckle; Fingers += Finger; Curl += FQuat(First.Value.Key, UE_HALF_PI).RotateVector(Finger); ++Count;
                    if (Name.Contains(TEXT("Index"))) { IndexKnuckle = Knuckle; bIndex = true; }
                    if (Name.Contains(TEXT("Pinky"))) { PinkyKnuckle = Knuckle; bPinky = true; }
                }
                if (Count >= 2 && bIndex && bPinky)
                {
                    const FVector Line = (IndexKnuckle - PinkyKnuckle).GetSafeNormal();
                    const FVector Center = Knuckles / Count + Curl.GetSafeNormal() * Holding.WrapSeat.X - Fingers.GetSafeNormal() * Holding.WrapSeat.Y;
                    const float Scale = Holding.Base.GetScale3D().X;
                    const FQuat Aim = FQuat::FindBetweenNormals(Holding.Tip, Line);
                    Holding.Base = FTransform(Aim, Center - Aim.RotateVector(Holding.Point * Scale), FVector(Scale)).GetRelativeTransform(HandReference);
                    Holding.Item->SetRelativeTransform(Holding.Base);
                }
            }
            const FVector AxisPoint = HandReference.TransformPosition(Holding.Base.TransformPosition(Holding.Point));
            const FVector AxisLine = HandReference.TransformVectorNoScale(Holding.Base.TransformVectorNoScale(Holding.Tip)).GetSafeNormal();
            const auto FromHandle = [&](const FVector& Point) {
                const FVector Offset = Point - AxisPoint;
                return (Offset - AxisLine * FVector::DotProduct(Offset, AxisLine)).Size();
            };
            for (const auto& First : Bendable)
            {
                if (Reference.GetParentIndex(First.Key) != HandBone) continue;
                TArray<int32> Chain = {First.Key};
                for (bool bMore = true; bMore;)
                {
                    bMore = false;
                    for (const auto& Next : Bendable)
                        if (Reference.GetParentIndex(Next.Key) == Chain.Last()) { Chain.Add(Next.Key); bMore = true; break; }
                }
                TArray<FVector> Points, Axes;
                for (const int32 Bone : Chain) { Points.Add(ReferenceTransform(Reference, Bone).GetLocation()); Axes.Add(Bendable[Bone].Key); }
                const FVector Last = Points.Num() > 1 ? Points.Last() - Points[Points.Num() - 2] : FVector::ZeroVector;
                Points.Add(Points.Last() + Last * .8f);
                FString Report;
                for (int32 Joint = 0; Joint < Chain.Num(); ++Joint)
                {
                    float Angle = Bendable[Chain[Joint]].Value;
                    bool bTouch = false;
                    // A joint already against the handle while straight (a thumb whose base the handle passes) keeps
                    // its configured curl.
                    const bool bAgainst = FromHandle(Points[Joint + 1]) <= Holding.WrapRadius;
                    for (float Trial = 2; Trial <= 110 && !bAgainst; Trial += 2)
                        if (FromHandle(Points[Joint] + FQuat(Axes[Joint], FMath::DegreesToRadians(Trial)).RotateVector(Points[Joint + 1] - Points[Joint])) <= Holding.WrapRadius)
                        { Angle = Trial; bTouch = true; break; }
                    const FQuat Bend(Axes[Joint], FMath::DegreesToRadians(Angle));
                    for (int32 Later = Joint + 1; Later < Points.Num(); ++Later) Points[Later] = Points[Joint] + Bend.RotateVector(Points[Later] - Points[Joint]);
                    for (int32 Later = Joint + 1; Later < Axes.Num(); ++Later) Axes[Later] = Bend.RotateVector(Axes[Later]);
                    const FQuat Parent = ReferenceTransform(Reference, Reference.GetParentIndex(Chain[Joint])).GetRotation();
                    for (auto& Curl : Curls)
                        if (Curl.Bone == Reference.GetBoneName(Chain[Joint]))
                            Curl.ParentSpace = Parent.Inverse() * FQuat(Bendable[Chain[Joint]].Key, FMath::DegreesToRadians(Angle)) * Parent;
                    Report += FString::Printf(TEXT(" %s=%.0f%s"), *Reference.GetBoneName(Chain[Joint]).ToString(), Angle, bTouch ? TEXT("") : bAgainst ? TEXT("(against)") : TEXT("(no touch)"));
                }
                UE_LOG(LogTemp, Display, TEXT("WC_HERO_WRAP hero=%s%s"), *HeroId, *Report);
            }
        }
    for (int32 Index = 0; Index < Grips.Num(); ++Index)
    {
        const auto& Gripped = Grips[Index];
        if (!Gripped.bWrist) continue;
        FWCWristAim Wrist;
        Wrist.Hand = Gripped.Bone;
        Wrist.Grip = Gripped.Base.TransformPosition(Gripped.Point);
        Wrist.Tip = Gripped.Base.TransformVectorNoScale(Gripped.Tip).GetSafeNormal();
        Wrist.RestBend = Gripped.WristBend; Wrist.RestMax = Gripped.WristRestMax; Wrist.StrikeMax = Gripped.WristStrikeMax;
        if (Items.IsValidIndex(Gripped.StrikeItem))
        {
            Wrist.Carrier = Items[Gripped.StrikeItem]->GetAttachSocketName();
            Wrist.Spot = Items[Gripped.StrikeItem]->GetRelativeTransform().TransformPosition(Gripped.StrikeAt);
            Wrist.Snap = Gripped.StrikeSnap;
        }
        Wrists.Add(Wrist); WristGrips.Add(Index);
    }
    if (Grips.ContainsByPredicate([](const FWCGripItem& Held) { return Held.StrikeItem >= 0; }))
        Skeletal->RegisterOnBoneTransformsFinalizedDelegate(
            FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this, &UWCHeroPresentationComponent::PlaceStrikes));
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
        if (const auto* Pose = ArmPoses.Find(Current)) { Instance->HeldArm.UpperHeld = Pose->Key; Instance->HeldArm.LowerHeld = Pose->Value; }
        Instance->Curls = Curls;
        SecondHand.Weight = FMath::FInterpTo(SecondHand.Weight, SecondHandClips.Contains(Current) ? 1.f : 0.f, DeltaSeconds, 9);
        Instance->SecondHand = SecondHand;
        for (auto& Reach : Reaches) Reach.Weight = FMath::FInterpTo(Reach.Weight, Reach.Clips.Contains(Current) ? 1.f : 0.f, DeltaSeconds, 9);
        Instance->Reaches = Reaches; Instance->ReachTime = Clock;
        StraightNow = FMath::FInterpTo(StraightNow, StraightClips.Contains(Current) ? StraightAmount : 0.f, DeltaSeconds, 7);
        Instance->StraightBones = StraightBones; Instance->StraightWeight = StraightNow;
        StanceNow = FMath::FInterpTo(StanceNow, StanceClips.Contains(Current) ? 1.f : 0.f, DeltaSeconds, 5);
        Instance->Stance = Stance; Instance->StanceWeight = StanceNow; Instance->StanceRate = StanceRate; Instance->StanceLower = StanceLower; Instance->bStancePlant = bStancePlant;
        for (int32 Index = 0; Index < Wrists.Num(); ++Index)
        {
            const auto& Held = Grips[WristGrips[Index]];
            Wrists[Index].RestWeight = FMath::FInterpTo(Wrists[Index].RestWeight, Held.WristRestClips.Contains(Current) ? 1.f : 0.f, DeltaSeconds, 6);
            Wrists[Index].StrikeWeight = Held.StrikeWeight;
        }
        Instance->Solids = Solids; Instance->Wrists = Wrists;
    }
    ClearBody(DeltaSeconds);
    Clock += DeltaSeconds;
    for (const auto& Drift : Floats)
    {
        FTransform Placed = Drift.Base;
        Placed.SetLocation(Drift.Base.GetLocation() + Drift.Up * Drift.Bob * FMath::Sin(Clock * 1.7f + Drift.Phase));
        Placed.SetRotation(FQuat(Drift.Up.GetSafeNormal(), FMath::DegreesToRadians(Clock * Drift.Spin)) * Drift.Base.GetRotation());
        if (Drift.bGround)
        {
            // Rolled forward (about the hero's left-right axis) only while walking.
            const_cast<FWCFloatItem&>(Drift).Roll += Current == TEXT("Move") ? DeltaSeconds * Drift.RollRate : 0;
            Placed.SetRotation(FQuat(FVector::XAxisVector, FMath::DegreesToRadians(-Drift.Roll)) * Drift.Base.GetRotation());
            // Recoil: knocked straight back and a little up, then rolled forward into place again.
            const_cast<FWCFloatItem&>(Drift).Kick = FMath::FInterpTo(Drift.Kick, 0, DeltaSeconds, 5);
            Placed.AddToTranslation(FVector(0, -Drift.Kick, Drift.Kick * .12f));
        }
        Drift.Item->SetRelativeTransform(Placed);
    }
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
        if (Held.bHang)
        {
            // It hangs from the hand under its own weight and trails a little behind the hand's motion.
            const FVector Moved = Held.LastGrip.IsZero() || DeltaSeconds <= 0 ? FVector::ZeroVector : (Grip - Held.LastGrip) / DeltaSeconds;
            Held.LastGrip = Grip;
            const FVector Wanted = (FVector(0, 0, -1) - Moved.GetClampedToMaxSize(260) * .0035f).GetSafeNormal();
            Held.Swing = FMath::VInterpTo(Held.Swing, Wanted, DeltaSeconds, 7).GetSafeNormal();
            if (Held.Swing.IsNearlyZero()) Held.Swing = FVector(0, 0, -1);
            const FQuat Drop = FQuat::FindBetweenNormals(Along, Held.Swing);
            FTransform Placed = Rest;
            Placed.SetRotation(Drop * Rest.GetRotation());
            Placed.SetLocation(Grip + Drop.RotateVector(Rest.GetLocation() - Grip));
            Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
            continue;
        }
        if (Held.TouchClips.Num() && Items.IsValidIndex(Held.TouchItem) && Current != TEXT("Defeat"))
        {
            // Lowered for the first moments of the clip, then carried upright again until the next one.
            const bool bTouching = Held.TouchClips.Contains(Current) && Seconds < .5f;
            // The tip is brought down to the other item: the item turns about the grip to point at that spot.
            const FVector Spot = Skeletal->GetComponentTransform().InverseTransformPosition(
                Items[Held.TouchItem]->GetComponentTransform().TransformPosition(Held.TouchAt));
            const FQuat Wanted = FQuat::FindBetweenNormals(Along, bTouching ? (Spot - Grip).GetSafeNormal() : FVector(0, .1f, 1).GetSafeNormal());
            Held.Clearance = FQuat::Slerp(Held.Clearance, Wanted, FMath::Clamp(DeltaSeconds * (bTouching ? 22 : 7), 0.f, 1.f)).GetNormalized();
            FTransform Placed = Rest;
            Placed.SetRotation(Held.Clearance * Rest.GetRotation());
            Placed.SetLocation(Grip + Held.Clearance.RotateVector(Rest.GetLocation() - Grip));
            Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
            continue;
        }
        if (Held.StrikeClips.Num() && Items.IsValidIndex(Held.StrikeItem))
        {
            Held.StrikeWeight = FMath::FInterpTo(Held.StrikeWeight, Held.StrikeClips.Contains(Current) ? 1.f : 0.f, DeltaSeconds, 12);
            // While striking, PlaceStrikes places it once this frame's bones are final.
            if (Held.StrikeWeight > .01f) { Held.Clearance = FQuat::Identity; continue; }
        }
        if (Held.AimClips.Contains(Current))
        {
            // Levelled at the enemy: the item points straight ahead of the hero, pivoting about the grip.
            const FQuat Level = FQuat::FindBetweenNormals(Along, FVector(0, 1, .03f).GetSafeNormal());
            FTransform Placed = Rest;
            Placed.SetRotation(Level * Rest.GetRotation());
            Placed.SetLocation(Grip + Level.RotateVector(Rest.GetLocation() - Grip));
            Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
            continue;
        }
        if (Held.bUpright && Current != TEXT("Defeat"))
        {
            // Stand the staff on end with a slight forward lean; no body clearance is needed for an upright staff.
            const FQuat Stand = FQuat::FindBetweenNormals(Along, FVector(0, .1f, 1).GetSafeNormal());
            FTransform Placed = Rest;
            Placed.SetRotation(Stand * Rest.GetRotation());
            Placed.SetLocation(Grip + Stand.RotateVector(Rest.GetLocation() - Grip));
            Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
            continue;
        }
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
        // Solid items (a drum): the deepest of a few points along the item decides a turn about the grip.
        for (int Pass = 0; Pass < 2; ++Pass)
            for (const auto& Solid : Solids)
            {
                const FTransform Carried = Skeletal->GetSocketTransform(Solid.Carrier, RTS_Component);
                const FVector Axis = Carried.TransformVectorNoScale(Solid.Axis).GetSafeNormal(), Base = Carried.TransformPosition(Solid.Base);
                FVector Deepest = FVector::ZeroVector, At = Grip;
                for (int Step = 1; Step <= 6; ++Step)
                {
                    const FVector Point = Grip + Turn.RotateVector(Along) * Held.Length * Step / 6.f;
                    const FVector Out = OutOfSolid(Point, Base, Axis, Solid.Height, Solid.Radius + Held.Radius);
                    if (Out.SizeSquared() > Deepest.SizeSquared()) { Deepest = Out; At = Point; }
                }
                const float Lever = FVector::Dist(At, Grip);
                if (Deepest.IsNearlyZero() || Lever < 8) continue;
                const FVector Hinge = FVector::CrossProduct(At - Grip, Deepest.GetSafeNormal()).GetSafeNormal();
                if (!Hinge.IsNearlyZero()) Turn = FQuat(Hinge, FMath::Min(FMath::Atan2(Deepest.Size(), Lever), .6f)) * Turn;
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

void UWCHeroPresentationComponent::PlaceStrikes()
{
    // Runs when this frame's bones are final. Placing a drumstick from the last frame's hand would let a quick
    // wrist turn of the arm reach swing the stick away from the drum for a frame or two.
    const auto* Instance = Skeletal ? Cast<UWCHeroAnimInstance>(Skeletal->GetAnimInstance()) : nullptr;
    if (!Instance) return;
    for (auto& Held : Grips)
    {
        if (Held.StrikeWeight <= .01f || !Items.IsValidIndex(Held.StrikeItem)) continue;
        const FTransform Hand = Skeletal->GetSocketTransform(Held.Bone, RTS_Component);
        const FTransform Rest = Held.Base * Hand;
        const FVector Grip = Rest.TransformPosition(Held.Point);
        const FVector Along = Rest.TransformVectorNoScale(Held.Tip).GetSafeNormal();
        // The head is aimed at the spot, lifted with this hand's beat so the stick flicks up between strikes.
        float Lift = 0;
        for (const auto& Reach : Instance->Reaches)
            if (Reach.Hand == Held.Bone) Lift = Reach.Weight * Reach.Beat * FMath::Max(0.f, FMath::Sin(Instance->ReachTime * Reach.Rate * UE_TWO_PI + Reach.Phase));
        const UStaticMeshComponent* Target = Items[Held.StrikeItem];
        const FTransform Carried = Target->GetRelativeTransform() * Skeletal->GetSocketTransform(Target->GetAttachSocketName(), RTS_Component);
        const FVector Spot = Carried.TransformPosition(Held.StrikeAt) + FVector(0, 0, Lift * Held.StrikeSnap);
        const FQuat Aim = FQuat::Slerp(FQuat::Identity, FQuat::FindBetweenNormals(Along, (Spot - Grip).GetSafeNormal()), Held.StrikeWeight);
        FTransform Placed = Rest;
        Placed.SetRotation(Aim * Rest.GetRotation());
        Placed.SetLocation(Grip + Aim.RotateVector(Rest.GetLocation() - Grip));
        Held.Item->SetRelativeTransform(Placed.GetRelativeTransform(Hand));
    }
}

void UWCHeroPresentationComponent::GlowPoints(TFunctionRef<void(const FVector&, const FLinearColor&, float)> Each) const
{
    if (!Skeletal) return;
    const float Scale = Skeletal->GetComponentScale().Z;
    for (const auto& Glow : Glows) Each(Skeletal->GetSocketTransform(Glow.Bone).TransformPosition(Glow.At), Glow.Color, Glow.Size * Scale);
}

FVector UWCHeroPresentationComponent::MuzzleLocation(int Index) const
{
    if (Floats.Num() && !Floats[0].bGround) return Floats[FMath::Abs(Index) % Floats.Num()].Item->GetComponentLocation();
    for (const auto& Held : Grips) if (Held.bUpright || Held.bHang || Held.AimClips.Num())
    {
        const FTransform Item = Held.Item->GetComponentTransform();
        return Item.TransformPosition(Held.Point) + Item.TransformVectorNoScale(Held.Tip).GetSafeNormal() * Held.Length * .92f;
    }
    if (Skeletal) return Skeletal->GetSocketLocation(TEXT("RightHand"));
    if (StaticBody) return StaticBody->GetComponentLocation() + FVector(0, 0, 110);
    return GetComponentLocation() + FVector(0, 0, 95);
}

FString UWCHeroPresentationComponent::Describe() const
{
    // One JSON fragment per frame for the frame recorder: the clip, the feet, and how each held item sits in its hand.
    const auto Point = [](const FVector& P) { return FString::Printf(TEXT("[%.1f,%.1f,%.1f]"), P.X, P.Y, P.Z); };
    FString Out = FString::Printf(TEXT("\"clip\":\"%s\",\"clip_s\":%.3f"), *Current.ToString(), Seconds);
    if (Skeletal)
    {
        Out += TEXT(",\"lfoot\":") + Point(Skeletal->GetSocketLocation(TEXT("LeftFoot"))) + TEXT(",\"rfoot\":") + Point(Skeletal->GetSocketLocation(TEXT("RightFoot")));
        Out += TEXT(",\"lhand\":") + Point(Skeletal->GetSocketLocation(TEXT("LeftHand"))) + TEXT(",\"rhand\":") + Point(Skeletal->GetSocketLocation(TEXT("RightHand")));
        Out += TEXT(",\"hips\":") + Point(Skeletal->GetSocketLocation(TEXT("Hips")));
    }
    Out += TEXT(",\"items\":[");
    bool First = true;
    for (const auto& Held : Grips)
    {
        const FTransform Item = Held.Item->GetComponentTransform();
        const FVector Grip = Item.TransformPosition(Held.Point), Hand = Skeletal->GetSocketLocation(Held.Bone);
        const FVector Tip = Grip + Item.TransformVectorNoScale(Held.Tip).GetSafeNormal() * Held.Length;
        // How deep the weapon's line passes into the torso: the distance from the spine line, in centimetres.
        FVector OnWeapon, OnBody;
        FMath::SegmentDistToSegmentSafe(Grip + (Tip - Grip) * .25f, Tip, Skeletal->GetSocketLocation(TEXT("Hips")), Skeletal->GetSocketLocation(TEXT("Head")), OnWeapon, OnBody);
        Out += FString::Printf(TEXT("%s{\"bone\":\"%s\",\"gap\":%.2f,\"grip\":%s,\"tip\":%s,\"spine_clearance\":%.1f}"), First ? TEXT("") : TEXT(","),
            *Held.Bone.ToString(), FVector::Dist(Grip, Hand), *Point(Grip), *Point(Tip), FVector::Dist(OnWeapon, OnBody));
        // How far the item has turned in the hand away from its grip there, in degrees (0: held as gripped).
        const FVector Rigid = (Held.Base * Skeletal->GetSocketTransform(Held.Bone)).TransformVectorNoScale(Held.Tip).GetSafeNormal();
        Out.InsertAt(Out.Len() - 1, FString::Printf(TEXT(",\"slip\":%.1f"), FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(
            FVector::DotProduct(Rigid, Item.TransformVectorNoScale(Held.Tip).GetSafeNormal()), -1., 1.)))));
        // A drumstick also reports the spot its head is aimed at, so strikes can be checked against the drum.
        if (Items.IsValidIndex(Held.StrikeItem))
            Out.InsertAt(Out.Len() - 1, TEXT(",\"spot\":") + Point(Items[Held.StrikeItem]->GetComponentTransform().TransformPosition(Held.StrikeAt)));
        First = false;
    }
    for (const auto& Drift : Floats)
    {
        Out += FString::Printf(TEXT("%s{\"float\":%s}"), First ? TEXT("") : TEXT(","), *Point(Drift.Item->GetComponentLocation()));
        First = false;
    }
    Out += TEXT("]");
    if (Solids.Num())
    {
        Out += TEXT(",\"solids\":[");
        for (int32 Index = 0; Index < Solids.Num(); ++Index)
        {
            const FTransform Body = Skeletal->GetSocketTransform(Solids[Index].Carrier);
            Out += FString::Printf(TEXT("%s{\"base\":%s,\"top\":%s,\"radius\":%.1f}"), Index ? TEXT(",") : TEXT(""),
                *Point(Body.TransformPosition(Solids[Index].Base)),
                *Point(Body.TransformPosition(Solids[Index].Base) + Body.TransformVectorNoScale(Solids[Index].Axis) * Solids[Index].Height),
                Solids[Index].Radius * Skeletal->GetComponentScale().X);
        }
        Out += TEXT("]");
    }
    return Out;
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
    if (StaticMotion == 1)
    {
        // A heavy walker: feet on the ground, a rolling waddle while it moves, recoil when it fires, and it topples when beaten.
        const bool Walking = State == wc::ActionState::Moving && !Defeated;
        Offset = FVector(0, 0, StaticLift + (Walking ? FMath::Abs(FMath::Sin(Clock * 7.5f)) * 5 : FMath::Sin(Clock * 3.2f) * .8f));
        Scale = FVector(StaticScale);
        Lean = Walking ? 4 : 0; Side = Walking ? FMath::Sin(Clock * 7.5f) * 6 : FMath::Sin(Clock * 3.2f) * .6f;
        if (StaticCasting) { Scale *= FVector(1 + Pulse * .05f, 1 + Pulse * .05f, 1 - Pulse * .06f); Offset.Y -= Pulse * 14; Lean -= Pulse * 7; }
        else { Offset.Y -= Pulse * 9; Lean -= Pulse * 4; }
        if (State == wc::ActionState::Stunned) Side += FMath::Sin(Clock * 30) * 2;
        if (Defeated) { const float Fall = FMath::Clamp(DefeatAge / .7f, 0.f, 1.f); Lean = -82 * Fall * Fall; Side = 0; Offset.Z = StaticLift * FMath::Lerp(1.f, .55f, Fall); }
    }
    else if (StaticMotion == 2)
    {
        // A living flame: it hovers higher, never holds one shape, and gutters out when beaten.
        Offset.Z += 22;
        const float Flicker = FMath::Sin(Clock * 11) * .035f + FMath::Sin(Clock * 17.3f) * .02f;
        if (!Defeated) Scale *= FVector(1 - Flicker * .6f, 1 - Flicker * .6f, 1 + Flicker);
        else { const float Fall = FMath::Clamp(DefeatAge / .6f, 0.f, 1.f); Scale = FVector(StaticScale * FMath::Lerp(1.f, .04f, Fall)); Offset.Z = StaticLift + 30; }
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
    for (auto It = HiddenItems.CreateIterator(); It; ++It)
    {
        It.Value() -= Paused ? 0 : DeltaSeconds;
        if (It.Value() > 0) continue;
        if (Items.IsValidIndex(It.Key())) Items[It.Key()]->SetVisibility(true, true);
        It.RemoveCurrent();
    }
    if (!Reviewing)
    {
        if (!Unit) { PlayedAction = 0; Play(TEXT("Idle"), true); }
        else if (Unit->health <= 0 || Unit->state == wc::ActionState::Defeated) Play(TEXT("Defeat"), false);
        else if (bCelebrate && Clips.Contains(TEXT("Taunt"))) Play(TEXT("Taunt"), true);
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
