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
        
        self.node_colors = {
            'start': '#90EE90',    # Light green
            'process': '#87CEEB',  # Sky blue  
            'decision': '#FFB6C1', # Light pink
            'end': '#FFA07A',      # Light salmon
            'default': '#E6E6FA'   # Lavender
        }
        
        # Setup output directory / 设置输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test', 'demo_output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup Chinese font
        self.chinese_font = self._setup_chinese_font()
    
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
                
            # Enhanced pattern matching
            arrow_patterns = [
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?(?:\|(.+?)\|)?',
                r'(\w+)\s*-->\s*(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?(?:\|(.+?)\|)?',
                r'(\w+)(\[.*?\]|\{.*?\}|\(.*?\))?\s*-->\s*(\w+)(?:\|(.+?)\|)?'
            ]
            
            match_found = False
            for pattern in arrow_patterns:
                arrow_match = re.match(pattern, line)
                if arrow_match:
                    match_found = True
                    groups = arrow_match.groups()
                    
                    if len(groups) >= 3:
                        from_id = groups[0]
                        from_label = groups[1] if len(groups) > 1 else None
                        to_id = groups[2] if len(groups) > 2 else groups[1]
                        to_label = groups[3] if len(groups) > 3 else None
                        connection_label = groups[4] if len(groups) > 4 else ''
                        
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
    
    def _generate_compact_flowchart(self, nodes: List[Dict], connections: List[Dict], layout: str, input_type: str) -> str:
        """Generate compact flowchart with optimized space usage and save as PNG file"""
        if not nodes:
            raise ValueError("No nodes to generate flowchart")
        
        # Calculate optimal canvas size with intelligent multi-row/column layout / 智能多行多列布局的画布尺寸计算
        node_count = len(nodes)
        
        if layout == "left-right":
            # Intelligent horizontal layout with multi-row support / 智能水平布局支持多行
            max_nodes_per_row = 4  # 每行最多4个节点，避免过度拉伸
            rows = max(1, (node_count + max_nodes_per_row - 1) // max_nodes_per_row)  # 向上取整
            cols = min(node_count, max_nodes_per_row)
            
            canvas_width = max(6, self.margin_x * 2 + cols * self.horizontal_spacing)
            canvas_height = max(4, self.margin_y * 2 + rows * (self.node_height + self.vertical_spacing))
        else:
            # Intelligent vertical layout with multi-column support / 智能垂直布局支持多列
            max_nodes_per_col = 5  # 每列最多5个节点，避免过度拉伸
            cols = max(1, (node_count + max_nodes_per_col - 1) // max_nodes_per_col)  # 向上取整
            rows = min(node_count, max_nodes_per_col)
            
            canvas_width = max(6, self.margin_x * 2 + cols * (self.node_width + self.horizontal_spacing))
            canvas_height = max(6, self.margin_y * 2 + rows * self.vertical_spacing)
        
        # Create figure with dynamic size / 创建动态尺寸的图形
        fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
        ax.set_xlim(0, canvas_width)
        ax.set_ylim(0, canvas_height)
        ax.axis('off')
        
        # Calculate intelligent multi-row/column positions / 计算智能多行多列位置
        if layout == "left-right":
            max_nodes_per_row = 4
            rows = max(1, (node_count + max_nodes_per_row - 1) // max_nodes_per_row)
            cols = min(node_count, max_nodes_per_row)
        else:
            max_nodes_per_col = 5
            cols = max(1, (node_count + max_nodes_per_col - 1) // max_nodes_per_col)
            rows = min(node_count, max_nodes_per_col)
        
        positions = self._calculate_intelligent_positions(nodes, layout, canvas_width, canvas_height, rows, cols)
        
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
        
        # Save as PNG file / 保存为PNG文件
        plt.savefig(file_path, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.1)
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
        """Draw a compact node with optimized size"""
        x, y = position
        node_type = node.get('type', 'default')
        label = node.get('label', '')
        
        # Truncate long labels / 截断长标签
        if len(label) > 15:
            label = label[:12] + "..."
        
        color = self.node_colors.get(node_type, self.node_colors['default'])
        
        # Compact node dimensions / 紧凑节点尺寸
        if node_type == 'decision':
            width, height = self.node_width * 0.9, self.node_height * 0.9
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                               boxstyle="round,pad=0.05", 
                               facecolor=color, edgecolor='black', linewidth=1.5)
        else:
            width, height = self.node_width, self.node_height
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                               boxstyle="round,pad=0.05",
                               facecolor=color, edgecolor='black', linewidth=1.5)
        
        ax.add_patch(box)
        
        # Compact text / 紧凑文本
        ax.text(x, y, label, ha='center', va='center', fontsize=8, 
               weight='bold', wrap=True, fontproperties=self.chinese_font)
    
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
        """Draw a direct arrow connection / 绘制直接箭头连接"""
        arrow = ConnectionPatch(from_pos, to_pos, "data", "data",
                              arrowstyle="->", shrinkA=35, shrinkB=35,
                              mutation_scale=15, fc="black", ec="black",
                              linewidth=1.5)
        ax.add_patch(arrow)
    
    def _draw_stepped_connection(self, ax, from_pos: Tuple[float, float], to_pos: Tuple[float, float], direction: str):
        """Draw a stepped connection (L-shaped) for better multi-row/column readability / 绘制阶梯连接（L形）以提高多行多列可读性"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        if direction == "horizontal-first":
            # Go horizontal first, then vertical / 先水平后垂直
            mid_x = from_x + (to_x - from_x) * 0.7  # 70% of the way horizontally
            mid_y = from_y
            
            # Draw first segment (horizontal) / 绘制第一段（水平）
            ax.plot([from_x, mid_x], [from_y, mid_y], 'k-', linewidth=1.5)
            
            # Draw second segment (vertical) with arrow / 绘制第二段（垂直）带箭头
            arrow = ConnectionPatch((mid_x, mid_y), to_pos, "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=35,
                                  mutation_scale=15, fc="black", ec="black",
                                  linewidth=1.5)
            ax.add_patch(arrow)
        else:  # vertical-first
            # Go vertical first, then horizontal / 先垂直后水平
            mid_x = from_x
            mid_y = from_y + (to_y - from_y) * 0.7  # 70% of the way vertically
            
            # Draw first segment (vertical) / 绘制第一段（垂直）
            ax.plot([from_x, mid_x], [from_y, mid_y], 'k-', linewidth=1.5)
            
            # Draw second segment (horizontal) with arrow / 绘制第二段（水平）带箭头
            arrow = ConnectionPatch((mid_x, mid_y), to_pos, "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=35,
                                  mutation_scale=15, fc="black", ec="black",
                                  linewidth=1.5)
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
