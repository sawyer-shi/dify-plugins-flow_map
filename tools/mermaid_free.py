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
from .mermaid_parser import MermaidParser


class MermaidFreeTool(Tool):
    """
    流程图 - 自由布局工具
    支持所有Mermaid语法生成对应图表，为中文和英文分别编写单独的布局算法
    仅使用Mermaid默认最经典简单的绘图风格
    """
    
    def __init__(self, runtime, session, **kwargs):
        super().__init__(runtime=runtime, session=session)
    
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
            
            # 解析Mermaid语法
            chart_type, elements = self._parse_mermaid(mermaid_code)
            
            # 根据语言类型选择布局算法
            if is_chinese:
                positions = self._chinese_layout_algorithm(elements, chart_type)
            else:
                positions = self._english_layout_algorithm(elements, chart_type)
            
            # 生成图像
            image_path = self._generate_image(chart_type, elements, positions, is_chinese)
            
            # 读取生成的PNG文件并返回为blob
            with open(image_path, "rb") as f:
                png_data = f.read()
            
            # 计算文件大小(以MB为单位)
            file_size_bytes = len(png_data)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # 生成成功消息
            layout_type = "Chinese" if is_chinese else "English"
            success_text = f"Successfully generated free layout flowchart with {layout_type} layout optimization. File size: {file_size_mb:.2f}M. Contains {len([e for e in elements if e['type'] == 'node'])} nodes and {len([e for e in elements if e['type'] == 'edge'])} connections."
            
            # 先返回文本消息
            yield self.create_text_message(success_text)
            
            # 返回PNG文件作为blob带元数据
            yield self.create_blob_message(
                png_data, 
                meta={
                    "mime_type": "image/png",
                    "filename": f"free_layout_mermaid_free_{layout_type.lower()}.png"
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
    
    def _chinese_layout_algorithm(self, elements: List[Dict[str, Any]], chart_type: str) -> Dict[str, Tuple[int, int]]:
        """
        中文布局算法 - 适应中文阅读习惯，从上到下，从右到左
        """
        positions = {}
        nodes = [e for e in elements if e["type"] == "node"]
        edges = [e for e in elements if e["type"] == "edge"]
        
        if not nodes:
            return positions
        
        # 中文布局参数
        node_width = 120
        node_height = 60
        horizontal_spacing = 150
        vertical_spacing = 100
        
        # 根据图表类型选择布局策略
        if chart_type in ["flowchart", "graph"]:
            # 流程图 - 层次布局
            positions = self._hierarchical_layout(nodes, edges, node_width, node_height, 
                                                horizontal_spacing, vertical_spacing, 
                                                right_to_left=True)
        elif chart_type == "sequence":
            # 序列图 - 从右到左的时间线
            positions = self._sequence_layout(nodes, node_width, node_height, 
                                            horizontal_spacing, right_to_left=True)
        elif chart_type == "class":
            # 类图 - 网格布局
            positions = self._grid_layout(nodes, node_width, node_height, 
                                        horizontal_spacing, vertical_spacing, 
                                        right_to_left=True)
        elif chart_type == "state":
            # 状态图 - 圆形布局
            positions = self._circular_layout(nodes, right_to_left=True)
        elif chart_type == "er":
            # ER图 - 层次布局
            positions = self._hierarchical_layout(nodes, edges, node_width, node_height, 
                                                horizontal_spacing, vertical_spacing, 
                                                right_to_left=True)
        else:
            # 默认网格布局
            positions = self._grid_layout(nodes, node_width, node_height, 
                                        horizontal_spacing, vertical_spacing, 
                                        right_to_left=True)
        
        return positions
    
    def _english_layout_algorithm(self, elements: List[Dict[str, Any]], chart_type: str) -> Dict[str, Tuple[int, int]]:
        """
        英文布局算法 - 适应英文阅读习惯，从上到下，从左到右
        """
        positions = {}
        nodes = [e for e in elements if e["type"] == "node"]
        edges = [e for e in elements if e["type"] == "edge"]
        
        if not nodes:
            return positions
        
        # 英文布局参数
        node_width = 120
        node_height = 60
        horizontal_spacing = 150
        vertical_spacing = 100
        
        # 根据图表类型选择布局策略
        if chart_type in ["flowchart", "graph"]:
            # 流程图 - 层次布局
            positions = self._hierarchical_layout(nodes, edges, node_width, node_height, 
                                                horizontal_spacing, vertical_spacing, 
                                                right_to_left=False)
        elif chart_type == "sequence":
            # 序列图 - 从左到右的时间线
            positions = self._sequence_layout(nodes, node_width, node_height, 
                                            horizontal_spacing, right_to_left=False)
        elif chart_type == "class":
            # 类图 - 网格布局
            positions = self._grid_layout(nodes, node_width, node_height, 
                                        horizontal_spacing, vertical_spacing, 
                                        right_to_left=False)
        elif chart_type == "state":
            # 状态图 - 圆形布局
            positions = self._circular_layout(nodes, right_to_left=False)
        elif chart_type == "er":
            # ER图 - 层次布局
            positions = self._hierarchical_layout(nodes, edges, node_width, node_height, 
                                                horizontal_spacing, vertical_spacing, 
                                                right_to_left=False)
        else:
            # 默认网格布局
            positions = self._grid_layout(nodes, node_width, node_height, 
                                        horizontal_spacing, vertical_spacing, 
                                        right_to_left=False)
        
        return positions
    
    def _hierarchical_layout(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                           node_width: int, node_height: int, horizontal_spacing: int, 
                           vertical_spacing: int, right_to_left: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        层次布局算法
        """
        positions = {}
        
        # 构建邻接表
        adjacency = {node["id"]: [] for node in nodes}
        in_degree = {node["id"]: 0 for node in nodes}
        
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            
            if from_node in adjacency and to_node in adjacency:
                adjacency[from_node].append(to_node)
                in_degree[to_node] += 1
        
        # 拓扑排序确定层级
        levels = {}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        
        current_level = 0
        while queue:
            next_queue = []
            for node_id in queue:
                levels[node_id] = current_level
                for neighbor in adjacency[node_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue
            current_level += 1
        
        # 处理可能存在的循环
        for node in nodes:
            if node["id"] not in levels:
                levels[node["id"]] = 0
        
        # 按层级分组节点
        level_nodes = {}
        for node_id, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node_id)
        
        # 计算位置
        max_level = max(levels.values()) if levels else 0
        canvas_width = (max_level + 1) * horizontal_spacing + node_width
        canvas_height = len(nodes) * vertical_spacing + node_height
        
        for level, node_ids in level_nodes.items():
            # 计算该层节点的垂直位置
            total_height = len(node_ids) * vertical_spacing
            start_y = (canvas_height - total_height) // 2 + node_height // 2
            
            for i, node_id in enumerate(node_ids):
                if right_to_left:
                    # 从右到左布局
                    x = canvas_width - (level + 1) * horizontal_spacing - node_width // 2
                else:
                    # 从左到右布局
                    x = level * horizontal_spacing + node_width // 2
                
                y = start_y + i * vertical_spacing
                positions[node_id] = (x, y)
        
        return positions
    
    def _sequence_layout(self, nodes: List[Dict[str, Any]], node_width: int, node_height: int, 
                        horizontal_spacing: int, right_to_left: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        序列图布局算法
        """
        positions = {}
        
        # 简单的水平排列
        canvas_width = len(nodes) * horizontal_spacing + node_width
        canvas_height = node_height * 3
        
        for i, node in enumerate(nodes):
            if right_to_left:
                # 从右到左布局
                x = canvas_width - (i + 1) * horizontal_spacing - node_width // 2
            else:
                # 从左到右布局
                x = i * horizontal_spacing + node_width // 2
            
            y = canvas_height // 2
            positions[node["id"]] = (x, y)
        
        return positions
    
    def _grid_layout(self, nodes: List[Dict[str, Any]], node_width: int, node_height: int, 
                    horizontal_spacing: int, vertical_spacing: int, 
                    right_to_left: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        网格布局算法
        """
        positions = {}
        
        # 计算网格大小
        cols = math.ceil(math.sqrt(len(nodes)))
        rows = math.ceil(len(nodes) / cols)
        
        canvas_width = cols * horizontal_spacing + node_width
        canvas_height = rows * vertical_spacing + node_height
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            
            if right_to_left:
                # 从右到左布局
                x = canvas_width - (col + 1) * horizontal_spacing - node_width // 2
            else:
                # 从左到右布局
                x = col * horizontal_spacing + node_width // 2
            
            y = row * vertical_spacing + node_height // 2
            positions[node["id"]] = (x, y)
        
        return positions
    
    def _circular_layout(self, nodes: List[Dict[str, Any]], right_to_left: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        圆形布局算法
        """
        positions = {}
        
        if not nodes:
            return positions
        
        # 计算圆形参数
        radius = min(200, 50 * len(nodes))
        center_x = radius + 100
        center_y = radius + 100
        
        # 计算角度步长
        angle_step = 2 * math.pi / len(nodes)
        
        for i, node in enumerate(nodes):
            if right_to_left:
                # 顺时针方向（从右到左阅读习惯）
                angle = i * angle_step
            else:
                # 逆时针方向（从左到右阅读习惯）
                angle = -i * angle_step
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            positions[node["id"]] = (int(x), int(y))
        
        return positions
    
    def _generate_image(self, chart_type: str, elements: List[Dict[str, Any]], 
                       positions: Dict[str, Tuple[int, int]], is_chinese: bool) -> str:
        """
        生成图像并返回文件路径
        """
        # 使用FreeLayoutRenderer生成图像
        renderer = FreeLayoutRenderer()
        return renderer.render_mermaid(chart_type, elements, positions, is_chinese)