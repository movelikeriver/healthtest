"""
The command line version of blood sugar simulator.

Usage:
    python3 simulator-main.py
"""

from blood_sugar_simulator import datautil, simulator

# main function

actions = [
    # breakfast
    datautil.Action('07:10', datautil.DataType.FOOD, id=18, volume=1.0),
    datautil.Action('07:20', datautil.DataType.FOOD, id=77, volume=0.8),

    # exercise
    datautil.Action('08:50', datautil.DataType.EXERCISE, id=2, volume=0.7),

    # lunch
    datautil.Action('12:10', datautil.DataType.FOOD, id=121, volume=0.5),
    datautil.Action('12:20', datautil.DataType.FOOD, id=111, volume=0.5),

    # snack
    datautil.Action('14:20', datautil.DataType.FOOD, id=81, volume=0.3),

    # exercise
    datautil.Action('15:20', datautil.DataType.EXERCISE, id=6, volume=0.5),

    # dinner
    datautil.Action('18:30', datautil.DataType.FOOD, id=120, volume=0.3),
    datautil.Action('18:40', datautil.DataType.FOOD, id=21, volume=0.4),
    datautil.Action('18:50', datautil.DataType.FOOD, id=20, volume=0.2),

    # exercise
    datautil.Action('20:30', datautil.DataType.EXERCISE, id=3, volume=0.5),
]

granularity_in_minute = 5

results, events_start = simulator.start(actions, granularity_in_minute)
print('\n==== blood sugar ====')
for r in results:
    print(r.to_string())

print('\n==== events ====')
for e in events_start:
    print(e.to_string())

print('\n==== glycation ====')
minutes = simulator.glycation(results, granularity_in_minute)
print('\n{0} minutes in high blood sugar'.format(minutes))
