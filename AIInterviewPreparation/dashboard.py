"""
dashboard.py
Home Dashboard: welcome screen with app branding, quick-stats, and shortcut
cards into each major feature.
"""

import os

import customtkinter as ctk
from PIL import Image

from utils import COLORS, FONT_FAMILY, ASSETS_DIR


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Welcome banner
        banner = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=16)
        banner.pack(fill="x", padx=10, pady=15)

        top_row = ctk.CTkFrame(banner, fg_color="transparent")
        top_row.pack(fill="x", padx=25, pady=25)

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(64, 64))
                ctk.CTkLabel(top_row, image=logo_img, text="").pack(side="left", padx=(0, 20))
            except Exception:
                pass

        text_col = ctk.CTkFrame(top_row, fg_color="transparent")
        text_col.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            text_col, text="Welcome to AI Interview Preparation",
            font=(FONT_FAMILY, 24, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_col, text="Sharpen your resume, ace mock interviews, and test your technical "
                           "knowledge — all in one place, fully offline.",
            font=(FONT_FAMILY, 13), text_color=COLORS["text_muted"], wraplength=650, justify="left"
        ).pack(anchor="w", pady=(5, 0))

        # Quick stats row
        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(fill="x", padx=10, pady=5)
        sd = self.app.session_data
        self._stat_card(stats_row, "Resume Score", sd.get("resume_score"), 0)
        self._stat_card(stats_row, "Interview Score", sd.get("interview_score"), 1)
        self._stat_card(stats_row, "Quiz Score", sd.get("quiz_score"), 2)
        self._stat_card(stats_row, "Communication", sd.get("communication_score"), 3)
        for i in range(4):
            stats_row.grid_columnconfigure(i, weight=1)

        # Feature shortcut cards
        ctk.CTkLabel(
            scroll, text="Get Started", font=(FONT_FAMILY, 18, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=10, pady=(25, 10))

        shortcuts_row = ctk.CTkFrame(scroll, fg_color="transparent")
        shortcuts_row.pack(fill="x", padx=10)

        shortcuts = [
            ("📄 Resume Analysis", "Upload your resume and get an instant score.", "Resume Analysis"),
            ("🎤 Mock Interview", "Practice with typed or voice answers.", "Mock Interview"),
            ("🧠 Technical Quiz", "Test yourself across 8 core CS topics.", "Technical Quiz"),
            ("🗣  HR Questions", "Practice 50+ common HR questions.", "HR Questions"),
            ("📈 Results", "View your full performance report.", "Results"),
            ("🏆 Certificate", "Generate your completion certificate.", "Certificate"),
        ]

        for i, (title, desc, target) in enumerate(shortcuts):
            card = ctk.CTkFrame(shortcuts_row, fg_color=COLORS["card"], corner_radius=14)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            shortcuts_row.grid_columnconfigure(i % 3, weight=1)

            ctk.CTkLabel(card, text=title, font=(FONT_FAMILY, 15, "bold"),
                         text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(18, 5))
            ctk.CTkLabel(card, text=desc, font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"],
                         wraplength=220, justify="left").pack(anchor="w", padx=18, pady=(0, 12))
            ctk.CTkButton(
                card, text="Open →", height=32, corner_radius=8, fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                command=lambda t=target: self.app.show_frame(t)
            ).pack(anchor="w", padx=18, pady=(0, 18))

    def _stat_card(self, parent, label, value, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=14)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        display = f"{value:.0f}%" if isinstance(value, (int, float)) else "—"
        ctk.CTkLabel(card, text=label, font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"]).pack(
            anchor="w", padx=15, pady=(15, 2))
        ctk.CTkLabel(card, text=display, font=(FONT_FAMILY, 22, "bold"), text_color=COLORS["accent"]).pack(
            anchor="w", padx=15, pady=(0, 15))

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
