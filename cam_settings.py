from Generic.file_handling import save_dict_to_file
''''
Reference for camera commmands can be found in cl600x2-SU-07-D_manual.pdf in microscope folder

The dictionary values are (cam command, framegrabber command if appropriate)
'''


cam_dict = {'gain':             ['#G', None,0, [0, 1]],
            'fpn' :             ['#F', None, 1, [0, 1]],
            'frameformat':      ['#R', ['FG_XOFFSET', 'FG_YOFFSET', 'FG_HEIGHT', 'FG_WIDTH'], [0, 0, 1280, 1024], [[0, 1280], [0, 1024], [200, 1280], [1, 1024]]],
            'framerate':        ['#r', 'FG_FRAMESPERSEC', 400, [20, None]],
            'maxframerate':     ['#A', None, None, None],
            'exptime':          ['#e', 'FG_EXPOSURE', 1000, [1, None]],
            'maxexptime':       ['#a', None, None, None],
            'dualslope':        ['#D', None, 0, [0, 1]],
            'dualslopetime':    ['#d', None, 1, [1, 1000]],
            'tripleslope':      ['#T', None, 0, [0, 1]],
            'tripleslopetime':  ['#t', None, 1, [1, 150]],
            'blacklevel':       ['#z', None, 100, [0,255]]
}



if __name__ == '__main__':
    import numpy as np
    from Generic.filedialogs import save_filename

    filename=save_filename(directory='/opt/Microscope/ConfigFiles/', file_filter='*.ccf')
    save_dict_to_file(filename, cam_dict)