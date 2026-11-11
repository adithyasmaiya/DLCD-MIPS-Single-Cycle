
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath


checks = []

# Test 1: R-type register reads and destination selection
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("ADD", 10, 8, 9),
])

cpu.run()

trace = cpu.trace[2]

checks.extend([
    ("First register address", trace["read_register1"] == 8),
    ("Second register address", trace["read_register2"] == 9),
    ("First register data", trace["read_data1"] == 10),
    ("Second register data", trace["read_data2"] == 20),
    ("R-type destination register", trace["destination_register"] == 10),
    ("Register write enabled", trace["register_write_enable"] is True),
    ("ALU write-back source", trace["writeback_source"] == "ALU"),
    ("ALU write-back data", trace["register_write_data"] == 30),
])

# Test 2: I-type destination selection
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 25),
])

cpu.run()

trace = cpu.trace[0]

checks.extend([
    ("I-type destination register", trace["destination_register"] == 8),
    ("I-type write-back data", trace["register_write_data"] == 25),
])

# Test 3: Load instruction write-back
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 8, 0, 40),
    ("SW", 8, 0, 0),
    ("LW", 9, 0, 0),
])

cpu.run()

trace = cpu.trace[2]

checks.extend([
    ("LW destination register", trace["destination_register"] == 9),
    ("LW write-back source", trace["writeback_source"] == "DATA_MEMORY"),
    ("LW write-back data", trace["register_write_data"] == 40),
])

# Test 4: Register zero protection
cpu = SingleCycleDatapath()

cpu.load_program([
    ("ADDI", 0, 0, 100),
])

cpu.run()

checks.append((
    "Register zero remains unchanged",
    cpu.reg[0] == 0
))

passed = 0

for name, condition in checks:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    passed += int(condition)

print(f"\nRegister-file tests: {passed}/{len(checks)} passed")

if passed != len(checks):
    raise SystemExit(1)

print("REGISTER FILE VERIFIED")