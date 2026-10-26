import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mips_simulator import SingleCycleMIPS
from src.control_unit import CONTROL_SIGNALS

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

checks = []

def check(name, condition, detail=""):
    passed = bool(condition)
    checks.append((name, passed, detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))

# Test 1: Arithmetic, logic, memory and control flow.
cpu = SingleCycleMIPS()
cpu.load_program([
    ("ADDI", 8, 0, 10),    # R8 = 10
    ("ADDI", 9, 0, 20),    # R9 = 20
    ("ADD", 10, 8, 9),     # R10 = 30
    ("SUB", 11, 9, 8),     # R11 = 10
    ("AND", 12, 8, 9),     # R12 = 0
    ("OR", 13, 8, 9),      # R13 = 30
    ("SLT", 14, 8, 9),     # R14 = 1
    ("SW", 10, 0, 0),      # MEM[0] = 30
    ("LW", 15, 0, 0),      # R15 = 30
    ("BEQ", 10, 15, 1),    # Skip next instruction
    ("ADDI", 16, 0, 999),
    ("J", 12),             # Jump outside this program
])

registers, memory, trace = cpu.run()

check("ADDI", registers[8] == 10 and registers[9] == 20)
check("ADD", registers[10] == 30)
check("SUB", registers[11] == 10)
check("AND", registers[12] == 0)
check("OR", registers[13] == 30)
check("SLT", registers[14] == 1)
check("SW", memory.get(0) == 30)
check("LW", registers[15] == 30)
check("BEQ", registers[16] == 0, "Instruction after taken branch skipped")
check("J", trace[-1]["instruction"][0] == "J")
check(
    "Byte-addressed PC",
    [item["pc"] for item in trace]
    == [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 44]
)

check(
    "Branch target",
    trace[9]["next_pc"] == 44
    and trace[10]["pc"] == 44
)
check("Register zero", registers[0] == 0)

# Test 2: Required control-unit entries.
required = ["ADD", "SUB", "AND", "OR", "SLT",
            "ADDI", "LW", "SW", "BEQ", "J"]

check(
    "Control table coverage",
    all(op in CONTROL_SIGNALS for op in required),
    f"{len(required)} required instruction types"
)

# Save execution trace as CSV.
with open(RESULTS / "execution_trace.csv",
          "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["pc", "instruction", "details", "next_pc"]
    )
    writer.writeheader()
    for row in trace:
        writer.writerow({
            **row,
            "instruction": " ".join(map(str, row["instruction"]))
        })

# Save verification report.
with open(RESULTS / "verification_report.txt", "w") as file:
    for name, passed, detail in checks:
        file.write(
            f"{'PASS' if passed else 'FAIL'} | {name} | {detail}\n"
        )

    file.write(f"\nPassed: {sum(p for _, p, _ in checks)}")
    file.write(f"\nFailed: {sum(not p for _, p, _ in checks)}\n")

print("\nExecution trace saved to results/execution_trace.csv")
print("Verification report saved to results/verification_report.txt")
print(f"\nPassed: {sum(p for _, p, _ in checks)}/{len(checks)}")

if not all(p for _, p, _ in checks):
    raise SystemExit("Verification failed.")
