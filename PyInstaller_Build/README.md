# PyInstaller build (for OSX)

Read me first!!!

To get a more professional-looking you will need, at minimum, to create an application icns file and a 512x512 png file from your icns creation process. Directions for this process can be found by Googling "how to create custom mac icns" (without the quotes).

$ mkdir `<build dir>`
$ cd `<build dir>`

In your PyInstaller build directory `<build dir>,` put copies of your Python script `<your script>.py` (the one containing "if __name__ == '__main__': etc.") and any Python modules you have authored.

In addition, create a directory `<build dir>/data`, and into this directory, copy your app_icon_512x512.png mentioned above.

$ mkdir `data`

In order for your application to find app_icon_512x512.png and for Kivy to use it at app launch:
```
import os, sys
import platform
...
...
os_platform = platform.system()
execution_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
...
...
if (os_platform == "Darwin"):
    execution_directory = execution_directory.split("<your app>.app")[0]

    def resource_path ( relative_path ):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = execution_directory

        return os.path.join(base_path, relative_path)

    path_to_icon_image = resource_path(os.path.join("data", "app_icon_512x512.png"))

    Config.set('kivy','window_icon', path_to_icon_image)
    Config.write()
...
...
```

You should have already done:
$ pip install pyinstaller
or at the very least recently done:
$ pip install --upgrade pyinstaller

After the setup detailed above:
$ cd `<build dir>`
$ pyinstaller -F -w --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant --exclude-module twisted --add-data 'data/*.*:data' --osx-bundle-identifier `<your bundle identifier>`  -i `<your icns>.icns`  `<your app>.py`

PyInstaller will walk down your script/module/submodule structure finding all of the dependencies that are not "hidden". To make sure this works as intended, try executing `<build dir>/<your script>.py`. If it fails, PyInstaller will probably fail also.

You may be surprised at the size of `<your app>.app` in the `<build dir>/dist` directory. Paraphrasing the Python philosophy, Kivy adds "Executing at all is better than small executable size." Take matplotlib as an example. If matplotlib, and specifically matplotlib.pyplot, is a dependency of your application you should include as your first mention of matplotlib:
```
import matplotlib
matplotlib.use('AGG')
```
This will significantly reduce the footprint of your app, because PyInstaller will not walk down those other environment import trees.
