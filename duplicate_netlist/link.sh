#!/bin/sh
gcc -Wall -g -c duplicate.c -o duplicate.o
g++ -g -o duplicate duplicate.o libabc.a -lm -ldl -lreadline -lpthread
