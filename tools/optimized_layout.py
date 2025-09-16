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
import matplotlib.patheffects as PathEffects  # 添加路径效果支持
import matplotlib.font_manager as fm
import numpy as np
from PIL import Image

# Import English layout generator / 导入英文布局生成器
from .english_layout import EnglishFlowchartGenerator


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
        self.node_width = 2.2   # 减小宽度，提高空间利用率
        self.node_height = 1.0  # 减小高度，提高空间利用率
        
        # 英文文本专用的节点尺寸
        self.english_node_width = 2.8   # 英文文本需要更宽的节点
        self.english_node_height = 1.1  # 英文文本可能需要稍高的节点
        
        # Compact spacing for efficient layouts / 紧凑间距以提高布局效率
        self.horizontal_spacing = 2.4  # 减小水平间距，紧凑布局
        self.vertical_spacing = 1.6    # 减小垂直间距，紧凑布局
        
        # Optimized canvas margins / 优化的画布边距
        self.margin_x = 0.8  # 减小水平边距，节省空间
        self.margin_y = 0.8  # 减小垂直边距，节省空间
        
        # Visual enhancement: Theme system / 视觉增强：主题系统
        self.themes = self._initialize_themes()
        self.current_theme = 'modern'  # Default theme / 默认主题（改为现代主题）
        
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
        self.min_nodes_per_row = 3        # 每行最少节点数（避免2元素排版）
        self.max_nodes_per_row = 6        # 每行最多节点数
        self.min_nodes_per_col = 3        # 每列最少节点数（避免2元素排版）
        self.max_nodes_per_col = 8        # 每列最多节点数
        
        # Initialize English layout generator / 初始化英文布局生成器
        self.english_generator = EnglishFlowchartGenerator()
    
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
                'connection_width': 2.0,
                # 带标签箭头的颜色配置（中英文支持）
                'connection_label_colors': {
                    # 中文标签
                    '通过': '#4CAF50',    # 绿色 - 成功
                    '是': '#4CAF50',        # 绿色 - 肯定
                    '成功': '#4CAF50',      # 绿色 - 成功
                    '正确': '#4CAF50',      # 绿色 - 正确
                    '不通过': '#F44336',  # 红色 - 失败
                    '否': '#F44336',        # 红色 - 否定
                    '失败': '#F44336',      # 红色 - 失败
                    '错误': '#F44336',      # 红色 - 错误
                    '可能': '#FF9800',      # 橙色 - 不确定
                    '待定': '#FF9800',      # 橙色 - 待定
                    # 英文标签
                    'approved': '#4CAF50',    # Green - Success
                    'yes': '#4CAF50',         # Green - Positive
                    'success': '#4CAF50',     # Green - Success
                    'correct': '#4CAF50',     # Green - Correct
                    'true': '#4CAF50',        # Green - True
                    'rejected': '#F44336',    # Red - Failure
                    'no': '#F44336',          # Red - Negative
                    'failed': '#F44336',      # Red - Failed
                    'error': '#F44336',       # Red - Error
                    'false': '#F44336',       # Red - False
                    'maybe': '#FF9800',       # Orange - Uncertain
                    'pending': '#FF9800',     # Orange - Pending
                    'default': '#424242'      # 默认颜色
                }
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
                'connection_width': 1.8,
                # 带标签箭头的颜色配置（中英文支持）
                'connection_label_colors': {
                    # 中文标签
                    '通过': '#388E3C',    # 绿色 - 成功  
                    '是': '#388E3C',        # 绿色 - 肯定
                    '成功': '#388E3C',      # 绿色 - 成功
                    '正确': '#388E3C',      # 绿色 - 正确
                    '不通过': '#D32F2F',  # 红色 - 失败
                    '否': '#D32F2F',        # 红色 - 否定
                    '失败': '#D32F2F',      # 红色 - 失败
                    '错误': '#D32F2F',      # 红色 - 错误
                    '可能': '#F57C00',      # 橙色 - 不确定
                    '待定': '#F57C00',      # 橙色 - 待定
                    # 英文标签
                    'approved': '#388E3C',    # Green - Success
                    'yes': '#388E3C',         # Green - Positive
                    'success': '#388E3C',     # Green - Success
                    'correct': '#388E3C',     # Green - Correct
                    'true': '#388E3C',        # Green - True
                    'rejected': '#D32F2F',    # Red - Failure
                    'no': '#D32F2F',          # Red - Negative
                    'failed': '#D32F2F',      # Red - Failed
                    'error': '#D32F2F',       # Red - Error
                    'false': '#D32F2F',       # Red - False
                    'maybe': '#F57C00',       # Orange - Uncertain
                    'pending': '#F57C00',     # Orange - Pending
                    'default': '#37474F'      # 默认颜色
                }
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
                'connection_width': 2.2,
                # 带标签箭头的颜色配置（中英文支持）
                'connection_label_colors': {
                    # 中文标签
                    '通过': '#00E676',    # 亮绿色 - 成功
                    '是': '#00E676',        # 亮绿色 - 肯定
                    '成功': '#00E676',      # 亮绿色 - 成功
                    '正确': '#00E676',      # 亮绿色 - 正确
                    '不通过': '#FF1744',  # 亮红色 - 失败
                    '否': '#FF1744',        # 亮红色 - 否定
                    '失败': '#FF1744',      # 亮红色 - 失败
                    '错误': '#FF1744',      # 亮红色 - 错误
                    '可能': '#FF6D00',      # 亮橙色 - 不确定
                    '待定': '#FF6D00',      # 亮橙色 - 待定
                    # 英文标签
                    'approved': '#00E676',    # Bright Green - Success
                    'yes': '#00E676',         # Bright Green - Positive
                    'success': '#00E676',     # Bright Green - Success
                    'correct': '#00E676',     # Bright Green - Correct
                    'true': '#00E676',        # Bright Green - True
                    'rejected': '#FF1744',    # Bright Red - Failure
                    'no': '#FF1744',          # Bright Red - Negative
                    'failed': '#FF1744',      # Bright Red - Failed
                    'error': '#FF1744',       # Bright Red - Error
                    'false': '#FF1744',       # Bright Red - False
                    'maybe': '#FF6D00',       # Bright Orange - Uncertain
                    'pending': '#FF6D00',     # Bright Orange - Pending
                    'default': '#FFFFFF'      # 默认颜色
                }
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
                'connection_width': 1.5,
                # 带标签箭头的颜色配置（中英文支持）
                'connection_label_colors': {
                    # 中文标签
                    '通过': '#689F38',    # 深绿色 - 成功
                    '是': '#689F38',        # 深绿色 - 肯定
                    '成功': '#689F38',      # 深绿色 - 成功
                    '正确': '#689F38',      # 深绿色 - 正确
                    '不通过': '#C62828',  # 深红色 - 失败
                    '否': '#C62828',        # 深红色 - 否定
                    '失败': '#C62828',      # 深红色 - 失败
                    '错误': '#C62828',      # 深红色 - 错误
                    '可能': '#EF6C00',      # 深橙色 - 不确定
                    '待定': '#EF6C00',      # 深橙色 - 待定
                    # 英文标签
                    'approved': '#689F38',    # Deep Green - Success
                    'yes': '#689F38',         # Deep Green - Positive
                    'success': '#689F38',     # Deep Green - Success
                    'correct': '#689F38',     # Deep Green - Correct
                    'true': '#689F38',        # Deep Green - True
                    'rejected': '#C62828',    # Deep Red - Failure
                    'no': '#C62828',          # Deep Red - Negative
                    'failed': '#C62828',      # Deep Red - Failed
                    'error': '#C62828',       # Deep Red - Error
                    'false': '#C62828',       # Deep Red - False
                    'maybe': '#EF6C00',       # Deep Orange - Uncertain
                    'pending': '#EF6C00',     # Deep Orange - Pending
                    'default': '#616161'      # 默认颜色
                }
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
                'connection_width': 1.5,
                # 带标签箭头的颜色配置（中英文支持）
                'connection_label_colors': {
                    # 中文标签
                    '通过': '#4CAF50',    # 绿色 - 成功
                    '是': '#4CAF50',        # 绿色 - 肯定
                    '成功': '#4CAF50',      # 绿色 - 成功
                    '正确': '#4CAF50',      # 绿色 - 正确
                    '不通过': '#F44336',  # 红色 - 失败
                    '否': '#F44336',        # 红色 - 否定
                    '失败': '#F44336',      # 红色 - 失败
                    '错误': '#F44336',      # 红色 - 错误
                    '可能': '#FF9800',      # 橙色 - 不确定
                    '待定': '#FF9800',      # 橙色 - 待定
                    # 英文标签
                    'approved': '#4CAF50',    # Green - Success
                    'yes': '#4CAF50',         # Green - Positive
                    'success': '#4CAF50',     # Green - Success
                    'correct': '#4CAF50',     # Green - Correct
                    'true': '#4CAF50',        # Green - True
                    'rejected': '#F44336',    # Red - Failure
                    'no': '#F44336',          # Red - Negative
                    'failed': '#F44336',      # Red - Failed
                    'error': '#F44336',       # Red - Error
                    'false': '#F44336',       # Red - False
                    'maybe': '#FF9800',       # Orange - Uncertain
                    'pending': '#FF9800',     # Orange - Pending
                    'default': '#333333'      # 默认颜色
                }
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
    
    def _get_connection_color(self, connection_label: str) -> str:
        """
        Get connection color based on label
        根据标签获取连接颜色
        """
        theme = self.get_current_theme()
        label_colors = theme.get('connection_label_colors', {})
        
        if not connection_label:
            return theme['connection_color']
        
        # 检查精确匹配
        if connection_label in label_colors:
            return label_colors[connection_label]
        
        # 检查包含匹配（不区分大小写）
        label_lower = connection_label.lower().strip()
        for key, color in label_colors.items():
            if key != 'default' and (key.lower() in label_lower or label_lower in key.lower()):
                return color
        
        # 返回默认颜色
        return label_colors.get('default', theme['connection_color'])
    
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
        """Generate compact flowchart from Mermaid syntax with intelligent layout selection"""
        try:
            nodes, connections = self._parse_mermaid(text)
            
            if not nodes:
                return {
                    "success": False,
                    "error": "No valid nodes found in Mermaid syntax",
                    "message": "Please provide valid Mermaid flowchart syntax"
                }
            
            # 智能选择布局算法 - Intelligent layout algorithm selection
            text_analysis = self._analyze_text_characteristics(nodes)
            structure_analysis = self._analyze_flowchart_structure(nodes, connections)
            
            # 判断是否使用英文专用布局（但不包括分支场景）
            use_english_layout = (
                text_analysis["is_primarily_english"] and  # 主要是英文
                not structure_analysis['has_branches'] and  # 无分支结构（分支用标准自由布局）
                (
                    text_analysis["avg_text_length"] > 20 or  # 平均文本较长
                    text_analysis["text_complexity"] == "complex"  # 文本复杂
                )
            )
            
            if use_english_layout:
                # 使用英文专用布局算法（仅限无分支的复杂英文文本）
                print(f"[DEBUG] Using English grid layout for complex English text (avg_len: {text_analysis['avg_text_length']:.1f}, no branches)")
                file_path = self.english_generator.generate_english_flowchart(nodes, connections, layout, "mermaid")
            else:
                # 使用标准布局算法（包括英文分支流程图）
                if structure_analysis['has_branches']:
                    print(f"[DEBUG] Using standard FREE layout for branching flowchart (english: {text_analysis['is_primarily_english']}, branches: {len(structure_analysis['branch_nodes'])})")
                else:
                    print(f"[DEBUG] Using standard GRID layout for linear flowchart (english: {text_analysis['is_primarily_english']})")
                file_path = self._generate_compact_flowchart(nodes, connections, layout, "mermaid")
            
            return {
                "success": True,
                "file_path": file_path,
                "nodes_count": len(nodes),
                "connections_count": len(connections),
                "layout": layout,
                "format": "png",
                "input_type": "mermaid",
                "layout_algorithm": "english_optimized" if use_english_layout else "standard"
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
                # 2. 带标签箭头：A -- 标签 --> B (支持用户提供的语法)
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*--\s*([^-]+?)\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?',
                # 3. 普通箭头：A --> B（源和目标都可能有标签）
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?',
                # 4. 简化箭头：A --> B（备用模式）
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
                        if len(groups) >= 5:
                            from_id = groups[0]
                            from_label = groups[1] if groups[1] else None
                            connection_label = groups[2]  # 箭头标签
                            to_id = groups[3]
                            to_label = groups[4] if groups[4] else None
                        else:
                            continue  # 跳过不合法的匹配
                    elif pattern_index == 1:  # 带标签箭头模式：A -- 标签 --> B
                        if len(groups) >= 5:
                            from_id = groups[0]
                            from_label = groups[1] if groups[1] else None
                            connection_label = groups[2].strip()  # 箭头标签，去除空格
                            to_id = groups[3]
                            to_label = groups[4] if groups[4] else None
                        else:
                            continue  # 跳过不合法的匹配
                    elif pattern_index == 2:  # 普通箭头模式：A --> B（源和目标都可能有标签）
                        if len(groups) >= 4:
                            from_id = groups[0]
                            from_label = groups[1] if groups[1] else None
                            to_id = groups[2]
                            to_label = groups[3] if groups[3] else None
                            connection_label = ''  # 无标签
                        else:
                            continue  # 跳过不合法的匹配
                    else:  # pattern_index == 3, 简化箭头模式：A --> B
                        if len(groups) >= 2:
                            from_id = groups[0]
                            from_label = None
                            to_id = groups[1]
                            to_label = groups[2] if len(groups) > 2 and groups[2] else None
                            connection_label = ''  # 无标签
                        else:
                            continue  # 跳过不合法的匹配
                    
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
    
    def _analyze_flowchart_structure(self, nodes: List[Dict], connections: List[Dict]) -> Dict[str, Any]:
        """
        Analyze flowchart structure to detect branches and decision points
        分析流程图结构以检测分支和决策点
        """
        # Build connection graph / 构建连接图
        outgoing_connections = {}
        incoming_connections = {}
        
        for connection in connections:
            from_id = connection['from']
            to_id = connection['to']
            
            # Track outgoing connections / 跟踪出向连接
            if from_id not in outgoing_connections:
                outgoing_connections[from_id] = []
            outgoing_connections[from_id].append(connection)
            
            # Track incoming connections / 跟踪入向连接
            if to_id not in incoming_connections:
                incoming_connections[to_id] = []
            incoming_connections[to_id].append(connection)
        
        # Detect branch nodes (nodes with multiple outgoing connections) / 检测分支节点（有多个出向连接的节点）
        branch_nodes = []
        decision_nodes = []
        
        for node in nodes:
            node_id = node['id']
            outgoing_count = len(outgoing_connections.get(node_id, []))
            
            # Node with multiple outgoing connections is a branch point / 有多个出向连接的节点是分支点
            if outgoing_count > 1:
                branch_nodes.append(node_id)
                
                # Check if it's explicitly a decision node / 检查是否明确是决策节点
                if node.get('type') == 'decision' or '{' in node.get('label', ''):
                    decision_nodes.append(node_id)
        
        # Detect merge nodes (nodes with multiple incoming connections) / 检测合并节点（有多个入向连接的节点）
        merge_nodes = []
        for node in nodes:
            node_id = node['id']
            incoming_count = len(incoming_connections.get(node_id, []))
            if incoming_count > 1:
                merge_nodes.append(node_id)
        
        # Calculate branching complexity / 计算分支复杂度
        max_branches = max([len(outgoing_connections.get(node['id'], [])) for node in nodes], default=0)
        total_branches = sum([max(0, len(outgoing_connections.get(node['id'], [])) - 1) for node in nodes])
        
        has_branches = len(branch_nodes) > 0
        has_complex_branches = max_branches > 2 or total_branches > 2
        
        return {
            'has_branches': has_branches,
            'has_complex_branches': has_complex_branches,
            'branch_nodes': branch_nodes,
            'decision_nodes': decision_nodes,
            'merge_nodes': merge_nodes,
            'max_branches': max_branches,
            'total_branches': total_branches,
            'outgoing_connections': outgoing_connections,
            'incoming_connections': incoming_connections
        }
    
    def _analyze_text_characteristics(self, nodes: List[Dict]) -> Dict[str, Any]:
        """
        分析文本特征，包括英文文本的特殊处理
        Analyze text characteristics with special handling for English text
        """
        # Calculate text lengths / 计算文本长度
        text_lengths = []
        english_node_count = 0
        total_english_chars = 0
        
        for node in nodes:
            label = node.get('label', '')
            # Count characters, treating Chinese characters properly / 正确计算中文字符
            length = len(label)
            text_lengths.append(length)
            
            # 检测英文文本（包含字母和空格的比例）
            english_chars = sum(1 for c in label if c.isalpha() and ord(c) < 128 or c.isspace())
            if english_chars / max(1, len(label)) > 0.6:  # 60%以上是英文字符
                english_node_count += 1
                total_english_chars += english_chars
        
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        max_length = max(text_lengths) if text_lengths else 0
        min_length = min(text_lengths) if text_lengths else 0
        
        # 英文文本特征分析
        is_primarily_english = english_node_count / len(nodes) > 0.5 if nodes else False
        avg_english_length = total_english_chars / max(1, english_node_count)
        
        # Determine text complexity with English adjustment / 确定文本复杂度（考虑英文调整）
        if is_primarily_english:
            # 英文文本的阈值需要调整，因为英文通常更长
            short_threshold = self.max_text_length_short * 1.5  # 英文短文本阈值增加50%
            medium_threshold = self.max_text_length_medium * 1.8  # 英文中等文本阈值增加80%
        else:
            short_threshold = self.max_text_length_short
            medium_threshold = self.max_text_length_medium
        
        if avg_length <= short_threshold:
            complexity = "simple"
        elif avg_length <= medium_threshold:
            complexity = "medium"
        else:
            complexity = "complex"
        
        # Check for long text nodes / 检查长文本节点
        has_long_text = any(length > medium_threshold for length in text_lengths)
        
        # Analyze text distribution / 分析文本分布
        if len(text_lengths) > 0:
            length_variance = sum((l - avg_length) ** 2 for l in text_lengths) / len(text_lengths)
        else:
            length_variance = 0
            
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
            "text_lengths": text_lengths,
            "is_primarily_english": is_primarily_english,
            "english_node_count": english_node_count,
            "avg_english_length": avg_english_length
        }
    
    def _get_node_dimensions(self, node: Dict) -> Tuple[float, float]:
        """
        根据节点内容获取动态节点尺寸
        Get dynamic node dimensions based on node content
        """
        label = node.get('label', '')
        
        # 检测是否为英文文本
        english_chars = sum(1 for c in label if c.isalpha() and ord(c) < 128 or c.isspace())
        is_english = english_chars / max(1, len(label)) > 0.6
        
        if is_english:
            # 英文文本使用更宽的节点
            base_width = self.english_node_width
            base_height = self.english_node_height
            
            # 根据文本长度进一步调整
            if len(label) > 40:
                base_width *= 1.2  # 超长英文文本增加20%宽度
            elif len(label) > 25:
                base_width *= 1.1  # 长英文文本增加10%宽度
        else:
            # 中文文本使用标准节点尺寸
            base_width = self.node_width
            base_height = self.node_height
            
            # 根据中文文本长度调整
            if len(label) > 20:
                base_width *= 1.1  # 长中文文本增加10%宽度
        
        return base_width, base_height
    
    def _calculate_dynamic_spacing(self, node_count: int, layout: str) -> Tuple[float, float]:
        """
        根据节点数量和布局类型动态计算间距
        Calculate dynamic spacing based on node count and layout type
        """
        base_h_spacing = self.horizontal_spacing
        base_v_spacing = self.vertical_spacing
        
        # 根据节点数量调整间距系数 - 更激进的紧凑化
        if node_count <= 4:
            # 少量节点：适中空间
            spacing_factor = 1.0
        elif node_count <= 8:
            # 中等数量：紧凑布局
            spacing_factor = 0.85
        elif node_count <= 12:
            # 较多节点：更紧凑
            spacing_factor = 0.75
        else:
            # 大量节点：最紧凑布局
            spacing_factor = 0.65
        
        dynamic_h_spacing = base_h_spacing * spacing_factor
        dynamic_v_spacing = base_v_spacing * spacing_factor
        
        # 更紧凑的最小间距，防止重叠但节省空间
        min_h_spacing = self.node_width + 0.5  # 减小空白间距
        min_v_spacing = self.node_height + 0.4  # 减小空白间距
        
        dynamic_h_spacing = max(dynamic_h_spacing, min_h_spacing)
        dynamic_v_spacing = max(dynamic_v_spacing, min_v_spacing)
        
        return dynamic_h_spacing, dynamic_v_spacing
    
    def _calculate_adaptive_grid(self, nodes: List[Dict], layout: str) -> Tuple[int, int]:
        """Calculate adaptive grid dimensions based on content analysis / 基于内容分析计算自适应网格尺寸"""
        node_count = len(nodes)
        if node_count == 0:
            return 1, 1
            
        text_analysis = self._analyze_text_characteristics(nodes)
        
        if layout == "left-right":
            # 水平布局：优先横向排列，减少行数
            if node_count <= 6:
                # 少量节点：单行排列
                cols = node_count
                rows = 1
            elif node_count <= 12:
                # 中等节点：2行排列
                cols = (node_count + 1) // 2
                rows = 2
            elif node_count <= 18:
                # 较多节点：3行排列
                cols = (node_count + 2) // 3
                rows = 3
            else:
                # 大量节点：4行排列
                cols = (node_count + 3) // 4
                rows = 4
            
            # 根据文本复杂度调整：复杂文本减少每行列数
            if text_analysis["text_complexity"] == "complex" or text_analysis["has_long_text"]:
                if cols > 4:
                    cols = max(4, cols - 1)
                    rows = max(1, (node_count + cols - 1) // cols)
            
            # 确保网格尺寸合理
            cols = max(1, min(cols, node_count))
            rows = max(1, (node_count + cols - 1) // cols)
            
        else:  # top-bottom
            # 垂直布局：优先纵向排列，减少列数
            if node_count <= 8:
                # 少量节点：单列排列
                cols = 1
                rows = node_count
            elif node_count <= 16:
                # 中等节点：2列排列
                cols = 2
                rows = (node_count + 1) // 2
            elif node_count <= 24:
                # 较多节点：3列排列
                cols = 3
                rows = (node_count + 2) // 3
            else:
                # 大量节点：4列排列
                cols = 4
                rows = (node_count + 3) // 4
            
            # 根据文本复杂度调整：复杂文本减少每列行数
            if text_analysis["text_complexity"] == "complex" or text_analysis["has_long_text"]:
                if rows > 6:
                    rows = max(6, rows - 1)
                    cols = max(1, (node_count + rows - 1) // rows)
            
            # 确保网格尺寸合理
            cols = max(1, min(cols, node_count))
            rows = max(1, (node_count + cols - 1) // cols)
        
        return rows, cols
    
    def _calculate_adaptive_canvas_size(self, nodes: List[Dict], layout: str, rows: int, cols: int) -> Tuple[float, float]:
        """Calculate adaptive canvas size based on content analysis / 基于内容分析计算自适应画布尺寸"""
        text_analysis = self._analyze_text_characteristics(nodes)
        node_count = len(nodes)
        
        # 使用动态间距计算
        dynamic_h_spacing, dynamic_v_spacing = self._calculate_dynamic_spacing(node_count, layout)
        
        # Base spacing / 基础间距
        base_h_spacing = dynamic_h_spacing
        base_v_spacing = dynamic_v_spacing
        
        # Adjust spacing based on text complexity / 根据文本复杂度调整间距
        if text_analysis["text_complexity"] == "complex":
            h_spacing = base_h_spacing * 1.1  # 复杂文本需要更多空间
            v_spacing = base_v_spacing * 1.1
        elif text_analysis["text_complexity"] == "simple":
            h_spacing = base_h_spacing * 0.95  # 简单文本可以更紧凑
            v_spacing = base_v_spacing * 0.95
        else:
            h_spacing = base_h_spacing
            v_spacing = base_v_spacing
        
        # Adjust for long text / 针对长文本调整
        if text_analysis["has_long_text"]:
            h_spacing *= 1.1
            v_spacing *= 1.05
        
        # 英文文本特殊处理
        if text_analysis["is_primarily_english"]:
            # 英文文本通常需要更多水平空间
            h_spacing *= 1.2  # 增加20%水平空间
            # 如果平均英文长度很长，进一步调整
            if text_analysis["avg_english_length"] > 40:
                h_spacing *= 1.3  # 超长英文再增加30%
            # 垂直空间也需要适度增加以适应可能的换行
            v_spacing *= 1.1
        
        # 紧凑间距计算：平衡防重叠和空间利用
        # 使用适度的间距增强，避免浪费空间
        compact_h_spacing = h_spacing * 1.1  # 仅增加10%水平间距
        compact_v_spacing = v_spacing * 1.1  # 仅增加10%垂直间距
        
        # Calculate canvas dimensions / 计算画布尺寸
        if layout == "left-right":
            # 水平布局：紧凑计算所需宽度
            required_width = cols * self.node_width + (cols - 1) * compact_h_spacing if cols > 1 else self.node_width
            canvas_width = max(8, self.margin_x * 2 + required_width * 1.1)  # 仅10%额外空间
            
            # 计算实际需要的高度
            required_height = rows * self.node_height + (rows - 1) * compact_v_spacing if rows > 1 else self.node_height
            canvas_height = max(6, self.margin_y * 2 + required_height * 1.1)  # 仅10%额外空间
            
        else:  # top-bottom
            # 垂直布局：紧凑计算所需高度
            # 计算实际需要的宽度
            required_width = cols * self.node_width + (cols - 1) * compact_h_spacing if cols > 1 else self.node_width
            canvas_width = max(6, self.margin_x * 2 + required_width * 1.1)  # 仅10%额外空间
            
            # 计算实际需要的高度
            required_height = rows * self.node_height + (rows - 1) * compact_v_spacing if rows > 1 else self.node_height
            canvas_height = max(8, self.margin_y * 2 + required_height * 1.1)  # 仅10%额外空间
        
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
            # 水平布局：优先横向排列，确保间距均匀
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # 计算节点间的实际间距，去除间距因子的干扰
            if cols > 1:
                # 计算每个节点占用的总宽度（包括节点和间距）
                total_node_width = cols * self.node_width
                remaining_width = available_width - total_node_width
                x_spacing_gap = remaining_width / (cols - 1) if cols > 1 else 0  # 节点间纯间距
                x_spacing = self.node_width + x_spacing_gap  # 节点中心到中心的距离
            else:
                x_spacing = available_width
                
            if rows > 1:
                # 计算每个节点占用的总高度（包括节点和间距）
                total_node_height = rows * self.node_height
                remaining_height = available_height - total_node_height
                y_spacing_gap = remaining_height / (rows - 1) if rows > 1 else 0  # 节点间纯间距
                y_spacing = self.node_height + y_spacing_gap  # 节点中心到中心的距离
            else:
                y_spacing = available_height
            
            # 确保最小间距，防止节点重叠
            min_x_spacing = self.node_width + 0.8  # 最小水平间距
            min_y_spacing = self.node_height + 0.8  # 最小垂直间距
            x_spacing = max(x_spacing, min_x_spacing)
            y_spacing = max(y_spacing, min_y_spacing)
            
            # 按行优先的顺序计算节点位置
            for i, node in enumerate(nodes):
                row = i // cols  # 当前行号（从0开始）
                col = i % cols   # 当前列号（从0开始）
                
                # 计算节点中心位置
                x = self.margin_x + self.node_width/2 + col * x_spacing
                y = canvas_height - self.margin_y - self.node_height/2 - row * y_spacing
                
                # 边界安全检查：确保节点不会超出画布边界
                x = max(self.margin_x + self.node_width/2, 
                       min(canvas_width - self.margin_x - self.node_width/2, x))
                y = max(self.margin_y + self.node_height/2, 
                       min(canvas_height - self.margin_y - self.node_height/2, y))
                
                positions[node['id']] = (x, y)
        
        else:  # top-bottom
            # 垂直布局：优先纵向排列，确保间距均匀
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # 计算节点间的实际间距，去除间距因子的干扰
            if cols > 1:
                # 计算每个节点占用的总宽度（包括节点和间距）
                total_node_width = cols * self.node_width
                remaining_width = available_width - total_node_width
                x_spacing_gap = remaining_width / (cols - 1) if cols > 1 else 0  # 节点间纯间距
                x_spacing = self.node_width + x_spacing_gap  # 节点中心到中心的距离
            else:
                x_spacing = available_width
                
            if rows > 1:
                # 计算每个节点占用的总高度（包括节点和间距）
                total_node_height = rows * self.node_height
                remaining_height = available_height - total_node_height
                y_spacing_gap = remaining_height / (rows - 1) if rows > 1 else 0  # 节点间纯间距
                y_spacing = self.node_height + y_spacing_gap  # 节点中心到中心的距离
            else:
                y_spacing = available_height
            
            # 确保最小间距，防止节点重叠
            min_x_spacing = self.node_width + 0.8  # 最小水平间距
            min_y_spacing = self.node_height + 0.8  # 最小垂直间距
            x_spacing = max(x_spacing, min_x_spacing)
            y_spacing = max(y_spacing, min_y_spacing)
            
            # 按列优先的顺序计算节点位置
            for i, node in enumerate(nodes):
                col = i // rows  # 当前列号（从0开始）
                row = i % rows   # 当前行号（从0开始）
                
                # 计算节点中心位置
                x = self.margin_x + self.node_width/2 + col * x_spacing
                y = canvas_height - self.margin_y - self.node_height/2 - row * y_spacing
                
                # 边界安全检查：确保节点不会超出画布边界
                x = max(self.margin_x + self.node_width/2, 
                       min(canvas_width - self.margin_x - self.node_width/2, x))
                y = max(self.margin_y + self.node_height/2, 
                       min(canvas_height - self.margin_y - self.node_height/2, y))
                
                positions[node['id']] = (x, y)
        
        return positions
    
    def _generate_compact_flowchart(self, nodes: List[Dict], connections: List[Dict], layout: str, input_type: str) -> str:
        """Generate compact flowchart with optimized space usage and save as PNG file"""
        if not nodes:
            raise ValueError("No nodes to generate flowchart")
        
        # Calculate adaptive grid dimensions and canvas size based on structure / 根据结构计算自适应网格尺寸和画布大小
        structure_analysis = self._analyze_flowchart_structure(nodes, connections)
        
        if structure_analysis['has_branches']:
            # 分支场景使用紧凑但防重叠的画布尺寸
            base_multiplier = 1.8  # 大幅减小基础倍数，减小画布尺寸
            
            # 根据分支复杂度适度调整
            if structure_analysis['has_complex_branches']:
                complexity_factor = 1.2  # 复杂分支适度增加
            else:
                complexity_factor = 1.1  # 简单分支小幅增加
            
            # 针对组织架构图等树形结构优化：更严格控制画布尺寸
            if structure_analysis['max_branches'] > 2:  # 多分支场景
                tree_factor = 1.25  # 严格限制树形结构的画布尺寸
                # 特别针对超多分支的组织架构图
                if structure_analysis['max_branches'] > 4:
                    tree_factor = 1.15  # 超多分支时更加紧凑
            else:
                tree_factor = 1.0
            
            # 更紧凑的节点数量因子
            node_count_factor = min(1.2, 1.0 + (len(nodes) / 60.0))  # 限制最大1.2倍，每60个节点增加20%
            
            # 计算紧凑的基础画布尺寸
            base_canvas_size = len(nodes) * base_multiplier * complexity_factor * tree_factor
            
            # 根据布局方向调整，更紧凑
            if layout == "left-right":
                canvas_width = max(12, base_canvas_size * node_count_factor)  # 减小最小尺寸
                canvas_height = max(8, base_canvas_size * 0.6)  # 更紧凑的垂直空间
            else:  # top-bottom
                canvas_width = max(8, base_canvas_size * 0.6)  # 更紧凑的水平空间
                canvas_height = max(12, base_canvas_size * node_count_factor)  # 减小最小尺寸
            
            # 更严格的尺寸限制：防止画布过大但确保足够空间
            max_dimension = 60  # 进一步减小最大尺寸限制
            canvas_width = min(canvas_width, max_dimension)
            canvas_height = min(canvas_height, max_dimension)
            
            rows, cols = 1, 1  # 自由布局不使用网格
        else:
            # For linear scenarios, use normal grid calculation / 线性场景使用正常网格计算
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
        
        # Calculate adaptive positions using structure-aware layout / 使用结构感知布局计算自适应位置
        structure_analysis = self._analyze_flowchart_structure(nodes, connections)
        if structure_analysis['has_branches']:
            # Use free layout for branching scenarios / 分支场景使用自由布局
            print(f"[DEBUG] Using FREE LAYOUT for branching flowchart (branches: {len(structure_analysis['branch_nodes'])})")
            positions = self._calculate_free_layout_positions(nodes, connections, layout, canvas_width, canvas_height)
        else:
            # Use grid layout with L-turn connections for linear scenarios / 线性场景使用网格布局+L转弯连接
            print(f"[DEBUG] Using GRID LAYOUT with L-turn connections for linear flowchart")
            positions = self._calculate_branch_aware_positions(nodes, connections, layout, canvas_width, canvas_height, rows, cols)
        
        # Draw nodes / 绘制节点
        for node in nodes:
            self._draw_compact_node(ax, node, positions[node['id']])
        
        # Draw intelligent connections / 绘制智能连接
        for connection in connections:
            self._draw_intelligent_connection(ax, connection, positions, layout, nodes, connections)
        
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
            # 水平布局：优先横向排列，确保间距均匀
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # 计算节点间的实际间距
            if cols > 1:
                total_node_width = cols * self.node_width
                remaining_width = available_width - total_node_width
                x_spacing_gap = remaining_width / (cols - 1) if cols > 1 else 0
                x_spacing = self.node_width + x_spacing_gap
            else:
                x_spacing = available_width
                
            if rows > 1:
                total_node_height = rows * self.node_height
                remaining_height = available_height - total_node_height
                y_spacing_gap = remaining_height / (rows - 1) if rows > 1 else 0
                y_spacing = self.node_height + y_spacing_gap
            else:
                y_spacing = available_height
            
            # 确保最小间距
            min_x_spacing = self.node_width + 0.8
            min_y_spacing = self.node_height + 0.8
            x_spacing = max(x_spacing, min_x_spacing)
            y_spacing = max(y_spacing, min_y_spacing)
            
            # 按行优先计算节点位置
            for i, node in enumerate(nodes):
                row = i // cols  # 当前行
                col = i % cols   # 当前列
                
                # 计算位置
                x = self.margin_x + self.node_width/2 + col * x_spacing
                y = canvas_height - self.margin_y - self.node_height/2 - row * y_spacing
                
                positions[node['id']] = (x, y)
        
        else:  # top-bottom
            # 垂直布局：优先纵向排列，确保间距均匀
            available_width = canvas_width - 2 * self.margin_x
            available_height = canvas_height - 2 * self.margin_y
            
            # 计算节点间的实际间距
            if cols > 1:
                total_node_width = cols * self.node_width
                remaining_width = available_width - total_node_width
                x_spacing_gap = remaining_width / (cols - 1) if cols > 1 else 0
                x_spacing = self.node_width + x_spacing_gap
            else:
                x_spacing = available_width
                
            if rows > 1:
                total_node_height = rows * self.node_height
                remaining_height = available_height - total_node_height
                y_spacing_gap = remaining_height / (rows - 1) if rows > 1 else 0
                y_spacing = self.node_height + y_spacing_gap
            else:
                y_spacing = available_height
            
            # 确保最小间距
            min_x_spacing = self.node_width + 0.8
            min_y_spacing = self.node_height + 0.8
            x_spacing = max(x_spacing, min_x_spacing)
            y_spacing = max(y_spacing, min_y_spacing)
            
            # 按列优先计算节点位置
            for i, node in enumerate(nodes):
                col = i // rows  # 当前列
                row = i % rows   # 当前行
                
                # 计算位置
                x = self.margin_x + self.node_width/2 + col * x_spacing
                y = canvas_height - self.margin_y - self.node_height/2 - row * y_spacing
                
                positions[node['id']] = (x, y)
        
        return positions
    
    def _calculate_branch_aware_positions(self, nodes: List[Dict], connections: List[Dict], layout: str, canvas_width: float, canvas_height: float, rows: int, cols: int) -> Dict[str, Tuple[float, float]]:
        """Calculate branch-aware node positions to prevent overlap in branching scenarios / 计算分支感知的节点位置以防止分支场景中的重叠"""
        positions = {}
        node_count = len(nodes)
        text_analysis = self._analyze_text_characteristics(nodes)
        structure_analysis = self._analyze_flowchart_structure(nodes, connections)
        
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
        
        # Apply additional spacing for branching scenarios / 为分支场景应用额外间距
        if structure_analysis['has_branches']:
            branch_spacing_factor = 1.5 if structure_analysis['has_complex_branches'] else 1.3
            h_spacing_factor *= branch_spacing_factor
            v_spacing_factor *= branch_spacing_factor
        
        if layout == "left-right":
            # Branch-aware multi-row horizontal layout / 分支感知多行水平布局
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
            
            # Position nodes with branch-aware adjustments / 分支感知的节点定位
            for i, node in enumerate(nodes):
                row = i // cols
                col = i % cols
                
                # Basic position / 基础位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                # 边界安全检查：确保节点不会超出画布边界
                x = max(self.margin_x + self.node_width/2, 
                       min(canvas_width - self.margin_x - self.node_width/2, x))
                y = max(self.margin_y + self.node_height/2, 
                       min(canvas_height - self.margin_y - self.node_height/2, y))
                
                # Fine-tune position for branch nodes / 为分支节点微调位置
                node_id = node['id']
                if node_id in structure_analysis['branch_nodes']:
                    # Give branch nodes extra horizontal space / 为分支节点提供额外水平空间
                    x += x_spacing * 0.1
                elif node_id in structure_analysis['merge_nodes']:
                    # Give merge nodes extra space too / 为合并节点也提供额外空间
                    x -= x_spacing * 0.1
                
                # Fine-tune position based on text length / 根据文本长度微调位置
                text_length = len(node.get('label', ''))
                if text_length > text_analysis["avg_text_length"] * 1.5:
                    # Give more space to long text nodes / 为长文本节点提供更多空间
                    if col < cols - 1:  # Not the last column
                        x += x_spacing * 0.1
                
                positions[node['id']] = (x, y)
        
        else:  # top-bottom
            # Branch-aware multi-column vertical layout / 分支感知多列垂直布局
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
            
            # Position nodes with branch-aware adjustments / 分支感知的节点定位
            for i, node in enumerate(nodes):
                col = i // rows
                row = i % rows
                
                # Basic position / 基础位置
                x = self.margin_x + x_spacing * (col + 0.5)
                y = canvas_height - self.margin_y - y_spacing * (row + 0.5)
                
                # 边界安全检查：确保节点不会超出画布边界
                x = max(self.margin_x + self.node_width/2, 
                       min(canvas_width - self.margin_x - self.node_width/2, x))
                y = max(self.margin_y + self.node_height/2, 
                       min(canvas_height - self.margin_y - self.node_height/2, y))
                
                # Fine-tune position for branch nodes / 为分支节点微调位置
                node_id = node['id']
                if node_id in structure_analysis['branch_nodes']:
                    # Give branch nodes extra vertical space / 为分支节点提供额外垂直空间
                    y += y_spacing * 0.1
                elif node_id in structure_analysis['merge_nodes']:
                    # Give merge nodes extra space too / 为合并节点也提供额外空间
                    y -= y_spacing * 0.1
                
                # Fine-tune position based on text length / 根据文本长度微调位置
                text_length = len(node.get('label', ''))
                if text_length > text_analysis["avg_text_length"] * 1.5:
                    # Give more space to long text nodes / 为长文本节点提供更多空间
                    if row < rows - 1:  # Not the last row
                        y -= y_spacing * 0.1
                
                # 最终边界检查（在微调后）
                x = max(self.margin_x + self.node_width/2, 
                       min(canvas_width - self.margin_x - self.node_width/2, x))
                y = max(self.margin_y + self.node_height/2, 
                       min(canvas_height - self.margin_y - self.node_height/2, y))
                
                positions[node['id']] = (x, y)
        
        return positions
    
    def _calculate_free_layout_positions(self, nodes: List[Dict], connections: List[Dict], layout: str, canvas_width: float, canvas_height: float) -> Dict[str, Tuple[float, float]]:
        """Calculate free layout positions for branching flowcharts / 计算分支流程图的自由布局位置"""
        positions = {}
        structure_analysis = self._analyze_flowchart_structure(nodes, connections)
        
        # Build node hierarchy based on connections / 根据连接构建节点层次结构
        node_levels = self._build_node_hierarchy(nodes, connections)
        max_level = max(node_levels.values()) if node_levels else 0
        
        # Group nodes by level / 按层级分组节点
        levels = {}
        for node_id, level in node_levels.items():
            if level not in levels:
                levels[level] = []
            levels[level].append(node_id)
        
        # 计算紧凑的边距，确保节点不会被裁切但节省空间
        # 更紧凑的边距百分比，为节点留出更多可用空间
        margin_x = max(self.node_width/2 + 0.2, canvas_width * 0.03)  # 3%边距或节点半宽+小边距，取较大者
        margin_y = max(self.node_height/2 + 0.2, canvas_height * 0.03)  # 3%边距或节点半高+小边距，取较大者
        available_width = canvas_width - 2 * margin_x
        available_height = canvas_height - 2 * margin_y
        
        if layout == "left-right":
            # Free horizontal layout / 自由水平布局
            level_width = available_width / (max_level + 1) if max_level > 0 else available_width
            
            for level, node_ids in levels.items():
                level_x = margin_x + level * level_width + level_width / 2
                
                # Handle multiple nodes at same level / 处理同一层级的多个节点
                if len(node_ids) == 1:
                    # Single node at center / 单个节点居中
                    node_id = node_ids[0]
                    y = canvas_height / 2
                    positions[node_id] = (level_x, y)
                else:
                    # Multiple nodes distributed vertically / 多个节点垂直分布
                    self._distribute_nodes_vertically(node_ids, positions, level_x, available_height, margin_y, canvas_height, structure_analysis)
        
        else:  # top-bottom
            # Free vertical layout / 自由垂直布局
            level_height = available_height / (max_level + 1) if max_level > 0 else available_height
            
            for level, node_ids in levels.items():
                level_y = canvas_height - margin_y - level * level_height - level_height / 2
                
                # Handle multiple nodes at same level / 处理同一层级的多个节点
                if len(node_ids) == 1:
                    # Single node at center / 单个节点居中
                    node_id = node_ids[0]
                    x = canvas_width / 2
                    positions[node_id] = (x, level_y)
                else:
                    # Multiple nodes distributed horizontally / 多个节点水平分布
                    self._distribute_nodes_horizontally(node_ids, positions, level_y, available_width, margin_x, canvas_width, structure_analysis)
        
        return positions
    
    def _build_node_hierarchy(self, nodes: List[Dict], connections: List[Dict]) -> Dict[str, int]:
        """Build node hierarchy levels based on flow connections / 根据流连接构建节点层次级别"""
        node_levels = {}
        
        # Find start nodes (no incoming connections) / 找到起始节点（无入向连接）
        incoming_counts = {}
        outgoing_map = {}
        
        for node in nodes:
            incoming_counts[node['id']] = 0
            outgoing_map[node['id']] = []
        
        for conn in connections:
            incoming_counts[conn['to']] += 1
            outgoing_map[conn['from']].append(conn['to'])
        
        # Start nodes have no incoming connections / 起始节点没有入向连接
        start_nodes = [node_id for node_id, count in incoming_counts.items() if count == 0]
        
        # BFS to assign levels / 使用BFS分配层级
        queue = [(node_id, 0) for node_id in start_nodes]
        visited = set()
        
        while queue:
            node_id, level = queue.pop(0)
            
            if node_id in visited:
                continue
                
            visited.add(node_id)
            node_levels[node_id] = level
            
            # Add children to queue / 将子节点添加到队列
            for child_id in outgoing_map[node_id]:
                if child_id not in visited:
                    queue.append((child_id, level + 1))
        
        # Handle any unconnected nodes / 处理任何未连接的节点
        for node in nodes:
            if node['id'] not in node_levels:
                node_levels[node['id']] = 0
        
        return node_levels
    
    def _distribute_nodes_vertically(self, node_ids: List[str], positions: Dict, x: float, available_height: float, margin_y: float, canvas_height: float, structure_analysis: Dict):
        """Distribute nodes vertically with enhanced branch-aware spacing / 增强分支感知的垂直分布节点"""
        node_count = len(node_ids)
        
        # 增强防重叠机制：特别针对组织架构等多分支场景
        # 根据分支复杂度动态调整间距因子
        base_spacing_factor = 2.4  # 基础间距因子大幅提升
        
        # 检测是否包含分支节点
        has_branch_nodes = any(node_id in structure_analysis['branch_nodes'] for node_id in node_ids)
        has_decision_nodes = any(node_id in structure_analysis.get('decision_nodes', []) for node_id in node_ids)
        
        # 根据节点类型调整间距
        if has_branch_nodes or has_decision_nodes:
            # 分支/决策节点场景：需要更多间距防止重叠
            spacing_factor = base_spacing_factor * 1.5  # 分支场景增加50%间距
            
            # 组织架构等复杂树形结构进一步增强
            if structure_analysis.get('max_branches', 0) > 3:
                spacing_factor *= 1.3  # 复杂多分支再增加30%
        else:
            # 普通节点：使用标准间距
            spacing_factor = base_spacing_factor
        
        # 计算有效空间，留出更多安全边距
        effective_height = available_height * 0.85  # 使用85%防止边缘溢出，留15%空间
        
        # 计算增强的最小安全间距（绝对防重叠）
        min_safe_spacing = self.node_height + 1.2  # 节点高度 + 更大的安全空隙
        node_spacing = max(min_safe_spacing, (effective_height / max(1, node_count - 1)) if node_count > 1 else 0)
        node_spacing *= spacing_factor
        
        # 确保最小间距不会太大导致溢出
        max_allowed_spacing = effective_height / max(1, node_count - 1) if node_count > 1 else node_spacing
        if node_spacing > max_allowed_spacing * 2:  # 防止间距过大
            node_spacing = max_allowed_spacing * 1.8  # 限制为合理倍数
        
        # 垂直居中组
        total_height = (node_count - 1) * node_spacing if node_count > 1 else 0
        start_y = canvas_height / 2 + total_height / 2
        
        for i, node_id in enumerate(node_ids):
            y = start_y - i * node_spacing
            # 增强的边界检查：确保节点完全在画布内，不会被裁切
            safe_margin_y = margin_y + self.node_height/2 + 0.5  # 增强安全边距
            max_y = canvas_height - safe_margin_y
            min_y = safe_margin_y
            
            # 边界调整：如果超出范围，重新分布所有节点
            if y > max_y or y < min_y:
                # 重新计算更紧凑但安全的间距
                safe_total_height = canvas_height - 2 * safe_margin_y
                safe_spacing = safe_total_height / max(1, node_count - 1) if node_count > 1 else 0
                safe_spacing = max(min_safe_spacing, safe_spacing)
                
                # 重新分布所有节点
                safe_start_y = canvas_height - safe_margin_y - (node_count - 1) * safe_spacing / 2
                y = safe_start_y - i * safe_spacing
                y = max(min_y, min(max_y, y))  # 最终边界保护
                
            positions[node_id] = (x, y)
    
    def _distribute_nodes_horizontally(self, node_ids: List[str], positions: Dict, y: float, available_width: float, margin_x: float, canvas_width: float, structure_analysis: Dict):
        """Distribute nodes horizontally with enhanced branch-aware spacing / 增强分支感知的水平分布节点"""
        node_count = len(node_ids)
        
        # 增强防重叠机制：特别针对组织架构等多分支场景
        # 根据分支复杂度动态调整间距因子
        base_spacing_factor = 2.4  # 基础间距因子大幅提升
        
        # 检测是否包含分支节点
        has_branch_nodes = any(node_id in structure_analysis['branch_nodes'] for node_id in node_ids)
        has_decision_nodes = any(node_id in structure_analysis.get('decision_nodes', []) for node_id in node_ids)
        
        # 根据节点类型调整间距
        if has_branch_nodes or has_decision_nodes:
            # 分支/决策节点场景：需要更多间距防止重叠
            spacing_factor = base_spacing_factor * 1.5  # 分支场景增加50%间距
            
            # 组织架构等复杂树形结构进一步增强
            if structure_analysis.get('max_branches', 0) > 3:
                spacing_factor *= 1.3  # 复杂多分支再增加30%
        else:
            # 普通节点：使用标准间距
            spacing_factor = base_spacing_factor
        
        # 计算有效空间，留出更多安全边距
        effective_width = available_width * 0.85  # 使用85%防止边缘溢出，留15%空间
        
        # 计算增强的最小安全间距（绝对防重叠）
        min_safe_spacing = self.node_width + 1.2  # 节点宽度 + 更大的安全空隙
        node_spacing = max(min_safe_spacing, (effective_width / max(1, node_count - 1)) if node_count > 1 else 0)
        node_spacing *= spacing_factor
        
        # 确保最小间距不会太大导致溢出
        max_allowed_spacing = effective_width / max(1, node_count - 1) if node_count > 1 else node_spacing
        if node_spacing > max_allowed_spacing * 2:  # 防止间距过大
            node_spacing = max_allowed_spacing * 1.8  # 限制为合理倍数
        
        # 水平居中组
        total_width = (node_count - 1) * node_spacing if node_count > 1 else 0
        start_x = margin_x + available_width / 2 - total_width / 2
        
        for i, node_id in enumerate(node_ids):
            x = start_x + i * node_spacing
            # 增强的边界检查：确保节点完全在画布内，不会被裁切
            safe_margin_x = margin_x + self.node_width/2 + 0.5  # 增强安全边距
            max_x = canvas_width - safe_margin_x
            min_x = safe_margin_x
            
            # 边界调整：如果超出范围，重新分布所有节点
            if x > max_x or x < min_x:
                # 重新计算更紧凑但安全的间距
                safe_total_width = canvas_width - 2 * safe_margin_x
                safe_spacing = safe_total_width / max(1, node_count - 1) if node_count > 1 else 0
                safe_spacing = max(min_safe_spacing, safe_spacing)
                
                # 重新分布所有节点
                safe_start_x = margin_x + safe_margin_x + (node_count - 1) * safe_spacing / 2
                x = safe_start_x - i * safe_spacing
                x = max(min_x, min(max_x, x))  # 最终边界保护
                
            positions[node_id] = (x, y)

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
        
        # 优化文本处理：不截断，允许超出框体
        # 但为太长的文本进行智能换行
        display_label = self._format_text_for_display(label)
        
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
                                                 '#00000040', '#00000040', alpha=0.3, node=node)
            ax.add_patch(shadow_patch)
        
        # Create main node patch / 创建主节点补丁
        node_patch = self._create_node_patch(x, y, shape, node_type, color, border_color, node=node)
        
        # Add gradient effect if enabled / 如果启用渐变效果
        if self.gradient_enabled:
            node_patch = self._apply_gradient_effect(node_patch, color)
        
        ax.add_patch(node_patch)
        
        # 增强文本渲染：支持多行和自适应字体大小
        self._draw_enhanced_text(ax, x, y, display_label, text_color)
        
    def _format_text_for_display(self, text: str) -> str:
        """
        格式化文本以优化显示，支持智能换行和超出框显示，特别优化英文文本
        Format text for optimized display with intelligent line breaks, especially for English text
        """
        if not text:
            return ''
        
        # 检测是否为英文文本
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128 or c.isspace())
        is_english = english_chars / max(1, len(text)) > 0.6
        
        # 英文文本和中文文本使用不同的阈值
        if is_english:
            short_threshold = 15  # 英文短文本阈值
            medium_threshold = 35  # 英文中等文本阈值
            long_threshold = 70   # 英文长文本阈值
        else:
            short_threshold = 10  # 中文短文本阈值
            medium_threshold = 20 # 中文中等文本阈值
            long_threshold = 40   # 中文长文本阈值
            
        # 如果文本较短，直接返回
        if len(text) <= short_threshold:
            return text
            
        # 对于中等长度文本，尝试智能换行
        if len(text) <= medium_threshold:
            if is_english:
                # 英文文本：在空格或连字符处分行
                return self._format_english_text_medium(text)
            else:
                # 中文文本：在标点符号处分行
                return self._format_chinese_text_medium(text)
        
        # 对于较长文本，进行多行换行
        if len(text) <= long_threshold:
            if is_english:
                return self._format_english_text_long(text)
            else:
                return self._format_chinese_text_long(text)
        
        # 对于超长文本，截取但保留更多内容
        if is_english:
            return text[:60] + '...'
        else:
            return text[:35] + '...'
    
    def _format_english_text_medium(self, text: str) -> str:
        """格式化中等长度的英文文本"""
        # 查找合适的分割位置（空格、连字符、标点符号等）
        mid_point = len(text) // 2
        
        # 先在附近寻找空格
        for i in range(mid_point - 3, mid_point + 8):
            if i > 0 and i < len(text) and text[i] == ' ':
                return text[:i] + '\n' + text[i+1:]
        
        # 再在附近寻找连字符或标点
        for i in range(mid_point - 3, mid_point + 8):
            if i > 0 and i < len(text) and text[i] in '-.,;:':
                return text[:i+1] + '\n' + text[i+1:]
        
        # 如果没有找到合适的分割点，在中间分割
        return text[:mid_point] + '\n' + text[mid_point:]
    
    def _format_chinese_text_medium(self, text: str) -> str:
        """格式化中等长度的中文文本"""
        # 查找合适的换行位置（空格、标点符号等）
        mid_point = len(text) // 2
        for i in range(mid_point - 2, mid_point + 3):
            if i > 0 and i < len(text) and text[i] in ' 、。，：；！？':
                return text[:i+1] + '\n' + text[i+1:]
        
        # 如果没有找到合适的分割点，在中间分割
        return text[:mid_point] + '\n' + text[mid_point:]
    
    def _format_english_text_long(self, text: str) -> str:
        """格式化长英文文本"""
        lines = []
        words = text.split()
        current_line = ''
        max_chars_per_line = 20  # 英文每行最大字符数
        
        for word in words:
            # 检查添加这个单词后是否超过限制
            test_line = current_line + (' ' if current_line else '') + word
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 最多3行，多余的用省略号
        if len(lines) > 3:
            lines = lines[:3]
            if len(lines[-1]) > 15:
                lines[-1] = lines[-1][:15] + '...'
            else:
                lines[-1] += '...'
        
        return '\n'.join(lines)
    
    def _format_chinese_text_long(self, text: str) -> str:
        """格式化长中文文本"""
        lines = []
        current_line = ''
        chars_per_line = 15  # 中文每行大约15个字符
        
        words = text.replace('，', '，|').replace('。', '。|').replace('；', '；|').replace('：', '：|').split('|')
        
        for word in words:
            if len(current_line + word) <= chars_per_line:
                current_line += word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 最多3行，多余的用省略号
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = lines[-1][:12] + '...'
        
        return '\n'.join(lines)
    
    def _draw_enhanced_text(self, ax, x: float, y: float, text: str, color: str):
        """
        增强文本渲染，支持多行、自适应字体大小和超出框显示，特别优化英文文本
        Enhanced text rendering with special optimization for English text
        """
        if not text:
            return
        
        # 检测是否为英文文本
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128 or c.isspace())
        is_english = english_chars / max(1, len(text)) > 0.6
            
        # 根据文本长度和行数调整字体大小
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        line_count = len(lines)
        
        # 英文和中文使用不同的字体大小策略
        if is_english:
            # 英文文本的字体大小调整
            if line_count == 1:
                # 单行英文文本
                if max_line_length <= 10:
                    font_size = 9
                elif max_line_length <= 15:
                    font_size = 8
                elif max_line_length <= 25:
                    font_size = 7
                elif max_line_length <= 35:
                    font_size = 6
                else:
                    font_size = 5
            elif line_count == 2:
                # 两行英文文本
                if max_line_length <= 15:
                    font_size = 7
                elif max_line_length <= 25:
                    font_size = 6
                else:
                    font_size = 5
            else:
                # 三行或更多英文文本
                if max_line_length <= 12:
                    font_size = 6
                elif max_line_length <= 20:
                    font_size = 5
                else:
                    font_size = 4.5
        else:
            # 中文文本的字体大小调整（保持原有逻辑）
            if line_count == 1:
                # 单行文本
                if max_line_length <= 6:
                    font_size = 11
                elif max_line_length <= 10:
                    font_size = 10
                elif max_line_length <= 15:
                    font_size = 9
                elif max_line_length <= 20:
                    font_size = 8
                else:
                    font_size = 7
            elif line_count == 2:
                # 两行文本
                if max_line_length <= 10:
                    font_size = 9
                elif max_line_length <= 15:
                    font_size = 8
                else:
                    font_size = 7
            else:
                # 三行或更多文本
                if max_line_length <= 8:
                    font_size = 8
                elif max_line_length <= 12:
                    font_size = 7
                else:
                    font_size = 6
        
        # 确保字体大小不会太小
        font_size = max(4.5, font_size)
        
        # 调整行间距，多行文本时更紧凑
        if line_count <= 2:
            linespacing = 1.0
        else:
            linespacing = 0.8
        
        # 绘制文本，完全允许超出节点边界
        # 使用超粗字体组合：heavy + fontstretch="ultra-expanded"
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=font_size, weight='heavy',  # 使用最粗的字体设置
               fontproperties=self.chinese_font,
               color=color, zorder=10,
               linespacing=linespacing,
               clip_on=False,      # 允许超出边界
               bbox=dict(boxstyle="round,pad=0.15", facecolor=color, alpha=0.1, edgecolor='none'),  # 添加轻微背景增强可读性
               path_effects=[PathEffects.withStroke(linewidth=2, foreground='white', alpha=0.3)]) # 添加描边效果增强粗细
    
    def _create_node_patch(self, x: float, y: float, shape: str, node_type: str, 
                          fill_color: str, border_color: str, alpha: float = 1.0, node: Optional[Dict] = None):
        """
        Create a node patch with specified shape and colors
        创建指定形状和颜色的节点补丁
        """
        # 获取动态节点尺寸
        if node:
            width, height = self._get_node_dimensions(node)
        else:
            width, height = self.node_width, self.node_height
        
        if shape == 'diamond' or node_type == 'decision':
            # Diamond shape for decision nodes / 决策节点使用菱形
            diamond_width, diamond_height = width * 0.9, height * 0.9
            # Create diamond using polygon
            diamond_points = [
                [x, y + diamond_height/2],      # Top
                [x + diamond_width/2, y],       # Right
                [x, y - diamond_height/2],      # Bottom
                [x - diamond_width/2, y]        # Left
            ]
            from matplotlib.patches import Polygon
            patch = Polygon(diamond_points, facecolor=fill_color, 
                          edgecolor=border_color, linewidth=self.border_width, alpha=alpha)
        elif shape == 'round':
            # Rounded rectangle for start/end nodes / 开始/结束节点使用圆角矩形
            patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                 boxstyle="round,pad=0.1", 
                                 facecolor=fill_color, edgecolor=border_color, 
                                 linewidth=self.border_width, alpha=alpha)
        else:  # 'rect' - regular rectangle
            # Regular rectangle for process nodes / 处理节点使用矩形
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
    
    def _draw_intelligent_connection(self, ax, connection: Dict, positions: Dict[str, Tuple[float, float]], layout: str, nodes: List[Dict], connections: List[Dict]):
        """Draw intelligent connection between nodes with branch-aware routing and label-based coloring / 绘制智能节点连接，具有分支感知路由和基于标签的颜色"""
        from_id = connection['from']
        to_id = connection['to']
        connection_label = connection.get('label', '')
        
        if from_id not in positions or to_id not in positions:
            return
        
        from_pos = positions[from_id]
        to_pos = positions[to_id]
        
        # Analyze flowchart structure to detect branches / 分析流程图结构以检测分支
        structure_analysis = self._analyze_flowchart_structure(nodes, connections)
        has_branches = structure_analysis['has_branches']
        branch_nodes = structure_analysis['branch_nodes']
        
        # Calculate connection points based on node positions / 根据节点位置计算连接点
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Determine optimal connection style based on branch detection / 根据分支检测确定最佳连接样式
        dx = to_x - from_x
        dy = to_y - from_y
        
        # If there are branches, use direct connections to avoid overlap / 如果有分支，使用直接连接以避免重叠
        if has_branches and (from_id in branch_nodes or to_id in branch_nodes):
            # For branch scenarios, always use direct arrows to prevent element overlap
            # 对于分支场景，始终使用直接箭头以防止元素重叠
            self._draw_direct_arrow(ax, from_pos, to_pos, connection_label)
        else:
            # For non-branch scenarios, use layout-based routing / 对于非分支场景，使用基于布局的路由
            if layout == "left-right":
                # For left-right layout, prefer horizontal flow / 左右布局优先水平流向
                if abs(dx) > abs(dy):  # Mostly horizontal
                    # Direct horizontal connection / 直接水平连接
                    self._draw_direct_arrow(ax, from_pos, to_pos, connection_label)
                else:  # Mostly vertical (multi-row case)
                    # Draw stepped connection for better readability / 绘制阶梯连接以提高可读性
                    self._draw_stepped_connection(ax, from_pos, to_pos, "horizontal-first", connection_label)
            else:  # top-bottom
                # For top-bottom layout, prefer vertical flow / 上下布局优先垂直流向
                if abs(dy) > abs(dx):  # Mostly vertical
                    # Direct vertical connection / 直接垂直连接
                    self._draw_direct_arrow(ax, from_pos, to_pos, connection_label)
                else:  # Mostly horizontal (multi-column case)
                    # Draw stepped connection for better readability / 绘制阶梯连接以提高可读性
                    self._draw_stepped_connection(ax, from_pos, to_pos, "vertical-first", connection_label)
        
        # 如果有标签，在箭头中间绘制标签文本
        if connection_label:
            self._draw_connection_label(ax, from_pos, to_pos, connection_label)
    
    def _draw_direct_arrow(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float], connection_label: str = ''):
        """Draw a direct arrow connection with theme support and label-based coloring / 绘制带主题支持和标签颜色的直接箭头连接"""
        theme = self.get_current_theme()
        connection_color = self._get_connection_color(connection_label)
        connection_width = theme['connection_width']
        
        arrow = ConnectionPatch(from_pos, to_pos, "data", "data",
                              arrowstyle="->", shrinkA=35, shrinkB=35,
                              mutation_scale=18, fc=connection_color, ec=connection_color,
                              linewidth=connection_width, alpha=0.9)
        ax.add_patch(arrow)
    
    def _draw_stepped_connection(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float], direction: str, connection_label: str = ''):
        """Draw a stepped connection (L-shaped) with theme support and label-based coloring / 绘制带主题支持和标签颜色的阶梯连接（L形）"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Get theme colors / 获取主题颜色
        theme = self.get_current_theme()
        connection_color = self._get_connection_color(connection_label)
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
    
    def _draw_connection_label(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float], label: str):
        """
        Draw connection label at the middle of the arrow
        在箭头中间绘制连接标签
        """
        if not label:
            return
        
        # 计算标签位置（箭头中点）
        mid_x = (from_pos[0] + to_pos[0]) / 2
        mid_y = (from_pos[1] + to_pos[1]) / 2
        
        # 获取主题颜色
        theme = self.get_current_theme()
        label_color = self._get_connection_color(label)
        
        # 绘制标签背景（小圆角矩形）
        label_bg = mpatches.FancyBboxPatch(
            (mid_x - 0.25, mid_y - 0.1), 0.5, 0.2,
            boxstyle="round,pad=0.05", 
            facecolor=label_color, 
            edgecolor=label_color,
            alpha=0.9, 
            zorder=8
        )
        ax.add_patch(label_bg)
        
        # 绘制标签文本 - 进一步增强字体粗细
        ax.text(mid_x, mid_y, label, ha='center', va='center', 
               fontsize=7, weight='heavy', color='white',  # 使用最粗的字体设置
               fontproperties=self.chinese_font, zorder=9,
               path_effects=[PathEffects.withStroke(linewidth=1.5, foreground='black', alpha=0.8)]) # 添加黑色描边增强粗细
    
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
