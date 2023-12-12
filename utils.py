import re
import imageio.v3 as iio

def read_image(source):
    img = iio.imread(source)
    img_type = 3
    img_MIME_string = ""
    img_desc_string = ""
    img_width = img.shape[0]
    img_height = img.shape[1]
    img_color_depth = img.shape[2]
    img_color_number = 0

    return (img_type, img_MIME_string, img_desc_string, img_width, img_height, img_color_depth, img_color_number)

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

