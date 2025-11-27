#include<bits/stdc++.h>
#include<chrono>
using namespace std;
int main(){
    const int N=2000000;
    vector <bool> is_prime(N+1,true);
    is_prime[0]=is_prime[1]=false;

    auto start=chrono::high_resolution_clock::now();

    for(int p=2;p*p<=N;p++){
        if(is_prime[p]){
            for(int multiple=p*p;multiple<=N;multiple+=p){
                is_prime[multiple]=false;
            }
        }
    }
    auto end=chrono::high_resolution_clock::now();
    chrono::duration<double> diff=end-start;


    int count_primes=0;
    for(int i=2;i<=N;++i){
        if(is_prime[i]) count_primes++;
    }

    cout<<"primes= "<<count_primes<<"\n";
    cout<<"sieve took " << diff.count()<<"\n";

    return 0;

}