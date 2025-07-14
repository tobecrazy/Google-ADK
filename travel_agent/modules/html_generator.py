from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import os

class HTMLGenerator:
    """负责将旅行规划数据渲染成HTML文件。"""

    def __init__(self, template_dir: str = 'travel_agent/templates'):
        """
        初始化HTMLGenerator。
        Args:
            template_dir: HTML模板文件所在的目录。
        """
        # 获取当前文件所在的目录，然后构建到templates的相对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 假设templates目录在travel_agent的根目录下
        self.template_path = os.path.join(current_dir, '..', template_dir)
        self.env = Environment(loader=FileSystemLoader(self.template_path))

    def generate_html(self, plan_data: Dict[str, Any], template_name: str = 'travel_plan.html') -> str:
        """
        根据提供的旅行规划数据和模板生成HTML内容。
        Args:
            plan_data: 包含旅行规划所有数据的字典。
            template_name: 要使用的HTML模板文件名。
        Returns:
            生成的HTML字符串。
        """
        template = self.env.get_template(template_name)
        return template.render(plan_data)
