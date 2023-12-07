import re

def strip_class_name(cls_name):
    result = re.search("MD[^>']*", cls_name) # leave everything that starts with MD
    return result.group(0)

def bytes_to_int(ba, little_endian=False):
    if type(ba) == int:
        return ba
    
    res = 0
    if little_endian:
        g = ba[-1::-1]
    else:
        g = ba

    for b in g:
        res = 256 * res + b
    return res

def resolve(data_):
    is_last = (data_ & 0b10000000) != 0 # checking the first bit
    block_type = data_ & 0b01111111

    return block_type, is_last

if __name__ == "__main__":
    for i in range(10, 5, -1):
        print(i)

