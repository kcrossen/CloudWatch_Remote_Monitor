# PyInstaller build (for OSX)

Read me first!!!
```
$ mkdir <this directory>
$ cd <this directory>
```
Put all of the files from this diectory here.

Copy your executable Python script into this directory: 
```
$ cp ~/<your development directory>/<your app script>.py .
```
To make the launched app's icon yours rather than the Kivy icon, 
  replace all of the png files in 
  `<path to your python>/site-packages/kivy/data/logo` 
  with your own pngs.
$ cp *.png <absolute path to your python>/site-packages/kivy/data/logo

Now run:
```
$ pyinstaller -F -w --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant --exclude-module twisted --osx-bundle-identifier <your bundle identifier>  -i <your app icon>.icns  <your app script>.py
```
Currently, GitHub is failing to upload "appicons.icns" so get it from the zipped kit.
