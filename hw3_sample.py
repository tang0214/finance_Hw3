import ccxt
import pandas as pd
import time

# 初始化 OKX 交易所，启用 sandbox 模式
okx = ccxt.okx({
    'apiKey': '',
    'secret': '',
    'password': '',
    'enableRateLimit': True,
})

"""隨便你策略怎麼寫，但一定要一定要一定要加這一行，這是使用模擬交易模式-----------------------------------------------------------------------------------------------------------"""

okx.set_sandbox_mode(True)  

"""-------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


symbol = 'BTC/USDT'
timeframe = '1h'  # 時間週期1HR
ma_period = 7  # MA7

def fetch_ohlcv(symbol, timeframe):
    """拿歷史資料"""
    ohlcv = okx.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_ma(df, period):
    """計算MA"""
    df['MA'] = df['close'].rolling(window=period).mean()
    return df

def get_latest_signal(df):
    """根據MA生成信號"""
    if df['close'].iloc[-1] > df['MA'].iloc[-1]:
        return 'buy'
    elif df['close'].iloc[-1] < df['MA'].iloc[-1]:
        return 'sell'
    else:
        return 'hold'

def execute_trade(signal, symbol):
    """根據信號進行操作"""
    balance = okx.fetch_balance()
    usdt_balance = balance['total'].get('USDT', 0)  
    btc_balance = balance['total'].get('BTC', 0)  

    print(f"當前 USDT 餘額: {usdt_balance}")
    print(f"當前 BTC 餘額: {btc_balance}")

    if signal == 'buy':  #買入
        if usdt_balance > 10:  
            order = okx.create_market_buy_order(symbol, usdt_balance / okx.fetch_ticker(symbol)['last'])
            print(f"買入: {order}")
        else:
            print("USDT餘額不足，無法執行買入操作。")
    
    elif signal == 'sell': #賣出
        if btc_balance > 0.001:  
            order = okx.create_market_sell_order(symbol, btc_balance)
            print(f"賣出: {order}")
        else:
            print("BTC餘額不足，無法執行賣出操作。")
    else:
        print("持有：不執行任何操作。")

def main():
    """持續監控市場及交易"""
    while True:
        df = fetch_ohlcv(symbol, timeframe)
        df = calculate_ma(df, ma_period)
        signal = get_latest_signal(df)
        print(f"最新信號: {signal}")
        execute_trade(signal, symbol)
        time.sleep(60)  # 一小時檢查一次

if __name__ == "__main__":
    main()


