from track_editor import TrackEditor
import os
from dataclasses import dataclass

from utils import fuse_dicts


@dataclass
class AddTracks:
    content: list


@dataclass
class RemoveTracks:
    content: list


@dataclass
class AddMetadata:
    content: list


class QuitApp:
    pass


class Manager:
    def __init__(self):
        self.tracks = []
        self.metadata = {}

    def import_tracks(self, paths_: list[str], **kwargs):
        added_tracks = []

        for path_ in paths_:
            if os.path.isdir(path_):
                _, _, file_paths = next(os.walk(path_))

                for file_path in file_paths:
                    full_file_path = os.path.join(path_, file_path)
                    if file_path.endswith(".flac"):
                        te = TrackEditor(full_file_path)
                        if te is None:
                            continue

                        self.tracks.append(te)
                        added_tracks.append(file_path)

            elif os.path.isfile(path_):
                if path_.endswith(".flac"):
                    te = TrackEditor(path_)
                    if te is None:
                        return
                    
                    self.tracks.append(te)
                    added_tracks.append(path_)
                else:
                    raise Exception("Provided path does not contain flac file")

            else:
                raise Exception("Invalid path")
        
        return AddTracks(added_tracks)
        
    def edit_tracks(self, **kwargs):
        picked_tracks = kwargs["picked_tracks"]
        metadata = kwargs["picked_metadata"]

        if metadata is None:
            metadata = self.metadata

        for t in picked_tracks:
            for field, value in metadata.items():
                self.tracks[t].edit_field(field, value)
    
    def get_metadata(self, *args, **kwargs):
        picked_tracks = kwargs["picked_tracks"]
        
        res = {}

        for i, track in enumerate(self.tracks):
            if picked_tracks[i]:
                res = fuse_dicts(res, track.comments)

        return AddMetadata(res.items())
    
    def remove_tracks(self, tracks_to_remove):
        for t_ in tracks_to_remove:
            self.tracks[t_] = None

        while self.tracks.count(None) > 0:
            self.tracks.remove(None)

        return RemoveTracks(tracks_to_remove)
    
    def quit(self, *args, **kwargs):
        return QuitApp()

    # for debugging
    def print_metadata(self):
        for track in self.tracks:
            track.print_comments()
            print()

    
if __name__ == "__main__":
    manager = Manager()
    manager.import_tracks(["D:\Music\Albums\Electric Light Orchestra - Time"])
    print(manager.get_metadata([i for i in range(13)]))