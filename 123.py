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

def search_media_action():
    media_type = media_type_combobox.get()
    title = title_entry.get()
    results = self.manager.search_media(media_type, title)
    tree.delete(*tree.get_children())
    for result in results:
        title, media_type = result[:2]
        tree.insert("", "end", values=(title, media_type))