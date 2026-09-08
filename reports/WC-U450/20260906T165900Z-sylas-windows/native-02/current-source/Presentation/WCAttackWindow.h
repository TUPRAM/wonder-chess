#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <string>

namespace wc::presentation {
struct AttackWindow { double start = 0, release = 0, end = 0; };
using AttackWindows = std::array<AttackWindow, 2>;
inline bool ValidateAttackWindows(const AttackWindows& windows, double length,
                                 double windup, std::string& error) {
    error.clear();
    if (!std::isfinite(length) || !std::isfinite(windup) || length <= 0 || windup <= 0) {
        error = "Invalid asset length or canonical windup"; return false;
    }
    double prior = 0;
    for (const auto& window : windows) {
        if (!std::isfinite(window.start) || !std::isfinite(window.release) || !std::isfinite(window.end) ||
            std::abs(window.start - prior) > .0001 || window.start < 0 ||
            window.release <= window.start || window.end <= window.release || window.end > length + .0001 ||
            std::abs(window.release - window.start - windup) > .0001) {
            error = "Attack windows must be contiguous, bounded, and release at canonical windup"; return false;
        }
        prior = window.end;
    }
    if (std::abs(prior - length) > .0001) {
        error = "Attack windows must cover the full sequence"; return false;
    }
    return true;
}
struct AttackSample { int window = -1; double position = 0; bool complete = false; };
inline AttackSample SampleAttack(const AttackWindows& windows, std::uint64_t ordinal, double elapsed) {
    if (!ordinal || !std::isfinite(elapsed)) return {};
    const int index = int((ordinal - 1) % windows.size());
    const auto& window = windows[index];
    const double duration = window.end - window.start;
    return {index, window.start + std::clamp(elapsed, 0.0, duration), elapsed >= duration};
}
// Independent of actor lifetime: a reconstructed view uses the snapshot ordinal and clock.
struct AttackClock {
    std::uint64_t action = 0, ordinal = 0;
    int snapshot = -1, startTick = 0;
    double elapsed = 0;
    void Update(std::uint64_t nextAction, std::uint64_t nextOrdinal, int nextSnapshot,
                int nextStart, double tickSeconds, double frameSeconds) {
        const double authoritative = std::max(0, nextSnapshot - nextStart) * tickSeconds;
        if (action != nextAction || ordinal != nextOrdinal || startTick != nextStart || nextSnapshot != snapshot)
            elapsed = authoritative;
        else
            elapsed = std::min(elapsed + std::max(0.0, frameSeconds), authoritative + tickSeconds);
        action = nextAction; ordinal = nextOrdinal; snapshot = nextSnapshot; startTick = nextStart;
    }
};
}
