# /astrbot_plugin_class2_notify/handlers/chat_handler.py

from astrbot.api.event import AstrMessageEvent
from astrbot.api import html_renderer
from astrbot.core import logger
from ..services import Class2API


# HTML 模板 - 仿照图片中的卡片样式
COURSE_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 18px;
            opacity: 0.9;
        }
        
        .course-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 25px;
        }
        
        .course-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .course-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.2);
        }
        
        .course-cover {
            position: relative;
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }
        
        .course-cover img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .course-status-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .status-0 { background: #9e9e9e; } /* 未上架 */
        .status-1 { background: #ffc107; } /* 未开始 */
        .status-2 { background: #4caf50; } /* 进行中 */
        .status-3 { background: #f44336; } /* 已结束 */
        .status-4 { background: #607d8b; } /* 已下架 */
        
        .course-content {
            padding: 20px;
        }
        
        .course-title {
            font-size: 22px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .course-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        .meta-tag {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
        }
        
        .meta-tag .emoji {
            margin-right: 4px;
        }
        
        .course-info {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .info-row {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .info-row:last-child {
            margin-bottom: 0;
        }
        
        .info-label {
            font-weight: bold;
            color: #666;
            min-width: 80px;
            flex-shrink: 0;
        }
        
        .info-value {
            color: #333;
            flex: 1;
        }
        
        .highlight {
            color: #667eea;
            font-weight: bold;
        }
        
        .people-info {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            padding: 12px;
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-radius: 8px;
        }
        
        .people-info .emoji {
            font-size: 20px;
        }
        
        .people-text {
            flex: 1;
            font-size: 14px;
            color: #333;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 第二课堂课程列表</h1>
            <p>共 {{ total_count }} 个课程{% if display_count < total_count %} · 显示前 {{ display_count }} 个{% endif %}</p>
        </div>
        
        <div class="course-grid">
            {% for course in courses %}
            <div class="course-card">
                <div class="course-cover">
                    {% if course.cover_url %}
                    <img src="{{ course.cover_url }}" alt="{{ course.title }}" onerror="this.style.display='none'">
                    {% endif %}
                    <div class="course-status-badge status-{{ course.sign_status }}">
                        {{ course.status_text }}
                    </div>
                </div>
                
                <div class="course-content">
                    <div class="course-title">{{ course.title }}</div>
                    
                    <div class="course-meta">
                        {% if course.category %}
                        <span class="meta-tag">
                            <span class="emoji">📂</span> {{ course.category }}
                        </span>
                        {% endif %}
                        {% if course.type %}
                        <span class="meta-tag">
                            <span class="emoji">🏷️</span> {{ course.type }}
                        </span>
                        {% endif %}
                        {% if course.score %}
                        <span class="meta-tag">
                            <span class="emoji">⭐</span> {{ course.score }} 分
                        </span>
                        {% endif %}
                    </div>
                    
                    {% if course.department %}
                    <div class="info-row">
                        <span class="info-label">主办单位：</span>
                        <span class="info-value">{{ course.department }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.sign_time %}
                    <div class="info-row">
                        <span class="info-label">报名时间：</span>
                        <span class="info-value">{{ course.sign_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.activity_time %}
                    <div class="info-row">
                        <span class="info-label">活动时间：</span>
                        <span class="info-value">{{ course.activity_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.time_place %}
                    <div class="info-row">
                        <span class="info-label">时间地点：</span>
                        <span class="info-value">{{ course.time_place }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.show_people_info %}
                    <div class="people-info">
                        <span class="emoji">👥</span>
                        <div class="people-text">
                            <span class="highlight">{{ course.apply_count }}/{{ course.max_people }}</span> 人
                            · 剩余 <span class="highlight">{{ course.remaining }}</span> 个名额
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            {% if total_count > display_count %}
            <p>还有 {{ total_count - display_count }} 个课程未显示</p>
            {% endif %}
            <p style="margin-top: 10px;">💡 使用 /第二课堂 [状态] 查看不同状态的课程</p>
            <p>状态：0-未上架 | 1-未开始 | 2-进行中 | 3-已结束 | 4-已下架</p>
        </div>
    </div>
</body>
</html>
'''


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
            activity_time = f"{course['sign_in_start_time']} ~ {course['sign_out_end_time']}"
        
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
            "type": course.get("transcript_index_type", {}).get("transcript_type_name", ""),
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
                    "type": "png",
                    "full_page": True,
                }
                
                image_url = await html_renderer.render_custom_template(COURSE_LIST_TEMPLATE, template_data, options=options)
                yield event.image_result(image_url)
                
            except Exception as e:
                logger.error(f"生成课程列表图片失败: {e}")
                # 图片生成失败时，回退到文本形式
                fallback_message = f"📚 第二课堂课程列表\n\n共 {len(filtered_courses)} 个课程\n\n"
                for idx, course in enumerate(filtered_courses[:display_count], 1):
                    fallback_message += f"{idx}. {course.get('title', '未知课程')}\n"
                    fallback_message += f"   状态: {self.api_service.SIGN_STATUS_MAP.get(course.get('sign_status'), '未知')}\n\n"
                
                if len(filtered_courses) > display_count:
                    fallback_message += f"\n还有 {len(filtered_courses) - display_count} 个课程未显示"
                
                yield event.plain_result(fallback_message)

        except Exception as e:
            logger.error(f"查询课程失败: {e}")
            yield event.plain_result("查询课程时出现错误，请稍后重试。")
