from trader import QuantitativeTrader
# 示例使用
initial_balance = 100000  # 初始资金额度
trader = QuantitativeTrader(initial_balance)

day_bound = 100  # 假设有100天的数据

# 模拟股票价格变动
for i in range(1, day_bound):
    trader.trade("512480", i)  # 假设股票ID为"512480"，天数从0到99

trader.all_balance()  # 打印当前总资产