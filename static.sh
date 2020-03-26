#!/bin/sh

gcc -Wall -g -c demo.c -o demo.o
g++ -g -o demo demo.o libabc.a -lm -ldl -lreadline -lpthread
