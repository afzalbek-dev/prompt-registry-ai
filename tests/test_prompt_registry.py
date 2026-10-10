import pytest
from prompt_registry.storage import PromptStorage
from prompt_registry.registry import PromptRegistry, PromptTemplate
from prompt_registry.evaluator import PromptEvaluator


def test_prompt_template_variable_extraction_and_render():
    pt = PromptTemplate("Assalomu alaykum {user}, sizning buyurtmangiz #{order_id} tayyor!")
    assert set(pt.variables) == {"user", "order_id"}

    rendered = pt.render(user="Aziz", order_id="105")
    assert rendered == "Assalomu alaykum Aziz, sizning buyurtmangiz #105 tayyor!"

    with pytest.raises(ValueError):
        pt.render(user="Aziz")  # order_id yetishmayapti


def test_prompt_versioning_and_evaluations(tmp_path):
    db_file = str(tmp_path / "prompts_test.db")
    storage = PromptStorage(db_file)
    registry = PromptRegistry(storage)
    evaluator = PromptEvaluator(storage)

    # v1
    id1 = registry.register("support_bot", "Yordam bering: {msg}")
    p1 = registry.get("support_bot")
    assert p1["version"] == 1

    # v2
    id2 = registry.register("support_bot", "Xush kelibsiz! Sizga qanday yordam bera olaman: {msg}")
    p2 = registry.get("support_bot")
    assert p2["version"] == 2

    # Eng so'nggi versiyani render qilish
    out2 = registry.render("support_bot", msg="Parolni tiklash")
    assert "Xush kelibsiz!" in out2

    # v1 ni render qilish
    out1 = registry.render("support_bot", version=1, msg="Parolni tiklash")
    assert out1 == "Yordam bering: Parolni tiklash"

    # Baholash
    evaluator.evaluate(id2, 4.5, latency_ms=120, notes="Juda tez")
    evaluator.evaluate(id2, 5.0, latency_ms=100, notes="A'lo")

    metrics = evaluator.get_metrics(id2)
    assert metrics["count"] == 2
    assert metrics["average_score"] == 4.75
    storage.close()
