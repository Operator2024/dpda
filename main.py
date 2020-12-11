from typing import Text, Set as set_type, List, Tuple, Dict
from re import *
from copy import copy
from json import dump

def pda_alphavite(word: Text) -> set_type[Text]:
    open_brackert = 0
    close_bracket = 0
    alphavite: set_type[Text] = {""}
    for i in word:
        if i != "(" and i != ")":
            alphavite.add(i)
        elif i == "(":
            open_brackert += 1
        elif i == ")":
            close_bracket += 1

    if close_bracket != open_brackert:
        return {"The total count of open brackets is not equal to the total count of closed brackets"}
    else:
        return alphavite


def pda_graph(q: Text, symbol: Text, q_set: set_type, stack: List, alphavite: set_type[Text], level) -> Tuple:
    if q == "q0":
        if "[a-zA-Z]" in alphavite:
            if findall("[a-zA-Z]", symbol) != []:
                if "empty" in stack and len(stack) == 1:
                    q_current = "q1"
                    return q_current, stack, level
    elif q == "q1":
        if "[a-zA-Z]" in alphavite or "[0-9]" in alphavite :
            if findall("[a-zA-Z]", symbol) != [] or findall("[0-9]", symbol) != []:
                if "empty" in stack and len(stack) == 1:
                    q_current = "q1"
                    return q_current, stack, level
            else:
                if symbol == "=":
                    q_current ="q2"
                    return q_current, stack, level + 1
    elif q == "q2":
        if "(" not in alphavite and "(" == symbol:
            stack.insert(0, "(")
            q_current = "q3"
            return q_current, stack, level + 1
        elif "[0-9]" in alphavite and findall("[0-9]", symbol) != []:
            q_current = "q4"
            return q_current, stack, level
        elif "[a-zA-Z]" in alphavite and findall("[a-zA-Z]", symbol) != []:
            q_current = "q5"
            return q_current, stack, level
    elif q == "q3":
        if "(" not in alphavite and "(" == symbol:
            stack.insert(0, "(")
            q_current = "q3"
            return q_current, stack, level + 1
        elif "[0-9]" in alphavite and findall("[0-9]", symbol) != []:
            q_current = "q4"
            return q_current, stack, level
        elif "[a-zA-Z]" in alphavite and findall("[a-zA-Z]", symbol) != []:
            q_current = "q5"
            return q_current, stack, level
        elif findall("(\*|\+)", symbol) != []:
            raise Exception("An arithmetic operation symbol can't appear after bracket and before a variable!")
    elif q == "q4":
        if "[0-9]" in alphavite and findall("[0-9]", symbol) != []:
            q_current = "q4"
            return q_current, stack, level
        elif "[0-9]" in alphavite and findall("\)", symbol) != []:
            if len(stack) > 1 and "(" in stack:
                q_current = "q6"
                stack.pop(0)
                return q_current, stack, level - 1
        elif findall("(\*|\+)", symbol) != []:
            if "*" in alphavite and "+" in alphavite:
                q_current = "q2"
                return q_current, stack, level
        elif findall("[a-zA-Z]", symbol) != []:
            raise Exception("Number can't be before a letter when declaring a variable!")
    elif q == "q5":
        if "[0-9]" in alphavite and findall("[0-9]", symbol) != []:
            q_current = "q5"
            return q_current, stack, level
        elif "[a-zA-Z]" in alphavite and findall("[a-zA-Z]", symbol) != []:
            q_current = "q5"
            return q_current, stack, level
        elif "[0-9]" in alphavite and findall("\)", symbol) != [] or "[a-zA-Z]" in alphavite and findall("\)", symbol) != []:
            if len(stack) > 1 and "(" in stack:
                q_current = "q6"
                stack.pop(0)
                return q_current, stack, level - 1
        elif findall("(\*|\+)", symbol) != []:
            if "*" in alphavite and "+" in alphavite:
                q_current = "q2"
                return q_current, stack, level
    elif q == "q6":
        if ")" not in alphavite and ")" == symbol:
            if len(stack) > 1:
                if stack[0] != empty_stack:
                    stack.pop(0)
                    q_current = "q6"
                    return q_current, stack, level - 1
            else:
                raise Exception("Stack contains no paired brackets")
        elif "[0-9]" in alphavite and findall("[0-9]", symbol) != []:
            raise Exception("This state only supports the closing bracket or arithmetic operation symbol")
        elif "[a-zA-Z]" in alphavite and findall("[a-zA-Z]", symbol) != []:
            raise Exception("This state only supports the closing bracket or arithmetic operation symbol")
        elif findall("(\*|\+)", symbol) != []:
            q_current = "q2"
            return q_current, stack, level

# Запись по знаку, закрывающей скобке, либо по концу строки и пустоте стека
def json_graph(level, x, graph, lexem, oper = None):
    a = "variable=((AB+2)*3)*(1+6)"
    # 1,0,..,+

    total_level = level + x
    print(total_level, "TESTDEBUG", graph.keys())

    if graph.get(f"{total_level}") is None:
        graph_vertex = copy(graph_ll)
        graph_vertex["LEVEL"] = total_level
        graph_vertex["LEVEL_ORIG"] = level
        graph_vertex["X"] = x
        if graph_vertex["LEFT"] == "":
            if lexem != "":
                graph_vertex["LEFT"] = lexem
            else:
                if graph.get(f"{total_level+1}") is not None:
                    graph_vertex["LEFT"] = copy(graph[f"{total_level+1}"])
            if graph_vertex["OPER"] == "" and oper is not None:
                graph_vertex["OPER"] = oper

    elif graph.get(f"{total_level}") is not None:
        if oper is None and lexem == "":
            # total_level = old_level
            graph_vertex = copy(graph[f"{total_level}"])
            if str(graph_vertex["LEVEL"]) == f"{total_level}":
                if graph_vertex["LEFT"] != "":
                    if graph_vertex["OPER"] != "":
                        if graph_vertex["RIGHT"] != "":
                            pass
                        else:
                            graph_vertex["RIGHT"] = copy(graph[f"{total_level+1}"])
        elif oper is None and lexem != "":
            graph_vertex = copy(graph[f"{total_level}"])
            if str(graph_vertex["LEVEL"]) == f"{total_level}":
                if graph_vertex["LEFT"] != "":
                    if graph_vertex["OPER"] != "":
                        graph_vertex["RIGHT"] = lexem
        elif oper is not None and lexem != "":
            graph_vertex = copy(graph[f"{total_level}"])

            if str(graph_vertex["LEVEL"]) == f"{total_level}":
                if graph_vertex["LEFT"] != "":
                    if graph_vertex["OPER"] != "":
                        if graph_vertex["RIGHT"] != "":
                            level_keys = [k for k in graph.keys()]

                            x = (int(max(level_keys)) + 1) - level
                            total_level = level + x

                            graph_vertex["LEVEL"] = total_level
                            graph_vertex["LEVEL_ORIG"] = level
                            graph_vertex["X"] = x

                            graph_vertex["LEFT"] = ""
                            graph_vertex["OPER"] = ""
                            graph_vertex["RIGHT"] = ""

                            graph_vertex["LEFT"] = lexem
                            graph_vertex["OPER"] = oper
        elif oper is not None and lexem == "":
            graph_vertex = copy(graph[f"{total_level}"])

            if str(graph_vertex["LEVEL"]) == f"{total_level}":
                if graph_vertex["LEFT"] != "":
                    if graph_vertex["OPER"] != "":
                        if graph_vertex["RIGHT"] != "":
                            level_keys = [k for k in graph.keys()]

                            x = (int(max(level_keys)) + 1) - level
                            total_level = level + x

                            graph_vertex["LEVEL"] = total_level
                            graph_vertex["LEVEL_ORIG"] = level
                            graph_vertex["X"] = x

                            graph_vertex["LEFT"] = ""
                            graph_vertex["OPER"] = ""
                            graph_vertex["RIGHT"] = ""

                            graph_vertex["LEFT"] = graph[f"{total_level-1}"]
                            graph_vertex["OPER"] = oper
        else:
            pass

    graph[f"{total_level}"] = copy(graph_vertex)
    return graph, x

if __name__ == '__main__':

    q_states: set_type = {"q0", "q1", "q2", "q3", "q4", "q5", "q6"}
    q_start: Text = "q0"
    q_end: set_type = {"q4", "q5", "q6"}

    sigma_alphavite: set_type[Text] = {"[a-zA-Z]", "[0-9]", "+", "*", "."}
    empty_stack: Text = "empty"
    stack: List = [empty_stack]

    q_current = q_start

    graph: Dict = {}
    graph_ll: Dict = {"LEVEL": -1, "LEVEL_ORIG": -1, "LEFT": "", "OPER": "", "RIGHT": "", "CODE": [], "X": 0}
    asm_free_idx = 0
    level = -1
    lexema: Text = ""
    reset = False

    # a = "variable=((AB+2)*3)*(1+6)"
    a = "variable=(2+((2+7)*PRICE2))*((TAX33X+2)*(6+TT))"
    cnt = 0
    x = 0
    for i in a:

        if reset:
            lexema = ""
            reset = False

        if i == "=":
            q_current, stack, level = pda_graph(q_current, i, q_states, stack, sigma_alphavite, level)
            print(q_current, stack, level, i)
            graph_vertex_ = copy(graph_ll)
            if graph_vertex_["LEVEL"] == -1:
                if graph_vertex_["LEFT"] == "":
                    graph_vertex_["LEFT"] = lexema
                    reset = True
                    if graph_vertex_["OPER"] == "":
                        graph_vertex_["OPER"] = "="
                graph[f"-1"] = graph_vertex_

        elif i == "(":
            q_current, stack, level = pda_graph(q_current, i, q_states, stack, sigma_alphavite, level)
            print(i, level)

        elif i == ")":
            old_level = level
            q_current, stack, level = pda_graph(q_current, i, q_states, stack, sigma_alphavite, level)
            print(i, level, lexema)

            graph, kx = json_graph(old_level, x, graph, lexema)
            x = kx
            if cnt + 1 == len(a):
                if x != 0:
                    graph[f"{level}"]["RIGHT"] = copy(graph[f"{old_level+x}"])
                else:
                    graph[f"{level}"]["RIGHT"] = copy(graph[f"{old_level}"])
            reset = True

        elif i == "*" or i == "+":
            q_current, stack, level = pda_graph(q_current, i, q_states, stack, sigma_alphavite, level)
            print(q_current, stack, level, i)

            print(x, "X")
            graph, kx = json_graph(level, x, graph, lexema, i)
            x = kx
            reset = True


        else:
            q_current, stack, level = pda_graph(q_current, i, q_states, stack, sigma_alphavite, level)
            print(q_current, stack, level, i)

            if cnt +1 == len(a):
                lexema += i
                graph, kx = json_graph(level, x, graph, lexema)
                x = kx
                # reset = True

            else:
                lexema += i

        if cnt +1 == len(a):
            graph["-1"]["RIGHT"] = copy(graph["0"])
        cnt += 1

    print(lexema)
    print(graph["-1"])
    print(graph["4"])

    with open("output.json", "w") as wr:
        dump(graph["-1"], wr, indent=1)

