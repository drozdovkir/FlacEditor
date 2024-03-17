from md_description import MDDescriptionTree, MDBlockApplication, MDBlockCuesheet, MDBlockSeekTable, MDBlockStreamInfo, MDBlockHeader, MDBlockData
from md import MD
from md_padding import MDBlockPadding
from md_vorbis import MDBlockVorbisComment
from md_image import MDBlockImage

import ui


def test_tree(number):
    match number:
        case 0:
            tree = MD()

            flac_marker = MDDescriptionTree(length=4)

            tree.add_child(flac_marker)

            stream_info_block = MDBlockStreamInfo()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData(length_=824)

            stream_info_block.add_child(head)
            stream_info_block.add_child(body)

            tree.add_child(stream_info_block)

            vorbis_block = MDBlockVorbisComment()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData()
            a = MDDescriptionTree(length=4)
            b = MDDescriptionTree(length=10)
            c = MDDescriptionTree(length=4)
            d = MDDescriptionTree(length=4)
            e = MDDescriptionTree(length=9)
            f = MDDescriptionTree(length=4)
            g = MDDescriptionTree(length=9)

            body.add_child(a)
            body.add_child(b)
            body.add_child(c)
            body.add_child(d)
            body.add_child(e)
            body.add_child(f)
            body.add_child(g)

            vorbis_block.add_child(head)
            vorbis_block.add_child(body)

            vorbis_block.add_content(["ARTIST=ME", "ALBUM=WOW"])

            tree.add_child(vorbis_block)

            padding_block = MDBlockPadding()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData(length_=1000)

            padding_block.add_child(head)
            padding_block.add_child(body)

            padding_block.add_content(1000)

            tree.add_child(padding_block)

            tree.padding_block_idx = 3
            tree.vorbis_block_idx = 2
        
        case 1:
            tree = MD()

            flac_marker = MDDescriptionTree(length=4)

            tree.add_child(flac_marker)

            stream_info_block = MDBlockStreamInfo()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData(length_=824)

            stream_info_block.add_child(head)
            stream_info_block.add_child(body)

            tree.add_child(stream_info_block)

            padding_block = MDBlockPadding()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData(length_=1000)

            padding_block.add_child(head)
            padding_block.add_child(body)

            padding_block.add_content(1000)

            tree.add_child(padding_block)

            pic_block = MDBlockImage()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData(length_=560)

            pic_block.add_child(head)
            pic_block.add_child(body)

            tree.add_child(pic_block)

            vorbis_block = MDBlockVorbisComment()
            head = MDBlockHeader()
            a = MDDescriptionTree(length=1)
            b = MDDescriptionTree(length=3)

            head.add_child(a)
            head.add_child(b)

            body = MDBlockData()
            a = MDDescriptionTree(length=4)
            b = MDDescriptionTree(length=10)
            c = MDDescriptionTree(length=4)
            d = MDDescriptionTree(length=4)
            e = MDDescriptionTree(length=9)
            f = MDDescriptionTree(length=4)
            g = MDDescriptionTree(length=9)

            body.add_child(a)
            body.add_child(b)
            body.add_child(c)
            body.add_child(d)
            body.add_child(e)
            body.add_child(f)
            body.add_child(g)

            vorbis_block.add_child(head)
            vorbis_block.add_child(body)

            vorbis_block.add_content(["ARTIST=ME", "ALBUM=WOW"])

            tree.add_child(vorbis_block)

            tree.padding_block_idx = 2
            tree.vorbis_block_idx = 4
            tree.img_block_idx = 3
    
    return tree

if __name__ == "__main__":
    tracks = ["hahaahahahhahahahahahahahahhahahahahahahhahahahahahahahahahhahahahahahahahahah.flac", 
              "wow.flac", "opa.flac", "xd.flac",
               "lolololololollolololololololololololololollololololololollolololololollolololol.flac", 
               "bbbb.flac", "lol.flac", "bestsong.flac", "t.flac",
              "hello.flac", "g.flac", "ggg.flac"]
    
    picked = [False for _ in tracks]

    metadata = {"ARTIST": "me", "ALBUM": "nice", "GENRE": "rock", "YEAR": "1995", "STUDIO": "garage", "LICENSE": "emmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"}

    ui.create_layout()

    track_index = 0

    while True:
        key = ui.read_key()
        b = ui.process_key(key)

        if b != 0:
            break
