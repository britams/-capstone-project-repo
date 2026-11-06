# -*- coding: utf-8 -*-
"""daynight.py — 낮에만 처리, 밤에는 전부 가둠 (승준 결정 2026-11-06 20:23, CAP-AI-SJ-46)

승준 결정
- 밤에는 방생하지 않는다. 해 진 뒤 들어온 말벌, 그리고 해 질 때 마킹실에 남아 있던 말벌도 → 상용 트랩 포획통으로 (가둠)
- 아침(해 뜬 뒤)부터만 판별·마킹·급이·방생을 한다.
이유: 방생 굴뚝은 위가 하늘로 열려 낮빛으로 말벌을 위로 이끄는 구조(출구 조명 없음, SJ-45) → 밤엔 말벌이 안 나감.

밤 동작 (CAD 그대로, 부품 추가 없음):
  방생 문 REL 닫힘 / 입구 문 IN 열림 / 격리 문 CAP 열림 → 들어온 말벌은 마킹실을 지나 격리 통로(172) → 포획통.
  조명 끔 → 포획통 쪽(위)이 하늘빛으로 더 밝아 그쪽으로 감 (상용 트랩과 같은 원리)

해 뜸·짐: 날짜로 계산 (NOAA 근사식, 오차 수 분). 위치 기본값 = 공주 (북위 36.46, 동경 127.12), 한국 시간 UTC+9.
  처리 시간 = 해 뜸 + 30분 ~ 해 짐 − 30분 (DAY_MARGIN_MIN). 경계 30분은 굴뚝이 충분히 밝을 때만 방생하려고 둠.
Pi 5는 RTC 배터리(회로 BOM)로 전원이 꺼져도 날짜·시간을 유지.

사용:
    from daynight import is_day, night_mode
    if not is_day(datetime.now()): night_mode(link)      # link = trap_link.TrapLink
시험:  python daynight.py      (11/06 공주 해 뜸·짐 출력 + 판정 시험)
"""
import math
from datetime import datetime, timedelta, timezone

LAT, LON, TZ_H = 36.46, 127.12, 9.0
DAY_MARGIN_MIN = 30


def sun_times(day, lat=LAT, lon=LON, tz_h=TZ_H):
    """그날 해 뜸·해 짐 (현지 시각, datetime). NOAA 일반 근사식 (천정각 90.833°)"""
    n = day.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    la = math.radians(lat)
    cos_ha = math.cos(math.radians(90.833)) / (math.cos(la) * math.cos(decl)) - math.tan(la) * math.tan(decl)
    ha = math.degrees(math.acos(max(-1.0, min(1.0, cos_ha))))
    noon_utc_min = 720 - 4 * lon - eqt
    base = datetime(day.year, day.month, day.day)
    rise = base + timedelta(minutes=noon_utc_min - 4 * ha + tz_h * 60)
    sset = base + timedelta(minutes=noon_utc_min + 4 * ha + tz_h * 60)
    return rise, sset


def is_day(now, margin_min=DAY_MARGIN_MIN):
    """처리해도 되는 시간인가 (해 뜸 + 30분 ~ 해 짐 − 30분)"""
    rise, sset = sun_times(now)
    return rise + timedelta(minutes=margin_min) <= now <= sset - timedelta(minutes=margin_min)


def night_mode(link, log=print):
    """밤: 방생 문 닫고, 입구·격리 문 열어 상용 트랩처럼 전부 포획통으로. 펜은 올림, 바닥은 0."""
    link.pen(True)
    link.move('F', 0.0)
    link.door('REL', 'CLOSE')
    link.door('IN', 'OPEN')
    link.door('CAP', 'OPEN')
    log('NIGHT: 방생 문 닫음, 입구·격리 문 엶 → 전부 포획통으로 (아침까지)')


def day_mode(link, log=print):
    """아침: 격리 문 닫고 입구 문 열어 다시 처리 시작 (방생 문은 닫힌 채)"""
    link.door('CAP', 'CLOSE')
    link.door('REL', 'CLOSE')
    link.door('IN', 'OPEN')
    log('DAY: 처리 시작')


if __name__ == "__main__":
    d = datetime(2026, 11, 6)
    r, s = sun_times(d)
    print("공주 2026-11-06  해 뜸 %s  해 짐 %s" % (r.strftime("%H:%M"), s.strftime("%H:%M")))
    for d2 in (datetime(2026, 6, 21), datetime(2026, 12, 21)):
        r2, s2 = sun_times(d2)
        print("공주 %s  해 뜸 %s  해 짐 %s" % (d2.date(), r2.strftime("%H:%M"), s2.strftime("%H:%M")))
    tests = [(datetime(2026, 11, 6, 7, 10), False), (datetime(2026, 11, 6, 9, 0), True),
             (datetime(2026, 11, 6, 17, 20), False), (datetime(2026, 11, 6, 22, 0), False)]
    ok = all(is_day(t) == want for t, want in tests)
    print("판정 시험", "통과" if ok else "실패", [(t.strftime("%H:%M"), is_day(t)) for t, _ in tests])
