import Tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.createWidgets()
        #self.after(500, lambda: self.focus_force())


    def createWidgets(self):
        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack()
        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit)
        self.quitButton.grid()

        self.console = tk.Text(self, height=40, width=100,
                               state=tk.DISABLED)
        #self.console.config(state=tk.DISABLED)
        self.console.grid()

    def append_text(self, text):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.config(state=tk.DISABLED)

app = Application()
app.master.title('Sample application')
app.mainloop()
