import hashlib
import pathlib
from typing import Dict, Iterable, Iterator, List, Tuple


class DuplicateFinder:
    def __init__(self, paths: Iterable[str] = None) -> None:
        self.paths = list(paths)
        self.duplicates: Dict[Tuple[str, int], List[pathlib.Path]] = {}

    def find_duplicates(self) -> None:
        sizes: Dict[int, List[pathlib.Path]] = {}
        for p in set(self.paths):
            for f in pathlib.Path(p).glob("**/*"):
                if f.is_file():
                    sizes.setdefault(f.stat().st_size, []).append(f)

        dup_sizes = (path_list for path_list in sizes.values()
                     if len(path_list) > 1)

        for path_list in dup_sizes:
            self.compare_hashes(path_list)

    def gen_chunk(self, path: pathlib.Path, chunk_size: int = 4096) \
            -> Iterator[bytes]:
        """Read a chunk from the path

        First call will yield the first `chunk_size` bytes
        Second will yield the remainder of the file.

        Args:
            path: Path to file to be read
            chunk_size: Number of bytes to yield with the first call
        """

        with open(path, 'rb') as f:
            yield f.read(chunk_size)
            yield f.read()

    def compare_hashes(self, paths: List[pathlib.Path]) -> None:

        hashes = {'': [(path, hashlib.md5(), self.gen_chunk(path))
                       for path in paths]}
        while True:
            hex_, list_of_paths = hashes.popitem()
            for path, hasher, chunker in list_of_paths:
                try:
                    chunk = next(chunker)

                # At end of file and still have duplicates
                except StopIteration:
                    key = (hex_, path.stat().st_size)
                    self.duplicates.setdefault(key, []).append(path)
                    continue

                hasher.update(chunk)
                (hashes
                    .setdefault(hasher.hexdigest(), [])
                    .append((path, hasher, chunker)))

            hashes = {k: v for k, v in hashes.items() if len(v) > 1}

            # No duplicates left, break out of while loop
            if not hashes:
                break
