# /astrbot_plugin_class2_notify/handlers/chat_handler.py

from astrbot.api.event import AstrMessageEvent
from astrbot.api import html_renderer
from astrbot.core import logger
from ..services import Class2API


class ChatHandler:
    """聊天处理器：负责处理用户的课程查询请求"""

    def __init__(self, config, api_service: Class2API):
        self.config = config
        self.api_service = api_service

    async def process_course_query(self, event: AstrMessageEvent, status_arg: str = None):
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
                status_list = [int(s.strip()) for s in status_arg.split(",") if s.strip().isdigit()]
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
            filtered_courses = self.api_service.filter_courses_by_status(all_courses, status_list)

            if not filtered_courses:
                status_names = [self.api_service.SIGN_STATUS_MAP.get(s, str(s)) for s in status_list]
                yield event.plain_result(
                    f"没有找到状态为 {', '.join(status_names)} 的课程。\n"
                    f"当前共有 {len(all_courses)} 个课程。"
                )
                return

            # 格式化课程信息（Markdown格式）
            message_lines = [
                f"# 📚 第二课堂课程列表\n",
                f"**共 {len(filtered_courses)} 个课程**\n"
            ]

            # 最多显示前10个课程
            display_count = min(len(filtered_courses), 10)
            for idx, course in enumerate(filtered_courses[:display_count], 1):
                course_markdown = self.api_service.format_course_info(course, idx)
                message_lines.append(course_markdown)
                message_lines.append("")  # 空行分隔

            if len(filtered_courses) > display_count:
                message_lines.append(f"\n> 还有 {len(filtered_courses) - display_count} 个课程未显示")

            message_lines.append(f"\n> 💡 提示：使用 `/第二课堂 [状态]` 查看不同状态的课程")
            message_lines.append("> 状态：0-未上架, 1-未开始, 2-进行中, 3-已结束, 4-已下架")

            message = "\n".join(message_lines)
            
            # 生成图片
            try:
                image_url = await html_renderer.render_t2i(message)
                yield event.image_result(image_url)
            except Exception as e:
                logger.error(f"生成课程列表图片失败: {e}")
                # 图片生成失败时，回退到文本形式
                yield event.plain_result(message)

        except Exception as e:
            logger.error(f"查询课程失败: {e}")
            yield event.plain_result("查询课程时出现错误，请稍后重试。")
