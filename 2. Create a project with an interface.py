# 7.3.1. Асинхронное программирование
# 7.3.2. Библиотека g4f
# 7.3.3. Потоковый вывод данных
# 7.3.4. Генерация изображений

# 1. Получаем курсы валют из интернета
# 2. Создаем проект с интерфейсом

### Программа с оконным интерфейсом  ###

from tkinter import *
from tkinter import messagebox as mb
import requests
import json

def exchange():
    code = entry.get().upper()

    if code:
        try:
            response = requests.get(f'https://open.er-api.com/v6/latest/USD')
            response.raise_for_status()  
            data = response.json()

            if code in data['rates']:
                exchange_rate = data['rates'][code]
                             
                mb.showinfo("Курс обмена", f"Курс к доллару: {exchange_rate:.2f} {code} за 1 доллар")
            else:
                mb.showerror("Ошибка", f"Валюта {code} не найдена")
        except Exception as e:
            mb.showerror("Ошибка", f"Ошибка: {e}")

    else:
        mb.showwarning("Внимание", "Введите код валюты")

# Создание графического интерфейса
window = Tk()
window.title("Курс обмена валюты к доллару")
window.geometry("360x180")

Label(text="Введите код валюты:").pack(padx=10, pady=10)

entry = Entry()
entry.pack(padx=10, pady=10)

Button(text="Получить курс обмена к доллару", command=exchange).pack(padx=10, pady=10)

window.mainloop()
