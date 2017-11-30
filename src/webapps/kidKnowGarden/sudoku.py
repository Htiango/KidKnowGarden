from itertools import product
import random
import copy
import timeit


def solve_sudoku(size, grid):
    """
    solve sudoku using algorithm X
    :param size:
    :param grid:
    :return:
    """
    R, C = size
    N = R * C
    X = ([("rc", rc) for rc in product(range(N), range(N))] +
         [("rn", rn) for rn in product(range(N), range(1, N + 1))] +
         [("cn", cn) for cn in product(range(N), range(1, N + 1))] +
         [("bn", bn) for bn in product(range(N), range(1, N + 1))])
    Y = dict()
    for r, c, n in product(range(N), range(N), range(1, N + 1)):
        b = (r // R) * R + (c // C)  # Box number
        Y[(r, c, n)] = [
            ("rc", (r, c)),
            ("rn", (r, n)),
            ("cn", (c, n)),
            ("bn", (b, n))]
    X, Y = exact_cover(X, Y)
    for i, row in enumerate(grid):
        for j, n in enumerate(row):
            if n:
                select(X, Y, (i, j, n))
    for solution in solve(X, Y, []):
        for (r, c, n) in solution:
            grid[r][c] = n
        yield grid


def exact_cover(X, Y):
    """
    if no conflict
    :param X:
    :param Y:
    :return:
    """
    X = {j: set() for j in X}
    for i, row in Y.items():
        for j in row:
            X[j].add(i)
    return X, Y


def solve(X, Y, solution):
    """
    solve sudoku
    :param X:
    :param Y:
    :param solution:
    :return:
    """
    if not X:
        yield list(solution)
    else:
        c = min(X, key=lambda c: len(X[c]))
        for r in list(X[c]):
            solution.append(r)
            cols = select(X, Y, r)
            for s in solve(X, Y, solution):
                yield s
            deselect(X, Y, r, cols)
            solution.pop()


def select(X, Y, r):
    """
    select if OK
    :param X:
    :param Y:
    :param r:
    :return:
    """
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].remove(i)
        cols.append(X.pop(j))
    return cols


def deselect(X, Y, r, cols):
    """
    deselect if not OK
    :param X:
    :param Y:
    :param r:
    :param cols:
    :return:
    """
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)


def get_random_num(sudoku, index):
    """
    get a random index of possible candidates
    :param sudoku:
    :param index:
    :return:
    """
    candidate = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    row = int(index / 9)
    col = index % 9

    grid_x = int(row / 3) * 3
    grid_y = int(col / 3) * 3

    j = 0
    while j < col:
        if sudoku[row * 9 + j] in candidate:
            candidate.remove(sudoku[row * 9 + j])
        j += 1

    i = 0
    while i < row:
        if sudoku[i * 9 + col] in candidate:
            candidate.remove(sudoku[i * 9 + col])
        i += 1

    for _i in range(0, 3):
        for _j in range(0, 3):
            if sudoku[(grid_x + _i) * 9 + grid_y + _j] in candidate:
                candidate.remove(sudoku[(grid_x + _i) * 9 + grid_y + _j])

    if len(candidate) == 0:
        random_num = -1
    else:
        random_num = random.choice(candidate)

    return random_num


def sudoku_generate_backtracking():
    """
    use backtracking to generate a full matrix sudoku
    :return:
    """
    sudoku = [0] * 81
    i = 0
    while i < 81:
        random_num = get_random_num(sudoku, i)
        if random_num == -1:
            sudoku = [0] * 81
            i = 0
        else:
            sudoku[i] = random_num
            i += 1
    return sudoku


def change_style(sudoku):
    """
    format the sudoku input
    :param sudoku:
    :return:
    """
    sudoku = sudoku.split(',')
    sudoku = [int(i) for i in sudoku]
    sudoku = [sudoku[x:x + 9] for x in range(0, 81, 9)]
    return sudoku


def check_submit_answer(sudoku):
    """
    check if submit answer is correct
    :param sudoku:
    :return: 0 for not complete answer, -1 for wrong answer, 1 for correct answer
    """
    if sudoku.find("0") >=0:
        return 0

    try:
        sudoku = change_style(sudoku)
        generator = solve_sudoku((3, 3), sudoku)
        solution = next(generator)
    except (KeyError,ValueError,StopIteration) as e1:
        return -1
    return 1


def get_answer(sudoku):
    """
    get the solution of teh sudoku
    :param sudoku:
    :return:
    """
    sudoku = change_style(sudoku)
    generator = solve_sudoku((3, 3), sudoku)
    solution = next(generator)
    solution = sum(solution, [])
    return solution


def get_one_hint(sudoku):
    """
    give user a hint step
    :param sudoku:
    :return: (false, false) if nowhere to hint, (-1,-1) if KeyError or valueError happens, otherwise (index, value)
    """
    sudoku = sudoku.split(',')
    try:
        sudoku = [int(i) for i in sudoku]
    except ValueError as name:
        return (-2, -2)
    enable_indexes = [i for i, x in enumerate(sudoku) if x == 0]
    if len(enable_indexes) == 0:
        return (False, False)
    random_index = random.choice(enable_indexes)
    sudoku = [sudoku[x:x + 9] for x in range(0, 81, 9)]
    generator = solve_sudoku((3, 3), sudoku)
    try:
        solution = next(generator)
    except (KeyError,StopIteration) as name:
        return (-1,-1)
    solution = sum(solution, [])
    value = solution[random_index]
    return (random_index, value)


def unique_answer(grid):
    """
    check if there is unique solution
    :param grid:
    :return:
    """
    generator = solve_sudoku((3, 3), grid)
    count = 0
    try:
        while 1:
            next(generator)
            count += 1
    except StopIteration:
        # print("here")
        pass
    if count > 1:
        return False
    return True


def generate(max_iter):
    """
    generate a random sudoku
    :param max_iter: the maximum missing cell in a matrix
    :return:
    """
    full_sudoku = sudoku_generate_backtracking()
    full_sudoku = [full_sudoku[x:x + 9] for x in range(0, 81, 9)]
    enable_pairs = [(i, j) for i in range(9) for j in range(9)]

    sudoku = full_sudoku
    random_pair = random.choice(enable_pairs)

    i = 0
    j = 0

    while i < max_iter:

        sudoku_tmp = copy.deepcopy(sudoku)

        sudoku_tmp[random_pair[0]][random_pair[1]] = 0
        flag = unique_answer(sudoku_tmp)

        if flag:
            i += 1
            sudoku[random_pair[0]][random_pair[1]] = 0
            enable_pairs.remove(random_pair)
            random.shuffle(enable_pairs)
            j = 0
        else:
            j += 1
            if j >= len(enable_pairs):
                break
        random_pair = enable_pairs[j]

    for i in range(9):
        result = ''
        for j in range(9):
            if sudoku[i][j] == 0:
                result += '.'
            else:
                result += str(sudoku[i][j])
    sudoku = sum(sudoku, [])
    return sudoku
