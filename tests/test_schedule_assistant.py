"""
个人日程助手测试模块
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.event_manager import EventManager


class TestEventManager:
    """测试日程管理核心功能"""

    def setup_method(self):
        """每个测试前初始化"""
        self.manager = EventManager(data_file="data/test_events.json")
        # 清空测试数据
        self.manager.events = {}
        self.manager._save_events()

    def teardown_method(self):
        """每个测试后清理"""
        test_file = Path("data/test_events.json")
        if test_file.exists():
            test_file.unlink()

    def test_add_event(self):
        """测试添加日程"""
        result = self.manager.add_event(
            title="团队周会",
            start_time="2026-03-10 15:00",
            end_time="2026-03-10 16:00",
            description="讨论 Q2 计划",
            location="会议室 A"
        )
        assert result["status"] == "success"
        assert "event_id" in result
        assert "已创建日程" in result["message"]

    def test_add_event_with_conflict(self):
        """测试添加冲突日程"""
        # 先添加一个日程
        self.manager.add_event("团队会议", "2026-03-15 10:00", "2026-03-15 11:00")

        # 尝试添加时间重叠的日程
        result = self.manager.add_event("面试", "2026-03-15 10:30", "2026-03-15 11:30")

        assert result["status"] == "conflict"
        assert "团队会议" in result["message"]
        assert len(result["conflicts"]) == 1

    def test_add_event_no_conflict(self):
        """测试添加不冲突的日程"""
        # 添加一个日程
        self.manager.add_event("会议 A", "2026-03-15 10:00", "2026-03-15 11:00")

        # 添加紧接其后的日程（不冲突）
        result = self.manager.add_event("会议 B", "2026-03-15 11:00", "2026-03-15 12:00")

        assert result["status"] == "success"

    def test_query_events(self):
        """测试查询日程"""
        # 先添加一些测试数据
        self.manager.add_event("测试会议 1", "2026-03-15 10:00", "2026-03-15 11:00")
        self.manager.add_event("测试会议 2", "2026-03-20 14:00", "2026-03-20 15:00")

        result = self.manager.query_events(
            start_date="2026-03-01",
            end_date="2026-03-31"
        )
        assert result["status"] == "success"
        assert "events" in result
        assert result["count"] == 2

    def test_query_events_with_keyword(self):
        """测试带关键词查询"""
        self.manager.add_event("团队会议", "2026-03-15 10:00", "2026-03-15 11:00", description="重要讨论")
        self.manager.add_event("个人日程", "2026-03-20 14:00", "2026-03-20 15:00")

        result = self.manager.query_events(
            start_date="2026-03-01",
            end_date="2026-03-31",
            keyword="团队"
        )
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["events"][0]["title"] == "团队会议"

    def test_modify_event(self):
        """测试修改日程"""
        # 先添加
        add_result = self.manager.add_event("测试会议", "2026-03-15 10:00", "2026-03-15 11:00")
        event_id = add_result["event_id"]

        # 再修改
        modify_result = self.manager.modify_event(
            event_id=event_id,
            title="修改后的会议"
        )
        assert modify_result["status"] == "success"

        # 验证修改
        query_result = self.manager.query_events("2026-03-01", "2026-03-31")
        event = next(e for e in query_result["events"] if e["event_id"] == event_id)
        assert event["title"] == "修改后的会议"

    def test_delete_event(self):
        """测试删除日程"""
        add_result = self.manager.add_event("临时会议", "2026-03-20 14:00", "2026-03-20 15:00")
        event_id = add_result["event_id"]

        delete_result = self.manager.delete_event(event_id=event_id)
        assert delete_result["status"] == "success"

        # 验证已删除
        query_result = self.manager.query_events("2026-03-01", "2026-03-31")
        assert query_result["count"] == 0

    def test_delete_nonexistent_event(self):
        """测试删除不存在的日程"""
        result = self.manager.delete_event(event_id="nonexistent")
        assert result["status"] == "error"
        assert "未找到" in result["message"]

    def test_modify_nonexistent_event(self):
        """测试修改不存在的日程"""
        result = self.manager.modify_event(event_id="nonexistent", title="新标题")
        assert result["status"] == "error"
        assert "未找到" in result["message"]

    def test_modify_event_with_conflict(self):
        """测试修改日程产生冲突"""
        # 添加两个日程
        result1 = self.manager.add_event("会议 A", "2026-03-15 10:00", "2026-03-15 11:00")
        self.manager.add_event("会议 B", "2026-03-15 14:00", "2026-03-15 15:00")

        # 尝试将会议 A 改到与会议 B 冲突的时间
        result = self.manager.modify_event(
            event_id=result1["event_id"],
            start_time="2026-03-15 14:30",
            end_time="2026-03-15 15:30"
        )

        assert result["status"] == "conflict"
        assert "会议 B" in result["message"]

    def test_modify_event_exclude_self(self):
        """测试修改日程时排除自身（不产生假冲突）"""
        # 添加一个日程
        result1 = self.manager.add_event("会议 A", "2026-03-15 10:00", "2026-03-15 11:00")

        # 修改自己的时间（应该成功，不与自己冲突）
        result = self.manager.modify_event(
            event_id=result1["event_id"],
            start_time="2026-03-15 09:00",
            end_time="2026-03-15 10:00"
        )

        assert result["status"] == "success"

    def test_check_conflict_method(self):
        """测试冲突检测方法"""
        # 添加一个日程
        self.manager.add_event("会议 A", "2026-03-15 10:00", "2026-03-15 11:00")

        # 检测重叠时间段
        conflicts = self.manager.check_conflict("2026-03-15 10:30", "2026-03-15 11:30")
        assert len(conflicts) == 1
        assert conflicts[0]["title"] == "会议 A"

        # 检测不重叠时间段
        conflicts = self.manager.check_conflict("2026-03-15 11:00", "2026-03-15 12:00")
        assert len(conflicts) == 0

        # 检测完全包含时间段
        conflicts = self.manager.check_conflict("2026-03-15 09:30", "2026-03-15 11:30")
        assert len(conflicts) == 1


class TestScheduleParser:
    """测试日程解析器"""

    def setup_method(self):
        from src.doc_parser import ScheduleParser
        self.parser = ScheduleParser()

    def test_extract_title(self):
        """测试标题提取"""
        title = self.parser._extract_title("明天下午 3 点团队会议")
        assert title == "团队会议"

    def test_extract_time_with_date(self):
        """测试时间提取 - 日期格式"""
        text = "2026-03-10 15:00~16:00 团队会议"
        time_info = self.parser._extract_time(text)
        assert time_info["raw"] != ""

    def test_extract_time_with_relative(self):
        """测试时间提取 - 相对时间"""
        # 支持 HH:MM 格式
        text = "明天 15:00 开会"
        time_info = self.parser._extract_time(text)
        assert time_info["raw"] != ""

        # 支持中文时间格式
        text = "明天下午3点开会"
        time_info = self.parser._extract_time(text)
        assert time_info["raw"] != ""

    def test_normalize_chinese_time(self):
        """测试中文时间标准化"""
        # 下午3点 -> 15:00
        result = self.parser.normalize_time("明天下午3点")
        assert "15:00" in result

        # 上午9点 -> 09:00
        result = self.parser.normalize_time("明天上午9点")
        assert "09:00" in result

        # 晚上8点半 -> 20:30
        result = self.parser.normalize_time("晚上8点半")
        assert "20:30" in result

    def test_normalize_time_relative(self):
        """测试时间标准化 - 相对时间"""
        normalized = self.parser.normalize_time("明天 15:00")
        assert len(normalized) == 16  # YYYY-MM-DD HH:MM

    def test_normalize_time_standard(self):
        """测试时间标准化 - 标准格式"""
        normalized = self.parser.normalize_time("2026-03-10 15:00")
        assert normalized == "2026-03-10 15:00"

    def test_parse_chat_log(self):
        """测试聊天记录解析"""
        chat_text = """
        张三：我们明天下午 3 点开会讨论项目
        李四：好的，会议地点在哪里？
        张三：在会议室 A，大概一个小时
        """
        schedules = self.parser.parse_chat_log(chat_text)
        assert isinstance(schedules, list)

    def test_parse_markdown_file(self, tmp_path):
        """测试 Markdown 文件解析"""
        md_content = """
        # 项目计划

        ## 日程安排
        - 2026-03-10 15:00~16:00 团队会议
        - 2026-03-15 10:00~11:00 项目评审
        """
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding='utf-8')

        schedules = self.parser.parse_markdown_file(str(md_file))
        assert isinstance(schedules, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
