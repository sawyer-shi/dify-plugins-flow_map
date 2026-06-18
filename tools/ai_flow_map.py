#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Flow Map Tool

Summarizes plain user text into Mermaid flowchart syntax with a selected LLM
model, then reuses the existing local flowchart renderers.
"""

import re
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AIFlowMapTool(Tool):
    """Generate a flowchart from plain text by asking an LLM to produce Mermaid first."""

    _LAYOUT_ALIASES = {
        "tb": "top_bottom",
        "td": "top_bottom",
        "top_bottom": "top_bottom",
        "top-bottom": "top_bottom",
        "vertical": "top_bottom",
        "上下": "top_bottom",
        "上下结构": "top_bottom",
        "垂直": "top_bottom",
        "lr": "left_right",
        "left_right": "left_right",
        "left-right": "left_right",
        "horizontal": "left_right",
        "左右": "left_right",
        "左右结构": "left_right",
        "水平": "left_right",
        "free": "free",
        "smart": "free",
        "自由": "free",
        "自由结构": "free",
    }

    def _normalize_layout_mode(self, layout_mode: Any) -> str:
        value = str(layout_mode or "free").strip().lower()
        return self._LAYOUT_ALIASES.get(value, "free")

    def _get_layout_tool_class(self, layout_mode: str) -> type[Tool]:
        normalized = self._normalize_layout_mode(layout_mode)
        if normalized == "top_bottom":
            from tools.mermaid_tb import MermaidTBTool

            return MermaidTBTool
        if normalized == "left_right":
            from tools.mermaid_lr import MermaidLRTool

            return MermaidLRTool
        from tools.mermaid_free import MermaidFreeTool

        return MermaidFreeTool

    def _to_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y", "on"}
        return bool(value)

    def _clean_llm_mermaid(self, text: Any) -> str:
        mermaid = "" if text is None else str(text)
        mermaid = re.sub(r"<think>.*?</think>", "", mermaid, flags=re.DOTALL | re.IGNORECASE)
        mermaid = re.sub(r"<thought>.*?</thought>", "", mermaid, flags=re.DOTALL | re.IGNORECASE)
        mermaid = mermaid.replace("\\n", "\n").strip()

        fenced = re.search(r"```(?:mermaid)?\s*(.*?)```", mermaid, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            mermaid = fenced.group(1).strip()
        else:
            mermaid = re.sub(r"^```(?:mermaid)?\s*", "", mermaid, flags=re.IGNORECASE).strip()
            mermaid = re.sub(r"\s*```$", "", mermaid).strip()

        lines = [line.strip().rstrip(";") for line in mermaid.splitlines() if line.strip()]
        if not lines:
            return "flowchart TD\nA[Start] --> B[End]"

        # Drop common prose wrappers before the first valid Mermaid line.
        first_mermaid_index = 0
        for index, line in enumerate(lines):
            if self._looks_like_mermaid_line(line):
                first_mermaid_index = index
                break
        lines = lines[first_mermaid_index:]

        if lines and lines[0].lower().startswith("graph "):
            lines[0] = re.sub(r"^graph\b", "flowchart", lines[0], flags=re.IGNORECASE)

        if not lines[0].lower().startswith("flowchart"):
            lines.insert(0, "flowchart TD")

        return "\n".join(lines).strip()

    def _looks_like_mermaid_line(self, line: str) -> bool:
        lower = line.lower()
        if lower.startswith("flowchart ") or lower.startswith("graph "):
            return True
        return bool(re.match(r"^\w+(\[.*?\]|\{.*?\}|\(.*?\))?\s*(-->|--|->|==>)", line))

    def _build_prompt(self, text_content: str, layout_mode: str) -> str:
        normalized = self._normalize_layout_mode(layout_mode)
        direction = "TD" if normalized != "left_right" else "LR"
        layout_tips = {
            "top_bottom": "Use flowchart TD. Prefer a clear top-to-bottom process with start, process, decision, and end nodes when appropriate.",
            "left_right": "Use flowchart LR. Prefer a left-to-right process that works well for timelines, pipelines, and cross-team workflows.",
            "free": "Use flowchart TD by default. Keep the structure concise so the free renderer can optimize placement locally.",
        }
        tip = layout_tips.get(normalized, layout_tips["free"])
        return f"""
You are an expert flowchart designer.

Convert the user's text into clean Mermaid flowchart code.

Requirements:
1. Return Mermaid flowchart code only. Do not use code fences or explanations.
2. Start with `flowchart {direction}`.
3. Use short, faithful node labels in the user's source language.
4. Use decision nodes with curly braces only when the source describes a real condition.
5. Use labeled arrows for important outcomes, such as yes/no, pass/fail, approved/rejected.
6. Keep node IDs simple ASCII identifiers such as A, B, C, D1.
7. {tip}

User text:
{text_content}
""".strip()

    def _invoke_llm(self, llm_model: dict[str, Any], prompt: str) -> str:
        from dify_plugin.entities.model.message import UserPromptMessage

        messages = [UserPromptMessage(content=prompt)]
        invoke_fn = getattr(self, "invoke_model", None)
        if callable(invoke_fn):
            response = invoke_fn(model=llm_model, messages=messages)
            message = getattr(response, "message", None)
            if message is not None:
                return getattr(message, "content", "")
            return getattr(response, "content", str(response))

        session = getattr(self, "session", None)
        if session and getattr(session, "model", None):
            llm_service = getattr(session.model, "llm", None)
            if not llm_service:
                raise AttributeError("No LLM service found in current Dify session.")
            response = llm_service.invoke(model_config=llm_model, prompt_messages=messages, stream=False)
            if hasattr(response, "message"):
                return response.message.content
            return getattr(response, "content", str(response))

        raise AttributeError("No available LLM invoke interface.")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            llm_model = tool_parameters.get("model_config")
            text_content = str(tool_parameters.get("text_content") or "").strip()
            layout_mode = self._normalize_layout_mode(tool_parameters.get("layout_mode"))
            theme = str(tool_parameters.get("theme") or "modern").strip() or "modern"
            filename = str(tool_parameters.get("filename") or "").strip()
            download_mermaid = self._to_bool(tool_parameters.get("download_mermaid", False))

            if not llm_model:
                yield self.create_text_message("AI flowchart generation failed: Please select an LLM model.")
                yield self.create_json_message({"success": False, "error": "model_config is required"})
                return
            if not text_content:
                yield self.create_text_message("AI flowchart generation failed: No text content provided.")
                yield self.create_json_message({"success": False, "error": "text_content is required"})
                return

            prompt = self._build_prompt(text_content, layout_mode)
            model_output = self._invoke_llm(llm_model, prompt)
            mermaid_code = self._clean_llm_mermaid(model_output)

            yield self.create_text_message("AI Mermaid generated successfully. Rendering flowchart...")

            layout_tool_class = self._get_layout_tool_class(layout_mode)
            layout_tool = layout_tool_class(runtime=self.runtime, session=self.session)
            render_parameters = {
                "text": mermaid_code,
                "theme": theme,
                "filename": filename,
            }

            for message in layout_tool._invoke(render_parameters):
                yield message

            if download_mermaid:
                mermaid_filename = f"{filename or 'ai_flow_map'}.mmd"
                yield self.create_blob_message(
                    mermaid_code.encode("utf-8"),
                    meta={
                        "mime_type": "text/plain",
                        "filename": mermaid_filename,
                    },
                )

            yield self.create_json_message(
                {
                    "success": True,
                    "layout_mode": layout_mode,
                    "theme": theme,
                    "generated_mermaid": mermaid_code,
                    "download_mermaid": download_mermaid,
                }
            )
        except Exception as e:
            error_msg = str(e)
            yield self.create_text_message(f"AI flowchart generation failed: {error_msg}")
            yield self.create_json_message({"success": False, "error": error_msg})


def get_tool():
    return AIFlowMapTool
