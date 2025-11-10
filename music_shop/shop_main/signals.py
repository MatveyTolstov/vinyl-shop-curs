from django.contrib.auth.models import Group
from django.db import IntegrityError
import logging


logger = logging.getLogger(__name__)


def create_manager_group(sender, **kwargs):
    try:
        Group.objects.create(name='Manager')
        logger.info("Manager group created")
    except IntegrityError:
        logger.info("Manager group already exists")