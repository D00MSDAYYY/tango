import settings as stgs


obj = {"a": [1, 2, 3]}
proxy = stgs.mutable_proxy(obj, lambda : print("i invoked"))
proxy["a"].append(4)  # Не вызовет on_change!