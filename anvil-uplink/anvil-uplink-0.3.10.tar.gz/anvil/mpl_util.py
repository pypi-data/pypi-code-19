import matplotlib.pyplot as plt
import anvil
import io


#!defFunction(anvil.mpl_util,anvil.Media instance)!2: "Return the current Matplotlib figure as an PNG image. Returns an Anvil Media object that can be displayed in Image components." ["plot_image"]
def plot_image():
  with io.BytesIO() as buf:
    plt.savefig(buf, format='png')
    buf.seek(0)    
    return anvil.BlobMedia('image/png', buf.read())
