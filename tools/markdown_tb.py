# -*- coding: utf-8 -*-
"""
Markdown Top-Bottom Flowchart Tool
Markdown上下布局流程图工具

Generate flowcharts from Markdown text with top-bottom layout.
从Markdown文本生成上下布局的流程图。
"""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .optimized_layout import OptimizedFlowchartGenerator


class MarkdownTBTool(Tool):
    """
    Markdown Top-Bottom Flowchart Tool
    Markdown上下布局流程图工具
    """
    
    def __init__(self, runtime, session, **kwargs):
        super().__init__(runtime=runtime, session=session)
        self.generator = OptimizedFlowchartGenerator()
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Generate top-bottom flowchart from Markdown text
        从Markdown文本生成上下布局流程图
        """
        try:
            text = tool_parameters.get('text', '')
            
            if not text.strip():
                yield self.create_json_message({
                    "success": False,
                    "error": "Input text is empty",
                    "message": "Please provide Markdown text to generate flowchart"
                })
                return
            
            # Force top-bottom layout / 强制使用上下布局
            result = self.generator.generate_from_markdown(text, "top-bottom")
            
            if result["success"]:
                # Read the generated PNG file and return as blob / 读取生成的PNG文件并返回为blob
                file_path = result["file_path"]
                with open(file_path, "rb") as f:
                    png_data = f.read()
                
                # Return PNG file as blob with metadata / 返回PNG文件作为blob带元数据
                yield self.create_blob_message(
                    png_data, 
                    meta={
                        "mime_type": "image/png",
                        "filename": f"flowchart_markdown_tb_{result.get('nodes_count', 0)}nodes.png"
                    }
                )
            else:
                # Return error as JSON / 返回错误信息
                yield self.create_json_message(result)
            
        except Exception as e:
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "message": "Failed to generate top-bottom flowchart from Markdown"
            })
