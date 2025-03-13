// RUN: %parser %s | %filecheck %s
namespace llvm {
//@s snip1

// CHECK-LABEL: "id": "snip1"
// CHECK: "start_lineno": [[@LINE-3]]
// CHECK-DAG: "context_stack":
// CHECK-DAG: "type": "NAMESPACE"
    bool function(char param) {
        return true;
    }
// CHECK-DAG: "end_lineno": [[@LINE+1]]
//- snip1
}

//@s snip2
// CHECK-LABEL: "id": "snip2"
// CHECK: "start_lineno": [[@LINE-2]]
// CHECK-DAG: "end_lineno": [[@LINE+7]]
// CHECK-DAG: "context_stack":
// CHECK: "type": "AFTER"
// CHECK-NEXT: "line": 2
    bool function2(char param) {
        return true;
    }
//- snip2