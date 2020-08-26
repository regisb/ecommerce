"""
Django management command to import the SDN (Consolidated Screening List) CSV.
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from ecommerce.extensions.payment.utils import populate_sdn_fallback_data_and_metadata, retrieve_sdn_csv_file

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Import the SDN (Consolidated Screening List) CSV into the SDNFallbackMetadata and SDNFallbackData models.
    """

    def handle(self, *args, **options):
        sdn_file = retrieve_sdn_csv_file()
        with transaction.atomic():
            populate_sdn_fallback_data_and_metadata(sdn_file)
        logger.info('Imported SDN CSV into the SDNFallbackMetadata and SDNFallbackData models.')
        self.stdout.write(
            self.style.SUCCESS(
                'Imported SDN CSV into the SDNFallbackMetadata and SDNFallbackData models.'
            )
        )
