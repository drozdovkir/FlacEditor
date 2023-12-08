from md_description import MDDescriptionTree, MDBlockApplication, MDBlockCuesheet, MDBlockSeekTable, MDBlockStreamInfo, MDBlockHeader, MDBlockData
from md import MD
from md_padding import MDBlockPadding
from md_vorbis import MDBlockVorbisComment
from md_image import MDBlockImage

from utils import *
from collections import namedtuple

BlockInfo = namedtuple("BlockInfo", "block_type is_last")

def read_content(track, length_, content_type=None):
    track_bytes = track.read(length_)
    match content_type:
        case "le":
            content = bytes_to_int(track_bytes, little_endian=True)
        case "be":
            content = bytes_to_int(track_bytes)
        case "s":
            content = track_bytes.decode("utf-8")
        case _:
            content = None

    desc = MDDescriptionTree(length=length_)

    return desc, track_bytes, content

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

def process_md_block_header(track):
    track_bytes = track.read(4)
    f, t = resolve(track_bytes[0])
    block_info = BlockInfo(f, t)
    body_length = bytes_to_int(track_bytes[1:4])

    md_block_header_desc = MDBlockHeader()

    desc_1 = MDDescriptionTree(start=0, length=1)
    desc_2 = MDDescriptionTree(start=1, length=3)

    md_block_header_desc.add_child(desc_1)
    md_block_header_desc.add_child(desc_2)

    return md_block_header_desc, track_bytes, block_info, body_length

def process_md_block_data(track, length):
    return MDBlockData(length_=length), bytearray(track.read(length)), None

def process_md_block_padding(track, length):
    return MDBlockData(length_=length), bytearray(track.read(length)), length

def process_flac_marker(track):
    track_bytes = track.read(4)
    marker = track_bytes.decode("utf-8")
    if marker != "fLaC":
        raise Exception()
    return MDDescriptionTree(length=4), track_bytes

def process_md_block_vorbis_comment(track, length):
    desc = MDBlockData()
    track_bytes = bytearray()

    desc_1, tb, vendor_length = read_content(track, 4, "le")
    track_bytes += tb

    desc_2, tb, _ = read_content(track, vendor_length, "s")
    track_bytes += tb

    desc_3, tb, user_comment_list_length = read_content(track, 4, "le")
    track_bytes += tb

    desc.add_child(desc_1)
    desc.add_child(desc_2)
    desc.add_child(desc_3)

    user_comments = []
    for _ in range(user_comment_list_length):
        desc_a, tb, user_comment_length = read_content(track, 4, "le")
        track_bytes += tb

        desc_b, tb, user_comment = read_content(track, user_comment_length, "s")
        track_bytes += tb
        
        user_comments.append(user_comment)
        
        desc.add_child(desc_a)
        desc.add_child(desc_b)
    
    return desc, track_bytes, user_comments

def process_md_block_image(track, length):
    desc = MDBlockData()
    track_bytes = bytearray()

    desc_1, tb, img_type = read_content(track, 4, "be")
    track_bytes += tb

    desc_2, tb, MIME_length = read_content(track, 4, "be")
    track_bytes += tb

    desc_3, tb, MIME_string = read_content(track, MIME_length, "s")
    track_bytes += tb

    desc_4, tb, desc_string_length = read_content(track, 4, "be")
    track_bytes += tb

    desc_5, tb, desc_string = read_content(track, desc_string_length, "s")
    track_bytes += tb

    desc_6, tb, img_width = read_content(track, 4, "be")
    track_bytes += tb

    desc_7, tb, img_height = read_content(track, 4, "be")
    track_bytes += tb

    desc_8, tb, img_color_depth = read_content(track, 4, "be")
    track_bytes += tb

    desc_9, tb, _ = read_content(track, 4, "be")
    track_bytes += tb

    desc_10, tb, img_size = read_content(track, 4, "be")
    track_bytes += tb

    desc_11, tb, _ = read_content(track, img_size)
    track_bytes += tb

    img_attrs = (img_type, MIME_string, desc_string, img_width, img_height, img_color_depth)

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

    return desc, track_bytes, img_attrs

def process_md_block(track):
    md_block_header_desc, track_bytes_1, block_info, body_length = process_md_block_header(track)

    if block_info.block_type > 6:
        raise Exception()
    
    process_md_block_data = processors[block_info.block_type]
    MDBlock = md_classes[block_info.block_type]
    md_block_data_desc, track_bytes_2, data = process_md_block_data(track, body_length)

    description = MDBlock()
    description.add_child(md_block_header_desc)
    description.add_child(md_block_data_desc)
    
    description.add_content(data)

    return description, track_bytes_1 + track_bytes_2, block_info

processors = {0: process_md_block_data,
              1: process_md_block_padding,
              2: process_md_block_data,
              3: process_md_block_data,
              4: process_md_block_vorbis_comment,
              5: process_md_block_data,
              6: process_md_block_image}

md_classes = {0: MDBlockStreamInfo,
              1: MDBlockPadding,
              2: MDBlockApplication,
              3: MDBlockSeekTable,
              4: MDBlockVorbisComment,
              5: MDBlockCuesheet,
              6: MDBlockImage}

def process_md(track):
    track_bytes = bytearray()
    desc_1, tb = process_flac_marker(track)
    md_desc = MD()
    md_desc.add_child(desc_1)
    track_bytes += tb

    i = 1
    while True:
        desc_, tb, block_info = process_md_block(track)
        md_desc.add_child(desc_)
        track_bytes += tb

        match block_info.block_type:
            case 1:
                md_desc.padding_block_idx = i
            case 4:
                md_desc.vorbis_block_idx = i
            case 6:
                md_desc.img_block_idx = i

        i += 1
        if block_info.is_last:
            break
    
    return md_desc, track_bytes
