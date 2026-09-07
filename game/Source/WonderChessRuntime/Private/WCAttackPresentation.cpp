#include "WCAttackPresentation.h"
#include "Animation/AnimSequence.h"

EWCAttackWindowStatus WCReadAttackWindows(const UAnimSequence* Animation, double WindupSeconds,
                                         wc::presentation::AttackWindows& Windows, FString& Error) {
  Error.Reset();
  if (!Animation) { Error = TEXT("Attack sequence missing"); return EWCAttackWindowStatus::Invalid; }
  static const TCHAR* Names[] = {TEXT("WC_Attack_R_Start"), TEXT("WC_Attack_R_Release"), TEXT("WC_Attack_R_End"),
                                 TEXT("WC_Attack_L_Start"), TEXT("WC_Attack_L_Release"), TEXT("WC_Attack_L_End")};
  double Times[6]{}; bool Found[6]{}; int Count = 0;
  for (const auto& Marker : Animation->AuthoredSyncMarkers) {
    const FString Name = Marker.MarkerName.ToString();
    if (!Name.StartsWith(TEXT("WC_Attack_"))) continue;
    int Index = -1;
    for (int Candidate = 0; Candidate < 6; ++Candidate) if (Name == Names[Candidate]) { Index = Candidate; break; }
    if (Index < 0 || Found[Index]) {
      Error = TEXT("Unknown or duplicate attack-window marker: ") + Name; return EWCAttackWindowStatus::Invalid;
    }
    Found[Index] = true; Times[Index] = Marker.Time; ++Count;
  }
  if (!Count) return EWCAttackWindowStatus::Absent;
  if (Count != 6) { Error = TEXT("Attack sequence requires all six window markers"); return EWCAttackWindowStatus::Invalid; }
  Windows = {{{Times[0], Times[1], Times[2]}, {Times[3], Times[4], Times[5]}}};
  std::string Reason;
  if (!wc::presentation::ValidateAttackWindows(Windows, Animation->GetPlayLength(), WindupSeconds, Reason)) {
    Error = UTF8_TO_TCHAR(Reason.c_str()); return EWCAttackWindowStatus::Invalid;
  }
  return EWCAttackWindowStatus::Valid;
}
