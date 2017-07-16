import unittest

from blood_sugar_simulator import datautil, simulator


class TestSimulator(unittest.TestCase):

    def test_time_to_index(self):
        self.assertEqual(simulator.time_to_index('00:00', 30), 0)
        self.assertEqual(simulator.time_to_index('02:45', 30), 5)
        self.assertEqual(simulator.time_to_index('02:45', 60), 2)
        self.assertEqual(simulator.time_to_index('02:30', 30), 5)
        self.assertEqual(simulator.time_to_index('24:00', 30), 48)

    def test_index_to_time(self):
        self.assertEqual(simulator.index_to_time(0, 30), '00:00')
        self.assertEqual(simulator.index_to_time(5, 30), '02:30')
        self.assertEqual(simulator.index_to_time(2, 60), '02:00')
        self.assertEqual(simulator.index_to_time(48, 30), '24:00')

    def test_actions_to_events(self):
        events = simulator.actions_to_events([
            datautil.Action('07:10', datautil.DataType.FOOD, 18, 1.0),
            datautil.Action('07:40', datautil.DataType.EXERCISE, 4, 0.5)], 10)

        self.assertEqual(4, len(events))

        self.assertEqual(events[0].timestamp, 43)
        self.assertEqual(events[0].sugar_grad, 4.25)
        self.assertEqual(events[0].is_end, False)

        self.assertEqual(events[1].timestamp, 46)
        self.assertEqual(events[1].sugar_grad, -10.0)
        self.assertEqual(events[1].is_end, False)

        self.assertEqual(events[2].timestamp, 49)
        self.assertEqual(events[2].sugar_grad, -10.0)
        self.assertEqual(events[2].is_end, True)

        self.assertEqual(events[3].timestamp, 55)
        self.assertEqual(events[3].sugar_grad, 4.25)
        self.assertEqual(events[3].is_end, True)


if __name__ == '__main__':
    unittest.main()
