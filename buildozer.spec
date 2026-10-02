[app]

# (str) Title of your application
title = BARAT-Core

# (str) Package name
package.name = baratcore

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Application versioning (method 1)
version = 0.1

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen to the user
fullscreen = 0


# =======================================================
# Android specific
# =======================================================

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you justగతంలో మనకు ఏపీకే (APK) విజయవంతంగా డౌన్‌లోడ్ అయిన పూర్తి స్థిరమైన **`buildozer.spec`** కోడ్ ఇది. 

మీ రిపోజిటరీలోని `buildozer.spec` ఫైల్‌‌లో ఉన్న పాత కోడ్ మొత్తం తీసేసి, కింద ఉన్న ఈ పూర్తి కోడ్‌ను కాపీ చేసి పేస్ట్ చేయండి:

```ini
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
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0
