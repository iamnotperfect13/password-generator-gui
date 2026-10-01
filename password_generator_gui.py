"""
Генератор паролей — GUI версия (Tkinter)

Нажимаешь кнопку "Сгенерировать" — получаешь пароль.
Не понравился — жмёшь ещё раз, получаешь следующий.
Цвет текста показывает силу пароля: красный / жёлтый / зелёный.
Есть переключатель светлой/тёмной темы.
"""

import secrets
import string
import tkinter as tk
from tkinter import ttk


# --- Логика генерации --------------------------------------------------------

CATEGORIES = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.<>?",
}


def build_charset(use_lower, use_upper, use_digits, use_symbols):
    active = []
    if use_lower:
        active.append(CATEGORIES["lower"])
    if use_upper:
        active.append(CATEGORIES["upper"])
    if use_digits:
        active.append(CATEGORIES["digits"])
    if use_symbols:
        active.append(CATEGORIES["symbols"])
    if not active:
        raise ValueError("Нужно выбрать хотя бы одну категорию символов")
    return active


def generate_password(length, active_categories):
    if length < len(active_categories):
        raise ValueError("Длина пароля меньше количества категорий")

    password_chars = [secrets.choice(cat) for cat in active_categories]
    full_pool = "".join(active_categories)
    remaining = length - len(password_chars)
    password_chars += [secrets.choice(full_pool) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def estimate_strength(length, active_categories):
    pool_size = sum(len(cat) for cat in active_categories)
    entropy_bits = length * (pool_size.bit_length() - 1)

    if entropy_bits < 40:
        return "слабый", "#e74c3c"
    elif entropy_bits < 70:
        return "средний", "#f39c12"
    else:
        return "сильный", "#2ecc71"


# --- Темы ---------------------------------------------------------------------

THEMES = {
    "light": {
        "bg": "#f4f4f6",
        "fg": "#1a1a1a",
        "field_bg": "#ffffff",
        "accent": "#3b82f6",
        "accent_fg": "#ffffff",
        "muted": "#6b6b6b",
    },
    "dark": {
        "bg": "#1e1f26",
        "fg": "#e8e8ea",
        "field_bg": "#2a2b35",
        "accent": "#3b82f6",
        "accent_fg": "#ffffff",
        "muted": "#9a9aa5",
    },
}


# --- GUI ------------------------------------------------------------------

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.theme_name = "dark"

        root.title("Генератор паролей")
        root.geometry("460x520")
        root.minsize(420, 480)

        self.style = ttk.Style(root)
        self.style.theme_use("clam")

        padding = {"padx": 18, "pady": 8}

        # --- Шапка: заголовок + переключатель темы ---
        header = ttk.Frame(root)
        header.pack(fill="x", padx=18, pady=(16, 4))
        ttk.Label(header, text="Генератор паролей", font=("Segoe UI", 15, "bold")).pack(side="left")
        self.theme_btn = ttk.Button(header, text="☀ / 🌙", width=8, command=self.toggle_theme)
        self.theme_btn.pack(side="right")

        # --- Длина пароля ---
        length_frame = ttk.Frame(root)
        length_frame.pack(fill="x", **padding)
        ttk.Label(length_frame, text="Длина пароля:", font=("Segoe UI", 11)).pack(side="left")
        self.length_var = tk.IntVar(value=12)
        self.length_spin = ttk.Spinbox(
            length_frame, from_=4, to=64, width=6, textvariable=self.length_var,
            font=("Segoe UI", 11)
        )
        self.length_spin.pack(side="left", padx=10)

        # --- Категории символов ---
        options_frame = ttk.LabelFrame(root, text="Категории символов")
        options_frame.pack(fill="x", padx=18, pady=10)

        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        for text, var in [
            ("Строчные (a-z)", self.use_lower),
            ("Заглавные (A-Z)", self.use_upper),
            ("Цифры (0-9)", self.use_digits),
            ("Спецсимволы (!@#...)", self.use_symbols),
        ]:
            ttk.Checkbutton(options_frame, text=text, variable=var).pack(anchor="w", padx=10, pady=4)

        # --- Кнопка генерации ---
        self.generate_btn = ttk.Button(
            root, text="Сгенерировать", command=self.on_generate, style="Accent.TButton"
        )
        self.generate_btn.pack(fill="x", padx=18, pady=(10, 6), ipady=6)

        # --- Результат ---
        self.result_frame = tk.Frame(root)
        self.result_frame.pack(fill="x", padx=18, pady=10)

        self.password_var = tk.StringVar(value="")
        self.password_label = tk.Label(
            self.result_frame,
            textvariable=self.password_var,
            font=("Consolas", 18, "bold"),
            wraplength=400,
        )
        self.password_label.pack(pady=(6, 2))

        self.strength_var = tk.StringVar(value="")
        self.strength_label = tk.Label(
            self.result_frame,
            textvariable=self.strength_var,
            font=("Segoe UI", 10),
        )
        self.strength_label.pack(pady=(0, 6))

        # --- Копировать ---
        self.copy_btn = ttk.Button(root, text="Скопировать", command=self.on_copy)
        self.copy_btn.pack(fill="x", padx=18, pady=(0, 4), ipady=4)

        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 10))

        self.apply_theme()
        self.on_generate()

    # --- Темизация ---

    def apply_theme(self):
        t = THEMES[self.theme_name]

        self.root.configure(bg=t["bg"])

        self.style.configure("TFrame", background=t["bg"])
        self.style.configure("TLabelframe", background=t["bg"], foreground=t["fg"])
        self.style.configure("TLabelframe.Label", background=t["bg"], foreground=t["fg"],
                              font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabel", background=t["bg"], foreground=t["fg"])
        self.style.configure("TCheckbutton", background=t["bg"], foreground=t["fg"],
                              font=("Segoe UI", 10))
        self.style.map("TCheckbutton", background=[("active", t["bg"])])
        self.style.configure("TButton", background=t["field_bg"], foreground=t["fg"],
                              font=("Segoe UI", 10), borderwidth=0)
        self.style.map("TButton", background=[("active", t["muted"])])
        self.style.configure("Accent.TButton", background=t["accent"], foreground=t["accent_fg"],
                              font=("Segoe UI", 11, "bold"), borderwidth=0)
        self.style.map("Accent.TButton", background=[("active", t["accent"])])
        self.style.configure("TSpinbox", fieldbackground=t["field_bg"], foreground=t["fg"],
                              background=t["field_bg"])

        self.result_frame.configure(bg=t["bg"])
        self.password_label.configure(bg=t["bg"])
        self.strength_label.configure(bg=t["bg"])
        self.status_label.configure(bg=t["bg"], fg=t["muted"])

        # Текущий цвет силы пароля не трогаем — он задаётся отдельно
        if not self.password_var.get() or self.password_var.get() == "—":
            self.password_label.configure(fg=t["fg"])

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.apply_theme()
        # перекрасить текущий пароль/статус заново под новую тему, если нужно
        self.on_generate(keep_settings=True)

    # --- Логика ---

    def get_active_categories(self):
        return build_charset(
            self.use_lower.get(),
            self.use_upper.get(),
            self.use_digits.get(),
            self.use_symbols.get(),
        )

    def on_generate(self, keep_settings=False):
        t = THEMES[self.theme_name]
        try:
            active = self.get_active_categories()
            length = self.length_var.get()

            if keep_settings and self.password_var.get() and self.password_var.get() != "—":
                password = self.password_var.get()
            else:
                password = generate_password(length, active)

            strength_text, color = estimate_strength(length, active)

            self.password_var.set(password)
            self.password_label.configure(fg=color)
            self.strength_var.set(f"Сила пароля: {strength_text}")
            self.strength_label.configure(fg=color)
            self.status_var.set("")
        except ValueError as e:
            self.password_var.set("—")
            self.strength_var.set(str(e))
            self.strength_label.configure(fg=t["fg"])

    def on_copy(self):
        password = self.password_var.get()
        if password and password != "—":
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.status_var.set("Скопировано!")
            self.root.after(1500, lambda: self.status_var.set(""))


def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
