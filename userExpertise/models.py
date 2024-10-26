from django.db import models
from django.contrib.auth.models import User

class expertUser(models.Model):
    BADGE_CHOICES = [
        ( "Expert" , 'Expert') , 
        ( "Novice" , 'Novice'),
    ]
    user =  models.ForeignKey(User , on_delete = models.CASCADE)
    badge = models.CharField(max_length = 255 , choices = BADGE_CHOICES , default  = 'Novice')
    score = models.IntegerField()
    
class Domain(models.Model):
    domain = models.CharField(max_length=255)
    score = models.IntegerField(default=0)  # Add score field

    def __str__(self):
        return self.domain
    
    
class Tags(models.Model):
    name = models.CharField(max_length=50)
    user = models.ManyToManyField(User)
    domain = models.ForeignKey(Domain , on_delete = models.CASCADE , null = False)


    
    
    
    
