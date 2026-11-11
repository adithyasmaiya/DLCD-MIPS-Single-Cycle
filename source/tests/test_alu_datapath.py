
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath


checks = []


def execute(program):
    cpu = SingleCycleDatapath()
    cpu.load_program(program)
    cpu.run()
    return cpu


# Test 1: ADD
cpu = execute([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("ADD", 10, 8, 9),
])

checks.append(("ADD operation", cpu.reg[10] == 30))
checks.append(("ADD ALU result", cpu.trace[2]["alu_result"] == 30))


# Test 2: SUB
cpu = execute([
    ("ADDI", 8, 0, 20),
    ("ADDI", 9, 0, 10),
    ("SUB", 10, 8, 9),
])

checks.append(("SUB operation", cpu.reg[10] == 10))


# Test 3: AND
cpu = execute([
    ("ADDI", 8, 0, 12),
    ("ADDI", 9, 0, 10),
    ("AND", 10, 8, 9),
])

checks.append(("AND operation", cpu.reg[10] == 8))


# Test 4: OR
cpu = execute([
    ("ADDI", 8, 0, 12),
    ("ADDI", 9, 0, 10),
    ("OR", 10, 8, 9),
])

checks.append(("OR operation", cpu.reg[10] == 14))


# Test 5: SLT - positive comparison
cpu = execute([
    ("ADDI", 8, 0, 5),
    ("ADDI", 9, 0, 10),
    ("SLT", 10, 8, 9),
])

checks.append(("SLT positive comparison", cpu.reg[10] == 1))


# Test 6: SLT - negative comparison
cpu = execute([
    ("ADDI", 8, 0, -5),
    ("ADDI", 9, 0, 3),
    ("SLT", 10, 8, 9),
])

checks.append(("SLT negative comparison", cpu.reg[10] == 1))


# Test 7: Zero flag
cpu = execute([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, -10),
    ("ADD", 10, 8, 9),
])

checks.append(("ALU Zero flag", cpu.trace[2]["zero"] is True))


# Test 8: Nonzero flag
cpu = execute([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 5),
    ("ADD", 10, 8, 9),
])

checks.append(("ALU nonzero flag", cpu.trace[2]["zero"] is False))


# Test 9: 32-bit wraparound
cpu = execute([
    ("ADDI", 8, 0, 32767),
    ("ADDI", 9, 0, 1),
    ("ADD", 10, 8, 9),
])

checks.append(("32-bit arithmetic result", cpu.reg[10] == 32768))


passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nALU datapath tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("ALU DATAPATH VERIFIED")