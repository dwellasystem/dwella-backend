# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.contrib.auth.hashers import make_password, identify_hasher
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @receiver(pre_save, sender=User)
# def hash_password(sender, instance, **kwargs):
#     try:
#         identify_hasher(instance.password)
#     except ValueError:
#         instance.password = make_password(instance.password)