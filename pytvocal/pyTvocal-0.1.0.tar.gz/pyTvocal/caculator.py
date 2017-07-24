import time
from Tkinter import *


class Calc:
    def __init__(self):
        self.gui()

    def modIt(self):
        firstItem = self.firstItemEntry.get()
        secondItem = self.secondItemEntry.get()
        modRes = int(firstItem) % int(secondItem)
        self.resVar.set(modRes)
        return modRes

    def timeIt(self):
        timeRes = time.localtime(time.time())
        timeRes = time.strftime("%H:%M:%S", timeRes)
        self.resVar.set(timeRes)
        return timeRes

    def plusIt(self):
        firstItem = self.firstItemEntry.get()
        secondItem = self.secondItemEntry.get()
        plusRes = int(firstItem) + int(secondItem)
        self.resVar.set(plusRes)
        return plusRes

    def primeIt(self):
        primeRes = []
        firstItem = self.firstItemEntry.get()
        secondItem = self.secondItemEntry.get()
        for n in range(int(firstItem), int(secondItem)):
            for x in range(2, n):
                if n % x == 0:
                    break
            else:
                primeRes.append(n)
        self.resVar.set(primeRes)
        return primeRes

    def gui(self):
        root = Tk()
        root.title('DIY calculator!')
        self.resVar = StringVar()
        self.resEntry = Entry(textvariable=self.resVar, width=20, state='disabled')
        self.resEntry.grid(row=0, column=0, columnspan=2)
        self.firstItemLabel = Label(text='first item:', width=10)
        self.firstItemLabel.grid(row=1, column=0)
        self.firstItemVar = StringVar()
        self.firstItemVar.set('2')
        self.firstItemEntry = Entry(textvariable=self.firstItemVar, width=10)
        self.firstItemEntry.grid(row=1, column=1)
        self.secondItemLabel = Label(text='second item:', width=10)
        self.secondItemLabel.grid(row=2, column=0)
        self.secondItemVar = StringVar()
        self.secondItemVar.set('8')
        self.secondItemEntry = Entry(textvariable=self.secondItemVar, width=10)
        self.secondItemEntry.grid(row=2, column=1)
        self.modButton = Button(text='mod', command=self.modIt, width=10)
        self.modButton.grid(row=3, column=0)
        self.plusButton = Button(text='plus', command=self.plusIt, width=10)
        self.plusButton.grid(row=3, column=1)
        self.primeButton = Button(text='prime', command=self.primeIt, width=10)
        self.primeButton.grid(row=4, column=0)
        self.timeButton = Button(text='time', command=self.timeIt, width=10)
        self.timeButton.grid(row=4, column=1)
        root.mainloop()
        return 0


if __name__ == '__main__':
    calc = Calc()
