// RUN: %parser -d %s | %filecheck %s
bool someFunction(int a, int b) {
    if (a == 3) {
        if (b == 4) {
            return true;
// CHECK: Context[[[@LINE-1]]]
// CHECK-NEXT: bool someFunction
        }
    }
}

static VersionTuple getCanonicalVersionForOS(OSType OSKind,
                                               const VersionTuple &Version);

// check that there is no context here
// CHECK: Context[[[@LINE+1]]]
// CHECK-NEXT: end context
