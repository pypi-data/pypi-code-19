from __future__ import absolute_import, division, print_function, unicode_literals

from fincalendar.equity_config import SETTLEMENT_CYCLE, EXCHANGE_SETTLEMENT_CYCLE_OVERRIDES


def get_settlement_cycles(asset_class):
    """ Returns settlement cycle configuration for an asset_class """
    if asset_class.upper() == 'EQUITY':
        return {'settlement_cycle': SETTLEMENT_CYCLE,
                'exchange_settlement_cycle_overrides': EXCHANGE_SETTLEMENT_CYCLE_OVERRIDES}
    # Add additional asset classes here
    raise NotImplementedError("This asset class is not yet configured")


def get_country_settlement_cycle(asset_class, country_code):
    if asset_class.upper() == 'EQUITY':
        settlement_cycle = SETTLEMENT_CYCLE.get(country_code)
        if not settlement_cycle:
            raise NotImplementedError("This country/asset class combination is not yet configured")        
        return settlement_cycle
    # Add additional asset classes here
    raise NotImplementedError("This asset class is not yet configured")

# TODO - Add an exchange-level settlement cycle
