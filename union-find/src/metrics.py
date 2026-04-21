from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass
class ResumoTempo:
	"""Resumo estatistico dos tempos de execucao."""

	media: float
	desvio_padrao: float
	minimo: float
	maximo: float
	repeticoes: int


def calcular_resumo_tempos(tempos: list[float]) -> ResumoTempo:
	"""Calcula media, desvio padrao, minimo e maximo de uma lista de tempos."""
	if not tempos:
		raise ValueError("lista de tempos vazia")

	media = statistics.mean(tempos)
	desvio_padrao = statistics.stdev(tempos) if len(tempos) > 1 else 0.0

	return ResumoTempo(
		media=media,
		desvio_padrao=desvio_padrao,
		minimo=min(tempos),
		maximo=max(tempos),
		repeticoes=len(tempos),
	)


def resumo_para_dict(nome_algoritmo: str, n: int, tempos: list[float]) -> dict[str, float | int | str]:
	"""Converte o resumo de tempos para um formato facil de salvar em tabela."""
	resumo = calcular_resumo_tempos(tempos)
	return {
		"algoritmo": nome_algoritmo,
		"n": n,
		"repeticoes": resumo.repeticoes,
		"tempo_medio": resumo.media,
		"desvio_padrao": resumo.desvio_padrao,
		"tempo_minimo": resumo.minimo,
		"tempo_maximo": resumo.maximo,
	}

