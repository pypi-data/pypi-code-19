import scrapy
import datetime
import string
from datetime import date
import calendar
import re

# scrapy runspider --nolog lunch_spider.py
class LunchSpider(scrapy.Spider):
    name = "lunch"

    def start_requests(self):
        yield scrapy.Request(url="http://foodamenus.com/appboy", callback=self.parse)

    def parse(self, response):
        weekday = calendar.day_name[date.today().weekday()].lower()
        # TODO(liann): make this more resilient to page changes
        tmpl = string.Template("//h2[contains(translate(., $upper_day, $day), $day)]")
        xpath_query = tmpl.substitute(upper_day=weekday.upper(),day=weekday)

        # get results from page, downcase errthing
        matches = response.xpath(xpath_query).extract()
        matches = list(map(lambda match: match.lower(), matches))

        for match in matches:
            if weekday.lower() in match:
                matcher = re.compile(weekday +': (.*)</')
                restaurant_names = matcher.findall(match)
                message = "today's lunch is %s!!!!!!!!!!!" % restaurant_names[0]
                print(message)
                yield {'message': message}
