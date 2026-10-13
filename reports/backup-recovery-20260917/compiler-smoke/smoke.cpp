#include <windows.h>
#include <array>
#include <numeric>
#include <iostream>
static_assert(_MSC_VER >= 1944 && _MSC_VER < 1950, "Expected MSVC 14.44");
int main() {
    const std::array<int, 4> values{1, 2, 3, 4};
    const int sum = std::accumulate(values.begin(), values.end(), 0);
    if (sum != 10 || GetCurrentProcessId() == 0) return 1;
    std::cout << "WONDER_CHESS_BUILD_TOOLS_SMOKE_PASS compiler=" << _MSC_FULL_VER << " sum=" << sum << '\n';
    return 0;
}
