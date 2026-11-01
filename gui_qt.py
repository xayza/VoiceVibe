#!/usr/bin/env python3
"""VoiceVibe GUI - dep, de dung, dung PySide6 + QSS (CSS cho Qt).

Vi sao chon PySide6 + QSS, khong phai Tkinter cu:
- QSS viet giong CSS: mau, bo tron, hover, padding, font - de lam dep.
- Qt la thu ma HaizFlow cung dung (Qt/QML), giao dien chuyen nghiep, chay tot tren Windows.
- Van dong goi duoc thanh 1 file exe bang PyInstaller, an mo la mo.
- Web UI bang HTML/CSS cung dep, nhung can mo trinh duyet + chay server, khong gon
  bang 1 file exe desktop.

Chay:  pip install -r requirements-qt.txt
       python gui_qt.py
Build exe: build-exe.bat (build gui_qt.py)
"""
import asyncio
import os
import shutil
import sys
import tempfile
import threading

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QLabel, QMainWindow, QMessageBox,
    QPushButton, QSlider, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout,
)

from models import INSTALL_STEPS, delete_model, list_models, save_haizflow_models_dir
from tts import synthesize
from voices import ALL_VOICES

QSS = """
QMainWindow { background: #12141c; }
QWidget { color: #eef1f8; font-family: Segoe UI, Arial; font-size: 14px; }
QTabWidget::pane { border: 1px solid #2a2f45; border-radius: 14px; background: #171a26; padding: 14px; }
QTabBar::tab { background: #1e2233; padding: 10px 22px; border-radius: 10px; margin-right: 6px; }
QTabBar::tab:selected { background: #6c5ce7; color: white; }
QTextEdit, QComboBox { background: #1e2233; border: 1px solid #2a2f45; border-radius: 10px; padding: 10px; }
QPushButton { background: #6c5ce7; color: white; border: none; border-radius: 12px; padding: 12px 20px; font-weight: bold; }
QPushButton:hover { background: #7d6df0; }
QPushButton#danger { background: #e74c3c; }
QPushButton#ghost { background: #232842; }
QLabel#title { font-size: 26px; font-weight: bold; color: white; }
QLabel#subtitle { color: #9aa3c0; font-size: 13px; }
QLabel#status { color: #00d2a8; }
QSlider::groove:horizontal { height: 6px; background: #2a2f45; border-radius: 3px; }
QSlider::handle:horizontal { width: 18px; background: #6c5ce7; border-radius: 9px; margin: -6px 0; }
"""


class Worker(threading.Thread):
    def __init__(self, coro, on_done):
        super().__init__(daemon=True)
        self.coro, self.on_done = coro, on_done

    def run(self):
        try:
            asyncio.run(self.coro)
            self.on_done(True, "Done.")
        except Exception as exc:  # noqa: BLE001
            self.on_done(False, str(exc))


class MainWindow(QMainWindow):
    done = Signal(bool, str)
    vc_done = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceVibe - Text to Speech & Voice Conversion")
        self.resize(760, 620)
        self.done.connect(self._on_done)
        self.vc_done.connect(self._on_vc_done)

        root = QWidget()
        layout = QVBoxLayout(root)
        title = QLabel("🎙️ VoiceVibe")
        title.setObjectName("title")
        subtitle = QLabel("Nhap text la co giong doc. Chon file la doi duoc giong. Khong can biet code.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._tts_tab(), "🎤 Text to Speech")
        tabs.addTab(self._vc_tab(), "🔄 Doi giong")
        tabs.addTab(self._models_tab(), "📦 Model")
        layout.addWidget(tabs)
        self.setCentralWidget(root)

    def _on_done(self, ok, msg):
        self.status.setText(msg if ok else f"Loi: {msg}")
        if not ok:
            QMessageBox.warning(self, "VoiceVibe", msg)

    def _tts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Text can doc:"))
        self.text = QTextEdit()
        self.text.setPlaceholderText("Dan script, truyen, bai viet... vao day. Text dai tu chia nho.")
        layout.addWidget(self.text)

        row = QHBoxLayout()
        row.addWidget(QLabel("Giong:"))
        self.voice = QComboBox()
        for provider, voices in ALL_VOICES.items():
            for voice in voices:
                self.voice.addItem(f"{provider}: {voice}", voice)
        row.addWidget(self.voice, 1)
        row.addWidget(QLabel("Toc do:"))
        self.rate = QComboBox()
        self.rate.addItems(["-20%", "-10%", "+0%", "+10%", "+20%", "+30%"])
        self.rate.setCurrentText("+0%")
        row.addWidget(self.rate)
        layout.addLayout(row)

        btn = QPushButton("▶  Tao xong nghe thu truoc")
        btn.clicked.connect(self._generate_preview)
        layout.addWidget(btn)
        self.save_btn = QPushButton("⬇  Nghe ok roi, tai xuong file mp3")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_preview)
        layout.addWidget(self.save_btn)
        layout.addWidget(QLabel("Luồng mới: tạo -> nghe thử -> ok mới tải. Không lưu ngay khi chưa nghe."))
        self.status = QLabel("San sang.")
        self.status.setObjectName("status")
        layout.addWidget(self.status)
        self.preview_path = ""
        return tab

    def _generate_preview(self):
        text = self.text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "VoiceVibe", "Chua co text de doc.")
            return
        # Generate to a temp file first, so the user can listen before saving.
        fd, self.preview_path = tempfile.mkstemp(suffix=".mp3", prefix="voicevibe_preview_")
        os.close(fd)
        self.save_btn.setEnabled(False)
        self.status.setText("Dang tao ban nghe thu...")
        voice = self.voice.currentData()
        rate = self.rate.currentText()
        def on_preview_done(ok, msg):
            if ok:
                self.save_btn.setEnabled(True)
                self.status.setText("Da tao xong. Dang mo ban nghe thu, nghe ok thi bam nut tai xuong.")
                # Open with the system default player on Windows; no extra audio lib needed.
                try:
                    os.startfile(self.preview_path)  # type: ignore[attr-defined]
                except Exception:
                    QMessageBox.information(self, "Nghe thu", f"Ban nghe thu o: {self.preview_path}")
            self.done.emit(ok, msg if not ok else "Da tao ban nghe thu.")
        Worker(synthesize(text, voice, rate, "+0Hz", "+0%", self.preview_path), on_preview_done).start()

    def _save_preview(self):
        if not self.preview_path or not os.path.exists(self.preview_path):
            QMessageBox.warning(self, "VoiceVibe", "Chua co ban nghe thu. Hay bam tao truoc.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Tai xuong file mp3", "output.mp3", "MP3 (*.mp3)")
        if not output:
            return
        shutil.copyfile(self.preview_path, output)
        self.status.setText(f"Da tai xuong: {output}")

    def _vc_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("1. File am thanh goc (wav):"))
        self.src = QTextEdit()
        self.src.setMaximumHeight(40)
        layout.addWidget(self.src)
        btn1 = QPushButton("Chon file goc")
        btn1.setObjectName("ghost")
        btn1.clicked.connect(lambda: self._pick(self.src))
        layout.addWidget(btn1)
        layout.addWidget(QLabel("2. File giong mau (wav, 1-30 giay, sach):"))
        self.ref = QTextEdit()
        self.ref.setMaximumHeight(40)
        layout.addWidget(self.ref)
        btn2 = QPushButton("Chon file giong mau")
        btn2.setObjectName("ghost")
        btn2.clicked.connect(lambda: self._pick(self.ref))
        layout.addWidget(btn2)
        row = QHBoxLayout()
        row.addWidget(QLabel("Model:"))
        self.model = QComboBox()
        self.model.addItems(["seed-vc", "rvc-v2", "openvoice-v2"])
        row.addWidget(self.model, 1)
        row.addWidget(QLabel("Che do:"))
        self.mode = QComboBox()
        self.mode.addItems(["light", "balanced", "quality"])
        row.addWidget(self.mode)
        layout.addLayout(row)
        btn = QPushButton("🔄  Doi giong xong nghe thu truoc")
        btn.clicked.connect(self._convert)
        layout.addWidget(btn)
        self.vc_save_btn = QPushButton("⬇  Nghe ok roi, tai xuong file wav")
        self.vc_save_btn.setEnabled(False)
        self.vc_save_btn.clicked.connect(self._save_vc_preview)
        layout.addWidget(self.vc_save_btn)
        self.vc_status = QLabel("San sang.")
        self.vc_status.setObjectName("status")
        layout.addWidget(self.vc_status)
        self.vc_preview_path = ""
        layout.addWidget(QLabel("Luồng mới, giống TTS: doi -> nghe thu -> ok moi tai. Light la mac dinh cho may yeu. Seed-VC la tot nhat neu khong train."))
        return tab

    def _pick(self, widget):
        path, _ = QFileDialog.getOpenFileName(self, "Chon file wav", "", "WAV (*.wav)")
        if path:
            widget.setPlainText(path)

    def _on_vc_done(self, ok, msg):
        self.vc_status.setText(msg)
        if not ok:
            QMessageBox.warning(self, "VoiceVibe", msg)

    def _convert(self):
        from voice_convert import main as vc_main
        src = self.src.toPlainText().strip()
        ref = self.ref.toPlainText().strip()
        if not src or not ref:
            QMessageBox.warning(self, "VoiceVibe", "Can ca file goc va file giong mau.")
            return
        fd, self.vc_preview_path = tempfile.mkstemp(suffix=".wav", prefix="voicevibe_vc_preview_")
        os.close(fd)
        self.vc_save_btn.setEnabled(False)
        self.vc_status.setText("Dang doi giong, tao ban nghe thu...")
        model = self.model.currentText()
        mode = self.mode.currentText()
        temp = self.vc_preview_path
        def run():
            try:
                code = vc_main(["--model", model, "--mode", mode, "--source", src, "--reference", ref, "--output", temp])
                if code == 0 and os.path.exists(temp) and os.path.getsize(temp) > 0:
                    self.vc_save_btn.setEnabled(True)
                    try:
                        os.startfile(temp)  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    self.vc_done.emit(True, "Da doi xong. Dang mo ban nghe thu, nghe ok thi bam nut tai xuong.")
                elif code == 0:
                    self.vc_done.emit(False, "Model chua cai hoac chua tao duoc file. Hay cai model theo huong dan trong tab Model roi thu lai.")
                else:
                    self.vc_done.emit(False, "Chuyen voice chua xong. Hay kiem tra model da cai chua.")
            except Exception as exc:
                self.vc_done.emit(False, str(exc))
        threading.Thread(target=run, daemon=True).start()

    def _save_vc_preview(self):
        if not self.vc_preview_path or not os.path.exists(self.vc_preview_path):
            QMessageBox.warning(self, "VoiceVibe", "Chua co ban nghe thu. Hay bam doi giong truoc.")
            return
        output, _ = QFileDialog.getSaveFileName(self, "Tai xuong file wav", "converted.wav", "WAV (*.wav)")
        if not output:
            return
        shutil.copyfile(self.vc_preview_path, output)
        self.vc_status.setText(f"Da tai xuong: {output}")

    def _models_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Model dang co tren may (model nam trong thu muc models/, khong nam trong git):"))
        self.model_text = QTextEdit()
        self.model_text.setReadOnly(True)
        layout.addWidget(self.model_text)
        self._refresh_models()
        row = QHBoxLayout()
        self.del_name = QComboBox()
        self.del_name.addItems(["seed-vc", "rvc-v2", "openvoice-v2", "omnivoice", "vieneu"])
        row.addWidget(self.del_name, 1)
        del_btn = QPushButton("🗑  Xoa model de nhe may")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._delete_model)
        row.addWidget(del_btn)
        layout.addLayout(row)
        layout.addWidget(QLabel("Cai giong local - chon 1 trong 2:"))
        row2 = QHBoxLayout()
        for name, label in [("omnivoice", "Cai OmniVoice"), ("vieneu", "Cai VieNeu")]:
            btn = QPushButton(label)
            btn.setObjectName("ghost")
            btn.clicked.connect(lambda _=False, n=name: self._install_local(n))
            row2.addWidget(btn)
        layout.addLayout(row2)
        return tab

    def _refresh_models(self):
        lines = []
        for item in list_models():
            state = f"da cai, {item['size_mb']} MB" if item["installed"] else "chua cai"
            lines.append(f"{item['name']}: {state}")
        self.model_text.setPlainText("\n".join(lines))

    def _delete_model(self):
        name = self.del_name.currentText()
        if QMessageBox.question(self, "Xoa model", f"Xoa model {name} de giai phong dung luong?") != QMessageBox.Yes:
            return
        freed = delete_model(name)
        QMessageBox.information(self, "Xoa model", f"Da xoa {name}, giai phong {freed} MB.")
        self._refresh_models()

    def _install_local(self, name):
        steps = "\n".join(INSTALL_STEPS[name])
        QMessageBox.information(self, f"Cai {name}", steps)
        folder = QFileDialog.getExistingDirectory(self, "Chon thu muc Models cua HaizFlow")
        if folder:
            save_haizflow_models_dir(folder)
            QMessageBox.information(self, "Da luu", f"Da luu duong dan HaizFlow: {folder}")
            self._refresh_models()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
