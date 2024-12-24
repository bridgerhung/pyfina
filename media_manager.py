import os
import sqlite3
import tkinter as tk
from tkinter import Scrollbar, ttk, filedialog, simpledialog
import tempfile
import mimetypes

class MediaManager:
    """Media Manager Class for handling various media files.
    This class provides functionality to manage different types of media files (PDF, MP4, MP3)
    through a SQLite database. It allows for basic CRUD operations and file handling.
    Attributes:
        db_name (str): Name of the SQLite database file.
    Methods:
        setup_database(): 
            Initializes the SQLite database with required table structure.
        get_media_data(title: str) -> bytes:
            Retrieves binary data of a media file from database.
        add_media(media_type: str, title: str) -> str:
            Adds a new media file to the database.
            Supports PDF, MP4, and MP3 formats.
        open_media(title: str) -> str:
            Opens a media file using the system's default application.
        delete_media(title: str) -> str:
            Removes a media file from the database.
        rename_media(old_title: str, new_title: str) -> str:
            Renames a media file in the database.
        search_media(media_type: str, title: str) -> list:
            Searches for media files based on type and title.
            Returns a list of matching records.
    Requirements:
        - sqlite3
        - tkinter (for filedialog)
        - mimetypes
        - tempfile
        - os
    """
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
            cursor.execute('DELETE FROM media WHERE title = ?', (title,))
            conn.commit()
            return f'Media "{title}" deleted.'

    def rename_media(self, old_title, new_title):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
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

class MediaManagerApp:
    """
    A GUI application for managing media files using Tkinter.
    This class provides a graphical user interface for managing different types of media files
    (PDF, MP4, MP3). It allows users to add, search, delete, rename, and open media files
    through a user-friendly interface.
    Attributes:
        manager (MediaManager): Instance of MediaManager class handling media operations
        root (tk.Tk): Main window of the application
        status_label (tk.Label): Label for displaying status messages
    Methods:
        center_window(window): Centers a window on the screen
        add_media_gui(): Opens a window for adding new media
        manage_media_gui(): Opens a window for managing existing media
    The GUI includes:
    - Main window with options to add and manage media
    - Add media window with fields for media type and title
    - Manage media window with search, view, delete, and rename capabilities
    - Status messages for operation feedback
    """
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

        button_frame = tk.Frame(manage_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="打開選中媒體", command=open_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="刪除選中媒體", command=delete_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="重新命名標題", command=rename_media_action, font=font_large).pack(side="left", padx=5)
        tk.Button(button_frame, text="返回上一頁", command=manage_window.destroy, font=font_large).pack(side="left", padx=5)

        

        # Perform initial search to populate the treeview
        search_media_action()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaManagerApp(root)
    root.mainloop()
