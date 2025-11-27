// convolution.cpp
#include <iostream>
#include <vector>
#include <chrono>

using namespace std;

int main() {
    const int H = 2000; // height
    const int W = 2000; // width
    vector<float> A(H*W, 1.0f), B(H*W, 0.0f);
    // simple 3x3 sharpening kernel
    float K[3][3] = {{0,-1,0},{-1,5,-1},{0,-1,0}};

    auto start = chrono::high_resolution_clock::now();
    for (int y = 1; y < H-1; ++y) {
        for (int x = 1; x < W-1; ++x) {
            float sum = 0.0f;
            for (int ky = -1; ky <= 1; ++ky)
                for (int kx = -1; kx <= 1; ++kx)
                    sum += K[ky+1][kx+1] * A[(y+ky)*W + (x+kx)];
            B[y*W + x] = sum;
        }
    }
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> diff = end - start;
    cout << "Conv center: " << B[(H/2)*W + (W/2)] << "\\n";
    cout << "Convolution took " << diff.count() << endl;
    return 0;
}
