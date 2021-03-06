"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram      = [0] * 256  # Must share space with 1) stack (holds the register's addresses), 2) reserved memory spaces, and 3) instructions to be loaded
                                   # Stack is part of the memory,   
                                   # RAM: starts from zero, so technically 255, pre-allocating memory 2 ** 8bit = 256 
        self.reg      = [0] * 8  # 8 general-purpose 8-bit numeric registers R0-R7. Piece of memory. Stores the value 
        self.IR       = [0] * 1
        self.PC       = 0  # Program Counter, 
        self.MAR      = [0] * 1 # Addr, these are temp variables to reduce number of index operations
        self.MDR      = [0] * 1 # Data, these are temp variables to reduce number of index operations
        self.FL       = [0] * 8
        
        # R7 is reserved as the stack pointer (SP)
        self.reg[7]= 0xF4
        self.SP  = self.reg[7]
        self.L   = self.FL[5]
        self.G   = self.FL[6]
        self.E   = self.FL[7]
        
        
        global HLT,PRN,LDI,MUL,PUSH,POP,CALL,RET,ADD,JMP,CMP,JEQ,JNE
        HLT  = 0b00000001
        LDI  = 0b10000010
        PRN  = 0b01000111
        MUL  = 0b10100010
        PUSH = 0b01000101
        POP  = 0b01000110
        CALL = 0b01010000
        RET  = 0b00010001
        ADD  = 0b10100000
        JMP  = 0b01010100
        CMP  = 0b10100111
        JEQ  = 0b01010101
        JNE  = 0b01010110


        
        # # Set up the branch table
        # self.branchtable = {}
        # self.branchtable[LDI] = self.handle_LDI
        # self.branchtable[PRN] = self.handle_PRN
        # self.branchtable[MUL] = self.handle_MUL
        # self.branchtable[HLT] = self.handle_HLT
        

    def load(self,program_filename):
        """Load a program into memory."""
        # Load program into memory
        address = 0 
        with open(program_filename) as f:
            for line in f:
                line = line.split("#")
                line = line[0].strip()
                if line == '':
                    continue
                self.ram[address] = int(line,2)
                address += 1

    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB": 
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            self.L = self.G = self.E = 0
            if self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.G = 1 
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1  
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self):
        """
        Accept the address to read and return the value stored there.
        """
        self.MDR = self.reg[self.MAR]
        return 
    
    def ram_write(self):
        """ 
        Accept a value to write, and the address to write it to.
        """
        self.reg[self.MAR] = self.MDR
        
    def get_inst_count(self):
            inst_len = ((self.ram[self.PC] & self.IR) >> 6) + 1   # 3
            return inst_len
        
        
    def run(self):
        """Run the CPU."""
        
        running = True
        
        while running:
            self.IR = self.ram[self.PC]
            # print(self.IR)
#         print(bin(self.IR))
#         self.branchtable[bin(self.IR)]()
            inst_count = self.get_inst_count()
            # self.trace()
            
            if self.IR == LDI: # Save the register
                self.MAR = self.ram[self.PC + 1]
                self.MDR = self.ram[self.PC + 2]
                self.ram_write()
                self.PC += inst_count

            elif self.IR == PRN: # Print Register 0
                self.MAR = self.ram[self.PC + 1]
                
                self.ram_read()
                print(self.MDR)
                self.PC += inst_count
                
            elif self.IR == MUL: 
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                op = "MUL"
                self.alu(op, reg_a,reg_b)
                self.PC += inst_count

            elif self.IR == ADD: # Print Register 0
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                op = "ADD"
                self.alu(op, reg_a,reg_b)
                self.PC += inst_count    

            elif self.IR == CMP: 
                reg_a = self.ram[self.PC + 1]
                reg_b = self.ram[self.PC + 2]
                # print(reg_a,reg_b)
                op = "CMP"
                self.alu(op, reg_a,reg_b)
                self.PC += inst_count

            
            elif self.IR == PUSH:
                # decrement the stack pointer
                self.SP -= 1
                
                # copy value from register into ram
                self.MAR = self.ram[self.PC + 1]
                self.MDR = self.reg[self.MAR] # this is what we want to push
                
                self.ram[self.SP] = self.MDR # store the value on the stack
                
                
                self.PC += inst_count
                
            elif self.IR == POP:
                # Copy the value from the address pointed to by SP to the given register.
                self.MDR = self.ram[self.SP] # value pointed by SP
                self.MAR = self.ram[self.PC + 1] # address of the register - MAR is address
                
                self.reg[self.MAR] = self.MDR # copy value to the register
                
                # Increment SP vs lookup the address of the RAM 
                self.SP += 1
                self.PC += inst_count

            elif self.IR == HLT: # Halt command
                running = False

            elif self.IR == CALL:

                # compute return address
                self.MAR = self.PC + 2

                #push on the stack
                self.SP -= 1 # decrement the stack pointer
                self.ram[self.SP] = self.MAR

                # Set the PC to the value in the given register
                
                self.MAR = self.ram[self.PC + 1]
                self.PC = self.reg[self.MAR] # The PC is set to the address stored in the given register.

            elif self.IR == RET:

                # pop return address from top of stack
                self.MAR = self.ram[self.SP]

                # print("top of stack address:",self.MAR)
                self.SP += 1

                # set the pc
                self.PC = self.MAR


            elif self.IR == JMP:
                self.MAR = self.ram[self.PC + 1] 
                self.PC = self.reg[self.MAR]


            elif self.IR == JEQ:
                if self.E == 1:
                    self.MAR = self.ram[self.PC + 1] 
                    self.PC = self.reg[self.MAR]
                else:
                    self.PC += inst_count


            elif self.IR == JNE:
                if self.E == 0:
                    self.MAR = self.ram[self.PC + 1] 
                    self.PC = self.reg[self.MAR]
                else:
                    self.PC += inst_count


            else:
                print("Unknown instruction ",self.IR)
                running = False



if __name__ == "__main__":
    cpu = CPU()
    cpu.load("sctest.ls8")
    # print(cpu.ram[12])
    cpu.run()
    # cpu.trace()
    # print("---------")
    # print(cpu.IR)
    # print(cpu.PC)
    # print(cpu.IR)
    # print(cpu.FL)
    # print(cpu.MAR)
    # print(cpu.MDR)
    # print(cpu.ram)