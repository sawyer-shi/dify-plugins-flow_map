# -*- coding: utf-8 -*-
"""
Mermaid Free Layout Flowchart Tool
Mermaid自由布局流程图工具

Generate flowcharts from any Mermaid syntax with optimized free layout for Chinese and English.
从任何Mermaid语法生成流程图，为中文和英文提供优化的自由布局。
"""

import re
import os
import tempfile
from typing import Dict, Any, Optional, List, Tuple, Generator
import json
from PIL import Image, ImageDraw, ImageFont
import math

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .free_layout_renderer import FreeLayoutRenderer
from .free_mermaid_parser import MermaidParser
from .free_layout_manager import LayoutManager


class MermaidFreeTool(Tool):
    """
    流程图 - 自由布局工具
    仅支持Mermaid流程图语法，为中文和英文分别编写单独的布局算法
    仅使用Mermaid默认最经典简单的绘图风格
    """
    
    def __init__(self, runtime, session, **kwargs):
        super().__init__(runtime=runtime, session=session)
        # 初始化布局管理器
        self.layout_manager = LayoutManager()
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Generate free layout flowchart from any Mermaid syntax
        从任何Mermaid语法生成自由布局流程图
        """
        try:
            # 获取Mermaid语法
            mermaid_code = tool_parameters.get("text", "")
            
            if not mermaid_code.strip():
                yield self.create_text_message(
                    "Failed to generate flowchart: Input text is empty. Please provide Mermaid syntax to generate flowchart."
                )
                return
            
            # 获取图表风格选项，默认为经典风格
            chart_style = tool_parameters.get("style", "classic")
            is_hand_drawn = (chart_style == "hand_drawn")
            
            # 检测语言类型
            is_chinese = self._detect_chinese(mermaid_code)
            
            # 解析Mermaid语法，只支持flowchart类型
            chart_type, elements = self._parse_mermaid(mermaid_code)
            
            # 使用布局管理器进行布局
            positions = self.layout_manager.layout(elements, chart_type, is_chinese)
            
            # 生成图像
            image_path = self._generate_image(chart_type, elements, positions, is_chinese, is_hand_drawn)
            
            # 读取生成的PNG文件并返回为blob
            with open(image_path, "rb") as f:
                png_data = f.read()
            
            # 计算文件大小(以MB为单位)
            file_size_bytes = len(png_data)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # 生成成功消息
            layout_type = "Chinese" if is_chinese else "English"
            style_type = "Hand Drawn" if is_hand_drawn else "Classic"
            success_text = f"Successfully generated {style_type} free layout flowchart with {layout_type} layout optimization. File size: {file_size_mb:.2f}M. Contains {len([e for e in elements if e['type'] == 'node'])} nodes and {len([e for e in elements if e['type'] == 'edge'])} connections."
            
            # 先返回文本消息
            yield self.create_text_message(success_text)
            
            # 返回PNG文件作为blob带元数据
            yield self.create_blob_message(
                png_data, 
                meta={
                    "mime_type": "image/png",
                    "filename": f"free_layout_mermaid_free_{layout_type.lower()}_{chart_style}.png"
                }
            )
            
        except Exception as e:
            error_text = f"Failed to generate free layout flowchart from Mermaid: {str(e)}"
            yield self.create_text_message(error_text)
    
    def _detect_chinese(self, text: str) -> bool:
        """
        检测文本是否包含中文字符
        """
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(chinese_pattern.search(text))
    
    def _parse_mermaid(self, mermaid_code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        解析Mermaid语法，提取图表类型和元素
        使用新的MermaidParser进行解析
        """
        parser = MermaidParser()
        return parser.parse(mermaid_code)
    
    def _extract_node_label(self, node_str: str) -> str:
        """
        从节点字符串中提取标签
        """
        # 尝试匹配方括号格式
        match = re.search(r'\[(.*?)\]', node_str)
        if match:
            return match.group(1)
        
        # 尝试匹配圆括号格式
        match = re.search(r'\((.*?)\)', node_str)
        if match:
            return match.group(1)
        
        # 如果没有找到标签，返回节点ID
        return node_str.split('[')[0].split('(')[0].strip()
    
    def _generate_image(self, chart_type: str, elements: List[Dict[str, Any]], 
                       positions: Dict[str, Tuple[int, int]], is_chinese: bool, is_hand_drawn: bool = False) -> str:
        """
        生成图像并返回文件路径
        """
        # 使用FreeLayoutRenderer生成图像
        renderer = FreeLayoutRenderer()
        return renderer.render_mermaid(chart_type, elements, positions, is_chinese)