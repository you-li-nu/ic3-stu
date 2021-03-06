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
    #file2 = file0.split('.')[0] + '_' + file1.split('.')[0] + "_syn" + ".bench"
    #file3 = file0.split('.')[0] + '_' + file1.split('.')[0] + "_stu" + ".bench"

    filename0 = file0[file0.index('_') + 1 : file0.rindex('.')]
    filename1 = file1[file1.index('_') + 1 : file1.rindex('.')]
    assert(filename0 == filename1)
    file2 = "syn_" + filename0 + ".bench"
    file3 = "stu_" + filename0 + ".bench"
    print ("file0: " + file0)
    print ("file1: " + file1)
    print ("file2: " + file2)
    print ("file3: " + file3)
    f0 = open(file0, 'r')
    f1 = open(file1, 'r')
    f2 = open(file2, 'w')
    f3 = open(file3, 'w')
    input_list = []# assume inputs are identical to both circuits.
    output0_list = []
    output1_list = []
    
    for line in f0.read().splitlines():
        if line.startswith('#'):
            continue
        if line.startswith('INPUT('):
            input_list.append(line[line.index('(') + 1:line.index(')')])
        if line.startswith('OUTPUT('):
            output0_list.append(line[line.index('(') + 1:line.index(')')])
            continue
        #print (line)
        f2.write(process_line(line, '', input_list))
        f3.write(process_line(line, '', input_list))
    dff_out_list = []# f1
    dff_in_list = []# f1                        
    #print(input_list)
    for line in f1.read().splitlines():
        if line.startswith('#') or line.startswith('INPUT('):#ignore inputs and outputs
            continue
        if line.startswith('OUTPUT('):
            output1_list.append(line[line.index('(') + 1:line.index(')')])
            continue
        f2.write(process_line(line, '', input_list))
        if "DFF" in line and "vdd" not in line and "gnd" not in line:
            process_dff(line, '', dff_out_list, dff_in_list)
            f3.write(process_line(line, '', input_list))
        else:
            continue
    for i in range(len(dff_out_list)):
        newline = dff_in_list[i] + " = BUF(" + dff_out_list[i] + ')' + '\n'
        f3.write(newline)

    output_list = output0_list + output1_list
    add_metering('', '', f2, output_list)
    add_metering('', '', f3, output_list)
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
        
def add_metering(label0, label1, f, output_list):
    # assume 2 * k primary outputs in each copy of the product machine.
    # named 
    assert(len(output_list) % 2 == 0)
    length = len(output_list) // 2
    # switch equiv
    for i in range(length):
        f.write("NEQUIV_" + str(i) + " = " + "XOR(" + label0 + output_list[i] + ", " + label1 + output_list[i + length] + ')' + '\n')
    f.write("NEQUIV" + " = " + "OR(")
    for i in range(length):
        f.write("NEQUIV_" + str(i))
        if i != (length - 1):
            f.write(", ")
        else:
            if length == 1:
                f.write(", gnd")
            f.write(')' + '\n')
    # equiv output
    f.write("OUTPUT(" + "NEQUIV" + ')' + '\n')
    
        
    

    

if __name__ == '__main__':
    main()
