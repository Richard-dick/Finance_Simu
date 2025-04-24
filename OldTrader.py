from BaseTrader import BaseTrader
# 追涨杀跌的高手

class OldTrader(BaseTrader):
    def __init__(self, initial_balance):
        super().__init__(initial_balance)
        

    def trade(self, stock_id, cur_price):

        self.day_id += 1  # 更新当前天数
        self.last_price = self.cur_price
        self.cur_price = cur_price  # 更新当前价格
        if stock_id not in self.holdings:
            self.holdings[stock_id] = {'price': cur_price, 'shares': 0, 'can_sell': True}
        
        self.old_strategy(stock_id)
        self.balance_history.append(self.all_balance())  # 记录总资产变化

    def old_strategy(self, stock_id, buy_ration=0.2, sell_ration=0.3):
        # 追涨杀跌的高手
        # 涨了就买，跌了就卖

        if self.last_price == 0:
            self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
            return  # 如果没有上一个价格，则返回
        if self.holdings[stock_id]["shares"] == 0: 
            last_price = self.last_price
            if last_price < self.cur_price: # 涨了， 冲冲冲
                self.buy(stock_id, buy_ration * self.balance)  # 买入底仓
            else:
                self.trade_history.append([self.day_id, 0, 0, self.cur_price])  # 记录交易情况
        else: # ! 有仓位的更新
            last_price = self.last_price  # 获取自己的持仓成本价格
            current_price = self.cur_price  # 获取当前价格
            if last_price <= current_price:# ! 说明涨了
                self.buy(stock_id, buy_ration * self.balance)
            elif last_price > current_price:  # ! 说明跌了
                self.sell(stock_id, sell_ration)  # 追高
            else:
                self.trade_history.append([self.day_id, 0, 0, self.cur_price])

        if self.traded:
            self.traded = False
            self.check_balance()  # 打印当前总资产
    
        
        