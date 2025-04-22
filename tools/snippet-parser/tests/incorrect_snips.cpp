//@s nova-isel-lowering-cpp-1

//===- NovaIselLowering.cpp - Nova DAG Lowering Implementation -----------===//
#include "NovaIselLowering.h"

using namespace llvm;

#define DEBUG_TYPE "nova-isel"

NovaTargetLowering::NovaTargetLowering(const TargetMachine &TM,
                                       const NovaSubtarget &STI)
    : TargetLowering(TM) {}

//- nova-isel-lowering-cpp-1

// //@s nova-isel-lowering-cpp-2

// NovaTargetLowering::LowerReturn(SDValue Chain, CallingConv::ID CallConv,
//                                bool isVarArg,
//                                const SmallVectorImpl<ISD::OutputArg> &Outs,
//                                const SmallVectorImpl<SDValue> &OutVals,
//                                const SDLoc &dl, SelectionDAG &DAG) const {
  
// }
// //- nova-isel-lowering-cpp-2