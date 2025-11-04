# /astrbot_plugin_2class_notify/services/course_storage.py

import os
import json
from typing import List, Dict, Any, Optional
from astrbot.core import logger


class CourseStorage:
    """课程数据存储服务，用于保存和对比课程数据"""

    def __init__(self):
        self.storage_dir = os.path.join("data", "astrbot_plugin_2class_notify")
        self.storage_file = os.path.join(self.storage_dir, "courses.json")
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info(f"创建存储目录: {self.storage_dir}")

    def save_courses(self, courses_data: Dict[str, Any]) -> bool:
        """
        保存课程数据
        
        Args:
            courses_data: 课程数据（完整的API响应）
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(courses_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"课程数据已保存到: {self.storage_file}")
            return True
        except Exception as e:
            logger.error(f"保存课程数据失败: {e}")
            return False

    def load_courses(self) -> Optional[Dict[str, Any]]:
        """
        加载已保存的课程数据
        
        Returns:
            课程数据，如果不存在则返回None
        """
        if not os.path.exists(self.storage_file):
            logger.debug("课程数据文件不存在")
            return None

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"已加载课程数据: {len(data.get('items', []))} 个课程")
            return data
        except Exception as e:
            logger.error(f"加载课程数据失败: {e}")
            return None

    def find_new_courses(self, old_courses: List[Dict[str, Any]], new_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        找出新增的课程
        
        Args:
            old_courses: 旧课程列表
            new_courses: 新课程列表
            
        Returns:
            新增的课程列表
        """
        if not old_courses:
            # 首次运行，不报告所有项为新增
            logger.info("首次运行，不报告新课程")
            return []

        old_ids = {course.get("id") for course in old_courses if course.get("id")}
        new_items = [
            course for course in new_courses
            if course.get("id") and course.get("id") not in old_ids
        ]

        if new_items:
            logger.info(f"发现 {len(new_items)} 个新课程")
        
        return new_items

    def clear_storage(self) -> bool:
        """
        清空存储的课程数据
        
        Returns:
            是否清空成功
        """
        try:
            if os.path.exists(self.storage_file):
                os.remove(self.storage_file)
                logger.info("已清空课程数据")
            return True
        except Exception as e:
            logger.error(f"清空课程数据失败: {e}")
            return False
