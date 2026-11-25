"""Servidor da interface de expansão da base (Front/expansao.html).

Rodar, a partir da pasta Scrapping_api:
  ..\\.venv\\Scripts\\python -m uvicorn expansion_server:app --port 8010 --env-file ..\\.env
e abrir http://127.0.0.1:8010/
"""

import json
import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from expansion import STEPS, Expansion  # noqa: E402
from expansion.diversity import report  # noqa: E402

FRONT = ROOT / "Front"
app = FastAPI(title="Expansão da base do TCC")


class Runner:
    """Roda uma etapa por vez numa thread e guarda o último evento de progresso."""

    def __init__(self):
        self.lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None
        self.expansion: Optional[Expansion] = None
        self.last_event: dict = {}
        self.error: Optional[str] = None

    @property
    def running(self) -> bool:
        return bool(self.thread and self.thread.is_alive())

    def start(self, step: str, cells: int, cap: int, max_artists: int, tracks_per_artist: int):
        with self.lock:
            if self.running:
                raise HTTPException(409, "Já existe uma etapa rodando. Pare a atual antes de começar outra.")
            self.error = None
            self.last_event = {"step": step, "message": "começando"}
            self.expansion = Expansion(progress=self._on_progress)

            def work():
                try:
                    exp = self.expansion
                    if step == "search":
                        exp.run_search(exp.plan_queries(cap=cap), max_cells=cells)
                    elif step == "artists":
                        exp.run_artists(max_artists=max_artists, tracks_per_artist=tracks_per_artist)
                    elif step == "enrich":
                        exp.run_enrich()
                    elif step == "features":
                        exp.run_features()
                    elif step == "export":
                        exp.run_export()
                        report(exp.data_dir / "diversity.json")
                except Exception as err:  # mostrado na interface
                    self.error = f"{err.__class__.__name__}: {err}"
                finally:
                    if self.expansion:
                        self.expansion.save()

            self.thread = threading.Thread(target=work, daemon=True)
            self.thread.start()

    def _on_progress(self, event: dict):
        self.last_event = event

    def stop(self):
        if self.expansion:
            self.expansion.stop.set()


runner = Runner()


def snapshot() -> dict:
    exp = runner.expansion if runner.running else Expansion()
    cells = exp.plan_queries()
    return {
        "running": runner.running,
        "event": {k: v for k, v in runner.last_event.items() if k != "counters"},
        "error": runner.error,
        "counters": exp.counters(),
        "cells_total": len(cells),
        "cells_done": len(set(exp.state["queries_done"]) & {c["id"] for c in cells}),
        "artists_total": len(exp.artists),
        "last_export": exp.state.get("last_export"),
        "log": exp.state.get("log", [])[-12:],
        "steps": STEPS,
    }


@app.get("/")
def page():
    return FileResponse(FRONT / "expansao.html", media_type="text/html")


@app.get("/favicon.svg")
def favicon():
    return FileResponse(FRONT / "favicon.svg", media_type="image/svg+xml")


app.mount("/assets", StaticFiles(directory=FRONT / "assets"), name="assets")


@app.get("/api/state")
def state():
    return snapshot()


@app.post("/api/run")
async def run(request: Request):
    form = await request.form()
    step = str(form.get("step", ""))
    if step not in STEPS:
        raise HTTPException(400, f"Etapa desconhecida: {step}")

    def number(name: str, default: int) -> int:
        try:
            return max(1, int(str(form.get(name) or default)))
        except ValueError:
            raise HTTPException(400, f"{name} precisa ser um número")

    runner.start(step, number("cells", 20), number("cap", 200), number("max_artists", 100), number("tracks_per_artist", 5))
    return {"ok": True, "step": step}


@app.post("/api/stop")
def stop():
    runner.stop()
    return {"ok": True}


@app.get("/api/report")
def diversity():
    path = Expansion().data_dir / "diversity.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return report(path)
