import os
import unittest

from morningstar import sysex_converter


class TestSysexConverter(unittest.TestCase):

    @unittest.skip("under development")
    def test_debug_yaml_matches_sysex(self):
        with open(os.path.dirname(__file__) + '/../../yaml/debug.yml', 'r') as expectation_file:
            yaml_output = sysex_converter.process_file(os.path.dirname(__file__) + '/debug.syx')
            print(yaml_output)
            actual = yaml_output.split("\n")
            expectation = expectation_file.readlines()
            for i, line in enumerate(expectation):
                print("Checking line " + str(i + 1))
                print("Expected : " + line[:-1])
                print("Generated: " + actual[i])
                self.assertEqual(actual[i], line.rstrip())


if __name__ == "__main__":
    unittest.main()
