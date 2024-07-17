import pytest


def adjust_params(params):
    def _():
        for v in params:
            if len(v) == 3:
                yield v
            else:
                yield v + (None,)

    return list(_())


def adjust_id_params(params):
    def _():
        for v in params:
            id, v = v[0], v[1:]
            if len(v) == 3:
                yield pytest.param(*v, id=id)
            else:
                yield pytest.param(*v, None, id=id)

    return list(_())


def extract_messages(resp):
    return [m.message for m in resp.context["messages"]]
