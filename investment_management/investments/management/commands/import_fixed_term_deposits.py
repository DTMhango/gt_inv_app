import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date
from investments.models import FixedTermDeposit, User
from datetime import datetime

class Command(BaseCommand):
    help = 'Import FixedTermDeposit data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        print(f"Attempting to open file: {csv_file}")

        try:
            with open(csv_file, newline='', encoding='utf-8-sig') as file:
                print("File opened successfully")
                reader = csv.DictReader(file)
                
                # Get the fieldnames and remove BOM from the first fieldname
                fieldnames = reader.fieldnames
                if fieldnames[0].startswith('\ufeff'):
                    fieldnames[0] = fieldnames[0][1:]

                # Create a new reader with the corrected fieldnames
                reader = csv.DictReader(file, fieldnames=fieldnames)
                
                # Skip the header row since we already processed it
                next(reader)

                for row in reader:
                    print("Processing row:", row)  # Print each row for debugging
                    try:
                        manager = User.objects.get(pk=row['manager_id'])

                        # Parse dates
                        start_date = datetime.strptime(row['start_date'], '%d/%m/%Y').date()
                        maturity_date = datetime.strptime(row['maturity_date'], '%d/%m/%Y').date()

                        FixedTermDeposit.objects.create(
                            fxd_id=row['fxd_id'],
                            start_date=start_date,
                            maturity_date=maturity_date,
                            principal_amount=row['principal_amount'],
                            currency=row['currency'],
                            interest_rate=row['interest_rate'],
                            bank_rating=row['bank_rating'],  # Corrected from bond_rating to bank_rating
                            counterparty=row['counterparty'],
                            manager=manager,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Successfully added FixedTermDeposit {row["fxd_id"]}'))
                    except User.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Manager with ID {row["manager_id"]} does not exist. Skipping FixedTermDeposit {row["fxd_id"]}.'))
                    except ValueError as e:
                        self.stdout.write(self.style.WARNING(f'Error parsing date for FixedTermDeposit {row["fxd_id"]}: {e}'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file}" does not exist')
        except Exception as e:
            print(f"Error: {e}")
