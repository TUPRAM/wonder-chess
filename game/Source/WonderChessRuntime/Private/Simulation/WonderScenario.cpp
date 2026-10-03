#include "Simulation/WonderScenario.h"
#include <algorithm>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <tuple>

namespace wc
{
namespace
{
constexpr const char *Magic = "WCVNEXT-FORMATION-1";
constexpr std::size_t MaxBytes = 64 * 1024;
constexpr std::size_t MaxText = 512;
Id Checksum(const std::string &bytes)
{
    Id value = 14695981039346656037ULL;
    for (unsigned char byte : bytes) { value ^= byte; value *= 1099511628211ULL; }
    return value;
}
struct Writer
{
    std::string bytes;
    void Number(Id value) { for (int i = 0; i < 8; ++i) bytes.push_back(char((value >> (i * 8)) & 255)); }
    void Text(const std::string &value) { Number(value.size()); bytes += value; }
};
struct Reader
{
    const std::string &bytes;
    std::size_t offset = 0;
    Id Number()
    {
        if (offset > bytes.size() || bytes.size() - offset < 8) throw std::runtime_error("Truncated scenario");
        Id value = 0;
        for (int i = 0; i < 8; ++i) value |= Id(static_cast<unsigned char>(bytes[offset++])) << (i * 8);
        return value;
    }
    int Integer(int low, int high)
    {
        const Id value = Number();
        if (value > Id(high) || value < Id(low)) throw std::runtime_error("Scenario number outside bounds");
        return int(value);
    }
    std::string Text()
    {
        const Id size = Number();
        if (size > MaxText || offset > bytes.size() || size > bytes.size() - offset)
            throw std::runtime_error("Invalid scenario text length");
        const auto value = bytes.substr(offset, std::size_t(size));
        offset += std::size_t(size);
        return value;
    }
};
bool ValidText(const std::string &text, bool required = true)
{
    return (!required || !text.empty()) && text.size() <= MaxText &&
        std::none_of(text.begin(), text.end(), [](unsigned char c) { return c < 32 || c == 127; });
}
int Definition(const Catalog &catalog, const std::string &id)
{
    for (int i = 0; i < int(catalog.units.size()); ++i) if (catalog.units[i].id == id) return i;
    throw std::runtime_error("Unknown scenario hero: " + id);
}
int Relic(const Catalog &catalog, const std::string &id)
{
    if (id.empty()) return -1;
    for (int i = 0; i < int(catalog.relics.size()); ++i) if (catalog.relics[i].id == id) return i;
    throw std::runtime_error("Unknown scenario relic: " + id);
}
void Require(bool condition, const char *error) { if (!condition) throw std::runtime_error(error); }
void Identity(const Catalog &catalog, FormationScenario &scenario)
{
    scenario.profileId = catalog.profileId; scenario.schemaVersion = catalog.schemaVersion;
    scenario.balanceVersion = catalog.balanceVersion; scenario.contentDigest = catalog.contentDigest;
}
OwnedUnit Unit(const Catalog &catalog, Id id, const char *hero, int x, int y,
    Facing facing = Facing::Forward, int star = 1)
{
    OwnedUnit unit;
    unit.id = id; unit.definition = Definition(catalog, hero); unit.star = star;
    unit.onBoard = true; unit.cell = {x, y}; unit.facing = facing;
    return unit;
}
void WriteEvent(Writer &out, const CombatEvent &event)
{
    out.Number(event.tick); out.Number(event.source); out.Number(event.target); out.Number(event.action);
    out.Number(int(event.effect)); out.Number(event.requested); out.Number(event.resolved);
    out.Number(event.absorbed); out.Number(event.healthLoss); out.Number(event.overkill);
    out.Number(event.cell.column); out.Number(event.cell.row); out.Number(event.absorbedFrom);
    out.Number(int(event.damageType)); out.Number(event.basicAttack); out.Number(event.radius);
    out.Number(int(event.mechanic)); out.Number(event.origin.column); out.Number(event.origin.row);
    out.Number(event.guardedBy); out.Number(event.prevented);
}
Int Copies(int star) { return star == 3 ? 9 : star == 2 ? 3 : 1; }
} // namespace

FormationScenario MakeScenario(const Catalog &catalog, const std::string &name,
    const std::vector<OwnedUnit> &a, const std::vector<OwnedUnit> &b, Id seed)
{
    FormationScenario scenario;
    scenario.id = scenario.name = name; scenario.intendedVariable = "Player formation";
    Identity(catalog, scenario); scenario.seed = seed; scenario.armies = {a, b};
    return scenario;
}

bool ValidateScenario(const Catalog &catalog, const FormationScenario &scenario, std::string &error)
{
    error.clear();
    try
    {
        Require(catalog.profileId == "wonder_vnext", "Formation scenarios require wonder_vnext");
        const auto catalogError = catalog.Validate();
        if (!catalogError.empty()) throw std::runtime_error(catalogError);
        Require(scenario.profileId == catalog.profileId && scenario.schemaVersion == catalog.schemaVersion &&
            scenario.balanceVersion == catalog.balanceVersion && scenario.contentDigest == catalog.contentDigest,
            "Scenario profile or content version does not match this build");
        Require(ValidText(scenario.id) && ValidText(scenario.name) && ValidText(scenario.intendedVariable) &&
            ValidText(scenario.profileId) && ValidText(scenario.schemaVersion) && ValidText(scenario.balanceVersion) &&
            ValidText(scenario.contentDigest), "Invalid or oversized scenario metadata");
        std::set<Id> identities;
        for (const auto &army : scenario.armies)
        {
            Require(!army.empty() && army.size() <= 10, "Scenario requires one to ten units per side");
            std::set<std::pair<int, int>> cells;
            std::set<int> relics;
            for (const auto &unit : army)
            {
                Require(unit.id > 0 && unit.id < (Id(1) << 20) && identities.insert(unit.id).second,
                    "Invalid or duplicated scenario instance identity");
                Require(unit.definition >= 0 && unit.definition < int(catalog.units.size()), "Unknown scenario hero index");
                Require(unit.star >= 1 && unit.star <= 3 && unit.onBoard && !unit.neutral && unit.bench == -1 &&
                    unit.hpScaleBp == 10000 && unit.damageScaleBp == 10000, "Scenario unit is not a normal deployed recruit");
                Require(unit.cell.column >= 0 && unit.cell.column < catalog.rules.columns && unit.cell.row >= 0 &&
                    unit.cell.row < catalog.rules.deploymentRows && cells.insert({unit.cell.column, unit.cell.row}).second,
                    "Invalid or occupied scenario deployment cell");
                Require(unit.facing >= Facing::Forward && unit.facing <= Facing::Left, "Invalid scenario facing");
                Require(unit.relic >= -1 && unit.relic < int(catalog.relics.size()), "Unknown scenario relic index");
                if (unit.relic >= 0)
                    Require(relics.insert(unit.relic).second && RelicCompatible(catalog.relics[unit.relic],
                        catalog.units[unit.definition].ability.mechanic), "Duplicate or incompatible scenario relic");
            }
            Require(int(relics.size()) <= catalog.rules.maximumRelics, "Scenario exceeds equipped relic limit");
        }
        return true;
    }
    catch (const std::exception &exception) { error = exception.what(); return false; }
}

std::string SaveScenario(const Catalog &catalog, const FormationScenario &scenario, std::string &error)
{
    if (!ValidateScenario(catalog, scenario, error)) return {};
    Writer out;
    out.Text(Magic); out.Text(scenario.profileId); out.Text(scenario.schemaVersion);
    out.Text(scenario.balanceVersion); out.Text(scenario.contentDigest);
    out.Text(scenario.id); out.Text(scenario.name); out.Text(scenario.intendedVariable); out.Number(scenario.seed);
    for (const auto &army : scenario.armies)
    {
        out.Number(army.size());
        for (const auto &unit : army)
        {
            out.Number(unit.id); out.Text(catalog.units[unit.definition].id); out.Number(unit.star);
            out.Text(unit.relic < 0 ? "" : catalog.relics[unit.relic].id);
            out.Number(unit.cell.column); out.Number(unit.cell.row); out.Number(int(unit.facing));
        }
    }
    out.Number(Checksum(out.bytes));
    if (out.bytes.size() > MaxBytes) { error = "Scenario exceeds supported size"; return {}; }
    return out.bytes;
}

bool LoadScenario(const Catalog &catalog, const std::string &bytes, FormationScenario &scenario, std::string &error)
{
    error.clear();
    try
    {
        Require(bytes.size() >= 8 && bytes.size() <= MaxBytes, "Invalid scenario size");
        const std::string payload = bytes.substr(0, bytes.size() - 8);
        Reader check{bytes, bytes.size() - 8};
        Require(check.Number() == Checksum(payload), "Scenario integrity check failed");
        Reader in{payload};
        Require(in.Text() == Magic, "Unsupported scenario format version");
        FormationScenario pending;
        pending.profileId = in.Text(); pending.schemaVersion = in.Text();
        pending.balanceVersion = in.Text(); pending.contentDigest = in.Text();
        pending.id = in.Text(); pending.name = in.Text(); pending.intendedVariable = in.Text(); pending.seed = in.Number();
        for (auto &army : pending.armies)
        {
            const int size = in.Integer(1, 10);
            for (int i = 0; i < size; ++i)
            {
                OwnedUnit unit;
                unit.id = in.Number(); unit.definition = Definition(catalog, in.Text()); unit.star = in.Integer(1, 3);
                unit.relic = Relic(catalog, in.Text()); unit.cell.column = in.Integer(0, catalog.rules.columns - 1);
                unit.cell.row = in.Integer(0, catalog.rules.deploymentRows - 1); unit.facing = Facing(in.Integer(0, 3));
                unit.onBoard = true; army.push_back(unit);
            }
        }
        Require(in.offset == payload.size(), "Unexpected scenario trailing data");
        if (!ValidateScenario(catalog, pending, error)) return false;
        scenario = std::move(pending);
        return true;
    }
    catch (const std::exception &exception) { error = exception.what(); return false; }
}

FormationScenario MirrorScenario(const FormationScenario &scenario)
{
    auto mirrored = scenario;
    std::swap(mirrored.armies[0], mirrored.armies[1]);
    mirrored.id += "-mirror"; mirrored.name += " (mirrored)";
    return mirrored;
}
ScenarioPair MirrorScenarioPair(const ScenarioPair &pair)
{
    auto mirrored = pair;
    mirrored.id += "-mirror"; mirrored.a = MirrorScenario(pair.a); mirrored.b = MirrorScenario(pair.b);
    for (auto &change : mirrored.changes) change.side = 1 - change.side;
    return mirrored;
}
bool ValidateScenarioPair(const Catalog &catalog, const ScenarioPair &pair, std::string &error)
{
    if (!ValidateScenario(catalog, pair.a, error) || !ValidateScenario(catalog, pair.b, error)) return false;
    try
    {
        Require(ValidText(pair.id) && ValidText(pair.question) && pair.a.seed == pair.b.seed &&
            pair.a.intendedVariable == pair.b.intendedVariable, "Scenario pair identity or seed mismatch");
        Require(!pair.changes.empty(), "Scenario pair has no declared formation changes");
        std::set<std::pair<int, Id>> declared;
        for (const auto &change : pair.changes)
        {
            Require(change.side >= 0 && change.side <= 1 && (change.position || change.facing) &&
                declared.insert({change.side, change.unit}).second, "Invalid or duplicate declared formation change");
            const auto &army = pair.a.armies[change.side];
            Require(std::any_of(army.begin(), army.end(), [&](const OwnedUnit &unit) { return unit.id == change.unit; }),
                "Declared change references a missing unit");
        }
        for (int side = 0; side < 2; ++side)
        {
            const auto &a = pair.a.armies[side], &b = pair.b.armies[side];
            Require(a.size() == b.size(), "Causal pair cannot change army size");
            for (std::size_t i = 0; i < a.size(); ++i)
            {
                const auto &x = a[i], &y = b[i];
                Require(x.id == y.id && x.definition == y.definition && x.star == y.star && x.relic == y.relic,
                    "Causal pair cannot change roster, instance order, stars or relics");
                const auto change = std::find_if(pair.changes.begin(), pair.changes.end(),
                    [&](const FormationChange &c) { return c.side == side && c.unit == x.id; });
                const bool position = !(x.cell == y.cell), facing = x.facing != y.facing;
                if (change == pair.changes.end()) Require(!position && !facing, "Undeclared formation change");
                else Require(position == change->position && facing == change->facing,
                    "Actual formation difference does not match its declaration");
            }
        }
        return true;
    }
    catch (const std::exception &exception) { error = exception.what(); return false; }
}

std::vector<ScenarioPair> BuiltinScenarioPairs(const Catalog &catalog)
{
    const char *bell = "wc_vn_shieldbearer", *crag = "wc_vn_boar_rusher", *root = "wc_vn_grove_druid",
        *snap = "wc_vn_hookjaw", *prism = "wc_vn_prism_scholar", *tide = "wc_vn_tide_caller";
    auto unit = [&](Id id, const char *hero, int x, int y) { return Unit(catalog, id, hero, x, y); };
    std::vector<ScenarioPair> pairs;
    auto add = [&](const char *id, const char *name, const char *variable, const char *question, AbilityMechanic mechanic,
                   std::vector<OwnedUnit> a, std::vector<OwnedUnit> b) -> ScenarioPair & {
        ScenarioPair pair;
        pair.id = id; pair.question = question; pair.mechanic = mechanic;
        for (auto &opponent : b) opponent.id += 1000;
        pair.a = MakeScenario(catalog, name, a, b, 41001 + pairs.size());
        pair.a.id = std::string(id) + "-A"; pair.a.intendedVariable = variable;
        pair.b = pair.a; pair.b.id = std::string(id) + "-B"; pair.b.name += " alternative";
        pairs.push_back(std::move(pair)); return pairs.back();
    };
    auto &guard = add("F01", "Guard orientation", "Bellback facing", "Which ally actually receives protection?",
        AbilityMechanic::DirectionalGuard, {unit(1,bell,3,3),unit(2,root,3,2)},
        {unit(1,prism,4,2),unit(2,crag,3,3)});
    guard.b.armies[0][0].facing = Facing::Backward; guard.changes = {{0,1,false,true}};
    auto &charge = add("F02", "Approach and landing", "Cragstoat starting position", "Does this approach produce a released charge?",
        AbilityMechanic::MomentumCharge, {unit(1,crag,3,0),unit(2,bell,2,3)},
        {unit(1,bell,4,2),unit(2,root,4,0)});
    charge.b.armies[0][0].cell = {3,3}; charge.changes = {{0,1,true,false}};
    auto &grove = add("F03", "Grove establishment", "Grandmother Root starting position", "When does the grove heal, and what interrupts it?",
        AbilityMechanic::StationaryGrove, {unit(1,bell,3,3),unit(2,root,3,2),unit(3,crag,2,3)},
        {unit(1,tide,4,3),unit(2,snap,3,2),unit(3,crag,2,3)});
    grove.b.armies[0][1].cell = {0,0}; grove.changes = {{0,2,true,false}};
    auto &screen = add("F04", "Strike screen", "Defending Bellback starting position", "Who intercepts the committed distant strike?",
        AbilityMechanic::ScreenedStrike, {unit(1,snap,3,3),unit(2,bell,2,3)},
        {unit(1,bell,4,3),unit(2,root,4,1)});
    screen.b.armies[1][0].cell = {1,3}; screen.changes = {{1,1001,true,false}};
    auto &beam = add("F05", "Crossfire coverage", "Defender spacing", "Which creatures are struck by each crossing beam?",
        AbilityMechanic::CrossingBeams, {unit(1,prism,3,3),unit(2,bell,2,3)},
        {unit(1,bell,4,3),unit(2,root,4,1),unit(3,snap,2,3)});
    beam.b.armies[1][1].cell = {1,0}; beam.b.armies[1][2].cell = {0,2};
    beam.changes = {{1,1002,true,false},{1,1003,true,false}};
    auto &push = add("F06", "Tide facing", "Reefglass facing", "Where can the first lane target actually be pushed?",
        AbilityMechanic::TidalPush, {unit(1,tide,3,3),unit(2,bell,2,3)},
        {unit(1,bell,4,3),unit(2,root,4,0),unit(3,crag,1,3)});
    push.b.armies[0][0].facing = Facing::Right; push.changes = {{0,1,false,true}};
    auto &cocoon = add("F07", "Silkmother and Bellback", "Enemy approach position",
        "Which approaching enemy is cocooned while Bellback protects Silkmother?",
        AbilityMechanic::CocoonProjectile, {unit(1,bell,3,3),unit(2,"wc_vn_soul_jailer",3,2)},
        {unit(1,crag,4,3),unit(2,prism,2,2)});
    cocoon.b.armies[1][0].cell = {0,0};cocoon.changes = {{1,1001,true,false}};
    for (const auto &pair : pairs)
    {
        std::string error;
        if (!ValidateScenarioPair(catalog, pair, error)) throw std::runtime_error(pair.id + ": " + error);
    }
    return pairs;
}

Int ScenarioInvestment(const Catalog &catalog, const std::vector<OwnedUnit> &army)
{
    Int investment = 0;
    for (const auto &unit : army) investment += catalog.Definition(unit.definition).cost * Copies(unit.star);
    return investment;
}
ScenarioRun RunScenario(const Catalog &catalog, const FormationScenario &scenario)
{
    std::string error;
    if (!ValidateScenario(catalog, scenario, error)) throw std::invalid_argument(error);
    Combat combat(catalog, scenario.armies[0], scenario.armies[1], scenario.seed);
    std::map<Id, Int> health;
    std::map<Id, int> sides;
    for (const auto &unit : combat.Units()) { health[unit.id] = unit.health; sides[unit.id] = unit.side; }
    while (!combat.Result().complete)
    {
        combat.Tick();
        const auto issue = combat.InvariantError();
        if (!issue.empty()) throw std::runtime_error(issue);
        Require(combat.CurrentTick() <= catalog.rules.combatTimeoutMs / catalog.rules.tickMs + 1,
            "Scenario exceeded configured combat deadline");
    }
    ScenarioRun run;
    run.result = combat.Result(); run.events = combat.Events();
    for (int side = 0; side < 2; ++side) run.sides[side].investment = ScenarioInvestment(catalog, scenario.armies[side]);
    for (const auto &unit : combat.Units())
        if (unit.health > 0) run.sides[unit.side].survivorInvestment += catalog.units[unit.definition].cost * Copies(unit.star);
    Writer trace;
    for (const auto &event : run.events)
    {
        WriteEvent(trace, event);
        auto &source = run.sides[sides.at(event.source)], &target = run.sides[sides.at(event.target)];
        if (run.firstMeaningfulTick < 0 && event.effect != Effect::Dash &&
            (event.resolved > 0 || event.prevented > 0)) run.firstMeaningfulTick = event.tick;
        if (event.effect == Effect::Damage)
        {
            Require(event.resolved == event.absorbed + event.healthLoss + event.overkill,
                "Scenario damage event does not reconcile");
            target.healthLoss += event.healthLoss; target.guardPrevented += event.prevented;
            source.damageEvents++; if (event.guardedBy) target.guardedHits++;
            health[event.target] -= event.healthLoss;
            if (health[event.target] == 0 && run.firstDeathTick < 0) run.firstDeathTick = event.tick;
            if (event.mechanic == AbilityMechanic::MomentumCharge) source.chargeHits++;
            if (event.mechanic == AbilityMechanic::ScreenedStrike) source.strikeHits++;
            if (event.mechanic == AbilityMechanic::CrossingBeams) source.beamHits++;
            if (event.mechanic == AbilityMechanic::TidalPush) source.tideHits++;
        }
        if (event.effect == Effect::Heal)
        {
            Require(event.resolved >= 0 && event.resolved <= event.requested, "Scenario healing event does not reconcile");
            target.healing += event.resolved; target.deliveredOverheal += event.requested - event.resolved;
            target.healingEvents++; health[event.target] += event.resolved;
            if (event.mechanic == AbilityMechanic::StationaryGrove) source.grovePulses++;
        }
        if (event.effect == Effect::Dash && event.mechanic == AbilityMechanic::MomentumCharge) source.chargeLandings++;
        if (event.effect == Effect::Dash && event.mechanic == AbilityMechanic::TidalPush) source.tidePushes++;
        if (event.effect == Effect::Stun && event.mechanic == AbilityMechanic::CocoonProjectile && event.resolved>0) source.cocoons++;
    }
    for (const auto &unit : combat.Units()) Require(health[unit.id] == unit.health, "Scenario health ledger does not reconcile");
    trace.Number(run.result.complete); trace.Number(run.result.timeout); trace.Number(run.result.winner);
    trace.Number(run.result.ticks); trace.Number(run.result.survivors[0]); trace.Number(run.result.survivors[1]);
    run.signature = Checksum(trace.bytes);
    std::ostringstream outcome;
    outcome << (run.result.timeout ? "Deadline adjudication" : "Elimination resolution") << ": "
        << (run.result.winner < 0 ? "tie" : run.result.winner == 0 ? "side A wins" : "side B wins")
        << " after " << run.result.ticks * catalog.rules.tickMs << " ms; survivors "
        << run.result.survivors[0] << ":" << run.result.survivors[1] << ".";
    run.findings.push_back(outcome.str());
    std::ostringstream mechanics;
    mechanics << "Observed A/B: guard prevented " << run.sides[0].guardPrevented << "/" << run.sides[1].guardPrevented
        << " health subunits; effective healing " << run.sides[0].healing << "/" << run.sides[1].healing
        << "; released charge hits " << run.sides[0].chargeHits << "/" << run.sides[1].chargeHits
        << "; tide pushes " << run.sides[0].tidePushes << "/" << run.sides[1].tidePushes
        << "; cocoons " << run.sides[0].cocoons << "/" << run.sides[1].cocoons << ".";
    run.findings.push_back(mechanics.str());
    return run;
}

std::vector<EarlyResponseScenario> BuiltinEarlyResponseScenarios(const Catalog &catalog)
{
    const char *bell = "wc_vn_shieldbearer", *crag = "wc_vn_boar_rusher", *root = "wc_vn_grove_druid",
        *snap = "wc_vn_hookjaw", *prism = "wc_vn_prism_scholar";
    const std::vector<OwnedUnit> defenders{Unit(catalog,1001,bell,4,3),Unit(catalog,1002,root,4,2),Unit(catalog,1003,crag,3,3)};
    std::vector<EarlyResponseScenario> result;
    auto add = [&](const char *id, int level, int budget, int cost, const char *hypothesis, std::vector<OwnedUnit> army) {
        EarlyResponseScenario test;
        test.id = id; test.level = level; test.investmentBudget = budget; test.maximumRecruitCost = cost;
        test.hypothesis = hypothesis; test.scenario = MakeScenario(catalog, id, army, defenders, 42007);
        test.scenario.intendedVariable = "Acquisition-limited roster and approach; separate from causal formation pairs";
        result.push_back(std::move(test));
    };
    add("F07-L3-pressure",3,4,1,"Cost-1 pressure; two-star Cragstoat represents three purchased copies",
        {Unit(catalog,1,crag,3,0,Facing::Forward,2),Unit(catalog,2,bell,2,3)});
    add("F07-L3-width",3,4,1,"Three cost-1 recruits; unspent budget is disclosed",
        {Unit(catalog,1,crag,2,0),Unit(catalog,2,crag,5,0),Unit(catalog,3,bell,3,3)});
    add("F07-L4-angle",4,5,3,"Snapvine first has nonzero offer weight at level 4; test an angled screen strike",
        {Unit(catalog,1,snap,0,3),Unit(catalog,2,crag,5,0),Unit(catalog,3,bell,3,3)});
    add("F07-L5-crossfire",5,6,4,"Prism first has nonzero offer weight at level 5; availability is not a guaranteed purchase",
        {Unit(catalog,1,prism,3,2),Unit(catalog,2,crag,5,0),Unit(catalog,3,bell,3,3)});
    add("F07-L6-crossfire",6,6,4,"Same level-5 roster and budget with level-6 offer access; no free Reefglass",
        {Unit(catalog,1,prism,3,2),Unit(catalog,2,crag,5,0),Unit(catalog,3,bell,3,3)});
    for (const auto &test : result)
    {
        std::string error;
        if (!ValidateEarlyResponse(catalog, test, error)) throw std::runtime_error(test.id + ": " + error);
    }
    return result;
}
bool ValidateEarlyResponse(const Catalog &catalog, const EarlyResponseScenario &test, std::string &error)
{
    if (!ValidateScenario(catalog, test.scenario, error)) return false;
    try
    {
        Require(test.level >= 3 && test.level <= 6 && test.maximumRecruitCost >= 1 && test.maximumRecruitCost <= 4 &&
            test.investmentBudget > 0, "Invalid early response acquisition bounds");
        const auto offers = catalog.rules.shopWeights.find(test.level);
        Require(offers != catalog.rules.shopWeights.end(), "Missing early response shop weights");
        for (int side = 0; side < 2; ++side)
        {
            const auto &army = test.scenario.armies[side];
            Require(int(army.size()) <= test.level && ScenarioInvestment(catalog, army) <= test.investmentBudget,
                "Early response exceeds capacity or purchase investment budget");
            for (const auto &unit : army)
            {
                const int cost = catalog.units[unit.definition].cost;
                Require(cost >= 1 && cost <= 5 && offers->second[cost - 1] > 0 && unit.relic == -1,
                    "Early response uses unavailable recruit or free relic");
                if (side == 0) Require(cost <= test.maximumRecruitCost, "Response exceeds declared recruit-cost limit");
            }
        }
        return true;
    }
    catch (const std::exception &exception) { error = exception.what(); return false; }
}
} // namespace wc
