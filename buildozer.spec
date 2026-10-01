[app]

# App Title & Package
title = BARAT Core
package.name = baratcore
package.domain = org.barat

# Source code where the main.py lives
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Versioning
version = 0.1

# Application requirements
requirements = python3,kivy

# Orientation
orientation = portrait

# Android specific configurations
fullscreen = 0
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk_api = 21

# Modern 64-bit architecture only (prevents compile errors)
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
