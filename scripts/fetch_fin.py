#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量取东财公开业绩报表(营收/净利/毛利率),用于卡点报告季度更新。
用法: python fetch_fin.py [--cash] code1 code2 ...
"""
import json, urllib.request, sys, time, os

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://data.eastmoney.com/"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


def perf(code, n=4):
    url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD"
           "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORTDATE,TOTAL_OPERATE_INCOME,YSTZ,"
           "PARENT_NETPROFIT,SJLTZ,XSMLL,WEIGHTAVG_ROE"
           "&filter=(SECURITY_CODE%3D%22" + code + "%22)&pageNumber=1&pageSize=" + str(n) +
           "&sortColumns=REPORTDATE&sortTypes=-1&source=WEB&client=WEB")
    return get(url).get("result", {}).get("data", []) or []


def cash(code, n=4):
    """经营活动现金流净额(现金流量表,单季/累计)"""
    url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_CASHFLOW"
           "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORT_DATE,NETCASH_OPERATE,NETCASH_OPERATE_RATIO"
           "&filter=(SECURITY_CODE%3D%22" + code + "%22)&pageNumber=1&pageSize=" + str(n) +
           "&sortColumns=REPORT_DATE&sortTypes=-1&source=WEB&client=WEB")
    return get(url).get("result", {}).get("data", []) or []


if __name__ == "__main__":
    args = sys.argv[1:]
    want_cash = "--cash" in args
    codes = [a for a in args if not a.startswith("--")]
    store = {}
    for c in codes:
        try:
            p = perf(c)
            d = {"perf": p}
            if want_cash and p:
                d["cash"] = cash(c)
            store[c] = d
            for row in p[:3]:
                print("%s %s %s | 营收 %.2f亿 (%+.2f%%) | 归母 %.2f亿 (%+.2f%%) | 毛利率 %.2f%% | ROE %.2f%%" % (
                    c, row["SECURITY_NAME_ABBR"], row["REPORTDATE"][:10],
                    row["TOTAL_OPERATE_INCOME"] / 1e8, row["YSTZ"],
                    row["PARENT_NETPROFIT"] / 1e8, row["SJLTZ"],
                    row["XSMLL"] or 0, row["WEIGHTAVG_ROE"] or 0))
            if want_cash:
                for row in store[c].get("cash", [])[:3]:
                    v = row.get("NETCASH_OPERATE")
                    print("     现金流 %s: %s 亿" % (row.get("REPORT_DATE", "")[:10],
                                                  "%.2f" % (v / 1e8) if v is not None else "NA"))
        except Exception as e:
            print("%s ERROR %s" % (c, e))
            store[c] = {"error": str(e)}
        print("-" * 60)
        time.sleep(0.25)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_fin_latest.json")
    try:
        old = json.load(open(out, encoding="utf-8"))
        old.update(store)
        store = old
    except Exception:
        pass
    json.dump(store, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved:", out)
