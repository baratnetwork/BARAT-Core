import json
import os
import re
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# Dark Theme Setting
Window.clearcolor = (0.05, 0.07, 0.11, 1)

DATA_FILE = "barat_secure_vault.json"


class BaratCoreApp(App):

    def build(self):
        self.load_user_data()
        self.is_mining = False
        self.mining_event = None

        root = BoxLayout(orientation="vertical", padding=16, spacing=12)

        # Header Title
        title_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=65
        )
        title_label = Label(
            text="[b][color=00e5ff]BARAT NETWORK[/color][/b]",
            markup=True,
            font_size="24sp",
            size_hint=(1, None),
            height=35,
        )
        sub_title = Label(
            text="[color=8892b0]Proof of Intelligence & Decentralized Node[/color]",
            markup=True,
            font_size="12sp",
            size_hint=(1, None),
            height=20,
        )
        title_box.add_widget(title_label)
        title_box.add_widget(sub_title)
        root.add_widget(title_box)

        # Account Status & KYC Bar
        status_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=30,
            spacing=10,
        )
        self.user_tag = Label(
            text=f"[color=a8b2d1]User: {self.data.get('username', 'Miner_Node')}[/color]",
            markup=True,
            font_size="13sp",
            halign="left",
        )
        kyc_state = self.data.get("kyc_status", "Unverified")
        kyc_color = (
            "00ff66"
            if kyc_state == "Verified"
            else ("ffaa00" if kyc_state == "Pending" else "ff4444")
        )
        self.kyc_tag = Label(
            text=f"[color={kyc_color}]KYC: {kyc_state}[/color]",
            markup=True,
            font_size="13sp",
            halign="right",
        )
        status_bar.add_widget(self.user_tag)
        status_bar.add_widget(self.kyc_tag)
        root.add_widget(status_bar)

        # Live Balance Container
        balance_card = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=85, padding=8
        )
        bal_head = Label(
            text="[color=a8b2d1]LIVE ACCUMULATED BALANCE[/color]",
            markup=True,
            font_size="11sp",
        )
        self.balance_label = Label(
            text=f"[b][color=ffffff]{self.data.get('balance', 0.0):.6f} BARAT[/color][/b]",
            markup=True,
            font_size="26sp",
        )
        balance_card.add_widget(bal_head)
        balance_card.add_widget(self.balance_label)
        root.add_widget(balance_card)

        # Mining Node Stats
        stats_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=35,
            spacing=5,
        )
        self.speed_label = Label(
            text="[color=64ffda]Rate: 0.2500 B/hr[/color]",
            markup=True,
            font_size="12sp",
        )
        self.blocks_label = Label(
            text=f"[color=64ffda]Blocks: {self.data.get('verified_blocks', 0)}[/color]",
            markup=True,
            font_size="12sp",
        )
        stats_box.add_widget(self.speed_label)
        stats_box.add_widget(self.blocks_label)
        root.add_widget(stats_box)

        # Input & Verification Section
        input_container = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=110,
            spacing=6,
        )

        self.wallet_input = TextInput(
            text=self.data.get("wallet_address", ""),
            hint_text="Enter Web3 Wallet Address (0x... or Solana)",
            multiline=False,
            size_hint=(1, None),
            height=42,
            background_color=(0.1, 0.14, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1),
            font_size="12sp",
        )
        input_container.add_widget(self.wallet_input)

        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=40,
            spacing=8,
        )

        self.claim_btn = Button(
            text="Claim / Sync",
            background_color=(0, 0.7, 0.9, 1),
            bold=True,
            font_size="13sp",
        )
        self.claim_btn.bind(on_press=self.validate_and_claim)

        self.kyc_btn = Button(
            text="KYC Portal",
            background_color=(0.2, 0.3, 0.5, 1),
            bold=True,
            font_size="13sp",
        )
        self.kyc_btn.bind(on_press=self.open_kyc_modal)

        btn_row.add_widget(self.claim_btn)
        btn_row.add_widget(self.kyc_btn)
        input_container.add_widget(btn_row)

        self.status_msg = Label(
            text="",
            markup=True,
            font_size="11sp",
            size_hint=(1, None),
            height=18,
        )
        input_container.add_widget(self.status_msg)
        root.add_widget(input_container)

        # Mining Button
        self.mine_btn = Button(
            text="START PROOF-OF-INTELLIGENCE NODE",
            size_hint=(1, None),
            height=50,
            background_color=(0.0, 0.8, 0.4, 1),
            bold=True,
            font_size="14sp",
        )
        self.mine_btn.bind(on_press=self.toggle_mining)
        root.add_widget(self.mine_btn)

        # Logs Stream
        log_title = Label(
            text="[color=8892b0]NODE COMPUTATION STREAM (LOGS)[/color]",
            markup=True,
            font_size="10sp",
            size_hint=(1, None),
            height=18,
        )
        root.add_widget(log_title)

        self.log_scroll = ScrollView(size_hint=(1, 1))
        self.log_content = Label(
            text="[color=556677]>> Node ready. Awaiting operational trigger...[/color]\n",
            markup=True,
            font_size="10sp",
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.log_content.bind(
            texture_size=lambda instance, val: setattr(
                self.log_content, "height", val[1]
            )
        )
        self.log_content.bind(
            size=lambda instance, val: setattr(
                self.log_content, "text_size", (val[0], None)
            )
        )
        self.log_scroll.add_widget(self.log_content)
        root.add_widget(self.log_scroll)

        return root

    def load_user_data(self):
        default_data = {
            "username": "BARAT_Miner_01",
            "balance": 0.000000,
            "wallet_address": "",
            "kyc_status": "Unverified",
            "kyc_id": "",
            "verified_blocks": 0,
            "last_active": time.time(),
        }
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = default_data
        else:
            self.data = default_data
            self.save_user_data()

    def save_user_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def validate_and_claim(self, instance):
        wallet = self.wallet_input.text.strip()
        evm_pattern = r"^0x[a-fA-F0-9]{40}$"
        sol_pattern = r"^[1-9A-HJ-NP-za-km-z]{32,44}$"

        if not wallet:
            self.status_msg.text = (
                "[color=ff4444]Failed: Address box cannot be empty![/color]"
            )
            return

        is_evm = re.match(evm_pattern, wallet)
        is_sol = re.match(sol_pattern, wallet)

        if not (is_evm or is_sol):
            self.status_msg.text = "[color=ff3333]Failed: Invalid Address! Valid EVM or Solana required.[/color]"
            return

        self.data["wallet_address"] = wallet
        self.save_user_data()
        chain = "EVM" if is_evm else "SOLANA"
        self.status_msg.text = (
            f"[color=00ff66]Success: Valid {chain} linked & synced![/color]"
        )

    def open_kyc_modal(self, instance):
        box = BoxLayout(orientation="vertical", padding=14, spacing=10)
        box.add_widget(
            Label(
                text="[b]BARAT Identity Verification (KYC)[/b]",
                markup=True,
                font_size="15sp",
            )
        )
        box.add_widget(
            Label(
                text="Enter Govt ID / Passport / National ID Number:",
                font_size="11sp",
                color=(0.7, 0.8, 0.9, 1),
            )
        )

        id_input = TextInput(
            text=self.data.get("kyc_id", ""),
            multiline=False,
            size_hint=(1, None),
            height=40,
            background_color=(0.15, 0.2, 0.28, 1),
            foreground_color=(1, 1, 1, 1),
        )
        box.add_widget(id_input)

        modal_status = Label(
            text=f"Current Status: {self.data.get('kyc_status', 'Unverified')}",
            font_size="12sp",
            color=(0.9, 0.7, 0.2, 1),
        )
        box.add_widget(modal_status)

        action_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=40,
            spacing=8,
        )
        submit_btn = Button(
            text="Submit KYC", background_color=(0, 0.7, 0.5, 1)
        )
        close_btn = Button(
            text="Close", background_color=(0.5, 0.2, 0.2, 1)
        )
        action_row.add_widget(submit_btn)
        action_row.add_widget(close_btn)
        box.add_widget(action_row)

        popup = Popup(
            title="KYC Compliance Portal",
            content=box,
            size_hint=(0.9, 0.45),
            auto_dismiss=False,
        )

        def submit_kyc(btn):
            val = id_input.text.strip()
            if len(val) >= 6:
                self.data["kyc_id"] = val
                self.data["kyc_status"] = "Pending"
                self.save_user_data()
                self.kyc_tag.text = "[color=ffaa00]KYC: Pending[/color]"
                popup.dismiss()
                self.status_msg.text = "[color=ffaa00]KYC Submitted! Under decentralized verification.[/color]"
            else:
                modal_status.text = "Error: ID must be at least 6 characters!"

        submit_btn.bind(on_press=submit_kyc)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def toggle_mining(self, instance):
        if not self.is_mining:
            self.is_mining = True
            self.mine_btn.text = "HALT COMPUTATION NODE"
            self.mine_btn.background_color = (0.9, 0.2, 0.2, 1)
            self.mining_event = Clock.schedule_interval(
                self.process_mining_step, 1.0
            )
            self.append_log(
                "[color=00ff66]>> Node thread initialized. Solving PoI"
                " computations...[/color]"
            )
        else:
            self.is_mining = False
            self.mine_btn.text = "START PROOF-OF-INTELLIGENCE NODE"
            self.mine_btn.background_color = (0.0, 0.8, 0.4, 1)
            if self.mining_event:
                self.mining_event.cancel()
            self.append_log(
                "[color=ffaa00]>> Node thread suspended by operator.[/color]"
            )

    def process_mining_step(self, dt):
        increment = 0.0000694
        current_bal = self.data.get("balance", 0.0) + increment
        self.data["balance"] = current_bal
        self.balance_label.text = (
            f"[b][color=ffffff]{current_bal:.6f} BARAT[/color][/b]"
        )

        if int(time.time()) % 15 == 0:
            self.data["verified_blocks"] = (
                self.data.get("verified_blocks", 0) + 1
            )
            self.blocks_label.text = (
                f"[color=64ffda]Blocks: {self.data['verified_blocks']}[/color]"
            )
            tasks = [
                "Neural_Weight_Matrix_Normalized",
                "Genomic_Fold_Chunk_Validated",
                "Consensus_Hash_Proof_Signed",
                "Climate_Tensor_Block_Calculated",
            ]
            import random

            selected_task = random.choice(tasks)
            self.append_log(
                f"[color=00e5ff]>> Verified {selected_task} [Block"
                f" #{self.data['verified_blocks']}][/color]"
            )
            self.save_user_data()

    def append_log(self, msg):
        self.log_content.text += f"\n{msg}"


if __name__ == "__main__":
    BaratCoreApp().run()
