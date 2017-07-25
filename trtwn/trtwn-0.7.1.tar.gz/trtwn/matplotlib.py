import scipy.constants as sc
from trtwn.fs import changeExtension
import matplotlib as mpl
from matplotlib import pylab as plt

def figsize(scale, textwidthInPt, heightRatio=1/sc.golden_ratio): # Get this from LaTeX using \the\textwidth inside \begin{document}\end{document}
    textwidthInInch = textwidthInPt / 72.27 # Latex's point size is **not** 72 pt/in
    figWidthInInch = textwidthInInch * scale
    figHeightInInch = figWidthInInch * heightRatio
    return [figWidthInInch, figHeightInInch]

def newfig(scale, textwidthInPt, heightRatio=1/sc.golden_ratio):
    size = figsize(scale, textwidthInPt, heightRatio)
    return plt.figure(figsize=size)

def savePgfAndPdf(filepath):
    pgf = changeExtension(filepath, "pgf")
    pdf = changeExtension(filepath, "pdf")
    plt.savefig(pgf, dpi=300)
    plt.savefig(pdf, dpi=300)

def arrowed_spines(fig, ax):

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # removing the default axis on all sides:
    for side in ['bottom','right','top','left']:
        ax.spines[side].set_visible(False)

    # removing the axis ticks
    plt.xticks([]) # labels
    plt.yticks([])
    ax.xaxis.set_ticks_position('none') # tick markers
    ax.yaxis.set_ticks_position('none')

    # get width and height of axes object to compute
    # matching arrowhead length and width
    dps = fig.dpi_scale_trans.inverted()
    bbox = ax.get_window_extent().transformed(dps)
    width, height = bbox.width, bbox.height

    # manual arrowhead width and length
    hw = 1./20.*(ymax-ymin)
    hl = 1./20.*(xmax-xmin)
    lw = .2 # axis line width
    ohg = 0.3 # arrow overhang

    # compute matching arrowhead length and width
    yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
    yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

    # draw x and y axis
    ax.arrow(xmin, 0, xmax-xmin, 0., fc='k', ec='k', lw = lw,
             head_width=hw, head_length=hl, overhang = ohg,
             length_includes_head= True, clip_on = False)

    ax.arrow(0, ymin, 0., ymax-ymin, fc='k', ec='k', lw = lw,
             head_width=yhw, head_length=yhl, overhang = ohg,
             length_includes_head= True, clip_on = False)
