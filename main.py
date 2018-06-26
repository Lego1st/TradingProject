import os
import datetime as dt
import sys
import backtrader as bt 
import backtrader.feeds as btfeeds
from myindicators import *

DATAPATH = "BTCUSDT1HourBinance.csv"
TEST_RANGE = False

class MyHLOC(btfeeds.GenericCSVData):

    params = (
        ('fromdate', dt.datetime(2018, 1, 1)),
        ('todate', dt.datetime(2018, 5, 31)),
        ('dtformat', ('%Y-%m-%d %H:%M:%S')),
        ('tmformat', ('%H:%M:%S')),

        ('datetime', 1),
        ('open', 2),
        ('high', 3),
        ('low', 4),
        ('close', 5),
        ('volume', 6),
        ('openinterest', -1)
        )

class TestStrategy(bt.Strategy):

    params = (
        ('maperiod', 27),
        ('printlog', False)
        )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.maperiod)
        self.ma = ALMA(self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("BUY EXECUTED, price: %.2f, cost: %.2f, comm: %.2f" % 
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log("SELL EXECUTED, price: %.2f, cost: %.2f, comm: %.2f" % 
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" %
                (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log("Close, %.2f" % self.dataclose[0])

        if self.order:
            return
        
        if not self.position:
            if self.dataclose[0] > self.ma[0]:
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.ma[0]:
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' % (self.params.maperiod, self.broker.getvalue()), doprint=True)

if __name__ == "__main__":
    
    cerebro = bt.Cerebro()
    if TEST_RANGE:
        cerebro.optstrategy(TestStrategy,maperiod=range(3, 30))
    else:
        cerebro.addstrategy(TestStrategy, printlog=True)

    data = MyHLOC(dataname=DATAPATH)
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.001)
    # Display finance monitor
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    if not TEST_RANGE:
        cerebro.plot()