# -*- coding: utf-8 -*-
"""
Independent Layout Algorithm for Mermaid Free Tool
独立布局算法实现

This module provides a standalone layout algorithm for generating flowcharts
from Mermaid syntax, without dependencies on other layout modules.
"""

import os
import math
import time
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont


class FreeLayoutRenderer:
    """
    自由布局渲染器
    独立实现Mermaid图表的布局和渲染功能
    """
    
    def __init__(self):
        pass
    
    def render_mermaid(self, chart_type: str, elements: List[Dict[str, Any]], 
                      positions: Dict[str, Tuple[int, int]], is_chinese: bool) -> str:
        """
        渲染Mermaid图表并返回文件路径
        
        Args:
            chart_type: 图表类型
            elements: 图表元素列表
            positions: 节点位置字典
            is_chinese: 是否为中文
            
        Returns:
            生成的图像文件路径
        """
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = int(time.time())
        layout_type = "chinese" if is_chinese else "english"
        filename = f"free_layout_mermaid_free_{layout_type}_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)
        
        # 计算画布大小
        nodes = [e for e in elements if e["type"] == "node"]
        edges = [e for e in elements if e["type"] == "edge"]
        
        if not positions:
            # 如果没有位置信息，使用默认布局
            for i, node in enumerate(nodes):
                positions[node["id"]] = (i * 150 + 100, i * 100 + 100)
        
        # 计算画布边界 - 增加更大的边距以确保所有元素都在画布内
        min_x = min(pos[0] for pos in positions.values()) - 100
        max_x = max(pos[0] for pos in positions.values()) + 100
        min_y = min(pos[1] for pos in positions.values()) - 100
        max_y = max(pos[1] for pos in positions.values()) + 100
        
        # 确保最小画布大小
        min_canvas_width = 800
        min_canvas_height = 600
        
        canvas_width = max(max_x - min_x, min_canvas_width)
        canvas_height = max(max_y - min_y, min_canvas_height)
        
        # 创建图像
        image = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            if is_chinese:
                # 尝试加载中文字体
                font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", "chinese_font.ttc")
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 14)
                else:
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 调整位置到画布坐标系
        adjusted_positions = {}
        for node_id, pos in positions.items():
            adjusted_positions[node_id] = (pos[0] - min_x, pos[1] - min_y)
        
        # 绘制连接线
        for edge in edges:
            from_pos = adjusted_positions.get(edge["from"])
            to_pos = adjusted_positions.get(edge["to"])
            
            if from_pos and to_pos:
                # 获取边样式，默认为箭头
                style = edge.get("style", "arrow")
                
                if style == "arrow":
                    # 绘制带箭头的线
                    self._draw_arrow_line(draw, from_pos, to_pos)
                elif style == "line":
                    # 绘制普通线
                    draw.line([from_pos, to_pos], fill='black', width=2)
                elif style == "dotted_arrow":
                    # 绘制虚线箭头
                    self._draw_dotted_arrow_line(draw, from_pos, to_pos)
                elif style == "thick_arrow":
                    # 绘制粗线箭头
                    self._draw_thick_arrow_line(draw, from_pos, to_pos)
                else:
                    # 默认绘制带箭头的线
                    self._draw_arrow_line(draw, from_pos, to_pos)
                
                # 绘制边标签（如果有）
                label = edge.get("label", "")
                if label:
                    self._draw_edge_label(draw, from_pos, to_pos, label, font)
        
        # 绘制节点
        for node in nodes:
            pos = adjusted_positions.get(node["id"])
            if pos:
                # 获取节点形状，默认为矩形
                shape = node.get("shape", "rectangle")
                
                # 绘制节点
                self._draw_node(draw, node, pos, font)
        
        # 保存图像
        image.save(output_path)
        
        return output_path
    
    def _draw_arrow_line(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """
        绘制带箭头的线
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
        """
        # 计算节点边缘的位置（避免箭头被节点遮挡）
        # 假设节点大小为120x60，所以半径约为60和30
        node_radius_x = 60
        node_radius_y = 30
        
        # 计算方向向量
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance
        
        # 调整终点位置到节点边缘
        adjusted_to_x = to_pos[0] - unit_x * node_radius_x
        adjusted_to_y = to_pos[1] - unit_y * node_radius_y
        adjusted_to_pos = (adjusted_to_x, adjusted_to_y)
        
        # 绘制线
        draw.line([from_pos, adjusted_to_pos], fill='black', width=2)
        
        # 计算箭头方向
        angle = math.atan2(dy, dx)
        
        # 箭头长度
        arrow_length = 10
        arrow_angle = math.pi / 6
        
        # 计算箭头两个端点
        x1 = adjusted_to_x - arrow_length * math.cos(angle - arrow_angle)
        y1 = adjusted_to_y - arrow_length * math.sin(angle - arrow_angle)
        x2 = adjusted_to_x - arrow_length * math.cos(angle + arrow_angle)
        y2 = adjusted_to_y - arrow_length * math.sin(angle + arrow_angle)
        
        # 绘制箭头
        draw.polygon([(adjusted_to_x, adjusted_to_y), (x1, y1), (x2, y2)], fill='black')
    
    def _draw_dotted_arrow_line(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """
        绘制虚线箭头
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
        """
        # 计算节点边缘的位置（避免箭头被节点遮挡）
        # 假设节点大小为120x60，所以半径约为60和30
        node_radius_x = 60
        node_radius_y = 30
        
        # 计算方向向量
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance
        
        # 调整终点位置到节点边缘
        adjusted_to_x = to_pos[0] - unit_x * node_radius_x
        adjusted_to_y = to_pos[1] - unit_y * node_radius_y
        adjusted_to_pos = (adjusted_to_x, adjusted_to_y)
        
        # 计算虚线段 - 进一步增加虚线间隔，使虚线和实线区别更明显
        # 虚线参数
        dash_length = 10  # 增加虚线段长度
        gap_length = 8    # 进一步增加间隔长度
        
        # 调整后的距离
        adjusted_distance = distance - node_radius_x
        
        # 绘制虚线
        current_distance = 0
        while current_distance < adjusted_distance:
            # 计算当前段的起点和终点
            start_x = from_pos[0] + unit_x * current_distance
            start_y = from_pos[1] + unit_y * current_distance
            
            end_distance = min(current_distance + dash_length, adjusted_distance)
            end_x = from_pos[0] + unit_x * end_distance
            end_y = from_pos[1] + unit_y * end_distance
            
            # 绘制虚线段
            draw.line([(start_x, start_y), (end_x, end_y)], fill='black', width=2)
            
            # 更新当前距离
            current_distance += dash_length + gap_length
        
        # 绘制箭头
        self._draw_arrow_head(draw, (end_x, end_y), adjusted_to_pos)
    
    def _draw_thick_arrow_line(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """
        绘制粗线箭头
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
        """
        # 计算节点边缘的位置（避免箭头被节点遮挡）
        # 假设节点大小为120x60，所以半径约为60和30
        node_radius_x = 60
        node_radius_y = 30
        
        # 计算方向向量
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        # 单位向量和垂直向量
        unit_x = dx / distance
        unit_y = dy / distance
        perp_x = -unit_y
        perp_y = unit_x
        
        # 调整终点位置到节点边缘
        adjusted_to_x = to_pos[0] - unit_x * node_radius_x
        adjusted_to_y = to_pos[1] - unit_y * node_radius_y
        
        # 粗线宽度
        width = 4
        
        # 计算四个角点
        p1 = (from_pos[0] + perp_x * width/2, from_pos[1] + perp_y * width/2)
        p2 = (from_pos[0] - perp_x * width/2, from_pos[1] - perp_y * width/2)
        
        # 计算箭头起点的四个角点（留出箭头空间）
        arrow_start_distance = distance - node_radius_x - 10
        arrow_start_x = from_pos[0] + unit_x * arrow_start_distance
        arrow_start_y = from_pos[1] + unit_y * arrow_start_distance
        
        p3 = (arrow_start_x - perp_x * width/2, arrow_start_y - perp_y * width/2)
        p4 = (arrow_start_x + perp_x * width/2, arrow_start_y + perp_y * width/2)
        
        # 绘制粗线
        draw.polygon([p1, p2, p3, p4], fill='black')
        
        # 绘制箭头
        self._draw_arrow_head(draw, (arrow_start_x, arrow_start_y), (adjusted_to_x, adjusted_to_y))
    
    def _draw_arrow_head(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """
        绘制箭头
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
        """
        # 计算箭头方向
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        # 计算箭头角度
        angle = math.atan2(dy, dx)
        
        # 箭头长度
        arrow_length = 10
        arrow_angle = math.pi / 6
        
        # 计算箭头两个端点
        x1 = to_pos[0] - arrow_length * math.cos(angle - arrow_angle)
        y1 = to_pos[1] - arrow_length * math.sin(angle - arrow_angle)
        x2 = to_pos[0] - arrow_length * math.cos(angle + arrow_angle)
        y2 = to_pos[1] - arrow_length * math.sin(angle + arrow_angle)
        
        # 绘制箭头
        draw.polygon([(to_pos[0], to_pos[1]), (x1, y1), (x2, y2)], fill='black')
    
    def _draw_edge_label(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], 
                        to_pos: Tuple[int, int], label: str, font):
        """
        绘制边标签
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
            label: 标签文本
            font: 字体
        """
        # 计算中点位置
        mid_x = (from_pos[0] + to_pos[0]) / 2
        mid_y = (from_pos[1] + to_pos[1]) / 2
        
        # 计算文本边界框
        if hasattr(draw, 'textbbox'):
            # 使用textbbox方法（PIL 8.0.0+）
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        elif hasattr(draw, 'textsize'):
            # 使用textsize方法（较旧版本的PIL）
            text_width, text_height = draw.textsize(label, font=font)
        else:
            # 回退到估算
            text_width = len(label) * 8
            text_height = 14
        
        # 绘制背景
        padding = 4
        draw.rectangle(
            [mid_x - text_width/2 - padding, mid_y - text_height/2 - padding,
             mid_x + text_width/2 + padding, mid_y + text_height/2 + padding],
            fill='white', outline='white'
        )
        
        # 绘制文本
        draw.text((mid_x - text_width/2, mid_y - text_height/2), label, fill='black', font=font)
    
    def _draw_node(self, draw: ImageDraw.ImageDraw, node: Dict[str, Any], 
                  pos: Tuple[int, int], font):
        """
        绘制节点
        
        Args:
            draw: ImageDraw对象
            node: 节点数据
            pos: 节点位置
            font: 字体
        """
        # 获取节点属性
        shape = node.get("shape", "rectangle")
        label = node.get("label", "")
        
        # 节点尺寸
        node_width = 120
        node_height = 60
        
        # 根据形状绘制节点
        if shape == "rectangle":
            self._draw_rectangle_node(draw, pos, node_width, node_height)
        elif shape == "rounded":
            self._draw_rounded_node(draw, pos, node_width, node_height)
        elif shape == "diamond":
            self._draw_diamond_node(draw, pos, node_width, node_height)
        elif shape == "circle":
            self._draw_circle_node(draw, pos, node_width, node_height)
        elif shape == "stadium":
            self._draw_stadium_node(draw, pos, node_width, node_height)
        elif shape == "parallelogram":
            self._draw_parallelogram_node(draw, pos, node_width, node_height, False)
        elif shape == "parallelogram_alt":
            self._draw_parallelogram_node(draw, pos, node_width, node_height, True)
        elif shape == "subroutine":
            self._draw_subroutine_node(draw, pos, node_width, node_height)
        elif shape == "cylinder":
            self._draw_cylinder_node(draw, pos, node_width, node_height)
        else:
            # 默认绘制矩形
            self._draw_rectangle_node(draw, pos, node_width, node_height)
        
        # 绘制文本
        if label:
            self._draw_node_text(draw, pos, label, font)
    
    def _draw_rectangle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                            width: int, height: int):
        """绘制矩形节点"""
        x1 = pos[0] - width // 2
        y1 = pos[1] - height // 2
        x2 = pos[0] + width // 2
        y2 = pos[1] + height // 2
        draw.rectangle([x1, y1, x2, y2], outline='black', fill='white')
    
    def _draw_rounded_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int):
        """绘制圆角矩形节点"""
        x1 = pos[0] - width // 2
        y1 = pos[1] - height // 2
        x2 = pos[0] + width // 2
        y2 = pos[1] + height // 2
        radius = min(width, height) // 5
        
        # 绘制圆角矩形（简化版，使用多边形近似）
        points = [
            (x1 + radius, y1), (x2 - radius, y1),
            (x2, y1 + radius), (x2, y2 - radius),
            (x2 - radius, y2), (x1 + radius, y2),
            (x1, y2 - radius), (x1, y1 + radius)
        ]
        draw.polygon(points, outline='black', fill='white')
    
    def _draw_diamond_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int):
        """绘制菱形节点"""
        points = [
            (pos[0], pos[1] - height // 2),  # 上
            (pos[0] + width // 2, pos[1]),  # 右
            (pos[0], pos[1] + height // 2),  # 下
            (pos[0] - width // 2, pos[1])   # 左
        ]
        draw.polygon(points, outline='black', fill='white')
    
    def _draw_circle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                         width: int, height: int):
        """绘制圆形节点"""
        radius = min(width, height) // 2
        draw.ellipse(
            [pos[0] - radius, pos[1] - radius, pos[0] + radius, pos[1] + radius],
            outline='black', fill='white'
        )
    
    def _draw_stadium_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int):
        """绘制体育场形节点"""
        radius = height // 2
        # 绘制中间矩形
        draw.rectangle(
            [pos[0] - width // 2 + radius, pos[1] - height // 2,
             pos[0] + width // 2 - radius, pos[1] + height // 2],
            outline='black', fill='white'
        )
        # 绘制左右半圆
        draw.ellipse(
            [pos[0] - width // 2, pos[1] - height // 2,
             pos[0] - width // 2 + height, pos[1] + height // 2],
            outline='black', fill='white'
        )
        draw.ellipse(
            [pos[0] + width // 2 - height, pos[1] - height // 2,
             pos[0] + width // 2, pos[1] + height // 2],
            outline='black', fill='white'
        )
    
    def _draw_parallelogram_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                                width: int, height: int, reverse: bool):
        """绘制平行四边形节点"""
        offset = width // 4
        if reverse:
            points = [
                (pos[0] - width // 2 + offset, pos[1] - height // 2),  # 左上
                (pos[0] + width // 2, pos[1] - height // 2),          # 右上
                (pos[0] + width // 2 - offset, pos[1] + height // 2),  # 右下
                (pos[0] - width // 2, pos[1] + height // 2)           # 左下
            ]
        else:
            points = [
                (pos[0] - width // 2, pos[1] - height // 2),          # 左上
                (pos[0] + width // 2 - offset, pos[1] - height // 2),  # 右上
                (pos[0] + width // 2, pos[1] + height // 2),          # 右下
                (pos[0] - width // 2 + offset, pos[1] + height // 2)   # 左下
            ]
        draw.polygon(points, outline='black', fill='white')
    
    def _draw_subroutine_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                             width: int, height: int):
        """绘制子程序节点"""
        x1 = pos[0] - width // 2
        y1 = pos[1] - height // 2
        x2 = pos[0] + width // 2
        y2 = pos[1] + height // 2
        
        # 绘制主矩形
        draw.rectangle([x1, y1, x2, y2], outline='black', fill='white')
        
        # 绘制额外的边框线
        draw.line([x1 + 10, y1, x1 + 10, y2], fill='black', width=2)
        draw.line([x2 - 10, y1, x2 - 10, y2], fill='black', width=2)
    
    def _draw_cylinder_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                           width: int, height: int):
        """绘制圆柱形节点"""
        x1 = pos[0] - width // 2
        x2 = pos[0] + width // 2
        y1 = pos[1] - height // 2
        y2 = pos[1] + height // 2
        ellipse_height = height // 4
        
        # 绘制主体矩形
        draw.rectangle([x1, y1 + ellipse_height, x2, y2], outline='black', fill='white')
        
        # 绘制顶部椭圆
        draw.ellipse([x1, y1, x2, y1 + ellipse_height * 2], outline='black', fill='white')
        
        # 绘制底部椭圆
        draw.ellipse([x1, y2 - ellipse_height * 2, x2, y2], outline='black', fill='white')
    
    def _draw_node_text(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                       text: str, font):
        """绘制节点文本"""
        # 计算文本边界框
        if hasattr(draw, 'textbbox'):
            # 使用textbbox方法（PIL 8.0.0+）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # 计算文本的左上角位置，使文本居中
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        elif hasattr(draw, 'textsize'):
            # 使用textsize方法（较旧版本的PIL）
            text_width, text_height = draw.textsize(text, font=font)
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        else:
            # 回退到估算
            text_width = len(text) * 8
            text_height = 14
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        
        # 绘制文本
        draw.text((text_x, text_y), text, fill='black', font=font)