import m3u8
import os


def create_transcoded_m3u8(original_m3u8_path, path):
    playlist = m3u8.load(original_m3u8_path)
    for segment in playlist.segments:
        segment.uri = new_chunk_path(segment.uri)
    #new_m3u8_path = os.path.join(os.path.dirname(original_m3u8_path), path)
    playlist.dump(path)

def new_chunk_path(path):
    # FIXME: filtering audio only
    return path.replace('.ts', '.aac')


create_transcoded_m3u8("http://wshls.acgvideo.com/live//live_1379344_1651168/playlist.m3u8", "./t")
