#!/usr/bin/python3
import sys
import os
import re



def main():
    program_name = sys.argv[0]
    if (len(sys.argv) != 2):
        print("./stutter.py fast.bench")
        assert(False)
    file0 = sys.argv[1]#origin, fast
    file1 = "fast" + '_' + file0[: file0.rindex('.')] + ".bench"#renamed, fast
    file2 = "slow" + '_' + file0[: file0.rindex('.')] + ".bench"#renamed, slow
    print ("file0: " + file0)
    print ("file1: " + file1)
    print ("file2: " + file2)
    f0 = open(file0, 'r')
    f1 = open(file1, 'w')
    f2 = open(file2, 'w')
    input_list = []
    dff_out_list = []
    dff_in_list = []
    
    for line in f0.read().splitlines():
        if line.startswith('#') or line.startswith('OUTPUT('):#ignore outputs
            continue
        if line.startswith('INPUT('):
            input_list.append(line[line.index('(') + 1:line.index(')')])
        if "DFF" in line and "vdd" not in line and "gnd" not in line:
            process_dff(line, "fast_", dff_out_list, dff_in_list)
        #print (line)
    f0.seek(0)
    #print(dff_out_list)

    
    #print(input_list)
    for line in f0.read().splitlines():
        if line.startswith('#'):
            f1.write(line + '\n')
        elif line.startswith('OUTPUT(') or line.startswith('INPUT('):
            f1.write(process_line(line, "fast_", input_list))
        else:
            f1.write(process_line(line, "fast_", input_list))
    f0.seek(0)

    for line in f0.read().splitlines():
        if line.startswith('#'):
            f2.write(line + '\n')
        elif line.startswith('OUTPUT(') or line.startswith('INPUT('):
            f2.write(process_line(line, "slow_", input_list))
        else:
            if "DFF" in line and "vdd" not in line and "gnd" not in line:
                f2.write(process_line(process_line(line, "AUX_", dff_out_list), "slow_", input_list))#add slow_AUX to dff inputs. Add slow_ to dff outputs.
            if "DFF" not in line:
                f2.write(process_line(line, "slow_", input_list))

    add_flip(f2, 4, "slow_", dff_in_list, dff_out_list)

    f0.close()
    f1.close()
    f2.close()

def process_dff(line, label, dff_out_list, dff_in_list):
    assert("DFF" in line)
    seg0 = line[:line.index('=')]
    seg0 = seg0.strip()
    seg2 = line[line.index('(') + 1:]
    seg2 = seg2.strip()
    seg2 = seg2.strip(')')
    dff_out_list.append(seg0)
    dff_in_list.append(seg2)

def add_flip(file, num, label, dff_in_list, dff_out_list):
    rflip_out_list = []
    rflip_in_list = []
    for i in range(num):
        rflip_out_list.append(label + "RFLIP" + '_' + "OUT" + '_' + str(i))
        rflip_in_list.append(label + "RFLIP" + '_' + "IN" + '_' + str(i))

    file.write("# flip register\n")
    for i in range(num):
        line = rflip_out_list[i] + " = " + "DFF(" + rflip_in_list[i] + ")\n"
        file.write(line)

    file.write("# init 0\n")
    line = label + "INIT_0" + " = " + "NOR("
    for i in range(num):
        line = line + rflip_out_list[i]
        if i != num - 1:
            line = line + ", "
    line = line + ")\n"
    file.write(line)
    file.write("# wire flip register\n")
    line = rflip_in_list[0] + " = " + "OR(" + rflip_out_list[num - 1] + ", " + label + "INIT_0" + ")\n"
    file.write(line)
    # a flop will flip if: 1. itself would flip, and 2. the msb of the shifter is 1
    for i in range(1, num):
        line = rflip_in_list[i] + " = " + "BUF(" + rflip_out_list[i - 1] + ")\n"
        file.write(line)
    for i in range(len(dff_out_list)):
        line = label + "DIFF_" + str(i) + " = " + "XOR(" + label + dff_out_list[i] + ", " + label + dff_in_list[i] + ")\n"
        file.write(line)
    for i in range(len(dff_out_list)):
        line = label + "FLIP_" + str(i) + " = " + "AND(" + label + "DIFF_" + str(i) + ", " + rflip_out_list[num - 1] + ")\n"
        file.write(line)
    for i in range(len(dff_out_list)):
        line = label + "AUX_" + dff_in_list[i] + " = " + "XOR(" + label + dff_out_list[i] + ", " + label + "FLIP_" + str(i) + ")\n"
        file.write(line)
       

    
    
def process_line(line, label, except_list):
    # add label to each wire except primary inputs, gnd, and vdd
    if '=' in line:
        seg0 = line[:line.index('=')]
        seg0 = add_label(seg0, label, except_list)
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
        seg2_list[i] = add_label(seg2_list[i], label, except_list)
        
    newline = newline + ' '.join(seg2_list)
    #print(newline)
    return newline + '\n'
    
def add_label(seg, label, except_list):
    # add label to each wire except primary inputs, gnd, and vdd
    tmp_seg = seg.strip()
    if (tmp_seg.strip(')')) in except_list or (tmp_seg.strip(',')) in except_list:
        return seg
    else:
        return label + seg
    

if __name__ == '__main__':
    main()
