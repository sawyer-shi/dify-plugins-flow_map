# -*- coding: utf-8 -*-
"""
改进的自由流程图布局算法
Improved Free Flowchart Layout Algorithm

专注于防止节点覆盖、遮盖或接触，然后再实现连线
"""

import math
from typing import Dict, Any, List, Tuple, Set


class ImprovedFlowchartLayout:
    """
    改进的自定义流程图布局类
    首先确保节点不会相互覆盖、遮盖或接触，然后再实现连线
    """
    
    def __init__(self):
        # 默认布局参数
        self.node_width = 140
        self.node_height = 60
        self.min_horizontal_spacing = 200  # 最小水平间距，确保节点不接触
        self.min_vertical_spacing = 120    # 最小垂直间距，确保节点不接触
        self.margin = 50                   # 画布边距
        
        # 判断分支（菱形）节点需要更大的空间
        self.diamond_width = 160           # 菱形节点宽度
        self.diamond_height = 80           # 菱形节点高度
        self.diamond_horizontal_spacing = 240  # 菱形节点的水平间距
        self.diamond_vertical_spacing = 160    # 菱形节点的垂直间距
        
        # 节点位置记录
        self.node_positions = {}
        self.node_rectangles = {}  # 记录每个节点的矩形区域 {node_id: (left, top, right, bottom)}
        
    def layout(self, elements: List[Dict[str, Any]], is_chinese: bool = False) -> Dict[str, Any]:
        """
        计算流程图布局
        
        Args:
            elements: 图表元素列表
            is_chinese: 是否为中文布局（从右到左）
            
        Returns:
            包含节点位置和画布大小的字典
        """
        # 提取节点和边
        nodes = [e for e in elements if e["type"] == "node"]
        edges = [e for e in elements if e["type"] == "edge"]
        
        if not nodes:
            return {"positions": {}, "canvas_width": 800, "canvas_height": 600}
        
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
        
        complexity = self._analyze_graph_complexity(nodes, edges, adjacency, in_degree)
        
        # 拓扑排序，确定节点的层级
        levels = self._topological_sort_levels(nodes, in_degree, adjacency)
        
        # 重置节点位置记录
        self.node_positions = {}
        self.node_rectangles = {}
        
        # 计算节点位置，确保节点不重叠
        positions, canvas_width, canvas_height = self._calculate_non_overlapping_positions(
            levels, is_chinese, adjacency, node_map, complexity["spacing_scale"]
        )
        
        return {
            "positions": positions,
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
            "routing_mode": "complex_orthogonal" if complexity["is_complex"] else "standard",
            "complexity_score": complexity["score"],
            "effective_horizontal_spacing": int(self.min_horizontal_spacing * complexity["spacing_scale"]),
            "effective_vertical_spacing": int(self.min_vertical_spacing * complexity["spacing_scale"]),
        }
    
    def _analyze_graph_complexity(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]],
                                  adjacency: Dict[str, List[str]], in_degree: Dict[str, int]) -> Dict[str, Any]:
        """
        评估流程图复杂度，用于自动拉开节点间距并启用复杂连线路由。
        """
        node_count = len(nodes)
        edge_count = len(edges)
        branch_count = sum(1 for targets in adjacency.values() if len(targets) > 1)
        merge_count = sum(1 for degree in in_degree.values() if degree > 1)
        density = edge_count / max(node_count, 1)
        
        score = 0.0
        if node_count > 12:
            score += (node_count - 12) / 8
        if edge_count > 16:
            score += (edge_count - 16) / 10
        score += branch_count * 0.25
        score += merge_count * 0.2
        if density > 1.15:
            score += (density - 1.15) * 1.5
        
        is_complex = node_count > 12 or edge_count > 16 or branch_count >= 4 or merge_count >= 3 or score >= 1.0
        spacing_scale = 1.0
        if is_complex:
            spacing_scale = min(2.0, 1.25 + min(score, 3.0) * 0.18)
        
        return {
            "is_complex": is_complex,
            "score": round(score, 2),
            "spacing_scale": spacing_scale,
        }
    
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
        
        # 处理可能存在的环（将剩余节点添加到不同层级）
        remaining_nodes = [node["id"] for node in nodes if node["id"] not in visited]
        if remaining_nodes:
            # 对于环中的节点，尝试根据它们在图中的位置分配到不同层级
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
    
    def _calculate_non_overlapping_positions(self, levels: List[List[str]], 
                                           is_chinese: bool, 
                                           adjacency: Dict[str, List[str]],
                                           node_map: Dict[str, Dict[str, Any]],
                                           spacing_scale: float = 1.0) -> Tuple[Dict[str, Tuple[int, int]], int, int]:
        """
        计算节点的位置，确保节点不重叠
        
        Args:
            levels: 节点层级列表
            is_chinese: 是否为中文布局（从右到左）
            adjacency: 邻接表
            node_map: 节点ID到节点信息的映射
            
        Returns:
            元组，包含节点位置字典、画布宽度和画布高度
        """
        positions = {}
        horizontal_spacing = int(self.min_horizontal_spacing * spacing_scale)
        vertical_spacing = int(self.min_vertical_spacing * spacing_scale)
        diamond_horizontal_spacing = int(self.diamond_horizontal_spacing * spacing_scale)
        diamond_vertical_spacing = int(self.diamond_vertical_spacing * spacing_scale)
        
        # 计算画布的初始大小
        max_level_width = max(len(level) for level in levels) if levels else 0
        
        # 初始画布大小计算
        initial_canvas_width = max_level_width * horizontal_spacing + 2 * self.margin
        initial_canvas_height = len(levels) * vertical_spacing + 2 * self.margin
        
        # 设置最小画布尺寸，确保不会太小
        min_canvas_width = 800
        min_canvas_height = 600
        
        canvas_width = max(initial_canvas_width, min_canvas_width)
        canvas_height = max(initial_canvas_height, min_canvas_height)
        
        # 为每个层级计算节点位置
        for level_idx, level in enumerate(levels):
            level_y = self.margin + level_idx * vertical_spacing
            
            # 计算该层节点的起始x坐标，使节点居中
            level_width = len(level) * horizontal_spacing
            start_x = (canvas_width - level_width) / 2 + horizontal_spacing / 2
            
            # 为该层每个节点计算位置
            for node_idx, node_id in enumerate(level):
                # 获取节点信息，判断是否为菱形节点
                node = node_map.get(node_id, {})
                node_shape = node.get("shape", "rectangle")
                
                # 根据节点形状调整间距
                if node_shape == "diamond":
                    # 菱形节点需要更大的空间
                    if is_chinese:
                        # 中文布局：从右到左
                        node_x = canvas_width - start_x - node_idx * diamond_horizontal_spacing
                    else:
                        # 英文布局：从左到右
                        node_x = start_x + node_idx * diamond_horizontal_spacing
                else:
                    # 普通节点
                    if is_chinese:
                        # 中文布局：从右到左
                        node_x = canvas_width - start_x - node_idx * horizontal_spacing
                    else:
                        # 英文布局：从左到右
                        node_x = start_x + node_idx * horizontal_spacing
                
                # 先记录节点的矩形区域，以便后续节点可以检查重叠
                self._record_node_rectangle(node_id, node_x, level_y, node_shape)
                
                # 检查并调整位置，确保不与已有节点重叠
                adjusted_x, adjusted_y = self._find_non_overlapping_position(
                    node_id, node_x, level_y, is_chinese, canvas_width, node_shape,
                    horizontal_spacing, vertical_spacing, diamond_horizontal_spacing, diamond_vertical_spacing
                )
                
                positions[node_id] = (int(adjusted_x), int(adjusted_y))
                
                # 更新节点的矩形区域为最终位置
                self._record_node_rectangle(node_id, adjusted_x, adjusted_y, node_shape)
        
        # 检查并调整画布大小，确保所有节点都在画布内
        canvas_width, canvas_height = self._adjust_canvas_size(positions, canvas_width, canvas_height)
        
        return positions, canvas_width, canvas_height
    
    def _adjust_canvas_size(self, positions: Dict[str, Tuple[int, int]], 
                          current_width: int, current_height: int) -> Tuple[int, int]:
        """
        根据节点位置调整画布大小，确保所有节点都在画布内
        
        Args:
            positions: 节点位置字典
            current_width: 当前画布宽度
            current_height: 当前画布高度
            
        Returns:
            调整后的画布宽度和高度
        """
        if not positions:
            return current_width, current_height
        
        # 找出所有节点的边界
        min_x = min(pos[0] for pos in positions.values())
        max_x = max(pos[0] for pos in positions.values())
        min_y = min(pos[1] for pos in positions.values())
        max_y = max(pos[1] for pos in positions.values())
        
        # 计算需要的画布大小，考虑节点尺寸和边距
        needed_width = max_x + self.node_width // 2 + self.margin
        needed_height = max_y + self.node_height // 2 + self.margin
        
        # 如果有负坐标，需要调整
        if min_x < self.margin:
            needed_width += self.margin - min_x
        if min_y < self.margin:
            needed_height += self.margin - min_y
        
        # 确保画布不小于最小尺寸
        min_canvas_width = 800
        min_canvas_height = 600
        
        adjusted_width = max(current_width, needed_width, min_canvas_width)
        adjusted_height = max(current_height, needed_height, min_canvas_height)
        
        return adjusted_width, adjusted_height
    
    def _find_non_overlapping_position(self, node_id: str, initial_x: float, initial_y: float, 
                                     is_chinese: bool, canvas_width: float, node_shape: str = "rectangle",
                                     effective_horizontal_spacing: float = None,
                                     effective_vertical_spacing: float = None,
                                     effective_diamond_horizontal_spacing: float = None,
                                     effective_diamond_vertical_spacing: float = None) -> Tuple[float, float]:
        """
        找到一个不与已有节点重叠的位置
        
        Args:
            node_id: 当前节点ID
            initial_x: 初始x坐标
            initial_y: 初始y坐标
            is_chinese: 是否为中文布局
            canvas_width: 画布宽度
            node_shape: 节点形状
            
        Returns:
            调整后的坐标 (x, y)
        """
        # 初始位置
        x, y = initial_x, initial_y
        
        # 根据节点形状设置间距
        if node_shape == "diamond":
            horizontal_spacing = effective_diamond_horizontal_spacing or self.diamond_horizontal_spacing
            vertical_spacing = effective_diamond_vertical_spacing or self.diamond_vertical_spacing
        else:
            horizontal_spacing = effective_horizontal_spacing or self.min_horizontal_spacing
            vertical_spacing = effective_vertical_spacing or self.min_vertical_spacing
        
        # 检查是否与已有节点重叠
        max_attempts = 50  # 最大尝试次数
        attempt = 0
        
        while attempt < max_attempts:
            # 计算当前节点的矩形区域
            node_rect = self._calculate_node_rectangle(x, y, node_shape)
            
            # 检查是否与已有节点重叠
            overlap = False
            for existing_id, existing_rect in self.node_rectangles.items():
                if existing_id == node_id:
                    continue
                    
                if self._rectangles_overlap(node_rect, existing_rect):
                    overlap = True
                    break
            
            if not overlap:
                # 没有重叠，返回当前位置
                return x, y
            
            # 有重叠，调整位置
            # 尝试多种调整策略
            if attempt % 4 == 0:
                # 向右/左移动
                if is_chinese:
                    x -= horizontal_spacing / 2
                else:
                    x += horizontal_spacing / 2
            elif attempt % 4 == 1:
                # 向下移动
                y += vertical_spacing / 2
            elif attempt % 4 == 2:
                # 向左/右移动
                if is_chinese:
                    x += horizontal_spacing / 2
                else:
                    x -= horizontal_spacing / 2
            else:
                # 向上移动
                y -= vertical_spacing / 2
            
            # 确保不超出画布边界
            x = max(self.margin, min(x, canvas_width - self.margin))
            y = max(self.margin, y)
            
            attempt += 1
        
        # 如果尝试了多次仍然重叠，返回最后的位置
        return x, y
    
    def _calculate_node_rectangle(self, x: float, y: float, node_shape: str = "rectangle") -> Tuple[float, float, float, float]:
        """
        计算节点的矩形区域
        
        Args:
            x: 节点中心x坐标
            y: 节点中心y坐标
            node_shape: 节点形状
            
        Returns:
            矩形区域 (left, top, right, bottom)
        """
        # 根据节点形状设置尺寸
        if node_shape == "diamond":
            width = self.diamond_width
            height = self.diamond_height
        else:
            width = self.node_width
            height = self.node_height
            
        left = x - width / 2
        right = x + width / 2
        top = y - height / 2
        bottom = y + height / 2
        
        return (left, top, right, bottom)
    
    def _record_node_rectangle(self, node_id: str, x: float, y: float, node_shape: str = "rectangle"):
        """
        记录节点的矩形区域
        
        Args:
            node_id: 节点ID
            x: 节点中心x坐标
            y: 节点中心y坐标
            node_shape: 节点形状
        """
        self.node_rectangles[node_id] = self._calculate_node_rectangle(x, y, node_shape)
    
    def _rectangles_overlap(self, rect1: Tuple[float, float, float, float], 
                          rect2: Tuple[float, float, float, float]) -> bool:
        """
        检查两个矩形是否重叠
        
        Args:
            rect1: 矩形1 (left, top, right, bottom)
            rect2: 矩形2 (left, top, right, bottom)
            
        Returns:
            是否重叠
        """
        left1, top1, right1, bottom1 = rect1
        left2, top2, right2, bottom2 = rect2
        
        # 检查是否有重叠
        # 添加一个小边距，确保节点之间有一定的间距
        margin = 10  # 额外的边距
        
        return not (right1 + margin < left2 or 
                   right2 + margin < left1 or 
                   bottom1 + margin < top2 or 
                   bottom2 + margin < top1)
    
    def set_layout_params(self, node_width: int = None, node_height: int = None, 
                         min_horizontal_spacing: int = None, min_vertical_spacing: int = None):
        """
        设置布局参数
        
        Args:
            node_width: 节点宽度
            node_height: 节点高度
            min_horizontal_spacing: 最小水平间距
            min_vertical_spacing: 最小垂直间距
        """
        if node_width is not None:
            self.node_width = node_width
        if node_height is not None:
            self.node_height = node_height
        if min_horizontal_spacing is not None:
            self.min_horizontal_spacing = min_horizontal_spacing
        if min_vertical_spacing is not None:
            self.min_vertical_spacing = min_vertical_spacing