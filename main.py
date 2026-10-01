import json
import os
import re
import time
import random
import hashlib
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle

# Ultra Deep-Space Cyber Background
Window.clearcolor = (0.015, 0.03, 0.06, 1)

DATA_VAULT = "barat_secure_vault.json"
CURRENT_VERSION = "3.0.0"
MIN_KYC_BLOCKS = 50
SESSION_HOURS = 24

BIP39_WORDS = [
    "quantum", "neural", "tensor", "matrix", "carbon", "genome", "protein",
    "stellar", "cipher", "plasma", "galaxy", "atomic", "photon", "vector",
    "synapse", "nebula", "binary", "crypto", "beacon", "energy", "fusion"
]

def hash_sec(val):
    return hashlib.sha256(val.encode()).hexdigest()

def get_vault():
    defaults = {
        "version": CURRENT_VERSION,
        "users": {},
        "current_session": None,
        "used_ids": [],
        "stats": {"nodes": 18450, "hashrate": "620.8 TH/s", "blocks": 341020}
    }
    if os.path.exists(DATA_VAULT):
        try:
            with open(DATA_VAULT, "r") as f:
                return json.load(f)
        except Exception:
            return defaults
    return defaults

def save_vault(data):
    try:
        with open(DATA_VAULT, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass


# -------------------- 1. 3D INDIA MAP + BARAT EMBLEM GRAPHIC WIDGET --------------------
class BaratEmblem3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        r = min(self.width, self.height) * 0.42

        with self.canvas:
            # --- LAYER 1: 3D Holographic India Geo-Network Grid (Backdrop) ---
            # Cyber Grid Aura
            Color(0.0, 0.9, 0.5, 0.08)
            Ellipse(pos=(cx - r*1.3, cy - r*1.3), size=(r*2.6, r*2.6))
            Color(1.0, 0.6, 0.1, 0.05)
            Ellipse(pos=(cx - r*1.15, cy - r*1.15), size=(r*2.3, r*2.3))

            # India Constellation Coordinates (PoI Nodes Topology)
            Color(0.0, 0.9, 1.0, 0.35)
            nodes = [
                (0, 0.8), (0.2, 0.65), (-0.2, 0.5), (0.1, 0.3), (0.4, 0.25),
                (-0.4, 0.2), (0.3, 0.0), (-0.35, -0.1), (0.15, -0.3), (-0.1, -0.5),
                (0.0, -0.75)
            ]
            abs_pts = [(cx + nx*r*0.9, cy + ny*r*0.9) for nx, ny in nodes]
            for i in range(len(abs_pts) - 1):
                Line(points=[abs_pts[i][0], abs_pts[i][1], abs_pts[i+1][0], abs_pts[i+1][1]], width=1.1)

            Color(1.0, 0.7, 0.1, 0.7)
            for px, py in abs_pts:
                Ellipse(pos=(px - 2.5, py - 2.5), size=(5, 5))

            # --- LAYER 2: Front Metallic Gold Circular Emblem Ring ---
            # Outer Ring Shadow & Glow
            Color(0.85, 0.65, 0.15, 0.25)
            Line(circle=(cx, cy, r + 4), width=3.0)

            # Solid Gold Outer Circuit Border
            Color(0.95, 0.75, 0.2, 1.0)
            Line(circle=(cx, cy, r), width=2.8)

            # Deep Emerald Tech Core
            Color(0.04, 0.15, 0.12, 0.96)
            Ellipse(pos=(cx - r*0.92, cy - r*0.92), size=(r*1.84, r*1.84))

            # Inner Gold Accent Ring
            Color(0.85, 0.65, 0.15, 0.8)
            Line(circle=(cx, cy, r*0.92), width=1.2)

            # Quantum Atom Orbits (Front Hologram)
            Color(0.0, 0.9, 1.0, 0.5)
            Line(ellipse=(cx - r*0.4, cy + r*0.1, r*0.8, r*0.3), width=1.2)
            Line(ellipse=(cx - r*0.2, cy + r*0.1, r*0.4, r*0.6), width=1.2)

            # Central Processor Core
            Color(0.0, 1.0, 0.5, 0.8)
            Ellipse(pos=(cx - 6, cy - 6), size=(12, 12))


# -------------------- 2. ROUND PULSING START BUTTON --------------------
class CircularButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.draw_circle, size=self.draw_circle)

    def draw_circle(self, *args):
        self.canvas.before.clear()
        cx = self.center_x
        cy = self.center_y
        rad = min(self.width, self.height) / 2.0 - 6

        with self.canvas.before:
            # Outer Glow
            Color(0.0, 0.9, 0.6, 0.2)
            Ellipse(pos=(cx - rad - 8, cy - rad - 8), size=((rad + 8)*2, (rad + 8)*2))
            
            # Button Center Disc
            if self.state == 'down':
                Color(0.08, 0.25, 0.18, 1)
            else:
                Color(0.05, 0.18, 0.13, 1)
            Ellipse(pos=(cx - rad, cy - rad), size=(rad*2, rad*2))
            
            # Emerald Rim
            Color(0.0, 0.85, 0.55, 0.9)
            Line(circle=(cx, cy, rad), width=2.4)


# -------------------- 3. AUTH SCREEN (ANTI-BOT VERIFIED) --------------------
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n1 = random.randint(3, 9)
        self.n2 = random.randint(2, 8)
        self.ans = self.n1 * self.n2

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', padding=[24, 28, 24, 28], spacing=14, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        title = Label(
            text="[b][color=00e5ff]BARAT NETWORK[/color][/b]",
            markup=True,
            font_size='26sp',
            size_hint=(1, None),
            height=36
        )
        sub = Label(
            text="[color=8892b0]Proof of Intelligence (PoI) Global Infrastructure[/color]",
            markup=True,
            font_size='11sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(title)
        box.add_widget(sub)

        self.user_in = TextInput(
            hint_text="Node Username / ID",
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='13sp',
            padding=[10, 12, 10, 10]
        )
        self.pass_in = TextInput(
            hint_text="Node Access Key (Password)",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='13sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.user_in)
        box.add_widget(self.pass_in)

        # Anti-Bot Security Gate
        self.gate_lbl = Label(
            text=f"[color=64ffda]Human Verification: {self.n1} x {self.n2} = ?[/color]",
            markup=True,
            font_size='12sp',
            size_hint=(1, None),
            height=22
        )
        self.gate_in = TextInput(
            hint_text="Enter result to confirm you are human",
            multiline=False,
            size_hint=(1, None),
            height=44,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.gate_lbl)
        box.add_widget(self.gate_in)

        in_btn = Button(
            text="SIGN IN TO NODE",
            size_hint=(1, None),
            height=46,
            background_color=(0.0, 0.70, 0.90, 1),
            bold=True,
            font_size='13sp'
        )
        in_btn.bind(on_press=self.do_login)

        reg_btn = Button(
            text="CREATE NEW NODE ACCOUNT",
            size_hint=(1, None),
            height=46,
            background_color=(0.12, 0.20, 0.30, 1),
            bold=True,
            font_size='13sp'
        )
        reg_btn.bind(on_press=self.do_register)

        box.add_widget(in_btn)
        box.add_widget(reg_btn)

        self.msg = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=24)
        box.add_widget(self.msg)

        scroll.add_widget(box)
        self.add_widget(scroll)

    def refresh_gate(self):
        self.n1 = random.randint(3, 9)
        self.n2 = random.randint(2, 8)
        self.ans = self.n1 * self.n2
        self.gate_lbl.text = f"[color=64ffda]Human Verification: {self.n1} x {self.n2} = ?[/color]"
        self.gate_in.text = ""

    def verify_gate(self):
        v = self.gate_in.text.strip()
        if not v or not v.isdigit() or int(v) != self.ans:
            self.msg.text = "[color=ff4444]Human Verification Failed. Re-enter math answer.[/color]"
            self.refresh_gate()
            return False
        return True

    def do_login(self, instance):
        if not self.verify_gate():
            return
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault()

        if u in vault["users"] and vault["users"][u]["pwd"] == hash_sec(p):
            vault["current_session"] = u
            save_vault(vault)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "mining_screen"
            self.manager.get_screen("mining_screen").sync_ui()
        else:
            self.msg.text = "[color=ff3333]Invalid Credentials! Please check again.[/color]"
            self.refresh_gate()

    def do_register(self, instance):
        if not self.verify_gate():
            return
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault()

        if len(u) < 3 or len(p) < 6:
            self.msg.text = "[color=ffaa00]User: 3+ chars, Password: 6+ chars required![/color]"
            return

        if u in vault["users"]:
            self.msg.text = "[color=ff4444]Node Identifier already taken![/color]"
            return

        phrase = " ".join(random.sample(BIP39_WORDS, 12))
        vault["users"][u] = {
            "pwd": hash_sec(p),
            "mining_balance": 0.000000,
            "wallet_balance": 0.000000,
            "passphrase": phrase,
            "blocks": 0,
            "kyc_status": "Unverified",
            "session_start": 0,
            "is_active": False
        }
        vault["current_session"] = u
        vault["stats"]["nodes"] += 1
        save_vault(vault)

        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = "mining_screen"
        self.manager.get_screen("mining_screen").sync_ui()


# -------------------- 4. MINING DASHBOARD (CANVA STYLE EMBLEM & START BUTTON) --------------------
class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticker = None

        layout = BoxLayout(orientation='vertical', padding=[16, 12, 16, 10], spacing=8)

        # Header Info Card
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=26)
        self.user_lbl = Label(text="[color=8892b0]Node: Miner[/color]", markup=True, font_size='11sp', halign='left')
        self.user_lbl.bind(size=self.user_lbl.setter('text_size'))
        self.kyc_lbl = Label(text="[color=ff4444]● Unverified[/color]", markup=True, font_size='11sp', halign='right')
        self.kyc_lbl.bind(size=self.kyc_lbl.setter('text_size'))
        top_bar.add_widget(self.user_lbl)
        top_bar.add_widget(self.kyc_lbl)
        layout.add_widget(top_bar)

        # 3D INDIA MAP + BARAT EMBLEM (Generated completely in-code)
        self.emblem = BaratEmblem3D(size_hint=(1, None), height=210)
        layout.add_widget(self.emblem)

        # Subtitle Under Logo
        brand_sub = Label(
            text="[b][color=f5a623]PROOF OF INTELLIGENCE[/color][/b]\n[color=8892b0]SUSTAINABLE MOBILE MINING • INDIA NODE[/color]",
            markup=True,
            halign='center',
            size_hint=(1, None),
            height=34,
            font_size='10sp'
        )
        layout.add_widget(brand_sub)

        # Tokens Mined Card (Exact Canva style)
        self.mined_header = Label(
            text="[color=ffffff]Tokens Mined[/color]",
            markup=True,
            font_size='13sp',
            size_hint=(1, None),
            height=18
        )
        self.bal_display = Label(
            text="[b][color=ffffff]0.000000[/color] [color=00e5ff]$BARAT[/color][/b]",
            markup=True,
            font_size='22sp',
            size_hint=(1, None),
            height=34
        )
        layout.add_widget(self.mined_header)
        layout.add_widget(self.bal_display)

        # Session Status & Blocks
        meta_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=20)
        self.timer_lbl = Label(text="[color=ffaa00]24h Cycle: Inactive[/color]", markup=True, font_size='10sp')
        self.blocks_lbl = Label(text="[color=64ffda]Verified Blocks: 0[/color]", markup=True, font_size='10sp')
        meta_bar.add_widget(self.timer_lbl)
        meta_bar.add_widget(self.blocks_lbl)
        layout.add_widget(meta_bar)

        # Center Round START Button
        btn_container = BoxLayout(size_hint=(1, None), height=140, padding=[20, 5, 20, 5])
        self.start_btn = CircularButton(
            text="START",
            bold=True,
            font_size='18sp',
            size_hint=(None, None),
            size=(130, 130),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.start_btn.bind(on_press=self.toggle_session)
        btn_container.add_widget(self.start_btn)
        layout.add_widget(btn_container)

        # Claim Button
        claim_btn = Button(
            text="CLAIM TO INTERNAL WALLET",
            size_hint=(1, None),
            height=38,
            background_color=(0.0, 0.60, 0.80, 1),
            bold=True,
            font_size='11sp'
        )
        claim_btn.bind(on_press=self.claim_tokens)
        layout.add_widget(claim_btn)

        # Bottom Universal Nav
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=42, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_wall = Button(text="Wallet & KYC", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.go_to("wallet_screen"))
        n_stat = Button(text="Stats", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.go_to("stats_screen"))
        n_out = Button(text="Exit", background_color=(0.35, 0.10, 0.10, 1), font_size='11sp')
        n_out.bind(on_press=self.logout)

        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        nav.add_widget(n_out)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_ui(self):
        vault = get_vault()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.user_lbl.text = f"[color=8892b0]Node: [b]{user}[/b][/color]"
            st = udata.get("kyc_status", "Unverified")
            col = "00ff66" if st == "Verified" else ("ffaa00" if st == "Pending" else "ff4444")
            self.kyc_lbl.text = f"[color={col}][b]● {st}[/b][/color]"
            self.bal_display.text = f"[b][color=ffffff]{udata.get('mining_balance', 0.0):.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"
            self.blocks_lbl.text = f"[color=64ffda]Verified Blocks: {udata.get('blocks', 0)}[/color]"

            now = time.time()
            elapsed = now - udata.get("session_start", 0)
            if udata.get("is_active", False) and elapsed < (SESSION_HOURS * 3600):
                rem = int((SESSION_HOURS * 3600) - elapsed)
                self.timer_lbl.text = f"[color=00ff66]Active: {rem//3600}h {(rem%3600)//60}m left[/color]"
                self.start_btn.text = "MINING"
                if not self.ticker:
                    self.ticker = Clock.schedule_interval(self.step_mine, 1.0)
            else:
                udata["is_active"] = False
                self.timer_lbl.text = "[color=ffaa00]24h Cycle Complete[/color]"
                self.start_btn.text = "START"
                if self.ticker:
                    self.ticker.cancel()
                    self.ticker = None

    def toggle_session(self, instance):
        vault = get_vault()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        now = time.time()
        elapsed = now - udata.get("session_start", 0)

        if not udata.get("is_active", False) or elapsed >= (SESSION_HOURS * 3600):
            udata["is_active"] = True
            udata["session_start"] = now
            save_vault(vault)
            self.sync_ui()

    def step_mine(self, dt):
        vault = get_vault()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        udata["mining_balance"] += 0.0000694
        self.bal_display.text = f"[b][color=ffffff]{udata['mining_balance']:.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"

        if int(time.time()) % 10 == 0:
            udata["blocks"] += 1
            vault["stats"]["blocks"] += 1
            self.blocks_lbl.text = f"[color=64ffda]Verified Blocks: {udata['blocks']}[/color]"

        save_vault(vault)

    def claim_tokens(self, instance):
        vault = get_vault()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        amt = udata.get("mining_balance", 0.0)
        if amt > 0.0001:
            udata["wallet_balance"] = udata.get("wallet_balance", 0.0) + amt
            udata["mining_balance"] = 0.0
            save_vault(vault)
            self.sync_ui()

    def go_to(self, target):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = target
        if target == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_ui()
        elif target == "stats_screen":
            self.manager.get_screen("stats_screen").sync_ui()

    def logout(self, instance):
        if self.ticker:
            self.ticker.cancel()
        vault = get_vault()
        vault["current_session"] = None
        save_vault(vault)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "auth_screen"


# -------------------- 5. WALLET & KYC SCREEN --------------------
class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scan_ticker = None
        self.scan_val = 0

        layout = BoxLayout(orientation='vertical', padding=[16, 14, 16, 10], spacing=8)

        title = Label(
            text="[b][color=00e5ff]BARAT NON-CUSTODIAL WALLET[/color][/b]",
            markup=True,
            font_size='17sp',
            size_hint=(1, None),
            height=26
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Balance Card
        self.w_bal = Label(
            text="Internal Vault: [b]0.000000 $BARAT[/b]",
            markup=True,
            font_size='14sp',
            size_hint=(1, None),
            height=26
        )
        box.add_widget(self.w_bal)

        # 12-Word Passphrase Key Button
        phrase_btn = Button(
            text="VIEW 12-WORD SEED PHRASE KEY",
            size_hint=(1, None),
            height=40,
            background_color=(0.14, 0.20, 0.30, 1),
            font_size='11sp'
        )
        phrase_btn.bind(on_press=self.show_phrase)
        box.add_widget(phrase_btn)

        # Solana Transfer Section
        box.add_widget(Label(text="[b][color=64ffda]TRANSFER TO EXTERNAL SOLANA MAINNET[/color][/b]", markup=True, font_size='12sp', size_hint=(1, None), height=20))
        
        self.dest_sol = TextInput(
            hint_text="Destination Solana Public Key (Base58)",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        self.amt_sol = TextInput(
            hint_text="Amount of BARAT to transfer",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        box.add_widget(self.dest_sol)
        box.add_widget(self.amt_sol)

        send_btn = Button(
            text="EXECUTE SOLANA TRANSFER (2% Protocol Fee)",
            size_hint=(1, None),
            height=42,
            background_color=(0.0, 0.65, 0.85, 1),
            bold=True,
            font_size='11sp'
        )
        send_btn.bind(on_press=self.do_solana_transfer)
        box.add_widget(send_btn)

        self.tx_msg = Label(text="", markup=True, font_size='10sp', size_hint=(1, None), height=20)
        box.add_widget(self.tx_msg)

        # KYC Section
        box.add_widget(Label(text="[b][color=00e5ff]DECENTRALIZED KYC PROTOCOL[/color][/b]", markup=True, font_size='13sp', size_hint=(1, None), height=22))
        
        self.kyc_gate = Label(text="Eligibility: Checking...", markup=True, font_size='11sp', size_hint=(1, None), height=20)
        box.add_widget(self.kyc_gate)

        self.id_in = TextInput(
            hint_text="National ID / Passport Number",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        box.add_widget(self.id_in)

        self.id_btn = Button(
            text="SUBMIT ID DOCUMENT",
            size_hint=(1, None),
            height=40,
            background_color=(0.14, 0.45, 0.30, 1),
            font_size='11sp'
        )
        self.id_btn.bind(on_press=self.submit_id)
        box.add_widget(self.id_btn)

        self.scan_bar = ProgressBar(max=100, size_hint=(1, None), height=14)
        box.add_widget(self.scan_bar)

        self.face_btn = Button(
            text="START AI BIOMETRIC LIVENESS SCAN",
            size_hint=(1, None),
            height=42,
            background_color=(0.5, 0.35, 0.0, 1),
            bold=True,
            font_size='11sp'
        )
        self.face_btn.bind(on_press=self.start_face_check)
        box.add_widget(self.face_btn)

        self.kyc_status_lbl = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=24)
        box.add_widget(self.kyc_status_lbl)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Nav
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=42, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.go_to("mining_screen"))
        n_wall = Button(text="Wallet & KYC", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_stat = Button(text="Stats", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.go_to("stats_screen"))
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_ui(self):
        vault = get_vault()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.w_bal.text = f"Internal Vault: [b]{udata.get('wallet_balance', 0.0):.6f} $BARAT[/b]"
            st = udata.get("kyc_status", "Unverified")
            blks = udata.get("blocks", 0)

            if st == "Verified":
                self.kyc_gate.text = "[color=00ff66]✓ KYC Verified. Solana transfers enabled![/color]"
                self.id_btn.disabled = True
                self.face_btn.disabled = True
                self.kyc_status_lbl.text = "[color=00ff66]Tier-1 Node Verified[/color]"
            elif blks < MIN_KYC_BLOCKS:
                rem = MIN_KYC_BLOCKS - blks
                self.kyc_gate.text = f"[color=ff4444]Locked: Mine {rem} more blocks to unlock (Min: {MIN_KYC_BLOCKS})[/color]"
                self.id_btn.disabled = True
                self.face_btn.disabled = True
            else:
                self.kyc_gate.text = f"[color=00ff66]✓ Eligible ({blks} Blocks). Proceed to ID & Face Scan.[/color]"
                self.id_btn.disabled = False
                self.face_btn.disabled = False
                col = "ffaa00" if st == "Pending" else "ff4444"
                self.kyc_status_lbl.text = f"[color={col}]Status: {st}[/color]"

    def show_phrase(self, instance):
        vault = get_vault()
        user = vault.get("current_session")
        phrase = vault["users"][user].get("passphrase", "")

        box = BoxLayout(orientation='vertical', padding=12, spacing=8)
        box.add_widget(Label(text="[b][color=ffaa00]SECRET 12-WORD PASSPHRASE[/color][/b]", markup=True, font_size='12sp'))
        
        t = TextInput(text=phrase, readonly=True, size_hint=(1, None), height=60, background_color=(0.04, 0.08, 0.12, 1), foreground_color=(0, 0.9, 1, 1), font_size='11sp')
        box.add_widget(t)
        
        b = Button(text="CLOSE", size_hint=(1, None), height=36, background_color=(0, 0.5, 0.7, 1))
        box.add_widget(b)

        p = Popup(title="Seed Key Backup", content=box, size_hint=(0.85, 0.4), auto_dismiss=False)
        b.bind(on_press=p.dismiss)
        p.open()

    def do_solana_transfer(self, instance):
        vault = get_vault()
        user = vault.get("current_session")
        udata = vault["users"][user]

        if udata.get("kyc_status") != "Verified":
            self.tx_msg.text = "[color=ff3333]Error: KYC Verification required for Solana transfers![/color]"
            return

        dest = self.dest_sol.text.strip()
        amt_s = self.amt_sol.text.strip()

        if not re.match(r"^[1-9A-HJ-NP-za-km-z]{32,44}$", dest):
            self.tx_msg.text = "[color=ff3333]Invalid Solana Base58 Address![/color]"
            return

        try:
            amt = float(amt_s)
        except ValueError:
            self.tx_msg.text = "[color=ff4444]Enter valid transfer number![/color]"
            return

        if udata.get("wallet_balance", 0.0) < amt:
            self.tx_msg.text = "[color=ff4444]Insufficient wallet balance![/color]"
            return

        fee = amt * 0.02
        net = amt - fee
        udata["wallet_balance"] -= amt
        save_vault(vault)
        self.sync_ui()
        self.tx_msg.text = f"[color=00ff66]Transferred {net:.4f} BARAT to Solana! (2% Fee to Reserve)[/color]"

    def submit_id(self, instance):
        doc = self.id_in.text.strip()
        if len(doc) < 6:
            self.kyc_status_lbl.text = "[color=ff4444]ID must be at least 6 characters![/color]"
            return

        d_hash = hash_sec(doc)
        vault = get_vault()
        if d_hash in vault.get("used_ids", []):
            self.kyc_status_lbl.text = "[color=ff2222]ID already used by another account![/color]"
            return

        user = vault.get("current_session")
        vault["users"][user]["id_hash"] = d_hash
        vault["users"][user]["kyc_status"] = "Pending"
        vault["used_ids"].append(d_hash)
        save_vault(vault)
        self.kyc_status_lbl.text = "[color=ffaa00]ID Verified. Now start Face Liveness Scan.[/color]"

    def start_face_check(self, instance):
        vault = get_vault()
        user = vault.get("current_session")
        if not vault["users"][user].get("id_hash"):
            self.kyc_status_lbl.text = "[color=ff3333]Submit ID record first![/color]"
            return

        self.scan_val = 0
        self.scan_bar.value = 0
        self.face_btn.text = "BIOMETRIC SCANNING..."
        self.face_btn.disabled = True
        self.scan_ticker = Clock.schedule_interval(self.step_scan, 0.15)

    def step_scan(self, dt):
        self.scan_val += 10
        self.scan_bar.value = self.scan_val
        if self.scan_val >= 100:
            if self.scan_ticker:
                self.scan_ticker.cancel()
            vault = get_vault()
            user = vault.get("current_session")
            vault["users"][user]["kyc_status"] = "Verified"
            save_vault(vault)
            self.face_btn.text = "FACE VERIFIED ✓"
            self.kyc_status_lbl.text = "[color=00ff66]KYC Approved! Full Tier-1 Access Granted.[/color]"
            self.sync_ui()

    def go_to(self, target):
        self.manager.transition = SlideTransition(direction='right' if target == "mining_screen" else 'left')
        self.manager.current = target
        if target == "mining_screen":
            self.manager.get_screen("mining_screen").sync_ui()
        elif target == "stats_screen":
            self.manager.get_screen("stats_screen").sync_ui()


# -------------------- 6. STATS SCREEN --------------------
class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[16, 14, 16, 10], spacing=10)

        title = Label(
            text="[b][color=00e5ff]GLOBAL NETWORK METRICS[/color][/b]",
            markup=True,
            font_size='17sp',
            size_hint=(1, None),
            height=26
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[8, 8, 8, 8])
        box.bind(minimum_height=box.setter('height'))

        self.n_lbl = Label(text="Active PoI Nodes: 18,450", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        self.h_lbl = Label(text="Global Hashrate: 620.8 TH/s", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        self.b_lbl = Label(text="Research Blocks Solved: 341,020", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        p_lbl = Label(text="[color=8892b0]Core Architecture: Hybrid PoI & Solana Bridge[/color]", markup=True, font_size='11sp', size_hint=(1, None), height=24)

        box.add_widget(self.n_lbl)
        box.add_widget(self.h_lbl)
        box.add_widget(self.b_lbl)
        box.add_widget(p_lbl)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Nav
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=42, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.go_to("mining_screen"))
        n_wall = Button(text="Wallet & KYC", background_color=(0.10, 0.15, 0.22, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.go_to("wallet_screen"))
        n_stat = Button(text="Stats", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_ui(self):
        vault = get_vault()
        stats = vault.get("stats", {})
        self.n_lbl.text = f"Active PoI Nodes: [b]{stats.get('nodes', 18450):,}[/b]"
        self.h_lbl.text = f"Global Hashrate: [b]{stats.get('hashrate', '620.8 TH/s')}[/b]"
        self.b_lbl.text = f"Research Blocks Solved: [b]{stats.get('blocks', 341020):,}[/b]"

    def go_to(self, target):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = target
        if target == "mining_screen":
            self.manager.get_screen("mining_screen").sync_ui()
        elif target == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_ui()


# -------------------- APPLICATION ENTRY POINT --------------------
class BaratCoreApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthScreen(name="auth_screen"))
        sm.add_widget(MiningScreen(name="mining_screen"))
        sm.add_widget(WalletScreen(name="wallet_screen"))
        sm.add_widget(StatsScreen(name="stats_screen"))

        vault = get_vault()
        if vault.get("current_session") and vault["current_session"] in vault["users"]:
            sm.current = "mining_screen"
            sm.get_screen("mining_screen").sync_ui()
        else:
            sm.current = "auth_screen"

        return sm


if __name__ == "__main__":
    BaratCoreApp().run()
