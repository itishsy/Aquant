from dataclasses import dataclass


@dataclass
class Symbol:
    def __init__(self, series=None):
        if series is not None:
            for k in series.keys():
                val = series[k]
                if k == '股票代码':
                    self.code = val
                elif k == '股票名称':
                    self.name = val
                elif str(k).startswith('净利润'):
                    self.profit = val if isinstance(val, float) else 0.0
                elif str(k).startswith('总市值'):
                    self.total = val if isinstance(val, float) else 0.0
                elif str(k).startswith('流通市值'):
                    self.circulating = val if isinstance(val, float) else 0.0
                elif str(k).startswith('所处行业'):
                    self.industry = val
                elif str(k).startswith('市盈率'):
                    self.pe = val if isinstance(val, float) else 0.0
                elif k == '市净率':
                    self.pb = val if isinstance(val, float) else 0.0
                elif k == 'ROE':
                    self.roe = val if isinstance(val, float) else 0.0
                elif k == '毛利率':
                    self.gross = val if isinstance(val, float) else 0.0
                elif k == '净利率':
                    self.net = val if isinstance(val, float) else 0.0
                elif k == '板块编号':
                    self.sector = val

    id: int
    code: str
    name: str
    status: int
    profit: float
    total: float
    circulating: float
    industry: str
    pe: float
    pb: float
    roe: float
    gross: float
    net: float
    sector: str
    created: str
    comment: str






