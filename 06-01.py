'''
Как работает выбор API:
CoinGecko
    Любые: BTC→USD, ETH→RUB, BTC→ETH
    Универсальный, самый простой
CoinCap
    Только через USD (но можно пересчитать в EUR/RUB)
    Нужно 2 запроса для фиата
CryptoCompare
    Например: BTC→USD
    Требует fsym / tsyms
Binance
    Только торговые пары: BTCUSDT, ETHBTC
    Не поддерживает RUB напрямую
'''
# Qwen

import tkinter as tk
from tkinter import ttk, Toplevel, Text, Scrollbar, Frame, Label
import requests
import json
import pprint

# --- Функция для отображения результата в отдельном окне ---
def show_result_window(title, data):
    result_window = Toplevel(root)
    result_window.title(title)
    result_window.geometry("800x600")
    result_window.resizable(True, True)

    Label(result_window, text=title, font=("Helvetica", 14, "bold")).pack(pady=10)

    frame = Frame(result_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    text_widget = Text(frame, wrap=tk.NONE, font=("Courier", 10))
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    v_scroll = Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    h_scroll = Scrollbar(result_window, orient=tk.HORIZONTAL, command=text_widget.xview)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    text_widget.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    p = pprint.PrettyPrinter(indent=4, width=100, depth=5)
    formatted_data = p.pformat(data)

    text_widget.insert(tk.END, formatted_data)
    text_widget.config(state=tk.DISABLED)  # Только для чтения


# --- Функции для запросов к API ---
def fetch_binance():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        show_result_window("Binance API: BTC/USDT", data)
    except Exception as e:
        show_error("Binance", e)

def fetch_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        show_result_window("CoinGecko API: Bitcoin (USD)", data)
    except Exception as e:
        show_error("CoinGecko", e)

def fetch_cryptocompare():
    try:
        url = "https://min-api.cryptocompare.com/data/pricemultifull"
        params = {'fsyms': 'BTC', 'tsyms': 'USD'}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        show_result_window("CryptoCompare: BTC → USD", data)
    except Exception as e:
        show_error("CryptoCompare", e)


# --- Обработка ошибок ---
def show_error(source, error):
    error_window = Toplevel(root)
    error_window.title("Ошибка")
    error_window.geometry("500x200")
    Label(
        error_window,
        text=f"Ошибка при запросе к {source}:",
        font=("Helvetica", 12, "bold"),
        fg="red"
    ).pack(pady=10)
    text_widget = Text(error_window, wrap=tk.WORD, font=("Courier", 10), height=6)
    text_widget.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, str(error))
    text_widget.config(state=tk.DISABLED)


# --- Обработчик кнопки "Получить данные" ---
def on_fetch():
    selection = api_combobox.get()
    if selection == "Binance Public API":
        fetch_binance()
    elif selection == "CoinGecko":
        fetch_coingecko()
    elif selection == "CryptoCompare":
        fetch_cryptocompare()
    else:
        show_error("Выбор API", "Не выбран корректный источник данных.")


# --- Основное окно ---
root = tk.Tk()
root.title("Криптовалютный курс — Выбор API")
root.geometry("400x200")
root.resizable(False, False)

# Заголовок
Label(root, text="Выберите источник данных", font=("Helvetica", 14, "bold")).pack(pady=20)

# Выпадающий список с тремя API
api_options = ["Binance Public API", "CoinGecko", "CryptoCompare"]
api_combobox = ttk.Combobox(root, values=api_options, state="readonly", width=30, font=("Helvetica", 11))
api_combobox.set("Выберите API")  # значение по умолчанию
api_combobox.pack(pady=10)

# Кнопка получения данных
ttk.Button(root, text="Получить курс", command=on_fetch).pack(pady=10)

# Запуск приложения
root.mainloop()