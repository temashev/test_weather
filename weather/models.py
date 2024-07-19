from django.db import models

class CitySearchHistory(models.Model):
    city_name = models.CharField(max_length=100)
    search_count = models.IntegerField(default=1)

    def __str__(self):
        return self.city_name
