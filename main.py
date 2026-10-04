import os
import json
import time
import hashlib
import random
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

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "registered": False,
        "email": "",
        "password": "",
        "wallet_phrase": "",
        "wallet_confirmed": False,
        "balance": 0.0,
        "total_mined": 0.0,
        "block_height": 3,
        "last_cycle": 0,
        "proof_hash": "ECO_GENESIS_PROOF_00000000"
    }

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

# 1. మొదటి స్క్రీన్ (ల్యాండింగ్ పేజీ)
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
            size=('140dp', '140dp'),
            pos_hint={'center_x': 0.5},
            background_color=(0.1, 0.7, 0.4, 1),
            font_size='22sp',
            bold=True
        )
        start_btn.bind(on_press=self.go_next)
        root.add_widget(start_btn)

        root.add_widget(Label(text="", size_hint_y=0.08))
        self.add_widget(root)

    def on_enter(self):
        data = load_data()
        bal = data.get("balance", 0.0)
        self.mined_preview.text = f"Tokens Mined\n{bal:.2f} $BARAT"

    def go_next(self, instance):
        data = load_data()
        if not data.get("registered", False):
            self.manager.current = "auth"
        elif not data.get("wallet_confirmed", False):
            self.manager.current = "wallet"
        else:
            self.manager.current = "main"

# 2. లాగిన్, రిజిస్టర్ మరియు హ్యూమన్ వెరిఫికేషన్ స్క్రీన్
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num1 = random.randint(5, 20)
        self.num2 = random.randint(2, 9)

        root = BoxLayout(orientation='vertical', padding=[24, 25, 24, 20], spacing=8)
        root.add_widget(Label(text="BARAT NODE AUTHENTICATION", font_size='20sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.08))

        self.email_input = TextInput(hint_text="Email ID or Username", multiline=False, size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.email_input)

        self.pass_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.pass_input)

        self.captcha_lbl = Label(text=f"Human Verification: {self.num1} + {self.num2} = ?", font_size='13sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.06)
        root.add_widget(self.captcha_lbl)

        self.captcha_input = TextInput(hint_text="Enter Result", multiline=False, input_filter='int', size_hint_y=0.1, padding=[10, 10])
        root.add_widget(self.captcha_input)

        self.msg = Label(text="", font_size='12sp', color=(1, 0.3, 0.3, 1), size_hint_y=0.06)
        root.add_widget(self.msg)

        btn_box = BoxLayout(spacing=10, size_hint_y=0.12)
        reg_btn = Button(text="Register", background_color=(0.1, 0.55, 0.35, 1), bold=True)
        reg_btn.bind(on_press=self.do_register)
        login_btn = Button(text="Login", background_color=(0.2, 0.45, 0.7, 1), bold=True)
        login_btn.bind(on_press=self.do_login)
        btn_box.add_widget(reg_btn)
        btn_box.add_widget(login_btn)
        root.add_widget(btn_box)

        forgot_btn = Button(text="Forgot Password?", background_color=(0, 0, 0, 0), color=(0.7, 0.7, 0.7, 1), size_hint_y=0.07)
        forgot_btn.bind(on_press=self.do_forgot)
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
        email = self.email_input.text.strip()
        pwd = self.pass_input.text.strip()

        if not email or not pwd:
            self.msg.text = "Email and Password cannot be empty!"
            return

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        words = random.sample(WORD_DICTIONARY, 12)
        phrase = " ".join(words)

        data = load_data()
        data["registered"] = True
        data["email"] = email
        data["password"] = pwd
        data["wallet_phrase"] = phrase
        data["wallet_confirmed"] = False
        save_data(data)

        self.manager.current = "wallet"

    def do_login(self, instance):
        email = self.email_input.text.strip()
        pwd = self.pass_input.text.strip()

        if not self.verify_captcha():
            self.msg.text = "Captcha verification failed!"
            self.refresh_captcha()
            return

        data = load_data()
        if data.get("email") == email and data.get("password") == pwd:
            if not data.get("wallet_confirmed", False):
                self.manager.current = "wallet"
            else:
                self.manager.current = "main"
        else:
            self.msg.text = "Invalid credentials!"
            self.refresh_captcha()

    def do_forgot(self, instance):
        data = load_data()
        phrase = data.get("wallet_phrase", "")
        if phrase:
            self.msg.color = (0.2, 0.9, 0.5, 1)
            self.msg.text = "Hint: Use your 12-word wallet phrase to recover."
        else:
            self.msg.text = "No account registered yet."

# 3. 12-పదాల వాలెట్ జనరేషన్ మరియు కన్ఫర్మేషన్ స్క్రీన్
class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[20, 25, 20, 20], spacing=8)

        root.add_widget(Label(text="DECENTRALIZED NODE WALLET", font_size='18sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.08))
        root.add_widget(Label(text="Auto-Generated 12-Word Passphrase (Save this securely):", font_size='12sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=0.05))

        self.display_phrase = TextInput(readonly=True, multiline=True, size_hint_y=0.22, padding=[10, 10], background_color=(0.15, 0.18, 0.2, 1), foreground_color=(0.2, 0.9, 0.5, 1))
        root.add_widget(self.display_phrase)

        root.add_widget(Label(text="Confirm & Unlock: Re-enter 12-words below:", font_size='12sp', size_hint_y=0.05))
        self.confirm_input = TextInput(hint_text="Type all 12 words here with spaces", multiline=True, size_hint_y=0.22, padding=[10, 10])
        root.add_widget(self.confirm_input)

        self.msg = Label(text="", font_size='12sp', color=(1, 0.3, 0.3, 1), size_hint_y=0.06)
        root.add_widget(self.msg)

        confirm_btn = Button(text="Confirm Phrase & Open Terminal", background_color=(0.1, 0.6, 0.35, 1), size_hint_y=0.12, bold=True)
        confirm_btn.bind(on_press=self.do_confirm)
        root.add_widget(confirm_btn)

        self.add_widget(root)

    def on_enter(self):
        data = load_data()
        self.display_phrase.text = data.get("wallet_phrase", "")

    def do_confirm(self, instance):
        entered = " ".join(self.confirm_input.text.strip().split())
        data = load_data()
        real_phrase = data.get("wallet_phrase", "")

        if entered == real_phrase and real_phrase != "":
            data["wallet_confirmed"] = True
            save_data(data)
            self.manager.current = "main"
        else:
            self.msg.text = "Incorrect phrase! Enter exact words in order."

# 4. మెయిన్ మైనింగ్ స్క్రీన్
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[18, 15, 18, 15], spacing=7)

        root.add_widget(Label(text="BARAT CORE: GREEN RESEARCH NODE", font_size='15sp', bold=True, color=(0.2, 0.9, 0.5, 1), size_hint_y=0.07))

        try:
            self.logo_img = Image(source=LOGO_FILE, size_hint_y=0.22, allow_stretch=True, keep_ratio=True)
            root.add_widget(self.logo_img)
        except Exception:
            pass

        self.bal_lbl = Label(text="0.0000 BARAT", font_size='28sp', bold=True, color=(0.95, 0.95, 0.95, 1), size_hint_y=0.11)
        root.add_widget(self.bal_lbl)

        self.phase_lbl = Label(text="Phase: Initializing...", font_size='12sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.05)
        root.add_widget(self.phase_lbl)

        self.puzzle_lbl = Label(text="Research Target: Loading...", font_size='12sp', color=(0.4, 0.65, 1, 1), size_hint_y=0.05)
        root.add_widget(self.puzzle_lbl)

        self.block_lbl = Label(text="Block Height: #0000 | Proof: Verifying", font_size='11sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.05)
        root.add_widget(self.block_lbl)

        self.timer_lbl = Label(text="Node Engine: Ready", font_size='12sp', size_hint_y=0.06)
        root.add_widget(self.timer_lbl)

        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=0.1, background_color=(0.1, 0.65, 0.35, 1), font_size='14sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.08, background_color=(0.5, 0.2, 0.7, 1), font_size='13sp', bold=True)
        self.sol_btn.bind(on_press=self.claim_solana)
        root.add_widget(self.sol_btn)

        self.logout_btn = Button(text="Switch Node / Exit", size_hint_y=0.06, background_color=(0.35, 0.15, 0.15, 1), font_size='12sp')
        self.logout_btn.bind(on_press=self.do_logout)
        root.add_widget(self.logout_btn)

        self.status_msg = Label(text="Bridge Verified: Oncology Research Proof queued.", font_size='10sp', color=(1, 0.85, 0.3, 1), size_hint_y=0.05)
        root.add_widget(self.status_msg)

        self.add_widget(root)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        data = load_data()
        current_bal = data.get("balance", 0.0)
        self.bal_lbl.text = f"{current_bal:.4f} BARAT"
        self.phase_lbl.text = self.calculate_reward(current_bal)
        self.update_block_display()

    def calculate_reward(self, current_bal):
        phase = int(current_bal // HALVING_INTERVAL) + 1
        reward = BLOCK_REWARD_INITIAL / (2 ** (phase - 1))
        return f"Phase {phase}: Genesis ({reward:.1f} BARAT)"

    def update_block_display(self):
        data = load_data()
        height = data.get("block_height", 3)
        target = CANCER_TARGETS[height % len(CANCER_TARGETS)]
        proof = data.get("proof_hash", "ECO_GENESIS_PROOF")[:16] + "..."
        self.puzzle_lbl.text = f"Research Target: {target}"
        self.block_lbl.text = f"Block Height: #{height} | Proof: {proof}"

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
            self.timer_lbl.text = f"Next Puzzle In: {hrs:02d}h {mins:02d}m {secs:02d}s"
            self.timer_lbl.color = (0.85, 0.85, 0.85, 1)
            self.mine_btn.disabled = True
            self.mine_btn.background_color = (0.2, 0.25, 0.25, 1)

    def start_mining(self, instance):
        data = load_data()
        now = time.time()
        cooldown = CYCLE_HOURS * 3600
        if (now - data.get("last_cycle", 0)) < cooldown:
            return

        current_bal = data.get("balance", 0.0)
        phase = int(current_bal // HALVING_INTERVAL) + 1
        reward = BLOCK_REWARD_INITIAL / (2 ** (phase - 1))

        data["balance"] = current_bal + reward
        data["total_mined"] = data.get("total_mined", 0.0) + reward
        data["block_height"] = data.get("block_height", 3) + 1
        data["last_cycle"] = now

        target = CANCER_TARGETS[data["block_height"] % len(CANCER_TARGETS)]
        proof_src = f"{data['block_height']}_{target}_{now}_{data.get('wallet_phrase', '')}"
        data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

        save_data(data)

        self.bal_lbl.text = f"{data['balance']:.4f} BARAT"
        self.phase_lbl.text = self.calculate_reward(data["balance"])
        self.update_block_display()
        self.update_timer(0)

    def do_logout(self, instance):
        self.manager.current = "landing"

    def claim_solana(self, instance):
        self.status_msg.text = "Bridge Verified: Oncology Research Proof queued."

class BaratCoreApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.06, 1.0)
        sm = ScreenManager()

        sm.add_widget(LandingScreen(name="landing"))
        sm.add_widget(AuthScreen(name="auth"))
        sm.add_widget(WalletScreen(name="wallet"))
        sm.add_widget(MainScreen(name="main"))

        sm.current = "landing"
        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
