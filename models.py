"""Model manager for VoiceVibe.

Models are NOT stored in git. They live in a local `models/` folder on the
user's machine, so deleting a model actually frees disk space.
The GUI's model tab lists installed models, their size, and has a Delete
button. Downloading a new model just means installing its folder again.

Recommended configs (from each project's own docs, see README):
- Seed-VC: best zero-shot voice conversion today, no training needed.
  Python 3.10, CUDA 11.8+, NVIDIA GPU 8 GB VRAM recommended (6 GB minimum),
  reference clip 1-30 seconds, clean, no music/noise.
  VC defaults: diffusion-steps 30, inference-cfg-rate 0.7, length-adjust 1.0,
  f0-condition off for speech, on for singing (then 30-50 steps).
- RVC v2: best trained voice conversion, via Applio or RVC WebUI.
  40k or 48k sample rate, f0 on, RMVPE pitch extraction,
  10-30 minutes of clean isolated vocal for training, 8 GB VRAM recommended.
- OpenVoice v2: light zero-shot tone-color conversion, fallback if no GPU.
- HaizFlow clone: VieNeu clone / OmniVoice reference voice, only with a
  sample the user owns or has permission to use. Needs HaizFlow packs.
"""
import json
import shutil
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / "models"

# Light-machine presets: speed first, quality second. Light mode is the
# default recommendation on a weak machine, even if quality drops a bit.
PRESETS = {
    "light": {"seed_vc_diffusion_steps": 12, "rvc_sample_rate": "32k", "chunk_chars": 600, "device": "cpu"},
    "balanced": {"seed_vc_diffusion_steps": 20, "rvc_sample_rate": "40k", "chunk_chars": 900, "device": "auto"},
    "quality": {"seed_vc_diffusion_steps": 30, "rvc_sample_rate": "48k", "chunk_chars": 1200, "device": "cuda"},
}
LIGHT_NOTES = (
    "May nhe: dung Edge TTS truoc (0 MB model, khong can GPU). "
    "Seed-VC dung ban ONNX + DirectML neu khong co NVIDIA, hoac ban small 22050. "
    "RVC dung ban 32k thay vi 48k. Luon xoa model khong dung de nhe may."
)


MODELS = {
    "seed-vc": {
        "label": "Seed-VC (zero-shot, tot nhat hien nay)",
        "kind": "voice-conversion",
        "needs_gpu": "8 GB VRAM khuyen nghi, 6 GB toi thieu",
        "reference": "1-30 giay, sach, khong nhac nen",
        "config": {"diffusion_steps": 30, "inference_cfg_rate": 0.7, "length_adjust": 1.0, "f0_condition": False},
        "install": "git clone https://github.com/Plachtaa/seed-vc.git models/seed-vc && cd models/seed-vc && python download_weights.py",
    },
    "rvc-v2": {
        "label": "RVC v2 (train rieng, chat luong cao)",
        "kind": "voice-conversion",
        "needs_gpu": "8 GB VRAM khuyen nghi, 6 GB toi thieu",
        "reference": "10-30 phut vocal sach de train, hoac model .pth co san",
        "config": {"sample_rate": "40k", "f0": True, "f0_method": "rmvpe"},
        "install": "Dung Applio (applio.org) hoac RVC WebUI, dat model .pth vao models/rvc-v2/",
    },
    "openvoice-v2": {
        "label": "OpenVoice v2 (nhe, zero-shot)",
        "kind": "voice-conversion",
        "needs_gpu": "GPU khuyen nghi, CPU van chay duoc cham hon",
        "reference": "1 vai giay giong mau",
        "config": {},
        "install": "git clone https://github.com/myshell-ai/OpenVoice.git models/openvoice-v2",
    },
    "omnivoice": {
        "label": "OmniVoice (tu HaizFlow, phi thuong mai)",
        "kind": "tts",
        "needs_gpu": "Theo goi HaizFlow CPU/GPU",
        "reference": "Khong can, dung preset trong voices.py",
        "config": {},
        "install": "Can goi tai nguyen HaizFlow, chi duong dan MODELS_DIR cua HaizFlow",
    },
    "vieneu": {
        "label": "VieNeu 3.8.3 (tu HaizFlow, tieng Viet)",
        "kind": "tts",
        "needs_gpu": "CPU/GPU theo goi HaizFlow, Windows .pyd",
        "reference": "Khong can, dung preset trong voices.py",
        "config": {},
        "install": "Can goi tai nguyen HaizFlow VieNeu, chi duong dan MODELS_DIR cua HaizFlow",
    },
}


def model_path(name):
    return MODELS_DIR / name


def dir_size(path):
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def list_models():
    """Return status for every known model, with size in MB."""
    out = []
    for name, info in MODELS.items():
        path = model_path(name)
        out.append({
            "name": name,
            "label": info["label"],
            "installed": path.exists(),
            "size_mb": round(dir_size(path) / 1024 / 1024, 1),
            "path": str(path),
        })
    return out


def delete_model(name):
    """Delete a model's local folder. Returns MB freed. Refuses unknown names."""
    if name not in MODELS:
        raise ValueError(f"Model khong biet: {name}")
    path = model_path(name)
    freed = dir_size(path)
    if path.exists():
        shutil.rmtree(path)
    return round(freed / 1024 / 1024, 1)


def status_text():
    lines = []
    for item in list_models():
        state = f"da cai, {item['size_mb']} MB" if item["installed"] else "chua cai"
        lines.append(f"{item['name']}: {state}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(status_text())
