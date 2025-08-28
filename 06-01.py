from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests

def update_base_label(event):
    code = base_combobox.get()
    name = cryptocurrencies[code]
    b_label.config(text=name)

def update_target_label(event):
    code = target_combobox.get()
    name = currencies[code]
    t_label.config(text=name)

def exchange():
    base_code = base_combobox.get().lower()   # CoinGecko использует lowercase
    target_code = target_combobox.get().upper()

    if not base_code or not target_code:
        mb.showwarning("Внимание", "Выберите обе валюты")
        return

    try:
        # Запрос к CoinGecko: получаем цену базовой криптовалюты в целевой валюте
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': base_code,
            'vs_currencies': target_code.lower()
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if base_code in data:
            rate_data = data[base_code]
            if target_code.lower() in rate_data:
                exchange_rate = rate_data[target_code.lower()]
                base_name = cryptocurrencies[base_code.upper()]
                target_name = currencies[target_code]
                mb.showinfo(
                    "Курс обмена",
                    f"1 {base_name} = {exchange_rate:,.6f} {target_name}"
                )
            else:
                mb.showerror("Ошибка", f"Курс для {target_code} недоступен")
        else:
            mb.showerror("Ошибка", f"Криптовалюта {base_code} не найдена")

    except requests.exceptions.ConnectionError:
        mb.showerror("Ошибка", "Проверьте подключение к интернету")
    except requests.exceptions.Timeout:
        mb.showerror("Ошибка", "Время ожидания истекло")
    except Exception as e:
        mb.showerror("Ошибка", f"Произошла ошибка: {e}")

# Словарь криптовалют (код → полное название)
cryptocurrencies = {
    "BTC": "Биткойн",
    "ETH": "Эфириум",
    "BNB": "Binance Coin",
    "SOL": "Солана",
    "XRP": "Риппл",
    "DOGE": "Догекоин",
    "ADA": "Кардано",
    "TRX": "Трон",
    "DOT": "Полкадот",
    "MATIC": "Матич"
}

# Словарь целевых валют (можно фиат и крипта)
currencies = {
    "USD": "Доллар США",
    "EUR": "Евро",
    "RUB": "Российский рубль",
    "GBP": "Фунт стерлингов",
    "JPY": "Японская иена",
    "BTC": "Биткойн",
    "ETH": "Эфириум",
    "BNB": "Binance Coin"
}

# Создание окна
window = Tk()
window.title("Конвертер криптовалют")
window.geometry("400x380")
window.resizable(False, False)

# Интерфейс
Label(window, text="Базовая криптовалюта:", font=("Arial", 10)).pack(pady=5)
base_combobox = ttk.Combobox(window, values=list(cryptocurrencies.keys()), state="readonly")
base_combobox.pack(pady=5)
base_combobox.bind("<<ComboboxSelected>>", update_base_label)

b_label = ttk.Label(window, text="", foreground="blue", font=("Arial", 9, "italic"))
b_label.pack(pady=5)

Label(window, text="Целевая валюта:", font=("Arial", 10)).pack(pady=5)
target_combobox = ttk.Combobox(window, values=list(currencies.keys()), state="readonly")
target_combobox.pack(pady=5)
target_combobox.bind("<<ComboboxSelected>>", update_target_label)

t_label = ttk.Label(window, text="", foreground="blue", font=("Arial", 9, "italic"))
t_label.pack(pady=5)

# Кнопка
Button(
    window,
    text="Получить курс обмена",
    background="green",
    foreground="white",
    font=("Arial", 10, "bold"),
    command=exchange
).pack(pady=20)

# Запуск приложения
window.mainloop()
