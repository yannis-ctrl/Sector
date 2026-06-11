import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── core/storage.py ──────────────────────────────────────
import json
from pathlib import Path

DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "data"

class Storage:
    def __init__(self, filename):
        self.path = DATA_DIR / filename
        DATA_DIR.mkdir(exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, key):
        return self._read().get(key)

    def set(self, key, value):
        data = self._read()
        data[key] = value
        self._write(data)

    def all(self):
        return self._read()

# ── core/auth.py ─────────────────────────────────────────
import hashlib
import uuid
import time

user_store = Storage("users.json")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    if user_store.get(username):
        return False, "Nom d'utilisateur deja pris."
    data = {
        "username": username,
        "password_hash": hash_password(password),
        "user_id": str(uuid.uuid4()),
        "avatar": "",
        "bio": "",
        "followers": [],
        "following": [],
        "created_at": time.time()
    }
    user_store.set(username, data)
    return True, "Compte cree avec succes."

def login(username, password):
    data = user_store.get(username)
    if not data:
        return False, "Utilisateur introuvable."
    if data["password_hash"] != hash_password(password):
        return False, "Mot de passe incorrect."
    return True, "Connexion reussie."

# ── screens ──────────────────────────────────────────────
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=15)
        layout.add_widget(Label(text="SECTOR", font_size=40, bold=True))
        layout.add_widget(Label(text="", size_hint_y=0.1))
        self.username_input = TextInput(
            hint_text="Nom d'utilisateur",
            multiline=False,
            size_hint_y=None,
            height=45
        )
        self.password_input = TextInput(
            hint_text="Mot de passe",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=45
        )
        self.message_label = Label(text="", color=(1, 0.3, 0.3, 1))
        btn_login = Button(
            text="Se connecter",
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.6, 1, 1)
        )
        btn_register = Button(
            text="Creer un compte",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.8, 0.4, 1)
        )
        btn_login.bind(on_press=self.handle_login)
        btn_register.bind(on_press=self.handle_register)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.message_label)
        layout.add_widget(btn_login)
        layout.add_widget(btn_register)
        self.add_widget(layout)

    def handle_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.message_label.text = "Remplis tous les champs."
            return
        success, msg = login(username, password)
        self.message_label.text = msg
        if success:
            App.get_running_app().current_user = username
            App.get_running_app().go_to("feed")

    def handle_register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.message_label.text = "Remplis tous les champs."
            return
        success, msg = register(username, password)
        self.message_label.text = msg

class FeedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="SECTOR - Feed", font_size=28, bold=True))
        layout.add_widget(Label(text="Bienvenue ! Les videos apparaitront ici."))
        btn_logout = Button(
            text="Se deconnecter",
            size_hint_y=None,
            height=50,
            background_color=(0.9, 0.2, 0.2, 1)
        )
        btn_logout.bind(on_press=self.handle_logout)
        layout.add_widget(btn_logout)
        self.add_widget(layout)

    def handle_logout(self, instance):
        App.get_running_app().current_user = None
        App.get_running_app().go_to("login")

# ── app ──────────────────────────────────────────────────
class SectorApp(App):
    current_user = None

    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(FeedScreen(name="feed"))
        return self.sm

    def go_to(self, screen_name):
        self.sm.current = screen_name

if __name__ == "__main__":
    SectorApp().run()
