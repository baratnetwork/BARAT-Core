import os
import json
import time
import hashlib
import random
import re
import urllib.request
import urllib.error
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.resources import resource_find, resource_add_path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
resource_add_path(BASE_DIR)

if os.path.exists(os.path.join(BASE_DIR, "icon.png")):
    LOGO_FILE = os.path.join(BASE_DIR, "icon.png")
elif os.path.exists(os.path.join(BASE_DIR, "icon.png.png")):
    LOGO_FILE = os.path.join(BASE_DIR, "icon.png.png")
else:
    LOGO_FILE = resource_find("icon.png") or "icon.png"

DATA_FILE = "barat_data.json"
HALVING_INTERVAL = 5250000.0
BLOCK_REWARD_INITIAL = 10.0
CYCLE_HOURS = 24

MIN_CYCLES_REQUIRED = 5
MIN_WITHDRAW_AMOUNT = 50.0
GAS_FEE_PERCENTAGE = 0.02
FOUNDER_SOLANA_WALLET = "9zYbQMJ9VD2NjXRhd83s4LSUcu9AnLTeetXLd5URWk2z"

# GitHub Cloud Sync Credentials
GITHUB_USER = "sudheerkirandora"
GITHUB_TOKEN = "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"
GIST_DESCRIPTION = "BARAT_CORE_NETWORK_CLOUD_LEDGER"

CANCER_TARGETS = [
    "KRAS-G12D-Target-Model-X7",
    "MYC-Oncogene-Transcription-L3",
    "TP53-Binding-Conformation-V2",
    "EGFR-Exon20-Kinase-Domain-Z9",
    "BRCA1-DNA-Repair-Fold-Alpha"
]

WORD_DICTIONARY = [
    "alpha", "bravo", "cancer", "decode", "energy", "future", 
    "genome", "health", "immune", "jupiter", "kinase", "logic", 
    "matrix", "neural", "oxygen", "protein", "quantum", "repair", 
    "solana", "target", "ultra", "vector", "wallet", "xenon"
]

def get_server_time():
    try:
        req = urllib.request.Request("https://api.github.com", headers={"User-Agent": "BaratCoreApp"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            date_str = resp.headers.get('Date')
            if date_str:
                return time.mktime(time.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT"))
    except Exception:
        pass
    return time.time()

def sync_to_github_cloud(data):
    def run_sync():
        try:
            url = "https://api.github.com/gists"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "BaratCoreApp"
            }
            gist_id = data.get("cloud_gist_id", "")
            payload = {
                "description": GIST_DESCRIPTION,
                "public": False,
                "files": {
                    f"{data.get('username', 'node')}_backup.json": {
                        "content": json.dumps(data)
                    }
                }
            }
            json_bytes = json.dumps(payload).encode('utf-8')
            if gist_id:
                patch_url = f"{url}/{gist_id}"
                req = urllib.request.Request(patch_url, data=json_bytes, headers=headers, method="PATCH")
            else:
                req = urllib.request.Request(url, data=json_bytes, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "id" in res_data:
                    data["cloud_gist_id"] = res_data["id"]
                    save_local_only(data)
        except Exception:
            pass
    threading.Thread(target=run_sync, daemon=True).start()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_solana_address(addr):
    if not (32 <= len(addr) <= 44):
        return False
    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]+$'
    return bool(re.match(base58_pattern, addr))

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "registered": False,
        "username": "",
        "email": "",
        "password": "",
        "wallets": [],
        "active_wallet_index": 0,
        "balance": 0.0,
        "total_mined": 0.0,
        "completed_cycles": 0,
        "block_height": 3,
        "last_cycle": 0,
        "proof_hash": "ECO_GENESIS_PROOF_00000000",
        "kyc_status": "Not Verified (Unlocks at 5 Cycles)",
        "cloud_gist_id": "",
        "bridge_transactions": []
    }

def save_local_only(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def save_data(data):
    save_local_only(data)
    sync_to_github_cloud(data)

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=10)

        try:
            logo = Image(source=LOGO_FILE, size_hint_y=0.45, allow_stretch=True, keep_ratio=True)
            root.add_widget(logo)
        except Exception:
            pass

        root.add_widget(Label(
            text="PROOF OF INTELLIGENCE\nSUSTAINABLE MOBILE MINING",
            font_size='14sp',
            bold=True,
            halign="center",
            color=(0.85, 0.75, 0.45, 1),
            size_hint_y=0.12
        ))

        self.mined_preview = Label(
            text="Tokens Mined\n0.00 $BARAT",
            font_size='15sp',
            halign="center",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.12
        )
        root.add_widget(self.mined_preview)

        start_btn = Button(
            text="START",
            size_hint=(None, None),
            size=('130dp', '130dp'),
            pos_hint={'center_x': 0.5},
            background_color=(0.1, 0.7, 0.4, 1),
            font_size='22sp',
            bold=True
        )
        start_btn.bind(on_press=self.go_next)
        root.add_widget(start_btn)

        root.add_widget(Label(text="", size_hint_y=0.06))
        self.add_widget(root)

    def on_enter(self):
        data = load_data()
        tot = data.get("balance", 0.0)
        for w in data.get("wallets", []):
            tot += w.get("balance", 0.0)
        self.mined_preview.text = f"Tokens Mined\n{tot:.2f} $BARAT"

    def go_next(self, instance):
        data = load_data()
        if not data.get("registered", False):
            self.manager.current = "auth"
        else:
            self.manager.current = "main"

class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)

        root = BoxLayout(orientation='vertical', padding=[24, 20, 24, 15], spacing=8)
        root.add_widget(Label(text="BARAT NODE SECURITY", font_size='18sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.09))

        self.user_input = TextInput(hint_text="Username (e.g. barat_node1)", multiline=False, size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.user_input)

        self.email_input = TextInput(hint_text="Valid Email (e.g. name@gmail.com)", multiline=False, size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.email_input)

        self.pass_input = TextInput(hint_text="Password (Min 6 characters)", password=True, multiline=False, size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.pass_input)

        self.captcha_lbl = Label(text=f"Human Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.06)
        root.add_widget(self.captcha_lbl)

        self.captcha_input = TextInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.3, 0.3, 1), size_hint_y=0.06)
        root.add_widget(self.msg)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.11)
        reg_btn = Button(text="Register & Mine", background_color=(0.1, 0.55, 0.35, 1), bold=True)
        reg_btn.bind(on_press=self.do_register)
        login_btn = Button(text="Login", background_color=(0.2, 0.45, 0.7, 1), bold=True)
        login_btn.bind(on_press=self.do_login)
        btn_box.add_widget(reg_btn)
        btn_box.add_widget(login_btn)
        root.add_widget(btn_box)

        self.add_widget(root)

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Human Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_register(self, instance):
        uname = self.user_input.text.strip()
        email = self.email_input.text.strip()
        pwd = self.pass_input.text.strip()

        if len(uname) < 3 or not is_valid_email(email) or len(pwd) < 6:
            self.msg.text = "Invalid details provided!"
            return

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        data = load_data()
        data["registered"] = True
        data["username"] = uname
        data["email"] = email
        data["password"] = pwd
        save_data(data)
        self.manager.current = "main"

    def do_login(self, instance):
        ident = self.user_input.text.strip() or self.email_input.text.strip()
        pwd = self.pass_input.text.strip()

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        data = load_data()
        if (data.get("email") == ident or data.get("username") == ident) and data.get("password") == pwd:
            self.manager.current = "main"
        else:
            self.msg.text = "Invalid credentials!"
            self.refresh_captcha()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[16, 10, 16, 10], spacing=5)

        top_bar = BoxLayout(size_hint_y=0.07, spacing=6)
        top_bar.add_widget(Label(text="BARAT CORE NODE", font_size='13sp', bold=True, color=(0.2, 0.9, 0.5, 1)))
        
        wallet_mgr_btn = Button(text="Wallets", size_hint_x=0.28, background_color=(0.2, 0.5, 0.7, 1), font_size='11sp', bold=True)
        wallet_mgr_btn.bind(on_press=self.open_wallet_manager_popup)
        top_bar.add_widget(wallet_mgr_btn)

        profile_btn = Button(text="Profile", size_hint_x=0.28, background_color=(0.15, 0.45, 0.65, 1), font_size='11sp', bold=True)
        profile_btn.bind(on_press=self.open_profile_popup)
        top_bar.add_widget(profile_btn)
        root.add_widget(top_bar)

        try:
            self.logo_img = Image(source=LOGO_FILE, size_hint_y=0.17, allow_stretch=True, keep_ratio=True)
            root.add_widget(self.logo_img)
        except Exception:
            pass

        bal_box = BoxLayout(size_hint_y=0.11)
        self.mined_bal_lbl = Label(text="Mined: 0.00", font_size='14sp', bold=True, color=(0.95, 0.95, 0.95, 1))
        self.active_wallet_lbl = Label(text="Active: None\nBal: 0.00", font_size='13sp', bold=True, color=(0.1, 0.9, 0.5, 1), halign="center")
        bal_box.add_widget(self.mined_bal_lbl)
        bal_box.add_widget(self.active_wallet_lbl)
        root.add_widget(bal_box)

        self.claim_wallet_btn = Button(text="Claim Mined to Active Wallet", size_hint_y=0.07, background_color=(0.15, 0.5, 0.35, 1), font_size='12sp')
        self.claim_wallet_btn.bind(on_press=self.claim_to_active_wallet)
        root.add_widget(self.claim_wallet_btn)

        self.phase_lbl = Label(text="Phase: Initializing...", font_size='11sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.04)
        root.add_widget(self.phase_lbl)

        self.puzzle_lbl = Label(text="Target: Loading...", font_size='11sp', color=(0.4, 0.65, 1, 1), size_hint_y=0.04)
        root.add_widget(self.puzzle_lbl)

        self.block_lbl = Label(text="Height: #0000 | Proof: Verifying", font_size='10sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        root.add_widget(self.block_lbl)

        self.timer_lbl = Label(text="Engine: Ready", font_size='11sp', size_hint_y=0.05)
        root.add_widget(self.timer_lbl)

        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=0.09, background_color=(0.1, 0.65, 0.35, 1), font_size='13sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.08, background_color=(0.5, 0.2, 0.7, 1), font_size='12sp', bold=True)
        self.sol_btn.bind(on_press=self.open_solana_bridge_popup)
        root.add_widget(self.sol_btn)

        self.logout_btn = Button(text="Switch Node / Exit", size_hint_y=0.05, background_color=(0.35, 0.15, 0.15, 1), font_size='11sp')
        self.logout_btn.bind(on_press=self.do_logout)
        root.add_widget(self.logout_btn)

        self.status_msg = Label(text="Cloud Engine Synchronized.", font_size='10sp', color=(1, 0.85, 0.3, 1), size_hint_y=0.04)
        root.add_widget(self.status_msg)

        self.add_widget(root)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        self.refresh_dashboard()

    def get_active_wallet(self, data):
        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        if wallets and 0 <= idx < len(wallets):
            return wallets[idx]
        return None

    def refresh_dashboard(self):
        data = load_data()
        mined = data.get("balance", 0.0)
        self.mined_bal_lbl.text = f"Mined:\n{mined:.2f} BARAT"

        active = self.get_active_wallet(data)
        if active:
            w_name = active.get("name", "Wallet")
            w_bal = active.get("balance", 0.0)
            self.active_wallet_lbl.text = f"Active: {w_name}\nBal: {w_bal:.2f} BARAT"
        else:
            self.active_wallet_lbl.text = "Active: None\n(Create in Wallets)"

        self.phase_lbl.text = self.calculate_reward(data.get("total_mined", mined))
        self.update_block_display()

    def claim_to_active_wallet(self, instance):
        data = load_data()
        mined = data.get("balance", 0.0)
        if mined <= 0:
            self.status_msg.text = "No mined balance available."
            return

        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        if not wallets or idx >= len(wallets):
            self.status_msg.text = "Please select/create a wallet first!"
            return

        wallets[idx]["balance"] = wallets[idx].get("balance", 0.0) + mined
        data["balance"] = 0.0
        data["wallets"] = wallets
        save_data(data)
        self.refresh_dashboard()
        self.status_msg.text = f"Transferred to {wallets[idx]['name']}!"

    def calculate_reward(self, total_mined):
        phase = int(total_mined // HALVING_INTERVAL) + 1
        reward = BLOCK_REWARD_INITIAL / (2 ** (phase - 1))
        return f"Phase {phase}: Genesis ({reward:.1f} BARAT/cycle)"

    def update_block_display(self):
        data = load_data()
        height = data.get("block_height", 3)
        target = CANCER_TARGETS[height % len(CANCER_TARGETS)]
        self.puzzle_lbl.text = f"Research Target: {target}"
        self.block_lbl.text = f"Block Height: #{height} | Cycles: {data.get('completed_cycles', 0)}"

    def update_timer(self, dt):
        data = load_data()
        last_cycle = data.get("last_cycle", 0)
        now = time.time()
        cooldown = CYCLE_HOURS * 3600
        elapsed = now - last_cycle

        if elapsed >= cooldown:
            self.timer_lbl.text = "Node Engine: Ready to Solve Block"
            self.timer_lbl.color = (0.2, 0.9, 0.5, 1)
            self.mine_btn.disabled = False
            self.mine_btn.background_color = (0.1, 0.65, 0.35, 1)
        else:
            rem = int(cooldown - elapsed)
            hrs = rem // 3600
            mins = (rem % 3600) // 60
            secs = rem % 60
            self.timer_lbl.text = f"Next Block In: {hrs:02d}h {mins:02d}m {secs:02d}s"
            self.timer_lbl.color = (0.85, 0.85, 0.85, 1)
            self.mine_btn.disabled = True
            self.mine_btn.background_color = (0.2, 0.25, 0.25, 1)

    def start_mining(self, instance):
        now = get_server_time()
        data = load_data()
        cooldown = CYCLE_HOURS * 3600
        if (now - data.get("last_cycle", 0)) < cooldown:
            return

        total_mined = data.get("total_mined", 0.0)
        phase = int(total_mined // HALVING_INTERVAL) + 1
        reward = BLOCK_REWARD_INITIAL / (2 ** (phase - 1))

        data["balance"] = data.get("balance", 0.0) + reward
        data["total_mined"] = total_mined + reward
        data["block_height"] = data.get("block_height", 3) + 1
        data["completed_cycles"] = data.get("completed_cycles", 0) + 1
        data["last_cycle"] = now

        target = CANCER_TARGETS[data["block_height"] % len(CANCER_TARGETS)]
        proof_src = f"{data['block_height']}_{target}_{now}"
        data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

        save_data(data)
        self.refresh_dashboard()
        self.update_timer(0)

    def open_wallet_manager_popup(self, instance):
        data = load_data()
        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="MULTI-WALLET CONTROL CENTER", font_size='14sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.11))

        active_info = "No active wallet. Create or import below."
        if wallets and 0 <= idx < len(wallets):
            active_info = f"Current Active: {wallets[idx]['name']} (Bal: {wallets[idx].get('balance',0.0):.2f})"
        box.add_widget(Label(text=active_info, font_size='11sp', color=(0.85, 0.85, 0.85, 1), size_hint_y=0.09))

        w_summary = "Wallets: " + (", ".join([f"{w['name']}" for w in wallets]) if wallets else "Empty")
        box.add_widget(Label(text=w_summary, font_size='10sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.08))

        create_btn = Button(text="+ Create New Wallet (Auto-Phrase)", size_hint_y=0.14, background_color=(0.1, 0.6, 0.35, 1), font_size='11sp', bold=True)
        import_btn = Button(text="Import Wallet via 12-Word Key", size_hint_y=0.14, background_color=(0.2, 0.45, 0.7, 1), font_size='11sp', bold=True)
        switch_btn = Button(text="Switch Active Wallet", size_hint_y=0.14, background_color=(0.5, 0.35, 0.2, 1), font_size='11sp')
        close_btn = Button(text="Done / Close", size_hint_y=0.14, background_color=(0.35, 0.15, 0.15, 1))

        box.add_widget(create_btn)
        box.add_widget(import_btn)
        box.add_widget(switch_btn)
        box.add_widget(close_btn)

        popup = Popup(title="Multi-Wallet Manager", content=box, size_hint=(0.92, 0.65), auto_dismiss=False)

        def do_create(btn):
            popup.dismiss()
            self.open_create_wallet_popup()

        def do_import(btn):
            popup.dismiss()
            self.open_import_wallet_popup()

        def do_switch(btn):
            if wallets:
                data["active_wallet_index"] = (idx + 1) % len(wallets)
                save_data(data)
                popup.dismiss()
                self.refresh_dashboard()

        create_btn.bind(on_press=do_create)
        import_btn.bind(on_press=do_import)
        switch_btn.bind(on_press=do_switch)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_create_wallet_popup(self):
        data = load_data()
        wallets = data.get("wallets", [])
        w_num = len(wallets) + 1
        new_name = f"Wallet {w_num}"
        phrase = " ".join(random.sample(WORD_DICTIONARY, 12))

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text=f"CREATING: {new_name}", font_size='14sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.12))
        phrase_box = TextInput(text=phrase, readonly=True, multiline=True, size_hint_y=0.25, padding=[6, 6])
        box.add_widget(phrase_box)

        confirm_btn = Button(text="Save & Activate", size_hint_y=0.16, background_color=(0.1, 0.6, 0.35, 1), bold=True)
        cancel_btn = Button(text="Cancel", size_hint_y=0.14, background_color=(0.4, 0.2, 0.2, 1))
        box.add_widget(confirm_btn)
        box.add_widget(cancel_btn)

        popup = Popup(title="New Key Vault", content=box, size_hint=(0.90, 0.58), auto_dismiss=False)

        def save_new_wallet(btn):
            wallets.append({"name": new_name, "phrase": phrase, "balance": 0.0})
            data["wallets"] = wallets
            data["active_wallet_index"] = len(wallets) - 1
            save_data(data)
            popup.dismiss()
            self.refresh_dashboard()

        confirm_btn.bind(on_press=save_new_wallet)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_import_wallet_popup(self):
        data = load_data()
        wallets = data.get("wallets", [])

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="IMPORT EXISTING WALLET", font_size='14sp', bold=True, color=(0.2, 0.6, 0.9, 1), size_hint_y=0.12))

        input_phrase = TextInput(hint_text="Enter 12 words", multiline=True, size_hint_y=0.25, padding=[6, 6])
        box.add_widget(input_phrase)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        import_btn = Button(text="Import", background_color=(0.15, 0.5, 0.7, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(import_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Import Seed Vault", content=box, size_hint=(0.90, 0.56), auto_dismiss=False)

        def do_import(btn):
            words = input_phrase.text.strip().split()
            if len(words) == 12:
                phrase = " ".join(words)
                wallets.append({"name": f"Wallet {len(wallets) + 1} (Imported)", "phrase": phrase, "balance": 0.0})
                data["wallets"] = wallets
                data["active_wallet_index"] = len(wallets) - 1
                save_data(data)
                popup.dismiss()
                self.refresh_dashboard()

        import_btn.bind(on_press=do_import)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_profile_popup(self, instance):
        data = load_data()
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=7)
        box.add_widget(Label(text="NODE PROFILE & KYC", font_size='14sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.15))
        box.add_widget(Label(text=f"Username: @{data.get('username')}\nEmail: {data.get('email')}", font_size='11sp', size_hint_y=0.2))
        
        close_btn = Button(text="Close", size_hint_y=0.15, background_color=(0.4, 0.2, 0.2, 1))
        box.add_widget(close_btn)

        popup = Popup(title="Node Identity Center", content=box, size_hint=(0.90, 0.50), auto_dismiss=False)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_solana_bridge_popup(self, instance):
        data = load_data()
        active = self.get_active_wallet(data)
        wallet_bal = active.get("balance", 0.0) if active else 0.0

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="BARAT -> SOLANA MAIN BRIDGE", font_size='14sp', bold=True, color=(0.6, 0.3, 0.9, 1), size_hint_y=0.12))
        
        addr_input = TextInput(hint_text="Paste Solana Wallet Address", multiline=False, size_hint_y=0.16, padding=[8, 8])
        amount_input = TextInput(hint_text="BARAT Amount", multiline=False, input_filter='float', size_hint_y=0.16, padding=[8, 8])
        box.add_widget(addr_input)
        box.add_widget(amount_input)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        submit_btn = Button(text="Confirm Bridge", background_color=(0.5, 0.2, 0.7, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(submit_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Solana Gateway", content=box, size_hint=(0.90, 0.58), auto_dismiss=False)

        def execute_bridge(btn):
            sol_addr = addr_input.text.strip()
            try:
                amt = float(amount_input.text.strip())
            except ValueError:
                return

            if active and amt <= wallet_bal and amt >= MIN_WITHDRAW_AMOUNT and is_valid_solana_address(sol_addr):
                gas_fee = amt * GAS_FEE_PERCENTAGE
                active["balance"] -= amt
                data.setdefault("bridge_transactions", []).append({
                    "timestamp": time.time(),
                    "destination": sol_addr,
                    "net_transferred": amt - gas_fee,
                    "founder_wallet": FOUNDER_SOLANA_WALLET
                })
                save_data(data)
                self.refresh_dashboard()
                popup.dismiss()

        submit_btn.bind(on_press=execute_bridge)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def do_logout(self, instance):
        self.manager.current = "landing"

class BaratCoreApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.06, 1.0)
        self.icon = LOGO_FILE
        sm = ScreenManager()
        sm.add_widget(LandingScreen(name="landing"))
        sm.add_widget(AuthScreen(name="auth"))
        sm.add_widget(MainScreen(name="main"))
        sm.current = "landing"
        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
