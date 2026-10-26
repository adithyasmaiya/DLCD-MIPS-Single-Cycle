
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mips_simulator import SingleCycleMIPS

cpu = SingleCycleMIPS()

cpu.load_program([
    ("ADDI", 8, 0, -5),  # R8 = -5
    ("ADDI", 9, 0, 3),   # R9 = 3
    ("SLT", 10, 8, 9),   # Signed comparison: -5 < 3
    ("SW", 8, 4, 0),     # MEM[4] = -5
    ("LW", 11, 4, 0),    # R11 = MEM[4]
    ("ADDI", 0, 0, 99),  # R0 must remain zero
    ("SUB", 12, 9, 8),   # R12 = 3 - (-5) = 8
])

registers, memory, trace = cpu.run()

checks = [
    ("Negative immediate", cpu.signed(registers[8]) == -5),
    ("Signed SLT", registers[10] == 1),
    ("Negative value stored", memory.get(4) == 0xFFFFFFFB),
    ("Negative value loaded", registers[11] == 0xFFFFFFFB),
    ("Register zero invariant", registers[0] == 0),
    ("Subtraction with negative operand",
     registers[12] == 8),
    ("Byte-addressed PC",
     [row["pc"] for row in trace] ==
     [0, 4, 8, 12, 16, 20, 24]),
]

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nEdge-case tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("EDGE-CASE VERIFICATION PASSED")
