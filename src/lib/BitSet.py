#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

import math
import array

class BitSet(object):  
    # from low to high "00000001 00000010 00000011", the array is [1, 2, 3]  
    def __init__(self, capacity = 64):          
        super(BitSet, self).__init__()
        self.unit_size = 8  
        self.unit_count = abs(math.floor((capacity + self.unit_size - 1) / self.unit_size));  
        self.capacity = capacity  
        self.arr = array.array("B", [0] * self.unit_count)  
   
    def any(self):  
        #any bit is 1
        for a in self.arr:  
            if a != 0:  
                return True  
        return False  
   
    def all(self):  
        #all bits are 1
        t = (1 << self.unit_size) - 1  
        for a in self.arr:  
            if (a & t) != t:  
                return False  
        return True       
   
    def none(self):  
        # all bit are 0
        for a in self.arr:  
            if a != 0:  
                return False  
        return True  
        
    # all bits are 0, return true
    def isEmpty(self):  
        return self.none();  
  
    #at least one bit is 1, return true
    def intersects(self):  
        return self.any();  
  
    #bits size
    def length():  
        return self.size();  
  
    def __len__():  
        return self.size();  
  
    def size(self):  
        # all bits size
        return self.unit_count * self.unit_size          
   
    def count(self):  
        # the 1 bits size
        c = 0  
        for a in self.arr:  
            while a > 0:  
                if a & 1:  
                    c += 1  
                a = a>>1  
        return c   
   
    def get(self, pos):  
        #get the value of position "pos"
        index = int(pos / self.unit_size)  
        offset = (self.unit_size - (pos - index * self.unit_size) - 1) % self.unit_size  
        return (self.arr[index] >> offset) & 1  
  
    # find the next bit 0
    def nextClearBit(self, startIndex = 0):  
        for i in range(startIndex+1, self.size()):  
            if self.get(i) == 0:  
                return i;  
  
        return -1;  
  
    # find the next bit 1
    def nextSetBit(self, startIndex = 0):  
        for i in range(startIndex+1, self.size()):  
            if self.get(i) == 1:  
                return i;  
  
        return -1;          
   
    def test(self, pos):  
        # test whether the position "pos" is 1
        if self.get(pos):  
            return 1  
        return 0   
   
    def set(self, pos=-1):  
        # Set the position "pos" to bit 1
        # if pos = -1, all bits are set to 1        
        if pos >= 0:  
            index = int(pos / self.unit_size)  
            offset = (self.unit_size - (pos - index * self.unit_size) - 1) % self.unit_size  
            self.arr[index] = (self.arr[index]) | (1 << offset)  
        else:  
            t = (1 << self.unit_size) - 1  
            for i in range(self.unit_count):  
                self.arr[i] = self.arr[i] | t                   
   
    def reset(self, pos=-1):  
        # Set the position "pos" to bit 0
        # if pos = -1, all bits are set to 0
        if pos >= 0:  
            index = int(pos / self.unit_size)  
            offset = (self.unit_size - (pos - index * self.unit_size) - 1) % self.unit_size  
            x = (1 << offset)  
            self.arr[index] = (self.arr[index]) & (~x)  
        else:  
            for i in range(self.unit_count):  
                self.arr[i] = 0  
   
    # clear all bits
    def clear(self):  
        self.reset(-1);  
  
    def __getitem__(self, idx):  
        if idx < 0 or idx >= self.size():  
            raise IndexError("index out of range.");  
  
        return self.get(idx);  
  
    def __setitem__(self, idx, val):  
        if idx < 0 or idx >= self.size():  
            raise IndexError("index out of range.");  
  
        if (val == 0):  
            self.reset(idx);  
        elif(val == 1):  
            self.set(idx);  
  
    # not operation
    def flip(self, pos=-1):  
        if pos >= 0:  
            if self.get(pos):  
                self.reset(pos)  
            else:  
                self.set(pos)  
        else:  
            for i in range(self.unit_count):  
                self.arr[i] = ~self.arr[i] + (1 << self.unit_size)        
  
    # and operation
    def andOp(self, otherbit):  
        if type(self) != type(otherbit):  
             raise TypeError("and Op undefined for " + str(type(self)) + " + " + str(type(other)))  
  
        size_1 = self.size();  
        size_2 = otherbit.size();  
  
        minsize = min(size_1, size_2);  
  
        #如果比特集是从高位到低位排列，而操作应该是低位对齐  
        #所以应该是逆序迭代，但这种方式在两个比特集位数不等时会有问题  
        #所以还是默认比特集是小头序，即低字节先读取  
        #这样这个类设置数据时就是默认把低位设满  
        for i in range(minsize):  
            a = self.get(i);  
            b = otherbit.get(i);  
  
            if (a & b == 1):  
                self.set(i);  
            else:  
                self.reset(i);  
  
    # or operation
    def orOp(self, otherbit):  
        if type(self) != type(otherbit):  
             raise TypeError("or Op undefined for " + str(type(self)) + " + " + str(type(other)))  
  
        size_1 = self.size();  
        size_2 = otherbit.size();  
  
        minsize = min(size_1, size_2);  
  
        #如果比特集是从高位到低位排列，而操作应该是低位对齐  
        #所以应该是逆序迭代，但这种方式在两个比特集位数不等时会有问题  
        #所以还是默认比特集是小头序，即低字节先读取  
        #这样这个类设置数据时就是默认把低位设满  
        for i in range(minsize):  
            a = self.get(i);  
            b = otherbit.get(i);  
  
            if (a | b == 1):  
                self.set(i);  
            else:  
                self.reset(i);  
  
    # xor operation
    def xorOp(self, otherbit):  
        if type(self) != type(otherbit):  
             raise TypeError("xor Op undefined for " + str(type(self)) + " + " + str(type(other)))  
  
        size_1 = self.size();  
        size_2 = otherbit.size();  
  
        minsize = min(size_1, size_2);  
  
        #如果比特集是从高位到低位排列，而操作应该是低位对齐  
        #所以应该是逆序迭代，但这种方式在两个比特集位数不等时会有问题  
        #所以还是默认比特集是小头序，即低字节先读取  
        #这样这个类设置数据时就是默认把低位设满  
        for i in range(minsize):  
            a = self.get(i);  
            b = otherbit.get(i);  
  
            if (a != b):  
                self.set(i);  
            else:  
                self.reset(i);  
  
    def clone(self, otherbit):  
        self.unit_size = otherbit.unit_size;  
        self.unit_count = otherbit.unit_count;  
        self.capacity = otherbit.capacity;  
        self.arr = otherbit.arr;     
  
    # bits string output  
    def binstr(self):  
        b = ""  
        for a in self.arr:  
            t = bin(a)  
            b += "0" * (self.unit_size - len(t) + 2) + t + ","  
        return "[" + b.replace("0b", "").strip(",") + "]"  
   
    def show(self):  
        return self.arr            
          
    # bits hashcode
    def hashCode(self):  
        #return hash(str(self.show()));  
        return hash(self);

def main():  
    b_1 = BitSet(1024)  
    b_2 = BitSet(1024)  
  
    for i in range(1024):  
        if (i%2 == 0):  
            b_1.set(i);  
        if (i%5 != 0):  
            b_2.set(i);

    print("b_1: ", b_1.binstr(), b_1.show());  
    print("b_2: ", b_2.binstr(), b_2.show());  
  
    #AND
    b_2.andOp(b_1);  
    print("after and, b_2 = ", b_2.binstr(), b_2.show());  
      
    #OR 
    b_2.orOp(b_1);  
    print("after or, b_2 = ", b_2.binstr(), b_2.show());  
  
    #XOR  
    b_2.xorOp(b_1);  
    print("after xor, b_2 = ", b_2.binstr(), b_2.show());  
  
    #clone  
    b_3 = BitSet(8);  
    b_3.clone(b_2);  
    print(b_3.binstr(), b_3.show());  
  
    #XOR  
    b_2.xorOp(b_1);  
    print("after xor, b_2 = ", b_2.binstr(), b_2.show());  
    print(b_3.binstr(), b_3.show());  
  
    print(b_2.hashCode(), b_3.hashCode());  
  
    b_3.clone(b_1);  
    print(b_1.hashCode(), b_3.hashCode());  
    print(b_1.show());  
  
    print(b_3.binstr(), b_3.nextSetBit(5));     
  
if __name__ == '__main__':
    main()