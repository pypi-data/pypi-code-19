#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

from datetime import datetime
import unittest
import sqlite3

from myorm.dbobject import DbObject, TooManyResultsError
from myorm.fields import BooleanField, CharField, DateTimeField, ForeignKey, IntegerField, TextField
from myorm import TestAdaptor

DbObject.adaptor = TestAdaptor()


class Driver(DbObject):

    name = CharField(max_length=10)


class Car(DbObject):

    wheels = IntegerField(default=4)
    seats = IntegerField(default=5)
    manufacturer = CharField(max_length=120)
    description = TextField()
    motorcycle = BooleanField(default=False)
    built = DateTimeField()
    driver = ForeignKey(Driver)


class TestMethods(unittest.TestCase):

    def setUp(self):
        print('\nSetting up: %s' % self.shortDescription())
        Driver.create_table()
        harry = Driver.objects.create(name='Harry')
        Car.create_table()
        self.car1 = Car.objects.create(wheels=4, manufacturer='Mercedes', seats=5, driver=harry)
        self.car2 = Car.objects.create(wheels=4, manufacturer='BMW', seats=3)
        self.car2 = Car.objects.create(wheels=4, manufacturer='Porsche', seats=2, built=datetime.now())
        self.car2 = Car.objects.create(wheels=2, manufacturer='Harley Davidson', seats=2, motorcycle=True)

    def test_create_instance(self):
        """ Creates a car and should return an object with an id """

        suzuki = Car.objects.create(wheels=2, manufacturer='Suzuki')
        self.assertEqual(type(suzuki.id), int)
        self.assertEqual(suzuki.wheels, 2)
        self.assertTrue(isinstance(suzuki, Car))
        self.assertTrue(isinstance(suzuki, DbObject))

    def test_save_instance(self):

        """ Tests the save() method in instances"""
        suzuki = Car(wheels=4, seats=5)
        suzuki.save()
        self.assertEqual(suzuki.wheels, 4)
        self.assertEqual(suzuki.seats, 5)

        suzuki.wheels = 6
        suzuki.seats = 10
        suzuki.save()

        new_inst = Car.objects.get(id=suzuki.id)
        self.assertEqual(new_inst.wheels, 6)
        self.assertEqual(new_inst.seats, 10)
        self.assertEqual(new_inst.seats, 10)

        vw = Car(wheels=4, manufacturer='VW').save()
        self.assertEqual(type(vw.id), int)
        self.assertEqual(vw.manufacturer, 'VW')
        vw.manufacturer = 'Opel'
        opel = Car.objects.get(id=vw.id)
        self.assertEqual(opel.manufacturer, 'VW')
        vw.save()
        opel = Car.objects.get(id=vw.id)
        self.assertEqual(opel.manufacturer, 'Opel')

    def test_filter(self):
        """ Some filter tests """

        self.assertEqual(Car.objects.filter(id=10000), [])
        self.assertEqual(Car.objects.filter(manufacturer='Mercedes')[0].wheels, 4)

    def test_all(self):
        """ Tests the objecs.all() method """

        self.assertEqual(len(Car.objects.all()), len(Car.objects.filter()))

    def test_get(self):
        """ Tests the get method. """

        self.assertEqual(Car.objects.get(manufacturer='Mercedes').id, Car.objects.get(seats=5).id)
        with self.assertRaises(TooManyResultsError):
            Car.objects.get(wheels=4)

    def test_in_filters(self):
        """ Tests the __in filter """

        self.assertEqual(len(Car.objects.filter(manufacturer__in=['BMW', 'Porsche'])), 2)

    def test_lte_gte_filters(self):
        """ Tests the __lte, __lt, __gte and __gt filter """

        # Single filters:
        self.assertEqual(len(Car.objects.filter(seats__lte=3)), 3)
        self.assertEqual(len(Car.objects.filter(seats__lt=3)), 2)
        self.assertEqual(len(Car.objects.filter(seats__gte=3)), 2)
        self.assertEqual(len(Car.objects.filter(seats__gt=3)), 1)

        # Combined filters:
        self.assertEqual(len(Car.objects.filter(seats__lte=3, wheels=2)), 1)
        self.assertEqual(len(Car.objects.filter(seats__lt=3, wheels=2)), 1)
        self.assertEqual(len(Car.objects.filter(seats__gte=3, manufacturer='BMW')), 1)
        self.assertEqual(len(Car.objects.filter(seats__gt=2, manufacturer='Mercedes')), 1)

        # Combined limit filters
        self.assertEqual(len(Car.objects.filter(seats__lte=3, wheels__gt=3)), 2)

    def test_order_by_filters(self):
        """ Tests the order_by filter """

        self.assertEqual(Car.objects.filter(order_by='seats')[0].manufacturer, 'Porsche')
        self.assertEqual(Car.objects.filter(order_by='-seats')[0].manufacturer, 'Mercedes')
        self.assertEqual(Car.objects.filter(seats=2, order_by='-wheels')[0].manufacturer, 'Porsche')
        self.assertEqual(Car.objects.filter(seats=2, order_by='wheels')[0].manufacturer, 'Harley Davidson')

    def test_bulk_create(self):
        """ Tests the mass creation of objects """

        old_len = len(Car.objects.all())
        cars = [Car(wheels=i, seats=4, manufacturer='Lada', description='cheap') for i in range(0, 5203)]
        Car.objects.bulk_create(cars)
        self.assertEqual(old_len - len(Car.objects.all()) + len(Car.objects.all()), old_len)

    def test_delete(self):
        """ Tests the deletion of objects """

        old_len = len(Car.objects.all())
        self.car1.delete()
        self.assertEqual(len(Car.objects.all()), old_len - 1)

    def test_raw_queries(self):
        """ Tests some raw queries """
        old_len = len(Car.objects.all())

        mercedes = DbObject.raw("SELECT id FROM car WHERE manufacturer=?", "Mercedes")
        self.assertEqual(len(mercedes), len(Car.objects.filter(manufacturer="Mercedes")))
        self.assertEqual(mercedes[0][0], Car.objects.get(manufacturer="Mercedes").id)

        all = DbObject.raw("SELECT id FROM car")
        self.assertEqual(len(all), old_len)

        with self.assertRaises(IndexError):
            Car.objects.get(manufacturer="General Motors")
        DbObject.raw("INSERT INTO car (wheels, seats, manufacturer) VALUES (4, 8, 'General Motors')")
        self.assertEqual(Car.objects.get(manufacturer="General Motors").seats, 8)

        with self.assertRaises(IndexError):
            Car.objects.get(manufacturer="MAN")
        DbObject.raw("INSERT INTO car (wheels, seats, manufacturer) VALUES (?, ?, ?)", 8, 39, 'MAN')
        self.assertEqual(Car.objects.get(manufacturer="MAN").seats, 39)

    def test_field_defaults(self):
        """ Tests the defaults of the fields """
        toyota = Car.objects.create(manufacturer='Toyota')
        self.assertEqual(toyota.manufacturer, 'Toyota')
        self.assertEqual(toyota.wheels, 4)
        self.assertEqual(toyota.seats, 5)

        nissan = Car.objects.create(manufacturer='Nissan', wheels=8, seats=2)
        self.assertEqual(nissan.manufacturer, 'Nissan')
        self.assertEqual(nissan.wheels, 8)
        self.assertEqual(nissan.seats, 2)

    def tearDown(self):
        print('Tearing down')
        DbObject.adaptor._execute_query(("DROP TABLE car", None))
        DbObject.adaptor._execute_query(("DROP TABLE driver", None))

if __name__ == '__main__':
    unittest.main()
