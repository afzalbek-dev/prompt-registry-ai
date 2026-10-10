# Prompt Registry AI

AI tizimlari va LLM ilovalari uchun promptlar versiyasini boshqarish, o'zgaruvchilarni renderlash va javob sifatini (evaluations) baholash vositasi.

## Xususiyatlari
- **Prompt Versiyalash**: Bir xil prompt nomining barcha o'zgarishlarini v1, v2, v3 tarzida SQLite bazasida saqlash.
- **O'zgaruvchilar Validatsiyasi**: Shablonlardagi `{param}` qiymatlarini tekshirish va to'liq render qilish.
- **Baholash va Metrikalar**: Javoblar sifati (0 dan 5 gacha ball), javob kechikishi (latency) va foydalanuvchi izohlarini qayd etish.
- **CLI & Python SDK**: CLI orqali promptlarni sinovdan o'tkazish yoki ilovangiz ichida qulay SDK sifatida ishlatish.

## Foydalanish (Python)
```python
from prompt_registry import PromptRegistry, PromptStorage, PromptEvaluator

storage = PromptStorage("prompts.db")
registry = PromptRegistry(storage)

# Promptni ro'yxatga olish
pid = registry.register("translator", "Translate the following text into Uzbek: {text}", model="gpt-4o")

# Render qilish
rendered = registry.render("translator", text="Hello world")
print(rendered)

# Baholash
evaluator = PromptEvaluator(storage)
evaluator.evaluate(pid, score=4.8, latency_ms=250, notes="Aniq tarjima")
```

## CLI
```bash
prompt-registry register summarizer "Quyidagi matnni 3 ta punktda xulosala: {content}"
prompt-registry render summarizer --vars '{"content": "Sun'iy intellekt rivojlanmoqda..."}'
prompt-registry eval 1 4.5 --notes "Yaxshi xulosa"
```

## Testlar
```bash
pytest tests/ -v
```

## Litsenziya
MIT
