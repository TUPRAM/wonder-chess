#if WITH_DEV_AUTOMATION_TESTS
#include "WCAttackPresentation.h"
#include "Animation/AnimSequence.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWCAttackWindowMetadataTest, "WonderChess.Presentation.AttackWindowMetadata",
    EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::EngineFilter)
bool FWCAttackWindowMetadataTest::RunTest(const FString& Parameters) {
  wc::presentation::AttackWindows Windows;
  FString Error;
  TestTrue(TEXT("Missing animation rejected"), WCReadAttackWindows(nullptr, .25, Windows, Error) == EWCAttackWindowStatus::Invalid);
  auto* Sequence = NewObject<UAnimSequence>();
  TestTrue(TEXT("Ordinary unmarked animation remains supported"), WCReadAttackWindows(Sequence, .25, Windows, Error) == EWCAttackWindowStatus::Absent);
  FAnimSyncMarker Marker; Marker.MarkerName = TEXT("WC_Attack_R_Start"); Marker.Time = 0;
  Sequence->AuthoredSyncMarkers.Add(Marker);
  TestTrue(TEXT("Partial marker set rejected"), WCReadAttackWindows(Sequence, .25, Windows, Error) == EWCAttackWindowStatus::Invalid);
  Sequence->AuthoredSyncMarkers.Add(Marker);
  TestTrue(TEXT("Duplicate marker rejected"), WCReadAttackWindows(Sequence, .25, Windows, Error) == EWCAttackWindowStatus::Invalid && Error.Contains(TEXT("duplicate")));
  Sequence->AuthoredSyncMarkers.Reset(); Marker.MarkerName = TEXT("WC_Attack_Unexpected"); Sequence->AuthoredSyncMarkers.Add(Marker);
  TestTrue(TEXT("Unknown owned marker rejected"), WCReadAttackWindows(Sequence, .25, Windows, Error) == EWCAttackWindowStatus::Invalid);
  Sequence->AuthoredSyncMarkers.Reset(); Marker.MarkerName = TEXT("Footstep"); Sequence->AuthoredSyncMarkers.Add(Marker);
  TestTrue(TEXT("Unrelated sync markers ignored"), WCReadAttackWindows(Sequence, .25, Windows, Error) == EWCAttackWindowStatus::Absent);
  const wc::presentation::AttackWindows Valid{{{0,.25,.65},{.65,.90,1.30}}};
  std::string Reason;
  TestTrue(TEXT("Validated complete window contract"), wc::presentation::ValidateAttackWindows(Valid, 1.3, .25, Reason));
  const auto Right = wc::presentation::SampleAttack(Valid, 1, .25), Left = wc::presentation::SampleAttack(Valid, 2, .25);
  TestTrue(TEXT("Right and left each release250ms after their starts"), Right.window == 0 && Left.window == 1 &&
      FMath::Abs(Right.position - .25) < .0001 && FMath::Abs(Left.position - .90) < .0001);
  TestTrue(TEXT("Long recovery cannot enter second cut"), wc::presentation::SampleAttack(Valid, 1, 10).position == .65);
  return true;
}
#endif
