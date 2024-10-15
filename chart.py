import sqlite3
import matplotlib.pyplot as plt

DB_PATH = 'db/database.db'

def get_progress_data():
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute('''
            SELECT pain_level, COUNT(*) as count FROM progress GROUP BY pain_level
        ''')
        return cursor.fetchall()

def plot_pie_chart():
    data = get_progress_data()
    
    if not data:
        print("Нет данных для построения диаграммы.")
        return

    # Разделим данные на уровни боли и их количество
    labels = [f"Уровень боли {row[0]}" for row in data]
    counts = [row[1] for row in data]

    # Построение круговой диаграммы
    plt.figure(figsize=(6,6))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("Распределение уровня боли")
    plt.axis('equal')  # Для того, чтобы диаграмма выглядела как круг
    plt.show()

if __name__ == '__main__':
    plot_pie_chart()
