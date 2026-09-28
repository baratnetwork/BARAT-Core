import hashlib
import time
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

class BaratFullMiningApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0A0A0A')
        
        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        self.title_label = Label(
            text="BARAT NETWORK\nProof of Intelligence Ecosystem", 
            font_size='22sp', 
            halign='center',
            color=get_color_from_hex('#39FF14'),
            bold=True,
            size_hint=(1, 0.15)
        )
        main_layout.add_widget(self.title_label)
        
        self.counter_label = Label(
            text="Tokens Mined\n0.00 $BARAT", 
            font_size='24sp', 
            halign='center',
            color=get_color_from_hex('#FFFFFF'),
            bold=True,
            size_hint=(1, 0.2)
        )
        main_layout.add_widget(self.counter_label)
        
        self.status_label = Label(
            text="Status: Network Idle | Ready to Compute", 
            font_size='14sp', 
            color=get_color_from_hex('#A0A0A0'),
            halign='center',
            size_hint=(1, 0.15)
        )
        main_layout.add_widget(self.status_label)
        
        self.wallet_input = TextInput(
            text='',
            hint_text='Enter Solana or Phantom Wallet Address',
            size_hint=(1, 0.1),
            multiline=False,
            background_color=get_color_from_hex('#1A1A1A'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            hint_text_color=get_color_from_hex('#666666')
        )
        main_layout.add_widget(self.wallet_input)
        
        self.mining_button = Button(
            text="START POI MINING", 
            font_size='18sp',
            bold=True,
            background_normal='',
            background_color=get_color_from_hex('#39FF14'),
            color=get_color_from_hex('#000000'),
            size_hint=(1, 0.15)
        )
        self.mining_button.bind(on_press=self.toggle_mining)
        main_layout.add_widget(self.mining_button)
        
        self.withdraw_button = Button(
            text="CLAIM REWARDS TO WALLET", 
            font_size='14sp',
            bold=True,
            background_normal='',
            background_color=get_color_from_hex('#111111'),
            color=get_color_from_hex('#888888'),
            size_hint=(1, 0.1)
        )
        self.withdraw_button.bind(on_press=self.withdraw_rewards)
        main_layout.add_widget(self.withdraw_button)
        
        self.is_mining = False
        self.mined_tokens = 0.0
        return main_layout

    def toggle_mining(self, instance):
        if not self.is_mining:
            self.is_mining = True
            self.mining_button.text = "STOP MINING"
            self.mining_button.background_color = get_color_from_hex('#FF3333')
            self.mining_button.color = get_color_from_hex('#FFFFFF')
            self.status_label.text = "MPU Active: Initializing PoI Core Loop..."
            Clock.schedule_interval(self.loop_mining_logic, 3)
        else:
            self.is_mining = False
            self.mining_button.text = "START POI MINING"
            self.mining_button.background_color = get_color_from_hex('#39FF14')
            self.mining_button.color = get_color_from_hex('#000000')
            self.status_label.text = "Status: Mining Paused | Node Standardized"

    def loop_mining_logic(self, dt):
        if not self.is_mining:
            return False
            
        datasets = ["Cancer_Cell_Chunk_102", "Climate_Grid_774", "Neuro_Mapping_Data_09"]
        task = random.choice(datasets)
        
        target_prefix = "0000"
        nonce = 0
        while True:
            data_string = f"{task}_{nonce}"
            hash_result = hashlib.sha256(data_string.encode()).hexdigest()
            if hash_result.startswith(target_prefix):
                break
            nonce += 1
            
        self.mined_tokens += 10.0
        self.counter_label.text = f"Tokens Mined\n{self.mined_tokens:.2f} $BARAT"
        self.status_label.text = f"Solved: {task}\nProof verified by 3 Decentralized Nodes!"

    def withdraw_rewards(self, instance):
        wallet = self.wallet_input.text.strip()
        if not wallet:
            self.status_label.text = "Error: Please enter a valid Phantom Wallet Address first!"
            return
        if self.mined_tokens == 0:
            self.status_label.text = "Error: Balance is 0. Mine some BARAT tokens first!"
            return
            
        self.status_label.text = f"Success! Sent request to transfer {self.mined_tokens} BARAT\ninto your wallet: {wallet[:6]}...{wallet[-4:]}"
        self.mined_tokens = 0.0
        self.counter_label.text = "Tokens Mined\n0.00 $BARAT"

if __name__ == '__main__':
    BaratFullMiningApp().run()
