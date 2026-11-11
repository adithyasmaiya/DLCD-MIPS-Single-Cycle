from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath


def run_program(program):
    cpu = SingleCycleDatapath()
    cpu.load_program(program)
    _, _, trace = cpu.run()
    return trace


checks = []

# Test 1: Taken branch
trace = run_program([
    ("ADDI", 8, 0, 10),
    ("BEQ", 8, 8, 2),
])

branch = trace[1]

checks.append(("PC + 4 calculation", branch["pc_plus4"] == 8))
checks.append(("Sign-extended branch offset", branch["sign_extended_imm"] == 2))
checks.append(("Shift-left-2 branch offset", branch["shifted_branch_offset"] == 8))
checks.append(("Branch target calculation", branch["branch_target"] == 16))
checks.append(("Taken branch decision", branch["branch_taken"] is True))

# Test 2: Not-taken branch
trace = run_program([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("BEQ", 8, 9, 2),
])

branch = trace[2]

checks.append(("Not-taken branch decision", branch["branch_taken"] is False))
checks.append(("Sequential PC after not-taken branch", branch["next_pc"] == 12))

# Test 3: Negative branch offset
negative_cpu = SingleCycleDatapath()

negative_cpu.load_program([
    ("BEQ", 0, 0, -1),
])

negative_cpu.step()
branch = negative_cpu.trace[0]

checks.append((
    "Negative branch offset sign extension",
    branch["sign_extended_imm"] == 0xFFFFFFFF
))

checks.append((
    "Negative branch offset shift",
    branch["shifted_branch_offset"] == 0xFFFFFFFC
))

checks.append((
    "Negative branch target",
    branch["branch_target"] == 0
))

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nBranch datapath tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("BRANCH DATAPATH VERIFIED")