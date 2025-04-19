from utils import round_shares, get_stock_info, sell_fee

"""
进行了一定的抽象：
- 非常简单的策略
"""


class SimpleTrader:
    def __init__(self, initial_balance):
        """
        初始化量化交易者
        :param initial_balance: 初始资金额度
        """
        self.balance = initial_balance  # 可用资金
        self.holdings = {}  # 持有的股票信息 list，list 内格式为 {stock_id: {'price': buy_price, 'shares': shares, 'can_sell': can_sell}}
        self.day_id = 0  # 当前天数
        self.traded = False  # 是否交易过

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
        """
        买入股票
        :param stock_id: 股票ID
        :param amount: 买入金额
        """
        holding = self.holdings.get(stock_id, None)
        buy_price = get_stock_info(stock_id, self.day_id)  # 获取当前价格
        buy_share = round_shares(amount / buy_price)  # 计算购买份数
        # 计算买入实际金额
        buy_amount = buy_share * buy_price

        if buy_amount > self.balance:# 一般来说是不会发生的
            print("余额不足，无法买入")
            return
        if holding:
            # 如果已经持有该股票，则更新持有信息
            holding['price'] = (holding['price'] * holding['shares'] + buy_amount) / (holding['shares'] + buy_share)
            holding['shares'] += buy_share
        else:
            # 如果没有持有该股票，则添加新的持有信息
            self.holdings[stock_id] = {'price': buy_price, 'shares': buy_share, 'can_sell': True}
        self.balance -= buy_amount  # 扣除买入金额
        self.traded = True  # 标记为已交易
        print("Day:", self.day_id, "| 买入", stock_id, "| 数量", buy_share, "| 价格", buy_price, "| 剩余资金", self.balance)

    def sell(self, stock_id, share_ratio):
        holding = self.holdings.get(stock_id, None)
        sold_shares = round_shares(holding['shares'] * share_ratio)
        if sold_shares > holding['shares'] or sold_shares == 0:
            return  # 如果没有可卖出的股票，则返回

        if holding:
            # 卖出持有的股票
            self.traded = True  # 标记为已交易
            sell_price = get_stock_info(stock_id, self.day_id)
            holding['shares'] -= sold_shares
            get_money = sold_shares * sell_price
            self.balance += (get_money - sell_fee(get_money))  # 扣除手续费
            print("Day:", self.day_id, "| 卖出", stock_id, "| 数量", sold_shares, "| 价格", sell_price, "| 剩余资金：", self.balance)
        else:
            print("没有持有该股票，无法卖出")
            

    def all_balance(self):
        """
        计算当前总资产
        :return: 当前总资产
        """
        total_value = self.balance
        for stock_id in self.holdings.keys():
            holding = self.holdings[stock_id]
            total_value += holding['shares'] * get_stock_info(stock_id, self.day_id)  # 获取当前价格
        return total_value
    
    def check_balance(self):
        """
        计算当前总资产
        :return: 当前总资产
        """
        total_value = self.balance
        for stock_id in self.holdings.keys():
            holding = self.holdings[stock_id]
            total_value += holding['shares'] * get_stock_info(stock_id, self.day_id)  # 获取当前价格
            print(self.day_id, stock_id, holding['shares'], holding['price'], get_stock_info(stock_id, self.day_id))
        print(f"Day: {self.day_id} | 当前总资产: {total_value} | 可用资金: {self.balance}")


