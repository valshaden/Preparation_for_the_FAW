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
# Deepseek

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
        self.root.title("Курсы криптовалют")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Инициализируем источники данных ДО setup_ui
        self.data_sources = {
            'Binance': self.get_binance_data,
            'CoinGecko': self.get_coingecko_data,
            'CryptoCompare': self.get_cryptocompare_data
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Курсы криптовалют", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Выбор API
        ttk.Label(main_frame, text="Выберите источник данных:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.api_var = tk.StringVar(value="Binance")
        api_combobox = ttk.Combobox(main_frame, textvariable=self.api_var, 
                                   values=list(self.data_sources.keys()), 
                                   state="readonly", width=15)
        api_combobox.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        # Кнопка получения данных
        self.get_data_btn = ttk.Button(main_frame, text="Получить данные", 
                                      command=self.get_data_threaded)
        self.get_data_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Область для вывода результатов
        ttk.Label(main_frame, text="Результаты:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.result_text = scrolledtext.ScrolledText(main_frame, width=70, height=20, 
                                                   font=('Consolas', 10))
        self.result_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Кнопка очистки
        clear_btn = ttk.Button(main_frame, text="Очистить", command=self.clear_results)
        clear_btn.grid(row=6, column=0, pady=10)
        
        # Кнопка сохранения
        save_btn = ttk.Button(main_frame, text="Сохранить в файл", command=self.save_to_file)
        save_btn.grid(row=6, column=1, pady=10)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def get_data_threaded(self):
        """Запуск получения данных в отдельном потоке"""
        self.get_data_btn.config(state='disabled')
        self.progress.start(10)
        self.result_text.insert(tk.END, f"Запрос данных от {self.api_var.get()}...\n")
        self.result_text.see(tk.END)
        
        thread = Thread(target=self.get_data)
        thread.daemon = True
        thread.start()
    
    def get_data(self):
        """Основная функция получения данных"""
        try:
            selected_api = self.api_var.get()
            data_function = self.data_sources[selected_api]
            data = data_function()
            
            self.root.after(0, self.display_results, data, selected_api)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Ошибка: {str(e)}")
        finally:
            self.root.after(0, self.stop_progress)
    
    def stop_progress(self):
        """Остановка прогресс бара"""
        self.progress.stop()
        self.get_data_btn.config(state='normal')
    
    def display_results(self, data, source_name):
        """Отображение результатов в текстовом поле"""
        if data:
            self.result_text.insert(tk.END, f"\n=== Данные от {source_name} ===\n")
            
            # Используем pprint для красивого форматирования
            pp = pprint.PrettyPrinter(indent=2)
            formatted_data = pp.pformat(data)
            
            self.result_text.insert(tk.END, formatted_data + "\n\n")
            self.result_text.insert(tk.END, f"Получено {len(data)} записей\n")
            self.result_text.insert(tk.END, "="*50 + "\n\n")
        else:
            self.result_text.insert(tk.END, f"Не удалось получить данные от {source_name}\n\n")
        
        self.result_text.see(tk.END)
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        messagebox.showerror("Ошибка", message)
        self.result_text.insert(tk.END, f"{message}\n\n")
        self.result_text.see(tk.END)
    
    def clear_results(self):
        """Очистить текстовое поле"""
        self.result_text.delete(1.0, tk.END)
    
    def save_to_file(self):
        """Сохранить результаты в файл"""
        try:
            content = self.result_text.get(1.0, tk.END)
            if content.strip():
                with open('crypto_prices.txt', 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успех", "Данные сохранены в файл 'crypto_prices.txt'")
            else:
                messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")
    
    def get_binance_data(self):
        """Получаем данные с Binance Public API"""
        try:
            symbols_url = 'https://api.binance.com/api/v3/ticker/price'
            result = requests.get(symbols_url, timeout=10)
            
            if result.status_code == 200:
                data = result.json()
                popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 
                               'DOGEUSDT', 'DOTUSDT', 'UNIUSDT', 'LTCUSDT', 'LINKUSDT']
                
                binance_data = {}
                for coin in data:
                    if coin['symbol'] in popular_coins:
                        binance_data[coin['symbol']] = float(coin['price'])
                
                return binance_data
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Binance: {e}")
    
    def get_coingecko_data(self):
        """Получаем данные с CoinGecko"""
        try:
            url = 'https://api.coingecko.com/api/v3/coins/markets'
            params = {
                'vs_currency': 'usd',
                'ids': 'bitcoin,ethereum,bnb,cardano,ripple,dogecoin,polkadot,uniswap,litecoin,chainlink',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false'
            }
            
            result = requests.get(url, params=params, timeout=10)
            
            if result.status_code == 200:
                data = result.json()
                coingecko_data = {}
                for coin in data:
                    coingecko_data[coin['symbol'].upper()] = {
                        'price': coin['current_price'],
                        'market_cap': coin['market_cap'],
                        'volume': coin['total_volume']
                    }
                
                return coingecko_data
            else:
                return None
                
        except Exception as e:
            raise Exception(f"CoinGecko: {e}")
    
    def get_cryptocompare_data(self):
        """Получаем данные с CryptoCompare"""
        try:
            url = 'https://min-api.cryptocompare.com/data/pricemulti'
            params = {
                'fsyms': 'BTC,ETH,BNB,ADA,XRP,DOGE,DOT,UNI,LTC,LINK',
                'tsyms': 'USD'
            }
            
            result = requests.get(url, params=params, timeout=10)
            
            if result.status_code == 200:
                data = result.json()
                cryptocompare_data = {}
                for coin, price_data in data.items():
                    cryptocompare_data[coin] = {
                        'price': price_data['USD'],
                        'source': 'CryptoCompare'
                    }
                
                return cryptocompare_data
            else:
                return None
                
        except Exception as e:
            raise Exception(f"CryptoCompare: {e}")

def main():
    """Основная функция программы"""
    root = tk.Tk()
    app = CryptoPriceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    