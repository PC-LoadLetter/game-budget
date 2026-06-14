from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from game_budget.config import JOURNAL_FILENAME, data_dir
from game_budget.main import create_app
from game_budget.service import init_data


def main() -> None:
    parser = argparse.ArgumentParser(prog="game-budget")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run the web server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--data", type=Path, default=None)

    init_cmd = sub.add_parser("init", help="Initialize data directory")
    init_cmd.add_argument("--data", type=Path, default=None)
    init_cmd.add_argument(
        "--sample",
        type=Path,
        default=Path("samples") / JOURNAL_FILENAME,
        help="Sample journal to copy if none exists",
    )

    args = parser.parse_args()
    if args.command == "serve":
        path = data_dir(args.data)
        app = create_app(path)
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.command == "init":
        path = data_dir(args.data)
        init_data(path, sample_journal=args.sample if args.sample.exists() else None)
        print(f"Initialized {path}")


if __name__ == "__main__":
    main()
