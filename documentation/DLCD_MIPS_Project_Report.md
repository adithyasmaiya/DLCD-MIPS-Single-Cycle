# DLCD Mini Project: Single-Cycle MIPS and gem5

Report generated: 2026-10-13

## 1. Project objective

Develop and verify an educational 32-bit MIPS instruction-level functional model, document its control signals, and execute a MIPS binary using gem5.

## 2. Python model

The model supports ADDI, ADD, SUB, AND, OR, SLT, LW, SW, BEQ and J.
Its PC uses byte addresses, with sequential instructions advancing by four bytes.

## 3. Verification artifacts

- Control/execution CSV exists: True
- Main verification report: `results/verification_report.txt`
- Control-unit test: `tests/test_control_unit.py`
- Edge-case test: `tests/test_edge_cases.py`

### Main verification report

```text
PASS | ADDI | 
PASS | ADD | 
PASS | SUB | 
PASS | AND | 
PASS | OR | 
PASS | SLT | 
PASS | SW | 
PASS | LW | 
PASS | BEQ | Instruction after taken branch skipped
PASS | J | 
PASS | Byte-addressed PC | 
PASS | Branch target | 
PASS | Register zero | 
PASS | Control table coverage | 10 required instruction types

Passed: 14
Failed: 0
```

## 4. gem5 execution

The test binary `programs/mips_add_print` printed `30` and exited normally in gem5 syscall-emulation mode.

The CPU model used was `MipsAtomicSimpleCPU`. This is gem5's existing atomic CPU model, not a custom single-cycle CPU implementation.

### Recorded statistics

- simSeconds: 0.000000
- simTicks: 38000
- simInsts: 37
- simOps: 37

## 5. Interpretation and limitations

The Python model is an instruction-level functional model. Its instruction trace and control table are useful for verifying functional behavior, but they do not establish physical single-cycle datapath timing.

The gem5 run demonstrates execution of a real MIPS ELF binary using gem5's MIPS syscall-emulation support. Its statistics describe that gem5 configuration and must not be presented as measurements of a custom single-cycle processor.

Further work is needed to integrate the control logic and datapath into a cycle-accurate or hardware-level single-cycle implementation, if required by the project specification.

## 6. Project files

- `src/mips_simulator.py`
- `src/control_unit.py`
- `src/single_cycle_demo.py`
- `tests/verify_mips.py`
- `tests/test_control_unit.py`
- `tests/test_edge_cases.py`
- `docs/datapath.mmd`
- `results/single_cycle_control_trace.csv`
- `results/gem5_add_print/stats.txt`
