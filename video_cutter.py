from Generic.video.videoviewer import VideoViewer


class VideoCutter(VideoViewer):
    def __init__(self, parent, cam, filename=None):
        self.filename = filename
        self.cam = cam
        self.framenum = 1
        VideoViewer.__init__(self, parent, filename=filename)
        self.selector.start_callback(1)
        self.selector.stop_callback(self.cam.camset.cam_dict['numpicsbuffer'][2])

    def load_vid(self):
        return 1, self.cam.camset.cam_dict['numpicsbuffer'][2]

    def load_frame(self):
        pixmap=self.cam.get_pixmap_image(self.framenum)
        self.viewer.setImage(pixmap)

    def save_callback(self):
        op_filename = self.filename + '_frames_' + str(self.selector.start) + '_' + str(
            self.selector.stop)
        self.cam.save_vid(startframe=self.selector.start, stopframe=self.selector.stop, ext='.mp4',filename=op_filename)



if __name__ == '__main__':
    filename = '/home/ppzmis/Videos/test20190812_155928.mp4'
    vid = VideoCutter(filename=filename)