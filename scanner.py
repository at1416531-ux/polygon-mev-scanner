def scan():
    loan_amount_usdc = 100000 * 10**6  # Симулируем заем в 100,000 USDC
    fee_aave = loan_amount_usdc * 0.0009 # Комиссия Aave 0.09%
    estimated_gas_cost_usd = 0.05 # Примерная цена газа в Polygon

    while True:
        # Получаем, сколько MATIC дадут за 100к USDC на обеих биржах
        matic_quick = get_price(quick_contract, loan_amount_usdc, [USDC, WMATIC])
        matic_sushi = get_price(sushi_contract, loan_amount_usdc, [USDC, WMATIC])

        if matic_quick > 0 and matic_sushi > 0:
            # Считаем обратный путь: сколько USDC получим обратно
            # Путь: Quick (купили MATIC) -> Sushi (продали MATIC за USDC)
            back_sushi = get_price(sushi_contract, matic_quick, [WMATIC, USDC])
            
            # Путь: Sushi (купили MATIC) -> Quick (продали MATIC за USDC)
            back_quick = get_price(quick_contract, matic_sushi, [WMATIC, USDC])

            best_return = max(back_sushi, back_quick)
            
            # РАСЧЕТ ПРИБЫЛИ
            gross_profit = (best_return - loan_amount_usdc) / 10**6
            net_profit = gross_profit - (fee_aave / 10**6) - estimated_gas_cost_usd

            if net_profit > 0:
                print(f"!!! НАЙДЕНА ВОЗМОЖНОСТЬ !!!")
                print(f"Чистая прибыль (симуляция): ${net_profit:.2f}")
            else:
                print(f"Мониторинг... Лучший исход: ${net_profit:.4f} (убыток из-за комиссий)")
        
        time.sleep(10)
