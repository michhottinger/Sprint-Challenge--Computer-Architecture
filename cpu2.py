import sys


"""CPU functionality."""

## ALU ops
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
MOD = 0b10100100
INC = 0b01100101
DEC = 0b01100110
CMP = 0b10100111
AND = 0b10101000
NOT = 0b01101001
OR  = 0b10101010
XOR = 0b10101011
SHL = 0b10101100
SHR = 0b10101101

## PC mutators
CALL = 0b01010000
RET  = 0b00010001
INT  = 0b01010010
IRET = 0b00010011
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
JGT  = 0b01010111
JLT  = 0b01011000
JLE  = 0b01011001
JGE  = 0b01011010

## Other
NOP  = 0b00000000
HLT  = 0b00000001
LDI  = 0b10000010
LD   = 0b10000011
ST   = 0b10000100
PUSH = 0b01000101
POP  = 0b01000110
PRN  = 0b01000111
PRA  = 0b01001000



class CPU:
    """Main CPU class."""

    def __init__(self):
       
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc =0
        self.flags = {}
        self.branch_table = {
            0b01000111 : "PRN",
            0b00000001 : "HLT",
            0b10000010 : "LDI",
            0b10100010 : "MUL",
            0b01000101 : "PUSH",
            0b01000110 : "POP",
            0b01010000 : "CALL",
            0b01010100 : "JMP",
            0b00010001 : "RET",
            0b10100000 : "ADD",
            0b01010110 : "JNE",
            0b10100111 : "CMP",
            0b01010101 : "JEQ"
        }
        

    def load(self):
        """Load a program into memory."""

        address = 0

        program = []
        with open (sys.argv[1]) as f:
            for line in f:
                try: 
                    line = line.split("#", 1)[0]
                    line = int(line, 2)
                    program.append(line)
                except ValueError:
                    pass
                
                
        for instruction in program:
            self.ram[address] = instruction
            address += 1

            #Memory Address Register_ (MAR) and the _Memory Data Register_ (MDR)
    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
    
    def PRN(self, reg):
        print(self.reg[reg])
    
    def LDI(self, reg, value):
        self.reg[reg] = value
        
    def HLT(self):
        return False
        
#     def JEQ(self, reg):
#         if self.flags['E'] == 1:
#             self.pc == self.reg[reg]
#         else:
#             self.pc += 2
            
#     def JNE(self, reg):
#         if self.flags['E'] == 0:
#             self.pc == self.reg[reg]
#         else:
#             self.pc +=2
            
#     def JMP(self, reg):
#         self.pc = self.reg[reg]
        
    
    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""
        a = self.reg[reg_a]
        b = self.reg[reg_b]

        if op == "ADD":
            a += b
        
        elif op == "MUL":
            a *= b
            
        elif op == "CMP":
            
            if a == b:
                self.flags['E'] = 1
            else:
                self.flags['E'] = 0
            
            if a < b:
                self.flags['L'] = 1
            else:
                self.flags['L'] = 0
            
            if a > b:
                self.flags['G'] = 1
            else:
                self.flags['G'] = 0
            
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.flags,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        sp = 7#stack pointer
        self.reg[sp] = 0xf4 #start one above f3 then decrement
        running = True
        count = 1
    
   
        
        while running:
            ir = self.ram_read(self.pc) # Instruction Register, contains a copy of the currently executing instruction
#             print('---------------------')
#             print(self.pc, ir, self.branch_table.get(ir))
#             self.trace()
#             print('---------------------')
            if ir in self.branch_table:
                self.branch_table[ir]
            
            if ir in self.branch_table and self.branch_table[ir] == "HLT":
                running = self.HLT()
                print("halted here")
               
          
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            if ir in self.branch_table and not self.branch_table[ir] == "HLT":
                
                if self.branch_table[ir] == "LDI":
                    self.LDI(operand_a, operand_b)
                    self.pc += 3
                
                elif self.branch_table[ir] == "PRN":
                    self.PRN(operand_a)
                    self.pc += 2
                
                elif self.branch_table[ir] == "PUSH":
                    #decrement stack pointer
                    self.reg[sp] -= 1
    
                    self.reg[sp] &= 0xff#keeps r7 in the range 00-ff
    
                    #get register number
                    reg_num = self.ram[self.pc+1]
                    value = self.reg[reg_num]
    
                    #store in memory
                    address_to_push_to = self.reg[sp]
                    self.ram[address_to_push_to] = value
                    if (ir & (1<< 7)) >> 7 ==1:
                        self.pc += 3
                    else:
                        self.pc += 2
     
                elif self.branch_table[ir] == "POP":
                    #get value from RAM
                    address_to_pop_from = self.reg[sp]
                    value = self.ram[address_to_pop_from]
        
                    #store in the given registery
                    reg_num = self.ram[self.pc + 1]
                    self.reg[reg_num] = value
        
                    #increment SP
                    self.reg[sp] +=1
                    #print(self.reg[sp])
                    if (ir & (1<< 7)) >> 7 ==1:
                        self.pc += 3
                    else:
                        self.pc += 2
                
                elif self.branch_table[ir] == "CALL":
                    return_addr = self.pc + 2 #where we RET to
                    
                    #push on the stack
                    self.reg[sp] -=1
                    address_to_push_to = self.reg[sp]
                    self.ram[address_to_push_to] = return_addr
                    
                    #set the PC to the subroutine address
                    reg_num = self.ram[self.pc + 1]
                    subroutine_addr = self.reg[reg_num]
                   
                    self.pc = subroutine_addr
                    
                    #print(self.pc) #THIS is getting stopped at 24, HLT
                    
                elif self.branch_table[ir] == "RET":
                     #get reutrn address from top of stack
                    address_to_pop_from = self.reg[sp]
                    return_addr = self.ram[address_to_pop_from]
                    self.reg[sp] += 1

                    #set pc to return addr
                    self.pc = return_addr
                               
                elif self.branch_table[ir] == "JNE":
#                     print("here")
                    if self.flags['E'] == 0:
                        self.pc = self.reg[operand_a]
                    else:
                        self.pc +=2
                
                elif self.branch_table[ir] == "JMP":
                    self.pc = self.reg[operand_a]
                
                elif self.branch_table[ir] == "JEQ":
                    if self.flags['E'] == 1:
                        self.pc = self.reg[operand_a]
                    else:
                        self.pc += 2
                    
                else: 
                    op = self.branch_table[ir]
                    self.alu(op, operand_a, operand_b)
                    
                    if (ir & (1<< 7)) >> 7 ==1:
                        self.pc += 3
                    else:
                        self.pc += 2
                
            count +=1
               