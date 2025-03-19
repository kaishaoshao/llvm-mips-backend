// RUN: %parser -d %s | %filecheck %s

template<typename T> class DenseMapInfo {};
class MCRegister {
    int id() {return 0;}
};

class forward;

template <> struct DenseMapInfo<MCRegister> {
  static inline MCRegister getEmptyKey() {
  // CHECK: Context[[[@LINE]]]
  // CHECK-NEXT: struct DenseMapInfo<MCRegister> {
  // CHECK-NEXT: static inline MCRegister getEmptyKey() {
    return DenseMapInfo<unsigned>::getEmptyKey();
  }
  static inline MCRegister getTombstoneKey() {
    return DenseMapInfo<unsigned>::getTombstoneKey();
  }
  static unsigned getHashValue(const MCRegister &Val) {
    return DenseMapInfo<unsigned>::getHashValue(Val.id());
  }
  static bool isEqual(const MCRegister &LHS, const MCRegister &RHS) {
    return LHS == RHS;
  }
};

// inline hashcode hash_value(const MCRegister &Reg) {
//   return hash_value(Reg.id());
// }