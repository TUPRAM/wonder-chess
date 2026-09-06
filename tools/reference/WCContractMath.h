// Portable arithmetic oracle only. No Unreal headers; no claim of Unreal compilation.
#pragma once
#include <cstdint>
#include <optional>
#include <algorithm>
namespace wc_contract {
using I = std::int64_t;
inline I HalfUp(I n, I d) { return (2*n+d)/(2*d); } // internal prevalidated nonnegative bounds
inline std::optional<I> Damage(I raw, int type, I armor, I resist, I bonusBp=0) {
  if (raw<0 || raw>10000000 || type<0 || type>2 || armor<0 || armor>10000 || resist<0 || resist>10000 || bonusBp<0 || bonusBp>100000) return std::nullopt;
  const I defense=type==0?armor:type==1?resist:0;
  return HalfUp(raw*(10000+bonusBp)*100,10000*(100+defense));
}
inline std::optional<I> StarValue(I base, int star, I bonusBp=0) {
  if(base<0 || base>100000000 || star<1 || star>3 || bonusBp<0 || bonusBp>100000) return std::nullopt;
  constexpr I factors[]{10000,18000,32400};
  return HalfUp(base*factors[star-1]*(10000+bonusBp),100000000);
}
inline std::optional<I> IntervalTicks(I rateMilli,I bonusBp=0) {
  if(rateMilli<=0 || rateMilli>2500 || bonusBp<=-10000 || bonusBp>100000) return std::nullopt;
  I rate=std::clamp<I>(HalfUp(rateMilli*(10000+bonusBp),10000),250,2500);
  return (1000000+rate*50-1)/(rate*50);
}
}
