
''''
Reference for camera commmands can be found in cl600x2-SU-07-D_manual.pdf in microscope folder

The dictionary values are (cam command, framegrabber command if appropriate)
'''

cam_shell = '/opt/Microscope/ConfigFiles/UpdateCam'
#cam_shell = '/opt/SiliconSoftware/Runtime5.7.0/siso-rt5-5.7.0.76321-linux-amd64/bin/clshell'
mcf_file = ''


param_dict = {'serial':('#N',''),
              'firmware':('#f',''),
              'baudrate':('#B',''),
              'gain':('#G',''),
              'fpn':('#F',''),
              'lut':('#L',''),
              'updatelut':('#l',''),
              'extsync':('#S',''),
              'synchpol':('#P',''),
              'synchmod':('#m',''),
              'synchsrc':('#s',''),
              'frameformat':('#R',''),
              'framerate':('#r',''),
              'maxframerate': ('#A',''),
              'exptime': ('#e',''),
              'maxexptime': ('#a',''),
              'dualslope': ('#D',''),
              'dualslopetime': ('#d',''),
              'tripleslope': ('#T',''),
              'tripleslopetime': ('#t',''),
              'cameramode': ('#C',''),
              'testimagemode': ('#I',''),
              'currentmode': ('#v',''),
              'startupmode': ('#V',''),
              'recordonusermode': ('#u',''),
              'resetcamera': ('#o',''),
              'blacklevel': ('#z',''),
              'camlinkdatafreq': ('#c', ''),
              'numroi': ('#h',''),
              'roistart': ('#H',''),
              'nondestructivereadout': ('#k', ''),
              'lasterror': ('#E',''),
              'invert': ('#Q',''),
              'calibration': ('#K',''),
              'movingwindow': ('#M',''),
              'camerastate': ('#X',''),
              'framestampingmode': ('#Z','')


}