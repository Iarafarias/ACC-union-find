from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from quick_find import QuickFindUF
from quick_union import QuickUnionUF
from weighted_quick_union import WeightedQuickUnionUF


UFClassFactory = Callable[[int], Any]


@dataclass
class ExperimentResult:
	"""Resultado consolidado da execucao de um experimento."""

	custos: list[int]
	custos_medios: list[float]
	tempo_total: float
	registros: list[dict[str, float | int]]

	def to_dataframe(self) -> Any:
		"""Converte registros para DataFrame (quando pandas estiver disponivel)."""
		try:
			import pandas as pd  # type: ignore
		except ImportError as exc:
			raise RuntimeError("pandas nao instalado. Use pip install pandas") from exc
		return pd.DataFrame(self.registros)


def read_connections_file(file_path: str | Path) -> tuple[int, list[tuple[int, int]]]:
	"""Le arquivo de conexoes no formato: N na 1a linha e pares p q nas demais."""
	path = Path(file_path)
	if not path.exists():
		raise FileNotFoundError(f"arquivo nao encontrado: {path}")

	with path.open("r", encoding="utf-8") as f:
		raw_lines = [line.strip() for line in f if line.strip()]

	if not raw_lines:
		raise ValueError("arquivo vazio")

	try:
		n = int(raw_lines[0])
	except ValueError as exc:
		raise ValueError("a primeira linha deve ser um inteiro N") from exc

	pairs: list[tuple[int, int]] = []
	for line_number, line in enumerate(raw_lines[1:], start=2):
		parts = line.split()
		if len(parts) != 2:
			raise ValueError(f"linha {line_number} invalida: esperado 'p q'")
		try:
			p = int(parts[0])
			q = int(parts[1])
		except ValueError as exc:
			raise ValueError(f"linha {line_number} invalida: esperado inteiros") from exc
		pairs.append((p, q))

	return n, pairs


def run_connections(
	n: int,
	pairs: list[tuple[int, int]],
	uf_factory: UFClassFactory,
) -> ExperimentResult:
	"""Executa unions e coleta custo por operacao, custo medio e tempo total."""
	uf = uf_factory(n)

	custos: list[int] = []
	custos_medios: list[float] = []
	registros: list[dict[str, float | int]] = []

	soma_custos = 0
	start = time.perf_counter()

	for index, (p, q) in enumerate(pairs, start=1):
		uf.union(p, q)

		custo_i = int(uf.custo_i)
		total_acessos = int(uf.total_acessos)
		soma_custos += custo_i
		custo_medio = soma_custos / index

		custos.append(custo_i)
		custos_medios.append(custo_medio)
		registros.append(
			{
				"operacao": index,
				"p": p,
				"q": q,
				"custo_i": custo_i,
				"total_acessos": total_acessos,
				"custo_medio": custo_medio,
			}
		)

	tempo_total = time.perf_counter() - start
	return ExperimentResult(
		custos=custos,
		custos_medios=custos_medios,
		tempo_total=tempo_total,
		registros=registros,
	)


def run_experiment(file_path: str | Path, uf_factory: UFClassFactory) -> ExperimentResult:
	"""Pipeline completo: leitura da entrada e execucao do experimento."""
	n, pairs = read_connections_file(file_path)
	return run_connections(n=n, pairs=pairs, uf_factory=uf_factory)


def get_algorithm_factory(name: str) -> UFClassFactory:
	"""Resolve o algoritmo Union-Find pelo nome."""
	normalized = name.strip().lower()
	factories: dict[str, UFClassFactory] = {
		"quick_find": QuickFindUF,
		"quick_union": QuickUnionUF,
		"weighted_quick_union": WeightedQuickUnionUF,
	}
	try:
		return factories[normalized]
	except KeyError as exc:
		valid = ", ".join(sorted(factories))
		raise ValueError(f"algoritmo invalido: {name}. Opcoes: {valid}") from exc


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Executa experimentos com Union-Find")
	parser.add_argument(
		"--input",
		required=True,
		help="Arquivo de entrada (1a linha N; demais linhas: p q)",
	)
	parser.add_argument(
		"--algorithm",
		required=True,
		choices=["quick_find", "quick_union", "weighted_quick_union"],
		help="Algoritmo Union-Find a ser usado",
	)
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	factory = get_algorithm_factory(args.algorithm)
	result = run_experiment(args.input, factory)

	print(f"operacoes: {len(result.custos)}")
	print(f"tempo_total_s: {result.tempo_total:.6f}")
	if result.custos:
		print(f"custo_medio_final: {result.custos_medios[-1]:.4f}")
	else:
		print("custo_medio_final: 0.0000")


if __name__ == "__main__":
	main()

