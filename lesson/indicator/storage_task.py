import storage

storage.upset_all()
#storage.upset('300059')

codes = storage.query('SELECT code FROM `all_realtime`')

for idx,row in codes.iterrows():
    code = row['code']
    if code.find('ST') == -1 and (code.startswith('0') or code.startswith('6') or code.startswith('3')) :
        storage.upset(code)





