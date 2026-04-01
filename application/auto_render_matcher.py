"""
自动渲染匹配器
负责逐行编译插件配置中的正则，并判断文本是否需要转图片。
"""

import re
from typing import Pattern

from astrbot.api import logger


class AutoRenderMatcher:
    """自动渲染匹配器"""

    def __init__(self, pattern_text: str):
        self._patterns = self._compile_patterns(pattern_text)

    def should_render(self, text: str) -> bool:
        """判断文本是否命中任意规则"""
        if not text or not self._patterns:
            return False

        for pattern in self._patterns:
            if pattern.search(text):
                return True

        return False

    def _compile_patterns(self, pattern_text: str) -> list[Pattern[str]]:
        """逐行编译插件配置中的正则"""
        compiled_patterns: list[Pattern[str]] = []

        for raw_line in pattern_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            try:
                compiled_patterns.append(re.compile(line))
            except re.error as exc:
                logger.warning(f"[MathJax2Image] 忽略非法正则: {line}，原因: {exc}")

        logger.info(f"[MathJax2Image] 自动渲染规则已加载: {len(compiled_patterns)} 条")
        return compiled_patterns
