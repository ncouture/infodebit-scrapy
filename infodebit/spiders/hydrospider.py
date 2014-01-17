# This scraper finds all regions listed on
# http://www.cehq.gouv.qc.ca/suivihydro/default.asp to get data
# from stations listed under them and retrieves any water flow
# statistics available in order to store them locally


from scrapy.item import Item, Field
from scrapy.http import Request, Response
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import ItemLoader


class StationHydrique(Item):
    entry_type = Field()
    station_id = Field()
    hack = Field()
    name = Field()
    description = Field()
    municipality = Field()
    region = Field()
    lake_or_river_name = Field()
    hydrographic_region = Field()
    drainage_basin = Field()
    flow_regime = Field()
    federal_station_number = Field()
    reference_system = Field()


class HistoricalWaterFlow(Item):
    entry_type = Field()
    station_id = Field()
    date = Field()
    time = Field()
    hack = Field()
    water_flow = Field()


class HydroSpider(BaseSpider):
    """http://www.cehq.gouv.qc.ca"""
    name = "cehq"
    allowed_domains = ["www.cehq.gouv.qc.ca"]
    start_urls = ["http://www.cehq.gouv.qc.ca/suivihydro/default.asp"]

    def parse(self, response):
        # fetch all regions URLs
        hxs = HtmlXPathSelector(response)
        if response.url == 'http://www.cehq.gouv.qc.ca/suivihydro/default.asp':
            regions_urls = self.get_regions_urls(hxs)
            for url in regions_urls:
                yield Request(url, callback=self.parse)

        # to fetch all stations URLs
        if 'ListeStation.asp' in response.url:
            stations_urls = self.get_stations_urls(hxs)
            for url in stations_urls:
                yield Request(url, callback=self.parse)

        # to fetch their file information,
        if 'graphique.asp' in response.url:
            (station_id,
             name,
             description,
             municipality,
             region,
             lake_or_river_name,
             hydrographic_region,
             drainage_basin,
             flow_regime,
             federal_station_number) = self.get_station_items(hxs)[:10]

            # update our items,
            l = ItemLoader(item=StationHydrique())
            l.add_value('entry_type', 'station')
            l.add_value('station_id', station_id)
            l.add_value('hack', 'station' + station_id)
            l.add_value('name', name)
            l.add_value('description', description)
            l.add_value('municipality', municipality)
            l.add_value('region', region)
            l.add_value('lake_or_river_name', lake_or_river_name)
            l.add_value('hydrographic_region', hydrographic_region)
            l.add_value('drainage_basin', drainage_basin)
            l.add_value('flow_regime', flow_regime)
            l.add_value('federal_station_number', federal_station_number)
            yield l.load_item()

            # and fetch any data table URL available
            data_table_url = self.get_data_table_url(hxs)
            if data_table_url:
                yield Request(data_table_url, callback=self.parse)

        # to store all of it...
        if 'tableau.asp' in response.url:
            station_id = response.url.split('NoStation=')[1].split('&')[0]
            stats = self.get_data_table_statistics(hxs)
            for stat in stats:
                l = ItemLoader(item=HistoricalWaterFlow())
                l.add_value('entry_type', 'historical')
                l.add_value('station_id', station_id)
                l.add_value('date', stat[0])
                l.add_value('time', stat[1])
                l.add_value('hack', station_id + stat[0] + stat[1])
                l.add_value('water_flow', stat[2])
                yield l.load_item()
            
    def get_regions_urls(self, hxs):
        rel_urls = hxs.xpath(
            '//a[contains(@href, "ListeStation.asp")]/@href').extract()
        return ["http://www.cehq.gouv.qc.ca/suivihydro/" + url
                for url in rel_urls]

    def get_stations_urls(self, hxs):
        rel_urls = hxs.xpath(
            '//a[contains(@href, "graphique.asp")]/@href').extract()
        return ["http://www.cehq.gouv.qc.ca/suivihydro/" + url
                for url in rel_urls]

    def get_station_items(self, hxs):
        return [i.strip() for i in
                hxs
                .xpath('//td[@class="style10"]/text()').extract()]

    def get_data_table_url(self, hxs):
        rel_url = hxs.xpath(
            '//a[contains(@href, "tableau.asp")]/@href').extract()
        if rel_url:
            return "http://www.cehq.gouv.qc.ca/suivihydro/" + rel_url[0]
        return ""
                
    def get_data_table_statistics(self, hxs):
        # returns a list of tuples:
        #     (date, time, water flow)
        stats = [field.extract().strip()
                 for field in hxs.xpath(
                     '//td[contains(@width, "33%")]//text()')]
        return zip(*[iter(stats)]*3)
