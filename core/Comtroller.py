
from core.ComtrollerExtend.Request import Request
from core.ComtrollerExtend.Session import Session
from core.ComtrollerExtend.Model import Model
from core.ComtrollerExtend.common.Time import Time
from core.ComtrollerExtend.common.Password import Password
from core.ComtrollerExtend.common.Str import Str


class Controller(Request, Session, Model, Time, Password, Str):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()


