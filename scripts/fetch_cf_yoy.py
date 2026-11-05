#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取单公司多期经营现金流(用于同比),输出 2025Q3 vs 2026Q3 累计对比。"""
import json, urllib.request, sys, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://data.eastmoney.com/"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))


def cash(code, n=8):
    url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_CASHFLOW"
           "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORT_DATE,NETCASH_OPERATE"
           "&filter=(SECURITY_CODE%3D%22" + code + "%22)&pageNumber=1&pageSize=" + str(n) +
           "&sortColumns=REPORT_DATE&sortTypes=-1&source=WEB&client=WEB")
    return get(url).get("result", {}).get("data", []) or []


def perf(code, n=8):
    url = ("https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD"
           "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,REPORTDATE,TOTAL_OPERATE_INCOME,YSTZ,"
           "PARENT_NETPROFIT,SJLTZ,XSMLL"
           "&filter=(SECURITY_CODE%3D%22" + code + "%22)&pageNumber=1&pageSize=" + str(n) +
           "&sortColumns=REPORTDATE&sortTypes=-1&source=WEB&client=WEB")
    return get(url).get("result", {}).get("data", []) or []


for c in sys.argv[1:]:
    print("=" * 70)
    p = {r["REPORTDATE"][:10]: r for r in perf(c)}
    cf = {r["REPORT_DATE"][:10]: r.get("NETCASH_OPERATE") for r in cash(c)}
    name = next(iter(p.values()))["SECURITY_NAME_ABBR"] if p else c
    print(name, c)
    for d in ("2026-09-30", "2025-09-30", "2026-06-30", "2025-06-30"):
        r = p.get(d)
        cv = cf.get(d)
        if r:
            print("  %s 营收 %.2f亿(%+.2f%%) 归母 %.2f亿(%+.2f%%) 毛利率 %.2f%% | 经营现金流 %s" % (
                d, r["TOTAL_OPERATE_INCOME"] / 1e8, r["YSTZ"] or 0,
                r["PARENT_NETPROFIT"] / 1e8, r["SJLTZ"] or 0, r["XSMLL"] or 0,
                ("%.2f亿" % (cv / 1e8)) if cv is not None else "NA"))
    time.sleep(0.3)
