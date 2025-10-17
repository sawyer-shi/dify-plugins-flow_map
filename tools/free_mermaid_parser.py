# -*- coding: utf-8 -*-
"""
Mermaid Syntax Parser
独立的 Mermaid 语法解析器，支持节点/边/标签/方向等常见语法。

输出结构与 MermaidFreeTool 兼容：
- 返回 (chart_type, elements)
- elements: List[Dict]
  - node: {"type":"node","id":str,"label":str,"shape":str}
  - edge: {"type":"edge","from":str,"to":str,"style":str,"label":str}
"""
import re
from typing import Tuple, List, Dict, Any


class MermaidParser:
    def parse(self, mermaid_code: str) -> Tuple[str, List[Dict[str, Any]]]:
        code = self._preprocess(mermaid_code)
        chart_type, direction = self._detect_chart_type_and_dir(code)
        nodes_map: Dict[str, Dict[str, Any]] = {}
        edges_set = set()
        edges: List[Dict[str, Any]] = []

        # 忽略第一行类型声明，只解析后续有效语句
        lines = [l for l in code.split("\n") if l.strip()]
        if lines and self._is_chart_decl_line(lines[0]):
            lines = lines[1:]

        # 解析每一行（支持链式 A-->B-->C）
        for raw in lines:
            # 跳过图表声明行
            if self._is_chart_decl_line(raw):
                continue
            line = raw.strip()
            if not line or line.startswith("%%"):
                continue
            if line.lower().startswith("subgraph") or line.lower() == "end":
                # 暂不处理子图结构，内容仍按普通语句解析
                continue

            # 判断是否是连接语句
            if self._contains_connector(line):
                # 提取边标签 - 支持两种格式：A -->|是| B 和 A --是--> B
                # 先处理 |标签| 格式
                edge_labels = re.findall(r"\|(.*?)\|", line)
                line_wo_labels = re.sub(r"\|(.*?)\|", "", line)
                
                # 再处理连接符中间的标签格式，如 A --是--> B
                # 使用正则表达式匹配连接符中间的文本
                connector_labels = re.findall(r'--([^->]+?)-->|->([^->]+?)->|--([^->]+?)--|==([^=]+?)==>', line_wo_labels)
                # 合并所有标签
                for label_match in connector_labels:
                    for label in label_match:
                        if label.strip():  # 只添加非空标签
                            edge_labels.append(label.strip())
                
                # 移除连接符中间的标签，便于后续处理
                line_wo_labels = re.sub(r'--[^->]+?-->', '-->', line_wo_labels)
                line_wo_labels = re.sub(r'->[^->]+?->', '->', line_wo_labels)
                line_wo_labels = re.sub(r'--[^->]+?--', '--', line_wo_labels)
                line_wo_labels = re.sub(r'==[^=]+?==>', '==>', line_wo_labels)
                
                parts = self._split_by_connectors(line_wo_labels)
                # parts 形如 [node, op, node, op, node]
                label_idx = 0
                for i in range(0, len(parts) - 2, 2):
                    left = parts[i].strip()
                    op = parts[i + 1]
                    right = parts[i + 2].strip()
                    
                    # 解析节点
                    left_node = self._parse_node(left)
                    right_node = self._parse_node(right)
                    
                    # 添加到节点映射
                    if left_node["id"] not in nodes_map:
                        nodes_map[left_node["id"]] = left_node
                    if right_node["id"] not in nodes_map:
                        nodes_map[right_node["id"]] = right_node
                    
                    # 解析连接样式
                    edge_style = self._parse_edge_style(op)
                    
                    # 获取边标签（如果有）
                    edge_label = edge_labels[label_idx] if label_idx < len(edge_labels) else ""
                    label_idx += 1
                    
                    # 创建边的唯一标识
                    edge_id = f"{left_node['id']}->{right_node['id']}"
                    
                    # 避免重复添加相同的边
                    if edge_id not in edges_set:
                        edges_set.add(edge_id)
                        edges.append({
                            "type": "edge",
                            "from": left_node["id"],
                            "to": right_node["id"],
                            "style": edge_style,
                            "label": edge_label
                        })
            else:
                # 可能是单独的节点定义
                node = self._parse_node(line)
                if node["id"]:
                    nodes_map[node["id"]] = node
        
        # 构建最终结果
        elements = []
        
        # 添加节点到元素列表
        for node_id, node in nodes_map.items():
            elements.append(node)
        
        # 添加边到元素列表
        for edge in edges:
            elements.append(edge)
        
        return chart_type, elements
    
    def _preprocess(self, mermaid_code: str) -> str:
        """预处理Mermaid代码，移除多余空白和注释"""
        lines = []
        for line in mermaid_code.split("\n"):
            stripped = line.strip()
            # 移除行末的分号
            if stripped.endswith(";"):
                stripped = stripped[:-1].strip()
            # 移除多余的mermaid代码标记
            if stripped.startswith("```mermaid"):
                stripped = stripped[len("```mermaid"):].strip()
            elif stripped.startswith("```"):
                stripped = stripped[len("```"):].strip()
            # 保留非空行和非注释行
            if stripped and not stripped.startswith("%%"):
                lines.append(stripped)
        return "\n".join(lines)
    
    def _detect_chart_type_and_dir(self, code: str) -> Tuple[str, str]:
        """检测图表类型和方向，仅支持流程图"""
        first_line = code.split("\n")[0].lower() if code else ""
        
        # 只支持流程图类型，任何输入都视为流程图
        chart_type = "flowchart"
        direction = "TD"  # Top to Down
        
        # 检测方向
        if "td" in first_line or "tb" in first_line:
            direction = "TD"
        elif "bt" in first_line:
            direction = "BT"
        elif "rl" in first_line:
            direction = "RL"
        elif "lr" in first_line:
            direction = "LR"
        
        return chart_type, direction
    
    def _is_chart_decl_line(self, line: str) -> bool:
        """判断是否是图表声明行"""
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in [
            "flowchart", "graph", "sequencediagram", "classdiagram", 
            "statediagram", "erdiagram", "gantt", 
            "pie", "journey"
        ])
    
    def _contains_connector(self, line: str) -> bool:
        """判断行中是否包含连接符"""
        return any(conn in line for conn in ["-->", "->", "---", "--", "-.->", "-.->", "==>", "=>"])
    
    def _split_by_connectors(self, line: str) -> List[str]:
        """按连接符分割行"""
        # 按优先级从高到低排序，避免短连接符匹配长连接符的一部分
        connectors = ["-->", "-.->", "==>", "->", "---", "--", "==>", "=>"]
        
        # 使用正则表达式分割，同时保留连接符
        pattern = "(" + "|".join(re.escape(conn) for conn in connectors) + ")"
        parts = re.split(pattern, line)
        
        # 移除空字符串
        result = [part for part in parts if part.strip()]
        
        return result
    
    def _parse_node(self, node_str: str) -> Dict[str, Any]:
        """解析节点字符串，提取ID、标签和形状"""
        node_str = node_str.strip()
        
        # 默认值
        node_id = node_str
        node_label = node_str
        node_shape = "rectangle"  # 默认形状
        
        # 匹配各种节点格式
        # A[Text] - 矩形
        match = re.match(r'^(\w+)\[(.*?)\]$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "rectangle"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A(Text) - 圆角矩形
        match = re.match(r'^(\w+)\((.*?)\)$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "rounded"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A{Text} - 菱形/决策
        match = re.match(r'^(\w+)\{(.*?)\}$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "diamond"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A>Text] - 不对称形状
        match = re.match(r'^(\w+)>(.*?)\]$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "stadium"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A((Text)) - 圆形
        match = re.match(r'^(\w+)\(\((.*?)\)\)$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "circle"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A[/Text/] - 平行四边形
        match = re.match(r'^(\w+)\/(.*?)\/$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "parallelogram"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A[\Text/] - 反向平行四边形
        match = re.match(r'^(\w+)\\\[(.*?)\\\/$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "parallelogram_alt"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A[[Text]] - 子程序/子流程
        match = re.match(r'^(\w+)\[\[(.*?)\]\]$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "subroutine"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # A[::Text] - 圆柱形
        match = re.match(r'^(\w+)\[\[(.*?)\]\]$', node_str)
        if match:
            node_id = match.group(1)
            node_label = match.group(2)
            node_shape = "cylinder"
            return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
        
        # 如果没有匹配到任何格式，使用默认值
        return {"type": "node", "id": node_id, "label": node_label, "shape": node_shape}
    
    def _parse_edge_style(self, connector: str) -> str:
        """解析连接符，返回边样式"""
        connector = connector.strip()
        
        if connector in ["-->", "->"]:
            return "arrow"
        elif connector in ["---", "--"]:
            return "line"
        elif connector in ["-.->", "-.->"]:
            return "dotted_arrow"
        elif connector in ["==>", "=>"]:
            return "thick_arrow"
        else:
            return "arrow"  # 默认样式