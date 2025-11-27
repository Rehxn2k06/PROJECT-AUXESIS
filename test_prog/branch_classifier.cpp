#include<iostream>
#include<vector>
#include<random>
#include<chrono>

int main()
{
    const int N=2000000;

    std::vector<int> data(N);
    std::mt19937 rng(123456);
    std::uniform_int_distribution<int> dist(0,1000);

    for(int i=0;i<N;++i)
    {
        data[i]=dist(rng);
    }

    int c_small=0;
    int c_medium=0;
    int c_large=0;
    int c_weird=0;

    auto start=std::chrono::high_resolution_clock::now();


    for (int i = 0; i < N; ++i) {
        int x = data[i];

        if (x < 100) {
            if (x % 2 == 0) {
                c_small++;
            } else {
                c_weird++;
            }
        } else if (x < 500) {
            if (x % 3 == 0) {
                c_medium++;
            } else if (x % 5 == 0) {
                c_weird++;
            } else {
                c_small++;
            }
        } else if (x < 800) {
            if (x % 7 == 0) {
                c_large++;
            } else if (x % 11 == 0) {
                c_weird++;
            } else {
                c_medium++;
            }
        } else {
            if (x % 2 == 1 && x % 3 == 0) {
                c_large++;
            } else {
                c_weird++;
            }
        }
    }

    auto end=std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff=end-start;

    std::cout<<"count: small="<<c_small<<"medium"<<c_medium<<"large"<<c_large<<"weird"<<c_weird<<'\n';
    std::cout<<"branch classify took "<<diff.count()<<"\n";

    return 0;

}