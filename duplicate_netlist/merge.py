#!/usr/bin/python3
import sys
import os
import re



def main():
    program_name = sys.argv[0]
    if (len(sys.argv) != 3):
        print("./duplicate.py syn.bench stu.bench")
        assert(False)
    file0 = sys.argv[1]#syn
    file1 = sys.argv[2]#stu
    filename0 = file0[file0.index('_') + 1 : file0.rindex('.')]
    file2 = "merge_" + filename0 + ".bench"
    print ("file0: " + file0)
    print ("file1: " + file1)
    print ("file2: " + file2)
    f0 = open(file0, 'r')
    f1 = open(file1, 'r')
    f2 = open(file2, 'w')
    input_list = []# assume inputs are identical to both circuits.
    output0_list = []
    output1_list = []
    
    for line in f0.read().splitlines():
        #print (line)
        if line.startswith('#'):
            continue
        if line.startswith('INPUT('):
            input_list.append(line[line.index('(') + 1:line.index(')')])
        if line.startswith('OUTPUT('):
            output0_list.append("syn_" + line[line.index('(') + 1:line.index(')')])
            continue
        f2.write(process_line(line, "syn_", []))   
    for line in f1.read().splitlines():
        #print (line)
        if line.startswith('#') or line.startswith('INPUT('):#ignore inputs and outputs
            continue
        if line.startswith('OUTPUT('):
            output1_list.append("stu_" + line[line.index('(') + 1:line.index(')')])
            continue
        f2.write(process_line(line, "stu_", []))

    output_list = output0_list + output1_list
    assert (len(output_list) == 2)
    f2.write("NEQUIV" + " = " + "AND(" + output_list[0] + ", " + output_list[1] + ")\n")
    f2.write("OUTPUT(" + "NEQUIV" + ')' + '\n')

    f0.close()
    f1.close()
    f2.close()


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
        
    

if __name__ == '__main__':
    main()
