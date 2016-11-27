from django.db import models

# Create your models here.
class Domains(models.Model):
    """ドメイン"""
    id = models.IntegerField()
    name = models.CharField('名前', max_length=45)
    display_name = models.CharField('表示名', max_length=255, blank=False)
    user_id = models.IntegerField('ユーザ')
    server_id = models.IntegerField('ユーザ')
    size = models.IntegerField('ユーザ')
    ram = models.IntegerField('ユーザ')
    vcpus = models.IntegerField('ユーザ')
    ip = models.CharField('表示名', max_length=255, blank=False)
    key_path = models.CharField('表示名', max_length=255, blank=False)
    status = models.CharField('名前', max_length=45)
    create_date = models.DateField()
    update_date = models.DateField()
    class Meta:
        db_table = 'domains'

    def __str__(self):
        return self.name

class VcServers(models.Model):
    """ドメイン"""
    id = models.IntegerField('名前', max_length=45)
    name = models.CharField('名前', max_length=45)
    free_size_gb = models.IntegerField('名前', max_length=45)
    create_date = models.DateField()
    update_date = models.DateField()
    class Meta:
        db_table = 'vc_servers'

    def __str__(self):
        return self.name
