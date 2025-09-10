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
        
        # Compact node dimensions / 紧凑的节点尺寸
        self.node_width = 1.4
        self.node_height = 0.6
        
        # Tight spacing / 紧密间距
        self.horizontal_spacing = 1.8  # 节点间水平间距
        self.vertical_spacing = 1.0    # 节点间垂直间距
        
        # Canvas margins / 画布边距
        self.margin_x = 0.8
        self.margin_y = 0.5
        
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
        
        # Calculate optimal canvas size based on node count / 根据节点数量计算最佳画布尺寸
        node_count = len(nodes)
        
        if layout == "left-right":
            # Compact horizontal layout / 紧凑水平布局
            canvas_width = max(6, min(12, self.margin_x * 2 + node_count * self.horizontal_spacing))
            canvas_height = max(3, 4)
        else:
            # Compact vertical layout / 紧凑垂直布局  
            canvas_width = max(4, 6)
            canvas_height = max(4, min(10, self.margin_y * 2 + node_count * self.vertical_spacing))
        
        # Create figure with dynamic size / 创建动态尺寸的图形
        fig, ax = plt.subplots(figsize=(canvas_width, canvas_height))
        ax.set_xlim(0, canvas_width)
        ax.set_ylim(0, canvas_height)
        ax.axis('off')
        
        # Calculate compact positions / 计算紧凑位置
        positions = self._calculate_compact_positions(nodes, layout, canvas_width, canvas_height)
        
        # Draw nodes / 绘制节点
        for node in nodes:
            self._draw_compact_node(ax, node, positions[node['id']])
        
        # Draw connections / 绘制连接
        for connection in connections:
            self._draw_compact_connection(ax, connection, positions)
        
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
    
    def _calculate_compact_positions(self, nodes: List[Dict], layout: str, canvas_width: float, canvas_height: float) -> Dict[str, Tuple[float, float]]:
        """Calculate compact node positions to maximize space utilization"""
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
    
    def _draw_compact_connection(self, ax, connection: Dict, positions: Dict[str, Tuple[float, float]]):
        """Draw compact connection between nodes"""
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
