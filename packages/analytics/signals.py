# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from .models import PageVisit, SiteVisit


# @receiver(post_save, sender=PageVisit)
# def add_site_visit_count(sender, instance, created, **kwargs):
#     if created:
#         SiteVisit.objects.create(
#             site=instance.page.host,
#             ip_addr=instance.ip_addr,
#         )




