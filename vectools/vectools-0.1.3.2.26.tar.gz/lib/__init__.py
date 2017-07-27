"""
# This file controls which input names call which functions.


"""

operations_dict = {
    "Normalization": {
        "zscorenorm": "lib.normalization.z_score_normalization",
        "quantnorm":  "lib.normalization.quantile_normalization",
        "medpolish":  "lib.normalization.median_polish_normalization"
    },
    "Math": {
        "add":         "lib.mathematics.add",
        "subtract":    "lib.mathematics.subtract",
        "multiply":    "lib.mathematics.multiply",
        "dotproduct":  "lib.mathematics.dot_product",
        "inverse":     "lib.mathematics.inverse",
        "determinant": "lib.mathematics.determinant",
        "eigenvec":    "lib.mathematics.eigen_vectors",
        "eigenvalues": "lib.mathematics.eigen_values",
        "sum":         "lib.mathematics.sum_up"
    },
    "Manipulation": {
        "append":       "lib.manipulation.append_values_to",
        "aggregate":    "lib.manipulation.aggregate",
        "creatematrix": "lib.manipulation.create_matrix",
        "format":       "lib.manipulation.format_vec",
        "chop":         "lib.manipulation.chop",
        "concat":       "lib.manipulation.concatenate",
        "join":         "lib.manipulation.join",
        "vrep":         "lib.manipulation.vrep",
        "slice":        "lib.manipulation.vec_slice",
        "sort":         "lib.manipulation.vector_sort",
        "transpose":    "lib.manipulation.transpose",
        "unique":       "lib.manipulation.unique"
        # "to_svmlight": manipulation.to_svmlight,
        # "svml_to_csv": manipulation.to_csv,
        # "makeaddable": makeaddable,
        # "append_matrix": append_matrix,
        # "max": colmax,
    },
    "Analysis and Statistics": {
        # "runLDA":     "lib.analysis.run_lda",
        "min":        "lib.analysis.minimum",
        "max":        "lib.analysis.maximum",
        "median":     "lib.analysis.median",
        "sd":         "lib.analysis.sd",
        "mean":       "lib.analysis.average",
        "percentile": "lib.analysis.percentile",
        "pearson":    "lib.analysis.pearson_group",
        "pca":        "lib.analysis.run_pca",
        # "shape":      "lib.analysis.shape",
        "spearman":   "lib.analysis.spearman",
        "confmat":    "lib.analysis.confusion_matrix",
        "roc":        "lib.analysis.roc_curve"
    },
    "Descriptors": {
        "ncomp":       "lib.descriptor_CLI_interfaces.ncomposition_command_line",
        "splitncomp":  "lib.descriptor_CLI_interfaces.split_ncomposition_command_line",
        "physchem":    "lib.descriptor_CLI_interfaces.physicochemical_properties_ncomposition_command_line",
        "geary":       "lib.descriptor_CLI_interfaces.geary_autocorrelation_command_line",
        "mbroto":      "lib.descriptor_CLI_interfaces.normalized_moreaubroto_autocorrelation_command_line",
        "moran":       "lib.descriptor_CLI_interfaces.moran_autocorrelation_command_line",
        "pseudoaac":   "lib.descriptor_CLI_interfaces.pseudo_amino_acid_composition_command_line",
        "seqordcoup":  "lib.descriptor_CLI_interfaces.sequence_order_coupling_number_total_command_line",
        "quasiseqord": "lib.descriptor_CLI_interfaces.quasi_sequence_order_command_line",
        "summary":     "lib.analysis.summary"
    },
    "Supervised Learning": {
        "svmtrain":    "lib.supervised_learning.svm_train",
        "svmclassify": "lib.supervised_learning.svm_classify",
        "linreg":      "lib.supervised_learning.linear_regression",
        # "neuralnet":   "lib.supervised_learning.neural_network",
        # "randforest":  "lib.supervised_learning.random_forest"
    },
    "Unsupervised Learning": {
        "kmeans":   "lib.unsupervised_learning.k_means_clustering",
        "dbscan":   "lib.unsupervised_learning.DBSCAN",
        "affcl":    "lib.unsupervised_learning.affinity_propagation_clustering",
        "hierarc":  "lib.unsupervised_learning.hierarchical_cluster",
        "silscore": "lib.unsupervised_learning.silhouette_score",
    },
    "Graph Operations": {
        "edges":       "lib.graph.listedges",
        "addedge":     "lib.graph.addedge",
        "addnode":     "lib.graph.addnode",
        "paths":       "lib.graph.listpaths",
        "graphformat": "lib.graph.graphformat",
    }
}
