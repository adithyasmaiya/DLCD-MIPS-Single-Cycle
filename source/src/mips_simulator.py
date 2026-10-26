class SingleCycleMIPS:
    """Educational 32-bit MIPS functional model."""

    MASK = 0xFFFFFFFF

    def __init__(self):
        self.reg = [0] * 32
        self.pc = 0
        self.memory = {}
        self.instructions = []
        self.trace = []

    @staticmethod
    def signed(value):
        value &= 0xFFFFFFFF
        return value - 0x100000000 if value & 0x80000000 else value

    def load_program(self, instructions):
        self.instructions = instructions[:]
        self.reg = [0] * 32
        self.pc = 0
        self.memory = {}
        self.trace = []

    def write_reg(self, index, value):
        if index != 0:
            self.reg[index] = value & self.MASK
        self.reg[0] = 0

    def run(self, max_steps=1000):
        steps = 0

        while 0 <= self.pc // 4 < len(self.instructions):
            if self.pc % 4:
                raise RuntimeError(f"Unaligned PC: {self.pc}")
            if steps >= max_steps:
                raise RuntimeError("Maximum steps reached")

            old_pc = self.pc
            op, *args = self.instructions[old_pc // 4]
            next_pc = (old_pc + 4) & self.MASK
            details = ""

            if op == "ADDI":
                rt, rs, imm = args
                if not -32768 <= imm <= 32767:
                    raise ValueError("ADDI immediate must be signed 16-bit")
                result = self.signed(self.reg[rs]) + imm
                if not -(1 << 31) <= result < (1 << 31):
                    raise OverflowError("ADDI signed overflow")
                self.write_reg(rt, result)
                details = f"R{rt} = R{rs} + {imm}"

            elif op in ("ADD", "SUB"):
                rd, rs, rt = args
                a, b = self.signed(self.reg[rs]), self.signed(self.reg[rt])
                result = a + b if op == "ADD" else a - b
                if not -(1 << 31) <= result < (1 << 31):
                    raise OverflowError(f"{op} signed overflow")
                self.write_reg(rd, result)
                details = f"R{rd} = R{rs} {op} R{rt}"

            elif op in ("AND", "OR"):
                rd, rs, rt = args
                result = (self.reg[rs] & self.reg[rt]
                          if op == "AND"
                          else self.reg[rs] | self.reg[rt])
                self.write_reg(rd, result)
                details = f"R{rd} = R{rs} {op} R{rt}"

            elif op == "SLT":
                rd, rs, rt = args
                result = int(self.signed(self.reg[rs]) <
                             self.signed(self.reg[rt]))
                self.write_reg(rd, result)
                details = f"R{rd} = signed(R{rs}) < signed(R{rt})"

            elif op in ("LW", "SW"):
                rt, offset, base = args
                if not -32768 <= offset <= 32767:
                    raise ValueError(f"{op} offset must be signed 16-bit")
                address = (self.reg[base] + offset) & self.MASK
                if address % 4:
                    raise RuntimeError(f"Unaligned word access: {address}")

                if op == "LW":
                    self.write_reg(rt, self.memory.get(address, 0))
                    details = f"R{rt} = MEM[{address}]"
                else:
                    self.memory[address] = self.reg[rt]
                    details = f"MEM[{address}] = R{rt}"

            elif op == "BEQ":
                rs, rt, offset = args
                if not -32768 <= offset <= 32767:
                    raise ValueError("BEQ offset must be signed 16-bit")
                if self.reg[rs] == self.reg[rt]:
                    next_pc = (old_pc + 4 + (offset << 2)) & self.MASK
                details = f"BEQ R{rs}, R{rt}, offset={offset}"

            elif op == "J":
                target26 = args[0]
                if not 0 <= target26 < (1 << 26):
                    raise ValueError("Jump target must be 26-bit")
                next_pc = ((old_pc + 4) & 0xF0000000) | (target26 << 2)
                details = f"J target26={target26}"

            else:
                raise ValueError(f"Unsupported instruction: {op}")

            self.reg[0] = 0
            self.trace.append({
                "pc": old_pc,
                "instruction": (op, *args),
                "details": details,
                "next_pc": next_pc,
            })
            self.pc = next_pc
            steps += 1

        return self.reg, self.memory, self.trace


if __name__ == "__main__":
    cpu = SingleCycleMIPS()
    cpu.load_program([
        ("ADDI", 8, 0, 10),
        ("ADDI", 9, 0, 20),
        ("ADD", 10, 8, 9),
        ("SUB", 11, 9, 8),
        ("SW", 10, 0, 0),
        ("LW", 12, 0, 0),
        ("BEQ", 10, 12, 1),
        ("ADDI", 13, 0, 999),
        ("J", 9),
    ])

    registers, memory, trace = cpu.run()

    print("MIPS BYTE-ADDRESSED EXECUTION TRACE")
    for item in trace:
        print(
            f"PC={item['pc']:02d} | {item['instruction']} | "
            f"{item['details']} | next PC={item['next_pc']}"
        )

    print("\nFINAL REGISTERS")
    for index in (8, 9, 10, 11, 12, 13):
        print(f"R{index} = {registers[index]}")

    print("\nDATA MEMORY")
    print(memory)

    assert registers[10] == 30
    assert registers[11] == 10
    assert registers[12] == 30
    assert registers[13] == 0
    assert memory[0] == 30
    assert [item["pc"] for item in trace] == [0, 4, 8, 12, 16, 20, 24, 32]

    print("\nALL TESTS PASSED")
