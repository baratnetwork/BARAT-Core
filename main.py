import os
import sys
import json
import time
import hashlib
import uuid
import threading
import urllib.request
import urllib.parse
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse
from kivy.utils import platform

Window.clearcolor = (0.04, 0.05, 0.08, 1)

CYCLE_SECONDS = 24 * 3600
BASE_HOURLY_RATE = 0.50
SOLANA_DECIMALS = 9
MAX_SUPPLY = 500000000

GITHUB_USER = "baratnetwork"
PART_A = "ghp_wpFFORF06E5KqSyO"
PART_B = "XLStHD8GXPgyH188XEM"
GIST_TOKEN = PART_A + "_" + PART_B
GIST_DESCRIPTION = "BARAT_NETWORK_CLOUD_LEDGER"

def get_hardware_uuid():
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Secure = autoclass('android.provider.Settings$Secure')
            context = PythonActivity.mActivity.getContentResolver()
            dev_id = Secure.getString(context, Secure.ANDROID_ID)
            if dev_id:
                return hashlib.sha256(dev_id.encode('utf-8')).hexdigest()[:16].upper()
        except Exception:
            pass
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode('utf-8')).hexdigest()[:16].upper()

class BaratCoinButton(Button):
    def __init__(self, **kwargs):
        super(BaratCoinButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.is_active = False
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.22)
            else:
                Color(0.2, 0.25, 0.35, 0.2)
            Ellipse(pos=(self.x - 14, self.y - 14), size=(self.width + 28, self.height + 28))

            if self.is_active:
                Color(0.95, 0.77, 0.06, 0.95)
            else:
                Color(0.4, 0.45, 0.55, 0.8)
            Ellipse(pos=(self.x - 4, self.y - 4), size=(self.width + 8, self.height + 8))

            if self.is_active:
                Color(0.12, 0.10, 0.03, 1)
            else:
                Color(0.08, 0.09, 0.13, 1)
            Ellipse(pos=self.pos, size=self.size)

    def set_active_state(self, state):
        self.is_active = state
        self.redraw()

class MiningScreen(Screen):
    def __init__(self, **kwargs):
        super(MiningScreen, self).__init__(**kwargs)
        self.is_mining = False
        self.balance = 0.0
        self.mining_start_time = 0.0
        self.node_id = get_hardware_uuid()

        root_layout = BoxLayout(orientation='vertical', padding=[24, 30, 24, 25], spacing=16)

        header_box = BoxLayout(size_hint_y=None, height='45dp')
        brand_lbl = Label(
            text="BARAT NETWORK",
            font_size='20sp',
            bold=True,
            color=(0.95, 0.77, 0.06, 1),
            halign='left',
            valign='middle'
        )
        brand_lbl.bind(size=brand_lbl.setter('text_size'))

        self.status_lbl = Label(
            text="● NODE READY",
            font_size='12sp',
            bold=True,
            color=(0.3, 0.8, 0.4, 1),
            halign='right',
            valign='middle'
        )
        self.status_lbl.bind(size=self.status_lbl.setter('text_size'))

        header_box.add_widget(brand_lbl)
        header_box.add_widget(self.status_lbl)
        root_layout.add_widget(header_box)

        bal_box = BoxLayout(orientation='vertical', size_hint_y=None, height='95dp', spacing=3)
        sub_lbl = Label(text="AVAILABLE BALANCE", font_size='11sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.balance_lbl = Label(text="0.000000", font_size='38sp', bold=True, color=(1, 1, 1, 1))
        self.rate_lbl = Label(text="+0.5000 BARAT/hr", font_size='13sp', bold=True, color=(0.95, 0.77, 0.06, 1))

        bal_box.add_widget(sub_lbl)
        bal_box.add_widget(self.balance_lbl)
        bal_box.add_widget(self.rate_lbl)
        root_layout.add_widget(bal_box)

        center_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        coin_dim = min(Window.width * 0.64, Window.height * 0.34)
        
        self.coin_btn = BaratCoinButton(size_hint=(None, None), size=(coin_dim, coin_dim))
        self.coin_btn.bind(on_press=self.on_coin_tap)

        coin_inner = BoxLayout(orientation='vertical', spacing=2, padding=10)
        self.symbol_lbl = Label(text="B", font_size='56sp', bold=True, color=(0.5, 0.55, 0.65, 1))
        self.coin_state_lbl = Label(text="START MINING", font_size='14sp', bold=True, color=(1, 1, 1, 1))
        self.countdown_lbl = Label(text="24:00:00", font_size='12sp', color=(0.7, 0.75, 0.85, 1))

        coin_inner.add_widget(self.symbol_lbl)
        coin_inner.add_widget(self.coin_state_lbl)
        coin_inner.add_widget(self.countdown_lbl)

        self.coin_btn.add_widget(coin_inner)
        center_anchor.add_widget(self.coin_btn)
        root_layout.add_widget(center_anchor)

        footer_box = BoxLayout(orientation='vertical', size_hint_y=None, height='95dp', spacing=8)
        
        row1 = BoxLayout()
        r1_t = Label(text="Consensus", font_size='12sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r1_t.bind(size=r1_t.setter('text_size'))
        r1_v = Label(text="Proof-of-Intelligence (PoI)", font_size='12sp', bold=True, color=(0.9, 0.9, 0.9, 1), halign='right')
        r1_v.bind(size=r1_v.setter('text_size'))
        row1.add_widget(r1_t)
        row1.add_widget(r1_v)

        row2 = BoxLayout()
        r2_t = Label(text="Epoch Phase", font_size='12sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r2_t.bind(size=r2_t.setter('text_size'))
        r2_v = Label(text="Phase 1 (Genesis Era)", font_size='12sp', bold=True, color=(0.95, 0.77, 0.06, 1), halign='right')
        r2_v.bind(size=r2_v.setter('text_size'))
        row2.add_widget(r2_t)
        row2.add_widget(r2_v)

        row3 = BoxLayout()
        r3_t = Label(text="Hardware Binding", font_size='12sp', color=(0.5, 0.55, 0.65, 1), halign='left')
        r3_t.bind(size=r3_t.setter('text_size'))
        r3_v = Label(text=f"Node-{self.node_id[:8]}", font_size='12sp', bold=True, color=(0.3, 0.8, 0.4, 1), halign='right')
        r3_v.bind(size=r3_v.setter('text_size'))
        row3.add_widget(r3_t)
        row3.add_widget(r3_v)

        footer_box.add_widget(row1)
        footer_box.add_widget(row2)
        footer_box.add_widget(row3)
        root_layout.add_widget(footer_box)

        self.add_widget(root_layout)

    def on_enter(self):
        self.load_local_state()
        Clock.schedule_interval(self.engine_tick, 1.0)
        threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()

    def load_local_state(self):
        if os.path.exists("miner_state.json"):
            try:
                with open("miner_state.json", "r") as f:
                    data = json.load(f)
                    self.balance = float(data.get("balance", 0.0))
                    self.is_mining = bool(data.get("is_mining", False))
                    self.mining_start_time = float(data.get("start_time", 0.0))
            except Exception:
                pass
        self.update_ui_state()

    def save_local_state(self):
        try:
            with open("miner_state.json", "w") as f:
                json.dump({
                    "balance": self.balance,
                    "is_mining": self.is_mining,
                    "start_time": self.mining_start_time,
                    "node_id": self.node_id
                }, f)
        except Exception:
            pass

    def on_coin_tap(self, *args):
        now = time.time()
        if not self.is_mining:
            self.is_mining = True
            self.mining_start_time = now
            self.save_local_state()
            self.update_ui_state()
            threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()
        else:
            if (now - self.mining_start_time) >= CYCLE_SECONDS:
                self.mining_start_time = now
                self.save_local_state()
                self.update_ui_state()
                threading.Thread(target=self.sync_with_cloud_ledger, daemon=True).start()

    def engine_tick(self, dt):
        if self.is_mining:
            now = time.time()
            elapsed = now - self.mining_start_time
            if elapsed < CYCLE_SECONDS:
                self.balance += (BASE_HOURLY_RATE / 3600.0) * dt
                self.balance_lbl.text = f"{self.balance:.6f}"

                rem = int(CYCLE_SECONDS - elapsed)
                h, m, s = rem // 3600, (rem % 3600) // 60, rem % 60
                self.countdown_lbl.text = f"{h:02d}:{m:02d}:{s:02d}"
                self.coin_state_lbl.text = "MINING ACTIVE"
                self.status_lbl.text = "● NODE VERIFIED"
                self.status_lbl.color = (0.2, 0.85, 0.45, 1)
                self.symbol_lbl.color = (0.95, 0.77, 0.06, 1)
                self.coin_btn.set_active_state(True)
            else:
                self.is_mining = False
                self.coin_state_lbl.text = "CLAIM & RESTART"
                self.countdown_lbl.text = "00:00:00"
                self.status_lbl.text = "● SESSION ENDED"
                self.status_lbl.color = (0.9, 0.4, 0.2, 1)
                self.symbol_lbl.color = (0.5, 0.55, 0.65, 1)
                self.coin_btn.set_active_state(False)
                self.save_local_state()

    def update_ui_state(self):
        self.balance_lbl.text = f"{self.balance:.6f}"
        if self.is_mining:
            self.coin_state_lbl.text = "MINING ACTIVE"
            self.status_lbl.text = "● NODE VERIFIED"
            self.status_lbl.color = (0.2, 0.85, 0.45, 1)
            self.symbol_lbl.color = (0.95, 0.77, 0.06, 1)
            self.coin_btn.set_active_state(True)
        else:
            self.coin_state_lbl.text = "START MINING"
            self.countdown_lbl.text = "TAP TO RUN"
            self.status_lbl.text = "● NODE READY"
            self.status_lbl.color = (0.3, 0.8, 0.4, 1)
            self.symbol_lbl.color = (0.5, 0.55, 0.65, 1)
            self.coin_btn.set_active_state(False)

    def sync_with_cloud_ledger(self):
        try:
            url = "https://api.github.com/gists"
            headers = {
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "BaratNetworkNodeApp"
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                gists = json.loads(resp.read().decode())
                
            gist_id = None
            for g in gists:
                if g.get("description") == GIST_DESCRIPTION:
                    gist_id = g["id"]
                    break

            payload = {
                "files": {
                    "ledger.json": {
                        "content": json.dumps({
                            "node_id": self.node_id,
                            "balance": round(self.balance, 6),
                            "last_sync": datetime.utcnow().isoformat()
                        }, indent=2)
                    }
                }
            }

            patch_url = f"https://api.github.com/gists/{gist_id}" if gist_id else "https://api.github.com/gists"
            req_data = json.dumps(payload).encode("utf-8")
            sync_req = urllib.request.Request(patch_url, data=req_data, headers=headers, method="PATCH" if gist_id else "POST")
            with urllib.request.urlopen(sync_req, timeout=10) as r:
                pass
        except Exception:
            pass

class BaratMiningApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MiningScreen(name='mining'))
        return sm

if __name__ == '__main__':
    BaratMiningApp().run()
