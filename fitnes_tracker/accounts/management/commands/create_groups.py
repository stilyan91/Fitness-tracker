import pdb

from django.contrib.auth import models as auth_models, get_user_model
from django.contrib.contenttypes import models
from fitnes_tracker.accounts.models import FitnessUser

from django.core.management.base import BaseCommand

UserModel = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Create group for staff users:
        staff_group, created = auth_models.Group.objects.get_or_create(name='Staffs')
        # Set permissions for view and change users
        if created:
            view_change_permissions = auth_models.Permission.objects.filter(
                codename__in=['view_fitnessuser',
                              'change_fitnessuser', ])
            for permission in view_change_permissions:
                staff_group.permissions.add(permission)

        # Create group of superusers:
        superusers_group, created = auth_models.Group.objects.get_or_create(name='Super Users')
        # Set full permissions
        if created:
            all_permissions = auth_models.Permission.objects.all()
            for perm in all_permissions:
                superusers_group.permissions.add(perm)

        self.stdout.write("Successfully created the groups")
