# /astrbot_plugin_2class_notify/services/class2_api.py

import aiohttp
from typing import Optional, Dict, List, Any
from astrbot.core import logger


class Class2API:
    """第二课堂API服务"""

    # 课程状态映射 (基于 sign_status)
    SIGN_STATUS_MAP = {
        0: "未上架",
        1: "未开始",
        2: "进行中",
        3: "已结束",
        4: "已下架"
    }

    def __init__(self, config):
        self.config = config
        self.base_url = config.api_domain.rstrip("/")
        self.token = config.api_token
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建session"""
        if self.session is None or self.session.closed:
            headers = {
                "Content-Type": "application/json",
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session

    async def close(self):
        """关闭session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_course_list(self, page: int = 1, limit: int = 200) -> Optional[Dict[str, Any]]:
        """
        获取课程列表
        
        Args:
            page: 页码
            limit: 每页数量
            
        Returns:
            课程列表响应数据
        """
        try:
            session = await self._get_session()
            params = {"page": page, "limit": limit}
            
            async with session.get("/api/course/list", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"获取课程列表失败: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取课程列表异常: {e}")
            return None

    async def get_course_detail(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        获取课程详情
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程详情数据
        """
        try:
            session = await self._get_session()
            
            async with session.get(f"/api/course/info/{course_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"获取课程详情失败 (ID: {course_id}): HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取课程详情异常 (ID: {course_id}): {e}")
            return None

    def format_course_info(self, course: Dict[str, Any], index: int = 0) -> str:
        """
        格式化课程信息为Markdown格式
        
        Args:
            course: 课程数据
            index: 序号（用于列表显示）
            
        Returns:
            格式化后的Markdown文本
        """
        sign_status = course.get("sign_status", -1)
        status_text = self.SIGN_STATUS_MAP.get(sign_status, "未知")
        
        # 状态emoji
        status_emoji = {
            2: "🟢",  # 进行中
            1: "🟡",  # 未开始
            0: "⚪",  # 未上架
        }.get(sign_status, "🔴")  # 已结束/已下架
        
        lines = []
        
        # 标题行
        if index > 0:
            lines.append(f"## {index}. {course.get('title', '未知课程')}")
        else:
            lines.append(f"## {course.get('title', '未知课程')}")
        
        # 状态
        if status_emoji:
            lines.append(f"**状态**: {status_emoji} {status_text}")
        else:
            lines.append(f"**状态**: {status_text}")
        
        # 课程ID
        if course.get("id"):
            lines.append(f"**🆔 ID**: {course['id']}")
        
        # 分类
        if course.get("transcript_index") and course["transcript_index"].get("transcript_name"):
            lines.append(f"**📂 分类**: {course['transcript_index']['transcript_name']}")
        
        # 类型
        if course.get("transcript_index_type") and course["transcript_index_type"].get("transcript_type_name"):
            lines.append(f"**🏷️ 类型**: {course['transcript_index_type']['transcript_type_name']}")
        
        # 报名时间
        if course.get("sign_start_time") and course.get("sign_end_time"):
            lines.append(f"**📅 报名时间**: {course['sign_start_time']} ~ {course['sign_end_time']}")
        
        # 活动时间
        if course.get("sign_in_start_time") and course.get("sign_out_end_time"):
            lines.append(f"**🕐 活动时间**: {course['sign_in_start_time']} ~ {course['sign_out_end_time']}")
        
        # 时间地点
        if course.get("time_place"):
            time_place = course["time_place"].replace("\r\n", " ").replace("\n", " ")
            lines.append(f"**⏰ 时间地点**: {time_place}")
        
        # 人数信息
        if course.get("course_apply_count") is not None and course.get("max"):
            remaining = course["max"] - course["course_apply_count"]
            lines.append(f"**👥 人数**: {course['course_apply_count']}/{course['max']} (剩余: {remaining})")
        
        # 积分
        if course.get("score"):
            lines.append(f"**⭐ 积分**: {course['score']} 分")
        
        # 完成要求
        if course.get("completion_flag_text"):
            lines.append(f"**✅ 完成**: {course['completion_flag_text']}")
        
        # 主办单位
        if course.get("department"):
            lines.append(f"**🏢 主办**: {course['department']}")
        
        # 联系方式
        if course.get("connect"):
            lines.append(f"**📞 联系**: {course['connect']}")
        
        return "\n\n".join(lines)

    def filter_courses_by_status(self, courses: List[Dict[str, Any]], status_list: List[int]) -> List[Dict[str, Any]]:
        """
        根据报名状态筛选课程
        
        Args:
            courses: 课程列表
            status_list: 状态列表 (0-未上架, 1-未开始, 2-进行中, 3-已结束, 4-已下架)
            
        Returns:
            筛选后的课程列表
        """
        return sorted([
            course for course in courses
            if course.get("sign_status") in status_list
        ], 
          key=lambda x: x.get("sign_status", -1),
        )
