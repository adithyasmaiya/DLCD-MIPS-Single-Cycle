MASK = 0xFFFFFFFF


def u32(value):
    return value & MASK


def signed(value):
    value = u32(value)
    return value - 0x100000000 if value & 0x80000000 else value


def validate_imm16(value):
    if not -32768 <= value <= 32767:
        raise ValueError(
            f"Immediate value out of signed 16-bit range: {value}"
        )
    return value


def sign_extend16(value):
    value &= 0xFFFF

    if value & 0x8000:
        return value | 0xFFFF0000

    return value


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
        self.program_base = 0
        self.trace = []
        self.program = []

    def load_program(self, program, start_address=0):
        if not isinstance(start_address, int):
            raise ValueError("Start address must be an integer")

        if not 0 <= start_address <= MASK or start_address % 4 != 0:
            raise ValueError("Start address must be an aligned 32-bit address")

        self.program = list(program)
        self.reg = [0] * 32
        self.memory = {}
        self.program_base = start_address
        self.pc = start_address
        self.trace = []

    def step(self):
        if self.pc < 0 or self.pc % 4 != 0:
            raise ValueError(f"Invalid instruction address: {self.pc}")

        if self.pc < self.program_base:
            return False

        index = (self.pc - self.program_base) // 4

        if index >= len(self.program):
            return False

        old_pc = self.pc
        instruction = self.program[index]
        op, *args = instruction
        signals = decode(op)

        (
            reg_dst, alu_src, mem_to_reg, reg_write,
            mem_read, mem_write, branch, jump, alu_control
        ) = signals

        pc_plus4 = u32(old_pc + 4)
        next_pc = pc_plus4
        pc_source = "SEQUENTIAL"

        rs = rt = rd = 0
        read_a = read_b = alu_b = alu_result = 0

        address = None
        write_reg = None
        write_value = None
        sign_extended_imm = None

        shifted_branch_offset = None
        branch_target = None
        branch_taken = False

        jump_target_26 = None
        shifted_jump_target = None
        pc_upper_4 = None
        jump_address = None

        # Register-file read addresses and data
        read_register1 = None
        read_register2 = None
        read_data1 = 0
        read_data2 = 0

        # Register-file write-back signals
        destination_register = None
        register_write_enable = bool(reg_write)
        register_write_data = None
        writeback_source = None

        # Explicit MUX information

        # RegDst MUX
        regdst_input0 = None
        regdst_input1 = None
        regdst_selected = None

        # ALUSrc MUX
        alusrc_input0 = None
        alusrc_input1 = None
        alusrc_selected = None

        # MemToReg MUX
        memtoreg_input0 = None
        memtoreg_input1 = None
        memtoreg_selected = None

        # Next-PC MUX
        pc_mux_input0 = pc_plus4
        pc_mux_input1 = None
        pc_mux_input2 = None
        pc_mux_selected = "SEQUENTIAL"

        memory_read_data = None

        # Instruction decoding and register reads
        if op == "ADDI":
            rt, rs, imm = args
            imm = validate_imm16(imm)

            read_register1 = rs
            read_register2 = rt

            read_data1 = self.reg[rs]
            read_data2 = self.reg[rt]

            sign_extended_imm = sign_extend16(imm)

            read_a = read_data1
            read_b = read_data2
            alu_b = sign_extended_imm

            write_reg = rt

        elif op in ("ADD", "SUB", "AND", "OR", "SLT"):
            rd, rs, rt = args

            read_register1 = rs
            read_register2 = rt

            read_data1 = self.reg[rs]
            read_data2 = self.reg[rt]

            read_a = read_data1
            read_b = read_data2
            alu_b = read_b

            write_reg = rd

        elif op in ("LW", "SW"):
            rt, offset, base = args
            offset = validate_imm16(offset)

            read_register1 = base
            read_register2 = rt

            read_data1 = self.reg[base]
            read_data2 = self.reg[rt]

            sign_extended_imm = sign_extend16(offset)

            rs = base
            read_a = read_data1
            read_b = read_data2
            alu_b = sign_extended_imm

            address = u32(read_a + alu_b)

            if address % 4 != 0:
                raise ValueError("Unaligned word memory access")

            if op == "LW":
                write_reg = rt

        elif op == "BEQ":
            rs, rt, offset = args
            offset = validate_imm16(offset)

            read_register1 = rs
            read_register2 = rt

            read_data1 = self.reg[rs]
            read_data2 = self.reg[rt]

            sign_extended_imm = sign_extend16(offset)

            read_a = read_data1
            read_b = read_data2
            alu_b = read_b

            shifted_branch_offset = u32(sign_extended_imm << 2)
            branch_target = u32(pc_plus4 + shifted_branch_offset)

        elif op == "J":
            target = args[0]

            if not isinstance(target, int) or not 0 <= target < (1 << 26):
                raise ValueError("Jump target must be a 26-bit integer")

            jump_target_26 = target
            shifted_jump_target = u32(target << 2)
            pc_upper_4 = pc_plus4 & 0xF0000000

            jump_address = u32(
                pc_upper_4 | shifted_jump_target
            )

        # ALUSrc MUX
        alusrc_input0 = read_data2
        alusrc_input1 = sign_extended_imm

        if alu_src == 0:
            alusrc_selected = "REGISTER"
        elif alu_src == 1:
            alusrc_selected = "IMMEDIATE"

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

        zero = (alu_result == 0)

        # Branch decision
        branch_taken = bool(branch and zero)

        if branch_taken:
            next_pc = branch_target
            pc_source = "BRANCH"

        # Jump selection
        if jump:
            next_pc = jump_address
            pc_source = "JUMP"

        # Next-PC MUX
        pc_mux_input1 = branch_target
        pc_mux_input2 = jump_address
        pc_mux_selected = pc_source

        # Data memory
        if mem_read:
            memory_read_data = self.memory.get(address, 0)
            write_value = memory_read_data
            writeback_source = "DATA_MEMORY"

        if mem_write:
            self.memory[address] = read_data2

        # RegDst MUX inputs
        regdst_input0 = rt
        regdst_input1 = rd

        if reg_dst == 0:
            regdst_selected = "RT"
        elif reg_dst == 1:
            regdst_selected = "RD"

        # MemToReg MUX inputs
        memtoreg_input0 = alu_result
        memtoreg_input1 = memory_read_data

        if mem_to_reg == 0:
            memtoreg_selected = "ALU"
        elif mem_to_reg == 1:
            memtoreg_selected = "MEMORY"

        # Destination register selection
        if reg_dst == 1:
            destination_register = rd
        elif reg_dst == 0:
            destination_register = rt

        # Write-back selection
        if reg_write:
            if mem_to_reg:
                write_value = memory_read_data
                writeback_source = "DATA_MEMORY"
            else:
                write_value = alu_result
                writeback_source = "ALU"

            register_write_data = u32(write_value)

            if destination_register != 0:
                self.reg[destination_register] = register_write_data

        self.reg[0] = 0

        # Execution trace
        self.trace.append({
            "cycle": len(self.trace) + 1,
            "pc": old_pc,
            "pc_plus4": pc_plus4,
            "instruction": instruction,
            "next_pc": next_pc,
            "pc_source": pc_source,
            "control": signals,

            "read_register1": read_register1,
            "read_register2": read_register2,
            "read_data1": read_data1,
            "read_data2": read_data2,

            "sign_extended_imm": sign_extended_imm,
            "alu_b": alu_b,
            "alu_result": alu_result,
            "zero": zero,

            "shifted_branch_offset": shifted_branch_offset,
            "branch_target": branch_target,
            "branch_taken": branch_taken,

            "jump_target_26": jump_target_26,
            "shifted_jump_target": shifted_jump_target,
            "pc_upper_4": pc_upper_4,
            "jump_address": jump_address,

            "memory_address": address,
            "memory_read_data": memory_read_data,

            "destination_register": destination_register,
            "register_write_enable": register_write_enable,
            "register_write_data": register_write_data,
            "writeback_source": writeback_source,

            "write_register": write_reg,
            "write_value": write_value,

            # Explicit MUX information
            "regdst_input0": regdst_input0,
            "regdst_input1": regdst_input1,
            "regdst_selected": regdst_selected,

            "alusrc_input0": alusrc_input0,
            "alusrc_input1": alusrc_input1,
            "alusrc_selected": alusrc_selected,

            "memtoreg_input0": memtoreg_input0,
            "memtoreg_input1": memtoreg_input1,
            "memtoreg_selected": memtoreg_selected,

            "pc_mux_input0": pc_mux_input0,
            "pc_mux_input1": pc_mux_input1,
            "pc_mux_input2": pc_mux_input2,
            "pc_mux_selected": pc_mux_selected,
        })

        self.pc = next_pc
        return True

    def run(self, max_cycles=1000):
        while self.step():
            if len(self.trace) >= max_cycles:
                raise RuntimeError("Maximum cycle count reached")

        return self.reg, self.memory, self.trace