// matmul.cpp
#include <iostream>
#include <vector>
#include <chrono>
using namespace std;

int main() {
    const int N = 600; 
    vector<double> A(N*N, 1.0), B(N*N, 1.0), C(N*N, 0.0);

    auto start = chrono::high_resolution_clock::now();
    for (int i = 0; i < N; ++i) {
        for (int k = 0; k < N; ++k) {
            double aik = A[i*N + k];
            for (int j = 0; j < N; ++j) {
                C[i*N + j] += aik * B[k*N + j];
            }
        }
    }
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> diff = end - start;
    // Use one element to avoid dead-code elimination
    cout << "C[0]=" << C[0] << "\\n";
    cout << "MatMul took " << diff.count() << endl;
    return 0;
}
