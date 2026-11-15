#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, subprocess, datetime, os

TZ = datetime.timezone(datetime.timedelta(hours=8))
CAL = "feishu.cn_SWi1Uv0eKz1ZL9wRrLYoEe@group.calendar.feishu.cn"

def ts(s):
    return str(int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp()))

def ev(summary, start, end, location, desc, reminders):
    return {
        "summary": summary,
        "description": desc,
        "start_time": {"timestamp": ts(start), "timezone": "Asia/Shanghai"},
        "end_time": {"timestamp": ts(end), "timezone": "Asia/Shanghai"},
        "location": {"name": location},
        "reminders": [{"minutes": m} for m in reminders],
        "visibility": "default",
    }

DESC_JN = """**报名链接**：https://cbgc.scol.com.cn/news/8040335
**评分依据**：W1 35（决赛向投资与产业评委路演）；W2 14（无成立年限与财报门槛，需BP与路演PPT）；W3 15（金牛主城当天往返）；W4 12（区人社局等区级政府）；W5 15（8分钟路演+5分钟问答）。
**建议动作**：申请路演
**已知联系人**：段老师 17380134636；官方QQ群 1107052737
**准备材料**：报名表、负责人身份证复印件、营业执照扫描件、商业计划书、路演PPT"""

DESC_JN_DL = """**截止**：2026-11-19 23:59（今日为最后核对节点）
**准备材料**：报名表、负责人身份证复印件、营业执照扫描件、商业计划书、路演PPT
**入口**：https://cbgc.scol.com.cn/news/8040335（报名表+官方QQ群1107052737）
**入场方式**：决赛地点由主办方另行通知，报名后留意群公告
**T-3（11/16）**：完成BP终稿、路演PPT定版
**T-1（11/18）**：提交全部材料并电话确认收件"""

DESC_JN_DAY = """**今天去哪**：成都市金牛区决赛现场（具体地点以主办方通知为准）
**目标见谁**：区人社局/区科技局评委、投资机构评委、参赛企业创始人
**重点聊什么**：用校园与赛事两条线的成片案例讲清“5机位+AI成片55元/条”的成本优势，争取赛后一对一"""

DESC_ZJ = """**报名链接**：https://cs.huodongxing.com/event/9881944494611
**评分依据**：W1 35（投资机构合伙人到场评审对接）；W2 8（观众报名条件未公布，需致电协办方）；W3 15（高新区主城当天往返）；W4 15（浙江省商务厅联合四川省商务厅）；W5 6（路演名额已定，只能听会与自由交流）。
**建议动作**：报名
**已知联系人**：协办方 毕友·百鲲资本（活动页未留电话，需通过活动行私信）"""

DESC_ZJ_DAY = """**今天去哪**：成都高新区天府四街158号OCG国际会议中心A座4楼易上厅
**目标见谁**：四川省商务厅相关处室、投资机构合伙人、AI路演项目创始人
**重点聊什么**：以“AI自动成片+定点摄像头”切入文旅与赛事影像，寻找可嫁接到电商内容生产的合作方"""

DESC_LC = """**报名链接**：https://cs.huodongxing.com/event/9883675698300
**评分依据**：W1 35（路演对接天使/种子投资人与产业基金）；W2 8（路演门槛未公开，需致电孵化器）；W3 15（成都主城当天往返）；W4 3（民营孵化器）；W5 15（公开招募路演项目）。
**建议动作**：申请路演
**已知联系人**：盈创星空金融科技孵化器（活动页未留电话，需活动行私信）"""

DESC_LC_DAY = """**今天去哪**：四川成都（具体场馆以主办方通知为准）
**目标见谁**：天使/种子投资人、产业基金合伙人、同场路演项目创始人
**重点聊什么**：用55元/条的成片报价与学校年包1.7-2.8万模型讲单位经济性，争取3个月内可签约的试点"""

EVENTS = [
    ("【A1 大赛与路演·91】成都市金牛区2026年“未来产业、数字经济”就业创业大赛暨“蓉漂杯”创新创业大赛",
     "2026-11-27 09:00", "2026-11-27 18:00", "成都市金牛区（决赛地点另行通知）", DESC_JN, [30]),
    ("报名截止｜成都市金牛区2026年“未来产业、数字经济”就业创业大赛暨“蓉漂杯”创新创业大赛",
     "2026-11-19 09:00", "2026-11-19 09:30", "线上提交", DESC_JN_DL, [10080, 4320, 1440]),
    ("【今天去哪】金牛大赛决赛：见评委与投资机构",
     "2026-11-27 08:00", "2026-11-27 08:30", "成都市金牛区（决赛地点另行通知）", DESC_JN_DAY, [0]),
    ("【A1 大赛与路演·79】之江创客2026全球电子商务创业创新大赛西南赛区决赛",
     "2026-11-18 13:30", "2026-11-18 17:30", "成都市高新区天府四街158号OCG国际会议中心A座4楼易上厅", DESC_ZJ, [60]),
    ("【今天去哪】之江创客西南赛区决赛：见投资机构",
     "2026-11-18 08:00", "2026-11-18 08:30", "成都市高新区天府四街158号OCG国际会议中心A座4楼易上厅", DESC_ZJ_DAY, [0]),
    ("【A2 基金对接·76】【路演项目招募】绿色低碳产业投融资对接会",
     "2026-11-25 14:00", "2026-11-25 17:00", "四川成都（具体场馆未公开）", DESC_LC, [60]),
    ("【今天去哪】绿色低碳产业投融资对接会：争取路演名额",
     "2026-11-25 08:00", "2026-11-25 08:30", "四川成都（具体场馆未公开）", DESC_LC_DAY, [0]),
]

out = []
for i, (summary, s, e, loc, desc, rem) in enumerate(EVENTS, 1):
    body = ev(summary, s, e, loc, desc, rem)
    p = "/tmp/ev_%d.json" % i
    json.dump(body, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run(["lark-cli", "calendar", "events", "create", "--calendar-id", CAL,
                        "--data", "@" + p, "--as", "user", "--format", "json"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        ok = d.get("ok")
        eid = (d.get("data", {}).get("event") or {}).get("event_id")
        print(i, ok, eid, summary[:30])
    except Exception:
        print(i, "ERR", r.stdout[:300], r.stderr[:200])
    out.append({"summary": summary, "raw": r.stdout})
json.dump(out, open("/workspace/calendar_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
