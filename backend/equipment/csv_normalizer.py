"""
CSV Normalization and Validation Layer

This module provides robust CSV parsing with:
- Case-insensitive header matching
- Whitespace trimming
- Type normalization
- Comprehensive validation
"""
import csv
import io
from typing import List, Dict, Tuple
from django.conf import settings


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors"""
    def __init__(self, errors: List[Dict]):
        self.errors = errors
        super().__init__(f"CSV validation failed with {len(errors)} error(s)")


class CSVNormalizer:
    """
    Handles CSV normalization according to specification.
    
    External CSV headers → Internal field names mapping:
    - Equipment Name → equipment_name
    - Type → type
    - Flowrate → flowrate
    - Pressure → pressure
    - Temperature → temperature
    """
    
    # Header mapping: external (normalized) → internal
    HEADER_MAPPING = {
        'equipment name': 'equipment_name',
        'type': 'type',
        'flowrate': 'flowrate',
        'pressure': 'pressure',
        'temperature': 'temperature',
    }
    
    # Required fields
    REQUIRED_FIELDS = ['equipment_name', 'type', 'flowrate', 'pressure', 'temperature']
    
    # Numeric fields
    NUMERIC_FIELDS = ['flowrate', 'pressure', 'temperature']
    
    @staticmethod
    def normalize_header(header: str) -> str:
        """Normalize a header: lowercase, strip whitespace"""
        return header.strip().lower()
    
    @staticmethod
    def normalize_type(value: str) -> str:
        """
        Normalize equipment type value:
        - Lowercase
        - Replace spaces with underscores
        
        Example: "Heat Exchanger" → "heat_exchanger"
        """
        return value.strip().lower().replace(' ', '_')
    
    @classmethod
    def parse_csv(cls, file_content: bytes, max_size: int = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse and normalize CSV content.
        
        Args:
            file_content: Raw bytes of CSV file
            max_size: Maximum file size in bytes (optional)
            
        Returns:
            Tuple of (normalized_data, errors)
            - normalized_data: List of dictionaries with normalized field names
            - errors: List of validation error dictionaries
            
        Raises:
            CSVValidationError: If critical validation fails
        """
        # Check file size
        if max_size and len(file_content) > max_size:
            raise CSVValidationError([{
                'error': f'File size exceeds limit of {max_size} bytes'
            }])
        
        # Decode content
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise CSVValidationError([{
                'error': 'File must be UTF-8 encoded'
            }])
        
        # Parse CSV
        try:
            csv_file = io.StringIO(content_str)
            reader = csv.DictReader(csv_file)
            
            # Normalize and validate headers
            if not reader.fieldnames:
                raise CSVValidationError([{
                    'error': 'CSV file is empty or has no headers'
                }])
            
            # Create header mapping
            header_map = {}
            normalized_headers = {}
            
            for header in reader.fieldnames:
                normalized = cls.normalize_header(header)
                if normalized in cls.HEADER_MAPPING:
                    internal_name = cls.HEADER_MAPPING[normalized]
                    header_map[header] = internal_name
                    normalized_headers[normalized] = internal_name
            
            # Check for missing required columns
            missing_columns = []
            for required in cls.REQUIRED_FIELDS:
                # Find the normalized external header for this internal field
                found = False
                for ext_norm, internal in cls.HEADER_MAPPING.items():
                    if internal == required and ext_norm in normalized_headers:
                        found = True
                        break
                if not found:
                    # Convert internal name back to readable format
                    readable = required.replace('_', ' ').title()
                    missing_columns.append(readable)
            
            if missing_columns:
                raise CSVValidationError([{
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }])
            
            # Parse rows
            normalized_data = []
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                normalized_row = {}
                row_errors = []
                
                # Map and validate each field
                for external_header, internal_field in header_map.items():
                    value = row.get(external_header, '').strip()
                    
                    # Check for empty required fields
                    if not value:
                        row_errors.append({
                            'row': row_num,
                            'column': external_header,
                            'error': 'Field cannot be empty'
                        })
                        continue
                    
                    # Normalize type field
                    if internal_field == 'type':
                        value = cls.normalize_type(value)
                    
                    # Validate and convert numeric fields
                    if internal_field in cls.NUMERIC_FIELDS:
                        try:
                            value = float(value)
                        except ValueError:
                            row_errors.append({
                                'row': row_num,
                                'column': external_header,
                                'error': 'Expected numeric value'
                            })
                            continue
                    
                    normalized_row[internal_field] = value
                
                # Add row if valid
                if row_errors:
                    errors.extend(row_errors)
                elif normalized_row:  # Skip empty rows
                    normalized_data.append(normalized_row)
            
            # Check if we have any valid data
            if not normalized_data and not errors:
                raise CSVValidationError([{
                    'error': 'CSV file contains no valid data rows'
                }])
            
            # If there are validation errors, raise them
            if errors:
                raise CSVValidationError(errors)
            
            return normalized_data, []
            
        except csv.Error as e:
            raise CSVValidationError([{
                'error': f'CSV parsing error: {str(e)}'
            }])
    
    @classmethod
    def validate_and_normalize(cls, file_content: bytes) -> List[Dict]:
        """
        Main entry point for CSV validation and normalization.
        
        Args:
            file_content: Raw bytes of CSV file
            
        Returns:
            List of normalized equipment dictionaries
            
        Raises:
            CSVValidationError: If validation fails
        """
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', None)
        normalized_data, errors = cls.parse_csv(file_content, max_size)
        
        if errors:
            raise CSVValidationError(errors)
        
        return normalized_data
