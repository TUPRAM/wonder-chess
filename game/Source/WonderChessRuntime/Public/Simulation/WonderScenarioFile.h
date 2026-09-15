#pragma once
#include "Simulation/WonderScenario.h"
#include <filesystem>

namespace wc
{
struct ScenarioFileResult
{
    bool succeeded = false, recoveredPrevious = false;
    std::string message;
};
// One durable local slot with a retained last valid primary in <path>.previous.
// Loads never trust uncommitted staging files; rejection preserves the caller's scenario.
ScenarioFileResult SaveScenarioFile(const Catalog &catalog, const FormationScenario &scenario,
    const std::filesystem::path &path);
ScenarioFileResult LoadScenarioFile(const Catalog &catalog, const std::filesystem::path &path,
    FormationScenario &scenario);
} // namespace wc
