import os

db_path = 'db/database.db'

if os.path.exists(db_path):
    os.remove(db_path)
    print("База данных успешно удалена!")
else:
    print("База данных не найдена!")
