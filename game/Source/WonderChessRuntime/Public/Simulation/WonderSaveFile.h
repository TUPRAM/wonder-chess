#pragma once
#include <filesystem>
#include <string>

namespace wc
{
class Match;
enum class PreparationSaveStatus
{
    Saved,
    Loaded,
    RecoveredPrevious,
    Ineligible,
    Missing,
    Invalid,
    IoError
};
struct PreparationSaveResult
{
    PreparationSaveStatus status = PreparationSaveStatus::IoError;
    std::string message;
    bool Succeeded() const
    {
        return status == PreparationSaveStatus::Saved || status == PreparationSaveStatus::Loaded ||
               status == PreparationSaveStatus::RecoveredPrevious;
    }
};

// Writes a validated offline preparation snapshot, retaining the last valid primary in
// <path>.previous. Uncommitted <path>.pending files are never offered as recovery saves.
// An incompatible/corrupt primary is preserved and must be moved aside before saving again.
PreparationSaveResult SavePreparationFile(const Match &match, const std::filesystem::path &path);
// Tries the primary and then its previous snapshot. A failed load never changes the match.
// Recovery is reported explicitly and preserves both files for diagnosis.
PreparationSaveResult LoadPreparationFile(Match &match, const std::filesystem::path &path);
} // namespace wc
