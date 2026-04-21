from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from rodar_experimento import executar_experimento_varias_vezes, obter_algoritmo


ALGORITMOS = ["quick_find", "quick_union", "ponderado_quick_union"]


def listar_arquivos_entrada(pasta_dados: Path) -> list[Path]:
    arquivos = sorted(pasta_dados.glob("*.txt"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum arquivo .txt encontrado em: {pasta_dados}")
    return arquivos


def ler_n_arquivo(caminho_arquivo: Path) -> int:
    with caminho_arquivo.open("r", encoding="utf-8") as f:
        primeira_linha = f.readline().strip()
    try:
        return int(primeira_linha)
    except ValueError as exc:
        raise ValueError(f"primeira linha invalida em {caminho_arquivo}") from exc


def reduzir_serie(
    x: list[int],
    y1: list[int],
    y2: list[float],
    max_pontos: int,
) -> tuple[list[int], list[int], list[float]]:
    if max_pontos <= 0 or len(x) <= max_pontos:
        return x, y1, y2

    passo = max(1, len(x) // max_pontos)
    return x[::passo], y1[::passo], y2[::passo]


def salvar_csv_operacoes(
    caminho_saida: Path,
    registros: list[dict[str, float | int]],
) -> None:
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with caminho_saida.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["operacao", "p", "q", "custo_i", "total_acessos", "custo_medio"],
        )
        writer.writeheader()
        writer.writerows(registros)


def plotar_custos(
    caminho_saida: Path,
    titulo: str,
    custos: list[int],
    custos_medios: list[float],
    max_pontos: int,
) -> None:
    import matplotlib.pyplot as plt  # type: ignore

    x = list(range(1, len(custos) + 1))
    x_plot, custos_plot, custos_medios_plot = reduzir_serie(x, custos, custos_medios, max_pontos)

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(x_plot, custos_plot, color="gray", linewidth=1.0, alpha=0.7, label="custo_i")
    plt.plot(x_plot, custos_medios_plot, color="red", linewidth=1.8, label="custo medio")
    plt.title(titulo)
    plt.xlabel("Numero de conexoes processadas")
    plt.ylabel("Acessos ao vetor")
    plt.legend()
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=140)
    plt.close()


def salvar_csv_tempos(caminho_saida: Path, linhas: list[dict[str, float | int | str]]) -> None:
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with caminho_saida.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "algoritmo",
                "instancia",
                "n",
                "runs",
                "tempo_medio_s",
                "desvio_padrao_s",
                "tempo_ultima_execucao_s",
                "qtd_operacoes",
            ],
        )
        writer.writeheader()
        writer.writerows(linhas)


def plotar_tempo_por_n(
    caminho_saida: Path,
    algoritmo: str,
    linhas_tempo: list[dict[str, float | int | str]],
) -> None:
    import matplotlib.pyplot as plt  # type: ignore

    linhas_alg = [l for l in linhas_tempo if l["algoritmo"] == algoritmo]
    linhas_alg.sort(key=lambda l: int(l["n"]))

    if not linhas_alg:
        return

    ns = [int(l["n"]) for l in linhas_alg]
    medias = [float(l["tempo_medio_s"]) for l in linhas_alg]
    desvios = [float(l["desvio_padrao_s"]) for l in linhas_alg]

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4.8))
    plt.errorbar(ns, medias, yerr=desvios, color="tab:blue", marker="o", capsize=4)
    plt.title(f"Tempo de execucao por N - {algoritmo}")
    plt.xlabel("Quantidade de elementos (N)")
    plt.ylabel("Tempo medio (s)")
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=140)
    plt.close()


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa todos os experimentos e gera graficos")
    parser.add_argument("--data-dir", default="union-find/data", help="Pasta com arquivos de entrada")
    parser.add_argument("--results-dir", default="union-find/results", help="Pasta para CSVs de saida")
    parser.add_argument("--plots-dir", default="union-find/plots", help="Pasta para graficos")
    parser.add_argument("--runs", type=int, default=10, help="Numero de repeticoes por experimento")
    parser.add_argument(
        "--quick-find-runs",
        type=int,
        default=1,
        help="Numero de repeticoes apenas para quick_find",
    )
    parser.add_argument(
        "--quick-find-max-n",
        type=int,
        default=10_000,
        help="Pula quick_find quando N for maior que este limite",
    )
    parser.add_argument(
        "--quick-union-max-n",
        type=int,
        default=100_000,
        help="Pula quick_union quando N for maior que este limite",
    )
    parser.add_argument(
        "--max-plot-points",
        type=int,
        default=50_000,
        help="Limite de pontos por grafico de custo (reduz para manter desempenho)",
    )
    return parser


def main() -> None:
    parser = criar_parser()
    args = parser.parse_args()

    pasta_dados = Path(args.data_dir)
    pasta_resultados = Path(args.results_dir)
    pasta_plots = Path(args.plots_dir)

    arquivos_entrada = listar_arquivos_entrada(pasta_dados)
    linhas_tempo: list[dict[str, float | int | str]] = []

    for arquivo in arquivos_entrada:
        instancia = arquivo.stem
        n = ler_n_arquivo(arquivo)

        for nome_algoritmo in ALGORITMOS:
            if nome_algoritmo == "quick_find" and n > args.quick_find_max_n:
                print(
                    f"Pulando quick_find em {instancia}: N={n} > {args.quick_find_max_n}"
                )
                continue

            if nome_algoritmo == "quick_union" and n > args.quick_union_max_n:
                print(
                    f"Pulando quick_union em {instancia}: N={n} > {args.quick_union_max_n}"
                )
                continue

            runs_atuais = args.quick_find_runs if nome_algoritmo == "quick_find" else args.runs
            criar_uf = obter_algoritmo(nome_algoritmo)
            resultado, estatisticas = executar_experimento_varias_vezes(
                caminho_arquivo=arquivo,
                criar_uf=criar_uf,
                runs=runs_atuais,
            )

            csv_operacoes = pasta_resultados / f"{nome_algoritmo}_{instancia}_operacoes.csv"
            salvar_csv_operacoes(csv_operacoes, resultado.registros)

            grafico_custos = pasta_plots / f"{nome_algoritmo}_{instancia}_custos.png"
            plotar_custos(
                caminho_saida=grafico_custos,
                titulo=f"{nome_algoritmo} - {instancia}",
                custos=resultado.custos,
                custos_medios=resultado.custos_medios,
                max_pontos=args.max_plot_points,
            )

            linhas_tempo.append(
                {
                    "algoritmo": nome_algoritmo,
                    "instancia": instancia,
                    "n": n,
                    "runs": estatisticas.runs,
                    "tempo_medio_s": estatisticas.tempo_medio,
                    "desvio_padrao_s": estatisticas.desvio_padrao,
                    "tempo_ultima_execucao_s": resultado.tempo_total,
                    "qtd_operacoes": len(resultado.custos),
                }
            )

            print(f"Concluido: {nome_algoritmo} em {instancia}")

    csv_tempos = pasta_resultados / "resumo_tempos.csv"
    salvar_csv_tempos(csv_tempos, linhas_tempo)

    for nome_algoritmo in ALGORITMOS:
        grafico_tempo = pasta_plots / f"{nome_algoritmo}_tempo_por_n.png"
        plotar_tempo_por_n(grafico_tempo, nome_algoritmo, linhas_tempo)

    print(f"Resumo salvo em: {csv_tempos}")
    print(f"Graficos salvos em: {pasta_plots}")


if __name__ == "__main__":
    main()
