from trader import QuantitativeTrader
from SimpleTrader import SimpleTrader
from BaseTrader import BaseTrader, StockData
from PerfectTrader import PerfectTrader
from OldTrader import OldTrader



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

semiConductor = StockData(semi_id, 2024)  # 假设股票ID为"512480"，天数从0到99
# semiConductor.draw_data(2022)
# exit()
base_trader = BaseTrader(initial_balance)
perfect_trader = PerfectTrader(initial_balance)
old_trader = OldTrader(initial_balance)
data_size = semiConductor.get_trade_day()

for i in range(0, data_size):
    cur_price = semiConductor.get_data_by_day_id(i)  # 获取当前价格
    # base_trader.trade("512480", cur_price, strategy='simple') 
    # perfect_trader.trade("512480", cur_price)
    old_trader.trade("512480", cur_price)  

# perfect_trader.perfect_strategy("512480")  # 执行完所有的交易后，调用完美策略
old_trader.buy_sell_graph()  # 打印当前总资产
old_trader.check_balance()
