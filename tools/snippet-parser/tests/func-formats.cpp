// RUN: %parser -d %s | %filecheck %s
// Check all formatting styles for functions.
#include <iostream>

using namespace std;

int main() {
  cout << "Hello, World!" << endl;
// CHECK: Context[[[@LINE-1]]]:
// CHECK-NEXT: [:[[@LINE-3]]] int main
  auto lambda = []() { cout << "Hello, Lambda!" << endl; };

  auto lambdaWithParams = [](int a, int b) {
    cout << "Sum: " << a + b << endl;
// CHECK: Context[[[@LINE-1]]]:
// CHECK-NEXT: [:7] int main
  };
  return 0;
}

bool AMDGPUTargetMachine::splitModule(
    Module &M, unsigned NumParts,
    function_ref<void(std::unique_ptr<Module> MPart)> ModuleCallback) {
      cout << "Hello, World!" << endl;
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: [:[[@LINE-5]]] bool AMDGPUTargetMachine::splitModule
  return false;
}

void main(int param = 0, typename something::type anotherParma) {
  cout << "Hello, World!" << endl;
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: [:[[@LINE-3]]] void main
}

extern "C" LLVM_ATTRIBUTE_WEAK void __sanitizer_cov_trace_pc_guard(uint32_t *Guard) {
  cout << "Hello, World!" << endl;
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: [:[[@LINE-3]]] extern "C"
}

bool llvm::debuginfoShouldUseDebugInstrRef(const Triple &T) {
  cout << "function";
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: [:[[@LINE-3]]]
}