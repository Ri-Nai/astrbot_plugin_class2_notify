# /astrbot_plugin_2class_notify/services/scheduler_service.py

import asyncio
from typing import List, Dict, Any
from astrbot.core import logger
from astrbot.api import html_renderer
from .class2_api import Class2API
from .course_storage import CourseStorage


class SchedulerService:
    """定时任务服务：负责管理课程监控任务"""

    def __init__(self, context, config, api_service: Class2API, storage_service: CourseStorage):
        self.context = context
        self.config = config
        self.api_service = api_service
        self.storage_service = storage_service
        self.monitor_task = None
        self.is_running = False

    def start_monitoring(self):
        """启动课程监控任务"""
        if self.is_running:
            logger.warning("课程监控任务已在运行中")
            return

        if not self.config.enable_notification:
            logger.info("自动通知已禁用，不启动监控任务")
            return

        if not self.config.api_domain:
            logger.warning("未配置API域名，无法启动监控任务")
            return

        self.monitor_task = asyncio.create_task(self._monitor_courses())
        logger.info(f"已启动课程监控任务，检查间隔: {self.config.check_interval} 分钟")

    async def _monitor_courses(self):
        """监控课程更新的主循环"""
        self.is_running = True
        
        # 首次运行，加载现有数据
        logger.info("初始化课程监控...")
        await self._check_and_notify(is_first_run=True)

        while self.is_running:
            try:
                # 等待指定的间隔时间
                await asyncio.sleep(self.config.check_interval * 60)
                
                # 检查更新并通知
                await self._check_and_notify(is_first_run=False)
                
            except asyncio.CancelledError:
                logger.info("课程监控任务被取消")
                break
            except Exception as e:
                logger.error(f"课程监控出错: {e}")
                # 出错后等待一段时间再继续
                await asyncio.sleep(60)

    async def _check_and_notify(self, is_first_run: bool = False):
        """
        检查课程更新并发送通知
        
        Args:
            is_first_run: 是否首次运行
        """
        try:
            # 获取最新课程列表
            response = await self.api_service.get_course_list(page=1, limit=200)
            
            if not response or not response.get("data"):
                logger.warning("获取课程列表失败或数据为空")
                return

            new_courses_data = response.get("data", {})
            new_courses = new_courses_data.get("items", [])
            
            if is_first_run:
                logger.info(f"首次运行，发现 {len(new_courses)} 个课程")
                # 首次运行，保存数据但不发送通知
                self.storage_service.save_courses(new_courses_data)
                return

            # 加载旧数据
            old_data = self.storage_service.load_courses()
            old_courses = old_data.get("items", []) if old_data else []

            # 查找新增课程
            added_courses = self.storage_service.find_new_courses(old_courses, new_courses)

            if added_courses:
                logger.info(f"发现 {len(added_courses)} 个新课程")
                # 发送通知
                await self._send_notifications(added_courses)
            else:
                logger.debug("无新增课程")

            # 保存最新数据
            self.storage_service.save_courses(new_courses_data)

        except Exception as e:
            logger.error(f"检查课程更新失败: {e}")

    async def _send_notifications(self, new_courses: List[Dict[str, Any]]):
        """
        发送新课程通知到配置的群组
        
        Args:
            new_courses: 新增的课程列表
        """
        if not self.config.notify_groups:
            logger.warning("未配置通知群组，跳过发送通知")
            return

        # 获取平台实例
        platforms = self.context.platform_manager.get_insts()
        platform = next(
            (p for p in platforms if p.metadata.name == "aiocqhttp"),
            None,
        )

        if platform is None:
            logger.error("未找到 aiocqhttp 平台实例，无法发送通知")
            return

        client = platform.get_client()

        # 构建通知消息（Markdown格式）
        message_lines = [
            f"# 🎉 第二课堂新课程通知\n",
            f"**发现 {len(new_courses)} 个新课程！**\n"
        ]
        
        for idx, course in enumerate(new_courses[:5], 1):  # 最多显示5个
            course_markdown = self.api_service.format_course_info(course, idx)
            message_lines.append(course_markdown)
            message_lines.append("")  # 空行分隔

        if len(new_courses) > 5:
            message_lines.append(f"\n> 还有 {len(new_courses) - 5} 个新课程，请使用 `/第二课堂` 命令查看")

        message = "\n".join(message_lines)

        # 生成图片
        try:
            message_image_url = await html_renderer.render_t2i(message)
        except Exception as e:
            logger.error(f"生成通知图片失败: {e}")
            message_image_url = None

        # 发送到所有配置的群组
        for group_id in self.config.notify_groups:
            try:
                # 只发送图片消息
                if message_image_url:
                    image_payload = {
                        "group_id": int(group_id),
                        "message": [
                            {
                                "type": "image",
                                "data": {"file": message_image_url},
                            },
                        ],
                    }
                    await client.api.call_action("send_group_msg", **image_payload)
                    logger.info(f"已向群 {group_id} 发送新课程通知")
                else:
                    logger.warning(f"图片生成失败，跳过向群 {group_id} 发送通知")
            except Exception as e:
                logger.error(f"向群 {group_id} 发送通知失败: {e}")

    async def stop_monitoring(self):
        """停止课程监控任务"""
        if not self.is_running:
            return

        self.is_running = False
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("课程监控任务已停止")
