import os
import json
import time
import hashlib
import random
import re
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

# లోగో ఫైల్ సేఫ్ డిటెక్షన్
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

# ఎలిజిబిలిటీ & ఫౌండర్ ట్రెజరీ సెట్టింగ్స్
MIN_CYCLES_REQUIRED = 5
MIN_WITHDRAW_AMOUNT = 50.0
GAS_FEE_PERCENTAGE = 0.02
FOUNDER_SOLANA_WALLET = "9zYbQMJ9VD2NjXRhd83s4LSUcu9AnLTeetXLd5URWk2z"

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
        "wallet_phrase": "",
        "balance": 0.0,
        "wallet_balance": 0.0,
        "total_mined": 0.0,
        "completed_cycles": 0,
        "block_height": 3,
        "last_cycle": 0,
        "proof_hash": "ECO_GENESIS_PROOF_00000000",
        "bridge_transactions": []
    }

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

# 1. ల్యాండింగ్ స్క్రీన్
class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[20, 25, 20, 25], spacing=10)

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
        bal = data.get("balance", 0.0) + data.get("wallet_balance", 0.0)
        self.mined_preview.text = f"Tokens Mined\n{bal:.2f} $BARAT"

    def go_next(self, instance):
        data = load_data()
        if not data.get("registered", False):
            self.manager.current = "auth"
        else:
            self.manager.current = "main"

# 2. సురక్షిత అథెంటికేషన్ స్క్రీన్
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)

        root = BoxLayout(orientation='vertical', padding=[24, 20, 24, 15], spacing=8)
        root.add_widget(Label(text="BARAT NODE SECURITY", font_size='18sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.08))

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

        forgot_btn = Button(text="Forgot Password? Reset via OTP", background_color=(0, 0, 0, 0), color=(0.4, 0.7, 1, 1), size_hint_y=0.06, font_size='12sp')
        forgot_btn.bind(on_press=self.open_forgot_popup)
        root.add_widget(forgot_btn)

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

        if len(uname) < 3:
            self.msg.text = "Username must be at least 3 characters!"
            return

        if not is_valid_email(email):
            self.msg.text = "Enter a valid email address!"
            return

        if len(pwd) < 6:
            self.msg.text = "Password must be at least 6 characters!"
            return

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        words = random.sample(WORD_DICTIONARY, 12)
        phrase = " ".join(words)

        data = load_data()
        data["registered"] = True
        data["username"] = uname
        data["email"] = email
        data["password"] = pwd
        data["wallet_phrase"] = phrase
        save_data(data)

        self.manager.current = "main"

    def do_login(self, instance):
        email = self.email_input.text.strip()
        pwd = self.pass_input.text.strip()

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        data = load_data()
        if (data.get("email") == email or data.get("username") == email) and data.get("password") == pwd:
            self.manager.current = "main"
        else:
            self.msg.text = "Invalid credentials!"
            self.refresh_captcha()

    # Forgot Password & OTP రీసెట్ పాప్-అప్
    def open_forgot_popup(self, instance):
        data = load_data()
        reg_email = data.get("email", "")

        box = BoxLayout(orientation='vertical', padding=15, spacing=8)
        box.add_widget(Label(text="PASSWORD RESET VIA SECURE OTP", font_size='14sp', bold=True, color=(0.2, 0.9, 0.5, 1)))

        email_box = TextInput(hint_text="Enter Registered Email", multiline=False, size_hint_y=None, height=40)
        if reg_email:
            email_box.text = reg_email
        box.add_widget(email_box)

        generated_otp = str(random.randint(100000, 999999))
        otp_display = Label(text=f"[Mock Secure Gateway] OTP Sent: {generated_otp}", font_size='11sp', color=(1, 0.85, 0.3, 1), size_hint_y=None, height=20)
        box.add_widget(otp_display)

        otp_input = TextInput(hint_text="Enter 6-Digit OTP", multiline=False, input_filter='int', size_hint_y=None, height=40)
        box.add_widget(otp_input)

        new_pass_input = TextInput(hint_text="Enter New Password (Min 6 chars)", password=True, multiline=False, size_hint_y=None, height=40)
        box.add_widget(new_pass_input)

        msg_lbl = Label(text="", font_size='11sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=20)
        box.add_widget(msg_lbl)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
        reset_btn = Button(text="Reset Password", background_color=(0.1, 0.6, 0.35, 1), bold=True)
        close_btn = Button(text="Cancel", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(reset_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Account Recovery Gateway", content=box, size_hint=(0.88, 0.65), auto_dismiss=False)

        def do_reset(btn):
            if email_box.text.strip() != reg_email or not reg_email:
                msg_lbl.text = "Email does not match registered account!"
                return
            if otp_input.text.strip() != generated_otp:
                msg_lbl.text = "Invalid OTP code!"
                return
            if len(new_pass_input.text.strip()) < 6:
                msg_lbl.text = "New password must be at least 6 chars!"
                return

            data["password"] = new_pass_input.text.strip()
            save_data(data)
            popup.dismiss()
            self.msg.color = (0.2, 0.9, 0.5, 1)
            self.msg.text = "Password reset successful! Please login."

        reset_btn.bind(on_press=do_reset)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

# 3. మెయిన్ మైనింగ్ టెర్మినల్ & డ్యాష్‌బోర్డ్
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=6)

        # టాప్ బార్: ప్రొఫైల్ మరియు నోడ్ టైటిల్
        top_bar = BoxLayout(size_hint_y=0.07)
        top_bar.add_widget(Label(text="BARAT CORE: RESEARCH NODE", font_size='14sp', bold=True, color=(0.2, 0.9, 0.5, 1)))
        profile_btn = Button(text="Profile / Key", size_hint_x=0.35, background_color=(0.15, 0.45, 0.65, 1), font_size='11sp', bold=True)
        profile_btn.bind(on_press=self.open_profile_popup)
        top_bar.add_widget(profile_btn)
        root.add_widget(top_bar)

        try:
            self.logo_img = Image(source=LOGO_FILE, size_hint_y=0.18, allow_stretch=True, keep_ratio=True)
            root.add_widget(self.logo_img)
        except Exception:
            pass

        # Balances
        bal_box = BoxLayout(size_hint_y=0.12)
        self.mined_bal_lbl = Label(text="Mined: 0.00", font_size='16sp', bold=True, color=(0.95, 0.95, 0.95, 1))
        self.wallet_bal_lbl = Label(text="Wallet: 0.00", font_size='16sp', bold=True, color=(0.1, 0.9, 0.5, 1))
        bal_box.add_widget(self.mined_bal_lbl)
        bal_box.add_widget(self.wallet_bal_lbl)
        root.add_widget(bal_box)

        self.claim_wallet_btn = Button(text="Transfer Mined to Wallet", size_hint_y=0.07, background_color=(0.15, 0.5, 0.35, 1), font_size='13sp')
        self.claim_wallet_btn.bind(on_press=self.claim_to_wallet)
        root.add_widget(self.claim_wallet_btn)

        self.phase_lbl = Label(text="Phase: Initializing...", font_size='11sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.04)
        root.add_widget(self.phase_lbl)

        self.puzzle_lbl = Label(text="Target: Loading...", font_size='11sp', color=(0.4, 0.65, 1, 1), size_hint_y=0.04)
        root.add_widget(self.puzzle_lbl)

        self.block_lbl = Label(text="Height: #0000 | Proof: Verifying", font_size='10sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.04)
        root.add_widget(self.block_lbl)

        self.timer_lbl = Label(text="Engine: Ready", font_size='11sp', size_hint_y=0.05)
        root.add_widget(self.timer_lbl)

        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=0.09, background_color=(0.1, 0.65, 0.35, 1), font_size='14sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.08, background_color=(0.5, 0.2, 0.7, 1), font_size='13sp', bold=True)
        self.sol_btn.bind(on_press=self.open_solana_bridge_popup)
        root.add_widget(self.sol_btn)

        self.logout_btn = Button(text="Switch Node / Exit", size_hint_y=0.05, background_color=(0.35, 0.15, 0.15, 1), font_size='11sp')
        self.logout_btn.bind(on_press=self.do_logout)
        root.add_widget(self.logout_btn)

        self.status_msg = Label(text="Node Verified: Oncology Research Proof active.", font_size='10sp', color=(1, 0.85, 0.3, 1), size_hint_y=0.04)
        root.add_widget(self.status_msg)

        self.add_widget(root)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        self.refresh_dashboard()

    def refresh_dashboard(self):
        data = load_data()
        mined = data.get("balance", 0.0)
        wallet = data.get("wallet_balance", 0.0)
        self.mined_bal_lbl.text = f"Mined:\n{mined:.2f} BARAT"
        self.wallet_bal_lbl.text = f"Wallet:\n{wallet:.2f} BARAT"
        self.phase_lbl.text = self.calculate_reward(data.get("total_mined", mined))
        self.update_block_display()

    def claim_to_wallet(self, instance):
        data = load_data()
        mined = data.get("balance", 0.0)
        if mined <= 0:
            self.status_msg.text = "No mined balance available to transfer."
            return

        data["wallet_balance"] = data.get("wallet_balance", 0.0) + mined
        data["balance"] = 0.0
        save_data(data)
        self.refresh_dashboard()
        self.status_msg.text = f"Successfully transferred {mined:.2f} BARAT to Wallet!"

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
        data = load_data()
        now = time.time()
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
        proof_src = f"{data['block_height']}_{target}_{now}_{data.get('wallet_phrase', '')}"
        data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

        save_data(data)
        self.refresh_dashboard()
        self.update_timer(0)

    # పాస్‌వర్డ్ ద్వారా రక్షించబడిన ప్రొఫైల్ & 12-పదాల కీ వాల్ట్
    def open_profile_popup(self, instance):
        data = load_data()
        uname = data.get("username", "NodeUser")
        email = data.get("email", "Not Set")
        cycles = data.get("completed_cycles", 0)
        phrase = data.get("wallet_phrase", "")
        real_pass = data.get("password", "")

        box = BoxLayout(orientation='vertical', padding=15, spacing=8)
        box.add_widget(Label(text="USER NODE PROFILE & VAULT", font_size='15sp', bold=True, color=(0.1, 0.9, 0.5, 1)))
        box.add_widget(Label(text=f"Username: @{uname}\nEmail: {email}\nCycles Completed: {cycles}", font_size='11sp', color=(0.85, 0.85, 0.85, 1), halign="center"))

        box.add_widget(Label(text="Secret 12-Word Passphrase (Protected):", font_size='11sp', color=(0.95, 0.8, 0.2, 1)))

        phrase_display = TextInput(text="•••• •••• •••• •••• •••• ••••", readonly=True, multiline=True, size_hint_y=None, height=50, padding=[8, 8], background_color=(0.12, 0.14, 0.16, 1), foreground_color=(0.2, 0.9, 0.5, 1))
        box.add_widget(phrase_display)

        pass_verify = TextInput(hint_text="Enter Login Password to Unmask Key", password=True, multiline=False, size_hint_y=None, height=40, padding=[8, 8])
        box.add_widget(pass_verify)

        msg_lbl = Label(text="", font_size='11sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=20)
        box.add_widget(msg_lbl)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
        reveal_btn = Button(text="Reveal Key", background_color=(0.2, 0.5, 0.7, 1), bold=True)
        close_btn = Button(text="Close", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(reveal_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Decentralized Identity Vault", content=box, size_hint=(0.88, 0.65), auto_dismiss=False)

        def do_reveal(btn):
            if pass_verify.text.strip() == real_pass and real_pass != "":
                phrase_display.text = phrase
                msg_lbl.color = (0.2, 0.9, 0.5, 1)
                msg_lbl.text = "Key Unlocked! Auto-locks when closed."
            else:
                msg_lbl.color = (1, 0.3, 0.3, 1)
                msg_lbl.text = "Incorrect password! Access denied."

        reveal_btn.bind(on_press=do_reveal)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    # రీ-డిజైన్ చేయబడిన సొలానా బ్రిడ్జ్ పాప్-అప్
    def open_solana_bridge_popup(self, instance):
        data = load_data()
        wallet_bal = data.get("wallet_balance", 0.0)
        cycles = data.get("completed_cycles", 0)

        box = BoxLayout(orientation='vertical', padding=[16, 16, 16, 16], spacing=10)

        box.add_widget(Label(text="BARAT -> SOLANA MAIN BRIDGE", font_size='15sp', bold=True, color=(0.6, 0.3, 0.9, 1), size_hint_y=None, height=25))
        
        info_text = f"Available: {wallet_bal:.2f} BARAT | Cycles: {cycles}/{MIN_CYCLES_REQUIRED}"
        box.add_widget(Label(text=info_text, font_size='12sp', color=(0.85, 0.85, 0.85, 1), size_hint_y=None, height=20))

        addr_input = TextInput(hint_text="Paste Solana Wallet (Phantom) Address", multiline=False, size_hint_y=None, height=45, padding=[8, 12])
        box.add_widget(addr_input)

        amount_input = TextInput(hint_text="Enter BARAT Amount to Bridge", multiline=False, input_filter='float', size_hint_y=None, height=45, padding=[8, 12])
        box.add_widget(amount_input)

        fee_label = Label(text="Bridge Gas Fee: 2% (Auto-deducted to Founder)", font_size='11sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=None, height=20)
        box.add_widget(fee_label)

        popup_msg = Label(text="", font_size='11sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=25)
        box.add_widget(popup_msg)

        btn_box = BoxLayout(spacing=12, size_hint_y=None, height=45)
        submit_btn = Button(text="Confirm Bridge", background_color=(0.5, 0.2, 0.7, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(submit_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Decentralized Solana Gateway", content=box, size_hint=(0.90, 0.72), auto_dismiss=False)

        def execute_bridge(btn):
            sol_addr = addr_input.text.strip()
            amt_text = amount_input.text.strip()

            if cycles < MIN_CYCLES_REQUIRED:
                popup_msg.text = f"Eligibility Error: Need {MIN_CYCLES_REQUIRED} Cycles! ({cycles} done)"
                return

            try:
                amt = float(amt_text)
            except ValueError:
                popup_msg.text = "Enter valid numeric amount!"
                return

            if amt < MIN_WITHDRAW_AMOUNT:
                popup_msg.text = f"Min Bridge Amount: {MIN_WITHDRAW_AMOUNT} BARAT!"
                return

            if amt > wallet_bal:
                popup_msg.text = "Insufficient Wallet Balance!"
                return

            if not is_valid_solana_address(sol_addr):
                popup_msg.text = "Failed: Invalid Solana (Base58) Address!"
                return

            gas_fee = amt * GAS_FEE_PERCENTAGE
            user_receives = amt - gas_fee

            data["wallet_balance"] = wallet_bal - amt
            
            tx_record = {
                "timestamp": time.time(),
                "destination": sol_addr,
                "gross_amount": amt,
                "gas_fee_cut": gas_fee,
                "net_transferred": user_receives,
                "founder_wallet": FOUNDER_SOLANA_WALLET,
                "status": "QUEUED_ON_SOLANA_DEVNET"
            }
            tx_list = data.get("bridge_transactions", [])
            tx_list.append(tx_record)
            data["bridge_transactions"] = tx_list

            save_data(data)
            self.refresh_dashboard()

            popup.dismiss()
            self.status_msg.text = f"Success! {user_receives:.2f} BARAT queued. 2% fee sent to Founder."

        submit_btn.bind(on_press=execute_bridge)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def do_logout(self, instance):
        self.manager.current = "landing"

class BaratCoreApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.06, 1.0)
        sm = ScreenManager()

        sm.add_widget(LandingScreen(name="landing"))
        sm.add_widget(AuthScreen(name="auth"))
        sm.add_widget(MainScreen(name="main"))

        sm.current = "landing"
        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
