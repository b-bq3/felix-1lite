# FELIX-1lite �

نموذج لغوي صغير (~25M parameters) بالعربية الفصحى. مبني من الصفر بدون أي نموذج جاهز.

---

## ⚡ جرب FELIX بدون تحميل

| الخيار | الرابط |
|--------|--------|
| 🌐 **عرض حي (Static Space)** | [huggingface.co/spaces/b-bq3/felix-1lite-demo](https://huggingface.co/spaces/b-bq3/felix-1lite-demo) |
| 🤗 **Model repo على HF** | [huggingface.co/b-bq3/felix-1lite](https://huggingface.co/b-bq3/felix-1lite) |
| 📦 **الكود على GitHub** | [github.com/b-bq3/felix-1lite](https://github.com/b-bq3/felix-1lite) |

---

## ✨ المميزات

- ✅ محادثة عامة بالعربية الفصحى
- ✅ توليد أكواد (Python, JavaScript)
- ✅ أفكار إبداعية من لا شيء
- ✅ شخصية فيلسوف ساخر متمرد
- ✅ يتكيّف مع شخصيتك (عبر fine-tuning)
- ✅ MIT License — استخدمه كيفما تشاء

---

## 🚀 تشغيل سريع

### 1) على Google Colab (~30 دقيقة)

```python
!git clone https://github.com/b-bq3/felix-1lite.git
%cd felix-1lite
!pip install torch --quiet
!python generate_data.py
!python felix.py
```

### 2) محادثة بعد التدريب

```python
from felix import chat
print(chat("ما هو الذكاء الاصطناعي؟"))
```

---

## 📁 الملفات

| ملف | الوصف |
|-----|-------|
| `felix.py` | النموذج الكامل (مع تعليقات) |
| `felix_clean.py` | نسخة production بدون تعليقات |
| `app.py` | واجهة Gradio |
| `app_clean.py` | نسخة production |
| `generate_data.py` | توليد بيانات FELIX |
| `felix_data.txt` | بيانات أولية (200K حرف) |
| `TRAINING.md` | دليل التدريب المفصّل |
| `README.md` | هذا الملف |

---

## 📚 أدلة مفصّلة

- **[TRAINING.md](TRAINING.md)** — تدريب خطوة بخطوة
- **[الـ Static Space](https://huggingface.co/spaces/b-bq3/felix-1lite-demo)** — عرض حي

---

## 🛠️ تعديل الإعدادات

في `felix.py` → `CONFIG`:

```python
CONFIG = {
    "block_size": 256,
    "n_layer": 6,
    "n_head": 8,
    "n_embd": 384,
    "batch_size": 32,
    "learning_rate": 3e-4,
    "max_iters": 3000,
}
```

---

## 📊 الحجم والأداء

- **Parameters:** ~25M
- **حجم النموذج بعد التدريب:** ~100 MB
- **وقت التدريب على T4:** 30-45 دقيقة
- **VRAM المطلوب:** 2-3 GB
- **سرعة التوليد:** 10-20 tokens/ثانية

---

## 📝 الترخيص

MIT — استخدمه تجارياً أو أكاديمياً، بدون قيود.

---

## 🤝 المساهمة

افتح Issue أو Pull Request على GitHub.

---

**صُنع بـ ❤️ بالعربية الفصحى**
