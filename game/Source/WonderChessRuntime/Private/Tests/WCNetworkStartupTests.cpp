#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "WCNetworkSession.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FWCNetworkStartupTest, "WonderChess.Network.StartupEndpointValidation",
    EAutomationTestFlags_ApplicationContextMask |
        EAutomationTestFlags::EngineFilter)
bool FWCNetworkStartupTest::RunTest(const FString &Parameters) {
  FString Result;
  TestTrue(
      TEXT("Loopback and explicit nondefault port"),
      UWCNetworkSession::NormalizeJoinAddress(TEXT("127.0.0.1:7780"), Result));
  TestEqual(TEXT("Canonical endpoint"), Result,
            FString(TEXT("127.0.0.1:7780")));
  TestTrue(
      TEXT("LAN address with default port"),
      UWCNetworkSession::NormalizeJoinAddress(TEXT("192.168.1.20"), Result));
  TestEqual(TEXT("Default game port"), Result,
            FString(TEXT("192.168.1.20:7777")));
  for (const TCHAR *Invalid :
       {TEXT(""), TEXT("localhost"), TEXT("256.1.2.3"), TEXT("1.2.3"),
        TEXT("1.2.3.4.5"), TEXT("1..3.4"), TEXT("1.2.3.-1"), TEXT("1.2.3.4:0"),
        TEXT("1.2.3.4:65536"), TEXT("1.2.3.4:"), TEXT("1.2.3.4:abc"),
        TEXT("1.2.3.4:7777?listen"), TEXT("1.2.3.4:7777:80"),
        TEXT("/Game/WonderChess/Maps/L_WC_Menu"), TEXT("https://example.com"),
        TEXT(" 127.0.0.1")}) {
    TestFalse(FString::Printf(TEXT("Reject %s"), Invalid),
              UWCNetworkSession::NormalizeJoinAddress(Invalid, Result));
    TestTrue(TEXT("No partial address on rejection"), Result.IsEmpty());
  }
  return !HasAnyErrors();
}
#endif
