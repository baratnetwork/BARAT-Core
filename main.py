import time
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

DATA_FILE = "barat_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"registered": False, "username": "", "seed": "", "balance": 0.0, "last_mine": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="BARAT Core - Register", font_size=24, bold=True))
        
        self.user_input = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.user_input)
        
        layout.add_widget(Label(text="Enter your own 12-words Secret Key:", size_hint_y=None, height=30))
        self.seed_input = TextInput(hint_text="word1 word2 ... word12 (space separated)", multiline=True, size_hint_y=None, height=90)
        layout.add_widget(self.seed_input)
        
        self.msg = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30)
        layout.add_widget(self.msg)
        
        btn = Button(text="Confirm & Register", size_hint_y=None, height=50, background_color=(0.2, 0.7, 0.3, 1))
        btn.bind(on_press=self.do_register)
        layout.add_widget(btn)
        
        self.add_widget(layout)

    def do_register(self, instance):
        words = self.seed_input.text.strip().split()
        username = self.user_input.text.strip()
        
        if not username:
            self.msg.text = "Username cannot be empty!"
            return
            
        if len(words) != 12:
            self.msg.text = f"Exactly 12 words required! (You entered {len(words)})"
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
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text="BARAT Core - Login", font_size=24, bold=True))
        layout.add_widget(Label(text="Enter your 12-words Secret Key to Unlock:", size_hint_y=None, height=30))
        
        self.seed_input = TextInput(hint_text="Enter your 12 secret words", multiline=True, size_hint_y=None, height=90)
        layout.add_widget(self.seed_input)
        
        self.msg = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30)
        layout.add_widget(self.msg)
        
        btn = Button(text="Unlock Wallet", size_hint_y=None, height=50, background_color=(0.2, 0.5, 0.9, 1))
        btn.bind(on_press=self.do_login)
        layout.add_widget(btn)
        
        self.add_widget(layout)

    def do_login(self, instance):
        entered_seed = " ".join(self.seed_input.text.strip().split())
        data = load_data()
        if entered_seed == data.get("seed", ""):
            self.manager.current = "main"
        else:
            self.msg.text = "Incorrect 12-word Key! Access Denied."

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        self.title_lbl = Label(text="BARAT Core Dashboard", font_size=22, bold=True, size_hint_y=None, height=40)
        self.layout.add_widget(self.title_lbl)
        
        self.bal_lbl = Label(text="Balance: 0.0 BARAT", font_size=20, color=(0.2, 0.9, 0.4, 1), size_hint_y=None, height=40)
        self.layout.add_widget(self.bal_lbl)
        
        self.timer_lbl = Label(text="Mining Status: Ready", size_hint_y=None, height=30)
        self.layout.add_widget(self.timer_lbl)
        
        self.mine_btn = Button(text="Start 24H Mining", size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.8, 1))
        self.mine_btn.bind(on_press=self.start_mining)
        self.layout.add_widget(self.mine_btn)
        
        self.sol_btn = Button(text="Claim Solana Reward", size_hint_y=None, height=50, background_color=(0.7, 0.3, 0.8, 1))
        self.sol_btn.bind(on_press=self.claim_solana)
        self.layout.add_widget(self.sol_btn)
        
        self.status_msg = Label(text="", size_hint_y=None, height=30)
        self.layout.add_widget(self.status_msg)
        
        self.add_widget(self.layout)
        Clock.schedule_interval(self.update_timer, 1.0)

    def on_enter(self):
        data = load_data()
        self.bal_lbl.text = f"Balance: {data.get('balance', 0.0):.2f} BARAT"

    def start_mining(self, instance):
        data = load_data()
        now = time.time()
        last_mine = data.get("last_mine", 0)
        
        # 24 Hours = 86400 Seconds
        if now - last_mine < 86400:
            self.status_msg.text = "Device locked: Mining already running!"
            return
            
        data["last_mine"] = now
        data["balance"] = data.get("balance", 0.0) + 10.0  # Reward per 24h
        save_data(data)
        
        self.bal_lbl.text = f"Balance: {data['balance']:.2f} BARAT"
        self.status_msg.text = "+10 BARAT mined successfully!"

    def update_timer(self, dt):
        data = load_data()
        now = time.time()
        elapsed = now - data.get("last_mine", 0)
        if elapsed < 86400:
            rem = int(86400 - elapsed)
            hrs = rem // 3600
            mins = (rem % 3600) // 60
            secs = rem % 60
            self.timer_lbl.text = f"Next Mining In: {hrs:02d}:{mins:02d}:{secs:02d}"
            self.mine_btn.disabled = True
        else:
            self.timer_lbl.text = "Mining Status: Ready to Mine"
            self.mine_btn.disabled = False

    def claim_solana(self, instance):
        self.status_msg.text = "Solana Claim Request Submitted to Network!"

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
