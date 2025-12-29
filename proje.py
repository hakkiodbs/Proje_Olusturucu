import os
import re
import json
import subprocess
import shutil
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, colorchooser

# --- RENK PALETİ ---
COLOR_BG_MAIN = "#1e1e1e"
COLOR_BG_HEADER = "#2d2d2d"
COLOR_INPUT_BG = "#252526"
COLOR_TEXT_FG = "#d4d4d4"
COLOR_PLACEHOLDER = "#6e6e6e" # Silik yazı rengi

COLOR_BTN_BG = "#007acc"
COLOR_BTN_HOVER = "#0062a3"
COLOR_CLOSE_BG = "#c42b1c"

COLOR_LOG_SUCCESS = "#4EC9B0"
COLOR_LOG_EXIST = "#F44747"
COLOR_LOG_INFO = "#569cd6"

COLOR_FOLDER_TAG = "#569cd6"
COLOR_FILE_TAG = "#ce9178"

COLOR_ICON_ACTIVE = "#ffffff"
COLOR_ICON_INACTIVE = "#666666"

COLOR_SCROLL_TROUGH = "#1e1e1e"
COLOR_SCROLL_THUMB = "#424242"
COLOR_SCROLL_HOVER = "#6e6e6e"
COLOR_SCROLL_ARROW = "#1e1e1e"

FONT_MAIN = ("Segoe UI", 9)
FONT_HEADER = ("Segoe UI", 10, "bold")
FONT_CODE = ("Consolas", 11)
FONT_ICON = ("Segoe UI Symbol", 14)

PRESETS_FILE = "user_presets_v5.json"
CONFIG_FILE = "app_config.json"

# --- İKONLAR ---
FILE_ICONS = {
    ".py": "🐍", ".html": "🌐", ".css": "🎨", ".js": "📜",
    ".json": "⚙️", ".txt": "📝", ".md": "📝",
    ".png": "🖼️", ".jpg": "🖼️", ".exe": "🚀"
}
DEFAULT_FILE_ICON = "📄"
DEFAULT_FOLDER_ICON = "📁"

# --- HAYALET YAZI (PLACEHOLDER) ---
PLACEHOLDER_TEXT = """Buraya proje yapısını yazın veya yapıştırın...

Örnek Kullanım:
AnaKlasor
    AltKlasor
        dosya.txt

Nasıl Kullanılır?
1. Kategori ve Şablon seçerek başlayabilirsiniz.
2. Kendiniz yazacaksanız; Alt klasör için TAB tuşunu kullanın.
3. Yazdıktan sonra '🔨 Yapılandır' butonu ile görselleştirin.
4. '🚀 PROJEYİ OLUŞTUR' butonu ile dosyaları yaratın."""

# --- KATEGORİLİ ŞABLONLAR ---
DEFAULT_PRESETS = {
    "Web Projeleri": {
        "Flask App": """📁 Flask-App
│   ├── app.py
│   ├── requirements.txt
│   ├── static
│   │   ├── css
│   │   └── js
│   └── templates
│       ├── index.html
│       └── base.html""",
        "Django Basic": """📁 Django-Project
│   ├── manage.py
│   ├── requirements.txt
│   └── project_name
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py"""
    },
    "Masaüstü Projeleri": {
        "Python GUI": """📁 Tkinter-App
│   ├── main.py
│   ├── gui.py
│   └── assets""",
        "Console Tool": """📁 Console-Tool
│   ├── main.py
│   ├── utils.py
│   └── README.md"""
    },
    "Veri Bilimi": {
        "Data Analysis": """📁 Data-Science
│   ├── data
│   ├── notebooks
│   └── src""",
        "ML Project": """📁 ML-Project
│   ├── models
│   ├── src
│   └── config.yaml"""
    },
    "Mobil Projeler": {
        "Kivy App": """📁 Kivy-App
│   ├── main.py
│   ├── main.kv
│   └── assets"""
    }
}

DOCKER_TEMPLATES = {
    "Dockerfile": """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]""",
    "docker-compose.yml": """version: '3.8'
services:
  app:
    build: .
    volumes:
      - .:/app
    restart: always"""
}

TEMPLATES = {
    "main.py": "print('Proje Başlatıldı!')",
    "app.py": "from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home(): return 'Hello'\nif __name__=='__main__': app.run()",
    "README.md": "# Proje Dokümantasyonu"
}

class SavePresetDialog(tk.Toplevel):
    def __init__(self, parent, categories):
        super().__init__(parent)
        self.title("Şablon Kaydet")
        self.geometry("350x220")
        self.configure(bg=COLOR_BG_MAIN)
        self.result = None
        
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 175
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text="Şablon Adı:", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG).pack(pady=(15, 2))
        self.name_entry = tk.Entry(self, bg=COLOR_INPUT_BG, fg=COLOR_TEXT_FG, font=FONT_MAIN)
        self.name_entry.pack(pady=5, padx=20, fill=tk.X)
        self.name_entry.focus_set()

        tk.Label(self, text="Kategori (Seç veya Yeni Yaz):", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG).pack(pady=(10, 2))
        
        self.cat_combo = ttk.Combobox(self, values=list(categories), state="normal") 
        self.cat_combo.set("Masaüstü Projeleri")
        self.cat_combo.pack(pady=5, padx=20, fill=tk.X)

        btn_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        btn_frame.pack(side=tk.BOTTOM, pady=20)
        
        tk.Button(btn_frame, text="Kaydet", command=self.on_save, bg=COLOR_LOG_SUCCESS, fg="white", bd=0, padx=15, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="İptal", command=self.destroy, bg=COLOR_CLOSE_BG, fg="white", bd=0, padx=15, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def on_save(self):
        name = self.name_entry.get().strip()
        cat = self.cat_combo.get().strip()
        if name and cat:
            self.result = (cat, name)
            self.destroy()
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir isim ve kategori girin.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(bg=COLOR_BG_MAIN)
        
        self.is_maximized = False
        self.pre_max_geometry = "1200x800+100+100"
        self._offsetx = 0; self._offsety = 0
        self.accent_color = "#007acc"
        self.is_placeholder_active = False 

        self.all_presets = DEFAULT_PRESETS.copy()
        self.load_custom_presets_from_file()
        self.load_app_config() 
        
        # Panellerin durumunu takip etmek için değişkenler
        self.show_editor = True
        self.show_explorer = True
        self.show_logs = True
        self.show_top_pane = True

        self.setup_styles()
        self.setup_ui()
        self.bind("<Map>", self.on_restore)
        
        target = self.path_entry.get() if self.path_entry.get() else os.getcwd()
        self.refresh_file_viewer(target)
        
        # BAŞLANGIÇTA OTOMATİK ŞABLON YÜKLEMİYORUZ
        # Sadece placeholder gösteriyoruz.
        self.add_placeholder()

    # --- PLACEHOLDER (HAYALET YAZI) MANTIĞI ---
    def add_placeholder(self):
        # Eğer içerik doluysa placeholder ekleme
        if self.text_area.get("1.0", "end-1c").strip(): return
        
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", PLACEHOLDER_TEXT)
        self.text_area.config(fg=COLOR_PLACEHOLDER)
        self.is_placeholder_active = True

    def remove_placeholder(self, event=None):
        if self.is_placeholder_active:
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(fg=COLOR_TEXT_FG)
            self.is_placeholder_active = False

    def on_focus_out(self, event):
        if not self.text_area.get("1.0", "end-1c").strip():
            self.add_placeholder()

    # --- FORMATLAMA & EDİTÖR ---
    def format_structure_visuals(self):
        if self.is_placeholder_active: return

        raw_text = self.text_area.get("1.0", tk.END)
        lines = [l for l in raw_text.split('\n') if l.strip()]
        formatted = []
        for line in lines:
            clean = re.sub(r'[│├└─\t]+', '', line).strip()
            clean = re.sub(r'[📁📂📄🐍🌐🎨📜⚙️📝🖼️🚀🐙🔒🗄️]', '', clean).strip()
            if not clean: continue
            
            orig_indent = len(re.match(r'^(\s*)', line).group(1))
            level = orig_indent // 4
            prefix = ("│   " * (level - 1) + "├── ") if level > 0 else ""
            
            is_file = "." in clean
            icon = FILE_ICONS.get(os.path.splitext(clean)[1].lower(), DEFAULT_FILE_ICON) if is_file else DEFAULT_FOLDER_ICON
            formatted.append(f"{prefix}{icon} {clean}")
            
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(formatted))
        self.highlight_syntax()

    def handle_tab(self, e): 
        if self.is_placeholder_active: self.remove_placeholder(None)
        self.text_area.insert("insert", "    ")
        return "break"
    
    def handle_enter(self, e):
        if self.is_placeholder_active: self.remove_placeholder(None)
        cur = self.text_area.get("insert linestart", "insert lineend")
        ind = re.match(r"^(\s*)", cur)
        self.text_area.insert("insert", "\n" + (ind.group(1) if ind else ""))
        self.text_area.see("insert")
        return "break"

    # --- OLUŞTURMA MOTORU ---
    def generate_structure(self):
        if self.is_placeholder_active: return self.log_write("Yapı boş, lütfen proje yapısını girin!", "error")

        tree_text = self.text_area.get("1.0", tk.END).strip()
        base_path = self.path_entry.get()
        if not tree_text: return self.log_write("Yapı boş!", "error")
        
        self.clear_logs() 
        self.log_write("İşlem Başladı...", "info")
        
        lines = tree_text.split('\n')
        path_stack = []
        created_count = 0

        try:
            for line in lines:
                if not line.strip(): continue
                clean_line = line.replace('│', ' ').replace('├', ' ').replace('└', ' ').replace('─', ' ')
                level = len(re.match(r'^(\s*)', clean_line).group(1)) // 4
                name = re.sub(r'[│├└─\s\t]+', '', line).strip()
                name = re.sub(r'[📁📂📄🐍🌐🎨📜⚙️📝🖼️🚀🐙🔒🗄️]', '', name).strip()
                if not name: continue

                while path_stack and path_stack[-1][0] >= level: path_stack.pop()
                parent = path_stack[-1][1] if path_stack else base_path
                full_path = os.path.join(parent, name)
                
                if os.path.exists(full_path):
                    self.log_write(f"[MEVCUT] {name}", "error")
                    if not ("." in name): 
                        path_stack.append((level, full_path))
                else:
                    if "." in name:
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        content = TEMPLATES.get(name, TEMPLATES.get(os.path.splitext(name)[1], ""))
                        content = content.replace("{PROJECT_NAME}", os.path.basename(base_path))
                        content = content.replace("{DATE}", datetime.datetime.now().strftime("%d.%m.%Y"))
                        with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
                        self.log_write(f"[DOSYA] {name}", "success")
                    else:
                        os.makedirs(full_path, exist_ok=True)
                        path_stack.append((level, full_path))
                        self.log_write(f"[KLASÖR] {name}", "success")
                    created_count += 1
            
            if self.var_git.get(): 
                subprocess.run(["git", "init"], cwd=base_path, shell=True)
                self.log_write("Git başlatıldı.", "info")

            if self.var_docker.get():
                for f, c in DOCKER_TEMPLATES.items():
                    with open(os.path.join(base_path, f), "w", encoding="utf-8") as df: 
                        df.write(c)
                self.log_write("Docker dosyaları eklendi.", "info")
            
            self.refresh_file_viewer(base_path)
            self.log_write(f"Tamamlandı! {created_count} yeni öge.", "success")
        except Exception as e: self.log_write(f"Hata: {e}", "error")

    # --- UI & LOGIC ---
    def log_write(self, msg, tag="info"):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f">> {msg}\n", tag)
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def clear_logs(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

    def highlight_syntax(self, e=None):
        self.text_area.tag_remove("folder", "1.0", tk.END)
        self.text_area.tag_remove("file", "1.0", tk.END)
        for i, line in enumerate(self.text_area.get("1.0", tk.END).split("\n")):
            if any(x in line for x in "📁📂"): 
                self.text_area.tag_add("folder", f"{i+1}.0", f"{i+1}.end")
            elif "." in line: 
                self.text_area.tag_add("file", f"{i+1}.0", f"{i+1}.end")
        self.text_area.tag_config("folder", foreground=COLOR_FOLDER_TAG, font=("Consolas", 11, "bold"))
        self.text_area.tag_config("file", foreground=COLOR_FILE_TAG)

    def on_category_change(self, event):
        selected_cat = self.cat_var.get()
        if selected_cat in self.all_presets:
            templates = list(self.all_presets[selected_cat].keys())
            self.preset_combo['values'] = templates
            if templates:
                self.preset_combo.set(templates[0])
                self.load_preset(None)
            else:
                self.preset_combo.set("Şablon Yok")
                if hasattr(self, 'text_area'):
                    self.text_area.delete("1.0", tk.END)
                    self.add_placeholder()

    def load_preset(self, event):
        cat = self.cat_var.get()
        name = self.preset_var.get()
        if not hasattr(self, 'text_area'): return
        
        if cat in self.all_presets and name in self.all_presets[cat]:
            self.remove_placeholder(None) # Şablon yüklenirken placeholder silinir
            content = self.all_presets[cat][name]
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.highlight_syntax()

    def load_custom_presets_from_file(self):
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    custom_data = json.load(f)
                    for cat, templates in custom_data.items():
                        if cat not in self.all_presets:
                            self.all_presets[cat] = {}
                        self.all_presets[cat].update(templates)
            except: pass

    def save_current_as_preset(self):
        if self.is_placeholder_active: return messagebox.showwarning("Uyarı", "Editör boş, lütfen içerik girin!")

        content = self.text_area.get("1.0", tk.END).strip()
        if not content: return messagebox.showwarning("Uyarı", "Editör boş!")
        
        dialog = SavePresetDialog(self, self.all_presets.keys())
        self.wait_window(dialog)
        
        if dialog.result:
            cat, name = dialog.result
            if cat not in self.all_presets: self.all_presets[cat] = {}
            self.all_presets[cat][name] = content
            
            custom_data = {}
            if os.path.exists(PRESETS_FILE):
                try: 
                    with open(PRESETS_FILE, "r", encoding="utf-8") as f: 
                        custom_data = json.load(f)
                except: pass
            
            if cat not in custom_data: custom_data[cat] = {}
            custom_data[cat][name] = content
            
            try:
                with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                    json.dump(custom_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("Hata", str(e))
                return
            
            self.cat_combo['values'] = list(self.all_presets.keys())
            self.cat_combo.set(cat)
            self.on_category_change(None)
            self.preset_combo.set(name)
            self.log_write(f"Şablon kaydedildi: {cat} / {name}", "success")

    def load_app_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: 
                    config = json.load(f)
                self.geometry(config.get("geometry", "1200x800"))
                self.accent_color = config.get("accent_color", "#007acc")
            except: pass
    
    def save_app_config(self):
        config = {
            "geometry": self.geometry(), 
            "accent_color": self.accent_color,
            "last_path": self.path_entry.get()
        }
        try: 
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: 
                json.dump(config, f, indent=4)
        except: pass

    # --- IMPORT ---
    def import_structure_from_folder(self):
        target_dir = filedialog.askdirectory()
        if not target_dir: return
        root_name = os.path.basename(target_dir)
        structure_lines = [f"📁 {root_name}"]
        ignored = {'.git', '__pycache__', 'venv', 'node_modules'}
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in ignored and not d.startswith('.')]
            files = [f for f in files if f not in ignored and not f.startswith('.')]
            level = root.replace(target_dir, '').count(os.sep)
            indent = '    ' * (level + 1)
            if root != target_dir: structure_lines.append(f"{'    ' * level}📁 {os.path.basename(root)}")
            for f in files: structure_lines.append(f"{indent}📄 {f}")
        
        self.remove_placeholder(None)
        self.text_area.delete("1.0", tk.END); self.text_area.insert("1.0", "\n".join(structure_lines))
        self.highlight_syntax(); self.log_write(f"İçe aktarıldı: {root_name}", "success")

    def clear_editor(self): 
        self.text_area.delete("1.0", tk.END)
        self.add_placeholder()
    
    def pick_accent_color(self):
        c = colorchooser.askcolor(color=self.accent_color)[1]
        if c:
            self.accent_color = c; self.save_app_config()
            self.btn_create.config(bg=c)
            if hasattr(self, 'btn_format'):
                self.btn_format.config(fg=c)
            ttk.Style().map("Treeview", background=[('selected', c)])

    # --- UI KURULUMU ---
    def setup_styles(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("Treeview", background=COLOR_INPUT_BG, foreground=COLOR_TEXT_FG, fieldbackground=COLOR_INPUT_BG, borderwidth=0, font=FONT_MAIN)
        s.configure("Treeview.Heading", background=COLOR_BG_HEADER, foreground="white", borderwidth=0, font=FONT_HEADER)
        s.map("Treeview", background=[('selected', self.accent_color)])
        s.configure("TCheckbutton", background=COLOR_BG_MAIN, foreground=COLOR_TEXT_FG, font=FONT_MAIN)
        s.configure("Vertical.TScrollbar", gripcount=0, background=COLOR_SCROLL_THUMB, darkcolor=COLOR_SCROLL_TROUGH, lightcolor=COLOR_SCROLL_TROUGH, troughcolor=COLOR_SCROLL_TROUGH, bordercolor=COLOR_SCROLL_TROUGH, arrowcolor=COLOR_SCROLL_ARROW)

    def setup_ui(self):
        self.title_bar = tk.Frame(self, bg=COLOR_BG_HEADER, height=30)
        self.title_bar.pack(side=tk.TOP, fill=tk.X)
        self.title_bar.bind("<Button-1>", self.click_window)
        self.title_bar.bind("<B1-Motion>", self.drag_window)
        
        tk.Label(self.title_bar, text="Proje Oluşturucu v6.1 (Final Stable)", bg=COLOR_BG_HEADER, fg="white", font=FONT_HEADER).pack(side=tk.LEFT, padx=15)
        self.create_win_btn("✕", self.close_app, COLOR_CLOSE_BG)
        self.create_win_btn("☐", self.toggle_maximize, "#3e3e42")
        self.create_win_btn("_", self.minimize_app, "#3e3e42")
        tk.Button(self.title_bar, text="🎨", command=self.pick_accent_color, bg=COLOR_BG_HEADER, fg="white", bd=0, cursor="hand2").pack(side=tk.RIGHT, padx=5)

        content = tk.Frame(self, bg=COLOR_BG_MAIN, padx=5, pady=5); content.pack(fill=tk.BOTH, expand=True)
        settings = tk.Frame(content, bg=COLOR_BG_MAIN); settings.pack(fill=tk.X, pady=(0, 5))
        
        r1 = tk.Frame(settings, bg=COLOR_BG_MAIN); r1.pack(fill=tk.X, pady=2)
        tk.Label(r1, text="Hedef:", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG).pack(side=tk.LEFT)
        self.path_entry = tk.Entry(r1, font=FONT_CODE, bg=COLOR_INPUT_BG, fg=COLOR_TEXT_FG, relief="flat")
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)
        self.path_entry.insert(0, os.getcwd())
        tk.Button(r1, text="...", command=self.select_directory, bg=COLOR_BG_HEADER, fg="white", relief="flat", width=3).pack(side=tk.LEFT)
        tk.Button(r1, text="📂 Import", command=self.import_structure_from_folder, bg=COLOR_BG_MAIN, fg=COLOR_FOLDER_TAG, bd=0, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=10)

        r2 = tk.Frame(settings, bg=COLOR_BG_MAIN); r2.pack(fill=tk.X, pady=2)
        tk.Label(r2, text="Kategori:", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG).pack(side=tk.LEFT)
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(r2, textvariable=self.cat_var, state="readonly", width=20)
        self.cat_combo['values'] = list(self.all_presets.keys())
        self.cat_combo.pack(side=tk.LEFT, padx=5)
        self.cat_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        tk.Label(r2, text="Şablon:", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG).pack(side=tk.LEFT, padx=(10,0))
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(r2, textvariable=self.preset_var, state="readonly", width=25)
        self.preset_combo.pack(side=tk.LEFT, padx=5)
        self.preset_combo.bind("<<ComboboxSelected>>", self.load_preset)

        tk.Button(r2, text="💾 Kaydet", command=self.save_current_as_preset, bg=COLOR_BG_MAIN, fg=COLOR_LOG_SUCCESS, bd=0, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(r2, text="🧹", command=self.clear_editor, bg=COLOR_BG_MAIN, fg=COLOR_LOG_EXIST, bd=0).pack(side=tk.LEFT)
        
        self.btn_format = tk.Button(r2, text="🔨 Yapılandır", command=self.format_structure_visuals, bg=COLOR_BG_MAIN, fg=self.accent_color, bd=0, font=("Segoe UI", 9, "bold"))
        self.btn_format.pack(side=tk.LEFT, padx=5)

        tf = tk.Frame(r2, bg=COLOR_BG_MAIN); tf.pack(side=tk.RIGHT)
        self.btn_editor = tk.Button(tf, text="◧", command=self.toggle_editor, bg=COLOR_BG_MAIN, fg="white", bd=0, font=FONT_ICON); self.btn_editor.pack(side=tk.LEFT)
        self.btn_explorer = tk.Button(tf, text="◨", command=self.toggle_explorer, bg=COLOR_BG_MAIN, fg="white", bd=0, font=FONT_ICON); self.btn_explorer.pack(side=tk.LEFT)
        self.btn_log = tk.Button(tf, text="◪", command=self.toggle_logs, bg=COLOR_BG_MAIN, fg="white", bd=0, font=FONT_ICON); self.btn_log.pack(side=tk.LEFT)

        r3 = tk.Frame(settings, bg=COLOR_BG_MAIN); r3.pack(fill=tk.X, pady=5)
        self.btn_create = tk.Button(r3, text="🚀 PROJEYİ OLUŞTUR", command=self.generate_structure, bg=self.accent_color, fg="white", font=("Segoe UI", 11, "bold"), relief="flat")
        self.btn_create.pack(fill=tk.X, ipady=2)

        self.v_pane = tk.PanedWindow(content, orient=tk.VERTICAL, bg=COLOR_BG_MAIN, sashwidth=4, bd=0); self.v_pane.pack(fill=tk.BOTH, expand=True)
        self.h_pane = tk.PanedWindow(self.v_pane, orient=tk.HORIZONTAL, bg=COLOR_BG_MAIN, sashwidth=4, bd=0)

        self.editor_frame = tk.Frame(self.h_pane, bg=COLOR_BG_MAIN)
        tk.Label(self.editor_frame, text="YAPI EDİTÖRÜ", bg=COLOR_BG_MAIN, fg="#666", font=("Segoe UI", 8)).pack(anchor="w")
        ec = tk.Frame(self.editor_frame, bg=COLOR_INPUT_BG); ec.pack(fill=tk.BOTH, expand=True)
        esc = ttk.Scrollbar(ec, orient="vertical"); esc.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area = tk.Text(ec, font=FONT_CODE, bg=COLOR_INPUT_BG, fg=COLOR_TEXT_FG, relief="flat", padx=10, pady=10, yscrollcommand=esc.set, wrap="none")
        self.text_area.pack(fill=tk.BOTH, expand=True); esc.config(command=self.text_area.yview)
        
        # Placeholder Eventleri
        self.text_area.bind("<FocusIn>", self.remove_placeholder)
        self.text_area.bind("<FocusOut>", self.on_focus_out)
        self.text_area.bind("<Button-1>", self.remove_placeholder)
        
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<Tab>", self.handle_tab)
        self.text_area.bind("<Return>", self.handle_enter)

        self.explorer_frame = tk.Frame(self.h_pane, bg=COLOR_BG_MAIN)
        tk.Label(self.explorer_frame, text="KLASÖR GEZGİNİ", bg=COLOR_BG_MAIN, fg="#666", font=("Segoe UI", 8)).pack(anchor="w")
        tc = tk.Frame(self.explorer_frame, bg=COLOR_INPUT_BG); tc.pack(fill=tk.BOTH, expand=True)
        tsc = ttk.Scrollbar(tc, orient="vertical"); tsc.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(tc, selectmode="browse", yscrollcommand=tsc.set); self.tree.pack(fill=tk.BOTH, expand=True); tsc.config(command=self.tree.yview)
        self.tree.heading("#0", text="Dosyalar", anchor="w"); self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.h_pane.add(self.editor_frame, minsize=300); self.h_pane.add(self.explorer_frame, minsize=200)

        self.log_frame = tk.Frame(self.v_pane, bg=COLOR_BG_MAIN)
        lh = tk.Frame(self.log_frame, bg=COLOR_BG_MAIN); lh.pack(fill=tk.X)
        tk.Label(lh, text="ÇIKTI & SEÇENEKLER", bg=COLOR_BG_MAIN, fg="#666", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        
        # ÇÖP KUTUSU (LOG TEMİZLEME)
        tk.Button(lh, text="🗑️", command=self.clear_logs, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_FG, bd=0, cursor="hand2", font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=5)

        self.var_code = tk.BooleanVar(); self.var_git = tk.BooleanVar(); self.var_docker = tk.BooleanVar()
        ttk.Checkbutton(lh, text="VS Code", variable=self.var_code).pack(side=tk.RIGHT)
        ttk.Checkbutton(lh, text="Git", variable=self.var_git).pack(side=tk.RIGHT, padx=5)
        ttk.Checkbutton(lh, text="Docker", variable=self.var_docker).pack(side=tk.RIGHT, padx=5)
        
        lc = tk.Frame(self.log_frame, bg="#1e1e1e"); lc.pack(fill=tk.BOTH, expand=True)
        lsc = ttk.Scrollbar(lc, orient="vertical"); lsc.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_area = tk.Text(lc, font=("Consolas", 9), bg="#1e1e1e", fg="#a0a0a0", relief="flat", state="disabled", yscrollcommand=lsc.set)
        self.log_area.pack(fill=tk.BOTH, expand=True); lsc.config(command=self.log_area.yview)
        self.log_area.tag_config("success", foreground=COLOR_LOG_SUCCESS); self.log_area.tag_config("error", foreground=COLOR_LOG_EXIST); self.log_area.tag_config("info", foreground=COLOR_LOG_INFO)

        self.v_pane.add(self.h_pane, stretch="always"); self.v_pane.add(self.log_frame, minsize=100)

        footer = tk.Frame(content, bg=COLOR_BG_MAIN); footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(2,0))
        tk.Label(footer, text="Tasarımcı Hakkı", bg=COLOR_BG_MAIN, fg="#444", font=("Segoe UI", 8)).pack()
        grip = tk.Label(footer, bg="#444", cursor="size_nw_se"); grip.place(relx=1.0, rely=1.0, anchor="se", width=15, height=15)
        grip.bind("<Button-1>", self.start_resize); grip.bind("<B1-Motion>", self.perform_resize)

    # --- DÜZELTİLEN TOGGLE BUTONLARI (KESİN ÇÖZÜM) ---
    def toggle_editor(self):
        if self.show_editor:
            self.h_pane.forget(self.editor_frame)
            self.btn_editor.config(text="□", fg=COLOR_ICON_INACTIVE)
            self.show_editor = False
        else:
            if self.show_explorer:
                self.h_pane.add(self.editor_frame, before=self.explorer_frame)
            else:
                self.h_pane.add(self.editor_frame)
            self.btn_editor.config(text="◧", fg="white")
            self.show_editor = True

    def toggle_explorer(self):
        if self.show_explorer:
            self.h_pane.forget(self.explorer_frame)
            self.btn_explorer.config(text="□", fg=COLOR_ICON_INACTIVE)
            self.show_explorer = False
        else:
            self.h_pane.add(self.explorer_frame)
            self.btn_explorer.config(text="◨", fg="white")
            self.show_explorer = True

    def toggle_logs(self): 
        if self.show_logs:
            self.v_pane.forget(self.log_frame)
            self.btn_log.config(text="□", fg=COLOR_ICON_INACTIVE)
            self.show_logs = False
        else:
            self.v_pane.add(self.log_frame)
            self.btn_log.config(text="◪", fg="white")
            self.show_logs = True

    def create_win_btn(self, t, c, h):
        b = tk.Button(self.title_bar, text=t, command=c, bg=COLOR_BG_HEADER, fg="white", bd=0, width=4)
        b.pack(side=tk.RIGHT, fill=tk.Y); b.bind("<Enter>", lambda e: b.config(bg=h)); b.bind("<Leave>", lambda e: b.config(bg=COLOR_BG_HEADER))

    def click_window(self, e): self._offsetx=e.x; self._offsety=e.y
    def drag_window(self, e): self.geometry(f"+{self.winfo_pointerx()-self._offsetx}+{self.winfo_pointery()-self._offsety}")
    def close_app(self): self.save_app_config(); self.destroy()
    def minimize_app(self): self.overrideredirect(False); self.state('iconic')
    def on_restore(self, e): 
        if self.state()=='normal' and not self.overrideredirect(): self.overrideredirect(True)
    def toggle_maximize(self):
        if not self.is_maximized: self.pre_max_geometry=self.geometry(); self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0"); self.is_maximized=True
        else: self.geometry(self.pre_max_geometry); self.is_maximized=False
    def start_resize(self,e): self._rx=e.x_root; self._ry=e.y_root; self._rw=self.winfo_width(); self._rh=self.winfo_height()
    def perform_resize(self,e): self.geometry(f"{max(self._rw+(e.x_root-self._rx),800)}x{max(self._rh+(e.y_root-self._ry),600)}")
    def select_directory(self):
        d = filedialog.askdirectory(); 
        if d: self.path_entry.delete(0,tk.END); self.path_entry.insert(0,d); self.refresh_file_viewer(d)
    
    # --- EDİTÖR SEÇİMİ ---
    def get_available_editors(self):
        editors = []
        editor_defs = [
            ("Visual Studio Code", "code", [os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"), r"C:\Program Files\Microsoft VS Code\Code.exe"]),
            ("Notepad++", "notepad++", [r"C:\Program Files\Notepad++\notepad++.exe", r"C:\Program Files (x86)\Notepad++\notepad++.exe"]),
            ("Sublime Text", "subl", [r"C:\Program Files\Sublime Text 3\sublime_text.exe"]),
            ("Notepad", "notepad", [])
        ]
        for name, cmd, paths in editor_defs:
            found = False
            if shutil.which(cmd): editors.append((name, cmd)); found = True
            if not found:
                for p in paths:
                    if os.path.exists(p): editors.append((name, f'"{p}"')); found = True; break
        return editors

    def open_file_with(self, file_path, editor_cmd=None):
        try:
            if editor_cmd:
                subprocess.Popen(f'{editor_cmd} "{file_path}"', shell=True)
                self.log_write(f"Dosya açıldı: {os.path.basename(file_path)}", "success")
            else:
                os.startfile(file_path); self.log_write(f"Varsayılanla açıldı: {os.path.basename(file_path)}", "success")
        except Exception as e: self.log_write(f"Açma hatası: {e}", "error")

    def show_open_with_dialog(self, file_path):
        dialog = tk.Toplevel(self); dialog.title("Birlikte Aç"); dialog.configure(bg=COLOR_BG_MAIN); dialog.overrideredirect(True)
        w, h = 400, 350; x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2); y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        tk.Frame(dialog, bg="#007acc", height=2).pack(side=tk.TOP, fill=tk.X)
        tk.Label(dialog, text=f"Dosyayı Aç: {os.path.basename(file_path)}", bg=COLOR_BG_MAIN, fg="white", font=FONT_HEADER, wraplength=380).pack(pady=15)
        editors = self.get_available_editors()
        btn_frame = tk.Frame(dialog, bg=COLOR_BG_MAIN); btn_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        tk.Button(btn_frame, text="⚡ Sistem Varsayılanı", command=lambda: [self.open_file_with(file_path), dialog.destroy()], bg="#2d2d2d", fg="white", relief="flat", anchor="w", padx=10).pack(fill=tk.X, pady=2)
        tk.Frame(btn_frame, bg="#333", height=1).pack(fill=tk.X, pady=5)
        for name, cmd in editors: tk.Button(btn_frame, text=f"📝 {name}", command=lambda c=cmd: [self.open_file_with(file_path, c), dialog.destroy()], bg="#2d2d2d", fg="white", relief="flat", anchor="w", padx=10).pack(fill=tk.X, pady=2)
        tk.Button(dialog, text="İptal", command=dialog.destroy, bg=COLOR_CLOSE_BG, fg="white", relief="flat").pack(side=tk.BOTTOM, fill=tk.X, pady=0, ipady=5)

    def on_tree_double_click(self, e):
        try: item = self.tree.selection()[0]
        except: return
        if item == "__UP__":
            current = self.path_entry.get(); parent = os.path.dirname(current)
            if parent != current: self.path_entry.delete(0,tk.END); self.path_entry.insert(0,parent); self.refresh_file_viewer(parent)
            return
        path = item
        if os.path.isdir(path): self.path_entry.delete(0,tk.END); self.path_entry.insert(0,path); self.refresh_file_viewer(path)
        else: self.show_open_with_dialog(path)

    def refresh_file_viewer(self, path):
        for i in self.tree.get_children(): self.tree.delete(i)
        if not os.path.exists(path): return
        parent = os.path.dirname(path)
        if parent and parent != path: self.tree.insert("", "end", iid="__UP__", text="🔙 .. (Üst Dizin)")
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'): continue
                fp = os.path.join(path, item)
                icon = DEFAULT_FOLDER_ICON if os.path.isdir(fp) else FILE_ICONS.get(os.path.splitext(item)[1].lower(), DEFAULT_FILE_ICON)
                self.tree.insert("", "end", iid=fp, text=f" {icon} {item}")
        except: pass
        
    def import_structure_from_folder(self):
        target_dir = filedialog.askdirectory()
        if not target_dir: return
        root_name = os.path.basename(target_dir)
        structure_lines = [f"📁 {root_name}"]
        ignored = {'.git', '__pycache__', 'venv', 'node_modules'}
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in ignored and not d.startswith('.')]
            files = [f for f in files if f not in ignored and not f.startswith('.')]
            level = root.replace(target_dir, '').count(os.sep)
            indent = '    ' * (level + 1)
            if root != target_dir: structure_lines.append(f"{'    ' * level}📁 {os.path.basename(root)}")
            for f in files: structure_lines.append(f"{indent}📄 {f}")
        
        self.remove_placeholder(None)
        self.text_area.delete("1.0", tk.END); self.text_area.insert("1.0", "\n".join(structure_lines))
        self.highlight_syntax(); self.log_write(f"İçe aktarıldı: {root_name}", "success")

    def clear_editor(self): 
        self.text_area.delete("1.0", tk.END)
        self.add_placeholder()
    
    def pick_accent_color(self):
        c = colorchooser.askcolor(color=self.accent_color)[1]
        if c:
            self.accent_color = c; self.save_app_config(); self.btn_create.config(bg=c); self.btn_format.config(fg=c)
            ttk.Style().map("Treeview", background=[('selected', c)])

if __name__ == "__main__":
    app = App()
    app.mainloop()
