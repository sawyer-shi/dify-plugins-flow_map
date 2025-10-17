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
        # 默认布局参数 - 增加间距避免重叠
        self.node_width = 140
        self.node_height = 60
        self.horizontal_spacing = 220  # 增加水平间距，避免节点重叠
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
        
        # 处理可能存在的环（将剩余节点添加到不同层级，避免重叠）
        remaining_nodes = [node["id"] for node in nodes if node["id"] not in visited]
        if remaining_nodes:
            # 对于环中的节点，尝试根据它们在图中的位置分配到不同层级
            # 简单策略：根据连接关系，将环中节点分散到不同层级
            for node_id in remaining_nodes:
                # 找到该节点连接的已访问节点
                connected_visited = [n for n in adjacency[node_id] if n in visited]
                if connected_visited:
                    # 找到连接节点中最小的层级
                    min_level = float('inf')
                    for n in connected_visited:
                        for i, level in enumerate(levels):
                            if n in level:
                                min_level = min(min_level, i)
                                break
                    
                    # 将当前节点放在最小层级的下一层
                    if min_level + 1 < len(levels):
                        levels[min_level + 1].append(node_id)
                    else:
                        levels.append([node_id])
                else:
                    # 如果没有连接到已访问节点，放在最后
                    if len(levels) > 0:
                        levels[-1].append(node_id)
                    else:
                        levels.append([node_id])
                
                visited.add(node_id)
        
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
        
        # 计算画布宽度和高度
        canvas_width = max_level_width * self.horizontal_spacing + 2 * self.margin
        canvas_height = len(levels) * self.vertical_spacing + 2 * self.margin
        
        # 为每个节点计算位置
        for level_idx, level in enumerate(levels):
            level_y = self.margin + level_idx * self.vertical_spacing
            
            # 计算该层节点的起始x坐标，使节点居中
            level_width = len(level) * self.horizontal_spacing
            start_x = (canvas_width - level_width) / 2 + self.horizontal_spacing / 2
            
            # 检查与前面层级的节点是否重叠，如果重叠则调整
            for node_idx, node_id in enumerate(level):
                if is_chinese:
                    # 中文布局：从右到左
                    node_x = canvas_width - start_x - node_idx * self.horizontal_spacing
                else:
                    # 英文布局：从左到右
                    node_x = start_x + node_idx * self.horizontal_spacing
                
                # 检查与前面层级的节点是否重叠
                overlap = True
                attempts = 0
                
                while overlap and attempts < 10:  # 最多尝试10次调整
                    overlap = False
                    # 检查与前面层级的节点是否重叠
                    for prev_level_idx in range(level_idx):
                        for prev_node_id in levels[prev_level_idx]:
                            if prev_node_id in positions:
                                prev_x, prev_y = positions[prev_node_id]
                                # 检查是否与前面层级的节点重叠
                                # 考虑节点大小，检查矩形区域是否重叠
                                node_left = node_x - self.node_width / 2
                                node_right = node_x + self.node_width / 2
                                node_top = level_y - self.node_height / 2
                                node_bottom = level_y + self.node_height / 2
                                
                                prev_left = prev_x - self.node_width / 2
                                prev_right = prev_x + self.node_width / 2
                                prev_top = prev_y - self.node_height / 2
                                prev_bottom = prev_y + self.node_height / 2
                                
                                # 检查矩形区域是否重叠
                                # 两个矩形重叠的条件是：一个矩形的左边小于另一个矩形的右边，且右边大于另一个矩形的左边
                                # 对于垂直方向，我们放宽条件，只要两个节点在同一列（水平重叠）就认为重叠
                                horizontal_overlap = (node_left < prev_right and node_right > prev_left)
                                # 垂直方向放宽条件，只要节点在同一列（水平重叠）就认为可能重叠
                                vertical_overlap = (node_top < prev_bottom and node_bottom > prev_top) or (abs(node_x - prev_x) < 10)  # x坐标相近也认为可能重叠
                                
                                if horizontal_overlap and vertical_overlap:
                                    overlap = True
                                    # 调整x坐标，向右移动
                                    node_x += self.horizontal_spacing / 2
                                    break
                        if overlap:
                            break
                    attempts += 1
                
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