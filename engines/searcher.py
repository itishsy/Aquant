from engines.engine import Searcher, job_engine
import strategies.utils as utl
from models.symbol import Symbol
from candles.storage import find_candles


@job_engine
class U20(Searcher):

    def search(self, code):

        candles = find_candles(code)

        if (len(candles) < 100 or
                not utl.is_beyond_ma(candles[-20:], 20, ma_ratio=0.7) or
                not utl.is_active(candles[-20:]) or
                utl.is_daily_top(candles) or
                utl.is_top_divergence(code, 60, limit=utl.cal_limit(60, 5)) or
                utl.is_top_volume(candles, pre_ratio=0.7, nxt_ratio=0.9, limit=20) or
                utl.is_big_a(candles[-30:], down_ratio=0.618)):
            return

        # 6天内发出30min底背离信号
        sig = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 6))
        if not sig:
            # 3天内发出15min底背离信号
            sig = utl.driver_bottom_signal(code, 15, utl.cal_limit(15, 3))
        return sig


@job_engine
class U10(Searcher):

    def search(self, code):
        candles = find_candles(code)

        if (len(candles) < 100 or
                candles[-1].close > candles[-1].ma10 or
                not utl.is_beyond_ma(candles[-15:], 10, ma_ratio=0.9) or
                not utl.is_active(candles[-20:], zhang_ting=0.085, zhang_ting_size=1) or
                utl.is_top_volume(candles[-50:], pre_ratio=0.9, nxt_ratio=0.9, limit=15) or
                utl.is_daily_top(candles) or
                utl.is_top_divergence(code, 60, limit=utl.cal_limit(60, 10))):
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


@job_engine
class U615(Searcher):

    def search(self, code):

        candles = find_candles(code)

        # 在ma60线之上\活跃度不足\日級別顶背离\高位放量\大A形态
        if (len(candles) < 100 or
                not utl.is_active(candles[-50:]) or
                utl.is_daily_top(candles) or
                utl.is_top_volume(candles, pre_ratio=0.7, nxt_ratio=0.8, limit=30) or
                utl.is_big_a(candles[-50:], down_ratio=0.618)):
            return

        if utl.is_beyond_ma(candles[-50:], 60, ma_ratio=0.6) or utl.is_beyond_x(candles[-50:], x_ratio=0.5):
            # 15天内发出的60min底背离信号
            sig60 = utl.driver_bottom_signal(code, 60, utl.cal_limit(60, 15))
            if sig60:
                # 6天内发出的15min底背离信号
                sig15 = utl.driver_bottom_signal(code, 15, utl.cal_limit(15, 6))
                if sig15 and sig15.dt > sig60.dt:
                    return sig15


@job_engine
class U305(Searcher):

    def search(self, code):

        candles = find_candles(code)

        if (len(candles) < 100 or
                not utl.is_active(candles[-50:]) or
                utl.is_daily_top(candles) or
                utl.is_top_volume(candles, pre_ratio=0.7, nxt_ratio=0.8, limit=20) or
                utl.is_big_a(candles[-50:], down_ratio=0.618)):
            return

        if utl.is_beyond_ma(candles[-30:], 60, ma_ratio=0.5) or utl.is_beyond_x(candles[-50:], x_ratio=0.5):
            # 10天内发出30min底背离信号
            sig30 = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 10))
            if sig30:
                # 5天内发出5min底背离信号
                sig5 = utl.driver_bottom_signal(code, 5, utl.cal_limit(5, 5))
                if sig5 and sig5.dt > sig30.dt:
                    return sig5

