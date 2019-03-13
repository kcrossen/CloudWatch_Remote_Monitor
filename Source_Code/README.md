Instructions for setting up the CW_Remote.ini file will be found in CW_Remote_Ini_Create.py. The CW_Remote.ini file must reside in the same folder as the CW_Remote.py file.

This runs in PyCharm on OS-X and in PyDroid3 on an Android tablet. So far, every method to package this script has failed, py2app, PyInstaller, Buildozer in Kivy VM ...

### Dependencies: ###
```
urllib3
botocore
boto3
kivy
```

No luck getting Kivy's buildozer script to package for OSX. Here's how to do it by hand on OS-X 10.11.6 w/ Python 2.7.16, quickly and certainly:

1a) Install Kivy-1.10.1_osx10.13.5_builtin_python2_r1.dmg from https://github.com/kivy/kivy/releases

2a) Copy /Applications/Kivy2.app to ~/someplace_quiet as Kivy.app

3a) When you succeed, your app has your icon, but the windows it launches have the Kivy icon, create your own icon set:
```
appIcon.icns
kivy-icon-64.ico
kivy-icon-16.png
kivy-icon-24.png
kivy-icon-32.png
kivy-icon-48.png
kivy-icon-64.png
kivy-icon-128.png
kivy-icon-256.png
kivy-icon-512.png
```
4a) In Finder, right-click ~/someplace_quiet/Kivy.app:

4b) select "Show Package Contents", navigate to Contents/Resources and copy/replace appIcon.icns there

4c) still at Contents/Resources, in Finder menu click New Folder, and name it yourapp

4d) navigate to Contents/Resources/yourapp and copy your appIcon.icns there

4e) navigate to Contents/Resources/kivy/kivy/data/logo and copy/replace *.png, *.ico above to there

4f) select anything in Contents/Resource rght-click and pick Get Info, selct all of the "Where:" entry and copy

4g) in another Finder tab on Finder menu, Go, Go to Folder..., paste and type in /.kivy, Go

4h) navigate to icon directory and copy/replace *.png, *.ico as above to there 

5a) select anything in Contents/Resources/venv rght-click and pick Get Info, selct all of the "Where:" entry and copy

5b) start your terminal, iTerm2 in my case, 

5c) cd **paste what you copied** 
  
5d) for each dependency, in my case urllib3, botocore, boto3, do

5e) pip install urllib3 -t ., and same for all of your dependencies
  
6a) I'm using PyCharm to develop, so I take a copy of my working script, CW_Rempote.py and rename it main.py

6b) copy this new main.py to Contents/Resources/yourapp as in 4d) above.

7a) Should work if the directions were followed.
