# -*- coding: utf-8 -*-
"""
自由流程图布局算法
Free Flowchart Layout Algorithm

独立的流程图布局实现，不依赖于其他流程图工具
"""

import math
from typing import Dict, Any, List, Tuple


class FlowchartLayout:
    """
    自由流程图布局类
    实现简单的层次布局算法
    """
    
    def __init__(self):
        # 默认布局参数
        self.node_width = 140
        self.node_height = 60
        self.horizontal_spacing = 180
        self.vertical_spacing = 100
        self.margin = 50
    
    def layout(self, elements: List[Dict[str, Any]], is_chinese: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        计算流程图布局
        
        Args:
            elements: 图表元素列表
            is_chinese: 是否为中文布局（从右到左）
            
        Returns:
            节点位置字典
        """
        # 提取节点和边
        nodes = [e for e in elements if e["type"] == "node"]
        edges = [e for e in elements if e["type"] == "edge"]
        
        if not nodes:
            return {}
        
        # 构建节点ID到节点的映射
        node_map = {node["id"]: node for node in nodes}
        
        # 构建邻接表
        adjacency = {node["id"]: [] for node in nodes}
        in_degree = {node["id"]: 0 for node in nodes}
        
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            
            if from_node in node_map and to_node in node_map:
                adjacency[from_node].append(to_node)
                in_degree[to_node] += 1
        
        # 拓扑排序，确定节点的层级
        levels = self._topological_sort_levels(nodes, in_degree, adjacency)
        
        # 计算节点位置
        positions = self._calculate_positions(levels, is_chinese)
        
        return positions
    
    def _topological_sort_levels(self, nodes: List[Dict[str, Any]], 
                                in_degree: Dict[str, int], 
                                adjacency: Dict[str, List[str]]) -> List[List[str]]:
        """
        通过拓扑排序确定节点的层级
        
        Args:
            nodes: 节点列表
            in_degree: 入度字典
            adjacency: 邻接表
            
        Returns:
            节点层级列表，每个层级包含节点ID列表
        """
        # 初始化队列，包含所有入度为0的节点
        queue = [node["id"] for node in nodes if in_degree[node["id"]] == 0]
        levels = []
        visited = set()
        
        while queue:
            current_level = queue[:]
            queue = []
            levels.append(current_level)
            
            for node_id in current_level:
                if node_id in visited:
                    continue
                    
                visited.add(node_id)
                
                # 更新邻接节点的入度
                for neighbor_id in adjacency[node_id]:
                    in_degree[neighbor_id] -= 1
                    if in_degree[neighbor_id] == 0 and neighbor_id not in visited:
                        queue.append(neighbor_id)
        
        # 处理可能存在的环（将剩余节点添加到最后一个层级）
        remaining_nodes = [node["id"] for node in nodes if node["id"] not in visited]
        if remaining_nodes:
            levels.append(remaining_nodes)
        
        return levels
    
    def _calculate_positions(self, levels: List[List[str]], is_chinese: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        计算节点的位置
        
        Args:
            levels: 节点层级列表
            is_chinese: 是否为中文布局（从右到左）
            
        Returns:
            节点位置字典
        """
        positions = {}
        
        # 计算每层的最大宽度
        max_level_width = max(len(level) for level in levels) if levels else 0
        
        # 计算画布宽度
        canvas_width = max_level_width * self.horizontal_spacing + 2 * self.margin
        canvas_height = len(levels) * self.vertical_spacing + 2 * self.margin
        
        # 为每个节点计算位置
        for level_idx, level in enumerate(levels):
            level_y = self.margin + level_idx * self.vertical_spacing
            
            # 计算该层节点的起始x坐标，使节点居中
            level_width = len(level) * self.horizontal_spacing
            start_x = (canvas_width - level_width) / 2 + self.horizontal_spacing / 2
            
            for node_idx, node_id in enumerate(level):
                if is_chinese:
                    # 中文布局：从右到左
                    node_x = canvas_width - start_x - node_idx * self.horizontal_spacing
                else:
                    # 英文布局：从左到右
                    node_x = start_x + node_idx * self.horizontal_spacing
                
                positions[node_id] = (int(node_x), int(level_y))
        
        return positions
    
    def set_layout_params(self, node_width: int = None, node_height: int = None, 
                         horizontal_spacing: int = None, vertical_spacing: int = None):
        """
        设置布局参数
        
        Args:
            node_width: 节点宽度
            node_height: 节点高度
            horizontal_spacing: 水平间距
            vertical_spacing: 垂直间距
        """
        if node_width is not None:
            self.node_width = node_width
        if node_height is not None:
            self.node_height = node_height
        if horizontal_spacing is not None:
            self.horizontal_spacing = horizontal_spacing
        if vertical_spacing is not None:
            self.vertical_spacing = vertical_spacing