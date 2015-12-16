#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import xlrd
import sqlite3
import sys

def parse_excel(fname):
    excel = xlrd.open_workbook(fname)
    sheet = excel.sheet_by_index(0)
    # 1 device, 2 phone, 3 channel
    # ignore heading.
    rs = []
    for r in range(1, sheet.nrows):
        device = sheet.cell(r, 1).value
        phone = sheet.cell(r, 2).value
        channel = sheet.cell(r, 3).value
        if not phone: continue
        device = int(device)
        phone = str(int(phone))
	if not phone.startswith('13'): continue
        rs.append((device, phone, channel))
        # print 'device = %s, phone = %s, channel = %s' % (device, phone, channel)
    return rs

def import_sqlite(rs, fname):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    for r in rs:
        (device, phone, channel) = r
        try:
            c.execute("INSERT INTO pb VALUES(?, ?, ?, ?, ?)", (phone, 0, 0, device, channel))
        except sqlite3.IntegrityError as e:
            pass
    conn.commit()
    c.close()
    conn.close()
    
def main():
    excel = sys.argv[1]
    rs = parse_excel(excel)
    sqlite = sys.argv[2]
    import_sqlite(rs, sqlite)
    

if __name__ == '__main__':
    main()
