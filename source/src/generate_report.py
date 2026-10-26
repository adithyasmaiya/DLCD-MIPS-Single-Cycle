
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPORT = RESULTS / "DLCD_MIPS_Project_Report.md"

def read_file(path):
    return path.read_text() if path.exists() else "Not available yet."

def extract_stats(path):
    wanted = {"simTicks", "simInsts", "simOps", "simSeconds"}
    found = {}

    if path.exists():
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] in wanted:
                found[parts[0]] = parts[1]

    return found

verification = read_file(RESULTS / "verification_report.txt")
control_trace = RESULTS / "single_cycle_control_trace.csv"
gem5_stats = extract_stats(RESULTS / "gem5_add_print" / "stats.txt")

lines = [
    "# DLCD Mini Project: Single-Cycle MIPS and gem5",
    "",
    f"Report generated: {date.today().isoformat()}",
    "",
    "## 1. Project objective",
    "",
    "Develop and verify an educational 32-bit MIPS instruction-level "
    "functional model, document its control signals, and execute a "
    "MIPS binary using gem5.",
    "",
    "## 2. Python model",
    "",
    "The model supports ADDI, ADD, SUB, AND, OR, SLT, LW, SW, BEQ and J.",
    "Its PC uses byte addresses, with sequential instructions advancing "
    "by four bytes.",
    "",
    "## 3. Verification artifacts",
    "",
    f"- Control/execution CSV exists: {control_trace.exists()}",
    "- Main verification report: `results/verification_report.txt`",
    "- Control-unit test: `tests/test_control_unit.py`",
    "- Edge-case test: `tests/test_edge_cases.py`",
    "",
    "### Main verification report",
    "",
    "```text",
    verification.rstrip(),
    "```",
    "",
    "## 4. gem5 execution",
    "",
    "The test binary `programs/mips_add_print` printed `30` and exited "
    "normally in gem5 syscall-emulation mode.",
    "",
    "The CPU model used was `MipsAtomicSimpleCPU`. This is gem5's existing "
    "atomic CPU model, not a custom single-cycle CPU implementation.",
    "",
    "### Recorded statistics",
    "",
]

if gem5_stats:
    for key, value in gem5_stats.items():
        lines.append(f"- {key}: {value}")
else:
    lines.append("Statistics were not found in the expected output file.")

lines += [
    "",
    "## 5. Interpretation and limitations",
    "",
    "The Python model is an instruction-level functional model. Its "
    "instruction trace and control table are useful for verifying "
    "functional behavior, but they do not establish physical single-cycle "
    "datapath timing.",
    "",
    "The gem5 run demonstrates execution of a real MIPS ELF binary using "
    "gem5's MIPS syscall-emulation support. Its statistics describe that "
    "gem5 configuration and must not be presented as measurements of a "
    "custom single-cycle processor.",
    "",
    "Further work is needed to integrate the control logic and datapath "
    "into a cycle-accurate or hardware-level single-cycle implementation, "
    "if required by the project specification.",
    "",
    "## 6. Project files",
    "",
    "- `src/mips_simulator.py`",
    "- `src/control_unit.py`",
    "- `src/single_cycle_demo.py`",
    "- `tests/verify_mips.py`",
    "- `tests/test_control_unit.py`",
    "- `tests/test_edge_cases.py`",
    "- `docs/datapath.mmd`",
    "- `results/single_cycle_control_trace.csv`",
    "- `results/gem5_add_print/stats.txt`",
    "",
]

REPORT.write_text("\n".join(lines))
print("Report generated:", REPORT)
print("CSV trace available:", control_trace.exists())
print("gem5 statistics found:", bool(gem5_stats))
