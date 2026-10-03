#pragma once
#include "Simulation/WonderSimulation.h"

namespace wc
{
struct FormationScenario
{
    std::string id, name, intendedVariable;
    std::string profileId, schemaVersion, balanceVersion, contentDigest;
    Id seed = 1;
    std::array<std::vector<OwnedUnit>, 2> armies;
};
struct FormationChange
{
    int side = 0;
    Id unit = 0;
    bool position = false, facing = false;
};
struct ScenarioPair
{
    std::string id, question;
    AbilityMechanic mechanic = AbilityMechanic::Standard;
    FormationScenario a, b;
    std::vector<FormationChange> changes;
};
FormationScenario MakeScenario(const Catalog &catalog, const std::string &name,
    const std::vector<OwnedUnit> &a, const std::vector<OwnedUnit> &b, Id seed);
bool ValidateScenario(const Catalog &catalog, const FormationScenario &scenario, std::string &error);
// The bounded binary format stores hero/relic stable IDs, never catalog array indices.
// A rejected load leaves the caller's last valid scenario unchanged.
std::string SaveScenario(const Catalog &catalog, const FormationScenario &scenario, std::string &error);
bool LoadScenario(const Catalog &catalog, const std::string &bytes, FormationScenario &scenario, std::string &error);
FormationScenario MirrorScenario(const FormationScenario &scenario);
ScenarioPair MirrorScenarioPair(const ScenarioPair &pair);
bool ValidateScenarioPair(const Catalog &catalog, const ScenarioPair &pair, std::string &error);
std::vector<ScenarioPair> BuiltinScenarioPairs(const Catalog &catalog);
Int ScenarioInvestment(const Catalog &catalog, const std::vector<OwnedUnit> &army);

struct ScenarioSideMetrics
{
    Int investment = 0, survivorInvestment = 0, healthLoss = 0, healing = 0,
        deliveredOverheal = 0, guardPrevented = 0;
    int damageEvents = 0, healingEvents = 0, guardedHits = 0, chargeLandings = 0,
        chargeHits = 0, grovePulses = 0, strikeHits = 0, beamHits = 0, tideHits = 0, tidePushes = 0,
        cocoons = 0;
};
struct ScenarioRun
{
    CombatResult result;
    Id signature = 0;
    int firstMeaningfulTick = -1, firstDeathTick = -1;
    std::array<ScenarioSideMetrics, 2> sides;
    std::vector<CombatEvent> events;
    std::vector<std::string> findings;
};
// Runs the real combat engine to its configured deadline, checking every tick.
// Overheal counts only delivered healing packets; fully healthy excluded targets emit no event.
ScenarioRun RunScenario(const Catalog &catalog, const FormationScenario &scenario);

struct EarlyResponseScenario
{
    std::string id, hypothesis;
    FormationScenario scenario;
    int level = 3, investmentBudget = 4, maximumRecruitCost = 1;
};
std::vector<EarlyResponseScenario> BuiltinEarlyResponseScenarios(const Catalog &catalog);
bool ValidateEarlyResponse(const Catalog &catalog, const EarlyResponseScenario &scenario, std::string &error);
} // namespace wc
