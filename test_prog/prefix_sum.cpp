#include<iostream>
#include<vector>
#include<chrono>

int main()
{
    const int N =2000000;
    std::vector<int> arr(N,1);
    std::vector<long long> prefix(N,0);

    auto start=std::chrono::high_resolution_clock::now();

    prefix[0]=arr[0];
    for ( int i=1;i<N;i++)
    {
        prefix[i]=prefix[i-1]+arr[i];
    }

    auto end=std::chrono::high_resolution_clock::now();
    std::chrono::duration<double>diff=end-start;

    std::cout<<"prefix[5] = "<<prefix[5]<<"\n";
    std::cout<<"prefix sum took "<<diff.count()<<"\n";
    return 0;

}