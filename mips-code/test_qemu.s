.data
message: .asciiz "Hello, World!\n"

.text
.globl __start

__start:
    ; li $v0, 4001
    ; li $a0, 1
    ; la $a1, message
    ; li $a2, 13
    ; syscall
    jr $31
    nop
    li $v0, 10 # exit
    syscall
