import datetime
import random

from klinklang.core.ptc import PossibleMonths


def get_random_dob():
    possible_days = [i for i in range(1, 28)]
    current_year = datetime.datetime.now().year
    possible_years = [i for i in range(current_year - 40, (current_year - 18))]

    year = random.choice(possible_years)
    month = random.choice(PossibleMonths)
    day = random.choice(possible_days)

    return year, month, day
