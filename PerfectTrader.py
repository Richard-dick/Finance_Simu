from BaseTrader import BaseTrader

class PerfectTrader(BaseTrader):
    def __init__(self, initial_balance):
        super().__init__(initial_balance)
        self.stock_history = []

    def trade(self, stock_id, current_price):
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': current_price, 'shares': 0, 'can_sell': True}
        
        self.stock_history.append(current_price)

    def perfect_strategy(self, stock_id):
        # 等到所有的股票信息更新完之后调用
        # 在 stock_history 中的高点卖出，低点买入
        indicator = -100.0 # -1 代表之前为下降，+1代表之前为上升。 第一天默认是下降
        self.stock_history.append(0.0)  # 添加一个末尾小值，避免越界且使得最后一天必然卖出
        for i in range(0, len(self.stock_history)-1):
            print(indicator*(self.stock_history[i+1] - self.stock_history[i]) < 0.0)
            self.cur_price = self.stock_history[i]
            self.day_id = i
            if indicator*(self.stock_history[i+1] - self.stock_history[i]) < 0.0:
                # 异号，明天会到顶/低
                if indicator < 0:
                    self.buy(stock_id, self.balance)
                    indicator = -indicator
                else:
                    self.sell(stock_id, 1)
                    indicator = -indicator
                
            elif indicator*(self.stock_history[i+1] - self.stock_history[i]) > 0.0:
                # 同号，保持之前的趋势，不动
                self.trade_history.append([i, 0, 0, self.stock_history[i]])
        
        