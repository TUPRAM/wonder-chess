#include "Simulation/WonderScenarioFile.h"
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
fs::path Suffix(fs::path path, const char *suffix) { path += suffix; return path; }
std::string SystemError(int code) { return std::error_code(code, std::system_category()).message(); }
std::string FileError(int code) { return std::error_code(code, std::generic_category()).message(); }
bool UsablePath(const fs::path &path)
{
    return !path.empty() && !path.filename().empty() && path.filename() != "." && path.filename() != "..";
}
class SlotLock
{
  public:
    explicit SlotLock(const fs::path &path)
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
    ~SlotLock()
    {
#if defined(_WIN32)
        if (handle_ != INVALID_HANDLE_VALUE) CloseHandle(handle_);
#else
        if (handle_ >= 0) close(handle_);
#endif
    }
    SlotLock(const SlotLock &) = delete;
    SlotLock &operator=(const SlotLock &) = delete;
    std::string error;
  private:
#if defined(_WIN32)
    HANDLE handle_ = INVALID_HANDLE_VALUE;
#else
    int handle_ = -1;
#endif
};
struct ReadResult
{
    bool valid = false, missing = false;
    std::string bytes, error;
    FormationScenario scenario;
};
ReadResult Read(const Catalog &catalog, const fs::path &path)
{
    ReadResult result;
    std::error_code error;
    const auto state = fs::symlink_status(path, error);
    if (error == std::errc::no_such_file_or_directory || (!error && !fs::exists(state)))
    { result.missing = true; result.error = "File does not exist"; return result; }
    if (error) { result.error = "Cannot inspect scenario: " + error.message(); return result; }
    if (!fs::is_regular_file(state)) { result.error = "Scenario path is not a regular file"; return result; }
    const auto size = fs::file_size(path, error);
    if (error) { result.error = "Cannot measure scenario: " + error.message(); return result; }
    if (size < 8 || size > 64 * 1024) { result.error = "Invalid scenario file size"; return result; }
    std::ifstream file(path, std::ios::binary);
    if (!file) { result.error = "Cannot open scenario for reading"; return result; }
    result.bytes.resize(std::size_t(size));
    if (!file.read(result.bytes.data(), std::streamsize(size)) || file.peek() != std::char_traits<char>::eof())
    { result.error = "Scenario changed or could not be read completely"; return result; }
    result.valid = LoadScenario(catalog, result.bytes, result.scenario, result.error);
    return result;
}
std::string Stage(const Catalog &catalog, const fs::path &path, const std::string &bytes)
{
    std::error_code stateError;
    const auto state = fs::symlink_status(path, stateError);
    if (stateError && stateError != std::errc::no_such_file_or_directory)
        return "Cannot inspect staging path: " + stateError.message();
    if (!stateError && fs::exists(state) && !fs::is_regular_file(state)) return "Staging path is not a regular file";
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
        if (_commit(_fileno(file)) != 0) error = "Cannot flush scenario to disk: " + FileError(errno);
#else
        if (fsync(fileno(file)) != 0) error = "Cannot flush scenario to disk: " + FileError(errno);
#endif
    }
    if (std::fclose(file) != 0 && error.empty()) error = "Cannot close staging file: " + FileError(errno);
    if (!error.empty()) return error;
    const auto stored = Read(catalog, path);
    if (!stored.valid) return "Staged scenario validation failed: " + stored.error;
    return stored.bytes == bytes ? std::string{} : "Staged scenario differs from requested formation";
}
std::string Replace(const fs::path &source, const fs::path &destination)
{
#if defined(_WIN32)
    if (!MoveFileExW(source.c_str(), destination.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
        return "Cannot atomically publish scenario: " + SystemError(int(GetLastError()));
#else
    std::error_code error;
    fs::rename(source, destination, error);
    if (error) return "Cannot atomically publish scenario: " + error.message();
    const auto parent = destination.has_parent_path() ? destination.parent_path() : fs::path(".");
    const int directory = open(parent.c_str(), O_RDONLY | O_DIRECTORY);
    if (directory < 0) return "Scenario published but directory flush unavailable: " + FileError(errno);
    const int flushed = fsync(directory), flushError = errno;
    close(directory);
    if (flushed != 0) return "Scenario published but directory flush failed: " + FileError(flushError);
#endif
    return {};
}
} // namespace

ScenarioFileResult SaveScenarioFile(const Catalog &catalog, const FormationScenario &scenario, const fs::path &path)
{
    try
    {
        std::string error;
        const auto bytes = SaveScenario(catalog, scenario, error);
        if (bytes.empty()) return {false, false, "Formation cannot be saved: " + error};
        if (!UsablePath(path)) return {false, false, "A scenario file path is required"};
        std::error_code directoryError;
        if (path.has_parent_path()) fs::create_directories(path.parent_path(), directoryError);
        if (directoryError) return {false, false, "Cannot create scenario directory: " + directoryError.message()};
        SlotLock lock(Suffix(path, ".lock"));
        if (!lock.error.empty()) return {false, false, "Cannot acquire scenario slot: " + lock.error};
        const auto existing = Read(catalog, path);
        if (!existing.valid && !existing.missing)
            return {false, false, "Existing scenario preserved: " + existing.error + ". Move it aside before saving again"};
        const auto pending = Suffix(path, ".pending");
        error = Stage(catalog, pending, bytes);
        if (!error.empty()) return {false, false, error + "; previous scenario preserved"};
        if (existing.valid)
        {
            const auto backup = Suffix(path, ".previous"), backupPending = Suffix(backup, ".pending");
            error = Stage(catalog, backupPending, existing.bytes);
            if (error.empty()) error = Replace(backupPending, backup);
            if (!error.empty()) return {false, false, error + "; primary scenario preserved"};
        }
        error = Replace(pending, path);
        if (!error.empty()) return {false, false, error + "; retained previous scenario remains available"};
        return {true, false, existing.valid ? "Formation saved; the previous valid formation is retained" : "Formation saved"};
    }
    catch (const std::exception &exception) { return {false, false, "Scenario save failed: " + std::string(exception.what())}; }
}
ScenarioFileResult LoadScenarioFile(const Catalog &catalog, const fs::path &path, FormationScenario &scenario)
{
    try
    {
        if (!UsablePath(path)) return {false, false, "A scenario file path is required"};
        auto primary = Read(catalog, path);
        if (primary.valid) { scenario = std::move(primary.scenario); return {true, false, "Saved formation restored"}; }
        auto previous = Read(catalog, Suffix(path, ".previous"));
        if (previous.valid)
        {
            scenario = std::move(previous.scenario);
            return {true, true, "Recovered the previous formation. Primary: " + primary.error + ". Existing files were preserved"};
        }
        return {false, false, "No valid formation could be restored. Primary: " + primary.error + ". Previous: " + previous.error};
    }
    catch (const std::exception &exception) { return {false, false, "Scenario load failed: " + std::string(exception.what())}; }
}
} // namespace wc
