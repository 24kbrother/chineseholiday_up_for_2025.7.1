#!/usr/local/bin/python3
# coding=utf-8
#holiday 模块：1.从服务端获取数据并、2.存入数据库 3.从数据库读数库

import os
import re
import datetime
import logging
_LOGGER = logging.getLogger(__name__)

ICS_DIR = os.path.dirname(os.path.realpath(__file__))
LUNAR_ICS = os.path.join(ICS_DIR, 'cal_lunar.ics')
FESTIVAL_ICS = os.path.join(ICS_DIR, 'cal_festival.ics')
HOLIDAY_ICS = os.path.join(ICS_DIR, 'cal_holiday.ics')
SOLARTERM_ICS = os.path.join(ICS_DIR, 'cal_solarTerm.ics')

def parse_ics_events(filepath):
    events = []
    if not os.path.exists(filepath):
        _LOGGER.warning(f"ICS file not found: {filepath}")
        return events
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    events_data = re.findall(r'BEGIN:VEVENT(.*?)END:VEVENT', content, re.DOTALL)
    for event_block in events_data:
        event = {}
        for line in event_block.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.split(';')[0]
                event[key.strip()] = value.strip()
        events.append(event)
    return events

def find_today_event(events):
    today = datetime.datetime.now().strftime('%Y%m%d')
    for e in events:
        dt = e.get('DTSTART', '')
        if dt.startswith(today):
            return e.get('SUMMARY', ''), e.get('DESCRIPTION', '')
    return '', ''

def find_next_event(events):
    today = datetime.datetime.now().date()
    min_days = 9999
    next_summary = ''
    for e in events:
        dt = e.get('DTSTART', '')
        try:
            d = datetime.datetime.strptime(dt[:8], '%Y%m%d').date()
            delta = (d - today).days
            if delta > 0 and delta < min_days:
                min_days = delta
                next_summary = e.get('SUMMARY', '')
        except Exception:
            continue
    return next_summary, min_days if next_summary else ('', '')

def find_next_holiday_event(events):
    today = datetime.datetime.now().date()
    min_days = 9999
    next_summary = ''
    next_desc = ''
    for e in events:
        summary = e.get('SUMMARY', '')
        desc = e.get('DESCRIPTION', '')
        if '假期' in summary and '补班' not in summary:
            dt = e.get('DTSTART', '')
            try:
                d = datetime.datetime.strptime(dt[:8], '%Y%m%d').date()
                delta = (d - today).days
                if delta > 0 and delta < min_days:
                    min_days = delta
                    # 提取「」内内容并去掉“假期”
                    match = re.search(r'「(.*?)」', summary)
                    if match:
                        value = match.group(1).replace('假期', '')
                        next_summary = value
                    else:
                        next_summary = summary.replace('假期', '')
                    # 提取描述
                    desc = re.sub(r'^[一二三四五六七八九十]+、', '', desc)
                    if '：' in desc:
                        desc = desc.split('：', 1)[1]
                    desc = desc.split('放假通知')[0].split('更新时间')[0].strip()
                    next_desc = desc
            except Exception:
                continue
    return next_summary, min_days if next_summary else ('', ''), next_desc

class Holiday:
    def __init__(self):
        # 节气
        solar_term_events = parse_ics_events(SOLARTERM_ICS)
        self._solar_term, _ = find_today_event(solar_term_events)
        self._next_solar_term, self._next_solar_term_days = find_next_event(solar_term_events)
        # 纪念日
        festival_events = parse_ics_events(FESTIVAL_ICS)
        self._festival, self._festival_desc = find_today_event(festival_events)
        # 节日
        holiday_events = parse_ics_events(HOLIDAY_ICS)
        self._holiday, self._holiday_desc = find_today_event(holiday_events)
        self._next_holiday, self._next_holiday_days, self._next_holiday_desc = find_next_holiday_event(holiday_events)

    @property
    def attributes(self):
        return {
            '节气': self._solar_term,
            '下一个节气': self._next_solar_term,
            '下一个节气还有': self._next_solar_term_days if self._next_solar_term else '',
            '纪念日': self._festival,
            '纪念日描述': self._festival_desc,
            '节日': self._holiday,
            '节日描述': self._holiday_desc,
            '下一个节日': self._next_holiday,
            '下一个节日还有': self._next_holiday_days if self._next_holiday else '',
            '下一个节日的描述': self._next_holiday_desc,
            '节假日放假详情': f"{self._holiday} {self._holiday_desc}" if self._holiday else "今天非节日"
        }

    def is_holiday(self, date=None):
        """兼容旧接口，判断指定日期是否为法定节假日"""
        if date is None:
            date = datetime.datetime.now().strftime('%Y%m%d')
        events = parse_ics_events(HOLIDAY_ICS)
        for e in events:
            dt = e.get('DTSTART', '')
            if dt.startswith(date):
                return True
        return False

    def is_holiday_status(self, date):
        """兼容旧接口，返回0/1/2，0为工作日，1为休息日，2为节假日"""
        if self.is_holiday(date.strftime('%Y%m%d')):
            return 2
        return 0

    def is_holiday_today(self):
        """判断今天是否为节假日（法定节假日）"""
        return self.is_holiday()

    def is_holiday_tomorrow(self):
        """判断明天是否为节假日（法定节假日）"""
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d')
        return self.is_holiday(tomorrow)

    def getHoliday(self, days=1):
        """兼容旧接口，返回今天的法定节假日（dict格式，key为日期字符串，value为节日名）"""
        today = datetime.datetime.now().strftime('%Y%m%d')
        if self._holiday:
            return {today: self._holiday}
        else:
            return {}

    def nearest_holiday_info(self, min_days=12, max_days=45):
        """兼容旧接口，返回未来min_days~max_days天内最近的法定节假日信息字符串"""
        events = parse_ics_events(HOLIDAY_ICS)
        today = datetime.datetime.now().date()
        nearest = None
        nearest_days = None
        for e in events:
            dt = e.get('DTSTART', '')
            try:
                d = datetime.datetime.strptime(dt[:8], '%Y%m%d').date()
                delta = (d - today).days
                if min_days <= delta <= max_days:
                    if nearest is None or (nearest_days is not None and delta < nearest_days):
                        nearest = e
                        nearest_days = delta
            except Exception:
                continue
        if nearest:
            return f"{nearest.get('SUMMARY', '')} {nearest.get('DESCRIPTION', '')} 还有{nearest_days}天"
        else:
            return "未来无节日"
