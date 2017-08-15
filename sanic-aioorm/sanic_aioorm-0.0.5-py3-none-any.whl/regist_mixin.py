__all__ = ["RegistMixin"]
import peewee


class RegistMixin:
    """将module注册到类内部,以便统一初始化
    """
    _regist_classes = {}

    @classmethod
    def regist(clz, target):
        """注册module的装饰器,也可以当作方法注册多对多关系表,如
        NoteUserThrough = User.roles.get_through_model()
        AioOrm.regist(NoteUserThrough)
        """
        clz._regist_classes[target.__name__] = target
        return target

    def create_tables(self, **kwargs):
        """创建表,将注册的model创建到数据库,后面可以添加关键字参数,用于创建对应表中的初始数据条目
        """
        app = self.app
        @app.listener('after_server_start')
        async def creat_db(app, loop):
            for name, target in type(self)._regist_classes.items():
                print('create tabel', name)
                try:
                    await target.create_table()
                except peewee.InternalError as ie:
                    print(str(ie))
                except AttributeError as ae:
                    raise ae
                except Exception as e:
                    raise e
                else:
                    print('create tabel', name, 'done!')
                if kwargs:
                    if kwargs.get(name) and (await target.select().count()) == 0:
                        print(name, 'insert original data')
                        iq = target.insert_many(kwargs.get(name))
                        try:
                            result = await iq.execute()
                        except Exception as e:
                            print(name, 'insert original data error')
                            print(str(e))
                        else:
                            if result:
                                print(name, 'insert original data succeed')
                            else:
                                print(name, 'insert original data failed')
