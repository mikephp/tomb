#!/usr/bin/env bash
#Copyright (C) dirlt

mkdir -p static

# 如果使用本地数据库
sqlite3 phone-book.db <<EOF
DROP TABLE IF EXISTS  pb;
CREATE TABLE IF NOT EXISTS pb (phone TEXT PRIMARY KEY, balance DECIMAL, marked TINYINT, device TEXT, channel TEXT);
-- 一些测试号码
-- INSERT INTO pb VALUES('13429038941', 0, 0, '?', '?')
-- INSERT INTO pb VALUES('13429038942', 0, 0, '?', '?')
-- INSERT INTO pb VALUES('13429038943', 0, 0, '?', '?')
-- INSERT INTO pb VALUES('13429038947', 0, 0, '?', '?')
EOF
