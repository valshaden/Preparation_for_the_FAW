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

from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests

# Словари криптовалют и валют
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

# Список доступных API
apis = {
    "CoinGecko": "https://api.coingecko.com/api/v3/simple/price",
    "CoinCap": "https://api.coincap.io/v2/assets/",
    "CryptoCompare": "https://min-api.cryptocompare.com/data/price",
    "Binance": "https://api.binance.com/api/v3/ticker/price"
}

def update_base_label(event):
    code = base_combobox.get()
    name = cryptocurrencies[code]
    b_label.config(text=name)

def update_target_label(event):
    code = target_combobox.get()
    name = currencies[code]
    t_label.config(text=name)

def exchange():
    base_code = base_combobox.get()
    target_code = target_combobox.get()
    selected_api = api_combobox.get()

    if not base_code or not target_code or not selected_api:
        mb.showwarning("Внимание", "Заполните все поля")
        return

    try:
        if selected_api == "CoinGecko":
            # https://api.coingecko.com/api/v3/simple/price?ids=btc&vs_currencies=usd
            url = apis[selected_api]
            params = {
                'ids': base_code.lower(),
                'vs_currencies': target_code.lower()
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if base_code.lower() in data:
                rate_data = data[base_code.lower()]
                if target_code.lower() in rate_data:
                    rate = rate_data[target_code.lower()]
                    show_result(base_code, target_code, rate)
                else:
                    mb.showerror("Ошибка", f"Курс {target_code} не найден")
            else:
                mb.showerror("Ошибка", "Не удалось получить данные")

        elif selected_api == "CoinCap":
            # https://api.coincap.io/v2/assets/bitcoin
            url = apis[selected_api] + base_code.lower()
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            price_usd = float(data['data']['priceUsd'])

            # Пересчитываем в целевую валюту (только если целевая — USD, EUR, RUB)
            if target_code == "USD":
                rate = price_usd
            elif target_code == "EUR":
                # Получаем USD → EUR от CoinCap
                eur_response = requests.get("https://api.coincap.io/v2/rates/euro")
                eur_rate = float(eur_response.json()['data']['rateUsd'])
                rate = price_usd / eur_rate
            elif target_code == "RUB":
                rub_response = requests.get("https://api.coincap.io/v2/rates/russian-ruble")
                rub_rate = float(rub_response.json()['data']['rateUsd'])
                rate = price_usd / rub_rate
            else:
                mb.showerror("Ошибка", "CoinCap поддерживает только USD, EUR, RUB")
                return
            show_result(base_code, target_code, rate)

        elif selected_api == "CryptoCompare":
            # https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD
            url = apis[selected_api]
            params = {
                'fsym': base_code,
                'tsyms': target_code
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if target_code in data:
                rate = data[target_code]
                show_result(base_code, target_code, rate)
            else:
                mb.showerror("Ошибка", "Курс не найден")

        elif selected_api == "Binance":
            # Только пары вроде BTCUSDT, ETHUSDT и т.д.
            symbol = base_code + target_code
            if target_code not in ["USDT", "BUSD", "BTC", "ETH", "BNB", "EUR"]:
                mb.showwarning("Внимание", "Binance поддерживает ограниченные пары (USDT, BTC, ETH...)")
                return
            url = apis[selected_api]
            params = {'symbol': symbol}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            price = float(data['price'])
            show_result(base_code, target_code, price)

    except requests.exceptions.ConnectionError:
        mb.showerror("Ошибка", "Нет подключения к интернету")
    except requests.exceptions.Timeout:
        mb.showerror("Ошибка", "Таймаут соединения")
    except Exception as e:
        mb.showerror("Ошибка", f"Ошибка: {e}")

def show_result(base, target, rate):
    base_name = cryptocurrencies[base]
    target_name = currencies[target]
    mb.showinfo("Курс обмена", f"1 {base_name} = {rate:,.6f} {target_name}")


# === GUI ===
window = Tk()
window.title("Конвертер криптовалют (с выбором API)")
window.geometry("450x480")
window.resizable(False, False)

# Выбор API
Label(window, text="Выберите API:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
api_combobox = ttk.Combobox(
    window,
    values=list(apis.keys()),
    state="readonly"
)
api_combobox.pack(pady=5)
api_combobox.set("CoinGecko")  # API по умолчанию

# Базовая криптовалюта
Label(window, text="Базовая криптовалюта:", font=("Arial", 10)).pack(pady=5)
base_combobox = ttk.Combobox(window, values=list(cryptocurrencies.keys()), state="readonly")
base_combobox.pack(pady=5)
base_combobox.bind("<<ComboboxSelected>>", update_base_label)

b_label = ttk.Label(window, text="", foreground="blue", font=("Arial", 9, "italic"))
b_label.pack(pady=5)

# Целевая валюта
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

# Запуск
window.mainloop()
