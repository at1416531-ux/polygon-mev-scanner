import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from web3 import Web3

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner is running")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- ЛОГИКА ---
RPC_URL = os.environ.get('POLYGON_RPC', "https://polygon-rpc.com")

def scan_logic():
    print(f"INIT: Connecting to RPC: {RPC_URL}", flush=True)
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("FATAL: RPC Connection Failed", flush=True)
        return

    print(f"SUCCESS: Connected. Block: {w3.eth.block_number}", flush=True)

    # Контракты Роутеров
    QUICK_ROUTER = w3.to_checksum_address("0xa5E0829CaCEd4fFDD63873453b1af510AD6C34f4")
    SUSHI_ROUTER = w3.to_checksum_address("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506")
    
    # Токены
    USDC = w3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    WMATIC = w3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")

    # Уточненный ABI
    ABI = '[{"constant":true,"inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"name":"amounts","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"}]'
    
    quick_contract = w3.eth.contract(address=QUICK_ROUTER, abi=ABI)
    sushi_contract = w3.eth.contract(address=SUSHI_ROUTER, abi=ABI)

    while True:
        try:
            amount_in = 1000 * 10**6 # 1000 USDC
            
            # Запрос QuickSwap
            amounts_q = quick_contract.functions.getAmountsOut(amount_in, [USDC, WMATIC]).call()
            out_q = amounts_q[1]
            
            # Запрос SushiSwap
            amounts_s = sushi_contract.functions.getAmountsOut(out_q, [WMATIC, USDC]).call()
            back_s = amounts_s[1]
            
            profit = (back_s - amount_in) / 10**6
            print(f"[SCAN] USDC -> MATIC -> USDC | Profit: {profit:.4f}$", flush=True)
            
        except Exception as e:
            print(f"RPC_LIMIT_OR_ERROR: Попробуй сменить RPC на Alchemy. Ошибка: {str(e)[:50]}...", flush=True)
        
        time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    scan_logic()
