#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/04/2018 4:45 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : order.py
# @Software: PyCharm

from collections import namedtuple
from abc import ABCMeta, abstractmethod

Customer = namedtuple('Customer', 'name fidelity')


class LineItem:
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price

    def total(self):
        return self.price * self.quantity


class Order:
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion

    def total(self):
        if not hasattr(self, '__total'):
            self.__total = sum(item.total() for item in self.cart)
        return self.__total

    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion.discount(self)
        return self.total() - discount

    def __repr__(self):
        fmt = '<Order total: {:.2f},due: {:.2f}>'
        return fmt.format(self.total(), self.due())


class Promotion:
    __metaclass__ = ABCMeta

    @abstractmethod
    def discount(self, order):
        """:returns valus of discount"""


class FirstPromo(Promotion):
    def discount(self, order):
        return order.total() * .05 if order.customer.fidelity >= 1000 else 0


class SecondPromo(Promotion):
    def discount(self, order):
        discount = 0
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * .1
        return discount


if __name__ == '__main__':
    joe = Customer('Jone Doe', 0)
    ann = Customer('Ann Smith', 1100)
    cart = [LineItem('banana', 4, .5), LineItem('apple', 30, 1.5)]
    print Order(joe, cart, FirstPromo())
    print Order(ann, cart, FirstPromo())
