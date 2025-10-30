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
from .free_layout_renderer import ImprovedFlowchartRenderer
from .free_mermaid_parser import MermaidParser
from .free_layout_manager import LayoutManager


class MermaidFreeTool(Tool):
    """
    流程图 - 自由布局工具
    仅支持Mermaid流程图语法，为中文和英文分别编写单独的布局算法
    使用默认经典绘图风格
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
            
            # 检测语言类型
            is_chinese = self._detect_chinese(mermaid_code)
            
            # 解析Mermaid语法，只支持flowchart类型
            chart_type, elements = self._parse_mermaid(mermaid_code)
            
            # 使用布局管理器进行布局
            layout_result = self.layout_manager.layout(elements, chart_type, is_chinese)
            positions = layout_result.get("positions", {})
            
            # 生成图像 - 使用默认风格
            image_path = self._generate_image(chart_type, elements, positions, is_chinese)
            
            # 读取生成的PNG文件并返回为blob
            with open(image_path, "rb") as f:
                png_data = f.read()
            
            # 计算文件大小(以MB为单位)
            file_size_bytes = len(png_data)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # 统计节点和连接数
            nodes_count = len([e for e in elements if e['type'] == 'node'])
            connections_count = len([e for e in elements if e['type'] == 'edge'])
            
            # 准备包含流程图信息的JSON数据
            layout_type = "Chinese" if is_chinese else "English"
            json_data = {
                "layout_type": "free",
                "nodes_count": nodes_count,
                "connections_count": connections_count,
                "file_size_bytes": file_size_bytes,
                "file_size_mb": round(file_size_mb, 2),
                "language": layout_type,
                "success": True
            }
            
            # 生成成功消息
            success_text = f"Successfully generated free layout flowchart with {layout_type} layout optimization. File size: {file_size_mb:.2f}M. Contains {nodes_count} nodes and {connections_count} connections."
            
            # 先返回文本消息
            yield self.create_text_message(success_text)
            
            # 返回包含流程图详细信息的JSON消息
            yield self.create_json_message(json_data)
            
            # 返回PNG文件作为blob带元数据
            yield self.create_blob_message(
                png_data, 
                meta={
                    "mime_type": "image/png",
                    "filename": f"free_layout_mermaid_flowchart_{layout_type.lower()}.png"
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
                       positions: Dict[str, Tuple[int, int]], is_chinese: bool) -> str:
        """
        生成图像并返回文件路径
        """
        # 使用布局管理器的render方法生成图像
        # 首先转换positions为布局管理器期望的格式
        layout_result = self._convert_positions_to_layout_result(elements, positions)
        
        # 直接使用渲染器渲染图像
        image = self.layout_manager.flowchart_renderer.render_mermaid("", layout_result)
        
        # 保存图像并返回路径
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "test", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        import time
        timestamp = int(time.time())
        layout_type = "chinese" if is_chinese else "english"
        filename = f"free_layout_mermaid_flowchart_{layout_type}_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)
        
        image.save(output_path)
        return output_path
    
    def _convert_positions_to_layout_result(self, elements: List[Dict[str, Any]], 
                                          positions: Dict[str, Tuple[int, int]]) -> Dict[str, Any]:
        """
        将元素列表和位置字典转换为布局结果格式
        """
        nodes = {}
        connections = []
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        # 处理节点
        for element in elements:
            if element["type"] == "node":
                node_id = element["id"]
                x, y = positions.get(node_id, (0, 0))
                nodes[node_id] = {
                    'x': x,
                    'y': y,
                    'shape': element.get("shape", "rectangle"),
                    'text': element.get("label", node_id),
                    'type': element.get("node_type", "default")
                }
                
                # 更新边界值
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        
        # 处理连接
        for element in elements:
            if element["type"] == "edge":
                connections.append({
                    'from': element["from"],
                    'to': element["to"],
                    'line_type': element.get("style", "solid"),
                    'label': element.get("label", None)
                })
        
        # 计算合适的画布大小，确保所有节点都在画布内
        # 考虑节点尺寸（默认节点宽度140，高度60）
        node_width = 140
        node_height = 60
        margin = 100  # 增加边距，确保所有元素都在画布内
        
        # 如果有负坐标，需要调整
        if min_x < margin:
            shift_x = margin - min_x
            # 调整所有节点位置
            for node_id in nodes:
                nodes[node_id]['x'] += shift_x
            max_x += shift_x
            min_x = margin
        
        if min_y < margin:
            shift_y = margin - min_y
            # 调整所有节点位置
            for node_id in nodes:
                nodes[node_id]['y'] += shift_y
            max_y += shift_y
            min_y = margin
        
        # 计算画布大小，确保包含所有节点和边距
        canvas_width = max(max_x + node_width // 2 + margin, 800)  # 最小宽度800
        canvas_height = max(max_y + node_height // 2 + margin, 600)  # 最小高度600
        
        return {
            'nodes': nodes,
            'connections': connections,
            'canvas_width': canvas_width,
            'canvas_height': canvas_height
        }
    
    def _generate_mermaid_code(self, elements: List[Dict[str, Any]]) -> str:
        """
        从元素列表生成基本的Mermaid代码
        """
        lines = ["flowchart TD"]
        
        for element in elements:
            if element["type"] == "node":
                node_id = element["id"]
                label = element.get("label", node_id)
                lines.append(f"    {node_id}[{label}]")
            elif element["type"] == "edge":
                from_node = element["from"]
                to_node = element["to"]
                label = element.get("label", "")
                if label:
                    lines.append(f"    {from_node} -->|{label}| {to_node}")
                else:
                    lines.append(f"    {from_node} --> {to_node}")
        
        return "\n".join(lines)