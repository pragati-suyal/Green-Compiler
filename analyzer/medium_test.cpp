#include <iostream>
using namespace std;

int main() {
    
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += i;
    }
    
    if (sum > 10) {
        cout << sum << endl;
    }

    return 0;
}
