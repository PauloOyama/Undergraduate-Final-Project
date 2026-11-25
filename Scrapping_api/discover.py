"""Linha de comando da expansão da base.

Exemplos (a partir da pasta Scrapping_api, com o .env na raiz do projeto):
  python discover.py search --cells 3        # roda 3 células da grade de busca
  python discover.py artists --max 50        # álbuns de 50 artistas novos
  python discover.py enrich                  # ISRC, popularidade e gêneros
  python discover.py features                # atributos de áudio (ReccoBeats)
  python discover.py export                  # CSV em Understanding_Spotify_Metadata/DataSet
  python discover.py report                  # diversidade antes x depois
  python discover.py all --cells 20 --max 100
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from expansion import Expansion  # noqa: E402
from expansion.diversity import report  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Expande a base de músicas do TCC")
    parser.add_argument("step", choices=["plan", "search", "artists", "enrich", "features", "export", "report", "all"])
    parser.add_argument("--cells", type=int, help="quantas células da grade de busca rodar agora")
    parser.add_argument("--cap", type=int, default=200, help="teto de faixas por célula")
    parser.add_argument("--max", type=int, help="quantos artistas expandir agora")
    args = parser.parse_args()

    def show(event):
        if event.get("message"):
            done, total = event.get("done"), event.get("total")
            prefix = f"[{event.get('step')} {done}/{total}]" if total else f"[{event.get('step')}]"
            print(prefix, event["message"])

    exp = Expansion(progress=show)
    cells = exp.plan_queries(cap=args.cap)
    if args.step == "plan":
        print(f"{len(cells)} células na grade; {len(exp.state['queries_done'])} já feitas")
        for c in cells[:15]:
            print(" ", c["market"], c["query"])
        return
    if args.step in ("search", "all"):
        exp.run_search(cells, max_cells=args.cells)
    if args.step in ("artists", "all"):
        exp.run_artists(max_artists=args.max)
    if args.step in ("enrich", "all"):
        exp.run_enrich()
    if args.step in ("features", "all"):
        exp.run_features()
    if args.step in ("export", "all"):
        print(json.dumps(exp.run_export(), ensure_ascii=False, indent=2))
    if args.step in ("report", "all"):
        print(json.dumps(report(exp.data_dir / "diversity.json"), ensure_ascii=False, indent=2))
    print("contadores:", exp.counters())


if __name__ == "__main__":
    main()
