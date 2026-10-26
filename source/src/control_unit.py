CONTROL_SIGNALS = {
    # RegDst, ALUSrc, MemToReg, RegWrite, MemRead,
    # MemWrite, Branch, Jump, ALUOp
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

HEADERS = (
    "Instruction", "RegDst", "ALUSrc", "MemToReg",
    "RegWrite", "MemRead", "MemWrite", "Branch",
    "Jump", "ALUOp"
)

def print_control_table():
    print("SINGLE-CYCLE MIPS CONTROL UNIT")
    print("-" * 100)
    print(" | ".join(HEADERS))
    print("-" * 100)

    for instruction, signals in CONTROL_SIGNALS.items():
        print(" | ".join(map(str, (instruction, *signals))))

if __name__ == "__main__":
    print_control_table()
