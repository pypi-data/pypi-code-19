data_set = dendropy.DataSet.get(
    path="path/to/file",
    schema="nexus",
    label=None,
    taxon_namespace=None,
    exclude_chars=False,
    exclude_trees=False,
    rooting="default-unrooted",
    edge_length_type=float,
    suppress_edge_lengths=False,
    extract_comment_metadata=True,
    store_tree_weights=False,
    encode_splits=False,
    finish_node_fn=None,
    case_sensitive_taxon_labels=False,
    preserve_underscores=False,
    suppress_internal_node_taxa=True,
    suppress_leaf_node_taxa=False,
    terminating_semicolon_required=True,
    ignore_unrecognized_keyword_arguments=False,
    )



