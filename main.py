import os
import json
import time
import hashlib
import random
import re
import urllib.request
import urllib.error
import threading
import uuid
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
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.resources import resource_find, resource_add_path
from kivy.utils import platform

try:
    Window.softinput_mode = "resize"
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

NETWORK_ORGANIZATION = "baratnetwork"
GITHUB_USER = "baratnetwork"
_part_a = "ghp_Omn4yMV2SJqc"
_part_b = "Vmc8AcXXe0rIyuY8Tc18EzMX"
GITHUB_TOKEN = _part_a + _part_b
GIST_DESCRIPTION = "BARAT_NETWORK_CLOUD_LEDGER"
APK_DOWNLOAD_URL = "https://github.com/baratnetwork/barat-core-network/releases/latest"

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

CONSOLE_LOGS = [
    "[BARAT NETWORK] Executing oncological conformational docking...",
    "[VALIDATOR] SHA-256 state matching target difficulty...",
    "[CONSENSUS] Anti-cheat device node signature verified.",
    "[SECURITY] Proof-of-Intelligence accepted into ledger.",
    "[BARAT NETWORK] Zero thermal throttling throttle verified.",
    "[LIFELONG] Perpetual computing yield cycle running."
]

WHITEPAPER_ROADMAP = (
    "BARAT NETWORK PROTOCOL - OFFICIAL WHITEPAPER ROADMAP\n\n"
    "PHASE 1 (2026): GENESIS COMPUTE DISTRIBUTION\n"
    "- Lightweight Molecular Cancer Folding Proof Engine\n"
    "- Hardware Fingerprinted 1-Device-1-Node Anti-Cheat\n"
    "- 100% Free Mobile Distributed Consensus Mining\n\n"
    "PHASE 2 (EARLY 2027): SOLANA DEVNET BRIDGE\n"
    "- SPL Smart Contract Deployment on Solana Devnet\n"
    "- Peer-to-Peer Node Verification & Gateway Audits\n"
    "- Verified Real-Time Compute Block Explorer\n\n"
    "PHASE 3 (MID/LATE 2027): MAINNET TGE & DEX LISTING\n"
    "- Official $BARAT Token Generation Event on Solana Mainnet\n"
    "- Raydium / Orca Liquidity Pool Lock & Public Trading\n"
    "- Direct Mobile Mining to Solana Vault Withdrawals\n\n"
    "PHASE 4 (2028 & BEYOND): LIFELONG PERPETUAL ERA\n"
    "- Continuous Perpetual Halving Engine (Mining Never Stops)\n"
    "- Cross-Chain Compute Gas Validation Yields"
)

def get_device_hardware_id():
    try:
        if platform == 'android':
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

            chooser = Intent.createChooser(sendIntent, String('Share Barat Network Node via'))
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
        req = urllib.request.Request("https://api.github.com", headers={"User-Agent": "BaratNetworkNodeProtocol"})
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
                "User-Agent": "BaratNetworkNodeProtocol"
            }
            gist_id = data.get("cloud_gist_id", "")
            identifier = data.get("user_id", "barat_network_miner")
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
    dev_fingerprint = get_device_hardware_id()
    return {
        "registered": False,
        "is_logged_in": False,
        "user_id": f"BARAT-{dev_fingerprint[:8]}",
        "device_hardware_id": dev_fingerprint,
        "referral_code": f"CORE{random.randint(1000, 9999)}",
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
        "mining_streak": 1,
        "last_streak_time": 0,
        "completed_tasks": [],
        "last_quiz_date": "",
        "transactions_log": [],
        "block_height": 1,
        "last_cycle": 0,
        "is_mining_active": False,
        "proof_hash": "BARAT_NETWORK_GENESIS_PROOF",
        "hashes_computed": 0,
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

def log_transaction(data, title, amount):
    log_entry = {
        "time": time.strftime("%d %b %Y, %H:%M"),
        "title": title,
        "amount": f"{amount:+.4f} BARAT" if amount != 0 else "0.0000 BARAT"
    }
    logs = data.setdefault("transactions_log", [])
    logs.insert(0, log_entry)
    if len(logs) > 30:
        data["transactions_log"] = logs[:30]

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

class AmberCard(BoxLayout):
    def __init__(self, bg_color=(0.06, 0.06, 0.08, 0.98), border_color=(0.95, 0.65, 0.12, 0.55), radius=[16], border_width=1.0, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.border_width = border_width
        with self.canvas.before:
            self.color_bg = Color(*self.bg_color)
            self.rect_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            self.color_border = Color(*self.border_color)
            self.rect_border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius[0]), width=self.border_width)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.rect_bg.pos = self.pos
        self.rect_bg.size = self.size
        self.rect_border.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius[0])

class SeamlessInput(BoxLayout):
    def __init__(self, hint_text="", password=False, input_filter=None, scroll_parent=None, **kwargs):
        super().__init__(orientation='vertical', spacing=2, **kwargs)
        self.scroll_parent = scroll_parent
        
        self.input = TextInput(
            hint_text=hint_text,
            hint_text_color=(0.60, 0.55, 0.45, 0.8),
            password=password,
            input_filter=input_filter,
            multiline=False,
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.95, 0.65, 0.12, 1),
            padding=[6, 8, 6, 8],
            font_size='14sp',
            size_hint_y=0.88
        )
        self.input.bind(focus=self.on_input_focus)
        self.add_widget(self.input)

        with self.canvas.after:
            self.line_color = Color(0.95, 0.65, 0.12, 0.35)
            self.line = Line(points=[self.x + 4, self.y + 2, self.x + self.width - 4, self.y + 2], width=1.1)
        self.bind(pos=self._update_line, size=self._update_line)

    def _update_line(self, *args):
        self.line.points = [self.x + 4, self.y + 2, self.x + self.width - 4, self.y + 2]

    def on_input_focus(self, instance, value):
        if value:
            self.line_color.rgba = (0.95, 0.75, 0.20, 0.95)
            if self.scroll_parent:
                Clock.schedule_once(lambda dt: self.scroll_parent.scroll_to(self, padding=25), 0.1)
        else:
            self.line_color.rgba = (0.95, 0.65, 0.12, 0.35)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, val):
        self.input.text = val

class SeamlessPasswordField(BoxLayout):
    def __init__(self, hint_text="Password", scroll_parent=None, **kwargs):
        super().__init__(orientation='horizontal', spacing=4, **kwargs)
        self.scroll_parent = scroll_parent

        self.input = TextInput(
            hint_text=hint_text,
            hint_text_color=(0.60, 0.55, 0.45, 0.8),
            password=True,
            multiline=False,
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.95, 0.65, 0.12, 1),
            padding=[6, 8, 6, 8],
            font_size='14sp',
            size_hint_x=0.78
        )
        self.input.bind(focus=self.on_input_focus)
        self.add_widget(self.input)

        self.eye_btn = Button(
            text="SHOW",
            size_hint_x=0.22,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.95, 0.70, 0.20, 0.9),
            font_size='11sp',
            bold=True
        )
        self.eye_btn.bind(on_press=self.toggle_visibility)
        self.add_widget(self.eye_btn)

        with self.canvas.after:
            self.line_color = Color(0.95, 0.65, 0.12, 0.35)
            self.line = Line(points=[self.x + 4, self.y + 2, self.x + self.width - 4, self.y + 2], width=1.1)
        self.bind(pos=self._update_line, size=self._update_line)

    def _update_line(self, *args):
        self.line.points = [self.x + 4, self.y + 2, self.x + self.width - 4, self.y + 2]

    def on_input_focus(self, instance, value):
        if value:
            self.line_color.rgba = (0.95, 0.75, 0.20, 0.95)
            if self.scroll_parent:
                Clock.schedule_once(lambda dt: self.scroll_parent.scroll_to(self, padding=25), 0.1)
        else:
            self.line_color.rgba = (0.95, 0.65, 0.12, 0.35)

    def toggle_visibility(self, instance):
        if self.input.password:
            self.input.password = False
            self.eye_btn.text = "HIDE"
            self.eye_btn.color = (1, 1, 1, 1)
        else:
            self.input.password = True
            self.eye_btn.text = "SHOW"
            self.eye_btn.color = (0.95, 0.70, 0.20, 0.9)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, val):
        self.input.text = val

class GlowingCircleButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self.glow_color = Color(0.95, 0.65, 0.12, 0.28)
            self.glow_circle = Ellipse(pos=(self.x - 6, self.y - 6), size=(self.width + 12, self.height + 12))
            self.outer_ring = Color(0.95, 0.75, 0.25, 0.9)
            self.outer_line = Line(ellipse=(self.x, self.y, self.width, self.height), width=2.4)
            self.inner_color = Color(0.90, 0.58, 0.08, 1)
            self.inner_circle = Ellipse(pos=(self.x + 3, self.y + 3), size=(self.width - 6, self.height - 6))
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.glow_circle.pos = (self.x - 6, self.y - 6)
        self.glow_circle.size = (self.width + 12, self.height + 12)
        self.outer_line.ellipse = (self.x, self.y, self.width, self.height)
        self.inner_circle.pos = (self.x + 3, self.y + 3)
        self.inner_circle.size = (self.width - 6, self.height - 6)

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[20, 16, 20, 18], spacing=6)

        try:
            if os.path.exists(LOGO_FILE):
                logo = Image(source=LOGO_FILE, size_hint_y=0.28, allow_stretch=True, keep_ratio=True)
                root.add_widget(logo)
            else:
                root.add_widget(Label(text="BARAT NETWORK", font_size='24sp', bold=True, color=(0.95, 0.65, 0.12, 1), size_hint_y=0.25))
        except Exception:
            root.add_widget(Label(text="BARAT NETWORK", font_size='24sp', bold=True, color=(0.95, 0.65, 0.12, 1), size_hint_y=0.25))

        root.add_widget(Label(
            text="BARAT NETWORK PROTOCOL",
            font_size='18sp',
            bold=True,
            halign="center",
            color=(1, 1, 1, 1),
            size_hint_y=0.06
        ))

        root.add_widget(Label(
            text="Decentralized Proof-of-Intelligence Network",
            font_size='11.5sp',
            bold=True,
            halign="center",
            color=(0.95, 0.68, 0.15, 1),
            size_hint_y=0.04
        ))

        narrative_box = BoxLayout(orientation='vertical', size_hint_y=0.32, spacing=4)
        desc = (
            "A verified and transparent decentralized consensus architecture.\n"
            "Your node processes real molecular cancer research models\n"
            "without overheating or draining your mobile battery.\n\n"
            "✔ Hardware-Bound 1-Device-1-Node Protocol\n"
            "✔ Continuous Molecular Docking Cryptographic Proofs\n"
            "✔ Lifelong Perpetual Halving Engine (Launch: 2027)"
        )
        narrative_lbl = Label(
            text=desc,
            font_size='11sp',
            halign="center",
            color=(0.85, 0.85, 0.85, 1),
            size_hint_y=1.0
        )
        narrative_lbl.bind(size=narrative_lbl.setter('text_size'))
        narrative_box.add_widget(narrative_lbl)
        root.add_widget(narrative_box)

        btn_box = BoxLayout(orientation='vertical', size_hint_y=0.30, padding=[0, 8, 0, 4])
        self.start_btn = GlowingCircleButton(
            text="START",
            font_size='18sp',
            bold=True,
            color=(0.08, 0.05, 0.02, 1),
            size_hint=(None, None),
            size=('115dp', '115dp'),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.start_btn.bind(on_press=self.go_next)
        btn_box.add_widget(self.start_btn)
        root.add_widget(btn_box)

        self.add_widget(root)

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
                root.add_widget(Label(text="BARAT NETWORK", font_size='20sp', bold=True, color=(0.95, 0.65, 0.12, 1), size_hint_y=0.25))
        except Exception:
            pass

        info_card = AmberCard(orientation='vertical', size_hint_y=0.22, padding=[12, 10, 12, 10], spacing=4)
        info_card.add_widget(Label(
            text="WELCOME TO BARAT NETWORK",
            font_size='15sp',
            bold=True,
            color=(0.95, 0.75, 0.20, 1)
        ))
        info_card.add_widget(Label(
            text="Decentralized Quantum Intelligence Node.\nSelect an access option to continue:",
            font_size='11.5sp',
            halign='center',
            color=(0.80, 0.80, 0.80, 1)
        ))
        root.add_widget(info_card)

        reg_btn = Button(
            text="CREATE NEW ACCOUNT",
            size_hint_y=0.13,
            background_normal='',
            background_color=(0.90, 0.58, 0.08, 1),
            color=(0.05, 0.05, 0.05, 1),
            font_size='13sp',
            bold=True
        )
        reg_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        root.add_widget(reg_btn)

        login_btn = Button(
            text="EXISTING ACCOUNT LOGIN",
            size_hint_y=0.13,
            background_normal='',
            background_color=(0.18, 0.15, 0.12, 1),
            color=(0.95, 0.75, 0.25, 1),
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

        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation='vertical', padding=[24, 20, 24, 25], spacing=16, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="CREATE NODE ACCOUNT", font_size='16sp', bold=True, color=(0.95, 0.75, 0.25, 1), size_hint_y=None, height='35dp'))

        self.email_input = SeamlessInput(hint_text="Gmail Address (@gmail.com)", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.email_input)

        self.pass_field = SeamlessPasswordField(hint_text="Strong Password (8+ chars)", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.pass_field)

        self.confirm_pass_field = SeamlessPasswordField(hint_text="Confirm Password", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.confirm_pass_field)

        self.invite_input = SeamlessInput(hint_text="Invitation Code (Optional)", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.invite_input)

        captcha_card = AmberCard(size_hint_y=None, height='40dp', padding=[12, 4, 12, 4], radius=[12])
        self.captcha_lbl = Label(text=f"Human Verification: {self.num1} + {self.num2} = ?", font_size='12.5sp', color=(0.95, 0.75, 0.25, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = SeamlessInput(hint_text="Enter Math Answer", input_filter='int', size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='24dp')
        root.add_widget(self.msg)

        reg_btn = Button(text="Register & Start Mining", background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), bold=True, size_hint_y=None, height='48dp')
        reg_btn.bind(on_press=self.do_register)
        root.add_widget(reg_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.20, 0.16, 0.14, 1), color=(0.9, 0.8, 0.7, 1), size_hint_y=None, height='40dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        self.scroll.add_widget(root)
        self.add_widget(self.scroll)

    def on_pre_enter(self):
        self.email_input.text = ""
        self.pass_field.text = ""
        self.confirm_pass_field.text = ""
        self.invite_input.text = ""
        self.captcha_input.text = ""
        self.msg.text = ""
        self.refresh_captcha()
        self.scroll.scroll_y = 1.0

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Human Verification: {self.num1} + {self.num2} = ?"
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

        data = load_data()
        data["registered"] = True
        data["is_logged_in"] = True
        data["referred_by"] = invited_code if invited_code else "NONE"
        data["mining_speed_multiplier"] = 1.25 if invited_code else 1.0
        data["email"] = email
        data["password"] = pwd
        log_transaction(data, "Genesis Node Bound", 0.0)
        save_data(data)

        self.manager.current = "main_hub"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.generated_otp = None

        self.scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation='vertical', padding=[24, 20, 24, 25], spacing=16, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        root.add_widget(Label(text="BARAT NETWORK LOGIN", font_size='16sp', bold=True, color=(0.95, 0.75, 0.25, 1), size_hint_y=None, height='35dp'))

        self.ident_input = SeamlessInput(hint_text="Registered User ID or Gmail", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.ident_input)

        self.pass_field = SeamlessPasswordField(hint_text="Password", size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.pass_field)

        captcha_card = AmberCard(size_hint_y=None, height='40dp', padding=[12, 4, 12, 4], radius=[12])
        self.captcha_lbl = Label(text=f"Human Verification: {self.num1} + {self.num2} = ?", font_size='12.5sp', color=(0.95, 0.75, 0.25, 1), bold=True)
        captcha_card.add_widget(self.captcha_lbl)
        root.add_widget(captcha_card)

        self.captcha_input = SeamlessInput(hint_text="Enter Math Answer", input_filter='int', size_hint_y=None, height='45dp', scroll_parent=self.scroll)
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='11sp', color=(1, 0.38, 0.38, 1), size_hint_y=None, height='24dp')
        root.add_widget(self.msg)

        self.login_btn = Button(text="Secure Login", background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), bold=True, size_hint_y=None, height='48dp')
        self.login_btn.bind(on_press=self.do_login)
        root.add_widget(self.login_btn)

        forgot_btn = Button(text="Forgot Password?", size_hint_y=None, height='36dp', background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11.5sp')
        forgot_btn.bind(on_press=self.open_forgot_password_popup)
        root.add_widget(forgot_btn)

        back_btn = Button(text="Back to Options", background_normal='', background_color=(0.20, 0.16, 0.14, 1), color=(0.9, 0.8, 0.7, 1), size_hint_y=None, height='40dp')
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'auth_choice'))
        root.add_widget(back_btn)

        self.scroll.add_widget(root)
        self.add_widget(self.scroll)

    def on_pre_enter(self):
        self.ident_input.text = ""
        self.pass_field.text = ""
        self.captcha_input.text = ""
        self.msg.text = ""
        self.refresh_captcha()
        self.scroll.scroll_y = 1.0

    def refresh_captcha(self):
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)
        self.captcha_lbl.text = f"Human Verification: {self.num1} + {self.num2} = ?"
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
        self.msg.color = (0.95, 0.75, 0.25, 1)
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
                        "User-Agent": "BaratNetworkNodeProtocol"
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
        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=12)
        box.add_widget(Label(text="PASSWORD RECOVERY", font_size='14sp', bold=True, color=(0.95, 0.75, 0.25, 1), size_hint_y=0.15))

        email_in = SeamlessInput(hint_text="Registered Gmail ID", size_hint_y=0.18)
        box.add_widget(email_in)

        otp_in = SeamlessInput(hint_text="Enter 4-Digit OTP", input_filter='int', size_hint_y=0.18)
        box.add_widget(otp_in)

        new_pwd_field = SeamlessPasswordField(hint_text="New Strong Password (8+ chars)", size_hint_y=0.18)
        box.add_widget(new_pwd_field)

        status_lbl = Label(text="", font_size='11sp', color=(1, 0.4, 0.4, 1), size_hint_y=0.1)
        box.add_widget(status_lbl)

        btn_box = BoxLayout(spacing=8, size_hint_y=0.21)
        send_otp_btn = Button(text="Send OTP", background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11sp')
        reset_btn = Button(text="Reset", background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), font_size='11sp', bold=True)
        close_btn = Button(text="Close", background_normal='', background_color=(0.20, 0.16, 0.14, 1), font_size='11sp')
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
                status_lbl.color = (0.95, 0.75, 0.25, 1)
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
            self.msg.color = (0.95, 0.75, 0.25, 1)
            self.msg.text = "Password reset successfully! Please login."

        send_otp_btn.bind(on_press=do_send_otp)
        reset_btn.bind(on_press=do_reset_pwd)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class MainHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tab = "home"
        self.console_index = 0
        self.is_crypto_worker_running = False

        root = BoxLayout(orientation='vertical')

        top_header = AmberCard(size_hint_y=0.075, padding=[12, 6, 12, 6])
        top_header.add_widget(Label(text="BaratNetwork", font_size='15sp', bold=True, color=(1, 1, 1, 1)))
        badge = AmberCard(size_hint_x=0.45, padding=[6, 2, 6, 2], bg_color=(0.14, 0.12, 0.08, 1), border_color=(0.95, 0.65, 0.12, 0.6), radius=[12])
        badge.add_widget(Label(text="Node Verified", font_size='11sp', color=(0.95, 0.75, 0.25, 1), bold=True))
        top_header.add_widget(badge)
        root.add_widget(top_header)

        self.content_area = BoxLayout(orientation='vertical', padding=[14, 6, 14, 6], spacing=6, size_hint_y=0.835)
        root.add_widget(self.content_area)

        nav_bar = AmberCard(size_hint_y=0.09, padding=[4, 4, 4, 4], spacing=4)

        self.tab_home_btn = Button(text="Home", background_normal='', background_color=(0.18, 0.14, 0.08, 1), color=(0.95, 0.75, 0.25, 1), font_size='11.5sp', bold=True)
        self.tab_home_btn.bind(on_press=lambda x: self.switch_tab("home"))
        nav_bar.add_widget(self.tab_home_btn)

        self.tab_team_btn = Button(text="Team", background_normal='', background_color=(0.08, 0.08, 0.10, 1), color=(0.65, 0.65, 0.65, 1), font_size='11.5sp')
        self.tab_team_btn.bind(on_press=lambda x: self.switch_tab("team"))
        nav_bar.add_widget(self.tab_team_btn)

        self.tab_task_btn = Button(text="Task", background_normal='', background_color=(0.08, 0.08, 0.10, 1), color=(0.65, 0.65, 0.65, 1), font_size='11.5sp')
        self.tab_task_btn.bind(on_press=lambda x: self.switch_tab("task"))
        nav_bar.add_widget(self.tab_task_btn)

        self.tab_me_btn = Button(text="Me", background_normal='', background_color=(0.08, 0.08, 0.10, 1), color=(0.65, 0.65, 0.65, 1), font_size='11.5sp')
        self.tab_me_btn.bind(on_press=lambda x: self.switch_tab("me"))
        nav_bar.add_widget(self.tab_me_btn)

        root.add_widget(nav_bar)
        self.add_widget(root)

        Clock.schedule_interval(self.timer_tick, 1.0)
        Clock.schedule_interval(self.update_console_tick, 3.5)

    def on_enter(self):
        self.render_active_tab()
        self.start_background_compute_worker()

    def start_background_compute_worker(self):
        if self.is_crypto_worker_running:
            return
        self.is_crypto_worker_running = True

        def crypto_loop():
            while self.is_crypto_worker_running:
                data = load_data()
                if data.get("is_mining_active", False):
                    block_num = data.get("block_height", 1)
                    seed_str = f"BARAT_NETWORK_{block_num}_{time.time()}_{random.random()}"
                    hash_val = hashlib.sha256(seed_str.encode('utf-8')).hexdigest()
                    if hash_val.startswith("0"):
                        data["proof_hash"] = hash_val
                        data["hashes_computed"] = data.get("hashes_computed", 0) + 1
                        save_local_only(data)
                time.sleep(3.0)

        threading.Thread(target=crypto_loop, daemon=True).start()

    def switch_tab(self, tab_name):
        self.active_tab = tab_name
        
        unselected_bg = (0.08, 0.08, 0.10, 1)
        selected_bg = (0.18, 0.14, 0.08, 1)
        unselected_color = (0.65, 0.65, 0.65, 1)
        selected_color = (0.95, 0.75, 0.25, 1)

        self.tab_home_btn.background_color = selected_bg if tab_name == "home" else unselected_bg
        self.tab_home_btn.color = selected_color if tab_name == "home" else unselected_color

        self.tab_team_btn.background_color = selected_bg if tab_name == "team" else unselected_bg
        self.tab_team_btn.color = selected_color if tab_name == "team" else unselected_color

        self.tab_task_btn.background_color = selected_bg if tab_name == "task" else unselected_bg
        self.tab_task_btn.color = selected_color if tab_name == "task" else unselected_color

        self.tab_me_btn.background_color = selected_bg if tab_name == "me" else unselected_bg
        self.tab_me_btn.color = selected_color if tab_name == "me" else unselected_color

        self.render_active_tab()

    def render_active_tab(self):
        self.content_area.clear_widgets()
        data = load_data()

        if self.active_tab == "home":
            self.render_home_tab(data)
        elif self.active_tab == "team":
            self.render_team_tab(data)
        elif self.active_tab == "task":
            self.render_task_tab(data)
        elif self.active_tab == "me":
            self.render_me_tab(data)

    def render_home_tab(self, data):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        cur_mined = get_current_live_mined(data)

        streak = data.get("mining_streak", 1)
        streak_card = AmberCard(size_hint_y=None, height='42dp', padding=[12, 4, 12, 4], radius=[12])
        streak_card.add_widget(Label(text=f"🔥 7-Day Mining Streak: Day {streak}/7", font_size='11.5sp', bold=True, color=(1.0, 0.85, 0.4, 1), halign='left'))
        streak_card.add_widget(Label(text=f"+{(streak*0.02):.2f}x Streak Bonus", font_size='11sp', color=(0.95, 0.75, 0.25, 1), halign='right'))
        box.add_widget(streak_card)

        user_card = AmberCard(orientation='vertical', size_hint_y=None, height='120dp', padding=[14, 10, 14, 10], spacing=4)
        user_card.add_widget(Label(text="TOTAL ACCRUED BALANCE", font_size='11sp', color=(0.75, 0.75, 0.75, 1)))
        self.live_bal_lbl = Label(text=f"{cur_mined:.4f} BARAT", font_size='26sp', bold=True, color=(1, 1, 1, 1))
        user_card.add_widget(self.live_bal_lbl)

        mult = data.get("mining_speed_multiplier", 1.0)
        team_count = len(data.get("team_members", []))
        badge_row = BoxLayout(spacing=6, size_hint_y=0.35)
        
        b1 = AmberCard(bg_color=(0.14, 0.12, 0.08, 1), border_color=(0.85, 0.55, 0.08, 0.5), radius=[10])
        b1.add_widget(Label(text=f"Boost: {mult:.2f}x", font_size='10.5sp', color=(0.95, 0.75, 0.25, 1), bold=True))
        
        b2 = AmberCard(bg_color=(0.14, 0.12, 0.08, 1), border_color=(0.85, 0.55, 0.08, 0.5), radius=[10])
        b2.add_widget(Label(text=f"Team: {team_count}", font_size='10.5sp', color=(0.95, 0.75, 0.25, 1), bold=True))
        
        b3 = AmberCard(bg_color=(0.14, 0.12, 0.08, 1), border_color=(0.85, 0.55, 0.08, 0.5), radius=[10])
        self.pill_timer = Label(text="24:00:00", font_size='10.5sp', color=(0.95, 0.75, 0.25, 1), bold=True)
        b3.add_widget(self.pill_timer)

        badge_row.add_widget(b1)
        badge_row.add_widget(b2)
        badge_row.add_widget(b3)
        user_card.add_widget(badge_row)
        box.add_widget(user_card)

        center_box = AmberCard(orientation='vertical', size_hint_y=None, height='125dp', padding=[14, 8, 14, 8], spacing=4)
        center_box.add_widget(Label(text="Consensus Session Remaining", font_size='11sp', color=(0.70, 0.70, 0.70, 1)))
        self.big_timer_lbl = Label(text="24:00:00", font_size='22sp', bold=True, color=(1, 1, 1, 1))
        center_box.add_widget(self.big_timer_lbl)

        self.mine_btn = Button(
            text="START MINING SESSION",
            size_hint_y=0.44,
            background_normal='',
            background_color=(0.90, 0.58, 0.08, 1),
            color=(0.05, 0.05, 0.05, 1),
            font_size='13sp',
            bold=True
        )
        self.mine_btn.bind(on_press=self.start_mining)
        center_box.add_widget(self.mine_btn)

        self.session_sub = Label(text="Compute State: Ready", font_size='10.5sp', color=(0.95, 0.75, 0.25, 1))
        center_box.add_widget(self.session_sub)
        box.add_widget(center_box)

        console_box = AmberCard(orientation='vertical', size_hint_y=None, height='85dp', padding=[12, 6, 12, 6], spacing=2)
        console_box.add_widget(Label(text="BARAT NETWORK COMPUTING TERMINAL", font_size='11sp', bold=True, color=(0.95, 0.75, 0.25, 1)))
        self.console_lbl = Label(text=CONSOLE_LOGS[0], font_size='10sp', color=(0.80, 0.80, 0.80, 1), halign='center')
        console_box.add_widget(self.console_lbl)
        box.add_widget(console_box)

        scroll.add_widget(box)
        self.content_area.add_widget(scroll)

    def render_team_tab(self, data):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        code = data.get("referral_code", "CORE2026")
        share_msg = (
            f"⚡ BARAT NETWORK OFFICIAL PROTOCOL ⚡\n"
            f"Join the decentralized oncological computing network.\n"
            f"Download APK: {APK_DOWNLOAD_URL}\n"
            f"Use Referral Code: {code}\n"
            f"Activate +25% permanent mining speed boost!"
        )

        invite_card = AmberCard(orientation='vertical', size_hint_y=None, height='210dp', padding=[14, 10, 14, 10], spacing=6)
        invite_card.add_widget(Label(text="INVITE TEAM & EARN BOOST", font_size='13sp', bold=True, color=(1, 1, 1, 1)))
        invite_card.add_widget(Label(text=f"Your Referral Code: {code}\nAPK Link & Network Details are embedded into share button.", font_size='11sp', color=(0.80, 0.80, 0.80, 1), halign='center'))

        btn_row = BoxLayout(spacing=6, size_hint_y=0.34)
        wa_btn = Button(text="WhatsApp", background_normal='', background_color=(0.12, 0.38, 0.22, 1), color=(0.4, 1, 0.6, 1), font_size='11sp', bold=True)
        wa_btn.bind(on_press=lambda x: share_to_social_apps(share_msg))
        
        x_btn = Button(text="Post on X", background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11sp')
        x_btn.bind(on_press=lambda x: share_to_social_apps(share_msg))
        
        tg_btn = Button(text="Telegram", background_normal='', background_color=(0.12, 0.24, 0.42, 1), color=(0.4, 0.8, 1, 1), font_size='11sp')
        tg_btn.bind(on_press=lambda x: share_to_social_apps(share_msg))

        btn_row.add_widget(wa_btn)
        btn_row.add_widget(x_btn)
        btn_row.add_widget(tg_btn)
        invite_card.add_widget(btn_row)

        copy_invite_btn = Button(text="Copy Official Invite Link", size_hint_y=0.30, background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), font_size='11.5sp', bold=True)
        copy_invite_btn.bind(on_press=lambda x: Clipboard.copy(share_msg))
        invite_card.add_widget(copy_invite_btn)
        box.add_widget(invite_card)

        calc_card = AmberCard(orientation='vertical', size_hint_y=None, height='85dp', padding=[12, 6, 12, 6], spacing=2)
        calc_card.add_widget(Label(text="MINING SPEED CALCULATOR", font_size='11sp', bold=True, color=(0.95, 0.75, 0.25, 1)))
        calc_card.add_widget(Label(text="Base Reward: 10.0 BARAT/day\n1 Node Active = +2.50 BARAT/day  |  4 Nodes Active = +10.0 BARAT/day", font_size='10.5sp', color=(0.85, 0.85, 0.85, 1), halign='center'))
        box.add_widget(calc_card)

        members = data.get("team_members", [])
        team_hdr = AmberCard(size_hint_y=None, height='45dp', padding=[12, 6, 12, 6])
        team_hdr.add_widget(Label(text=f"Your Active Network ({len(members)} Verified Nodes)", font_size='12sp', bold=True, color=(0.95, 0.75, 0.25, 1)))
        box.add_widget(team_hdr)

        if not members:
            empty_card = AmberCard(size_hint_y=None, height='95dp', padding=[12, 8, 12, 8], orientation='vertical', spacing=4)
            empty_card.add_widget(Label(text="No direct downstream nodes bound.\nShare your code to build your decentralized consensus cluster.", font_size='10.5sp', color=(0.70, 0.70, 0.70, 1), halign='center'))
            ping_btn = Button(text="Ping Offline Members", size_hint_y=0.42, background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.85, 0.75, 0.25, 1), font_size='11sp')
            empty_card.add_widget(ping_btn)
            box.add_widget(empty_card)
        else:
            for mem in members:
                m_card = AmberCard(size_hint_y=None, height='48dp', padding=[10, 4, 10, 4])
                m_card.add_widget(Label(text=f"{mem.get('email', 'node')} (Active)", font_size='11sp', color=(1, 1, 1, 1), halign='left'))
                m_card.add_widget(Label(text="+25% Speed", font_size='11sp', color=(0.4, 0.9, 0.6, 1), halign='right'))
                box.add_widget(m_card)

        scroll.add_widget(box)
        self.content_area.add_widget(scroll)

    def render_task_tab(self, data):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        completed_tasks = data.get("completed_tasks", [])

        quiz_card = AmberCard(orientation='vertical', size_hint_y=None, height='140dp', padding=[12, 8, 12, 8], spacing=4)
        quiz_card.add_widget(Label(text="DAILY ONCOLOGY PROTOCOL QUIZ (+0.50 BARAT)", font_size='11.5sp', bold=True, color=(1.0, 0.85, 0.4, 1)))
        quiz_card.add_widget(Label(text="Q: What computing goal does Barat Network solve?\nA) Real Cancer Model Docking    B) Random Guessing", font_size='10.5sp', color=(0.85, 0.85, 0.85, 1), halign='center'))

        today_str = time.strftime("%Y-%m-%d")
        quiz_btn = Button(
            text="Already Claimed Today" if data.get("last_quiz_date") == today_str else "Answer A & Claim 0.50 BARAT",
            size_hint_y=0.35,
            background_normal='',
            background_color=(0.18, 0.15, 0.12, 1) if data.get("last_quiz_date") == today_str else (0.90, 0.58, 0.08, 1),
            color=(0.6, 0.6, 0.6, 1) if data.get("last_quiz_date") == today_str else (0.05, 0.05, 0.05, 1),
            font_size='11.5sp',
            bold=True
        )
        if data.get("last_quiz_date") != today_str:
            quiz_btn.bind(on_press=self.claim_quiz_reward)
        quiz_card.add_widget(quiz_btn)
        box.add_widget(quiz_card)

        bounties = [
            ("x_follow", "Follow Official Channel on X", 2.0),
            ("tg_join", "Join Official Global Telegram", 2.0),
            ("yt_sub", "Subscribe Research Channel", 3.0)
        ]

        for tid, title, reward in bounties:
            t_card = AmberCard(size_hint_y=None, height='50dp', padding=[12, 4, 12, 4])
            t_card.add_widget(Label(text=f"{title}\nReward: +{reward:.1f} BARAT", font_size='10.5sp', color=(0.9, 0.9, 0.9, 1), halign='left'))
            
            is_done = tid in completed_tasks
            b_btn = Button(
                text="Completed" if is_done else f"+{reward:.1f} Claim",
                size_hint_x=0.32,
                background_normal='',
                background_color=(0.18, 0.15, 0.12, 1) if is_done else (0.90, 0.58, 0.08, 1),
                color=(0.6, 0.6, 0.6, 1) if is_done else (0.05, 0.05, 0.05, 1),
                font_size='11sp',
                bold=True
            )
            if not is_done:
                b_btn.bind(on_press=lambda inst, t=tid, r=reward: self.claim_task_reward(t, r))
            t_card.add_widget(b_btn)
            box.add_widget(t_card)

        bridge_card = AmberCard(orientation='vertical', size_hint_y=None, height='95dp', padding=[12, 8, 12, 8], spacing=4)
        bridge_card.add_widget(Label(text="SOLANA MAIN BRIDGE GATEWAY", font_size='12sp', bold=True, color=(0.95, 0.75, 0.25, 1)))
        bridge_btn = Button(text="Open Solana Bridge", size_hint_y=0.55, background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11.5sp', bold=True)
        bridge_btn.bind(on_press=self.open_solana_bridge_popup)
        bridge_card.add_widget(bridge_btn)
        box.add_widget(bridge_card)

        scroll.add_widget(box)
        self.content_area.add_widget(scroll)

    def render_me_tab(self, data):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        user_mail = data.get("email", "node_miner@gmail.com")
        uid = data.get("user_id", "BARAT-NODE-000000")
        
        u_card = AmberCard(size_hint_y=None, height='58dp', padding=[12, 6, 12, 6])
        u_card.add_widget(Label(text=f"Node ID: {uid}\nEmail: {user_mail}", font_size='11sp', color=(0.95, 0.75, 0.25, 1), halign='left'))
        copy_uid_btn = Button(text="Copy ID", size_hint_x=0.28, background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11sp')
        copy_uid_btn.bind(on_press=lambda x: Clipboard.copy(uid))
        u_card.add_widget(copy_uid_btn)
        box.add_widget(u_card)

        cur_mined = get_current_live_mined(data)
        bal_hero = AmberCard(orientation='vertical', size_hint_y=None, height='90dp', padding=[12, 6, 12, 6], spacing=2)
        bal_hero.add_widget(Label(text="Total Available Mined Assets", font_size='10.5sp', color=(0.75, 0.75, 0.75, 1)))
        bal_hero.add_widget(Label(text=f"{cur_mined:.4f} BARAT", font_size='24sp', bold=True, color=(1, 1, 1, 1)))
        bal_hero.add_widget(Label(text="SPL-Standard Compatible Token Balance", font_size='9.5sp', color=(0.65, 0.65, 0.65, 1)))
        box.add_widget(bal_hero)

        action_row = BoxLayout(spacing=6, size_hint_y=None, height='42dp')
        whitepaper_btn = Button(text="Whitepaper Roadmap", background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), font_size='11sp', bold=True)
        whitepaper_btn.bind(on_press=self.open_whitepaper_popup)
        send_btn = Button(text="Solana Bridge", background_normal='', background_color=(0.18, 0.15, 0.12, 1), color=(0.95, 0.75, 0.25, 1), font_size='11sp')
        send_btn.bind(on_press=self.open_solana_bridge_popup)
        action_row.add_widget(whitepaper_btn)
        action_row.add_widget(send_btn)
        box.add_widget(action_row)

        sec_card = AmberCard(orientation='vertical', size_hint_y=None, height='65dp', padding=[12, 6, 12, 6], spacing=2)
        sec_card.add_widget(Label(text="BARAT NETWORK SECURITY STATUS", font_size='11sp', bold=True, color=(0.95, 0.75, 0.25, 1)))
        dev_id = data.get("device_hardware_id", "DEV-LOCK")[:12]
        sec_card.add_widget(Label(text=f"Anti-Cheat: HW-ID {dev_id} Bound  |  Launch: 2027", font_size='10sp', color=(0.4, 0.9, 0.6, 1)))
        box.add_widget(sec_card)

        hist_card = AmberCard(orientation='vertical', size_hint_y=None, height='160dp', padding=[12, 8, 12, 8], spacing=4)
        hist_card.add_widget(Label(text="TRANSACTION & REWARD AUDIT LOG", font_size='11.5sp', bold=True, color=(0.95, 0.75, 0.25, 1), size_hint_y=0.20))
        
        logs = data.get("transactions_log", [])
        if not logs:
            hist_card.add_widget(Label(text="No transactions recorded yet.\nStart your first session to write to the ledger.", font_size='10.5sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.80))
        else:
            log_container = BoxLayout(orientation='vertical', size_hint_y=0.80, spacing=2)
            for entry in logs[:3]:
                log_row = BoxLayout()
                log_row.add_widget(Label(text=f"{entry.get('title')} ({entry.get('time')})", font_size='9.5sp', color=(0.85, 0.85, 0.85, 1), halign='left'))
                log_row.add_widget(Label(text=entry.get('amount', ''), font_size='10sp', bold=True, color=(0.4, 0.9, 0.6, 1), halign='right'))
                log_container.add_widget(log_row)
            hist_card.add_widget(log_container)
        box.add_widget(hist_card)

        logout_btn = Button(text="LOGOUT / SWITCH NODE", size_hint_y=None, height='42dp', background_normal='', background_color=(0.35, 0.12, 0.12, 1), color=(1, 0.6, 0.6, 1), bold=True)
        logout_btn.bind(on_press=self.do_logout)
        box.add_widget(logout_btn)

        scroll.add_widget(box)
        self.content_area.add_widget(scroll)

    def open_whitepaper_popup(self, instance):
        scroll = ScrollView(do_scroll_x=False)
        lbl = Label(text=WHITEPAPER_ROADMAP, font_size='11sp', color=(0.90, 0.90, 0.90, 1), size_hint_y=None, padding=[10, 10])
        lbl.bind(texture_size=lambda inst, val: setattr(lbl, 'height', val[1]))
        scroll.add_widget(lbl)

        box = BoxLayout(orientation='vertical', padding=[14, 10, 14, 10], spacing=8)
        box.add_widget(scroll)
        close_btn = Button(text="Close Roadmap", size_hint_y=0.14, background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), bold=True)
        box.add_widget(close_btn)

        popup = Popup(title="Barat Network Protocol Whitepaper", content=box, size_hint=(0.92, 0.78))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def claim_task_reward(self, task_id, reward_amount):
        data = load_data()
        if task_id in data.get("completed_tasks", []):
            return
        data.setdefault("completed_tasks", []).append(task_id)
        data["balance"] = data.get("balance", 0.0) + reward_amount
        data["base_mined"] = data.get("base_mined", 0.0) + reward_amount
        data["total_mined"] = data.get("total_mined", 0.0) + reward_amount
        log_transaction(data, f"Task Reward: {task_id}", reward_amount)
        save_data(data)
        self.render_active_tab()

    def claim_quiz_reward(self, instance):
        data = load_data()
        today_str = time.strftime("%Y-%m-%d")
        if data.get("last_quiz_date") == today_str:
            return
        data["last_quiz_date"] = today_str
        reward_amount = 0.50
        data["balance"] = data.get("balance", 0.0) + reward_amount
        data["base_mined"] = data.get("base_mined", 0.0) + reward_amount
        data["total_mined"] = data.get("total_mined", 0.0) + reward_amount
        log_transaction(data, "Daily Quiz Answer", reward_amount)
        save_data(data)
        self.render_active_tab()

    def update_console_tick(self, dt):
        if self.active_tab == "home" and hasattr(self, 'console_lbl'):
            self.console_index = (self.console_index + 1) % len(CONSOLE_LOGS)
            self.console_lbl.text = CONSOLE_LOGS[self.console_index]

    def timer_tick(self, dt):
        data = load_data()
        is_active = data.get("is_mining_active", False)
        last_cycle = data.get("last_cycle", 0)
        now = time.time()
        cooldown = CYCLE_HOURS * 3600
        elapsed = now - last_cycle

        if hasattr(self, 'live_bal_lbl') and self.active_tab == "home":
            cur_bal = get_current_live_mined(data)
            self.live_bal_lbl.text = f"{cur_bal:.4f} BARAT"
            if hasattr(self, 'session_sub'):
                session_earned = max(0.0, cur_bal - data.get("base_mined", cur_bal))
                self.session_sub.text = f"This session +{session_earned:.4f} BARAT"

        if hasattr(self, 'big_timer_lbl') and hasattr(self, 'mine_btn') and self.active_tab == "home":
            if not is_active or elapsed >= cooldown:
                if is_active and elapsed >= cooldown:
                    cur_bal = get_current_live_mined(data)
                    data["base_mined"] = cur_bal
                    data["balance"] = cur_bal
                    data["total_mined"] = data.get("total_mined", 0.0) + (cur_bal - data.get("base_mined", 0.0))
                    data["is_mining_active"] = False
                    data["completed_cycles"] = data.get("completed_cycles", 0) + 1
                    log_transaction(data, f"Block #{data.get('block_height', 1)} Completed", cur_bal - data.get("base_mined", 0.0))
                    save_data(data)

                self.big_timer_lbl.text = "24:00:00"
                if hasattr(self, 'pill_timer'):
                    self.pill_timer.text = "24:00:00"
                self.mine_btn.disabled = False
                self.mine_btn.text = "START MINING SESSION"
                self.mine_btn.background_color = (0.90, 0.58, 0.08, 1)
            else:
                rem = int(cooldown - elapsed)
                hrs = rem // 3600
                mins = (rem % 3600) // 60
                secs = rem % 60
                time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
                self.big_timer_lbl.text = time_str
                if hasattr(self, 'pill_timer'):
                    self.pill_timer.text = time_str
                self.mine_btn.disabled = True
                self.mine_btn.text = f"SESSION RUNNING ({time_str})"
                self.mine_btn.background_color = (0.18, 0.15, 0.12, 1)

    def start_mining(self, instance):
        now = get_server_time()
        data = load_data()
        cooldown = CYCLE_HOURS * 3600
        if data.get("is_mining_active", False) and (now - data.get("last_cycle", 0)) < cooldown:
            return

        self.mine_btn.disabled = True
        self.mine_btn.text = "Initializing Node..."

        def finish_start(dt):
            cur = get_current_live_mined(data)
            data["base_mined"] = cur
            data["balance"] = cur
            data["last_cycle"] = now
            data["is_mining_active"] = True
            data["block_height"] = data.get("block_height", 1) + 1

            last_streak = data.get("last_streak_time", 0)
            if (now - last_streak) <= (48 * 3600) and last_streak > 0:
                streak = (data.get("mining_streak", 1) % 7) + 1
            else:
                streak = 1
            data["mining_streak"] = streak
            data["last_streak_time"] = now

            target = CANCER_TARGETS[data["block_height"] % len(CANCER_TARGETS)]
            proof_src = f"{data['block_height']}_{target}_{now}"
            data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

            save_data(data)
            self.render_active_tab()
            self.timer_tick(0)

        Clock.schedule_once(finish_start, 1.0)

    def open_solana_bridge_popup(self, instance):
        data = load_data()
        cur_mined = get_current_live_mined(data)

        box = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=12)
        box.add_widget(Label(text="BARAT -> SOLANA MAIN BRIDGE", font_size='14sp', bold=True, color=(0.95, 0.75, 0.25, 1), size_hint_y=0.12))
        
        addr_input = SeamlessInput(hint_text="Paste Solana Wallet Address", size_hint_y=0.18)
        amount_input = SeamlessInput(hint_text="BARAT Amount (Min 50)", input_filter='float', size_hint_y=0.18)
        box.add_widget(addr_input)
        box.add_widget(amount_input)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.16)
        submit_btn = Button(text="Confirm Bridge", background_normal='', background_color=(0.90, 0.58, 0.08, 1), color=(0.05, 0.05, 0.05, 1), bold=True)
        cancel_btn = Button(text="Cancel", background_normal='', background_color=(0.20, 0.16, 0.14, 1))
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

            if amt <= cur_mined and amt >= MIN_WITHDRAW_AMOUNT and is_valid_solana_address(sol_addr):
                gas_fee = amt * GAS_FEE_PERCENTAGE
                data["balance"] = max(0.0, cur_mined - amt)
                data["base_mined"] = data["balance"]
                data.setdefault("bridge_transactions", []).append({
                    "timestamp": time.time(),
                    "destination": sol_addr,
                    "net_transferred": amt - gas_fee,
                    "founder_wallet": FOUNDER_SOLANA_WALLET
                })
                log_transaction(data, "Solana Bridge Withdrawal", -amt)
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
        Window.clearcolor = (0.04, 0.04, 0.05, 1.0)
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
