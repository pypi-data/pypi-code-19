#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import glob
import os.path
import traceback
import pickle
import numpy as np
from skimage import io
from skimage.feature import hog
from sklearn import datasets, metrics, ensemble
from tempfile import TemporaryDirectory


DEFAULT_PICKLE_FILENAME = os.path.expanduser(
    '~/.image_dimension_classifier.pickle')
SYSTEM_PICKLE_FILENAME = os.path.join(
    os.path.dirname(__file__),
    '..', 'data', 'image_dimension_classifier.pickle')
IMAGE_FILE_EXTENSIONS = (
    'jpg', 'JPG',
    'jpeg', 'JPEG',
    'png', 'PNG,'
    'gif', 'GIF'
)


def get_new_classifier(data, target):
    classifier = ensemble.RandomForestClassifier(
        n_estimators=20,
        max_depth=3,
        criterion='gini')
    classifier.fit(data, target)
    return classifier


def get_maked_classifiler(
        pickle_filename,
        default_pickle_filename=DEFAULT_PICKLE_FILENAME):
    if pickle_filename is not None and os.path.exists(pickle_filename):
        pass
    elif os.path.exists(DEFAULT_PICKLE_FILENAME):
        pickle_filename = DEFAULT_PICKLE_FILENAME
    else:
        pickle_filename = SYSTEM_PICKLE_FILENAME

    try:
        with open(pickle_filename, mode='rb') as f:
            # TODO: pickle_filenameが不正な形式のときのエラー処理
            return pickle.load(f)
    except Exception as e:
        raise Exception('error is occured when pickle is loaded.')


def load_images(filenames, with_label=True, convert_image=True):
    hogs = np.ndarray((len(filenames), 57600), dtype=np.float)
    if with_label:
        labels = np.ndarray(len(filenames), dtype=np.int)

    with TemporaryDirectory() as tmpdir_name:
        if convert_image:
            filenames = crop_filenames(filenames, tmpdir_name)

        for j, filename in enumerate(filenames):
            image = io.imread(filename, as_grey=True)
            hogs[j] = hog(
                image,
                orientations=9,
                pixels_per_cell=(5, 5),
                cells_per_block=(5, 5),
                block_norm='L2-Hys'
            )
            if with_label:
                labels[j] = os.path.split(filename)[-1][0]

    if with_label:
        return datasets.base.Bunch(
            data=hogs,
            target=labels.astype(np.int),
            target_names=np.arange(2),
            DESCR=None)
    else:
        return datasets.base.Bunch(
            data=hogs,
            DESCR=None)


def show_statics(target, predicted):
    print("Accuracy:{}".format(
        metrics.accuracy_score(target, predicted)))
    print("Confusion matrix:\n{}".format(
        metrics.confusion_matrix(target, predicted)))
    print("Precision:{}".format(
        metrics.precision_score(target, predicted, pos_label=3)))
    print("Recall:{}".format(
        metrics.recall_score(target, predicted, pos_label=3)))
    print("F-measure:{}".format(
        metrics.f1_score(target, predicted, pos_label=3)))


def show_predicted_images(predicted_filenames, predicted):
    for filename, predict in zip(predicted_filenames, predicted):
        text = '{:<{}}: {}d'.format(
            filename,
            max(map(len, predicted_filenames)) - 1,
            predict)
        print(text)


def get_image_filenames(path):
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        filenames = list()
        for ext in IMAGE_FILE_EXTENSIONS:
            for image_filename in (glob.glob(
                    os.path.join(path, '*.{}'.format(ext)))):
                filenames.append(image_filename)
        return filenames
    else:
        return None


def crop_filenames(filenames, tmpdir_name):
    tmp_filenames = list()
    for filename in filenames:
        basename, ext = os.path.splitext(filename)
        barename = os.path.splitext(os.path.split(filename)[-1])[0]
        tmp_barename = '{}_cropped'.format(barename)
        tmp_filename = os.path.join(tmpdir_name, tmp_barename) + '.png'
        cmd = 'convert {}{} -crop 100x100+0+0 png24:{}'.format(
            basename, ext, tmp_filename)
        os.system(cmd)
        tmp_filenames.append(tmp_filename)
    return tmp_filenames


def update_pickle_file(
        classifier,
        pickle_filename=None,
        default_pickle_filename=DEFAULT_PICKLE_FILENAME):
    if not pickle_filename:
        pickle_filename = default_pickle_filename

    with open(os.path.expanduser(pickle_filename), mode='wb') as f:
        pickle.dump(classifier, f)


def get_either_show_statics(filenames):
    if len(filenames) <= 1:
        return False

    for filename in filenames:
        filename = os.path.split(filename)[-1]
        if not(filename.startswith('2d') or filename.startswith('3d')):
            return False
    return True


def get_parser():
    parser = argparse.ArgumentParser(description='classify image dimension')

    parser.add_argument(
        '--train', '-t',
        action='store',
        dest='train_path',
        help='training'
    )
    parser.add_argument(
        '--predict', '-p',
        action='store',
        dest='predicted_path',
        help='predict')
    parser.add_argument(
        '--pickle-filename', '-f',
        action='store',
        dest='pickle_filename',
        help='indicate pickle filename'
    )
    parser.add_argument(
        '--only-stats',
        action='store_true',
        dest='show_only_statics',
        help='show only statics as result'
    )
    parser.add_argument(
        '--not-convert',
        action='store_true',
        dest='not_convert_image',
        help='not convert image'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        dest='debug_mode',
        help='debug mode'
    )

    return parser


def main():
    args = get_parser().parse_args()
    try:
        if args.train_path:
            if not os.path.isdir(args.train_path):
                raise FileNotFoundError('train path is not found.')

            training_filenames = get_image_filenames(args.train_path)
            if training_filenames is None:
                raise FileNotFoundError('training path is not found')

            train = load_images(
                training_filenames,
                convert_image=not args.not_convert_image)
            classifier = get_new_classifier(train.data, train.target)

            update_pickle_file(
                classifier,
                args.pickle_filename,
                os.path.expanduser(DEFAULT_PICKLE_FILENAME))

        if args.predicted_path:
            predicted_path = args.predicted_path

            predicted_filenames = get_image_filenames(predicted_path)
            if predicted_filenames is None:
                raise FileNotFoundError('predicted path is not found')

            classifier = get_maked_classifiler(args.pickle_filename)
            view_statics = get_either_show_statics(predicted_filenames)
            test = load_images(
                predicted_filenames,
                with_label=view_statics,
                convert_image=not args.not_convert_image)
            predicted = classifier.predict(test.data)

            if not args.show_only_statics:
                show_predicted_images(predicted_filenames, predicted)

            if view_statics:
                show_statics(test.target, predicted)
    except Exception as e:
        print("Error is occured.", file=sys.stderr)
        if args.debug_mode:
            traceback.print_exc()
        else:
            print(e, file=sys.stderr)


if __name__ == '__main__':
    main()
