import unittest
import requests


class TestPR(unittest.TestCase):
    def test_pr(self):
        result = requests.get('http://127.0.0.1:8004/user/77dacbc1-eecd-422d-a68c-39021e033082')
        result = result.json()
        assert result['result'] == ['93a1b3e2-1090-497e-863c-e4d634a5c14b']
        assert result['error'] is None

        result = requests.get('http://127.0.0.1:8004/user/test')
        result = result.json()
        assert result['result'] is None
        assert result['error'] == 'Value "test" is not a valid UUID4'


if __name__ == '__main__':
    unittest.main()
