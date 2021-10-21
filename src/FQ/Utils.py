
def to_hhmmssfff(t):
    h = int(t / 3600)
    t -= h * 3600
    m = int(t / 60)
    t -= m * 60
    s = t
    return "{:02d}:{:02d}:{:06.3f}".format(h, m, s)


def timeformat_to_seconds(time_str):
    h, m, s = map(lambda x: int(x), time_str.split(":"))
    return h * 3600 + m * 60 + s
