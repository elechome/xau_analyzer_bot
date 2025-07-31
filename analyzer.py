import MetaTrader5 as mt5
import time
import json
from datetime import datetime

# โหลดการตั้งค่าจากไฟล์ settings.json
with open("settings.json") as f:
    settings = json.load(f)

symbol = settings["symbol"]
timeframe = settings["timeframe"]
period = settings["rsi_period"]
overbought = settings["rsi_overbought"]
oversold = settings["rsi_oversold"]
interval = settings["interval"]

# เชื่อมต่อ MT5
if not mt5.initialize():
    print("ไม่สามารถเชื่อมต่อ MT5:", mt5.last_error())
    quit()

print("เริ่มต้นการทำงานของระบบแจ้งเตือน RSI...")

try:
    while True:
        rates = mt5.copy_rates_from_pos(symbol, eval(timeframe), 0, 100)
        if rates is None or len(rates) < period:
            print("โหลดข้อมูลราคาล้มเหลว")
            time.sleep(interval)
            continue

        close_prices = [x.close for x in rates]
        deltas = [close_prices[i + 1] - close_prices[i] for i in range(len(close_prices) - 1)]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} | RSI = {rsi:.2f}")

        if rsi > overbought:
            print("⚠️ RSI Overbought! เตรียมพิจารณาขาย")
        elif rsi < oversold:
            print("🟢 RSI Oversold! เตรียมพิจารณาซื้อ")

        time.sleep(interval)

except KeyboardInterrupt:
    print("\nหยุดการทำงานของระบบตามคำสั่งผู้ใช้")

finally:
    mt5.shutdown()
