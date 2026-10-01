import json
import os
import re
import time
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Dark Cyber Background
Window.clearcolor = (0.03, 0.05, 0.08, 1)

DATA_VAULT = "barat_secure_vault.json"

def get_vault_data():
    defaults = {
        "users": {},
        "current_session": None,
        "global_stats": {
            "total_nodes": 12840,
            "network_hashrate": "428.5 TH/s",
            "total_blocks": 158902
        }
    }
    if os.path.exists(DATA_VAULT):
        try:
            with open(DATA_VAULT, "r") as f:
                return json.load(f)
        except Exception:
            return defaults
    return defaults

def save_vault_data(data):
    try:
        with open(DATA_VAULT, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass


# -------------------- 1. LOGIN & REGISTRATION SCREEN --------------------
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', padding=[24, 30, 24, 30], spacing=16, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        title = Label(
            text="[b][color=00e5ff]BARAT NETWORK[/color][/b]",
            markup=True,
            font_size='26sp',
            size_hint=(1, None),
            height=40
        )
        subtitle = Label(
            text="[color=8892b0]Proof of Intelligence (PoI) Global Node[/color]",
            markup=True,
            font_size='12sp',
            size_hint=(1, None),
            height=20
        )
        box.add_widget(title)
        box.add_widget(subtitle)

        info = Label(
            text="[color=ccd6f6]Secure Node Access Portal[/color]",
            markup=True,
            font_size='14sp',
            size_hint=(1, None),
            height=30
        )
        box.add_widget(info)

        self.user_in = TextInput(
            hint_text="Username / Node Identifier",
            multiline=False,
            size_hint=(1, None),
            height=48,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1),
            font_size='13sp',
            padding=[12, 14, 12, 12]
        )
        self.pass_in = TextInput(
            hint_text="Password / Security Key",
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=48,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1),
            font_size='13sp',
            padding=[12, 14, 12, 12]
        )
        box.add_widget(self.user_in)
        box.add_widget(self.pass_in)

        login_btn = Button(
            text="SIGN IN TO NODE",
            size_hint=(1, None),
            height=48,
            background_color=(0.0, 0.7, 0.9, 1),
            bold=True,
            font_size='13sp'
        )
        login_btn.bind(on_press=self.do_login)

        reg_btn = Button(
            text="CREATE NEW ACCOUNT",
            size_hint=(1, None),
            height=48,
            background_color=(0.14, 0.20, 0.30, 1),
            bold=True,
            font_size='13sp'
        )
        reg_btn.bind(on_press=self.do_register)

        box.add_widget(login_btn)
        box.add_widget(reg_btn)

        self.msg = Label(text="", markup=True, font_size='12sp', size_hint=(1, None), height=25)
        box.add_widget(self.msg)

        scroll.add_widget(box)
        self.add_widget(scroll)

    def do_login(self, instance):
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault_data()

        if not u or not p:
            self.msg.text = "[color=ff4444]యూజర్ నేమ్ మరియు పాస్‌వర్డ్ నమోదు చేయండి![/color]"
            return

        if u in vault["users"] and vault["users"][u]["password"] == p:
            vault["current_session"] = u
            save_vault_data(vault)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "mining_screen"
            self.manager.get_screen("mining_screen").sync_screen()
        else:
            self.msg.text = "[color=ff3333]వివరాలు సరిపోలలేదు! దయచేసి తనిఖీ చేయండి.[/color]"

    def do_register(self, instance):
        u = self.user_in.text.strip()
        p = self.pass_in.text.strip()
        vault = get_vault_data()

        if len(u) < 3 or len(p) < 4:
            self.msg.text = "[color=ffaa00]యూజర్ నేమ్ (3 అక్షరాలు), పాస్‌వర్డ్ (4 అక్షరాలు) ఉండాలి![/color]"
            return

        if u in vault["users"]:
            self.msg.text = "[color=ff4444]ఈ యూజర్ నేమ్ ఇప్పటికే ఉంది![/color]"
            return

        vault["users"][u] = {
            "password": p,
            "balance": 0.000000,
            "wallet_address": "",
            "kyc_status": "Unverified",
            "kyc_id": "",
            "verified_blocks": 0,
            "node_multiplier": 1.0
        }
        vault["current_session"] = u
        vault["global_stats"]["total_nodes"] += 1
        save_vault_data(vault)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = "mining_screen"
        self.manager.get_screen("mining_screen").sync_screen()


# -------------------- 2. MINING DASHBOARD SCREEN --------------------
class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_mining = False
        self.mining_ticker = None

        layout = BoxLayout(orientation='vertical', padding=[14, 12, 14, 8], spacing=8)

        # Header Info Card
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        self.user_lbl = Label(text="[color=ccd6f6]Node: Miner[/color]", markup=True, font_size='12sp', halign='left')
        self.user_lbl.bind(size=self.user_lbl.setter('text_size'))
        self.kyc_lbl = Label(text="[color=ff4444]● Unverified[/color]", markup=True, font_size='12sp', halign='right')
        self.kyc_lbl.bind(size=self.kyc_lbl.setter('text_size'))
        top_bar.add_widget(self.user_lbl)
        top_bar.add_widget(self.kyc_lbl)
        layout.add_widget(top_bar)

        # Main Balance Card
        bal_card = BoxLayout(orientation='vertical', size_hint=(1, None), height=85, padding=6, spacing=2)
        bal_sub = Label(text="[color=8892b0]LIVE ACCUMULATED ASSETS[/color]", markup=True, font_size='10sp', size_hint=(1, None), height=14)
        self.bal_display = Label(text="[b][color=ffffff]0.000000[/color] [color=00e5ff]$BARAT[/color][/b]", markup=True, font_size='24sp', size_hint=(1, None), height=38)
        
        stat_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=18)
        self.speed_lbl = Label(text="[color=64ffda]Rate: 0.2500 B/hr[/color]", markup=True, font_size='11sp')
        self.blocks_lbl = Label(text="[color=64ffda]Blocks: 0[/color]", markup=True, font_size='11sp')
        stat_bar.add_widget(self.speed_lbl)
        stat_bar.add_widget(self.blocks_lbl)

        bal_card.add_widget(bal_sub)
        bal_card.add_widget(self.bal_display)
        bal_card.add_widget(stat_bar)
        layout.add_widget(bal_card)

        # Action Buttons (Start Node & Boost Power)
        btn_grid = BoxLayout(orientation='horizontal', size_hint=(1, None), height=46, spacing=8)
        self.power_btn = Button(
            text="START NODE",
            background_color=(0.0, 0.75, 0.45, 1),
            bold=True,
            font_size='13sp'
        )
        self.power_btn.bind(on_press=self.toggle_node)

        self.boost_btn = Button(
            text="BOOST SPEED 2X",
            background_color=(0.7, 0.4, 0.0, 1),
            bold=True,
            font_size='12sp'
        )
        self.boost_btn.bind(on_press=self.boost_speed)

        btn_grid.add_widget(self.power_btn)
        btn_grid.add_widget(self.boost_btn)
        layout.add_widget(btn_grid)

        # Scientific Computation Log Stream
        log_head = Label(text="[color=8892b0]PROOF-OF-INTELLIGENCE STREAM[/color]", markup=True, font_size='10sp', size_hint=(1, None), height=15, halign='left')
        log_head.bind(size=log_head.setter('text_size'))
        layout.add_widget(log_head)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.terminal = Label(
            text="[color=495d75]>> Node ready. Tap START NODE to resolve AI & Medical workloads...[/color]\n",
            markup=True,
            font_size='10sp',
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.terminal.bind(texture_size=lambda inst, v: setattr(self.terminal, 'height', v[1]))
        self.terminal.bind(size=lambda inst, v: setattr(self.terminal, 'text_size', (v[0], None)))
        self.scroll.add_widget(self.terminal)
        layout.add_widget(self.scroll)

        # Universal Navigation Bar
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_wall = Button(text="Wallet & KYC", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.navigate_to("wallet_screen"))
        n_stat = Button(text="Network Stats", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.navigate_to("stats_screen"))
        n_out = Button(text="Logout", background_color=(0.35, 0.12, 0.12, 1), font_size='11sp')
        n_out.bind(on_press=self.do_logout)

        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        nav.add_widget(n_out)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.user_lbl.text = f"[color=ccd6f6]Node: [b]{user}[/b][/color]"
            st = udata.get("kyc_status", "Unverified")
            col = "00ff66" if st == "Verified" else ("ffaa00" if st == "Pending" else "ff4444")
            self.kyc_lbl.text = f"[color={col}][b]● {st}[/b][/color]"
            self.bal_display.text = f"[b][color=ffffff]{udata.get('balance', 0.0):.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"
            self.blocks_lbl.text = f"[color=64ffda]Blocks: {udata.get('verified_blocks', 0)}[/color]"
            mult = udata.get("node_multiplier", 1.0)
            self.speed_lbl.text = f"[color=64ffda]Rate: {0.25 * mult:.4f} B/hr[/color]"

    def toggle_node(self, instance):
        if not self.is_mining:
            self.is_mining = True
            self.power_btn.text = "HALT NODE"
            self.power_btn.background_color = (0.85, 0.2, 0.2, 1)
            self.mining_ticker = Clock.schedule_interval(self.step_compute, 1.0)
            self.terminal.text += "\n[color=00ff66]>> Node thread initialized. Solving PoI scientific matrix...[/color]"
        else:
            self.is_mining = False
            self.power_btn.text = "START NODE"
            self.power_btn.background_color = (0.0, 0.75, 0.45, 1)
            if self.mining_ticker:
                self.mining_ticker.cancel()
            self.terminal.text += "\n[color=ffaa00]>> Node paused by user.[/color]"

    def boost_speed(self, instance):
        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            vault["users"][user]["node_multiplier"] = 2.0
            save_vault_data(vault)
            self.sync_screen()
            self.terminal.text += "\n[color=ffaa00]>> Node Speed Boosted to 2X (Research Protocol Applied)![/color]"

    def step_compute(self, dt):
        vault = get_vault_data()
        user = vault.get("current_session")
        if not user or user not in vault["users"]:
            return

        udata = vault["users"][user]
        mult = udata.get("node_multiplier", 1.0)
        udata["balance"] = udata.get("balance", 0.0) + (0.0000694 * mult)
        self.bal_display.text = f"[b][color=ffffff]{udata['balance']:.6f}[/color] [color=00e5ff]$BARAT[/color][/b]"

        if int(time.time()) % 10 == 0:
            udata["verified_blocks"] = udata.get("verified_blocks", 0) + 1
            vault["global_stats"]["total_blocks"] += 1
            self.blocks_lbl.text = f"[color=64ffda]Blocks: {udata['verified_blocks']}[/color]"
            tasks = [
                "Molecular_Protein_Folding_Matrix",
                "Atmospheric_Carbon_Grid_Tensor",
                "Neural_Weight_Consensus_Signed",
                "Genomic_Sequence_Hash_Verified",
                "Cancer_Cell_Receptor_Chunk_Solved"
            ]
            self.terminal.text += f"\n[color=00e5ff]>> Verified {random.choice(tasks)} [Block #{udata['verified_blocks']}][/color]"

        save_vault_data(vault)

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = target_screen
        if target_screen == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_screen()
        elif target_screen == "stats_screen":
            self.manager.get_screen("stats_screen").sync_screen()

    def do_logout(self, instance):
        if self.is_mining:
            self.toggle_node(None)
        vault = get_vault_data()
        vault["current_session"] = None
        save_vault_data(vault)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "auth_screen"


# -------------------- 3. WALLET & KYC PORTAL SCREEN --------------------
class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[16, 16, 16, 8], spacing=10)

        title = Label(
            text="[b][color=00e5ff]ASSET CLAIM & KYC PORTAL[/color][/b]",
            markup=True,
            font_size='18sp',
            size_hint=(1, None),
            height=28
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Wallet Field
        box.add_widget(Label(text="[color=8892b0]Web3 Target Wallet (Solana or EVM 0x):[/color]", markup=True, font_size='11sp', size_hint=(1, None), height=16))
        self.wallet_in = TextInput(
            hint_text="Paste 0x... or Solana Base58 Address",
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.wallet_in)

        sync_btn = Button(
            text="CLAIM / SYNC WALLET",
            size_hint=(1, None),
            height=44,
            background_color=(0.0, 0.6, 0.85, 1),
            bold=True,
            font_size='12sp'
        )
        sync_btn.bind(on_press=self.verify_wallet)
        box.add_widget(sync_btn)

        self.wallet_msg = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=20)
        box.add_widget(self.wallet_msg)

        # KYC Field
        box.add_widget(Label(text="[color=8892b0]Decentralized Identity KYC Tier-1:[/color]", markup=True, font_size='11sp', size_hint=(1, None), height=16))
        self.kyc_in = TextInput(
            hint_text="Enter Passport / National ID / Driving License No.",
            multiline=False,
            size_hint=(1, None),
            height=46,
            background_color=(0.08, 0.12, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp',
            padding=[10, 12, 10, 10]
        )
        box.add_widget(self.kyc_in)

        kyc_btn = Button(
            text="SUBMIT KYC IDENTIFICATION",
            size_hint=(1, None),
            height=44,
            background_color=(0.15, 0.50, 0.35, 1),
            bold=True,
            font_size='12sp'
        )
        kyc_btn.bind(on_press=self.submit_kyc)
        box.add_widget(kyc_btn)

        self.kyc_msg = Label(text="", markup=True, font_size='11sp', size_hint=(1, None), height=20)
        box.add_widget(self.kyc_msg)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Bar
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.navigate_to("mining_screen"))
        n_wall = Button(text="Wallet & KYC", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        n_stat = Button(text="Network Stats", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_stat.bind(on_press=lambda x: self.navigate_to("stats_screen"))
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            udata = vault["users"][user]
            self.wallet_in.text = udata.get("wallet_address", "")
            self.kyc_in.text = udata.get("kyc_id", "")
            st = udata.get("kyc_status", "Unverified")
            col = "00ff66" if st == "Verified" else ("ffaa00" if st == "Pending" else "ff4444")
            self.kyc_msg.text = f"[color={col}]ప్రస్తుత స్థితి: {st}[/color]"
            self.wallet_msg.text = ""

    def verify_wallet(self, instance):
        addr = self.wallet_in.text.strip()
        evm_re = r"^0x[a-fA-F0-9]{40}$"
        sol_re = r"^[1-9A-HJ-NP-za-km-z]{32,44}$"

        if not addr:
            self.wallet_msg.text = "[color=ff4444]వాలెట్ అడ్రస్ నమోదు చేయండి![/color]"
            return

        is_evm = re.match(evm_re, addr)
        is_sol = re.match(sol_re, addr)

        if not (is_evm or is_sol):
            self.wallet_msg.text = "[color=ff3333]చెల్లని అడ్రస్! సరైన 0x-EVM లేదా Solana అడ్రస్ ఇవ్వండి.[/color]"
            return

        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            vault["users"][user]["wallet_address"] = addr
            save_vault_data(vault)
            chain = "EVM (0x)" if is_evm else "SOLANA"
            self.wallet_msg.text = f"[color=00ff66]విజయవంతం: {chain} వాలెట్ లింక్ చేయబడింది![/color]"

    def submit_kyc(self, instance):
        doc = self.kyc_in.text.strip()
        if len(doc) < 6:
            self.kyc_msg.text = "[color=ff3333]కనీసం 6 అక్షరాలు/నంబర్లు ఉండాలి![/color]"
            return

        vault = get_vault_data()
        user = vault.get("current_session")
        if user and user in vault["users"]:
            vault["users"][user]["kyc_id"] = doc
            vault["users"][user]["kyc_status"] = "Pending"
            save_vault_data(vault)
            self.kyc_msg.text = "[color=00ff66]విజయవంతం: కేవైసీ సమర్పించబడింది (పరిశీలనలో ఉంది)![/color]"

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='right' if target_screen == "mining_screen" else 'left')
        self.manager.current = target_screen
        if target_screen == "mining_screen":
            self.manager.get_screen("mining_screen").sync_screen()
        elif target_screen == "stats_screen":
            self.manager.get_screen("stats_screen").sync_screen()


# -------------------- 4. GLOBAL NETWORK STATS SCREEN --------------------
class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[16, 16, 16, 8], spacing=12)

        title = Label(
            text="[b][color=00e5ff]GLOBAL NETWORK METRICS[/color][/b]",
            markup=True,
            font_size='18sp',
            size_hint=(1, None),
            height=28
        )
        layout.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(orientation='vertical', spacing=14, size_hint_y=None, padding=[10, 10, 10, 10])
        box.bind(minimum_height=box.setter('height'))

        self.nodes_lbl = Label(text="[color=ccd6f6]Active Nodes: 12,840[/color]", markup=True, font_size='14sp', size_hint=(1, None), height=30)
        self.hash_lbl = Label(text="[color=64ffda]Network Compute Power: 428.5 TH/s[/color]", markup=True, font_size='14sp', size_hint=(1, None), height=30)
        self.blks_lbl = Label(text="[color=ccd6f6]Total Blocks Verified: 158,902[/color]", markup=True, font_size='14sp', size_hint=(1, None), height=30)
        proto_lbl = Label(text="[color=8892b0]Protocol: Proof of Intelligence (PoI) Layer-1[/color]", markup=True, font_size='12sp', size_hint=(1, None), height=30)
        algo_lbl = Label(text="[color=8892b0]Workload: Biological Protein & AI Tensor Solving[/color]", markup=True, font_size='12sp', size_hint=(1, None), height=30)

        box.add_widget(self.nodes_lbl)
        box.add_widget(self.hash_lbl)
        box.add_widget(self.blks_lbl)
        box.add_widget(proto_lbl)
        box.add_widget(algo_lbl)

        scroll.add_widget(box)
        layout.add_widget(scroll)

        # Bottom Bar
        nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=44, spacing=6)
        n_mine = Button(text="Mining", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_mine.bind(on_press=lambda x: self.navigate_to("mining_screen"))
        n_wall = Button(text="Wallet & KYC", background_color=(0.12, 0.16, 0.24, 1), font_size='11sp')
        n_wall.bind(on_press=lambda x: self.navigate_to("wallet_screen"))
        n_stat = Button(text="Network Stats", background_color=(0.0, 0.5, 0.7, 1), font_size='11sp')
        nav.add_widget(n_mine)
        nav.add_widget(n_wall)
        nav.add_widget(n_stat)
        layout.add_widget(nav)

        self.add_widget(layout)

    def sync_screen(self):
        vault = get_vault_data()
        stats = vault.get("global_stats", {})
        self.nodes_lbl.text = f"[color=ccd6f6]Active Nodes: [b]{stats.get('total_nodes', 12840):,}[/b][/color]"
        self.hash_lbl.text = f"[color=64ffda]Network Compute Power: [b]{stats.get('network_hashrate', '428.5 TH/s')}[/b][/color]"
        self.blks_lbl.text = f"[color=ccd6f6]Total Blocks Verified: [b]{stats.get('total_blocks', 158902):,}[/b][/color]"

    def navigate_to(self, target_screen):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = target_screen
        if target_screen == "mining_screen":
            self.manager.get_screen("mining_screen").sync_screen()
        elif target_screen == "wallet_screen":
            self.manager.get_screen("wallet_screen").sync_screen()


# -------------------- MAIN APPLICATION CONTROLLER --------------------
class BaratCoreApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthScreen(name="auth_screen"))
        sm.add_widget(MiningScreen(name="mining_screen"))
        sm.add_widget(WalletScreen(name="wallet_screen"))
        sm.add_widget(StatsScreen(name="stats_screen"))

        vault = get_vault_data()
        if vault.get("current_session") and vault["current_session"] in vault["users"]:
            sm.current = "mining_screen"
            sm.get_screen("mining_screen").sync_screen()
        else:
            sm.current = "auth_screen"

        return sm


if __name__ == "__main__":
    BaratCoreApp().run()
