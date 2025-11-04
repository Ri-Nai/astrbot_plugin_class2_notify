# /astrbot_plugin_class2_notify/handlers/chat_handler.py

from astrbot.api.event import AstrMessageEvent
from astrbot.api import html_renderer
from astrbot.core import logger
from ..services import Class2API
from ..utils.templates import COURSE_LIST_TEMPLATE


class ChatHandler:
    """聊天处理器：负责处理用户的课程查询请求"""

    def __init__(self, config, api_service: Class2API):
        self.config = config
        self.api_service = api_service

    def _prepare_course_data(self, course: dict) -> dict:
        """
        准备课程数据用于模板渲染

        Args:
            course: 原始课程数据

        Returns:
            格式化后的课程数据
        """
        sign_status = course.get("sign_status", -1)

        # 格式化报名时间
        sign_time = None
        if course.get("sign_start_time") and course.get("sign_end_time"):
            sign_time = f"{course['sign_start_time']} ~ {course['sign_end_time']}"

        # 格式化活动时间
        activity_time = None
        if course.get("sign_in_start_time") and course.get("sign_out_end_time"):
            activity_time = (
                f"{course['sign_in_start_time']} ~ {course['sign_out_end_time']}"
            )

        # 计算剩余名额
        remaining = 0
        show_people_info = False
        if course.get("course_apply_count") is not None and course.get("max"):
            remaining = course["max"] - course["course_apply_count"]
            show_people_info = True

        # 处理时间地点
        time_place = None
        if course.get("time_place"):
            time_place = course["time_place"].replace("\r\n", " ").replace("\n", " ")

        return {
            "id": course.get("id", ""),
            "title": course.get("title", "未知课程"),
            "cover_url": course.get("cover_url", ""),
            "sign_status": sign_status,
            "status_text": self.api_service.SIGN_STATUS_MAP.get(sign_status, "未知"),
            "category": course.get("transcript_index", {}).get("transcript_name", ""),
            "type": course.get("transcript_index_type", {}).get(
                "transcript_type_name", ""
            ),
            "score": course.get("score", 0),
            "department": course.get("department", ""),
            "sign_time": sign_time,
            "activity_time": activity_time,
            "time_place": time_place,
            "apply_count": course.get("course_apply_count", 0),
            "max_people": course.get("max", 0),
            "remaining": remaining,
            "show_people_info": show_people_info,
            "completion": course.get("completion_flag_text", ""),
            "connect": course.get("connect", ""),
        }

    async def process_course_query(
        self,
        event: AstrMessageEvent,
        status_arg: str = None,
    ):
        """
        处理课程查询请求

        Args:
            event: 消息事件
            status_arg: 状态参数 (0, 1, 2 或 all)

        Yields:
            处理结果消息
        """
        # 解析状态参数
        if status_arg is None or status_arg == "":
            # 使用默认的状态过滤
            status_list = self.config.sign_status_filter
        elif status_arg.lower() == "all":
            # 显示所有状态
            status_list = [0, 1, 2, 3, 4]
        else:
            # 解析用户指定的状态
            try:
                # 支持逗号分隔的多个状态，如 "0,1,2"
                status_list = [
                    int(s.strip()) for s in status_arg.split(",") if s.strip().isdigit()
                ]
                if not status_list:
                    yield event.plain_result(
                        "状态参数错误！\n"
                        "用法：/第二课堂 [状态]\n"
                        "状态可选：0(未上架), 1(未开始), 2(进行中), 3(已结束), 4(已下架), all(全部)\n"
                        "示例：/第二课堂 0,1,2"
                    )
                    return
            except ValueError:
                yield event.plain_result(
                    "状态参数格式错误！\n"
                    "用法：/第二课堂 [状态]\n"
                    "状态可选：0(未上架), 1(未开始), 2(进行中), 3(已结束), 4(已下架), all(全部)"
                )
                return

        # 获取课程列表
        yield event.plain_result("正在查询第二课堂课程...")

        try:
            response = await self.api_service.get_course_list(page=1, limit=200)

            if not response or not response.get("data"):
                yield event.plain_result("获取课程列表失败，请稍后重试。")
                return

            all_courses = response["data"].get("items", [])

            if not all_courses:
                yield event.plain_result("暂无课程数据。")
                return

            # 根据状态筛选课程
            filtered_courses = self.api_service.filter_courses_by_status(
                all_courses, status_list
            )

            if not filtered_courses:
                status_names = [
                    self.api_service.SIGN_STATUS_MAP.get(s, str(s)) for s in status_list
                ]
                yield event.plain_result(
                    f"没有找到状态为 {', '.join(status_names)} 的课程。\n"
                    f"当前共有 {len(all_courses)} 个课程。"
                )
                return

            # 准备渲染数据
            display_count = min(len(filtered_courses), 10)
            courses_data = [
                self._prepare_course_data(course)
                for course in filtered_courses[:display_count]
            ]

            template_data = {
                "courses": courses_data,
                "total_count": len(filtered_courses),
                "display_count": display_count,
            }

            # 使用 HTML 模板渲染
            try:
                # 渲染选项：高质量 PNG 图片
                options = {
                    "full_page": True,
                }

                image_url = await html_renderer.render_custom_template(
                    COURSE_LIST_TEMPLATE,
                    template_data,
                    options=options,
                )
                yield event.image_result(image_url)

            except Exception as e:
                logger.error(f"生成课程列表图片失败: {e}")
                # 图片生成失败时，回退到文本形式
                fallback_message = (
                    f"📚 第二课堂课程列表\n\n共 {len(filtered_courses)} 个课程\n\n"
                )
                for idx, course in enumerate(filtered_courses[:display_count], 1):
                    fallback_message += f"{idx}. {course.get('title', '未知课程')}\n"
                    fallback_message += f"   状态: {self.api_service.SIGN_STATUS_MAP.get(course.get('sign_status'), '未知')}\n\n"

                if len(filtered_courses) > display_count:
                    fallback_message += (
                        f"\n还有 {len(filtered_courses) - display_count} 个课程未显示"
                    )

                yield event.plain_result(fallback_message)

        except Exception as e:
            logger.error(f"查询课程失败: {e}")
            yield event.plain_result("查询课程时出现错误，请稍后重试。")
