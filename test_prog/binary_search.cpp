#include<iostream>
#include<vector>
#include<algorithm>
#include<random>
#include<chrono>

int main()
{
    const int N=500000;
    const int Q=200000;

    std::vector<int> data(N);
    for(int i =0; i<N;++i)
    {
        data[i]=i*2;
    }

    std::vector<int> queries(Q);
    std::mt19937 rng(12345);
    std::uniform_int_distribution<int> dist(0,N*4);

    for(int i =0 ; i<Q;++i)
    {
        queries[i]=dist(rng);
    }

    auto start=std::chrono::high_resolution_clock::now();

    int hits=0;
    for(int i=0;i<Q;++i)
    {
        if(std::binary_search(data.begin(),data.end(),queries[i])){
            hits++;
        }
    }

    auto end= std::chrono::high_resolution_clock::now();
    std::chrono::duration<double>diff=end-start;

    std::cout<<"hits = "<<hits<<"\n";
    std::cout<<"Binary search took "<< diff.count()<<"\n";

    return 0 ;
}