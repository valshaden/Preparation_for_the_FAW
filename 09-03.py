# -*- coding: utf-8 -*-
# Упрощенная версия получения курсов криптовалют с табличным выводом
# Столбцы: "Название", "Тикер", "Курс", "Валюта"
# Источник по умолчанию: Binance
# Курс с двумя знаками после запятой
import requests
import tkinter as tk
from tkinter import ttk, messagebox

# --- Маппинг кодов к полным названиям криптовалют ---
CRYPTO_NAMES = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'BNB': 'Binance Coin',
    'SOL': 'Solana',
    'XRP': 'XRP', # Полное имя уже включено в тикер
    'ADA': 'Cardano',
    'DOGE': 'Dogecoin',
    'DOT': 'Polkadot',
    'MATIC': 'Polygon', # Полное имя уже включено в тикер
    'LTC': 'Litecoin',
    'USDT': 'Tether',
    'USDC': 'USD Coin',
    'BUSD': 'Binance USD'
}

# --- Маппинг кодов к полным названиям фиатных валют ---
FIAT_NAMES = {
    "USD": "Доллар США",
    "EUR": "Евро",
    "JPY": "Японская йена",
    "GBP": "Британский фунт стерлингов",
    "CHF": "Швейцарский франк",
    "CNY": "Китайский юань",
    "RUB": "Российский рубль"
}

# --- Список криптовалют для отслеживания в заданном порядке ---
TARGET_CRYPTOS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC', 'LTC']

# --- Функции для получения данных из API ---
def get_binance_data(base_currency):
    """Получаем данные по заданным криптовалютам с Binance относительно выбранной базовой валюты"""
    try:
        url = 'https://api.binance.com/api/v3/ticker/price'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Создаем словарь для быстрого поиска
        price_dict = {item['symbol']: float(item['price']) for item in data}
        result = []
        # Перебираем криптовалюты в заданном порядке
        for crypto in TARGET_CRYPTOS:
            # Определяем символ базовой валюты для Binance API
            # Binance использует USDT, BUSD для USD, и т.д.
            if base_currency == 'USD':
                fiat_symbols = ['USDT', 'BUSD']
            else:
                fiat_symbols = [base_currency]
            
            found_pair = False
            for fiat_symbol in fiat_symbols:
                pair = f"{crypto}{fiat_symbol}"
                if pair in price_dict:
                    price = price_dict[pair]
                    # Получаем полные названия
                    full_name = CRYPTO_NAMES.get(crypto, crypto)
                    currency_name = FIAT_NAMES.get(base_currency, base_currency)
                    result.append({
                        'name': full_name,
                        'ticker': crypto,
                        'price': price,
                        'currency': currency_name
                    })
                    found_pair = True
                    break # Найдена одна пара, переходим к следующей криптовалюте
            
            # Если не нашли пару с фиатом, пробуем BTC пару
            if not found_pair and base_currency != 'BTC':
                pair = f"{crypto}BTC"
                if pair in price_dict:
                    price = price_dict[pair]
                    full_name = CRYPTO_NAMES.get(crypto, crypto)
                    currency_name = CRYPTO_NAMES.get('BTC', 'BTC') # Имя для BTC из CRYPTO_NAMES
                    result.append({
                        'name': full_name,
                        'ticker': crypto,
                        'price': price,
                        'currency': currency_name
                    })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка Binance", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_coingecko_data(base_currency):
    """Получаем данные по заданным криптовалютам с CoinGecko относительно выбранной базовой валюты"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        # Маппинг тикеров CoinGecko
        coingecko_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'LTC': 'litecoin'
        }
        # CoinGecko использует те же коды валют
        params = {
            'vs_currency': base_currency.lower(), # CoinGecko ожидает код в нижнем регистре
            'ids': ','.join([coingecko_ids[c] for c in TARGET_CRYPTOS]),
            'order': 'market_cap_desc', # Порядок из API может отличаться
            'per_page': 20,
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Создаем словарь для сопоставления id CoinGecko с нашими данными
        id_to_crypto = {v: k for k, v in coingecko_ids.items()}
        
        # Создаем упорядоченный список результатов
        result = [None] * len(TARGET_CRYPTOS)
        for coin in data:
            if coin['id'] in id_to_crypto:
                crypto_code = id_to_crypto[coin['id']]
                if crypto_code in TARGET_CRYPTOS:
                    index = TARGET_CRYPTOS.index(crypto_code)
                    full_name = coin['name']
                    price = coin['current_price']
                    currency_name = FIAT_NAMES.get(base_currency.upper(), base_currency.upper())
                    result[index] = {
                        'name': full_name,
                        'ticker': crypto_code,
                        'price': price,
                        'currency': currency_name
                    }
        
        # Убираем None значения, если какие-то криптовалюты не были найдены
        result = [item for item in result if item is not None]
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CoinGecko", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_cryptocompare_data(base_currency):
    """Получаем данные по заданным криптовалютам с CryptoCompare относительно выбранной базовой валюты"""
    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        params = {
            'fsyms': ','.join(TARGET_CRYPTOS), # Запрашиваем в заданном порядке
            'tsyms': base_currency # CryptoCompare использует код валюты напрямую
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = []
        # Перебираем криптовалюты в заданном порядке
        for crypto_code in TARGET_CRYPTOS:
            if crypto_code in data:
                full_name = CRYPTO_NAMES.get(crypto_code, crypto_code)
                # Получаем цену в выбранной валюте
                if base_currency in data[crypto_code] and data[crypto_code][base_currency]:
                    price = data[crypto_code][base_currency]
                    currency_name = FIAT_NAMES.get(base_currency, base_currency)
                    result.append({
                        'name': full_name,
                        'ticker': crypto_code,
                        'price': price,
                        'currency': currency_name
                    })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CryptoCompare", f"Не удалось получить данные:\n{str(e)}")
        return None

# --- Функции интерфейса ---
def show_result_window(title, data):
    """Создает окно с таблицей для отображения результата"""
    if data is None:
        return  # Ошибка уже показана в функции API
    result_window = tk.Toplevel(root)
    result_window.title(f"Результаты: {title}")
    result_window.geometry("800x500")
    # Создаем фрейм для таблицы с возможностью прокрутки
    frame = ttk.Frame(result_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    # Определяем столбцы
    columns = ('name', 'ticker', 'price', 'currency')
    # Создаем Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
    # Определяем заголовки столбцов
    tree.heading('name', text='Название')
    tree.heading('ticker', text='Тикер')
    tree.heading('price', text='Курс')
    tree.heading('currency', text='Валюта')
    # Устанавливаем ширину столбцов
    tree.column('name', width=250, anchor=tk.W)
    tree.column('ticker', width=80, anchor=tk.CENTER)
    tree.column('price', width=150, anchor=tk.E)
    tree.column('currency', width=100, anchor=tk.CENTER)
    # Добавляем вертикальную прокрутку
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    # Размещаем таблицу и скроллбар
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # Заполняем таблицу данными в том порядке, в котором они пришли
    for item in data:
        # Форматируем цену с двумя знаками после запятой
        formatted_price = f"{item['price']:.2f}"
        tree.insert('', tk.END, values=(
            item['name'],
            item['ticker'],
            formatted_price,
            item['currency']
        ))
    # Добавляем метку с количеством записей
    count_label = ttk.Label(result_window, text=f"Всего записей: {len(data)}")
    count_label.pack(pady=(0, 10))

def on_get_data():
    """Обработчик нажатия кнопки 'Получить данные'"""
    selected_api = api_var.get()
    selected_base_currency_code = base_currency_var.get().split(' - ')[0] # Извлекаем код валюты из строки "USD - Доллар США"
    
    if selected_api == "Binance":
        data = get_binance_data(selected_base_currency_code)
        show_result_window(f"Binance Public API ({selected_base_currency_code})", data)
    elif selected_api == "CoinGecko":
        data = get_coingecko_data(selected_base_currency_code)
        show_result_window(f"CoinGecko API ({selected_base_currency_code})", data)
    elif selected_api == "CryptoCompare":
        data = get_cryptocompare_data(selected_base_currency_code)
        show_result_window(f"CryptoCompare API ({selected_base_currency_code})", data)
    else:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите источник данных.")

# --- Создание основного окна ---
root = tk.Tk()
root.title("Курсы криптовалют")
root.geometry("400x200") # Увеличен размер окна для размещения нового элемента
root.resizable(False, False)  # Запрет изменения размера

# Создание и размещение элементов интерфейса
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Выбор источника данных
ttk.Label(main_frame, text="Выберите источник данных:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
api_var = tk.StringVar(value="Binance")
api_combobox = ttk.Combobox(main_frame, textvariable=api_var, 
                           values=["Binance", "CoinGecko", "CryptoCompare"], 
                           state="readonly", width=20)
api_combobox.pack(anchor=tk.W, pady=(0, 10))

# Выбор базовой валюты
ttk.Label(main_frame, text="Выберите базовую валюту:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
# Создаем список значений для Combobox в формате "Код - Название"
base_currency_options = [f"{code} - {name}" for code, name in FIAT_NAMES.items()]
base_currency_var = tk.StringVar(value="USD - Доллар США") # Значение по умолчанию обновлено
base_currency_combobox = ttk.Combobox(main_frame, textvariable=base_currency_var, 
                                     values=base_currency_options, 
                                     state="readonly", width=30)
base_currency_combobox.pack(anchor=tk.W, pady=(0, 15))

# Кнопка для получения данных
get_data_btn = ttk.Button(main_frame, text="Получить данные", command=on_get_data)
get_data_btn.pack()

# Запуск главного цикла событий
root.mainloop()