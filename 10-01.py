# -*- coding: utf-8 -*-
# Упрощенная версия получения курсов криптовалют с табличным выводом
# Столбцы: "Название", "Тикер", "Курс", "Валюта"
# Источник по умолчанию: Binance
# Курс с двумя знаками после запятой
# Базовая валюта: Доллар США (USD)
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from datetime import datetime

# --- Маппинг кодов к полным названиям криптовалют ---
CRYPTO_NAMES = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'BNB': 'Binance Coin',
    'SOL': 'Solana',
    'XRP': 'XRP', # Полное имя уже включено в тикер
    'ADA': 'Cardano',
    'AVAX': 'Avalanche',
    'DOGE': 'Dogecoin',
    'DOT': 'Polkadot',
    'TRX': 'Tron',
    'LINK': 'Chainlink',
    'MATIC': 'Polygon', # Полное имя уже включено в тикер
    'SHIB': 'Shiba Inu',
    'LTC': 'Litecoin',
    'BCH': 'Bitcoin Cash',
    'ATOM': 'Cosmos',
    'XLM': 'Stellar',
    'ETC': 'Ethereum Classic',
    'XMR': 'Monero',
    'ALGO': 'Algorand',
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
TARGET_CRYPTOS = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'TRX',
    'LINK', 'MATIC', 'SHIB', 'LTC', 'BCH', 'ATOM', 'XLM', 'ETC', 'XMR', 'ALGO'
]

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
        # messagebox.showerror("Ошибка Binance", f"Не удалось получить данные:\n{str(e)}")
        # Не показываем ошибку в основном окне при автообновлении
        print(f"Ошибка Binance: {str(e)}")
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
            'AVAX': 'avalanche-2',
            'DOGE': 'dogecoin',
            'DOT': 'polkadot',
            'TRX': 'tron',
            'LINK': 'chainlink',
            'MATIC': 'matic-network',
            'SHIB': 'shiba-inu',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'ATOM': 'cosmos',
            'XLM': 'stellar',
            'ETC': 'ethereum-classic',
            'XMR': 'monero',
            'ALGO': 'algorand'
        }
        # CoinGecko использует код валюты в нижнем регистре
        params = {
            'vs_currency': BASE_CURRENCY_CODE.lower(),
            'ids': ','.join([coingecko_ids.get(c, '') for c in TARGET_CRYPTOS if c in coingecko_ids]), # Фильтруем только известные ID
            'order': 'market_cap_desc', # Порядок из API может отличаться
            'per_page': 30, # Увеличен лимит для 20 криптовалют
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
        # messagebox.showerror("Ошибка CoinGecko", f"Не удалось получить данные:\n{str(e)}")
        # Не показываем ошибку в основном окне при автообновлении
        print(f"Ошибка CoinGecko: {str(e)}")
        return None

def get_cryptocompare_data(additional_currency_code, usd_to_additional_rate):
    """Получаем данные по заданным криптовалютам с CryptoCompare относительно USD и дополнительной валюты"""
    if usd_to_additional_rate is None and additional_currency_code != BASE_CURRENCY_CODE:
        return None # Невозможно пересчитать без курса

    try:
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        # Формируем список символов из TARGET_CRYPTOS
        fsyms = ','.join(TARGET_CRYPTOS)
        params = {
            'fsyms': fsyms, # Запрашиваем в заданном порядке
            'tsyms': BASE_CURRENCY_CODE # Запрашиваем цены в USD
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = []
        # Перебираем криптовалюты в заданном порядке
        for crypto_code in TARGET_CRYPTOS:
            if crypto_code in data:  # <-- Исправлено: добавлено тело условия
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
        # messagebox.showerror("Ошибка CryptoCompare", f"Не удалось получить данные:\n{str(e)}")
        # Не показываем ошибку в основном окне при автообновлении
        print(f"Ошибка CryptoCompare: {str(e)}")
        return None

# --- Функции интерфейса ---
def show_result_window(api_name, title, data, additional_currency_code, usd_to_additional_rate):
    """Создает или обновляет окно с таблицей для отображения результата"""
    # Проверяем, существует ли уже окно для этого API
    if api_name in result_windows and result_windows[api_name].winfo_exists():
        # Если окно существует, обновляем его содержимое (включая заголовок)
        update_result_window(result_windows[api_name], title, data)
    else:
        # Если окно не существует, создаем новое
        result_window = tk.Toplevel(root)
        result_window.title(f"Результаты: {title}") # Устанавливаем начальный заголовок
        result_window.geometry("1000x650") # Увеличен размер окна для новых элементов

        # Сохраняем ссылку на окно и данные для автообновления
        result_windows[api_name] = result_window
        result_window.api_name = api_name
        result_window.additional_currency_code = additional_currency_code
        result_window.usd_to_additional_rate = usd_to_additional_rate
        result_window.is_auto_updating = False
        result_window.update_job = None

        # Создаем фрейм для элементов управления
        control_frame = ttk.Frame(result_window)
        control_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Метка и поле ввода интервала
        ttk.Label(control_frame, text="Интервал автообновления (мин):").pack(side=tk.LEFT)
        interval_var = tk.StringVar(value="10") # Значение по умолчанию
        interval_entry = ttk.Entry(control_frame, textvariable=interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=(5, 10))
        result_window.interval_var = interval_var

        # Кнопка включения/выключения автообновления
        auto_update_btn = ttk.Button(control_frame, text="Включить автообновление", 
                                    command=lambda: toggle_auto_update(result_window, auto_update_btn))
        auto_update_btn.pack(side=tk.LEFT, padx=(0, 10))
        result_window.auto_update_btn = auto_update_btn

        # Индикатор загрузки (изначально скрыт)
        loading_label = ttk.Label(control_frame, text="Загрузка...")
        loading_label.pack(side=tk.LEFT)
        loading_label.pack_forget() # Скрываем изначально
        result_window.loading_label = loading_label

        # Создаем фрейм для таблицы с возможностью прокрутки
        table_frame = ttk.Frame(result_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # Определяем столбцы
        columns = ('name', 'ticker', 'price', 'currency', 'price_additional', 'currency_additional')

        # Создаем Treeview
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=25) # Увеличена высота
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
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)

        # Сохраняем ссылку на treeview в окне для последующего обновления
        result_window.tree = tree

        # Заполняем таблицу данными
        update_treeview(tree, data)

        # Создаем фрейм для нижней панели информации
        info_frame = ttk.Frame(result_window)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Добавляем метку с количеством записей и временем последнего обновления
        count_and_time_label = ttk.Label(info_frame, text=f"Всего записей: {len(data) if data else 0} | Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        count_and_time_label.pack(side=tk.LEFT)
        result_window.count_and_time_label = count_and_time_label

        # Обработчик закрытия окна
        def on_closing():
            # Останавливаем автообновление при закрытии окна
            if result_window.update_job:
                result_window.after_cancel(result_window.update_job)
            result_windows.pop(api_name, None)  # Удаляем ссылку на окно
            result_window.destroy()

        result_window.protocol("WM_DELETE_WINDOW", on_closing)

def update_result_window(window, title, data):
    """Обновляет содержимое существующего окна результатов (включая заголовок)"""
    # Обновляем заголовок окна
    window.title(f"Результаты: {title}")

    # Очищаем таблицу
    for item in window.tree.get_children():
        window.tree.delete(item)

    # Заполняем таблицу новыми данными
    update_treeview(window.tree, data)

    # Обновляем метку с количеством записей и временем
    count = len(data) if data else 0
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    window.count_and_time_label.config(text=f"Всего записей: {count} | Последнее обновление: {current_time}")

    # Поднимаем окно на передний план
    window.lift()
    window.focus_force()

def update_treeview(tree, data):
    """Заполняет Treeview данными"""
    for item in data: # <-- Исправлено: добавлено тело цикла
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

def toggle_auto_update(window, button):
    """Включает или выключает автообновление для окна"""
    if window.is_auto_updating:
        # Выключаем автообновление
        window.is_auto_updating = False
        if window.update_job:
            window.after_cancel(window.update_job)
        button.config(text="Включить автообновление")
        window.loading_label.pack_forget() # Скрываем индикатор загрузки
    else:
        # Включаем автообновление
        try:
            interval_minutes = float(window.interval_var.get())
            if interval_minutes <= 0:
                raise ValueError("Интервал должен быть положительным числом")
        except ValueError:
            messagebox.showwarning("Некорректный ввод", "Пожалуйста, введите корректное положительное число для интервала (в минутах).")
            return
            
        window.is_auto_updating = True
        button.config(text="Выключить автообновление")
        # Запускаем цикл автообновления
        auto_update_loop(window, interval_minutes * 60 * 1000) # Преобразуем минуты в миллисекунды

def auto_update_loop(window, interval_ms):
    """Цикл автообновления данных"""
    if not window.winfo_exists() or not window.is_auto_updating:
        return
        
    # Показываем индикатор загрузки
    window.loading_label.pack(side=tk.LEFT)
    window.update_idletasks() # Принудительно обновляем интерфейс
    
    # Запускаем получение данных в отдельном потоке, чтобы не блокировать GUI
    threading.Thread(target=lambda: fetch_and_update_data(window), daemon=True).start()
    
    # Планируем следующее обновление
    window.update_job = window.after(int(interval_ms), lambda: auto_update_loop(window, interval_ms))

def fetch_and_update_data(window):
    """Получает новые данные и обновляет окно (выполняется в отдельном потоке)"""
    api_name = window.api_name
    additional_currency_code = window.additional_currency_code
    usd_to_additional_rate = window.usd_to_additional_rate
    
    # Получаем новые данные
    if api_name == "Binance":
        new_data = get_binance_data(additional_currency_code, usd_to_additional_rate)
    elif api_name == "CoinGecko":
        new_data = get_coingecko_data(additional_currency_code, usd_to_additional_rate)
    elif api_name == "CryptoCompare":
        new_data = get_cryptocompare_data(additional_currency_code, usd_to_additional_rate)
    else:
        new_data = None

    # Планируем обновление GUI в основном потоке
    if window.winfo_exists():
        window.after(0, lambda: update_gui_after_fetch(window, new_data, api_name, additional_currency_code))

def update_gui_after_fetch(window, data, api_name, additional_currency_code):
    """Обновляет GUI после получения данных (выполняется в основном потоке)"""
    # Скрываем индикатор загрузки
    window.loading_label.pack_forget()
    
    # Обновляем данные в окне
    if data is not None:
        # Формируем заголовок с информацией о валютах
        window_title = f"{api_name} API ({BASE_CURRENCY_CODE} + {additional_currency_code})"
        update_result_window(window, window_title, data)
    else:
        # Обновляем только время в случае ошибки
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        window.count_and_time_label.config(text=f"Всего записей: {window.tree.get_children().__len__()} | Последнее обновление: {current_time} (Ошибка при обновлении)")

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

    # Формируем заголовок с информацией о валютах
    window_title = f"{selected_api} API ({BASE_CURRENCY_CODE} + {selected_additional_currency_code})"

    if selected_api == "Binance":
        data = get_binance_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("Binance", window_title, data, selected_additional_currency_code, usd_to_additional_rate)
    elif selected_api == "CoinGecko":
        data = get_coingecko_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("CoinGecko", window_title, data, selected_additional_currency_code, usd_to_additional_rate)
    elif selected_api == "CryptoCompare":
        data = get_cryptocompare_data(selected_additional_currency_code, usd_to_additional_rate)
        show_result_window("CryptoCompare", window_title, data, selected_additional_currency_code, usd_to_additional_rate)
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
base_currency_label.pack(anchor=tk.CENTER, pady=(0, 5)) # Выравнивание по центру

# Выбор дополнительной валюты
ttk.Label(main_frame, text="Выберите дополнительную валюту:", font=('Arial', 10)).pack(anchor=tk.CENTER, pady=(5, 5)) # Выравнивание по центру
# Создаем список значений для Combobox в формате "Код - Название"
additional_currency_options = [f"{code} - {name}" for code, name in ADDITIONAL_CURRENCY_NAMES.items()]
# По умолчанию выберем RUB
additional_currency_var = tk.StringVar(value="RUB - Российский рубль") # <-- Изменено на RUB по умолчанию
additional_currency_combobox = ttk.Combobox(main_frame, textvariable=additional_currency_var,
                                     values=additional_currency_options,
                                     state="readonly", width=30)
additional_currency_combobox.pack(anchor=tk.CENTER, pady=(0, 10)) # Выравнивание по центру

# Выбор источника данных
ttk.Label(main_frame, text="Выберите источник данных:", font=('Arial', 10)).pack(anchor=tk.CENTER, pady=(5, 5)) # Выравнивание по центру
api_var = tk.StringVar(value="Binance")
api_combobox = ttk.Combobox(main_frame, textvariable=api_var,
                           values=["Binance", "CoinGecko", "CryptoCompare"],
                           state="readonly", width=20)
api_combobox.pack(anchor=tk.CENTER, pady=(0, 15)) # Выравнивание по центру

# Кнопка для получения данных
get_data_btn = ttk.Button(main_frame, text="Получить данные", command=on_get_data)
get_data_btn.pack(anchor=tk.CENTER) # Выравнивание по центру

# Запуск главного цикла событий
root.mainloop()