import os
import time
import sys
from web3 import Web3

# 1. ПОДКЛЮЧЕНИЕ (Берем из настроек Render или используем запасной)
# В настройках Render (Environment) добавь POLYGON_RPC
RPC_URL = os.environ.get('POLYGON_RPC', "https://polygon-rpc.com")

def main():
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not w3.is_connected():
            print(f"ОШИБКА: Не удалось подключиться к RPC: {RPC_URL}")
            return

        print(f"Успешное подключение! Номер блока: {w3.eth.block_number}")

        # Адреса
        QUICK_ROUTER = w3.to_checksum_address("0xa5E0829CaCEd4fFDD63873453b1af510AD6C34f4")
        SUSHI_ROUTER = w3.to_checksum_address("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506")
        WMATIC = w3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
        USDC = w3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

        ABI = '[{"inputs":[{"type":"uint256","name":"amountIn"},{"type":"address[]","name":"path"}],"name":"getAmountsOut","outputs":[{"type":"uint256[]","name":"amounts"}],"stateMutability":"view","type":"function"}]'

        quick_contract = w3.eth.contract(address=QUICK_ROUTER, abi=ABI)
        sushi_contract = w3.eth.contract(address=SUSHI_ROUTER, abi=ABI)

        print("--- Начинаю симуляцию арбитража ---")

        while True:
            amount_in = 1000 * 10**6 # 1000 USDC
            
            try:
                # Прямой путь
                out_quick = quick_contract.functions.getAmountsOut(amount_in, [USDC, WMATIC]).call()[1]
                back_sushi = sushi_contract.functions.getAmountsOut(out_quick, [WMATIC, USDC]).call()[1]
                
                profit = (back_sushi - amount_in) / 10**6
                print(f"Цикл пройден. Результат: {profit}$")
                
            except Exception as e:
                print(f"Ошибка при запросе цен: {e}")
            
            time.sleep(15)

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА СИСТЕМЫ: {e}")

if __name__ == "__main__":
    main()
