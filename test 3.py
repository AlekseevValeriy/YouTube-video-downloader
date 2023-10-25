try:
    a = 1
    assert a in [2]
except Exception as e:
    print(type(Exception()).__name__)