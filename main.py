from copy import copy
from json import dump
from time import sleep
from typing import Set as set_type

from codegen import *
from optimizecode import *


def inputverifier(word: Text) -> set_type[Text] or Text:
    lBracket = 0
    rBracket = 0
    sigmaAlphabet: set_type = set()
    for i in word:
        if i != "(" and i != ")":
            sigmaAlphabet.add(i)
        elif i == "(":
            lBracket += 1
        elif i == ")":
            rBracket += 1

    if rBracket != lBracket:
        return "The total count of open brackets is not equal to the total count of closed brackets"
    else:
        return sigmaAlphabet


def dpda(q: Text, symbol: Text, stack: List, sigmaAlphabet: set_type[Text], level) -> Tuple:
    if q == "q0":
        if "[a-zA-Z]" in sigmaAlphabet:
            if findall("[a-zA-Z]", symbol) != []:
                if "empty" in stack and len(stack) == 1:
                    qCurrentLocal = "q1"
                    return qCurrentLocal, stack, level
    elif q == "q1":
        if "[a-zA-Z]" in sigmaAlphabet or "[0-9]" in sigmaAlphabet:
            if findall("[a-zA-Z]", symbol) != [] or findall("[0-9]", symbol) != []:
                if "empty" in stack and len(stack) == 1:
                    qCurrentLocal = "q1"
                    return qCurrentLocal, stack, level
            else:
                if symbol == "=":
                    qCurrentLocal = "q2"
                    return qCurrentLocal, stack, level + 1
    elif q == "q2":
        if "(" not in sigmaAlphabet and "(" == symbol:
            stack.insert(0, "(")
            qCurrentLocal = "q3"
            return qCurrentLocal, stack, level + 1
        elif "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            qCurrentLocal = "q4"
            return qCurrentLocal, stack, level
        elif "[a-zA-Z]" in sigmaAlphabet and findall("[a-zA-Z]", symbol) != []:
            qCurrentLocal = "q5"
            return qCurrentLocal, stack, level
    elif q == "q3":
        if "(" not in sigmaAlphabet and "(" == symbol:
            stack.insert(0, "(")
            qCurrentLocal = "q3"
            return qCurrentLocal, stack, level + 1
        elif "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            qCurrentLocal = "q4"
            return qCurrentLocal, stack, level
        elif "[a-zA-Z]" in sigmaAlphabet and findall("[a-zA-Z]", symbol) != []:
            qCurrentLocal = "q5"
            return qCurrentLocal, stack, level
        elif findall("(\*|\+)", symbol) != []:
            raise Exception("An arithmetic operation symbol can't appear after bracket and before a variable!")
    elif q == "q4":
        if "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            qCurrentLocal = "q4"
            return qCurrentLocal, stack, level
        elif "[0-9]" in sigmaAlphabet and findall("\)", symbol) != []:
            if len(stack) > 1 and "(" in stack:
                qCurrentLocal = "q6"
                stack.pop(0)
                return qCurrentLocal, stack, level - 1
        elif findall("(\*|\+)", symbol) != []:
            if "*" in sigmaAlphabet and "+" in sigmaAlphabet:
                qCurrentLocal = "q2"
                return qCurrentLocal, stack, level
        elif "." in sigmaAlphabet and findall("\.", symbol) != []:
            qCurrentLocal = "q7"
            return qCurrentLocal, stack, level
        elif findall("[a-zA-Z]", symbol) != []:
            raise Exception("Number can't be before a letter when declaring a variable!")
    elif q == "q5":
        if "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            qCurrentLocal = "q5"
            return qCurrentLocal, stack, level
        elif "[a-zA-Z]" in sigmaAlphabet and findall("[a-zA-Z]", symbol) != []:
            qCurrentLocal = "q5"
            return qCurrentLocal, stack, level
        elif "[0-9]" in sigmaAlphabet and findall("\)", symbol) != [] or "[a-zA-Z]" in sigmaAlphabet and findall("\)", symbol) != []:
            if len(stack) > 1 and "(" in stack:
                qCurrentLocal = "q6"
                stack.pop(0)
                return qCurrentLocal, stack, level - 1
        elif findall("(\*|\+)", symbol) != []:
            if "*" in sigmaAlphabet and "+" in sigmaAlphabet:
                qCurrentLocal = "q2"
                return qCurrentLocal, stack, level
    elif q == "q6":
        if ")" not in sigmaAlphabet and ")" == symbol:
            if len(stack) > 1:
                if stack[0] != e:
                    stack.pop(0)
                    qCurrentLocal = "q6"
                    return qCurrentLocal, stack, level - 1
            else:
                raise Exception("Stack contains no paired brackets")
        elif "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            raise Exception("This state only supports the closing bracket or arithmetic operation symbol")
        elif "[a-zA-Z]" in sigmaAlphabet and findall("[a-zA-Z]", symbol) != []:
            raise Exception("This state only supports the closing bracket or arithmetic operation symbol")
        elif findall("(\*|\+)", symbol) != []:
            qCurrentLocal = "q2"
            return qCurrentLocal, stack, level
    elif q == "q7":
        if "." in sigmaAlphabet and findall("\.", symbol) != []:
            raise Exception("The second dot is invalid!")
        elif "[0-9]" in sigmaAlphabet and findall("[0-9]", symbol) != []:
            qCurrentLocal = "q7"
            return qCurrentLocal, stack, level
        elif findall("\)", symbol) != []:
            if len(stack) > 1 and "(" in stack:
                qCurrentLocal = "q6"
                stack.pop(0)
                return qCurrentLocal, stack, level - 1
        elif findall("(\*|\+)", symbol) != []:
            if "*" in sigmaAlphabet and "+" in sigmaAlphabet:
                qCurrentLocal = "q2"
                return qCurrentLocal, stack, level
        elif findall("[a-zA-Z]", symbol) != []:
            raise Exception("Number can't be before a letter when declaring a variable!")


# Запись по знаку, закрывающей скобке, либо по концу строки и пустоте стека
def json_graph(level, x, graph, lexem, oper=None):
    total_level = level + x

    if graph.get(f"{total_level}") is None:
        graph_vertex = copy(graphPattern)
        graph_vertex["LEVEL"] = total_level
        graph_vertex["LEVEL_ORIG"] = level
        graph_vertex["X"] = x
        if graph_vertex["LEFT"] == "":
            if lexem != "":
                graph_vertex["LEFT"] = lexem
            else:
                if graph.get(f"{total_level + 1}") is not None:
                    graph_vertex["LEFT"] = copy(graph[f"{total_level + 1}"])
            if graph_vertex["OPER"] == "" and oper is not None:
                graph_vertex["OPER"] = oper

    elif graph.get(f"{total_level}") is not None:
        if oper is None and lexem == "":
            graph_vertex = copy(graph[f"{total_level}"])
            if str(graph_vertex["LEVEL"]) == f"{total_level}":
                if graph_vertex["LEFT"] != "":
                    if graph_vertex["OPER"] != "":
                        if graph_vertex["RIGHT"] != "":
                            pass
                        else:
                            graph_vertex["RIGHT"] = copy(graph[f"{total_level + 1}"])
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

                            graph_vertex["LEFT"] = graph[f"{total_level - 1}"]
                            graph_vertex["OPER"] = oper
        else:
            pass

    graph[f"{total_level}"] = copy(graph_vertex)
    return graph, x


if __name__ == '__main__':

    qStates: set_type = {"q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7"}
    qStart: Text = "q0"
    qEnd: set_type = {"q4", "q5", "q6", "q7"}

    sAlphabet: set_type[Text] = {"[a-zA-Z]", "[0-9]", "+", "*", "."}
    e: Text = "empty"
    stack: List = [e]

    qCurrent = qStart

    graph: Dict = {}
    graphPattern: Dict = {"LEVEL": -1, "LEVEL_ORIG": -1, "LEFT": "", "OPER": "", "RIGHT": "", "CODE": [], "X": 0}
    level = -1
    lexeme: Text = ""
    reset = False

    userString: Text = input('Enter a string in this format, but without quotes "var=a+b":  ')

    if inputverifier(userString) != "The total count of open brackets is not equal to the total count of closed brackets":
        # cnt - Simple counter
        # x - nesting ratio to control the number of brackets and correct construction graph in json file.
        # Nesting ratio to control the number of brackets and correct construction graph in json file.
        # This coefficient will be more than 0 if definite nesting level already exists in dictionary (json).
        # In order not overwrite existing nesting level i used this coefficient
        # Example, variable=(a+b)*(c+6).
        # Left and right parts have brackets that equal nesting level - 1.
        # If i save (a+b) in nesting level 1, then (c+6) i can't save as nesting level 1 already usage, then i can use this coefficient and get a new nesting level different from 1.
        cnt = 0
        x = 0
        for i in userString:
            if reset:
                lexeme: Text = ""
                reset = False

            if i == "=":
                qCurrent, stack, level = dpda(qCurrent, i, stack, sAlphabet, level)
                graph_vertex_ = copy(graphPattern)
                if graph_vertex_["LEVEL"] == -1:
                    if graph_vertex_["LEFT"] == "":
                        graph_vertex_["LEFT"] = lexeme
                        reset = True
                        if graph_vertex_["OPER"] == "":
                            graph_vertex_["OPER"] = "="
                    graph[f"-1"] = graph_vertex_
            elif i == "(":
                qCurrent, stack, level = dpda(qCurrent, i, stack, sAlphabet, level)
            elif i == ")":
                old_level = level
                qCurrent, stack, level = dpda(qCurrent, i, stack, sAlphabet, level)

                graph, kx = json_graph(old_level, x, graph, lexeme)
                x = kx
                if cnt + 1 == len(userString):
                    if x != 0:
                        graph[f"{level}"]["RIGHT"] = copy(graph[f"{old_level + x}"])
                    else:
                        graph[f"{level}"]["RIGHT"] = copy(graph[f"{old_level}"])
                reset = True
            elif i == "*" or i == "+":
                qCurrent, stack, level = dpda(qCurrent, i, stack, sAlphabet, level)

                graph, kx = json_graph(level, x, graph, lexeme, i)
                x = kx
                reset = True
            else:
                qCurrent, stack, level = dpda(qCurrent, i, stack, sAlphabet, level)

                if cnt + 1 == len(userString):
                    lexeme += i
                    graph, kx = json_graph(level, x, graph, lexeme)
                    x = kx
                    # reset = True

                else:
                    lexeme += i

            if cnt + 1 == len(userString):
                graph["-1"]["RIGHT"] = copy(graph["0"])
            cnt += 1

        # for debug
        # print(lexeme)
        # print(graph["-1"])
        # print(graph["4"])
        if qCurrent in qEnd:
            with open("output.json", "w") as wr:
                dump(graph["-1"], wr, indent=1)
        elif qCurrent not in qEnd:
            print(f"The deterministic extrusion automaton has a current state {qCurrent}, which isn't in the set of final states")

        if qCurrent in qEnd:
            outputString: Text = ""
            codeRaw: Dict = {}
            if userString == validator(graph["-1"], outputString):
                codeRaw = generatorofcode(graph["-1"], codeRaw)
                codeRaw[int("-1")] = [codeRaw[int("-1")][2], f"STORE {graph['-1']['LEFT']}"]

                table, _ = generatoroftablename(codeRaw[int("-1")])
                with open("output.txt", "w", encoding="utf8") as wt:
                    wt.write("Table of names\n" + table + "=" * 10 + "\n")
                    wt.write("Unoptimized code - " + str(codeRaw[int("-1")]) + "\n")
                    wt.write(f"Optimized code - {codeoptimize3(codeoptimize2(codeoptimize(codeRaw[int('-1')]))[0])[0]}" + "\n")

            else:
                pass
    else:
        print("The total count of open brackets is not equal to the total count of closed brackets")
        sleep(5)
