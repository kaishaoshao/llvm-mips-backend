// RUN: %parser -d %s | %filecheck %s

#include <iostream>

bool isRequired() { return true; }

int main() {
// CHECK-LABEL: Context[7]
// CHECK-NEXT: [:7] int main
  if (isRequired()) {
    std::cout << "Required" << std::endl;
    void inlineFunc();
// CHECK-LABEL: Context[11]
// CHECK-NEXT: [:7] int main
  }
  return 0;
}
