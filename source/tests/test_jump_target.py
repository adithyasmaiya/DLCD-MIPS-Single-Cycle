
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mips_simulator import SingleCycleMIPS

cpu = SingleCycleMIPS()

cpu.load_program([
    ("J", 3),                 # Jump from PC=0 to PC=12
    ("ADDI", 8, 0, 111),      # PC=4: must be skipped
    ("ADDI", 9, 0, 222),      # PC=8: must be skipped
    ("ADDI", 10, 0, 333),     # PC=12: must execute
])

registers, memory, trace = cpu.run()

checks = [
    ("Jump target is PC=12", trace[0]["next_pc"] == 12),
    ("Target instruction executes", registers[10] == 333),
    ("First skipped instruction stays unchanged", registers[8] == 0),
    ("Second skipped instruction stays unchanged", registers[9] == 0),
    ("Only jump and target instruction execute",
     [item["pc"] for item in trace] == [0, 12]),
]

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nJump-target tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("JUMP TARGET VERIFICATION PASSED")
