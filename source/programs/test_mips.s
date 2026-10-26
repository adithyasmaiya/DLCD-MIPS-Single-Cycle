.set noreorder
.text
.globl _start

_start:
    addiu $t0, $zero, 10
    addiu $t1, $zero, 20
    addu  $t2, $t0, $t1

    # Linux MIPS exit syscall
    addiu $v0, $zero, 4001
    addu  $a0, $zero, $zero
    syscall
