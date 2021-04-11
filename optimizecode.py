from copy import deepcopy
from re import sub


def codeoptimize(unoptimizecode):
    t = []
    posl = []
    for i in range(0, len(unoptimizecode)):
        if type(unoptimizecode[i]) == list:
            unoptimizecode[i] = codeoptimize(unoptimizecode[i])
            if i + 1 < len(unoptimizecode):
                if type(unoptimizecode[i + 1]) != list:
                    if i + 2 >= len(unoptimizecode):
                        return unoptimizecode
                    else:
                        if len(posl) == 0 and "LOAD" in unoptimizecode[i]:
                            if i + 1 < len(unoptimizecode[i]):
                                if "ADD" in unoptimizecode[i + 1]:
                                    posl.append(unoptimizecode[i])
                                elif "MPY" in unoptimizecode[i + 1]:
                                    posl.append(unoptimizecode[i])
                                else:
                                    t.append(unoptimizecode[i])
                        elif len(posl) != 0:
                            if "LOAD" in posl[0] and ("ADD" in unoptimizecode[i] or "MPY" in unoptimizecode[i]):
                                posl.append(unoptimizecode[i])
                        else:
                            t.append(unoptimizecode[i])

        else:
            if len(posl) == 0 and "LOAD" in unoptimizecode[i]:
                if i + 1 < len(unoptimizecode[i]):
                    if "ADD" in unoptimizecode[i + 1]:
                        posl.append(unoptimizecode[i])
                    elif "MPY" in unoptimizecode[i + 1]:
                        posl.append(unoptimizecode[i])
                    else:
                        t.append(unoptimizecode[i])
            elif len(posl) != 0:
                if "LOAD" in posl[0] and ("ADD" in unoptimizecode[i] or "MPY" in unoptimizecode[i]):
                    posl.append(unoptimizecode[i])
            else:
                t.append(unoptimizecode[i])

    if len(posl) != 0:
        if len(posl) == 2:
            l1 = posl[0].split(" ")
            l2 = posl[1].split(" ")
            t.append(l1[0] + " " + l2[1])
            t.append(l2[0] + " " + l1[1])

    if len(t) == 1:
        return t[0]
    else:
        return t


def codeoptimize2(unoptimizecode):
    posl = []
    for j in range(0, len(unoptimizecode)):
        if type(unoptimizecode[j]) == list:
            cp = deepcopy(unoptimizecode)
            response = codeoptimize2(cp[j])

            if response is not None:
                optimizecode, sym = response
                flag = 0

                for k in range(j, len(unoptimizecode)):

                    if type(unoptimizecode[k]) != list:
                        if sym in unoptimizecode[k]:
                            flag += 1
                if flag == 0:
                    unoptimizecode[j] = optimizecode

        else:
            if len(posl) == 0 and "STORE" in unoptimizecode[j]:
                posl.append(unoptimizecode[j])
            elif len(posl) != 0 and "LOAD" in unoptimizecode[j]:
                t1 = posl[0].split(" ")
                t2 = 0
                for k in range(j, len(unoptimizecode)):
                    if t1[1] not in unoptimizecode[k]:
                        t2 += 1
                if t2 > 0:
                    if t1[1] in unoptimizecode[j]:
                        posl.append(unoptimizecode[j])

    if len(posl) == 2:
        for d in posl:
            unoptimizecode.remove(d)
        return unoptimizecode, posl[0].split(" ")[1]
    return unoptimizecode, "rtn"


def codeoptimize3(unoptimizecode):
    posl = []
    for j in range(0, len(unoptimizecode)):
        if type(unoptimizecode[j]) == list:
            cp = deepcopy(unoptimizecode)
            response = codeoptimize3(cp[j])

            if response is not None:
                optimizecode, sym, sym2 = response
                flag = 0
                for k in range(j, len(unoptimizecode)):
                    if type(unoptimizecode[k]) != list:
                        if sym2 in unoptimizecode[k] and "STORE" not in unoptimizecode[k]:
                            unoptimizecode[k] = sub("\\" + sym2, sym, unoptimizecode[k])
                if flag == 0:
                    unoptimizecode[j] = optimizecode

        else:
            if len(posl) == 0 and "LOAD" in unoptimizecode[j]:
                posl.append(unoptimizecode[j])
            elif len(posl) != 0 and "STORE" in unoptimizecode[j]:
                t1 = posl[0].split(" ")
                t2 = 0
                for k in range(j, len(unoptimizecode)):
                    if t1[1] not in unoptimizecode[k]:
                        t2 += 1
                if t2 > 0:
                    if t1[1] not in unoptimizecode[j] and j + 1 < len(unoptimizecode):
                        if "LOAD" in unoptimizecode[j + 1]:
                            unoptimizecode[j + 1] += "rrr"
                            posl.append(unoptimizecode[j])

    if len(posl) == 2:
        r1 = posl[0].split(" ")[1]
        for rep in range(0, len(unoptimizecode)):
            if "rrr" in unoptimizecode[rep]:
                tmp = unoptimizecode[rep].split(" ")
                unoptimizecode[rep] = tmp[0] + " " + r1
        for d in posl:
            unoptimizecode.remove(d)
        return unoptimizecode, posl[0].split(" ")[1], posl[1].split(" ")[1]
    return unoptimizecode, "rtn2", "rt2"
