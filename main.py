# /astrbot_plugin_class2_notify/__init__.py

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core import logger

from .config import load_config
from .services import Class2API, CourseStorage, SchedulerService
from .handlers import ChatHandler


@register(
    "astrbot_plugin_class2_notify",
    "Ri-Nai",
    "一个用于查询和推送第二课堂课程更新的插件",
    "1.0.0",
)
class Class2Notify(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        # 1. 加载配置
        self.config = load_config(self.context, config)

        # 2. 初始化服务层
        self.api_service = Class2API(self.config)
        self.storage_service = CourseStorage()
        
        # 3. 初始化调度服务
        self.scheduler_service = SchedulerService(
            self.context,
            self.config,
            self.api_service,
            self.storage_service
        )

        # 4. 初始化处理器层
        self.chat_handler = ChatHandler(self.config, self.api_service)

        # 5. 启动课程监控任务
        self.scheduler_service.start_monitoring()

    @filter.command("第二课堂", alias={"class2"})
    async def query_courses(self, event: AstrMessageEvent, page: str = "1"):
        """查询第二课堂课程"""
        try:
            page_num = max(1, int(page))  # 确保页码至少为1
            async for result in self.chat_handler.process_course_query(event, page_num):
                yield result
        except ValueError:
            yield event.plain_result("页码必须是正整数！\n例如：/第二课堂 2 表示查看第2页")

    @filter.command("help", alias={"帮助"})
    async def help(self, event: AstrMessageEvent):
        """提供帮助信息"""
        help_text = (
            "📚 第二课堂通知插件帮助\n\n"
            "/第二课堂 [页码] - 查询课程列表\n"
            "  每页显示10个课程\n"
            "  示例：\n"
            "    /第二课堂      # 查询第1页课程\n"
            "    /第二课堂 2    # 查询第2页课程\n"
            "    /第二课堂 3    # 查询第3页课程\n\n"
            "💡 当有新课程上线时，会自动推送到配置的群组"
        )
        yield event.plain_result(help_text)

    async def terminate(self):
        """插件卸载时的清理操作"""
        await self.scheduler_service.stop_monitoring()
        await self.api_service.close()
        logger.info("第二课堂通知插件已卸载")
