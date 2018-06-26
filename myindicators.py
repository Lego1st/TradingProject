import backtrader as bt 
import math

class ALMA(bt.Indicator):
    lines = ('ma',)
    params = (('period', 7), ('offset', 0.85), ('sigma', 6))
    plotinfo = dict(plot=True, subplot=False)

    def __init__(self):
        self.addminperiod(self.params.period)

    def algorithm(self, Size, Offset, Sigma, Price):

        m = (Offset * (Size - 1))
        s = Size / Sigma
        
        WtdSum = 0
        CumWt  = 0
        
        for k in range(Size):
            Wtd = math.exp(-((k-m)*(k-m))/(2*s*s))
            WtdSum = WtdSum + Wtd * Price[Size - 1 - k]
            CumWt = CumWt + Wtd
        
        res = WtdSum / CumWt
        
        return res

    def next(self):
        datas = self.data.get(size=self.p.period)
        self.l.ma[0] = self.algorithm(self.p.period, self.p.offset, self.p.sigma, datas)