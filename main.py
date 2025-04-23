from trader import QuantitativeTrader
from SimpleTrader import SimpleTrader
from BaseTrader import BaseTrader, StockData



# 示例使用
initial_balance = 100000  # 初始资金额度


# trader = SimpleTrader(initial_balance)

# day_start = 0
# day_bound = 242  # 假设有100天的数据

# # 模拟股票价格变动
# for i in range(day_start, day_bound):
#     trader.trade("512480", i, strategy='ma5')  # 假设股票ID为"512480"，天数从0到99

# trader.all_balance()  # 打印当前总资产

semiConductor = StockData("512480", 2020)  # 假设股票ID为"512480"，天数从0到99
base_trader = BaseTrader(initial_balance)
data_size = semiConductor.get_trade_day()

for i in range(0, data_size):
    cur_price = semiConductor.get_data_by_day_id(i)  # 获取当前价格
    base_trader.trade("512480", cur_price, strategy='simple')  # 假设股票ID为"512480"，天数从0到99

base_trader.all_balance()  # 打印当前总资产
