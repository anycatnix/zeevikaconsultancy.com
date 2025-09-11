from django.core.management.base import BaseCommand
from core.models import Company
from django.core.files import File
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Adds sample companies to the database'

    def handle(self, *args, **options):
        # Create the company logos directory if it doesn't exist
        logo_dir = os.path.join(settings.MEDIA_ROOT, 'company_logos')
        os.makedirs(logo_dir, exist_ok=True)

        companies = [
            {
                'name': 'TechCorp',
                'description': 'Leading technology solutions provider',
                'website': 'https://techcorp.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/techcorp.png')
            },
            {
                'name': 'InnovateSoft',
                'description': 'Innovative software development company',
                'website': 'https://innovatesoft.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/innovatesoft.png')
            },
            {
                'name': 'GlobalTech',
                'description': 'Global technology consulting firm',
                'website': 'https://globaltech.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/globaltech.png')
            },
            {
                'name': 'WebCrafters',
                'description': 'Web development and design agency',
                'website': 'https://webcrafters.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/webcrafters.png')
            },
            {
                'name': 'DataSphere',
                'description': 'Big data and analytics solutions',
                'website': 'https://datasphere.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/datasphere.png')
            },
            {
                'name': 'CloudNova',
                'description': 'Cloud infrastructure services',
                'website': 'https://cloudnova.example.com',
                'is_featured': True,
                'logo_path': os.path.join(settings.MEDIA_ROOT, 'company_logos/cloudnova.png')
            }
        ]

        for company_data in companies:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    'description': company_data['description'],
                    'website': company_data['website'],
                    'is_featured': company_data['is_featured'],
                    'is_active': True
                }
            )
            
            # If the company already exists, update its fields
            if not created:
                company.description = company_data['description']
                company.website = company_data['website']
                company.is_featured = company_data['is_featured']
                company.is_active = True
                company.save()

            # Add logo if path exists
            if os.path.exists(company_data['logo_path']) and not company.logo:
                with open(company_data['logo_path'], 'rb') as f:
                    company.logo.save(
                        os.path.basename(company_data['logo_path']),
                        File(f),
                        save=True
                    )
                self.stdout.write(self.style.SUCCESS(f'Added logo for {company.name}'))
            elif not os.path.exists(company_data['logo_path']):
                self.stdout.write(self.style.WARNING(f'Logo not found at {company_data["logo_path"]}'))

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} company: {company.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully added sample companies'))
        self.stdout.write(self.style.NOTICE('Note: If you see warnings about missing logos, you can add them later through the admin interface.'))
