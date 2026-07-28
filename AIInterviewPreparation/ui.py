"""
ui.py
Reusable UI building blocks: the navigation Sidebar and the Settings frame.
"""

import os
import shutil
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from utils import (
    COLORS, FONT_FAMILY, ASSETS_DIR, REPORTS_DIR, RESUMES_DIR,
    load_settings, save_settings,
)

NAV_ITEMS = [
    ("Dashboard", "🏠"),
    ("Resume Analysis", "📄"),
    ("Mock Interview", "🎤"),
    ("Technical Quiz", "🧠"),
    ("HR Questions", "🗣"),
    ("Results", "📈"),
    ("Certificate", "🏆"),
    ("Settings", "⚙"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["sidebar"], width=230, corner_radius=0)
        self.app = app
        self.buttons = {}
        self.pack_propagate(False)
        self._build_ui()

    def _build_ui(self):
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(25, 20), padx=15)

        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(40, 40))
                ctk.CTkLabel(header, image=logo_img, text="").pack(side="left", padx=(0, 10))
            except Exception:
                pass

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="AI Interview", font=(FONT_FAMILY, 16, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Preparation", font=(FONT_FAMILY, 12),
                     text_color=COLORS["secondary"]).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x", padx=15, pady=(0, 15))

        for name, icon in NAV_ITEMS:
            btn = ctk.CTkButton(
                self, text=f"  {icon}   {name}", anchor="w", height=42, corner_radius=10,
                font=(FONT_FAMILY, 13), fg_color="transparent", hover_color=COLORS["card_light"],
                text_color=COLORS["text_muted"],
                command=lambda n=name: self.app.show_frame(n)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.buttons[name] = btn

        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)

        exit_btn = ctk.CTkButton(
            self, text="  ⏻   Exit", anchor="w", height=42, corner_radius=10,
            font=(FONT_FAMILY, 13, "bold"), fg_color=COLORS["danger"], hover_color="#B91C1C",
            text_color="white", command=self.app.confirm_exit
        )
        exit_btn.pack(fill="x", padx=12, pady=(5, 20), side="bottom")

    def set_active(self, name):
        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                btn.configure(fg_color=COLORS["primary"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_muted"])


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="⚙  Settings", font=(FONT_FAMILY, 26, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=30, pady=(25, 15))

        settings = load_settings()

        # Theme card
        theme_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        theme_card.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(theme_card, text="Appearance", font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 10))

        self.theme_var = ctk.StringVar(value=settings.get("theme", "dark"))
        row = ctk.CTkFrame(theme_card, fg_color="transparent")
        row.pack(anchor="w", padx=20, pady=(0, 20))
        ctk.CTkRadioButton(row, text="Dark Theme", variable=self.theme_var, value="dark",
                           command=self._apply_theme, fg_color=COLORS["primary"]).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(row, text="Light Theme", variable=self.theme_var, value="light",
                           command=self._apply_theme, fg_color=COLORS["primary"]).pack(side="left")

        # Voice card
        voice_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        voice_card.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(voice_card, text="Voice Interview", font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 10))

        self.voice_var = ctk.BooleanVar(value=settings.get("voice_enabled", True))
        voice_row = ctk.CTkFrame(voice_card, fg_color="transparent")
        voice_row.pack(anchor="w", padx=20, pady=(0, 20))
        ctk.CTkSwitch(voice_row, text="Enable microphone / voice answers", variable=self.voice_var,
                      command=self._apply_voice, progress_color=COLORS["accent"]).pack(anchor="w")

        # Data management card
        data_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        data_card.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(data_card, text="Data Management", font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkButton(data_card, text="🗑  Clear Saved Reports", height=38, corner_radius=10,
                      fg_color=COLORS["danger"], hover_color="#B91C1C",
                      command=self._clear_reports).pack(anchor="w", padx=20, pady=(0, 20))

        # About card
        about_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        about_card.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(about_card, text="About Application", font=(FONT_FAMILY, 15, "bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            about_card,
            text="AI Interview Preparation v1.0\n"
                 "A fully offline desktop app to help you prepare for interviews:\n"
                 "resume analysis, mock interviews (typed + voice), technical quizzes,\n"
                 "HR question practice, performance reports, and certificate generation.\n"
                 "No database is used — all data is stored locally as files.",
            font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"], justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def _apply_theme(self):
        theme = self.theme_var.get()
        settings = load_settings()
        settings["theme"] = theme
        save_settings(settings)
        ctk.set_appearance_mode("dark" if theme == "dark" else "light")
        messagebox.showinfo("Theme Changed",
                             f"{theme.capitalize()} theme applied. Some elements may need an app restart "
                             f"to fully update.")

    def _apply_voice(self):
        settings = load_settings()
        settings["voice_enabled"] = self.voice_var.get()
        save_settings(settings)

    def _clear_reports(self):
        confirm = messagebox.askyesno(
            "Clear Reports", "This will permanently delete all saved reports. Continue?"
        )
        if not confirm:
            return
        try:
            for folder in (REPORTS_DIR,):
                for f in os.listdir(folder):
                    file_path = os.path.join(folder, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            messagebox.showinfo("Reports Cleared", "All saved reports have been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear reports: {e}")
