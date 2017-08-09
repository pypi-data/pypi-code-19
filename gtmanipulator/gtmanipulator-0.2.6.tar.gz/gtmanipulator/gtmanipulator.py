import pandas as pd
import numpy as np
import operator

class GtManipulator:
    """Class for handling Illumina iScan microarray data.
    
    Args:
        file (str): Filepath for file to be loaded as a DataFrame object. 
            (default None)
        data (DataFrame object): Alternative to loading in data from a raw
            file - useful for 'preprocessing' data.
        skip_lines (int): Number of lines to skip if loading raw file data.
            (default 0)
        header (int): Line to use a column names if loading raw file data.
            (default 0)
        index (int): Column to use as an index if loading raw file data.
            (default 0)
        delimiter (str): Delimiter to use if loading raw file data.
            (default ',')

    Attributes:
        data (DataFrame object): All data contained within the target file.
        summarized (boolean): Tracks if data has been summarized yet or not.
        count_cols (array-like): List of all columns added to the DataFrame
            object after summarization.
        frequencies (boolean): Tracks if allelic frequencies have been
            calculated or not.
        morphed (boolean): tracks if morphisms for markers or snps
            have been predicted or not.

    Raises:
        ValueError: If both file and data arguments are or are not given.
    """

    def __init__(self, file=None, data=None, skip_lines=0, 
                 header=0, index=0, delimiter =","):
        if file is not None and data is not None or file is None and data is None:
            raise ValueError("At least argument must be given.")
        elif file is not None:
            self.data = pd.read_csv(filepath_or_buffer=file, skiprows=skip_lines, 
                                    header=header, index_col=index, delimiter=delimiter)
        elif data is not None:
            self.data = data
        self.summarized = False
        self.count_cols = None
        self.frequencies = False
        self.morphed = False

    def save(self, filename, delimiter=",", **kwargs):
        """Convenience method to save a DataFrame object
        
        Args:
            filename (str): Filepath to save DataFrame object to.
            delimiter (str): Delimiter to save file with. (default ',')
        """
        self.data.to_csv(path_or_buf=filename, sep=delimiter, **kwargs)

    def transpose(self, **kwargs):
        """Convenience method to transpose data in a DataFrame object"""
        self.data.transpose(inplace=True)

    def summarize(self):
        """Summarize the genotype counts in the data by rows or columns.

        Returns:
            self.data (DataFrame object)
        """
        count_data = self.data.apply(lambda x: x.value_counts(), axis=1)
        count_data.fillna(0, inplace=True)
        self.count_cols = count_data.columns.values.tolist()
        if not self.summarized:
            self.data = pd.concat([self.data, count_data], axis=1)
            self.data[self.count_cols] = self.data[self.count_cols].astype(np.int64)
            self.summarized = True
        return self.data

    def calc_frequencies(self, missing={}):
        """Calculate the allelic frequencies (major and minor)
        
        Args:
            missing (dict): Dictionary of any values that should count as missing.
                (default {})

        Returns:
            self.data (DataFrame object): DataFrame object containing 
                summarization and allelic frequency data

        Raise:
            ValueError: If the GtManipulator object has not been 'summarize'.
        """
        if not self.summarized:
            raise ValueError("A GtManipulator object must be 'summarized' before allelic"
                             " frequencies can be calculate.\n")
        if not self.frequencies:
            new_cols = (("MajorHomo", "MajorHomoCount"), ("MinorHomo", "MinorHomoCount"),
                        ("MajorHet", "MajorHetCount"))
            for pair in new_cols:
                self.data[pair[0]] = None
                self.data[pair[1]] = 0
            self.data["MissingCount"] = 0
            self.data["TotalNotMissing"] = 0
            gt_helper = _GtAnalyzer(self.count_cols, missing)
            self.data = self.data.apply(gt_helper._get_allele_types, axis=1)
            self.frequencies = True
        return self.data

    def determine_morphisms(self, failed=0.20, mono=0.80, poly={"Type 1": (0.80, 0.20, 0.10),
                                                                "Type 2": (0.80, 0.10, 0.20),
                                                                "Type 3": (0.10, 0.10, 0.10)},
                            comp_ops={"Type 1": ("<", ">", "<="),
                                      "Type 2": ("<", "<=", ">"),
                                      "Type 3": (">", ">", ">")}):
        """Determines the morphisms of markers.

        Args:
            failed (float): Percentage of missing data required to 
                consider the marker or snp failed.
            mono (float): Percentage of any allele: major homo, 
                minor homo, major het required to consider
                the marker or snp monomorphic.
            poly (dict): Dictionary who's values are 3 element tuples
                representing percentage cutoffs for classifying
                polymorphic markers.
                (format {'Type n': MajorHomo%, MinorHomo%, MajorHet%})
                (default {'Type 1': (0.80, 0.20, 0.10),
                          'Type 2': (0.80, 0.10, 0.20),
                          'Type 3': (0.10, 0.10, 0.10)})
            comp_ops (dict): Dictionary who's values are 3 element tuples
                that correspond with threshold values in poly argument's 
                dictionary.
                (format 'Type n': 'comp_op', 'comp_op', 'comp_op')
                (default {'Type 1': ('<', '>', '<='),
                          'Type 2': ('<', '<=', '>'),
                          'Type 3': ('>', '>', '>')})

        Returns:
            self.data (DataFrame object): DataFrame object with information
                on morphisms for markers.

        Raises:
            ValueError: If the GtManipoulator object does not 
                have allelic frequencies.
        """
        if not self.frequencies:
            raise ValueError("Allelic frequencies must be calculated before morphisms "
                             "can be predicted.")
        if not self.morphed:
            self.data["Morphism"] = None
            gt_helper = _GtAnalyzer(count_cols=self.count_cols, failed=failed, mono=mono,
                                    poly=poly, comp_ops=comp_ops)
            self.data = self.data.apply(gt_helper._predict_morphisms, axis=1)
            self.morphed = True
        return self.data

class _GtAnalyzer:
    """Helper class for processing GtManipulator object data.
    
    Args:
        count_cols (array-like): A list of 'counted' columns for a GtManipulator object.
        missing (dict): Dictionary of any values that should count as missing.
            (default {})
        failed (float): Percentage of missing data required to 
            consider the marker or snp failed.
            (default None)
        mono (float): Percentage of any allele: major homo, 
            minor homo, major het required to consider
            the marker or snap monomorphic.
            (default None)
        poly (dict): Dictionary who's values are 3 element tuples
            representing percentage cutoffs for classifying
            (default None)
        comp_ops (dict): Dictionary who's values are 3 element tuples
            that correspond with threshold values in poly argument's 
            dictionary.

    Attributes:
        count_cols (array-like): A list of 'counted' columns for a GtManipulator object.
            (default None)
        missing (dict): Dictionary of any values that should count as missing.
            (default {})
        failed (float): Percentage of missing data required to 
            consider the marker or snp failed.
            (default None)
        mono (float): Percentage of any allele: major homo, 
            minor homo, major het required to consider
            the marker or snap monomorphic.
            (default None)
        poly (dict): Dictionary who's values are 3 element tuples
            representing percentage cutoffs for classifying
            (default None)
        comp_ops (dict): Dictionary who's values are 3 element tuples
            that correspond with threshold values in poly argument's 
            dictionary.
    """

    def __init__(self, count_cols=None, missing={}, failed=None, mono=None, 
                 poly=None, comp_ops=None):
        self.count_cols = count_cols
        self.missing = missing
        self.failed = failed
        self.mono = mono
        self.poly = poly
        self.comp_ops = comp_ops

    def _get_allele_types(self, data):
        """Determines major and minor homozygous and heterozygous alleles and their counts
        as well as counting 'missing' data.

        Args:
            data (Series object): Series object passed from a GtManipulator object's
                underlying DataFrame object

        Returns:
            series_data (Series object): Contains relevant alleles and missing data calculated
                for the passed Series object.

        Raises:
            ValueError: If count_cols attribute is  None.
        """
        if self.count_cols is None:
            raise ValueError("Count columns not passed from a GtManipulator object.")
        series_data = data
        homo_alleles = []
        het_alleles = []
        missing_alleles = 0
        for col in self.count_cols:
            if col in self.missing:
                if col in series_data.index.values:
                    missing_alleles += series_data[col]
            elif col == col[::-1]:
                homo_alleles.append((col, series_data[col]))
            elif col != col[::-1]:
                het_alleles.append((col, series_data[col]))
        homo_alleles.sort(key=lambda x: x[1], reverse=True)
        het_alleles.sort(key=lambda x: x[1], reverse=True)
        homo_alleles = [pair for pair in homo_alleles if pair[1] != 0]
        het_alleles = [pair for pair in het_alleles if pair[1] != 0]
        series_data["MajorHomo"] = homo_alleles[0][0] if len(homo_alleles) >= 1 else None
        series_data["MajorHomoCount"] = homo_alleles[0][1] if len(homo_alleles) >= 1 != 0 else None
        series_data["MinorHomo"] = homo_alleles[-1][0] if len(homo_alleles) >= 2 else None
        series_data["MinorHomoCount"] = homo_alleles[-1][1] if len(homo_alleles) >= 2 else None
        series_data["MajorHet"] =  het_alleles[0][0] if len(het_alleles) >= 1 else None
        series_data["MajorHetCount"] =  het_alleles[0][1] if len(het_alleles) >= 1 else None
        series_data["MissingCount"] = missing_alleles
        series_data["TotalNotMissing"] = sum([series_data[col] for col in self.count_cols])-series_data["MissingCount"]
        return series_data

    def _predict_morphisms(self, data):
        """Determines potential mono and polymorphic markers or snps.

        Args:
            data (Series object): Series object passed from a GtManipulator object's
                underlying DataFrame object     

        Returns:
            series_data (Series object): Contains morphism assignments based on
                a given threshold.

        Raises:
            ValueError: If any values are None, the comp_ops arguments contains
                elements in the tuple values, or if the poly and comp_ops
                arguments and their tuple values are not the same length.
            KeyError: If any keys in poly are not in comp_ops and vice versa.
        """
        if self.failed is None or self.mono is None or self.poly is None or self.comp_ops is None:
            raise ValueError("No arguments can be None-type.")
        elif not isinstance(self.poly, dict) or not isinstance(self.comp_ops, dict):
            raise TypeError("The poly and comp_ops arguments must be dicts.")
        elif len(self.poly) != len(self.comp_ops):
            raise ValueError("The poly and comp_ops arguments must be the same length.")
        ops = {">": operator.gt,
               "<": operator.lt,
               ">=": operator.ge,
               "<=": operator.le,
               "==": operator.eq}
        series_data = data
        if series_data["MissingCount"]/(series_data["MissingCount"]+series_data["TotalNotMissing"]) > self.failed:
            series_data["Morphism"] = "Failed"
            return series_data
        elif (series_data["MajorHomoCount"]/series_data["TotalNotMissing"] > self.mono or
                series_data["MinorHomoCount"]/series_data["TotalNotMissing"] > self.mono or
                series_data["MajorHetCount"]/series_data["TotalNotMissing"] > self.mono):
            series_data["Morphism"] = "Mono"
            return series_data
        major_homo_count = series_data.fillna(0)["MajorHomoCount"]
        minor_homo_count = series_data.fillna(0)["MinorHomoCount"]
        major_het_count = series_data.fillna(0)["MajorHetCount"]
        total = series_data.fillna(0)["TotalNotMissing"]
        for key in self.poly.keys():
            if key not in self.comp_ops:
                raise KeyError("The poly and comp_ops arguments must have the same keys.")
            elif (self.comp_ops[key][0] not in ops or self.comp_ops[key][1] not in ops or 
                    self.comp_ops[key][2] not in ops):
                raise ValueError("Invalid comparison operator detected. "
                                 " Valid options: [<, >, <=, >=, ==] ")
            elif len(self.comp_ops[key]) != len(self.poly[key]):
                raise ValueError("Tuple values must match in length for each poly comp_ops pair.")
            if (ops[self.comp_ops[key][0]](major_homo_count/total, self.poly[key][0]) and
                    ops[self.comp_ops[key][1]](minor_homo_count/total, self.poly[key][1]) and
                    ops[self.comp_ops[key][2]](major_het_count/total, self.poly[key][2])):
                series_data["Morphism"] = key
                return series_data
        series_data["Morphism"] = "?"
        return series_data
