#!/usr/bin/python3
import sys
import os
import re



def main():
    program_name = sys.argv[0]
    if (len(sys.argv) != 3):
        print("./duplicate.py slow.bench fast.bench")
        assert(False)
    file0 = sys.argv[1]#slow
    file1 = sys.argv[2]#fast
    file2 = file0.split('.')[0] + '_' + file1.split('.')[0] + "_syn" + ".bench"
    file3 = file0.split('.')[0] + '_' + file1.split('.')[0] + "_stu" + ".bench"
    print ("file0: " + file0)
    print ("file1: " + file1)
    print ("file2: " + file2)
    print ("file3: " + file3)
    f0 = open(file0, 'r')
    f1 = open(file1, 'r')
    f2 = open(file2, 'w')
    f3 = open(file3, 'w')
    input_list = []
    
    for line in f0.read().splitlines():
        if line.startswith('#') or line.startswith('OUTPUT('):#ignore outputs
            continue
        if line.startswith('INPUT('):
            input_list.append(line[line.index('(') + 1:line.index(')')])
        #print (line)
        f2.write(process_line(line, "slow_", input_list))
        f3.write(process_line(line, "slow_", input_list))
    dff_out_list = []
    dff_in_list = []
    #print(input_list)
    for line in f1.read().splitlines():
        if line.startswith('#') or line.startswith('OUTPUT(') or line.startswith('INPUT('):#ignore inputs and outputs
            continue
        f2.write(process_line(line, "fast_", input_list))
        if "DFF" in line and "vdd" not in line and "gnd" not in line:
            process_dff(line, "fast_", dff_out_list, dff_in_list)
            f3.write(process_line(line, "fast_", input_list))
        else:
            continue
    for i in range(len(dff_out_list)):
        newline = "fast_" + dff_in_list[i] + " = BUF(" + "fast_" + dff_out_list[i] + ')' + '\n'
        f3.write(newline)
    add_metering("slow_", "fast_", f2, dff_out_list, dff_in_list)
    add_metering("slow_", "fast_", f3, dff_out_list, dff_in_list)
    f0.close()
    f1.close()
    f2.close()
    f3.close()
    print(dff_in_list)
    print(dff_out_list)

def process_dff(line, label, dff_out_list, dff_in_list):
    assert("DFF" in line)
    seg0 = line[:line.index('=')]
    seg0 = seg0.strip()
    seg2 = line[line.index('(') + 1:]
    seg2 = seg2.strip()
    seg2 = seg2.strip(')')
    dff_out_list.append(seg0)
    dff_in_list.append(seg2)
    
    
def process_line(line, label, input_list):
    # add label to each wire except primary inputs, gnd, and vdd
    if '=' in line:
        seg0 = line[:line.index('=')]
        seg0 = add_label(seg0, label, input_list)
        if '(' in line:
            seg1 = line[line.index('='):line.index('(') + 1]
        else:
            seg1 = line[line.index('='):]
        newline = seg0 + seg1
    else:
        newline = line[:line.index('(') + 1]
    if '(' not in line:
        return newline + '\n'
    seg2 = line[line.index('(') + 1:]
    seg2_list = seg2.split()
    for i in range(len(seg2_list)):
        #print(seg2_list[i])
        if seg2_list[i].startswith("vdd") or seg2_list[i].startswith("gnd"):
            continue
        seg2_list[i] = add_label(seg2_list[i], label, input_list)
        
    newline = newline + ' '.join(seg2_list)
    #print(newline)
    return newline + '\n'
    
def add_label(seg, label, input_list):
    # add label to each wire except primary inputs, gnd, and vdd
    tmp_seg = seg
    if (tmp_seg.strip(')')) in input_list or (tmp_seg.strip(',')) in input_list:
        return seg
    else:
        return label + seg
        
def add_metering(label0, label1, f, dff_out_list, dff_in_list):
    # assume 2 * k primary inputs in each copy of the product machine.
    # named 
    assert(len(dff_out_list) % 2 == 0)
    length = len(dff_out_list) // 2
    # equiv
    for i in range(length + length):
        f.write("EQUIV_0_" + str(i) + " = " + "NXOR(" + label0 + dff_out_list[i] + ", " + label1 + dff_out_list[i] + ')' + '\n')
    f.write("EQUIV_0" + " = " + "AND(")
    for i in range(length + length):
        f.write("EQUIV_0_" + str(i))
        if i != (length + length - 1):
            f.write(", ")
        else:
            f.write(')' + '\n')
    # switch equiv
    for i in range(length + length):
        if i < length:
            f.write("EQUIV_1_" + str(i) + " = " + "NXOR(" + label0 + dff_out_list[i] + ", " + label1 + dff_out_list[i + length] + ')' + '\n')
        else:
            f.write("EQUIV_1_" + str(i) + " = " + "NXOR(" + label0 + dff_out_list[i] + ", " + label1 + dff_out_list[i - length] + ')' + '\n')
    f.write("EQUIV_1" + " = " + "AND(")
    for i in range(length + length):
        f.write("EQUIV_1_" + str(i))
        if i != (length + length - 1):
            f.write(", ")
        else:
            f.write(')' + '\n')
    # equiv output
    f.write("EQUIV" + " = " + "OR(" + "EQUIV_0" + ", " + "EQUIV_1" + ')' + '\n')
    f.write("OUTPUT(" + "EQUIV" + ')' + '\n')
    
        
    

    

if __name__ == '__main__':
    main()
