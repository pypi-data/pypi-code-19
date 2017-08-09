# -*- coding:utf-8 -*-
from framework.bootstrap import MainBootstrap
import argparse
import logging

__author__ = 'jiyue'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('data_file')
    parser.add_argument('output_feature_weight_file')
    parser.add_argument('feature_data_file')
    parser.add_argument('output_score_file')
    args = parser.parse_args()

    output_feature_weight_file = args.output_feature_weight_file
    feature_data_file = args.feature_data_file
    output_score_file = args.output_score_file
    data_file = args.data_file

    main_bootstrap = MainBootstrap()
    main_bootstrap.load_data(file_path=args.data_file)
    main_bootstrap.go_binning(event_identify=1, binning_spec_with=None, binned_other_value=None, binned_width=5,
                              binning_mode='ef')
    main_bootstrap.do_train(params={"class_weight": "balanced"}, model='lr')
    main_bootstrap.output_features_weight(args.output_feature_weight_file)
    main_bootstrap.train_score_card(feature_list=main_bootstrap.fea_list, target='label',
                                    feature_weights_file_path=output_feature_weight_file,
                                    feature_data_file=args.feature_data_file, output_score_file=args.output_score_file)
