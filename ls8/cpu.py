"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.program_counter = 0
        self.ram = [0] * 256
        self.equal_to = 0
        self.less_than = 0
        self.greater_than = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        # print('SYS',sys.argv[0])
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        progname = sys.argv[1]

        with open(progname) as file:
            for line in file:
                line = line.split("#")[0] #splits and removes #, then reads first thing in line [0]
                line = line.strip()  # lose whitespace

                if line == '':
                    continue

                val = int(line, 2) # LS-8 uses base 2!
                #print(val)

                self.ram[address] = val
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "CMP":
            if self.register[reg_a] == self.register[reg_b]:
                self.equal_to = 1
                self.less_than = 0
                self.greater_than = 0
            elif self.register[reg_a] > self.register[reg_b]:
                self.equal_to = 0
                self.less_than = 0
                self.greater_than = 1
            elif self.register[reg_a] < self.register[reg_b]:
                self.equal_to = 0
                self.less_than = 1
                self.greater_than = 0
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.program_counter,
            #self.fl,
            #self.ie,
            self.ram_read(self.program_counter),
            self.ram_read(self.program_counter + 1),
            self.ram_read(self.program_counter + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        stack_pointer = 7
        halted = False

        while not halted:
            instructions = self.ram[self.program_counter]

            if instructions == LDI:#LDI = load into register
                reg_slot = self.ram[self.program_counter + 1]
                value = self.ram[self.program_counter + 2]

                self.register[reg_slot] = value

                self.program_counter += 3

            elif instructions == PRN:#PRN = print register
                reg_slot = self.ram[self.program_counter + 1]
                print(self.register[reg_slot])

                self.program_counter +=2

            elif instructions == ADD:
                self.alu("ADD", self.ram[self.program_counter + 1], self.ram[self.program_counter + 2])
                self.program_counter += 3

            elif instructions == MUL:#MUL = multiply
                self.alu("MUL", self.ram[self.program_counter + 1], self.ram[self.program_counter + 2])
                self.program_counter += 3

            elif instructions == PUSH:
                self.register[stack_pointer] -= 1
                reg_slot = self.ram[self.program_counter + 1]
                reg_value = self.register[reg_slot]
                self.ram[self.register[stack_pointer]] = reg_value
                # print('reg',self.register[stack_pointer])
                # print('ram',self.ram[self.register[stack_pointer]])
                self.program_counter += 2
                # self.trace()

            elif instructions == POP:
                reg_value = self.ram[self.register[stack_pointer]]
                reg_slot = self.ram[self.program_counter + 1]
                self.register[reg_slot] = reg_value

                self.register[stack_pointer] += 1

                self.program_counter +=2
                # self.trace()

            elif instructions == CALL:
                #push return address onto stack
                return_address = self.program_counter + 2
                self.register[stack_pointer] -= 1
                self.ram[self.register[stack_pointer]] = return_address

                #set the pc to the value in the register
                reg_slot = self.ram[self.program_counter + 1]
                self.program_counter = self.register[reg_slot]

            elif instructions == RET:
                # pop the return address off stack
		        # store it in the pc
                self.program_counter = self.ram[self.register[stack_pointer]]
                self.register[stack_pointer] += 1

            elif instructions == CMP:
                reg_slot = self.ram[self.program_counter + 1]
                reg_value = self.ram[self.program_counter + 2]

                self.alu('CMP', reg_slot, reg_value)
                self.program_counter += 3

            elif instructions == JMP:
                reg_slot = self.ram[self.program_counter + 1]
                reg_value = self.ram[self.program_counter + 2]
                
                self.program_counter = self.register[reg_slot]          

            elif instructions == JEQ:
                reg_slot = self.ram[self.program_counter + 1]
                reg_value = self.ram[self.program_counter + 2]

                if self.equal_to == 1:
                    self.program_counter = self.register[reg_slot]
                else:
                    self.program_counter += 2

            elif instructions == JNE:
                reg_slot = self.ram[self.program_counter + 1]
                reg_value = self.ram[self.program_counter + 2]

                if self.equal_to == 0:
                    self.program_counter = self.register[reg_slot]
                else:
                    self.program_counter += 2

            elif instructions == HLT:#HLT = halt
                halted = True
                self.program_counter += 1

            else:
                print(f"Unknown instruction at program_counter index {self.program_counter}")
                sys.exit(1)