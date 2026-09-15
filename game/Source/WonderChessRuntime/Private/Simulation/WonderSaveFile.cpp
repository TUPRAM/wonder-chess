#include "Simulation/WonderSaveFile.h"
#include "Simulation/WonderSimulation.h"
#include <cerrno>
#include <cstdio>
#include <fstream>
#include <system_error>

#if defined(_WIN32)
#if defined(PLATFORM_WINDOWS)
#include "Windows/WindowsHWrapper.h"
#else
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <Windows.h>
#endif
#include <io.h>
#else
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>
#endif

namespace wc
{
namespace
{
namespace fs = std::filesystem;
using Status = PreparationSaveStatus;
constexpr std::uintmax_t MaximumFileBytes = 4 * 1024 * 1024;
fs::path Suffix(fs::path path, const char *suffix)
{
    path += suffix;
    return path;
}
std::string SystemError(int code)
{
    return std::error_code(code, std::system_category()).message();
}
std::string FileError(int code)
{
    return std::error_code(code, std::generic_category()).message();
}
bool UsablePath(const fs::path &path)
{
    const auto name = path.filename();
    return !path.empty() && !name.empty() && name != "." && name != "..";
}
// An OS-owned lock prevents two application instances from publishing the same slot.
class WriteLock
{
  public:
    explicit WriteLock(const fs::path &path)
    {
#if defined(_WIN32)
        handle_ = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_ALWAYS,
                              FILE_ATTRIBUTE_NORMAL | FILE_FLAG_DELETE_ON_CLOSE, nullptr);
        if (handle_ == INVALID_HANDLE_VALUE) error = SystemError(int(GetLastError()));
#else
        handle_ = open(path.c_str(), O_CREAT | O_RDWR, 0600);
        if (handle_ < 0 || flock(handle_, LOCK_EX | LOCK_NB) != 0) error = FileError(errno);
#endif
    }
    ~WriteLock()
    {
#if defined(_WIN32)
        if (handle_ != INVALID_HANDLE_VALUE) CloseHandle(handle_);
#else
        if (handle_ >= 0) close(handle_);
#endif
    }
    WriteLock(const WriteLock &) = delete;
    WriteLock &operator=(const WriteLock &) = delete;
    std::string error;
  private:
#if defined(_WIN32)
    HANDLE handle_ = INVALID_HANDLE_VALUE;
#else
    int handle_ = -1;
#endif
};
PreparationSaveResult ReadBytes(const fs::path &path, std::string &bytes)
{
    std::error_code error;
    const auto state = fs::symlink_status(path, error);
    if (error == std::errc::no_such_file_or_directory || (!error && !fs::exists(state)))
        return {Status::Missing, "Save file does not exist"};
    if (error) return {Status::IoError, "Cannot inspect save file: " + error.message()};
    if (!fs::is_regular_file(state)) return {Status::IoError, "Save path is not a regular file"};
    const auto size = fs::file_size(path, error);
    if (error) return {Status::IoError, "Cannot measure save file: " + error.message()};
    if (size < 8 || size > MaximumFileBytes) return {Status::Invalid, "Invalid save file size"};
    std::ifstream input(path, std::ios::binary);
    if (!input) return {Status::IoError, "Cannot open save file for reading"};
    bytes.resize(static_cast<std::size_t>(size));
    if (!input.read(bytes.data(), static_cast<std::streamsize>(size)) || input.peek() != std::char_traits<char>::eof())
        return {Status::IoError, "Save file changed or could not be read completely"};
    return {Status::Loaded, {}};
}
PreparationSaveResult ValidateBytes(const Catalog &catalog, const std::string &bytes)
{
    Match validation(catalog, 1, 0);
    std::string error;
    if (!validation.RestorePreparation(bytes, error)) return {Status::Invalid, error};
    return {Status::Loaded, {}};
}
PreparationSaveResult ReadValid(const Catalog &catalog, const fs::path &path, std::string &bytes)
{
    auto result = ReadBytes(path, bytes);
    return result.Succeeded() ? ValidateBytes(catalog, bytes) : result;
}
std::string WriteFlushed(const fs::path &path, const std::string &bytes)
{
    std::error_code stateError;
    const auto state = fs::symlink_status(path, stateError);
    if (stateError && stateError != std::errc::no_such_file_or_directory)
        return "Cannot inspect staging file: " + stateError.message();
    if (!stateError && fs::exists(state) && !fs::is_regular_file(state))
        return "Staging path is not a regular file";
    FILE *file = nullptr;
#if defined(_WIN32)
    const int opened = _wfopen_s(&file, path.c_str(), L"wb");
    if (opened != 0) return "Cannot open staging file: " + FileError(opened);
#else
    file = std::fopen(path.c_str(), "wb");
    if (!file) return "Cannot open staging file: " + FileError(errno);
#endif
    std::string error;
    if (std::fwrite(bytes.data(), 1, bytes.size(), file) != bytes.size()) error = "Cannot write complete staging file";
    if (error.empty() && std::fflush(file) != 0) error = "Cannot flush staging buffer: " + FileError(errno);
    if (error.empty())
    {
#if defined(_WIN32)
        if (_commit(_fileno(file)) != 0) error = "Cannot flush staging file to disk: " + FileError(errno);
#else
        if (fsync(fileno(file)) != 0) error = "Cannot flush staging file to disk: " + FileError(errno);
#endif
    }
    if (std::fclose(file) != 0 && error.empty()) error = "Cannot close staging file: " + FileError(errno);
    return error;
}
std::string Replace(const fs::path &source, const fs::path &destination)
{
#if defined(_WIN32)
    if (!MoveFileExW(source.c_str(), destination.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
        return "Cannot atomically replace save file: " + SystemError(int(GetLastError()));
#else
    std::error_code error;
    fs::rename(source, destination, error);
    if (error) return "Cannot atomically replace save file: " + error.message();
    const auto parent = destination.has_parent_path() ? destination.parent_path() : fs::path(".");
    const int directory = open(parent.c_str(), O_RDONLY | O_DIRECTORY);
    if (directory < 0) return "Save replaced, but cannot open directory for durability flush: " + FileError(errno);
    const int flushed = fsync(directory);
    const int flushError = errno;
    close(directory);
    if (flushed != 0) return "Save replaced, but directory durability flush failed: " + FileError(flushError);
#endif
    return {};
}
std::string StageValidated(const Catalog &catalog, const fs::path &path, const std::string &bytes)
{
    auto error = WriteFlushed(path, bytes);
    if (!error.empty()) return error;
    std::string stored;
    auto result = ReadValid(catalog, path, stored);
    if (!result.Succeeded()) return "Staged save verification failed: " + result.message;
    return stored == bytes ? std::string{} : "Staged save differs from the requested snapshot";
}
} // namespace

PreparationSaveResult SavePreparationFile(const Match &match, const fs::path &path)
{
    try
    {
        const auto bytes = match.SavePreparation();
        if (bytes.empty()) return {Status::Ineligible, "Only a valid offline wonder_vnext preparation can be saved"};
        auto validation = ValidateBytes(match.Definitions(), bytes);
        if (!validation.Succeeded()) return {Status::Ineligible, "Match cannot be saved: " + validation.message};
        if (!UsablePath(path)) return {Status::IoError, "A save file path is required"};
        std::error_code error;
        if (path.has_parent_path()) fs::create_directories(path.parent_path(), error);
        if (error) return {Status::IoError, "Cannot create save directory: " + error.message()};
        WriteLock lock(Suffix(path, ".lock"));
        if (!lock.error.empty()) return {Status::IoError, "Cannot acquire save slot: " + lock.error};
        std::string previous;
        auto existing = ReadValid(match.Definitions(), path, previous);
        if (!existing.Succeeded() && existing.status != Status::Missing)
            return {existing.status, "Existing save preserved: " + existing.message + ". Move it aside before saving again"};

        const auto pending = Suffix(path, ".pending");
        auto issue = StageValidated(match.Definitions(), pending, bytes);
        if (!issue.empty()) return {Status::IoError, issue + "; previous save preserved"};
        if (existing.Succeeded())
        {
            const auto backup = Suffix(path, ".previous");
            const auto backupPending = Suffix(backup, ".pending");
            issue = StageValidated(match.Definitions(), backupPending, previous);
            if (issue.empty()) issue = Replace(backupPending, backup);
            if (!issue.empty()) return {Status::IoError, issue + "; primary save preserved"};
        }
        issue = Replace(pending, path);
        if (!issue.empty()) return {Status::IoError, issue + "; any retained previous save is available for recovery"};
        return {Status::Saved, "Preparation saved. An interruption during combat resumes from this preparation"};
    }
    catch (const std::exception &exception)
    {
        return {Status::IoError, "Save failed: " + std::string(exception.what())};
    }
}

PreparationSaveResult LoadPreparationFile(Match &match, const fs::path &path)
{
    try
    {
        if (!UsablePath(path)) return {Status::IoError, "A save file path is required"};
        std::string primaryBytes;
        auto primary = ReadValid(match.Definitions(), path, primaryBytes);
        std::string restoreError;
        if (primary.Succeeded())
        {
            if (!match.RestorePreparation(primaryBytes, restoreError)) return {Status::Ineligible, restoreError};
            return {Status::Loaded, "Saved preparation restored"};
        }
        std::string previousBytes;
        auto previous = ReadValid(match.Definitions(), Suffix(path, ".previous"), previousBytes);
        if (previous.Succeeded())
        {
            if (!match.RestorePreparation(previousBytes, restoreError)) return {Status::Ineligible, restoreError};
            return {Status::RecoveredPrevious, "Recovered previous preparation. Primary save: " + primary.message +
                    ". Existing files were preserved"};
        }
        const auto status = primary.status == Status::Missing ? previous.status : primary.status;
        return {status, "No valid preparation could be restored. Primary: " + primary.message +
                        ". Previous: " + previous.message};
    }
    catch (const std::exception &exception)
    {
        return {Status::IoError, "Load failed: " + std::string(exception.what())};
    }
}
} // namespace wc
