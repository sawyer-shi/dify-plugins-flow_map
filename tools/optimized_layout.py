# -*- coding: utf-8 -*-
"""
Optimized Layout Generator
优化布局生成器

Provides compact layout algorithms for flowcharts to better utilize space.
提供紧凑的流程图布局算法，更好地利用空间。
"""

import os
import io
import base64
import re
import json
import datetime
from typing import Any, Dict, List, Tuple, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import matplotlib.font_manager as fm
import numpy as np
from PIL import Image


class OptimizedFlowchartGenerator:
    """
    Optimized Flowchart Generator with compact layouts
    优化的流程图生成器，支持紧凑布局
    """
    
    def __init__(self):
        """Initialize the generator"""
        # Compact figure size / 紧凑的图形尺寸
        self.fig_size = (10, 6)
        
        # Optimized node dimensions / 优化的节点尺寸
        self.node_width = 1.4
        self.node_height = 0.6
        
        # Intelligent spacing for multi-row/column layouts / 智能间距适配多行多列布局
        self.horizontal_spacing = 2.2  # 节点间水平间距（增加以适应多行）
        self.vertical_spacing = 1.4    # 节点间垂直间距（增加以适应多列）
        
        # Optimized canvas margins / 优化的画布边距
        self.margin_x = 0.6  # 减少水平边距以更好利用空间
        self.margin_y = 0.6  # 减少垂直边距以更好利用空间
        
        # Visual enhancement: Theme system / 视觉增强：主题系统
        self.themes = self._initialize_themes()
        self.current_theme = 'modern'  # Default theme / 默认主题
        
        # Node shapes for different types / 不同类型的节点形状
        self.node_shapes = {
            'start': 'round',      # Rounded rectangle / 圆角矩形
            'process': 'rect',     # Rectangle / 矩形
            'decision': 'diamond', # Diamond / 菱形
            'end': 'round',        # Rounded rectangle / 圆角矩形
            'default': 'rect'      # Rectangle / 矩形
        }
        
        # Setup output directory / 设置输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test', 'demo_output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup Chinese font
        self.chinese_font = self._setup_chinese_font()
        
        # Visual enhancement parameters / 视觉增强参数
        self.shadow_enabled = True      # Enable shadow effects / 启用阴影效果
        self.gradient_enabled = True    # Enable gradient effects / 启用渐变效果
        self.border_width = 1.5         # Border width / 边框宽度
        self.shadow_offset = (0.02, -0.02)  # Shadow offset / 阴影偏移
        
        # Adaptive grid system parameters / 自适应网格系统参数
        self.max_text_length_short = 8   # 短文本阈值
        self.max_text_length_medium = 15  # 中等文本阈值
        self.min_nodes_per_row = 2        # 每行最少节点数
        self.max_nodes_per_row = 6        # 每行最多节点数
        self.min_nodes_per_col = 2        # 每列最少节点数  
        self.max_nodes_per_col = 8        # 每列最多节点数
    
    def _initialize_themes(self):
        """
        Initialize color themes for different visual styles
        初始化不同视觉风格的颜色主题
        """
        return {
            'modern': {
                'name': 'Modern / 现代',
                'background': '#FFFFFF',
                'node_colors': {
                    'start': '#4CAF50',    # Material Green / 质感绿
                    'process': '#2196F3',  # Material Blue / 质感蓝
                    'decision': '#FF9800', # Material Orange / 质感橙
                    'end': '#F44336',      # Material Red / 质感红
                    'default': '#9C27B0'   # Material Purple / 质感紫
                },
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'connection_color': '#424242',
                'connection_width': 2.0
            },
            'business': {
                'name': 'Business / 商务',
                'background': '#F5F5F5',
                'node_colors': {
                    'start': '#1976D2',    # Deep Blue / 深蓝
                    'process': '#0277BD',  # Light Blue / 浅蓝
                    'decision': '#F57C00', # Deep Orange / 深橙
                    'end': '#388E3C',      # Green / 绿色
                    'default': '#5D4037'   # Brown / 棕色
                },
                'text_color': '#FFFFFF',
                'border_color': '#37474F',
                'connection_color': '#37474F',
                'connection_width': 1.8
            },
            'tech': {
                'name': 'Technology / 科技',
                'background': '#121212',
                'node_colors': {
                    'start': '#00E676',    # Bright Green / 亮绿
                    'process': '#00BCD4',  # Cyan / 青色
                    'decision': '#FF6D00', # Deep Orange / 深橙
                    'end': '#E91E63',      # Pink / 粉红
                    'default': '#9C27B0'   # Purple / 紫色
                },
                'text_color': '#FFFFFF',
                'border_color': '#FFFFFF',
                'connection_color': '#FFFFFF',
                'connection_width': 2.2
            },
            'minimal': {
                'name': 'Minimal / 简约',
                'background': '#FAFAFA',
                'node_colors': {
                    'start': '#616161',    # Grey 600
                    'process': '#757575',  # Grey 600
                    'decision': '#9E9E9E', # Grey 500
                    'end': '#424242',      # Grey 800
                    'default': '#6A6A6A'   # Grey
                },
                'text_color': '#FFFFFF',
                'border_color': '#9E9E9E',
                'connection_color': '#616161',
                'connection_width': 1.5
            },
            'classic': {
                'name': 'Classic / 经典',
                'background': '#FFFFFF',
                'node_colors': {
                    'start': '#90EE90',    # Light Green
                    'process': '#87CEEB',  # Sky Blue  
                    'decision': '#FFB6C1', # Light Pink
                    'end': '#FFA07A',      # Light Salmon
                    'default': '#E6E6FA'   # Lavender
                },
                'text_color': '#000000',
                'border_color': '#666666',
                'connection_color': '#333333',
                'connection_width': 1.5
            }
        }
    
    def set_theme(self, theme_name: str):
        """
        Set the current theme for flowchart generation
        设置流程图生成的当前主题
        
        Args:
            theme_name: Theme name ('modern', 'business', 'tech', 'minimal', 'classic')
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
        else:
            print(f"Warning: Theme '{theme_name}' not found, using default 'modern' theme")
            self.current_theme = 'modern'
    
    def get_current_theme(self) -> Dict[str, Any]:
        """
        Get the current theme configuration
        获取当前主题配置
        """
        return self.themes[self.current_theme]
    
    def _setup_chinese_font(self):
        """Setup Chinese font for matplotlib"""
        try:
            # Try local font file first
            font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'chinese_font.ttc')
            if os.path.exists(font_path):
                prop = fm.FontProperties(fname=font_path)
                return prop
            
            # Fallback to system fonts
            chinese_fonts = [
                'SimHei', 'Microsoft YaHei', 'PingFang SC', 
                'Hiragino Sans GB', 'WenQuanYi Micro Hei', 'DejaVu Sans'
            ]
            
            for font_name in chinese_fonts:
                try:
                    prop = fm.FontProperties(family=font_name)
                    return prop
                except:
                    continue
            
            return fm.FontProperties()
            
        except Exception as e:
            print(f"Warning: Could not setup Chinese font: {e}")
            return fm.FontProperties()
    
    def generate_from_markdown(self, text: str, layout: str = "left-right") -> Dict[str, Any]:
        """Generate compact flowchart from Markdown text"""
        try:
            nodes, connections = self._parse_markdown(text)
            
            if not nodes:
                return {
                    "success": False,
                    "error": "No valid nodes found in Markdown text",
                    "message": "Please provide valid Markdown with numbered or bullet lists"
                }
            
            file_path = self._generate_compact_flowchart(nodes, connections, layout, "markdown")
            
            return {
                "success": True,
                "file_path": file_path,
                "nodes_count": len(nodes),
                "connections_count": len(connections),
                "layout": layout,
                "format": "png",
                "input_type": "markdown"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate flowchart from Markdown"
            }
    
    def generate_from_mermaid(self, text: str, layout: str = "top-bottom") -> Dict[str, Any]:
        """Generate compact flowchart from Mermaid syntax"""
        try:
            nodes, connections = self._parse_mermaid(text)
            
            if not nodes:
                return {
                    "success": False,
                    "error": "No valid nodes found in Mermaid syntax",
                    "message": "Please provide valid Mermaid flowchart syntax"
                }
            
            file_path = self._generate_compact_flowchart(nodes, connections, layout, "mermaid")
            
            return {
                "success": True,
                "file_path": file_path,
                "nodes_count": len(nodes),
                "connections_count": len(connections),
                "layout": layout,
                "format": "png",
                "input_type": "mermaid"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate flowchart from Mermaid"
            }
    
    def _parse_markdown(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse Markdown text to extract flow nodes and connections"""
        nodes = []
        connections = []
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        node_id = 0
        prev_node_id = None
        
        for line in lines:
            if line.startswith('#') or not line:
                continue
                
            # Extract numbered list items
            match = re.match(r'^\d+\.\s*(.+)', line)
            if match:
                content = match.group(1)
                node_type = self._determine_node_type(content)
                
                nodes.append({
                    'id': f'node_{node_id}',
                    'label': content,
                    'type': node_type
                })
                
                if prev_node_id is not None:
                    connections.append({
                        'from': f'node_{prev_node_id}',
                        'to': f'node_{node_id}',
                        'label': ''
                    })
                
                prev_node_id = node_id
                node_id += 1
                
            # Handle bullet points
            elif line.startswith(('-', '*', '+')):
                content = line[1:].strip()
                node_type = self._determine_node_type(content)
                
                nodes.append({
                    'id': f'node_{node_id}',
                    'label': content,
                    'type': node_type
                })
                
                if prev_node_id is not None:
                    connections.append({
                        'from': f'node_{prev_node_id}',
                        'to': f'node_{node_id}',
                        'label': ''
                    })
                
                prev_node_id = node_id
                node_id += 1
        
        return nodes, connections
    
    def _parse_mermaid(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse Mermaid syntax to extract flow nodes and connections"""
        nodes = []
        connections = []
        node_dict = {}
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            if line.startswith('graph') or line.startswith('flowchart'):
                continue
                
            # Enhanced pattern matching for all Mermaid arrow types
            arrow_patterns = [
                # 1. 带标签箭头：A -->|标签| B (优先匹配)
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*-->\s*\|(.+?)\|\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?',
                # 2. 普通箭头：A --> B（源和目标都可能有标签）
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?',
                # 3. 简化箭头：A --> B（备用模式）
                r'(\w+)\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?'
            ]
            
            match_found = False
            for pattern_index, pattern in enumerate(arrow_patterns):
                arrow_match = re.match(pattern, line)
                if arrow_match:
                    match_found = True
                    groups = arrow_match.groups()
                    
                    # 处理不同模式的匹配结果
                    if pattern_index == 0:  # 带标签箭头模式：A -->|标签| B
                        from_id = groups[0]
                        from_label = groups[1] if groups[1] else None
                        connection_label = groups[2]  # 箭头标签
                        to_id = groups[3]
                        to_label = groups[4] if groups[4] else None
                    else:  # 普通箭头模式
                        from_id = groups[0]
                        from_label = groups[1] if len(groups) > 1 and groups[1] else None
                        to_id = groups[2] if len(groups) > 2 else groups[1]
                        to_label = groups[3] if len(groups) > 3 and groups[3] else None
                        connection_label = ''  # 无标签
                    
                    # Process from node
                    if from_id not in node_dict:
                        label = self._extract_mermaid_label(from_label) if from_label else from_id
                        node_type = self._determine_mermaid_node_type(from_label) if from_label else 'default'
                        
                        nodes.append({
                            'id': from_id,
                            'label': label,
                            'type': node_type
                        })
                        node_dict[from_id] = True
                    
                    # Process to node
                    if to_id not in node_dict:
                        label = self._extract_mermaid_label(to_label) if to_label else to_id
                        node_type = self._determine_mermaid_node_type(to_label) if to_label else 'default'
                        
                        nodes.append({
                            'id': to_id,
                            'label': label,
                            'type': node_type
                        })
                        node_dict[to_id] = True
                    
                    # Add connection
                    connections.append({
                        'from': from_id,
                        'to': to_id,
                        'label': connection_label or ''
                    })
                    break
        
        return nodes, connections
    
    def _determine_node_type(self, content: str) -> str:
        """Determine node type based on content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['start', 'begin', '开始', '启动']):
            return 'start'
        elif any(word in content_lower for word in ['end', 'finish', 'complete', '结束', '完成']):
            return 'end'
        elif any(word in content_lower for word in ['?', 'if', 'decide', 'choice', '判断', '选择', '决策', '是否']):
            return 'decision'
        elif any(word in content_lower for word in ['process', 'handle', 'execute', '处理', '执行']):
            return 'process'
        else:
            return 'default'
    
    def _determine_mermaid_node_type(self, shape: str) -> str:
        """Determine node type based on Mermaid shape"""
        if not shape:
            return 'default'
        
        content = self._extract_mermaid_label(shape).lower()
        
        if shape.startswith('[') and shape.endswith(']'):
            if any(word in content for word in ['start', 'begin', '开始', '启动']):
                return 'start'
            elif any(word in content for word in ['end', 'finish', 'complete', '结束', '完成']):
                return 'end'
            else:
                return 'process'
        elif shape.startswith('{') and shape.endswith('}'):
            return 'decision'
        elif shape.startswith('(') and shape.endswith(')'):
            return 'start'
        else:
            return 'default'
    
    def _extract_mermaid_label(self, shape: str) -> str:
        """Extract label from Mermaid node shape"""
        if not shape:
            return ''
        return re.sub(r'^[\[\{\(]|[\]\}\)]$', '', shape)
    
    def _analyze_text_characteristics(self, nodes: List[Dict]) -> Dict[str, Any]:
        """Analyze text characteristics of nodes for adaptive layout / 分析节点文本特征以实现自适应布局"""
        if not nodes:
            return {
                "avg_text_length": 0,
                "max_text_length": 0,
                "text_complexity": "simple",
                "has_long_text": False,
                "text_distribution": "uniform"
            }
        
        # Calculate text lengths / 计算文本长度
        text_lengths = []
        for node in nodes:
            label = node.get('label', '')
            # Count characters, treating Chinese characters properly / 正确计算中文字符
            length = len(label)
            text_lengths.append(length)
        
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        max_length = max(text_lengths) if text_lengths else 0
        min_length = min(text_lengths) if text_lengths else 0
        
        # Determine text complexity / 确定文本复杂度
        if avg_length <= self.max_text_length_short:
            complexity = "simple"
        elif avg_length <= self.max_text_length_medium:
            complexity = "medium"
        else:
            complexity = "complex"
        
        # Check for long text nodes / 检查长文本节点
        has_long_text = any(length > self.max_text_length_medium for length in text_lengths)
        
        # Analyze text distribution / 分析文本分布
        length_variance = sum((l - avg_length) ** 2 for l in text_lengths) / len(text_lengths)
        if length_variance < 2:
            distribution = "uniform"
        elif length_variance < 10:
            distribution = "varied"
        else:
            distribution = "mixed"
        
        return {
            "avg_text_length": avg_length,
            "max_text_length": max_length,
            "min_text_length": min_length,
            "text_complexity": complexity,
            "has_long_text": has_long_text,
            "text_distribution": distribution,
            "length_variance": length_variance,
            "text_lengths": text_lengths
        }
    
    def _calculate_adaptive_grid(self, nodes: List[Dict], layout: str) -> Tuple[int, int]:
        """Calculate adaptive grid dimensions based on content analysis / 基于内容分析计算自适应网格尺寸"""
        node_count = len(nodes)
        text_analysis = self._analyze_text_characteristics(nodes)
        
        if layout == "left-right":
            # Adaptive horizontal layout / 自适应水平布局
            base_nodes_per_row = 4  # 基础每行节点数
            
            # Adjust based on text complexity / 根据文本复杂度调整
            if text_analysis["text_complexity"] == "simple":
                nodes_per_row = min(self.max_nodes_per_row, base_nodes_per_row + 1)  # 简单文本可以多放
            elif text_analysis["text_complexity"] == "complex":
                nodes_per_row = max(self.min_nodes_per_row, base_nodes_per_row - 1)  # 复杂文本少放
            else:
                nodes_per_row = base_nodes_per_row
            
            # Adjust for long text / 针对长文本调整
            if text_analysis["has_long_text"]:
                nodes_per_row = max(self.min_nodes_per_row, nodes_per_row - 1)
            
            # Adjust for text distribution / 根据文本分布调整
            if text_analysis["text_distribution"] == "mixed":
                nodes_per_row = max(self.min_nodes_per_row, nodes_per_row - 1)
            
            # Calculate rows and columns / 计算行列数
            nodes_per_row = max(self.min_nodes_per_row, min(self.max_nodes_per_row, nodes_per_row))
            rows = max(1, (node_count + nodes_per_row - 1) // nodes_per_row)
            cols = min(node_count, nodes_per_row)
            
        else:  # top-bottom
            # Adaptive vertical layout / 自适应垂直布局
            base_nodes_per_col = 5  # 基础每列节点数
            
            # Adjust based on text complexity / 根据文本复杂度调整
            if text_analysis["text_complexity"] == "simple":
                nodes_per_col = min(self.max_nodes_per_col, base_nodes_per_col + 2)  # 简单文本可以多放
            elif text_analysis["text_complexity"] == "complex":
                nodes_per_col = max(self.min_nodes_per_col, base_nodes_per_col - 1)  # 复杂文本少放
            else:
                nodes_per_col = base_nodes_per_col
            
            # Adjust for long text / 针对长文本调整
            if text_analysis["has_long_text"]:
                nodes_per_col = max(self.min_nodes_per_col, nodes_per_col - 1)
            
            # Adjust for text distribution / 根据文本分布调整
            if text_analysis["text_distribution"] == "mixed":
                nodes_per_col = max(self.min_nodes_per_col, nodes_per_col - 1)
            
            # Calculate rows and columns / 计算行列数
            nodes_per_col = max(self.min_nodes_per_col, min(self.max_nodes_per_col, nodes_per_col))
            cols = max(1, (node_count + nodes_per_col - 1) // nodes_per_col)
            rows = min(node_count, nodes_per_col)
        
        return rows, cols
    
    def _calculate_adaptive_canvas_size(self, nodes: List[Dict], layout: str, rows: int, cols: int) -> Tuple[float, float]:
        """Calculate adaptive canvas size based on content analysis / 基于内容分析计算自适应画布尺寸"""
        text_analysis = self._analyze_text_characteristics(nodes)
        
        # Base spacing / 基础间距
        base_h_spacing = self.horizontal_spacing
        base_v_spacing = self.vertical_spacing
        
        # Adjust spacing based on text complexity / 根据文本复杂度调整间距
        if text_analysis["text_complexity"] == "complex":
            h_spacing = base_h_spacing * 1.2  # 复杂文本需要更多空间
            v_spacing = base_v_spacing * 1.3
        elif text_analysis["text_complexity"] == "simple":
            h_spacing = base_h_spacing * 0.9  # 简单文本可以更紧凑
            v_spacing = base_v_spacing * 0.9
        else:
            h_spacing = base_h_spacing
            v_spacing = base_v_spacing
        
        # Adjust for long text / 针对长文本调整
        if text_analysis["has_long_text"]:
            h_spacing *= 1.15
            v_spacing *= 1.1
        
        # Calculate canvas dimensions / 计算画布尺寸
        if layout == "left-right":
            canvas_width = max(6, self.margin_x * 2 + cols * h_spacing)
            canvas_height = max(4, self.margin_y * 2 + rows * (self.node_height + v_spacing))
        else:  # top-bottom
            canvas_width = max(6, self.margin_x * 2 + cols * (self.node_width + h_spacing))
            canvas_height = max(6, self.margin_y * 2 + rows * v_spacing)
        
        return canvas_width, canvas_height
    
    def _calculate_adaptive_positions(self, nodes: List[Dict], layout: str, canvas_width: float, canvas_height: float, rows: int, cols: int) -> Dict[str, Tuple[float, float]]:
        """Calculate adaptive node positions with content-aware spacing / 计算内容感知的自适应节点位置"""
        positions = {}
        node_count = len(nodes)
        text_analysis = self._analyze_text_characteristics(nodes)
        
        # Get adaptive spacing / 获取自适应间距
        base_h_spacing = self.horizontal_spacing
        base_v_spacing = self.vertical_spacing
        
        # Adjust spacing based on content / 根据内容调整间距
        if text_analysis["text_complexity"] == "complex":
            h_spacing_factor = 1.2
            v_spacing_factor = 1.3
        elif text_analysis["text_complexity"] == "simple":
            h_spacing_factor = 0.9
            v_spacing_factor = 0.9
        else:
            h_spacing_factor = 1.0
            v_spacing_factor = 1.0
        
        if text_analysis["has_long_text"]:
            h_spacing_factor *= 1.15
            v_spacing_factor *= 1.1
        
        if layout == "left-right":
            # Adaptive multi-row horizontal layout / 自适应多行水平布局
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # Calculate adaptive spacing / 计算自适应间距
            if cols > 1:
                x_spacing = (available_width / cols) * h_spacing_factor
            else:
                x_spacing = available_width
                
            if rows > 1:
                y_spacing = (available_height / rows) * v_spacing_factor
            else:
                y_spacing = available_height
            
            # Position nodes with content-aware adjustments / 内容感知的节点定位
            for i, node in enumerate(nodes):
                row = i // cols
                col = i % cols
                
                # Basic position / 基础位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                # Fine-tune position based on text length / 根据文本长度微调位置
                text_length = len(node.get('label', ''))
                if text_length > text_analysis["avg_text_length"] * 1.5:
                    # Give more space to long text nodes / 为长文本节点提供更多空间
                    if col < cols - 1:  # Not the last column
                        x += x_spacing * 0.1
                
                positions[node['id']] = (x, y)
        
        else:  # top-bottom
            # Adaptive multi-column vertical layout / 自适应多列垂直布局
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # Calculate adaptive spacing / 计算自适应间距
            if cols > 1:
                x_spacing = (available_width / cols) * h_spacing_factor
            else:
                x_spacing = available_width
                
            if rows > 1:
                y_spacing = (available_height / rows) * v_spacing_factor
            else:
                y_spacing = available_height
            
            # Position nodes with content-aware adjustments / 内容感知的节点定位
            for i, node in enumerate(nodes):
                col = i // rows
                row = i % rows
                
                # Basic position / 基础位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                # Fine-tune position based on text length / 根据文本长度微调位置
                text_length = len(node.get('label', ''))
                if text_length > text_analysis["avg_text_length"] * 1.5:
                    # Give more space to long text nodes / 为长文本节点提供更多空间
                    if row < rows - 1:  # Not the last row
                        y -= y_spacing * 0.1
                
                positions[node['id']] = (x, y)
        
        return positions
    
    def _generate_compact_flowchart(self, nodes: List[Dict], connections: List[Dict], layout: str, input_type: str) -> str:
        """Generate compact flowchart with optimized space usage and save as PNG file"""
        if not nodes:
            raise ValueError("No nodes to generate flowchart")
        
        # Calculate adaptive grid dimensions based on content analysis / 基于内容分析计算自适应网格尺寸
        node_count = len(nodes)
        rows, cols = self._calculate_adaptive_grid(nodes, layout)
        canvas_width, canvas_height = self._calculate_adaptive_canvas_size(nodes, layout, rows, cols)
        
        # Create figure with dynamic size and theme support / 创建带主题支持的动态尺寸图形
        theme = self.get_current_theme()
        fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
        fig.patch.set_facecolor(theme['background'])  # Set background color / 设置背景颜色
        ax.set_xlim(0, canvas_width)
        ax.set_ylim(0, canvas_height)
        ax.axis('off')
        ax.set_facecolor(theme['background'])  # Set axes background / 设置坐标轴背景
        
        # Calculate adaptive positions using the calculated grid / 使用计算出的网格计算自适应位置
        positions = self._calculate_adaptive_positions(nodes, layout, canvas_width, canvas_height, rows, cols)
        
        # Draw nodes / 绘制节点
        for node in nodes:
            self._draw_compact_node(ax, node, positions[node['id']])
        
        # Draw intelligent connections / 绘制智能连接
        for connection in connections:
            self._draw_intelligent_connection(ax, connection, positions, layout)
        
        # Generate unique filename / 生成唯一文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        layout_suffix = "lr" if layout == "left-right" else "tb"
        filename = f"flowchart_{input_type}_{layout_suffix}_{timestamp}.png"
        file_path = os.path.join(self.output_dir, filename)
        
        # Save as PNG file with theme background / 保存为带主题背景的PNG文件
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight', 
                   facecolor=theme['background'], edgecolor='none', pad_inches=0.1)
        plt.close(fig)
        
        return file_path
    
    def _calculate_intelligent_positions(self, nodes: List[Dict], layout: str, canvas_width: float, canvas_height: float, rows: int, cols: int) -> Dict[str, Tuple[float, float]]:
        """Calculate intelligent multi-row/column positions to maximize space utilization / 计算智能多行多列位置以最大化空间利用"""
        positions = {}
        node_count = len(nodes)
        
        if layout == "left-right":
            # Multi-row horizontal layout / 多行水平布局
            # Calculate available space for nodes / 计算节点可用空间
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # Calculate spacing between nodes / 计算节点间距
            if cols > 1:
                x_spacing = available_width / cols
            else:
                x_spacing = available_width
                
            if rows > 1:
                y_spacing = available_height / rows
            else:
                y_spacing = available_height
            
            # Position nodes in grid layout / 网格布局放置节点
            for i, node in enumerate(nodes):
                row = i // cols  # 当前行
                col = i % cols   # 当前列
                
                # Calculate position / 计算位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                positions[node['id']] = (x, y)
        
        else:  # top-bottom
            # Multi-column vertical layout / 多列垂直布局
            # Calculate available space for nodes / 计算节点可用空间
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # Calculate spacing between nodes / 计算节点间距
            if cols > 1:
                x_spacing = available_width / cols
            else:
                x_spacing = available_width
                
            if rows > 1:
                y_spacing = available_height / rows
            else:
                y_spacing = available_height
            
            # Position nodes in grid layout / 网格布局放置节点
            for i, node in enumerate(nodes):
                col = i // rows  # 当前列
                row = i % rows   # 当前行
                
                # Calculate position / 计算位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                positions[node['id']] = (x, y)
        
        return positions
    
    def _calculate_compact_positions(self, nodes: List[Dict], layout: str, canvas_width: float, canvas_height: float) -> Dict[str, Tuple[float, float]]:
        """Legacy compact position calculation (kept for compatibility) / 传统紧凑位置计算（保持兼容性）"""
        positions = {}
        node_count = len(nodes)
        
        if layout == "left-right":
            # Tight horizontal arrangement / 紧密水平排列
            if node_count == 1:
                positions[nodes[0]['id']] = (canvas_width / 2, canvas_height / 2)
            else:
                # Calculate positions with minimal spacing / 计算最小间距的位置
                start_x = self.margin_x + self.node_width / 2
                end_x = canvas_width - self.margin_x - self.node_width / 2
                
                if node_count > 1:
                    x_step = (end_x - start_x) / (node_count - 1)
                else:
                    x_step = 0
                
                y_center = canvas_height / 2
                
                for i, node in enumerate(nodes):
                    x = start_x + i * x_step
                    positions[node['id']] = (x, y_center)
        
        else:  # top-bottom
            # Tight vertical arrangement / 紧密垂直排列
            if node_count == 1:
                positions[nodes[0]['id']] = (canvas_width / 2, canvas_height / 2)
            else:
                # Calculate positions with minimal spacing / 计算最小间距的位置
                start_y = canvas_height - self.margin_y - self.node_height / 2
                end_y = self.margin_y + self.node_height / 2
                
                if node_count > 1:
                    y_step = (start_y - end_y) / (node_count - 1)
                else:
                    y_step = 0
                
                x_center = canvas_width / 2
                
                for i, node in enumerate(nodes):
                    y = start_y - i * y_step
                    positions[node['id']] = (x_center, y)
        
        return positions
    
    def _draw_compact_node(self, ax, node: Dict, position: Tuple[float, float]):
        """Draw a compact node with enhanced visual effects and theme support"""
        x, y = position
        node_type = node.get('type', 'default')
        label = node.get('label', '')
        
        # Truncate long labels / 截断长标签
        if len(label) > 15:
            label = label[:12] + "..."
        
        # Get current theme / 获取当前主题
        theme = self.get_current_theme()
        color = theme['node_colors'].get(node_type, theme['node_colors']['default'])
        text_color = theme['text_color']
        border_color = theme['border_color']
        
        # Get node shape / 获取节点形状
        shape = self.node_shapes.get(node_type, self.node_shapes['default'])
        
        # Draw shadow first if enabled / 如果启用阴影，先绘制阴影
        if self.shadow_enabled:
            shadow_x = x + self.shadow_offset[0]
            shadow_y = y + self.shadow_offset[1]
            shadow_patch = self._create_node_patch(shadow_x, shadow_y, shape, node_type, 
                                                 '#00000040', '#00000040', alpha=0.3)
            ax.add_patch(shadow_patch)
        
        # Create main node patch / 创建主节点补丁
        node_patch = self._create_node_patch(x, y, shape, node_type, color, border_color)
        
        # Add gradient effect if enabled / 如果启用渐变效果
        if self.gradient_enabled:
            node_patch = self._apply_gradient_effect(node_patch, color)
        
        ax.add_patch(node_patch)
        
        # Enhanced text rendering / 增强文本渲染
        font_size = 9 if len(label) <= 8 else 8
        ax.text(x, y, label, ha='center', va='center', fontsize=font_size,
               weight='bold', wrap=True, fontproperties=self.chinese_font,
               color=text_color, zorder=10)
    
    def _create_node_patch(self, x: float, y: float, shape: str, node_type: str, 
                          fill_color: str, border_color: str, alpha: float = 1.0):
        """
        Create a node patch with specified shape and colors
        创建指定形状和颜色的节点补丁
        """
        if shape == 'diamond' or node_type == 'decision':
            # Diamond shape for decision nodes / 决策节点使用菱形
            width, height = self.node_width * 0.9, self.node_height * 0.9
            # Create diamond using polygon
            diamond_points = [
                [x, y + height/2],      # Top
                [x + width/2, y],       # Right
                [x, y - height/2],      # Bottom
                [x - width/2, y]        # Left
            ]
            from matplotlib.patches import Polygon
            patch = Polygon(diamond_points, facecolor=fill_color, 
                          edgecolor=border_color, linewidth=self.border_width, alpha=alpha)
        elif shape == 'round':
            # Rounded rectangle for start/end nodes / 开始/结束节点使用圆角矩形
            width, height = self.node_width, self.node_height
            patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                 boxstyle="round,pad=0.1", 
                                 facecolor=fill_color, edgecolor=border_color, 
                                 linewidth=self.border_width, alpha=alpha)
        else:  # 'rect' - regular rectangle
            # Regular rectangle for process nodes / 处理节点使用矩形
            width, height = self.node_width, self.node_height
            patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                 boxstyle="round,pad=0.02",
                                 facecolor=fill_color, edgecolor=border_color, 
                                 linewidth=self.border_width, alpha=alpha)
        
        return patch
    
    def _apply_gradient_effect(self, patch, base_color: str):
        """
        Apply gradient effect to node patch (simplified version)
        为节点补丁应用渐变效果（简化版本）
        """
        # For now, we'll create a subtle gradient effect by adjusting the color
        # In a more advanced implementation, we could use matplotlib's gradient fills
        return patch
    
    def _draw_intelligent_connection(self, ax, connection: Dict, positions: Dict[str, Tuple[float, float]], layout: str):
        """Draw intelligent connection between nodes with optimal routing / 绘制智能节点连接，优化路径"""
        from_id = connection['from']
        to_id = connection['to']
        
        if from_id not in positions or to_id not in positions:
            return
        
        from_pos = positions[from_id]
        to_pos = positions[to_id]
        
        # Calculate connection points based on node positions / 根据节点位置计算连接点
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Determine optimal connection style based on layout and positions / 根据布局和位置确定最佳连接样式
        dx = to_x - from_x
        dy = to_y - from_y
        
        if layout == "left-right":
            # For left-right layout, prefer horizontal flow / 左右布局优先水平流向
            if abs(dx) > abs(dy):  # Mostly horizontal
                # Direct horizontal connection / 直接水平连接
                self._draw_direct_arrow(ax, from_pos, to_pos)
            else:  # Mostly vertical (multi-row case)
                # Draw stepped connection for better readability / 绘制阶梯连接以提高可读性
                self._draw_stepped_connection(ax, from_pos, to_pos, "horizontal-first")
        else:  # top-bottom
            # For top-bottom layout, prefer vertical flow / 上下布局优先垂直流向
            if abs(dy) > abs(dx):  # Mostly vertical
                # Direct vertical connection / 直接垂直连接
                self._draw_direct_arrow(ax, from_pos, to_pos)
            else:  # Mostly horizontal (multi-column case)
                # Draw stepped connection for better readability / 绘制阶梯连接以提高可读性
                self._draw_stepped_connection(ax, from_pos, to_pos, "vertical-first")
    
    def _draw_direct_arrow(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float]):
        """Draw a direct arrow connection with theme support / 绘制带主题支持的直接箭头连接"""
        theme = self.get_current_theme()
        connection_color = theme['connection_color']
        connection_width = theme['connection_width']
        
        arrow = ConnectionPatch(from_pos, to_pos, "data", "data",
                              arrowstyle="->", shrinkA=35, shrinkB=35,
                              mutation_scale=18, fc=connection_color, ec=connection_color,
                              linewidth=connection_width, alpha=0.9)
        ax.add_patch(arrow)
    
    def _draw_stepped_connection(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float], direction: str):
        """Draw a stepped connection (L-shaped) with theme support / 绘制带主题支持的阶梯连接（L形）"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Get theme colors / 获取主题颜色
        theme = self.get_current_theme()
        connection_color = theme['connection_color']
        connection_width = theme['connection_width']
        
        if direction == "horizontal-first":
            # Go horizontal first, then vertical / 先水平后垂直
            mid_x = from_x + (to_x - from_x) * 0.7  # 70% of the way horizontally
            mid_y = from_y
            
            # Draw first segment (horizontal) / 绘制第一段（水平）
            ax.plot([from_x, mid_x], [from_y, mid_y], color=connection_color, 
                   linewidth=connection_width, alpha=0.9)
            
            # Draw second segment (vertical) with arrow / 绘制第二段（垂直）带箭头
            arrow = ConnectionPatch((mid_x, mid_y), to_pos, "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=35,
                                  mutation_scale=16, fc=connection_color, ec=connection_color,
                                  linewidth=connection_width, alpha=0.9)
            ax.add_patch(arrow)
        else:  # vertical-first
            # Go vertical first, then horizontal / 先垂直后水平
            mid_x = from_x
            mid_y = from_y + (to_y - from_y) * 0.7  # 70% of the way vertically
            
            # Draw first segment (vertical) / 绘制第一段（垂直）
            ax.plot([from_x, mid_x], [from_y, mid_y], color=connection_color,
                   linewidth=connection_width, alpha=0.9)
            
            # Draw second segment (horizontal) with arrow / 绘制第二段（水平）带箭头
            arrow = ConnectionPatch((mid_x, mid_y), to_pos, "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=35,
                                  mutation_scale=16, fc=connection_color, ec=connection_color,
                                  linewidth=connection_width, alpha=0.9)
            ax.add_patch(arrow)
    
    def _draw_compact_connection(self, ax, connection: Dict, positions: Dict[str, Tuple[float, float]]):
        """Legacy compact connection drawing (kept for compatibility) / 传统紧凑连接绘制（保持兼容性）"""
        from_id = connection['from']
        to_id = connection['to']
        
        if from_id not in positions or to_id not in positions:
            return
        
        from_pos = positions[from_id]
        to_pos = positions[to_id]
        
        # Compact arrow / 紧凑箭头
        arrow = ConnectionPatch(from_pos, to_pos, "data", "data",
                              arrowstyle="->", shrinkA=35, shrinkB=35,
                              mutation_scale=15, fc="black", ec="black",
                              linewidth=1.5)
        ax.add_patch(arrow)
