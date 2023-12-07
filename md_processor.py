from md_description import *
from collections import namedtuple

BlockInfo = namedtuple("BlockInfo", "block_type is_last")

def read_content(track_bytes, index, length_, content_type=None):
    match content_type:
        case "le":
            content = bytes_to_int(track_bytes[index : index + length_], little_endian=True)
        case "be":
            content = bytes_to_int(track_bytes[index : index + length_])
        case "s":
            content = track_bytes[index : index + length_].decode("utf-8")
        case _:
            content = None

    index += length_
    desc = MDDescriptionTree(length=length_)

    return desc, index, content

def write_content(track_bytes, index, length_, content, content_type):
    match content_type:
        case "le":
            new_bytes = content.to_bytes(length=length_, byteorder="little")
        case "be":
            new_bytes = content.to_bytes(length=length_, byteorder="big")
        case "s":
            new_bytes = content.encode()
        case _:
            new_bytes = None
    
    i = 0
    for b in new_bytes:
        track_bytes[index + i] = b
        i += 1

    i = index + length_

def shift_bytes(track_bytes, start, finish, step, dir_):
    if dir_ * step > 0:
        for i in range(finish, start - dir_, -1):
            track_bytes[i + step*dir_] = track_bytes[i]
    else:
        for i in range(start, finish + dir_):
            track_bytes[i + step*dir_] = track_bytes[i]

def process_md_block_header(track_bytes, index):
    f, t = resolve(track_bytes[index])
    block_info = BlockInfo(f, t)
    body_length = bytes_to_int(track_bytes[index + 1 : index + 4])

    md_block_header_desc = MDBlockHeader()

    desc_1 = MDDescriptionTree(start=0, length=1)
    desc_2 = MDDescriptionTree(start=1, length=3)

    md_block_header_desc.add_child(desc_1)
    md_block_header_desc.add_child(desc_2)

    return md_block_header_desc, index + 4, block_info, body_length

def process_md_block_data(track_bytes, index, length):
    return MDBlockData(length_=length), index + length, None

def process_md_block_padding(track_bytes, index, length):
    return MDBlockData(length_=length), index + length, length

def process_flac_marker(track_bytes, index):
    marker = track_bytes[index : index + 4].decode("utf-8")
    if marker != "fLaC":
        raise Exception()
    return MDDescriptionTree(length=4), index + 4

def process_md_block_vorbis_comment(track_bytes, index, length_):
    desc = MDBlockData()

    desc_1, index, vendor_length = read_content(track_bytes, index, 4, "le")
    desc_2, index, _ = read_content(track_bytes, index, vendor_length, "s")
    desc_3, index, user_comment_list_length = read_content(track_bytes, index, 4, "le")

    desc.add_child(desc_1)
    desc.add_child(desc_2)
    desc.add_child(desc_3)

    user_comments = []
    for _ in range(user_comment_list_length):
        desc_a, index, user_comment_length = read_content(track_bytes, index, 4, "le")
        desc_b, index, user_comment = read_content(track_bytes, index, user_comment_length, "s")
        
        user_comments.append(user_comment)
        
        desc.add_child(desc_a)
        desc.add_child(desc_b)
    
    return desc, index, user_comments

def process_md_block_picture(track_bytes, index, length_):
    desc = MDBlockData()

    desc_1, index, pic_type = read_content(track_bytes, index, 4, "be")
    desc_2, index, MIME_length = read_content(track_bytes, index, 4, "be")
    desc_3, index, _ = read_content(track_bytes, index, MIME_length)
    desc_4, index, desc_string_length = read_content(track_bytes, index, 4, "be")
    desc_5, index, _ = read_content(track_bytes, index, desc_string_length)
    desc_6, index, pic_width = read_content(track_bytes, index, 4, "be")
    desc_7, index, pic_height = read_content(track_bytes, index, 4, "be")
    desc_8, index, pic_color_depth = read_content(track_bytes, index, 4, "be")
    desc_9, index, pic_color_number = read_content(track_bytes, index, 4, "be")
    desc_10, index, pic_size = read_content(track_bytes, index, 4, "be")
    desc_11, index, _ = read_content(track_bytes, index, pic_size)

    pic_attrs = (pic_type, pic_width, pic_height, pic_color_depth, pic_color_number)

    desc.add_child(desc_1)
    desc.add_child(desc_2)
    desc.add_child(desc_3)
    desc.add_child(desc_4)
    desc.add_child(desc_5)
    desc.add_child(desc_6)
    desc.add_child(desc_7)
    desc.add_child(desc_8)
    desc.add_child(desc_9)
    desc.add_child(desc_10)
    desc.add_child(desc_11)

    return desc, index, pic_attrs

def process_md_block(track_bytes, index):
    md_block_header_desc, index, block_info, body_length = process_md_block_header(track_bytes, index)

    if block_info.block_type > 6:
        raise Exception()
    
    process_md_block_data = processors[block_info.block_type]
    MDBlock = md_classes[block_info.block_type]
    md_block_data_desc, index, data = process_md_block_data(track_bytes, index, body_length)

    description = MDBlock()
    description.add_child(md_block_header_desc)
    description.add_child(md_block_data_desc)
    
    description.add_content(data)

    return description, index, block_info

processors = {0: process_md_block_data,
              1: process_md_block_padding,
              2: process_md_block_data,
              3: process_md_block_data,
              4: process_md_block_vorbis_comment,
              5: process_md_block_data,
              6: process_md_block_picture}

md_classes = {0: MDBlockStreamInfo,
              1: MDBlockPadding,
              2: MDBlockApplication,
              3: MDBlockSeekTable,
              4: MDBlockVorbisComment,
              5: MDBlockCuesheet,
              6: MDBlockPicture}

def process_md(track_bytes):
    index = 0
    desc_1, index = process_flac_marker(track_bytes, index)
    md_desc = MD()
    md_desc.add_child(desc_1)

    i = 1
    while True:
        desc_, index, block_info = process_md_block(track_bytes, index)
        md_desc.add_child(desc_)

        match block_info.block_type:
            case 1:
                md_desc.padding_block_idx = i
            case 4:
                md_desc.vorbis_block_idx = i
            case 6:
                md_desc.pic_block_idx = i

        i += 1
        if block_info.is_last:
            break
    
    return md_desc
    
if __name__ == "__main__":
    a = bytearray("aaaaaaabbbbbbbbbbbbbbbbbbbccccccc", encoding="utf-8")
    print(a)
    shift_bytes(a, 7, 25, -3, -1)
    print(a)
