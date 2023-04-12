import efinance as ef
import storage.database as db


def reverse_signal(stock_code, level, type, datetime):
    delete_sql = "DELETE FROM `reverse_signal` " \
                 "WHERE `stock_code` = '{}' " \
                 "AND `level` = '{}' " \
                 "AND `reverse_datetime` = '{}'" \
        .format(stock_code, level, datetime)
    db.execute(db.get_connect(), delete_sql)
    insert_sql = "INSERT INTO `reverse_signal` " \
                 "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`create`) " \
                 "VALUES('{}','{}','{}','{}',NOW())" \
        .format(stock_code, level, type, datetime)
    db.execute(db.get_connect(), insert_sql)


# def reverse_signal2(stock_code, level, type, datetime):
#     delete_sql = "DELETE FROM `reverse_signal` " \
#                  "WHERE `stock_code` = '{}' " \
#                  "AND `level` = '{}' " \
#                  "AND `reverse_datetime` = '{}'" \
#         .format(stock_code, level, datetime)
#     db.execute2(delete_sql)
#     insert_sql = "INSERT INTO `reverse_signal` " \
#                  "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`create`) " \
#                  "VALUES('{}','{}','{}','{}',NOW())" \
#         .format(stock_code, level, type, datetime)
#     db.execute2(insert_sql)
