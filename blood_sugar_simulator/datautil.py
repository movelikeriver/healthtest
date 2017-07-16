from enum import Enum
import csv


class DataType(Enum):
    """The enum of datatype."""
    FOOD = 1
    EXERCISE = 2


class Item:
    """An item in the database."""

    def __init__(self, type, id, name, total_sugar, elapse_in_hour):
        self.type = type
        self.id = id
        self.name = name
        self.total_sugar = total_sugar
        self.elapse_in_hour = elapse_in_hour


def load_food_dict():
    """Loads the food database to a dict."""

    m = {}
    with open('data/FoodDB.csv') as csvfile:
        r = csv.reader(csvfile)
        next(r, None)  # skip the headers
        for row in r:
            if len(row) != 3:
                raise Exception('error: ' + row)

            m[int(row[0])] = Item(DataType.FOOD, int(row[0]), row[1], int(row[2]), 2)
    return m


def load_exercise_dict():
    """Loads the exercise database to a dict."""

    m = {}
    with open('data/Exercise.csv') as csvfile:
        r = csv.reader(csvfile)
        next(r, None)  # skip the headers
        for row in r:
            if len(row) != 3:
                raise Exception('error: ' + row)

            m[int(row[0])] = Item(DataType.EXERCISE, int(row[0]), row[1], -int(row[2]), 1)
    return m


class Action:
    """Eat food or exercise."""

    def __init__(self, hhmm, datatype, id, volume):
        """Init.

        Args:
            hhmm: the string of 24h time format 'hh:mm', e.g. '17:32'.
            datatype: DataType enum.
            id: the data id in the database.
            volume: food or exercise volume, aka serving size.
        """
        self.hhmm = hhmm
        self.datatype = datatype
        self.id = id
        self.volume = volume
