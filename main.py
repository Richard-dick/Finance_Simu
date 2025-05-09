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
for stock_id in [gold_id]:
    # 累计三年的数据
    rftrader.load_stock(StockData(stock_id, 2021))
    rftrader.train()
    for year in [2022, 2023, 2024]:
        settedStock = StockData(stock_id, year)
        data_size = settedStock.get_trade_day()
        rftrader.load_stock(settedStock)
        # rftrader.train()
        print(year)
        print(data_size)
        # 获得该年的操作过程
        for i in range(0, data_size):
            cur_price = settedStock.get_data_by_day_id(i)
            cur_vol = settedStock.get_volume_by_day_id(i)
            base_trader.trade(stock_id, cur_price, strategy='simple')  # 执行交易
            # perfect_trader.trade(stock_id, cur_price)
            # old_trader.trade(stock_id, cur_price)  
            # enhancedTrader.trade(stock_id, cur_price, cur_vol, strategy='volume_price')  # 执行交易
            rftrader.trade(stock_id, cur_price, cur_day=i)


# perfect_trader.perfect_strategy("512480")  # 执行完所有的交易后，调用完美策略
# base_trader.buy_sell_graph()
# base_trader.check_balance()
# print(base_trader.calc_sharp_ratio())

# enhancedTrader.buy_sell_graph() 
# enhancedTrader.check_balance()
# print(enhancedTrader.calc_sharp_ratio())
rftrader.buy_sell_graph() 
rftrader.check_balance()
print(rftrader.calc_sharp_ratio())
