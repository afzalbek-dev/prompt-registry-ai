import argparse
import sys
import json
from .storage import PromptStorage
from .registry import PromptRegistry
from .evaluator import PromptEvaluator


def main():
    parser = argparse.ArgumentParser(description="Prompt Registry AI - Promptlar boshqaruvi va baholash")
    parser.add_argument("--db", default="/tmp/prompts.db", help="SQLite ma'lumotlar bazasi fayli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reg_p = subparsers.add_parser("register", help="Yangi prompt yoki versiyani ro'yxatga olish")
    reg_p.add_argument("name", help="Prompt nomi (masalan: code_review)")
    reg_p.add_argument("template", help="Shablon matni (masalan: 'Quyidagi kodni tahlil qil: {code}')")
    reg_p.add_argument("--model", default="gpt-4o", help="Mo'ljallangan model")

    render_p = subparsers.add_parser("render", help="Prompt shablonini to'ldirib chiqarish")
    render_p.add_argument("name", help="Prompt nomi")
    render_p.add_argument("--version", type=int, help="Versiya raqami")
    render_p.add_argument("--vars", help="JSON formatidagi o'zgaruvchilar, masalan: '{\"code\":\"x=1\"}'")

    eval_p = subparsers.add_parser("eval", help="Prompt versiyasini baholash")
    eval_p.add_argument("prompt_id", type=int, help="Prompt versiyasi ID")
    eval_p.add_argument("score", type=float, help="Ball (0 dan 5 gacha)")
    eval_p.add_argument("--notes", default="", help="Izoh")

    args = parser.parse_args()
    storage = PromptStorage(args.db)
    registry = PromptRegistry(storage)
    evaluator = PromptEvaluator(storage)

    if args.command == "register":
        pid = registry.register(args.name, args.template, model=args.model)
        p = storage.get_prompt(args.name)
        print(f"✅ Saqlandi: '{args.name}' v{p['version']} (ID: {pid})")
    elif args.command == "render":
        variables = json.loads(args.vars) if args.vars else {}
        output = registry.render(args.name, args.version, **variables)
        print(output)
    elif args.command == "eval":
        evaluator.evaluate(args.prompt_id, args.score, notes=args.notes)
        m = evaluator.get_metrics(args.prompt_id)
        print(f"✅ Baholandi! O'rtacha ball: {m['average_score']}/5.0 (jami: {m['count']} ta baho)")


if __name__ == "__main__":
    main()
