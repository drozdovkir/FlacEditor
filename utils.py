import re
import imageio.v3 as iio

def read_image(source):
    img = iio.imread(source)

    img_attrs = {"type": 3,
                 "MIME_string": "",
                 "description_string": "",
                 "width": img.shape[0],
                 "height": img.shape[1],
                 "color_depth": img.shape[2],
                 "color_number": 0}

    return (img_attrs, img)

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

def compare_strings(s1: str, s2: str):
    while (i < len(s1)) and (i < len(s2)):
        if s1[i] != s2[i]:
            return i
        i += 1
    return len(s1)

def fuse_dicts(d1: dict, d2: dict):
    for key in d2:
        v2 = d2[key]
        if key in d1:
            v1 = d1[key]
            if isinstance(v1, list):
                v1.append(v2)
            elif v1 != v2:
                d1[key] = [v1, v2]
        else:
            d1[key] = v2
    
    return d1

if __name__ == "__main__":
    d1 = {"ARTIST": "me", "GENRE": "wow"}
    d2 = {"ALBUM": "opa", "ARTIST": "me", "GENRE": "xd"}
    d3 = {"GENRE": "rock"}

    print(fuse_dicts(fuse_dicts(d1, d2), d3))

