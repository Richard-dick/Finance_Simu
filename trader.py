import pandas as pd
from utils import get_stock_info
from SimpleTrader import SimpleTrader

"""
进行了一定的抽象：
- 非常简单的策略
"""


class QuantitativeTrader(SimpleTrader):
    def __init__(self, initial_balance):
        super().__init__(initial_balance)  # 初始化父类

    def trade(self, stock_id, day_id, strategy='simple'):
        """
        根据策略进行交易
        :param stock_id: 股票ID
        :param day_id: 天数
        :param strategy: 交易策略，默认为简单策略
        """
        self.day_id = day_id  # 更新当前天数
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': get_stock_info(stock_id, 0), 'shares': 0, 'can_sell': True}
        if strategy == 'simple':
            self.simple_strategy(stock_id, buy_ration=0.2, sell_ration=0.4)
        

    def simple_strategy(self, stock_id, buy_ration, sell_ration, buy_factor = 0.95, sell_factor = 1.05):
        """
        简单的交易策略：对于 stock_id 股票，判断当前价格与持仓价格的关系，决定买入或卖出
        :param stock_id: 股票ID
        :param buy_factor: 买入因子 <= 1，当前价格 < 持仓价格*buy_factor,  说明跌了挺多的 买入 buy_ration
        :param sell_factor: 卖出因子>= 1，当前价格 > 持仓价格*sell_factor, 说明涨了挺多的 卖出 sell_ration
        :param buy_ration: 买入比例
        :param sell_ration: 卖出比例
        """
        # 如果持有该股票，则依赖持有价格进行对比交易，否则依赖过去一天的价格进行对比交易
        if self.holdings[stock_id]["shares"] == 0: 
            # ! 建仓只需要有一个降低的条件就行了
            last_price = get_stock_info(stock_id, self.day_id - 1)
            if last_price > get_stock_info(stock_id, self.day_id):
                self.buy(stock_id, buy_ration * self.balance)  # 买入底仓
        else: # ! 有仓位的更新
            last_price = self.holdings[stock_id]["price"]  # 获取自己的持仓成本价格
            current_price = get_stock_info(stock_id, self.day_id)  # 获取当前价格
            if last_price*sell_factor < current_price:# ! 说明涨了
                self.sell(stock_id, sell_ration)  # 卖出10%的持有量
            elif last_price*buy_factor > current_price:  # ! 说明跌了
                self.buy(stock_id, buy_ration * self.balance)

        
        if self.traded:
            self.traded = False
            self.check_balance()  # 打印当前总资产
        
    def buy(self, stock_id, amount):
        super().buy(stock_id, amount)  # 调用父类的买入方法

    def sell(self, stock_id, share_ratio):
        super().sell(stock_id, share_ratio)  # 调用父类的卖出方法

    def all_balance(self):
        return super().all_balance()  # 调用父类的方法
    
    def check_balance(self):
        super().check_balance()  # 调用父类的方法


