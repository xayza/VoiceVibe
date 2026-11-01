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
