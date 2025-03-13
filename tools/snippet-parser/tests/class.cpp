// RUN: %parser -d %s | %filecheck %s

#include "somefile"
#include <iostream>

using namespace std;

class A {
    bool Field;
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: class A
    A() {
        cout << "A";
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT:class A
// CHECK-NEXT: A()
    }

    bool operator==(const A& a) {
        return true;
// CHECK-LABEL: Context[20]
// CHECK-NEXT: [:8] class A
// CHECK: [:19] bool operator==
    }
};