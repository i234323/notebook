import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import configparser
import random

# Константы
CONFIG_FILE = "TCD.ini"

# Загрузка конфигурации
def load_config():
    config = configparser.ConfigParser()
    # Удаляем BOM из файла перед чтением
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as file:
        content = file.read()
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        file.write(content)

    config.read(CONFIG_FILE, encoding="utf-8")
    return config

# Функции для шифрования/дешифрования с использованием XOR
def xor_encrypt_decrypt(text, key):
    return ''.join(chr(ord(char) ^ key) for char in text)

class TCDNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Блокнот TCD")
        self.filename = None
        self.config = load_config()
        self.key = int(self.config["main"]["keyuser"])

        # Создание компонентов интерфейса
        self.create_widgets()
        self.create_context_menu()
        self.root.bind("<KeyPress>", self.key_handler)
        self.text_area.bind("<Button-3>", self.show_context_menu)

    def create_widgets(self):
        # Текстовое поле
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True)
        self.text_area.pack(expand=1, fill=tk.BOTH)

        # Строка состояния
        self.status = tk.StringVar()
        self.status.set("Статус операции")
        self.status_bar = tk.Label(self.root, textvariable=self.status, anchor=tk.W, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Главное меню
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Новый", command=self.new_file)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Правка"
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Копировать", command=self.copy_text)
        edit_menu.add_command(label="Вставить", command=self.paste_text)
        edit_menu.add_command(label="Вырезать", command=self.cut_text)
        edit_menu.add_command(label="Выделить всё", command=self.select_all_text)
        edit_menu.add_command(label="Параметры", command=self.edit_parameters)
        menu_bar.add_cascade(label="Правка", menu=edit_menu)

        # Меню "Справка"
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Содержание", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

    def create_context_menu(self):
        # Контекстное меню (правая кнопка мыши)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_command(label="Выделить всё", command=self.select_all_text)

    def show_context_menu(self, event):
        # Показать контекстное меню
        self.context_menu.post(event.x_root, event.y_root)

    def key_handler(self, event):
        if event.state == 4:  # Ctrl нажат
            if event.keycode == 83:  # Ctrl+S
                self.save_file()
            elif event.keycode == 78:  # Ctrl+N
                self.new_file()
            elif event.keycode == 79:  # Ctrl+O
                self.open_file()
            elif event.keycode == 81:  # Ctrl+Q
                self.root.quit()
            elif event.keycode == 67:  # Ctrl+C
                self.copy_text()
            elif event.keycode == 86:  # Ctrl+V
                self.paste_text()
            elif event.keycode == 88:  # Ctrl+X
                self.cut_text()
            elif event.keycode == 65:  # Ctrl+A
                self.select_all_text()
            elif event.keycode == 122:  # Ctrl+Z
                self.text_area.edit_undo()
        else:
            if event.keycode == 112:  # F1
                self.show_help()

    # Операции с текстом
    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")

    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")

    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")

    def select_all_text(self):
        self.text_area.tag_add("sel", "1.0", "end")
        self.status.set("Выделен весь текст.")

    # Операции с файлами
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.status.set("Создан новый файл.")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("TTXT файлы", "*.ttxt")])
        if file_path:
            config = configparser.ConfigParser()
            config.read(file_path, encoding="utf-8")
            try:
                key_open = int(config["main"]["keyopen"])
                encrypted_content = config["main"]["mess"]
                final_key = (self.key + key_open) % 256
                decrypted_content = xor_encrypt_decrypt(encrypted_content, final_key)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, decrypted_content)
                self.filename = file_path
                self.status.set(f"Открыт файл {os.path.basename(file_path)}")
            except Exception:
                messagebox.showerror("Ошибка", "Не удалось расшифровать содержимое файла.")

    def save_file(self):
        if not self.filename:
            self.save_file_as()
        else:
            self.write_to_file(self.filename)

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".ttxt",
                                                 filetypes=[("TTXT файлы", "*.ttxt")])
        if file_path:
            self.filename = file_path
            self.write_to_file(file_path)

    def write_to_file(self, file_path):
        random_key = ''.join(random.choices("0123456789", k=10))
        final_key = (self.key + int(random_key)) % 256
        encrypted_content = xor_encrypt_decrypt(self.text_area.get(1.0, tk.END).strip(), final_key)

        config = configparser.ConfigParser()
        config["main"] = {
            "keyopen": random_key,
            "mess": encrypted_content
        }
        with open(file_path, "w", encoding="utf-8") as file:
            config.write(file)

        self.status.set(f"Файл {os.path.basename(file_path)} сохранён.")

    def edit_parameters(self):
        new_key = simpledialog.askinteger("Изменение ключа", "Введите новый числовой ключ шифрования:")
        if new_key:
            self.key = new_key
            self.config["main"]["keyuser"] = str(new_key)
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                self.config.write(file)
            self.status.set("Ключ шифрования успешно обновлён.")

    @staticmethod
    def show_help():
        messagebox.showinfo("Содержание", "Это Блокнот TCD с функцией шифрования/дешифрования.")

    @staticmethod
    def show_about():
        messagebox.showinfo("О программе", "(С) Алексей Кузнецов v1.0 2024\n"
                                           "Благодарность маме и папе:\n"
                                           "Кузнецова Татьяна Горгиевна\n"
                                           "Кузнецов Олег Степанович")

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    app = TCDNotepad(root)
    root.mainloop()
