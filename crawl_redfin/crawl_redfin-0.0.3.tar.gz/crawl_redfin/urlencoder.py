#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
try:
    from .pkg.crawlib.urlencoder import BaseUrlEncoder
except:
    from crawl_redfin.pkg.crawlib.urlencoder import BaseUrlEncoder


class UrlEncoder(BaseUrlEncoder):
    """Redfin url encoder.
    """
    domain = "https://www.redfin.com"

    def state_listpage(self):
        """

        Example: https://www.redfin.com/sitemap
        """
        return "https://www.redfin.com/sitemap"

    def county_and_zipcode_listpage(self, state):
        """

        Example: https://www.redfin.com/sitemap/MD
        """
        return "https://www.redfin.com/sitemap/{state}".format(
            state=state)

    def city_listpage(self, href=None,
                      county_code=None, state=None, county_name=None):
        """

        parameter example:

        :param href: "/sitemap/1324/MD/Montgomery-County"
        :param county_code: "1324"
        :param state: example: "MD"
        :param county_name: "Montgomery-County"

        Example: https://www.redfin.com/sitemap/1324/MD/Montgomery-County
        """
        if href:
            return self.url_join(href)
        else:
            return "https://www.redfin.com/sitemap/{county_code}/{state}/{county_name}".\
                format(
                    county_code=county_code,
                    state=state,
                    county_name=county_name,
                )

    def house_by_city(self, href=None,
                      city_code=None, state=None, city_name=None):
        """

        parameter example:

        :param href: /city/17332/MD/Rockville
        :param county_code: "17332"
        :param state: "MD"
        :param county_name: "Rockville"

        Example: https://www.redfin.com/city/17332/MD/Rockville
        """
        if href:
            return self.url_join(href)
        else:
            return "https://www.redfin.com/city/{city_code}/{state}/{city_name}".\
                format(
                    city_code=city_code,
                    state=state,
                    city_name=city_name,
                )

    def house_by_zipcode(self, zipcode):
        return "https://www.redfin.com/zipcode/{zipcode}".format(
            zipcode=zipcode)

    def house_listpage_csv(self,
                           region_id,
                           house_type_code=None,
                           sold_within_days=36500,
                           returns=10000):
        """Get house listed in a city.

        :param region_id: city region id.
        :param house_type_code: see :class:`~crawl_redfin.const.house_type.HouseType`.
        :param sold_within_days: sold in, like 365 days.
        :param returns: max house returned.

        Example: https://www.redfin.com/stingray/api/gis-csv?al=1&market=dc&num_homes=100&ord=redfin-recommended-asc&page_number=1&region_id=7974&region_type=6&sf=1,2,3,4,5,6,7&sold_within_days=365&sp=true&status=9&uipt=2&v=8
        """
        if house_type_code is None:
            house_type_code = [1, 2, 3, 4, 5, 6]

        if isinstance(house_type_code, (list, tuple)):
            house_type_code = ",".join([str(i) for i in house_type_code])
        else:
            house_type_code = str(house_type_code)

        return "https://www.redfin.com/stingray/api/gis-csv?al=1&market=dc&num_homes={returns}&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type=6&sf=1,2,3,4,5,6,7&sold_within_days={sold_within_days}&sp=true&status=9&uipt={house_type_code}&v=8".format(
            returns=returns,
            region_id=region_id,
            sold_within_days=sold_within_days,
            house_type_code=house_type_code,
        )


urlencoder = UrlEncoder()


if __name__ == "__main__":
    import webbrowser
    from crawl_redfin.const import HouseType

    def test_all():
        webbrowser.open(urlencoder.state_listpage())
        webbrowser.open(urlencoder.county_and_zipcode_listpage(state="MD"))
        webbrowser.open(
            urlencoder.city_listpage(href="/sitemap/1324/MD/Montgomery-County"))
        webbrowser.open(
            urlencoder.house_by_city(href="/city/17332/MD/Rockville"))
        webbrowser.open(
            urlencoder.house_by_zipcode("20850"))

        url = urlencoder.house_listpage_csv(
            7974,
            HouseType.Condo.id,
            sold_within_days=365,
            returns=100,
        )
        print(url)

    test_all()
