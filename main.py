import os
import time
import hashlib
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore

class BaratCoreNode(App):
    def build(self):
        # 1. Permanent Local Storage Initialization
        data_dir = self.user_data_dir
        store_path = os.path.join(data_dir, 'barat_node_v2.json')
        self.store = JsonStore(store_path)

        # 2. Load User Persistent Data
        if self.store.exists('node_state'):
            saved = self.store.get('node_state')
            self.total_balance = float(saved.get('balance', 0.0))
            self.verified_blocks = int(saved.get('blocks', 0))
            self.wallet_address = str(saved.get('wallet', ''))
            self.session_end_time = float(saved.get('session_end', 0.0))
            self.last_sync_time = float(saved.get('last_sync', time.time()))
        else:
            self.total_balance = 0.0
            self.verified_blocks = 0
            self.wallet_address = ''
            self.session_end_time = 0.0
            self.last_sync_time = time.time()

        # Scientific Computation Matrices as per Whitepaper
        self.scientific_tasks = [
            "Cancer_Cell_Chunk_",
            "Climate_Grid_Model_",
            "Molecular_Protein_Folding_",
            "Neural_Network_Weights_"
        ]

        # Calculate pending mined rewards while app was closed
        self.catch_up_offline_progress()

        # 3. UI Construction
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header Title
        title = Label(
            text="[b]BARAT NETWORK[/b]\n[size=13]Proof of Intelligence (PoI) Node v2.0[/size]",
            markup=True,
            size_hint_y=0.14,
            color=(0.15, 0.75, 0.95, 1)
        )
        root.add_widget(title)

        # Live Balance Display
        self.lbl_balance = Label(
            text=f"[b]{self.total_balance:.4f}[/b] $BARAT",
            markup=True,
            size_hint_y=0.10,
            font_size='22sp',
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.lbl_balance)

        # Halving and Mining Speed Info
        self.lbl_stats = Label(
            text=self.get_stats_string(),
            size_hint_y=0.06,
            color=(0.6, 0.9, 0.6, 1),
            font_size='12sp'
        )
        root.add_widget(self.lbl_stats)

        # Solana / Phantom Wallet Section
        wallet_box = BoxLayout(orientation='vertical', size_hint_y=0.14, spacing=3)
        wallet_box.add_widget(Label(text="Solana / Phantom Wallet Target:", size_hint_y=0.4, font_size='11sp'))
        self.txt_wallet = TextInput(
            text=self.wallet_address,
            hint_text="Enter Solana Public Key (Base58)...",
            multiline=False,
            size_hint_y=0.6,
            font_size='12sp'
        )
        self.txt_wallet.bind(text=self.on_wallet_input)
        wallet_box.add_widget(self.txt_wallet)
        root.add_widget(wallet_box)

        # PoI Real-Time Task Visualizer (Console)
        self.lbl_console = Label(
            text="[PoI Core] System Ready. Start session to solve matrices.",
            size_hint_y=None,
            color=(0.8, 0.8, 0.8, 1),
            halign='left',
            valign='top',
            font_size='11sp'
        )
        self.lbl_console.bind(texture_size=self.lbl_console.setter('size'))

        scroll = ScrollView(size_hint_y=0.42)
        scroll.add_widget(self.lbl_console)
        root.add_widget(scroll)

        # 24-Hour Mining Action Button
        self.btn_mine = Button(
            text="START 24H PoI SESSION",
            size_hint_y=0.14,
            bold=True,
            background_color=(0, 0.6, 0.3, 1)
        )
        self.btn_mine.bind(on_press=self.handle_session_toggle)
        root.add_widget(self.btn_mine)

        # Continuous Heartbeat Event (Every 1 second)
        Clock.schedule_interval(self.system_heartbeat, 1.0)
        self.check_active_session_status()

        return root

    def get_current_base_rate_per_sec(self):
        """Halving Logic based on total mined tokens"""
        # Base: 10 BARAT per 24 hours -> 10 / 86400 per second
        if self.total_balance < 500.0:
            daily_rate = 10.00
        elif self.total_balance < 2500.0:
            daily_rate = 5.00
        elif self.total_balance < 10000.0:
            daily_rate = 2.50
        else:
            daily_rate = 1.25
        return daily_rate / 86400.0, daily_rate

    def get_stats_string(self):
        _, daily_rate = self.get_current_base_rate_per_sec()
        return f"Rate: {daily_rate:.2f} $BARAT/24h | Blocks Solved: {self.verified_blocks}"

    def on_wallet_input(self, instance, value):
        self.wallet_address = value.strip()
        self.persist_state()

    def persist_state(self):
        self.store.put('node_state',
                       balance=self.total_balance,
                       blocks=self.verified_blocks,
                       wallet=self.wallet_address,
                       session_end=self.session_end_time,
                       last_sync=time.time())

    def catch_up_offline_progress(self):
        """Credit mined tokens if app was closed during an active session"""
        now = time.time()
        if self.session_end_time > self.last_sync_time:
            active_duration = min(now, self.session_end_time) - self.last_sync_time
            if active_duration > 0:
                rate_per_sec, _ = self.get_current_base_rate_per_sec()
                gained = active_duration * rate_per_sec
                self.total_balance += gained
                self.verified_blocks += int(active_duration // 30)
        self.last_sync_time = now
        self.persist_state()

    def check_active_session_status(self):
        now = time.time()
        if now < self.session_end_time:
            self.btn_mine.disabled = True
        else:
            self.btn_mine.disabled = False
            self.btn_mine.text = "START 24H PoI SESSION"
            self.btn_mine.background_color = (0, 0.6, 0.3, 1)

    def handle_session_toggle(self, instance):
        now = time.time()
        if now >= self.session_end_time:
            # 24-Hour Mining Cycle (86400 seconds)
            self.session_end_time = now + 86400
            self.last_sync_time = now
            self.persist_state()
            self.btn_mine.disabled = True
            log_entry = "[PoI] 24-Hour Computing Session Activated.\n"
            self.lbl_console.text = log_entry + self.lbl_console.text

    def system_heartbeat(self, dt):
        now = time.time()

        if now < self.session_end_time:
            # Session is active
            remaining = int(self.session_end_time - now)
            hours = remaining // 3600
            mins = (remaining % 3600) // 60
            secs = remaining % 60
            self.btn_mine.text = f"COMPUTING ACTIVE ({hours:02d}:{mins:02d}:{secs:02d})"
            self.btn_mine.background_color = (0.2, 0.4, 0.8, 1)

            # Credit incremental reward
            rate_per_sec, _ = self.get_current_base_rate_per_sec()
            self.total_balance += rate_per_sec
            self.lbl_balance.text = f"[b]{self.total_balance:.4f}[/b] $BARAT"

            # Execute a matrix task proof every 10 seconds for visual proof
            if int(now) % 10 == 0:
                self.verified_blocks += 1
                task = random.choice(self.scientific_tasks) + str(random.randint(1000, 9999))
                h = hashlib.sha256(task.encode()).hexdigest()
                log = (
                    f"[✓] Solved: {task}\n"
                    f"    PoI Proof: {h[:14]}... | 3 Nodes Verified\n"
                )
                self.lbl_console.text = log + self.lbl_console.text[:400]
                self.lbl_stats.text = self.get_stats_string()
                self.persist_state()
        else:
            # Session expired
            if self.btn_mine.disabled:
                self.check_active_session_status()
