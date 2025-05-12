from BaseTrader import BaseTrader

class EnhancedTrader(BaseTrader):
    def __init__(self, initial_balance):
        """
        增强版量化交易者（支持量价策略）
        :param initial_balance: 初始资金额度
        """
        super().__init__(initial_balance)
        self.price_history = []    # 价格历史序列（用于计算技术指标）
        self.volume_history = []  # 成交量历史序列
        self.position = 0         # 0-空仓 1-持仓（状态跟踪）

    def trade(self, stock_id, cur_price, volume, strategy='volume_price'):
        """
        执行交易（重写父类方法）
        :param stock_id: 股票ID
        :param cur_price: 当前价格
        :param volume: 当日成交量
        :param strategy: 策略名称
        """
        self.day_id += 1
        self._update_history(cur_price, volume)
        
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': cur_price, 'shares': 0, 'can_sell': True}

        if strategy == 'volume_price':
            self.volume_price_strategy(stock_id)
            
        self.balance_history.append(self.all_balance())

    def _update_history(self, price, volume):
        """更新历史数据序列"""
        self.last_price = self.cur_price
        self.cur_price = price
        self.price_history.append(price)
        self.volume_history.append(volume)

    def volume_price_strategy(self, stock_id, 
                             short_window=5, 
                             long_window=20,
                             vol_window=5,
                             buy_ratio=0.2,
                             sell_ratio=1.0):
        """
        量价结合策略（核心逻辑）
        策略逻辑：
        1. 当短期均线上穿长期均线，且成交量放大时买入
        2. 当价格跌破长期均线时清仓
        3. 成交量放大定义为：当日成交量超过过去vol_window日平均的1.2倍
        """
        if len(self.price_history) < long_window:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])
            return  # 数据不足不交易
        # print(self.cur_price)

        # 计算技术指标
        short_ma = sum(self.price_history[-short_window:])/short_window
        long_ma = sum(self.price_history[-long_window:])/long_window
        vol_ma = sum(self.volume_history[-vol_window:])/vol_window
        
        current_shares = self.holdings[stock_id]['shares']
        current_vol = self.volume_history[-1]

        # 卖出信号条件
        sell_condition = (
            short_ma > long_ma and                # 均线交叉
            self.cur_price > short_ma and         # 价格在短期均线上方
            current_vol > vol_ma * 1.35            # 成交量放大
        )

        # 买入信号条件
        buy_condition = (
            self.cur_price < long_ma and           # 价格跌破长期均线
            current_vol < vol_ma * 0.7 or         # 成交量萎缩
            (short_ma < long_ma and current_vol < vol_ma * 1.1)  # 短期均线下穿长期均线，且成交量没有明显上涨
        )

        # 交易逻辑-1
        if buy_condition:
            if current_shares == 0:  # 空仓时建仓
                self.buy(stock_id, buy_ratio * self.balance)
                self.position = 1
            else:                     # 持仓时加仓
                self.buy(stock_id, buy_ratio *0.5 * self.balance)
        elif sell_condition and current_shares > 0:
            self.sell(stock_id, sell_ratio)  # 卖出持仓的50%
            if self.holdings[stock_id]['shares'] == 0:
                self.position = 0
        else:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])

        # -2
        # 交易逻辑
        # if buy_condition:
        #     if current_shares == 0:  # 空仓时建仓
        #         self.buy_hand(stock_id, 50)
        #         self.position = 1
        #     else:                     # 持仓时加仓
        #         self.buy_hand(stock_id, 50)
        # elif sell_condition and current_shares > 0:
        #     self.sell_hand(stock_id, 50)  # 卖出持仓的50%
        #     if self.holdings[stock_id]['shares'] == 0:
        #         self.position = 0
        # else:
        #     self.trade_history.append([self.day_id, 0, 0, self.cur_price])

    # 保持父类的buy/sell方法不变，可视需要添加成交量记录
    def buy(self, stock_id, amount):
        """重写买入方法，添加成交量记录"""
        super().buy(stock_id, amount)
        # 在交易记录中添加成交量信息（扩展父类功能）
        # if self.trade_history:
        #     last_trade = self.trade_history[-1]
        #     last_trade.append(self.volume_history[-1])  # 格式：[day, shares, amount, price, volume]

    def sell(self, stock_id, share_ratio):
        """重写卖出方法，添加成交量记录"""
        super().sell(stock_id, share_ratio)
        # if self.trade_history:
        #     last_trade = self.trade_history[-1]
        #     last_trade.append(self.volume_history[-1])

    def buy_hand(self, stock_id, hand):
        """重写买入方法，添加成交量记录"""
        super().buy_by_hand(stock_id, hand)
        # 在交易记录中添加成交量信息（扩展父类功能）
        # if self.trade_history:
        #     last_trade = self.trade_history[-1]
        #     last_trade.append(self.volume_history[-1])  # 格式：[day, shares, amount, price, volume]

    def sell_hand(self, stock_id, hand):
        """重写卖出方法，添加成交量记录"""
        super().sell_by_hand(stock_id, hand)
        # if self.trade_history:
        #     last_trade = self.trade_history[-1]
        #     last_trade.append(self.volume_history[-1])