"""
改进的流程图渲染器，专注于防止连线穿过节点
"""

import math
import os
import re
from typing import Dict, List, Tuple, Any
from PIL import Image, ImageDraw, ImageFont


class ImprovedFlowchartRenderer:
    """改进的流程图渲染器，确保连线不会穿过节点"""
    
    def __init__(self):
        # 颜色配置
        self.colors = {
            'background': '#FFFFFF',
            'node_fill': '#F0F8FF',
            'node_outline': '#4682B4',
            'text': '#000000',
            'arrow': '#000000',
            'start_node': '#E6FFE6',      # 淡绿色 - 开始节点
            'end_node': '#F0F0F0',        # 淡灰色 - 结束节点
            'process_node': '#F0F8FF',    # 淡蓝色 - 处理节点
            'decision_node': '#FFFFCC',   # 淡黄色 - 判断节点
            'data_node': '#E0FFFF',
            'subroutine_node': '#F5F5DC',
            'circle_node': '#F0FFF0',
            'diamond_node': '#FFFFCC'     # 淡黄色 - 菱形判断节点
        }
        
        # 线条宽度配置
        self.line_widths = {
            'node_outline': 2,
            'arrow': 1,  # 将连接线宽度从2改为1，防止掩盖文字
            'text': 1
        }
        
        # 节点尺寸配置
        self.node_width = 140
        self.node_height = 60
        self.route_channel_gap = 18
        self.curve_sample_count = 24
        self._reset_route_state()
        
        # 字体配置 - 支持中文，优先使用插件内嵌字体
        self.font_size = 12
        
        # 初始化字体路径
        self.font_path = ""
        self.bold_font_path = ""
        
        # 设置中文字体
        self._setup_chinese_font()
        
        # 尝试获取插件内嵌加粗字体路径
        self._setup_bold_font()
        
        # 备选字体列表
        self.fallback_fonts = self._get_fallback_fonts()
        
        # 备选加粗字体列表
        self.fallback_bold_fonts = self._get_fallback_bold_fonts()
    
    def render_mermaid(self, mermaid_code: str, layout_result: Dict[str, Any], description: str = "") -> Image.Image:
        """
        渲染Mermaid流程图
        
        Args:
            mermaid_code: Mermaid代码
            layout_result: 布局结果，包含节点位置和连接信息
            description: 流程图描述信息，显示在画布左上方
            
        Returns:
            渲染后的图像
        """
        return self._render_flowchart(layout_result, description)
    
    def _render_flowchart(self, layout_result: Dict[str, Any], description: str = "") -> Image.Image:
        """
        渲染流程图
        
        Args:
            layout_result: 布局结果
            description: 流程图描述信息，显示在画布左上方
            
        Returns:
            渲染后的图像
        """
        # 创建画布
        canvas_width = layout_result.get('canvas_width', 800)
        canvas_height = layout_result.get('canvas_height', 600)
        
        # 如果有描述信息，增加画布高度以容纳描述文本
        description_height = 0
        if description:
            # 估算描述文本所需高度
            description_height = self._estimate_description_height(description)
            canvas_height += description_height + 20  # 额外20像素间距
        
        # 添加边距
        margin = 50
        canvas_width += margin * 2
        canvas_height += margin * 2
        
        # 创建图像
        image = Image.new('RGB', (canvas_width, canvas_height), self.colors['background'])
        draw = ImageDraw.Draw(image)
        
        # 绘制描述信息（如果有）
        if description:
            # 调整节点位置，为描述信息留出空间
            description_y = margin
            self._draw_description(draw, description, margin, description_y, canvas_width - margin * 2)
            # 增加额外的边距，确保描述信息不与节点重叠
            extra_margin = description_height + 20
        else:
            extra_margin = 0
        
        # 获取节点和连接信息
        nodes = layout_result.get('nodes', {})
        connections = layout_result.get('connections', [])
        self._reset_route_state(
            layout_result.get('routing_mode') == 'complex_orthogonal',
            route_bounds=(8, 8, canvas_width - 8, canvas_height - 8)
        )
        rendered_nodes = {}
        
        # 绘制节点
        for node_id, node_data in nodes.items():
            # 调整位置，添加边距和描述信息空间
            pos = (node_data['x'] + margin, node_data['y'] + margin + extra_margin)
            rendered_node = dict(node_data)
            rendered_node['x'] = pos[0]
            rendered_node['y'] = pos[1]
            rendered_nodes[node_id] = rendered_node
            self._draw_node(draw, node_id, node_data, pos)
        
        # 绘制连接线（使用改进的算法，确保不穿过节点）
        for connection in connections:
            from_node = connection['from']
            to_node = connection['to']
            line_type = connection.get('line_type', 'solid')
            label = connection.get('label', None)
            
            from_pos = (rendered_nodes[from_node]['x'], rendered_nodes[from_node]['y'])
            to_pos = (rendered_nodes[to_node]['x'], rendered_nodes[to_node]['y'])
            
            # 使用改进的连线算法，确保不穿过节点
            self._draw_smart_arrow_line(
                draw, from_pos, to_pos, 
                rendered_nodes[from_node].get('shape', 'rectangle'),
                rendered_nodes[to_node].get('shape', 'rectangle'),
                line_type, label, rendered_nodes, from_node, to_node
            )
        
        return image
    
    def _reset_route_state(self, complex_routing_enabled: bool = False, route_bounds: Tuple[int, int, int, int] = None):
        """重置单次渲染中的连线路由状态。"""
        self._complex_routing_enabled = complex_routing_enabled
        self._route_channel_counts = {}
        self._label_rectangles = []
        self._route_bounds = route_bounds
    
    def _reserve_route_channel(self, from_node_id: str, to_node_id: str) -> int:
        """为同一对节点的连线分配稳定的错位通道。"""
        key = tuple(sorted([str(from_node_id), str(to_node_id)]))
        count = self._route_channel_counts.get(key, 0)
        self._route_channel_counts[key] = count + 1
        
        if count == 0:
            return 0
        direction = 1 if count % 2 == 1 else -1
        magnitude = (count + 1) // 2
        return direction * magnitude * self.route_channel_gap
    
    def _draw_node(self, draw: ImageDraw.ImageDraw, node_id: str, node_data: Dict[str, Any], pos: Tuple[int, int]):
        """
        绘制节点
        
        Args:
            draw: ImageDraw对象
            node_id: 节点ID
            node_data: 节点数据
            pos: 节点位置
        """
        # 归一化形状与类型，缺省时根据形状/文本智能推断
        raw_shape = node_data.get('shape', 'rectangle')
        shape = 'rounded_rectangle' if raw_shape == 'rounded' else raw_shape
        text = node_data.get('text', node_id)
        raw_type = node_data.get('type') or node_data.get('node_type')
        if not raw_type:
            t_lower = str(text).lower()
            if shape == 'diamond':
                raw_type = 'decision'
            elif ('开始' in str(text)) or ('start' in t_lower):
                raw_type = 'start'
            elif ('结束' in str(text)) or ('完成' in str(text)) or ('end' in t_lower):
                raw_type = 'end'
            else:
                raw_type = 'operation'
        
        # 获取填充颜色，考虑节点类型和形状
        fill_color = self._get_node_fill_color(raw_type, shape)
        
        # 根据形状绘制节点
        if shape == 'rectangle':
            self._draw_rectangle_node(draw, pos, fill_color)
        elif shape == 'rounded_rectangle':
            self._draw_rounded_rectangle_node(draw, pos, fill_color)
        elif shape == 'diamond':
            self._draw_diamond_node(draw, pos, fill_color)
        elif shape == 'circle':
            self._draw_circle_node(draw, pos, fill_color)
        elif shape == 'parallelogram':
            self._draw_parallelogram_node(draw, pos, fill_color)
        elif shape == 'subroutine':
            self._draw_subroutine_node(draw, pos, fill_color)
        elif shape == 'cylinder':
            self._draw_cylinder_node(draw, pos, fill_color)
        elif shape == 'stadium':
            self._draw_stadium_node(draw, pos, fill_color)
        else:
            # 默认为矩形
            self._draw_rectangle_node(draw, pos, fill_color)
        
        # 绘制文本
        self._draw_node_text(draw, pos, text)
    
    def _draw_rectangle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制矩形节点"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        
        x1 = pos[0] - half_width
        y1 = pos[1] - half_height
        x2 = pos[0] + half_width
        y2 = pos[1] + half_height
        
        draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_rounded_rectangle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制圆角矩形节点"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        radius = 10  # 圆角半径
        
        x1 = pos[0] - half_width
        y1 = pos[1] - half_height
        x2 = pos[0] + half_width
        y2 = pos[1] + half_height
        
        # 绘制圆角矩形（简化版，使用多个形状组合）
        # 主体矩形
        draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 四个角的圆
        draw.pieslice([x1, y1, x1+2*radius, y1+2*radius], 180, 270, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        draw.pieslice([x2-2*radius, y1, x2, y1+2*radius], 270, 360, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        draw.pieslice([x2-2*radius, y2-2*radius, x2, y2], 0, 90, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        draw.pieslice([x1, y2-2*radius, x1+2*radius, y2], 90, 180, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_diamond_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制菱形节点"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        
        points = [
            (pos[0], pos[1] - half_height),  # 上
            (pos[0] + half_width, pos[1]),   # 右
            (pos[0], pos[1] + half_height),  # 下
            (pos[0] - half_width, pos[1])    # 左
        ]
        
        draw.polygon(points, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_circle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制圆形节点"""
        radius = min(self.node_width, self.node_height) // 2
        
        x1 = pos[0] - radius
        y1 = pos[1] - radius
        x2 = pos[0] + radius
        y2 = pos[1] + radius
        
        draw.ellipse([x1, y1, x2, y2], fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_parallelogram_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制平行四边形节点"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        offset = 15  # 倾斜量
        
        points = [
            (pos[0] - half_width + offset, pos[1] - half_height),  # 左上
            (pos[0] + half_width + offset, pos[1] - half_height),  # 右上
            (pos[0] + half_width - offset, pos[1] + half_height),  # 右下
            (pos[0] - half_width - offset, pos[1] + half_height)   # 左下
        ]
        
        draw.polygon(points, fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_subroutine_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制子程序节点（带双线边框）"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        
        x1 = pos[0] - half_width
        y1 = pos[1] - half_height
        x2 = pos[0] + half_width
        y2 = pos[1] + half_height
        
        # 外边框
        draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 内边框
        inner_offset = 5
        draw.rectangle([x1+inner_offset, y1+inner_offset, x2-inner_offset, y2-inner_offset], 
                      fill=None, outline=self.colors['node_outline'], width=1)
    
    def _draw_cylinder_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制圆柱形节点"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        ellipse_height = 15  # 椭圆高度
        
        # 主体矩形
        draw.rectangle([pos[0]-half_width, pos[1]-half_height+ellipse_height//2, 
                       pos[0]+half_width, pos[1]+half_height-ellipse_height//2], 
                      fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 顶部椭圆
        draw.ellipse([pos[0]-half_width, pos[1]-half_height, 
                     pos[0]+half_width, pos[1]-half_height+ellipse_height], 
                    fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 底部椭圆
        draw.ellipse([pos[0]-half_width, pos[1]+half_height-ellipse_height, 
                     pos[0]+half_width, pos[1]+half_height], 
                    fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    def _draw_stadium_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], fill_color: str):
        """绘制体育场形节点（矩形两端加半圆）"""
        half_width = self.node_width // 2
        half_height = self.node_height // 2
        radius = half_height
        
        # 中间矩形
        draw.rectangle([pos[0]-half_width+radius, pos[1]-half_height, 
                       pos[0]+half_width-radius, pos[1]+half_height], 
                      fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 左侧半圆
        draw.ellipse([pos[0]-half_width, pos[1]-half_height, 
                     pos[0]-half_width+2*radius, pos[1]+half_height], 
                    fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
        
        # 右侧半圆
        draw.ellipse([pos[0]+half_width-2*radius, pos[1]-half_height, 
                     pos[0]+half_width, pos[1]+half_height], 
                    fill=fill_color, outline=self.colors['node_outline'], width=self.line_widths['node_outline'])
    
    
    def _format_text_for_display_enhanced(self, text: str, max_width: int = 120) -> str:
        """
        增强的文本格式化方法，更好地处理中英文混合文本
        
        Args:
            text: 原始文本
            max_width: 最大宽度（字符数）
            
        Returns:
            格式化后的文本
        """
        if not text:
            return ""
        
        # 检测文本语言
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(text)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        # 如果主要是中文，使用中文换行规则
        if chinese_ratio > 0.5:
            return self._format_chinese_text_enhanced(text, max_width)
        else:
            return self._format_english_text_enhanced(text, max_width)
    
    def _format_chinese_text_enhanced(self, text: str, max_width: int) -> str:
        """
        增强的中文文本格式化
        """
        # 中文标点符号
        chinese_punctuation = '，。！？；：""''（）【】《》'
        
        lines = []
        current_line = ""
        
        for char in text:
            # 如果当前行已达到最大宽度，尝试在标点符号处换行
            if len(current_line) >= max_width:
                # 寻找最近的标点符号
                last_punct_pos = -1
                for i in range(len(current_line) - 1, -1, -1):
                    if current_line[i] in chinese_punctuation:
                        last_punct_pos = i
                        break
                
                if last_punct_pos > 0:
                    # 在标点符号后换行
                    lines.append(current_line[:last_punct_pos + 1])
                    current_line = current_line[last_punct_pos + 1:] + char
                else:
                    # 强制换行
                    lines.append(current_line)
                    current_line = char
            else:
                current_line += char
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
    
    def _format_english_text_enhanced(self, text: str, max_width: int) -> str:
        """
        增强的英文文本格式化
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # 如果单词本身超过最大宽度，强制换行
            if len(word) > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                
                # 分割长单词
                while len(word) > max_width:
                    lines.append(word[:max_width])
                    word = word[max_width:]
                
                current_line = word
            else:
                # 检查添加这个单词是否会超过最大宽度
                if current_line:
                    test_line = current_line + " " + word
                else:
                    test_line = word
                
                if len(test_line) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)

    def _draw_node_text(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], text: str):
        """Draw text on node with improved font handling"""
        # 格式化文本
        text = self._format_text_for_display_enhanced(text)
        
        # 初始化字体变量
        font = None
        bold_font = None
        
        # 检查文本是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        # 如果包含中文字符，优先使用中文字体
        if has_chinese:
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, self.font_size)
                    # print(f"Successfully loaded Chinese font: {self.font_path}")
                # print("No Chinese font path available")
            except Exception as e:
                # print(f"Failed to load Chinese font: {e}")
                # 尝试加载备选字体
                for fallback_font in self.fallback_fonts:
                    try:
                        font = ImageFont.truetype(fallback_font, self.font_size)
                        # print(f"Successfully loaded fallback Chinese font: {fallback_font}")
                        break
                    except Exception as e:
                        # print(f"Failed to load fallback Chinese font {fallback_font}: {e}")
                        continue
        else:
            # 英文文本，尝试加载英文字体
            try:
                # 尝试加载系统英文字体
                english_fonts = [
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "C:\\Windows\\Fonts\\calibri.ttf",
                    "C:\\Windows\\Fonts\\verdana.ttf",
                    "C:\\Windows\\Fonts\\tahoma.ttf"
                ]
                
                for english_font in english_fonts:
                    if os.path.exists(english_font):
                        try:
                            font = ImageFont.truetype(english_font, self.font_size)
                            # print(f"Successfully loaded English font: {english_font}")
                            break
                        except Exception as e:
                            # print(f"Failed to load English font {english_font}: {e}")
                            continue
                
                # 如果英文字体加载失败，尝试使用中文字体
                if not font and self.font_path:
                    font = ImageFont.truetype(self.font_path, self.font_size)
                    # print(f"Using Chinese font for English text: {self.font_path}")
            except Exception as e:
                # print(f"Failed to load any font for English text: {e}")
                pass
        
        # 尝试加载加粗字体 - 优先使用加粗字体
        try:
            if self.bold_font_path:
                bold_font = ImageFont.truetype(self.bold_font_path, self.font_size)
                # print(f"Successfully loaded bold font: {self.bold_font_path}")
            else:
                # 如果没有专门的加粗字体，尝试使用原始字体的加粗版本
                if font and self.font_path:
                    try:
                        bold_font = ImageFont.truetype(self.font_path, self.font_size, index=1)
                        # print(f"Successfully loaded bold variant of main font")
                    except Exception as e:
                        # print(f"Failed to load bold variant: {e}")
                        bold_font = font
                else:
                    # 尝试加载备选加粗字体
                    for fallback_bold_font in self.fallback_bold_fonts:
                        try:
                            bold_font = ImageFont.truetype(fallback_bold_font, self.font_size)
                            # print(f"Successfully loaded fallback bold font: {fallback_bold_font}")
                            break
                        except Exception as e:
                            # print(f"Failed to load fallback bold font {fallback_bold_font}: {e}")
                            continue
        except Exception as e:
            # print(f"Failed to load bold font: {e}")
            # 如果加载加粗字体失败，使用普通字体
            bold_font = font
        
        # 如果所有字体都加载失败，使用默认字体
        if not font:
            try:
                font = ImageFont.load_default()
                bold_font = font
                # print("Using default font")
            except Exception as e:
                # print(f"Failed to load default font: {e}")
                font = None
                bold_font = None
        
        # 计算文本边界框
        if font and hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        elif font and hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(text, font=font)
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        else:
            # 回退到估算
            text_width = len(text) * 8
            text_height = 14
            text_x = pos[0] - text_width // 2
            text_y = pos[1] - text_height // 2
        
        # 绘制文本 - 优先使用加粗字体
        if bold_font or font:
            draw.text((text_x, text_y), text, fill=self.colors['text'], font=bold_font if bold_font else font)
            # print(f"Successfully drew text: {text}")
        else:
            # 如果没有可用字体，使用默认绘制方式
            draw.text((text_x, text_y), text, fill=self.colors['text'])
            # print(f"Drew text without font: {text}")
    
    def _draw_smart_arrow_line(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                              from_shape="rectangle", to_shape="rectangle", line_type="solid", 
                              label=None, nodes=None, from_node_id="", to_node_id=""):
        """
        智能绘制带箭头的线，确保不穿过节点
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
            from_shape: 起始节点形状
            to_shape: 结束节点形状
            line_type: 线条类型
            label: 标签文本
            nodes: 所有节点信息，用于检测碰撞
            from_node_id: 起始节点ID
            to_node_id: 结束节点ID
        """
        # 计算节点边缘的位置（避免箭头被节点遮挡）
        from_adjusted_pos = self._calculate_node_edge_point(from_pos, to_pos, from_shape)
        to_adjusted_pos = self._calculate_node_edge_point(to_pos, from_pos, to_shape)
        if getattr(self, "_complex_routing_enabled", False):
            path_points = self._find_complex_curve_path(
                from_adjusted_pos, to_adjusted_pos, nodes, from_pos, to_pos, from_node_id, to_node_id
            )
            self._draw_path_with_arrow(draw, path_points, line_type)
            if label and len(path_points) >= 2:
                label_segment_index = self._select_label_segment_index(path_points)
                self._draw_edge_label(
                    draw, path_points[label_segment_index], path_points[label_segment_index + 1],
                    label, from_node_id, to_node_id
                )
            return
        
        # 尝试直接连接
        if not self._line_intersects_nodes(from_adjusted_pos, to_adjusted_pos, nodes, from_pos, to_pos):
            # 直接连接不穿过任何节点，使用简单连线
            self._draw_arrow_line_by_type(draw, from_adjusted_pos, to_adjusted_pos, line_type)
            if label:
                self._draw_edge_label_enhanced(draw, from_adjusted_pos, to_adjusted_pos, label)
            return
        
        # 直接连接会穿过节点，尝试找到绕行路径
        path_points = self._find_path_around_nodes(from_adjusted_pos, to_adjusted_pos, nodes, from_pos, to_pos)
        
        # 绘制路径
        for i in range(len(path_points) - 1):
            self._draw_arrow_line_by_type(draw, path_points[i], path_points[i+1], line_type, is_last_segment=(i == len(path_points) - 2))
        
        # 绘制标签（在路径中点）
        if label and len(path_points) >= 2:
            mid_index = len(path_points) // 2
            # 确保不会越界
            if mid_index + 1 < len(path_points):
                self._draw_edge_label(draw, path_points[mid_index], path_points[mid_index+1], label, from_node_id, to_node_id)
            else:
                # 如果只有两个点，使用这两个点
                self._draw_edge_label(draw, path_points[0], path_points[1], label, from_node_id, to_node_id)
    
    def _draw_path_with_arrow(self, draw: ImageDraw.ImageDraw, path_points: List[Tuple[int, int]], line_type="solid"):
        for i in range(len(path_points) - 1):
            self._draw_arrow_line_by_type(
                draw, path_points[i], path_points[i + 1], line_type,
                is_last_segment=(i == len(path_points) - 2)
            )
    
    def _select_label_segment_index(self, path_points: List[Tuple[int, int]]) -> int:
        if len(path_points) <= 2:
            return 0
        return max(0, min(len(path_points) - 2, len(path_points) // 2 - 1))
    
    def _find_complex_curve_path(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                 nodes: Dict[str, Any], from_node_pos: Tuple[int, int],
                                 to_node_pos: Tuple[int, int], from_node_id: str,
                                 to_node_id: str) -> List[Tuple[int, int]]:
        """复杂自由结构优先使用贝塞尔曲线分流，碰到节点时回退到正交路由。"""
        channel_offset = self._reserve_route_channel(from_node_id, to_node_id)
        curve_path = self._build_bezier_curve_path(from_pos, to_pos, channel_offset)
        boundaries = self._build_node_boundaries(nodes, from_node_pos, to_node_pos, padding=12)
        if self._path_within_route_bounds(curve_path) and not self._path_intersects_boundaries(curve_path, boundaries):
            return curve_path
        
        fallback = self._find_complex_orthogonal_path_with_offset(
            from_pos, to_pos, nodes, from_node_pos, to_node_pos, channel_offset
        )
        if self._path_within_route_bounds(fallback):
            return fallback
        return self._clamp_path_to_route_bounds(fallback)
    
    def _build_bezier_curve_path(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                 channel_offset: int) -> List[Tuple[int, int]]:
        x1, y1 = from_pos
        x2, y2 = to_pos
        dx = x2 - x1
        dy = y2 - y1
        distance = max(1.0, math.sqrt(dx ** 2 + dy ** 2))
        unit_x = dx / distance
        unit_y = dy / distance
        perp_x = -unit_y
        perp_y = unit_x
        
        base_curve = min(120, max(35, distance * 0.22))
        bend = base_curve + abs(channel_offset) * 1.1
        direction = 1 if channel_offset >= 0 else -1
        
        control1 = (
            x1 + dx * 0.33 + perp_x * bend * direction,
            y1 + dy * 0.33 + perp_y * bend * direction,
        )
        control2 = (
            x1 + dx * 0.67 + perp_x * bend * direction,
            y1 + dy * 0.67 + perp_y * bend * direction,
        )
        
        points = []
        for index in range(self.curve_sample_count + 1):
            t = index / self.curve_sample_count
            point = self._cubic_bezier_point(from_pos, control1, control2, to_pos, t)
            int_point = (int(round(point[0])), int(round(point[1])))
            if not points or points[-1] != int_point:
                points.append(int_point)
        return points
    
    def _cubic_bezier_point(self, p0, p1, p2, p3, t: float) -> Tuple[float, float]:
        inv = 1 - t
        x = (
            inv ** 3 * p0[0] +
            3 * inv ** 2 * t * p1[0] +
            3 * inv * t ** 2 * p2[0] +
            t ** 3 * p3[0]
        )
        y = (
            inv ** 3 * p0[1] +
            3 * inv ** 2 * t * p1[1] +
            3 * inv * t ** 2 * p2[1] +
            t ** 3 * p3[1]
        )
        return x, y
    
    def _find_complex_orthogonal_path_with_offset(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                                  nodes: Dict[str, Any], from_node_pos: Tuple[int, int],
                                                  to_node_pos: Tuple[int, int],
                                                  channel_offset: int) -> List[Tuple[int, int]]:
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        candidates = []
        
        if abs(dx) >= abs(dy):
            mid_x = (from_pos[0] + to_pos[0]) // 2 + channel_offset
            candidates.append([from_pos, (mid_x, from_pos[1]), (mid_x, to_pos[1]), to_pos])
            candidates.append([from_pos, (from_pos[0], from_pos[1] + channel_offset), (to_pos[0], from_pos[1] + channel_offset), to_pos])
        else:
            mid_y = (from_pos[1] + to_pos[1]) // 2 + channel_offset
            candidates.append([from_pos, (from_pos[0], mid_y), (to_pos[0], mid_y), to_pos])
            candidates.append([from_pos, (from_pos[0] + channel_offset, from_pos[1]), (from_pos[0] + channel_offset, to_pos[1]), to_pos])
        
        detour = max(self.node_width, self.node_height) + abs(channel_offset) + 40
        candidates.extend([
            [from_pos, (from_pos[0], from_pos[1] - detour), (to_pos[0], from_pos[1] - detour), to_pos],
            [from_pos, (from_pos[0], from_pos[1] + detour), (to_pos[0], from_pos[1] + detour), to_pos],
            [from_pos, (from_pos[0] - detour, from_pos[1]), (from_pos[0] - detour, to_pos[1]), to_pos],
            [from_pos, (from_pos[0] + detour, from_pos[1]), (from_pos[0] + detour, to_pos[1]), to_pos],
        ])
        
        node_boundaries = self._build_node_boundaries(nodes, from_node_pos, to_node_pos, padding=12)
        valid_candidates = [
            candidate for candidate in candidates
            if self._path_within_route_bounds(candidate) and not self._path_intersects_boundaries(candidate, node_boundaries)
        ]
        if valid_candidates:
            return min(valid_candidates, key=self._path_score)
        fallback = self._find_path_around_nodes(from_pos, to_pos, nodes, from_node_pos, to_node_pos)
        if fallback and self._path_within_route_bounds(fallback):
            return fallback
        direct = [from_pos, to_pos]
        return direct if self._path_within_route_bounds(direct) else self._clamp_path_to_route_bounds(direct)
    
    def _find_complex_orthogonal_path(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                      nodes: Dict[str, Any], from_node_pos: Tuple[int, int],
                                      to_node_pos: Tuple[int, int], from_node_id: str,
                                      to_node_id: str) -> List[Tuple[int, int]]:
        """复杂图使用正交折线和通道偏移，减少线条互相覆盖。"""
        channel_offset = self._reserve_route_channel(from_node_id, to_node_id)
        return self._find_complex_orthogonal_path_with_offset(
            from_pos, to_pos, nodes, from_node_pos, to_node_pos, channel_offset
        )
    
    def _build_node_boundaries(self, nodes: Dict[str, Any], from_node_pos: Tuple[int, int],
                               to_node_pos: Tuple[int, int], padding: int = 5) -> List[Dict]:
        boundaries = []
        if not nodes:
            return boundaries
        for node_data in nodes.values():
            node_center = (node_data['x'], node_data['y'])
            if node_center == from_node_pos or node_center == to_node_pos:
                continue
            node_shape = node_data.get('shape', 'rectangle')
            if node_shape == 'circle':
                boundaries.append({
                    'type': 'circle',
                    'center': node_center,
                    'radius': min(self.node_width, self.node_height) // 2 + padding
                })
            elif node_shape == 'diamond':
                boundaries.append({
                    'type': 'diamond',
                    'center': node_center,
                    'half_width': self.node_width // 2 + padding,
                    'half_height': self.node_height // 2 + padding
                })
            else:
                boundaries.append({
                    'type': 'rectangle',
                    'center': node_center,
                    'half_width': self.node_width // 2 + padding,
                    'half_height': self.node_height // 2 + padding
                })
        return boundaries
    
    def _path_intersects_boundaries(self, path_points: List[Tuple[int, int]], boundaries: List[Dict]) -> bool:
        for index in range(len(path_points) - 1):
            if self._line_intersects_boundaries(path_points[index], path_points[index + 1], boundaries):
                return True
        return False
    
    def _path_within_route_bounds(self, path_points: List[Tuple[int, int]]) -> bool:
        if not getattr(self, "_route_bounds", None):
            return True
        left, top, right, bottom = self._route_bounds
        return all(left <= point[0] <= right and top <= point[1] <= bottom for point in path_points)
    
    def _clamp_path_to_route_bounds(self, path_points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if not getattr(self, "_route_bounds", None):
            return path_points
        left, top, right, bottom = self._route_bounds
        clamped = []
        for x, y in path_points:
            clamped.append((int(min(max(x, left), right)), int(min(max(y, top), bottom))))
        return clamped
    
    def _path_score(self, path_points: List[Tuple[int, int]]) -> float:
        length = 0.0
        turns = max(0, len(path_points) - 2)
        for index in range(len(path_points) - 1):
            p1 = path_points[index]
            p2 = path_points[index + 1]
            length += math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        return length + turns * 35
    
    def _draw_arrow_line_by_type(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                                line_type="solid", is_last_segment=True):
        """
        根据线条类型绘制带箭头的线
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
            line_type: 线条类型
            is_last_segment: 是否是最后一段（只在最后一段绘制箭头）
        """
        # 计算箭头方向
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        # 处理零距离情况
        if dx == 0 and dy == 0:
            return
        
        # 根据线条类型绘制线
        if line_type == "dotted":
            self._draw_dotted_line_segment(draw, from_pos, to_pos)
        elif line_type == "thick":
            draw.line([from_pos, to_pos], fill=self.colors['arrow'], width=4)
        else:  # solid
            draw.line([from_pos, to_pos], fill=self.colors['arrow'], width=self.line_widths['arrow'])
        
        # 只在最后一段绘制箭头
        if is_last_segment:
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
            draw.polygon([(to_pos[0], to_pos[1]), (x1, y1), (x2, y2)], fill=self.colors['arrow'])
    
    def _draw_dotted_line_segment(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """绘制虚线段"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        # 计算虚线的段数和每段的长度
        line_length = math.sqrt(dx**2 + dy**2)
        if line_length == 0:
            return
            
        dash_length = 5
        gap_length = 3
        segment_length = dash_length + gap_length
        
        # 计算需要多少段虚线
        num_segments = int(line_length / segment_length)
        
        # 绘制虚线段
        for i in range(num_segments):
            start_segment = (
                from_pos[0] + (dx * i * segment_length) / line_length,
                from_pos[1] + (dy * i * segment_length) / line_length
            )
            
            end_segment = (
                from_pos[0] + (dx * (i * segment_length + dash_length)) / line_length,
                from_pos[1] + (dy * (i * segment_length + dash_length)) / line_length
            )
            
            # 确保不会超出终点
            if math.sqrt((end_segment[0] - from_pos[0])**2 + (end_segment[1] - from_pos[1])**2) < line_length:
                draw.line([start_segment, end_segment], fill=self.colors['arrow'], width=self.line_widths['arrow'])
    
    def _line_intersects_nodes(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                              nodes: Dict[str, Any], from_node_pos: Tuple[int, int], to_node_pos: Tuple[int, int]) -> bool:
        """
        检查线段是否与任何节点相交（除了起始和结束节点）
        
        Args:
            from_pos: 线段起始位置（节点边缘）
            to_pos: 线段结束位置（节点边缘）
            nodes: 所有节点信息
            from_node_pos: 起始节点中心位置
            to_node_pos: 结束节点中心位置
            
        Returns:
            是否与任何节点相交
        """
        if not nodes:
            return False
            
        for node_id, node_data in nodes.items():
            # 跳过起始和结束节点
            node_center = (node_data['x'], node_data['y'])
            if node_center == from_node_pos or node_center == to_node_pos:
                continue
                
            # 检查线段是否与节点矩形相交
            node_shape = node_data.get('shape', 'rectangle')
            
            if node_shape == 'circle':
                # 圆形节点
                radius = min(self.node_width, self.node_height) // 2
                if self._line_intersects_circle(from_pos, to_pos, node_center, radius):
                    return True
            elif node_shape == 'diamond':
                # 菱形节点
                half_width = self.node_width // 2
                half_height = self.node_height // 2
                if self._line_intersects_diamond(from_pos, to_pos, node_center, half_width, half_height):
                    return True
            else:
                # 默认为矩形节点
                half_width = self.node_width // 2
                half_height = self.node_height // 2
                if self._line_intersects_rectangle(from_pos, to_pos, node_center, half_width, half_height):
                    return True
        
        return False
    
    def _line_intersects_rectangle(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                                  center: Tuple[int, int], half_width: int, half_height: int) -> bool:
        """检查线段是否与矩形相交"""
        # 矩形边界
        left = center[0] - half_width
        right = center[0] + half_width
        top = center[1] - half_height
        bottom = center[1] + half_height
        
        # 检查线段端点是否在矩形内
        if (left <= p1[0] <= right and top <= p1[1] <= bottom) or \
           (left <= p2[0] <= right and top <= p2[1] <= bottom):
            return True
        
        # 检查线段是否与矩形的四条边相交
        return (self._line_segments_intersect(p1, p2, (left, top), (right, top)) or  # 上边
                self._line_segments_intersect(p1, p2, (right, top), (right, bottom)) or  # 右边
                self._line_segments_intersect(p1, p2, (right, bottom), (left, bottom)) or  # 下边
                self._line_segments_intersect(p1, p2, (left, bottom), (left, top)))  # 左边
    
    def _line_intersects_circle(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                               center: Tuple[int, int], radius: int) -> bool:
        """检查线段是否与圆相交"""
        # 计算线段到圆心的最短距离
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        if dx == 0 and dy == 0:
            # 线段退化为点
            dist = math.sqrt((p1[0] - center[0])**2 + (p1[1] - center[1])**2)
            return dist <= radius
        
        # 计算投影参数
        t = max(0, min(1, ((center[0] - p1[0]) * dx + (center[1] - p1[1]) * dy) / (dx * dx + dy * dy)))
        
        # 计算最近点
        closest_x = p1[0] + t * dx
        closest_y = p1[1] + t * dy
        
        # 计算距离
        dist = math.sqrt((closest_x - center[0])**2 + (closest_y - center[1])**2)
        
        return dist <= radius
    
    def _line_intersects_diamond(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                                center: Tuple[int, int], half_width: int, half_height: int) -> bool:
        """检查线段是否与菱形相交"""
        # 菱形的四个顶点
        top = (center[0], center[1] - half_height)
        right = (center[0] + half_width, center[1])
        bottom = (center[0], center[1] + half_height)
        left = (center[0] - half_width, center[1])
        
        # 检查线段是否与菱形的四条边相交
        return (self._line_segments_intersect(p1, p2, top, right) or
                self._line_segments_intersect(p1, p2, right, bottom) or
                self._line_segments_intersect(p1, p2, bottom, left) or
                self._line_segments_intersect(p1, p2, left, top))
    
    def _line_segments_intersect(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                               p3: Tuple[int, int], p4: Tuple[int, int]) -> bool:
        """检查两条线段是否相交"""
        # 计算方向
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
        # 检查相交
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _find_path_around_nodes(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                               nodes: Dict[str, Any], from_node_pos: Tuple[int, int], to_node_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        找到绕过节点的路径，使用更智能的路径规划算法
        
        Args:
            from_pos: 起始位置（节点边缘）
            to_pos: 结束位置（节点边缘）
            nodes: 所有节点信息
            from_node_pos: 起始节点中心位置
            to_node_pos: 结束节点中心位置
            
        Returns:
            路径点列表
        """
        # 动态调整偏移量，基于节点大小和距离
        node_size = max(self.node_width, self.node_height)
        distance = math.sqrt((to_pos[0] - from_pos[0])**2 + (to_pos[1] - from_pos[1])**2)
        
        # 基础偏移量：节点大小的一半加上一些余量
        base_offset = node_size // 2 + 25  # 增加余量，确保线条不会太贴近节点
        # 根据距离调整偏移量，距离越远偏移量可以适当减小
        distance_factor = min(1.5, max(0.8, distance / 500))
        initial_offset = int(base_offset * distance_factor)
        
        # 计算直接路径的中点
        mid_x = (from_pos[0] + to_pos[0]) // 2
        mid_y = (from_pos[1] + to_pos[1]) // 2
        
        # 计算方向向量
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if distance == 0:
            return [from_pos, to_pos]
        
        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance
        
        # 计算垂直于主方向的单位向量
        perp_x = -unit_y
        perp_y = unit_x
        
        # 创建一个节点边界框的列表，用于快速碰撞检测
        node_boundaries = []
        for node_id, node_data in nodes.items():
            # 跳过起始和结束节点
            node_center = (node_data['x'], node_data['y'])
            if node_center == from_node_pos or node_center == to_node_pos:
                continue
            
            # 根据节点形状创建边界框
            node_shape = node_data.get('shape', 'rectangle')
            if node_shape == 'circle':
                radius = min(self.node_width, self.node_height) // 2 + 5  # 添加额外边距
                node_boundaries.append({
                    'type': 'circle',
                    'center': node_center,
                    'radius': radius
                })
            elif node_shape == 'diamond':
                half_width = self.node_width // 2 + 5  # 添加额外边距
                half_height = self.node_height // 2 + 5
                node_boundaries.append({
                    'type': 'diamond',
                    'center': node_center,
                    'half_width': half_width,
                    'half_height': half_height
                })
            else:
                # 默认为矩形节点
                half_width = self.node_width // 2 + 5  # 添加额外边距
                half_height = self.node_height // 2 + 5
                node_boundaries.append({
                    'type': 'rectangle',
                    'center': node_center,
                    'half_width': half_width,
                    'half_height': half_height
                })
        
        # 尝试多个候选路径，优先选择最短且不相交的路径
        candidates = []
        
        # 1. 尝试单点绕行路径（4个主要方向）
        candidates.append([from_pos, (mid_x + int(perp_x * initial_offset), mid_y + int(perp_y * initial_offset)), to_pos])
        candidates.append([from_pos, (mid_x - int(perp_x * initial_offset), mid_y - int(perp_y * initial_offset)), to_pos])
        candidates.append([from_pos, (mid_x + int(unit_x * initial_offset), mid_y + int(unit_y * initial_offset)), to_pos])
        candidates.append([from_pos, (mid_x - int(unit_x * initial_offset), mid_y - int(unit_y * initial_offset)), to_pos])
        
        # 2. 尝试两点绕行路径（L形路径）
        # 水平优先
        corner1 = (to_pos[0], from_pos[1])
        candidates.append([from_pos, corner1, to_pos])
        
        # 垂直优先
        corner2 = (from_pos[0], to_pos[1])
        candidates.append([from_pos, corner2, to_pos])
        
        # 3. 尝试Z形路径（三点绕行）
        # 上方绕行
        candidates.append([
            from_pos, 
            (from_pos[0] + int(unit_x * initial_offset/2), from_pos[1] - int(initial_offset)),
            (to_pos[0] - int(unit_x * initial_offset/2), to_pos[1] - int(initial_offset)),
            to_pos
        ])
        
        # 下方绕行
        candidates.append([
            from_pos, 
            (from_pos[0] + int(unit_x * initial_offset/2), from_pos[1] + int(initial_offset)),
            (to_pos[0] - int(unit_x * initial_offset/2), to_pos[1] + int(initial_offset)),
            to_pos
        ])
        
        # 4. 尝试S形路径（四点绕行）
        # 左侧绕行
        candidates.append([
            from_pos,
            (from_pos[0] - int(initial_offset), from_pos[1] + int(unit_y * initial_offset/2)),
            (to_pos[0] - int(initial_offset), to_pos[1] - int(unit_y * initial_offset/2)),
            to_pos
        ])
        
        # 右侧绕行
        candidates.append([
            from_pos,
            (from_pos[0] + int(initial_offset), from_pos[1] + int(unit_y * initial_offset/2)),
            (to_pos[0] + int(initial_offset), to_pos[1] - int(unit_y * initial_offset/2)),
            to_pos
        ])
        
        # 5. 对于较长的路径，尝试更复杂的绕行方式
        if distance > 200:
            # 多点绕行路径
            offset = initial_offset * 1.2
            
            # 上方多点绕行
            candidates.append([
                from_pos,
                (from_pos[0] + dx // 4, from_pos[1] - int(offset)),
                (from_pos[0] + dx // 2, from_pos[1] - int(offset * 0.8)),
                (from_pos[0] + 3 * dx // 4, from_pos[1] - int(offset)),
                to_pos
            ])
            
            # 下方多点绕行
            candidates.append([
                from_pos,
                (from_pos[0] + dx // 4, from_pos[1] + int(offset)),
                (from_pos[0] + dx // 2, from_pos[1] + int(offset * 0.8)),
                (from_pos[0] + 3 * dx // 4, from_pos[1] + int(offset)),
                to_pos
            ])
        
        # 评估每个候选路径
        best_path = None
        best_score = float('inf')
        
        for candidate in candidates:
            # 检查路径是否可行（所有线段都不与节点相交）
            path_is_valid = True
            
            for i in range(len(candidate) - 1):
                if self._line_intersects_boundaries(candidate[i], candidate[i+1], node_boundaries):
                    path_is_valid = False
                    break
            
            if not path_is_valid:
                continue
            
            # 计算路径长度
            path_length = 0
            for i in range(len(candidate) - 1):
                path_length += math.sqrt((candidate[i+1][0] - candidate[i][0])**2 + 
                                        (candidate[i+1][1] - candidate[i][1])**2)
            
            # 计算路径复杂度（转向次数和角度变化）
            path_complexity = 0
            for i in range(1, len(candidate) - 1):
                # 计算两个连续线段之间的角度变化
                v1 = (candidate[i][0] - candidate[i-1][0], candidate[i][1] - candidate[i-1][1])
                v2 = (candidate[i+1][0] - candidate[i][0], candidate[i+1][1] - candidate[i][1])
                
                # 归一化向量
                len1 = math.sqrt(v1[0]**2 + v1[1]**2)
                len2 = math.sqrt(v2[0]**2 + v2[1]**2)
                
                if len1 > 0 and len2 > 0:
                    v1_norm = (v1[0]/len1, v1[1]/len1)
                    v2_norm = (v2[0]/len2, v2[1]/len2)
                    
                    # 计算点积
                    dot_product = v1_norm[0]*v2_norm[0] + v1_norm[1]*v2_norm[1]
                    dot_product = max(-1, min(1, dot_product))  # 限制在[-1,1]范围内
                    
                    # 计算角度（弧度）
                    angle = math.acos(dot_product)
                    path_complexity += angle
            
            # 计算综合评分（路径长度 + 复杂度惩罚）
            score = path_length + path_complexity * 30  # 每弧度角度变化增加30的惩罚
            
            # 更新最佳路径
            if score < best_score:
                best_score = score
                best_path = candidate
        
        # 如果没有找到可行的绕行路径，尝试使用更大的偏移量
        if best_path is None:
            # 逐步增加偏移量，最多尝试3次
            for multiplier in [1.5, 2.0, 3.0]:
                offset = int(initial_offset * multiplier)
                
                # 重新尝试单点绕行路径
                candidates = [
                    [from_pos, (mid_x + int(perp_x * offset), mid_y + int(perp_y * offset)), to_pos],
                    [from_pos, (mid_x - int(perp_x * offset), mid_y - int(perp_y * offset)), to_pos],
                    [from_pos, (mid_x + int(unit_x * offset), mid_y + int(unit_y * offset)), to_pos],
                    [from_pos, (mid_x - int(unit_x * offset), mid_y - int(unit_y * offset)), to_pos]
                ]
                
                # 尝试L形路径
                candidates.append([from_pos, (to_pos[0], from_pos[1] - int(offset)), to_pos])
                candidates.append([from_pos, (to_pos[0], from_pos[1] + int(offset)), to_pos])
                candidates.append([from_pos, (from_pos[0] - int(offset), to_pos[1]), to_pos])
                candidates.append([from_pos, (from_pos[0] + int(offset), to_pos[1]), to_pos])
                
                for candidate in candidates:
                    path_is_valid = True
                    
                    for i in range(len(candidate) - 1):
                        if self._line_intersects_boundaries(candidate[i], candidate[i+1], node_boundaries):
                            path_is_valid = False
                            break
                    
                    if path_is_valid:
                        # 计算路径长度
                        path_length = 0
                        for i in range(len(candidate) - 1):
                            path_length += math.sqrt((candidate[i+1][0] - candidate[i][0])**2 + 
                                                    (candidate[i+1][1] - candidate[i][1])**2)
                        
                        if path_length < best_score:
                            best_score = path_length
                            best_path = candidate
                
                # 如果找到了可行路径，停止尝试更大的偏移量
                if best_path is not None:
                    break
        
        # 如果还是没有找到可行路径，返回直接路径（即使会穿过节点）
        if best_path is None:
            # print("Warning: Could not find a path that avoids all nodes, using direct path")
            best_path = [from_pos, to_pos]
        
        return best_path
    
    def _line_intersects_boundaries(self, p1: Tuple[int, int], p2: Tuple[int, int], 
                                   boundaries: List[Dict]) -> bool:
        """
        检查线段是否与任何边界框相交
        
        Args:
            p1: 线段起点
            p2: 线段终点
            boundaries: 边界框列表
            
        Returns:
            是否与任何边界框相交
        """
        for boundary in boundaries:
            if boundary['type'] == 'circle':
                if self._line_intersects_circle(p1, p2, boundary['center'], boundary['radius']):
                    return True
            elif boundary['type'] == 'diamond':
                if self._line_intersects_diamond(p1, p2, boundary['center'], boundary['half_width'], boundary['half_height']):
                    return True
            else:  # rectangle
                if self._line_intersects_rectangle(p1, p2, boundary['center'], boundary['half_width'], boundary['half_height']):
                    return True
        return False
    
    def _calculate_node_edge_point(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                                 shape: str) -> Tuple[int, int]:
        """
        计算节点边缘的点，用于连接线的起点或终点
        
        Args:
            from_pos: 起始节点位置
            to_pos: 目标节点位置
            shape: 节点形状
            
        Returns:
            节点边缘上的点坐标
        """
        # 节点尺寸
        width = self.node_width
        height = self.node_height
        
        # 计算方向向量
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return from_pos
        
        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance
        
        # 根据形状计算边缘点
        if shape == "circle":
            # 圆形节点
            radius = min(width, height) // 2
            edge_x = from_pos[0] + unit_x * radius
            edge_y = from_pos[1] + unit_y * radius
            return (int(edge_x), int(edge_y))
            
        elif shape == "diamond":
            # 菱形节点
            half_width = width // 2
            half_height = height // 2
            
            # 菱形的边界方程：|x/(w/2)| + |y/(h/2)| = 1
            # 计算与菱形边界的交点
            t = 1 / (abs(unit_x)/half_width + abs(unit_y)/half_height)
            edge_x = from_pos[0] + unit_x * t
            edge_y = from_pos[1] + unit_y * t
            return (int(edge_x), int(edge_y))
                
        elif shape == "stadium":
            # 体育场形节点（矩形两端加半圆）
            radius = height // 2
            half_width = width // 2 - radius
            half_height = height // 2  # 添加half_height定义
            
            # 判断方向向量主要指向哪个区域
            abs_dx = abs(unit_x)
            abs_dy = abs(unit_y)
            
            if abs_dx * half_height > abs_dy * half_width:
                # 指向左右两侧的半圆区域
                if unit_x > 0:
                    edge_x = from_pos[0] + half_width + radius
                else:
                    edge_x = from_pos[0] - (half_width + radius)
                edge_y = from_pos[1] + unit_y * radius
            else:
                # 指向上下两侧的矩形区域
                edge_x = from_pos[0] + unit_x * (half_width + radius)
                if unit_y > 0:
                    edge_y = from_pos[1] + half_height
                else:
                    edge_y = from_pos[1] - half_height
            return (int(edge_x), int(edge_y))
                
        else:
            # 默认为矩形节点
            half_width = width // 2
            half_height = height // 2
            
            # 计算与矩形边界的交点
            if abs(unit_x) * half_height > abs(unit_y) * half_width:
                # 更接近水平方向，与左右边相交
                if unit_x > 0:
                    edge_x = from_pos[0] + half_width
                else:
                    edge_x = from_pos[0] - half_width
                edge_y = from_pos[1] + unit_y * half_width / abs(unit_x)
            else:
                # 更接近垂直方向，与上下边相交
                if unit_y > 0:
                    edge_y = from_pos[1] + half_height
                else:
                    edge_y = from_pos[1] - half_height
                edge_x = from_pos[0] + unit_x * half_height / abs(unit_y)
            return (int(edge_x), int(edge_y))
    
    def _draw_edge_label(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], 
                        to_pos: Tuple[int, int], label: str, from_node_id: str = "", to_node_id: str = ""):
        """
        绘制边标签
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
            label: 标签文本
            from_node_id: 起始节点ID
            to_node_id: 结束节点ID
        """
        # 初始化字体变量
        font = None
        
        # 尝试加载主字体
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, self.font_size - 2)
                # print(f"Successfully loaded font for edge label: {self.font_path}")
        except Exception as e:
            # print(f"Failed to load font for edge label: {e}")
            # 尝试加载备选字体
            for fallback_font in self.fallback_fonts:
                try:
                    font = ImageFont.truetype(fallback_font, self.font_size - 2)
                    # print(f"Successfully loaded fallback font for edge label: {fallback_font}")
                    break
                except Exception as e:
                    # print(f"Failed to load fallback font for edge label {fallback_font}: {e}")
                    continue
        
        # 如果所有字体都加载失败，使用默认字体
        if not font:
            try:
                font = ImageFont.load_default()
                # print("Using default font for edge label")
            except Exception as e:
                # print(f"Failed to load default font for edge label: {e}")
                font = None
        
        # 计算标签位置（在线的中点）
        mid_x = (from_pos[0] + to_pos[0]) // 2
        mid_y = (from_pos[1] + to_pos[1]) // 2
        
        # 计算文本边界框
        if font and hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        elif font and hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(label, font=font)
        else:
            # 回退到估算
            text_width = len(label) * 8
            text_height = 14
        
        # 根据标签内容或节点ID选择颜色
        label_color = self._get_label_color(label, from_node_id, to_node_id)
        
        # 绘制背景矩形
        padding = 4
        bg_x1 = mid_x - text_width // 2 - padding
        bg_y1 = mid_y - text_height // 2 - padding
        bg_x2 = mid_x + text_width // 2 + padding
        bg_y2 = mid_y + text_height // 2 + padding
        bg_x1, bg_y1, bg_x2, bg_y2 = self._place_label_without_overlap((bg_x1, bg_y1, bg_x2, bg_y2))
        mid_x = (bg_x1 + bg_x2) // 2
        mid_y = (bg_y1 + bg_y2) // 2
        
        # 绘制阴影
        shadow_offset = 2
        shadow_rect = [bg_x1 + shadow_offset, bg_y1 + shadow_offset, bg_x2 + shadow_offset, bg_y2 + shadow_offset]
        draw.rectangle(shadow_rect, fill=(200, 200, 200), outline=None)
        
        # 绘制背景矩形，使用与标签匹配的颜色
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=label_color, outline=self.colors['node_outline'])
        
        # 绘制文本
        text_x = mid_x - text_width // 2
        text_y = mid_y - text_height // 2
        if font:
            draw.text((text_x, text_y), label, fill=self.colors['text'], font=font)
        else:
            draw.text((text_x, text_y), label, fill=self.colors['text'])
            # print("Drew edge label without font")
    
    def _get_label_color(self, label: str, from_node_id: str = "", to_node_id: str = "") -> str:
        """
        根据标签内容或节点ID选择颜色
        
        Args:
            label: 标签文本
            from_node_id: 起始节点ID
            to_node_id: 结束节点ID
            
        Returns:
            标签背景颜色
        """
        # 定义标签颜色映射
        label_colors = {
            # 条件相关
            "是": "#90EE90",  # 浅绿色
            "否": "#FFB6C1",  # 浅红色
            "真": "#90EE90",  # 浅绿色
            "假": "#FFB6C1",  # 浅红色
            "true": "#90EE90",  # 浅绿色
            "false": "#FFB6C1",  # 浅红色
            "yes": "#90EE90",  # 浅绿色
            "no": "#FFB6C1",  # 浅红色
            "通过": "#90EE90",  # 浅绿色
            "失败": "#FFB6C1",  # 浅红色
            "成功": "#90EE90",  # 浅绿色
            "错误": "#FFB6C1",  # 浅红色
            
            # 流程相关
            "开始": "#87CEEB",  # 天蓝色
            "结束": "#DDA0DD",  # 梅红色
            "start": "#87CEEB",  # 天蓝色
            "end": "#DDA0DD",  # 梅红色
            "begin": "#87CEEB",  # 天蓝色
            "finish": "#DDA0DD",  # 梅红色
            
            # 操作相关
            "处理": "#F0E68C",  # 卡其色
            "执行": "#F0E68C",  # 卡其色
            "process": "#F0E68C",  # 卡其色
            "execute": "#F0E68C",  # 卡其色
            "操作": "#F0E68C",  # 卡其色
            
            # 数据相关
            "输入": "#E0FFFF",  # 浅青色
            "输出": "#E0FFFF",  # 浅青色
            "input": "#E0FFFF",  # 浅青色
            "output": "#E0FFFF",  # 浅青色
            "数据": "#E0FFFF",  # 浅青色
            "data": "#E0FFFF",  # 浅青色
            
            # 决策相关
            "判断": "#FFFFE0",  # 浅黄色
            "决策": "#FFFFE0",  # 浅黄色
            "decision": "#FFFFE0",  # 浅黄色
            "judge": "#FFFFE0",  # 浅黄色
            "check": "#FFFFE0",  # 浅黄色
        }
        
        # 检查标签文本是否在颜色映射中
        label_lower = label.lower().strip()
        if label_lower in label_colors:
            return label_colors[label_lower]
        
        # 检查标签文本是否包含颜色映射中的关键词
        for keyword, color in label_colors.items():
            if keyword in label_lower:
                return color
        
        # 如果起始或结束节点是特殊类型，根据节点类型选择颜色
        if from_node_id.lower() in ["start", "开始"] or to_node_id.lower() in ["start", "开始"]:
            return "#87CEEB"  # 天蓝色
        elif from_node_id.lower() in ["end", "结束"] or to_node_id.lower() in ["end", "结束"]:
            return "#DDA0DD"  # 梅红色
        
        # 默认颜色
        return self.colors['background']
    def _draw_edge_label_enhanced(self, draw: ImageDraw.ImageDraw, from_pos: Tuple[int, int], 
                                to_pos: Tuple[int, int], label: str):
        """
        增强的边标签绘制方法，更好地处理标签位置和样式
        
        Args:
            draw: ImageDraw对象
            from_pos: 起始位置
            to_pos: 结束位置
            label: 标签文本
        """
        if not label:
            return
        
        # 初始化字体变量
        font = None
        
        # 检查标签是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', label))
        
        # 尝试加载字体
        if has_chinese:
            # 中文标签，优先使用中文字体
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, self.font_size - 2)
                    # print(f"Successfully loaded Chinese font for edge label: {self.font_path}")
                else:
                    # print("No Chinese font path available for edge label")
                    pass
            except Exception as e:
                # print(f"Failed to load Chinese font for edge label: {e}")
                # 尝试加载备选字体
                for fallback_font in self.fallback_fonts:
                    try:
                        font = ImageFont.truetype(fallback_font, self.font_size - 2)
                        # print(f"Successfully loaded fallback Chinese font for edge label: {fallback_font}")
                        break
                    except Exception as e:
                        # print(f"Failed to load fallback Chinese font for edge label {fallback_font}: {e}")
                        continue
        else:
            # 英文标签，尝试加载英文字体
            try:
                # 尝试加载系统英文字体
                english_fonts = [
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "C:\\Windows\\Fonts\\calibri.ttf",
                    "C:\\Windows\\Fonts\\verdana.ttf",
                    "C:\\Windows\\Fonts\\tahoma.ttf"
                ]
                
                for english_font in english_fonts:
                    if os.path.exists(english_font):
                        try:
                            font = ImageFont.truetype(english_font, self.font_size - 2)
                            # print(f"Successfully loaded English font for edge label: {english_font}")
                            break
                        except Exception as e:
                            # print(f"Failed to load English font for edge label {english_font}: {e}")
                            continue
                
                # 如果英文字体加载失败，尝试使用中文字体
                if not font and self.font_path:
                    font = ImageFont.truetype(self.font_path, self.font_size - 2)
                    # print(f"Using Chinese font for English edge label: {self.font_path}")
            except Exception as e:
                # print(f"Failed to load any font for English edge label: {e}")
                pass
        
        # 如果所有字体都加载失败，使用默认字体
        if not font:
            try:
                font = ImageFont.load_default()
                # print("Using default font for edge label")
            except Exception as e:
                # print(f"Failed to load default font for edge label: {e}")
                font = None
        
        # 计算标签位置（在线的中点，但稍微偏移以避免与线重叠）
        mid_x = (from_pos[0] + to_pos[0]) / 2
        mid_y = (from_pos[1] + to_pos[1]) / 2
        
        # 计算线的方向，用于确定标签偏移方向
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            # 计算垂直于线的方向
            perp_dx = -dy / length
            perp_dy = dx / length
            
            # 根据线的方向调整偏移量
            if abs(dx) > abs(dy):  # 水平线
                offset = 15
            else:  # 垂直线
                offset = 15
            
            # 应用偏移
            label_x = mid_x + perp_dx * offset
            label_y = mid_y + perp_dy * offset
        else:
            label_x = mid_x
            label_y = mid_y
        
        # 计算文本边界框
        if font and hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        elif font and hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(label, font=font)
        else:
            # 回退到估算
            text_width = len(label) * 8
            text_height = 14
        
        # 绘制背景矩形（带圆角）
        padding = 6
        bg_x1 = label_x - text_width // 2 - padding
        bg_y1 = label_y - text_height // 2 - padding
        bg_x2 = label_x + text_width // 2 + padding
        bg_y2 = label_y + text_height // 2 + padding
        bg_x1, bg_y1, bg_x2, bg_y2 = self._place_label_without_overlap((bg_x1, bg_y1, bg_x2, bg_y2))
        label_x = (bg_x1 + bg_x2) / 2
        label_y = (bg_y1 + bg_y2) / 2
        
        # 绘制阴影
        shadow_offset = 2
        shadow_rect = [bg_x1 + shadow_offset, bg_y1 + shadow_offset, bg_x2 + shadow_offset, bg_y2 + shadow_offset]
        draw.rectangle(shadow_rect, fill=(200, 200, 200), outline=None)
        
        # 绘制背景
        bg_rect = [bg_x1, bg_y1, bg_x2, bg_y2]
        draw.rectangle(bg_rect, fill=self.colors['background'], outline=self.colors['node_outline'])
        
        # 绘制文本
        text_x = label_x - text_width // 2
        text_y = label_y - text_height // 2
        if font:
            draw.text((text_x, text_y), label, fill=self.colors['text'], font=font)
        else:
            draw.text((text_x, text_y), label, fill=self.colors['text'])
            # print("Drew edge label without font")

    def _place_label_without_overlap(self, rect: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """为边标签寻找一个不与已有标签重叠的位置。"""
        if not getattr(self, "_label_rectangles", None):
            self._label_rectangles = []
        
        x1, y1, x2, y2 = rect
        offsets = [
            (0, 0), (0, -22), (0, 22), (28, 0), (-28, 0),
            (28, -22), (-28, -22), (28, 22), (-28, 22),
            (0, -44), (0, 44),
        ]
        for dx, dy in offsets:
            candidate = (x1 + dx, y1 + dy, x2 + dx, y2 + dy)
            if not any(self._rectangles_overlap_simple(candidate, used, margin=4) for used in self._label_rectangles):
                self._label_rectangles.append(candidate)
                return candidate
        
        self._label_rectangles.append(rect)
        return rect
    
    def _rectangles_overlap_simple(self, rect1: Tuple[float, float, float, float],
                                   rect2: Tuple[float, float, float, float],
                                   margin: int = 0) -> bool:
        left1, top1, right1, bottom1 = rect1
        left2, top2, right2, bottom2 = rect2
        return not (
            right1 + margin < left2 or
            right2 + margin < left1 or
            bottom1 + margin < top2 or
            bottom2 + margin < top1
        )



    
    def _setup_chinese_font(self):
        """
        设置中文字体，参考OptimizedFlowchartGenerator的实现
        """
        # 尝试获取插件内嵌字体路径
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取插件根目录
            plugin_root = os.path.dirname(current_dir)
            # 构建内嵌字体路径 - 使用绝对路径
            embedded_font_path = os.path.join(plugin_root, "fonts", "chinese_font.ttc")
            
            # 检查内嵌字体是否存在
            if os.path.exists(embedded_font_path):
                self.font_path = embedded_font_path
                # print(f"Using embedded font: {embedded_font_path}")
                return
            else:
                # print(f"Embedded font not found at: {embedded_font_path}")
                pass
        except Exception as e:
            # print(f"Error loading embedded font: {e}")
            pass
        
        # 如果内嵌字体不存在，尝试系统字体
        # 优化字体顺序，优先使用更现代的中文字体
        system_fonts = [
            "C:\\Windows\\Fonts\\msyh.ttc",      # 微软雅黑
            "C:\\Windows\\Fonts\\msyhbd.ttc",    # 微软雅黑加粗
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体加粗
            "C:\\Windows\\Fonts\\simsun.ttc",    # 宋体
            "C:\\Windows\\Fonts\\simkai.ttf",    # 楷体
            "/System/Library/Fonts/PingFang.ttc",      # macOS
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                self.font_path = font_path
                # print(f"Using system font: {font_path}")
                return
        
        # 如果都不存在，返回空字符串
        # print("No suitable font found, will use default font")
        self.font_path = ""
    
    def _get_fallback_fonts(self) -> List[str]:
        """
        获取备选字体列表
        参考OptimizedFlowchartGenerator的实现
        
        Returns:
            备选字体路径列表
        """
        # 尝试获取插件内嵌字体路径
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_root = os.path.dirname(current_dir)
            embedded_font_path = os.path.join(plugin_root, "fonts", "chinese_font.ttc")
            
            if os.path.exists(embedded_font_path):
                return [embedded_font_path]
        except Exception as e:
            # print(f"Error loading fallback font: {e}")
            pass
        
        # 系统备选字体 - 优化字体顺序，优先使用更现代的中文字体
        system_fonts = [
            "C:\\Windows\\Fonts\\msyh.ttc",      # 微软雅黑
            "C:\\Windows\\Fonts\\msyhbd.ttc",    # 微软雅黑加粗
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体加粗
            "C:\\Windows\\Fonts\\simsun.ttc",    # 宋体
            "C:\\Windows\\Fonts\\simkai.ttf",    # 楷体
            "C:\\Windows\\Fonts\\simfang.ttf",   # 仿宋
            "C:\\Windows\\Fonts\\arial.ttf",     # Arial
            "C:\\Windows\\Fonts\\calibri.ttf",  # Calibri
            "C:\\Windows\\Fonts\\verdana.ttf",  # Verdana
            "C:\\Windows\\Fonts\\tahoma.ttf",   # Tahoma
            "/System/Library/Fonts/PingFang.ttc",      # macOS
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Medium.ttc", # macOS
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        ]
        
        # 过滤存在的字体
        existing_fonts = []
        for font_path in system_fonts:
            if os.path.exists(font_path):
                existing_fonts.append(font_path)
        
        return existing_fonts
    
    def _setup_bold_font(self):
        """
        设置加粗字体，参考OptimizedFlowchartGenerator的实现
        """
        # 尝试获取插件内嵌加粗字体路径
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取插件根目录
            plugin_root = os.path.dirname(current_dir)
            # 构建内嵌加粗字体路径 - 使用绝对路径
            embedded_bold_font_path = os.path.join(plugin_root, "fonts", "chinese_font_bold.ttc")
            
            # 检查内嵌加粗字体是否存在
            if os.path.exists(embedded_bold_font_path):
                self.bold_font_path = embedded_bold_font_path
                # print(f"Using embedded bold font: {embedded_bold_font_path}")
                return
            else:
                # print(f"Embedded bold font not found at: {embedded_bold_font_path}")
                pass
        except Exception as e:
            # print(f"Error loading embedded bold font: {e}")
            pass
        
        # 如果内嵌加粗字体不存在，尝试使用原始字体的加粗版本
        if self.font_path and os.path.exists(self.font_path):
            try:
                # 尝试使用字体的加粗版本
                font = ImageFont.truetype(self.font_path, 14, index=1)
                self.bold_font_path = self.font_path
                # print(f"Using bold variant of main font: {self.font_path}")
                return
            except Exception as e:
                # print(f"Error using bold font variant: {e}")
                pass
        
        # 如果都不存在，尝试系统加粗字体
        # 优化字体顺序，优先使用更现代的中文字体
        system_fonts = [
            "C:\\Windows\\Fonts\\msyhbd.ttc",    # 微软雅黑加粗
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体（本身就是加粗的）
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体加粗
            "C:\\Windows\\Fonts\\simsun.ttc",    # 宋体
            "C:\\Windows\\Fonts\\simkai.ttf",    # 楷体
            "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold
            "C:\\Windows\\Fonts\\arial.ttf",     # Arial（尝试使用index=1）
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Medium.ttc", # macOS
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",  # Linux
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                self.bold_font_path = font_path
                # print(f"Using system bold font: {font_path}")
                return
        
        # 如果都不存在，返回空字符串
        # print("No suitable bold font found, will use default font")
        self.bold_font_path = ""
    
    def _get_fallback_bold_fonts(self) -> List[str]:
        """
        获取备选加粗字体列表，用于字体加载失败时的备选方案
        参考OptimizedFlowchartGenerator的实现
        
        Returns:
            备选加粗字体路径列表
        """
        # 尝试获取插件内嵌加粗字体路径
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_root = os.path.dirname(current_dir)
            embedded_bold_font_path = os.path.join(plugin_root, "fonts", "chinese_font_bold.ttc")
            
            if os.path.exists(embedded_bold_font_path):
                return [embedded_bold_font_path]
        except Exception as e:
            # print(f"Error loading fallback bold font: {e}")
            pass
        
        # 如果内嵌加粗字体不存在，尝试使用原始字体的加粗版本
        if self.font_path and os.path.exists(self.font_path):
            return [self.font_path]  # 返回原始字体路径，使用index=1加载加粗版本
        
        # 系统备选加粗字体
        # 优化字体顺序，优先使用更现代的中文字体
        # 包含Windows、macOS和Linux的常用加粗字体
        system_bold_fonts = [
            # Windows 加粗字体
            "C:\\Windows\\Fonts\\msyhbd.ttc",    # 微软雅黑加粗
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体（本身就是加粗的）
            "C:\\Windows\\Fonts\\simhei.ttf",    # 黑体加粗
            "C:\\Windows\\Fonts\\simsunb.ttf",   # 宋体加粗
            "C:\\Windows\\Fonts\\simkai.ttf",    # 楷体
            "C:\\Windows\\Fonts\\simfang.ttf",   # 仿宋
            "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold
            "C:\\Windows\\Fonts\\arial.ttf",     # Arial（尝试使用index=1）
            "C:\\Windows\\Fonts\\calibrib.ttf",  # Calibri Bold
            "C:\\Windows\\Fonts\\calibri.ttf",   # Calibri（尝试使用index=1）
            "C:\\Windows\\Fonts\\timesbd.ttf",   # Times New Roman Bold
            "C:\\Windows\\Fonts\\times.ttf",     # Times New Roman（尝试使用index=1）
            
            # macOS 加粗字体
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Medium.ttc", # macOS
            "/System/Library/Fonts/PingFang.ttc",      # macOS
            
            # Linux 加粗字体
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
        ]
        
        # 过滤掉不存在的字体
        existing_fonts = [font for font in system_bold_fonts if os.path.exists(font)]
        
        # 如果没有找到任何字体，返回默认字体
        if not existing_fonts:
            # print("No fallback bold fonts found, using default font")
            return ["arial.ttf"]  # 默认字体
        
        return existing_fonts
    
    def _get_node_fill_color(self, node_type: str, node_shape: str = "rectangle") -> str:
        """
        根据节点类型和形状获取填充颜色（遵循规范的浅色系）
        """
        # 归一化输入
        node_type = (node_type or "").strip().lower()
        node_shape = (node_shape or "rectangle").strip().lower()

        # 类型到颜色的映射（优先使用类内 colors 配置）
        type_to_color = {
            'start': self.colors.get('start_node', '#E6FFE6'),
            'end': self.colors.get('end_node', '#F0F0F0'),
            'decision': self.colors.get('decision_node', '#FFFFCC'),
            'process': self.colors.get('process_node', '#F0F8FF'),
            'operation': self.colors.get('process_node', '#F0F8FF'),
            'data': self.colors.get('data_node', '#E0FFFF'),
            'input': self.colors.get('data_node', '#E0FFFF'),
            'output': self.colors.get('data_node', '#E0FFFF'),
            'subroutine': self.colors.get('subroutine_node', '#F5F5DC'),
        }

        # 当未提供类型时，尝试基于形状推断
        if not node_type:
            if node_shape == 'diamond':
                node_type = 'decision'
            elif node_shape in ('parallelogram',):
                node_type = 'data'
            elif node_shape == 'circle':
                return self.colors.get('circle_node', self.colors.get('process_node', '#F0F8FF'))
            else:
                node_type = 'process'

        # 形状优先级覆盖（如菱形、圆形有专属颜色）
        if node_shape == 'diamond':
            return self.colors.get('diamond_node', type_to_color.get('decision', '#FFFFCC'))
        if node_shape == 'circle':
            return self.colors.get('circle_node', type_to_color.get(node_type, self.colors.get('node_fill', '#F0F8FF')))

        # 其余情况按节点类型返回
        if node_type in type_to_color:
            return type_to_color[node_type]

        # 兜底颜色
        return self.colors.get('node_fill', '#F0F8FF')
    
    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """
        调整颜色的亮度
        
        Args:
            hex_color: 十六进制颜色值
            factor: 亮度因子（>1变亮，<1变暗）
            
        Returns:
            调整后的十六进制颜色值
        """
        # 将十六进制颜色转换为RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 调整亮度
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        # 转换回十六进制
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _estimate_description_height(self, description: str) -> int:
        """
        估算描述文本所需的高度
        
        Args:
            description: 描述文本
            
        Returns:
            估算的高度（像素）
        """
        if not description:
            return 0
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
        except:
            try:
                # 尝试备选字体
                for font_path in self.fallback_fonts:
                    try:
                        font = ImageFont.truetype(font_path, self.font_size)
                        break
                    except:
                        continue
                else:
                    # 如果所有字体都失败，使用默认字体
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # 计算文本尺寸
        try:
            # 获取绘制边界
            bbox = font.getbbox(description)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 如果无法获取边界，使用估算值
            char_count = len(description)
            text_width = char_count * self.font_size * 0.6  # 估算字符宽度
            text_height = self.font_size * 1.2  # 估算字符高度
        
        # 估算最大行宽（画布宽度减去边距）
        max_line_width = 800 - 100  # 假设画布宽度为800，边距为50*2
        
        # 计算需要的行数
        if text_width <= max_line_width:
            lines = 1
        else:
            lines = math.ceil(text_width / max_line_width)
        
        # 计算总高度（行数 * 行高 + 行间距）
        line_height = text_height
        total_height = lines * line_height + (lines - 1) * 5  # 行间距为5像素
        
        return int(total_height)
    
    def _draw_description(self, draw: ImageDraw.ImageDraw, description: str, 
                         x: int, y: int, max_width: int):
        """
        在画布左上方绘制描述文本
        
        Args:
            draw: ImageDraw对象
            description: 描述文本
            x: 起始x坐标
            y: 起始y坐标
            max_width: 文本最大宽度
        """
        if not description:
            return
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
        except:
            try:
                # 尝试备选字体
                for font_path in self.fallback_fonts:
                    try:
                        font = ImageFont.truetype(font_path, self.font_size)
                        break
                    except:
                        continue
                else:
                    # 如果所有字体都失败，使用默认字体
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # 文本换行处理
        words = description.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            try:
                # 获取文本宽度
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
            except:
                # 如果无法获取宽度，使用估算值
                text_width = len(test_line) * self.font_size * 0.6
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # 单个词太长，强制换行
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        # 绘制每一行文本
        line_height = self.font_size * 1.2
        y_offset = y
        
        for line in lines:
            # 绘制文本
            draw.text((x, y_offset), line, fill=self.colors['text'], font=font)
            y_offset += line_height + 5  # 行间距为5像素
    
    def _adjust_color_hue(self, hex_color: str, hue_shift: int) -> str:
        """
        调整颜色的色调
        
        Args:
            hex_color: 十六进制颜色值
            hue_shift: 色调偏移量（0-360度）
            
        Returns:
            调整后的十六进制颜色值
        """
        # 将十六进制颜色转换为RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 转换为HSV
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        cmax = max(r_norm, g_norm, b_norm)
        cmin = min(r_norm, g_norm, b_norm)
        delta = cmax - cmin
        
        # 计算色调
        if delta == 0:
            h = 0
        elif cmax == r_norm:
            h = 60 * (((g_norm - b_norm) / delta) % 6)
        elif cmax == g_norm:
            h = 60 * (((b_norm - r_norm) / delta) + 2)
        else:
            h = 60 * (((r_norm - g_norm) / delta) + 4)
        
        # 调整色调
        h = (h + hue_shift) % 360
        
        # 转换回RGB
        c = cmax
        x = c * (1 - abs(((h / 60) % 2) - 1))
        m = cmin
        
        if 0 <= h < 60:
            r_norm, g_norm, b_norm = c, x, 0
        elif 60 <= h < 120:
            r_norm, g_norm, b_norm = x, c, 0
        elif 120 <= h < 180:
            r_norm, g_norm, b_norm = 0, c, x
        elif 180 <= h < 240:
            r_norm, g_norm, b_norm = 0, x, c
        elif 240 <= h < 300:
            r_norm, g_norm, b_norm = x, 0, c
        else:
            r_norm, g_norm, b_norm = c, 0, x
        
        r = min(255, max(0, int((r_norm + m) * 255)))
        g = min(255, max(0, int((g_norm + m) * 255)))
        b = min(255, max(0, int((b_norm + m) * 255)))
        
        # 转换回十六进制
        return f"#{r:02x}{g:02x}{b:02x}"