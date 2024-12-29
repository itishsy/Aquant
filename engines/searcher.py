from engines.engine import Searcher, job_engine
from strategies.ma10 import MA10
from strategies.ma20 import MA20
from strategies.ma60 import MA60
import strategies.utils as utl
from models.symbol import Symbol


@job_engine
class U20(Searcher):

    def search(self, code):

        candles = utl.choices(code, 20)

        if (not candles or
                not utl.is_beyond_ma(candles, 20, ma_ratio=0.9) or
                not utl.is_active(candles) or
                utl.is_top_divergence(code, 101) or
                utl.is_top_divergence(code, 60, limit=utl.cal_limit(60, 5)) or
                utl.is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.9) or
                utl.is_big_a(candles, down_ratio=0.618)):
            return

        # 6天内发出30min底背离信号
        sig = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 6))
        if not sig:
            # 3天内发出15min底背离信号
            sig = utl.driver_bottom_signal(code, 15, utl.cal_limit(15, 3))

        return sig
        # return MA20.search(code)


@job_engine
class U60(Searcher):

    def search(self, code):
        candles = utl.choices(code, 30)

        # 在ma60线之上\活跃度不足\日級別顶背离\高位放量\大A形态
        if (not candles or
                not utl.is_beyond_ma(candles, 60, ma_ratio=0.9) or
                not utl.is_active(candles) or
                utl.is_top_divergence(code, 101) or
                utl.is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.8) or
                utl.is_big_a(candles, down_ratio=0.618)):
            return

        # 15天内发出的60min底背离信号
        sig = utl.driver_bottom_signal(code, 60, utl.cal_limit(60, 15))
        if not sig:
            # 8天内发出的30min底背离信号
            sig = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 8))

        return sig
        # return MA60.search(code)


@job_engine
class U10(Searcher):

    def search(self, code):
        candles = utl.choices(code, 10)

        if (not candles or
                candles[-1].close > candles[-1].ma10 or
                not utl.is_beyond_ma(candles, 10, ma_ratio=0.9) or
                not utl.is_active(candles, zhang_ting=0.085, zhang_ting_size=1) or
                utl.is_top_volume(candles, pre_ratio=0.9, nxt_ratio=0.9) or
                utl.is_top_divergence(code, 60, limit=utl.cal_limit(60, 6)) or
                utl.is_top_divergence(code, 30, limit=utl.cal_limit(30, 3))):
            return

        # 2天内发出5min底背离信号
        sig = utl.driver_bottom_signal(code, 5, utl.cal_limit(5, 2))
        if sig:
            sig.notify = 0
            return sig
        else:
            sym = Symbol.get(Symbol.code == code)
            sym.is_watch = 1
            sym.save()

        # return MA10.search(code)
