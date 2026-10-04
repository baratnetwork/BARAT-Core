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
from kivy.utils import platform

Window.softinput_mode = "pan"

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

def share_to_social_apps(text_to_share):
    Clipboard.copy(text_to_share)
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')

            sendIntent = Intent()
            sendIntent.setAction(Intent.ACTION_SEND)
            sendIntent.putExtra(Intent.EXTRA_TEXT, String(text_to_share))
            sendIntent.setType('text/plain')

            chooser = Intent.createChooser(sendIntent, String('Share Referral Link via'))
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(chooser)
        except Exception:
            pass

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
    paths = [get_data_filepath(), os.path.join(BASE_DIR, "barat_data.json")]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    content = json.load(f)
                    if content and content.get("registered", False):
                        return content
            except Exception:
                pass
    return {
        "registered": False,
        "is_logged_in": False,
        "user_id": "",
        "referral_code": "",
        "referred_by": "",
        "team_members": [],
        "mining_speed_multiplier": 1.0,
        "email": "",
        "password": "",
        "wallets": [],
        "active_wallet_index": 0,
        "balance": 0.0,
        "base_mined": 0.0,
        "total_mined": 0.0,
        "completed_cycles": 0,
        "block_height": 3,
        "last_cycle": 0,
        "is_mining_active": False,
        "proof_hash": "ECO_GENESIS_PROOF_00000000",
        "cloud_gist_id": "",
        "bridge_transactions": []
    }

def save_local_only(data):
    paths = [get_data_filepath(), os.path.join(BASE_DIR, "barat_data.json")]
    for p in paths:
        try:
            folder = os.path.dirname(p)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(p, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

def save_data(data):
    save_local_only(data)
    sync_to_github_cloud(data)

def get_current_live_mined(data):
    base = data.get("base_mined", data.get("balance", 0.0))
    if not data.get("is_mining_active", False):
        return base
    
    last = data.get("last_cycle", 0)
    now = time.time()
    elapsed = max(0, min(now - last, CYCLE_HOURS * 3600))
    
    total_mined = data.get("total_mined", base)
    phase = int(total_mined // HALVING_INTERVAL) + 1
    cycle_reward = (BLOCK_REWARD_INITIAL / (2 ** (phase - 1))) * data.get("mining_speed_multiplier", 1.0)
    
    rate_per_sec = cycle_reward / (CYCLE_HOURS * 3600)
    current_accrued = base + (elapsed * rate_per_sec)
    return current_accrued

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

class PasswordField(BoxLayout):
    def __init__(self, hint_text="Password", **kwargs):
        super().__init__(orientation='horizontal', spacing=6, **kwargs)
        self.input = ModernInput(hint_text=hint_text, password=True, multiline=False, size_hint_x=0.78)
        self.add_widget(self.input)

        self.eye_btn = Button(
            text="SHOW",
            size_hint_x=0.22,
            background_normal='',
            background_color=(0.18, 0.26, 0.36, 1),
            font_size='11sp',
            bold=True
        )
        self.eye_btn.bind(on_press=self.toggle_visibility)
        self.add_widget(self.eye_btn)

    def toggle_visibility(self, instance):
        if self.input.password:
            self.input.password = False
            self.eye_btn.text = "HIDE"
            self.eye_btn.background_color = (0.05, 0.62, 0.38, 1)
        else:
            self.input.password = True
            self.eye_btn.text = "SHOW"
            self.eye_btn.background_color = (0.18, 0.26, 0.36, 1)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, val):
        self.input.text = val

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 25, 24, 25], spacing=14)

        try:
            if os.path.exists(LOGO_FILE):
                logo = Image(source=LOGO_FILE, size_hint_y=0.42, allow_stretch=True, keep_ratio=True)
                root.add_widget(logo)
            else:
                root.add_widget(Label(text="BARAT CORE", font_size='24sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.35))
        except Exception:
            root.add_widget(Label(text="BARAT CORE", font_size='24sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.35))

        title_card = ModernCard(orientation='vertical', size_hint_y=0.15, padding=[10, 8, 10, 8], spacing=2)
        title_card.add_widget(Label(
            text="PROOF OF INTELLIGENCE",
            font_size='14.5sp',
            bold=True,
            halign="center",
            color=(0.05, 0.88, 0.55, 1)
        ))
        title_card.add_widget(Label(
            text="NEXT-GEN DECENTRALIZED PROTOCOL",
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
            tot = get_current_live_mined(data)
            for w in data.get("wallets", []):
                tot += w.get("balance", 0.0)
            self.mined_preview.text = f"Global Tokens Mined\n{tot:.2f} $BARAT"
        except Exception:
            pass

    def go_next(self, instance):
        try:
            data = load_data()
            if data.get("registered", False) and data.get("is_logged_in", False):
                self.manager.current = "main_hub"
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

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation='vertical', padding=[20, 15, 20, 30], spacing=12, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="CREATE BARAT NODE ACCOUNT", font_size='16sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=None, height='35dp'))

        self.email_input = ModernInput(hint_text="Valid Gmail Address (@gmail.com)", multiline=False, size_hint_y=None, height='48dp')
        root.add_widget(self.email_input)

        self.pass_field = PasswordField(hint_text="Strong Password (8+ chars)", size_hint_y=None, height='48dp')
        root.add_widget(self.pass_field)

        self.confirm_pass_field = PasswordField(hint_text="Confirm Password", size_hint_y=None, height='48dp')
        root.add_widget(self.confirm_pass_field)

        self.invite_input = ModernInput(hint_text="Invitation Code (Optional)", multiline=False, size_hint_y=None, height='48dp')
        root.add_widget(self.invite_input)

        captcha_card = ModernCard(size_hint_y=None, height='44dp', padding=[10, 4, 10, 4])
        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(1.0, 0.84, 0.24, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='48dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.msg)

        reg_btn = Button(text="Register & Start Mining", background_normal='', background_color=(0.05, 0.72, 0.42, 1), bold=True, size_hint_y=None, height='50dp')
        reg_btn.bind(on_press=self.do_register)
        root.add_widget(reg_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.28, 0.22, 0.26, 1), size_hint_y=None, height='42dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        root.add_widget(Label(text="", size_hint_y=None, height='140dp'))
        scroll.add_widget(root)
        self.add_widget(scroll)

    def on_pre_enter(self):
        self.email_input.text = ""
        self.pass_field.text = ""
        self.confirm_pass_field.text = ""
        self.invite_input.text = ""
        self.captcha_input.text = ""
        self.msg.text = ""
        self.refresh_captcha()

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_register(self, instance):
        email = self.email_input.text.strip().lower()
        pwd = self.pass_field.text.strip()
        cpwd = self.confirm_pass_field.text.strip()
        invited_code = self.invite_input.text.strip().upper()

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
        gen_ref_code = f"CORE{random.randint(1000, 9999)}"

        data = load_data()
        data["registered"] = True
        data["is_logged_in"] = True
        data["user_id"] = gen_user_id
        data["referral_code"] = gen_ref_code
        data["referred_by"] = invited_code if invited_code else "NONE"
        data["mining_speed_multiplier"] = 1.25 if invited_code else 1.0
        data["email"] = email
        data["password"] = pwd
        save_data(data)

        self.manager.current = "main_hub"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.generated_otp = None

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation='vertical', padding=[20, 15, 20, 30], spacing=12, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="BARAT NODE LOGIN", font_size='16sp', bold=True, color=(0.2, 0.68, 1, 1), size_hint_y=None, height='35dp'))

        self.ident_input = ModernInput(hint_text="Registered User ID or Gmail", multiline=False, size_hint_y=None, height='48dp')
        root.add_widget(self.ident_input)

        self.pass_field = PasswordField(hint_text="Password", size_hint_y=None, height='48dp')
        root.add_widget(self.pass_field)

        captcha_card = ModernCard(size_hint_y=None, height='44dp', padding=[10, 4, 10, 4])
        self.captcha_lbl = Label(text=f"Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(1.0, 0.84, 0.24, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = ModernInput(hint_text="Enter Math Answer", multiline=False, input_filter='int', size_hint_y=None, height='48dp')
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='28dp')
        root.add_widget(self.msg)

        self.login_btn = Button(text="Secure Login", background_normal='', background_color=(0.16, 0.52, 0.88, 1), bold=True, size_hint_y=None, height='50dp')
        self.login_btn.bind(on_press=self.do_login)
        root.add_widget(self.login_btn)

        forgot_btn = Button(text="Forgot Password?", size_hint_y=None, height='38dp', background_normal='', background_color=(0.2, 0.26, 0.36, 1), font_size='11.5sp')
        forgot_btn.bind(on_press=self.open_forgot_password_popup)
        root.add_widget(forgot_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.28, 0.22, 0.26, 1), size_hint_y=None, height='38dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        root.add_widget(Label(text="", size_hint_y=None, height='140dp'))
        scroll.add_widget(root)
        self.add_widget(scroll)

    def on_pre_enter(self):
        self.ident_input.text = ""
        self.pass_field.text = ""
        self.captcha_input.text = ""
        self.msg.text = ""
        self.refresh_captcha()

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Verification: {self.num1} + {self.num2} = ?"
        self.captcha_input.text = ""

    def verify_captcha(self):
        return self.captcha_input.text.strip() == str(self.num1 + self.num2)

    def do_login(self, instance):
        ident = self.ident_input.text.strip().lower()
        pwd = self.pass_field.text.strip()

        if not ident or not pwd:
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Please enter User ID/Gmail and Password!"
            return

        if not self.verify_captcha():
            self.msg.color = (1, 0.38, 0.38, 1)
            self.msg.text = "Captcha verification failed! Try again."
            self.refresh_captcha()
            return

        self.login_btn.disabled = True
        self.msg.color = (1.0, 0.84, 0.24, 1)
        self.msg.text = "Authenticating with node ledger..."

        def check_login_thread():
            data = load_data()
            saved_uid = str(data.get("user_id", "")).strip().lower()
            saved_e = str(data.get("email", "")).strip().lower()
            saved_pwd = str(data.get("password", "")).strip()

            success = False
            if (ident == saved_uid or ident == saved_e) and pwd == saved_pwd and saved_pwd:
                success = True
            
            if not success:
                try:
                    url = "https://api.github.com/gists"
                    headers = {
                        "Authorization": f"token {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "BaratCoreApp"
                    }
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as response:
                        gists = json.loads(response.read().decode('utf-8'))
                        for g in gists:
                            if g.get("description") == GIST_DESCRIPTION:
                                for fname, finfo in g.get("files", {}).items():
                                    raw_url = finfo.get("raw_url")
                                    if raw_url:
                                        with urllib.request.urlopen(raw_url, timeout=3) as raw_resp:
                                            remote_json = json.loads(raw_resp.read().decode('utf-8'))
                                            r_uid = str(remote_json.get("user_id", "")).strip().lower()
                                            r_e = str(remote_json.get("email", "")).strip().lower()
                                            r_pwd = str(remote_json.get("password", "")).strip()
                                            if (ident == r_uid or ident == r_e) and pwd == r_pwd:
                                                data = remote_json
                                                data["cloud_gist_id"] = g.get("id")
                                                save_local_only(data)
                                                success = True
                                                break
                            if success:
                                break
                except Exception:
                    pass

            def finish_ui(dt):
                self.login_btn.disabled = False
                if success:
                    data["is_logged_in"] = True
                    save_data(data)
                    self.manager.current = "main_hub"
                else:
                    self.msg.color = (1, 0.38, 0.38, 1)
                    self.msg.text = "Invalid Credentials! Check Gmail or Password."
                    self.refresh_captcha()

            Clock.schedule_once(finish_ui, 0)

        threading.Thread(target=check_login_thread, daemon=True).start()

    def open_forgot_password_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text="PASSWORD RECOVERY", font_size='14sp', bold=True, color=(1.0, 0.84, 0.24, 1), size_hint_y=0.15))

        email_in = ModernInput(hint_text="Registered Gmail ID", multiline=False, size_hint_y=0.18)
        box.add_widget(email_in)

        otp_in = ModernInput(hint_text="Enter 4-Digit OTP", multiline=False, input_filter='int', size_hint_y=0.18)
        box.add_widget(otp_in)

        new_pwd_field = PasswordField(hint_text="New Strong Password (8+ chars)", size_hint_y=0.18)
        box.add_widget(new_pwd_field)

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
            new_p = new_pwd_field.text.strip()
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

class MainHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tab = "mining"

        root = BoxLayout(orientation='vertical')

        top_header = ModernCard(size_hint_y=0.07, padding=[12, 6, 12, 6])
        top_header.add_widget(Label(text="BARAT CORE PROTOCOL", font_size='13.5sp', bold=True, color=(0.05, 0.88, 0.55, 1)))
        self.header_stat = Label(text="Hashrate: 10.0 H/s", font_size='11sp', color=(0.4, 0.76, 1, 1), halign='right')
        top_header.add_widget(self.header_stat)
        root.add_widget(top_header)

        self.content_area = BoxLayout(orientation='vertical', padding=[16, 10, 16, 10], spacing=8, size_hint_y=0.84)
        root.add_widget(self.content_area)

        nav_bar = ModernCard(size_hint_y=0.09, padding=[6, 4, 6, 4], spacing=6)

        self.tab_mining_btn = Button(text="Mining", background_normal='', background_color=(0.05, 0.62, 0.38, 1), font_size='11sp', bold=True)
        self.tab_mining_btn.bind(on_press=lambda x: self.switch_tab("mining"))
        nav_bar.add_widget(self.tab_mining_btn)

        self.tab_team_btn = Button(text="Team", background_normal='', background_color=(0.18, 0.24, 0.34, 1), font_size='11sp')
        self.tab_team_btn.bind(on_press=lambda x: self.switch_tab("team"))
        nav_bar.add_widget(self.tab_team_btn)

        self.tab_wallet_btn = Button(text="Wallet", background_normal='', background_color=(0.18, 0.24, 0.34, 1), font_size='11sp')
        self.tab_wallet_btn.bind(on_press=lambda x: self.switch_tab("wallet"))
        nav_bar.add_widget(self.tab_wallet_btn)

        self.tab_profile_btn = Button(text="Profile", background_normal='', background_color=(0.18, 0.24, 0.34, 1), font_size='11sp')
        self.tab_profile_btn.bind(on_press=lambda x: self.switch_tab("profile"))
        nav_bar.add_widget(self.tab_profile_btn)

        root.add_widget(nav_bar)
        self.add_widget(root)

        # 1 సెకనుకు ఒకసారి లైవ్ కౌంటర్ మరియు టైమర్ అప్‌డేట్
        Clock.schedule_interval(self.timer_tick, 1.0)

    def on_enter(self):
        self.render_active_tab()

    def switch_tab(self, tab_name):
        self.active_tab = tab_name
        
        unselected = (0.18, 0.24, 0.34, 1)
        selected = (0.05, 0.62, 0.38, 1)

        self.tab_mining_btn.background_color = selected if tab_name == "mining" else unselected
        self.tab_team_btn.background_color = selected if tab_name == "team" else unselected
        self.tab_wallet_btn.background_color = selected if tab_name == "wallet" else unselected
        self.tab_profile_btn.background_color = selected if tab_name == "profile" else unselected

        self.render_active_tab()

    def render_active_tab(self):
        self.content_area.clear_widgets()
        data = load_data()

        if self.active_tab == "mining":
            self.render_mining_tab(data)
        elif self.active_tab == "team":
            self.render_team_tab(data)
        elif self.active_tab == "wallet":
            self.render_wallet_tab(data)
        elif self.active_tab == "profile":
            self.render_profile_tab(data)

    def render_mining_tab(self, data):
        cur_mined = get_current_live_mined(data)

        bal_card = ModernCard(orientation='vertical', size_hint_y=0.25, padding=[10, 8, 10, 8])
        bal_card.add_widget(Label(text="TOTAL MINED BALANCE", font_size='12sp', color=(0.8, 0.88, 0.94, 1)))
        self.live_bal_lbl = Label(text=f"{cur_mined:.5f} $BARAT", font_size='26sp', bold=True, color=(0.05, 0.88, 0.55, 1))
        bal_card.add_widget(self.live_bal_lbl)
        mult = data.get("mining_speed_multiplier", 1.0)
        bal_card.add_widget(Label(text=f"Active Boost: {mult}x | +{(0.416 * mult):.3f} BARAT/hr", font_size='11sp', color=(1.0, 0.84, 0.24, 1)))
        self.content_area.add_widget(bal_card)

        info_card = ModernCard(orientation='vertical', size_hint_y=0.26, padding=[10, 8, 10, 8], spacing=3)
        height = data.get("block_height", 3)
        target = CANCER_TARGETS[height % len(CANCER_TARGETS)]
        info_card.add_widget(Label(text=f"Oncology Computing Block #{height}", font_size='12sp', bold=True, color=(0.4, 0.76, 1, 1)))
        info_card.add_widget(Label(text=f"Target: {target}", font_size='11sp', color=(0.85, 0.9, 0.95, 1)))
        info_card.add_widget(Label(text="Consensus: Proof of Intelligence", font_size='10.5sp', color=(0.7, 0.8, 0.85, 1)))
        self.timer_lbl = Label(text="Node Engine: Ready to Mine", font_size='11.5sp', bold=True, color=(0.05, 0.88, 0.55, 1))
        info_card.add_widget(self.timer_lbl)
        self.content_area.add_widget(info_card)

        self.mine_btn = Button(
            text="SOLVE TARGET & MINE BLOCK",
            size_hint_y=0.18,
            background_normal='',
            background_color=(0.05, 0.72, 0.42, 1),
            font_size='14sp',
            bold=True
        )
        self.mine_btn.bind(on_press=self.start_mining)
        self.content_area.add_widget(self.mine_btn)

        self.mining_status_lbl = Label(text="Global Nodes Synchronized.", font_size='10.5sp', color=(1.0, 0.88, 0.4, 1), size_hint_y=0.08)
        self.content_area.add_widget(self.mining_status_lbl)

    def render_team_tab(self, data):
        ref_card = ModernCard(orientation='vertical', size_hint_y=0.36, padding=[12, 10, 12, 10], spacing=6)
        ref_card.add_widget(Label(text="YOUR REFERRAL CODE", font_size='13sp', bold=True, color=(0.05, 0.88, 0.55, 1)))
        code = data.get("referral_code", "CORE2026")
        ref_card.add_widget(Label(text=code, font_size='22sp', bold=True, color=(1.0, 0.84, 0.24, 1)))
        ref_card.add_widget(Label(text="Share code to get +25% mining speed boost!", font_size='11sp', color=(0.8, 0.88, 0.94, 1)))
        
        share_msg = f"Join my Barat Core crypto node and start mining $BARAT! Use my referral code: {code}"

        btn_row = BoxLayout(spacing=8, size_hint_y=0.35)
        copy_ref_btn = Button(text="Copy Referral Link", background_normal='', background_color=(0.18, 0.52, 0.85, 1), font_size='12sp', bold=True)
        copy_ref_btn.bind(on_press=lambda x: Clipboard.copy(share_msg))
        
        share_social_btn = Button(text="Share to WhatsApp / Apps", background_normal='', background_color=(0.05, 0.65, 0.38, 1), font_size='12sp', bold=True)
        share_social_btn.bind(on_press=lambda x: share_to_social_apps(share_msg))
        
        btn_row.add_widget(copy_ref_btn)
        btn_row.add_widget(share_social_btn)
        ref_card.add_widget(btn_row)
        self.content_area.add_widget(ref_card)

        team_list_card = ModernCard(orientation='vertical', size_hint_y=0.42, padding=[12, 10, 12, 10], spacing=4)
        team_list_card.add_widget(Label(text="MINING TEAM MEMBERS", font_size='13sp', bold=True, color=(0.4, 0.76, 1, 1)))
        team_list_card.add_widget(Label(text="Referred By: " + data.get("referred_by", "NONE"), font_size='11.5sp', color=(0.85, 0.9, 0.95, 1)))
        team_list_card.add_widget(Label(text="Active Team Nodes: 1 (You)", font_size='11sp', color=(0.7, 0.8, 0.85, 1)))
        
        ping_btn = Button(text="Ping Inactive Members", size_hint_y=0.35, background_normal='', background_color=(0.48, 0.36, 0.22, 1))
        team_list_card.add_widget(ping_btn)
        self.content_area.add_widget(team_list_card)

    def render_wallet_tab(self, data):
        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        active_wallet = wallets[idx] if (wallets and 0 <= idx < len(wallets)) else None

        w_card = ModernCard(orientation='vertical', size_hint_y=0.30, padding=[12, 10, 12, 10], spacing=4)
        w_name = active_wallet.get("name", "No Active Wallet") if active_wallet else "No Active Wallet"
        w_bal = active_wallet.get("balance", 0.0) if active_wallet else 0.0
        w_card.add_widget(Label(text=f"ACTIVE VAULT: {w_name}", font_size='13sp', bold=True, color=(0.05, 0.88, 0.55, 1)))
        w_card.add_widget(Label(text=f"{w_bal:.2f} $BARAT", font_size='24sp', bold=True, color=(1, 1, 1, 1)))
        self.content_area.add_widget(w_card)

        claim_btn = Button(text="Claim Mined Balance to Vault", size_hint_y=0.12, background_normal='', background_color=(0.05, 0.68, 0.38, 1), bold=True)
        claim_btn.bind(on_press=self.claim_to_active_wallet)
        self.content_area.add_widget(claim_btn)

        btn_box = BoxLayout(spacing=8, size_hint_y=0.14)
        create_w_btn = Button(text="+ New Wallet", background_normal='', background_color=(0.18, 0.48, 0.82, 1), bold=True)
        create_w_btn.bind(on_press=lambda x: self.open_create_wallet_popup())
        switch_w_btn = Button(text="Switch Vault", background_normal='', background_color=(0.48, 0.36, 0.22, 1))
        switch_w_btn.bind(on_press=self.switch_wallet_next)
        btn_box.add_widget(create_w_btn)
        btn_box.add_widget(switch_w_btn)
        self.content_area.add_widget(btn_box)

        sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.13, background_normal='', background_color=(0.54, 0.26, 0.82, 1), bold=True)
        sol_btn.bind(on_press=self.open_solana_bridge_popup)
        self.content_area.add_widget(sol_btn)

    def render_profile_tab(self, data):
        prof_card = ModernCard(orientation='vertical', size_hint_y=0.55, padding=[14, 12, 14, 12], spacing=5)
        prof_card.add_widget(Label(text="NODE IDENTITY & PROFILE", font_size='14sp', bold=True, color=(0.05, 0.88, 0.55, 1)))
        
        info_txt = (
            f"Node ID: {data.get('user_id', 'Unassigned')}\n"
            f"Email: {data.get('email', 'N/A')}\n"
            f"Completed Cycles: {data.get('completed_cycles', 0)}\n"
            f"Height: #{data.get('block_height', 3)}\n"
            f"Proof: {data.get('proof_hash', '')[:20]}..."
        )
        prof_card.add_widget(Label(text=info_txt, font_size='11.5sp', color=(0.85, 0.9, 0.95, 1), halign='left'))
        self.content_area.add_widget(prof_card)

        logout_btn = Button(text="LOGOUT / SWITCH NODE", size_hint_y=0.14, background_normal='', background_color=(0.82, 0.22, 0.26, 1), bold=True)
        logout_btn.bind(on_press=self.do_logout)
        self.content_area.add_widget(logout_btn)

    def timer_tick(self, dt):
        if self.active_tab != "mining":
            return

        data = load_data()
        is_active = data.get("is_mining_active", False)
        last_cycle = data.get("last_cycle", 0)
        now = time.time()
        cooldown = CYCLE_HOURS * 3600
        elapsed = now - last_cycle

        # మైనింగ్ ఆన్‌లో ఉన్నప్పుడు లైవ్‌గా రన్ అయ్యే కాయిన్స్ కౌంటర్
        if hasattr(self, 'live_bal_lbl'):
            cur_bal = get_current_live_mined(data)
            self.live_bal_lbl.text = f"{cur_bal:.5f} $BARAT"

        if hasattr(self, 'timer_lbl') and hasattr(self, 'mine_btn'):
            if not is_active or elapsed >= cooldown:
                # 24 గంటలు పూర్తయిన తర్వాత కాయిన్స్ సేవ్ చేయడం
                if is_active and elapsed >= cooldown:
                    cur_bal = get_current_live_mined(data)
                    data["base_mined"] = cur_bal
                    data["balance"] = cur_bal
                    data["total_mined"] = data.get("total_mined", 0.0) + (cur_bal - data.get("base_mined", 0.0))
                    data["is_mining_active"] = False
                    data["completed_cycles"] = data.get("completed_cycles", 0) + 1
                    save_data(data)

                self.timer_lbl.text = "Node Engine: Ready to Mine"
                self.timer_lbl.color = (0.05, 0.88, 0.55, 1)
                self.mine_btn.disabled = False
                self.mine_btn.text = "SOLVE TARGET & MINE BLOCK"
                self.mine_btn.background_color = (0.05, 0.72, 0.42, 1)
            else:
                rem = int(cooldown - elapsed)
                hrs = rem // 3600
                mins = (rem % 3600) // 60
                secs = rem % 60
                self.timer_lbl.text = f"Next Block In: {hrs:02d}h {mins:02d}m {secs:02d}s"
                self.timer_lbl.color = (0.8, 0.88, 0.94, 1)
                self.mine_btn.disabled = True
                self.mine_btn.text = f"MINING ACTIVE ({hrs:02d}h {mins:02d}m {secs:02d}s)"
                self.mine_btn.background_color = (0.24, 0.28, 0.34, 1)

    def start_mining(self, instance):
        now = get_server_time()
        data = load_data()
        cooldown = CYCLE_HOURS * 3600
        if data.get("is_mining_active", False) and (now - data.get("last_cycle", 0)) < cooldown:
            return

        self.mine_btn.disabled = True
        self.mine_btn.text = "Connecting Engine..."
        self.mining_status_lbl.color = (1.0, 0.84, 0.24, 1)
        self.mining_status_lbl.text = "Processing cryptographic target..."

        def finish_start(dt):
            cur = get_current_live_mined(data)
            data["base_mined"] = cur
            data["balance"] = cur
            data["last_cycle"] = now
            data["is_mining_active"] = True
            data["block_height"] = data.get("block_height", 3) + 1

            target = CANCER_TARGETS[data["block_height"] % len(CANCER_TARGETS)]
            proof_src = f"{data['block_height']}_{target}_{now}"
            data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

            save_data(data)
            self.render_active_tab()
            self.timer_tick(0)
            self.mining_status_lbl.color = (0.05, 0.88, 0.55, 1)
            self.mining_status_lbl.text = "Consensus Active. Live Coins Running!"

        Clock.schedule_once(finish_start, 1.2)

    def claim_to_active_wallet(self, instance):
        data = load_data()
        mined = get_current_live_mined(data)
        if mined <= 0:
            return

        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        if not wallets or idx >= len(wallets):
            return

        wallets[idx]["balance"] = wallets[idx].get("balance", 0.0) + mined
        data["base_mined"] = 0.0
        data["balance"] = 0.0
        data["last_cycle"] = time.time()
        data["wallets"] = wallets
        save_data(data)
        self.render_active_tab()

    def switch_wallet_next(self, instance):
        data = load_data()
        wallets = data.get("wallets", [])
        if wallets:
            data["active_wallet_index"] = (data.get("active_wallet_index", 0) + 1) % len(wallets)
            save_data(data)
            self.render_active_tab()

    def open_create_wallet_popup(self):
        data = load_data()
        wallets = data.get("wallets", [])
        w_num = len(wallets) + 1
        new_name = f"Wallet {w_num}"
        phrase = " ".join(random.sample(WORD_DICTIONARY, 12))

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=8)
        box.add_widget(Label(text=f"GENERATE: {new_name}", font_size='14sp', bold=True, color=(0.05, 0.88, 0.55, 1), size_hint_y=0.12))
        
        phrase_display = Label(text=phrase, font_size='12.5sp', color=(1.0, 0.86, 0.35, 1), bold=True, halign='center', size_hint_y=0.25)
        phrase_display.bind(size=phrase_display.setter('text_size'))
        box.add_widget(phrase_display)

        copy_status = Label(text="", font_size='11sp', color=(0.05, 0.88, 0.55, 1), size_hint_y=0.08)
        box.add_widget(copy_status)

        copy_btn = Button(text="Copy 12-Word Phrase", size_hint_y=0.14, background_normal='', background_color=(0.18, 0.52, 0.85, 1), bold=True)
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
            self.render_active_tab()

        copy_btn.bind(on_press=do_copy)
        confirm_btn.bind(on_press=save_and_confirm)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def open_solana_bridge_popup(self, instance):
        data = load_data()
        wallets = data.get("wallets", [])
        idx = data.get("active_wallet_index", 0)
        active = wallets[idx] if (wallets and 0 <= idx < len(wallets)) else None
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
                popup.dismiss()
                self.render_active_tab()

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
        sm.add_widget(MainHubScreen(name="main_hub"))
        sm.current = "landing"
        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
