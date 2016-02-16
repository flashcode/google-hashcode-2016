#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Google Hash Code 2016 - Qualification
#
# © 2016 Team "The Rabbit Club"
#
# Version: 1.0
#

"""Google Hash Code 2016."""

from __future__ import print_function

import math
import sys


def get_distance(ra, ca, rb, cb):
    if ra == rb and ca == cb:
        return 0
    return math.ceil(math.sqrt((ra-rb)*(ra-rb) + (ca-cb)*(ca-cb)))


class Warehouse(object):

    def __init__(self, id, r, c, products):
        self.id = id
        self.r = r
        self.c = c
        self.products = products

    def __str__(self):
        return 'WH(id=%d, %d,%d,products=%s)' % (
            self.id, self.r, self.c,
            ','.join([str(product) for product in self.products]))


class Drone(object):

    def __init__(self, id, r, c, payload, num_products):
        self.id = id
        self.r = r
        self.c = c
        self.payload = payload
        self.items = [0] * num_products
        self.busy = 0
        self.target = (-1, -1)

    def load(self, warehouse, order, product_type, num_items, turns_left):
        distance = get_distance(self.r, self.c, warehouse.r, warehouse.c)
        if distance + 1 > turns_left - 1:
            return False
        # print('Drone %d: load %d items of type %d (target: %dx%d)' % (
        #     self.id, num_items, product_type, order.r, order.c))
        self.c, self.r = (warehouse.c, warehouse.r)
        self.items[product_type] += num_items
        self.busy = distance + 1
        warehouse.products[product_type] -= num_items
        self.target = (order.r, order.c)
        self.target_product_type = product_type
        self.target_num_items = num_items
        self.target_order_id = order.id
        order.items[product_type] -= num_items
        return True

    def deliver(self, turns_left):
        distance = get_distance(self.r, self.c, self.target[0], self.target[1])
        if distance + 1 > turns_left - 1:
            return False
        # print('Drone %d: deliver %d items of type %d to %dx%d' % (
        #     self.id, self.target_num_items, self.target_product_type,
        #     self.target[0], self.target[1]))
        self.c, self.r = (self.target[0], self.target[1])
        self.items[self.target_product_type] -= self.target_num_items
        self.busy = distance + 1
        self.target = (-1, -1)
        return True

    def cur_weight(self, products):
        weight = 0
        for i in range(0, len(self.items)):
            weight += self.items[i] * products[i]
        return weight

    def __str__(self):
        return 'Drone(id=%d, (%d,%d), payload=%d)' % (self.id, self.r, self.c,
                                                      self.payload)


class Order(object):

    def __init__(self, id, r, c, items):
        self.id = id
        self.r = r
        self.c = c
        self.items = items

    def __str__(self):
        return 'Order(id=%d,(%dx%d),items=%s)' % (
            self.id, self.r, self.c,
            ','.join([str(item) for item in self.items]))

    def get_first_product_type_to_deliver(self, grid):
        for i in range(0, len(self.items)):
            if self.items[i] > 0 and grid.product_type_available(i):
                return (i, self.items[i], self)
        return (-1, -1, None)


class Grid(object):

    def __init__(self, rows, cols, num_products, products, num_drones, turns,
                 payload, warehouses, orders):
        self.rows = rows
        self.cols = cols
        self.grid = []
        for i in range(1, rows):
            self.grid.append([0] * cols)
        self.num_products = num_products
        self.products = products
        self.num_drones = num_drones
        self.turns = turns
        self.payload = payload
        self.warehouses = warehouses
        self.orders = orders
        self.drones = []
        for i in range(0, self.num_drones):
            self.drones.append(
                Drone(i,
                      self.warehouses[0].r,
                      self.warehouses[0].c,
                      self.payload,
                      self.num_products))
        self.commands = []  # commands to put in output file

    def __str__(self):
        return ('%dx%d (%d drones, %d turns, %d payload):\n'
                '  products=%s,\n'
                '  warehouses=%s,\n'
                '  orders=%s,\n'
                '  drones=%s' % (
                    self.rows, self.cols, self.num_drones, self.turns,
                    self.payload,
                    str(self.products),
                    ', '.join([str(wh) for wh in self.warehouses]),
                    ', '.join([str(order) for order in self.orders]),
                    ', '.join([str(drone) for drone in self.drones])))

    def get_nearest_warehouse_with_product(self, r, c, product_type, num_items,
                                           order):
        min_dist = 999999999
        warehouse = None
        for i in range(0, len(self.warehouses)):
            if self.warehouses[i].products[product_type] > 0:
                distance1 = get_distance(r, c,
                                         self.warehouses[i].r,
                                         self.warehouses[i].c)
                distance2 = get_distance(self.warehouses[i].r,
                                         self.warehouses[i].c,
                                         order.r,
                                         order.c)
                distance = distance1 + distance2
                if distance < min_dist:
                    warehouse = self.warehouses[i]
                    min_dist = distance
        return warehouse

    def product_type_available(self, product_type):
        for warehouse in self.warehouses:
            if warehouse.products[product_type] > 0:
                return True
        return False


def read_file(filename):
    """Read the input file."""
    grid = None
    with open(filename, 'r') as fin:
        line = fin.readline()

        rows, cols, num_drones, turns, payload = [
            int(num) for num in line.split()]

        num_products = int(fin.readline())
        products = [int(num) for num in fin.readline().split()]

        num_warehouses = int(fin.readline())
        warehouses = []
        for i in range(0, num_warehouses):
            r, c = [int(num) for num in fin.readline().split()]
            wh_products = [int(num) for num in fin.readline().split()]
            warehouses.append(Warehouse(i, r, c, wh_products))

        num_orders = int(fin.readline())
        orders = []
        for i in range(0, num_orders):
            r, c = [int(num) for num in fin.readline().split()]
            num_items = int(fin.readline())
            counts = [int(num) for num in fin.readline().split()]
            items = [0] * num_products
            for j in range(0, num_items):
                items[counts[j]] += 1
            orders.append(Order(i, r, c, items))

        grid = Grid(rows, cols, num_products, products, num_drones, turns,
                    payload, warehouses, orders)

    return grid


def deliver(grid):
    grid.turn = 0
    while True:
        turns_left = grid.turns - grid.turn
        for drone in grid.drones:
            if drone.busy > 0:
                drone.busy -= 1
            else:
                if drone.target != (-1, -1):
                    # deliver
                    command = (drone.id,
                               'D',
                               drone.target_order_id,
                               drone.target_product_type,
                               drone.target_num_items)
                    if drone.deliver(turns_left):
                        grid.commands.append(command)
                else:
                    # load
                    _type = -1
                    for order in grid.orders:
                        _type, _count, order = (
                            order.get_first_product_type_to_deliver(grid))
                        if _type >= 0:
                            break
                    if _type >= 0:
                        weight_avail = (
                            drone.payload - drone.cur_weight(grid.products))
                        max_count = int(weight_avail / grid.products[_type])
                        _count = min(_count, max_count)
                        warehouse = grid.get_nearest_warehouse_with_product(
                            drone.r, drone.c, _type, _count, order)
                        if warehouse:
                            _count = min(_count, warehouse.products[_type])
                            command = (drone.id,
                                       'L',
                                       warehouse.id,
                                       _type,
                                       _count)
                            if drone.load(warehouse, order, _type, _count,
                                          turns_left):
                                grid.commands.append(command)
        grid.turn += 1
        if grid.turn >= grid.turns:
            break
        if grid.turn % 1000 == 0:
            print('turn: %d' % grid.turn)


def write_file(grid, filename):
    """Write output file."""
    with open(filename, 'w') as fout:
        fout.write('%d\n' % len(grid.commands))
        for command in grid.commands:
            fout.write(' '.join([str(item) for item in command]) + '\n')


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    print('Running on file: %s' % sys.argv[1])

    # read input file
    grid = read_file(sys.argv[1])
    # print(grid)

    try:
        deliver(grid)
    except KeyboardInterrupt:
        pass

    # write output file
    write_file(grid, sys.argv[2])


if __name__ == '__main__':
    main()
