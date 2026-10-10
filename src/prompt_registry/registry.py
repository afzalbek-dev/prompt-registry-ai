import re
from typing import Dict, Any, List, Optional
from .storage import PromptStorage


class PromptTemplate:
    """Prompt shablonini saqlash va o'zgaruvchilarni render qilish."""

    def __init__(self, template: str):
        self.template = template
        self.variables = self._extract_variables(template)

    @staticmethod
    def _extract_variables(template: str) -> List[str]:
        # Masalan: "Salom {name}, bugun {topic} haqida yoz"
        return re.findall(r"\{([a-zA-Z0-9_]+)\}", template)

    def render(self, **kwargs) -> str:
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Shablon uchun o'zgaruvchilar yetishmayapti: {', '.join(missing)}")
        return self.template.format(**kwargs)


class PromptRegistry:
    """Promptlarni ro'yxatga olish va chaqirib olish boshqaruvchisi."""

    def __init__(self, storage: PromptStorage):
        self.storage = storage

    def register(self, name: str, template: str, model: str = "default") -> int:
        pt = PromptTemplate(template)
        return self.storage.save_prompt(name, template, pt.variables, model)

    def get(self, name: str, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        return self.storage.get_prompt(name, version)

    def render(self, name: str, version: Optional[int] = None, **kwargs) -> str:
        p = self.get(name, version)
        if not p:
            raise ValueError(f"Prompt topilmadi: {name}")
        pt = PromptTemplate(p["template"])
        return pt.render(**kwargs)
