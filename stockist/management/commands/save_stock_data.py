import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from stockist.utils import get_stock_data, validate_stock_symbol
import csv

class Command(BaseCommand):
    help = 'Fetch stock data and save it as a JSON file.'

    def handle(self, *args, **kwargs):
        # Path to the CSV file containing the stock symbols
    
        csv_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'master_stock_data.csv' )
        symbols = []
        csv_errors = []

        # Read the CSV file to get the list of stock symbols
        try:
            with open(csv_path, 'r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Skip header row
                for row in csv_reader:
                    if row and row[0].strip():
                        symbol = row[0].strip().upper()
                        if validate_stock_symbol(symbol):
                            symbols.append(symbol)
                        else:
                            csv_errors.append(f"Invalid stock symbol found: {symbol}")
            if not symbols:
                self.stdout.write(self.style.ERROR("No valid stock symbols found in the CSV file."))
                return
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"The file {csv_path} was not found."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while reading the CSV file: {str(e)}"))
            return

        # Fetch the stock data using the get_stock_data function
        stock_data, fetch_errors, most_active, top_gainers, top_losers, flagged_for_review = get_stock_data(symbols)

        if fetch_errors:
            self.stdout.write(self.style.ERROR("Errors occurred while fetching stock data:"))
            for error in fetch_errors:
                self.stdout.write(self.style.ERROR(error))

        # Save the data as a JSON file
        output_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'stock_data.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            with open(output_path, 'w') as json_file:
                json.dump({
                    'all_stocks': stock_data,
                    'most_active': most_active,
                    'top_gainers': top_gainers,
                    'top_losers': top_losers,
                    'flagged_for_review' : flagged_for_review
                }, json_file, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Stock data successfully saved to {output_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while saving the JSON file: {str(e)}"))

