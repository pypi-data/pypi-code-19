__all__ = ["RegistMixin"]
import peewee


class RegistMixin:
    _regist_classes = {}

    @classmethod
    def regist(clz, target):
        clz._regist_classes[target.__name__] = target
        return target

    def create_tables(self, **kwargs):
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
