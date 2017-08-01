__author__ = 'jiyue'
import matplotlib.pyplot as plt
import numpy as np


def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion Matrix', cmap=plt.cm.Blues):
    import itertools

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def compute_corr(df, corr_value):
    cor = df.corr()
    cor.loc[:, :] = np.tril(cor, k=-1)  # below main lower triangle of an array
    cor = cor.stack()
    return cor[(cor > corr_value) | (cor < -corr_value)]


def nan_value_analysis(df):
    return df.select_dtypes(include=['float']).describe().T.assign(
        missing_pct=df.apply(lambda x: (len(x) - x.count()) / float(len(x))))
