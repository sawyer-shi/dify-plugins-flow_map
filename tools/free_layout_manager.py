# -*- coding: utf-8 -*-
"""
布局管理器
Layout Manager

仅管理流程图布局算法
"""

from typing import Dict, Any, List, Tuple
from .free_flowchart_layout import FlowchartLayout


class LayoutManager:
    """
    布局管理器类
    仅支持流程图布局算法
    """
    
    def __init__(self):
        # 初始化流程图布局算法
        self.flowchart_layout = FlowchartLayout()
    
    def layout(self, elements: List[Dict[str, Any]], chart_type: str, is_chinese: bool = False) -> Dict[str, Tuple[int, int]]:
        """
        使用流程图布局算法
        
        Args:
            elements: 图表元素列表
            chart_type: 图表类型（仅支持流程图）
            is_chinese: 是否为中文布局（从右到左）
            
        Returns:
            节点位置字典
        """
        # 只支持流程图布局
        return self.flowchart_layout.layout(elements, is_chinese)
    
    def get_layout_instance(self, chart_type: str):
        """
        获取流程图布局实例
        
        Args:
            chart_type: 图表类型（仅支持流程图）
            
        Returns:
            流程图布局实例
        """
        # 只返回流程图布局实例
        return self.flowchart_layout
    
    def set_flowchart_params(self, node_width: int = None, node_height: int = None, 
                            horizontal_spacing: int = None, vertical_spacing: int = None):
        """
        设置流程图布局参数
        
        Args:
            node_width: 节点宽度
            node_height: 节点高度
            horizontal_spacing: 水平间距
            vertical_spacing: 垂直间距
        """
        self.flowchart_layout.set_layout_params(
            node_width, node_height, horizontal_spacing, vertical_spacing
        )