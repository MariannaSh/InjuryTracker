import matplotlib.pyplot as plt
import os
from database import get_progress_data

def create_pie_chart():
    data = get_progress_data()  # Получаем данные о прогрессе
    if not data:
        return None  # Возвращаем None, если нет данных для построения

    pain_levels = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=pain_levels, autopct='%1.1f%%', startangle=140)
    plt.title('Распределение уровней боли')
    plt.axis('equal')

    # Убедимся, что папка static существует
    if not os.path.exists('static'):
        os.makedirs('static')

    chart_path = 'static/chart.png'
    plt.savefig(chart_path)
    plt.close()

    return chart_path  # Возвращаем путь к созданной диаграмме
