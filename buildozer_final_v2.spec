name: Build Android APK Final V2

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Install System Dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev libltdl-dev

      - name: Install Buildozer & Cython
        run: |
          python -m pip install --upgrade pip
          pip install "Cython==0.29.36"
          pip install buildozer

      # ఆండ్రాయిడ్ SDK లైసెన్స్‌లను గిట్‌హబ్ రన్నర్‌పై బలవంతంగా ముందే యాక్సెప్ట్ చేసే పక్కా లాజిక్
      - name: Force Accept Android SDK Licenses
        run: |
          mkdir -p ~/.android
          touch ~/.android/repositories.cfg
          mkdir -p $ANDROID_HOME/licenses || true
          echo -e "\n8933bad161ad75d6b1a485377d61f4a75a5b585e\n45f2885d62723d754b823e2182d321695b47a195\n24333f1a63b68b449d31d4e98585262c3123d22e" > $ANDROID_HOME/licenses/android-sdk-license || true

      - name: Build APK with Buildozer
        run: |
          buildozer -v android debug --filename buildozer_final_v2.spec

      - name: Upload APK Artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: BARAT-Core-APK
          path: bin/*.apk
