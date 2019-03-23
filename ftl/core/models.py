from django.contrib.auth.models import User, AbstractUser
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


# FTP orgs
class FTLOrg(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)  # URL of the org
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# FTL users
class FTLUser(AbstractUser):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)


# FTL Documents
class FTLDocument(models.Model):
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    ftl_user = models.ForeignKey('FTLUser', on_delete=models.CASCADE)
    ftl_folder = TreeForeignKey('FTLFolder', on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField()
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# FTL Folders
class FTLFolder(MPTTModel):
    name = models.CharField(max_length=128)
    org = models.ForeignKey('FTLOrg', on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
