from __future__ import annotations


class QuickUnionUF:
	def __init__(self, n: int) -> None:
		if n < 0:
			raise ValueError("O n deve ser nao negativo")

		self.id: list[int] = list(range(n))
		self.custo_i: int = n
		self.total_acessos: int = n

	def _validate_index(self, p: int) -> None:
		if not 0 <= p < len(self.id):
			raise IndexError(f"Indice fora do intervalo: {p}")

	def _start_operation(self) -> None:
		self.custo_i = 0

	def _read_id(self, index: int) -> int:
		self.custo_i += 1
		self.total_acessos += 1
		return self.id[index]

	def _write_id(self, index: int, value: int) -> None:
		self.custo_i += 1
		self.total_acessos += 1
		self.id[index] = value

	def _find_root(self, p: int) -> int:
		atual = p
		pai = self._read_id(atual)

		while atual != pai:
			atual = pai
			pai = self._read_id(atual)

		return atual

	def find(self, p: int) -> int:
		self._start_operation()
		self._validate_index(p)
		return self._find_root(p)

	def union(self, p: int, q: int) -> None:
		self._start_operation()
		self._validate_index(p)
		self._validate_index(q)

		raiz_p = self._find_root(p)
		raiz_q = self._find_root(q)

		if raiz_p == raiz_q:
			return

		self._write_id(raiz_p, raiz_q)

	def connected(self, p: int, q: int) -> bool:
		self._start_operation()
		self._validate_index(p)
		self._validate_index(q)
		return self._find_root(p) == self._find_root(q)

