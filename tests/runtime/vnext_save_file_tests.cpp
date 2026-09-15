#include "Simulation/WonderSaveFile.h"
#include "VNext/WonderVNextCatalog.generated.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#if defined(_WIN32)
#define NOMINMAX
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#endif

namespace
{
namespace fs = std::filesystem;
using Status = wc::PreparationSaveStatus;
int checks = 0;
void Check(bool condition, const std::string &message)
{
    ++checks;
    if (!condition) throw std::runtime_error(message);
}
fs::path Suffix(fs::path path, const char *suffix) { path += suffix; return path; }
std::string Read(const fs::path &path)
{
    std::ifstream file(path, std::ios::binary);
    if (!file) throw std::runtime_error("Cannot read test fixture");
    return std::string(std::istreambuf_iterator<char>(file), {});
}
void Write(const fs::path &path, const std::string &bytes)
{
    fs::create_directories(path.parent_path());
    std::ofstream file(path, std::ios::binary);
    file.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!file) throw std::runtime_error("Cannot write test fixture");
}
void AdvanceTo(wc::Match &match, int round)
{
    for (int tick = 0; tick < 200000; ++tick)
    {
        if (match.Round() == round && match.CurrentPhase() == wc::Phase::Preparation) return;
        if (match.CurrentPhase() == wc::Phase::Finished || match.CurrentPhase() == wc::Phase::Aborted) break;
        match.Tick(match.Definitions().rules.tickMs);
    }
    throw std::runtime_error("Expected preparation round was not reached");
}
std::string Complete(wc::Match &match)
{
    for (int tick = 0; tick < 200000 && match.CurrentPhase() != wc::Phase::Finished; ++tick)
    {
        match.Tick(match.Definitions().rules.tickMs);
        if (match.CurrentPhase() == wc::Phase::Aborted) throw std::runtime_error("Tournament aborted");
    }
    Check(match.CurrentPhase() == wc::Phase::Finished, "resumed tournament finishes");
    Check(match.InvariantError().empty(), "finished tournament invariants");
    std::string result;
    for (const auto &record : match.Records()) result += std::to_string(record.postHash) + "\n";
    for (const auto &seat : match.Seats())
        result += std::to_string(seat.health) + ":" + std::to_string(seat.placement) + ":" +
                  std::to_string(seat.shopRng.state) + ":" + std::to_string(seat.botRng.state) + ":" +
                  std::to_string(seat.relicRng.state) + "\n";
    return result;
}
void Roundtrip(const wc::Catalog &catalog, const fs::path &root)
{
    const auto path = root / fs::path(L"unicode-\u732b") / "preparation.wcsave";
    wc::Match original(catalog, 8131, 0);
    AdvanceTo(original, 4);
    const auto first = original.SavePreparation();
    Check(!first.empty() && !original.Seats()[0].relicOffers.empty(), "snapshot includes round history and relic draft");
    const auto originalNamespace = original.Namespace();
    auto saved = wc::SavePreparationFile(original, path);
    Check(saved.status == Status::Saved && saved.Succeeded(), "initial durable save: " + saved.message);
    Check(Read(path) == first, "disk bytes equal logical snapshot");
    Check(original.SavePreparation() == first && original.Namespace() == originalNamespace, "save never changes source match");
    Check(!fs::exists(Suffix(path, ".previous")), "first save does not invent a backup");
    Check(!fs::exists(Suffix(path, ".pending")), "committed staging name no longer exists");
    original.Tick(catalog.rules.tickMs);
    const auto second = original.SavePreparation();
    Check(second != first && !second.empty(), "new preparation has real progressed decisions");
    saved = wc::SavePreparationFile(original, path);
    Check(saved.status == Status::Saved, "replacement succeeds: " + saved.message);
    Check(Read(path) == second && Read(Suffix(path, ".previous")) == first, "atomic replacement retains previous exact snapshot");
    wc::Match restored(catalog, 7, 1);
    auto loaded = wc::LoadPreparationFile(restored, path);
    Check(loaded.status == Status::Loaded && loaded.Succeeded(), "primary loads explicitly");
    Check(restored.SavePreparation() == second && restored.Namespace() != originalNamespace, "exact state and streams, fresh authority namespace");
    Check(Complete(original) == Complete(restored), "disk recovery preserves every later round hash, placement and RNG stream");
    std::cout << "PASS roundtrip_history_relics_streams_and_full_tournament\n";
}
void InterruptedWrites(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match firstMatch(catalog, 71, 1), secondMatch(catalog, 91, 1);
    const auto first = firstMatch.SavePreparation(), second = secondMatch.SavePreparation();
    const std::vector<std::string> pendingStates = {"", second.substr(0, second.size() / 2), second};
    for (std::size_t stage = 0; stage < pendingStates.size(); ++stage)
    {
        const auto path = root / ("interrupt-" + std::to_string(stage)) / "save";
        Write(path, first);
        Write(Suffix(path, ".pending"), pendingStates[stage]);
        Write(Suffix(path, ".previous.pending"), first.substr(0, first.size() / 2));
        wc::Match loaded(catalog, 1, 0);
        auto result = wc::LoadPreparationFile(loaded, path);
        Check(result.status == Status::Loaded && loaded.SavePreparation() == first, "interruption before/during/after staging retains committed snapshot");
        result = wc::SavePreparationFile(secondMatch, path);
        Check(result.status == Status::Saved && Read(path) == second && Read(Suffix(path, ".previous")) == first,
              "new save safely replaces abandoned staging files");
    }
    const auto beforeReplace = root / "backup-published" / "save";
    Write(beforeReplace, first); Write(Suffix(beforeReplace, ".previous"), first); Write(Suffix(beforeReplace, ".pending"), second);
    wc::Match loaded(catalog, 1, 0);
    Check(wc::LoadPreparationFile(loaded, beforeReplace).status == Status::Loaded && loaded.SavePreparation() == first,
          "interrupt after backup publish and before replacement resumes original primary");
    const auto afterReplace = root / "primary-published" / "save";
    Write(afterReplace, second); Write(Suffix(afterReplace, ".previous"), first);
    Check(wc::LoadPreparationFile(loaded, afterReplace).status == Status::Loaded && loaded.SavePreparation() == second,
          "interrupt after primary replacement resumes new complete primary");
    const auto pendingOnly = root / "never-committed" / "save";
    Write(Suffix(pendingOnly, ".pending"), second);
    const auto unchanged = loaded.SavePreparation();
    Check(wc::LoadPreparationFile(loaded, pendingOnly).status == Status::Missing && loaded.SavePreparation() == unchanged,
          "even a valid uncommitted staging snapshot is never silently loaded");
    std::cout << "PASS interrupted_write_boundaries\n";
}
void Corruption(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match source(catalog, 131, 1), target(catalog, 232, 1);
    const auto valid = source.SavePreparation(), unchanged = target.SavePreparation();
    auto corrupt = valid; corrupt[corrupt.size() / 2] ^= 1;
    const auto path = root / "corrupt-primary" / "save";
    Write(path, corrupt); Write(Suffix(path, ".previous"), valid);
    auto result = wc::LoadPreparationFile(target, path);
    Check(result.status == Status::RecoveredPrevious && result.Succeeded() && !result.message.empty(), "corrupt primary reports explicit previous-save recovery");
    Check(target.SavePreparation() == valid && Read(path) == corrupt && Read(Suffix(path, ".previous")) == valid,
          "recovery preserves corrupt evidence and previous valid bytes");
    Check(wc::SavePreparationFile(source, path).status == Status::Invalid && Read(path) == corrupt,
          "save cannot silently overwrite corrupt primary");
    const auto noBackup = root / "both-invalid" / "save";
    Write(noBackup, corrupt); Write(Suffix(noBackup, ".previous"), valid.substr(0, valid.size() / 2));
    wc::Match untouched(catalog, 232, 1);
    result = wc::LoadPreparationFile(untouched, noBackup);
    Check(result.status == Status::Invalid && !result.Succeeded() && untouched.SavePreparation() == unchanged,
          "two invalid snapshots leave live state intact");
    const auto missingPrimary = root / "missing-primary" / "save";
    Write(Suffix(missingPrimary, ".previous"), valid);
    Check(wc::LoadPreparationFile(untouched, missingPrimary).status == Status::RecoveredPrevious && untouched.SavePreparation() == valid,
          "previous save recovers when primary is missing");
    auto changedCatalog = catalog; changedCatalog.contentDigest += "-incompatible";
    wc::Match incompatible(changedCatalog, 232, 1);
    const auto incompatibleState = incompatible.SavePreparation();
    result = wc::LoadPreparationFile(incompatible, missingPrimary);
    Check(result.status == Status::Invalid && incompatible.SavePreparation() == incompatibleState,
          "different build rejects incompatible prior snapshot without state change");
    const auto incompatiblePrimary = root / "incompatible-primary" / "save";
    Write(incompatiblePrimary, incompatibleState); Write(Suffix(incompatiblePrimary, ".previous"), valid);
    Check(wc::LoadPreparationFile(untouched, incompatiblePrimary).status == Status::RecoveredPrevious &&
          Read(incompatiblePrimary) == incompatibleState, "matching backup may recover while incompatible primary is preserved");
    const auto oversized = root / "oversized" / "save";
    Write(oversized, std::string(4 * 1024 * 1024 + 1, 'x'));
    const auto beforeOversized = untouched.SavePreparation();
    Check(wc::LoadPreparationFile(untouched, oversized).status == Status::Invalid && untouched.SavePreparation() == beforeOversized,
          "bounded loader rejects oversized file before parsing");
    std::cout << "PASS corrupt_incompatible_missing_and_oversized_files\n";
}
void IoFailures(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match source(catalog, 16, 1), next(catalog, 17, 1);
    const auto oldBytes = source.SavePreparation();
    const auto parentFile = root / "parent-is-file";
    Write(parentFile, "occupied");
    auto result = wc::SavePreparationFile(source, parentFile / "save");
    Check(result.status == Status::IoError && Read(parentFile) == "occupied", "directory creation failure preserves existing parent file");
    const auto stagingDirectory = root / "staging-is-directory" / "save";
    Write(stagingDirectory, oldBytes); fs::create_directory(Suffix(stagingDirectory, ".pending"));
    result = wc::SavePreparationFile(next, stagingDirectory);
    Check(result.status == Status::IoError && Read(stagingDirectory) == oldBytes, "staging write failure preserves primary");
    const auto backupDirectory = root / "backup-is-directory" / "save";
    Write(backupDirectory, oldBytes); fs::create_directory(Suffix(backupDirectory, ".previous"));
    result = wc::SavePreparationFile(next, backupDirectory);
    Check(result.status == Status::IoError && Read(backupDirectory) == oldBytes, "backup replacement failure preserves primary");
    Check(wc::SavePreparationFile(source, {}).status == Status::IoError &&
          wc::LoadPreparationFile(source, {}).status == Status::IoError, "empty path rejected clearly");
#if defined(_WIN32)
    const auto lockedPath = root / "primary-locked" / "save";
    Write(lockedPath, oldBytes);
    HANDLE primary = CreateFileW(lockedPath.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    Check(primary != INVALID_HANDLE_VALUE, "real Windows sharing-denial fixture opens");
    result = wc::SavePreparationFile(next, lockedPath);
    CloseHandle(primary);
    Check(result.status == Status::IoError && Read(lockedPath) == oldBytes && Read(Suffix(lockedPath, ".previous")) == oldBytes,
          "native replacement denial preserves primary and validated backup");
    Check(wc::SavePreparationFile(next, lockedPath).status == Status::Saved, "save retries after real sharing failure and abandoned staging");
    const auto busyPath = root / "busy-slot" / "save";
    Write(busyPath, oldBytes);
    const auto lockPath = Suffix(busyPath, ".lock");
    HANDLE lock = CreateFileW(lockPath.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_ALWAYS,
                              FILE_ATTRIBUTE_NORMAL | FILE_FLAG_DELETE_ON_CLOSE, nullptr);
    Check(lock != INVALID_HANDLE_VALUE, "real concurrent writer lock opens");
    result = wc::SavePreparationFile(next, busyPath);
    CloseHandle(lock);
    Check(result.status == Status::IoError && Read(busyPath) == oldBytes, "concurrent writer is rejected without touching primary");
    Check(wc::SavePreparationFile(next, busyPath).status == Status::Saved, "OS lock releases and later save succeeds");
#endif
    std::cout << "PASS filesystem_failures_and_writer_exclusion\n";
}
void Eligibility(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match offline(catalog, 11, 1), network(catalog, 12, 2), hosted(catalog, 13, 1, true);
    const auto path = root / "eligible" / "save";
    Check(wc::SavePreparationFile(offline, path).status == Status::Saved, "offline fixture saved");
    const auto bytes = Read(path);
    for (wc::Match *match : {&network, &hosted})
    {
        const auto beforeNamespace = match->Namespace();
        const auto beforeSeed = match->Seed();
        match->TakeOver(0);
        if (match == &network) match->TakeOver(1);
        Check(wc::SavePreparationFile(*match, path).status == Status::Ineligible && Read(path) == bytes,
              "online origin cannot save after every human becomes a bot");
        Check(wc::LoadPreparationFile(*match, path).status == Status::Ineligible && match->Namespace() == beforeNamespace && match->Seed() == beforeSeed,
              "online-origin target cannot restore an offline file");
    }
    for (int tick = 0; tick < 10000 && offline.CurrentPhase() == wc::Phase::Preparation; ++tick) offline.Tick(catalog.rules.tickMs);
    Check(offline.CurrentPhase() == wc::Phase::Combat && wc::SavePreparationFile(offline, path).status == Status::Ineligible && Read(path) == bytes,
          "combat progress cannot overwrite the preparation boundary");
    auto legacy = catalog; legacy.profileId = "alpha_24";
    wc::Match legacyMatch(legacy, 1, 0);
    const auto legacyPath = root / "legacy" / "save";
    Check(wc::SavePreparationFile(legacyMatch, legacyPath).status == Status::Ineligible && !fs::exists(legacyPath),
          "legacy profile cannot write a successor slot");
    std::cout << "PASS_offline_origin_profile_and_preparation_eligibility\n";
}
void ColdWrite(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match source(catalog, 7319, 0);
    AdvanceTo(source, 4);
    Check(wc::SavePreparationFile(source, root / "cold.save").status == Status::Saved, "first process saves preparation");
    Write(root / "cold.expected.snapshot", source.SavePreparation());
    Write(root / "cold.expected.outcome", Complete(source));
    std::cout << "PASS cold_process_writer\n";
}
void ColdRead(const wc::Catalog &catalog, const fs::path &root)
{
    wc::Match target(catalog, 999, 1);
    Check(wc::LoadPreparationFile(target, root / "cold.save").status == Status::Loaded, "new process reads prior save");
    Check(target.SavePreparation() == Read(root / "cold.expected.snapshot"), "new process restores every snapshot byte");
    Check(Complete(target) == Read(root / "cold.expected.outcome"), "new process matches full original tournament and streams");
    std::cout << "PASS cold_process_relaunch_and_full_tournament\n";
}
} // namespace
int main(int argc, char **argv)
{
    try
    {
        if (argc != 3) throw std::runtime_error("Usage: wonder_vnext_save_files suite|cold-write|cold-read fresh-directory");
        const auto catalog = wcvnext::WonderVNextCatalog();
        Check(catalog.Validate().empty(), "canonical catalog validates");
        const fs::path root(argv[2]);
        const std::string mode(argv[1]);
        if (mode == "suite")
        {
            if (fs::exists(root)) throw std::runtime_error("Test suite requires a fresh directory");
            fs::create_directories(root);
            Roundtrip(catalog, root); InterruptedWrites(catalog, root); Corruption(catalog, root);
            IoFailures(catalog, root); Eligibility(catalog, root);
        }
        else if (mode == "cold-write")
        {
            if (fs::exists(root)) throw std::runtime_error("Cold writer requires a fresh directory");
            fs::create_directories(root); ColdWrite(catalog, root);
        }
        else if (mode == "cold-read") ColdRead(catalog, root);
        else throw std::runtime_error("Unknown test mode");
        std::cout << "PASS " << checks << " checks\n";
        return 0;
    }
    catch (const std::exception &exception)
    {
        std::cerr << "FAIL after " << checks << " checks: " << exception.what() << "\n";
        return 1;
    }
}
