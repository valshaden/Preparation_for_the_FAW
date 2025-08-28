import requests
import json
import pprint
from time import sleep
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread

class CryptoPriceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Курсы криптовалют - Главное окно")
        self.root.geometry("400x150")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_main_ui()
    
    def setup_main_ui(self):
        """Настройка главного окна"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Получение курсов криптовалют", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 15))
        
        # Выбор API через выпадающий список
        ttk.Label(main_frame, text="Выберите источник данных:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.api_var = tk.StringVar(value="CoinGecko")  # По умолчанию CoinGecko
        api_combobox = ttk.Combobox(main_frame, textvariable=self.api_var, 
                                   values=["Binance", "CoinGecko", "CryptoCompare"], 
                                   state="readonly", width=15)
        api_combobox.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # Кнопка получения данных
        get_data_btn = ttk.Button(main_frame, text="Получить данные", 
                                 command=self.open_selected_api_window)
        get_data_btn.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def open_selected_api_window(self):
        """Открытие окна для выбранного API"""
        selected_api = self.api_var.get()
        
        if selected_api == "Binance":
            api_function = self.get_binance_data
        elif selected_api == "CoinGecko":
            api_function = self.get_coingecko_data
        elif selected_api == "CryptoCompare":
            api_function = self.get_cryptocompare_data
        else:
            messagebox.showerror("Ошибка", "Неизвестный источник данных")
            return
        
        api_window = tk.Toplevel(self.root)
        api_window.title(f"{selected_api} - Получение данных")
        api_window.geometry("800x600")
        api_window.configure(bg='#f0f0f0')
        
        APIWindow(api_window, selected_api, api_function)
    
    def get_binance_data(self, callback):
        """Получаем данные с Binance Public API"""
        try:
            callback("🔄 Подключаемся к Binance API...")
            sleep(1)
            
            symbols_url = 'https://api.binance.com/api/v3/ticker/price'
            result = requests.get(symbols_url, timeout=10)
            
            if result.status_code == 200:
                callback("✅ Подключение успешно! Обрабатываем данные...")
                sleep(1)
                
                data = result.json()
                popular_coins = {
                    'BTCUSDT': {'name': 'Bitcoin', 'ticker': 'BTC'},
                    'ETHUSDT': {'name': 'Ethereum', 'ticker': 'ETH'},
                    'BNBUSDT': {'name': 'Binance Coin', 'ticker': 'BNB'},
                    'ADAUSDT': {'name': 'Cardano', 'ticker': 'ADA'},
                    'XRPUSDT': {'name': 'Ripple', 'ticker': 'XRP'},
                    'DOGEUSDT': {'name': 'Dogecoin', 'ticker': 'DOGE'},
                    'SOLUSDT': {'name': 'Solana', 'ticker': 'SOL'},
                    'DOTUSDT': {'name': 'Polkadot', 'ticker': 'DOT'},
                    'LTCUSDT': {'name': 'Litecoin', 'ticker': 'LTC'},
                    'LINKUSDT': {'name': 'Chainlink', 'ticker': 'LINK'}
                }
                
                binance_data = []
                
                for coin in data:
                    if coin['symbol'] in popular_coins:
                        coin_info = popular_coins[coin['symbol']]
                        binance_data.append({
                            'name': coin_info['name'],
                            'ticker': coin_info['ticker'],
                            'price': float(coin['price']),
                            'currency': 'USDT'
                        })
                        callback(f"📊 Найдена криптовалюта: {coin_info['name']} ({coin_info['ticker']})")
                        sleep(0.3)
                
                callback("✅ Данные успешно получены!")
                sleep(1)
                return binance_data
            else:
                callback(f"❌ Ошибка: HTTP {result.status_code}")
                return None
                
        except Exception as e:
            callback(f"❌ Ошибка при получении данных: {e}")
            return None
    
    def get_coingecko_data(self, callback):
        """Получаем данные с CoinGecko"""
        try:
            callback("🔄 Подключаемся к CoinGecko API...")
            sleep(1)
            
            url = 'https://api.coingecko.com/api/v3/coins/markets'
            params = {
                'vs_currency': 'usd',
                'ids': 'bitcoin,ethereum,bnb,cardano,ripple,dogecoin,solana,polkadot,litecoin,chainlink',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false'
            }
            
            result = requests.get(url, params=params, timeout=15)
            
            if result.status_code == 200:
                callback("✅ Подключение успешно! Обрабатываем данные...")
                sleep(1)
                
                data = result.json()
                coin_names = {
                    'bitcoin': 'Bitcoin',
                    'ethereum': 'Ethereum',
                    'bnb': 'Binance Coin',
                    'cardano': 'Cardano',
                    'ripple': 'Ripple',
                    'dogecoin': 'Dogecoin',
                    'solana': 'Solana',
                    'polkadot': 'Polkadot',
                    'litecoin': 'Litecoin',
                    'chainlink': 'Chainlink'
                }
                
                coingecko_data = []
                
                for coin in data:
                    coin_name = coin_names.get(coin['id'], coin['id'].capitalize())
                    coingecko_data.append({
                        'name': coin_name,
                        'ticker': coin['symbol'].upper(),
                        'price': coin['current_price'],
                        'currency': 'USD'
                    })
                    callback(f"📊 {coin_name} ({coin['symbol'].upper()}): ${coin['current_price']}")
                    sleep(0.3)
                
                callback("✅ Данные успешно получены!")
                sleep(1)
                return coingecko_data
            else:
                callback(f"❌ Ошибка: HTTP {result.status_code}")
                return None
                
        except Exception as e:
            callback(f"❌ Ошибка при получении данных: {e}")
            return None
    
    def get_cryptocompare_data(self, callback):
        """Получаем данные с CryptoCompare"""
        try:
            callback("🔄 Подключаемся к CryptoCompare API...")
            sleep(1)
            
            url = 'https://min-api.cryptocompare.com/data/pricemulti'
            params = {
                'fsyms': 'BTC,ETH,BNB,ADA,XRP,DOGE,SOL,DOT,LTC,LINK',
                'tsyms': 'USD'
            }
            
            result = requests.get(url, params=params, timeout=10)
            
            if result.status_code == 200:
                callback("✅ Подключение успешно! Обрабатываем данные...")
                sleep(1)
                
                data = result.json()
                coin_names = {
                    'BTC': 'Bitcoin',
                    'ETH': 'Ethereum',
                    'BNB': 'Binance Coin',
                    'ADA': 'Cardano',
                    'XRP': 'Ripple',
                    'DOGE': 'Dogecoin',
                    'SOL': 'Solana',
                    'DOT': 'Polkadot',
                    'LTC': 'Litecoin',
                    'LINK': 'Chainlink'
                }
                
                cryptocompare_data = []
                
                for coin, price_data in data.items():
                    cryptocompare_data.append({
                        'name': coin_names.get(coin, coin),
                        'ticker': coin,
                        'price': price_data['USD'],
                        'currency': 'USD'
                    })
                    callback(f"📊 {coin_names.get(coin, coin)} ({coin}): ${price_data['USD']}")
                    sleep(0.3)
                
                callback("✅ Данные успешно получены!")
                sleep(1)
                return cryptocompare_data
            else:
                callback(f"❌ Ошибка: HTTP {result.status_code}")
                return None
                
        except Exception as e:
            callback(f"❌ Ошибка при получении данных: {e}")
            return None

class APIWindow:
    def __init__(self, parent, api_name, api_function):
        self.parent = parent
        self.api_name = api_name
        self.api_function = api_function
        self.data = None
        
        self.setup_window()
        self.start_data_loading()
    
    def setup_window(self):
        """Настройка окна API"""
        main_frame = ttk.Frame(self.parent, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text=f"{self.api_name} - Получение данных", 
                               font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 15))
        
        # Область процесса
        ttk.Label(main_frame, text="Процесс:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.process_text = scrolledtext.ScrolledText(main_frame, width=70, height=6, 
                                                    font=('Consolas', 9), state='disabled')
        self.process_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Область результатов с таблицей
        ttk.Label(main_frame, text="Результаты:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        # Создаем фрейм для таблицы
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Создаем Treeview для таблицы
        self.tree = ttk.Treeview(table_frame, columns=('name', 'ticker', 'price', 'currency'), 
                               show='headings', height=12)
        
        # Настраиваем колонки
        self.tree.heading('name', text='Название')
        self.tree.heading('ticker', text='Тикер')
        self.tree.heading('price', text='Курс')
        self.tree.heading('currency', text='Валюта')
        
        self.tree.column('name', width=150, anchor='w')
        self.tree.column('ticker', width=80, anchor='center')
        self.tree.column('price', width=120, anchor='e')
        self.tree.column('currency', width=80, anchor='center')
        
        # Добавляем scrollbar для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопка закрытия
        close_btn = ttk.Button(main_frame, text="Закрыть", command=self.parent.destroy)
        close_btn.grid(row=6, column=0, pady=10)
        
        # Настройка растягивания
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def update_process(self, message):
        """Обновление области процесса"""
        self.process_text.config(state='normal')
        self.process_text.insert(tk.END, f"{message}\n")
        self.process_text.see(tk.END)
        self.process_text.config(state='disabled')
    
    def start_data_loading(self):
        """Запуск загрузки данных"""
        self.progress.start(10)
        thread = Thread(target=self.load_data)
        thread.daemon = True
        thread.start()
    
    def load_data(self):
        """Загрузка данных в отдельном потоке"""
        try:
            # Передаем callback функцию для обновления процесса
            self.data = self.api_function(self.update_process)
            self.parent.after(0, self.display_results)
            
        except Exception as e:
            self.parent.after(0, self.update_process, f"❌ Критическая ошибка: {e}")
        finally:
            self.parent.after(0, self.stop_progress)
    
    def display_results(self):
        """Отображение результатов в таблице"""
        if self.data:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Заполняем таблицу данными
            for coin_data in self.data:
                self.tree.insert('', 'end', values=(
                    coin_data['name'],
                    coin_data['ticker'],
                    f"{coin_data['price']:,.2f}",
                    coin_data['currency']
                ))
            
            self.update_process(f"✅ Таблица заполнена: {len(self.data)} записей")
        else:
            self.update_process("❌ Не удалось получить данные для таблицы")
    
    def stop_progress(self):
        """Остановка прогресс бара"""
        self.progress.stop()

def main():
    """Основная функция программы"""
    root = tk.Tk()
    app = CryptoPriceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()