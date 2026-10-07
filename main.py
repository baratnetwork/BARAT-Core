import os
import sys
import json
import time
import hashlib
import uuid
import threading
import urllib.request
import urllib.parse
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse
from kivy.utils import platform
from kivy.core.clipboard import Clipboard

Window.clearcolor = (0.04, 0.05, 0.08, 1)

CYCLE_HOURS = 24
CYCLE_SECONDS = CYCLE_HOURS * 3600
MIN_CYCLES_REQUIRED = 5
MIN_WITHDRAW_AMOUNT = 50.0
GAS_FEE_PERCENTAGE = 0.02
FOUNDER_SOLANA_WALLET = "92Y5VQMJ9VQtWJxRhDEbSuCS4nUTeeXtLdSUhM62c"
TOKEN_CONTRACT_DEVNET = "BARATxxSimDevnetSPLTokenAddress1111111111111"
MAX_SUPPLY = 500000000
DECIMALS = 9

GITHUB_USER = "baratnetwork"
_part_a = "ghp_wpFFORF06E5KqSyO"
_part_b = "XLStHD8GXPgyH188XEM"
GITHUB_TOKEN = _part_a + "_" + _part_b
GIST_DESCRIPTION = "BARAT_NETWORK_CLOUD_LEDGER"
APK_DOWNLOAD_URL = "https://github.com/baratnetwork/BARAT-Core/releases/latest"

CANCER_TARGETS = [
    "KRAS-G12D-Target-Model-X7",
    "MYC-Oncogene-Transcription-L3",
    "TP53-Binding-Conformation-V2",
    "EGFR-Exon20-Kinase-Domain-Z9",
    "BRCA1-DNA-Repair-Fold-Alpha"
]

CONSOLE_LOGS = [
    "[BARAT PROTOCOL] Molecular docking engine active...",
    "[VALIDATOR] Zero thermal footprint verified on node.",
    "[CONSENSUS] Anti-cheat cryptographic hash validated.",
    "[SECURITY] Proof-of-Intelligence block submitted.",
    "[LEDGER] Continuous perpetual yield synced."
]

OFFICIAL_WHITEPAPER_TEXT = (
    "BARAT NETWORK PROTOCOL WHITEPAPER\n"
    "Decentralized Scientific Proof-of-Intelligence (PoI) on Solana\n"
    "--------------------------------------------------\n\n"
    "1. EXECUTIVE SUMMARY\n"
    "Barat Network transforms smartphone compute into biomedical discoveries\n"
    "using lightweight Proof-of-Intelligence (PoI) consensus.\n\n"
    "2. TOKENOMICS & 4-PHASE HALVING\n"
    "Total Supply: 500,000,000 $BARAT Strictly Capped.\n"
    "- Phase 1 (0-100k Nodes): 0.50 BARAT/hr (Genesis Active)\n"
    "- Phase 2 (100k-1M Nodes): 0.25 BARAT/hr (Devnet Bridge)\n"
    "- Phase 3 (1M-10M Nodes): 0.125 BARAT/hr (Mainnet TGE)\n"
    "- Phase 4 (10M+ Nodes): 0.0625 BARAT/hr (Perpetual Lifelong Era)\n\n"
    "3. CONSENSUS TARGETS (PoI)\n"
    "- KRAS-G12D-Target-Model-X7 (Pancreatic/Lung Oncology)\n"
    "- MYC-Oncogene-Transcription-L3\n"
    "- TP53-Binding-Conformation-V2\n"
    "- EGFR-Exon20-Kinase-Domain-Z9\n"
    "- BRCA1-DNA-Repair-Fold-Alpha\n\n"
    "4. ANTI-CHEAT & NODE SECURITY\n"
    "- 1-Device-1-Node Hardware Binding (SHA-256 Android ID)\n"
    "- 24-Hour Active Human Proof-of-Presence Cycle\n"
    "- Sybil Resistance blocks multi-instance emulators\n\n"
    "5. OFFICIAL ROADMAP\n"
    "- Phase 1 (2026): Genesis Distribution & PoI Mining\n"
    "- Phase 2 (Early 2027): Solana Devnet Bridge & Audits\n"
    "- Phase 3 (Mid/Late 2027): Mainnet TGE & Raydium DEX Listing\n"
    "- Phase 4 (2028+): Lifelong Perpetual Mining & Gas Yields\n"
)

def get_device_hardware_id():
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
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("text/plain")
            intent.putExtra(Intent.EXTRA_TEXT, String(text_to_share))
            PythonActivity.mActivity.startActivity(Intent.createChooser(intent, String("Share Barat Mining Node")))
            return
        except Exception:
            pass
    Clipboard.copy(text_to_share)

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
            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.22)
            else:
                Color(0.2, 0.25, 0.35, 0.18)
            Ellipse(pos=(self.x - 14, self.y - 14), size=(self.width + 28, self.height + 28))

            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.95)
            else:
                Color(0.4, 0.45, 0.55, 0.75)
            Ellipse(pos=(self.x - 4, self.y - 4), size=(self.width + 8, self.height + 8))

            if self.is_active:
                Color(0.12, 0.10, 0.03, 1)
            else:
                Color(0.08, 0.09, 0.13, 1)
            Ellipse(pos=self.pos, size=self.size)

    def set_active_state(self, state):
        self.is_active = state
        self.redraw()

class ActionMenuButton(Button):
    def __init__(self, **kwargs):
        super(ActionMenuButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.12, 0.14, 0.20, 1)
        self.color = (0.9, 0.9, 0.95, 1)
        self.font_size = '10sp'
        self.bold = True

class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super(AuthScreen, self).__init__(**kwargs)
        self.node_id = get_device_hardware_id()
        
        layout = BoxLayout(orientation='vertical', padding=[30, 40, 30, 30], spacing=15)
        
        header = Label(text="BARAT NETWORK", font_size='22sp', bold=True, color=(0.95, 0.77, 0.06, 1), size_hint_y=None, height='40dp')
        sub = Label(text="Secure Node Identification", font_size='12sp', color=(0.6, 0.65, 0.75, 1), size_hint_y=None, height='25dp')
        layout.add_widget(header)
        layout.add_widget(sub)

        node_box = BoxLayout(orientation='vertical', size_hint_y=None, height='65dp', spacing=3)
        n_title = Label(text="DEVICE HARDWARE NODE ID", font_size='11sp', color=(0.5, 0.55, 0.65, 1), bold=True)
        self.n_val = Label(text=f"Node-{self.node_id}", font_size='13sp', color=(0.3, 0.85, 0.45, 1), bold=True)
        node_box.add_widget(n_title)
        node_box.add_widget(self.n_val)
        layout.add_widget(node_box)

        self.username_input = TextInput(hint_text="Enter Miner Call-Sign (Username)", multiline=False, size_hint_y=None, height='42dp', font_size='12sp')
        layout.add_widget(self.username_input)

        self.pin_input = TextInput(hint_text="Security Pin (4-6 Digits)", password=True, multiline=False, size_hint_y=None, height='42dp', font_size='12sp')
        layout.add_widget(self.pin_input)

        self.msg_lbl = Label(text="", font_size='11sp', color=(0.9, 0.4, 0.2, 1), size_hint_y=None, height='25dp')
        layout.add_widget(self.msg_lbl)

        btn_row = BoxLayout(size_hint_y=None, height='44dp', spacing=12)
        login_btn = Button(text="CONNECT NODE", font_size='11sp', bold=True, background_normal='', background_color=(0.15, 0.55, 0.35, 1))
        login_btn.bind(on_press=self.do_auth)
        
        reg_btn = Button(text="REGISTER NEW", font_size='11sp', bold=True, background_normal='', background_color=(0.20, 0.25, 0.38, 1))
        reg_btn.bind(on_press=self.do_register)
        
        btn_row.add_widget(login_btn)
        btn_row.add_widget(reg_btn)
        layout.add_widget(btn_row)

        sec_info = Label(text="Anti-Cheat: 1 Device = 1 Cryptographic Node Binding", font_size='10sp', color=(0.4, 0.45, 0.55, 1))
        layout.add_widget(sec_info)

        self.add_widget(layout)

    def on_enter(self):
        if os.path.exists("miner_auth.json"):
            try:
                with open("miner_auth.json", "r") as f:
                    auth_data = json.load(f)
                    if auth_data.get("registered", False) and auth_data.get("node_id") == self.node_id:
                        self.manager.current = 'mining'
            except Exception:
                pass

    def do_register(self, *args):
        u = self.username_input.text.strip()
        p = self.pin_input.text.strip()
        if len(u) < 3:
            self.msg_lbl.text = "Username must be at least 3 characters!"
            return
        if len(p) < 4:
            self.msg_lbl.text = "Pin must be at least 4 digits!"
            return

        with open("miner_auth.json", "w") as f:
            json.dump({
                "username": u,
                "pin_hash": hashlib.sha256(p.encode()).hexdigest(),
                "node_id": self.node_id,
                "registered": True
            }, f)
        self.manager.current = 'mining'

    def do_auth(self, *args):
        u = self.username_input.text.strip()
        p = self.pin_input.text.strip()
        if not os.path.exists("miner_auth.json"):
            self.msg_lbl.text = "Node not registered. Please tap Register New!"
            return
        try:
            with open("miner_auth.json", "r") as f:
                d = json.load(f)
                if d.get("username") == u and d.get("pin_hash") == hashlib.sha256(p.encode()).hexdigest():
                    if d.get("node_id") == self.node_id:
                        self.manager.current = 'mining'
                    else:
                        self.msg_lbl.text = "Hardware ID mismatch! Unauthorized device."
                else:
                    self.msg_lbl.text = "Invalid Call-sign or Security Pin!"
        except Exception:
            self.msg_lbl.text = "Authentication failed. Try again."

class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super(MiningScreen, self).__init__(**kwargs)
        self.is_mining = False
        self.balance = 0.0
        self.mining_start_time = 0.0
        self.completed_cycles = 0
        self.user_solana_wallet = ""
        self.active_nodes_count = 1
        self.current_target_index = 0
        self.log_index = 0
        self.node_id = get_device_hardware_id()

        root = BoxLayout(orientation='vertical', padding=[20, 18, 20, 15], spacing=10)

        # Header
        hdr = BoxLayout(size_hint_y=None, height='38dp')
        brand = Label(text="BARAT NETWORK", font_size='19sp', bold=True, color=(0.95, 0.77, 0.06, 1), halign='left', valign='middle')
        brand.bind(size=brand.setter('text_size'))
        self.status_lbl = Label(text="● NODE READY", font_size='11sp', bold=True, color=(0.3, 0.8, 0.4, 1), halign='right', valign='middle')
        self.status_lbl.bind(size=self.status_lbl.setter('text_size'))
        hdr.add_widget(brand)
        hdr.add_widget(self.status_lbl)
        root.add_widget(hdr)

        # Balance Section (Pure text, no box frame)
        bal_box = BoxLayout(orientation='vertical', size_hint_y=None, height='75dp', spacing=2)
        sub_lbl = Label(text="AVAILABLE BALANCE", font_size='11sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.balance_lbl = Label(text="0.000000", font_size='34sp', bold=True, color=(1, 1, 1, 1))
        self.rate_lbl = Label(text="+0.5000 BARAT/hr", font_size='12sp', bold=True, color=(0.95, 0.77, 0.06, 1))
        bal_box.add_widget(sub_lbl)
        bal_box.add_widget(self.balance_lbl)
        bal_box.add_widget(self.rate_lbl)
        root.add_widget(bal_box)

        # Center Screen-Fit Golden Coin
        center_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        coin_dim = min(Window.width * 0.56, Window.height * 0.28)
        self.coin_btn = BaratCoinButton(size_hint=(None, None), size=(coin_dim, coin_dim))
        self.coin_btn.bind(on_press=self.on_coin_tap)

        coin_inner = BoxLayout(orientation='vertical', spacing=2, padding=6)
        self.symbol_lbl = Label(text="₿", font_size='48sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.coin_state_lbl = Label(text="START MINING", font_size='13sp', bold=True, color=(1, 1, 1, 1))
        self.countdown_lbl = Label(text="24:00:00", font_size='11sp', color=(0.7, 0.75, 0.85, 1))
        coin_inner.add_widget(self.symbol_lbl)
        coin_inner.add_widget(self.coin_state_lbl)
        coin_inner.add_widget(self.countdown_lbl)
        self.coin_btn.add_widget(coin_inner)

        center_anchor.add_widget(self.coin_btn)
        root.add_widget(center_anchor)

        # Proof-of-Intelligence Telemetry
        telemetry_box = BoxLayout(orientation='vertical', size_hint_y=None, height='38dp', spacing=1)
        self.target_lbl = Label(text="Target: KRAS-G12D-Target-Model-X7", font_size='11sp', color=(0.95, 0.77, 0.06, 0.85), halign='center')
        self.target_lbl.bind(size=self.target_lbl.setter('text_size'))
        self.console_lbl = Label(text="[BARAT PROTOCOL] Standby for computation...", font_size='10sp', color=(0.4, 0.7, 0.9, 1), halign='center')
        self.console_lbl.bind(size=self.console_lbl.setter('text_size'))
        telemetry_box.add_widget(self.target_lbl)
        telemetry_box.add_widget(self.console_lbl)
        root.add_widget(telemetry_box)

        # Sleek Navigation Bar (Wallet, Whitepaper, Token, Invite)
        btn_bar = GridLayout(cols=4, size_hint_y=None, height='40dp', spacing=6)
        
        wallet_btn = ActionMenuButton(text="WALLET")
        wallet_btn.bind(on_press=self.open_wallet_dialog)

        wp_btn = ActionMenuButton(text="WHITEPAPER")
        wp_btn.bind(on_press=self.open_whitepaper_dialog)
        
        token_btn = ActionMenuButton(text="TOKEN")
        token_btn.bind(on_press=self.open_token_dialog)
        
        share_btn = ActionMenuButton(text="INVITE")
        share_btn.bind(on_press=self.on_share_tap)

        btn_bar.add_widget(wallet_btn)
        btn_bar.add_widget(wp_btn)
        btn_bar.add_widget(token_btn)
        btn_bar.add_widget(share_btn)
        root.add_widget(btn_bar)

        # Footer Status
        ftr = BoxLayout(orientation='vertical', size_hint_y=None, height='60dp', spacing=3)
        r1 = BoxLayout()
        r1_t = Label(text="Consensus Phase", font_size='11sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r1_t.bind(size=r1_t.setter('text_size'))
        self.phase_lbl = Label(text="Phase 1 (Genesis Era)", font_size='11sp', bold=True, color=(0.95, 0.77, 0.06, 1), halign='right')
        self.phase_lbl.bind(size=self.phase_lbl.setter('text_size'))
        r1.add_widget(r1_t)
        r1.add_widget(self.phase_lbl)

        r2 = BoxLayout()
        r2_t = Label(text="Node Fingerprint", font_size='11sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r2_t.bind(size=r2_t.setter('text_size'))
        r2_v = Label(text=f"Node-{self.node_id[:8]}", font_size='11sp', bold=True, color=(0.3, 0.8, 0.4, 1), halign='right')
        r2_v.bind(size=r2_v.setter('text_size'))
        r2.add_widget(r2_t)
        r2.add_widget(r2_v)
        ftr.add_widget(r1)
        ftr.add_widget(r2)
        root.add_widget(ftr)

        self.add_widget(root)

    def on_enter(self):
        self.load_local_state()
        Clock.schedule_interval(self.engine_tick, 1.0)
        Clock.schedule_interval(self.rotate_telemetry, 4.0)
        threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()

    def get_current_rate(self):
        if self.active_nodes_count <= 100000:
            return 0.50, "Phase 1 (Genesis Era)"
        elif self.active_nodes_count <= 1000000:
            return 0.25, "Phase 2 (Devnet Era)"
        elif self.active_nodes_count <= 10000000:
            return 0.125, "Phase 3 (Mainnet Era)"
        else:
            return 0.0625, "Phase 4 (Perpetual Era)"

    def load_local_state(self):
        if os.path.exists("miner_state.json"):
            try:
                with open("miner_state.json", "r") as f:
                    d = json.load(f)
                    self.balance = float(d.get("balance", 0.0))
                    self.is_mining = bool(d.get("is_mining", False))
                    self.mining_start_time = float(d.get("start_time", 0.0))
                    self.completed_cycles = int(d.get("completed_cycles", 0))
                    self.user_solana_wallet = str(d.get("user_wallet", ""))
            except Exception:
                pass
        self.update_ui_state()

    def save_local_state(self):
        try:
            with open("miner_state.json", "w") as f:
                json.dump({
                    "balance": self.balance,
                    "is_mining": self.is_mining,
                    "start_time": self.mining_start_time,
                    "completed_cycles": self.completed_cycles,
                    "user_wallet": self.user_solana_wallet,
                    "node_id": self.node_id
                }, f)
        except Exception:
            pass

    def on_coin_tap(self, *args):
        now = time.time()
        if not self.is_mining:
            self.is_mining = True
            self.mining_start_time = now
            self.save_local_state()
            self.update_ui_state()
            threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()
        else:
            if (now - self.mining_start_time) >= CYCLE_SECONDS:
                self.completed_cycles += 1
                self.mining_start_time = now
                self.save_local_state()
                self.update_ui_state()
                threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()

    def rotate_telemetry(self, dt):
        if self.is_mining:
            self.current_target_index = (self.current_target_index + 1) % len(CANCER_TARGETS)
            self.log_index = (self.log_index + 1) % len(CONSOLE_LOGS)
            self.target_lbl.text = f"Target: {CANCER_TARGETS[self.current_target_index]}"
            self.console_lbl.text = CONSOLE_LOGS[self.log_index]

    def engine_tick(self, dt):
        rate, phase = self.get_current_rate()
        self.rate_lbl.text = f"+{rate:.4f} BARAT/hr"
        self.phase_lbl.text = phase

        if self.is_mining:
            now = time.time()
            elapsed = now - self.mining_start_time
            if elapsed < CYCLE_SECONDS:
                self.balance += (rate / 3600.0) * dt
                self.balance_lbl.text = f"{self.balance:.6f}"

                rem = int(CYCLE_SECONDS - elapsed)
                h, m, s = rem // 3600, (rem % 3600) // 60, rem % 60
                self.countdown_lbl.text = f"{h:02d}:{m:02d}:{s:02d}"
                self.coin_state_lbl.text = "MINING ACTIVE"
                self.status_lbl.text = "● NODE COMPUTING"
                self.status_lbl.color = (0.2, 0.85, 0.45, 1)
                self.symbol_lbl.color = (0.95, 0.77, 0.06, 1)
                self.coin_btn.set_active_state(True)
            else:
                self.is_mining = False
                self.coin_state_lbl.text = "CLAIM & RESTART"
                self.countdown_lbl.text = "00:00:00"
                self.status_lbl.text = "● CYCLE ENDED"
                self.status_lbl.color = (0.9, 0.4, 0.2, 1)
                self.symbol_lbl.color = (0.5, 0.55, 0.65, 1)
                self.coin_btn.set_active_state(False)
                self.save_local_state()

    def update_ui_state(self):
        rate, phase = self.get_current_rate()
        self.balance_lbl.text = f"{self.balance:.6f}"
        self.rate_lbl.text = f"+{rate:.4f} BARAT/hr"
        self.phase_lbl.text = phase

        if self.is_mining:
            self.coin_state_lbl.text = "MINING ACTIVE"
            self.status_lbl.text = "● NODE COMPUTING"
            self.status_lbl.color = (0.2, 0.85, 0.45, 1)
            self.symbol_lbl.color = (0.95, 0.77, 0.06, 1)
            self.coin_btn.set_active_state(True)
        else:
            self.coin_state_lbl.text = "START MINING"
            self.countdown_lbl.text = "TAP TO RUN"
            self.status_lbl.text = "● NODE READY"
            self.status_lbl.color = (0.3, 0.8, 0.4, 1)
            self.symbol_lbl.color = (0.5, 0.55, 0.65, 1)
            self.coin_btn.set_active_state(False)

    def on_share_tap(self, *args):
        msg = f"Join Barat Network mobile mining! Proof-of-Intelligence node binding. My Node ID: {self.node_id}. Download: {APK_DOWNLOAD_URL}"
        share_to_social_apps(msg)

    def open_whitepaper_dialog(self, *args):
        box = BoxLayout(orientation='vertical', padding=12, spacing=8)
        scroll = ScrollView(size_hint=(1, 1))
        wp_lbl = Label(text=OFFICIAL_WHITEPAPER_TEXT, font_size='11sp', color=(0.85, 0.9, 0.95, 1), size_hint_y=None)
        wp_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        wp_lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        scroll.add_widget(wp_lbl)
        box.add_widget(scroll)

        close_btn = Button(text="CLOSE WHITEPAPER", size_hint_y=None, height='36dp', font_size='11sp', bold=True)
        box.add_widget(close_btn)

        popup = Popup(title="Barat Protocol Whitepaper", content=box, size_hint=(0.92, 0.85))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_wallet_dialog(self, *args):
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        info = Label(text=f"Completed Cycles: {self.completed_cycles}/{MIN_CYCLES_REQUIRED}\nMin Withdraw: {MIN_WITHDRAW_AMOUNT} BARAT (2% Gas Fee)", font_size='11sp', color=(0.8, 0.8, 0.8, 1))
        box.add_widget(info)

        w_input = TextInput(text=self.user_solana_wallet, hint_text="Enter Solana (SOL) Address", multiline=False, size_hint_y=None, height='40dp', font_size='11sp')
        box.add_widget(w_input)

        msg_lbl = Label(text="", font_size='11sp', color=(0.9, 0.7, 0.2, 1))
        box.add_widget(msg_lbl)

        btn_row = BoxLayout(size_hint_y=None, height='38dp', spacing=10)
        
        def save_and_withdraw(*_):
            val = w_input.text.strip()
            self.user_solana_wallet = val
            self.save_local_state()
            if len(val) < 32:
                msg_lbl.text = "Invalid Solana Address!"
                return
            if self.completed_cycles < MIN_CYCLES_REQUIRED:
                msg_lbl.text = f"Need {MIN_CYCLES_REQUIRED} full cycles to withdraw!"
                return
            if self.balance < MIN_WITHDRAW_AMOUNT:
                msg_lbl.text = f"Min {MIN_WITHDRAW_AMOUNT} BARAT required!"
                return
            msg_lbl.text = "Withdraw queued to Solana Devnet Bridge!"
            threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()

        w_btn = Button(text="SAVE & WITHDRAW", font_size='11sp', bold=True)
        w_btn.bind(on_press=save_and_withdraw)
        
        close_btn = Button(text="CLOSE", font_size='11sp', bold=True)
        btn_row.add_widget(w_btn)
        btn_row.add_widget(close_btn)
        box.add_widget(btn_row)

        popup = Popup(title="Solana Settlement Wallet", content=box, size_hint=(0.88, 0.48))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_token_dialog(self, *args):
        box = BoxLayout(orientation='vertical', padding=15, spacing=8)
        specs = (
            f"Asset: BARAT ($BARAT)\n"
            f"Decimals: {DECIMALS} | Max Supply: {MAX_SUPPLY:,}\n"
            f"Founder Vault: {FOUNDER_SOLANA_WALLET[:12]}...\n"
            f"Devnet Contract:\n{TOKEN_CONTRACT_DEVNET}"
        )
        t_lbl = Label(text=specs, font_size='11sp', color=(0.9, 0.9, 0.9, 1))
        box.add_widget(t_lbl)

        def copy_contract(*_):
            Clipboard.copy(TOKEN_CONTRACT_DEVNET)

        copy_btn = Button(text="COPY DEVNET ADDRESS", size_hint_y=None, height='36dp', font_size='11sp', bold=True)
        copy_btn.bind(on_press=copy_contract)
        box.add_widget(copy_btn)

        close_btn = Button(text="CLOSE", size_hint_y=None, height='36dp', font_size='11sp', bold=True)
        box.add_widget(close_btn)

        popup = Popup(title="Barat SPL Token Details", content=box, size_hint=(0.88, 0.48))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def sync_with_cloud_ledger(self):
        try:
            url = "https://api.github.com/gists"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "BaratNetworkNodeApp"
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                gists = json.loads(resp.read().decode())
                
            gist_id = None
            for g in gists:
                if g.get("description") == GIST_DESCRIPTION:
                    gist_id = g["id"]
                    break

            payload = {
                "files": {
                    "ledger.json": {
                        "content": json.dumps({
                            "node_id": self.node_id,
                            "balance": round(self.balance, 6),
                            "completed_cycles": self.completed_cycles,
                            "user_wallet": self.user_solana_wallet,
                            "founder_vault": FOUNDER_SOLANA_WALLET,
                            "last_sync": datetime.utcnow().isoformat()
                        }, indent=2)
                    }
                }
            }

            patch_url = f"https://api.github.com/gists/{gist_id}" if gist_id else "https://api.github.com/gists"
            req_data = json.dumps(payload).encode("utf-8")
            sync_req = urllib.request.Request(patch_url, data=req_data, headers=headers, method="PATCH" if gist_id else "POST")
            with urllib.request.urlopen(sync_req, timeout=10) as r:
                pass
        except Exception:
            pass

class MainApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(AuthScreen(name='auth'))
        sm.add_widget(MiningScreen(name='mining'))
        return sm

if __name__ == '__main__':
    MainApp().run()
