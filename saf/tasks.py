def completeSemanticsEnumerate(single=False):
    pass


def completeSemanticsDecide(skeptically=False):
    pass


_tasks = {
    'EE-CO': completeSemanticsEnumerate
}


def getTasks():
    return _tasks.keys()


def getTaskMethod(task_str):
    try:
        return _tasks[task_str]
    except KeyError:
        print(F'{task_str} is an unsupported problem task!')
        print('Use --problems to see the list of supportted tasks.')
        import sys
        sys.exit(1)
