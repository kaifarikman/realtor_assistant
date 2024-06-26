import datetime


def check_number(s: str):
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return "error"


def check_date(s: str):
    try:
        s = list(map(int, s.split('.')))
        date = datetime.datetime(int(s[2]), int(s[1]), int(s[0]))
        return True, "OK"
    except Exception as e:
        return False, e


# Python3 program for the above approach
from math import gcd


# Function to convert the floating
# values into fraction
def findFraction(s):
    # Initialize variables
    be_deci = ""
    af_deci = ""
    reccu = ""

    x = True
    y = False
    z = False

    # Traverse the floating string
    for i in range(len(s)):

        # Check if decimal part exist
        if (s[i] == '.'):
            x = False
            y = True
            continue

        # Check if recurrence
        # sequence exist
        if (s[i] == '('):
            z = True
            y = False
            continue

        # Retrieve decimal part
        # and recurrence resquence
        if (x):
            be_deci += s[i]

        if (y):
            af_deci += s[i]

        if (z):

            # Traverse the string
            while i < len(s) and s[i] != ')':
                reccu += s[i]
                i += 1

            break

    # Convert to integer
    num_be_deci = int(be_deci)
    num_af_deci = 0

    # If no recurrence sequence exist
    if len(af_deci) != 0:
        num_af_deci = int(af_deci)

    # Initialize numerator & denominator
    numr = (num_be_deci *
            pow(10, len(af_deci)) +
            num_af_deci)

    deno = pow(10, len(af_deci))

    # No recurring term
    if len(reccu) == 0:
        gd = gcd(numr, deno)

        # Print the result
        return numr // gd, "/", deno // gd

    # If recurring term exist
    else:

        # Convert recurring term to integer
        reccu_num = int(reccu)

        # reccu.size() is num of
        # digit in recur term
        numr1 = (numr * pow(10, len(reccu)) +
                 reccu_num)

        deno1 = deno * pow(10, len(reccu))

        # eq 2 - eq 1
        res_numr = numr1 - numr
        res_deno = deno1 - deno

        gd = gcd(res_numr, res_deno)

        return res_numr // gd, " / ", res_deno // gd
