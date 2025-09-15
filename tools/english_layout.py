# -*- coding: utf-8 -*-
"""
English Text Layout Generator
英文文本专用布局生成器

Specialized layout algorithms optimized for English text rendering.
专门为英文文本渲染优化的布局算法。
"""

import os
import re
import datetime
from typing import Any, Dict, List, Tuple, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import matplotlib.patheffects as PathEffects
import matplotlib.font_manager as fm
import numpy as np


class EnglishFlowchartGenerator:
    """
    English-optimized Flowchart Generator
    英文优化的流程图生成器
    
    This class provides layout algorithms specifically designed for English text,
    accounting for different character widths, word spacing, and text flow patterns.
    """
    
    def __init__(self):
        """Initialize the English layout generator"""
        # English-optimized node dimensions / 英文优化的节点尺寸
        self.node_width = 3.2   # 为英文文本提供更宽的节点
        self.node_height = 1.2  # 适当增加高度以适应可能的换行
        
        # English-specific spacing for better readability / 英文专用间距以提高可读性
        self.horizontal_spacing = 3.8  # 增加水平间距防止长文本重叠
        self.vertical_spacing = 2.2    # 增加垂直间距确保清晰度
        
        # Optimized margins for English layouts / 英文布局的优化边距
        self.margin_x = 1.2  # 更大的水平边距
        self.margin_y = 1.0  # 更大的垂直边距
        
        # English text characteristics / 英文文本特征
        self.avg_char_width = 0.12  # 英文字符平均宽度（相对于节点）
        self.space_width = 0.08     # 空格宽度
        self.word_break_threshold = 25  # 单词换行阈值
        
        # Branch-aware spacing factors / 分支感知间距因子
        self.branch_spacing_multiplier = 2.8  # 分支场景间距倍数
        self.complex_branch_multiplier = 3.2  # 复杂分支间距倍数
        
        # Setup output directory / 设置输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test', 'demo_output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup font / 设置字体
        self.font = self._setup_font()
        
        # Theme support / 主题支持
        self.current_theme = 'modern'
        self.themes = self._initialize_themes()
    
    def _setup_font(self):
        """Setup font for English text rendering"""
        try:
            # Use system default English fonts
            english_fonts = [
                'Arial', 'Helvetica', 'Calibri', 'Segoe UI', 
                'Times New Roman', 'Georgia', 'DejaVu Sans'
            ]
            
            for font_name in english_fonts:
                try:
                    prop = fm.FontProperties(family=font_name)
                    return prop
                except:
                    continue
            
            return fm.FontProperties()
            
        except Exception as e:
            print(f"Warning: Could not setup English font: {e}")
            return fm.FontProperties()
    
    def _initialize_themes(self):
        """Initialize themes optimized for English text"""
        return {
            'modern': {
                'background': '#FFFFFF',
                'node_colors': {
                    'start': '#4CAF50',
                    'process': '#2196F3',
                    'decision': '#FF9800',
                    'end': '#F44336',
                    'default': '#9C27B0'
                },
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'connection_color': '#424242',
                'connection_width': 2.0
            }
        }
    
    def analyze_english_text(self, nodes: List[Dict]) -> Dict[str, Any]:
        """
        Analyze English text characteristics for optimal layout
        分析英文文本特征以优化布局
        """
        total_chars = 0
        total_words = 0
        max_word_length = 0
        long_text_nodes = 0
        
        for node in nodes:
            label = node.get('label', '')
            words = label.split()
            total_words += len(words)
            total_chars += len(label)
            
            if words:
                max_word_length = max(max_word_length, max(len(word) for word in words))
            
            # 检测长文本节点
            if len(label) > self.word_break_threshold:
                long_text_nodes += 1
        
        avg_chars_per_node = total_chars / len(nodes) if nodes else 0
        avg_words_per_node = total_words / len(nodes) if nodes else 0
        
        return {
            'avg_chars_per_node': avg_chars_per_node,
            'avg_words_per_node': avg_words_per_node,
            'max_word_length': max_word_length,
            'long_text_nodes': long_text_nodes,
            'has_long_text': long_text_nodes > 0,
            'text_complexity': self._determine_text_complexity(avg_chars_per_node, max_word_length)
        }
    
    def _determine_text_complexity(self, avg_chars: float, max_word: int) -> str:
        """Determine text complexity level"""
        if avg_chars <= 15 and max_word <= 8:
            return "simple"
        elif avg_chars <= 30 and max_word <= 15:
            return "medium"
        else:
            return "complex"
    
    def calculate_english_node_size(self, label: str) -> Tuple[float, float]:
        """
        Calculate optimal node size for English text
        为英文文本计算最佳节点尺寸
        """
        words = label.split()
        char_count = len(label)
        
        # 估算文本宽度（考虑字符宽度差异）
        estimated_width = char_count * self.avg_char_width + len(words) * self.space_width
        
        # 基础节点尺寸
        base_width = self.node_width
        base_height = self.node_height
        
        # 根据文本长度动态调整
        if char_count > 40:
            # 超长文本：显著增加宽度，可能需要换行
            width = base_width * 1.5
            height = base_height * 1.3  # 为换行预留空间
        elif char_count > 25:
            # 长文本：适度增加宽度
            width = base_width * 1.3
            height = base_height * 1.1
        elif char_count > 15:
            # 中等文本：小幅增加宽度
            width = base_width * 1.15
            height = base_height
        else:
            # 短文本：使用标准尺寸
            width = base_width
            height = base_height
        
        return width, height
    
    def calculate_english_grid_layout(self, nodes: List[Dict], layout: str) -> Tuple[int, int]:
        """
        Calculate optimal grid layout for English text nodes
        为英文文本节点计算最佳网格布局
        """
        node_count = len(nodes)
        if node_count == 0:
            return 1, 1
        
        text_analysis = self.analyze_english_text(nodes)
        
        # 根据文本复杂度调整网格策略
        if text_analysis["text_complexity"] == "complex":
            # 复杂文本：减少每行/列的节点数量
            max_per_line = 3
        elif text_analysis["text_complexity"] == "medium":
            # 中等文本：适中的节点数量
            max_per_line = 4
        else:
            # 简单文本：可以排列更多节点
            max_per_line = 5
        
        if layout == "left-right":
            # 水平布局：限制每行节点数
            if node_count <= max_per_line:
                cols = node_count
                rows = 1
            else:
                cols = max_per_line
                rows = (node_count + cols - 1) // cols
        else:  # top-bottom
            # 垂直布局：限制每列节点数
            if node_count <= max_per_line:
                rows = node_count
                cols = 1
            else:
                rows = max_per_line
                cols = (node_count + rows - 1) // rows
        
        return rows, cols
    
    def calculate_english_canvas_size(self, nodes: List[Dict], layout: str, rows: int, cols: int) -> Tuple[float, float]:
        """
        Calculate canvas size optimized for English text
        为英文文本优化画布尺寸计算
        """
        text_analysis = self.analyze_english_text(nodes)
        
        # 计算实际需要的节点尺寸
        max_node_width = 0
        max_node_height = 0
        
        for node in nodes:
            width, height = self.calculate_english_node_size(node.get('label', ''))
            max_node_width = max(max_node_width, width)
            max_node_height = max(max_node_height, height)
        
        # 使用实际最大节点尺寸计算画布
        effective_h_spacing = self.horizontal_spacing
        effective_v_spacing = self.vertical_spacing
        
        # 根据文本复杂度调整间距
        if text_analysis["text_complexity"] == "complex":
            effective_h_spacing *= 1.3
            effective_v_spacing *= 1.2
        elif text_analysis["has_long_text"]:
            effective_h_spacing *= 1.2
            effective_v_spacing *= 1.1
        
        # 计算总画布尺寸
        total_width = cols * max_node_width + (cols - 1) * effective_h_spacing
        total_height = rows * max_node_height + (rows - 1) * effective_v_spacing
        
        canvas_width = total_width + 2 * self.margin_x
        canvas_height = total_height + 2 * self.margin_y
        
        # 设置合理的最小和最大尺寸
        canvas_width = max(12, min(canvas_width, 100))  # 最小12，最大100
        canvas_height = max(8, min(canvas_height, 80))   # 最小8，最大80
        
        return canvas_width, canvas_height
    
    def calculate_english_positions(self, nodes: List[Dict], layout: str, canvas_width: float, canvas_height: float, rows: int, cols: int) -> Dict[str, Tuple[float, float]]:
        """
        Calculate precise positions for English text nodes
        为英文文本节点计算精确位置
        """
        positions = {}
        text_analysis = self.analyze_english_text(nodes)
        
        # 计算可用空间
        available_width = canvas_width - 2 * self.margin_x
        available_height = canvas_height - 2 * self.margin_y
        
        # 动态间距计算
        if cols > 1:
            x_spacing = available_width / cols
        else:
            x_spacing = available_width
            
        if rows > 1:
            y_spacing = available_height / rows
        else:
            y_spacing = available_height
        
        # 确保最小间距（防止重叠）
        min_x_spacing = self.node_width + 1.0  # 更大的最小间距
        min_y_spacing = self.node_height + 0.8
        x_spacing = max(x_spacing, min_x_spacing)
        y_spacing = max(y_spacing, min_y_spacing)
        
        # 计算节点位置
        for i, node in enumerate(nodes):
            if layout == "left-right":
                row = i // cols
                col = i % cols
            else:  # top-bottom
                col = i // rows
                row = i % rows
            
            # 计算基础位置
            x = self.margin_x + x_spacing * (col + 0.5)
            y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
            
            # 边界检查和调整
            node_width, node_height = self.calculate_english_node_size(node.get('label', ''))
            
            # 确保节点完全在画布内
            x = max(self.margin_x + node_width/2, min(canvas_width - self.margin_x - node_width/2, x))
            y = max(self.margin_y + node_height/2, min(canvas_height - self.margin_y - node_height/2, y))
            
            positions[node['id']] = (x, y)
        
        return positions
    
    def generate_english_flowchart(self, nodes: List[Dict], connections: List[Dict], layout: str, input_type: str) -> str:
        """
        Generate flowchart optimized for English text with branch-aware layout
        生成针对英文文本优化的流程图，支持分支感知布局
        """
        if not nodes:
            raise ValueError("No nodes to generate flowchart")
        
        # 分析文本特征和结构
        text_analysis = self.analyze_english_text(nodes)
        
        # 借用主生成器的结构分析方法
        from .optimized_layout import OptimizedFlowchartGenerator
        temp_generator = OptimizedFlowchartGenerator()
        structure_analysis = temp_generator._analyze_flowchart_structure(nodes, connections)
        
        # 根据分支结构选择布局算法
        if structure_analysis['has_branches']:
            # 有分支：使用自由布局
            canvas_width, canvas_height = self._calculate_branch_canvas_size(nodes, connections, layout)
            positions = self._calculate_english_free_positions(nodes, connections, layout, canvas_width, canvas_height)
        else:
            # 无分支：使用网格布局
            rows, cols = self.calculate_english_grid_layout(nodes, layout)
            canvas_width, canvas_height = self.calculate_english_canvas_size(nodes, layout, rows, cols)
            positions = self.calculate_english_positions(nodes, layout, canvas_width, canvas_height, rows, cols)
        
        # 创建图形
        theme = self.themes[self.current_theme]
        fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
        fig.patch.set_facecolor(theme['background'])
        ax.set_xlim(0, canvas_width)
        ax.set_ylim(0, canvas_height)
        ax.axis('off')
        ax.set_facecolor(theme['background'])
        
        # 绘制节点
        for node in nodes:
            self._draw_english_node(ax, node, positions[node['id']], theme)
        
        # 绘制连接
        for connection in connections:
            self._draw_english_connection(ax, connection, positions, theme)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        layout_suffix = "lr" if layout == "left-right" else "tb"
        filename = f"english_flowchart_{input_type}_{layout_suffix}_{timestamp}.png"
        file_path = os.path.join(self.output_dir, filename)
        
        # 保存文件
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight', 
                   facecolor=theme['background'], edgecolor='none', pad_inches=0.1)
        plt.close(fig)
        
        return file_path
    
    def _draw_english_node(self, ax, node: Dict, position: Tuple[float, float], theme: Dict):
        """Draw a node optimized for English text"""
        x, y = position
        label = node.get('label', '')
        node_type = node.get('type', 'default')
        
        # 获取节点尺寸
        width, height = self.calculate_english_node_size(label)
        
        # 获取颜色
        color = theme['node_colors'].get(node_type, theme['node_colors']['default'])
        text_color = theme['text_color']
        
        # 绘制节点形状
        if node_type == 'decision':
            # 菱形
            diamond_points = [
                [x, y + height/2], [x + width/2, y],
                [x, y - height/2], [x - width/2, y]
            ]
            from matplotlib.patches import Polygon
            patch = Polygon(diamond_points, facecolor=color, edgecolor='white', linewidth=2)
        else:
            # 矩形或圆角矩形
            style = "round,pad=0.1" if node_type in ['start', 'end'] else "round,pad=0.02"
            patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                 boxstyle=style, facecolor=color, edgecolor='white', linewidth=2)
        
        ax.add_patch(patch)
        
        # 绘制文本
        self._draw_english_text(ax, x, y, label, text_color, width)
    
    def _draw_english_text(self, ax, x: float, y: float, text: str, color: str, node_width: float):
        """Draw English text with optimal formatting"""
        if not text:
            return
        
        # 计算字体大小
        char_count = len(text)
        if char_count <= 10:
            font_size = 10
        elif char_count <= 20:
            font_size = 9
        elif char_count <= 30:
            font_size = 8
        else:
            font_size = 7
        
        # 文本换行处理
        formatted_text = self._format_english_text(text, node_width)
        
        # 绘制文本
        ax.text(x, y, formatted_text, ha='center', va='center', 
               fontsize=font_size, weight='bold',
               fontproperties=self.font, color=color, 
               linespacing=0.9, clip_on=False)
    
    def _format_english_text(self, text: str, node_width: float) -> str:
        """Format English text for optimal display"""
        words = text.split()
        if not words:
            return text
        
        # 估算每行可容纳的字符数
        chars_per_line = int(node_width / self.avg_char_width * 0.8)  # 留20%边距
        
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 最多3行
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = lines[-1][:chars_per_line-3] + "..."
        
        return '\n'.join(lines)
    
    def _draw_english_connection(self, ax, connection: Dict, positions: Dict, theme: Dict):
        """Draw connection between English nodes"""
        from_id = connection['from']
        to_id = connection['to']
        
        if from_id not in positions or to_id not in positions:
            return
        
        from_pos = positions[from_id]
        to_pos = positions[to_id]
        
        # 绘制箭头连接
        arrow = ConnectionPatch(from_pos, to_pos, "data", "data",
                              arrowstyle="->", shrinkA=45, shrinkB=45,
                              mutation_scale=20, fc=theme['connection_color'], 
                              ec=theme['connection_color'], linewidth=theme['connection_width'])
        ax.add_patch(arrow)