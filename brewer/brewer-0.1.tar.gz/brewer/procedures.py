from controller import Controller
from slack import BrewerBot
from strike_temp_calculator import calc_strike_temp
import time

con = Controller()
slack = BrewerBot()

vars = {
    "grain": 10.5,
    "water": 13.0,
    "grain_temp": 75.0,
    "mash_time": 3600.0,
    "mash_temp": 122.0,
    "mashout_temp": 172.0
}

def confirm():
    confirm = raw_input()
    if str(confirm) == "y" or str(confirm) == "Y":
        return True
    else:
        return False

def boot():
    print("Booting...")

    con.pid(0)
    con.hlt(0)
    con.pump(0)
    con.rims_to("mash")
    con.hlt_to("mash")

    print("Boot finished")

    slack.send("Ready to go")


def heat_strike_water():
    print("About to heat strike water")

    print("Is the strike water in the mash tun? [y/n] "),
    confirm()

    print("Is the return manifold in the mash tun? [y/n] "),
    confirm()

    print("Is the manual mash tun valve open? [y/n] "),
    confirm()

    con.rims_to("mash")

    con.pump(1)

    print("Is the pump running properly? [y/n] "),
    while not confirm():
        con.pump(0)
        time.sleep(4)
        con.pump(1)

    print("Is the strike water circulating well? [y/n] "),
    confirm()

    strike_temp = calc_strike_temp(vars['water'], vars['grain'], vars['grain_temp'], vars['mash_temp'])

    con.set_sv(strike_temp)
    print("SV has been calculated as " + str(strike_temp))

    slack.send("Strike temperature has been set to %s. Heating strike water." % str(strike_temp))
    print("Turning on the heater")
    con.pid(1)

    con.watch()
    slack.send("Strike water heated.")

def dough_in():
    con.pid(0)
    con.pump(0)
    time.sleep(3)
    print("Ready to dough in")

    print("Confirm when you're done with dough-in [y] ")
    confirm()

def mash():

    con.set_sv(vars["mash_temp"])
    print("Protein rest started")
    slack.send("Protein rest started")

    con.rims_to("mash")
    con.pid(1)
    con.pump(1)

    con.watch()
    time.sleep(20 * 60)
    print("Protein rest ended. Starting ramp up.")
    slack.send("Protein rest ended. Starting ramp up.")


    con.set_sv(150)
    con.pid(1)
    con.watch()
    print("Saccarification rest started")
    slack.send("Saccarification rest started")
    time.sleep(60 * 60)

    print("Saccarification rest ended")
    slack.send("Saccarification rest ended")

def mashout():
    slack.send("Start heating sparge water")
    print("Start heating sparge water")
    print("Mashout started")
    slack.send("Mashout started")
    con.set_sv(vars['mashout_temp'])

    con.pid(1)
    con.pump(1)

    slack.send("Heating to mashout temp. This will take a few minutes.")
    print("Heating to mashout temp")

    con.watch()

    print("Mashout complete")
    slack.send("Mashout complete")

def sparge():
    print("The sparge water better be heated. [y]"),
    confirm()

    print("Sparging started")

    con.hlt_to("mash")
    con.hlt(1)

    print("Waiting for 10 seconds")
    print("Regulate sparge balance")
    time.sleep(10)

    con.rims_to("boil")
    con.pump(1)

    print("Check the sparge balance and ignite the boil tun burner")
    slack.send("Check the sparge balance and ignite the boil tun burner")

    print("Waiting for intervention to turn off pump [y] "),
    confirm()

    con.pid(0)
    con.pump(0)
    con.hlt(0)

    print("Sparging complete")

def top_off():
    print("Do you need to top off? [y/n] "),
    if not confirm():
        return True

    con.hlt_to("boil")
    con.hlt(1)

    print("Waiting for intervention to turn off hlt [y/n] "),
    confirm()

    con.hlt(0)

    print("Topping off complete")

# 95 minutes
def boil():
    slack.send("Boil timers started")
    print("Boil timers started")
    time.sleep(5 * 60)
    slack.send("Add boil hops")
    print("Add boil hops")
    time.sleep(90 * 60)
    slack.send("Add aroma hops")
    print("Add aroma hops")


def master():
    boot()
    heat_strike_water()
    dough_in()
    mash()
    mashout()
    sparge()
    top_off()
    boil()
    return True
