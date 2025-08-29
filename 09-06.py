# -*- coding: utf-8 -*-
# Упрощенная версия получения курсов криптовалют с табличным выводом
# Столбцы: "Название", "Тикер", "Курс", "Валюта", "Курс USD", "Валюта USD"
# Источник по умолчанию: Binance
# Курс с двумя знаками после запятой
# Базовая валюта: Доллар США (USD)
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

# --- Базовая валюта ---
BASE_CURRENCY_CODE = "USD"
BASE_CURRENCY_NAME = "USD" # Короткое наименование для таблицы

# --- Маппинг кодов к полным названиям дополнительных валют ---
ADDITIONAL_CURRENCY_NAMES = {
    "EUR": "Евро",
    "JPY": "Японская йена",
    "GBP": "Британский фунт",
    "CHF": "Швейцарский франк",
    "CNY": "Китайский юань",
    "RUB": "Российский рубль"
}

# --- Список криптовалют для отслеживания в заданном порядке ---
TARGET_CRYPTOS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC', 'LTC']

# --- Словарь для хранения ссылок на открытые окна результатов ---
result_windows = {}

# --- Функции для получения данных из API ---
def get_exchange_rate(additional_currency_code):
    """Получает курс дополнительной валюты к доллару США с CryptoCompare"""
    if additional_currency_code == BASE_CURRENCY_CODE:
        return 1.0
    try:
        # Используем CryptoCompare для получения фиатного курса
        url = f'https://min-api.cryptocompare.com/data/price'
        params = {
            'fsym': BASE_CURRENCY_CODE,
            'tsyms': additional_currency_code
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data.get(additional_currency_code)
        if rate:
             return rate
        else:
             raise ValueError(f"Курс {BASE_CURRENCY_CODE} к {additional_currency_code} не найден в ответе API")
    except Exception as e:
        print(f"Ошибка при получении курса {BASE_CURRENCY_CODE} к {additional_currency_code}: {e}")
        messagebox.showerror("Ошибка", f"Не удалось получить курс {BASE_CURRENCY_CODE} к {additional_currency_code}:\n{str(e)}")
        return None

def get_binance_data(additional_currency_code, usd_to_additional_rate):
    """Получаем данные по заданным криптовалютам с Binance относительно USD и дополнительной валюты"""
    if usd_to_additional_rate is None and additional_currency_code != BASE_CURRENCY_CODE:
        return None # Невозможно пересчитать без курса
        
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
            # Binance использует USDT, BUSD для USD
            fiat_symbols = ['USDT', 'BUSD']
            
            found_pair = False
            for fiat_symbol in fiat_symbols:
                pair = f"{crypto}{fiat_symbol}"
                if pair in price_dict:
                    price_usd = price_dict[pair]
                    # Получаем цену в дополнительной валюте
                    if usd_to_additional_rate is not None:
                        price_additional = price_usd * usd_to_additional_rate
                    else:
                        price_additional = price_usd # Если дополнительная валюта - USD
                    
                    # Получаем полные названия
                    full_name = CRYPTO_NAMES.get(crypto, crypto)
                    # Всегда используем короткое имя базовой валюты для таблицы
                    currency_name = BASE_CURRENCY_NAME
                    additional_currency_name = additional_currency_code
                    result.append({
                        'name': full_name,
                        'ticker': crypto,
                        'price': price_usd,
                        'currency': currency_name,
                        'price_additional': price_additional,
                        'currency_additional': additional_currency_name
                    })
                    found_pair = True
                    break # Найдена одна пара, переходим к следующей криптовалюте
            
            # Если не нашли пару с фиатом, пробуем BTC пару (без пересчета в доп. валюту для простоты)
            if not found_pair and BASE_CURRENCY_CODE != 'BTC':
                pair = f"{crypto}BTC"
                if pair in price_dict:
                    price_btc = price_dict[pair]
                    # Для BTC пары пересчет сложнее, пропустим для простоты или добавим позже
                    # Здесь можно добавить логику пересчета BTC->USD->доп.валюта
                    # Пока пропускаем BTC пары для соответствия с другими API
                    pass
        return result
    except Exception as e:
        messagebox.showerror("Ошибка Binance", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_coingecko_data(additional_currency_code, usd_to_additional_rate):
    """Получаем данные по заданным криптовалютам с CoinGecko относительно USD и дополнительной валюты"""
    if usd_to_additional_rate is None and additional_currency_code != BASE_CURRENCY_CODE:
        return None # Невозможно пересчитать без курса
        
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
        # CoinGecko использует код валюты в нижнем регистре
        params = {
            'vs_currency': BASE_CURRENCY_CODE.lower(),
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
        for coin in data: # <-- Исправлено: добавлено тело цикла
            if coin['id'] in id_to_crypto:
                crypto_code = id_to_crypto[coin['id']]
                if crypto_code in TARGET_CRYPTOS:
                    index = TARGET_CRYPTOS.index(crypto_code)
                    full_name = coin['name']
                    price_usd = coin['current_price']
                    # Получаем цену в дополнительной валюте
                    if usd_to_additional_rate is not None:
                        price_additional = price_usd * usd_to_additional_rate
                    else:
                        price_additional = price_usd # Если дополнительная валюта - USD
                    
                    # Всегда используем короткое имя базовой валюты для таблицы
                    currency_name = BASE_CURRENCY_NAME
                    additional_currency_name = additional_currency_code
                    result[index] = {
                        'name': full_name,
                        'ticker': crypto_code,
                        'price': price_usd,
                        'currency': currency_name,
                        'price_additional': price_additional,
                        'currency_additional': additional_currency_name
                    }
        
        # Убираем None значения, если какие-то криптовалюты не были найдены
        result = [item for item in result if item is not None]
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CoinGecko", f"Не удалось получить данные:\n{str(e)}")
        return None

def get_cryptocompare_data(additional_currency_code, usd_to_additional_rate):
    """Получаем данные по заданным криптовалютам с CryptoCompare относительно USD и дополнительной валюты"""
    if usd_to_additional_rate is None and additional_currency_code != BASE_CURRENCY_CODE:
        return None # Невозможно пересчитать без курса
        
    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        params = {
            'fsyms': ','.join(TARGET_CRYPTOS), # Запрашиваем в заданном порядке
            'tsyms': BASE_CURRENCY_CODE # Запрашиваем цены в USD
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = []
        # Перебираем криптовалюты в заданном порядке
        for crypto_code in TARGET_CRYPTOS:
            if crypto_code in data: # <-- Исправлено: добавлено тело условия
                full_name = CRYPTO_NAMES.get(crypto_code, crypto_code)
                # Получаем цену в USD
                if BASE_CURRENCY_CODE in data[crypto_code] and data[crypto_code][BASE_CURRENCY_CODE]:
                    price_usd = data[crypto_code][BASE_CURRENCY_CODE]
                    # Получаем цену в дополнительной валюте
                    if usd_to_additional_rate is not None:
                        price_additional = price_usd * usd_to_additional_rate
                    else:
                        price_additional = price_usd # Если дополнительная валюта - USD
                    
                    # Всегда используем короткое имя базовой валюты для таблицы
                    currency_name = BASE_CURRENCY_NAME
                    additional_currency_name = additional_currency_code
                    result.append({
                        'name': full_name,
                        'ticker': crypto_code,
                        'price': price_usd,
                        'currency': currency_name,
                        'price_additional': price_additional,
                        'currency_additional': additional_currency_name
                    })
        return result
    except Exception as e:
        messagebox.showerror("Ошибка CryptoCompare", f"Не удалось получить данные:\n{str(e)}")
        return None

# --- Функции интерфейса ---
def show_result_window(api_name, title, data):
    """Создает или обновляет окно с таблицей для отображения результата"""
    if data is None:
        messagebox.showerror("Ошибка", f"Не удалось получить данные для {title}")
        return  # Ошибка уже показана в функции API
    
    # Проверяем, существует ли уже окно для этого API
    if api_name in result_windows and result_windows[api_name].winfo_exists():
        # Если окно существует, обновляем его содержимое
        update_result_window(result_windows[api_name], data)
    else:
        # Если окно не существует, создаем новое
        result_window = tk.Toplevel(root)
        result_window.title(f"Результаты: {title}")
        result_window.geometry("1000x500") # Увеличен размер окна для новых столбцов
        
        # Сохраняем ссылку на окно
        result_windows[api_name] = result_window
        
        # Создаем фрейм для таблицы с возможностью прокрутки
        frame = ttk.Frame(result_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Определяем столбцы
        columns = ('name', 'ticker', 'price', 'currency', 'price_additional', 'currency_additional')
        
        # Создаем Treeview
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Определяем заголовки столбцов
        tree.heading('name', text='Название')
        tree.heading('ticker', text='Тикер')
        tree.heading('price', text=f'Курс ({BASE_CURRENCY_NAME})')
        tree.heading('currency', text=f'Валюта ({BASE_CURRENCY_NAME})')
        tree.heading('price_additional', text='Курс (Доп. валюта)')
        tree.heading('currency_additional', text='Валюта (Доп. валюта)')
        
        # Устанавливаем ширину столбцов
        tree.column('name', width=200, anchor=tk.W)
        tree.column('ticker', width=70, anchor=tk.CENTER)
        tree.column('price', width=120, anchor=tk.E)
        tree.column('currency', width=60, anchor=tk.CENTER)
        tree.column('price_additional', width=120, anchor=tk.E)
        tree.column('currency_additional', width=60, anchor=tk.CENTER)
        
        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)
        
        # Сохраняем ссылку на treeview в окне для последующего обновления
        result_window.tree = tree
        
        # Заполняем таблицу данными
        update_treeview(tree, data)
        
        # Добавляем метку с количеством записей
        count_label = ttk.Label(result_window, text=f"Всего записей: {len(data)}")
        count_label.pack(pady=(0, 10))
        # Сохраняем ссылку на метку для последующего обновления
        result_window.count_label = count_label
        
        # Обработчик закрытия окна
        def on_closing():
            result_windows.pop(api_name, None)  # Удаляем ссылку на окно
            result_window.destroy()
        
        result_window.protocol("WM_DELETE_WINDOW", on_closing)

def update_result_window(window, data):
    """Обновляет содержимое существующего окна результатов"""
    # Очищаем таблицу
    for item in window.tree.get_children():
        window.tree.delete(item)
    
    # Заполняем таблицу новыми данными
    update_treeview(window.tree, data)
    
    # Обновляем метку с количеством записей
    window.count_label.config(text=f"Всего записей: {len(data)}")
    
    # Поднимаем окно на передний план
    window.lift()
    window.focus_force()

def update_treeview(tree, data):
    """Заполняет Treeview данными"""
    for item in data:
        # Форматируем цены с двумя знаками после запятой
        formatted_price = f"{item['price']:.2f}"
        formatted_price_additional = f"{item['price_additional']:.2f}"
        tree.insert('', tk.END, values=(
            item['name'],
            item['ticker'],
            formatted_price,
            item['currency'],
            formatted_price_additional,
            item['currency_additional']
        ))

def on_get_data():
    """Обработчик нажатия кнопки 'Получить данные'"""
    selected_api = api_var.get()
    selected_additional_currency_code = additional_currency_var.get().split(' - ')[0] # Извлекаем код валюты
    
    # Получаем курс дополнительной валюты к USD
    if selected_additional_currency_code != BASE_CURRENCY_CODE:
        usd_to_additional_rate = get_exchange_rate(selected_additional_currency_code)
        if usd_to_additional_rate is None:
            messagebox.showerror("Ошибка", "Не удалось получить курс дополнительной валюты. Данные не будут загружены.")
            return
    else:
        usd_to_additional_rate = 1.0 # Курс USD к USD = 1

    if selected_api == "Binance":
        data = get_binance_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("Binance", f"Binance Public API ({BASE_CURRENCY_CODE} + {selected_additional_currency_code})", data)
    elif selected_api == "CoinGecko":
        data = get_coingecko_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("CoinGecko", f"CoinGecko API ({BASE_CURRENCY_CODE} + {selected_additional_currency_code})", data)
    elif selected_api == "CryptoCompare":
        data = get_cryptocompare_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("CryptoCompare", f"CryptoCompare API ({BASE_CURRENCY_CODE} + {selected_additional_currency_code})", data)
    else:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите источник данных.")

# --- Создание основного окна ---
root = tk.Tk()
root.title("Курсы криптовалют")
root.geometry("400x250") # Увеличен размер окна для размещения всех элементов
root.resizable(False, False)  # Запрет изменения размера

# Создание и размещение элементов интерфейса
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Информация о базовой валюте
base_currency_label = ttk.Label(main_frame, text="Базовая валюта: Доллар США (USD)", font=('Arial', 10))
base_currency_label.pack(anchor=tk.W, pady=(0, 5))

# Выбор дополнительной валюты
ttk.Label(main_frame, text="Выберите дополнительную валюту:", font=('Arial', 10)).pack(anchor=tk.W, pady=(5, 5))
# Создаем список значений для Combobox в формате "Код - Название"
additional_currency_options = [f"{code} - {name}" for code, name in ADDITIONAL_CURRENCY_NAMES.items()]
# По умолчанию выберем RUB
additional_currency_var = tk.StringVar(value="RUB - Российский рубль") # <-- Изменено на RUB по умолчанию
additional_currency_combobox = ttk.Combobox(main_frame, textvariable=additional_currency_var, 
                                     values=additional_currency_options, 
                                     state="readonly", width=30)
additional_currency_combobox.pack(anchor=tk.W, pady=(0, 10))

# Выбор источника данных
ttk.Label(main_frame, text="Выберите источник данных:", font=('Arial', 10)).pack(anchor=tk.W, pady=(5, 5))
api_var = tk.StringVar(value="Binance")
api_combobox = ttk.Combobox(main_frame, textvariable=api_var, 
                           values=["Binance", "CoinGecko", "CryptoCompare"], 
                           state="readonly", width=20)
api_combobox.pack(anchor=tk.W, pady=(0, 15))

# Кнопка для получения данных
get_data_btn = ttk.Button(main_frame, text="Получить данные", command=on_get_data)
get_data_btn.pack()

# Запуск главного цикла событий
root.mainloop()