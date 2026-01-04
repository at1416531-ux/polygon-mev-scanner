import os
import time
import threading
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from web3 import Web3

# --- МИНИ-СЕРВЕР ДЛЯ RENDER (Health Check) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"SYSTEM: Health check server started on port {port}", flush=True)
    server.serve_forever()

# --- ЛОГИКА СКАНЕРА ---
RPC_URL = os.environ.get('POLYGON_RPC', "https://polygon-rpc.com")

def scan_logic():
    print(f"INIT: Connecting to RPC: {RPC_URL}", flush=True)
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # Попытка подключения
    if not w3.is_connected():
        print("CRITICAL: Connection failed! Checking connection...", flush=True)
        time.sleep(10)
    
    if w3.is_connected():
        print(f"SUCCESS: Connected to Polygon. Block: {w3.eth.block_number}", flush=True)
    else:
        print("FATAL: Could not connect to RPC. Check Environment Variables.", flush=True)
        return

    # Адреса (WMATIC/USDC)
    QUICK_ROUTER = w3.to_checksum_address("0xa5E0829CaCEd4fFDD63873453b1af510AD6C34f4")
    SUSHI_ROUTER = w3.to_checksum_address("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506")
    WMATIC = w3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
    USDC = w3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

    ABI = '[{"inputs":[{"type":"uint256","name":"amountIn"},{"type":"address[]","name":"path"}],"name":"getAmountsOut","outputs":[{"type":"uint256[]","name":"amounts"}],"stateMutability":"view","type":"function"}]'
    
    quick_contract = w3.eth.contract(address=QUICK_ROUTER, abi=ABI)
    sushi_contract = w3.eth.contract(address=SUSHI_ROUTER, abi=ABI)

    print("START: Scanning for arbitrage opportunities...", flush=True)

    while True:
        try:
            amount_in = 1000 * 10**6 # 1000 USDC
            
            # Запрос цен
            out_q = quick_contract.functions.getAmountsOut(amount_in, [USDC, WMATIC]).call()[1]
            back_s = sushi_contract.functions.getAmountsOut(out_q, [WMATIC, USDC]).call()[1]
            
            profit = (back_s - amount_in) / 10**6
            
            # Вывод результата
            status = "PROFIT!" if profit > 0 else "Watching..."
            print(f"[{status}] Spread: {profit:.4f}$ | MATIC out: {out_q/10**18:.2f}", flush=True)
            
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
        
        time.sleep(20) # Интервал 20 секунд для бесплатного RPC

if __name__ == "__main__":
    # Запуск сервера здоровья
    threading.Thread(target=run_health_server, daemon=True).start()
    # Запуск сканера
    scan_logic()
