import re

s = '=AeStockQuote("BC";"Cot";"SBCX23*.AJU")'
rs = re.search('=AeStockQuote\("(.+)";"(.+)";"(.+)"\)', s)
print(rs.groups(), len(rs.groups()))
            