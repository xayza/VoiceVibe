#!/usr/bin/env python3
"""Voice conversion in VoiceVibe: source audio -> target voice audio.

This is a thin, honest wrapper, not a fake converter:
- If the selected model folder is not installed, it prints the install
  command from models.py and stops, instead of pretending to convert.
- If Seed-VC is installed, it calls its inference script with the
  recommended config from models.py.
- RVC / OpenVoice need their own WebUI/CLI; this script prints the exact
  next step for the installed model.

Usage:
    python voice_convert.py --model seed-vc --source input.wav --reference ref.wav --output out.wav
    python voice_convert.py --list-models
    python voice_convert.py --delete-model seed-vc
"""
import argparse
import subprocess
import sys
from pathlib import Path

from models import MODELS, PRESETS, delete_model, list_models, model_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Voice conversion")
    parser.add_argument("--model", default="seed-vc", choices=list(MODELS))
    parser.add_argument("--mode", default="light", choices=["light", "balanced", "quality"],
                        help="light: may yeu, chay nhanh, it RAM/VRAM. Mac dinh la light.")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"],
                        help="auto: tu chon, cpu: ep chay CPU, cuda: ep chay GPU NVIDIA")
    parser.add_argument("--source", help="File am thanh goc (wav)")
    parser.add_argument("--reference", help="File giong mau (wav, 1-30 giay cho Seed-VC)")
    parser.add_argument("--output", default="converted.wav")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--delete-model", help="Xoa model de nhe may, vi du: seed-vc")
    args = parser.parse_args(argv)

    if args.list_models:
        for item in list_models():
            state = f"da cai, {item['size_mb']} MB" if item["installed"] else "chua cai"
            print(f"{item['name']}: {state} - {item['label']}")
        return 0

    if args.delete_model:
        freed = delete_model(args.delete_model)
        print(f"Da xoa {args.delete_model}, giai phong {freed} MB.")
        return 0

    if not args.source or not args.reference:
        parser.error("--source va --reference la bat buoc de chuyen voice.")
    path = model_path(args.model)
    if not path.exists():
        print(f"Model {args.model} chua cai. Cai bang:\n  {MODELS[args.model]['install']}")
        return 2
    if args.model == "seed-vc":
        script = path / "inference_v2.py"
        if not script.exists():
            print("Khong tim thay inference_v2.py trong models/seed-vc. Hay cai lai Seed-VC.")
            return 2
        cfg = MODELS["seed-vc"]["config"]
        preset = PRESETS[args.mode]
        device = args.device if args.device != "auto" else preset["device"]
        print(f"Mode: {args.mode} (diffusion-steps {preset['seed_vc_diffusion_steps']}, device {device})")
        cmd = [sys.executable, str(script),
               "--source", args.source, "--target", args.reference, "--output", args.output,
               "--diffusion-steps", str(preset["seed_vc_diffusion_steps"]),
               "--inference-cfg-rate", str(cfg["inference_cfg_rate"])]
        if device == "cpu":
            cmd += ["--device", "cpu"]
        print("Chay:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        print(f"Done: {args.output}")
        return 0
    print(f"Model {args.model} da cai tai {path}. Mo tool goc cua no de chay, "
          f"vi moi model co giao dien rieng. Huong dan: {MODELS[args.model]['install']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
