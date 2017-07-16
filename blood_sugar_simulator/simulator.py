"""
This is a simple simulator for blood sugar change by eating food or doing exercise.

Assume all the blood sugar change is in linear scale always, for example, even if the blood sugar is
very low (50), the exercise still reduces it further down no matter what.

Based on this assumption, this simulator is able to optimize the calculation by getting the gradient
(aka derivative) and total sugar in the key timestamps, then calculate the sugar value by linear interpolation.

Algorithm:
1) convert the actions to event interval array, then sort the events. O(N * logN), N is the number of events.
2) adjust the sugar in each step. this step is O(N), N is the number of events.
"""

import time

from blood_sugar_simulator import datautil


class Event:
    """The event with timestamp, sugar gradient, etc.

    This data structure is designed for the O(N) algorithm for generating the data.
    """

    def __init__(self, name, timestamp, sugar_grad, is_end=False):
        """Init.

        Args:
            name: the event name, like food or exercise name.
            timestamp: the timestamp index, depending on the granularity_in_minute.
            sugar_grad: the sugar change in each step, aka gradient.
            is_end: whether this timestamp index is the end of the event.
        """
        self.name = name
        self.timestamp = timestamp
        self.sugar_grad = sugar_grad
        self.is_end = is_end


class Result:
    """The data structure for the result which will be returned to caller."""

    def __init__(self, index, hhmm, sugar):
        self.index = index
        self.hhmm = hhmm
        self.sugar = sugar

    def to_string(self):
        return 'index={0}, hhmm={1}, sugar={2}'.format(self.index, self.hhmm, self.sugar)


class OutputEvent:
    """The data structure for events which will be returned to caller."""

    def __init__(self, index, hhmm, name, status, sugar_grad):
        self.index = index
        self.hhmm = hhmm
        self.name = name
        self.status = status
        self.sugar_grad = sugar_grad

    def to_string(self):
        return 'index={0}, hhmm={1}, status={3}, sugar_grad={4}, name={2}'.format(
            self.index, self.hhmm, self.name, self.status, self.sugar_grad)


def time_to_index(hhmm, granularity_in_minute):
    """Converts the hhmm time format to time bucket index.

    For example: hhmm='01:43', granularity_in_minute=30, it returns index 3,
    because the time bucket is
    [00:00-00:30, 00:30-01:00, 01:00-01:30, 01:30-02:00]

    Args:
        hhmm: the 24h time format, e.g. '17:39'.
        granularity_in_minute: the time bucket size by minute, recommend to use 10min or 5min level.

    Returns:
        The index of time bucket of the day.
    """

    segs = hhmm.split(':')
    return int((int(segs[0]) * 60 + int(segs[1])) / granularity_in_minute)


def index_to_time(index, granularity_in_minute):
    """Converts time bucket index to hhmm time format. Similar with time_to_index().

    Args:
        index: the index of time bucket of the day.
        granularity_in_minute: the time bucket size by minute, recommend to use 10min or 5min level.

    Returns:
        The 24h time format, e.g. '17:39'.
    """
    v = granularity_in_minute * index
    return '{hh:02d}:{mm:02d}'.format(hh = int(v / 60), mm = v % 60)


def actions_to_events(actions, granularity_in_minute):
    """Converts actions to events.

    Args:
        actions: the datautil.Action with data type, id and timestamp.
        granularity_in_minute: the granularity for tracking the metrics, e.g. every 30 minutes.

    Returns:
        The events sorted by time.
    """

    foods = datautil.load_food_dict()
    exercises = datautil.load_exercise_dict()

    events = []
    for a in actions:
        start = time_to_index(a.hhmm, granularity_in_minute)
        if a.datatype == datautil.DataType.FOOD:
            item = foods[a.id]
        elif a.datatype == datautil.DataType.EXERCISE:
            item = exercises[a.id]
        else:
            print('invalid ' + a.id)

        # assume both food and exercise are linear scale to blood sugar change
        elapse_in_hour = item.elapse_in_hour * a.volume
        total_sugar = item.total_sugar * a.volume

        # convert the hour unit to granularity_in_minute
        steps = int(elapse_in_hour * 60 / granularity_in_minute)
        sugar_grad = float(total_sugar) / steps
        end = start + steps
        events.append(Event(item.name, start, sugar_grad, is_end=False))
        events.append(Event(item.name, end, sugar_grad, is_end=True))

    return sorted(events, key=lambda e: e.timestamp)


def elapse(sugar, sugar_grad, granularity_in_minute, in_events, start_ts, end_ts):
    """Generates the sugar data by given start and end timestamps.

    Assume the sugar change is in linear scale.

    Args:
        sugar: the sugar in the start timestamp.
        sugar_grad: sugar grad in each step.
        start_ts: the start timestamp index.
        end_ts: the end timestamp index.

    Returns:
        array of results, sugar after processing
    """

    results = []
    for ts in range(start_ts, end_ts):
        if in_events == 0:
            if sugar < 80 and sugar_grad > 0:
                sugar += sugar_grad
            elif sugar > 80 and sugar_grad < 0:
                sugar += sugar_grad
        else:
            sugar += sugar_grad
        msg = 'timestamp {0} {3}, sugar {1}, grad {2}'.format(
            ts, sugar, sugar_grad, index_to_time(ts, granularity_in_minute))
        results.append(Result(ts, index_to_time(ts, granularity_in_minute), sugar))

    return results, sugar


def start(actions, granularity_in_minute):
    """Starts the simulator for this day.

    See the algorithm description on the of this file.

    Args:
        actions: the defined actions of the given day.
        granularity_in_minute: the granularity of each step.

    Returns:
        the array of results.
        the array of events.
    """

    events = actions_to_events(actions, granularity_in_minute)

    normal_grad = granularity_in_minute

    sugar_grad = 0.0
    sugar = 80.0  # preconfigured
    end_of_day = time_to_index('24:00', granularity_in_minute)

    last_timestamp = 0
    in_events = 0
    results = []
    start_events = []
    for e in events:
        # simulator the events in this previous time window.
        arr, sugar = elapse(sugar, sugar_grad, granularity_in_minute, in_events, last_timestamp, e.timestamp)
        results += arr
        # it's linear scale and accumulative.
        if e.is_end:
            sugar_grad -= e.sugar_grad
            status = ' end '
            in_events -= 1
        else:
            sugar_grad += e.sugar_grad
            status = 'begin'
            in_events += 1

        if in_events == 0:
            # If neither food nor exercise is affecting your blood sugar (it has been more than 1 or 2 hours),
            # it will approach 80 linearly at a rate of 1 per minute.
            if sugar > 80.0:
                sugar_grad = -normal_grad
            elif sugar < 80.0:
                sugar_grad = normal_grad

        start_events.append(
            OutputEvent(e.timestamp, index_to_time(e.timestamp, granularity_in_minute), e.name, status, e.sugar_grad))
        last_timestamp = e.timestamp

    arr, sugar = elapse(sugar, sugar_grad, granularity_in_minute, in_events, last_timestamp, end_of_day)
    results += arr
    
    return results, start_events


def glycation(results, granularity_in_minute):
    """Calculate glycation

    For every minute your blood sugar stays above 150, increment 'glycation' by 1.
    This is a measure of how much crystallized sugar is accumulating in your blood stream which increases
    heart disease risk.

    Args:

    Returns:
        how many minutes are this person in the high blood sugar status.
    """

    threshold = 150  # preconfigured

    arr = [r for r in results if r.sugar >= threshold]
    for r in arr:
        print(r.to_string())

    return granularity_in_minute * len(arr)
