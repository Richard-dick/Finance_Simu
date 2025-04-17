from pytdx.hq import TdxHq_API
import pandas as pd
import mplfinance as mpf



def draw_by_mouth(df:pd.DataFrame, stock_id:str):
    market_colors = mpf.make_marketcolors(
        up='red',    # 上涨颜色
        down='green',    # 下跌颜色
        edge='black',  # 蜡烛边框颜色
        wick='black',   # 影线颜色
        volume={'up': 'red', 'down': 'green'}   # 成交量按涨跌显示不同颜色
    )
    # 应用自定义颜色方案
    style = mpf.make_mpf_style(marketcolors=market_colors, gridstyle='--')

    monthly_data = df.groupby(pd.Grouper(freq='ME'))
    for month, data in monthly_data:
        # 重命名列以符合 mplfinance 的要求
        data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'})

        # 绘制并保存 K 线图
        file_name = 'img/'+ stock_id+ f'{month.strftime("%Y-%m")}.png'
        mpf.plot(data, type='candle', style=style, title=f'{stock_id}" "{month.strftime("%Y-%m")} K graph', volume=True, savefig=file_name)
        print(f"已保存图表: {file_name}")


# 创建 API 对象
api = TdxHq_API()

# 连接到通达信服务器
if api.connect('111.229.247.189', 7709):  # 替换为可用的服务器地址和端口
    print("连接成功")
else:
    print("连接失败")


# index_kline = api.get_index_bars(9, 1, '000001', 0, 10)  # 1 表示沪市，'000001' 是上证指数代码
# print(index_kline)

# kline_data = api.get_security_bars(9, 0, '000001', 0, 10)  # 9 表示日 K 线，获取 100 条数据
# print(kline_data)

# minute_data = api.get_minute_time_data(0, '000001')  # 0 表示深市，'000001' 是股票代码
# print(minute_data)

# df = pd.DataFrame(minute_data)
# print(df.head())

stock_id = '512480'

data = api.get_security_bars(9, 1, stock_id, 0, 365)
df = api.to_df(data)

# 保存为 Excel 文件
df.to_excel('tmp.xlsx', index=False)
print("数据已保存到 tmp.xlsx")


df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# 按月分组
# draw_by_mouth(df, stock_id)


api.disconnect()


