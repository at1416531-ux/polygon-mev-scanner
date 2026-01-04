from web3 import Web3
import time

# 1. ПОДКЛЮЧЕНИЕ К СЕТИ (Используй публичный RPC или Alchemy/Infura)
POLYGON_RPC = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

# 2. АДРЕСА РОУТЕРОВ (Глаза бота)
QUICK_ROUTER = "0xa5E0829CaCEd4fFDD63873453b1af510AD6C34f4"
SUSHI_ROUTER = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"

# 3. АДРЕСА ТОКЕНОВ
WMATIC = w3.to_checksum_address("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
USDC = w3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

# Минимальный интерфейс для получения цены
ABI = '[{"inputs":[{"uint256":"amountIn","address[]":"path"}],"name":"getAmountsOut","outputs":[{"uint256[]":"amounts"}],"stateMutability":"view","type":"function"}]'

quick_contract = w3.eth.contract(address=QUICK_ROUTER, abi=ABI)
sushi_contract = w3.eth.contract(address=SUSHI_ROUTER, abi=ABI)

def get_price(router_contract, amount_in, path):
    try:
        amounts = router_contract.functions.getAmountsOut(amount_in, path).call()
        return amounts[1]
    except:
        return 0

def scan():
    amount_to_test = 1000 * 10**6  # Тестируем на 1000 USDC
    path = [USDC, WMATIC]
    
    print("--- Сканирование Polygon на наличие арбитража ---")
    
    while True:
        price_quick = get_price(quick_contract, amount_to_test, path)
        price_sushi = get_price(sushi_contract, amount_to_test, path)
        
        if price_quick > 0 and price_sushi > 0:
            diff = abs(price_quick - price_sushi)
            # Если разница больше 0.5% (условно)
            if price_quick > price_sushi:
                print(f"Выгода! Quick дороже Sushi на {diff/10**18} MATIC")
            elif price_sushi > price_quick:
                print(f"Выгода! Sushi дороже Quick на {diff/10**18} MATIC")
            else:
                print("Цены равны. Ждем...")
        
        time.sleep(5) # Пауза 5 секунд между проверками

if __name__ == "__main__":
    scan()
