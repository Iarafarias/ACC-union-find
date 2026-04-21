from __future__ import annotations

import argparse
import statistics
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
from ponderado_quick_union import WeightedQuickUnionUF


CriadorUF = Callable[[int], Any]


@dataclass
class ResultadoExperimento:
	"""Dados coletados em uma execucao do experimento."""

	custos: list[int]
	custos_medios: list[float]
	tempo_total: float
	registros: list[dict[str, float | int]]


@dataclass
class EstatisticasTempo:
	"""Estatisticas de tempo para repeticoes do mesmo teste."""

	tempos: list[float]
	tempo_medio: float
	desvio_padrao: float
	runs: int


def ler_arquivo_conexoes(caminho_arquivo: str | Path) -> tuple[int, list[tuple[int, int]]]:
	"""Le arquivo no formato: 1a linha N; demais linhas com pares p q."""
	path = Path(caminho_arquivo)
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

	conexoes: list[tuple[int, int]] = []
	for line_number, line in enumerate(raw_lines[1:], start=2):
		parts = line.split()
		if len(parts) != 2:
			raise ValueError(f"linha {line_number} invalida: esperado 'p q'")
		try:
			p = int(parts[0])
			q = int(parts[1])
		except ValueError as exc:
			raise ValueError(f"linha {line_number} invalida: esperado inteiros") from exc
		conexoes.append((p, q))

	return n, conexoes


def executar_conexoes(
	n: int,
	conexoes: list[tuple[int, int]],
	criar_uf: CriadorUF,
) -> ResultadoExperimento:
	"""Processa as conexoes e coleta custos + tempo total."""
	uf = criar_uf(n)
	total_inicial = int(uf.total_acessos)

	custos: list[int] = []
	custos_medios: list[float] = []
	registros: list[dict[str, float | int]] = []

	start = time.perf_counter()

	for index, (p, q) in enumerate(conexoes, start=1):
		uf.union(p, q)

		custo_i = int(uf.custo_i)
		total_bruto = int(uf.total_acessos)
		total_acessos = total_bruto - total_inicial
		custo_medio = total_acessos / index

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
	return ResultadoExperimento(
		custos=custos,
		custos_medios=custos_medios,
		tempo_total=tempo_total,
		registros=registros,
	)


def executar_experimento(caminho_arquivo: str | Path, criar_uf: CriadorUF) -> ResultadoExperimento:
	"""Fluxo completo: leitura da entrada + execucao."""
	n, conexoes = ler_arquivo_conexoes(caminho_arquivo)
	return executar_conexoes(n=n, conexoes=conexoes, criar_uf=criar_uf)


def executar_experimento_varias_vezes(
	caminho_arquivo: str | Path,
	criar_uf: CriadorUF,
	runs: int = 10,
) -> tuple[ResultadoExperimento, EstatisticasTempo]:
	"""Executa o experimento varias vezes e calcula media/desvio de tempo."""
	if runs < 1:
		raise ValueError("runs deve ser >= 1")

	n, conexoes = ler_arquivo_conexoes(caminho_arquivo)

	ultimo_resultado: ResultadoExperimento | None = None
	tempos: list[float] = []
	for _ in range(runs):
		resultado = executar_conexoes(n=n, conexoes=conexoes, criar_uf=criar_uf)
		tempos.append(resultado.tempo_total)
		ultimo_resultado = resultado

	if ultimo_resultado is None:
		raise RuntimeError("falha inesperada ao executar repeticoes")

	tempo_medio = statistics.mean(tempos)
	desvio_padrao = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
	estatisticas = EstatisticasTempo(
		tempos=tempos,
		tempo_medio=tempo_medio,
		desvio_padrao=desvio_padrao,
		runs=runs,
	)
	return ultimo_resultado, estatisticas


def obter_algoritmo(nome: str) -> CriadorUF:
	"""Retorna a classe do algoritmo Union-Find escolhido."""
	nome_normalizado = nome.strip().lower()
	algoritmos: dict[str, CriadorUF] = {
		"quick_find": QuickFindUF,
		"quick_union": QuickUnionUF,
		"ponderado_quick_union": WeightedQuickUnionUF,
	}
	try:
		return algoritmos[nome_normalizado]
	except KeyError as exc:
		opcoes = ", ".join(sorted(algoritmos))
		raise ValueError(f"algoritmo invalido: {nome}. Opcoes: {opcoes}") from exc


def criar_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Executa experimentos com Union-Find")
	parser.add_argument(
		"--input",
		required=True,
		help="Arquivo de entrada (1a linha N; demais linhas: p q)",
	)
	parser.add_argument(
		"--algorithm",
		required=True,
		choices=["quick_find", "quick_union", "ponderado_quick_union"],
		help="Algoritmo Union-Find a ser usado",
	)
	parser.add_argument(
		"--runs",
		type=int,
		default=10,
		help="Numero de repeticoes para calcular media e desvio padrao do tempo",
	)
	return parser

def main() -> None:
	parser = criar_parser()
	args = parser.parse_args()

	algoritmo = obter_algoritmo(args.algorithm)
	resultado, estatisticas = executar_experimento_varias_vezes(
		args.input,
		algoritmo,
		runs=args.runs,
	)

	print(f"operacoes: {len(resultado.custos)}")
	print(f"runs: {estatisticas.runs}")
	print(f"tempo_ultima_execucao_s: {resultado.tempo_total:.6f}")
	print(f"tempo_medio_s: {estatisticas.tempo_medio:.6f}")
	print(f"desvio_padrao_s: {estatisticas.desvio_padrao:.6f}")
	if resultado.custos:
		print(f"custo_medio_final: {resultado.custos_medios[-1]:.4f}")
	else:
		print("custo_medio_final: 0.0000")


if __name__ == "__main__":
	main()

