from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
	sys.path.insert(0, str(SCRIPTS_DIR))

from rodar_experimento import executar_experimento_varias_vezes, obter_algoritmo


def criar_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Executa experimento Union-Find")
	parser.add_argument("--input", required=True, help="Arquivo de entrada")
	parser.add_argument(
		"--algorithm",
		required=True,
		choices=["quick_find", "quick_union", "ponderado_quick_union"],
		help="Algoritmo a ser testado",
	)
	parser.add_argument("--runs", type=int, default=10, help="Numero de repeticoes")
	return parser


def main() -> None:
	parser = criar_parser()
	args = parser.parse_args()

	algoritmo = obter_algoritmo(args.algorithm)
	resultado, estatisticas = executar_experimento_varias_vezes(
		caminho_arquivo=args.input,
		criar_uf=algoritmo,
		runs=args.runs,
	)

	print(f"operacoes: {len(resultado.custos)}")
	print(f"runs: {estatisticas.runs}")
	print(f"tempo_ultima_execucao_s: {resultado.tempo_total:.6f}")
	print(f"tempo_medio_s: {estatisticas.tempo_medio:.6f}")
	print(f"desvio_padrao_s: {estatisticas.desvio_padrao:.6f}")


if __name__ == "__main__":
	main()

