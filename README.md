# Overview
Safe, lightweight AWS/CW monitoring app targeted for Android, based on Kivy and boto3.

# Zero to OSX app for the modestly Pythonic
Obviously, if you know more about Python, you can successfully deviate more from this recipe. Or maybe ignore it altogether.

## Important note: This recipe can only totally work for OSX ##
Why? Because OSX apps are **not** monolithic binary files (as they are in Windows), internally they act almost like normal folders.

### My OS / platform / toolchain: ###
OSX 10.11.6 (long in the tooth, no longer supported by Docker, for example)

Python 2.7.16 (the current latest of this dynasty)

PyCharm CE 2017.3 (there are others out there, e.g. WingIDE, I've tried them all, but I use PyCharm)

### You'll need Kivy -- a simple but powerful Python GUI framework, SDK, etc. ###
I have installed the current "official" download shown here https://kivy.org/#download.

Some of the installation instructions here https://kivy.org/doc/stable/installation/installation.html didn't work as then written. But if you can do the usual install, the drag/drop of the dmg Kivy icon to the application fold icon, then you will be fine.

For PyCharm setup, which is not covered by the dmg, use PyCharm's "Terminal" tab to:
```
$ pip install kivy
```

And because my app is designed to interact with Amazon Web Services api, you may have other dependencies:
```
$ pip install urllib3
$ pip install botocore
$ pip install boto3
```

## This is absolutely crucial if painlessness is important to you: ##
### First, get your app working in PyCharm where debugging is relatively painless. ###

Second, from this very repository, download and unzip Kivy-OSX-Build_Kit.zip, 
```
$ cd <Kivy-OSX-Build_Kit>
```

### Read READ_ME_FIRST.txt, I mean really, read that first and follow the directions therein.
You will build get an OSX app that has my icon, admittedly not great. You can Google instructions for making your own icon source files. The process is quite simple and monumentally boring, but they get the job done in maybe 30 minutes.
