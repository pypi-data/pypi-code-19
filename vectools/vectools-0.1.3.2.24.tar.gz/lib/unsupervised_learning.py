"""
This module contains functions related to unsupervised learning.
"""
import sys
import numpy as np
from lib.inputoutput import ParseVectors, _shared_params, _slice_list, Vectors, VectorIO


def k_means_clustering(arg_parser):
    """ Preforms k-means clustering on a set of vectors.


    cat two_clusters.csv
    1,2
    1,4
    1,0
    4,2
    4,4
    4,0

    vectools kmeans -d "," -k 2  k.csv
    0,1,2
    0,1,4
    0,1,0
    1,4,2
    1,4,4
    1,4,0


    """

    from sklearn.cluster import KMeans

    arg_parser.add_argument(
        'matrices',
        nargs='*',
        help='Matrices to input.'
    )

    arg_parser.add_argument(
        '-k',
        required=True,
        type=int,
        help='The number of clusters and centroids to generate.'
    )

    arg_parser.add_argument(
        '-rs', '--random-state',
        type=int,
        default=None,
        help=''
    )

    _shared_params(arg_parser, only_apply_on=True)

    args = arg_parser.parse_args()

    vec_parser = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=False,
        has_row_names=False
    )

    data_frame, sliced_frame = vec_parser.parse_vectors(args.matrices)

    # Predict cluster memberships.
    cluster_obj = KMeans(n_clusters=args.k, random_state=args.random_state).fit(sliced_frame.as_matrix())

    data_frame.insert(0, "Clusters", cluster_obj.labels_)

    out_matrix = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    vectors = data_frame.as_matrix()
    row_titles = data_frame.index
    out_matrix.setcolumntitles(data_frame.columns.values)

    for i in range(len(cluster_obj.labels_)):
            out_matrix.iterative_out(
                str(row_titles[i]),
                vectors[i],
                column_titles=None
            )


def affinity_propagation_clustering(arg_parser):
    """ Preforms k-means clustering on a set of vectors.


    cat two_clusters.csv
    ..

    vectools affcl --damping 0.9 --preference -40 k.csv
    ...


    """

    # from sklearn.cluster import KMeans
    from sklearn.cluster import AffinityPropagation

    arg_parser.add_argument(
        'matrices',
        nargs='*',
        help='Matrices to input.'
    )

    arg_parser.add_argument(
        '--damping',
        required=True,
        type=float,
        help='Damping factor between 0.5 and 1.'
    )

    arg_parser.add_argument(
        '--preference',
        required=True,
        type=float,
        help='Damping factor between 0.5 and 1.'
    )

    arg_parser.add_argument(
        '-rs', '--random-state',
        type=int,
        default=None,
        help=''
    )

    _shared_params(arg_parser, only_apply_on=True)

    args = arg_parser.parse_args()

    vec_parser = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=False,
        has_row_names=False
    )

    data_frame, sliced_frame = vec_parser.parse_vectors(args.matrices)

    # Predict cluster memberships.
    cluster_obj = AffinityPropagation(damping=args.damping,
                                      preference=args.preference).fit(sliced_frame.as_matrix())

    data_frame.insert(0, "Clusters", cluster_obj.labels_)

    out_matrix = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    vectors = data_frame.as_matrix()
    row_titles = data_frame.index
    out_matrix.setcolumntitles(data_frame.columns.values)

    for i in range(len(cluster_obj.labels_)):
            out_matrix.iterative_out(
                str(row_titles[i]),
                vectors[i],
                column_titles=None
            )


def silhouette_score(parser):
    """ Calculate the silhouette score of a set of clusters.

    Input all as one vector
    OR
    as a label vector and main vector

    :param parser:
    :return:
    """
    from sklearn.metrics import silhouette_score

    # metrics.silhouette_score
    #parser.add_argument(
    #    'infile',
    #    nargs='?',
    #    type=str,
    #    default="sys.stdin"
    #)

    parser.add_argument(
        '--labels',
        type=str,
        help="The labels assigning vectors to classes.",
        default=None
    )

    parser.add_argument(
        '--vectors',
        type=str,
        help="Vectors that have been assigned to classes.",
        default=None
    )

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    lable_parser = ParseVectors(
        file_name=args.labels,
        has_col_names=False,  #  args.column_titles,
        has_row_names=False,  #  args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )
    labels = lable_parser.parse()
    labels = np.array([x[0] for x in labels])

    vector_parser = ParseVectors(
        file_name=args.vectors,
        has_col_names=False,  #  args.column_titles,
        has_row_names=False,  #  args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )
    vectors = vector_parser.parse()

    sil_score_obj = silhouette_score(
        vectors,
        labels,
        metric='euclidean',
        # sample_size=sample_size
    )

    print(sil_score_obj)


def som():
    # TODO
    x = 0


def hierarchical_cluster(arg_parser):
    """ Preform hierarchical/agglomerative clustering and returns cluster assignments or a linkage matrix.

    :param arg_parser:
    :return:
    """
    # TODO
    x = 0
    # http://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
    # http://scikit-learn.org/stable/auto_examples/cluster/plot_ward_structured_vs_unstructured.html
    # ward = AgglomerativeClustering(n_clusters=6, linkage='ward').fit(X)
    # ward = AgglomerativeClustering(n_clusters=6, connectivity=connectivity, linkage='ward').fit(X)

    arg_parser.add_argument('matrices',
                            nargs='*',
                            help='Matrices to add to a base matrix.')

    arg_parser.add_argument('--omit',
                            action="store_true",
                            help="Only print points landing within clusters.")

    arg_parser.add_argument('--linkage',
                            action="store_true",
                            help="Return the linkage matrix instead of cluster assignments.")

    arg_parser.add_argument('--n',
                            type=float,
                            default=0.5,
                            help='Maximum distance between two samples to be labeled as in the same neighborhood.')

    _shared_params(arg_parser, only_apply_on=True)

    args = arg_parser.parse_args()

    from sklearn.cluster import AgglomerativeClustering
    import scipy.cluster.hierarchy as sch

    vec_parser = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=False,
        has_row_names=False
    )

    data_frame, sliced_frame = vec_parser.parse_vectors(args.matrices)

    if args.linkage:
        """
        The first two numbers are indeces of clusters, explained in more detail below.
        Third number is the linkage distance.
        Fourth number is the number of genes within the cluster.
        """
        # Linkage matrix
        clusters = sch.linkage(sliced_frame, method='centroid')
        #data_frame.insert("Vec1", "Vec2", "Linkage_Distance", "Vectors_in_Cluster")
    else:
        clusters = AgglomerativeClustering(n_clusters=6, linkage='ward').fit(sliced_frame.as_matrix())
        data_frame.insert(0, "Clusters", clusters.labels_)

    out_matrix = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    vectors = data_frame.as_matrix()
    row_titles = data_frame.index
    out_matrix.setcolumntitles(data_frame.columns.values)

    if args.linkage:

        for i in range(len(clusters)):
            out_matrix.iterative_out(
                None,
                clusters[i],
                column_titles=None
            )

    else:
        for i in range(len(clusters.labels_)):
                if (args.omit and clusters.labels_[i] != -1) or (not args.omit):
                    out_matrix.iterative_out(
                        str(row_titles[i]),
                        vectors[i],
                        column_titles=None)


def DBSCAN(arg_parser):
    """ Preforms density based clustering of a set of vectors.
    :param parser:
    :return:
    """

    from sklearn.cluster import DBSCAN

    arg_parser.add_argument('matrices',
                            nargs='*',
                            help='Matrices to add to a base matrix.')

    arg_parser.add_argument('--omit',
                            action="store_true",
                            help="Only print points landing within clusters.")

    arg_parser.add_argument('--epsilon',
                            type=float,
                            default=0.5,
                            help='Maximum distance between two samples to be labeled as in the same neighborhood.')

    arg_parser.add_argument('--min-samples',
                            type=int,
                            default=5,
                            help='Minimum number of samples needed for a neighborhood to be considered as a core point.')

    _shared_params(arg_parser, only_apply_on=True)

    args = arg_parser.parse_args()

    vec_parser = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=False,
        has_row_names=False
    )

    data_frame, sliced_frame = vec_parser.parse_vectors(args.matrices)

    db = DBSCAN(eps=args.epsilon, min_samples=args.min_samples).fit(sliced_frame.as_matrix())

    data_frame.insert(0, "Clusters", db.labels_)

    out_matrix = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    vectors = data_frame.as_matrix()
    row_titles = data_frame.index
    out_matrix.setcolumntitles(data_frame.columns.values)

    for i in range(len(db.labels_)):
        if (args.omit and db.labels_[i] != -1) or (not args.omit):
            out_matrix.iterative_out(
                str(row_titles[i]),
                vectors[i],
                column_titles=None
            )

