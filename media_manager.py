import os
import sqlite3
import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, ttk, filedialog, simpledialog

class MediaManager:
    def __init__(self):
        self.db_name = 'media_manager.db'
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    title TEXT,
                    filepath TEXT
                )
            ''')
            conn.commit()

    def add_media(self, media_type, title):
        filetypes = {
            "pdf": [("PDF files", "*.pdf")],
            "mp4": [("MP4 files", "*.mp4")],
            "mp3": [("MP3 files", "*.mp3")]
        }
        filepath = filedialog.askopenfilename(filetypes=filetypes.get(media_type, [("All files", "*.*")]))
        if filepath and os.path.exists(filepath):
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO media (type, title, filepath) VALUES (?, ?, ?)', (media_type, title, filepath))
                conn.commit()
                return f'{media_type.capitalize()} "{title}" added successfully.'
        else:
            return 'File not found or no file selected!'

    def delete_media(self, title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM media WHERE title = ?', (title,))
            conn.commit()
            return f'Media "{title}" 已刪除.'

    def rename_media(self, old_title, new_title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE media SET title = ? WHERE title = ?', (new_title, old_title))
            conn.commit()
            return f' "{old_title}" 已重命名為 "{new_title}" .'

    def search_media(self, media_type=None, title=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if media_type and title:
                cursor.execute('SELECT title, filepath, type FROM media WHERE type = ? AND title LIKE ?', (media_type, f'%{title}%'))
            elif media_type:
                cursor.execute('SELECT title, filepath, type FROM media WHERE type = ?', (media_type,))
            elif title:
                cursor.execute('SELECT title, filepath, type FROM media WHERE title LIKE ?', (f'%{title}%',))
            else:
                cursor.execute('SELECT title, filepath, type FROM media')
            return cursor.fetchall()

    def get_media_path(self, title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT filepath FROM media WHERE title = ?', (title,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    def open_media(self, title):
        media_path = self.get_media_path(title)
        if media_path:
            try:
                os.startfile(media_path)
                return f'Opening "{title}"...'
            except Exception as e:
                return f'Could not open media: {e}'
        else:
            return 'Media not found!'

class MediaManagerApp:
    def __init__(self, root):
        self.manager = MediaManager()
        self.root = root
        self.root.title("媒體管理器")
        self.root.geometry("800x600")
        self.center_window(self.root)

        # 設定字體和按鈕大小
        font_large = ("Helvetica", 16)
        button_options = {"font": font_large, "padx": 10, "pady": 10}

        # 顯示標題和按鈕
        tk.Label(root, text="媒體管理器", font=("Helvetica", 24)).pack(pady=20)
        
        self.status_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        tk.Button(root, text="新增媒體", command=self.add_media_gui, **button_options).pack(pady=10)
        tk.Button(root, text="管理媒體", command=self.manage_media_gui, **button_options).pack(pady=10)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def add_media_gui(self):
        # 新增多媒體的GUI窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("新增媒體")
        add_window.geometry("500x350")
        self.center_window(add_window)

        font_large = ("Helvetica", 14)

        tk.Label(add_window, text="媒體類型:", font=font_large).pack(pady=10)
        media_type_combobox = ttk.Combobox(add_window, values=["pdf", "mp4", "mp3"], font=font_large)
        media_type_combobox.pack(pady=10)

        tk.Label(add_window, text="標題:", font=font_large).pack(pady=10)
        title_entry = tk.Entry(add_window, font=font_large)
        title_entry.pack(pady=10)

        def add_media_action():
            media_type = media_type_combobox.get()
            title = title_entry.get()
            result = self.manager.add_media(media_type, title)
            self.status_label.config(text=result)
            add_window.destroy()  # 關閉新增媒體的子視窗

        tk.Button(add_window, text="新增", command=add_media_action, font=font_large).pack(pady=20)
        tk.Button(add_window, text="返回上一頁", command=add_window.destroy, font=font_large).pack(pady=10)

    def manage_media_gui(self):
        manage_window = tk.Toplevel(self.root)
        manage_window.title("管理媒體")
        manage_window.geometry("800x600")
        self.center_window(manage_window)

        font_large = ("Helvetica", 14)

        tk.Label(manage_window, text="媒體類型 (pdf, mp4, mp3, 或留空):", font=font_large).pack(pady=10)
        media_type_combobox = ttk.Combobox(manage_window, values=["", "pdf", "mp4", "mp3"], font=font_large)
        media_type_combobox.pack(pady=10)

        tk.Label(manage_window, text="標題:", font=font_large).pack(pady=10)
        title_frame = tk.Frame(manage_window)
        title_frame.pack(pady=10)
        title_entry = tk.Entry(title_frame, font=font_large)
        title_entry.pack(side="left", padx=5)
        tk.Button(title_frame, text="搜尋", command=lambda: search_media_action(), font=font_large).pack(side="left", padx=5)

        columns = ("title", "filename", "type", "filepath")
        tree = ttk.Treeview(manage_window, columns=columns, show="headings", height=13)
        tree.heading("title", text="標題")
        tree.heading("filename", text="檔案名稱")
        tree.heading("type", text="檔案類型")
        tree.heading("filepath", text="檔案路徑")
        tree.pack(pady=10, fill="both", expand=True)

        scrollbar_y = Scrollbar(manage_window, orient="vertical", command=tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = Scrollbar(manage_window, orient="horizontal", command=tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        tree.configure(xscrollcommand=scrollbar_x.set)

        def search_media_action():
            media_type = media_type_combobox.get()
            title = title_entry.get()
            results = self.manager.search_media(media_type, title)
            tree.delete(*tree.get_children())
            for result in results:
                title, filepath, media_type = result
                filename = os.path.basename(filepath)
                tree.insert("", "end", values=(title, filename, media_type, filepath))

        def delete_media_action():
            selected_item = tree.selection()
            if selected_item:
                title = tree.item(selected_item, "values")[0]
                result = self.manager.delete_media(title)
                self.status_label.config(text=result)
                search_media_action()

        def open_media_action():
            selected_item = tree.selection()
            if selected_item:
                title = tree.item(selected_item, "values")[0]
                result = self.manager.open_media(title)
                self.status_label.config(text=result)

        def rename_media_action():
            selected_item = tree.selection()
            if selected_item:
                old_title = tree.item(selected_item, "values")[0]
                new_title = simpledialog.askstring("重新命名標題", "輸入新的標題:")
                if new_title:
                    result = self.manager.rename_media(old_title, new_title)
                    search_media_action()

        button_frame = tk.Frame(manage_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="打開選中媒體", command=open_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="刪除選中媒體", command=delete_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="重新命名標題", command=rename_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="返回上一頁", command=manage_window.destroy, font=font_large).pack(side="left", padx=5)

        # 預設列出所有檔案
        search_media_action()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaManagerApp(root)
    root.mainloop()
