from __future__ import annotations


class QuickFindUF:

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("O n deve ser nao negativo")

        self.id: list[int] = list(range(n))

        self.custoI: int = 0
        self.totalAcessos: int = 0

        self.custoI = n
        self.totalAcessos = n

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

    def find(self, p: int) -> int:
        self._start_operation()
        self._validate_index(p)
        return self._read_id(p)

    def union(self, p: int, q: int) -> None:
        self._start_operation()
        self._validate_index(p)
        self._validate_index(q)

        pid = self._read_id(p)
        qid = self._read_id(q)

        if pid == qid:
            return

        for i in range(len(self.id)):
            if self._read_id(i) == pid:
                self._write_id(i, qid)

    def connected(self, p: int, q: int) -> bool:
        self._start_operation()
        self._validate_index(p)
        self._validate_index(q)

        return self._read_id(p) == self._read_id(q)


