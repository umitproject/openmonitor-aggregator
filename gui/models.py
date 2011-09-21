from django.db import models
from django.core.cache import cache

MAX_RANGE=50 # in degrees
RANGE_LEAP=2 # in degree
ALL_REGIONS_KEY='all_regions'
CLOSEST_REGION_KEY='closest_region_%s_%s'
CLOSEST_REGIONS_KEY='closes_regions_%s_%s'

class Region(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, default='')
    lat = models.DecimalField()
    lon = models.DecimalField()
    region = models.ForeignKey('gui.Region', null=True, blank=True, default=None)
    aggregations = models.TextField(blank=True, null=True, default='')
    
    def add_aggregation(self, aggregation):
        aggregations = self.aggregations.split(',')
        aggregations.append(aggregation.id)
        self.aggregations = ','.join(aggregations)
        self.save()
    
    @staticmethod
    def all_regions():
        regions = cache.get(ALL_REGIONS_KEY, None)
        if regions is None:
            regions = [str(region) for region in Region.objects.all()]
            cache.set(ALL_REGIONS_KEY, regions)
        return regions
    
    @staticmethod
    def closest_region(lat, lon):
        """Not necessarily the closest region, but one in the closest range.
        TODO: make sure we save the regions in order of distance inside the
        aggregations so that we can retrieve the closest region rather than a
        random one in the closest range.
        """
        region = cache.get(CLOSEST_REGION_KEY % (lat, lon), None)
        if region is None:
            aggs = RegionAggregation.objects.filter(lat__gte=lat+MAX_RANGE, lat__lte=lat-MAX_RANGE,
                                                    lon__gte=lon+MAX_RANGE, lon__lte=lon-MAX_RANGE).order_by('range')[:1]
            region = Region.objects.get(pk=aggs.regions.split(',')[0])
            cache.set(CLOSEST_REGION_KEY % (lat, lon), region)
        return region
    
    @staticmethod
    def closest_regions(lat, lon):
        regions = cache.get(CLOSEST_REGIONS_KEY % (lat, lon), None)
        if regions is None:
            aggs = RegionAggregation.objects.filter(lat__gte=lat+MAX_RANGE, lat__lte=lat-MAX_RANGE,
                                                    lon__gte=lon+MAX_RANGE, lon__lte=lon-MAX_RANGE).order_by('range')
            regions = []
            for agg in aggs:
                regions += [Region.objects.get(pk=id) for id in agg.regions.split(',')]
            
            cache.set(CLOSEST_REGIONS_KEY % (lat, lon), regions)
        
        return regions
    
    @property
    def regions(self):
        regions = []
        regions += self.region.regions
        return regions
    
    def save(self, *args, **kwargs):
        super(Region, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return "%s%s" % (self.name, ", %s" % self.region if self.region else "")


class RegionAggregation(models.Model):
    lat = models.DecimalField() # Base Latitude
    lon = models.DecimalField() # Base Longitude
    range = models.IntegerField() # The range in degrees
    regions = models.TextField()

    def add(self, region):
        regions = self.regions.split(',')
        regions.append(region.id)
        self.regions = ','.join(regions)
        self.save()

    @staticmethod
    def add_region(region):
        """Is going to add the region to the aggregation ranges so we can link
        regions that are close to each other.
        """
        lat = region.lat
        lon = region.lon
        
        aggs = RegionAggregation.objects.filter(lat__gte=lat+MAX_RANGE, lat__lte=lat-MAX_RANGE,
                                                lon__gte=lon+MAX_RANGE, lon__lte=lon-MAX_RANGE)
        
        for agg in aggs:
            if ((agg.lat - agg.range) <= lat and (agg.lat + agg.range) >= lat) and \
                ((agg.lon - agg.range) <= lon and (agg.lon + agg.range) >= lon):
                agg.add(region)
                region.add_aggregation(agg)
