# coding=utf-8
"""
synopsis:基于redis的生产者-消费者模型
author: haoranzeus@gmail.com
"""
import redis
import json
import time
import threading
import random


class WoodenMenu:
    """
    菜单，生产者与消费者共享，
    生产者必须按照菜单做菜，消费者按照菜单消费
    paras:
        table - 消费者所处的模块，字符串形式
        dish - 该消费者要消费的一种产品，字符串形式
        foods - 该产品的实际数据，dict形式
    foods 参数建议：
        foods 用于表示实际要执行的任务，建议采用如下形式：
        foods = {
            "action": "要执行的任务字符串",
            "paras": {参数列表}
        }
    """
    def __init__(self, table, dish, foods):
        assert isinstance(foods, dict), "foods must be a dict"
        self.set_menu(table, dish, foods)

    def set_menu(self, table, dish, foods):
        self.table = table
        self.dish = dish
        self.foods = foods

    def get_menu(self):
        table_dish = self.table + ":" + self.dish
        foods = self.foods
        return table_dish, foods


class WoodenWaiter:
    """
    服务生，负责从cooker那里取走菜，以及将菜交给消费者
    """
    def __init__(self, host='localhost', port='6379', db=0):
        self.redis_clt = redis.StrictRedis(host=host, port=port, db=db)

    def take_dish(self, table_dish, foods):
        """
        生产者侧使用，将菜交给waiter
        paras:
            table_dish - "<model>:<task>"形式的字符串
            foods - dict 形式的执行命令
        """
        assert isinstance(foods, dict), "foods must be a dict"
        foods = json.dumps(foods)
        self.redis_clt.lpush(table_dish, foods)

    def serve_dish(self, table_dish):
        """
        消费者侧使用，从waiter处获得菜品
        """
        foods_bytes = self.redis_clt.rpop(table_dish)
        if foods_bytes is None:
            return None
        else:
            foods_str = foods_bytes.decode()
            foods = json.loads(foods_str)
            return foods


class WoodenCooker:
    """
    生产者，按照菜单进行生产
    """
    def __init__(self, menu, waiter):
        self.set_menu(menu)
        self.set_waiter(waiter)

    def set_menu(self, menu):
        assert isinstance(menu, WoodenMenu), "menu must be a WoodenMenu"
        self.menu = menu

    def set_waiter(self, waiter):
        assert isinstance(waiter, WoodenWaiter), \
                "waiter must be a WoodenWaiter"
        self.waiter = waiter

    def cookone(self, menu=None):
        """
        如果没给出菜单，就按照初始化的菜单做一个
        """
        if menu is None:
            menu = self.menu
        assert isinstance(menu, WoodenMenu), "menu must be a WoodenMenu"

        table_dish, foods = menu.get_menu()
        self.waiter.take_dish(table_dish, foods)


class WoodenCustomer(threading.Thread):
    """
    消费者
    paras:
        table_dish - "<model>:<task>"形式的字符串
        waiter - WoodenWaiter实例
        process - 针对取出的foods要做的处理
        seconds - 循环读取redis的周期时间
    process参数说明：
        该参数是一个方法，接收一个dict参数，也就是要取出的foods
    """
    def __init__(self, table, dish, waiter, process, seconds):
        super(WoodenCustomer, self).__init__()
        self.table_dish = table + ":" + dish
        self.waiter = waiter
        self.process = process
        self.seconds = seconds

    def call_waiter(self):
        foods = self.waiter.serve_dish(self.table_dish)
        if foods is not None:
            return self.process(foods)
        else:
            return None

    def call_waiter_cyclic(self, seconds):
        """
        周期性检测任务队列
        """
        while True:
            self.call_waiter()
            time.sleep(seconds)

    def run(self):
        self.call_waiter_cyclic(self.seconds)


class WoodenManager:
    """
    大堂经理，整体管理消费者
    """
    def __init__(self):
        self.customers = []

    def add_customer(self, customer):
        assert isinstance(customer, WoodenCustomer), \
                "customer must be a WoodenCustomer"

        self.customers.append(customer)

    def launch(self):
        for customer in self.customers:
            customer.start()


if __name__ == '__main__':
    table1 = 'cmdb'
    table2 = 'rbac'
    dish1 = 'custom_sync'
    dish2 = 'some_task'
    foods1 = {
        "action": "sync_custom_data",
        "paras": ""
    }
    foods2 = {
        "action": "some_action",
        "paras": {
            "para1": "value1",
            "para2": "value2"
        }
    }
    menu1 = WoodenMenu(table=table1, dish=dish1, foods=foods1)
    menu2 = WoodenMenu(table=table2, dish=dish2, foods=foods2)
    waiter = WoodenWaiter()
    cooker1 = WoodenCooker(menu=menu1, waiter=waiter)
    cooker2 = WoodenCooker(menu=menu2, waiter=waiter)

    def print_foods(foods):
        print('custom foods')
        print('foods is: {}'.format(foods))

    customer1 = WoodenCustomer(
            table=table1, dish=dish1, waiter=waiter,
            process=print_foods, seconds=1)
    customer2 = WoodenCustomer(
            table=table2, dish=dish2, waiter=waiter,
            process=print_foods, seconds=3)

    def cook_sometime():
        while True:
            seconds = random.randint(3, 10)
            time.sleep(seconds)
            print('cookone after {} seconds'.format(seconds))
            cooker1.cookone()
            cooker2.cookone()

    cooker_thread = threading.Thread(target=cook_sometime)
    cooker_thread.start()
    manager = WoodenManager()
    manager.add_customer(customer1)
    manager.add_customer(customer2)
    manager.launch()

    while True:
        time.sleep(1)
