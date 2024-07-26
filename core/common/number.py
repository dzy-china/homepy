
# 判断是否为数字字符串
def is_num_str(val: any) -> bool:
    try:
        n = eval(val)
        if isinstance(n, (int, float)):
            return True
        else:
            return False
    except:
        return False