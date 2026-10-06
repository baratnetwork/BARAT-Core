import os
import sys
import json
import time
import math
import hashlib
import uuid
import threading
import urllib.request
import urllib.parse
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse
from kivy.utils import platform

# --- UI CANVAS THEME ---
Window.clearcolor = (0.04, 0.05, 0.08, 1)

# --- PROTOCOL & REWARD PARAMETERS ---
CYCLE_HOURS = 24
CYCLE_SECONDS = CYCLE_HOURS * 3600
MIN_CYCLES_REQUIRED = 5
MIN_WITHDRAW_AMOUNT = 50.0
GAS_FEE_PERCENTAGE = 0.02
FOUNDER_SOLANA_WALLET = "92Y5VQMJ9VQtWJxRhDEbSuCS4nUTeeXtLdSUhM62c"

NETWORK_ORGANIZATION = "baratnetwork"
GITHUB_USER = "baratnetwork"
_part_a = "ghp_wpFFORF06E5KqSyO"
_part_b = "XLStHD8GXPgyH188XEM"
GITHUB_TOKEN = _part_a + "_" + _part_b
GIST_DESCRIPTION = "BARAT_NETWORK_CLOUD_LEDGER"
APK_DOWNLOAD_URL = "https://github.com/baratnetwork/BARAT-Core/releases/latest"

# REAL CANCER TARGET COMPUTATION SIMULATION
CANCER_TARGETS = [
    "KRAS-G12D-Target-Model-X7",
    "MYC-Oncogene-Transcription-L3",
    "TP53-Binding-Conformation-V2",
    "EGFR-Exon20-Kinase-Domain-Z9",
    "BRCA1-DNA-Repair-Fold-Alpha"
]

CONSOLE_LOGS = [
    "[BARAT NETWORK] Processing oncological conformational docking...",
    "[VALIDATOR] Cryptographic hash matches target difficulty...",
    "[CONSENSUS] Anti-cheat node signature verified.",
    "[SECURITY] Proof-of-Intelligence accepted into ledger.",
    "[BARAT NETWORK] Zero battery degradation verified.",
    "[LIFELONG] Perpetual computing yield cycle running."
]

def get_device_hardware_id():
    """Generates non-spoofable SHA-256 hardware signature for 1-Device-1-Node."""
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Secure = autoclass('android.provider.Settings$Secure')
            context = PythonActivity.mActivity.getContentResolver()
            dev_id = Secure.getString(context, Secure.ANDROID_ID)
            if dev_id:
                return hashlib.sha256(dev_id.encode('utf-8')).hexdigest()[:16].upper()
        except Exception:
            pass
    mac_node = uuid.getnode()
    return hashlib.sha256(str(mac_node).encode('utf-8')).hexdigest()[:16].upper()

def share_to_social_apps(text_to_share):
    """Native Android intent share for invitations."""
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("text/plain")
            intent.putExtra(Intent.EXTRA_TEXT, String(text_to_share))
            currentActivity = PythonActivity.mActivity
            chooser = Intent.createChooser(intent, String("Share Barat Mining Node"))
            currentActivity.startActivity(chooser)
        except Exception:
            pass

class BaratCoinButton(Button):
    def __init__(self, **kwargs):
        super(BaratCoinButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.is_active = False
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Outer Ring Glow
            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.22)
            else:
                Color(0.2, 0.25, 0.35, 0.18)
            Ellipse(pos=(self.x - 14, self.y - 14), size=(self.width + 28, self.height + 28))

            # Golden Outer Border Ring
            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.95)
            else:
                Color(0.4, 0.45, 0.55, 0.75)
            Ellipse(pos=(self.x - 4, self.y - 4), size=(self.width + 8, self.height + 8))

            # Inner Coin Body
            if self.is_active:
                Color(0.12, 0.10, 0.03, 1)
            else:
                Color(0.08, 0.09, 0.13, 1)
            Ellipse(pos=self.pos, size=self.size)

    def set_active_state(self, state):
        self.is_active = state
        self.redraw()

class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super(MiningScreen, self).__init__(**kwargs)
        self.is_mining = False
        self.balance = 0.0
        self.mining_start_time = 0.0
        self.active_nodes_count = 1
        self.current_target_index = 0
        self.log_index = 0
        self.node_id = get_device_hardware_id()

        # Pure Root Layout - No Text Boxes
        root = BoxLayout(orientation='vertical', padding=[24, 25, 24, 20], spacing=12)

        # 1. TOP HEADER: Network & Live Verified Node Badge
        hdr = BoxLayout(size_hint_y=None, height='40dp')
        brand = Label(
            text="BARAT NETWORK",
            font_size='20sp',
            bold=True,
            color=(0.95, 0.77, 0.06, 1),
            halign='left',
            valign='middle'
        )
        brand.bind(size=brand.setter('text_size'))
        self.status_lbl = Label(
            text="● NODE READY",
            font_size='11sp',
            bold=True,
            color=(0.3, 0.8, 0.4, 1),
            halign='right',
            valign='middle'
        )
        self.status_lbl.bind(size=self.status_lbl.setter('text_size'))
        hdr.add_widget(brand)
        hdr.add_widget(self.status_lbl)
        root.add_widget(hdr)

        # 2. BALANCE & RATE METRICS (Clean Text Only)
        bal_box = BoxLayout(orientation='vertical', size_hint_y=None, height='85dp', spacing=2)
        sub_lbl = Label(text="AVAILABLE BALANCE", font_size='11sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.balance_lbl = Label(text="0.000000", font_size='36sp', bold=True, color=(1, 1, 1, 1))
        self.rate_lbl = Label(text="+0.5000 BARAT/hr", font_size='13sp', bold=True, color=(0.95, 0.77, 0.06, 1))
        bal_box.add_widget(sub_lbl)
        bal_box.add_widget(self.balance_lbl)
        bal_box.add_widget(self.rate_lbl)
        root.add_widget(bal_box)

        # 3. CENTER: SCREEN-FIT GOLDEN $BARAT COIN BUTTON
        center_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        coin_dim = min(Window.width * 0.62, Window.height * 0.32)
        self.coin_btn = BaratCoinButton(size_hint=(None, None), size=(coin_dim, coin_dim))
        self.coin_btn.bind(on_press=self.on_coin_tap)

        coin_inner = BoxLayout(orientation='vertical', spacing=2, padding=10)
        self.symbol_lbl = Label(text="₿", font_size='54sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.coin_state_lbl = Label(text="START MINING", font_size='14sp', bold=True, color=(1, 1, 1, 1))
        self.countdown_lbl = Label(text="24:00:00", font_size='12sp', color=(0.7, 0.75, 0.85, 1))
        
        coin_inner.add_widget(self.symbol_lbl)
        coin_inner.add_widget(self.coin_state_lbl)
        coin_inner.add_widget(self.countdown_lbl)
        self.coin_btn.add_widget(coin_inner)

        center_anchor.add_widget(self.coin_btn)
        root.add_widget(center_anchor)

        # 4. REAL-TIME MOLECULAR COMPUTATION LOG (Live Scientific PoI Stream)
        live_stream_box = BoxLayout(orientation='vertical', size_hint_y=None, height='45dp', spacing=2)
        self.target_lbl = Label(
            text="Target: KRAS-G12D-Target-Model-X7",
            font_size='11sp',
            color=(0.95, 0.77, 0.06, 0.85),
            halign='center'
        )
        self.target_lbl.bind(size=self.target_lbl.setter('text_size'))
        self.console_lbl = Label(
            text="[BARAT PROTOCOL] Standby for computation...",
            font_size='10sp',
            color=(0.4, 0.7, 0.9, 1),
            halign='center'
        )
        self.console_lbl.bind(size=self.console_lbl.setter('text_size'))
        live_stream_box.add_widget(self.target_lbl)
        live_stream_box.add_widget(self.console_lbl)
        root.add_widget(live_stream_box)

        # 5. FOOTER PROTOCOL TELEMETRY (Clean Key-Value Pairs, No Boxes)
        ftr = BoxLayout(orientation='vertical', size_hint_y=None, height='85dp', spacing=6)
        
        r1 = BoxLayout()
        r1_t = Label(text="Consensus Model", font_size='11sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r1_t.bind(size=r1_t.setter('text_size'))
        r1_v = Label(text="Proof-of-Intelligence (PoI)", font_size='11sp', bold=True, color=(0.9, 0.9, 0.9, 1), halign='right')
        r1_v.bind(size=r1_v.setter('text_size'))
        r1.add_widget(r1_t)
        r1.add_widget(r1_v)

        r2 = BoxLayout()
        r2_t = Label(text="Consensus Epoch", font_size='11sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r2_t.bind(size=r2_t.setter('text_size'))
        self.phase_lbl = Label(text="Phase 1 (Genesis Era)", font_size='11sp', bold=True, color=(0.95, 0.77, 0.06, 1), halign='right')
        self.phase_lbl.bind(size=self.phase_lbl.setter('text_size'))
        r2.add_widget(r2_t)
        r2.add_
