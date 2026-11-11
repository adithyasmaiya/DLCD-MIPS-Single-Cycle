
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath, validate_imm16


def check_invalid_instruction(program):
    cpu = SingleCycleDatapath()
    cpu.load_program(program)

    try:
        cpu.step()
        return False
    except ValueError:
        return True


checks = [
    ("Maximum valid immediate", validate_imm16(32767) == 32767),
    ("Minimum valid immediate", validate_imm16(-32768) == -32768),
    ("Reject 32768", check_invalid_instruction([("ADDI", 8, 0, 32768)])),
    ("Reject -32769", check_invalid_instruction([("ADDI", 8, 0, -32769)])),
    ("Reject invalid LW offset", check_invalid_instruction([("LW", 8, 32768, 0)])),
    ("Reject invalid SW offset", check_invalid_instruction([("SW", 8, -32769, 0)])),
    ("Reject invalid BEQ offset", check_invalid_instruction([("BEQ", 0, 0, 32768)])),
]

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nImmediate validation tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("IMMEDIATE VALIDATION PASSED")