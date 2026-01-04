import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from web3 import Web3

# --- МИНИ-СЕРВЕР ДЛЯ RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# --- ЛОГИКА СКАНЕРА ---
RPC_URL = os.environ.get('POLYGON_RPC', "https://polygon-rpc.com")

def scan_logic():
    print(f"Попытка подключения к RPC: {RPC_URL}")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # Ждем подключения
    for i in range(5):
        if w3.is_connected():
            break
        print("Ожидание подключения к сети...")
        time.sleep(5)

    if not w3.is_connected():
        print("КРИТИЧЕСКАЯ ОШИБКА: Нет связи с блокчейном!")
        return

    print(f"СВЯЗЬ УСТАНОВЛЕНА. Блок: {w3.eth.block_number}")
    
    # Адреса (WMATIC/USDC)
    QUICK_ROUTER = "0xa5E0829CaCEd4fFDD63873453b1af510AD6C34f4"
    SUSHI_ROUTER = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
    WMATIC = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    ABI = '[{"inputs":[{"type":"uint256","name":"amountIn"},{"type":"address[]","name":"path"}],"name":"getAmountsOut","outputs":[{"type":"uint256[]","name":"amounts"}],"stateMutability":"view","type":"function"}]'
    
    quick_contract = w3.eth.contract(address=w3.to_checksum_address(QUICK_ROUTER), abi=ABI)
    sushi_contract = w3.eth.contract(address=w3.to_checksum_address(SUSHI_ROUTER), abi=ABI)

    while True:
        try:
            amount_in = 1000 * 10**6 # 1000 USDC
            # Симулируем: Quick -> Sushi
            out_q = quick_contract.functions.getAmountsOut(amount_in, [USDC, WMATIC]).call()[1]
            back_s = sushi_contract.functions.getAmountsOut(out_q, [WMATIC, USDC]).call()[1]
            
            profit = (back_s - amount_in) / 10**6
            print(f"[LIVE SCAN] Спред USDC: {profit}$")
        except Exception as e:
            print(f"Ошибка запроса: {e}")
        
        time.sleep(15)

if __name__ == "__main__":
    # Запускаем сервер проверки здоровья в отдельном потоке
    threading.Thread(target=run_health_server, daemon=True).start()
    # Запускаем сканер
    scan_logic()
