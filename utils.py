import pandas as pd




def round_shares(shares):
    """
    四舍五入到最接近的100整数
    :param shares: 股票数量
    :return: 四舍五入后的股票数量
    """
    return ((shares + 99) // 100) * 100

def get_stock_info(stock_id:int, day_id:int):
    file_path = stock_id + '-2024.xlsx'
    data = pd.read_excel(file_path)
    return data.iloc[day_id]["close"]  # 返回指定日期的收盘价

def sell_fee(amount):
    """
    计算卖出手续费，抽象后只是用这个
    :param amount: 卖出金额
    :return: 手续费
    """
    return max(amount * 0.0007, 5)