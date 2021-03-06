from typing import Callable, List, Optional

import plotly.graph_objects as go
import pandas as pd
import numpy as np

from insider.mixins import (
    MovingIndicatorMixin,
    KDJIndicatorMixin,
    RSIIndicatorMixin,
    VolumnIndicatorMixin,
)
from insider.stock import Stock
from insider.constants import MA_N, MD_N, EXPMA_N, RSI_N


class StockInsider(
    Stock,
    MovingIndicatorMixin,
    KDJIndicatorMixin,
    RSIIndicatorMixin,
    VolumnIndicatorMixin,
):
    """Plot daily trading indicators."""

    def __init__(self, code, ktype="D"):
        """
        code: Full stock code，(e.g. 'sz002156')，股票完整代码
        ktype: Data frequency, valid input is `D`, `W`, or `M`. 股票数据的频率
        """
        super().__init__(code, ktype)

    @staticmethod
    def _plot_line(df: pd.DataFrame, head: int, line_name: str, y: str = "close"):
        if head:
            df = df.tail(head)
        plot_data = go.Scatter(x=df["day"], y=df[y], name=line_name)
        return plot_data

    def _plot_moving_lines(
        self,
        func: Callable,
        verbose_func: Callable,
        name: str,
        y: str = "close",
        head: int = 90,
        ns: Optional[List] = None,
        verbose: bool = False,
    ):

        plot_data = []
        for n in ns:
            df = func(n=n)
            line_name = name + str(n)
            plot_data.append(self._plot_line(df, head, line_name, y=y))

        if verbose:
            df = self._df.copy()
            verbose_data = verbose_func(df, head)
            plot_data.append(verbose_data)

        layout = self._set_layout()
        fig = go.Figure(data=plot_data, layout=layout)
        if verbose:
            fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(title_text=f"{name.upper()} Chart ({self.stock_code})")
        fig.show()

    def plot_ma(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Moving Average Indicator. 绘出MA曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20, 60-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20, 60日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MA_N

        func = self.ma
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="ma",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_md(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Moving Deviation Indicator. 绘出MD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MD_N

        func = self.md
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="md",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_ema(
        self, head: int = 90, ns: Optional[List[int]] = None, verbose: bool = False
    ):
        """Plot Exponential Moving Average Indicator. 绘出EMA曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20, 60-day lines
            选择曲线的种类，e.g. [5, 10, 20, 60], 默认会绘出5, 10, 20, 60日曲线
            verbose: If to include stock price or not, default is False.
            选择是否将股票价格曲线一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = EXPMA_N

        func = self.ema
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            name="ema",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_macd(self, head: int = 90):
        """Plot MACD Indicator. 绘出MACD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。

        A mixed chart will be plotted, including a bar chart to visualize MACD, and line charts
        to visualize DIFF and DEA.
        将会绘出差值柱形图来表示MACD, 以及表示差离值和讯号线的线性图。
        """
        df_macd = self.macd()
        if head:
            df_macd = df_macd.tail(head)

        df_macd.loc[:, "color"] = df_macd["macd"].apply(
            lambda x: "red" if x >= 0 else "green"
        )

        layout = self._set_layout()
        fig = go.Figure(layout=layout)

        fig.add_trace(
            go.Bar(
                x=df_macd["day"],
                y=df_macd["macd"],
                base=0,
                marker_color=df_macd["color"],
                name="MACD",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_macd["day"], y=df_macd["dea"], marker_color="orange", name="DEA"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_macd["day"], y=df_macd["diff"], marker_color="black", name="DIFF"
            )
        )
        fig.update_layout(title_text=f"MACD Chart ({self.stock_code})")
        fig.show()

    def plot_kdj(self, head: int = 90, n: int = 9, smooth_type="sma"):
        """Plot KDJ Indicator. 绘出KDJ曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            n: The size of moving average period for K, default is 9. 平移平均曲线的窗口大小，默认
            是9个交易日。
            smooth_type: The metric to calculate moving average, default is `sma`, the other
            option is `ema`. 选择计算平移平均曲线的方式，默认是SMA, 另一个选择是EMA。
        """
        df_kdj = self.kdj(n=n, smooth_type=smooth_type)
        if head:
            df_kdj = df_kdj.tail(head)

        plot_data = []
        for col in ["K", "D", "J"]:
            plot_data.append(self._plot_line(df_kdj, head, col, y=col))

        layout = self._set_layout()
        fig = go.Figure(data=plot_data, layout=layout)
        fig.update_layout(title_text=f"KDJ Chart ({self.stock_code})")
        fig.show()

    def plot_rsi(self, head: int = 90, ns: Optional[List] = None):
        """Plot RSI Indicator. 绘出RSI曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 6, 12, 24-day lines
            选择曲线的种类，e.g. [6, 12], 默认会绘出6, 12, 24日曲线
        """
        if ns is None:
            ns = RSI_N

        func = self.rsi
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="rsi",
            name="RSI",
            head=head,
            ns=ns,
            verbose=False,
        )

    def plot_vrsi(self, head: int = 90, ns: Optional[List] = None):
        """Plot VRSI Indicator. 绘出VRSI曲线。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 6, 12, 24-day lines
            选择曲线的种类，e.g. [6, 12], 默认会绘出6, 12, 24日曲线
        """
        if ns is None:
            ns = RSI_N

        func = self.vrsi
        verbose_func = self._plot_stock_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="rsi",
            name="VRSI",
            head=head,
            ns=ns,
            verbose=False,
        )

    @staticmethod
    def _plot_volumn_data(df, head):
        df_volumn = df.copy()
        if head:
            df_volumn = df_volumn.tail(head)

        df_volumn = df_volumn.assign(
            color=lambda x: np.where(x["open"] < x["close"], "red", "green")
        )

        data = go.Bar(
            x=df_volumn["day"],
            y=df_volumn["volumn"],
            base=0,
            marker_color=df_volumn["color"],
            name="Volumn",
        )
        return data

    def plot_volumn(self, head: int = 90):
        """Plot Volumn over time. 绘出交易量能柱状图。

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的交易量能柱状图。
        """
        df_volumn = self._df.copy()
        data = self._plot_volumn_data(df_volumn, head)

        layout = self._set_layout()
        fig = go.Figure(data=[data], layout=layout)
        fig.update_layout(title_text=f"Volumn Chart ({self.stock_code})")
        fig.show()

    def plot_vma(
        self, head: int = 90, ns: Optional[List] = None, verbose: bool = False
    ):
        """Plot VMA over time. 绘出交易能量MA图曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
            verbose: If to include volumn change bar chart or not, default is False.
            选择是否将能量变化柱状图一起绘出，默认是False，将会只绘出指标曲线。
        """
        if ns is None:
            ns = MA_N

        func = self.vma
        verbose_func = self._plot_volumn_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="volumn",
            name="vma",
            head=head,
            ns=ns,
            verbose=verbose,
        )

    def plot_vmacd(self, head: int = 90):
        """Plot VMACD Indicator. 绘出VMACD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。

        A mixed chart will be plotted, including a bar chart to visualize VMACD, and line charts
        to visualize DIFF and DEA.
        将会绘出量能差值柱形图来表示VMACD, 以及表示差离值和讯号线的线性图。
        """
        df_vmacd = self.vmacd()
        if head:
            df_vmacd = df_vmacd.tail(head)

        df_vmacd.loc[:, "color"] = df_vmacd["macd"].apply(
            lambda x: "red" if x >= 0 else "green"
        )

        layout = self._set_layout()
        fig = go.Figure(layout=layout)

        fig.add_trace(
            go.Bar(
                x=df_vmacd["day"],
                y=df_vmacd["macd"],
                base=0,
                marker_color=df_vmacd["color"],
                name="VMACD",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_vmacd["day"], y=df_vmacd["dea"], marker_color="orange", name="DEA"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_vmacd["day"], y=df_vmacd["diff"], marker_color="black", name="DIFF"
            )
        )
        fig.update_layout(title_text=f"VMACD Chart ({self.stock_code})")
        fig.show()

    def plot_vstd(self, head: int = 90, ns: Optional[List] = None):
        """Plot VSTD chart. 绘出VSTD曲线

        Parameters:
            head: The recent number of trading days to plot, default is 90, 最近交易日的天数，
            默认90，将会绘出最近90个交易日的曲线。
            ns: Select which trading lines to plot, default is to plot 5, 10, 20-day lines
            选择曲线的种类，e.g. [5, 10], 默认会绘出5, 10, 20日曲线
        """
        if ns is None:
            ns = MD_N

        func = self.vstd
        verbose_func = self._plot_volumn_data
        self._plot_moving_lines(
            func=func,
            verbose_func=verbose_func,
            y="vstd",
            name="vstd",
            head=head,
            ns=ns,
            verbose=False,
        )
