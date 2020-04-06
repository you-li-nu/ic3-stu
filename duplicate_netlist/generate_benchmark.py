#!/usr/bin/python3
import sys
import os
import re

# a counterexample is found when a primary output is asserted to 1.

def main():
    program_name = sys.argv[0]
    if (len(sys.argv) != 2):
        print("./generate_benchmark.py fast.bench")
        assert(False)
    file0 = sys.argv[1]#fast
    filename = file0[:file0.index('.')]
    cmd = "./stutter.py " + filename + ".bench"
    os.system(cmd)
    cmd = "./duplicate.py " + "slow_" + filename + ".bench" + ' ' + "fast_" + filename + ".bench"
    os.system(cmd)
    cmd = "./merge.py " + "syn_" + filename + ".bench" + ' ' + "stu_" + filename + ".bench"
    os.system(cmd)
    

if __name__ == '__main__':
    main()
