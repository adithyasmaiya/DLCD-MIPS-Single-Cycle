
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath

cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("ADD", 10, 8, 9),
    ("SUB", 11, 9, 8),
    ("SW", 10, 0, 0),
    ("LW", 12, 0, 0),
    ("BEQ", 10, 12, 1),
    ("ADDI", 13, 0, 999),
    ("J", 9),
])

registers, memory, trace = cpu.run()

checks = [
    ("ADD result", registers[10] == 30),
    ("SUB result", registers[11] == 10),
    ("Store result", memory.get(0) == 30),
    ("Load result", registers[12] == 30),
    ("Taken branch", registers[13] == 0),
    ("Register zero", registers[0] == 0),
    ("Branch next PC", trace[6]["next_pc"] == 32),
    ("Jump target", trace[7]["next_pc"] == 36),
    ("One cycle per executed instruction", len(trace) == 8),
]

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nDatapath tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("DATAPATH VERIFICATION PASSED")

# Test ALU Zero flag for an ADD instruction
zero_cpu = SingleCycleDatapath()

zero_cpu.load_program([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, -10),
    ("ADD", 10, 8, 9),
])

_, _, zero_trace = zero_cpu.run()

zero_test = (
    zero_cpu.reg[10] == 0
    and zero_trace[2]["alu_result"] == 0
    and zero_trace[2]["zero"] is True
)

print(f"[{'PASS' if zero_test else 'FAIL'}] ALU Zero flag for ADD")

if not zero_test:
    raise SystemExit(1)