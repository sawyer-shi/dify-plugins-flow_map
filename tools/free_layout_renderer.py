import os
import time
import math
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont


class FreeLayoutRenderer:
    """
    自由布局渲染器
    独立实现Mermaid流程图的布局和渲染功能
    仅支持流程图类型
    """
    
    def __init__(self):
        """
        初始化自由布局渲染器
        """
        # 定义经典风格的颜色方案 - 更鲜明的颜色对比
        self.colors = {
            'background': '#FFFFFF',  # 纯白背景
            'node_fill': '#F0F8FF',   # 淡蓝色填充
            'node_outline': '#0066CC', # 深蓝色边框
            'text': '#000000',        # 黑色文本
            'arrow': '#0066CC',       # 深蓝色箭头
            'shadow': '#CCCCCC',      # 灰色阴影
            'start_node': '#90EE90',  # 浅绿色
            'end_node': '#FFB6C1',    # 浅红色
            'process_node': '#F0F8FF', # 淡蓝色
            'decision_node': '#FFFFE0', # 浅黄色
            'data_node': '#E6E6FA',   # 淡紫色
        }
        
        # 定义经典风格的线条宽度
        self.line_widths = {
            'node': 3,               # 更粗的节点边框
            'arrow': 3,              # 更粗的箭头
            'text': 1
        }
    
    def render_mermaid(self, chart_type: str, elements: List[Dict[str, Any]], 
                      positions: Dict[str, Tuple[int, int]], is_chinese: bool) -> str:
        """
        渲染Mermaid流程图并返回文件路径
        仅支持流程图类型
        
        Args:
            chart_type: 图表类型（仅支持flowchart）
            elements: 图表元素列表
            positions: 节点位置字典
            is_chinese: 是否为中文
            
        Returns:
            生成的图像文件路径
        """
        # 仅支持流程图渲染
        return self._render_flowchart(elements, positions, is_chinese)
    
    def _render_flowchart(self, elements: List[Dict[str, Any]], 
                         positions: Dict[str, Tuple[int, int]], is_chinese: bool) -> str:
        """
        渲染流程图
        
        Args:
            elements: 图表元素列表
            positions: 节点位置字典
            is_chinese: 是否为中文
            
        Returns:
            生成的图像文件路径
        """
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "test", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = int(time.time())
        layout_type = "chinese" if is_chinese else "english"
        filename = f"free_layout_mermaid_flowchart_{layout_type}_{timestamp}.png"
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
        image = Image.new('RGB', (canvas_width, canvas_height), self.colors['background'])
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
    
    def _draw_node(self, draw: ImageDraw.ImageDraw, node: Dict[str, Any], 
                  pos: Tuple[int, int], font):
        """绘制节点"""
        # 获取节点属性
        node_id = node.get("id", "")
        text = node.get("label", node_id)  # 修复：使用label字段而不是text字段
        shape = node.get("shape", "rectangle")
        node_type = node.get("node_type", "")
        
        # 获取节点大小
        width = 120
        height = 60
        
        # 根据节点形状绘制
        if shape == "stadium":
            self._draw_stadium_node(draw, pos, width, height, node_type)
        elif shape == "circle":
            self._draw_circle_node(draw, pos, width, height, node_type)
        elif shape == "diamond":
            self._draw_diamond_node(draw, pos, width, height, node_type)
        elif shape == "hexagon":
            self._draw_hexagon_node(draw, pos, width, height, node_type)
        elif shape == "parallelogram":
            self._draw_parallelogram_node(draw, pos, width, height, False, node_type)
        elif shape == "parallelogram_alt":
            self._draw_parallelogram_node(draw, pos, width, height, True, node_type)
        elif shape == "subroutine":
            self._draw_subroutine_node(draw, pos, width, height, node_type)
        elif shape == "cylinder":
            self._draw_cylinder_node(draw, pos, width, height, node_type)
        else:
            # 默认为矩形
            self._draw_rectangle_node(draw, pos, width, height, node_type)
        
        # 绘制文本
        self._draw_node_text(draw, pos, text, font)
    
    def _draw_rectangle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                            width: int, height: int, node_type=""):
        """绘制矩形节点"""
        x1 = pos[0] - width // 2
        y1 = pos[1] - height // 2
        x2 = pos[0] + width // 2
        y2 = pos[1] + height // 2
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制矩形
        # 绘制阴影
        shadow_offset = 4
        draw.rectangle([x1 + shadow_offset, y1 + shadow_offset, 
                      x2 + shadow_offset, y2 + shadow_offset], 
                     fill=self.colors['shadow'])
        
        # 绘制主体矩形
        draw.rectangle([x1, y1, x2, y2], 
                     outline=self.colors['node_outline'], 
                     fill=fill_color, 
                     width=self.line_widths['node'])
    
    def _draw_stadium_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int, node_type=""):
        """绘制体育场形节点"""
        radius = height // 2
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制体育场形节点
        # 绘制阴影
        shadow_offset = 4
        draw.rectangle(
            [pos[0] - width // 2 + radius + shadow_offset, pos[1] - height // 2 + shadow_offset,
             pos[0] + width // 2 - radius + shadow_offset, pos[1] + height // 2 + shadow_offset],
            fill=self.colors['shadow']
        )
        draw.ellipse(
            [pos[0] - width // 2 + shadow_offset, pos[1] - height // 2 + shadow_offset,
             pos[0] - width // 2 + height + shadow_offset, pos[1] + height // 2 + shadow_offset],
            fill=self.colors['shadow']
        )
        draw.ellipse(
            [pos[0] + width // 2 - height + shadow_offset, pos[1] - height // 2 + shadow_offset,
             pos[0] + width // 2 + shadow_offset, pos[1] + height // 2 + shadow_offset],
            fill=self.colors['shadow']
        )
        
        # 绘制主体
        draw.rectangle(
            [pos[0] - width // 2 + radius, pos[1] - height // 2,
             pos[0] + width // 2 - radius, pos[1] + height // 2],
            outline=self.colors['node_outline'], fill=fill_color, width=self.line_widths['node']
        )
        draw.ellipse(
            [pos[0] - width // 2, pos[1] - height // 2,
             pos[0] - width // 2 + height, pos[1] + height // 2],
            outline=self.colors['node_outline'], fill=fill_color, width=self.line_widths['node']
        )
        draw.ellipse(
            [pos[0] + width // 2 - height, pos[1] - height // 2,
             pos[0] + width // 2, pos[1] + height // 2],
            outline=self.colors['node_outline'], fill=fill_color, width=self.line_widths['node']
        )
    
    def _draw_circle_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                         width: int, height: int, node_type=""):
        """绘制圆形节点"""
        radius = min(width, height) // 2
        x1 = pos[0] - radius
        y1 = pos[1] - radius
        x2 = pos[0] + radius
        y2 = pos[1] + radius
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制圆形
        # 绘制阴影
        shadow_offset = 4
        draw.ellipse([x1 + shadow_offset, y1 + shadow_offset, 
                     x2 + shadow_offset, y2 + shadow_offset], 
                    fill=self.colors['shadow'])
        
        # 绘制圆形主体
        draw.ellipse([x1, y1, x2, y2], 
                    outline=self.colors['node_outline'], 
                    fill=fill_color, 
                    width=self.line_widths['node'])
    
    def _draw_diamond_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int, node_type=""):
        """绘制菱形节点"""
        half_width = width // 2
        half_height = height // 2
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制菱形
        # 绘制阴影
        shadow_offset = 4
        shadow_points = [
            (pos[0] + shadow_offset, pos[1] - half_height + shadow_offset),  # 上
            (pos[0] + half_width + shadow_offset, pos[1] + shadow_offset),    # 右
            (pos[0] + shadow_offset, pos[1] + half_height + shadow_offset),  # 下
            (pos[0] - half_width + shadow_offset, pos[1] + shadow_offset)     # 左
        ]
        draw.polygon(shadow_points, fill=self.colors['shadow'])
        
        # 绘制主体
        points = [
            (pos[0], pos[1] - half_height),      # 上
            (pos[0] + half_width, pos[1]),       # 右
            (pos[0], pos[1] + half_height),      # 下
            (pos[0] - half_width, pos[1])        # 左
        ]
        draw.polygon(points, outline=self.colors['node_outline'], 
                    fill=fill_color, width=self.line_widths['node'])
    
    def _draw_hexagon_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                          width: int, height: int, node_type=""):
        """绘制六边形节点"""
        half_width = width // 2
        half_height = height // 2
        offset = width // 6
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制六边形
        # 绘制阴影
        shadow_offset = 4
        shadow_points = [
            (pos[0] - offset + shadow_offset, pos[1] - half_height + shadow_offset),  # 左上
            (pos[0] + offset + shadow_offset, pos[1] - half_height + shadow_offset),  # 右上
            (pos[0] + half_width + shadow_offset, pos[1] + shadow_offset),            # 右
            (pos[0] + offset + shadow_offset, pos[1] + half_height + shadow_offset),  # 右下
            (pos[0] - offset + shadow_offset, pos[1] + half_height + shadow_offset),  # 左下
            (pos[0] - half_width + shadow_offset, pos[1] + shadow_offset)             # 左
        ]
        draw.polygon(shadow_points, fill=self.colors['shadow'])
        
        # 绘制主体
        points = [
            (pos[0] - offset, pos[1] - half_height),  # 左上
            (pos[0] + offset, pos[1] - half_height),  # 右上
            (pos[0] + half_width, pos[1]),            # 右
            (pos[0] + offset, pos[1] + half_height),  # 右下
            (pos[0] - offset, pos[1] + half_height),  # 左下
            (pos[0] - half_width, pos[1])             # 左
        ]
        draw.polygon(points, outline=self.colors['node_outline'], 
                    fill=fill_color, width=self.line_widths['node'])
    
    def _draw_parallelogram_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                                width: int, height: int, reverse: bool, node_type=""):
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
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制平行四边形
        # 绘制阴影
        shadow_offset = 4
        shadow_points = [(p[0] + shadow_offset, p[1] + shadow_offset) for p in points]
        draw.polygon(shadow_points, fill=self.colors['shadow'])
        
        # 绘制主体
        draw.polygon(points, outline=self.colors['node_outline'], 
                    fill=fill_color, width=self.line_widths['node'])
    
    def _draw_subroutine_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                             width: int, height: int, node_type=""):
        """绘制子程序节点"""
        x1 = pos[0] - width // 2
        y1 = pos[1] - height // 2
        x2 = pos[0] + width // 2
        y2 = pos[1] + height // 2
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制子程序节点
        # 绘制阴影
        shadow_offset = 4
        draw.rectangle([x1 + shadow_offset, y1 + shadow_offset, 
                      x2 + shadow_offset, y2 + shadow_offset], 
                     fill=self.colors['shadow'])
        
        # 绘制主体矩形
        draw.rectangle([x1, y1, x2, y2], 
                     outline=self.colors['node_outline'], 
                     fill=fill_color, 
                     width=self.line_widths['node'])
        
        # 绘制额外的边框线
        draw.line([x1 + 10, y1, x1 + 10, y2], 
                 fill=self.colors['node_outline'], 
                 width=self.line_widths['node'])
        draw.line([x2 - 10, y1, x2 - 10, y2], 
                 fill=self.colors['node_outline'], 
                 width=self.line_widths['node'])
    
    def _draw_cylinder_node(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], 
                           width: int, height: int, node_type=""):
        """绘制圆柱形节点"""
        x1 = pos[0] - width // 2
        x2 = pos[0] + width // 2
        y1 = pos[1] - height // 2
        y2 = pos[1] + height // 2
        ellipse_height = height // 4
        
        # 获取节点填充颜色
        fill_color = self._get_node_fill_color(node_type)
        
        # 使用经典风格绘制圆柱形节点
        # 绘制阴影
        shadow_offset = 4
        draw.rectangle([x1 + shadow_offset, y1 + ellipse_height + shadow_offset, 
                      x2 + shadow_offset, y2 + shadow_offset], 
                     fill=self.colors['shadow'])
        draw.ellipse([x1 + shadow_offset, y1 + shadow_offset, 
                     x2 + shadow_offset, y1 + ellipse_height * 2 + shadow_offset], 
                    fill=self.colors['shadow'])
        draw.ellipse([x1 + shadow_offset, y2 - ellipse_height * 2 + shadow_offset, 
                     x2 + shadow_offset, y2 + shadow_offset], 
                    fill=self.colors['shadow'])
        
        # 绘制主体矩形
        draw.rectangle([x1, y1 + ellipse_height, x2, y2], 
                     outline=self.colors['node_outline'], 
                     fill=fill_color, 
                     width=self.line_widths['node'])
        
        # 绘制顶部椭圆
        draw.ellipse([x1, y1, x2, y1 + ellipse_height * 2], 
                    outline=self.colors['node_outline'], 
                    fill=fill_color, 
                    width=self.line_widths['node'])
        
        # 绘制底部椭圆
        draw.ellipse([x1, y2 - ellipse_height * 2, x2, y2], 
                    outline=self.colors['node_outline'], 
                    fill=fill_color, 
                    width=self.line_widths['node'])
    
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
        
        # 使用经典风格绘制文本
        draw.text((text_x, text_y), text, fill=self.colors['text'], font=font)
    
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
        
        # 使用经典风格绘制箭头
        # 绘制线
        draw.line([from_pos, adjusted_to_pos], fill=self.colors['arrow'], width=self.line_widths['arrow'])
        
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
        draw.polygon([(adjusted_to_x, adjusted_to_y), (x1, y1), (x2, y2)], fill=self.colors['arrow'])
    
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
        
        # 虚线参数
        dash_length = 10  # 虚线段长度
        gap_length = 8    # 间隔长度
        
        # 调整后的距离
        adjusted_distance = distance - node_radius_x
        
        # 使用原始方法绘制虚线
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
            draw.line([(start_x, start_y), (end_x, end_y)], fill=self.colors['arrow'], width=self.line_widths['arrow'])
            
            # 更新距离
            current_distance = end_distance + gap_length
        
        # 绘制箭头
        angle = math.atan2(dy, dx)
        arrow_length = 10
        arrow_angle = math.pi / 6
        
        # 计算箭头两个端点
        x1 = adjusted_to_x - arrow_length * math.cos(angle - arrow_angle)
        y1 = adjusted_to_y - arrow_length * math.sin(angle - arrow_angle)
        x2 = adjusted_to_x - arrow_length * math.cos(angle + arrow_angle)
        y2 = adjusted_to_y - arrow_length * math.sin(angle + arrow_angle)
        
        # 绘制箭头
        draw.polygon([(adjusted_to_x, adjusted_to_y), (x1, y1), (x2, y2)], fill=self.colors['arrow'])
    
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
        
        # 单位向量
        unit_x = dx / distance
        unit_y = dy / distance
        
        # 调整终点位置到节点边缘
        adjusted_to_x = to_pos[0] - unit_x * node_radius_x
        adjusted_to_y = to_pos[1] - unit_y * node_radius_y
        adjusted_to_pos = (adjusted_to_x, adjusted_to_y)
        
        # 使用更粗的线条绘制箭头
        # 绘制线
        draw.line([from_pos, adjusted_to_pos], fill=self.colors['arrow'], width=self.line_widths['arrow'] + 2)
        
        # 计算箭头方向
        angle = math.atan2(dy, dx)
        
        # 箭头长度
        arrow_length = 12
        arrow_angle = math.pi / 6
        
        # 计算箭头两个端点
        x1 = adjusted_to_x - arrow_length * math.cos(angle - arrow_angle)
        y1 = adjusted_to_y - arrow_length * math.sin(angle - arrow_angle)
        x2 = adjusted_to_x - arrow_length * math.cos(angle + arrow_angle)
        y2 = adjusted_to_y - arrow_length * math.sin(angle + arrow_angle)
        
        # 绘制箭头
        draw.polygon([(adjusted_to_x, adjusted_to_y), (x1, y1), (x2, y2)], fill=self.colors['arrow'])
    
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
        # 计算标签位置（在线的中点）
        mid_x = (from_pos[0] + to_pos[0]) // 2
        mid_y = (from_pos[1] + to_pos[1]) // 2
        
        # 计算文本边界框
        if hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        elif hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(label, font=font)
        else:
            # 回退到估算
            text_width = len(label) * 8
            text_height = 14
        
        # 绘制背景矩形
        padding = 4
        bg_x1 = mid_x - text_width // 2 - padding
        bg_y1 = mid_y - text_height // 2 - padding
        bg_x2 = mid_x + text_width // 2 + padding
        bg_y2 = mid_y + text_height // 2 + padding
        
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=self.colors['background'], outline=self.colors['node_outline'])
        
        # 绘制文本
        text_x = mid_x - text_width // 2
        text_y = mid_y - text_height // 2
        draw.text((text_x, text_y), label, fill=self.colors['text'], font=font)
    
    def _get_node_fill_color(self, node_type: str) -> str:
        """
        根据节点类型获取填充颜色
        
        Args:
            node_type: 节点类型
            
        Returns:
            填充颜色
        """
        if node_type == "start":
            return self.colors['start_node']
        elif node_type == "end":
            return self.colors['end_node']
        elif node_type == "operation":
            return self.colors['process_node']
        elif node_type == "decision":
            return self.colors['decision_node']
        elif node_type == "inputoutput":
            return self.colors['data_node']
        else:
            return self.colors['node_fill']