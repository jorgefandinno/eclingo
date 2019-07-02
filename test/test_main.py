INPUT_PATH = 'test/g91/input/'
OUTPUT_PATH = 'test/g91/output/'


def test_prog():
    for i in range(1, 7):
        input_path = INPUT_PATH + ('prog0%s.lp' % i)
        result = g91.process(input_path)
        pretty_result = support.formalize(result)
        with open(OUTPUT_PATH + ('sol0%s.txt' % i, 'r')) as myfile:
            sol = myfile.read()
        assert pretty_result == sol
