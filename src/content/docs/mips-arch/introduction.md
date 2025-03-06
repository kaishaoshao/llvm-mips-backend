---
title: MIPS Architecture
description: Learn about the MIPS instruction set, register file organization, calling conventions, and special hardware features that influence backend implementation.
---

For reference, read Volume IA.
[Quick reference](https://web.archive.org/web/20200730010546/https://s3-eu-west-1.amazonaws.com/downloads-mips/documents/MD00565-2B-MIPS32-QRC-01.01.pdf)

https://pages.cs.wisc.edu/~markhill/cs354/Fall2008/beyond354/conventions.html

MIPS ABI: https://dmz-portal.mips.com/wiki/MIPS_ABI

Much of this information is taken from the [System V Application Binary Interface (MIPS RISC Processor)](https://sourceware.org/legacy-ml/binutils/2003-06/msg00436.html).

ABI Document: https://math-atlas.sourceforge.net/devel/assembly/mipsabi32.pdf

## Data representation

A byte is 8 bits. A halfword is 16 bits. A word is 32 bits. A doubleword is 64 bits.
We follow the big-endian convention, where the most significant byte is stored at the lowest address.

## CPU Registers

- 32 32-bit general purpose registers
- 2 special 32-bit registers to hold the results of multiplication and division.
- 1 32-bit program counter (pc)

The general registers are named `$0` to `$31`.

### Special CPU registers

### Register usage conventions

| Register Name | Software name | Use                                  |
| ------------- | ------------- | ------------------------------------ |
| $0            | $zero         | Hard-wired to 0                      |
| $1            | $at           | Reserved for assembler               |
| $2-$3         | $v0-$v1       | Return values from functions         |
| $4-$7         | $a0-$a3       | Arguments to functions               |
| $8-$15        | $t0-$t7       | Temporary registers                  |
| $16-$23       | $s0-$s7       | Saved registers (saved across calls) |
| $24-$25       | $t8-$t9       | More temporary registers             |
| $26-$27       | $k0-$k1       | Reserved for kernel                  |
| $28           | $gp           | Global pointer                       |
| $29           | $sp           | Stack pointer                        |
| $30           | $s8/$fp       | Frame pointer                        |
| $31           | $ra           | Return address                       |

Only $16-$23 and $28-30 are saved across function calls. Register $28 is not preserved when calling position independent code.

> More on $gp
> The global pointer points to the middle of a 64KB block of memory in the heap that holds constants and global variables. Objects in this heap can be quickly accessed with a single load or store instruction. The global pointer is set by the operating system when the program starts.
