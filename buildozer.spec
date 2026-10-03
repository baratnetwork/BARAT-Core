[app]

# (str) Title of your application
title = BARAT Core

# (str) Package name
package.name = baratcore

# (str) Package domain (needed for android packaging)
package.domain = org.barat

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0

# (str) Application versioning
version = 0.1

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.api = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
