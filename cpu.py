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
        self.sp = 7
        self.reg[7] = 0xf4 #will always point to reg 7 at f4
        self.flags = {}
        self.table = {}
        self.table[PRN] = self.prn
        self.table[HLT] = self.hlt
        self.table[LDI] = self.ldi
        self.table[MUL] = self.mul
        self.table[PUSH] = self.push
        self.table[POP] = self.pop
        self.table[CALL] = self.call
        self.table[JMP] = self.jmp
        self.table[RET] = self.ret
        self.table[ADD] = self.add
        self.table[JNE] = self.jne
        self.table[CMP] = self.cmp
        self.table[JEQ] = self.jeq
           

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

    
    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
    
    def prn(self, a=None, b=None):
        print(self.reg[a])
    
    def ldi(self, reg, value):
        self.reg[reg] = value
        
    def hlt(self, a=None, b=None):
        sys.exit(1)
        
    def mul(self, a=None, b=None):
        self.alu("MUL", a, b)
        
    def add(self, a=None, b=None):
        self.alu("ADD", a, b)
        
    def cmp(self, a=None, b=None):
        self.alu("CMP", a, b)
        
    def push(self, a=None, b=None):
        self.reg[sp] -= 1
        self.reg[sp] &= 0xff#keeps r7 in the range 00-ff
        #get register number
        reg_num = self.ram[self.pc+1]
        value = self.reg[reg_num]
        #store in memory
        address_to_push_to = self.reg[sp]
        self.ram[address_to_push_to] = value
        
    def pop(self, b=None):
        #get value from RAM
        address_to_pop_from = self.reg[sp]
        value = self.ram[address_to_pop_from]
        #store in the given registery
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        #increment SP
        self.reg[sp] +=1
        
    def call(self, b=None):
        return_addr = self.pc + 2 #where we RET to
        #push on the stack
        self.reg[sp] -=1
        address_to_push_to = self.reg[sp]
        self.ram[address_to_push_to] = return_addr
        #set the PC to the subroutine address
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]
        self.pc = subroutine_addr
        
    def ret(self):
        #get reutrn address from top of stack
        address_to_pop_from = self.reg[sp]
        return_addr = self.ram[address_to_pop_from]
        self.reg[sp] += 1
        #set pc to return addr
        self.pc = return_addr
                               
        
    def jeq(self, a=None, b=None):
        if self.flags['E'] == 1:
            self.pc = self.reg[a]
        else:
            self.pc += 2
            
    def jne(self, a=None, b=None):
        if self.flags['E'] == 0:
            self.pc = self.reg[a]
        else:
            self.pc +=2
            
    def jmp(self, a=None, b=None):
        self.pc = self.reg[a]
        
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.flags,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

############################       
        
    def run(self):
        """Run the CPU."""
        #a dict for instr that don't increment like the others
        manual = [CALL, JNE, RET, JMP, JEQ]
        count = 1
    
        while True:
            ir = self.ram_read(self.pc) # Instruction Register, contains a copy of the currently executing instruction
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
#             print('---------------------')
#             print(self.pc, ir, self.table.get(ir))
#             self.trace()
#             print('---------------------')
            if ir == HLT:
                self.hlt()
                print("Halted here")
            
            elif ir in manual:#this allows us to move manually set the pc
                self.table[ir](operand_a, operand_b)
            
            elif ir in self.table:
                self.table[ir](operand_a, operand_b)
                self.pc += (ir >> 6) + 1
                
            else:
                print(ir)
                
            count +=1
               