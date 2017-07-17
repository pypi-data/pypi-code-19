import builtins

class fa(object):
    def __init__(self, file_name, mode="r", fasta_mode="lines"):
        self._fasta_file = builtins.open(file_name, mode, encoding="utf-8")
        if not fasta_mode in ["seqs", "heads", "lines"]:
            raise ValueError("fasta_mode parameter must be either lines, seqs or heads")
        self._fasta_mode = fasta_mode
        self._offset = 0
        self._last_header = 0
        self._recent_header = False

    def setfastamode(self, fasta_mode):
        if not fasta_mode in ["seqs", "heads", "lines"]:
            raise ValueError("fasta_mode parameter must be either lines, seqs or heads")
        self._fasta_mode = fasta_mode

    def __iter__(self):
        if self._fasta_mode == "lines":
            unit = self.readline()
        elif self._fasta_mode == "heads":
            unit = self.readheader()
        else:
            unit = self.readseq()

        while unit:
            yield unit
            if self._fasta_mode == "lines":
                unit = self.readline()
            elif self._fasta_mode == "heads":
                unit = self.readheader()
            else:
                unit = self.readseq()

    def readline(self):
        line = self._fasta_file.readline()
        if line:
            if line[0] == ">":
                self._last_header += self._offset
                self._offset = 0
                self._recent_header = True
            else:
                self._recent_header = False

        self._offset += len(line)

        return str(line)

    def readseq(self):
        while not self._recent_header:
            line = self.readline()
            if not line:
                return line

        seq = ""

        line = self.readline()
        while line: 
            if self._recent_header:
                self._fasta_file.seek(self._last_header)
                self._offset = 0
                self._recent_header = False
                break

            seq += line.strip()
            line = self.readline()

        return seq


    def readseqs(self):
        seqs = []
        seq = self.readseq()
        while seq:
            seqs.append(seq)
            seq = self.readseq()

        return seqs

    def readheader(self):
        line = self.readline()

        while line:
            if line[0] == ">":
                return line.strip()
            line = self.readline()
        
        return line.strip()

    def readheaders(self):
        heads = []
        head = self.readheader()
        while head:
            heads.append(head)
            head = self.readheader()

        return heads

    def prevheader(self):
        prev = self._fasta_file.tell()
        self._fasta_file.seek(self._last_header)
        header = self._fasta_file.readline()
        self._fasta_file.seek(prev)
        return header.strip()

    def close(self):
        self._fasta_file.close()


class open(fa):
    def __init__(self, file_name, mode="r", fasta_mode="seqs"):
        super(self.__class__, self).__init__(file_name, mode, fasta_mode)

    def __enter__(self):
        return self

    def __exit__(self, excep_type, excep_val, trace):
        super(self.__class__, self).close()
