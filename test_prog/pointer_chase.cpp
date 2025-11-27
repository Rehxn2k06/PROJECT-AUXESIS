// pointer_chase.cpp
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
using namespace std;

int main() {
    const int N = 2'500'000; // number of nodes
    vector<int> next(N);
    // initialize with pseudo-random permutation for pointer-chase
    for (int i = 0; i < N; ++i) next[i] = (i + 1) % N;

    // shuffle with a fixed seed (deterministic)
    std::mt19937 rng(12345);
    for (int i = N - 1; i > 0; --i) {
        int j = rng() % (i + 1);
        std::swap(next[i], next[j]);
    }

    int idx = 0;
    const int STEPS = N; // traverse N steps
    auto start = chrono::high_resolution_clock::now();
    long long sum = 0;
    for (int s = 0; s < STEPS; ++s) {
        idx = next[idx];
        sum += idx;
    }
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> diff = end - start;
    cout << "PointerSum: " << sum << "\\n";
    cout << "Pointer chase took " << diff.count() << endl;
    return 0;
}
