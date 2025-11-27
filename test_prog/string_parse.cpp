// string_parse.cpp
#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <chrono>

using namespace std;

int main() {
    const int CHARS = 10'000'000;           // total chars
    const int WORD_MAX = 12;
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> letter(97, 122); // a-z
    string s;
    s.reserve(CHARS);
    // build a pseudo-random text with spaces
    for (int i = 0; i < CHARS; ++i) {
        if (rng() % 8 == 0) s.push_back(' ');
        else s.push_back((char)letter(rng));
    }

    auto start = chrono::high_resolution_clock::now();
    vector<string> tokens;
    tokens.reserve(100000);
    string cur;
    for (char c : s) {
        if (c == ' ') {
            if (!cur.empty()) { tokens.push_back(cur); cur.clear(); }
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) tokens.push_back(cur);
    // do a small work over tokens
    size_t total_len = 0;
    for (auto &t : tokens) total_len += t.size();
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> diff = end - start;
    cout << "Tokens: " << tokens.size() << " TotalLen: " << total_len << "\\n";
    cout << "String parse took " << diff.count() << endl;
    return 0;
}
