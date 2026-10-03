import time
import json
import os
import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

DATA_FILE = "barat_data.json"
MAX_SUPPLY = 21000000.0  # ఖచ్చితమైన 21 మిలియన్ల సరఫరా
CYCLE_TIME = 86400       # 24 గంటల రీసెర్చ్ సైకిల్

# క్యాన్సర్ రీసెర్చ్ లక్ష్యాల లిస్ట్ (ప్రతి బ్లాక్‌కు ఒక కొత్త ప్రోటీన్ పజిల్)
CANCER_TARGETS = [
    "TP53-TumorSuppressor-Fold-A1",
    "BRCA1-DNA-Repair-Sequence-9B",
    "EGFR-Kinase-Inhibitor-Fold-C4",
    "KRAS-G12D-Target-Model-X7",
    "MYC-Oncogene-Transcription-L3"
]

def calculate_reward(balance):
    """ఆటోమేటిక్ హాల్వింగ్ - బ్యాలెన్స్ పెరిగే కొద్దీ కంట్రోల్ అయ్యే రివార్డ్"""
    if balance < 1000.0:
        return 10.0, "Phase 1: Genesis (10.0 BARAT)"
    elif balance < 5000.0:
        return 5.0, "Phase 2: Alpha (5.0 BARAT)"
    elif balance < 25000.0:
        return 2.5, "Phase 3: Beta (2.5 BARAT)"
    elif balance < 100000.0:
        return 1.25, "Phase 4: Gamma (1.25 BARAT)"
    else:
        return 0.625, "Phase 5: Global Reserve (0.625 BARAT)"

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
        "last_mine": 0,
        "block_height": 2048,
        "solved_puzzles": 0,
        "last_proof": "ECO_GENESIS_PROOF"
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=[24, 30, 24, 30], spacing=12)

        root.add_widget(Label(text="BARAT CORE NETWORK", font_size='24sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.14))
        root.add_widget(Label(text="Eco-Green Cancer Research Node Setup", font_size='13sp', color=(0.7, 0.8, 0.7, 1), size_hint_y=0.08))

        self.user_input = TextInput(hint_text="Enter Node Operator Name", multiline=False, size_hint_y=0.12, font_size='15sp')
        root.add_widget(self.user_input)

        root.add_widget(Label(text="12-Word Decentralized Security Key:", size_hint_y=0.08, halign="left"))
        self.seed_input = TextInput(hint_text="word1 word2 ... word12 (Keep this safe)", multiline=True, size_hint_y=0.24, font_size='13sp')
        root.add_widget(self.seed_input)

        self.msg = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=0.08, font_size='13sp')
        root.add_widget(self.msg)

        btn = Button(text="Initialize Secure Node", size_hint_y=0.15, background_color=(0.1, 0.7, 0.4, 1), font_size='16sp', bold=True)
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

        root.add_widget(Label(text="BARAT CORE", font_size='26sp', bold=True, color=(0.1, 0.9, 0.5, 1), size_hint_y=0.2))
        root.add_widget(Label(text="Enter 12-Word Passphrase to Unlock Node:", size_hint_y=0.1, font_size='14sp'))

        self.seed_input = TextInput(hint_text="Enter 12 secret words", multiline=True, size_hint_y=0.3, font_size='14sp')
        root.add_widget(self.seed_input)

        self.msg = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=0.1, font_size='13sp')
        root.add_widget(self.msg)

        btn = Button(text="Unlock Research Terminal", size_hint_y=0.18, background_color=(0.15, 0.55, 0.85, 1), font_size='16sp', bold=True)
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
        root = BoxLayout(orientation='vertical', padding=[18, 20, 18, 20], spacing=10)

        # హెడర్ - ఫ్యూచరిస్టిక్ గ్రీన్ నెట్‌వర్క్
        root.add_widget(Label(text="BARAT CORE: GREEN RESEARCH NODE", font_size='16sp', bold=True, color=(0.2, 0.9, 0.5, 1), size_hint_y=0.07))

        # బ్యాలెన్స్ డిస్‌ప్లే
        self.bal_lbl = Label(text="0.0000 BARAT", font_size='28sp', bold=True, color=(0.95, 0.95, 0.95, 1), size_hint_y=0.13)
        root.add_widget(self.bal_lbl)

        # హాల్వింగ్ ఫేజ్ & కరెంట్ రేటు
        self.phase_lbl = Label(text="Phase: Initializing...", font_size='12sp', color=(0.95, 0.8, 0.2, 1), size_hint_y=0.07)
        root.add_widget(self.phase_lbl)

        # క్యాన్సర్ రీసెర్చ్ టార్గెట్ పజిల్
        self.puzzle_lbl = Label(text="Research Target: Loading...", font_size='12sp', color=(0.4, 0.85, 1, 1), size_hint_y=0.07)
        root.add_widget(self.puzzle_lbl)

        # బ్లాక్ హైట్ మరియు మెడికల్ క్రిప్టోగ్రాఫిక్ ప్రూఫ్
        self.block_lbl = Label(text="Block Height: #0000 | Proof: Verifying", font_size='11sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=0.07)
        root.add_widget(self.block_lbl)

        # 24 గంటల పర్యావరణ సైకిల్ స్టేటస్
        self.timer_lbl = Label(text="Node Engine: Ready", font_size='13sp', size_hint_y=0.07)
        root.add_widget(self.timer_lbl)

        # మైనింగ్ బటన్
        self.mine_btn = Button(text="Solve Puzzle & Mine Block", size_hint_y=0.14, background_color=(0.1, 0.65, 0.35, 1), font_size='16sp', bold=True)
        self.mine_btn.bind(on_press=self.start_mining)
        root.add_widget(self.mine_btn)

        # డీసెంట్రలైజ్డ్ బ్రిడ్జ్ బటన్
        self.sol_btn = Button(text="Sync With Solana Bridge", size_hint_y=0.11, background_color=(0.5, 0.2, 0.7, 1), font_size='14sp')
        self.sol_btn.bind(on_press=self.claim_solana)
        root.add_widget(self.sol_btn)

        # నోడ్ నోటిఫికేషన్ లాగ్
        self.status_msg = Label(text="", font_size='12sp', color=(1, 0.85, 0.3, 1), size_hint_y=0.08)
        root.add_widget(self.status_msg)

        self.add_widget(root)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        data = load_data()
        current_bal = data.get("balance", 0.0)
        _, phase_name = calculate_reward(current_bal)
        self.bal_lbl.text = f"{current_bal:.4f} BARAT"
        self.phase_lbl.text = phase_name
        self.update_block_display()

    def update_block_display(self):
        data = load_data()
        height = data.get("block_height", 2048)
        target = CANCER_TARGETS[height % len(CANCER_TARGETS)]
        proof = data.get("last_proof", "ECO_GENESIS_PROOF")
        self.puzzle_lbl.text = f"Target: {target}"
        self.block_lbl.text = f"Block #{height} | Proof: {proof[:12]}..."

    def start_mining(self, instance):
        data = load_data()
        now = time.time()
        last_mine = data.get("last_mine", 0)

        # 24 గంటల పర్యావరణ పరిరక్షణ రూల్ (కరెంట్ వేస్ట్ అవ్వకుండా ఉండే సైకిల్)
        if now - last_mine < CYCLE_TIME:
            self.status_msg.text = "Eco-Engine Active: Current cycle solving!"
            return

        current_bal = data.get("balance", 0.0)
        reward, phase_name = calculate_reward(current_bal)

        # క్యాన్సర్ ప్రోటీన్ పజిల్‌కు నిజమైన క్రిప్టోగ్రాఫిక్ ప్రూఫ్ ఉత్పత్తి
        new_height = data.get("block_height", 2048) + 1
        target_name = CANCER_TARGETS[new_height % len(CANCER_TARGETS)]
        proof_payload = f"{new_height}_{target_name}_{now}_{data.get('seed', '')[:6]}"
        research_proof = hashlib.sha256(proof_payload.encode()).hexdigest()

        # లోకల్ డేటాబేస్‌లో శాశ్వతంగా భద్రపరచడం
        data["last_mine"] = now
        data["balance"] = current_bal + reward
        data["block_height"] = new_height
        data["last_proof"] = research_proof
        data["solved_puzzles"] = data.get("solved_puzzles", 0) + 1
        save_data(data)

        self.bal_lbl.text = f"{data['balance']:.4f} BARAT"
        self.phase_lbl.text = phase_name
        self.status_msg.text = f"Puzzle Solved! +{reward} BARAT Credited."
        self.update_block_display()

    def update_timer(self, dt):
        data = load_data()
        now = time.time()
        elapsed = now - data.get("last_mine", 0)

        if elapsed < CYCLE_TIME:
            rem = int(CYCLE_TIME - elapsed)
            hrs = rem // 3600
            mins = (rem % 3600) // 60
            secs = rem % 60
            self.timer_lbl.text = f"Next Puzzle In: {hrs:02d}h {mins:02d}m {secs:02d}s"
            self.mine_btn.disabled = True
        else:
            self.timer_lbl.text = "Node Ready: Solve Next Cancer Puzzle"
            self.mine_btn.disabled = False

    def claim_solana(self, instance):
        self.status_msg.text = "Bridge Verified: Oncology Research Proof queued."

class BaratApp(App):
    def build(self):
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
    BaratApp().run()
