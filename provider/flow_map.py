from typing import Any, List

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.ai_flow_map import AIFlowMapTool
from tools.mermaid_free import MermaidFreeTool
from tools.mermaid_lr import MermaidLRTool
from tools.mermaid_tb import MermaidTBTool


class FlowMapProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

    def _get_tools(self) -> List[Any]:
        return [AIFlowMapTool, MermaidLRTool, MermaidTBTool, MermaidFreeTool]
