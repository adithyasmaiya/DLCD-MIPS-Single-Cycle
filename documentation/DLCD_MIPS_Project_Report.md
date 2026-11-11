# DLCD Mini Project Report
## Educational Single-Cycle MIPS Datapath Model and Separate gem5 Experiment

## 1. Project objective

The objective of this project is to develop and verify an educational 32-bit MIPS functional/architectural model for a defined instruction subset. The project models the control unit and datapath decisions, generates an instruction-by-instruction execution trace, and provides an interactive conceptual datapath visualization. A separate MIPS executable is also run using gem5 to demonstrate MIPS program execution and collect simulator statistics.

## 2. Project components

The submission contains the following components:

1. **MIPS functional simulator** — executes the supported instruction subset and maintains architectural state.
2. **Control unit** — provides control settings for the supported instruction types.
3. **Architectural datapath model** — models register reads, immediate extension, ALU operations, memory access, write-back, branch decisions and jump selection.
4. **MUX tracking** — records inputs and selected values for the RegDst, ALUSrc, MemToReg and next-PC selection paths.
5. **Cycle-trace generator** — records per-instruction values and control signals in CSV format.
6. **Interactive datapath viewer** — displays trace values and highlights conceptual components and paths for the selected instruction.
7. **Standalone verification scripts** — check instruction behaviour and individual datapath components.
8. **Separate gem5 experiment** — runs a MIPS executable using gem5's existing MIPS CPU model.

## 3. Supported instruction subset

The Python model supports:

| Instruction | Function |
|---|---|
| `ADDI` | Adds a sign-extended immediate to a register |
| `ADD` | Adds two register values |
| `SUB` | Subtracts one register value from another |
| `AND` | Performs bitwise AND |
| `OR` | Performs bitwise OR |
| `SLT` | Performs signed set-less-than |
| `LW` | Loads a word from data memory |
| `SW` | Stores a word to data memory |
| `BEQ` | Branches when two register values are equal |
| `J` | Jumps using the MIPS 26-bit target field |

The model uses byte-addressed program counters. Sequential execution advances the PC by four bytes, and word accesses are expected to be aligned.

## 4. Datapath and control-unit model

The conceptual datapath includes the program counter, instruction memory, register file, main control unit, sign extension, ALU control, ALU, data memory, branch logic, jump-address generation and next-PC selection.

The control-unit model associates each supported instruction with control settings. The ALU operation for R-type instructions is determined using the instruction's function field.

### 4.1 MUX selection tracking

The datapath trace explicitly records MUX inputs and selected values:

- **RegDst:** selects the destination register field (RT or RD).
- **ALUSrc:** selects the second ALU operand from a register value or sign-extended immediate.
- **MemToReg:** selects the value written back to the register file from the ALU result or data memory.
- **Next-PC selection:** records the sequential, branch or jump path.

The interactive viewer displays these values for the selected instruction. This makes it possible to inspect not only which conceptual blocks participate in an instruction, but also the recorded MUX selection.

## 5. Demonstration program and architectural trace

The demonstration program exercises arithmetic, memory, branch and jump behaviour. Its taken `BEQ` skips the instruction immediately following it, and a later `J` selects a jump target.

The generated architectural trace contains eight executed instructions.

Recorded final state:

| Register / memory location | Value |
|---|---:|
| R8 | 10 |
| R9 | 20 |
| R10 | 30 |
| R11 | 10 |
| R12 | 30 |
| R13 | 0 |
| Memory[0] | 30 |

The trace is saved as:

```text
results/single_cycle_cycle_trace.csv
```

The interactive viewer is generated at:

```text
results/datapath_view.html
```

The viewer allows the user to select an instruction and inspect its values, MUX selections and associated conceptual datapath components.

## 6. Verification and test results

The project includes 12 standalone Python test scripts. The recorded test run reported the following results:

| Test script | Passed checks |
|---|---:|
| `test_alu_datapath.py` | 10 |
| `test_branch_datapath.py` | 10 |
| `test_control_unit.py` | 10 |
| `test_datapath_model.py` | 9 |
| `test_edge_cases.py` | 7 |
| `test_immediate_validation.py` | 7 |
| `test_jump_datapath.py` | 11 |
| `test_jump_target.py` | 5 |
| `test_memory_datapath.py` | 13 |
| `test_register_file.py` | 14 |
| `test_sign_extension.py` | 7 |
| `verify_mips.py` | 14 |
| **Total** | **117** |

**Recorded result: 117 passed checks, 0 failed across 12 scripts.**

These are counts reported by the individual standalone scripts; they are not pytest-collected test functions. The separate `results/verification_report.txt` records 14 core instruction and architectural checks, with 14 passed and 0 failed.

## 7. Separate gem5 experiment

A separate MIPS executable, `mips_add_print`, was run using gem5's MIPS support. The local run used the `MipsAtomicSimpleCPU` CPU model in syscall-emulation mode with atomic memory and `SimpleMemory`.

### 7.1 Configuration

| Setting | Value |
|---|---|
| CPU model | `MipsAtomicSimpleCPU` |
| ISA | MIPS |
| Execution mode | Syscall emulation |
| Memory mode | Atomic |
| Memory object | `SimpleMemory` |
| Simulation frequency | 1 GHz |

### 7.2 Verified local statistics

The latest local `stats.txt` reported:

| Statistic | Value |
|---|---:|
| Simulated instructions (`simInsts`) | 37 |
| Simulated operations (`simOps`) | 37 |
| Simulated ticks (`simTicks`) | 19,000 |
| CPU cycles (`system.cpu.numCycles`) | 39 |
| CPI (`system.cpu.cpi`) | 1.054054 |
| IPC (`system.cpu.ipc`) | 0.948718 |
| Host execution time (`hostSeconds`) | 0.01 seconds |

The statistics are taken from the user's latest local gem5 run in `~/gem5_external/run_add_print/stats.txt`.

### 7.3 Interpretation

The gem5 experiment demonstrates execution of a MIPS binary using gem5's existing `MipsAtomicSimpleCPU` model. It is **not** a custom single-cycle MIPS processor implemented inside gem5. The gem5 statistics describe that gem5 configuration and are separate from the Python model's eight-instruction architectural trace. The two instruction counts and their statistics are not a direct performance comparison.

## 8. Project files and generated artifacts

| File / directory | Description |
|---|---|
| `source/src/mips_simulator.py` | MIPS functional simulator |
| `source/src/control_unit.py` | Control-signal model |
| `source/src/datapath_model.py` | Architectural datapath model |
| `source/src/cycle_trace.py` | CSV trace generator with MUX fields |
| `source/src/generate_datapath_view.py` | Interactive HTML viewer generator |
| `source/tests/` | Standalone test scripts |
| `source/programs/` | MIPS assembly sources and executable files |
| `results/single_cycle_cycle_trace.csv` | Per-instruction architectural trace |
| `results/datapath_view.html` | Interactive datapath visualization |
| `results/verification_report.txt` | Core verification summary |
| `results/gem5_add_print/` | gem5 configuration and statistics |

## 9. Limitations

- The Python implementation is an educational functional/architectural model of the supported MIPS instruction subset.
- The interactive datapath diagram is a conceptual architectural visualization. Its signal routes are illustrative and are not a gate-level netlist.
- The architectural trace records values and control decisions; it does not establish physical circuit timing or a synthesized single-cycle hardware implementation.
- The gem5 experiment uses gem5's existing `MipsAtomicSimpleCPU` model; it is not a custom single-cycle MIPS CPU implemented in gem5.
- gem5 statistics must not be attributed to the Python datapath model.
- The project does not claim FPGA implementation, hardware synthesis or measured gate-level timing.

## 10. Conclusion

The project demonstrates a tested educational MIPS functional/architectural model for a defined instruction subset, including control-unit behaviour, datapath operations, explicit MUX selection tracking, an instruction-level CSV trace and an interactive conceptual datapath viewer. The standalone verification scripts provide checks for instruction and datapath behaviour. A separate MIPS executable was also run using gem5's existing `MipsAtomicSimpleCPU` model, with its configuration and statistics reported independently. Together, these components provide complementary software-based demonstrations of MIPS execution and datapath concepts while keeping their implementation scope and results distinct.
