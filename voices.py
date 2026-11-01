"""Voice catalogs copied from HaizFlow (xayza/ReupMain).

Edge: src/haizflow/core/edge_voices.py - 6 voices, online, no model needed.
VieNeu: src/haizflow/core/vieneu_voices.py - 25 Vietnamese presets, VieNeu 3.8.3.
        Needs HaizFlow VieNeu resource pack (SDK + models, Windows .pyd files).
OmniVoice: src/haizflow/pipeline/omnivoice_tts.py OMNIVOICE_VOICE_INSTRUCTIONS
        - 41 presets. Needs HaizFlow OmniVoice model + worker.
        OmniVoice model is licensed for noncommercial use only (see HaizFlow README).

This file copies only the voice names/instructions, not the model files.
Model files are large and are NOT in the HaizFlow git repo either - they come
from HaizFlow resource packs.
"""

EDGE_VOICES = {
    "vi": (
        ("vi-VN-HoaiMyNeural", "Hoai My - Nu"),
        ("vi-VN-NamMinhNeural", "Nam Minh - Nam"),
    ),
    "en": (
        ("en-US-JennyNeural", "Jenny - Nu"),
        ("en-US-GuyNeural", "Guy - Nam"),
    ),
    "zh": (
        ("zh-CN-XiaoxiaoNeural", "Xiaoxiao - Nu"),
        ("zh-CN-YunxiNeural", "Yunxi - Nam"),
    ),
}

# (name, gender, region) - from VieNeu 3.8.3 voice bank
VIENEU_VOICES = (
    ("Hai Dang", "male", "Bac"),
    ("Truc Ly", "female", "Bac"),
    ("Thien Minh", "male", "Bac"),
    ("Mai Anh", "female", "Bac"),
    ("Thuy Dung", "female", "Nam"),
    ("Thien Tam Duc", "male", "Bac"),
    ("Ngoc Huyen", "female", "Bac"),
    ("Quang Son", "male", "Trung"),
    ("Ngoc Tran", "female", "Trung"),
    ("Minh Duc", "male", "Bac"),
    ("Pham Tuyen", "male", "Bac"),
    ("Thai Son", "male", "Nam"),
    ("Xuan Vinh", "male", "Bac"),
    ("Thanh Binh", "male", "Bac"),
    ("Ngoc Linh", "female", "Bac"),
    ("Doan Trang", "female", "Bac"),
    ("Thuc Doan", "female", "Nam"),
    ("Minh Triet", "male", "Nam"),
    ("My Duyen", "female", "Nam"),
    ("Quynh Anh", "female", "Bac"),
    ("Duc Tri", "male", "Nam"),
    ("Kim Thanh", "female", "Nam"),
    ("Adam", "male", "Nam"),
    ("Quoc Tuan", "male", "Bac"),
    ("Adam bua", "male", "Bac"),
)
# Original Vietnamese names with diacritics, for display in the GUI.
VIENEU_VOICES_VI = (
    "Hải Đăng", "Trúc Ly", "Thiện Minh", "Mai Anh", "Thùy Dung",
    "Thiền Tâm Đức", "Ngọc Huyền", "Quang Sơn", "Ngọc Trân", "Minh Đức",
    "Phạm Tuyên", "Thái Sơn", "Xuân Vĩnh", "Thanh Bình", "Ngọc Linh",
    "Đoan Trang", "Thục Đoan", "Minh Triết", "Mỹ Duyên", "Quỳnh Anh",
    "Đức Trí", "Kim Thanh", "Adam", "Quốc Tuấn", "Adam bựa",
)

# preset id -> instruction, from OmniVoice's strict instruction vocabulary
OMNIVOICE_VOICES = {
    "female": "female, young adult, moderate pitch",
    "male": "male, young adult, moderate pitch",
    "female_low": "female, young adult, low pitch",
    "deep": "male, young adult, low pitch",
    "bright": "female, young adult, high pitch",
    "male_high": "male, young adult, high pitch",
    "female_mature": "female, elderly, moderate pitch",
    "male_mature": "male, elderly, moderate pitch",
    "female_soprano": "female, young adult, very high pitch",
    "male_tenor": "male, young adult, very high pitch",
    "female_narrator": "female, elderly, low pitch",
    "male_narrator": "male, elderly, low pitch",
    "female_elder_high": "female, elderly, high pitch",
    "male_elder_high": "male, elderly, high pitch",
    "whisper": "whisper, young adult, moderate pitch",
    "whisper_low": "whisper, young adult, low pitch",
    "whisper_high": "whisper, young adult, high pitch",
    "whisper_elder": "whisper, elderly, low pitch",
    "elder": "elderly, moderate pitch",
    "storyteller": "elderly, low pitch",
    "child": "child, high pitch",
    "cartoon": "child, very high pitch",
    "child_soft": "child, moderate pitch",
    "child_low": "child, low pitch",
    "animated_bright": "child, very high pitch",
    "animated_soft": "child, moderate pitch",
    "comic_low": "child, low pitch",
    "tech_presenter": "male, young adult, moderate pitch",
    "show_host": "female, young adult, high pitch",
    "trailer_deep": "male, young adult, low pitch",
    "radio_warm": "female, young adult, low pitch",
    "mystery_whisper": "whisper, elderly, low pitch",
    "female_gentle": "female, young adult, moderate pitch",
    "male_soft": "male, young adult, low pitch",
    "female_confident": "female, young adult, high pitch",
    "male_broadcast": "male, elderly, moderate pitch",
    "child_bright": "child, high pitch",
    "elder_warm": "elderly, low pitch",
    "comic_high": "child, very high pitch",
    "documentary": "male, elderly, low pitch",
}

ALL_VOICES = {
    "edge": [voice for group in EDGE_VOICES.values() for voice, _label in group],
    "vieneu": [f"vieneu:{name}" for name in VIENEU_VOICES_VI],
    "omnivoice": [f"omnivoice:{name}" for name in OMNIVOICE_VOICES],
}
