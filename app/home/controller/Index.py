from core.route.DecoratorRoute import route
from app.common.controller.Base import Base


class Index(Base):
    @route('/')
    def index(self) -> str:
        result = 'index'
        # obj_mongodb = self.db(dbtype='mongodb', active_index=0)
        # result = obj_mongodb.database('meijieyi_ziyuan').table('xing_meiti_show').query()
        # print(self.env)
        return result

    @route('/demo')
    def demo(self):
        return 'demo'

    @route('/my-{name}')
    def my(self, my_name) -> list:
        return [my_name, {'name': '大神'}]
