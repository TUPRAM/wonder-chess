#include "Simulation/WonderSimulation.h"
#include "CatalogFixture.h"
#include <array>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>

// Experimental catalog copies only. These multipliers are not shipped balance.
int main(int argc, char** argv) {
    try {
        const int count = argc > 1 ? std::stoi(argv[1]) : 25;
        const int firstExperiment = argc > 2 ? std::stoi(argv[2]) : 0;
        const int experimentEnd = argc > 3 ? std::stoi(argv[3]) : 3;
        const int firstSeed = argc > 4 ? std::stoi(argv[4]) : 1;
        if (count < 1 || count > 1000) throw std::invalid_argument("seed count");
        if (firstExperiment < 0 || experimentEnd > 8 || firstExperiment >= experimentEnd || firstSeed < 1)
            throw std::invalid_argument("experiment range");
        std::ofstream waves("wave-outcomes.csv"), matches("matches.csv"), factors("experimental-factors.csv");
        waves << "experiment,seed,round,seat,winner,timeout,health_after,damage,reward\n";
        matches << "experiment,seed,rounds,simulated_ms,capped,bot_rejects\n";
        factors << "experiment,round,hp_scale_bp,damage_scale_bp\n";
        if (!waves || !matches || !factors) throw std::runtime_error("cannot open evidence");
        for (int experiment = firstExperiment; experiment < experimentEnd; ++experiment) {
            auto catalog = FixtureCatalog();
            for (auto& wave : catalog.waves) {
                if (wave.round >= 5 && experiment >= 5) {
                    const std::array<int,8> hp = experiment == 5 ? std::array<int,8>{12000,15600,20000,22500,27200,34000,37000,41000} : experiment == 6 ? std::array<int,8>{12000,16000,19000,21000,25000,28000,32000,36000} : std::array<int,8>{12000,15600,20000,22500,27000,34000,26000,30000};
                    const std::array<int,8> damage = experiment == 5 ? std::array<int,8>{15000,30000,45000,50700,35000,40000,42000,45000} : experiment == 6 ? std::array<int,8>{15000,35000,42000,42000,44000,50000,55000,60000} : std::array<int,8>{15000,30000,45000,50700,45000,65000,30000,34000};
                    wave.hpScaleBp = hp.at(wave.round/5-1);
                    wave.damageScaleBp = damage.at(wave.round/5-1);
                } else if (wave.round >= 5 && experiment > 0) {
                    const int step = wave.round / 5 - 1;
                    const int hp = experiment == 1 ? 13000 + step * 4000 : experiment == 2 ? 15000 + step * 6500 : experiment == 3 ? 12000 + step * 1000 : 14000 + step * 1500;
                    const int damage = experiment == 1 ? 12000 + step * 2000 : experiment == 2 ? 13000 + step * 3000 : experiment == 3 ? 15000 + step * 8000 : 20000 + step * 12000;
                    wave.hpScaleBp = std::min(100000, int((std::int64_t(wave.hpScaleBp) * hp + 5000) / 10000));
                    wave.damageScaleBp = std::min(100000, int((std::int64_t(wave.damageScaleBp) * damage + 5000) / 10000));
                }
                factors << experiment << ',' << wave.round << ',' << wave.hpScaleBp << ',' << wave.damageScaleBp << '\n';
            }
            const auto error = catalog.Validate();
            if (!error.empty()) throw std::runtime_error(error);
            for (int seed = firstSeed; seed < firstSeed + count; ++seed) {
                wc::Match match(catalog, seed, 0);
                int iterations = 0;
                while (match.CurrentPhase() != wc::Phase::Finished) {
                    match.Tick(50);
                    if (++iterations > 120000) throw std::runtime_error("match did not finish");
                }
                int rejects = 0;
                for (const auto& command : match.BotLog()) rejects += !command.reply.accepted;
                if (rejects) throw std::runtime_error("bot command rejected");
                for (const auto& round : match.Records()) {
                    if (!round.neutral) continue;
                    for (size_t index = 0; index < round.results.size(); ++index) {
                        const auto& result = round.results[index];
                        const int seat = round.pairs[index].a;
                        if (!result.complete || round.pairs[index].kind != wc::EncounterKind::Neutral)
                            throw std::runtime_error("invalid actual neutral result");
                        waves << experiment << ',' << seed << ',' << round.round << ',' << seat << ','
                              << result.winner << ',' << result.timeout << ',' << round.health[seat] << ','
                              << round.damage[seat] << ',' << round.pendingRewards[seat] << '\n';
                    }
                }
                matches << experiment << ',' << seed << ',' << match.Round() << ',' << match.ElapsedMs() << ',' << match.Capped() << ',' << rejects << '\n';
                std::cout << "experiment=" << experiment << " seed=" << seed << " rounds=" << match.Round() << '\n';
            }
        }
        std::cout << "PASS actual tournaments=" << count * (experimentEnd - firstExperiment) << " experimental catalog copies; canonical files unchanged\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL " << error.what() << '\n';
        return 1;
    }
}
