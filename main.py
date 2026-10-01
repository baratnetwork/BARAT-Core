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

# Cybernetic Deep-Space Web3 Palette
Window.clearcolor = (0.02, 0.04, 0.07, 1)

DATA_VAULT = "barat_secure_vault.json"
CURRENT_CLIENT_VERSION = "2.5.0"
MIN_KYC_BLOCKS = 50
SESSION_DURATION_SEC = 24 * 3600  # 24 Hours Active Node Session
PROJECT_FOUNDER_SOL_WALLET = "BARATFoundationSolanaReserveMasterKey999"

BIP39_WORDLIST = [
    "quantum", "neural", "tensor", "matrix", "carbon", "genome", "protein",
    "stellar", "cipher", "plasma", "galaxy", "atomic", "photon", "vector",
    "synapse", "nebula", "binary", "crypto", "beacon", "energy", "fusion",
    "orbital", "vortex", "zenith"
]

def hash_security(val):
    return hashlib.sha256(val.encode()).hexdigest()

def get_vault_data():
    defaults = {
        "client_version": CURRENT_CLIENT_VERSION,
        "users": {},
        "current_session": None,
        "used_ids": [],
        "remote_update": {
            "latest_version": "2.5.0",
            "update_available": False,
            "changelog": "Standard Release"
        },
        "global_stats": {
            "total_nodes": 14210,
            "network_hashrate": "512.4 TH/s",
            "total_blocks": 218490
        }
    }
    if os.path.exists(DATA_VAULT):
        try:
            with open(DATA_VAULT, "r") as f:
                return json.load(f)
        except Exception:
            return defaults
    return defaults

def save_vault_data(data):
    try:
        with open(DATA_VAULT, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass


# -------------------- 1. AUTH SCREEN (HUMAN VERIFICATION GATE) --------------------
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(3, 9)
        self.num2 = random.randint(2, 8)
        self.captcha_ans = self.num1 * self.num2

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', padding=[24, 28, 24, 28], spacing=14, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        title = Label(
            text="[b][color=00e5ff]BARAT NETWORK[/color][/b]",
            markup=True,
            font_size='28sp',
            size_hint=(1, None),
            height=42
        )
        subtitle = Label(
            text="[color=8892b0]Decentralized Proof-of-Intelligence Grid[/color]",
            markup=True,
            font_size='12sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(title)
        box.add_widget(subtitle)

        # Update Alert Banner
        self.update_banner = Label(
            text="",
            markup=True,
            font_size='11sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(self.update_banner)

        self.user_in = TextInput(
            hint_text="Node ID / Username",
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1),
            font_size='13sp',
            padding=[10, 12, 10, 10]
        )
        self.pass_in = TextInput(
            hint_text="Password / Security Key",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1),
            font_size='13sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.user_in)
        box.add_widget(self.pass_in)

        # Human Verification Layer (Anti-Bot)
        self.captcha_lbl = Label(
            text=f"[color=64ffda]Human Verification: {self.num1} x {self.num2} = ?[/color]",
            markup=True,
            font_size='12sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(self.captcha_lbl)

        self.captcha_in = TextInput(
            hint_text="Enter result to confirm you are not a bot",
            multiline=False,
            size_hint=(1, None),
            height=44,
            background_color=(0.06, 0.10, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.captcha_in)

        login_btn = Button(
            text="SIGN IN TO NODE",
            size_hint=(1, None),
            height=46,
            background_color=(0.0, 0.70, 0.90, 1),
            bold=True,
            font_size='13sp'
        )
        login_btn.bind(on_press=self.handle_login)

        reg_btn = Button(
            text="REGISTER NEW IDENTITY",
            size_hint=(1, None),
            height=46,
            background_color=(0.12, 0.18, 0.28, 1),
            bold=True,
            font_size='13sp'
        )
        reg_btn.bind(on_press=self.handle_register)

        box.add_widget(login_btn)
        box.add_widget(reg_btn)

        self.msg = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=24)
        box.add_widget(self.msg)

        scroll.add_widget(box)
        self.add_widget(scroll)

    def refresh_captcha(self):
        self.num1 = random.randint(3, 9)
        self.num2 = random.randint(2, 8)
        self.captcha_ans = self.num1 * self.num2
        self.captcha_lbl.text = f"[color=64ffda]Human Verification: {self.num1} x {self.num2} = ?[/color]"
        self.captcha_in.text = ""

    def verify_human(self):
        val = self.captcha_in.text.strip()
        if not val or not val.isdigit() or int(val) != self.captcha_ans:
            self.msg.text = "[color=ff4444]హ్యూమన్ వెరిఫికేషన్ విఫలమైంది! సరైన సమాధానం ఇవ్వండి.[/color]"
            self.refresh_captcha()
            return False
        return True

    def handle_login(self, instance):
        if not self.verify_human():
            return
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault_data()

        if not u or not p:
            self.msg.text = "[color=ff4444]వివరాలు నమోదు చేయండి![/color]"
            return

        if u in vault["users"] and vault["users"][u]["password_hash"] == hash_security(p):
            vault["current_session"] = u
            save_vault_data(vault)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "mining_screen"
            self.manager.get_screen("mining_screen").sync_screen()
        else:
            self.msg.text = "[color=ff3333]తప్పుడు వివరాలు! లాగిన్ విఫలమైంది.[/color]"
            self.refresh_captcha()

    def handle_register(self, instance):
        if not self.verify_human():
            return
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault_data()

        if len(u) < 3 or len(p) < 6:
            self.msg.text = "[color=ffaa00]యూజర్ కనీసం 3, పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి![/color]"
            return

        if u in vault["users"]:
            self.msg.text = "[color=ff4444]ఈ యూజర్ నేమ్ ఇప్పటికే రిజిస్టర్ అయింది![/color]"
            return

        # Generate Mnemonic Passphrase (12 words)
        phrase = " ".join(random.sample(BIP39_WORDLIST, 12))
        generated_sol_wallet = "BARAT_" + hashlib.sha256(phrase.encode()).hexdigest()[:38]

        vault["users"][u] = {
            "password_hash": hash_security(p),
            "unclaimed_mining": 0.000000,
            "wallet_balance": 0.000000,
            "passphrase": phrase,
            "internal_wallet": generated_sol_wallet,
            "destination_solana": "",
            "kyc_status": "Unverified",
            "kyc_id_hash": "",
            "verified_blocks": 0,
            "session_start_time": 0,
            "is_session_active": False,
            "node_multiplier": 1.0
        }
        vault["current_session"] = u
        vault["global_stats"]["total_nodes"] += 1
        save_vault_data(vault)

        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = "mining_screen"
        self.manager.get_screen("mining_screen").sync_screen()


# -------------------- 2. 24-HOUR MINING DASHBOARD --------------------
class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticker = None

        layout = BoxLayout(orientation='vertical', padding=[14, 12, 14, 8], spacing=8)

        # Header Info Card
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        self.user_lbl = Label(text="[color=ccd6f6]Node: Active[/color]", markup=True, font_size='12sp', halign='left')
        self.user_lbl.bind(size=self.user_lbl.setter('text_size'))
        self.kyc_lbl = Label(text="[color=ff4444]● Unverified[/color]", markup=True, font_size='12sp', halign='right')
        self.kyc_lbl.bind(size=self.kyc_lbl.setter('text_size'))
        top_bar.add_widget(self.user_lbl)
        top_bar.add_widget(self.kyc_lbl)
        layout.add_widget(top_bar)

        # Mining & Wallet Balances Card
        bal_card = BoxLayout(orientation='vertical', size_hint=(1, None), height=115, padding=8, spacing=3)
        bal_sub = Label(text="[color=8892b0]UNCLAIMED MINING ASSETS (POI WORKLOADS)[/color]", markup=True, font_size='10sp', size_hint=(1, None), height=14)
        self.unclaimed_lbl = Label(text="[b][color=ffffff]0.000000[/color] [color=00e5ff]$BARAT[/color][/b]", markup=True, font_size='24sp', size_hint=(1, None), height=36)
        
        stat_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=18)
        self.timer_lbl = Label(text="[color=ffaa00]Session: Inactive[/color]", markup=True, font_size='11sp')
        self.blocks_lbl = Label(text="[color=64ffda]Blocks: 0[/color]", markup=True, font_size='11sp')
        stat_bar.add_widget(self.timer_lbl)
        stat_bar.add_widget(self.blocks_lbl)

        bal_card.add_widget(bal_sub)
        bal_card.add_widget(self.unclaimed_lbl)
        bal_card.add_widget(stat_bar)
        layout.add_widget(bal_card)

        # Action Buttons (Start 24H Session & Claim to Wallet)
        btn_grid = BoxLayout(orientation='horizontal', size_hint=(1, None), height=46, spacing=8)
        self.power_btn = Button(
            text="START 24H NODE",
            background_color=(0.0, 0.75, 0.45, 1),
            bold=True,
            font_size='12sp'
        )
        self.power_btn.bind(on_press=self.toggle_node_session)

        self.claim_btn = Button(
            text="CLAIM TO WALLET",
            background_color=(0.0, 0.65, 0.85, 1),
            bold=True,
            font_size='12sp'
        )
        self.claim_btn.bind(on_press=self.claim_mining_to_wallet)

        btn_grid.add_widget(self.power_btn)
        btn_grid.add_widget(self.claim_btn)
        layout.add_widget(btn_grid)

        # Live Terminal Stream
        log_head = Label(text="[color=8892b0]GLOBAL POI COMPUTATIONAL STREAM[/color]", markup=True, font_size='10sp', size_hint=(1, None), height=14, halign='left')
        log_head.bind(size=log_head.setter('text_size'))
        layout.add_widget(log_head)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.terminal = Label(
            text="[color=495d75]>> BARAT Node Online. Ready for Medical and AI Tensor computation...[/color]\n",
            markup=True,
            font_size='10sp',
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.terminal.bind(texture_size=lambda inst, v: setattr(self.terminal, 'height', v[1]))
        self.terminal.bind(size=lambda inst, v: setattr(self.terminal, 'text_size', (v[0], None)))
        self.scroll.add_widget(self.terminal)
        layout.add_widget(self.scroll)

        # Universal Navigation
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_wall = Button(text="Barat Wallet", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.navigate_to("wallet_screen"))
        n_stat = Button(text="Stats", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.navigate_to("stats_screen"))
        n_out = Button(text="Sign Out", background_color=(0.35, 0.12, 0.12, 1), font_size='11sp')
        n_out.bind(on_press=self.do_logout)

        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        nav.add_widget(n_out)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.user_lbl.text = f"[color=ccd6f6]Node: [b]{user}[/b][/color]"
            st = udata.get("kyc_status", "Unverified")
            col = "00ff66" if st == "Verified" else ("ffaa00" if st == "Pending" else "ff4444")
            self.kyc_lbl.text = f"[color={col}][b]● {st}[/b][/color]"
            self.unclaimed_lbl.text = f"[b][color=ffffff]{udata.get('unclaimed_mining', 0.0):.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"
            self.blocks_lbl.text = f"[color=64ffda]Blocks: {udata.get('verified_blocks', 0)}[/color]"

            # Check 24-Hour Timer Status
            now = time.time()
            elapsed = now - udata.get("session_start_time", 0)
            if udata.get("is_session_active", False) and elapsed < SESSION_DURATION_SEC:
                rem_sec = int(SESSION_DURATION_SEC - elapsed)
                hrs = rem_sec // 3600
                mins = (rem_sec % 3600) // 60
                self.timer_lbl.text = f"[color=00ff66]Active: {hrs}h {mins}m left[/color]"
                self.power_btn.text = "NODE RUNNING"
                self.power_btn.background_color = (0.2, 0.5, 0.3, 1)
                if not self.ticker:
                    self.ticker = Clock.schedule_interval(self.step_compute, 1.0)
            else:
                udata["is_session_active"] = False
                self.timer_lbl.text = "[color=ffaa00]Session Ended. Restart[/color]"
                self.power_btn.text = "START 24H NODE"
                self.power_btn.background_color = (0.0, 0.75, 0.45, 1)
                if self.ticker:
                    self.ticker.cancel()
                    self.ticker = None

    def toggle_node_session(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        now = time.time()
        elapsed = now - udata.get("session_start_time", 0)

        if not udata.get("is_session_active", False) or elapsed >= SESSION_DURATION_SEC:
            udata["is_session_active"] = True
            udata["session_start_time"] = now
            save_vault_data(vault)
            self.sync_screen()
            self.terminal.text += "\n[color=00ff66]>> 24-Hour PoI Computation Session Activated![/color]"

    def step_compute(self, dt):
        vault = get_vault_data()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        now = time.time()
        if now - udata.get("session_start_time", 0) >= SESSION_DURATION_SEC:
            self.sync_screen()
            return

        # Mining increment
        udata["unclaimed_mining"] += 0.0000694
        self.unclaimed_lbl.text = f"[b][color=ffffff]{udata['unclaimed_mining']:.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"

        if int(now) % 8 == 0:
            udata["verified_blocks"] += 1
            vault["global_stats"]["total_blocks"] += 1
            self.blocks_lbl.text = f"[color=64ffda]Blocks: {udata['verified_blocks']}[/color]"
            tasks = [
                "Cancer_Protein_Fold_Chunk_Validated",
                "Atmospheric_CO2_Tensor_Computed",
                "Genomic_Sequence_Hash_Encrypted",
                "Neural_Synaptic_Weights_Mapped"
            ]
            self.terminal.text += f"\n[color=00e5ff]>> Verified {random.choice(tasks)} [Block #{udata['verified_blocks']}][/color]"

        save_vault_data(vault)

    def claim_mining_to_wallet(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        amount = udata.get("unclaimed_mining", 0.0)
        if amount <= 0.0001:
            self.terminal.text += "\n[color=ff4444]>> Claim Alert: కనీస బ్యాలెన్స్ (0.0001 BARAT) మైన్ చేయాలి![/color]"
            return

        udata["wallet_balance"] = udata.get("wallet_balance", 0.0) + amount
        udata["unclaimed_mining"] = 0.0
        save_vault_data(vault)
        self.sync_screen()
        self.terminal.text += f"\n[color=00ff66]>> Claim Success: {amount:.6f} BARAT అంతర్గత వాలెట్‌కు బదిలీ చేయబడ్డాయి![/color]"

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = target_screen
        if target_screen == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_screen()
        elif target_screen == "stats_screen":
            self.manager.get_screen("stats_screen").sync_screen()

    def do_logout(self, instance):
        if self.ticker:
            self.ticker.cancel()
        vault = get_vault_data()
        vault["current_session"] = None
        save_vault_data(vault)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "auth_screen"


# -------------------- 3. INBUILT WALLET & SECURE KYC PORTAL --------------------
class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scan_ticker = None
        self.scan_val = 0

        layout = BoxLayout(orientation='vertical', padding=[16, 14, 16, 8], spacing=10)

        title = Label(
            text="[b][color=00e5ff]BARAT NON-CUSTODIAL WALLET[/color][/b]",
            markup=True,
            font_size='18sp',
            size_hint=(1, None),
            height=28
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Balance Card
        self.vault_bal_lbl = Label(
            text="[color=ffffff]Wallet Balance: [b]0.000000 $BARAT[/b][/color]",
            markup=True,
            font_size='15sp',
            size_hint=(1, None),
            height=26
        )
        box.add_widget(self.vault_bal_lbl)

        # 12-Word Passphrase Button
        show_phrase_btn = Button(
            text="VIEW 12-WORD SEED PHRASE KEY",
            size_hint=(1, None),
            height=40,
            background_color=(0.15, 0.22, 0.32, 1),
            font_size='11sp'
        )
        show_phrase_btn.bind(on_press=self.display_phrase_popup)
        box.add_widget(show_phrase_btn)

        # Transfer to Solana Mainnet
        box.add_widget(Label(text="[b][color=64ffda]TRANSFER TO EXTERNAL SOLANA WALLET[/color][/b]", markup=True, font_size='12sp', size_hint=(1, None), height=20))
        
        self.dest_sol_in = TextInput(
            hint_text="Destination Solana Public Key (Base58)",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        self.send_amt_in = TextInput(
            hint_text="Amount of BARAT to transfer",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        box.add_widget(self.dest_sol_in)
        box.add_widget(self.send_amt_in)

        fee_notice = Label(
            text="[color=8892b0]Note: 2% Protocol Reserve Fee will be deducted and routed to BARAT Foundation Reserve.[/color]",
            markup=True,
            font_size='9sp',
            size_hint=(1, None),
            height=22
        )
        box.add_widget(fee_notice)

        send_sol_btn = Button(
            text="EXECUTE SOLANA TRANSFER",
            size_hint=(1, None),
            height=42,
            background_color=(0.0, 0.65, 0.85, 1),
            bold=True,
            font_size='12sp'
        )
        send_sol_btn.bind(on_press=self.execute_solana_transfer)
        box.add_widget(send_sol_btn)

        self.transfer_msg = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=20)
        box.add_widget(self.transfer_msg)

        # KYC Section (Eligibility + ID + Face)
        box.add_widget(Label(text="[b][color=00e5ff]DECENTRALIZED KYC PROTOCOL[/color][/b]", markup=True, font_size='13sp', size_hint=(1, None), height=22))
        
        self.kyc_gate_lbl = Label(
            text="అర్హత: తనిఖీ చేస్తోంది...",
            markup=True,
            font_size='11sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(self.kyc_gate_lbl)

        self.id_box = TextInput(
            hint_text="National ID / Passport Number",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='11sp',
            padding=[8, 10, 8, 8]
        )
        box.add_widget(self.id_box)

        self.id_btn = Button(
            text="SUBMIT ID RECORD",
            size_hint=(1, None),
            height=40,
            background_color=(0.15, 0.45, 0.35, 1),
            font_size='12sp'
        )
        self.id_btn.bind(on_press=self.submit_id)
        box.add_widget(self.id_btn)

        self.scan_bar = ProgressBar(max=100, size_hint=(1, None), height=14)
        box.add_widget(self.scan_bar)

        self.face_btn = Button(
            text="START BIOMETRIC FACE LIVENESS CHECK",
            size_hint=(1, None),
            height=42,
            background_color=(0.5, 0.35, 0.0, 1),
            bold=True,
            font_size='12sp'
        )
        self.face_btn.bind(on_press=self.start_face_scan)
        box.add_widget(self.face_btn)

        self.kyc_state_lbl = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=24)
        box.add_widget(self.kyc_state_lbl)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Bar
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.navigate_to("mining_screen"))
        n_wall = Button(text="Barat Wallet", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_stat = Button(text="Stats", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.navigate_to("stats_screen"))
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.vault_bal_lbl.text = f"[color=ffffff]Internal Balance: [b]{udata.get('wallet_balance', 0.0):.6f} $BARAT[/b][/color]"
            st = udata.get("kyc_status", "Unverified")
            blks = udata.get("verified_blocks", 0)

            if st == "Verified":
                self.kyc_gate_lbl.text = "[color=00ff66]✓ కేవైసీ విజయవంతంగా పూర్తయింది. సోలానా బదిలీలు ప్రారంభించవచ్చు![/color]"
                self.id_btn.disabled = True
                self.face_btn.disabled = True
                self.kyc_state_lbl.text = "[color=00ff66]Status: KYC Verified Node[/color]"
            elif blks < MIN_KYC_BLOCKS:
                rem = MIN_KYC_BLOCKS - blks
                self.kyc_gate_lbl.text = f"[color=ff4444]లాక్ చేయబడింది: ఇంకా {rem} బ్లాకులు కావాలి (కనీసం {MIN_KYC_BLOCKS})[/color]"
                self.id_btn.disabled = True
                self.face_btn.disabled = True
            else:
                self.kyc_gate_lbl.text = f"[color=00ff66]✓ అర్హత సాధించారు ({blks} Blocks). ఐడీ మరియు ఫేస్ ధృవీకరించండి.[/color]"
                self.id_btn.disabled = False
                self.face_btn.disabled = False
                col = "ffaa00" if st == "Pending" else "ff4444"
                self.kyc_state_lbl.text = f"[color={col}]Status: {st}[/color]"

    def display_phrase_popup(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        phrase = vault["users"][user].get("passphrase", "No Passphrase")

        content = BoxLayout(orientation='vertical', padding=14, spacing=10)
        content.add_widget(Label(text="[b][color=ffaa00]SECURITY ALERT: DO NOT SHARE THIS PHRASE[/color][/b]", markup=True, font_size='12sp'))
        
        phrase_txt = TextInput(
            text=phrase,
            readonly=True,
            size_hint=(1, None),
            height=70,
            background_color=(0.06, 0.1, 0.16, 1),
            foreground_color=(0, 0.9, 1, 1),
            font_size='11sp'
        )
        content.add_widget(phrase_txt)

        close_btn = Button(text="I HAVE STORED SAFELY", size_hint=(1, None), height=38, background_color=(0, 0.6, 0.8, 1))
        content.add_widget(close_btn)

        pop = Popup(title="12-Word Passphrase Seed Key", content=content, size_hint=(0.9, 0.45), auto_dismiss=False)
        close_btn.bind(on_press=pop.dismiss)
        pop.open()

    def execute_solana_transfer(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        udata = vault["users"][user]

        if udata.get("kyc_status") != "Verified":
            self.transfer_msg.text = "[color=ff3333]విఫలమైంది: కేవైసీ పూర్తయిన తర్వాతే సోలానా బదిలీలు సాధ్యం![/color]"
            return

        dest = self.dest_sol_in.text.strip()
        amt_str = self.send_amt_in.text.strip()

        sol_re = r"^[1-9A-HJ-NP-za-km-z]{32,44}$"
        if not re.match(sol_re, dest):
            self.transfer_msg.text = "[color=ff3333]తప్పు: సరైన Solana Base58 పబ్లిక్ కీ ఇవ్వండి![/color]"
            return

        try:
            amt = float(amt_str)
        except ValueError:
            self.transfer_msg.text = "[color=ff4444]సరైన సంఖ్యను నమోదు చేయండి![/color]"
            return

        if amt <= 10.0:
            self.transfer_msg.text = "[color=ffaa00]కనీస బదిలీ పరిమితి 10.0 BARAT![/color]"
            return

        if udata.get("wallet_balance", 0.0) < amt:
            self.transfer_msg.text = "[color=ff4444]సరిపడా బ్యాలెన్స్ లేదు![/color]"
            return

        # 2% Founder Protocol Fee
        fee = amt * 0.02
        final_transfer = amt - fee

        udata["wallet_balance"] -= amt
        save_vault_data(vault)
        self.sync_screen()

        self.transfer_msg.text = (
            f"[color=00ff66]విజయవంతం: {final_transfer:.4f} BARAT సోలానాకు పంపబడ్డాయి!\n"
            f"(2% ఫీజు {fee:.4f} BARAT ఫౌండర్ రిజర్వ్‌కు జమైంది)[/color]"
        )

    def submit_id(self, instance):
        doc = self.id_box.text.strip()
        if len(doc) < 6:
            self.kyc_state_lbl.text = "[color=ff4444]ఐడీ కనీసం 6 అక్షరాలు/సంఖ్యలు ఉండాలి![/color]"
            return

        doc_hash = hash_security(doc)
        vault = get_vault_data()

        if doc_hash in vault.get("used_ids", []):
            self.kyc_state_lbl.text = "[color=ff2222]హెచ్చరిక: ఈ ఐడీ ఇప్పటికే ఇంకో ఖాతాలో ఉపయోగించబడింది![/color]"
            return

        user = vault.get("current_session")
        vault["users"][user]["kyc_id_hash"] = doc_hash
        vault["users"][user]["kyc_status"] = "Pending"
        vault["used_ids"].append(doc_hash)
        save_vault_data(vault)

        self.kyc_state_lbl.text = "[color=ffaa00]Step 1 పూర్తయింది. ఇప్పుడు Face Liveness Check చేయండి.[/color]"

    def start_face_scan(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        if not vault["users"][user].get("kyc_id_hash"):
            self.kyc_state_lbl.text = "[color=ff3333]ముందుగా ID సబ్మిట్ చేయండి![/color]"
            return

        self.scan_val = 0
        self.scan_bar.value = 0
        self.face_btn.text = "BIOMETRIC SCANNING..."
        self.face_btn.disabled = True
        self.scan_ticker = Clock.schedule_interval(self.step_scan_progress, 0.15)

    def step_scan_progress(self, dt):
        self.scan_val += 10
        self.scan_bar.value = self.scan_val
        if self.scan_val == 30:
            self.kyc_state_lbl.text = "[color=00e5ff]>> 3D Mesh: ముఖాన్ని గుర్తిస్తోంది...[/color]"
        elif self.scan_val == 70:
            self.kyc_state_lbl.text = "[color=00e5ff]>> Anti-Spoof: లైవ్‌నెస్ ధృవీకరిస్తోంది...[/color]"
        elif self.scan_val >= 100:
            if self.scan_ticker:
                self.scan_ticker.cancel()
            vault = get_vault_data()
            user = vault.get("current_session")
            vault["users"][user]["kyc_status"] = "Verified"
            save_vault_data(vault)

            self.face_btn.text = "FACE VERIFIED ✓"
            self.kyc_state_lbl.text = "[color=00ff66]అభినందనలు! పూర్తి కేవైసీ పూర్తయింది.[/color]"
            self.sync_screen()

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='right' if target_screen == "mining_screen" else 'left')
        self.manager.current = target_screen
        if target_screen == "mining_screen":
            self.manager.get_screen("mining_screen").sync_screen()
        elif target_screen == "stats_screen":
            self.manager.get_screen("stats_screen").sync_screen()


# -------------------- 4. GLOBAL STATS SCREEN --------------------
class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[16, 14, 16, 8], spacing=10)

        title = Label(
            text="[b][color=00e5ff]GLOBAL NETWORK METRICS[/color][/b]",
            markup=True,
            font_size='18sp',
            size_hint=(1, None),
            height=28
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[8, 8, 8, 8])
        box.bind(minimum_height=box.setter('height'))

        self.nodes_lbl = Label(text="Active Nodes: 14,210", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        self.hash_lbl = Label(text="Network Compute: 512.4 TH/s", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        self.blks_lbl = Label(text="Verified Research Blocks: 218,490", markup=True, font_size='13sp', size_hint=(1, None), height=26)
        fee_info = Label(text="[color=8892b0]Founder Solana Reserve Active: Multi-Sig Locked[/color]", markup=True, font_size='11sp', size_hint=(1, None), height=24)
        ver_info = Label(text=f"[color=64ffda]Core Engine Build: v{CURRENT_CLIENT_VERSION}[/color]", markup=True, font_size='11sp', size_hint=(1, None), height=24)

        box.add_widget(self.nodes_lbl)
        box.add_widget(self.hash_lbl)
        box.add_widget(self.blks_lbl)
        box.add_widget(fee_info)
        box.add_widget(ver_info)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Bar
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.navigate_to("mining_screen"))
        n_wall = Button(text="Barat Wallet", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.navigate_to("wallet_screen"))
        n_stat = Button(text="Stats", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        stats = vault.get("global_stats", {})
        self.nodes_lbl.text = f"[color=ccd6f6]Active Nodes: [b]{stats.get('total_nodes', 14210):,}[/b][/color]"
        self.hash_lbl.text = f"[color=64ffda]Network Compute: [b]{stats.get('network_hashrate', '512.4 TH/s')}[/b][/color]"
        self.blks_lbl.text = f"[color=ccd6f6]Verified Research Blocks: [b]{stats.get('total_blocks', 218490):,}[/b][/color]"

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = target_screen
        if target_screen == "mining_screen":
            self.manager.get_screen("mining_screen").sync_screen()
        elif target_screen == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_screen()


# -------------------- MAIN CONTROLLER & AUTO UPDATE CHECK --------------------
class BaratCoreApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthScreen(name="auth_screen"))
        sm.add_widget(MiningScreen(name="mining_screen"))
        sm.add_widget(WalletScreen(name="wallet_screen"))
        sm.add_widget(StatsScreen(name="stats_screen"))

        vault = get_vault_data()

        # Check for Remote Update
        remote = vault.get("remote_update", {})
        if remote.get("update_available", False) and remote.get("latest_version") != CURRENT_CLIENT_VERSION:
            auth = sm.get_screen("auth_screen")
            auth.update_banner.text = f"[color=ffaa00]★ Update Alert: New Core v{remote.get('latest_version')} Ready![/color]"

        if vault.get("current_session") and vault["current_session"] in vault["users"]:
            sm.current = "mining_screen"
            sm.get_screen("mining_screen").sync_screen()
        else:
            sm.current = "auth_screen"

        return sm


if __name__ == "__main__":
    BaratCoreApp().run()
