# A very simple setup script to create 2 executables.
#
# Run the build process by entering 'setup.py py2exe' or
# 'python setup.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them hello.exe and test_wx.exe.

from distutils.core import setup
import os
from os.path import join
import shutil
import glob
import py2exe
from py2exe.build_exe import py2exe
#import matplotlib as mp

'''
pyCount_data_files = [

                      #("resource", ['resource\QLQuantitation.py']),
                      #("resource", ['resource\_QLQuantitation.pyd']),
                      #("resource", ['resource\ColorCalMatrix_EP6_FAM_HEX_Cy5_Q705_IdMatrix_DNA2.csv']),
                      # ID color matrix

                      ("", ['resource\pyCount.ico'])  # copy the icon here

                      ]
'''

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version='0',
    description='TestRecordAudio',
    name='Test',

    # targets to build

    #data_files=pyCount_data_files,

    options={'py2exe': {
        'includes': ["sip", 
                     #"matplotlib.backends.backend_tkagg",
                     #"matplotlib.backends.backend_wxagg",
                     #"matplotlib._image",
                     #"scipy.sparse.csgraph._validation", 
					 #r'scipy.special._ufuncs_cxx'
					 ],  # for scipy fitting function
        'dll_excludes': ["MSVCP90.dll"]  # "optimize": 2 #,'NETPackage', 'win32', 'pythonwin','System'
    }
    },
    console = [{'script': "Baidu_Yuyin_Audio.py"}],
    windows=[
        {
            'script': "Baidu_Yuyin_Audio.py"
            #'icon_resources': [(1, 'resource\pyCount.ico')]
        }
    ],
)
