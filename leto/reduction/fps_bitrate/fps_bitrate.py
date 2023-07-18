from aEye import Video, Aux, Labeler 

def fps_bitrate(video_list):
    labeler = Labeler()
    labeler.change_fps(video_list, 30)
    labeler.set_bitrate(video_list, 0)
    return video_list