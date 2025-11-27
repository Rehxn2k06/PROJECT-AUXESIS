#include<iostream>
#include<chrono>

long long fib(int n)
{
    if(n<=1) return n;
    return fib(n-1)+fib(n-2);
}

int main()
{
    int N=35;

    auto start=std::chrono::high_resolution_clock::now();
    long long result = fib(N);
    auto end=std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> diff=end-start;
    std::cout<<"fib("<<N<<") = "<<result<<"\n";
    std::cout<<"recusrsion took "<<diff.count()<<"\n";

    return 0;


}