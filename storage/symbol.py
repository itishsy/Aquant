from dataclasses import dataclass
from storage.dba import dba
import efinance as ef


@dataclass
class Symbol:
    def __init__(self, series=None):
        if series is not None:
            for key in series.keys():
                setattr(self, key, series[key])

    id: int
    code: str
    name: str
    status: int
    comment: str


def fetch_symbols():
    session = dba.get_session()
    sbs = session.query(Symbol).all()
    if len(sbs) == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        # df = df[df['name'].str.contains('ST') is False]
        symbols = []
        for i, row in df.iterrows():
            s = Symbol(row)
            s.status = 1
            symbols.append(s)
        session.add_all(symbols)
        session.commit()
