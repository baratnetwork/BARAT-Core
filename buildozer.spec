[app]
title = BARAT Core
package.name = baratcore
package.domain = org.barat
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 31
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
