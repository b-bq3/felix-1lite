# FELIX-1lite

نموذج لغوي صغير بالعربية الفصحى. مبني من الصفر.

---

## تجربة سريعة

| الرابط | الوصف |
|--------|-------|
| [huggingface.co/spaces/b-bq3/felix-1lite-demo](https://huggingface.co/spaces/b-bq3/felix-1lite-demo) | عرض حي (Static Space) |
| [huggingface.co/b-bq3/felix-1lite](https://huggingface.co/b-bq3/felix-1lite) | Model repo (الأوزان) |

---

## تشغيل محلي

```python
import sys
sys.path.insert(0, '.')
from felix import chat

print(chat("ما هو الذكاء الاصطناعي؟"))
```

---

## تدريب على Google Colab (~30 دقيقة)

```python
!git clone https://github.com/b-bq3/felix-1lite.git
%cd felix-1lite
!pip install torch --quiet
!python generate_data.py
!python felix.py  # التدريب الكامل
```

---

## الملفات

| ملف | الوصف |
|-----|-------|
| `felix.py` | النموذج (نظيف، بدون تعليقات) |
| `app.py` | واجهة Gradio |
| `generate_data.py` | توليد بيانات FELIX |
| `felix_data.txt` | 200K حرف عربي |
| `train_demo.py` | تدريب سريع (5 دقائق، 0.9M params) |
| `train_full.py` | تدريب كامل (30 دقيقة، 1.9M params) |
| `chat_cli.py` | محادثة تفاعلية في الطرفية |
| `site/` | Static Space (UI نظيف) |
| `TRAINING.md` | دليل التدريب المفصّل |

---

## تخصيص التدريب

عدّل `CONFIG` في `felix.py`:

```python
CONFIG = {
    "n_layer": 6,        # الطبقات (12 لنموذج أقوى)
    "n_head": 8,         # رؤوس الانتباه
    "n_embd": 384,       # بعد التضمين
    "block_size": 256,   # نافذة السياق
    "max_iters": 3000,   # عدد خطوات التدريب
    "learning_rate": 3e-4,
}
```

---

## الترخيص

MIT

---

صُنع بالعربية الفصحى 🤖