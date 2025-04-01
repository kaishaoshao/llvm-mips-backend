.text

.globl main
.data
n: .word 4                             # number of test cases
insp:  .word    0,   5,   10,      100  # input numbers
outs: .word    0, 170, 2640, 25164150  # expected result
failmsg: .asciiz "failed for test input: "
expectedmsg: .asciiz ". expected "
tobemsg: .asciiz " to be "
okmsg: .asciiz "all tests passed"
.text
runner:
        lw      $s0, n
        la      $s1, insp
        la      $s2, outs
run_test:
        lw      $s3, 0($s1)             # read input from memory
        move    $a0, $s3                # move it to a0
        jal     main   # call subroutine under test
        move    $v1, $v0                # move return value in v0 to v1 because we need v0 for syscall
        lw      $s4, 0($s2)             # read expected output from memory
        bne     $v1, $s4, exit_fail     # if expected doesn't match actual, jump to fail
        addi    $s1, $s1, 4             # move to next word in input
        addi    $s2, $s2, 4             # move to next word in output
        sub     $s0, $s0, 1             # decrement num of tests left to run
        bgt     $s0, $zero, run_test    # if more than zero tests to run, jump to run_test
exit_ok:
        la      $a0, okmsg              # put address of okmsg into a0
        li      $v0, 4                  # 4 is print string
        syscall
        li      $v0, 10                 # 10 is exit with zero status (clean exit)
        syscall
exit_fail:
        la      $a0, failmsg            # put address of failmsg into a0
        li      $v0, 4                  # 4 is print string
        syscall
        move    $a0, $s3                # set arg of syscall to input that failed the test
        li      $v0, 1                  # 1 is print int
        syscall
        la      $a0, expectedmsg
        li      $v0, 4
        syscall
        move    $a0, $v1                # print actual that failed on
        li      $v0, 1
        syscall
        la      $a0, tobemsg
        li      $v0, 4
        syscall
        move    $a0, $s4                # print expected value that failed on
        li      $v0, 1
        syscall
        li      $a0, 1                  # set exit code to 1
        li      $v0, 17                 # terminate with the exit code in $a0
        syscall

	li $t0, 1
	li $t5, 0
	mthi $t5
	mtlo $t5
	move $v0, $0
	bnez $a0, start
	li $v0, 0
	jr $ra
	start: addiu $a0, $a0, 1
	while1:
		beq $t0, $a0, end
		nop
	body:
		addu $t1, $t1, $t0
		maddu $t0, $t0
		# increment
		addiu $t0, $t0, 1
		j while1
	end:
	mflo $v0 #sum of sq
	mulu $t2, $t1, $t1 #sq of sum
	sub $v0, $t2, $v0
	jr $ra