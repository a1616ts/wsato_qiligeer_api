from django.db import models

# Create your models here.
class Domains(models.Model):
    """ドメイン"""
    display_name = models.CharField('instance name', max_length=45)
    os = models.CharField('os', max_length=255, blank=False)
    user_id = models.IntegerField('user id')
    server_id = models.IntegerField('serever id')
    size = models.IntegerField('size')
    ram = models.IntegerField('ram')
    vcpus = models.IntegerField('vcpus') #　TODO size やるならこれ　http://y0m0r.hateblo.jp/entry/20121030/1351606235
    ipv4_address = models.CharField('ipv4 address', max_length=255, blank=False) # IPAddressField
    sshkey_path = models.CharField('sshkey path', max_length=255, blank=False)
    status = models.CharField('status', max_length=45)
    create_date = models.DateField('create date')
    update_date = models.DateField('update_date')
    class Meta:
        db_table = 'domains'

    def __str__(self):
        return self.name

class VcServers(models.Model):
    id = models.IntegerField(max_length=45)
    name = models.CharField(max_length=45)
    free_size_gb = models.IntegerField()
    create_date = models.DateField()
    update_date = models.DateField()
    class Meta:
        db_table = 'vc_servers'

    def __str__(self):
        return self.name
