import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import itertools
import random
import string
from datetime import datetime

# --- إعدادات عامة --- #
SYMBOLS = ['!', '@', '#', '$', '%', '&', '*']
REPLACEMENTS = {'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['$', '5']}

# --- توليد الذكاء في الكلمات --- #
def smart_variants(word, use_replacements=True):
    variants = set()
    word = word.lower()
    variants.add(word)
    variants.add(word.capitalize())
    variants.add(word.upper())

    if use_replacements:
        for i in range(len(word)):
            if word[i] in REPLACEMENTS:
                for rep in REPLACEMENTS[word[i]]:
                    variants.add(word[:i] + rep + word[i+1:])
    return list(variants)

# --- كلمات من البيانات --- #
def generate_wordlist(inputs, min_len, max_len, use_symbols, use_replacements, patterns=[]):
    base_words = []
    for word in inputs:
        base_words.extend(smart_variants(word, use_replacements))

    wordlist = set()

    for pattern in patterns:
        for combo in itertools.permutations(base_words, pattern.count('{}')):
            pattern_word = pattern.format(*combo)
            if min_len <= len(pattern_word) <= max_len:
                wordlist.add(pattern_word)

    for r in range(1, 3):
        for combo in itertools.permutations(base_words, r):
            combined = ''.join(combo)
            if min_len <= len(combined) <= max_len:
                wordlist.add(combined)
                if use_symbols:
                    for sym in SYMBOLS:
                        wordlist.add(combined + sym)
                        wordlist.add(sym + combined)
    return sorted(wordlist)

# --- توليد عشوائي --- #
def generate_random_words(count, min_len, max_len, use_upper, use_digits, use_symbols, prefix='', suffix='', custom_digits='', custom_symbols=''):
    pool = string.ascii_lowercase
    if use_upper:
        pool += string.ascii_uppercase
    if use_digits:
        pool += custom_digits if custom_digits else string.digits
    if use_symbols:
        pool += custom_symbols if custom_symbols else ''.join(SYMBOLS)

    random_words = set()
    for _ in range(count * 3):
        core_length = random.randint(
            max(1, min_len - len(prefix) - len(suffix)),
            max_len - len(prefix) - len(suffix)
        )
        word = ''.join(random.choice(pool) for _ in range(core_length))
        final_word = prefix + word + suffix
        if min_len <= len(final_word) <= max_len:
            random_words.add(final_word)
        if len(random_words) >= count:
            break
    return list(random_words)

# --- حفظ --- #
def save_to_file(wordlist):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = filedialog.asksaveasfilename(defaultextension=".txt",
        initialfile=f"wordlist_{now}.txt",
        filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, "w", encoding="utf-8") as f:
            for word in wordlist:
                f.write(word + "\n")
        messagebox.showinfo("تم الحفظ", f"تم حفظ القائمة في:\n{path}")

# --- عرض --- #
def preview_words(wordlist):
    top = tk.Toplevel(root)
    top.title("معاينة كلمات المرور")
    text = tk.Text(top, width=60, height=30)
    text.pack()
    for word in wordlist:
        text.insert(tk.END, word + "\n")

# --- توليد --- #
def start_generation():
    inputs = []
    for entry in [entry_first, entry_last, entry_year, entry_city]:
        val = entry.get().strip()
        if val:
            inputs.append(val)
    extras = entry_extra.get("1.0", tk.END).strip().split()
    inputs.extend(extras)

    try:
        min_len = int(entry_min.get())
        max_len = int(entry_max.get())
        rand_count = int(entry_rand_count.get())
    except ValueError:
        messagebox.showerror("خطأ", "أدخل أرقام صحيحة للطول أو العشوائي.")
        return

    use_symbols = var_symbols.get()
    use_replacements = var_replace.get()
    use_rand = var_rand.get()

    rand_prefix = entry_prefix.get().strip()
    rand_suffix = entry_suffix.get().strip()
    rand_digits = entry_digits.get().strip()
    rand_custom_symbols = entry_symbols.get().strip()

    wordlist = []

    if inputs:
        wordlist.extend(generate_wordlist(
            inputs, min_len, max_len,
            use_symbols, use_replacements,
            patterns=["{}{}", "{}{}{}", "{}_{}"]
        ))

    if use_rand:
        rand_words = generate_random_words(
            rand_count, min_len, max_len,
            var_rand_upper.get(),
            var_rand_digits.get(),
            var_rand_symbols.get(),
            prefix=rand_prefix,
            suffix=rand_suffix,
            custom_digits=rand_digits,
            custom_symbols=rand_custom_symbols
        )
        wordlist.extend(rand_words)

    wordlist = sorted(set(wordlist))
    lbl_count.config(text=f"✅ الناتج: {len(wordlist)} كلمة")

    if var_preview.get():
        preview_words(wordlist)
    else:
        save_to_file(wordlist)

# ---------------- واجهة البرنامج ---------------- #
root = tk.Tk()
root.title("🔥 صانع Wordlist احترافي 🔥")
root.geometry("750x750")

frame_inputs = tk.LabelFrame(root, text="🔹 بيانات الضحية:")
frame_inputs.pack(padx=10, pady=10, fill="x")

labels = ["الاسم الأول:", "الاسم الأخير:", "سنة الميلاد:", "المدينة:"]
entries = []
for i, label_text in enumerate(labels):
    tk.Label(frame_inputs, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="e")
    entry = tk.Entry(frame_inputs, width=20)
    entry.grid(row=i//2, column=(i%2)*2+1)
    entries.append(entry)

entry_first, entry_last, entry_year, entry_city = entries

tk.Label(frame_inputs, text="كلمات إضافية:").grid(row=2, column=0, sticky="ne")
entry_extra = tk.Text(frame_inputs, width=40, height=3)
entry_extra.grid(row=2, column=1, columnspan=3)

frame_opts = tk.LabelFrame(root, text="⚙️ الإعدادات:")
frame_opts.pack(padx=10, pady=10, fill="x")

tk.Label(frame_opts, text="الحد الأدنى للطول:").grid(row=0, column=0)
entry_min = tk.Entry(frame_opts, width=5)
entry_min.insert(0, "6")
entry_min.grid(row=0, column=1)

tk.Label(frame_opts, text="الحد الأقصى للطول:").grid(row=0, column=2)
entry_max = tk.Entry(frame_opts, width=5)
entry_max.insert(0, "16")
entry_max.grid(row=0, column=3)

var_symbols = tk.BooleanVar(value=True)
tk.Checkbutton(frame_opts, text="إضافة رموز", variable=var_symbols).grid(row=1, column=0)

var_replace = tk.BooleanVar(value=True)
tk.Checkbutton(frame_opts, text="استبدال أحرف (a→@)", variable=var_replace).grid(row=1, column=1)

var_preview = tk.BooleanVar(value=False)
tk.Checkbutton(frame_opts, text="معاينة قبل الحفظ", variable=var_preview).grid(row=1, column=2)

frame_rand = tk.LabelFrame(root, text="🌀 توليد كلمات عشوائية:")
frame_rand.pack(padx=10, pady=10, fill="x")

var_rand = tk.BooleanVar()
tk.Checkbutton(frame_rand, text="تفعيل التوليد العشوائي", variable=var_rand).grid(row=0, column=0, sticky="w")

tk.Label(frame_rand, text="عدد الكلمات:").grid(row=1, column=0)
entry_rand_count = tk.Entry(frame_rand, width=5)
entry_rand_count.insert(0, "50")
entry_rand_count.grid(row=1, column=1)

var_rand_upper = tk.BooleanVar(value=True)
tk.Checkbutton(frame_rand, text="أحرف كبيرة", variable=var_rand_upper).grid(row=1, column=2)

var_rand_digits = tk.BooleanVar(value=True)
tk.Checkbutton(frame_rand, text="أرقام", variable=var_rand_digits).grid(row=1, column=3)

var_rand_symbols = tk.BooleanVar(value=True)
tk.Checkbutton(frame_rand, text="رموز", variable=var_rand_symbols).grid(row=1, column=4)

# إعدادات إضافية للعشوائي
frame_advanced = tk.Frame(frame_rand)
frame_advanced.grid(row=2, column=0, columnspan=5, pady=10)

labels = ["أول حروف:", "آخر حروف:", "الأرقام المستخدمة:", "الرموز المستخدمة:"]
entries = []
for i, txt in enumerate(labels):
    tk.Label(frame_advanced, text=txt).grid(row=i, column=0, sticky="e")
    entry = tk.Entry(frame_advanced, width=30)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

entry_prefix, entry_suffix, entry_digits, entry_symbols = entries

tk.Button(root, text="🚀 توليد Wordlist وحفظ", command=start_generation, bg="darkblue", fg="white", font=("Arial", 14)).pack(pady=20)

lbl_count = tk.Label(root, text="✅ الناتج: 0 كلمة", font=("Arial", 12))
lbl_count.pack()


root.mainloop()