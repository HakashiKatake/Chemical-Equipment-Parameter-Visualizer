"""
Tests for CSV Normalizer
"""
from django.test import TestCase
from equipment.csv_normalizer import CSVNormalizer, CSVValidationError


class CSVNormalizerTestCase(TestCase):
    
    def test_header_normalization(self):
        """Test header normalization"""
        self.assertEqual(CSVNormalizer.normalize_header('Equipment Name'), 'equipment name')
        self.assertEqual(CSVNormalizer.normalize_header('  Type  '), 'type')
        self.assertEqual(CSVNormalizer.normalize_header('FLOWRATE'), 'flowrate')
    
    def test_type_normalization(self):
        """Test type value normalization"""
        self.assertEqual(CSVNormalizer.normalize_type('Heat Exchanger'), 'heat_exchanger')
        self.assertEqual(CSVNormalizer.normalize_type('Pump'), 'pump')
        self.assertEqual(CSVNormalizer.normalize_type('  Compressor  '), 'compressor')
    
    def test_valid_csv(self):
        """Test parsing valid CSV"""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Valve-1,Valve,60,4.1,105"""
        
        result = CSVNormalizer.validate_and_normalize(csv_content)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['equipment_name'], 'Pump-1')
        self.assertEqual(result[0]['type'], 'pump')
        self.assertEqual(result[0]['flowrate'], 120.0)
    
    def test_missing_column(self):
        """Test CSV with missing column"""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure
Pump-1,Pump,120,5.2"""
        
        with self.assertRaises(CSVValidationError) as context:
            CSVNormalizer.validate_and_normalize(csv_content)
        
        self.assertIn('Missing required columns', str(context.exception))
    
    def test_empty_field(self):
        """Test CSV with empty required field"""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,,120,5.2,110"""
        
        with self.assertRaises(CSVValidationError) as context:
            CSVNormalizer.validate_and_normalize(csv_content)
        
        self.assertEqual(len(context.exception.errors), 1)
        self.assertEqual(context.exception.errors[0]['row'], 2)
    
    def test_invalid_numeric(self):
        """Test CSV with invalid numeric value"""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,invalid,5.2,110"""
        
        with self.assertRaises(CSVValidationError) as context:
            CSVNormalizer.validate_and_normalize(csv_content)
        
        self.assertIn('Expected numeric value', str(context.exception.errors))
