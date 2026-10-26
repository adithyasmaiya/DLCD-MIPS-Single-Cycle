
MASK = 0xFFFFFFFF


def u32(value):
    return value & MASK


def signed(value):
    value = u32(value)
    return value - 0x100000000 if value & 0x80000000 else value


def decode(op):
    # RegDst, ALUSrc, MemToReg, RegWrite,
    # MemRead, MemWrite, Branch, Jump, ALUControl
    table = {
        "ADD":  (1, 0, 0, 1, 0, 0, 0, 0, "ADD"),
        "SUB":  (1, 0, 0, 1, 0, 0, 0, 0, "SUB"),
        "AND":  (1, 0, 0, 1, 0, 0, 0, 0, "AND"),
        "OR":   (1, 0, 0, 1, 0, 0, 0, 0, "OR"),
        "SLT":  (1, 0, 0, 1, 0, 0, 0, 0, "SLT"),
        "ADDI": (0, 1, 0, 1, 0, 0, 0, 0, "ADD"),
        "LW":   (0, 1, 1, 1, 1, 0, 0, 0, "ADD"),
        "SW":   ("X", 1, "X", 0, 0, 1, 0, 0, "ADD"),
        "BEQ":  ("X", 0, "X", 0, 0, 0, 1, 0, "SUB"),
        "J":    ("X", "X", "X", 0, 0, 0, 0, 1, "NONE"),
    }

    if op not in table:
        raise ValueError(f"Unsupported instruction: {op}")

    return table[op]


class SingleCycleDatapath:
    """Educational architectural model of a single-cycle MIPS subset."""

    def __init__(self):
        self.reg = [0] * 32
        self.memory = {}
        self.pc = 0
        self.trace = []

    def load_program(self, program):
        self.program = list(program)
        self.reg = [0] * 32
        self.memory = {}
        self.pc = 0
        self.trace = []

    def step(self):
        if self.pc < 0 or self.pc % 4 != 0:
            raise ValueError(f"Invalid instruction address: {self.pc}")

        index = self.pc // 4
        if index >= len(self.program):
            return False

        old_pc = self.pc
        instruction = self.program[index]
        op, *args = instruction
        signals = decode(op)

        (reg_dst, alu_src, mem_to_reg, reg_write,
         mem_read, mem_write, branch, jump, alu_control) = signals

        next_pc = u32(old_pc + 4)
        rs = rt = rd = 0
        read_a = read_b = alu_b = alu_result = 0
        address = None
        write_reg = None
        write_value = None
        zero = False

        # Register read and ALU input selection
        if op == "ADDI":
            rt, rs, imm = args
            read_a = self.reg[rs]
            alu_b = u32(imm)
            write_reg = rt

        elif op in ("ADD", "SUB", "AND", "OR", "SLT"):
            rd, rs, rt = args
            read_a = self.reg[rs]
            read_b = self.reg[rt]
            alu_b = read_b
            write_reg = rd

        elif op in ("LW", "SW"):
            rt, offset, base = args
            rs = base
            read_a = self.reg[base]
            alu_b = u32(offset)
            address = u32(read_a + alu_b)
            if address % 4 != 0:
                raise ValueError("Unaligned word memory access")
            if op == "LW":
                write_reg = rt

        elif op == "BEQ":
            rs, rt, offset = args
            read_a = self.reg[rs]
            read_b = self.reg[rt]
            alu_b = read_b

        elif op == "J":
            target = args[0]
            if not 0 <= target < (1 << 26):
                raise ValueError("Jump target must be 26-bit")
            next_pc = u32(
                (u32(old_pc + 4) & 0xF0000000) | (target << 2)
            )

        # ALU
        if alu_control == "ADD":
            alu_result = u32(read_a + alu_b)
        elif alu_control == "SUB":
            alu_result = u32(read_a - alu_b)
        elif alu_control == "AND":
            alu_result = read_a & alu_b
        elif alu_control == "OR":
            alu_result = read_a | alu_b
        elif alu_control == "SLT":
            alu_result = int(signed(read_a) < signed(alu_b))

        zero = (u32(read_a) == u32(read_b))

        # Branch target selection
        if branch and zero:
            next_pc = u32(old_pc + 4 + (offset << 2))

        # Data memory
        if mem_read:
            write_value = self.memory.get(address, 0)

        if mem_write:
            self.memory[address] = self.reg[rt]

        # Write-back mux and register-file write
        if reg_write:
            if not mem_to_reg:
                write_value = alu_result

            if write_reg != 0:
                self.reg[write_reg] = u32(write_value)

        self.reg[0] = 0

        self.trace.append({
            "cycle": len(self.trace) + 1,
            "pc": old_pc,
            "instruction": instruction,
            "next_pc": next_pc,
            "control": signals,
            "read_a": read_a,
            "read_b": read_b,
            "alu_b": alu_b,
            "alu_result": alu_result,
            "zero": zero,
            "memory_address": address,
            "write_register": write_reg,
            "write_value": write_value,
        })

        self.pc = next_pc
        return True

    def run(self, max_cycles=1000):
        while self.step():
            if len(self.trace) >= max_cycles:
                raise RuntimeError("Maximum cycle count reached")

        return self.reg, self.memory, self.trace

