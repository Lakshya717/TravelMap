from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class carousel(models.Model):
    image = models.ImageField(
        upload_to='SiteSettings/carousel',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ],
        null=True,
        blank=True
    )

    title = models.CharField(max_length=100,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    href = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return f"{self.title}"
    
class features(models.Model):
    logo = models.ImageField(
        upload_to='SiteSettings/features',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ],
        null=True,
        blank=True
    )

    title = models.CharField(max_length=100,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    href_label = models.CharField(max_length=250,blank=True,null=True) 
    href = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return f"{self.title}"

class step(models.Model):
    title = models.CharField(max_length=100,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    order = models.PositiveIntegerField(blank=True,null=True,help_text="Used to order steps in the timeline")
    
    class Meta:
        ordering = ['order']  

    def __str__(self):
        return f"{self.order}. {self.title}"