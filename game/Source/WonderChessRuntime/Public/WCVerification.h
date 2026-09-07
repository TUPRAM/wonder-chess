#pragma once
#include "CoreMinimal.h"
class AWCMatchController;
// Read-only clock shared by frame CSV and front-end stage markers.
bool WCReadVerificationClock(AWCMatchController *Controller, double &WallSeconds,
                             FString &FrameCsvPath);
void WCTickVerification(AWCMatchController *Controller, float Delta);
void WCRecordVerificationReply(AWCMatchController *Controller, bool Accepted,
                               const FString &Reason, int64 Request = 0);
