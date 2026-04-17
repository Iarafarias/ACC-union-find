from __future__ import annotations


class WeightedQuickUnionUF:

	__slots__ = ("id", "size", "custoI", "totalAcessos")

	def __init__(self, n: int) -> None:
		if n < 0:
			raise ValueError("O n deve ser não negativo!")

		self.id: list[int] = list(range(n))
		self.size: list[int] = [1] * n

		self.custoI: int = 0
		self.totalAcessos: int = 0

		self.custoI = 2 * n
		self.totalAcessos = 2 * n

	def _validate_index(self, p: int) -> None:
		if not 0 <= p < len(self.id):
			raise IndexError(f"Indice fora do intervalo: {p}")

	def _start_operation(self) -> None:
		self.custoI = 0

	def _read_id(self, index: int) -> int:
		self.custoI += 1
		self.totalAcessos += 1
		return self.id[index]

	def _write_id(self, index: int, value: int) -> None:
		self.custoI += 1
		self.totalAcessos += 1
		self.id[index] = value

	def _read_size(self, index: int) -> int:
		self.custoI += 1
		self.totalAcessos += 1
		return self.size[index]

	def _write_size(self, index: int, value: int) -> None:
		self.custoI += 1
		self.totalAcessos += 1
		self.size[index] = value

	def _find_root(self, p: int) -> int:
		current = p
		parent = self._read_id(current)

		while current != parent:
			current = parent
			parent = self._read_id(current)

		return current

	def find(self, p: int) -> int:
		self._start_operation()
		self._validate_index(p)
		return self._find_root(p)

	def union(self, p: int, q: int) -> None:
		self._start_operation()
		self._validate_index(p)
		self._validate_index(q)

		root_p = self._find_root(p)
		root_q = self._find_root(q)

		if root_p == root_q:
			return

		size_p = self._read_size(root_p)
		size_q = self._read_size(root_q)

		if size_p < size_q:
			self._write_id(root_p, root_q)
			self._write_size(root_q, size_q + size_p)
		else:
			self._write_id(root_q, root_p)
			self._write_size(root_p, size_p + size_q)

	def connected(self, p: int, q: int) -> bool:
		self._start_operation()
		self._validate_index(p)
		self._validate_index(q)
		return self._find_root(p) == self._find_root(q)
