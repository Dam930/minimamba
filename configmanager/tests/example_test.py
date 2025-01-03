import pytest


class TestExample:
    @pytest.mark.parametrize("variable", [5, 7])
    def test_size(self, variable):
        assert variable > 0
