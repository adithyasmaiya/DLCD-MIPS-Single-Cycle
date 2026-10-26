
import csv
from pathlib import Path

from mips_simulator import SingleCycleMIPS
from control_unit import CONTROL_SIGNALS

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

program = [
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("ADD", 10, 8, 9),
    ("SUB", 11, 9, 8),
    ("SW", 10, 0, 0),
    ("LW", 12, 0, 0),
    ("BEQ", 10, 12, 1),
    ("ADDI", 13, 0, 999),  # Skipped by BEQ
    ("J", 9),
]

signal_names = [
    "RegDst", "ALUSrc", "MemToReg", "RegWrite",
    "MemRead", "MemWrite", "Branch", "Jump", "ALUOp"
]

cpu = SingleCycleMIPS()
cpu.load_program(program)
registers, memory, trace = cpu.run()

rows = []

for item in trace:
    op = item["instruction"][0]
    signals = CONTROL_SIGNALS[op]

    row = {
        "PC": item["pc"],
        "Instruction": " ".join(map(str, item["instruction"])),
        "NextPC": item["next_pc"],
        "Details": item["details"],
    }

    row.update(dict(zip(signal_names, signals)))
    rows.append(row)

output = RESULTS / "single_cycle_control_trace.csv"

with output.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("SINGLE-CYCLE MIPS CONTROL AND EXECUTION TRACE")
print("-" * 72)

for row in rows:
    print(
        f"PC={row['PC']:02d} | {row['Instruction']:<20} "
        f"| NextPC={row['NextPC']:02d} "
        f"| RegWrite={row['RegWrite']} "
        f"| MemRead={row['MemRead']} "
        f"| MemWrite={row['MemWrite']} "
        f"| Branch={row['Branch']} "
        f"| Jump={row['Jump']}"
    )

print("\nFINAL STATE")
print("R10 =", registers[10])
print("R11 =", registers[11])
print("R12 =", registers[12])
print("R13 =", registers[13])
print("Memory =", memory)

assert registers[10] == 30
assert registers[11] == 10
assert registers[12] == 30
assert registers[13] == 0
assert memory.get(0) == 30

print("\nInstructions executed:", len(trace))
print("Control trace saved to:", output)
print("FUNCTIONAL CHECKS PASSED")
