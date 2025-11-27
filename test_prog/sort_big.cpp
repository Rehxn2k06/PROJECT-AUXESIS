#include <iostream>
#include <vector>
#include <algorithm> // Required for std::sort
#include <random>    // For generating random numbers
#include <chrono>    // For measuring time (optional)

int main() {
    const int array_size = 100000;
    std::vector<int> arr(array_size);

    // Populate the array with random numbers (for demonstration)
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(1, 1000000); // Numbers between 1 and 1,000,000

    for (int i = 0; i < array_size; ++i) {
        arr[i] = distrib(gen);
    }

    auto start_time = std::chrono::high_resolution_clock::now();


    std::sort(arr.begin(), arr.end());

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;
    std::cout << "Sorting 100,000 elements took " << diff.count() << std::endl;

    return 0;
}
