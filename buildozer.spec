[app]
title = BARAT Core
package.name = baratcore
package.domain = org.barat
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy==2.3.0,cython==0.29.36
orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
