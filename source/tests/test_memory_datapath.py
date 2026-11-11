
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath


checks = []

# Test 1: Basic store and load
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 100),
    ("ADDI", 9, 0, 42),
    ("SW", 9, 0, 8),
    ("LW", 10, 0, 8),
])

cpu.run()

sw_trace = cpu.trace[2]
lw_trace = cpu.trace[3]

checks.extend([
    ("Store memory address", sw_trace["memory_address"] == 100),
    ("Store data", cpu.memory.get(100) == 42),
    ("SW MemWrite enabled", sw_trace["control"][5] == 1),
    ("SW MemRead disabled", sw_trace["control"][4] == 0),
    ("Load memory address", lw_trace["memory_address"] == 100),
    ("LW MemRead enabled", lw_trace["control"][4] == 1),
    ("LW MemWrite disabled", lw_trace["control"][5] == 0),
    ("Loaded register value", cpu.reg[10] == 42),
    ("LW write-back data", lw_trace["register_write_data"] == 42),
])

# Test 2: Negative memory offset
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 20),
    ("ADDI", 9, 0, 55),
    ("SW", 9, -4, 8),
    ("LW", 10, -4, 8),
])

cpu.run()

checks.extend([
    ("Negative offset sign extension",
     cpu.trace[2]["sign_extended_imm"] == 0xFFFFFFFC),

    ("Negative offset address calculation",
     cpu.trace[2]["memory_address"] == 16),

    ("Negative offset load result",
     cpu.reg[10] == 55),
])

# Test 3: Unaligned memory access
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 10),
    ("LW", 9, 0, 8),
])

unaligned_rejected = False

try:
    cpu.run()
except ValueError as error:
    unaligned_rejected = "Unaligned" in str(error)

checks.append((
    "Reject unaligned word access",
    unaligned_rejected
))

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nMemory datapath tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("MEMORY DATAPATH VERIFIED")