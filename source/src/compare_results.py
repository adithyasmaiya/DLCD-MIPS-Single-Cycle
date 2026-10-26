
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

cycle_file = RESULTS / "single_cycle_cycle_trace.csv"
gem5_file = RESULTS / "gem5_add_print" / "stats.txt"

with cycle_file.open(newline="") as f:
    rows = list(csv.DictReader(f))

cycles = len(rows)

stats = {}
for line in gem5_file.read_text().splitlines():
    parts = line.split()
    if len(parts) >= 2:
        stats[parts[0]] = parts[1]

gem5_insts = int(stats["simInsts"])
gem5_ticks = int(stats["simTicks"])
sim_freq = int(stats["simFreq"])

# Current gem5 configuration uses a 1 GHz clock.
cpu_frequency = 1_000_000_000
ticks_per_cycle = sim_freq // cpu_frequency

gem5_cycles = gem5_ticks / ticks_per_cycle
gem5_cpi = gem5_cycles / gem5_insts

report = f"""
DLCD MINI PROJECT - SIMULATION COMPARISON
=========================================

PYTHON SINGLE-CYCLE ARCHITECTURAL MODEL
-----------------------------------------
Executed instructions : {cycles}
Assigned cycles       : {cycles}
Assumed CPI           : 1.00
Processor             : Educational MIPS datapath

GEM5 REFERENCE SIMULATION
-----------------------------------------
Executed instructions : {gem5_insts}
Simulated ticks       : {gem5_ticks}
Configured clock      : 1 GHz
Ticks per clock cycle : {ticks_per_cycle}
Estimated CPU cycles  : {gem5_cycles:.2f}
Calculated CPI        : {gem5_cpi:.3f}
Processor             : MipsAtomicSimpleCPU

INTERPRETATION
-----------------------------------------
The Python model assumes one architectural cycle
per executed instruction.

gem5 uses its existing atomic CPU model.
The gem5 CPI is calculated from simulated ticks
and the configured clock frequency.

These measurements come from different programs.
They are not a direct performance comparison.

Neither result establishes gate-level timing
or a custom single-cycle CPU inside gem5.
"""

output = RESULTS / "simulation_comparison.txt"
output.write_text(report)

print(report)
print("Saved:", output)
