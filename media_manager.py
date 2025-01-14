import os
import sqlite3
import tkinter as tk
from tkinter import Scrollbar, ttk, filedialog, simpledialog
import tempfile
import mimetypes

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
                    data BLOB
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()

    def get_media_data(self, title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM media WHERE title = ?', (title,))
            row = cursor.fetchone()
            return row[0] if row else None

    def add_media(self, media_type, title):
        filetypes = {
            "pdf": [("PDF files", "*.pdf")],
            "mp4": [("MP4 files", "*.mp4")],
            "mp3": [("MP3 files", "*.mp3")]
        }
        file_path = filedialog.askopenfilename(filetypes=filetypes[media_type])
        if file_path:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO media (type, title, data) VALUES (?, ?, ?)
                ''', (media_type, title, file_data))
            return f'Media "{title}" added successfully.'
        else:
            return 'File not found or no file selected!'

    def open_media(self, title):
        media_data = self.get_media_data(title)
        if media_data:
            mime_type, _ = mimetypes.guess_type(title)
            extension = mimetypes.guess_extension(mime_type) if mime_type else ''
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
                tmp_file.write(media_data)
                temp_path = tmp_file.name
            try:
                os.startfile(temp_path)
                return f'Opening "{title}"...'
            except Exception as e:
                return f'Could not open media: {e}'
        else:
            return 'Media not found.'

    def delete_media(self, title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # First set BLOB data to NULL to ensure it's cleared from the database
            cursor.execute('UPDATE media SET data = NULL WHERE title = ?', (title,))
            # Then delete the record
            cursor.execute('DELETE FROM media WHERE title = ?', (title,))
            conn.commit()
            # VACUUM to reclaim storage space
            cursor.execute('VACUUM')
            return f'Media "{title}" deleted.'

    def rename_media(self, old_title, new_title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Check if old title exists
            cursor.execute('SELECT COUNT(*) FROM media WHERE title = ?', (old_title,))
            if cursor.fetchone()[0] == 0:
                return f'Media "{old_title}" not found.'
            # Check if new title already exists
            cursor.execute('SELECT COUNT(*) FROM media WHERE title = ?', (new_title,))
            if cursor.fetchone()[0] > 0:
                return f'Title "{new_title}" already exists.'
            # Perform the rename
            cursor.execute('UPDATE media SET title = ? WHERE title = ?', (new_title, old_title))
            conn.commit()
            return f'Media "{old_title}" renamed to "{new_title}".'

    
    def search_media(self, media_type, title):
            query = 'SELECT title, type FROM media WHERE 1=1'
            params = []
            if media_type:
                query += ' AND type = ?'
                params.append(media_type)
            if title:
                query += ' AND title LIKE ?'
                params.append('%' + title + '%')
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()

    def register_user(self, username, password):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                return "User registered successfully."
            except sqlite3.IntegrityError:
                return "Username already exists."

    def login_user(self, username, password):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ? AND password = ?', (username, password))
            return "Login successful." if cursor.fetchone()[0] == 1 else "Invalid username or password."

class MediaManagerApp:
    
    def __init__(self, root):
        self.manager = MediaManager()
        self.root = root
        self.root.title("媒體管理器")
        self.root.geometry("800x600")
        self.center_window(self.root)

        font_large = ("Helvetica", 16)
        button_options = {"font": font_large, "padx": 10, "pady": 10}

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
            add_window.destroy()

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

        columns = ("title", "type")
        tree = ttk.Treeview(manage_window, columns=columns, show="headings", height=13)
        tree.heading("title", text="標題")
        tree.heading("type", text="檔案類型")
        tree.pack(pady=10, fill="both", expand=True)
        
        scrollbar_y = Scrollbar(manage_window, orient="vertical", command=tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar_y.set)

        def search_media_action():
            media_type = media_type_combobox.get()
            title = title_entry.get()
            results = self.manager.search_media(media_type, title)
            tree.delete(*tree.get_children())
            for result in results:
                title, media_type = result[:2]
                tree.insert("", "end", values=(title, media_type))

        def delete_media_action():
            selected_item = tree.selection()
            if selected_item:
                title = tree.item(selected_item, "values")[0]
                self.manager.delete_media(title)
                tree.delete(selected_item)

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
                    self.status_label.config(text=result)
                    search_media_action()  # Refresh the display after renaming
                    

        button_frame = tk.Frame(manage_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="打開選中媒體", command=open_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="刪除選中媒體", command=delete_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="重新命名標題", command=rename_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="返回上一頁", command=manage_window.destroy, font=font_large).pack(side="left", padx=5)

        

        # Perform initial search to populate the treeview
        search_media_action()

class AuthWindow:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("使用者驗證")
        self.root.geometry("400x250")

        self.center_window()  # Center the window

        font_large = ("Helvetica", 14)
        tk.Label(root, text="使用者名稱:", font=font_large).pack(pady=5)
        self.username_entry = tk.Entry(root, font=font_large)
        self.username_entry.pack()

        tk.Label(root, text="密碼:", font=font_large).pack(pady=5)
        self.password_entry = tk.Entry(root, show="*", font=font_large)
        self.password_entry.pack()

        self.status_label = tk.Label(root, text="", font=font_large)
        self.status_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="登入", command=self.login, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="註冊", command=self.register, font=font_large).pack(side="left", padx=5)

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        result = self.manager.login_user(username, password)
        self.status_label.config(text=result)
        if "successful" in result:
            self.open_main_app()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        result = self.manager.register_user(username, password)
        self.status_label.config(text=result)

    def open_main_app(self):
        self.root.destroy()
        new_root = tk.Tk()
        app = MediaManagerApp(new_root)
        new_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    manager = MediaManager()
    AuthWindow(root, manager)
    root.mainloop()

