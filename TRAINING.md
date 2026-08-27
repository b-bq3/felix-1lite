# 🚀 تدريب FELIX-1lite

دليل خطوة بخطوة لتدريب النموذج على Google Colab أو جهازك المحلي.

---

## � تجربة سريعة بدون تدريب (5 دقائق)

**الخيار 1: جرّب الكود مباشرة في المتصفح**

روح [huggingface.co/b-bq3/felix-1lite](https://huggingface.co/b-bq3/felix-1lite) → صفحة الـ Model.

**الخيار 2: شوف العرض الحي**

[https://huggingface.co/spaces/b-bq3/felix-1lite-demo](https://huggingface.co/spaces/b-bq3/felix-1lite-demo) — صفحة landing مع عينة محادثة.

---

## 📋 التدريب على Google Colab (الأسهل)

### الخطوة 1: افتح Colab
[https://colab.research.google.com](https://colab.research.google.com)

### الخطوة 2: فعّل GPU
- القائمة: **Runtime → Change runtime type**
- Hardware accelerator: **T4 GPU**
- اضغط Save

### الخطوة 3: انسخ والصق الخلية الأولى (تثبيت + تحميل البيانات)

```python
!git clone https://github.com/b-bq3/felix-1lite.git
%cd felix-1lite
!pip install torch --quiet
```

### الخطوة 4: الخلية الثانية (توليد البيانات)

```python
!python generate_data.py
```

يولد `felix_data.txt` (~200K حرف عربي).

### الخطوة 5: الخلية الثالثة (التدريب)

```python
!python felix.py
```

**الوقت المتوقع على T4:** 30-45 دقيقة
**الناتج:** ملف `felix-1lite.pt` (~100 MB)

### الخطوة 6: الخلية الرابعة (المحادثة)

```python
from felix import chat
print(chat("ما هو الذكاء الاصطناعي؟"))
print("---")
print(chat("اعطني فكرة مشروع برمجي"))
print("---")
print(chat("اكتب كود reverse string"))
```

---

## 🔧 التدريب على جهازك المحلي

### المتطلبات
- Python 3.10+
- PyTorch 2.0+
- GPU بـ 4GB+ VRAM (NVIDIA موصى به)
- أو CPU فقط (سيكون بطيء)

### الأوامر

```bash
git clone https://github.com/b-bq3/felix-1lite.git
cd felix-1lite
pip install -r requirements.txt
python generate_data.py
python felix.py
```

---

## 🎛️ تخصيص التدريب

عدّل `felix.py` — قسم `CONFIG`:

```python
CONFIG = {
    "block_size": 256,      # نافذة السياق (512 للمحادثات الطويلة)
    "n_layer": 6,           # عدد الطبقات (12 لنموذج أقوى)
    "n_head": 8,            # رؤوس الانتباه
    "n_embd": 384,          # بعد التضمين (768 لنموذج أكبر)
    "batch_size": 32,       # حجم الدفعة (16 إذا VRAM قليل)
    "learning_rate": 3e-4,  # معدل التعلم
    "max_iters": 3000,      # عدد خطوات التدريب (1000 سريع، 10000 أفضل)
}
```

### نصائح:
- **نموذج أسرع:** `n_layer=4`, `n_embd=256`, `max_iters=1000` (~5 دقائق)
- **نموذج أقوى:** `n_layer=8`, `n_embd=512`, `max_iters=5000` (~ساعتين)
- **سياق أطول:** `block_size=512` (يحتاج VRAM أكثر)

---

## � إضافة بياناتك الخاصة (Fine-tuning)

### الخطوة 1: جهّز بياناتك

أنشئ ملف `my_conversations.txt` بصيغة:

```
<USER> سؤالي الأول <SEP> <FELIX> إجابتي المقترحة
<USER> سؤالي الثاني <SEP> <FELIX> إجابتي المقترحة
```

كل سطر = محادثة واحدة.

### الخطوة 2: ادرب

```python
from felix import train
train(
    data_path="my_conversations.txt",
    checkpoint_path="felix-personal.pt",
)
```

### الخطوة 3: استخدم

```python
from felix import chat
print(chat("مرحبا", checkpoint="felix-personal.pt"))
```

---

## 🌐 نشر النموذج بعد التدريب

### Modal Labs (الأفضل، مجاني)
```bash
pip install modal
modal token new
modal deploy modal_app.py
```

### Render.com (مجاني)
- ارفع الكود على GitHub
- أنشئ Web Service جديد
- اختر Python environment
- Start command: `python app_clean.py`

### HuggingFace Pro ($9/شهر)
- ترقية لـ Pro
- أنشئ Space جديد بـ Gradio SDK
- ارفع felix.py + app.py + felix-1lite.pt

---

## 🆘 حل المشاكل

### خطأ: `OutOfMemoryError`
```python
# في felix.py غيّر:
"batch_size": 16,    # بدل 32
"block_size": 128,   # بدل 256
```

### خطأ: `CUDA not available`
```python
# غيّر الجهاز لـ CPU:
CONFIG["device"] = "cpu"
```
ملاحظة: التدريب على CPU بطيء جداً (~10x أبطأ).

### النموذج يولّد كلاماً غير مفهوم
- زِد `max_iters` (5000-10000)
- أضف بيانات أكثر في `generate_data.py`
- قلل `temperature` إلى 0.5 في `chat()`

---

## 📞 المساعدة

- افتح Issue على GitHub
- أو تواصل عبر HuggingFace

---

**بالتوفيق! 🚀**
