#include<bits/stdc++.h>
#include<chrono>
using namespace std;

int main()
{
    const int N=1700;
    vector<double> A(N*N),B(N*N);

    for(int i=0;i<N;++i){
        for(int j=0;j<N;++j){
            A[i*N+j]=i*0.001+j*0.002;
            
        }
    }

    auto start=chrono::high_resolution_clock::now();

    for(int i=0;i<N;++i){
        for(int j=0;j<N;++j){
            B[j*N+i]=A[i*N+j];
        }
    }
    auto end=chrono::high_resolution_clock::now();
    chrono::duration<double> diff=end-start;

    double checksum=0.0;
    for(int i=0;i<N*N;++i){
        checksum+=B[i];
    }

    cout<<"checksum= "<<checksum<<'\n';
    cout<<"transpose took "<< diff.count()<<'\n';

    return 0;
}