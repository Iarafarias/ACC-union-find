from __future__ import annotations

import argparse
from pathlib import Path


TAMANHOS_OBRIGATORIOS = [10_000, 50_000, 100_000, 500_000]


def gerar_caso_adversarial(n: int, caminho_saida: str | Path) -> Path:
	"""Gera conexoes no padrao: 0 1, 0 2, ..., 0 n-1."""
	if n < 2:
		raise ValueError("n deve ser >= 2")

	caminho = Path(caminho_saida)
	caminho.parent.mkdir(parents=True, exist_ok=True)

	with caminho.open("w", encoding="utf-8") as arquivo:
		arquivo.write(f"{n}\n")
		for i in range(1, n):
			arquivo.write(f"0 {i}\n")

	return caminho


def gerar_casos_obrigatorios(pasta_saida: str | Path) -> list[Path]:
	"""Gera os 4 casos obrigatorios do enunciado."""
	pasta = Path(pasta_saida)
	pasta.mkdir(parents=True, exist_ok=True)

	arquivos_gerados: list[Path] = []
	for n in TAMANHOS_OBRIGATORIOS:
		nome_arquivo = f"adversarial_{n}.txt"
		caminho = gerar_caso_adversarial(n, pasta / nome_arquivo)
		arquivos_gerados.append(caminho)

	return arquivos_gerados


def criar_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Gera arquivos de teste para Union-Find")
	parser.add_argument("--n", type=int, help="Tamanho N para gerar um caso unico")
	parser.add_argument("--output", help="Arquivo de saida para o caso unico")
	parser.add_argument(
		"--required",
		action="store_true",
		help="Gera os 4 casos obrigatorios do trabalho",
	)
	parser.add_argument(
		"--out-dir",
		default="union-find/data",
		help="Pasta de saida quando --required for usado",
	)
	return parser


def main() -> None:
	parser = criar_parser()
	args = parser.parse_args()

	if args.required:
		arquivos = gerar_casos_obrigatorios(args.out_dir)
		print("Casos obrigatorios gerados:")
		for caminho in arquivos:
			print(f"- {caminho}")
		return

	if args.n is None or not args.output:
		parser.error("para caso unico, informe --n e --output")

	caminho = gerar_caso_adversarial(args.n, args.output)
	print(f"Caso gerado em: {caminho}")


if __name__ == "__main__":
	main()

