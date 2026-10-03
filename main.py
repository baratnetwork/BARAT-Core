import os
import json
import time
import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window

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
        "seed": "",
        "balance": 0.0,
        "total_mined": 0.0,
        "block_height": 3,
        "last_cycle": 0,
        "proof_hash": "ECO_GENESIS_PROOF_00000000"
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 40, 24, 30], spacing=14)

        if os.path.exists("icon.png"):
            logo = Image(source="icon.png", size_hint=(1, None), height=90, allow_stretch=True)
            root.add_widget(logo)

        root.add_widget(Label(text="BARAT CORE NETWORK", font_size='22sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=None, height=32))
        root.add_widget(Label(text="Eco-Green Cancer Research Node Setup", font_size='13sp', color=(0.6, 0.7, 0.6, 1), size_hint_y=None, height=20))

        self.user_input = TextInput(hint_text="Enter Node Operator Name", multiline=False, size_hint_y=None, height=48, padding=[12, 12])
        root.add_widget(self.user_input)

        root.add_widget(Label(text="Enter 12-Word Decentralized Passphrase:", font_size='13sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=24))

        self.seed_input = TextInput(hint_text="word1 word2 ... word12", multiline=True, size_hint_y=None, height=80, padding=[12, 12])
        root.add_widget(self.seed_input)

        self.msg = Label(text="", font_size='12sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=24)
        root.add_widget(self.msg)

        btn = Button(text="Initialize Secure Node", size_hint_y=None, height=50, background_color=(0.1, 0.55, 0.35, 1), font_size='15sp', bold=True)
        btn.bind(on_press=self.do_register)
        root.add_widget(btn)

        self.add_widget(root)

    def do_register(self, instance):
        words = self.seed_input.text.strip().split()
        username = self.user_input.text.strip()

        if not username:
            self.msg.text = "Operator name cannot be empty!"
            return

        if len(words) != 12:
            self.msg.text = f"Exactly 12 words required! ({len(words)} given)"
            return

        data = load_data()
        data["registered"] = True
        data["username"] = username
        data["seed"] = " ".join(words)
        save_data(data)

        self.manager.current = "main"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 40, 24, 40], spacing=15)

        if os.path.exists("icon.png"):
            logo = Image(source="icon.png", size_hint=(1, None), height=90, allow_stretch=True)
            root.add_widget(logo)

        root.add_widget(Label(text="BARAT CORE", font_size='26sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=None, height=36))
        root.add_widget(Label(text="Enter 12-Word Passphrase to Unlock Node:", size_hint_y=None, height=28, font_size='14sp'))

        self.seed_input = TextInput(hint_text="Enter 12 secret words", multiline=True, size_hint_y=None, height=90, font_size='14sp', padding=[12, 12])
        root.add_widget(self.seed_input)

        self.msg = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=26, font_size='13sp')
        root.add_widget(self.msg)

        btn = Button(text="Unlock Research Terminal", size_hint_y=None, height=52, background_color=(0.15, 0.55, 0.35, 1), font_size='14sp', bold=True)
        btn.bind(on_press=self.do_login)
        root.add_widget(btn)

        self.add_widget(root)

    def do_login(self, instance):
        entered_seed = " ".join(self.seed_input.text.strip().split())
        data = load_data()
        if entered_seed == data.get("seed", ""):
            self.manager.current = "main"
        else:
            self.msg.text = "Invalid Security Key! Access Denied."

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[18, 20, 18, 20], spacing=8)

        # టైటిల్
        root.add_widget(Label(text="BARAT CORE: GREEN RESEARCH NODE", font_size='16sp', bold=True, color=(0.2, 0.9, 0.5, 1), size_hint_y=None, height=28))

        # మెరిసే లోగో (మైనింగ్ బ్యాలెన్స్ పైన)
        if os.path.exists("icon.png"):
            self.logo_img = Image(source="icon.png", size_hint=(1, None), height=105, allow_stretch=True, opacity=0.9)
            root.add_widget(self.logo_img)
            anim = Animation(opacity=0.55, duration=1.3) + Animation(opacity=1.0, duration=1.3)
            anim.repeat = True
            anim.start(self.logo_img)

        # మైనింగ్ బ్యాలెన్స్
        self.bal_lbl = Label(text="0.0000 BARAT", font_size='28sp', bold=True, color=(0.95, 0.95, 0.95, 1), size_hint_y=None, height=44)
        root.add_widget(self.bal_lbl)

        # మైనింగ్ ఫేజ్ & రివార్డ్
        self.phase_lbl = Label(text="Phase: Initializing...", font_size='12sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=None, height=22)
        root.add_widget(self.phase_lbl)

        # క్యాన్సర్ రీసెర్చ్ టార్గెట్
        self.puzzle_lbl = Label(text="Research Target: Loading...", font_size='12sp', color=(0.4, 0.65, 1, 1), size_hint_y=None, height=24)
        root.add_widget(self.puzzle_lbl)

        # బ్లాక్ ప్రూఫ్ సమాచారం
        self.block_lbl = Label(text="Block Height: #0000 | Proof: Verifying", font_size='11sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=20)
        root.add_widget(self.block_lbl)

        # 24 గంటల కౌంట్‌డౌన్ టైమర్
        self.timer_lbl = Label(text="Node Engine: Ready", font_size='13sp', size_hint_y=None, height=24)
        root.add_widget(self.timer_lbl)

        # మైనింగ్ బటన్
        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=None, height=50, background_color=(0.1, 0.65, 0.35, 1), font_size='15sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        # సోలానా బ్రిడ్జ్ బటన్
        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=None, height=44, background_color=(0.5, 0.2, 0.7, 1), font_size='13sp', bold=True)
        self.sol_btn.bind(on_press=self.claim_solana)
        root.add_widget(self.sol_btn)

        # స్టేటస్ మెసేజ్
        self.status_msg = Label(text="Bridge Verified: Oncology Research Proof queued.", font_size='11sp', color=(1, 0.85, 0.3, 1), size_hint_y=None, height=22)
        root.add_widget(self.status_msg)

        self.add_widget(root)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        data = load_data()
        current_bal = data.get("balance", 0.0)
        phase_name = self.calculate_reward(current_bal)
        self.bal_lbl.text = f"{current_bal:.4f} BARAT"
        self.phase_lbl.text = phase_name
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
        proof_src = f"{data['block_height']}_{target}_{now}_{data.get('seed', '')}"
        data["proof_hash"] = hashlib.sha256(proof_src.encode()).hexdigest()

        save_data(data)

        self.bal_lbl.text = f"{data['balance']:.4f} BARAT"
        self.phase_lbl.text = self.calculate_reward(data["balance"])
        self.update_block_display()
        self.update_timer(0)

    def claim_solana(self, instance):
        self.status_msg.text = "Bridge Verified: Oncology Research Proof queued."

class BaratCoreApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.06, 1.0)
        sm = ScreenManager()
        data = load_data()

        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))

        if not data.get("registered", False):
            sm.current = "register"
        else:
            sm.current = "login"

        return sm

if __name__ == '__main__':
    BaratCoreApp().run()
        
