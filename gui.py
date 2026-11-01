#!/usr/bin/env python3
"""Simple Tkinter GUI for the TTS-only tool. No video, no translation, no subtitles.

Run:  python gui.py
"""
import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models import delete_model, list_models
from tts import VOICES, synthesize

DEFAULT_VOICE = "vi-VN-HoaiMyNeural"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TTS Tool - Text to Speech")
        self.geometry("640x520")

        ttk.Label(self, text="Nhap text can doc:").pack(anchor="w", padx=10, pady=(10, 0))
        self.text = tk.Text(self, height=14, wrap="word")
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text="Giong:").pack(side="left")
        self.voice = tk.StringVar(value=DEFAULT_VOICE)
        ttk.Combobox(frame, textvariable=self.voice, values=list(VOICES), width=28).pack(side="left", padx=5)
        ttk.Label(frame, text="Toc do:").pack(side="left", padx=(10, 0))
        self.rate = tk.StringVar(value="+0%")
        ttk.Combobox(frame, textvariable=self.rate, values=["-30%", "-20%", "-10%", "+0%", "+10%", "+20%", "+30%"], width=8).pack(side="left", padx=5)

        self.status = tk.StringVar(value="San sang.")
        ttk.Label(self, textvariable=self.status).pack(anchor="w", padx=10)
        ttk.Button(self, text="Tao file mp3", command=self.generate).pack(pady=10)
        ttk.Button(self, text="Quan ly model (xem / xoa model)", command=self.manage_models).pack(pady=5)

    def manage_models(self):
        lines = []
        for item in list_models():
            state = f"da cai, {item['size_mb']} MB" if item["installed"] else "chua cai"
            lines.append(f"{item['name']}: {state}")
        top = tk.Toplevel(self)
        top.title("Model - xoa de nhe may")
        tk.Label(top, text="\n".join(lines), justify="left").pack(padx=15, pady=10)
        entry = ttk.Entry(top, width=30)
        entry.pack(padx=15)
        entry.insert(0, "seed-vc")
        def do_delete():
            name = entry.get().strip()
            if not name:
                return
            if not messagebox.askyesno("Xoa model", f"Xoa model {name} de giai phong dung luong?"):
                return
            try:
                freed = delete_model(name)
                messagebox.showinfo("Xoa model", f"Da xoa {name}, giai phong {freed} MB.")
                top.destroy()
            except Exception as exc:
                messagebox.showerror("Xoa model", str(exc))
        ttk.Button(top, text="Xoa model da nhap", command=do_delete).pack(pady=10)
        ttk.Label(top, text="Cai giong local (chon 1 trong 2):").pack(pady=(10, 0))
        def show_install(name):
            from models import INSTALL_STEPS, save_haizflow_models_dir
            from tkinter import filedialog as _fd
            info = tk.Toplevel(top)
            info.title(f"Cai {name}")
            tk.Label(info, text="\n".join(INSTALL_STEPS[name]), justify="left").pack(padx=15, pady=10)
            def pick():
                folder = _fd.askdirectory(title="Chon thu muc Models cua HaizFlow")
                if folder:
                    save_haizflow_models_dir(folder)
                    messagebox.showinfo("Da luu", f"Da luu duong dan HaizFlow: {folder}")
                    info.destroy()
            ttk.Button(info, text="Chon thu muc Models cua HaizFlow", command=pick).pack(pady=10)
        ttk.Button(top, text="Cai OmniVoice", command=lambda: show_install("omnivoice")).pack(pady=2)
        ttk.Button(top, text="Cai VieNeu", command=lambda: show_install("vieneu")).pack(pady=2)

    def generate(self):
        text = self.text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("TTS Tool", "Chua co text de doc.")
            return
        output = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3", "*.mp3")])
        if not output:
            return
        self.status.set("Dang tao giong doc...")
        threading.Thread(target=self._run, args=(text, output), daemon=True).start()

    def _run(self, text, output):
        try:
            asyncio.run(synthesize(text, self.voice.get(), self.rate.get(), "+0Hz", "+0%", output))
            self.after(0, lambda: self.status.set(f"Done: {output}"))
        except Exception as exc:  # noqa: BLE001 - show any TTS error to the user
            self.after(0, lambda: (self.status.set("Loi, thu lai."), messagebox.showerror("TTS Tool", str(exc))))


if __name__ == "__main__":
    App().mainloop()
