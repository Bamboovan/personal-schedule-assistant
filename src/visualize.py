"""日程可视化模块。

提供 ASCII 风格的日程视图渲染。

示例:
    >>> from src.visualize import render_week_view
    >>> print(render_week_view(events))
"""
from datetime import datetime, timedelta
from typing import Any


def get_week_bounds(date: datetime | None = None) -> tuple[datetime, datetime]:
    """获取指定日期所在周的起止日期。

    Args:
        date: 参考日期，默认为今天

    Returns:
        (周一开始, 周日结束)
    """
    if date is None:
        date = datetime.now()

    # 找到本周一
    monday = date - timedelta(days=date.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # 找到本周日
    sunday = monday + timedelta(days=6)

    return monday, sunday


def render_week_view(events: list[dict[str, Any]], week_date: datetime | None = None) -> str:
    """渲染 ASCII 周视图。

    Args:
        events: 日程列表，每个日程包含 title, start_time, end_time
        week_date: 参考日期，默认为今天

    Returns:
        ASCII 格式的周视图字符串
    """
    if not events:
        return "本周没有日程安排"

    # 获取周的起止
    monday, sunday = get_week_bounds(week_date)

    # 按天分组日程
    days_events: dict[int, list[dict[str, Any]]] = {i: [] for i in range(7)}

    for event in events:
        try:
            event_date = datetime.strptime(event['start_time'], "%Y-%m-%d %H:%M")
            day_offset = (event_date - monday).days
            if 0 <= day_offset < 7:
                days_events[day_offset].append(event)
        except (ValueError, KeyError):
            continue

    # 每天按时间排序
    for day in days_events:
        days_events[day].sort(key=lambda e: e.get('start_time', ''))

    # 星期名称
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    # 构建输出
    lines: list[str] = []

    # 标题
    week_num = monday.isocalendar()[1]
    month = monday.month
    lines.append("╔" + "═" * 58 + "╗")
    title = f"{month}月第{week_num}周日程"
    lines.append(f"║{title:^56}║")
    lines.append("╠" + "═" * 8 + "╦" + "═" * 8 + "╦" + "═" * 8 + "╦" + "═" * 8 + "╦" + "═" * 8 + "╦" + "═" * 8 + "╣")

    # 星期标题行
    header = "║"
    for name in weekday_names[:5]:
        header += f"{name:^8}║"
    header += f"{'周末':^8}║"
    lines.append(header)

    lines.append("╠" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "╬" + "═" * 8 + "╣")

    # 日程内容行（最多显示 3 行日程）
    max_rows = 3
    for row in range(max_rows):
        line = "║"
        for day_idx in range(7):
            day_events = days_events[day_idx]
            if row < len(day_events):
                event = day_events[row]
                # 提取时间
                time_str = event.get('start_time', '')[-5:] if event.get('start_time') else ''
                title = event.get('title', '')[:6]  # 限制标题长度
                cell = f"{time_str} {title}"
            else:
                cell = ""
            line += f"{cell:^8}║"
        lines.append(line)

    lines.append("╚" + "═" * 8 + "╩" + "═" * 8 + "╩" + "═" * 8 + "╩" + "═" * 8 + "╩" + "═" * 8 + "╩" + "═" * 8 + "╝")

    # 详细日程列表
    lines.append("")
    lines.append("详细日程：")
    lines.append("-" * 40)

    for day_idx in range(7):
        day_date = monday + timedelta(days=day_idx)
        day_events = days_events[day_idx]
        if day_events:
            lines.append(f"【{weekday_names[day_idx]} {day_date.strftime('%m/%d')}】")
            for event in day_events:
                start = event.get('start_time', '')[-5:] if event.get('start_time') else '??:??'
                end = event.get('end_time', '')[-5:] if event.get('end_time') else '??:??'
                title = event.get('title', '未命名')
                location = event.get('location', '')
                loc_str = f" [{location}]" if location else ""
                lines.append(f"  {start}-{end} {title}{loc_str}")
            lines.append("")

    return "\n".join(lines)


def render_day_view(events: list[dict[str, Any]], date: datetime | None = None) -> str:
    """渲染单日视图。

    Args:
        events: 当天的日程列表
        date: 日期，默认为今天

    Returns:
        ASCII 格式的单日视图字符串
    """
    if not events:
        return "今天没有日程安排"

    if date is None:
        date = datetime.now()

    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekday_names[date.weekday()]

    lines: list[str] = []
    lines.append(f"┌{'─' * 38}┐")
    lines.append(f"│{date.strftime('%Y年%m月%d日')} {weekday:^4}{' ' * 12}│")
    lines.append(f"├{'─' * 38}┤")

    for event in events:
        start = event.get('start_time', '')[-5:] if event.get('start_time') else '??:??'
        end = event.get('end_time', '')[-5:] if event.get('end_time') else '??:??'
        title = event.get('title', '未命名')
        location = event.get('location', '')

        time_str = f"{start}-{end}"
        loc_str = f" @{location}" if location else ""
        content = f" {time_str} {title}{loc_str}"

        if len(content) > 37:
            content = content[:34] + "..."

        lines.append(f"│{content:<38}│")

    lines.append(f"└{'─' * 38}┘")

    return "\n".join(lines)