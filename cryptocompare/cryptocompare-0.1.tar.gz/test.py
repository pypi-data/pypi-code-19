#!/usr/bin/env python

import cryptocompare

coins = ['BTC', 'ETH', 'ETC', 'XMR', 'DOGE', 'GNT', 'ZEC']

print('===================== TEST =======================')
print(cryptocompare.get_coin_info('BTC'))
print(cryptocompare.get_coin_info('BTC', curr='USD'))
print(cryptocompare.get_coin_info('BTC', curr='GBP',
        fields=[cryptocompare.PRICE, cryptocompare.MARKETCAP]))

print('===================== INFO =======================')
for coin in coins:
    print(cryptocompare.get_coin_info(coin, curr='EUR',
        fields=[cryptocompare.PRICE, cryptocompare.MARKETCAP]))

print('===================== PRICE ======================')
for coin in coins:
    print(cryptocompare.get_price(coin))
    print(cryptocompare.get_price(coin, curr='USD'))

print('====================== HIGH ======================')
for coin in coins:
    print(cryptocompare.get_high(coin))

print('====================== LOw =======================')
for coin in coins:
    print(cryptocompare.get_low(coin))

print('==================== CHANGE ======================')
for coin in coins:
    print(cryptocompare.get_change(coin, 'EUR'))

print('=================== CHANGE % =====================')
for coin in coins:
    print(cryptocompare.get_change(coin))
