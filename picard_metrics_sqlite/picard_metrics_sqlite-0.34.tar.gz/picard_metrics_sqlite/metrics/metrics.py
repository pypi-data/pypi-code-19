def picard_CalculateHsMetrics_to_df(stats_path, logger):
    select = 'BAIT_SET'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def do_picard_metrics(run_uuid, stats_path, input_state, bam, fasta, engine, logger, metrics_type, wxs_dict = None, vcf = None):
    if metrics_type == 'CollectJumpingLibraryMetrics':
        pass
    elif metrics_type == 'CollectVariantCallingMetrics':
        pass
    elif metrics_type == 'CollectWgsMetricsFromQuerySorted':
        pass
    elif metrics_type == 'CollectWgsMetricsFromSampledSites':
        pass
    elif metrics_type == 'CollectWgsMetricsWithNonZeroCoverage':
        pass
    elif metrics_type == 'EstimateLibraryComplexity':
        pass
    elif metrics_type == 'CalculateHsMetrics':
        table_name = 'picard_' + metrics_type
        df = picard_CalculateHsMetrics_to_df(stats_path, logger)
        if df is not None:
            df_list.append(df)
            table_name_list.append(table_name)
    else:
        logger.debug('Unknown metrics_type: %s' % metrics_type)
    for i, df in enumerate(df_list):
        logger.info('df_list enumerate i=%s:' % i)
        df['run_uuid'] = run_uuid
        df['bam'] = bam
        df['input_state'] = input_state
        df['fasta'] = fasta
        if vcf is not None:
            df['vcf'] = vcf
        table_name = table_name_list[i]
        df.to_sql(table_name, engine, if_exists='append')
    return
