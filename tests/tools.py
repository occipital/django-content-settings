def adjust_params(params):
    def _():
        for v in params:
            if len(v) == 3:
                yield v
            else:
                yield v + (None,)

    return list(_())
