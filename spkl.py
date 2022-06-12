#!/usr/bin/env python3

import sys
import subprocess

iota_counter = 0

def iota(reset = False):
    global iota_counter
    if reset: 
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result

OP_PUSH = iota()
OP_PLUS = iota()
OP_MINUS = iota()
OP_DUMP = iota()
COUNT_OPS = iota()

def push(x):
    return (OP_PUSH, x)

def plus():
    return (OP_PLUS, )
    
def minus():
    return (OP_MINUS, )
    
def dump():
    return (OP_DUMP, )

def simulate_program(program):
    stack = []
    for op in program:
        assert COUNT_OPS == 4, "Exhaustive Handling of operations"
        if op[0] == OP_PUSH:
            stack.append(op[1])
        elif op[0] == OP_PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a+b)
        elif op[0] == OP_MINUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(b-a)
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
            
        else:
            raise NotImplementedError("Unreachable")
    
def compile_program(program,out_path="main"):
    with open(out_path+".asm","w+") as out:
            out.writelines([
                    "segment .text\n",
                    "global _start\n",
                    "_start:\n"])
            out.write("""
dump:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 40
    mov     BYTE [rsp+31], 10
    lea     rcx, [rsp+30]
.L2:
    mov     rax, QWORD rdi
    lea     r8, [rsp+32]
    mul     r9
    mov     rax, rdi
    sub     r8, rcx
    shr     rdx, 3
    lea     rsi, [rdx+rdx*4]
    add     rsi, rsi
    sub     rax, rsi
    add     eax, 48
    mov     BYTE [rcx], al
    mov     rax, rdi
    mov     rdi, rdx
    mov     rdx, rcx
    sub     rcx, 1
    cmp     rax, 9
    ja      .L2
    lea     rax, [rsp+32]
    mov     edi, 1
    sub     rdx, rax
    xor     eax, eax
    lea     rsi, [rsp+32+rdx]
    mov     rdx, r8
    mov rax, 1
    syscall
    add     rsp, 40
    ret
""")    
            for op in program:
                if op[0] == OP_PUSH:
                    out.write("   ;; -- push %d --\n" % op[1])
                    out.write("   push %d\n" % op[1])
                elif op[0] == OP_PLUS:
                    out.write("   ;; -- plus --\n")
                    out.write("   pop rax\n")
                    out.write("   pop rbx\n")
                    out.write("   add rax, rbx\n")
                    out.write("   push rax\n")
                elif op[0] == OP_MINUS:
                    out.write("   ;; -- minus --\n")
                    out.write("   pop rax\n")
                    out.write("   pop rbx\n")
                    out.write("   sub rax, rbx\n")
                    out.write("   push rax\n")
                    
                elif op[0] == OP_DUMP:
                    out.write("   ;; -- dump --\n")
                    out.write("   pop rdi\n")
                    out.write("   call dump\n")
            out.writelines([
                    "   mov rax, 60\n",
                    "   mov rdi, 0\n",
                    "   syscall\n",
                    ])


def parse_word(word):
    assert COUNT_OPS == 4, "Exhaustive OP Handling"
    if word == '+':
        return plus()
    elif word == '-':
        return minus()
    elif word == '.':
        return dump()
    else:
        return push(int(word))

def pythify(path):
    with open(path, "r") as f:
        return [parse_word(word) for word in f.read().split()]

if __name__ == "__main__":
    argv = sys.argv

    if len(argv) < 2:
        print("""
Usage: sparkle [file] [options]...
Options:
  --help                   Display this information.
  --version                Display compiler version information.
  -dumpversion             Display the version of the compiler.
  -std=<standard>          Assume that the input sources are for <standard>.
  --sysroot=<directory>    Use <directory> as the root directory for heade
  -E                       Emulate only; do not compile, assemble or link.
  -c                       Compile and assemble, but do not link.
  -S                       Transpile only, do not assemble or link.
  -o=<file>                Place the output into <file>.
  -R                       Run the File after compilation
        """)
        exit(1)
    simulated = False
    cfile = None
    ppath = "main"
    argv = argv[1:]
    for e in argv:
        if not e.startswith("-"):
            cfile = e
    
    if not cfile:
        print("FATAL: no input file provided. Compilation halted.")
        exit(-1)
    program = pythify(cfile)
    for e in sys.argv:
        if e == "-E":
            simulate_program(program)
            simulated = True
        elif e.startswith("-o"):
            ppath = e.strip("-o=")
        elif e == "-dumpversion":
            print("spkl 1.0.0")
        elif e == "--version":
            print("spkl: Sparkles Compiler 1.0.0")
        


    if not simulated:
        compile_program(program, ppath)
        if not "-S" in sys.argv:
            subprocess.call(["nasm",'-felf64', f'{ppath}.asm'])
        if not "-c" in sys.argv:
            subprocess.call(["ld","-o",ppath, f"{ppath}.o"])

