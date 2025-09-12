# -*- coding: utf-8 -*-
"""
Mermaid Left-Right Flowchart Tool
Mermaid左右布局流程图工具

Generate flowcharts from Mermaid syntax with left-right layout.
从Mermaid语法生成左右布局的流程图。
"""

import os
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .optimized_layout import OptimizedFlowchartGenerator


class MermaidLRTool(Tool):
    """
    Mermaid Left-Right Flowchart Tool
    Mermaid左右布局流程图工具
    """
    
    def __init__(self, runtime, session, **kwargs):
        super().__init__(runtime=runtime, session=session)
        self.generator = OptimizedFlowchartGenerator()
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Generate left-right flowchart from Mermaid syntax
        从Mermaid语法生成左右布局流程图
        """
        try:
            text = tool_parameters.get('text', '')
            theme = tool_parameters.get('theme', 'modern')
            
            # Set theme / 设置主题
            self.generator.set_theme(theme)
            
            if not text.strip():
                yield self.create_text_message(
                    "Failed to generate flowchart: Input text is empty. Please provide Mermaid syntax to generate flowchart."
                )
                return
            
            # Force left-right layout / 强制使用左右布局
            result = self.generator.generate_from_mermaid(text, "left-right")
            
            if result["success"]:
                # Read the generated PNG file and return as blob / 读取生成的PNG文件并返回为blob
                file_path = result["file_path"]
                with open(file_path, "rb") as f:
                    png_data = f.read()
                
                # Calculate file size in MB / 计算文件大小(以MB为单位)
                file_size_bytes = len(png_data)
                file_size_mb = file_size_bytes / (1024 * 1024)
                
                # Generate success message / 生成成功消息
                success_text = f"Successfully generated left-right layout flowchart. File size: {file_size_mb:.2f}M. Contains {result.get('nodes_count', 0)} nodes and {result.get('connections_count', 0)} connections."
                
                # Return text message first / 先返回文本消息
                yield self.create_text_message(success_text)
                
                # Return PNG file as blob with metadata / 返回PNG文件作为blob带元数据
                yield self.create_blob_message(
                    png_data, 
                    meta={
                        "mime_type": "image/png",
                        "filename": f"flowchart_mermaid_lr_{result.get('nodes_count', 0)}nodes.png"
                    }
                )
            else:
                # Return error message / 返回错误信息
                error_text = f"Failed to generate left-right flowchart: {result.get('error', 'Unknown error')}"
                yield self.create_text_message(error_text)
            
        except Exception as e:
            error_text = f"Failed to generate left-right flowchart from Mermaid: {str(e)}"
            yield self.create_text_message(error_text)