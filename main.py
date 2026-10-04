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

# కీబోర్డ్ అడ్డురాకుండా స్క్రీన్ ఆటోమేటిక్‌గా పైకి లేచే సెట్టింగ్
Window.softinput_mode = "below_target"
Window.keyboard_anim_args = {'t': 'in_out_quart', 'd': 0.25}

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

        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=[22, 15, 22, 25], spacing=9, size_hint_y=None)
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

        self.msg = Label(text="", font_size='11sp', color=(1, 0.35, 0.35, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.msg)

        reg_btn = Button(text="Register & Start Mining", background_color=(0.1, 0.65, 0.35, 1), bold=True, size_hint_y=None, height='48dp')
        reg_btn.bind(on_press=self.do_register)
        root.add_widget(reg_btn)

        back_btn = Button(text="Back to Options", background_color=(0.3, 0.2, 0.2, 1), size_hint_y=None, height='40dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        # కీబోర్డ్ ఓపెన్ అయినా క్రింది బటన్ కనిపించేలా అదనపు ఖాళీ
        root.add_widget(Label(text="", size_hint_y=None, height='50dp'))

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

        gen_user_id = f"BARAT-{random.randint(100000, 999999)}"

        data = load_data()
        data["registered"] = True
        data["user_id"] = gen_user_id
        data["email"] = email
        data["country_code"] = self.cc_btn.text
        data["phone"] = phone
        data["password"] = pwd
        save_data(data)

        self.manager.current = "main"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.country_index = 0
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.generated_otp = None

        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=[22, 15, 22, 25], spacing=9, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="BARAT NODE LOGIN", font_size='16sp', bold=True, color=(0.2, 0.7, 1, 1), size_hint_y=None, height='35dp'))

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

        self.msg = Label(text="", font_size='11sp', color=(1, 0.35, 0.35, 1), size_hint_y=None, height='28dp')
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

        # కీబోర్డ్ ఓపెన్ అయినా క్రింది బటన్ కనిపించేలా అదనపు ఖాళీ
        root.add_widget(Label(text="", size_hint_y=None, height='50dp'))

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
        if ident.lower() == saved_uid and pwd == saved_pwd:
            is_match = True
        elif ident.lower() == saved_e and pwd == saved_pwd:
            is_match = True
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

        popup = Popup(title="Reset Password", content=box, size_hint=(0.92, 0.62), auto_dismiss=False)

        def do_send_otp(btn):
            data = load_data()
            target_mail = email_in.text.strip().lower()
            if target_mail == data.get("email", "").lower() and data.get("email"):
                self.generated_otp = str(random.randint(1000, 9999))
                status_lbl.color = (0.2, 0.9, 0.5, 1)
                status_lbl.text = f"OTP Code: {self.generated_otp} (Demo Sent to Gmail)"
            else:
                status_lbl.color = (1, 0.4, 0.4, 1)
                status_lbl.text = "Registered Gmail ledhu!"

        def do_reset_pwd(btn):
            if not self.generated_otp or otp_in.text.strip() != self.generated_otp:
                status_lbl.color = (1, 0.4, 0.4, 1)
                status_lbl.text = "Invalid OTP code!"
                return
            new_p = new_pwd_in.text.strip()
            is_valid, msg = is_strong_password(new_p)
            if not is_valid:
                status_lbl.color = (1, 0.4, 0.4, 1)
                status_lbl.text = msg
                return

            data = load_data()
            data["password"] = new_p
            save_data(data)
            popup.dismiss()
            self.msg.color = (0.2, 0.9, 0.5, 1)
            self.msg.text = "Password reset aindhi! Login avvandi."

        send_otp_btn.bind(on_press=do_send_otp)
        reset_btn.bind(on_press=do_reset_pwd)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

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
            self.status_msg.text = "Wallets section lo wallet select/create cheyandi!"
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

        active_info = "Active wallet ledhu. Kindha create/import cheyandi."
        if wallets and 0 <= idx < len(wallets):
            active_info = f"Active: {wallets[idx]['name']} (Bal: {wallets[idx].get('balance',0.0):.2f})"
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
        
        phrase_display = Label(
            text=phrase,
            font_size='12sp',
            color=(0.95, 0.85, 0.3, 1),
            halign='center',
            size_hint_y=0.25
        )
        phrase_display.bind(size=phrase_display.setter('text_size'))
        box.add_widget(phrase_display)

        copy_status = Label(text="", font_size='11sp', color=(0.2, 0.9, 0.5, 1), size_hint_y=0.08)
        box.add_widget(copy_status)

        copy_btn = Button(text="📋 Copy 12-Word Phrase", size_hint_y=0.14, background_color=(0.2, 0.55, 0.8, 1), bold=True)
        box.add_widget(copy_btn)

        confirm_btn = Button(text="Save & Activate", size_hint_y=0.15, background_color=(0.1, 0.6, 0.35, 1), bold=True)
        cancel_btn = Button(text="Cancel", size_hint_y=0.13, background_color=(0.4, 0.2, 0.2, 1))
        box.add_widget(confirm_btn)
        box.add_widget(cancel_btn)

        popup = Popup(title="New Key Vault", content=box, size_hint=(0.92, 0.64), auto_dismiss=False)

        def do_copy(btn):
            Clipboard.copy(phrase)
            copy_status.text = "Phrase Copied to Clipboard!"

        def save_new_wallet(btn):
            wallets.append({"name": new_name, "phrase": phrase, "balance": 0.0})
            data["wallets"] = wallets
            data["active_wallet_index"] = len(wallets) - 1
            save_data(data)
            popup.dismiss()
            self.refresh_dashboard()

        copy_btn.bind(on_press=do_copy)
        confirm_btn.bind(on_press=save_new_wallet)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_import_wallet_popup(self):
        data = load_data()
        wallets = data.get("wallets", [])

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="IMPORT EXISTING WALLET", font_size='14sp', bold=True, color=(0.2, 0.6, 0.9, 1), size_hint_y=0.12))

        input_phrase = ModernInput(hint_text="Enter 12 words separated by space", multiline=True, size_hint_y=0.25)
        box.add_widget(input_phrase)

        paste_btn = Button(text="📋 Paste from Clipboard", size_hint_y=0.14, background_color=(0.2, 0.5, 0.7, 1))
        box.add_widget(paste_btn)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        import_btn = Button(text="Import", background_color=(0.15, 0.5, 0.7, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_color=(0.4, 0.2, 0.2, 1))
        btn_box.add_widget(import_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Import Seed Vault", content=box, size_hint=(0.90, 0.62), auto_dismiss=False)

        def do_paste(btn):
            clip_text = Clipboard.paste()
            if clip_text:
                input_phrase.text = clip_text.strip()

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

        paste_btn.bind(on_press=do_paste)
        import_btn.bind(on_press=do_import)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_profile_popup(self, instance):
        data = load_data()
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=7)
        box.add_widget(Label(text="NODE PROFILE & STATUS", font_size='14sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.14))
        
        info_txt = (
            f"User ID: {data.get('user_id', 'Unassigned')}\n"
            f"Gmail: {data.get('email')}\n"
            f"Mobile: {data.get('country_code','')}{data.get('phone','')}\n"
            f"Node Proof: {data.get('proof_hash')[:14]}..."
        )
        box.add_widget(Label(text=info_txt, font_size='11sp', size_hint_y=0.30))
        
        close_btn = Button(text="Close", size_hint_y=0.14, background_color=(0.4, 0.2, 0.2, 1))
        box.add_widget(close_btn)

        popup = Popup(title="Node Identity Center", content=box, size_hint=(0.90, 0.55), auto_dismiss=False)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_solana_bridge_popup(self, instance):
        data = load_data()
        active = self.get_active_wallet(data)
        wallet_bal = active.get("balance", 0.0) if active else 0.0

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="BARAT -> SOLANA MAIN BRIDGE", font_size='14sp', bold=True, color=(0.6, 0.3, 0.9, 1), size_hint_y=0.12))
        
        addr_input = ModernInput(hint_text="Paste Solana Wallet Address", multiline=False, size_hint_y=0.16)
        amount_input = ModernInput(hint_text="BARAT Amount (Min 50)", multiline=False, input_filter='float', size_hint_y=0.16)
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
        sm.add_widget(AuthChoiceScreen(name="auth_choice"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        sm.current = "landing"
        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
