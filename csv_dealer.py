import csv
import io
import re


class HandleCsv:
    
    @staticmethod
    def is_valid_url(url):
        # Basic URL validation regex
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.match(url.strip()) is not None

    @staticmethod
    def read_and_validate_csv(csv_bytes : bytes):
        try:
            print("Type of input ",type(csv_bytes))
            # Convert bytes to a file-like object
            csv_file = io.StringIO(csv_bytes.decode('utf-8'))
            csv_reader = csv.reader(csv_file)

            # Check header
            header = next(csv_reader)
            expected_header = ["Sno.", "Product Name", "Input Image Urls"]
            if header != expected_header:
                raise ValueError(
                    f"Invalid header. Expected {expected_header}, got {header}")

            # Validate rows
            for row_num, row in enumerate(csv_reader, start=1):
                if len(row) != 3:
                    raise ValueError(
                        f"Row {row_num} has {len(row)} columns. Expected 3.")

                # Validate Sno. (should be a number)
                try:
                    int(row[0])
                except ValueError:
                    raise ValueError(
                        f"Invalid value in 'Sno.' column at row {row_num}. Expected a number, got '{row[0]}'")

                # Validate Product Name (should be a non-empty string)
                if not row[1] or not isinstance(row[1], str):
                    raise ValueError(
                        f"Invalid 'Product Name' at row {row_num}. Expected a non-empty string.")

                # Validate Input Image Urls (should be comma-separated links)
                urls = row[2].split(',')
                url_pattern = re.compile(r'https?://\S+')
                for url in urls:
                    if not url_pattern.match(url.strip()):
                        raise ValueError(
                            f"Invalid URL in 'Input Image Urls' at row {row_num}: '{url.strip()}'")

                print(f"Row {row_num}: {row}")

            print("CSV file is valid and matches the required format.")
            return True

        except Exception as e:
            print(f"Error: {e}")
        return False
