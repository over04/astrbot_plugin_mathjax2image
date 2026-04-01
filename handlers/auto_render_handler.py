"""
自动渲染处理器
负责在发送前拦截 LLM 文本消息，命中规则后替换成图片。
"""

import traceback
from typing import TYPE_CHECKING, Any

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
import astrbot.api.message_components as Comp

if TYPE_CHECKING:
    from ..application import AutoRenderMatcher, RenderOrchestrator


class AutoRenderHandler:
    """自动渲染处理器"""

    def __init__(self, matcher: "AutoRenderMatcher", render_orchestrator: "RenderOrchestrator"):
        self._matcher = matcher
        self._render_orchestrator = render_orchestrator
        self._pending_llm_events: set[int | str] = set()

    def mark_llm_event(self, event: AstrMessageEvent) -> None:
        """标记当前事件来源于 LLM 响应"""
        self._pending_llm_events.add(self._build_event_key(event))

    async def handle_decorating_result(self, event: AstrMessageEvent) -> None:
        """发送前拦截结果链，命中时替换成图片"""
        event_id = self._build_event_key(event)
        if event_id not in self._pending_llm_events:
            return

        try:
            result = event.get_result()
            chain = getattr(result, "chain", None)
            if not chain:
                return

            text = self._extract_text(chain)
            if not text:
                return

            if not self._matcher.should_render(text):
                return

            logger.info(f"[MathJax2Image] 命中自动渲染规则，内容长度: {len(text)}")
            image_path = await self._render_orchestrator.render(text)
            if not image_path.exists():
                logger.error(f"[MathJax2Image] 自动渲染失败，图片不存在: {image_path}")
                return

            result.chain = [Comp.Image.fromFileSystem(str(image_path))]
            logger.info(f"[MathJax2Image] 已将 LLM 文本替换为图片: {image_path}")
        except Exception as exc:
            logger.error(f"[MathJax2Image] 自动渲染失败，已回退原文本: {type(exc).__name__}: {exc}")
            logger.error(f"[MathJax2Image] 堆栈信息:\n{traceback.format_exc()}")
        finally:
            self._pending_llm_events.discard(event_id)

    def _extract_text(self, chain: list[Any]) -> str:
        """只提取纯文本结果链，遇到非文本段则跳过处理"""
        text_parts: list[str] = []

        for component in chain:
            if isinstance(component, str):
                text_parts.append(component)
                continue

            text = self._extract_text_from_component(component)
            if text is None:
                return ""

            text_parts.append(text)

        return "".join(text_parts).strip()

    def _extract_text_from_component(self, component: Any) -> str | None:
        """从消息段中提取文本内容"""
        for attr_name in ("text", "plain", "content"):
            attr_value = getattr(component, attr_name, None)
            if isinstance(attr_value, str):
                return attr_value

        return None

    def _build_event_key(self, event: AstrMessageEvent) -> int | str:
        """尽量使用稳定事件标识，避免不同钩子中的 event 实例不一致"""
        origin = getattr(event, "unified_msg_origin", None)
        if origin is not None:
            return str(origin)

        return id(event)
