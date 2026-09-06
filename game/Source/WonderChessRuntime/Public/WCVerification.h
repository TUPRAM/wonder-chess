#pragma once
#include "CoreMinimal.h"
class AWCMatchController;
void WCTickVerification(AWCMatchController *Controller, float Delta);
void WCRecordVerificationReply(AWCMatchController *Controller, bool Accepted,
                               const FString &Reason);
