import random
import math
import networkx

lower = int(input("Enter Lower Bound:- "))
upper = int(input("Enter Upper Bound:- "))

x = random.randint(lower, upper)
print("\n\tYou've only ",
      round(math.log(upper -lower + 1, 2)),
      " chances to guess the integer!\n")

count = 0
while count < math.log(upper - lower + 1, 2):
    count += 1
    guess = int(input("Guess a number:- "))

    if x == guess:
        ending = "tries"
        if count == 1:
            ending = "try"
        print("Congratulations! You did it in ",
              count, " ", ending, ".")
        break
    elif x > guess:
        print("Higher")
    else:
        print("Lower")

if count >= math.log(upper - lower + 1, 2):
    print("\nThe number was %d" % x)
    print("\tBetter luck next time!")

