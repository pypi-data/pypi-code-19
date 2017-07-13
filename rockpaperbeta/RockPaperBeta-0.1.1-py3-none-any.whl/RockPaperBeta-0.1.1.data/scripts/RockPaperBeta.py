import sys
import random
def rps():
    while True:
        game=['rock','paper','scissors']
        choose= input("What do you choose?")
        bob=(random.choice(game))
        if choose==str("rock"):
            print ("I chose "+bob+"!")
            if bob==("paper"):
                 print ("You lose!")
            if bob==("scissors"):
                 print ("You win!")
            if bob==("rock"):
                 print ("We tie!")

        if choose==str("paper"):
            print ("I chose "+bob+"!")
            if bob==("paper"):
                 print ("We tie!")
            if bob==("scissors"):
                print ("You lose!")
            if bob==("rock"):
                 print ("You lose!")
    

        if choose==str("scissors"):
            print ("I chose "+bob+"!")
            if bob==str("paper"):
                print ("You win!")
            if bob==str("scissors"):
                print ("We tie!")
            if bob==str("rock"):
                print ("You lose!")

        bill=input("Want to play again?")
        if bill==str("yes"):
            continue
        if bill==str("no"):
            break
rps()
