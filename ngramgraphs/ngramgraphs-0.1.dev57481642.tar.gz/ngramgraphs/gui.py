import shutil
from tempfile import NamedTemporaryFile
import errno
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

from ngramgraphs.graph import make_ngram_graph
from ngramgraphs.draw import draw_graph


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 800

EXAMPLE_TEXT = 'aaabbaabbba'
DEFAULT_N = 3
DEFAULT_BY_WORDS = False


def get_image(path):
    return ImageTk.PhotoImage(Image.open(path))


def update_graph(text, n, by_words, filename):
    graph = make_ngram_graph(text, n, by_words)
    draw_graph(graph, filename)
    return update_image(filename)


def update_image(filename):
    try:
        image = get_image(filename)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # program has just launched w/o loading an image yet
            image = None
        else:
            raise
    if image is not None:
        imgwidth, imgheight = image.width(), image.height()
    else:
        imgwidth, imgheight = DEFAULT_WIDTH, DEFAULT_HEIGHT
    return image, imgwidth, imgheight


def refresh_canvas(master, image, imgwidth, imgheight, vbar, hbar):
    canvas = tk.Canvas(
        master, yscrollcommand=vbar.set, xscrollcommand=hbar.set,
        width=imgwidth, height=imgheight)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))
    canvas.create_image((0, 0), image=image, anchor='nw')
    canvas.grid(row=0, column=0, rowspan=5)
    return canvas


# TODO: let the user choose the path
def main():
    master = tk.Tk()

    tempfile = NamedTemporaryFile(suffix='.jpg', delete=False)
    filename = tempfile.name
    image, imgwidth, imgheight = update_graph(
        EXAMPLE_TEXT, DEFAULT_N, DEFAULT_BY_WORDS, filename)
    master.image = image  # prevent garbage collection of image

    text_label = tk.Label(master, text='Text:')
    text_label.grid(row=0, column=2)
    text_input = tk.StringVar()
    entry = tk.Entry(master, textvariable=text_input)
    entry.insert(0, EXAMPLE_TEXT)
    entry.grid(row=0, column=3, columnspan=2, sticky='EW')

    mode_label = tk.Label(text='Mode:')
    mode_label.grid(row=1, column=2)
    by_words = tk.BooleanVar()
    by_words_button = tk.Radiobutton(
        master, text='by words', variable=by_words, value=True)
    by_chars_button = tk.Radiobutton(
        master, text='by characters', variable=by_words, value=False)
    by_words_button.grid(row=1, column=3)
    by_chars_button.grid(row=1, column=4)

    n_label = tk.Label(text='n value:')
    n_label.grid(row=2, column=2)
    default_n = tk.StringVar(master)
    default_n.set(DEFAULT_N)
    n = tk.Spinbox(master, from_=1, to=5, textvariable=default_n)
    n.grid(row=2, column=3)

    vbar = tk.Scrollbar(master, orient=tk.VERTICAL)
    hbar = tk.Scrollbar(master, orient=tk.HORIZONTAL)

    canvas = refresh_canvas(master, image, imgwidth, imgheight, vbar, hbar)

    vbar.grid(row=0, column=1, rowspan=5, sticky='NS')
    vbar.config(command=canvas.yview)

    hbar.grid(row=5, column=0, sticky='EW')
    hbar.config(command=canvas.xview)

    def callback():
        # don't refresh image if input text is empty
        text = text_input.get().strip()
        if not text:
            return
        canvas.grid_forget()  # avoid overlapping of canvasses
        n_value = int(n.get())
        image, imgwidth, imgheight = update_graph(
            text, n_value, by_words.get(), filename)
        master.image = image
        refresh_canvas(master, image, imgwidth, imgheight, vbar, hbar)
    button = tk.Button(
        master, text='Generate new graph', command=callback)
    button.grid(row=3, column=2, columnspan=2)

    def export():
        filename_dest = filedialog.asksaveasfilename(
            parent=master, defaultextension='.jpg')
        filename_src = filename
        shutil.copyfile(filename_src, filename_dest)
    export_button = tk.Button(
        master, text='Export graph to file ...', command=export)
    export_button.grid(row=4, column=2, columnspan=2)

    tk.mainloop()


if __name__ == '__main__':
    main()
