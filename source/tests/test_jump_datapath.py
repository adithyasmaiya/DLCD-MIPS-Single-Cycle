from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath


checks = []

# Test 1: Normal jump from PC = 0
cpu = SingleCycleDatapath()
cpu.load_program([("J", 9)])
cpu.step()

trace = cpu.trace[0]

checks.extend([
    ("26-bit jump target", trace["jump_target_26"] == 9),
    ("Jump target shift-left-2", trace["shifted_jump_target"] == 36),
    ("Upper four PC bits", trace["pc_upper_4"] == 0),
    ("Final jump address", trace["jump_address"] == 36),
    ("Next PC", trace["next_pc"] == 36),
    ("PC source selection", trace["pc_source"] == "JUMP"),
])

# Test 2: Jump with nonzero upper PC bits
cpu = SingleCycleDatapath()
cpu.load_program(
    [("J", 9)],
    start_address=0x10000000
)
cpu.step()

trace = cpu.trace[0]

checks.extend([
    ("Nonzero starting PC", trace["pc"] == 0x10000000),
    ("PC + 4", trace["pc_plus4"] == 0x10000004),
    ("Preserve upper four bits", trace["pc_upper_4"] == 0x10000000),
    ("Jump address with upper bits", trace["jump_address"] == 0x10000024),
    ("Final next PC", trace["next_pc"] == 0x10000024),
])

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nJump datapath tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("JUMP DATAPATH VERIFIED")