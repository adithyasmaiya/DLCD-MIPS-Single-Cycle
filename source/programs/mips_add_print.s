
.set noreorder

.text
.globl _start

_start:
    # Calculate 10 + 20 = 30
    addiu $t0, $zero, 10
    addiu $t1, $zero, 20
    addu  $t2, $t0, $t1

    # Prepare a buffer ending in newline
    la    $t4, buffer+15
    addiu $t3, $zero, 10
    sb    $t3, 0($t4)
    addiu $t4, $t4, -1

    # Convert the unsigned result in $t2 to decimal digits
    addiu $t7, $zero, 10

digit_loop:
    divu  $t2, $t7
    mfhi  $t3
    mflo  $t2
    addiu $t3, $t3, 48
    sb    $t3, 0($t4)
    addiu $t4, $t4, -1
    bne   $t2, $zero, digit_loop
    nop

    # Write the generated digits and newline to stdout
    addiu $a0, $zero, 1
    addiu $a1, $t4, 1
    la    $t6, buffer+16
    subu  $a2, $t6, $a1
    addiu $v0, $zero, 4004
    syscall

    # Exit normally
    addiu $a0, $zero, 0
    addiu $v0, $zero, 4001
    syscall

.data
.align 2
buffer:
    .space 16
