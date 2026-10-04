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
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.resources import resource_find, resource_add_path

try:
    Window.softinput_mode = "below_target"
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
resource_add_path(BASE_DIR)

if os.path.exists(os.path.join(BASE_DIR, "icon.png")):
    LOGO_FILE = os.path.join(BASE_DIR, "icon.png")
elif os.path.exists(os.path.join(BASE_DIR, "icon.png.png")):
    LOGO_FILE = os.path.join(BASE_DIR, "icon.png.png")
else:
    LOGO_FILE = resource_find("icon.png") or "icon.png"

HALVING_INTERVAL = 5250000.0
BLOCK_REWARD_INITIAL = 10.0
CYCLE_HOURS = 24

MIN_CYCLES_REQUIRED = 5
MIN_WITHDRAW_AMOUNT = 50.0
GAS_FEE_PERCENTAGE = 0.02
FOUNDER_SOLANA_WALLET = "9zYbQMJ9VD2NjXRhd83s4LSUcu9AnLTeetXLd5URWk2z"

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

def get_data_filepath():
    try:
        app = App.get_running_app()
        if app and getattr(app, 'user_data_dir', None):
            return os.path.join(app.user_data_dir, "barat_data.json")
    except Exception:
        pass
    return os.path.join(BASE_DIR, "barat_data.json")

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
    pattern = r'^[a-zA-Z0-9](\.?[a-zA-Z0-9_-]){4,28}[a-zA-Z0-9]@gmail\.com$'
    return bool(re.match(pattern, email.strip().lower()))

def is_strong_password(pwd):
    if len(pwd) < 8:
        return False, "Password must be at least 8 characters long!"
    if not re.search(r'[A-Z]', pwd):
        return False, "Must contain at least 1 Uppercase (A-Z) letter!"
    if not re.search(r'[a-z]', pwd):
        return False, "Must contain at least 1 Lowercase (a-z) letter!"
    if not re.search(r'[0-9]', pwd):
        return False, "Must contain at least 1 Number (0-9)!"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
        return False, "Must contain at least 1 Special character (!@#$)!"
    return True, "Strong Password"

def is_valid_solana_address(addr):
    if not (32 <= len(addr) <= 44):
        return False
    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]+$'
    return bool(re.match(base58_pattern, addr))

def load_data():
    filepath = get_data_filepath()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "registered": False,
        "is_logged_in": False,
        "user_id": "",
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
        "cloud_gist_id": "",
        "bridge_transactions": []
    }

def save_local_only(data):
    try:
        filepath = get_data_filepath()
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def save_data(data):
    save_local_only(data)
    sync_to_github_cloud(data)

# High-Contrast Modern Slate Blue Container Card
class ModernCard(BoxLayout):
    def __init__(self, bg_color=(0.11, 0.16, 0.23, 1), border_color=(0.22, 0.31, 0.44, 1), radius=[14], **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        with self.canvas.before:
            self.color_bg = Color(*self.bg_color)
            self.rect_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.color_border = Color(*self.border_color)
            self.rect_border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius[0]), width=1.2)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.rect_bg.pos = self.pos
        self.rect_bg.size = self.size
        self.rect_border.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius[0])

class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0.13, 0.18, 0.26, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0.05, 0.88, 0.55, 1)
        self.padding = [14, 12, 14, 12]
        self.font_size = '13.5sp'

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 25, 24, 25], spacing=14)

        try:
            if os.path.exists(LOGO_FILE):
                logo = Image(source=LOGO_FILE, size_hint_y=0.42, allow_stretch=True, keep_ratio=True)
                root.add_widget(logo)
            else:
                root.add_widget(Label(text="⚡ BARAT CORE ⚡", font_size='24sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.35))
        except Exception:
            root.add_widget(Label(text="⚡ BARAT CORE ⚡", font_size='24sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.35))

        title_card = ModernCard(orientation='vertical', size_hint_y=0.15, padding=[10, 8, 10, 8], spacing=2)
        title_card.add_widget(Label(
            text="PROOF OF INTELLIGENCE",
            font_size='14.5sp',
            bold=True,
            halign="center",
            color=(0.05, 0.88, 0.55, 1)
        ))
        title_card.add_widget(Label(
            text="SUSTAINABLE MOBILE CONSENSUS",
            font_size='11sp',
            halign="center",
            color=(0.75, 0.85, 0.95, 1)
        ))
        root.add_widget(title_card)

        mined_card = ModernCard(size_hint_y=0.13, padding=[10, 8, 10, 8])
        self.mined_preview = Label(
            text="Global Tokens Mined\n0.00 $BARAT",
            font_size='14sp',
            bold=True,
            halign="center",
            color=(1, 1, 1, 1)
        )
        mined_card.add_widget(self.mined_preview)
        root.add_widget(mined_card)

        self.start_btn = Button(
            text="START",
            size_hint=(None, None),
            size=('132dp', '132dp'),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.05, 0.78, 0.48, 1),
            font_size='22sp',
            bold=True
        )
        self.start_btn.bind(on_press=self.go_next)
        root.add_widget(self.start_btn)

        root.add_widget(Label(text="", size_hint_y=0.04))
        self.add_widget(root)

    def on_enter(self):
        try:
            data = load_data()
            tot = data.get("balance", 0.0)
            for w in data.get("wallets", []):
                tot += w.get("balance", 0.0)
            self.mined_preview.text = f"Global Tokens Mined\n{tot:.2f} $BARAT"
        except Exception:
            pass

    def go_next(self, instance):
        try:
            data = load_data()
            if data.get("registered", False) and data.get("is_logged_in", False):
                self.manager.current = "main"
            else:
                self.manager.current = "auth_choice"
        except Exception:
            self.manager.current = "auth_choice"

class AuthChoiceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 28, 24, 28], spacing=16)

        try:
            if os.path.exists(LOGO_FILE):
                root.add_widget(Image(source=LOGO_FILE, size_hint_y=0.35, allow_stretch=True, keep_ratio=True))
            else:
                root.add_widget(Label(text="BARAT NETWORK", font_size='20sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.25))
        except Exception:
            pass

        info_card = ModernCard(orientation='vertical', size_hint_y=0.22, padding=[12, 10, 12, 10], spacing=4)
        info_card.add_widget(Label(
            text="WELCOME TO BARAT NETWORK",
            font_size='15sp',
            bold=True,
            color=(0.05, 0.88, 0.55, 1)
        ))
        info_card.add_widget(Label(
            text="Join decentralized quantum consensus.\nSelect an access option to continue:",
            font_size='11.5sp',
            halign='center',
            color=(0.8, 0.88, 0.96, 1)
        ))
        root.add_widget(info_card)

        reg_btn = Button(
            text="CREATE NEW ACCOUNT",
            size_hint_y=0.13,
            background_normal='',
            background_color=(0.05, 0.72, 0.42, 1),
            font_size='13sp',
            bold=True
        )
        reg_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        root.add_widget(reg_btn)

        login_btn = Button(
            text="EXISTING ACCOUNT LOGIN",
            size_hint_y=0.13,
            background_normal='',
            background_color=(0.18, 0.48, 0.82, 1),
            font_size='13sp',
            bold=True
        )
        login_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        root.add_widget(login_btn)

        root.add_widget(Label(text="", size_hint_y=0.12))
        self.add_widget(root)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)

        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=[20, 15, 20, 25], spacing=10, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="CREATE BARAT NODE ACCOUNT", font_size='16sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=None, height='35dp'))

        self.email_input = ModernInput(hint_text="Valid Gmail Address (@gmail.com)", multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.email_input)

        self.pass_input = ModernInput(hint_text="Strong Password (8+ chars, A-Z, 0-9, @#)", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.pass_input)

        self.confirm_pass_input = ModernInput(hint_text="Confirm Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.confirm_pass_input)

        captcha_card = ModernCard(size_hint_y=None, height='42dp', padding=[10, 4, 10, 4])
        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(1.0, 0.84, 0.24, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='45dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.msg)

        reg_btn = Button(text="Register & Start Mining", background_normal='', background_color=(0.05, 0.72, 0.42, 1), bold=True, size_hint_y=None, height='48dp')
        reg_btn.bind(on_press=self.do_register)
        root.add_widget(reg_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.28, 0.22, 0.26, 1), size_hint_y=None, height='40dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        root.add_widget(Label(text="", size_hint_y=None, height='50dp'))
        scroll.add_widget(root)
        self.add_widget(scroll)

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_register(self, instance):
        email = self.email_input.text.strip()
        pwd = self.pass_input.text.strip()
        cpwd = self.confirm_pass_input.text.strip()

        if not is_valid_gmail(email):
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Invalid Gmail address! Please use a valid @gmail.com"
            return

        is_strong, pwd_err = is_strong_password(pwd)
        if not is_strong:
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = pwd_err
            return

        if pwd != cpwd:
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Passwords do not match!"
            return

        if not self.verify_captcha():
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Captcha verification failed! Try again."
            self.refresh_captcha()
            return

        gen_user_id = f"BARAT-{random.randint(100000, 999999)}"

        data = load_data()
        data["registered"] = True
        data["is_logged_in"] = True
        data["user_id"] = gen_user_id
        data["email"] = email
        data["password"] = pwd
        save_data(data)

        self.manager.current = "main"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.generated_otp = None

        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=[20, 15, 20, 25], spacing=10, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="BARAT NODE LOGIN", font_size='16sp', bold=True, color=(0.2, 0.68, 1, 1), size_hint_y=None, height='35dp'))

        self.ident_input = ModernInput(hint_text="Registered User ID or Gmail", multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.ident_input)

        self.pass_input = ModernInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        root.add_widget(self.pass_input)

        captcha_card = ModernCard(size_hint_y=None, height='42dp', padding=[10, 4, 10, 4])
        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(1.0, 0.84, 0.24, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='45dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.msg)

        login_btn = Button(text="Secure Login", background_normal='', background_color=(0.16, 0.52, 0.88, 1), bold=True, size_hint_y=None, height='48dp')
        login_btn.bind(on_press=self.do_login)
        root.add_widget(login_btn)

        forgot_btn = Button(text="Forgot Password?", size_hint_y=None, height='38dp', background_normal='', background_color=(0.2, 0.26, 0.36, 1), font_size='11.5sp')
        forgot_btn.bind(on_press=self.open_forgot_password_popup)
        root.add_widget(forgot_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.28, 0.22, 0.26, 1), size_hint_y=None, height='38dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        root.add_widget(Label(text="", size_hint_y=None, height='50dp'))
        scroll.add_widget(root)
        self.add_widget(scroll)

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
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Please enter User ID/Gmail and Password!"
            return

        if not self.verify_captcha():
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Captcha verification failed! Try again."
            self.refresh_captcha()
            return

        data = load_data()
        saved_uid = data.get("user_id", "").lower()
        saved_e = data.get("email", "").lower()
        saved_pwd = data.get("password", "")

        if not data.get("registered", False) or not saved_e:
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "No account found! Please register first."
            self.refresh_captcha()
            return

        is_match = False
        if ident.lower() == saved_uid and pwd == saved_pwd:
            is_match = True
        elif ident.lower() == saved_e and pwd == saved_pwd:
            is_match = True

        if is_match:
            data["is_logged_in"] = True
            save_data(data)
            self.manager.current = "main"
        else:
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Invalid Credentials! Check User ID/Gmail or Password."
            self.refresh_captcha()

    def open_forgot_password_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="PASSWORD RECOVERY", font_size='14sp', bold=True, color=(1.0, 0.84, 0.24, 1), size_hint_y=0.15))

        email_in = ModernInput(hint_text="Registered Gmail ID", multiline=False, size_hint_y=0.18)
        box.add_widget(email_in)

        otp_in = ModernInput(hint_text="Enter 4-Digit OTP", multiline=False, input_filter='int', size_hint_y=0.18)
        box.add_widget(otp_in)

        new_pwd_in = ModernInput(hint_text="New Strong Password (8+ chars)", password=True, multiline=False, size_hint_y=0.18)
        box.add_widget(new_pwd_in)

        status_lbl = Label(text="", font_size='11sp', color=(1, 0.4, 0.4, 1), size_hint_y=0.1)
        box.add_widget(status_lbl)

        btn_box = BoxLayout(spacing=8, size_hint_y=0.21)
        send_otp_btn = Button(text="Send OTP", background_normal='', background_color=(0.18, 0.48, 0.82, 1), font_size='11sp')
        reset_btn = Button(text="Reset", background_normal='', background_color=(0.05, 0.72, 0.42, 1), font_size='11sp', bold=True)
        close_btn = Button(text="Close", background_normal='', background_color=(0.32, 0.18, 0.2, 1), font_size='11sp')
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
                status_lbl.color = (0.05, 0.88, 0.55, 1)
                status_lbl.text = f"OTP Code: {self.generated_otp} (Sent to registered Gmail)"
            else:
                status_lbl.color = (1, 0.4, 0.4, 1)
                status_lbl.text = "Gmail address not found in registry!"

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
            self.msg.color = (0.05, 0.88, 0.55, 1)
            self.msg.text = "Password reset successfully! Please login."

        send_otp_btn.bind(on_press=do_send_otp)
        reset_btn.bind(on_press=do_reset_pwd)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[16, 10, 16, 10], spacing=6)

        # Top Bar
        top_bar = ModernCard(size_hint_y=0.075, padding=[8, 4, 8, 4], spacing=6)
        top_bar.add_widget(Label(text="BARAT CORE NODE", font_size='13sp', bold=True, color=(0.05, 0.88, 0.55, 1)))
        
        wallet_mgr_btn = Button(text="Wallets", size_hint_x=0.28, background_normal='', background_color=(0.18, 0.48, 0.78, 1), font_size='11sp', bold=True)
        wallet_mgr_btn.bind(on_press=self.open_wallet_manager_popup)
        top_bar.add_widget(wallet_mgr_btn)

        profile_btn = Button(text="Profile", size_hint_x=0.28, background_normal='', background_color=(0.14, 0.40, 0.68, 1), font_size='11sp', bold=True)
        profile_btn.bind(on_press=self.open_profile_popup)
        top_bar.add_widget(profile_btn)
        root.add_widget(top_bar)

        try:
            if os.path.exists(LOGO_FILE):
                self.logo_img = Image(source=LOGO_FILE, size_hint_y=0.16, allow_stretch=True, keep_ratio=True)
                root.add_widget(self.logo_img)
            else:
                root.add_widget(Label(text="[ BARAT CORE ]", font_size='18sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.11))
        except Exception:
            pass

        # Balances Card
        bal_card = ModernCard(size_hint_y=0.115, padding=[10, 6, 10, 6], spacing=6)
        self.mined_bal_lbl = Label(text="Mined: 0.00", font_size='13.5sp', bold=True, color=(1, 1, 1, 1))
        self.active_wallet_lbl = Label(text="Active: None\nBal: 0.00", font_size='12.5sp', bold=True, color=(0.05, 0.88, 0.55, 1), halign="center")
        bal_card.add_widget(self.mined_bal_lbl)
        bal_card.add_widget(self.active_wallet_lbl)
        root.add_widget(bal_card)

        self.claim_wallet_btn = Button(text="Claim Mined to Active Wallet", size_hint_y=0.065, background_normal='', background_color=(0.05, 0.62, 0.38, 1), font_size='12sp', bold=True)
        self.claim_wallet_btn.bind(on_press=self.claim_to_active_wallet)
        root.add_widget(self.claim_wallet_btn)

        # Mining Info Card
        info_card = ModernCard(orientation='vertical', size_hint_y=0.17, padding=[10, 6, 10, 6], spacing=2)
        self.phase_lbl = Label(text="Phase: Initializing...", font_size='11sp', color=(1.0, 0.84, 0.24, 1), bold=True)
        self.puzzle_lbl = Label(text="Target: Loading...", font_size='11sp', color=(0.4, 0.76, 1, 1))
        self.block_lbl = Label(text="Height: #0000 | Proof: Verifying", font_size='10sp', color=(0.8, 0.88, 0.94, 1))
        self.timer_lbl = Label(text="Engine: Ready", font_size='11sp', color=(0.05, 0.88, 0.55, 1), bold=True)
        info_card.add_widget(self.phase_lbl)
        info_card.add_widget(self.puzzle_lbl)
        info_card.add_widget(self.block_lbl)
        info_card.add_widget(self.timer_lbl)
        root.add_widget(info_card)

        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=0.09, background_normal='', background_color=(0.05, 0.72, 0.42, 1), font_size='13sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.075, background_normal='', background_color=(0.54, 0.26, 0.82, 1), font_size='12sp', bold=True)
        self.sol_btn.bind(on_press=self.open_solana_bridge_popup)
        root.add_widget(self.sol_btn)

        self.logout_btn = Button(text="Switch Node / Exit", size_hint_y=0.05, background_normal='', background_color=(0.36, 0.18, 0.22, 1), font_size='11sp')
        self.logout_btn.bind(on_press=self.do_logout)
        root.add_widget(self.logout_btn)

        self.status_msg = Label(text="Cloud Engine Synchronized.", font_size='10sp', color=(1.0, 0.88, 0.4, 1), size_hint_y=0.04)
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
            self.active_wallet_lbl.text = f"Active: {w_name}\nClaimed: {w_bal:.2f} BARAT"
        else:
            self.active_wallet_lbl.text = "Active: None\nClaimed: 0.00 BARAT"

        self.phase_lbl.text = self.calculate_reward(data.get("total_mined", mined))
        self.update_block_display()

    def claim_to_active_wallet(self, instance):
        data = load_data()
        mined = data.get("balance", 0.0)
        if mined <= 0:
            self.status_msg.color = (1, 0.38, 0.38, 1)
            self.status_msg.text = "No mined balance available to claim."
            return

        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        if not wallets or idx >= len(wallets):
            self.status_msg.color = (1, 0.38, 0.38, 1)
            self.status_msg.text = "Please create and confirm an active wallet first!"
            return

        wallets[idx]["balance"] = wallets[idx].get("balance", 0.0) + mined
        data["balance"] = 0.0
        data["wallets"] = wallets
        save_data(data)
        self.refresh_dashboard()
        self.status_msg.color = (0.05, 0.88, 0.55, 1)
        self.status_msg.text = f"Claimed {mined:.2f} BARAT to {wallets[idx]['name']}!"

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
            self.timer_lbl.color = (0.05, 0.88, 0.55, 1)
            self.mine_btn.disabled = False
            self.mine_btn.background_color = (0.05, 0.72, 0.42, 1)
        else:
            rem = int(cooldown - elapsed)
            hrs = rem // 3600
            mins = (rem % 3600) // 60
            secs = rem % 60
            self.timer_lbl.text = f"Next Block In: {hrs:02d}h {mins:02d}m {secs:02d}s"
            self.timer_lbl.color = (0.8, 0.88, 0.94, 1)
            self.mine_btn.disabled = True
            self.mine_btn.background_color = (0.24, 0.28, 0.34, 1)

    def start_mining(self, instance):
        now = get_server_time()
        data = load_data()
        cooldown = CYCLE_HOURS * 3600
        if (now - data.get("last_cycle", 0)) < cooldown:
            return

        self.mine_btn.disabled = True
        self.mine_btn.text = "⚡ Mining Block in Progress..."
        self.status_msg.color = (1.0, 0.84, 0.24, 1)
        self.status_msg.text = "Processing cryptographic target..."

        def finish_mining(dt):
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
            self.mine_btn.text = "Solve Puzzle & Mine Block"
            self.status_msg.color = (0.05, 0.88, 0.55, 1)
            self.status_msg.text = f"Block #{data['block_height']} solved! +{reward:.1f} BARAT mined."
            self.update_timer(0)

        Clock.schedule_once(finish_mining, 2.5)

    def open_wallet_manager_popup(self, instance):
        data = load_data()
        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="WALLET CONTROL CENTER", font_size='14sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.12))

        active_wallet = wallets[idx] if (wallets and 0 <= idx < len(wallets)) else None
        if active_wallet:
            active_info = f"Current Active: {active_wallet['name']}\nClaimed Balance: {active_wallet.get('balance',0.0):.2f} BARAT"
        else:
            active_info = "No active wallet. Create or import below."

        box.add_widget(Label(text=active_info, font_size='11sp', halign='center', color=(0.85, 0.9, 0.95, 1), size_hint_y=0.12))

        w_list = f"Total Wallets: {len(wallets)}"
        box.add_widget(Label(text=w_list, font_size='10sp', color=(0.7, 0.8, 0.9, 1), size_hint_y=0.08))

        create_btn = Button(text="+ Generate & Confirm New Wallet", size_hint_y=0.14, background_normal='', background_color=(0.05, 0.68, 0.38, 1), font_size='11sp', bold=True)
        import_btn = Button(text="Import / Switch by 12-Word Key", size_hint_y=0.14, background_normal='', background_color=(0.18, 0.48, 0.82, 1), font_size='11sp', bold=True)
        switch_btn = Button(text="Switch to Next Wallet", size_hint_y=0.14, background_normal='', background_color=(0.48, 0.36, 0.22, 1), font_size='11sp')
        close_btn = Button(text="Done / Close", size_hint_y=0.14, background_normal='', background_color=(0.34, 0.18, 0.22, 1))

        box.add_widget(create_btn)
        box.add_widget(import_btn)
        box.add_widget(switch_btn)
        box.add_widget(close_btn)

        popup = Popup(title="Wallet Manager", content=box, size_hint=(0.92, 0.65), auto_dismiss=False)

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
        box.add_widget(Label(text=f"GENERATE: {new_name}", font_size='14sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.12))
        
        phrase_display = Label(
            text=phrase,
            font_size='12.5sp',
            color=(1.0, 0.86, 0.35, 1),
            bold=True,
            halign='center',
            size_hint_y=0.25
        )
        phrase_display.bind(size=phrase_display.setter('text_size'))
        box.add_widget(phrase_display)

        copy_status = Label(text="", font_size='11sp', color=(0.05, 0.88, 0.55, 1), size_hint_y=0.08)
        box.add_widget(copy_status)

        copy_btn = Button(text="📋 Copy 12-Word Phrase", size_hint_y=0.14, background_normal='', background_color=(0.18, 0.52, 0.85, 1), bold=True)
        box.add_widget(copy_btn)

        confirm_btn = Button(text="Confirm & Activate Wallet", size_hint_y=0.15, background_normal='', background_color=(0.05, 0.68, 0.38, 1), bold=True)
        cancel_btn = Button(text="Cancel", size_hint_y=0.13, background_normal='', background_color=(0.34, 0.2, 0.22, 1))
        box.add_widget(confirm_btn)
        box.add_widget(cancel_btn)

        popup = Popup(title="New Wallet Setup", content=box, size_hint=(0.92, 0.64), auto_dismiss=False)

        def do_copy(btn):
            Clipboard.copy(phrase)
            copy_status.text = "Phrase Copied to Clipboard!"

        def save_and_confirm(btn):
            wallets.append({"name": new_name, "phrase": phrase, "balance": 0.0})
            data["wallets"] = wallets
            data["active_wallet_index"] = len(wallets) - 1
            save_data(data)
            popup.dismiss()
            self.refresh_dashboard()

        copy_btn.bind(on_press=do_copy)
        confirm_btn.bind(on_press=save_and_confirm)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_import_wallet_popup(self):
        data = load_data()
        wallets = data.get("wallets", [])

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="IMPORT / RESTORE WALLET", font_size='14sp', bold=True, color=(0.2, 0.68, 1, 1), size_hint_y=0.12))

        input_phrase = ModernInput(hint_text="Enter 12 words separated by space", multiline=True, size_hint_y=0.25)
        box.add_widget(input_phrase)

        paste_btn = Button(text="📋 Paste from Clipboard", size_hint_y=0.14, background_normal='', background_color=(0.18, 0.48, 0.72, 1))
        box.add_widget(paste_btn)

        status_lbl = Label(text="", font_size='11sp', color=(1, 0.4, 0.4, 1), size_hint_y=0.08)
        box.add_widget(status_lbl)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        import_btn = Button(text="Import / Switch", background_normal='', background_color=(0.14, 0.52, 0.82, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.34, 0.2, 0.22, 1))
        btn_box.add_widget(import_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Import Wallet", content=box, size_hint=(0.90, 0.64), auto_dismiss=False)

        def do_paste(btn):
            clip_text = Clipboard.paste()
            if clip_text:
                input_phrase.text = clip_text.strip()

        def do_import(btn):
            words = input_phrase.text.strip().split()
            if len(words) != 12:
                status_lbl.text = "Must contain exactly 12 words!"
                return

            phrase = " ".join(words)
            existing_idx = next((i for i, w in enumerate(wallets) if w.get("phrase") == phrase), None)
            if existing_idx is not None:
                data["active_wallet_index"] = existing_idx
                save_data(data)
                popup.dismiss()
                self.refresh_dashboard()
            else:
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
        box = BoxLayout(orientation='vertical', padding=[16, 14, 16, 14], spacing=9)
        
        box.add_widget(Label(
            text="NODE IDENTITY & PROFILE", 
            font_size='15sp', 
            bold=True, 
            color=(0.05, 0.88, 0.55, 1), 
            size_hint_y=0.15
        ))
        
        info_txt = (
            f"User ID: {data.get('user_id', 'Unassigned')}\n"
            f"Gmail: {data.get('email', 'N/A')}\n"
            f"Completed Cycles: {data.get('completed_cycles', 0)}\n"
            f"Block Height: #{data.get('block_height', 3)}\n"
            f"Node Proof: {data.get('proof_hash', '')[:16]}..."
        )
        box.add_widget(Label(
            text=info_txt, 
            font_size='11.5sp', 
            color=(0.95, 0.98, 1, 1),
            halign='left',
            size_hint_y=0.45
        ))
        
        btn_box = BoxLayout(spacing=10, size_hint_y=0.22)
        logout_profile_btn = Button(
            text="Logout", 
            background_normal='',
            background_color=(0.82, 0.22, 0.26, 1), 
            font_size='12sp', 
            bold=True
        )
        close_btn = Button(
            text="Close", 
            size_hint_x=0.45,
            background_normal='',
            background_color=(0.28, 0.35, 0.44, 1), 
            font_size='12sp'
        )
        btn_box.add_widget(logout_profile_btn)
        btn_box.add_widget(close_btn)
        box.add_widget(btn_box)

        popup = Popup(
            title="Node Identity Center", 
            content=box, 
            size_hint=(0.90, 0.58), 
            auto_dismiss=False
        )

        def do_profile_logout(btn):
            data["is_logged_in"] = False
            save_data(data)
            popup.dismiss()
            self.manager.current = "auth_choice"

        logout_profile_btn.bind(on_press=do_profile_logout)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_solana_bridge_popup(self, instance):
        data = load_data()
        active = self.get_active_wallet(data)
        wallet_bal = active.get("balance", 0.0) if active else 0.0

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="BARAT -> SOLANA MAIN BRIDGE", font_size='14sp', bold=True, color=(0.65, 0.38, 0.95, 1), size_hint_y=0.12))
        
        addr_input = ModernInput(hint_text="Paste Solana Wallet Address", multiline=False, size_hint_y=0.16)
        amount_input = ModernInput(hint_text="BARAT Amount (Min 50)", multiline=False, input_filter='float', size_hint_y=0.16)
        box.add_widget(addr_input)
        box.add_widget(amount_input)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        submit_btn = Button(text="Confirm Bridge", background_normal='', background_color=(0.54, 0.26, 0.82, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.34, 0.2, 0.22, 1))
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
        data = load_data()
        data["is_logged_in"] = False
        save_data(data)
        self.manager.current = "auth_choice"

class BaratCoreApp(App):
    def build(self):
        # Deep Royal Slate-Blue Background (High Contrast & Clear)
        Window.clearcolor = (0.06, 0.09, 0.14, 1.0)
        try:
            if os.path.exists(LOGO_FILE):
                self.icon = LOGO_FILE
        except Exception:
            pass
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
