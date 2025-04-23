import pandas as pd
import numpy as np


def get_moving_average(stock_id, day_id, window):
        """获取某支股票某日向前 window 日的移动平均价格"""
        prices = [get_stock_info(stock_id, i) for i in range(day_id - window, day_id)]
        if len(prices) < window:
            return None  # 不足以计算均线
        return sum(prices) / window

def round_shares(shares):
    """
    四舍五入到最接近的100整数
    :param shares: 股票数量
    :return: 四舍五入后的股票数量
    """
    return ((shares + 99) // 100) * 100

def get_stock_info(stock_id:int, day_id:int):
    # file_path = stock_id + '-2024.xlsx'
    file_path = './' + stock_id + '/'+ '2022.xlsx'
    data = pd.read_excel(file_path)
    return data.iloc[day_id]["close"]  # 返回指定日期的收盘价


def get_stock_info_by_year(stock_id:int, year:int, day_id:int):
    file_path = './' + stock_id + '/'+ year +'.xlsx'
    data = pd.read_excel(file_path)
    return data.iloc[day_id]["close"]  # 返回指定日期的收盘价

def sell_fee(amount):
    """
    计算卖出手续费，抽象后只是用这个
    :param amount: 卖出金额
    :return: 手续费
    """
    return max(amount * 0.0007, 5)

# def feature_extractor(stock_id, day_id, window=5):
#     """
#     特征提取器：使用比例型特征，避免价格绝对值影响
#     """
#     if day_id < window + 1:
#         return None

#     prices = [get_stock_info(stock_id, day_id - i) for i in range(window + 1)][::-1]
    
#     # # 对数收益率（更稳定）
#     # log_returns = np.diff(np.log(prices))  # log(P_t / P_{t-1})

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

def feature_extractor(stock_id, day_id, window=5):
    """
    简单特征：5日收益率、波动率、涨跌幅
    """
    if day_id < window + 1:
        return None

    prices = [get_stock_info(stock_id, day_id - i) for i in range(window + 1)][::-1]
    returns = np.diff(prices) / prices[:-1]
    vol = np.std(returns)
    mean_return = np.mean(returns)
    last_return = returns[-1]

    return [vol, mean_return, last_return]


def download_stock_data(stock_id, year):
    """
    下载股票数据
    :param stock_id: 股票ID
    :param year: 年份
    """
    api=TdxHq_API()

    with api.connect():
        data=[]

        for i in range(10):
                data+=api.get_security_bars(9,0,'000001',(9-i)*800,800)
    print(api.to_df(data))