#include <iostream>
#include <vector> // prgram check
#include <chrono> // benchmarking
using namespace std;

int main() {
    const int N = 1000000;
    vector<int> a(N, 1), b(N, 2);
    long long sum = 0;
    auto start = chrono::high_resolution_clock::now();//timer start
    for (int i = 0; i < N; i++) sum += a[i] * b[i];
    auto end = chrono::high_resolution_clock::now(); //timer end
    chrono::duration<double> diff = end - start;//benchmarking time for program
    cout << "Sum: " << sum << "\\n";
    cout << "Time: " << diff.count() << " s\\n";
    cout<<"\n";
    return 0;
}
