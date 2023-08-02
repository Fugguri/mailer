import time


def gen_filename():
    while True:
        pattern = 'file_{}.jpeg'
        t = int(time() * 1000)
        yield pattern.format(str(t))

# g = gen_filename()


def gen1(n):
    for i in n:
        yield i


def gen2(n):
    for i in range(n):
        yield i


g1 = gen1("nikita")
g2 = gen2(4)

tasks = [g1, g2]
while tasks:
    task = tasks.pop(0)
    try:
        i = next(task)
        print(i)
        tasks.append(task)
    except StopIteration:
        pass
