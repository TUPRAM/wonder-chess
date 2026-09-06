#include "../tools/reference/WCContractMath.h"
#include <cassert>
#include <iostream>
int main(){
 using namespace wc_contract;
 assert(Damage(12000,0,50,0)==8000);
 assert(Damage(12000,1,0,20)==10000);
 assert(Damage(9000,2,9999,9999)==9000);
 assert(Damage(10000,0,25,0,2500)==10000);
 assert(StarValue(100000,2,2500)==225000);
 assert(StarValue(4800,3)==15552);
 assert(IntervalTicks(800,2500)==20);
 assert(IntervalTicks(850)==24);
 assert(!Damage(100,0,-1,0));
 assert(!StarValue(100,4));
 std::cout<<"10 portable C++ arithmetic assertions passed; Unreal was NOT compiled.\n";
}
