#pragma once
#include "CoreMinimal.h"
#include "Presentation/WCAttackWindow.h"
class UAnimSequence;
enum class EWCAttackWindowStatus { Absent, Valid, Invalid };
EWCAttackWindowStatus WCReadAttackWindows(const UAnimSequence* Animation, double WindupSeconds,
                                         wc::presentation::AttackWindows& Windows, FString& Error);
