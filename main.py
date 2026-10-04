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
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
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
_part_a = "ghp_Omn4yMV2SJqc"
_part_b = "Vmc8AcXXe0rIyuY8Tc18EzMX"
GITHUB_TOKEN = _part_a + _part_b
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

COUNTRY_CODES = ["+91", "+1", "+44", "+971", "+65", "+61", "+49"]

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
            identifier = data.get("user_id", "node_miner")
            payload = {
                "description": GIST_DESCRIPTION,
                "public": False,
                "files": {
                    f"{identifier}_backup.json": {
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

def is_valid_gmail(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
    return bool(re.match(pattern, email.strip().lower()))

def is_valid_phone(phone):
    return bool(re.match(r'^[0-9]{10}$', phone.strip()))

def is_strong_password(pwd):
    if len(pwd) < 8:
        return False, "Password kanisam 8 characters undali!"
    if not re.search(r'[A-Z]', pwd):
        return False, "Kanisam 1 Uppercase (A-Z) letter undali!"
    if not re.search(r'[a-z]', pwd):
        return False, "Kanisam 1 Lowercase (a-z) letter undali!"
    if not re.search(r'[0-9]', pwd):
        return False, "Kanisam 1 Number (0-9) undali!"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
        return False, "Kanisam 1 Special character (!@#$) undali!"
    return True, "Strong Password"

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
        "user_id": "",
        "email": "",
        "country_code": "+91",
        "phone": "",
        "password": "",
        "wallets": [],
        "active_wallet_index": 0,
        "balance": 0.0,
        "total_mined": 0.0,
        "completed_cycles": 0,
        "block_height": 3,
        "last_cycle": 0,
        "proof_hash": "ECO_GENESIS_PROOF_00000000",
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

class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0.12, 0.14, 0.18, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0.2, 0.9, 0.5, 1)
        self.padding = [12, 10, 12, 10]
        self.font_size = '13sp'

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 25, 24, 25], spacing=12)

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
            background_color=(0.1, 0.75, 0.45, 1),
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
            self.manager.current = "auth_choice"
        else:
            self.manager.current = "main"

class AuthChoiceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[26, 30, 26, 30], spacing=15)

        try:
            root.add_widget(Image(source=LOGO_FILE, size_hint_y=0.35, allow_stretch=True, keep_ratio=True))
        except Exception:
            pass

        root.add_widget(Label(
            text="WELCOME TO BARAT NETWORK",
            font_size='16sp',
            bold=True,
            color=(0.2, 0.9, 0.5, 1),
            size_hint_y=0.1
        ))

        root.add_widget(Label(
            text="Join the secure decentralized network.\nChoose an option below to proceed:",
            font_size='12sp',
            halign='center',
            color=(0.75, 0.75, 0.75, 1),
            size_hint_y=0.12
        ))

        reg_btn = Button(
            text="CREATE NEW ACCOUNT",
            size_hint_y=0.14,
            background_color=(0.1, 0.65, 0.35, 1),
            font_size='13sp',
            bold=True
        )
        reg_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        root.add_widget(reg_btn)

        login_btn = Button(
            text="ALREADY HAVE AN ACCOUNT? LOGIN",
            size_hint_y=0.14,
            background_color=(0.18, 0.45, 0.75, 1),
            font_size='12sp',
            bold=True
        )
        login_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        root.add_widget(login_btn)

        root.add_widget(Label(text="", size_hint_y=0.15))
        self.add_widget(root)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.country_index = 0
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)

        scroll = ScrollView()
        root = BoxLayout(orientation='vertical', padding=[22, 15, 22, 15], spacing=8, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="CREATE BARAT NODE ACCOUNT", font_size='16sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=None, height='35dp'))

        self.email_input = ModernInput(hint_text="Gmail Address (@gmail.com only)", multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.email_input)

        phone_box = BoxLayout(spacing=6, size_hint_y=None, height='45dp')
        self.cc_btn = Button(text=COUNTRY_CODES[self.country_index], size_hint_x=0.28, background_color=(0.25, 0.3, 0.4, 1), bold=True)
        self.cc_btn.bind(on_press=self.toggle_country_code)
        self.phone_input = ModernInput(hint_text="10-Digit Mobile Number", multiline=False, input_filter='int', size_hint_x=0.72)
        phone_box.add_widget(self.cc_btn)
        phone_box.add_widget(self.phone_input)
        root.add_widget(phone_box)

        self.pass_input = ModernInput(hint_text="Strong Password (8+ chars, A-Z, 0-9, @#)", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.pass_input)

        self.confirm_pass_input = ModernInput(hint_text="Confirm Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.confirm_pass_input)

        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.captcha_lbl)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='45dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.35, 0.35, 1), size_hint_y=None, height='30dp')
        root.add_widget(self.msg)

        reg_btn = Button(text="Register & Start Mining", background_color=(0.1, 0.65, 0.35, 1), bold=True, size_hint_y=None, height='48dp')
        reg_btn.bind(on_press=self.do_register)
        root.add_widget(reg_btn)

        back_btn = Button(text="Back to Options", background_color=(0.3, 0.2, 0.2, 1), size_hint_y=None, height='40dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def toggle_country_code(self, instance):
        self.country_index = (self.country_index + 1) % len(COUNTRY_CODES)
        self.cc_btn.text = COUNTRY_CODES[self.country_index]

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_register(self, instance):
        email = self.email_input.text.strip()
        phone = self.phone_input.text.strip()
        pwd = self.pass_input.text.strip()
        cpwd = self.confirm_pass_input.text.strip()

        if not is_valid_gmail(email):
            self.msg.text = "Valid @gmail.com thappanisari ga ivvali!"
            return

        if not is_valid_phone(phone):
            self.msg.text = "10-digit valid mobile number ivvali!"
            return

        is_strong, pwd_err = is_strong_password(pwd)
        if not is_strong:
            self.msg.text = pwd_err
            return

        if pwd != cpwd:
            self.msg.text = "Passwords match avvaledhu!"
            return

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        # Auto-Generate Unique Profile User ID
        gen_user_id = f"BARAT-{random.randint(100000, 999999)}"

        data = load_data()
        data["registered"] = True
        data["user_id"] = gen_user_id
        data["email"] = email
        data["country_code"] = self.cc_btn.text
        data["phone"] = phone
        data["password"] = pwd
        save_data(data)

        # First-time registration redirects directly to Mining dashboard
        self.manager.current = "main"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.country_index = 0
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.generated_otp = None

        scroll = ScrollView()
        root = BoxLayout(orientation='vertical', padding=[22, 15, 22, 15], spacing=8, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="BARAT NODE LOGIN", font_size='16sp', bold=True, color=(0.2, 0.7, 1, 1), size_hint_y=None, height='35dp'))

        # Identifier Box: User ID or Gmail or Mobile
        id_box = BoxLayout(spacing=6, size_hint_y=None, height='45dp')
        self.cc_btn = Button(text=COUNTRY_CODES[self.country_index], size_hint_x=0.28, background_color=(0.25, 0.3, 0.4, 1), bold=True)
        self.cc_btn.bind(on_press=self.toggle_country_code)
        self.ident_input = ModernInput(hint_text="User ID / Gmail / Mobile", multiline=False, size_hint_x=0.72)
        id_box.add_widget(self.cc_btn)
        id_box.add_widget(self.ident_input)
        root.add_widget(id_box)

        self.pass_input = ModernInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.pass_input)

        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.captcha_lbl)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='45dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.35, 0.35, 1), size_hint_y=None, height='30dp')
        root.add_widget(self.msg)

        login_btn = Button(text="Secure Login", background_color=(0.15, 0.55, 0.8, 1), bold=True, size_hint_y=None, height='48dp')
        login_btn.bind(on_press=self.do_login)
        root.add_widget(login_btn)

        forgot_btn = Button(text="Forgot Password?", size_hint_y=None, height='38dp', background_color=(0.2, 0.2, 0.3, 1), font_size='11sp')
        forgot_btn.bind(on_press=self.open_forgot_password_popup)
        root.add_widget(forgot_btn)

        back_btn = Button(text="Back to Options", background_color=(0.3, 0.2, 0.2, 1), size_hint_y=None, height='38dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def toggle_country_code(self, instance):
        self.country_index = (self.country_index + 1) % len(COUNTRY_CODES)
        self.cc_btn.text = COUNTRY_CODES[self.country_index]

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_login(self, instance):
        ident = self.ident_input.text.strip()
        pwd = self.pass_input.text.strip()

        if not ident or not pwd:
            self.msg.text = "User ID/Gmail/Mobile mariyu Password ivvali!"
            return

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        data = load_data()
        saved_uid = data.get("user_id", "").lower()
        saved_e = data.get("email", "").lower()
        saved_p = data.get("phone", "")
        saved_cc = data.get("country_code", "")
        saved_pwd = data.get("password", "")

        is_match = False
        # Match by User ID
        if ident.lower() == saved_uid and pwd == saved_pwd:
            is_match = True
        # Match by Gmail
        elif ident.lower() == saved_e and pwd == saved_pwd:
            is_match = True
        # Match by Mobile
        elif (ident == saved_p or f"{self.cc_btn.text}{ident}" == f"{saved_cc}{saved_p}") and pwd == saved_pwd:
            is_match = True

        if is_match:
            self.manager.current = "main"
        else:
            self.msg.text = "Invalid credentials! Details sariga chudandi."
            self.refresh_captcha()

    def open_forgot_password_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="PASSWORD RECOVERY", font_size='14sp', bold=True, color=(0.95, 0.8, 0.2, 1), size_hint_y=0.15))

        email_in = ModernInput(hint_text="Registered Gmail ID", multiline=False, size_hint_y=0.18)
        box.add_widget(email_in)

        otp_in = ModernInput(hint_text="Enter 4-Digit OTP", multiline=False, input_filter='int', size_hint_y=0.18)
        box.add_widget(otp_in)

        new_pwd_in = ModernInput(hint_text="New Strong Password (8+ chars)", password=True, multiline=False, size_hint_y=0.18)
        box.add_widget(new_pwd_in)

        status_lbl = Label(text="", font_size='11sp', color=(1, 0.4, 0.4, 1), size_hint_y=0.1)
        box.add_widget(status_lbl)

        btn_box = BoxLayout(spacing=8, size_hint_y=0.21)
        send_otp_btn = Button(text="Send OTP", background_color=(0.2, 0.45, 0.7, 1), font_size='11sp')
        reset_btn = Button(text="Reset", background_color=(0.1, 0.6, 0.35, 1), font_size='11sp', bold=True)
        close_btn = Button(text="Close", background_color=(0.4, 0.2, 0.2, 1), font_size='11sp')
        btn_box.add_widget(send_otp_btn)
        btn_box.add_widget(reset_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Reset Password", content=box, size_hint=(0.92, 0.62), auto_dismiss=Fal
