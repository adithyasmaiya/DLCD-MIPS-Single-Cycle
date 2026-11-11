# Single-Cycle MIPS Datapath — DLCD Mini Project

## 1. Project overview

This project contains an educational 32-bit MIPS functional model, a control-unit model, an architectural single-cycle datapath model, execution-trace generation, an interactive HTML datapath viewer, standalone verification scripts, and a separate gem5 MIPS program experiment.

### Important scope distinction

- The Python implementation models the functional behaviour and datapath decisions of a small single-cycle MIPS instruction subset for learning and verification.
- The gem5 experiment runs a MIPS executable using gem5's existing `MipsAtomicSimpleCPU` model in syscall-emulation mode.
- The gem5 experiment is **not** a custom single-cycle CPU implemented inside gem5. Its statistics must not be interpreted as timing or performance measurements of the Python single-cycle model.

## 2. Supported instruction subset

The Python model supports:

| Instruction | Operation |
|---|---|
| `ADDI` | Add a sign-extended immediate to a register |
| `ADD` | Register addition |
| `SUB` | Register subtraction |
| `AND` | Bitwise AND |
| `OR` | Bitwise OR |
| `SLT` | Signed set-less-than |
| `LW` | Load a word from data memory |
| `SW` | Store a word to data memory |
| `BEQ` | Branch when two registers are equal |
| `J` | Jump using the MIPS 26-bit target field |

The implementation uses byte-addressed program counters. Sequential execution advances the PC by four bytes, and word accesses are expected to be aligned.

## 3. Project layout

Run the Python commands from the `submission/` directory.

```text
submission/
├── README.md
├── source/
│   ├── src/                 # Simulator, control unit, datapath, trace and viewer
│   ├── tests/               # Standalone Python test scripts
│   └── programs/             # MIPS assembly sources and executable files
├── results/
│   ├── gem5_add_print/       # gem5 configuration and statistics
│   ├── single_cycle_cycle_trace.csv
│   ├── execution_trace.csv
│   ├── datapath_view.html
│   └── verification_report.txt
├── documentation/            # Project report and supporting diagrams
└── screenshots/              # Evidence screenshots
```

Generated folders such as `__pycache__` are not required submission files.

## 4. Requirements

- Python 3.10 or later is recommended.
- The Python simulator, trace generator and HTML viewer use the Python standard library; no third-party Python package is required for these components.
- A web browser is required to open the generated HTML viewer.
- Re-running the gem5 experiment requires a gem5 build with MIPS ISA support and the corresponding MIPS executable.

The commands below use `python`, suitable for Windows PowerShell when Python is on `PATH`. On Linux, use `python3` if that is the installed command.

## 5. Run the Python MIPS simulator

From the `submission/` directory:

```bash
python source/src/mips_simulator.py
```

The script runs its built-in demonstration program and prints its execution trace, selected final register values, data memory and success checks.

## 6. Run the standalone test scripts

The project contains 12 standalone Python test scripts in `source/tests/`.

### Windows PowerShell

```powershell
$tests = Get-ChildItem .\source\tests\test_*.py
$tests += Get-Item .\source\tests\verify_mips.py

foreach ($test in $tests) {
    Write-Host "`n========== $($test.Name) ==========" -ForegroundColor Cyan
    python $test.FullName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "TEST FAILED: $($test.Name)" -ForegroundColor Red
        break
    }
}
```

### Linux / macOS shell

```bash
for test_file in source/tests/test_*.py source/tests/verify_mips.py; do
    echo "========== $test_file =========="
    python3 "$test_file" || exit 1
done
```

The recorded test run reported **117 passed checks across 12 scripts**. These are standalone scripts that execute their own checks; they are not pytest-collected test functions. Running `pytest` directly may therefore report no tests collected.

The separate `results/verification_report.txt` records 14 core instruction and architectural checks: 14 passed and 0 failed.

## 7. Generate the single-cycle execution trace

From the `submission/` directory:

```bash
python source/src/cycle_trace.py
```

This generates:

```text
results/single_cycle_cycle_trace.csv
```

The trace records each executed instruction, including PC values, control signals, register-file values, ALU values, branch/jump information, memory information and explicit MUX inputs/selections. The added MUX trace fields cover:

- `RegDst` — destination-register selection
- `ALUSrc` — second ALU operand selection
- `MemToReg` — register write-back source selection
- `PC` selection — sequential, branch or jump path

The demonstration program exercises arithmetic, memory, branch and jump behaviour. Its taken `BEQ` skips one `ADDI`, and the later `J` changes the next PC. The recorded trace contains eight executed instructions.

## 8. Generate and open the interactive datapath viewer

First generate the trace (Section 7), then run:

```bash
python source/src/generate_datapath_view.py
```

This generates:

```text
results/datapath_view.html
```

On Windows PowerShell, open it with:

```powershell
Start-Process .\results\datapath_view.html
```

Alternatively, open the `results` folder in File Explorer and double-click `datapath_view.html`.

Select an instruction in the browser to inspect its trace values, MUX selections and conceptual datapath components. The diagram is an **educational architectural visualization**: its signal routes are illustrative, not a gate-level netlist. Highlighting indicates conceptual participation in the selected instruction.

## 9. Separate gem5 experiment

The project includes a separate MIPS executable:

```text
source/programs/mips_add_print
```

The saved gem5 output is stored in:

```text
results/gem5_add_print/
```

The recorded configuration uses:

| Setting | Value |
|---|---|
| CPU model | `MipsAtomicSimpleCPU` |
| ISA | MIPS |
| Execution mode | Syscall emulation |
| Memory mode | Atomic |
| Memory object | `SimpleMemory` |
| Simulation frequency | 1 GHz |

### Verified local gem5 statistics

The latest local run's `stats.txt` reported:

| Statistic | Value |
|---|---:|
| Simulated instructions (`simInsts`) | 37 |
| Simulated operations (`simOps`) | 37 |
| Simulated ticks (`simTicks`) | 19,000 |
| CPU cycles (`system.cpu.numCycles`) | 39 |
| CPI (`system.cpu.cpi`) | 1.054054 |
| IPC (`system.cpu.ipc`) | 0.948718 |
| Host execution time (`hostSeconds`) | 0.01 s |

These values describe this gem5 run only. They are separate from the Python model's eight-instruction architectural trace and must not be treated as measured timing or performance of the Python single-cycle model.

To inspect the key values on Ubuntu, run:

```bash
grep -E "simInsts|simOps|simTicks|numCycles|cpi|ipc|hostSeconds" ~/gem5_external/run_add_print/stats.txt
```

Reproducing the experiment requires a compatible gem5 build with MIPS support. The exact invocation depends on the local gem5 build and configuration script.

## 10. Results and verification artifacts

| Artifact | Location | Purpose |
|---|---|---|
| Core verification report | `results/verification_report.txt` | Summary of 14 core checks |
| Architectural cycle trace | `results/single_cycle_cycle_trace.csv` | Per-instruction datapath trace, including MUX details |
| Execution trace | `results/execution_trace.csv` | Additional execution output |
| Interactive viewer | `results/datapath_view.html` | Instruction-by-instruction visualization |
| gem5 configuration | `results/gem5_add_print/config.ini` and `config.json` | Saved gem5 configuration |
| gem5 statistics | `results/gem5_add_print/stats.txt` | Statistics from the separate gem5 experiment |

## 11. Limitations

- The Python implementation is an educational functional/architectural model of the supported instruction subset; it is not a gate-level hardware implementation.
- The HTML datapath viewer is conceptual and does not represent a synthesized netlist or physical signal timing.
- The trace records architectural values and control decisions; it does not establish physical circuit timing.
- The gem5 run uses gem5's existing `MipsAtomicSimpleCPU` model. It is not a custom single-cycle MIPS CPU.
- gem5 statistics and Python model trace values come from different models and must not be directly equated.
- The project does not claim FPGA implementation, hardware synthesis or measured gate-level timing.

## 12. Documentation

The detailed project report and supporting documentation are available in the `documentation/` directory.