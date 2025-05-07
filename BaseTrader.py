import pandas as pd
from utils import round_shares, sell_fee

"""
进行了一定的抽象：
- 非常简单的策略
"""


class BaseTrader:
    def __init__(self, initial_balance):
        """
        初始化量化交易者
        :param initial_balance: 初始资金额度
        """
        self.balance = initial_balance  # 可用资金
        self.holdings = {}  # 持有的股票信息 list，list 内格式为 {stock_id: {'price': buy_price, 'shares': shares, 'can_sell': can_sell}}
        self.day_id = 0  # 当前天数
        # self.working_year = working_year
        self.cur_price = 0  # 当前价格
        self.last_price = 0  # 上一个价格
        self.traded = False  # 是否交易过
        self.balance_history = []  # 记录每一天的总资产变化
        self.trade_history = []  # 记录每一天的交易情况 内部为 [+-share, amount, price]

    def trade(self, stock_id, cur_price, strategy='simple'):
        """
        根据策略进行交易
        :param stock_id: 股票ID
        :param day_id: 天数
        :param strategy: 交易策略，默认为简单策略
        """
        self.day_id += 1  # 更新当前天数
        self.last_price = self.cur_price
        self.cur_price = cur_price  # 更新当前价格
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': cur_price, 'shares': 0, 'can_sell': True}
        if strategy == 'simple':
            self.simple_strategy(stock_id, buy_ration=0.1, sell_ration=0.4)
        
        self.balance_history.append(self.all_balance())  # 记录总资产变化
        

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
        if self.last_price == 0:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
            return  # 如果没有上一个价格，则返回
        if self.holdings[stock_id]["shares"] == 0: 
            # ! 建仓只需要有一个降低的条件就行了
            last_price = self.last_price
            if last_price > self.cur_price:
                self.buy(stock_id, buy_ration * self.balance)  # 买入底仓
            else:
                self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
        else: # ! 有仓位的更新
            last_price = self.holdings[stock_id]["price"]  # 获取自己的持仓成本价格
            current_price = self.cur_price  # 获取当前价格
            if last_price*sell_factor <= current_price:# ! 说明涨了
                self.sell(stock_id, sell_ration)  # 卖出10%的持有量
            elif last_price*buy_factor > current_price:  # ! 说明跌了
                self.buy(stock_id, buy_ration * self.balance)
            else:
                self.trade_history.append([self.day_id, 0, 0, self.cur_price])

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
        buy_price = self.cur_price  # 获取当前价格
        buy_share = round_shares(amount / buy_price)  # 计算购买份数
        # 计算买入实际金额
        buy_amount = buy_share * buy_price

        if buy_amount > self.balance:# 一般来说是不会发生的
            # print("余额不足，无法买入")
            # print("Day:", self.day_id, "| 买入", stock_id, "| 数量", buy_share, "| 价格", buy_price, "| 剩余资金", self.balance)
            self.trade_history.append([self.day_id, 0, 0, buy_price])  # 记录交易情况
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
        self.trade_history.append([self.day_id, buy_share, buy_amount, buy_price])  # 记录交易情况

    def sell(self, stock_id, share_ratio):
        holding = self.holdings.get(stock_id, None)
        sold_shares = round_shares(holding['shares'] * share_ratio)
        if sold_shares > holding['shares'] or sold_shares == 0:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
            return  # 如果没有可卖出的股票，则返回

        if holding:
            # 卖出持有的股票
            self.traded = True  # 标记为已交易
            sell_price = self.cur_price
            holding['shares'] -= sold_shares
            get_money = sold_shares * sell_price
            self.balance += (get_money - sell_fee(get_money))  # 扣除手续费
            print("Day:", self.day_id, "| 卖出", stock_id, "| 数量", sold_shares, "| 价格", sell_price, "| 剩余资金：", self.balance)
            self.trade_history.append([self.day_id, -sold_shares, get_money, sell_price])  # 记录交易情况
        else:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
            print("没有持有该股票，无法卖出")
            

    def all_balance(self):
        """
        计算当前总资产
        :return: 当前总资产
        """
        total_value = self.balance
        for stock_id in self.holdings.keys():
            holding = self.holdings[stock_id]
            total_value += holding['shares'] * self.cur_price  # 获取当前价格
        return total_value
    
    def buy_sell_graph(self):
        """
        将所有买卖情况画到图上
        """
        import matplotlib.pyplot as plt

        # 提取交易数据
        days = [trade[0] for trade in self.trade_history]

        prices = [trade[3] for trade in self.trade_history]

        # 绘制买入和卖出情况
        plt.figure(figsize=(24, 6))
        plt.plot(days, prices, label='Price', color='blue')
        for op in self.trade_history:
            if op[1] > 0:
                plt.scatter(op[0], op[3], color='red', marker='.', s =30)
            elif op[1] < 0:
                plt.scatter(op[0], op[3], color='blue', marker='.', s=30)

        plt.title('Buy and Sell History')
        plt.xlabel('Day')
        plt.ylabel('Shares')
        plt.grid()
        plt.legend()
        plt.show()


    def draw_balance(self):
        """
        绘制当前总资产变化图
        :return: None
        """
        import matplotlib.pyplot as plt

        # 计算总资产
        x = range(len(self.balance_history))
        # print(self.trade_history)
        init_price = self.trade_history[0][-1]  # 获取初始价格

        y = [100000 *_[-1]/init_price for _ in self.trade_history]
        plt.figure(figsize=(12, 6))
        

        # 绘制图形
        plt.plot(x, self.balance_history, label='strategy', color='blue')
        plt.plot(x, y, label='market', color='red')
        plt.title('Total Asset Value')
        plt.xlabel('Day')
        plt.ylabel('Total Value')
        plt.grid()
        plt.legend()
        plt.show()
    
    def check_balance(self):
        """
        计算当前总资产
        :return: 当前总资产
        """
        total_value = self.balance
        for stock_id in self.holdings.keys():
            holding = self.holdings[stock_id]
            total_value += holding['shares'] * self.cur_price  # 获取当前价格
            print(self.day_id, stock_id, holding['shares'], holding['price'], self.cur_price)
        print(f"Day: {self.day_id} | 当前总资产: {total_value} | 可用资金: {self.balance}")

    def calculate_max_drawdown(self):
        """
        计算给定净值序列的最大回撤。
        
        :param values: 净值序列，可以是一个list或numpy数组。
        :return: 最大回撤率（百分比形式）
        """
        values = self.balance_history
        peak = values[0]
        max_drawdown = 0.0
        
        for value in values:
            if value > peak:
                peak = value  # 更新峰值
            drawdown = (peak - value) / peak  # 计算当前回撤
            if drawdown > max_drawdown:
                max_drawdown = drawdown  # 更新最大回撤
                
        return max_drawdown * 100 



class StockData:
    def __init__(self, stock_id, year):
        self.stock_id = stock_id
        self.year = year
        # self.data = pd.read_excel(f'./{stock_id}/{year}.xlsx')
        self.data = pd.DataFrame()
        self.try_get_data(stock_id)

    
    def get_data_by_day_id(self, day:str):
        filtered_df = self.data[self.data['year'] == self.year]
        return filtered_df.iloc[day]["close"]
    
    def get_volume_by_day_id(self, day:str):
        filtered_df = self.data[self.data['year'] == self.year]
        return filtered_df.iloc[day]["vol"]
    
    def get_trade_day(self):
        """
        获取本年交易日数量
        """
        filtered_df = self.data[self.data['year'] == self.year]
        # print(filtered_df)
        return filtered_df.shape[0]  # 返回行数，即交易日数量
    
    def draw_data(self, year:int):
        """
        绘制数据
        :param stock_id: 股票ID
        :param year: 年份
        """
        import matplotlib.pyplot as plt

        # 读取数据
        df = self.data[self.data['year'] == self.year]

        index_list = range(self.get_trade_day())
        
        # 绘制收盘价曲线
        plt.figure(figsize=(12, 6))
        plt.plot(index_list, df['close'])
        plt.title(f'{self.stock_id} {year} close price')
        plt.xlabel('day index')
        plt.ylabel('close price')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def download_data(self, stock_id:str):
        """
        下载数据: 获得 8k 条数据
        ! 请注意确认是否是沪还是深
        """
        from pytdx.hq import TdxHq_API
        api=TdxHq_API()
        data = []

        with api.connect('111.229.247.189', 7709):
            print("连接成功")
            for i in range(10):
                data+=api.get_security_bars(9, 1, stock_id, (9-i)*800, 800)
        df = api.to_df(data)

        # 保存为 Excel 文件
        df.to_excel(stock_id + '.xlsx', index=False)
    
    def try_get_data(self, stock_id:str):
        """
        尝试获取数据
        :param stock_id: 股票ID
        :param year: 年份
        """
        try:
        # 尝试读取本地文件
            self.data = pd.read_excel(f'./{stock_id}.xlsx')
            print(f"成功加载本地数据: {stock_id}.xlsx")
        except FileNotFoundError:
            # 如果文件不存在，则下载数据
            print(f"本地数据文件 {stock_id}.xlsx 不存在，尝试下载数据...")
            self.download_data(stock_id)
            self.data = pd.read_excel(f'./{stock_id}.xlsx')
            print(f"成功下载并加载数据: {stock_id}.xlsx")
        except Exception as e:
            print(f"获取数据失败: {e}")
        
