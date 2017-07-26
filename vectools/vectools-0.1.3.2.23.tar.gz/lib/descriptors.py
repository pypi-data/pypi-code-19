from math import pow


class NComposition:

    def __init__(self, kmer_len, alphabet, round_to, allow_nonstandard=True):
        """
        :param kmer_len: An integer must be greater than zero.
        :param alphabet: A list of characters to use for alphabet.
        """
        from itertools import product
        # Generate sorted n-composition vectors.
        self.kmer_len = kmer_len
        self.alphabet_list = sorted([''.join(kmer) for kmer in product(alphabet, repeat=kmer_len)])
        self.round_to = round_to
        self.allow_nonstandard = allow_nonstandard

    def calc(self, sequence, return_string=False):
        """ This function calculates the n-composition of a sequence within a given alphabet.
        :param sequence:
        :param return_string:
        :return:
        """
        # Count the number of possible positions within the alphabet.
        # @TODO: Should we add a check to make sure all alphabet els are the same len?
        # sequence_list = [
        # sequence[i:i + len(self.alphabet_list[0])] for i in range(len(sequence) - (len(self.alphabet_list[0]) - 1))]
        seq_len = len(sequence)
        # Split up the sequence into k-mers moving +1 each time until the end of the sequnece minsu the kmer len.
        sequence_list = []
        for i in range(seq_len - (self.kmer_len - 1)):
            sequence_list.append(sequence[i:i + self.kmer_len])

        descriptor_vec = []
        for kmer in self.alphabet_list:
            vec_el = round(float(sequence_list.count(kmer)) / seq_len, self.round_to)
            if return_string:
                vec_el = str(vec_el)
            descriptor_vec.append(vec_el)
        return descriptor_vec

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.alphabet_list

#TODO: Make sliceable.
class SplitNComposition:

    def __init__(self, kmer_len, alphabet, round_to, allow_nonstandard=True):

        self.n_comp = NComposition(kmer_len, alphabet, round_to, allow_nonstandard=allow_nonstandard)
        n_terminal = ["start_" + c for c in self.n_comp.getcoltitles()]
        middle_seq = ["mid_" + c for c in self.n_comp.getcoltitles()]
        c_terminal = ["end_" + c for c in self.n_comp.getcoltitles()]
        self.col_titles = n_terminal + middle_seq + c_terminal

    def calc(self, sequence, start_len, stop_len):
        # Avoid list len related errors.
        assert len(sequence) > start_len and len(sequence) > stop_len

        start_seq_list = self.n_comp.calc(sequence[:start_len])
        mid_seq_list = self.n_comp.calc(sequence[start_len:-stop_len])
        end_seq_list = self.n_comp.calc(sequence[:stop_len])

        return start_seq_list + mid_seq_list + end_seq_list

    def getcoltitles(self):
        """
        :return: The column ids of the feature.
        """
        return self.col_titles


class GearyAutocorrelation:

    def __init__(self, roundto):
        self.roundto = roundto

        _Hydrophobicity = {
            "A": 0.02, "R": -0.42, "N": -0.77, "D": -1.04, "C": 0.77,
            "Q": -1.10, "E": -1.14, "G": -0.80, "H": 0.26, "I": 1.81,
            "L": 1.14, "K": -0.41, "M": 1.00, "F": 1.35, "P": -0.09,
            "S": -0.97, "T": -0.77, "W": 1.71, "Y": 1.11, "V": 1.13
        }
        _AvFlexibility = {
            "A": 0.357, "R": 0.529, "N": 0.463, "D": 0.511, "C": 0.346,
            "Q": 0.493, "E": 0.497, "G": 0.544, "H": 0.323, "I": 0.462,
            "L": 0.365, "K": 0.466, "M": 0.295, "F": 0.314, "P": 0.509,
            "S": 0.507, "T": 0.444, "W": 0.305, "Y": 0.420, "V": 0.386
        }
        _Polarizability = {
            "A": 0.046, "R": 0.291, "N": 0.134, "D": 0.105, "C": 0.128,
            "Q": 0.180, "E": 0.151, "G": 0.000, "H": 0.230, "I": 0.186,
            "L": 0.186, "K": 0.219, "M": 0.221, "F": 0.290, "P": 0.131,
            "S": 0.062, "T": 0.108, "W": 0.409, "Y": 0.298, "V": 0.140
        }

        _FreeEnergy = {
            "A": -0.368, "R": -1.03, "N": 0.0, "D": 2.06, "C": 4.53,
            "Q": 0.731, "E": 1.77, "G": -0.525, "H": 0.0, "I": 0.791,
            "L": 1.07, "K": 0.0, "M": 0.656, "F": 1.06, "P": -2.24,
            "S": -0.524, "T": 0.0, "W": 1.60, "Y": 4.91, "V": 0.401
        }

        _ResidueASA = {
            "A": 115.0, "R": 225.0, "N": 160.0, "D": 150.0, "C": 135.0,
            "Q": 180.0, "E": 190.0, "G": 75.0, "H": 195.0, "I": 175.0,
            "L": 170.0, "K": 200.0, "M": 185.0, "F": 210.0, "P": 145.0,
            "S": 115.0, "T": 140.0, "W": 255.0, "Y": 230.0, "V": 155.0
        }

        _ResidueVol = {
            "A": 52.6, "R": 109.1, "N": 75.7, "D": 68.4, "C": 68.3,
            "Q": 89.7, "E": 84.7, "G": 36.3, "H": 91.9, "I": 102.0,
            "L": 102.0, "K": 105.1, "M": 97.7, "F": 113.9, "P": 73.6,
            "S": 54.9, "T": 71.2, "W": 135.4, "Y": 116.2, "V": 85.1
        }
        _Steric = {
            "A": 0.52, "R": 0.68, "N": 0.76, "D": 0.76, "C": 0.62,
            "Q": 0.68, "E": 0.68, "G": 0.00, "H": 0.70, "I": 1.02,
            "L": 0.98, "K": 0.68, "M": 0.78, "F": 0.70, "P": 0.36,
            "S": 0.53, "T": 0.50, "W": 0.70, "Y": 0.70, "V": 0.76
        }

        _Mutability = {
            "A": 100.0, "R": 65.0, "N": 134.0, "D": 106.0, "C": 20.0,
            "Q": 93.0, "E": 102.0, "G": 49.0, "H": 66.0, "I": 96.0,
            "L": 40.0, "K": -56.0, "M": 94.0, "F": 41.0, "P": 56.0,
            "S": 120.0, "T": 97.0, "W": 18.0, "Y": 41.0, "V": 74.0
        }

        _Hydrophobicity = self._normalize_amino_acid_property(_Hydrophobicity)
        _AvFlexibility = self._normalize_amino_acid_property(_AvFlexibility)
        _Polarizability = self._normalize_amino_acid_property(_Polarizability)
        _FreeEnergy = self._normalize_amino_acid_property(_FreeEnergy)
        _ResidueASA = self._normalize_amino_acid_property(_ResidueASA)
        _ResidueVol = self._normalize_amino_acid_property(_ResidueVol)
        _Steric = self._normalize_amino_acid_property(_Steric)
        _Mutability = self._normalize_amino_acid_property(_Mutability)

        self.amino_acid_property_groups = (
            ('_Hydrophobicity', _Hydrophobicity),
            ('_AvFlexibility',  _AvFlexibility),
            ('_Polarizability', _Polarizability),
            ('_FreeEnergy',     _FreeEnergy),
            ('_ResidueASA',     _ResidueASA),
            ('_ResidueVol',     _ResidueVol),
            ('_Steric',         _Steric),
            ('_Mutability',     _Mutability),
        )

        self.col_names = []
        for group_name, group_values in self.amino_acid_property_groups:
            for i in range(1, 31):
                self.col_names.append('GearyAuto' + group_name + "_" + str(i))

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.col_names

    def _normalize_amino_acid_property(self, amino_acid_properties):
        """
        All of the amino acid indices are centralized and standardized before the calculation.
        Usage:
        result=NormalizeEachAAP(AAP)
        Input: AAP is a dict form containing the properties of 20 amino acids.
        Output: result is the a dict form containing the normalized properties
        of 20 amino acids.
        """
        assert len(amino_acid_properties) == 20, "There must be 20 amino acid properties."

        Result = {}

        for property_description, property_value in amino_acid_properties.items():
            Result[property_description] = (property_value - self._mean(amino_acid_properties.values())) / self._std(amino_acid_properties.values(), ddof=0)

        return Result

    def _mean(self, listvalue):
        """
        The mean value of the list data.
        """
        return sum(listvalue) / len(listvalue)

    def _std(self, listvalue, ddof=1):
        """
        The standard deviation of the list data.
        """
        import math
        mean = self._mean(listvalue)
        temp = [math.pow(i - mean, 2) for i in listvalue]
        res = math.sqrt(sum(temp) / (len(listvalue) - ddof))
        return res

    def calc(self, sequence):
        """ This function calculates the ncomposition of a sequence within a given alphabet.
        :param sequence:
        :param alphabet: list of kmers with the same length
        :param roundto:
        :return:
        """
        # Count the number of possible positions within the alphabet.
        #sequence_list = [sequence[i:i + len(self.alphabet_list[0])] for i in range(len(sequence) - (len(self.alphabet_list[0]) - 1))]
        #return [str(round(float(sequence_list.count(kmer)) / (len(sequence_list)), self.roundto)) for kmer in self.alphabet_list]
        # CalculateEachGearyAuto
        descriptor_vector = []
        for group_name, group_values in self.amino_acid_property_groups:
            # Generate titles
            # A dict containing amino acid properties.
            #normalized_aa_properties = NormalizeEachAAP(group_values)
            # Exchange amino acid for for their respective property values.

            cc = [group_values[amino_acid] for amino_acid in sequence]
            K = ((self._std(cc)) ** 2) * len(sequence) / (len(sequence) - 1)

            for i in range(1, 31):
                temp = 0
                for j in range(len(sequence) - i):
                    temp += (group_values[sequence[j]] - group_values[sequence[j + i]]) ** 2

                if K != 0:
                    if len(sequence) - i == 0:
                        vector_el = temp / (2 * (len(sequence))) / K
                    else:
                        vector_el = temp / (2 * (len(sequence) - i)) / K
                else:
                    vector_el = 0.0

                descriptor_vector.append(round(vector_el, self.roundto))


        return descriptor_vector


class PhysicoChemicalProperties:

    def __init__(self, roundto, allow_nonstandard=True):
        self.roundto = roundto

        self.allow_nonstandard = allow_nonstandard

        self.weight_dict = {
            "A": 89.0935,  "R": 174.2017, "N": 132.1184, "D": 133.1032, "C": 121.1590,
            "E": 147.1299, "Q": 146.1451, "G": 75.0669,  "H": 155.1552, "I": 131.1736,
            "L": 131.1736, "K": 146.1882, "M": 149.2124, "F": 165.1900, "P": 115.1310,
            "S": 105.0930, "T": 119.1197, "W": 204.2262, "Y": 181.1894, "V": 117.1469
        }

        self.wikipedia_pKas = {
            "C-terminal": 3.65,
            "N-terminal": 8.2,
            "C": 8.18,   # Cys, Cysteine
            "D": 3.9,    # Asp, Aspartic acid
            "E": 4.07,   # Glu, Glutamic acid
            "H": 6.04,   # His, Histidine
            "K": 10.54,  # Lys, Lysine
            "R": 12.48,  # Arg, Arginine
            "Y": 10.46   # Tyr, Tyrosine
        }

        # noinspection PyPackageRequirements
        self.physicochemical_groups = (
            ("charged_residues",           "DREKH"),
            ("hydrophillic_and_neutral",   "NQSTY"),
            ("basic_polar_or_pos_charged", "HKR"),
            ("acidic_or_neg_charged",      "DE"),
            ("aliphatic",                  "AGILV"),
            ("aromatic",                   "FWY"),
            ("small_DNT",                  "DNT"),
            ("tiny_AGPS",                  "AGPS"),
            ("large",                      "FRWY"),
            ("hydrophobic_and_aromatic",   "WF"),
            ("hydrophobic_and_neutral",    "ACGILMFPWV"),
            ("amidic",                     "NQ"),
            ("cyclic",                     "P"),
            ("hydroxylic",                 "ST"),
            ("sulfur",                     "CM"),
            ("h_bonding",                  "CDEHKNQRSTWY"),
            ("acidic_and_amide",           "DENQ"),
            ("ionizable",                  "DEHCYKR"),
            ("sulfer_bonding",             "C")
        )

        # This defines the physical property groups and names.
        self.physical_properties = (
            ("pI", self.peptideisoelectripoint),               # Find the isoelectric point or "pI".
            ("length", len),                              # Find the length of the peptide
            ("molecular_weight", self.peptidemolecularweight)  # Find the mass of the peptide
        )

        self.column_titles = [x[0] for x in self.physicochemical_groups]
        self.column_titles += [x[0] for x in self.physical_properties]

        self.average_weight = 0.0
        if self.allow_nonstandard:
            for el in self.weight_dict:
                self.average_weight += self.weight_dict[el]
            self.average_weight /= len(self.weight_dict)

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.column_titles

    def peptideisoelectripoint(self, prot_sequence):
        """
        @author: Tyler Weirick
        @date:   2013-6-26
        Naive calculation of isoelectric point. Based on information and
        algorithms from http://isoelectric.ovh.org

        Input: An amino acid sequence with amino acids represented as single
               letter charaters. Assumption is that data validation will be
               done before this step so no checking for non-standard amino
               acids, nucleic acid sequences, three letter codes, etc. will
               be done.
        Output: A float representing the isoelectric point of the given amino
                acid.
        Notes: I compared methods for counting amino acids. Using the built in
        count function is much faster

        Here are the results of a 100 itterations of the two methods
        With count() function: 0.000475883483886718 s
        Itterative counting  : 0.011758089065551758 s

        Itterative counting
        C,D,E,H,K,R,Y = 0,0,0,0,0,0,0
        for aa in prot_sequence:
            if   aa == "C":C+=1
            elif aa == "D":D+=1
            elif aa == "E":E+=1
            elif aa == "H":H+=1
            elif aa == "K":K+=1
            elif aa == "R":R+=1
            elif aa == "Y":Y+=1

        This makes sense as this the count() function is most likly implemented in C. Hoever,
        care should be taken when using on large strings. Although, I don't expect such a large amino
        acid could exist .
        :param prot_sequence:
        :return:
        """

        pKa_d = self.wikipedia_pKas

        # Just in case. Make sure all characters are upper case.
        prot_sequence = prot_sequence.upper()

        # Get the number of of each amino acid.
        C = prot_sequence.count("C")  # Cys, Cysteine
        D = prot_sequence.count("D")  # Asp, Aspartic acid
        E = prot_sequence.count("E")  # Glu, Glutamic acid
        H = prot_sequence.count("H")  # His, Histidine
        K = prot_sequence.count("K")  # Lys, Lysine
        R = prot_sequence.count("R")  # Arg, Arginine
        Y = prot_sequence.count("Y")  # Tyr, Tyrosine

        pH = 6.5  # Average pI
        pH_prev = 0.0
        pH_next = 14.0
        max_error = 0.001

        # Iterate until sign changes.
        while True:
            qn1 = -1/(1+pow(10, (pKa_d["C-terminal"]-pH)))  # C-terminal charge
            qp2 = 1/(1+pow(10,  (pH-pKa_d["N-terminal"])))  # N-terminal charge
            qn4 = -C/(1+pow(10, (pKa_d["C"]-pH)))  # C charge
            qn2 = -D/(1+pow(10, (pKa_d["D"]-pH)))  # D charge
            qn3 = -E/(1+pow(10, (pKa_d["E"]-pH)))  # E charge
            qp1 = H/(1+pow(10,  (pH-pKa_d["H"])))  # H charge
            qp3 = K/(1+pow(10,  (pH-pKa_d["K"])))  # K charge
            qp4 = R/(1+pow(10,  (pH-pKa_d["R"])))  # R charge
            qn5 = -Y/(1+pow(10, (pKa_d["Y"]-pH)))  # Y charge

            NQ = qn1 + qn2 + qn3 + qn4 + qn5 + qp1 + qp2 + qp3 + qp4

            temp = pH
            if NQ < 0:
                pH -= ((pH-pH_prev) / 2)
                pH_next = temp
            elif NQ > 0:
                pH -= ((pH-pH_next) / 2)
                pH_prev = temp

            if pH-pH_prev < max_error and pH_next-pH < max_error:
                break

        return pH

    def peptidemolecularweight(self, fasta_sequence):

        oxygen = 15.999
        hydrogen = 1.008
        fasta_sequence = fasta_sequence.upper()
        total_weight = 0
        for i in range(0, len(fasta_sequence)):
            # aa_char in fasta_sequence:
            # When a peptide is added to an existing chain, some atoms are removed.
            if fasta_sequence[i] in self.weight_dict:
                if i == 0:
                    total_weight += self.weight_dict[fasta_sequence[i]] - oxygen - hydrogen
                elif i == len(fasta_sequence) - 1:
                    total_weight += self.weight_dict[fasta_sequence[i]] - hydrogen
                else:
                    total_weight += self.weight_dict[fasta_sequence[i]] - oxygen - hydrogen * 2
            else:
                if self.allow_nonstandard:
                    total_weight += self.average_weight
                else:
                    assert False, "ERROR: %s not in standard amino acid dictionary." % fasta_sequence[i]

        return total_weight

    def calc(self, fasta_seq):
        # Make a temporary place to store output data,
        vector = []
        # Calculate AA group percentage properties.
        for group, bases in self.physicochemical_groups:
            # Count the numbers of amino acid belonging
            group_total_amino_acids = 0
            for amino_acid in bases:
                # .upper() could use this to set all data to upper case.
                # not sure if this is a good idea or not.
                group_total_amino_acids += fasta_seq.count(amino_acid)
            # group_total_amino_acids = sum([fasta_seq.count(amino_acid) for amino_acid in bases])
            # vector.append(round(float(group_total_amino_acids)/len(fasta_seq), ROUNDTO))
            vector.append(round(float(group_total_amino_acids) / len(fasta_seq), self.roundto))

        for group, function in self.physical_properties:
            vector.append(round(float(function(fasta_seq)), self.roundto))

        return vector


class NormalizedMoreauBrotoAutocorrelation:

    def __init__(self, roundto):
        self.roundto = roundto

        _Hydrophobicity = {
            "A": 0.02, "R": -0.42, "N": -0.77, "D": -1.04, "C": 0.77,
            "Q": -1.10, "E": -1.14, "G": -0.80, "H": 0.26, "I": 1.81,
            "L": 1.14, "K": -0.41, "M": 1.00, "F": 1.35, "P": -0.09,
            "S": -0.97, "T": -0.77, "W": 1.71, "Y": 1.11, "V": 1.13
        }

        _AvFlexibility = {
            "A": 0.357, "R": 0.529, "N": 0.463, "D": 0.511, "C": 0.346,
            "Q": 0.493, "E": 0.497, "G": 0.544, "H": 0.323, "I": 0.462,
            "L": 0.365, "K": 0.466, "M": 0.295, "F": 0.314, "P": 0.509,
            "S": 0.507, "T": 0.444, "W": 0.305, "Y": 0.420, "V": 0.386
        }
        _Polarizability = {
            "A": 0.046, "R": 0.291, "N": 0.134, "D": 0.105, "C": 0.128,
            "Q": 0.180, "E": 0.151, "G": 0.000, "H": 0.230, "I": 0.186,
            "L": 0.186, "K": 0.219, "M": 0.221, "F": 0.290, "P": 0.131,
            "S": 0.062, "T": 0.108, "W": 0.409, "Y": 0.298, "V": 0.140
        }

        _FreeEnergy = {
            "A": -0.368, "R": -1.03, "N": 0.0, "D": 2.06, "C": 4.53,
            "Q": 0.731, "E": 1.77, "G": -0.525, "H": 0.0, "I": 0.791,
            "L": 1.07, "K": 0.0, "M": 0.656, "F": 1.06, "P": -2.24,
            "S": -0.524, "T": 0.0, "W": 1.60, "Y": 4.91, "V": 0.401
        }

        _ResidueASA = {
            "A": 115.0, "R": 225.0, "N": 160.0, "D": 150.0, "C": 135.0,
            "Q": 180.0, "E": 190.0, "G": 75.0, "H": 195.0, "I": 175.0,
            "L": 170.0, "K": 200.0, "M": 185.0, "F": 210.0, "P": 145.0,
            "S": 115.0, "T": 140.0, "W": 255.0, "Y": 230.0, "V": 155.0
        }

        _ResidueVol = {
            "A": 52.6, "R": 109.1, "N": 75.7, "D": 68.4, "C": 68.3,
            "Q": 89.7, "E": 84.7, "G": 36.3, "H": 91.9, "I": 102.0,
            "L": 102.0, "K": 105.1, "M": 97.7, "F": 113.9, "P": 73.6,
            "S": 54.9, "T": 71.2, "W": 135.4, "Y": 116.2, "V": 85.1
        }
        _Steric = {
            "A": 0.52, "R": 0.68, "N": 0.76, "D": 0.76, "C": 0.62,
            "Q": 0.68, "E": 0.68, "G": 0.00, "H": 0.70, "I": 1.02,
            "L": 0.98, "K": 0.68, "M": 0.78, "F": 0.70, "P": 0.36,
            "S": 0.53, "T": 0.50, "W": 0.70, "Y": 0.70, "V": 0.76
        }

        _Mutability = {
            "A": 100.0, "R": 65.0, "N": 134.0, "D": 106.0, "C": 20.0,
            "Q": 93.0, "E": 102.0, "G": 49.0, "H": 66.0, "I": 96.0,
            "L": 40.0, "K": -56.0, "M": 94.0, "F": 41.0, "P": 56.0,
            "S": 120.0, "T": 97.0, "W": 18.0, "Y": 41.0, "V": 74.0
        }

        _Hydrophobicity = self._normalize_amino_acid_property(_Hydrophobicity)
        _AvFlexibility = self._normalize_amino_acid_property(_AvFlexibility)
        _Polarizability = self._normalize_amino_acid_property(_Polarizability)
        _FreeEnergy = self._normalize_amino_acid_property(_FreeEnergy)
        _ResidueASA = self._normalize_amino_acid_property(_ResidueASA)
        _ResidueVol = self._normalize_amino_acid_property(_ResidueVol)
        _Steric = self._normalize_amino_acid_property(_Steric)
        _Mutability = self._normalize_amino_acid_property(_Mutability)

        self.amino_acid_property_groups = (
            ('_Hydrophobicity', _Hydrophobicity),
            ('_AvFlexibility',  _AvFlexibility),
            ('_Polarizability', _Polarizability),
            ('_FreeEnergy',     _FreeEnergy),
            ('_ResidueASA',     _ResidueASA),
            ('_ResidueVol',     _ResidueVol),
            ('_Steric',         _Steric),
            ('_Mutability',     _Mutability),
        )

        self.col_names = []
        for group_name, group_values in self.amino_acid_property_groups:
            for i in range(1, 31):
                self.col_names.append('MoreauBrotoAuto' + group_name + "_" + str(i))

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.col_names

    def _normalize_amino_acid_property(self, amino_acid_properties):
        """
        All of the amino acid indices are centralized and standardized before the calculation.
        Usage:
        result=NormalizeEachAAP(AAP)
        Input: AAP is a dict form containing the properties of 20 amino acids.
        Output: result is the a dict form containing the normalized properties
        of 20 amino acids.
        """
        assert len(amino_acid_properties) == 20, "There must be 20 amino acid properties."

        Result = {}

        for property_description, property_value in amino_acid_properties.items():

            aa_properties_mean = self._mean(amino_acid_properties.values())
            aa_properties_std = self._std(amino_acid_properties.values(), ddof=0)

            Result[property_description] = (property_value - aa_properties_mean) / aa_properties_std

        return Result

    def _mean(self, listvalue):
        """
        The mean value of the list data.
        """
        return sum(listvalue) / len(listvalue)

    def _std(self, listvalue, ddof=1):
        """
        The standard deviation of the list data.
        """
        import math
        mean = self._mean(listvalue)
        temp = [math.pow(i - mean, 2) for i in listvalue]
        res = math.sqrt(sum(temp) / (len(listvalue) - ddof))
        return res

    def calc(self, sequence):
        """
        ####################################################################################
        you can use the function to compute MoreauBrotoAuto
        descriptors for different properties based on AADs.
        Usage:
        result=CalculateEachNormalizedMoreauBrotoAuto(protein,AAP,AAPName)
        Input: protein is a pure protein sequence.
        AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
        AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
        Output: result is a dict form containing 30 Normalized Moreau-Broto autocorrelation
        descriptors based on the given property.
        ####################################################################################
        This function calculates the ncomposition of a sequence within a given alphabet.
        :param sequence:
        :param alphabet: list of kmers with the same length
        :param roundto:
        :return:
        """
        # Count the number of possible positions within the alphabet.

        descriptor_vector = []
        for group_name, group_values in self.amino_acid_property_groups:
            # Generate titles
            # A dict containing amino acid properties.
            # normalized_aa_properties = NormalizeEachAAP(group_values)
            # Exchange amino acid for for their respective property values.
            for i in range(1, 31):
                temp = 0
                for j in range(len(sequence) - i):
                    #  temp = temp + AAPdic[ProteinSequence[j]] * AAPdic[ProteinSequence[j + 1]]
                    temp += (group_values[sequence[j]] * group_values[sequence[j + i]])

                if len(sequence) - i == 0:
                    vector_el = temp / len(sequence)
                else:
                    vector_el = temp / (len(sequence) - i)

                descriptor_vector.append(round(vector_el, self.roundto))

        return descriptor_vector


class MoranAutocorrelation:

    def __init__(self, roundto):
        self.roundto = roundto

        self.standard_amino_acids = [
            "A", "R", "N", "D", "C", "E", "Q", "G", "H", "I",
            "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"
        ]

        _Hydrophobicity = {
            "A": 0.02, "R": -0.42, "N": -0.77, "D": -1.04, "C": 0.77,
            "Q": -1.10, "E": -1.14, "G": -0.80, "H": 0.26, "I": 1.81,
            "L": 1.14, "K": -0.41, "M": 1.00, "F": 1.35, "P": -0.09,
            "S": -0.97, "T": -0.77, "W": 1.71, "Y": 1.11, "V": 1.13
        }

        _AvFlexibility = {
            "A": 0.357, "R": 0.529, "N": 0.463, "D": 0.511, "C": 0.346,
            "Q": 0.493, "E": 0.497, "G": 0.544, "H": 0.323, "I": 0.462,
            "L": 0.365, "K": 0.466, "M": 0.295, "F": 0.314, "P": 0.509,
            "S": 0.507, "T": 0.444, "W": 0.305, "Y": 0.420, "V": 0.386
        }
        _Polarizability = {
            "A": 0.046, "R": 0.291, "N": 0.134, "D": 0.105, "C": 0.128,
            "Q": 0.180, "E": 0.151, "G": 0.000, "H": 0.230, "I": 0.186,
            "L": 0.186, "K": 0.219, "M": 0.221, "F": 0.290, "P": 0.131,
            "S": 0.062, "T": 0.108, "W": 0.409, "Y": 0.298, "V": 0.140
        }

        _FreeEnergy = {
            "A": -0.368, "R": -1.03, "N": 0.0, "D": 2.06, "C": 4.53,
            "Q": 0.731, "E": 1.77, "G": -0.525, "H": 0.0, "I": 0.791,
            "L": 1.07, "K": 0.0, "M": 0.656, "F": 1.06, "P": -2.24,
            "S": -0.524, "T": 0.0, "W": 1.60, "Y": 4.91, "V": 0.401
        }

        _ResidueASA = {
            "A": 115.0, "R": 225.0, "N": 160.0, "D": 150.0, "C": 135.0,
            "Q": 180.0, "E": 190.0, "G": 75.0, "H": 195.0, "I": 175.0,
            "L": 170.0, "K": 200.0, "M": 185.0, "F": 210.0, "P": 145.0,
            "S": 115.0, "T": 140.0, "W": 255.0, "Y": 230.0, "V": 155.0
        }

        _ResidueVol = {
            "A": 52.6, "R": 109.1, "N": 75.7, "D": 68.4, "C": 68.3,
            "Q": 89.7, "E": 84.7, "G": 36.3, "H": 91.9, "I": 102.0,
            "L": 102.0, "K": 105.1, "M": 97.7, "F": 113.9, "P": 73.6,
            "S": 54.9, "T": 71.2, "W": 135.4, "Y": 116.2, "V": 85.1
        }
        _Steric = {
            "A": 0.52, "R": 0.68, "N": 0.76, "D": 0.76, "C": 0.62,
            "Q": 0.68, "E": 0.68, "G": 0.00, "H": 0.70, "I": 1.02,
            "L": 0.98, "K": 0.68, "M": 0.78, "F": 0.70, "P": 0.36,
            "S": 0.53, "T": 0.50, "W": 0.70, "Y": 0.70, "V": 0.76
        }

        _Mutability = {
            "A": 100.0, "R": 65.0, "N": 134.0, "D": 106.0, "C": 20.0,
            "Q": 93.0, "E": 102.0, "G": 49.0, "H": 66.0, "I": 96.0,
            "L": 40.0, "K": -56.0, "M": 94.0, "F": 41.0, "P": 56.0,
            "S": 120.0, "T": 97.0, "W": 18.0, "Y": 41.0, "V": 74.0
        }

        _Hydrophobicity = self._normalize_amino_acid_property(_Hydrophobicity)
        _AvFlexibility = self._normalize_amino_acid_property(_AvFlexibility)
        _Polarizability = self._normalize_amino_acid_property(_Polarizability)
        _FreeEnergy = self._normalize_amino_acid_property(_FreeEnergy)
        _ResidueASA = self._normalize_amino_acid_property(_ResidueASA)
        _ResidueVol = self._normalize_amino_acid_property(_ResidueVol)
        _Steric = self._normalize_amino_acid_property(_Steric)
        _Mutability = self._normalize_amino_acid_property(_Mutability)

        self.amino_acid_property_groups = (
            ('_Hydrophobicity', _Hydrophobicity),
            ('_AvFlexibility',  _AvFlexibility),
            ('_Polarizability', _Polarizability),
            ('_FreeEnergy',     _FreeEnergy),
            ('_ResidueASA',     _ResidueASA),
            ('_ResidueVol',     _ResidueVol),
            ('_Steric',         _Steric),
            ('_Mutability',     _Mutability),
        )

        self.col_names = []
        for group_name, group_values in self.amino_acid_property_groups:
            for i in range(1, 31):
                self.col_names.append('MoranAuto' + group_name + "_" + str(i))

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.col_names

    def _normalize_amino_acid_property(self, amino_acid_properties):
        """
        All of the amino acid indices are centralized and standardized before the calculation.
        Usage:
        result=NormalizeEachAAP(AAP)
        Input: AAP is a dict form containing the properties of 20 amino acids.
        Output: result is the a dict form containing the normalized properties
        of 20 amino acids.
        """
        assert len(amino_acid_properties) == 20, "There must be 20 amino acid properties."

        Result = {}

        for property_description, property_value in amino_acid_properties.items():

            aa_properties_mean = self._mean(amino_acid_properties.values())
            aa_properties_std = self._std(amino_acid_properties.values(), ddof=0)

            Result[property_description] = (property_value - aa_properties_mean) / aa_properties_std

        return Result

    def _mean(self, listvalue):
        """
        The mean value of the list data.
        """
        return sum(listvalue) / len(listvalue)

    def _std(self, listvalue, ddof=1):
        """
        The standard deviation of the list data.
        """
        import math
        mean = self._mean(listvalue)
        temp = [math.pow(i - mean, 2) for i in listvalue]
        res = math.sqrt(sum(temp) / (len(listvalue) - ddof))
        return res

    def calc(self, sequence):
        """
        ####################################################################################
        you can use the function to compute MoreauBrotoAuto
        descriptors for different properties based on AADs.
        Usage:
        result=CalculateEachNormalizedMoreauBrotoAuto(protein,AAP,AAPName)
        Input: protein is a pure protein sequence.
        AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
        AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
        Output: result is a dict form containing 30 Normalized Moreau-Broto autocorrelation
        descriptors based on the given property.
        ####################################################################################
        This function calculates the ncomposition of a sequence within a given alphabet.
        :param sequence:
        :param alphabet: list of kmers with the same length
        :param roundto:
        :return:
        """
        # Count the number of possible positions within the alphabet.

        descriptor_vector = []
        for group_name, group_values in self.amino_acid_property_groups:
            cds = 0
            for standard_aa in self.standard_amino_acids:
                cds += (sequence.count(standard_aa)) * (group_values[standard_aa])

            p_mean = cds / len(sequence)

            # Exchange amino acid for for their respective property values.
            cc = [group_values[amino_acid] for amino_acid in sequence]
            K = (self._std(cc, ddof=0)) ** 2

            for i in range(1, 31):
                temp = 0
                for j in range(len(sequence) - i):
                    temp += (group_values[sequence[j]] - p_mean) * (group_values[sequence[j + i]] - p_mean)

                if len(sequence) - i == 0:
                    # tmp_result['MoranAuto' + AAPName + str(i)] = round(temp / (len(ProteinSequence)) / K, 3)
                    vector_el = temp / len(sequence) / K
                else:
                    # tmp_result['MoranAuto' + AAPName + str(i)] = round(temp / (len(ProteinSequence) - i) / K, 3)
                    vector_el = temp / (len(sequence) - i) / K

                descriptor_vector.append(round(vector_el, self.roundto))

        return descriptor_vector


class PseudoAminoAcidComposition:
    """
    #######################################################################################
    Computing all of type I pseudo-amino acid compostion descriptors based on three given
    properties. Note that the number of PAAC strongly depends on the lamda value. if lamda
    = 20, we can obtain 20 + 20 = 40 PAAC descriptors. The size of these values depends on the
    choice of lamda and weight simultaneously.
    AAP=[_Hydrophobicity,_hydrophilicity,_residuemass]
    Usage:
    result = _GetAPseudoAAC(protein, lamda, weight)
    Input: protein is a pure protein sequence.
    lamda factor reflects the rank of correlation and is a non-Negative integer, such as 15.
    Note that (1)lamda should NOT be larger than the length of input protein sequence;
    (2) lamda must be non-Negative integer, such as 0, 1, 2, ...; (3) when lamda =0, the
    output of PseAA server is the 20-D amino acid composition.
    weight factor is designed for the users to put weight on the additional PseAA components
    with respect to the conventional AA components. The user can select any value within the
    region from 0.05 to 0.7 for the weight factor.
    Output: result is a dict form containing calculated 20+lamda PAAC descriptors.
    ########################################################################################
    res={}
    res.update(_GetPseudoAAC1(ProteinSequence,lamda=lamda,weight=weight))
    res.update(_GetPseudoAAC2(ProteinSequence,lamda=lamda,weight=weight))
    return res
    """

    def __init__(self, lamda=10, weight=0.05, roundto=5):
        self.lamda = lamda
        self.weight = weight
        self.roundto = roundto

        self.standard_amino_acids = [
            "A", "R", "N", "D", "C", "E", "Q", "G", "H", "I",
            "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"
        ]

        _hydrophobicity = {
            "A": 0.62,  "R": -2.53, "N": -0.78, "D": -0.90, "C": 0.29, "Q": -0.85, "E": -0.74, "G": 0.48,
            "H": -0.40, "I": 1.38,  "L": 1.06,  "K": -1.50, "M": 0.64, "F": 1.19,  "P": 0.12,  "S": -0.18,
            "T": -0.05, "W": 0.81,  "Y": 0.26,  "V": 1.08
        }

        _hydrophilicity = {
            "A": -0.5, "R": 3.0,  "N": 0.2, "D": 3.0,  "C": -1.0, "Q": 0.2, "E": 3.0, "G": 0.0,  "H": -0.5,
            "I": -1.8, "L": -1.8, "K": 3.0, "M": -1.3, "F": -2.5, "P": 0.0, "S": 0.3, "T": -0.4, "W": -3.4,
            "Y": -2.3, "V": -1.5
        }

        _residuemass = {
            "A": 15.0, "R": 101.0, "N": 58.0, "D": 59.0, "C": 47.0, "Q": 72.0, "E": 73.0, "G": 1.000, "H": 82.0,
            "I": 57.0, "L": 57.0,  "K": 73.0, "M": 75.0, "F": 91.0, "P": 42.0, "S": 31.0, "T": 45.0,  "W": 130.0,
            "Y": 107.0, "V": 43.0
        }

        _pK1 = {
            "A": 2.35, "C": 1.71, "D": 1.88, "E": 2.19, "F": 2.58, "G": 2.34, "H": 1.78, "I": 2.32, "K": 2.20,
            "L": 2.36, "M": 2.28, "N": 2.18, "P": 1.99, "Q": 2.17, "R": 2.18, "S": 2.21, "T": 2.15, "V": 2.29,
            "W": 2.38, "Y": 2.20
        }

        _pK2 = {
            "A": 9.87, "C": 10.78, "D": 9.60, "E": 9.67, "F": 9.24, "G": 9.60, "H": 8.97, "I": 9.76, "K": 8.90,
            "L": 9.60, "M": 9.21, "N": 9.09, "P": 10.6, "Q": 9.13, "R": 9.09, "S": 9.15, "T": 9.12, "V": 9.74,
            "W": 9.39, "Y": 9.11
        }

        _pI = {
            "A": 6.11, "C": 5.02, "D": 2.98,  "E": 3.08, "F": 5.91, "G": 6.06, "H": 7.64,  "I": 6.04, "K": 9.47,
            "L": 6.04, "M": 5.74, "N": 10.76, "P": 6.30, "Q": 5.65, "R": 10.76, "S": 5.68, "T": 5.60, "V": 6.02,
            "W": 5.88, "Y": 5.63
        }

        self.normalized_hydrophobicity = self._normalize_amino_acid_property(_hydrophobicity)
        self.normalized_hydrophilicity = self._normalize_amino_acid_property(_hydrophilicity)

        self.col_names = []
        for index, i in enumerate(self.standard_amino_acids):
            self.col_names.append('APAAC' + str(index + 1))

        for index in range(20, 20 + 2 * lamda):
            self.col_names.append('PAAC' + str(index + 1))

    def _mean(self, listvalue):
        """
        The mean value of the list data.
        """
        return sum(listvalue) / len(listvalue)

    def _std(self, listvalue, ddof=1):
        """
        The standard deviation of the list data.
        """
        import math
        mean = self._mean(listvalue)
        temp = [math.pow(i - mean, 2) for i in listvalue]
        res = math.sqrt(sum(temp) / (len(listvalue) - ddof))
        return res

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        return self.col_names

    def _normalize_amino_acid_property(self, amino_acid_properties):
        """
        All of the amino acid indices are centralized and standardized before the calculation.
        Usage:
        result=NormalizeEachAAP(AAP)
        Input: AAP is a dict form containing the properties of 20 amino acids.
        Output: result is the a dict form containing the normalized properties
        of 20 amino acids.
        """
        assert len(amino_acid_properties) == 20, "There must be 20 amino acid properties."

        Result = {}

        for property_description, property_value in amino_acid_properties.items():
            aa_properties_mean = self._mean(amino_acid_properties.values())
            aa_properties_std = self._std(amino_acid_properties.values(), ddof=0)

            Result[property_description] = (property_value - aa_properties_mean) / aa_properties_std

        return Result

    def calc(self, sequence):
        #res = {}
        #res.update(_GetPseudoAAC1(sequence, lamda=self.lamda, weight=self.weight))

        """
        #############################################################################################
        def GetPseudoAAC1(ProteinSequence,lamda=30,weight=0.05,AAP=[]):
            rightpart=0.0
            for i in range(lamda):
                rightpart=rightpart+GetSequenceOrderCorrelationFactor(ProteinSequence,i+1,AAP)
            AAC=GetAAComposition(ProteinSequence)
            result={}
            temp=1+weight*rightpart
            for index,i in enumerate(AALetter):
                result['PAAC'+str(index+1)]=round(AAC[i]/temp,3)
            return result
                :param sequence:
                :return:
        """

        seq_len = len(sequence)
        seq_len_float = float(seq_len)
        result = []
        rightpart = 0.0
        for i in range(self.lamda):
            #rightpart = rightpart + sum(GetSequenceOrderCorrelationFactorForAPAAC(ProteinSequence, k=i + 1))
            k = i + 1

            resHydrophobicity = 0
            reshydrophilicity = 0

            for i in range(seq_len - k):
                Ri = sequence[i]
                Rj = sequence[i + k]

                resHydrophobicity += self.normalized_hydrophobicity[Ri] * self.normalized_hydrophobicity[Rj]  # theta1
                reshydrophilicity += self.normalized_hydrophilicity[Ri] * self.normalized_hydrophilicity[Rj]  # theta2

            rightpart += round(resHydrophobicity / (seq_len - k), self.roundto)
            rightpart += round(reshydrophilicity / (seq_len - k), self.roundto)

        aa_comp = [round(100 * sequence.count(aa) / seq_len_float, self.roundto) for aa in self.standard_amino_acids]

        temp = 1 + self.weight * rightpart
        for index, i in enumerate(self.standard_amino_acids):
            #result['APAAC' + str(index + 1)] = round(aa_comp[i] / temp, 3)
            result.append(round(aa_comp[index] / temp, self.roundto))

        rightpart = []
        for i in range(self.lamda):
            #temp = GetSequenceOrderCorrelationFactorForAPAAC(sequence, k=i + 1)
            k = i + 1

            resHydrophobicity = 0
            reshydrophilicity = 0

            for i in range(seq_len - k):
                Ri = sequence[i]
                Rj = sequence[i + k]

                resHydrophobicity += self.normalized_hydrophobicity[Ri] * self.normalized_hydrophobicity[Rj]  # theta1
                reshydrophilicity += self.normalized_hydrophilicity[Ri] * self.normalized_hydrophilicity[Rj]  # theta2

            rightpart.append(resHydrophobicity)
            rightpart.append(resHydrophobicity)

        temp = 1 + self.weight * sum(rightpart)

        for index in range(20, 20 + 2 * self.lamda):
            result.append(round(self.weight * rightpart[index - 20] / temp * 100, self.roundto))
        return result


#def CompositionTransitionDistribution():
#    pass  # @TODO
#def sequenceordercouplingnumbers():
#    pass  # @TODO
#def quasisequenceorder():
#    pass  # @TODO
#def amphiphilicpseudoaminoacidcomposition():
#    pass  # @TODO


"""
#########################################################################################
Instead of using the conventional 20-D amino acid composition to represent the sample
of a protein, Prof. Kuo-Chen Chou proposed the pseudo amino acid (PseAA) composition
in order for inluding the sequence-order information. Based on the concept of Chou's
pseudo amino acid composition, the server PseAA was designed in a flexible way, allowing
users to generate various kinds of pseudo amino acid composition for a given protein
sequence by selecting different parameters and their combinations. This module aims at
computing two types of PseAA descriptors: Type I and Type II.
You can freely use and distribute it. If you have any problem, you could contact
with us timely.
References:
[1]: Kuo-Chen Chou. Prediction of Protein Cellular Attributes Using Pseudo-Amino Acid
Composition. PROTEINS: Structure, Function, and Genetics, 2001, 43: 246-255.
[2]: http://www.csbio.sjtu.edu.cn/bioinf/PseAAC/
[3]: http://www.csbio.sjtu.edu.cn/bioinf/PseAAC/type2.htm
[4]: Kuo-Chen Chou. Using amphiphilic pseudo amino acid composition to predict enzyme
subfamily classes. Bioinformatics, 2005,21,10-19.
Authors: Dongsheng Cao and Yizeng Liang.
Date: 2012.9.2
Email: oriental-cds@163.com
The hydrophobicity values are from JACS, 1962, 84: 4240-4246. (C. Tanford).
The hydrophilicity values are from PNAS, 1981, 78:3824-3828 (T.P.Hopp & K.R.Woods).
The side-chain mass for each of the 20 amino acids.
CRC Handbook of Chemistry and Physics, 66th ed., CRC Press, Boca Raton, Florida (1985).
R.M.C. Dawson, D.C. Elliott, W.H. Elliott, K.M. Jones, Data for Biochemical Research 3rd ed.,
Clarendon Press Oxford (1986).

#########################################################################################
"""


'''
def _mean(listvalue):
    """
    ########################################################################################
    The mean value of the list data.
    Usage:
    result=_mean(listvalue)
    ########################################################################################
    """
    return sum(listvalue)/len(listvalue)


def _std(listvalue, ddof=1):
    """
    ########################################################################################
    The standard deviation of the list data.
    Usage:
    result=_std(listvalue)
    ########################################################################################
    """
    mean=_mean(listvalue)
    temp=[math.pow(i-mean,2) for i in listvalue]
    res=math.sqrt(sum(temp)/(len(listvalue)-ddof))
    return res


def NormalizeEachAAP(AAP):
    """
    ########################################################################################
    All of the amino acid indices are centralized and
    standardized before the calculation.
    Usage:
    result=NormalizeEachAAP(AAP)
    Input: AAP is a dict form containing the properties of 20 amino acids.
    Output: result is the a dict form containing the normalized properties
    of 20 amino acids.
    ########################################################################################
    """
    if len(AAP.values())!=20:
        print('You can not input the correct number of properities of Amino acids!')
    else:
        Result={}
        for i,j in AAP.items():
            Result[i]=(j-_mean(AAP.values()))/_std(AAP.values(),ddof=0)
    return Result


def _GetCorrelationFunction(Ri='S',Rj='D',AAP=[_Hydrophobicity,_hydrophilicity,_residuemass]):
    """
    ########################################################################################
    Computing the correlation between two given amino acids using the above three
    properties.
    Usage:
    result=_GetCorrelationFunction(Ri,Rj)
    Input: Ri and Rj are the amino acids, respectively.
    Output: result is the correlation value between two amino acids.
    ########################################################################################
    """
    Hydrophobicity=NormalizeEachAAP(AAP[0])
    hydrophilicity=NormalizeEachAAP(AAP[1])
    residuemass=NormalizeEachAAP(AAP[2])
    theta1=math.pow(Hydrophobicity[Ri]-Hydrophobicity[Rj],2)
    theta2=math.pow(hydrophilicity[Ri]-hydrophilicity[Rj],2)
    theta3=math.pow(residuemass[Ri]-residuemass[Rj],2)
    theta=round((theta1+theta2+theta3)/3.0,3)
    return theta


def _GetSequenceOrderCorrelationFactor(ProteinSequence,k=1):
    """
    ########################################################################################
    Computing the Sequence order correlation factor with gap equal to k based on
    [_Hydrophobicity,_hydrophilicity,_residuemass].
    Usage:
    result=_GetSequenceOrderCorrelationFactor(protein,k)
    Input: protein is a pure protein sequence.
    k is the gap.
    Output: result is the correlation factor value with the gap equal to k.
    ########################################################################################
    """
    LengthSequence=len(ProteinSequence)
    res=[]
    for i in range(LengthSequence-k):
        AA1=ProteinSequence[i]
        AA2=ProteinSequence[i+k]
        res.append(_GetCorrelationFunction(AA1,AA2))
    result=round(sum(res)/(LengthSequence-k),3)
    return result


def GetAAComposition(ProteinSequence):

    """
    ########################################################################################
    Calculate the composition of Amino acids
    for a given protein sequence.
    Usage:
    result=CalculateAAComposition(protein)
    Input: protein is a pure protein sequence.
    Output: result is a dict form containing the composition of
    20 amino acids.
    ########################################################################################
    """
    LengthSequence=len(ProteinSequence)
    Result={}
    for i in AALetter:
        Result[i] = round(float(ProteinSequence.count(i))/LengthSequence*100,3)
    return Result


def _GetCorrelationFunctionForAPAAC(Ri='S',Rj='D',AAP=[_Hydrophobicity,_hydrophilicity]):
    """
    ########################################################################################
    Computing the correlation between two given amino acids using the above two
    properties for APAAC (type II PseAAC).
    Usage:
    result=_GetCorrelationFunctionForAPAAC(Ri,Rj)
    Input: Ri and Rj are the amino acids, respectively.
    Output: result is the correlation value between two amino acids.
    ########################################################################################
    """
    Hydrophobicity=NormalizeEachAAP(AAP[0])
    hydrophilicity=NormalizeEachAAP(AAP[1])
    theta1=round(Hydrophobicity[Ri]*Hydrophobicity[Rj],3)
    theta2=round(hydrophilicity[Ri]*hydrophilicity[Rj],3)

    return theta1, theta2


def GetSequenceOrderCorrelationFactorForAPAAC(ProteinSequence,k=1):
    """
    ########################################################################################
    Computing the Sequence order correlation factor with gap equal to k based on
    [_Hydrophobicity,_hydrophilicity] for APAAC (type II PseAAC) .
    Usage:
    result=GetSequenceOrderCorrelationFactorForAPAAC(protein,k)
    Input: protein is a pure protein sequence.
    k is the gap.
    Output: result is the correlation factor value with the gap equal to k.
    ########################################################################################
    """
    LengthSequence=len(ProteinSequence)
    resHydrophobicity=[]
    reshydrophilicity=[]
    for i in range(LengthSequence-k):
        AA1=ProteinSequence[i]
        AA2=ProteinSequence[i+k]
        temp=_GetCorrelationFunctionForAPAAC(AA1,AA2)
        resHydrophobicity.append(temp[0])
        reshydrophilicity.append(temp[1])
    result=[]
    result.append(round(sum(resHydrophobicity)/(LengthSequence-k),3))
    result.append(round(sum(reshydrophilicity)/(LengthSequence-k),3))
    return result


def GetAPseudoAAC1(ProteinSequence,lamda=30,weight=0.5):
    """
    ########################################################################################
    Computing the first 20 of type II pseudo-amino acid compostion descriptors based on
    [_Hydrophobicity,_hydrophilicity].
    ########################################################################################
    """
    rightpart=0.0
    for i in range(lamda):
        rightpart=rightpart+sum(GetSequenceOrderCorrelationFactorForAPAAC(ProteinSequence,k=i+1))
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*rightpart
    for index,i in enumerate(AALetter):
        result['APAAC'+str(index+1)]=round(AAC[i]/temp,3)
    return result


def GetAPseudoAAC2(ProteinSequence,lamda=30,weight=0.5):
    """
    #######################################################################################
    Computing the last lamda of type II pseudo-amino acid compostion descriptors based on
    [_Hydrophobicity,_hydrophilicity].
    #######################################################################################
    """
    rightpart=[]
    for i in range(lamda):
        temp=GetSequenceOrderCorrelationFactorForAPAAC(ProteinSequence,k=i+1)
        rightpart.append(temp[0])
        rightpart.append(temp[1])
        result={}
    temp=1+weight*sum(rightpart)
    for index in range(20,20+2*lamda):
        result['PAAC'+str(index+1)]=round(weight*rightpart[index-20]/temp*100,3)
    return result
#############################################################################################
def GetAPseudoAAC(ProteinSequence,lamda=30,weight=0.5):
    """
    #######################################################################################
    Computing all of type II pseudo-amino acid compostion descriptors based on the given
    properties. Note that the number of PAAC strongly depends on the lamda value. if lamda
    = 20, we can obtain 20+20=40 PAAC descriptors. The size of these values depends on the
    choice of lamda and weight simultaneously.
    Usage:
    result=GetAPseudoAAC(protein,lamda,weight)
    Input: protein is a pure protein sequence.
    lamda factor reflects the rank of correlation and is a non-Negative integer, such as 15.
    Note that (1)lamda should NOT be larger than the length of input protein sequence;
    (2) lamda must be non-Negative integer, such as 0, 1, 2, ...; (3) when lamda =0, the
    output of PseAA server is the 20-D amino acid composition.
    weight factor is designed for the users to put weight on the additional PseAA components
    with respect to the conventional AA components. The user can select any value within the
    region from 0.05 to 0.7 for the weight factor.
    Output: result is a dict form containing calculated 20+lamda PAAC descriptors.
    #######################################################################################
    """
    res={}
    res.update(GetAPseudoAAC1(ProteinSequence,lamda=lamda,weight=weight))
    res.update(GetAPseudoAAC2(ProteinSequence,lamda=lamda,weight=weight))
    return res
#############################################################################################
#############################################################################################
##################################Type I descriptors#########################################
####################### Pseudo-Amino Acid Composition descriptors############################
#############################based on different properties###################################
#############################################################################################
#############################################################################################
def GetCorrelationFunction(Ri='S',Rj='D',AAP=[]):
    """
    ########################################################################################
    Computing the correlation between two given amino acids using the given
    properties.
    Usage:
    result=GetCorrelationFunction(Ri,Rj,AAP)
    Input: Ri and Rj are the amino acids, respectively.
    AAP is a list form containing the properties, each of which is a dict form.
    Output: result is the correlation value between two amino acids.
    ########################################################################################
    """
    NumAAP=len(AAP)
    theta=0.0
    for i in range(NumAAP):
        temp=NormalizeEachAAP(AAP[i])
        theta=theta+math.pow(temp[Ri]-temp[Rj],2)
    result=round(theta/NumAAP,3)
    return result
#############################################################################################
def GetSequenceOrderCorrelationFactor(ProteinSequence,k=1,AAP=[]):
    """
    ########################################################################################
    Computing the Sequence order correlation factor with gap equal to k based on
    the given properities.
    Usage:
    result=GetSequenceOrderCorrelationFactor(protein,k,AAP)
    Input: protein is a pure protein sequence.
    k is the gap.
    AAP is a list form containing the properties, each of which is a dict form.
    Output: result is the correlation factor value with the gap equal to k.
    ########################################################################################
    """
    LengthSequence=len(ProteinSequence)
    res=[]
    for i in range(LengthSequence-k):
        AA1=ProteinSequence[i]
        AA2=ProteinSequence[i+k]
        res.append(GetCorrelationFunction(AA1,AA2,AAP))
    result=round(sum(res)/(LengthSequence-k),3)
    return result
#############################################################################################
def GetPseudoAAC1(ProteinSequence,lamda=30,weight=0.05,AAP=[]):
    """
    #######################################################################################
    Computing the first 20 of type I pseudo-amino acid compostion descriptors based on the given
    properties.
    ########################################################################################
    """
    rightpart=0.0
    for i in range(lamda):
        rightpart=rightpart+GetSequenceOrderCorrelationFactor(ProteinSequence,i+1,AAP)

    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*rightpart
    for index,i in enumerate(AALetter):
        result['PAAC'+str(index+1)]=round(AAC[i]/temp,3)
    return result

#############################################################################################
def GetPseudoAAC2(ProteinSequence,lamda=30,weight=0.05,AAP=[]):
    """
    #######################################################################################
    Computing the last lamda of type I pseudo-amino acid compostion descriptors based on the given
    properties.
    ########################################################################################
    """
    rightpart=[]
    for i in range(lamda):
        rightpart.append(GetSequenceOrderCorrelationFactor(ProteinSequence,i+1,AAP))
    result={}
    temp=1+weight*sum(rightpart)
    for index in range(20,20+lamda):
        result['PAAC'+str(index+1)]=round(weight*rightpart[index-20]/temp*100,3)
    return result
#############################################################################################

def GetPseudoAAC(ProteinSequence,lamda=30,weight=0.05,AAP=[]):
    """
    #######################################################################################
    Computing all of type I pseudo-amino acid compostion descriptors based on the given
    properties. Note that the number of PAAC strongly depends on the lamda value. if lamda
    = 20, we can obtain 20+20=40 PAAC descriptors. The size of these values depends on the
    choice of lamda and weight simultaneously. You must specify some properties into AAP.
    Usage:
    result=GetPseudoAAC(protein,lamda,weight)
    Input: protein is a pure protein sequence.
    lamda factor reflects the rank of correlation and is a non-Negative integer, such as 15.
    Note that (1)lamda should NOT be larger than the length of input protein sequence;
    (2) lamda must be non-Negative integer, such as 0, 1, 2, ...; (3) when lamda =0, the
    output of PseAA server is the 20-D amino acid composition.
    weight factor is designed for the users to put weight on the additional PseAA components
    with respect to the conventional AA components. The user can select any value within the
    region from 0.05 to 0.7 for the weight factor.
    AAP is a list form containing the properties, each of which is a dict form.
    Output: result is a dict form containing calculated 20+lamda PAAC descriptors.
    ########################################################################################
    """
    res={}
    res.update(GetPseudoAAC1(ProteinSequence, lamda, weight, AAP))
    res.update(GetPseudoAAC2(ProteinSequence, lamda, weight, AAP))
    return res

'''


class SequenceOrderCouplingNumberTotal:

    def __init__(self, maxlag=30, d=1):

        self.maxlag = maxlag
        self.d = d
        self.standard_amino_acids = [
            "A", "R", "N", "D", "C", "E", "Q", "G", "H", "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"
        ]

        # Distance is the Schneider-Wrede physicochemical distance matrix used by Chou et. al.
        self._distance1 = {
            "GW": 0.923, "GV": 0.464, "GT": 0.272, "GS": 0.158, "GR": 1.0, "GQ": 0.467, "GP": 0.323, "GY": 0.728,
            "GG": 0.0, "GF": 0.727, "GE": 0.807, "GD": 0.776, "GC": 0.312, "GA": 0.206, "GN": 0.381, "GM": 0.557,
            "GL": 0.591, "GK": 0.894, "GI": 0.592, "GH": 0.769, "ME": 0.879, "MD": 0.932, "MG": 0.569,
            "MF": 0.182, "MA": 0.383, "MC": 0.276, "MM": 0.0, "ML": 0.062, "MN": 0.447, "MI": 0.058, "MH": 0.648,
            "MK": 0.884, "MT": 0.358, "MW": 0.391, "MV": 0.12, "MQ": 0.372, "MP": 0.285, "MS": 0.417, "MR": 1.0,
            "MY": 0.255, "FP": 0.42, "FQ": 0.459, "FR": 1.0, "FS": 0.548, "FT": 0.499, "FV": 0.252, "FW": 0.207,
            "FY": 0.179, "FA": 0.508, "FC": 0.405, "FD": 0.977, "FE": 0.918, "FF": 0.0, "FG": 0.69, "FH": 0.663,
            "FI": 0.128, "FK": 0.903, "FL": 0.131, "FM": 0.169, "FN": 0.541, "SY": 0.615, "SS": 0.0, "SR": 1.0,
            "SQ": 0.358, "SP": 0.181, "SW": 0.827, "SV": 0.342, "ST": 0.174, "SK": 0.883, "SI": 0.478,
            "SH": 0.718, "SN": 0.289, "SM": 0.44, "SL": 0.474, "SC": 0.185, "SA": 0.1, "SG": 0.17, "SF": 0.622,
            "SE": 0.812, "SD": 0.801, "YI": 0.23, "YH": 0.678, "YK": 0.904, "YM": 0.268, "YL": 0.219, "YN": 0.512,
            "YA": 0.587, "YC": 0.478, "YE": 0.932, "YD": 1.0, "YG": 0.782, "YF": 0.202, "YY": 0.0, "YQ": 0.404,
            "YP": 0.444, "YS": 0.612, "YR": 0.995, "YT": 0.557, "YW": 0.244, "YV": 0.328, "LF": 0.139,
            "LG": 0.596, "LD": 0.944, "LE": 0.892, "LC": 0.296, "LA": 0.405, "LN": 0.452, "LL": 0.0, "LM": 0.062,
            "LK": 0.893, "LH": 0.653, "LI": 0.013, "LV": 0.133, "LW": 0.341, "LT": 0.397, "LR": 1.0, "LS": 0.443,
            "LP": 0.309, "LQ": 0.376, "LY": 0.205, "RT": 0.808, "RV": 0.914, "RW": 1.0, "RP": 0.796, "RQ": 0.668,
            "RR": 0.0, "RS": 0.86, "RY": 0.859, "RD": 0.305, "RE": 0.225, "RF": 0.977, "RG": 0.928, "RA": 0.919,
            "RC": 0.905, "RL": 0.92, "RM": 0.908, "RN": 0.69, "RH": 0.498, "RI": 0.929, "RK": 0.141, "VH": 0.649,
            "VI": 0.135, "EM": 0.83, "EL": 0.854, "EN": 0.599, "EI": 0.86, "EH": 0.406, "EK": 0.143, "EE": 0.0,
            "ED": 0.133, "EG": 0.779, "EF": 0.932, "EA": 0.79, "EC": 0.788, "VM": 0.12, "EY": 0.837, "VN": 0.38,
            "ET": 0.682, "EW": 1.0, "EV": 0.824, "EQ": 0.598, "EP": 0.688, "ES": 0.726, "ER": 0.234, "VP": 0.212,
            "VQ": 0.339, "VR": 1.0, "VT": 0.305, "VW": 0.472, "KC": 0.871, "KA": 0.889, "KG": 0.9, "KF": 0.957,
            "KE": 0.149, "KD": 0.279, "KK": 0.0, "KI": 0.899, "KH": 0.438, "KN": 0.667, "KM": 0.871, "KL": 0.892,
            "KS": 0.825, "KR": 0.154, "KQ": 0.639, "KP": 0.757, "KW": 1.0, "KV": 0.882, "KT": 0.759, "KY": 0.848,
            "DN": 0.56, "DL": 0.841, "DM": 0.819, "DK": 0.249, "DH": 0.435, "DI": 0.847, "DF": 0.924, "DG": 0.697,
            "DD": 0.0, "DE": 0.124, "DC": 0.742, "DA": 0.729, "DY": 0.836, "DV": 0.797, "DW": 1.0, "DT": 0.649,
            "DR": 0.295, "DS": 0.667, "DP": 0.657, "DQ": 0.584, "QQ": 0.0, "QP": 0.272, "QS": 0.461, "QR": 1.0,
            "QT": 0.389, "QW": 0.831, "QV": 0.464, "QY": 0.522, "QA": 0.512, "QC": 0.462, "QE": 0.861,
            "QD": 0.903, "QG": 0.648, "QF": 0.671, "QI": 0.532, "QH": 0.765, "QK": 0.881, "QM": 0.505,
            "QL": 0.518, "QN": 0.181, "WG": 0.829, "WF": 0.196, "WE": 0.931, "WD": 1.0, "WC": 0.56, "WA": 0.658,
            "WN": 0.631, "WM": 0.344, "WL": 0.304, "WK": 0.892, "WI": 0.305, "WH": 0.678, "WW": 0.0, "WV": 0.418,
            "WT": 0.638, "WS": 0.689, "WR": 0.968, "WQ": 0.538, "WP": 0.555, "WY": 0.204, "PR": 1.0, "PS": 0.196,
            "PP": 0.0, "PQ": 0.228, "PV": 0.244, "PW": 0.72, "PT": 0.161, "PY": 0.481, "PC": 0.179, "PA": 0.22,
            "PF": 0.515, "PG": 0.376, "PD": 0.852, "PE": 0.831, "PK": 0.875, "PH": 0.696, "PI": 0.363,
            "PN": 0.231, "PL": 0.357, "PM": 0.326, "CK": 0.887, "CI": 0.304, "CH": 0.66, "CN": 0.324, "CM": 0.277,
            "CL": 0.301, "CC": 0.0, "CA": 0.114, "CG": 0.32, "CF": 0.437, "CE": 0.838, "CD": 0.847, "CY": 0.457,
            "CS": 0.176, "CR": 1.0, "CQ": 0.341, "CP": 0.157, "CW": 0.639, "CV": 0.167, "CT": 0.233, "IY": 0.213,
            "VA": 0.275, "VC": 0.165, "VD": 0.9, "VE": 0.867, "VF": 0.269, "VG": 0.471, "IQ": 0.383, "IP": 0.311,
            "IS": 0.443, "IR": 1.0, "VL": 0.134, "IT": 0.396, "IW": 0.339, "IV": 0.133, "II": 0.0, "IH": 0.652,
            "IK": 0.892, "VS": 0.322, "IM": 0.057, "IL": 0.013, "VV": 0.0, "IN": 0.457, "IA": 0.403, "VY": 0.31,
            "IC": 0.296, "IE": 0.891, "ID": 0.942, "IG": 0.592, "IF": 0.134, "HY": 0.821, "HR": 0.697,
            "HS": 0.865, "HP": 0.777, "HQ": 0.716, "HV": 0.831, "HW": 0.981, "HT": 0.834, "HK": 0.566, "HH": 0.0,
            "HI": 0.848, "HN": 0.754, "HL": 0.842, "HM": 0.825, "HC": 0.836, "HA": 0.896, "HF": 0.907, "HG": 1.0,
            "HD": 0.629, "HE": 0.547, "NH": 0.78, "NI": 0.615, "NK": 0.891, "NL": 0.603, "NM": 0.588, "NN": 0.0,
            "NA": 0.424, "NC": 0.425, "ND": 0.838, "NE": 0.835, "NF": 0.766, "NG": 0.512, "NY": 0.641,
            "NP": 0.266, "NQ": 0.175, "NR": 1.0, "NS": 0.361, "NT": 0.368, "NV": 0.503, "NW": 0.945, "TY": 0.596,
            "TV": 0.345, "TW": 0.816, "TT": 0.0, "TR": 1.0, "TS": 0.185, "TP": 0.159, "TQ": 0.322, "TN": 0.315,
            "TL": 0.453, "TM": 0.403, "TK": 0.866, "TH": 0.737, "TI": 0.455, "TF": 0.604, "TG": 0.312, "TD": 0.83,
            "TE": 0.812, "TC": 0.261, "TA": 0.251, "AA": 0.0, "AC": 0.112, "AE": 0.827, "AD": 0.819, "AG": 0.208,
            "AF": 0.54, "AI": 0.407, "AH": 0.696, "AK": 0.891, "AM": 0.379, "AL": 0.406, "AN": 0.318, "AQ": 0.372,
            "AP": 0.191, "AS": 0.094, "AR": 1.0, "AT": 0.22, "AW": 0.739, "AV": 0.273, "AY": 0.552, "VK": 0.889
        }

        # Distance is the Grantham chemical distance matrix used by Grantham et. al.
        self._distance2 = {
            "GW": 0.923, "GV": 0.464, "GT": 0.272, "GS": 0.158, "GR": 1.0, "GQ": 0.467, "GP": 0.323, "GY": 0.728,
            "GG": 0.0, "GF": 0.727, "GE": 0.807, "GD": 0.776, "GC": 0.312, "GA": 0.206, "GN": 0.381, "GM": 0.557,
            "GL": 0.591, "GK": 0.894, "GI": 0.592, "GH": 0.769, "ME": 0.879, "MD": 0.932, "MG": 0.569,
            "MF": 0.182, "MA": 0.383, "MC": 0.276, "MM": 0.0, "ML": 0.062, "MN": 0.447, "MI": 0.058, "MH": 0.648,
            "MK": 0.884, "MT": 0.358, "MW": 0.391, "MV": 0.12, "MQ": 0.372, "MP": 0.285, "MS": 0.417, "MR": 1.0,
            "MY": 0.255, "FP": 0.42, "FQ": 0.459, "FR": 1.0, "FS": 0.548, "FT": 0.499, "FV": 0.252, "FW": 0.207,
            "FY": 0.179, "FA": 0.508, "FC": 0.405, "FD": 0.977, "FE": 0.918, "FF": 0.0, "FG": 0.69, "FH": 0.663,
            "FI": 0.128, "FK": 0.903, "FL": 0.131, "FM": 0.169, "FN": 0.541, "SY": 0.615, "SS": 0.0, "SR": 1.0,
            "SQ": 0.358, "SP": 0.181, "SW": 0.827, "SV": 0.342, "ST": 0.174, "SK": 0.883, "SI": 0.478,
            "SH": 0.718, "SN": 0.289, "SM": 0.44, "SL": 0.474, "SC": 0.185, "SA": 0.1, "SG": 0.17, "SF": 0.622,
            "SE": 0.812, "SD": 0.801, "YI": 0.23, "YH": 0.678, "YK": 0.904, "YM": 0.268, "YL": 0.219, "YN": 0.512,
            "YA": 0.587, "YC": 0.478, "YE": 0.932, "YD": 1.0, "YG": 0.782, "YF": 0.202, "YY": 0.0, "YQ": 0.404,
            "YP": 0.444, "YS": 0.612, "YR": 0.995, "YT": 0.557, "YW": 0.244, "YV": 0.328, "LF": 0.139,
            "LG": 0.596, "LD": 0.944, "LE": 0.892, "LC": 0.296, "LA": 0.405, "LN": 0.452, "LL": 0.0, "LM": 0.062,
            "LK": 0.893, "LH": 0.653, "LI": 0.013, "LV": 0.133, "LW": 0.341, "LT": 0.397, "LR": 1.0, "LS": 0.443,
            "LP": 0.309, "LQ": 0.376, "LY": 0.205, "RT": 0.808, "RV": 0.914, "RW": 1.0, "RP": 0.796, "RQ": 0.668,
            "RR": 0.0, "RS": 0.86, "RY": 0.859, "RD": 0.305, "RE": 0.225, "RF": 0.977, "RG": 0.928, "RA": 0.919,
            "RC": 0.905, "RL": 0.92, "RM": 0.908, "RN": 0.69, "RH": 0.498, "RI": 0.929, "RK": 0.141, "VH": 0.649,
            "VI": 0.135, "EM": 0.83, "EL": 0.854, "EN": 0.599, "EI": 0.86, "EH": 0.406, "EK": 0.143, "EE": 0.0,
            "ED": 0.133, "EG": 0.779, "EF": 0.932, "EA": 0.79, "EC": 0.788, "VM": 0.12, "EY": 0.837, "VN": 0.38,
            "ET": 0.682, "EW": 1.0, "EV": 0.824, "EQ": 0.598, "EP": 0.688, "ES": 0.726, "ER": 0.234, "VP": 0.212,
            "VQ": 0.339, "VR": 1.0, "VT": 0.305, "VW": 0.472, "KC": 0.871, "KA": 0.889, "KG": 0.9, "KF": 0.957,
            "KE": 0.149, "KD": 0.279, "KK": 0.0, "KI": 0.899, "KH": 0.438, "KN": 0.667, "KM": 0.871, "KL": 0.892,
            "KS": 0.825, "KR": 0.154, "KQ": 0.639, "KP": 0.757, "KW": 1.0, "KV": 0.882, "KT": 0.759, "KY": 0.848,
            "DN": 0.56, "DL": 0.841, "DM": 0.819, "DK": 0.249, "DH": 0.435, "DI": 0.847, "DF": 0.924, "DG": 0.697,
            "DD": 0.0, "DE": 0.124, "DC": 0.742, "DA": 0.729, "DY": 0.836, "DV": 0.797, "DW": 1.0, "DT": 0.649,
            "DR": 0.295, "DS": 0.667, "DP": 0.657, "DQ": 0.584, "QQ": 0.0, "QP": 0.272, "QS": 0.461, "QR": 1.0,
            "QT": 0.389, "QW": 0.831, "QV": 0.464, "QY": 0.522, "QA": 0.512, "QC": 0.462, "QE": 0.861,
            "QD": 0.903, "QG": 0.648, "QF": 0.671, "QI": 0.532, "QH": 0.765, "QK": 0.881, "QM": 0.505,
            "QL": 0.518, "QN": 0.181, "WG": 0.829, "WF": 0.196, "WE": 0.931, "WD": 1.0, "WC": 0.56, "WA": 0.658,
            "WN": 0.631, "WM": 0.344, "WL": 0.304, "WK": 0.892, "WI": 0.305, "WH": 0.678, "WW": 0.0, "WV": 0.418,
            "WT": 0.638, "WS": 0.689, "WR": 0.968, "WQ": 0.538, "WP": 0.555, "WY": 0.204, "PR": 1.0, "PS": 0.196,
            "PP": 0.0, "PQ": 0.228, "PV": 0.244, "PW": 0.72, "PT": 0.161, "PY": 0.481, "PC": 0.179, "PA": 0.22,
            "PF": 0.515, "PG": 0.376, "PD": 0.852, "PE": 0.831, "PK": 0.875, "PH": 0.696, "PI": 0.363,
            "PN": 0.231, "PL": 0.357, "PM": 0.326, "CK": 0.887, "CI": 0.304, "CH": 0.66, "CN": 0.324, "CM": 0.277,
            "CL": 0.301, "CC": 0.0, "CA": 0.114, "CG": 0.32, "CF": 0.437, "CE": 0.838, "CD": 0.847, "CY": 0.457,
            "CS": 0.176, "CR": 1.0, "CQ": 0.341, "CP": 0.157, "CW": 0.639, "CV": 0.167, "CT": 0.233, "IY": 0.213,
            "VA": 0.275, "VC": 0.165, "VD": 0.9, "VE": 0.867, "VF": 0.269, "VG": 0.471, "IQ": 0.383, "IP": 0.311,
            "IS": 0.443, "IR": 1.0, "VL": 0.134, "IT": 0.396, "IW": 0.339, "IV": 0.133, "II": 0.0, "IH": 0.652,
            "IK": 0.892, "VS": 0.322, "IM": 0.057, "IL": 0.013, "VV": 0.0, "IN": 0.457, "IA": 0.403, "VY": 0.31,
            "IC": 0.296, "IE": 0.891, "ID": 0.942, "IG": 0.592, "IF": 0.134, "HY": 0.821, "HR": 0.697,
            "HS": 0.865, "HP": 0.777, "HQ": 0.716, "HV": 0.831, "HW": 0.981, "HT": 0.834, "HK": 0.566, "HH": 0.0,
            "HI": 0.848, "HN": 0.754, "HL": 0.842, "HM": 0.825, "HC": 0.836, "HA": 0.896, "HF": 0.907, "HG": 1.0,
            "HD": 0.629, "HE": 0.547, "NH": 0.78, "NI": 0.615, "NK": 0.891, "NL": 0.603, "NM": 0.588, "NN": 0.0,
            "NA": 0.424, "NC": 0.425, "ND": 0.838, "NE": 0.835, "NF": 0.766, "NG": 0.512, "NY": 0.641,
            "NP": 0.266, "NQ": 0.175, "NR": 1.0, "NS": 0.361, "NT": 0.368, "NV": 0.503, "NW": 0.945, "TY": 0.596,
            "TV": 0.345, "TW": 0.816, "TT": 0.0, "TR": 1.0, "TS": 0.185, "TP": 0.159, "TQ": 0.322, "TN": 0.315,
            "TL": 0.453, "TM": 0.403, "TK": 0.866, "TH": 0.737, "TI": 0.455, "TF": 0.604, "TG": 0.312, "TD": 0.83,
            "TE": 0.812, "TC": 0.261, "TA": 0.251, "AA": 0.0, "AC": 0.112, "AE": 0.827, "AD": 0.819, "AG": 0.208,
            "AF": 0.54, "AI": 0.407, "AH": 0.696, "AK": 0.891, "AM": 0.379, "AL": 0.406, "AN": 0.318, "AQ": 0.372,
            "AP": 0.191, "AS": 0.094, "AR": 1.0, "AT": 0.22, "AW": 0.739, "AV": 0.273, "AY": 0.552, "VK": 0.889
        }

        self.name_and_matrix_tuples = [
            ("tausw", self._distance1),
            ("taugrant", self._distance2),
        ]

    def calc(self, sequence, return_string=False):
        """ This function calculates the SequenceOrderCouplingNumberTotal of a sequence.
        :param sequence:
        :param return_string:
        :return:
        """
        from math import pow
        tau_list = []
        seq_len = len(sequence)

        # name_and_matrix_tuples calculates SW and Grant
        for name, distance_matrix in self.name_and_matrix_tuples:
            for i in range(self.maxlag):
                d = i + 1
                tau = 0.0
                for i in range(seq_len - d):
                    tau += pow(distance_matrix[sequence[i] + sequence[i + d]], 2)
                tau_list.append(tau)

        return tau_list

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        column_titles = []
        for name, distance_matrix in self.name_and_matrix_tuples:
            for i in range(self.maxlag):
                d = i + 1
                column_titles.append(name + str(i + 1))
        return column_titles




'''
def GetAAComposition(ProteinSequence):

    """
    ###############################################################################
    Calculate the composition of Amino acids
    for a given protein sequence.
    Usage:
    result=CalculateAAComposition(protein)
    Input: protein is a pure protein sequence.
    Output: result is a dict form containing the composition of
    20 amino acids.
    ###############################################################################
    """
    LengthSequence=len(ProteinSequence)
    Result={}
    for i in AALetter:
        Result[i]=round(float(ProteinSequence.count(i))/LengthSequence,3)
    return Result

#############################################################################################
def GetQuasiSequenceOrder1(ProteinSequence,maxlag=30,weight=0.1,distancematrix={}):
    """
    ###############################################################################
    Computing the first 20 quasi-sequence-order descriptors for
    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder1(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################
    """
    rightpart=0.0
    for i in range(maxlag):
        rightpart=rightpart+GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix)
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*rightpart
    for index,i in enumerate(AALetter):
        result['QSO'+str(index+1)]=round(AAC[i]/temp,6)
    return result


#############################################################################################
def GetQuasiSequenceOrder2(ProteinSequence,maxlag=30,weight=0.1,distancematrix={}):
    """
    ###############################################################################
    Computing the last maxlag quasi-sequence-order descriptors for
    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder2(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################
    """
    rightpart=[]
    for i in range(maxlag):
        rightpart.append(GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix))
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*sum(rightpart)
    for index in range(20, 20+maxlag):
        result['QSO'+str(index+1)]=round(weight*rightpart[index-20]/temp,6)
    return result


#############################################################################################
def GetQuasiSequenceOrder1SW(ProteinSequence,maxlag=30,weight=0.1,distancematrix=_Distance1):
    """
    ###############################################################################
    Computing the first 20 quasi-sequence-order descriptors for
    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder1SW(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################
    """
    rightpart=0.0
    for i in range(maxlag):
        rightpart=rightpart+GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix)
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*rightpart
    for index,i in enumerate(AALetter):
        result['QSOSW'+str(index+1)]=round(AAC[i]/temp,6)
    return result


#############################################################################################
def GetQuasiSequenceOrder2SW(ProteinSequence,maxlag=30,weight=0.1,distancematrix=_Distance1):
    """
    ###############################################################################
    Computing the last maxlag quasi-sequence-order descriptors for

    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder2SW(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################

    """
    rightpart=[]
    for i in range(maxlag):
        rightpart.append(GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix))
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*sum(rightpart)
    for index in range(20,20+maxlag):
        result['QSOSW'+str(index+1)]=round(weight*rightpart[index-20]/temp,6)
    return result

#############################################################################################
def GetQuasiSequenceOrder1Grant(ProteinSequence,maxlag=30,weight=0.1,distancematrix=_Distance2):
    """
    ###############################################################################
    Computing the first 20 quasi-sequence-order descriptors for
    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder1Grant(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################
    """
    rightpart=0.0
    for i in range(maxlag):
        rightpart=rightpart+GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix)
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*rightpart
    for index,i in enumerate(AALetter):
        result['QSOgrant'+str(index+1)]=round(AAC[i]/temp,6)
    return result


#############################################################################################
def GetQuasiSequenceOrder2Grant(ProteinSequence,maxlag=30,weight=0.1,distancematrix=_Distance2):
    """
    ###############################################################################
    Computing the last maxlag quasi-sequence-order descriptors for

    a given protein sequence.
    Usage:
    result = GetQuasiSequenceOrder2Grant(protein,maxlag,weigt)
    see method GetQuasiSequenceOrder for the choice of parameters.
    ###############################################################################

    """
    rightpart=[]
    for i in range(maxlag):
        rightpart.append(GetSequenceOrderCouplingNumber(ProteinSequence,i+1,distancematrix))
    AAC=GetAAComposition(ProteinSequence)
    result={}
    temp=1+weight*sum(rightpart)
    for index in range(20,20+maxlag):
        result['QSOgrant'+str(index+1)]=round(weight*rightpart[index-20]/temp,6)
    return result
#############################################################################################

def GetQuasiSequenceOrder(ProteinSequence, maxlag=30, weight=0.1):
    """
    ###############################################################################
    Computing quasi-sequence-order descriptors for a given protein.
    [1]:Kuo-Chen Chou. Prediction of Protein Subcellar Locations by
    Incorporating Quasi-Sequence-Order Effect. Biochemical and Biophysical
    Research Communications 2000, 278, 477-483.
    Usage:
    result = GetQuasiSequenceOrder(protein,maxlag,weight)
    Input: protein is a pure protein sequence
    maxlag is the maximum lag and the length of the protein should be larger
    than maxlag. default is 30.
    weight is a weight factor.  please see reference 1 for its choice. default is 0.1.
    Output: result is a dict form containing all quasi-sequence-order descriptors
    ###############################################################################
    """
    result = dict()
    _Distance1 = ""
    _Distance2 = ""
    result.update(GetQuasiSequenceOrder1SW(ProteinSequence, maxlag, weight, _Distance1))
    result.update(GetQuasiSequenceOrder2SW(ProteinSequence, maxlag, weight, _Distance1))
    result.update(GetQuasiSequenceOrder1Grant(ProteinSequence, maxlag, weight, _Distance2))
    result.update(GetQuasiSequenceOrder2Grant(ProteinSequence, maxlag, weight, _Distance2))
    return result
'''


class QuasiSequenceOrder:

    def __init__(self, round_to=5, maxlag=30, weight=0.1):

        self.maxlag = maxlag

        self.weight = weight

        self.round_to = round_to

        self.standard_amino_acids = [
            "A", "R", "N", "D", "C", "E", "Q", "G", "H", "I",
            "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"
        ]

        # Distance is the Schneider-Wrede physicochemical distance matrix used by Chou et. al.
        self._distance1 = {
            "GW": 0.923, "GV": 0.464, "GT": 0.272, "GS": 0.158, "GR": 1.0, "GQ": 0.467, "GP": 0.323, "GY": 0.728,
            "GG": 0.0, "GF": 0.727, "GE": 0.807, "GD": 0.776, "GC": 0.312, "GA": 0.206, "GN": 0.381, "GM": 0.557,
            "GL": 0.591, "GK": 0.894, "GI": 0.592, "GH": 0.769, "ME": 0.879, "MD": 0.932, "MG": 0.569,
            "MF": 0.182, "MA": 0.383, "MC": 0.276, "MM": 0.0, "ML": 0.062, "MN": 0.447, "MI": 0.058, "MH": 0.648,
            "MK": 0.884, "MT": 0.358, "MW": 0.391, "MV": 0.12, "MQ": 0.372, "MP": 0.285, "MS": 0.417, "MR": 1.0,
            "MY": 0.255, "FP": 0.42, "FQ": 0.459, "FR": 1.0, "FS": 0.548, "FT": 0.499, "FV": 0.252, "FW": 0.207,
            "FY": 0.179, "FA": 0.508, "FC": 0.405, "FD": 0.977, "FE": 0.918, "FF": 0.0, "FG": 0.69, "FH": 0.663,
            "FI": 0.128, "FK": 0.903, "FL": 0.131, "FM": 0.169, "FN": 0.541, "SY": 0.615, "SS": 0.0, "SR": 1.0,
            "SQ": 0.358, "SP": 0.181, "SW": 0.827, "SV": 0.342, "ST": 0.174, "SK": 0.883, "SI": 0.478,
            "SH": 0.718, "SN": 0.289, "SM": 0.44, "SL": 0.474, "SC": 0.185, "SA": 0.1, "SG": 0.17, "SF": 0.622,
            "SE": 0.812, "SD": 0.801, "YI": 0.23, "YH": 0.678, "YK": 0.904, "YM": 0.268, "YL": 0.219, "YN": 0.512,
            "YA": 0.587, "YC": 0.478, "YE": 0.932, "YD": 1.0, "YG": 0.782, "YF": 0.202, "YY": 0.0, "YQ": 0.404,
            "YP": 0.444, "YS": 0.612, "YR": 0.995, "YT": 0.557, "YW": 0.244, "YV": 0.328, "LF": 0.139,
            "LG": 0.596, "LD": 0.944, "LE": 0.892, "LC": 0.296, "LA": 0.405, "LN": 0.452, "LL": 0.0, "LM": 0.062,
            "LK": 0.893, "LH": 0.653, "LI": 0.013, "LV": 0.133, "LW": 0.341, "LT": 0.397, "LR": 1.0, "LS": 0.443,
            "LP": 0.309, "LQ": 0.376, "LY": 0.205, "RT": 0.808, "RV": 0.914, "RW": 1.0, "RP": 0.796, "RQ": 0.668,
            "RR": 0.0, "RS": 0.86, "RY": 0.859, "RD": 0.305, "RE": 0.225, "RF": 0.977, "RG": 0.928, "RA": 0.919,
            "RC": 0.905, "RL": 0.92, "RM": 0.908, "RN": 0.69, "RH": 0.498, "RI": 0.929, "RK": 0.141, "VH": 0.649,
            "VI": 0.135, "EM": 0.83, "EL": 0.854, "EN": 0.599, "EI": 0.86, "EH": 0.406, "EK": 0.143, "EE": 0.0,
            "ED": 0.133, "EG": 0.779, "EF": 0.932, "EA": 0.79, "EC": 0.788, "VM": 0.12, "EY": 0.837, "VN": 0.38,
            "ET": 0.682, "EW": 1.0, "EV": 0.824, "EQ": 0.598, "EP": 0.688, "ES": 0.726, "ER": 0.234, "VP": 0.212,
            "VQ": 0.339, "VR": 1.0, "VT": 0.305, "VW": 0.472, "KC": 0.871, "KA": 0.889, "KG": 0.9, "KF": 0.957,
            "KE": 0.149, "KD": 0.279, "KK": 0.0, "KI": 0.899, "KH": 0.438, "KN": 0.667, "KM": 0.871, "KL": 0.892,
            "KS": 0.825, "KR": 0.154, "KQ": 0.639, "KP": 0.757, "KW": 1.0, "KV": 0.882, "KT": 0.759, "KY": 0.848,
            "DN": 0.56, "DL": 0.841, "DM": 0.819, "DK": 0.249, "DH": 0.435, "DI": 0.847, "DF": 0.924, "DG": 0.697,
            "DD": 0.0, "DE": 0.124, "DC": 0.742, "DA": 0.729, "DY": 0.836, "DV": 0.797, "DW": 1.0, "DT": 0.649,
            "DR": 0.295, "DS": 0.667, "DP": 0.657, "DQ": 0.584, "QQ": 0.0, "QP": 0.272, "QS": 0.461, "QR": 1.0,
            "QT": 0.389, "QW": 0.831, "QV": 0.464, "QY": 0.522, "QA": 0.512, "QC": 0.462, "QE": 0.861,
            "QD": 0.903, "QG": 0.648, "QF": 0.671, "QI": 0.532, "QH": 0.765, "QK": 0.881, "QM": 0.505,
            "QL": 0.518, "QN": 0.181, "WG": 0.829, "WF": 0.196, "WE": 0.931, "WD": 1.0, "WC": 0.56, "WA": 0.658,
            "WN": 0.631, "WM": 0.344, "WL": 0.304, "WK": 0.892, "WI": 0.305, "WH": 0.678, "WW": 0.0, "WV": 0.418,
            "WT": 0.638, "WS": 0.689, "WR": 0.968, "WQ": 0.538, "WP": 0.555, "WY": 0.204, "PR": 1.0, "PS": 0.196,
            "PP": 0.0, "PQ": 0.228, "PV": 0.244, "PW": 0.72, "PT": 0.161, "PY": 0.481, "PC": 0.179, "PA": 0.22,
            "PF": 0.515, "PG": 0.376, "PD": 0.852, "PE": 0.831, "PK": 0.875, "PH": 0.696, "PI": 0.363,
            "PN": 0.231, "PL": 0.357, "PM": 0.326, "CK": 0.887, "CI": 0.304, "CH": 0.66, "CN": 0.324, "CM": 0.277,
            "CL": 0.301, "CC": 0.0, "CA": 0.114, "CG": 0.32, "CF": 0.437, "CE": 0.838, "CD": 0.847, "CY": 0.457,
            "CS": 0.176, "CR": 1.0, "CQ": 0.341, "CP": 0.157, "CW": 0.639, "CV": 0.167, "CT": 0.233, "IY": 0.213,
            "VA": 0.275, "VC": 0.165, "VD": 0.9, "VE": 0.867, "VF": 0.269, "VG": 0.471, "IQ": 0.383, "IP": 0.311,
            "IS": 0.443, "IR": 1.0, "VL": 0.134, "IT": 0.396, "IW": 0.339, "IV": 0.133, "II": 0.0, "IH": 0.652,
            "IK": 0.892, "VS": 0.322, "IM": 0.057, "IL": 0.013, "VV": 0.0, "IN": 0.457, "IA": 0.403, "VY": 0.31,
            "IC": 0.296, "IE": 0.891, "ID": 0.942, "IG": 0.592, "IF": 0.134, "HY": 0.821, "HR": 0.697,
            "HS": 0.865, "HP": 0.777, "HQ": 0.716, "HV": 0.831, "HW": 0.981, "HT": 0.834, "HK": 0.566, "HH": 0.0,
            "HI": 0.848, "HN": 0.754, "HL": 0.842, "HM": 0.825, "HC": 0.836, "HA": 0.896, "HF": 0.907, "HG": 1.0,
            "HD": 0.629, "HE": 0.547, "NH": 0.78, "NI": 0.615, "NK": 0.891, "NL": 0.603, "NM": 0.588, "NN": 0.0,
            "NA": 0.424, "NC": 0.425, "ND": 0.838, "NE": 0.835, "NF": 0.766, "NG": 0.512, "NY": 0.641,
            "NP": 0.266, "NQ": 0.175, "NR": 1.0, "NS": 0.361, "NT": 0.368, "NV": 0.503, "NW": 0.945, "TY": 0.596,
            "TV": 0.345, "TW": 0.816, "TT": 0.0, "TR": 1.0, "TS": 0.185, "TP": 0.159, "TQ": 0.322, "TN": 0.315,
            "TL": 0.453, "TM": 0.403, "TK": 0.866, "TH": 0.737, "TI": 0.455, "TF": 0.604, "TG": 0.312, "TD": 0.83,
            "TE": 0.812, "TC": 0.261, "TA": 0.251, "AA": 0.0, "AC": 0.112, "AE": 0.827, "AD": 0.819, "AG": 0.208,
            "AF": 0.54, "AI": 0.407, "AH": 0.696, "AK": 0.891, "AM": 0.379, "AL": 0.406, "AN": 0.318, "AQ": 0.372,
            "AP": 0.191, "AS": 0.094, "AR": 1.0, "AT": 0.22, "AW": 0.739, "AV": 0.273, "AY": 0.552, "VK": 0.889
        }

        # Distance is the Grantham chemical distance matrix used by Grantham et. al.
        self._distance2 = {
            "GW": 0.923, "GV": 0.464, "GT": 0.272, "GS": 0.158, "GR": 1.0, "GQ": 0.467, "GP": 0.323, "GY": 0.728,
            "GG": 0.0, "GF": 0.727, "GE": 0.807, "GD": 0.776, "GC": 0.312, "GA": 0.206, "GN": 0.381, "GM": 0.557,
            "GL": 0.591, "GK": 0.894, "GI": 0.592, "GH": 0.769, "ME": 0.879, "MD": 0.932, "MG": 0.569,
            "MF": 0.182, "MA": 0.383, "MC": 0.276, "MM": 0.0, "ML": 0.062, "MN": 0.447, "MI": 0.058, "MH": 0.648,
            "MK": 0.884, "MT": 0.358, "MW": 0.391, "MV": 0.12, "MQ": 0.372, "MP": 0.285, "MS": 0.417, "MR": 1.0,
            "MY": 0.255, "FP": 0.42, "FQ": 0.459, "FR": 1.0, "FS": 0.548, "FT": 0.499, "FV": 0.252, "FW": 0.207,
            "FY": 0.179, "FA": 0.508, "FC": 0.405, "FD": 0.977, "FE": 0.918, "FF": 0.0, "FG": 0.69, "FH": 0.663,
            "FI": 0.128, "FK": 0.903, "FL": 0.131, "FM": 0.169, "FN": 0.541, "SY": 0.615, "SS": 0.0, "SR": 1.0,
            "SQ": 0.358, "SP": 0.181, "SW": 0.827, "SV": 0.342, "ST": 0.174, "SK": 0.883, "SI": 0.478,
            "SH": 0.718, "SN": 0.289, "SM": 0.44, "SL": 0.474, "SC": 0.185, "SA": 0.1, "SG": 0.17, "SF": 0.622,
            "SE": 0.812, "SD": 0.801, "YI": 0.23, "YH": 0.678, "YK": 0.904, "YM": 0.268, "YL": 0.219, "YN": 0.512,
            "YA": 0.587, "YC": 0.478, "YE": 0.932, "YD": 1.0, "YG": 0.782, "YF": 0.202, "YY": 0.0, "YQ": 0.404,
            "YP": 0.444, "YS": 0.612, "YR": 0.995, "YT": 0.557, "YW": 0.244, "YV": 0.328, "LF": 0.139,
            "LG": 0.596, "LD": 0.944, "LE": 0.892, "LC": 0.296, "LA": 0.405, "LN": 0.452, "LL": 0.0, "LM": 0.062,
            "LK": 0.893, "LH": 0.653, "LI": 0.013, "LV": 0.133, "LW": 0.341, "LT": 0.397, "LR": 1.0, "LS": 0.443,
            "LP": 0.309, "LQ": 0.376, "LY": 0.205, "RT": 0.808, "RV": 0.914, "RW": 1.0, "RP": 0.796, "RQ": 0.668,
            "RR": 0.0, "RS": 0.86, "RY": 0.859, "RD": 0.305, "RE": 0.225, "RF": 0.977, "RG": 0.928, "RA": 0.919,
            "RC": 0.905, "RL": 0.92, "RM": 0.908, "RN": 0.69, "RH": 0.498, "RI": 0.929, "RK": 0.141, "VH": 0.649,
            "VI": 0.135, "EM": 0.83, "EL": 0.854, "EN": 0.599, "EI": 0.86, "EH": 0.406, "EK": 0.143, "EE": 0.0,
            "ED": 0.133, "EG": 0.779, "EF": 0.932, "EA": 0.79, "EC": 0.788, "VM": 0.12, "EY": 0.837, "VN": 0.38,
            "ET": 0.682, "EW": 1.0, "EV": 0.824, "EQ": 0.598, "EP": 0.688, "ES": 0.726, "ER": 0.234, "VP": 0.212,
            "VQ": 0.339, "VR": 1.0, "VT": 0.305, "VW": 0.472, "KC": 0.871, "KA": 0.889, "KG": 0.9, "KF": 0.957,
            "KE": 0.149, "KD": 0.279, "KK": 0.0, "KI": 0.899, "KH": 0.438, "KN": 0.667, "KM": 0.871, "KL": 0.892,
            "KS": 0.825, "KR": 0.154, "KQ": 0.639, "KP": 0.757, "KW": 1.0, "KV": 0.882, "KT": 0.759, "KY": 0.848,
            "DN": 0.56, "DL": 0.841, "DM": 0.819, "DK": 0.249, "DH": 0.435, "DI": 0.847, "DF": 0.924, "DG": 0.697,
            "DD": 0.0, "DE": 0.124, "DC": 0.742, "DA": 0.729, "DY": 0.836, "DV": 0.797, "DW": 1.0, "DT": 0.649,
            "DR": 0.295, "DS": 0.667, "DP": 0.657, "DQ": 0.584, "QQ": 0.0, "QP": 0.272, "QS": 0.461, "QR": 1.0,
            "QT": 0.389, "QW": 0.831, "QV": 0.464, "QY": 0.522, "QA": 0.512, "QC": 0.462, "QE": 0.861,
            "QD": 0.903, "QG": 0.648, "QF": 0.671, "QI": 0.532, "QH": 0.765, "QK": 0.881, "QM": 0.505,
            "QL": 0.518, "QN": 0.181, "WG": 0.829, "WF": 0.196, "WE": 0.931, "WD": 1.0, "WC": 0.56, "WA": 0.658,
            "WN": 0.631, "WM": 0.344, "WL": 0.304, "WK": 0.892, "WI": 0.305, "WH": 0.678, "WW": 0.0, "WV": 0.418,
            "WT": 0.638, "WS": 0.689, "WR": 0.968, "WQ": 0.538, "WP": 0.555, "WY": 0.204, "PR": 1.0, "PS": 0.196,
            "PP": 0.0, "PQ": 0.228, "PV": 0.244, "PW": 0.72, "PT": 0.161, "PY": 0.481, "PC": 0.179, "PA": 0.22,
            "PF": 0.515, "PG": 0.376, "PD": 0.852, "PE": 0.831, "PK": 0.875, "PH": 0.696, "PI": 0.363,
            "PN": 0.231, "PL": 0.357, "PM": 0.326, "CK": 0.887, "CI": 0.304, "CH": 0.66, "CN": 0.324, "CM": 0.277,
            "CL": 0.301, "CC": 0.0, "CA": 0.114, "CG": 0.32, "CF": 0.437, "CE": 0.838, "CD": 0.847, "CY": 0.457,
            "CS": 0.176, "CR": 1.0, "CQ": 0.341, "CP": 0.157, "CW": 0.639, "CV": 0.167, "CT": 0.233, "IY": 0.213,
            "VA": 0.275, "VC": 0.165, "VD": 0.9, "VE": 0.867, "VF": 0.269, "VG": 0.471, "IQ": 0.383, "IP": 0.311,
            "IS": 0.443, "IR": 1.0, "VL": 0.134, "IT": 0.396, "IW": 0.339, "IV": 0.133, "II": 0.0, "IH": 0.652,
            "IK": 0.892, "VS": 0.322, "IM": 0.057, "IL": 0.013, "VV": 0.0, "IN": 0.457, "IA": 0.403, "VY": 0.31,
            "IC": 0.296, "IE": 0.891, "ID": 0.942, "IG": 0.592, "IF": 0.134, "HY": 0.821, "HR": 0.697,
            "HS": 0.865, "HP": 0.777, "HQ": 0.716, "HV": 0.831, "HW": 0.981, "HT": 0.834, "HK": 0.566, "HH": 0.0,
            "HI": 0.848, "HN": 0.754, "HL": 0.842, "HM": 0.825, "HC": 0.836, "HA": 0.896, "HF": 0.907, "HG": 1.0,
            "HD": 0.629, "HE": 0.547, "NH": 0.78, "NI": 0.615, "NK": 0.891, "NL": 0.603, "NM": 0.588, "NN": 0.0,
            "NA": 0.424, "NC": 0.425, "ND": 0.838, "NE": 0.835, "NF": 0.766, "NG": 0.512, "NY": 0.641,
            "NP": 0.266, "NQ": 0.175, "NR": 1.0, "NS": 0.361, "NT": 0.368, "NV": 0.503, "NW": 0.945, "TY": 0.596,
            "TV": 0.345, "TW": 0.816, "TT": 0.0, "TR": 1.0, "TS": 0.185, "TP": 0.159, "TQ": 0.322, "TN": 0.315,
            "TL": 0.453, "TM": 0.403, "TK": 0.866, "TH": 0.737, "TI": 0.455, "TF": 0.604, "TG": 0.312, "TD": 0.83,
            "TE": 0.812, "TC": 0.261, "TA": 0.251, "AA": 0.0, "AC": 0.112, "AE": 0.827, "AD": 0.819, "AG": 0.208,
            "AF": 0.54,  "AI": 0.407, "AH": 0.696, "AK": 0.891, "AM": 0.379, "AL": 0.406, "AN": 0.318, "AQ": 0.372,
            "AP": 0.191, "AS": 0.094, "AR": 1.0, "AT": 0.22, "AW": 0.739, "AV": 0.273, "AY": 0.552, "VK": 0.889
        }

    def _getsequenceordercouplingnumber(self, sequence, d, distance_matrix):
        """ Computes the dth-rank sequence order coupling number for an amino acid sequence.
        :param sequence: An amino acid sequence.
        :param d: The gap between two amino acids.
        :param distancematrix: One of the distance matrices.
        :return: tau - A float describing the sequence coupling number.
        """
        tau = 0.0
        for i in range(len(sequence) - d):
            tau += pow(distance_matrix[sequence[i] + sequence[i + d]], 2)
        return tau


    def calc(self, sequence, return_string=False):
        """ This function calculates the n-composition of a sequence within a given alphabet.
        :param sequence:
        :param return_string:
        :return:
        """
        from math import pow
        result = []
        seq_len = len(sequence)
        aa_composition = {aa: 100 * float(sequence.count(aa)) / float(seq_len) for aa in self.standard_amino_acids}

        # Compute the first 20 quasi-sequence-order descriptors for
        #right_part = 0.0
        #for i in range(self.maxlag):
        #    right_part += self._getsequenceordercouplingnumber(sequence, i + 1, self._distance1)

        right_part_list = []
        for i in range(self.maxlag):
            right_part_list.append(self._getsequenceordercouplingnumber(sequence, i + 1, self._distance1))

        # temp = 1.0 + self.weight * right_part
        temp = 1.0 + self.weight * sum(right_part_list)

        # Start GetQuasiSequenceOrderSW
        for amino_acid in self.standard_amino_acids:
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            result.append(round(aa_composition[amino_acid] / temp, self.round_to))
        # End GetQuasiSequenceOrderSW

        # Start GetQuasiSequenceOrder2SW
        # temp = 1.0 + self.weight * sum(right_part)
        for index in range(len(self.standard_amino_acids), len(self.standard_amino_acids) + self.maxlag):
            # result['QSOSW' + str(index + 1)] = round(self.weight * right_part[index - 20] / temp, 6)
            result.append(round(self.weight * right_part_list[index - 20] / temp, self.round_to))
        # End GetQuasiSequenceOrder2SW


        # Start GetQuasiSequenceOrder1Grant
        # result.update(GetQuasiSequenceOrder1Grant(sequence, self.maxlag, self.weight, self._distance2))

        #rightpart = 0.0
        #for i in range(self.maxlag):
        #    rightpart = rightpart + self._getsequenceordercouplingnumber(sequence, i + 1, self._distance2)

        rightpart = []
        for i in range(self.maxlag):
            rightpart.append(self._getsequenceordercouplingnumber(sequence, i + 1, self._distance2))

        result = {}
        #temp = 1 + self.weight * rightpart
        temp = 1 + self.weight * sum(rightpart)

        for amino_acid in self.standard_amino_acids:
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            result.append(round(aa_composition[amino_acid] / temp, self.round_to))

        #for index, i in enumerate(self.standard_amino_acids):
        #    result['QSOgrant' + str(index + 1)] = round(AAC[i] / temp, 6)
        # End
        # Start GetQuasiSequenceOrder2Grant
        # result.update(GetQuasiSequenceOrder2Grant(sequence, self.maxlag, self.weight, self._distance2))
        #for index in range(20, 20 + self.maxlag):
        #    # result['QSOgrant' + str(index + 1)] = round(self.weight * rightpart[index - 20] / temp, 6)
        for index in range(len(self.standard_amino_acids), len(self.standard_amino_acids) + self.maxlag):
            # result['QSOgrant' + str(index + 1)] = round(self.weight * rightpart[index - 20] / temp, 6)
            result.append(round(self.weight * right_part_list[index - 20] / temp, self.round_to))
        # End

        return result

    def getcoltitles(self):
        """
        :return: The column ids of the feature calculated.
        """
        title = []
        for amino_acid_number in range(len(self.standard_amino_acids)):
            # result.append(round(aa_composition[amino_acid] / temp, self.round_to))
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            title.append('QSOSW' + str(amino_acid_number + 1))

        for index_number in range(len(self.standard_amino_acids), len(self.standard_amino_acids) + self.maxlag):
            # result.append(round(aa_composition[amino_acid] / temp, self.round_to))
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            title.append('QSOSW' + str(index_number + 1))

        for amino_acid_number in range(len(self.standard_amino_acids)):
            # result.append(round(aa_composition[amino_acid] / temp, self.round_to))
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            title.append('QSOgrant' + str(amino_acid_number + 1))

        for index_number in range(len(self.standard_amino_acids), len(self.standard_amino_acids) + self.maxlag):
            # result.append(round(aa_composition[amino_acid] / temp, self.round_to))
            # result['QSOSW' + str(index + 1)] = round(AAC[i] / temp, 6)
            title.append('QSOgrant' + str(index_number + 1))


'''
def GetQuasiSequenceOrderp(ProteinSequence,maxlag=30,weight=0.1,distancematrix={}):
    """
    ###############################################################################
    Computing quasi-sequence-order descriptors for a given protein.
    [1]:Kuo-Chen Chou. Prediction of Protein Subcellar Locations by
    Incorporating Quasi-Sequence-Order Effect. Biochemical and Biophysical
    Research Communications 2000, 278, 477-483.

    Usage:
    result = GetQuasiSequenceOrderp(protein,maxlag,weight,distancematrix)
    Input: protein is a pure protein sequence
    maxlag is the maximum lag and the length of the protein should be larger
    than maxlag. default is 30.
    weight is a weight factor.  please see reference 1 for its choice. default is 0.1.
    distancematrix is a dict form containing 400 distance values
    Output: result is a dict form containing all quasi-sequence-order descriptors
    ###############################################################################
    """
    result=dict()
    result.update(GetQuasiSequenceOrder1(ProteinSequence,maxlag,weight,distancematrix))
    result.update(GetQuasiSequenceOrder2(ProteinSequence,maxlag,weight,distancematrix))
    return result
'''

'''
def ncomposition(sequence, alphabet, roundto=5):
    """ This function calculates the ncomposition of a sequence within a given alphabet.

    :param sequence:
    :param alphabet: list of kmers with the same length
    :param roundto:
    :return:
    """
    # Count the number of possible positions within the alphabet.
    sequence_list = [sequence[i:i+len(alphabet[0])] for i in range(len(sequence)-(len(alphabet[0])-1))]
    return [str(round(float(sequence_list.count(kmer)) / (len(sequence_list)), roundto)) for kmer in alphabet]


def splitncomposition(sequence, alphabet, start_len, stop_len, roundto=5):
    """ This function calculates the n-composition of the start, middle, and end of sequence within a given alphabet.

    :param sequence:
    :param alphabet:
    :param roundto:
    :return:
    """

    # Avoid list len related errors.
    assert len(sequence) > start_len and len(sequence) > stop_len

    start_seq_list = ncomposition(sequence[:start_len], alphabet, roundto=roundto)
    mid_seq_list = ncomposition(sequence[start_len:-stop_len], alphabet, roundto=roundto)
    end_seq_list = ncomposition(sequence[:stop_len], alphabet, roundto=roundto)

    return start_seq_list + mid_seq_list + end_seq_list

def CalculateGearyAuto(ProteinSequence, AAProperty, AAPropertyName):
    """
    A method used for computing Geary Auto for all properties
    Usage:
    result=CalculateGearyAuto(protein, AAP, AAPName)
    Input: protein is a pure protein sequence.
    AAProperty is a list or tuple form containing the properties of 20 amino acids (e.g., _AAProperty).
    AAPName is a list or tuple form used for indicating the property (e.g., '_AAPropertyName').
    Output: result is a dict form containing 30*p Geary autocorrelation
    descriptors based on the given properties.
    """
    Result={}

    for i in range(len(AAProperty)):

        Result[AAPropertyName[i]] = CalculateEachGearyAuto( ProteinSequence, AAProperty[i],  AAPropertyName[i])

    return Result

def CalculateEachGearyAuto(ProteinSequence, AAP, AAPName):
    """ Produces features describing Geary Auto Correlation of an amino acid sequence.
    you can use the function to compute GearyAuto
    descriptors for different properties based on AADs.
    Usage:
    result=CalculateEachGearyAuto(protein,AAP,AAPName)
    Input: protein is a pure protein sequence.
    AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
    AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
    Output: result is a dict form containing 30 Geary autocorrelation
    descriptors based on the given property.
    """
    # A dict containing amino acid properties.
    AAPdic = NormalizeEachAAP(AAP)
    # Make a list of values
    cc=[]
    for i in ProteinSequence:
        cc.append(AAPdic[i])
    K = ( (_std(cc)) ** 2) * len(ProteinSequence)/(len(ProteinSequence)-1)
    Result = {}
    for i in range(1, 31):
        temp = 0
        for j in range(len(ProteinSequence)-i):
            temp += (AAPdic[ProteinSequence[j]] - AAPdic[ProteinSequence[j+i]])**2

        if len(ProteinSequence) - i == 0:
            Result['GearyAuto'+AAPName+str(i)] = round(temp/(2*(len(ProteinSequence)))/K, 3)
        else:
            Result['GearyAuto'+AAPName+str(i)] = round(temp/(2*(len(ProteinSequence)-i))/K, 3)
    return Result

    vector = []
    column_titles = []
    amino_acid_sequence = ""
    # CalculateEachGearyAuto
    for group_name, group_values in amino_acid_property_groups:
        # Generate titles
        # A dict containing amino acid properties.
        normalized_aa_properties = NormalizeEachAAP(group_values)
        # Exchange amino acid for for their respective property values.
        cc = [normalized_aa_properties[amino_acid] for amino_acid in amino_acid_sequence]
        K = ((_std(cc)) ** 2) * len(amino_acid_sequence)/(len(amino_acid_sequence)-1)
        Result={}
        for i in range(1, 31):
            temp = 0
            for j in range(len(amino_acid_sequence)-i):
                temp += (normalized_aa_properties[amino_acid_sequence[j]] - normalized_aa_properties[amino_acid_sequence[j+i]])**2
            if len(amino_acid_sequence) - i == 0:
                Result['GearyAuto'+group_name+str(i)] = round(temp/(2*(len(amino_acid_sequence)))/K, 3)
            else:
                Result['GearyAuto'+group_name+str(i)] = round(temp/(2*(len(amino_acid_sequence)-i))/K, 3)
        return Result
    return Result

    """
    result={}
    result.update(CalculateNormalizedMoreauBrotoAutoHydrophobicity(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoAvFlexibility(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoPolarizability(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoFreeEnergy(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoResidueASA(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoResidueVol(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoSteric(ProteinSequence))
    result.update(CalculateNormalizedMoreauBrotoAutoMutability(ProteinSequence))
    return result
    """


def CalculateEachNormalizedMoreauBrotoAuto(ProteinSequence,AAP,AAPName):
    """
    ####################################################################################
    you can use the function to compute MoreauBrotoAuto
    descriptors for different properties based on AADs.
    Usage:
    result=CalculateEachNormalizedMoreauBrotoAuto(protein,AAP,AAPName)
    Input: protein is a pure protein sequence.
    AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
    AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
    Output: result is a dict form containing 30 Normalized Moreau-Broto autocorrelation
    descriptors based on the given property.
    ####################################################################################
    """
    AAPdic=NormalizeEachAAP(AAP)
    Result={}

    for i in range(1,31):
        temp=0
        for j in range(len(ProteinSequence)-i):
            temp=temp+AAPdic[ProteinSequence[j]]*AAPdic[ProteinSequence[j+1]]
        if len(ProteinSequence)-i==0:
            Result['MoreauBrotoAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence)),3)
        else:
            Result['MoreauBrotoAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence)-i),3)
    return Result


def CalculateMoranAuto(ProteinSequence, AAProperty, AAPropertyName):
    """
    A method used for computing MoranAuto for all properties
    Usage:
    result=CalculateMoranAuto(protein,AAP,AAPName)
    Input: protein is a pure protein sequence.
    AAProperty is a list or tuple form containing the properties of 20 amino acids (e.g., _AAProperty).
    AAPName is a list or tuple form used for indicating the property (e.g., '_AAPropertyName').
    Output: result is a dict form containing 30*p Moran autocorrelation
    descriptors based on the given properties.
    """
    Result={}
    for i in range(len(AAProperty)):
        Result[AAPropertyName[i]]=CalculateEachMoranAuto(ProteinSequence,AAProperty[i],AAPropertyName[i])
    return Result


def CalculateEachMoranAuto(ProteinSequence, AAP, AAPName):
    """
    ####################################################################################
    you can use the function to compute MoranAuto
    descriptors for different properties based on AADs.
    Usage:
    result=CalculateEachMoranAuto(protein,AAP,AAPName)
    Input: protein is a pure protein sequence.
    AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
    AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
    Output: result is a dict form containing 30 Moran autocorrelation
    descriptors based on the given property.
    ####################################################################################
    """
    AAPdic=NormalizeEachAAP(AAP)
    cds=0
    for i in AALetter:
        cds=cds+(ProteinSequence.count(i))*(AAPdic[i])
    Pmean=cds/len(ProteinSequence)
    cc=[]
    for i in ProteinSequence:
        cc.append(AAPdic[i])
    K=(_std(cc,ddof=0))**2
    Result={}
    for i in range(1,31):
        temp=0
        for j in range(len(ProteinSequence)-i):
                        temp=temp+(AAPdic[ProteinSequence[j]]-Pmean)*(AAPdic[ProteinSequence[j+i]]-Pmean)
        if len(ProteinSequence)-i==0:
            Result['MoranAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence))/K,3)
        else:
            Result['MoranAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence)-i)/K,3)
    return Result
def NormalizeEachAAP(amino_acid_properties):
    """
    All of the amino acid indices are centralized and standardized before the calculation.
    Usage:
    result=NormalizeEachAAP(AAP)
    Input: AAP is a dict form containing the properties of 20 amino acids.
    Output: result is the a dict form containing the normalized properties
    of 20 amino acids.
    """
    assert len(amino_acid_properties) == 20, "There must be 20 amino acid properties."
    Result = {}
    for property_description, property_value in amino_acid_properties.items():
        Result[property_description] = ( property_value - _mean( amino_acid_properties.values()) ) / _std( amino_acid_properties.values(), ddof=0)
    return Result

def normalizedmoreaubrotoautocorrelation(ProteinSequence, AAP, AAPName):
    """
    ####################################################################################
    you can use the function to compute MoreauBrotoAuto
    descriptors for different properties based on AADs.

    Usage:
    result=CalculateEachNormalizedMoreauBrotoAuto(protein,AAP,AAPName)
    Input: protein is a pure protein sequence.
    AAP is a dict form containing the properties of 20 amino acids (e.g., _AvFlexibility).
    AAPName is a string used for indicating the property (e.g., '_AvFlexibility').
    Output: result is a dict form containing 30 Normalized Moreau-Broto autocorrelation
    descriptors based on the given property.
    ####################################################################################
    """

    AAPdic=NormalizeEachAAP(AAP)
    Result={}
    for i in range(1,31):
            temp=0
            for j in range(len(ProteinSequence)-i):
                temp=temp+AAPdic[ProteinSequence[j]]*AAPdic[ProteinSequence[j+1]]
            if len(ProteinSequence)-i==0:
                Result['MoreauBrotoAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence)),3)
            else:
                Result['MoreauBrotoAuto'+AAPName+str(i)]=round(temp/(len(ProteinSequence)-i),3)
    return Result

'''
