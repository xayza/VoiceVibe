# TTS Tool - Text to Speech only

Tool rieng, chi co 1 chuc nang: nhap text -> tao file mp3 giong doc.
Khong tai video, khong dich, khong lam phu de, khong dang bai.

## Cai dat

```bash
pip install -r requirements.txt
```

Can mang internet, vi tool dung giong Edge TTS (mien phi, khong can API key).

## Cach dung - giao dien

```bash
python gui.py
```

Nhap text, chon giong, chon toc do, bam "Tao file mp3", chon noi luu.

## Cach dung - dong lenh

```bash
python tts.py --text "Xin chao, day la ban thu giong doc." --output hello.mp3
python tts.py --file script.txt --voice vi-VN-NamMinhNeural --rate +10% --output out.mp3
python tts.py --list-voices
```

Giong goi y:
- `vi-VN-HoaiMyNeural` - Tieng Viet, nu
- `vi-VN-NamMinhNeural` - Tieng Viet, nam
- `en-US-AriaNeural` - English, nu
- `en-US-GuyNeural` - English, nam

Text dai se tu chia nho theo cau roi noi lai bang ffmpeg (neu co ffmpeg).

## Chuyen voice (voice conversion) - model tot nhat hien nay

VoiceVibe co 2 loai: TTS (nhap text -> doc) va chuyen voice (am thanh goc -> giong khac).

Model khuyen nghi, theo tai lieu goc cua tung model:
- **Seed-VC** - tot nhat cho zero-shot, khong can train. Python 3.10, CUDA 11.8+,
  GPU NVIDIA 8 GB VRAM khuyen nghi (6 GB toi thieu), mau giong 1-30 giay sach.
  Cau hinh mac dinh: diffusion-steps 30, inference-cfg-rate 0.7, length-adjust 1.0,
  f0-condition tat cho noi chuyen, bat cho hat (30-50 steps).
- **RVC v2** - tot nhat neu train rieng 1 giong. 40k/48k, f0 bat, RMVPE,
  10-30 phut vocal sach de train, GPU 8 GB VRAM khuyen nghi. Dung qua Applio.
- **OpenVoice v2** - nhe, zero-shot, du phong khi khong co GPU manh.
- **HaizFlow clone** - VieNeu clone / OmniVoice reference, chi dung mau giong
  ma ban so huu hoac co quyen su dung. Can goi tai nguyen HaizFlow.

Chay chuyen voice:

```bash
python voice_convert.py --list-models
python voice_convert.py --model seed-vc --source input.wav --reference ref.wav --output out.wav
```

## Quan ly model - nut xoa de nhe may

Model khong nam trong git, chi nam trong thu muc `models/` tren may ban.
Trong giao dien, bam "Quan ly model", nhap ten model, bam "Xoa model da nhap"
la xoa sach thu muc do va giai phong dung luong, sau do tai lai khi can:

```bash
python voice_convert.py --delete-model seed-vc
python voice_convert.py --list-models
```

## Toi uu cho may nhe - chay tot

Nguyen tac: mac dinh la nhe, chi nang khi may du suc.
- **Dung Edge TTS truoc**: 0 MB model, khong can GPU, khong can tai model.
  Day la lua chon nhe nhat cho TTS.
- **Khong load model luc mo app**: GUI va CLI chi import Edge TTS khi bam tao,
  khong load Torch/ONNX luc khoi dong.
- **Mode light (mac dinh)**: chunk text nho 600 ky tu, Seed-VC diffusion-steps 12
  thay vi 30, RVC ban 32k thay vi 48k, ep CPU neu khong co GPU.
  ```bash
  python voice_convert.py --model seed-vc --mode light --device cpu --source in.wav --reference ref.wav --output out.wav
  ```
- **Seed-VC tren may khong co NVIDIA**: dung ban ONNX + DirectML, chay duoc
  tren GPU DirectX 12 thong thuong, khong bat buoc NVIDIA.
- **Cai dat nhe**: chi `pip install -r requirements.txt` (edge-tts).
  File `requirements-gpu.txt` (torch, onnxruntime) chi cai khi may co GPU va can
  chuyen voice nang.
- **Xoa model de nhe may**: model nam trong `models/`, khong nam trong git.
  Trong GUI bam "Quan ly model" -> nhap ten -> "Xoa model da nhap",
  hoac `python voice_convert.py --delete-model seed-vc`, roi tai lai khi can.
- **RAM toi thieu**: 8 GB RAM cho TTS Edge va OpenVoice, 16 GB khuyen nghi
  cho Seed-VC/RVC tren GPU.

## File exe - an mo la mo

Khong can cai Python, khong can chay lenh:
1. Vao repo VoiceVibe tren GitHub -> tab **Actions** -> lan chay moi nhat
   **Build Windows exe** -> tai artifact **VoiceVibe-Windows**, giai nen.
2. An dup file **VoiceVibe.exe** la mo giao dien, dan text, chon giong, bam tao mp3.

File exe duoc build tu dong bang GitHub Actions tren Windows (xem
`.github/workflows/build-exe.yml`), moi lan day code len main la co ban exe moi.
Neu muon tu build tren may Windows cua ban, chay file `build-exe.bat`.
