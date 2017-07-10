# coding=utf-8


def mask(card_number):
    """ Masks the credit card number """
    card_number = card_number[:6] + \
        card_number[-4:].rjust(len(card_number) - 6, "*")

    return card_number


def clear(card_info):
    """Clears the credit card number"""
    card_number = card_info.get('card_number', None)
    if card_number:
        card_info['card_number'] = mask(
            card_number
        )
        del card_info['cvv']
