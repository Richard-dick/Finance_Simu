from utils import round_shares, get_stock_info, sell_fee, get_moving_average, feature_extractor
from BaseTrader import BaseTrader

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

import matplotlib.pyplot as plt
import os

class RFtrader(BaseTrader):
    def __init__(self, initial_balance):
        """
        初始化量化交易者
        :param initial_balance: 初始资金额度
        """
        super().__init__(initial_balance)
        self.balance = initial_balance  # 可用资金
        self.holdings = {}  # 持有的股票信息 list，list 内格式为 {stock_id: {'price': buy_price, 'shares': shares, 'can_sell': can_sell}}
        self.day_id = 0  # 当前天数
        self.traded = False  # 是否交易过
        self.model = None
        self.stock_data = None
    
    def trade(self, stock_id, cur_price, cur_day, strategy='RF'):
        self.day_id += 1  # 更新当前天数
        self.last_price = self.cur_price
        self.cur_price = cur_price  # 更新当前价格
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': cur_price, 'shares': 0, 'can_sell': True}
        if strategy == 'RF':
            self.ml_strategy(stock_id=stock_id, model=self.model, cur_day=cur_day,
                                 buy_ration=0.2, sell_ration=0.4)
        
        self.balance_history.append(self.all_balance())  # 记录总资产变化

    def load_stock(self, stock_data):
        self.stock_data = stock_data
    
    # def train(self,):
    #     print("开始训练")
    #     # 准备训练数据
    #     X_data = []
    #     y_data = []

    #     for day_id in range(0, self.stock_data.get_trade_day()-1):
    #     # for day_id in range(5, 100):
    #         features = self.feature_extractor(day_id)
    #         if features is None:
    #             continue
    #         # 未来涨/跌作为标签
    #         future_return =  self.stock_data.get_data_by_day_id(day_id + 1) / self.stock_data.get_data_by_day_id(day_id) - 1
    #         label = 2 if future_return > 0 else 0 if future_return < 0 else 1
    #         X_data.append(features)
    #         y_data.append(label)

    #     # 训练模型
    #     X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2)
    #     model = RandomForestClassifier(n_estimators=100)
    #     model.fit(X_train, y_train)

    #     self.model = model
    #     print("训练结束")

    def train(self):
        print("开始训练")
        X_data = []
        y_data = []
        future_horizon = 40
        threshold = 0.000  # 0.5%

        for day_id in range(0, self.stock_data.get_trade_day() - future_horizon):
        # for day_id in range(0, 100 - future_horizon):
            features = self.feature_extractor(day_id)
            if features is None:
                continue

            cur_price = self.stock_data.get_data_by_day_id(day_id)

            # 获取未来 20 天的价格均值
            future_prices = [self.stock_data.get_data_by_day_id(day_id + i) for i in range(1, future_horizon + 1)]
            future_mean_price = np.mean(future_prices)
            future_trend = (future_mean_price / cur_price) - 1

            # 构造标签（基于未来均线 vs 当前价）
            if future_trend > threshold:
                label = 2  # 涨
            elif future_trend < -threshold:
                label = 0  # 跌
            else:
                label = 1  # 持平

            X_data.append(features)
            y_data.append(label)

        # 训练模型
        X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        self.model = model

        print("训练完成")
        from sklearn.metrics import classification_report
        print("测试集结果:")
        print(classification_report(y_test, model.predict(X_test)))

    
    def ml_strategy(self, stock_id, model, cur_day, buy_ration=0.2, sell_ration=0.4):
        """
        使用机器学习模型判断是否买入/卖出
        :param stock_id: 股票ID
        :param model: 已训练好的ML模型（分类器）
        :param feature_extractor: 函数，传入 stock_id, day_id 返回特征向量
        """
        cur_day = int(cur_day)  # 确保 day_id 是整数

        # 获取特征向量
        X = self.feature_extractor(cur_day)
        if X is None:
            return

        # 预测信号（0 = 卖出，1 = 持仓，2 = 买入）
        signal = model.predict([X])[0]

        # 根据预测信号执行操作
        if signal == 2:
            self.buy(stock_id, self.balance * buy_ration)
        elif signal == 0:
            self.sell(stock_id, sell_ration)
        else:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])

        if self.traded:
            self.traded = False
            self.check_balance()
    
    # def feature_extractor(self, day_id, window=5):
    #     """
    #     简单特征：5日收益率、波动率、涨跌幅
    #     """
    #     if day_id < window + 1:
    #         return None
    #     # if day_id == self.stock_data.get_trade_day():
    #     #     return None

    #     prices = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(window + 1)][::-1]
    #     # returns = np.diff(prices) / prices[:-1]
    #     # vol = np.std(returns)
    #     # mean_return = np.mean(returns)
    #     # last_return = returns[-1]

    #     # return [vol, mean_return, last_return]

    #     log_returns = np.diff(np.log(prices))  # log(P_t / P_{t-1})

    #     log_returns = np.diff(prices) / prices[:-1]

    #     # Z-score 标准化
    #     mean_return = np.mean(log_returns)
    #     std_return = np.std(log_returns) + 1e-8  # 防止除零
    #     z_scores = (log_returns - mean_return) / std_return

    #     vol = np.std(z_scores)
    #     mean_return = np.mean(z_scores)
    #     last_return = z_scores[-1]
    #     price_change_ratio = (prices[-1] / prices[0]) - 1  # 总收益率

    #     return [vol, mean_return, last_return, price_change_ratio]

    def feature_extractor(self, day_id):
        """
        特征：是否高于从0到100（步长为10）天的均线。
        返回长度为11的二值特征向量。
        """
        max_window = 50
        step = 10

        if day_id < max_window:
            return None

        # 获取最近 max_window 天的收盘价（含当天）
        prices = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(max_window)][::-1]
        close_price = prices[-1]  # 当前（day_id）当天收盘价

        features = []
        for window in range(0, max_window + 1, step):  # [0, 10, 20, ..., 100]
            if window == 0:
                # 特殊处理：0日均线就等于当天价格
                ma = close_price
            else:
                ma = np.mean(prices[-window:])
            above_ma = 1 if close_price > ma else 0
            features.append(above_ma)

        return features  # 长度为 11

    # def feature_extractor(self, day_id, window=5, max_window=100, step=25):
    #     """
    #     提取两类特征：
    #     1. 简单收益类特征：5日波动率、均值、最后一个标准化收益率、价格变化率（共4维）
    #     2. 均线判断特征：从0到100（每step天）日均线，判断是否高于（共 max_window//step + 1 维）
    #     总共特征维度：4 + ceil(100 / step) + 1
    #     """
    #     if day_id < max(max_window, window + 1):
    #         return None

    #     # ---------------------
    #     # Part 1: 收益率类特征
    #     # ---------------------
    #     prices_ret = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(window + 1)][::-1]
    #     log_returns = np.diff(np.log(prices_ret))  # 或普通收益率 np.diff(prices) / prices[:-1]
        
    #     mean_return = np.mean(log_returns)
    #     std_return = np.std(log_returns) + 1e-8  # 防止除零
    #     z_scores = (log_returns - mean_return) / std_return

    #     vol = np.std(z_scores)
    #     mean_z_return = np.mean(z_scores)
    #     last_z_return = z_scores[-1]
    #     price_change_ratio = (prices_ret[-1] / prices_ret[0]) - 1

    #     feature_ret = [vol, mean_z_return, last_z_return, price_change_ratio]

    #     # ---------------------
    #     # Part 2: 均线高于判断特征
    #     # ---------------------
    #     prices_ma = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(max_window)][::-1]
    #     close_price = prices_ma[-1]

    #     feature_ma = []
    #     for w in range(0, max_window + 1, step):  # e.g. 0, 25, 50, 75, 100
    #         if w == 0:
    #             ma = close_price
    #         else:
    #             ma = np.mean(prices_ma[-w:])
    #         feature_ma.append(1 if close_price > ma else 0)

    #     # 合并特征
    #     return feature_ret + feature_ma

    # def feature_extractor(self, day_id, short_window=5, long_window=20, vol_window=5):
    #     """
    #     构造基于 volume_price_strategy 的特征向量，用于决策树训练。
    #     """
    #     if day_id < max(short_window, long_window, vol_window):
    #         return None

    #     # 获取历史收盘价和成交量
    #     prices = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(long_window)][::-1]
    #     volumes = [self.stock_data.get_volume_by_day_id(day_id - i) for i in range(vol_window)][::-1]

    #     cur_price = prices[-1]
    #     short_ma = np.mean(prices[-short_window:])
    #     long_ma = np.mean(prices)
    #     vol_ma = np.mean(volumes)
    #     current_vol = volumes[-1]

    #     # 构造特征
    #     features = [
    #         short_ma / long_ma,             # 趋势强度
    #         cur_price / short_ma,           # 价格相对短期均线
    #         cur_price / long_ma,            # 价格相对长期均线
    #         current_vol / vol_ma,           # 成交量倍数
    #         int(short_ma > long_ma),        # 是否上穿
    #         int(short_ma < long_ma),        # 是否下穿
    #         int(current_vol > vol_ma * 1.35),  # 成交量放大
    #         int(current_vol < vol_ma * 0.7),   # 成交量萎缩
    #         int(cur_price > short_ma),      # 当前价格是否在短期均线上
    #     ]

    #     return features

    # def feature_extractor(self, day_id, short_window=5, long_window=20, vol_window=5):
    #     """
    #     特征向量只包含两个元素：
    #     - buy_condition 是否满足（1/0）
    #     - sell_condition 是否满足（1/0）
    #     """
    #     if day_id < max(short_window, long_window, vol_window):
    #         return None

    #     # 获取历史数据
    #     prices = [self.stock_data.get_data_by_day_id(day_id - i) for i in range(long_window)][::-1]
    #     volumes = [self.stock_data.get_volume_by_day_id(day_id - i) for i in range(vol_window)][::-1]

    #     cur_price = prices[-1]
    #     short_ma = np.mean(prices[-short_window:])
    #     long_ma = np.mean(prices)
    #     vol_ma = np.mean(volumes)
    #     current_vol = volumes[-1]

    #     # 条件判断
    #     buy_condition = int(
    #         (cur_price < long_ma and current_vol < vol_ma * 0.7)
    #         or (short_ma < long_ma and current_vol < vol_ma * 1.1)
    #     )

    #     sell_condition = int(
    #         short_ma > long_ma and cur_price > short_ma and current_vol > vol_ma * 1.35
    #     )

    #     return [buy_condition, sell_condition]  # 仅两维


    

    def buy_sell_graph(self, filename="trade_history_plot.png", save_dir="plots"):
        """
        将所有买卖情况画到图上，并保存为图片文件
        """
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)

        # 提取交易数据
        days = [trade[0] for trade in self.trade_history]
        prices = [trade[3] for trade in self.trade_history]

        # 绘图
        plt.figure(figsize=(24, 6))
        plt.plot(days, prices, label='Price', color='blue')

        for op in self.trade_history:
            if op[1] > 0:
                plt.scatter(op[0], op[3], color='red', marker='.', s=30, label='Buy')
            elif op[1] < 0:
                plt.scatter(op[0], op[3], color='blue', marker='.', s=30, label='Sell')

        plt.title('Buy and Sell History')
        plt.xlabel('Day')
        plt.ylabel('Price')
        plt.grid()
        # plt.legend(loc='best')

        # 保存图像
        plt.savefig(filepath)
        plt.close()  # 避免显示

        print(f"图像已保存到：{filepath}")
