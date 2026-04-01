"""
AstrBot MathJax2Image 插件
自动拦截 LLM 输出中的 Markdown / LaTeX / TikZ / Mermaid 内容并渲染为图片

主流程：
LLM 输出
  → on_llm_response 标记事件
  → on_decorating_result 读取最终文本
  → 正则命中后调用 RenderOrchestrator
  → 返回图片
"""

from pathlib import Path

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.provider import LLMResponse
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig

from .application import RenderOrchestrator, AutoRenderMatcher
from .handlers import AutoRenderHandler
from .utils.regex_patterns import AUTO_RENDER_DEFAULT_RULES


@register(
    "astrbot_plugin_mathjax2image",
    "Willixrain",
    "自动拦截 LLM 输出中的可渲染内容并转为图片",
    "3.1.0",
)
class MathJax2ImagePlugin(Star):
    """MathJax 转图片插件"""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._plugin_dir = Path(__file__).resolve().parent

        self._bg_color = config.get("background_color", "#FDFBF0")
        self._pattern_text = config.get("custom_match_patterns", "\n".join(AUTO_RENDER_DEFAULT_RULES))

        self._init_components()
        logger.info("[MathJax2Image] 插件已加载，自动拦截 LLM 消息中的可渲染内容")

    def _init_components(self):
        """初始化组件"""
        self._render_orchestrator = RenderOrchestrator(
            plugin_dir=self._plugin_dir,
            bg_color=self._bg_color,
        )
        self._auto_render_matcher = AutoRenderMatcher(self._pattern_text)
        self._auto_render_handler = AutoRenderHandler(
            matcher=self._auto_render_matcher,
            render_orchestrator=self._render_orchestrator,
        )

    @filter.on_llm_response()
    async def on_llm_response(self, event: AstrMessageEvent, response: LLMResponse):
        """标记当前事件来自 LLM，供发送前装饰阶段识别"""
        if response and getattr(response, "completion_text", None):
            self._auto_render_handler.mark_llm_event(event)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """发送前检测文本是否需要自动渲染"""
        await self._auto_render_handler.handle_decorating_result(event)

    async def terminate(self):
        """插件卸载时清理资源"""
        await self._render_orchestrator.close()
        logger.info("[MathJax2Image] 插件已卸载")
