
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mips_simulator import SingleCycleMIPS
from control_unit import CONTROL_SIGNALS

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
    ("ADDI", 13, 0, 999),
    ("J", 9),
]

cpu = SingleCycleMIPS()
cpu.load_program(program)
registers, memory, trace = cpu.run()

headers = [
    "Cycle", "PC", "Instruction", "NextPC",
    "RegDst", "ALUSrc", "MemToReg", "RegWrite",
    "MemRead", "MemWrite", "Branch", "Jump", "ALUOp",
    "ExecutionDetails",
]

rows = []

for cycle, item in enumerate(trace, start=1):
    instruction = item["instruction"]
    opcode = instruction[0]
    signals = CONTROL_SIGNALS[opcode]

    rows.append({
        "Cycle": cycle,
        "PC": item["pc"],
        "Instruction": " ".join(map(str, instruction)),
        "NextPC": item["next_pc"],
        **dict(zip(headers[4:13], signals)),
        "ExecutionDetails": item["details"],
    })

output = RESULTS / "single_cycle_cycle_trace.csv"

with output.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print("SINGLE-CYCLE ARCHITECTURAL TRACE")
print("-" * 78)

for row in rows:
    print(
        f"Cycle {row['Cycle']:02d} | PC={row['PC']:02d} "
        f"| {row['Instruction']:<18} "
        f"| NextPC={row['NextPC']:02d}"
    )

print("\nExecuted instructions:", len(trace))
print("Architectural cycles assigned:", len(rows))
print("Final R10:", registers[10])
print("Final R11:", registers[11])
print("Final R12:", registers[12])
print("Memory:", memory)
print("CSV saved:", output)

assert len(rows) == len(trace)
assert registers[10] == 30
assert registers[11] == 10
assert registers[12] == 30
assert registers[13] == 0
assert memory.get(0) == 30

print("CYCLE-TRACE CHECKS PASSED")
