[app]
title = BARAT Core
package.name = baratcore
package.domain = org.sudheerki
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

# ఇక్కడ మీ యాప్ క్రాష్ అవ్వకుండా అన్ని డిపెండెన్సీలను పక్కాగా యాడ్ చేసాను
requirements = python3,kivy==2.3.0,kivymd,requests,urllib5,certifi,charset-normalizer,idna

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.ndk = 25b

# బిల్డ్ ఎర్రర్ రాకుండా p4a బ్రాంచ్‌ను స్థిరీకరించాము
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
