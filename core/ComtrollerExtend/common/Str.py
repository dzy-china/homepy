from typing import final


class Str:
    def __init__(self):
        # 调用父类构造函数
        super().__init__()

    @final
    def join(self, vals, separator=',') -> str:
        """
        拼接 列表、元组，字典为字符串，默认拼接符为逗号','
        """
        ele_list = []
        for val in vals:
            ele_list.append(str(val)) if not isinstance(val, str) else ele_list.append(val)
        return separator.join(ele_list)
