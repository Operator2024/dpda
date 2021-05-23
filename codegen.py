from re import findall
from typing import Text, Dict, List, Any, Tuple


def validator(g: Dict, verifyingstring: Text) -> Text:
    cnt = 0
    for i in g:
        if isinstance(g.get(i), dict) is False:
            if i == "LEFT":
                verifyingstring += g["LEFT"]
            elif i == "OPER":
                verifyingstring += g["OPER"]
            elif i == "RIGHT":
                verifyingstring += g["RIGHT"]
        elif isinstance(g.get(i), dict):
            if g["LEVEL_ORIG"] != -1:
                verifyingstring += "("
            verifyingstring = validator(g[i], verifyingstring)
            if g["LEVEL_ORIG"] != -1:
                verifyingstring += ")"
        cnt += 1
    return verifyingstring


def generatorofcode(graph: Dict, codebygraph: Dict):
    for i in graph:
        if isinstance(graph.get(i), dict) is False:
            if i == "LEFT":
                codebygraph[graph["LEVEL"]] = [f"LOAD {graph['LEFT']}", f"STORE ${graph['LEVEL']}"]
            elif i == "OPER":
                pass
            elif i == "RIGHT":
                if codebygraph.get(graph["LEVEL"]) is not None:

                    if len(codebygraph[graph["LEVEL"]]) == 1:
                        codebygraph[graph["LEVEL"]].append(f"LOAD {graph['RIGHT']}")
                        codebygraph[graph["LEVEL"]].append(f"STORE ${graph['LEVEL']}")
                        if graph["OPER"] == "*":
                            codebygraph[graph["LEVEL"]].append(f"MPY ${graph['LEVEL'] + 1 -1}")
                        elif graph["OPER"] == "+":
                            codebygraph[graph["LEVEL"]].append(f"ADD ${graph['LEVEL'] + 1 -1}")
                    elif len(codebygraph[graph["LEVEL"]]) > 1:
                        codebygraph[graph["LEVEL"]].append(f"LOAD {graph['RIGHT']}")
                        if graph["OPER"] == "*":
                            codebygraph[graph["LEVEL"]].append(f"MPY ${graph['LEVEL']}")
                        elif graph["OPER"] == "+":
                            codebygraph[graph["LEVEL"]].append(f"ADD ${graph['LEVEL']}")

                elif codebygraph.get(graph["LEVEL"]) is None:
                    codebygraph[graph["LEVEL"]] = [f"LOAD {graph['LEFT']}", f"STORE ${graph['LEVEL']}"]

        elif isinstance(graph.get(i), dict):
            # a = 2 * ((TAX33X + 2) * (6 + TT))
            # ["ADD $2", "ADD $3", "MPY $2"]
            # level + 1
            # ["LOAD 2", "STORE $0", "MPY $2", "MPY $0", "STORE a"]
            # a = "variable=(2+((2+7)*PRICE2))*((TAX33X+2)*(6+TT))"
            codebygraph = generatorofcode(graph[i], codebygraph)

            if codebygraph.get(graph["LEVEL"]) is None:

                if int(graph[i]["LEVEL"]) - 1 == int(graph["LEVEL"]):
                    codebygraph[graph["LEVEL"]] = [codebygraph[graph[i]['LEVEL']]]
                elif int(graph[i]["LEVEL"]) == int(graph["LEVEL"]) - 1:
                    codebygraph[graph["LEVEL"]] = [codebygraph[graph[i]['LEVEL']]]
            elif codebygraph.get(graph["LEVEL"]) is not None:
                if len(codebygraph[graph["LEVEL"]]) == 1:
                    codebygraph[graph["LEVEL"]].append(codebygraph[graph[i]['LEVEL']])
                    if graph["OPER"] == "*":
                        codebygraph[graph["LEVEL"]].append(f"MPY {codebygraph[graph['LEVEL']][0][len(codebygraph[graph['LEVEL']][0]) - 1][4::]}")
                    elif graph["OPER"] == "+":
                        codebygraph[graph["LEVEL"]].append(f"ADD {codebygraph[graph['LEVEL']][0][len(codebygraph[graph['LEVEL']][0]) - 1][4::]}")
                elif len(codebygraph[graph["LEVEL"]]) > 1:
                    codebygraph[graph["LEVEL"]].append(codebygraph[graph[i]['LEVEL']])
                    if graph["OPER"] == "*":
                        codebygraph[graph["LEVEL"]].append(f"MPY ${graph['LEVEL']}")
                    elif graph["OPER"] == "+":
                        codebygraph[graph["LEVEL"]].append(f"ADD ${graph['LEVEL']}")
    return codebygraph


def generatoroftablename(code: List, names: Text = None, number: Any = 0) -> Tuple[Text, Any]:
    if names is None:
        names = ""

    for i in code:
        if isinstance(i, list):
            names, number = generatoroftablename(i, names, number)
        elif isinstance(i, list) is False:
            if findall("(LOAD\s(\d{1,}\.\d{1,}|\d{1,}|\w{1,})|STORE\s\w{1,})", i):
                if "LOAD" in i:
                    if findall("\d{1,}\.\d{1,}", i[5::]) and float(i[5::]):
                        if not findall(f"{i[5::]}\sVariable", names):
                            number += 1
                            names += f"{number} {i[5::]} Const, float type\n"
                    elif findall("\w{1,}", i[5::]) and not i[5::].isdigit():
                        if not findall(f"{i[5::]}\sVariable", names):
                            number += 1
                            names += f"{number} {i[5::]} Variable, string type\n"
                    elif findall("\d{1,}", i[5::]) and i[5::].isdigit():
                        if not findall(f"{i[5::]}\sVariable", names):
                            number += 1
                            names += f"{number} {i[5::]} Const, integer type\n"
                elif "STORE" in i:
                    if findall("\w{1,}", i[6::]):
                        if not findall(f"{i[6::]}\sVariable", names):
                            number += 1
                            names += f"{number} {i[6::]} Variable name\n"
    return names, number
