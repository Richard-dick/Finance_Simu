import pandas as pd

"""
进行了一定的抽象：
- 暂时忽略的交易费率
- 暂时忽略了买卖必须要有100股为基础的限制
- 暂时忽略
- 非常简单的策略

"""


class QuantitativeTrader:
    def __init__(self, initial_balance):
        """
        初始化量化交易者
        :param initial_balance: 初始资金额度
        """
        self.balance = initial_balance  # 可用资金
        self.holdings = {}  # 持有的股票信息 list，list 内格式为 {stock_id: {'price': buy_price, 'shares': shares, 'can_sell': can_sell}}
        self.day_id = 0  # 当前天数

    def trade(self, stock_id, day_id, strategy='simple'):
        """
        根据策略进行交易
        :param stock_id: 股票ID
        :param day_id: 天数
        :param strategy: 交易策略，默认为简单策略
        """
        self.day_id = day_id  # 更新当前天数
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': self.get_stock_info(stock_id, 0), 'shares': 0, 'can_sell': True}
        if strategy == 'simple':
            self.simple_strategy(stock_id, buy_ration=0.2, sell_ration=0.5)

    def simple_strategy(self, stock_id, buy_ration, sell_ration, buy_factor = 0.95, sell_factor = 1.05):
        """
        简单的交易策略：对于 stock_id 股票，判断当前价格与持仓价格的关系，决定买入或卖出
        :param stock_id: 股票ID
        :param buy_factor: 买入因子 <= 1，当前价格 < 持仓价格*buy_factor,  说明跌了挺多的 买入 buy_ration
        :param sell_factor: 卖出因子>= 1，当前价格 > 持仓价格*sell_factor, 说明涨了挺多的 卖出 sell_ration
        :param buy_ration: 买入比例
        :param sell_ration: 卖出比例
        """
        last_price = self.holdings[stock_id]["price"]  # 获取自己的持仓成本价格
        current_price = self.get_stock_info(stock_id, self.day_id)  # 获取当前价格
        if last_price*sell_factor < current_price:# ! 说明涨了
            self.sell(stock_id, sell_ration)  # 卖出10%的持有量
        elif last_price*buy_factor > current_price:  # ! 说明跌了
            self.buy(stock_id, buy_ration * self.balance)
            self.balance -= buy_ration * self.balance  # 扣除买入金额

    def get_stock_info(self, stock_id:int, day_id:int):
        file_path = stock_id + '-2024.xlsx'
        data = pd.read_excel(file_path)
        return data.iloc[day_id]["close"]  # 返回指定日期的收盘价
        
    def buy(self, stock_id, amount):
        buy_price = self.get_stock_info(stock_id, self.day_id)  # 获取当前价格
        # 检查是否已经持有该股票
        holding = self.holdings.get(stock_id, None)
        if holding:
            # 如果已经持有该股票，则更新持有信息
            holding['price'] = (holding['price'] * holding['shares'] + amount) / (holding['shares'] + amount / buy_price)
            holding['shares'] += amount / buy_price
        print("Day:", self.day_id, "| 买入股票", stock_id, "| 数量", amount / buy_price, "| 价格", buy_price, "| 剩余资金", self.balance)

    def sell(self, stock_id, share_ratio):
        holding = self.holdings.get(stock_id, None)
        if holding:
            # 卖出持有的股票
            sell_price = self.get_stock_info(stock_id, self.day_id)
            sold_shares = holding['shares'] * share_ratio
            holding['shares'] -= sold_shares
            get_money = sold_shares * sell_price
            self.balance += get_money
            print("Day:", self.day_id, "| 卖出股票", stock_id, "| 数量", sold_shares, "| 价格", sell_price, "| 剩余资金：", self.balance)
    

    def buy_fee(amount):
        """
        计算买入手续费
        :param amount: 买入金额
        :return: 手续费
        """
        return max(amount * 0.0001, 5) + amount*0.00001 


    def all_balance(self):
        """
        计算当前总资产
        :return: 当前总资产
        """
        total_value = self.balance
        for stock_id in self.holdings.keys():
            holding = self.holdings[stock_id]
            total_value += holding['shares'] * self.get_stock_info(stock_id, self.day_id)  # 获取当前价格
        print(f"Day: {self.day_id} | 当前总资产: {total_value} | 可用资金: {self.balance} | 持有股票: {self.holdings}")



# 示例使用
initial_balance = 100000  # 初始资金额度
trader = QuantitativeTrader(initial_balance)

day_bound = 100  # 假设有100天的数据

# 模拟股票价格变动
for i in range(1, day_bound):
    trader.trade("512480", i)  # 假设股票ID为"512480"，天数从0到99

trader.all_balance()  # 打印当前总资产