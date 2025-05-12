from trader import QuantitativeTrader
# from SimpleTrader import SimpleTrader
from BaseTrader import BaseTrader, StockData
from PerfectTrader import PerfectTrader
from OldTrader import OldTrader
from EnhancedTrader import EnhancedTrader
from RFtrader import RFtrader



# 示例使用
initial_balance = 100000  # 初始资金额度
semi_id = "512480"  # 半导体 etf 有涨有跌
gold_id = "518880"  # 黄金 etf   猛猛涨
volt_id = "515790"  # 光伏 etf   猛猛跌

# trader = SimpleTrader(initial_balance)

# day_start = 0
# day_bound = 242  # 假设有100天的数据

# # 模拟股票价格变动
# for i in range(day_start, day_bound):
#     trader.trade("512480", i, strategy='ma5')  # 假设股票ID为"512480"，天数从0到99

# trader.all_balance()  # 打印当前总资产

# semiConductor.draw_data(2022)
# exit()
base_trader = BaseTrader(initial_balance)
perfect_trader = PerfectTrader(initial_balance)
old_trader = OldTrader(initial_balance)
enhancedTrader = EnhancedTrader(initial_balance)
rftrader = RFtrader(initial_balance)

# 按每个 etf
for stock_id in [semi_id]:
    # 累计三年的数据
    rftrader.load_stock(StockData(stock_id, 2021))
    rftrader.train()
    for year in [2022, 2023, 2024]:
        settedStock = StockData(stock_id, year)
        data_size = settedStock.get_trade_day()
        rftrader.load_stock(settedStock)
        # rftrader.train()
        # print(year)
        # print(data_size)
        # 获得该年的操作过程
        for i in range(0, data_size):
            cur_price = settedStock.get_data_by_day_id(i)
            cur_vol = settedStock.get_volume_by_day_id(i)
            # base_trader.trade(stock_id, cur_price, strategy='simple')  # 执行交易
            # old_trader.trade(stock_id, cur_price)  
            # enhancedTrader.trade(stock_id, cur_price, cur_vol, strategy='volume_price')  # 执行交易
            rftrader.trade(stock_id, cur_price, cur_day=i)
            # perfect_trader.trade(stock_id, cur_price)


# perfect_trader.perfect_strategy(stock_id) 

# base trader result
# base_trader.draw_balance()
# base_trader.check_balance()
# print(base_trader.calc_sharp_ratio())
# print(base_trader.calculate_max_drawdown())
            
# old result
# old_trader.draw_balance()
# old_trader.check_balance()
# print(old_trader.calc_sharp_ratio())
# print(old_trader.calculate_max_drawdown())       

# enhancedTrader result
# enhancedTrader.draw_balance() 
# enhancedTrader.check_balance()
# print(enhancedTrader.calc_sharp_ratio())
# print(enhancedTrader.calculate_max_drawdown())

# RF result
rftrader.draw_balance() 
rftrader.check_balance()
print(rftrader.calc_sharp_ratio())
print(rftrader.calculate_max_drawdown())

# PF result
# perfect_trader.draw_balance() 
# perfect_trader.check_balance()
# print(perfect_trader.calc_sharp_ratio())
# print(perfect_trader.calculate_max_drawdown())


# draw ALL

# import matplotlib.pyplot as plt

# # 六条线
# base_history = base_trader.balance_history
# x = range(len(base_history))
# old_history = old_trader.balance_history
# enhanced_history = enhancedTrader.balance_history
# rf_history = rftrader.balance_history
# perfect_history = perfect_trader.balance_history
# trade_history = base_trader.trade_history
# init_price = trade_history[0][-1]  # 获取初始价格
# y = [100000 *_[-1]/init_price for _ in trade_history]


# plt.figure(figsize=(12, 8))

# # 绘制图形
# plt.plot(x, base_history, label='Base', color='blue')
# plt.plot(x, old_history, label='Old', color='green')
# plt.plot(x, enhanced_history, label='Enhanced', color='orange')
# plt.plot(x, rf_history, label='RF', color='purple')
# # plt.plot(x, perfect_history, label='Perfect', color='brown')
# plt.plot(x, y, label='Market', color='red', linestyle='--')

# plt.title('Total Asset Value')
# plt.xlabel('Day')
# plt.ylabel('Total Value')
# plt.grid()
# plt.legend()
# plt.show()