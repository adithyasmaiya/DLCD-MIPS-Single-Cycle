
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from control_unit import CONTROL_SIGNALS

# Order:
# RegDst, ALUSrc, MemToReg, RegWrite,
# MemRead, MemWrite, Branch, Jump, ALUOp

EXPECTED = {
    "ADD":  (1, 0, 0, 1, 0, 0, 0, 0, "R_TYPE"),
    "SUB":  (1, 0, 0, 1, 0, 0, 0, 0, "R_TYPE"),
    "AND":  (1, 0, 0, 1, 0, 0, 0, 0, "R_TYPE"),
    "OR":   (1, 0, 0, 1, 0, 0, 0, 0, "R_TYPE"),
    "SLT":  (1, 0, 0, 1, 0, 0, 0, 0, "R_TYPE"),
    "ADDI": (0, 1, 0, 1, 0, 0, 0, 0, "ADD"),
    "LW":   (0, 1, 1, 1, 1, 0, 0, 0, "ADD"),
    "SW":   ("X", 1, "X", 0, 0, 1, 0, 0, "ADD"),
    "BEQ":  ("X", 0, "X", 0, 0, 0, 1, 0, "SUB"),
    "J":    ("X", "X", "X", 0, 0, 0, 0, 1, "NONE"),
}

passed = 0
failed = 0

for instruction, expected in EXPECTED.items():
    actual = CONTROL_SIGNALS.get(instruction)

    if actual == expected:
        print(f"[PASS] {instruction}")
        passed += 1
    else:
        print(f"[FAIL] {instruction}")
        print(f"       Expected: {expected}")
        print(f"       Actual:   {actual}")
        failed += 1

print(f"\nControl-unit tests passed: {passed}/{len(EXPECTED)}")
print(f"Failed: {failed}")

if failed:
    raise SystemExit(1)

print("CONTROL UNIT VERIFICATION PASSED")
