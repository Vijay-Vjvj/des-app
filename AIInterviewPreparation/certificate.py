"""
certificate.py
Generates a professional completion certificate as a PDF and provides the
CustomTkinter frame that lets the user preview, download, and print it.
"""

import os
import subprocess
import sys
from tkinter import messagebox

import customtkinter as ctk

from utils import (
    COLORS, FONT_FAMILY, CERTIFICATES_DIR, today_str,
    generate_certificate_number,
)


def generate_certificate_pdf(candidate_name: str, course_name: str,
                              overall_score: float, output_path: str = None) -> str:
    """Creates a certificate PDF using reportlab and returns the file path."""
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    cert_number = generate_certificate_number()
    date_str = today_str()

    if output_path is None:
        safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (" ", "_")).strip() or "Candidate"
        filename = f"Certificate_{safe_name.replace(' ', '_')}_{cert_number}.pdf"
        output_path = os.path.join(CERTIFICATES_DIR, filename)

    width, height = landscape(A4)
    c = canvas.Canvas(output_path, pagesize=landscape(A4))

    bg = HexColor(COLORS["background"])
    primary = HexColor(COLORS["primary"])
    accent = HexColor(COLORS["accent"])
    white = HexColor("#FFFFFF")

    # Background
    c.setFillColor(bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Decorative border
    c.setStrokeColor(primary)
    c.setLineWidth(6)
    c.rect(1 * cm, 1 * cm, width - 2 * cm, height - 2 * cm, fill=0, stroke=1)
    c.setStrokeColor(accent)
    c.setLineWidth(2)
    c.rect(1.4 * cm, 1.4 * cm, width - 2.8 * cm, height - 2.8 * cm, fill=0, stroke=1)

    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(width / 2, height - 4 * cm, "CERTIFICATE OF COMPLETION")

    c.setFillColor(accent)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 5.2 * cm, "AI Interview Preparation")

    # Body
    c.setFillColor(white)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 7.5 * cm, "This certificate is proudly presented to")

    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 9 * cm, candidate_name)

    c.setFillColor(white)
    c.setFont("Helvetica", 13)
    c.drawCentredString(
        width / 2, height - 10.5 * cm,
        f"for successfully completing the \"{course_name}\" program"
    )
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(accent)
    c.drawCentredString(width / 2, height - 11.5 * cm, f"Overall Score: {overall_score:.1f}%")

    # Footer info
    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    c.drawString(2.5 * cm, 2 * cm, f"Date: {date_str}")
    c.drawRightString(width - 2.5 * cm, 2 * cm, f"Certificate No: {cert_number}")

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(HexColor(COLORS["text_muted"]))
    c.drawCentredString(width / 2, 1.6 * cm, "AI Interview Preparation - Generated Certificate")

    c.save()
    return output_path


class CertificateFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self.last_pdf_path = None
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="🏆 Certificate Generator",
            font=(FONT_FAMILY, 26, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            self, text="Generate a professional certificate based on your overall performance.",
            font=(FONT_FAMILY, 14), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 20))

        form_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        form_card.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(form_card, text="Candidate Name", font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["secondary"]).pack(anchor="w", padx=20, pady=(20, 4))
        self.name_entry = ctk.CTkEntry(form_card, placeholder_text="Enter your full name",
                                        height=38, corner_radius=8)
        self.name_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(form_card, text="Course Name", font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["secondary"]).pack(anchor="w", padx=20, pady=(15, 4))
        self.course_entry = ctk.CTkEntry(form_card, height=38, corner_radius=8)
        self.course_entry.insert(0, "AI Interview Preparation Program")
        self.course_entry.pack(fill="x", padx=20)

        score = self._get_overall_score()
        ctk.CTkLabel(
            form_card, text=f"Overall Score (auto-calculated): {score:.1f}%",
            font=(FONT_FAMILY, 13), text_color=COLORS["accent"]
        ).pack(anchor="w", padx=20, pady=(15, 20))

        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(btn_row, text="👁  Preview", height=42, corner_radius=10,
                      fg_color=COLORS["secondary"], hover_color=COLORS["primary_hover"],
                      command=self.preview_certificate).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="⬇  Download PDF", height=42, corner_radius=10,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      command=self.generate_and_open).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="🖨  Print", height=42, corner_radius=10,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      command=self.print_certificate).pack(side="left")

        self.status_label = ctk.CTkLabel(self, text="", font=(FONT_FAMILY, 12),
                                          text_color=COLORS["text_muted"])
        self.status_label.pack(anchor="w", padx=30, pady=10)

    def _get_overall_score(self):
        sd = self.app.session_data
        scores = [sd.get("resume_score"), sd.get("interview_score"),
                  sd.get("quiz_score"), sd.get("communication_score")]
        valid = [s for s in scores if isinstance(s, (int, float))]
        return sum(valid) / len(valid) if valid else 0.0

    def _generate(self):
        name = self.name_entry.get().strip() or "Candidate"
        course = self.course_entry.get().strip() or "AI Interview Preparation Program"
        score = self._get_overall_score()
        path = generate_certificate_pdf(name, course, score)
        self.last_pdf_path = path
        return path

    def preview_certificate(self):
        try:
            path = self._generate()
            self.status_label.configure(text=f"Certificate generated: {os.path.basename(path)}")
            self._open_file(path)
        except Exception as e:
            messagebox.showerror("Certificate Error", str(e))

    def generate_and_open(self):
        try:
            path = self._generate()
            self.status_label.configure(text=f"Saved to: {path}")
            messagebox.showinfo("Certificate Saved", f"Certificate saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Certificate Error", str(e))

    def print_certificate(self):
        try:
            path = self.last_pdf_path or self._generate()
            if sys.platform.startswith("win"):
                os.startfile(path, "print")
            else:
                self._open_file(path)
                messagebox.showinfo("Print", "Please use your PDF viewer's print option.")
        except Exception as e:
            messagebox.showerror("Print Error", str(e))

    def _open_file(self, path):
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception:
            pass
