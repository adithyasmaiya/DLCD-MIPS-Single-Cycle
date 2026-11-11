import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from datapath_model import SingleCycleDatapath

RESULTS = ROOT.parent / "results"
RESULTS.mkdir(exist_ok=True)

program = [
    ("ADDI", 8, 0, 10),
    ("ADDI", 9, 0, 20),
    ("ADD", 10, 8, 9),
    ("SUB", 11, 9, 8),
    ("SW", 10, 0, 0),
    ("LW", 12, 0, 0),
    ("BEQ", 10, 12, 1),
    ("ADDI", 13, 0, 999),
    ("J", 9),
]

cpu = SingleCycleDatapath()
cpu.load_program(program)

registers, memory, trace = cpu.run()

headers = [
    "Cycle",
    "PC",
    "PCPlus4",
    "Instruction",
    "NextPC",
    "PCSource",

    # Main control signals
    "RegDst",
    "ALUSrc",
    "MemToReg",
    "RegWrite",
    "MemRead",
    "MemWrite",
    "Branch",
    "Jump",
    "ALUControl",

    # Register file
    "ReadRegister1",
    "ReadRegister2",
    "ReadData1",
    "ReadData2",
    "DestinationRegister",
    "RegisterWriteEnable",
    "RegisterWriteData",
    "WritebackSource",

    # Immediate and ALU
    "SignExtendedImmediate",
    "ALUInputB",
    "ALUResult",
    "Zero",

    # Branch datapath
    "ShiftedBranchOffset",
    "BranchTarget",
    "BranchTaken",

    # Jump datapath
    "JumpTarget26",
    "ShiftedJumpTarget",
    "PCUpper4",
    "JumpAddress",

    # Memory
    "MemoryAddress",
    "MemoryReadData",

    # RegDst MUX
    "RegDstInput0",
    "RegDstInput1",
    "RegDstSelected",

    # ALUSrc MUX
    "ALUSrcInput0",
    "ALUSrcInput1",
    "ALUSrcSelected",

    # MemToReg MUX
    "MemToRegInput0",
    "MemToRegInput1",
    "MemToRegSelected",

    # Next-PC MUX
    "PCMuxInput0",
    "PCMuxInput1",
    "PCMuxInput2",
    "PCMuxSelected",

    # Additional execution information
    "ExecutionDetails",
]

rows = []

for item in trace:
    instruction = item["instruction"]
    control = item["control"]

    row = {
        "Cycle": item["cycle"],
        "PC": item["pc"],
        "PCPlus4": item["pc_plus4"],
        "Instruction": " ".join(map(str, instruction)),
        "NextPC": item["next_pc"],
        "PCSource": item["pc_source"],

        # Main control signals
        "RegDst": control[0],
        "ALUSrc": control[1],
        "MemToReg": control[2],
        "RegWrite": control[3],
        "MemRead": control[4],
        "MemWrite": control[5],
        "Branch": control[6],
        "Jump": control[7],
        "ALUControl": control[8],

        # Register file
        "ReadRegister1": item["read_register1"],
        "ReadRegister2": item["read_register2"],
        "ReadData1": item["read_data1"],
        "ReadData2": item["read_data2"],
        "DestinationRegister": item["destination_register"],
        "RegisterWriteEnable": item["register_write_enable"],
        "RegisterWriteData": item["register_write_data"],
        "WritebackSource": item["writeback_source"],

        # Immediate and ALU
        "SignExtendedImmediate": item["sign_extended_imm"],
        "ALUInputB": item["alu_b"],
        "ALUResult": item["alu_result"],
        "Zero": item["zero"],

        # Branch datapath
        "ShiftedBranchOffset": item["shifted_branch_offset"],
        "BranchTarget": item["branch_target"],
        "BranchTaken": item["branch_taken"],

        # Jump datapath
        "JumpTarget26": item["jump_target_26"],
        "ShiftedJumpTarget": item["shifted_jump_target"],
        "PCUpper4": item["pc_upper_4"],
        "JumpAddress": item["jump_address"],

        # Memory
        "MemoryAddress": item["memory_address"],
        "MemoryReadData": item["memory_read_data"],

        # RegDst MUX
        "RegDstInput0": item["regdst_input0"],
        "RegDstInput1": item["regdst_input1"],
        "RegDstSelected": item["regdst_selected"],

        # ALUSrc MUX
        "ALUSrcInput0": item["alusrc_input0"],
        "ALUSrcInput1": item["alusrc_input1"],
        "ALUSrcSelected": item["alusrc_selected"],

        # MemToReg MUX
        "MemToRegInput0": item["memtoreg_input0"],
        "MemToRegInput1": item["memtoreg_input1"],
        "MemToRegSelected": item["memtoreg_selected"],

        # Next-PC MUX
        "PCMuxInput0": item["pc_mux_input0"],
        "PCMuxInput1": item["pc_mux_input1"],
        "PCMuxInput2": item["pc_mux_input2"],
        "PCMuxSelected": item["pc_mux_selected"],

        # Additional execution information
        "ExecutionDetails": (
            f"ALU={item['alu_result']}; "
            f"PCSource={item['pc_source']}; "
            f"Writeback={item['writeback_source']}; "
            f"ALUSrc={item['alusrc_selected']}; "
            f"RegDst={item['regdst_selected']}; "
            f"MemToReg={item['memtoreg_selected']}"
        ),
    }

    rows.append(row)

output = RESULTS / "single_cycle_cycle_trace.csv"

with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print("=" * 85)
print("SINGLE-CYCLE MIPS COMPLETE DATAPATH TRACE")
print("=" * 85)

for row in rows:
    print(
        f"Cycle {row['Cycle']:02d} | "
        f"PC={row['PC']:08X} | "
        f"{row['Instruction']:<18} | "
        f"NextPC={row['NextPC']:08X} | "
        f"PCSource={row['PCSource']}"
    )

print("\nFINAL REGISTER STATE")
print("-" * 40)

for index in [8, 9, 10, 11, 12, 13]:
    print(f"R{index} = {registers[index]}")

print("\nFINAL MEMORY STATE")
print(memory)

print("\nTRACE SUMMARY")
print("-" * 40)
print("Executed instructions:", len(trace))
print("Architectural cycles assigned:", len(rows))
print("Total trace columns:", len(headers))
print("CSV saved:", output)

# Functional checks
assert len(rows) == len(trace)
assert registers[10] == 30
assert registers[11] == 10
assert registers[12] == 30
assert registers[13] == 0
assert memory.get(0) == 30

# Datapath checks
assert trace[0]["alu_result"] == 10
assert trace[2]["alu_result"] == 30
assert trace[4]["memory_address"] == 0
assert trace[5]["write_value"] == 30
assert trace[6]["branch_taken"] is True
assert trace[6]["next_pc"] == 32
assert trace[7]["pc_source"] == "JUMP"
assert trace[7]["next_pc"] == 36

# MUX checks
assert trace[0]["alusrc_selected"] == "IMMEDIATE"
assert trace[0]["regdst_selected"] == "RT"
assert trace[0]["memtoreg_selected"] == "ALU"

assert trace[2]["alusrc_selected"] == "REGISTER"
assert trace[2]["regdst_selected"] == "RD"

assert trace[5]["memtoreg_selected"] == "MEMORY"
assert trace[6]["pc_mux_selected"] == "BRANCH"
assert trace[7]["pc_mux_selected"] == "JUMP"

print("\nALL CYCLE-TRACE AND MUX CHECKS PASSED")