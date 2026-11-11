
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import sign_extend16, SingleCycleDatapath

checks = [
    ("Zero extension boundary", sign_extend16(0) == 0x00000000),
    ("Positive value", sign_extend16(10) == 0x0000000A),
    ("Maximum positive", sign_extend16(32767) == 0x00007FFF),
    ("Negative one", sign_extend16(-1) == 0xFFFFFFFF),
    ("Negative ten", sign_extend16(-10) == 0xFFFFFFF6),
    ("Minimum negative", sign_extend16(-32768) == 0xFFFF8000),
]

cpu = SingleCycleDatapath()
cpu.load_program([
    ("ADDI", 8, 0, -10),
])

_, _, trace = cpu.run()

checks.append((
    "ADDI sign extension in datapath",
    trace[0]["sign_extended_imm"] == 0xFFFFFFF6
    and cpu.reg[8] == 0xFFFFFFF6
))

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nSign-extension tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("SIGN EXTENSION VERIFIED")