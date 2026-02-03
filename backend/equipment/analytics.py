"""
Analytics Engine for Chemical Equipment Data

All analytics are computed server-side using pandas.
Frontend should never recompute analytics.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from django.conf import settings


class EquipmentAnalytics:
    """Server-side analytics engine for equipment data"""
    
    def __init__(self, equipment_data: List[Dict[str, Any]]):
        """
        Initialize analytics with equipment data.
        
        Args:
            equipment_data: List of normalized equipment dictionaries
        """
        self.df = pd.DataFrame(equipment_data)
        
    def get_global_summary(self) -> Dict[str, Any]:
        """
        Compute global summary statistics.
        
        Returns:
            Dictionary with:
            - total_count: Total number of equipment
            - avg_flowrate: Average flowrate (m³/h)
            - avg_pressure: Average pressure (bar)
            - avg_temperature: Average temperature (°C)
            - units: Dictionary of units for each metric
        """
        return {
            'total_count': len(self.df),
            'avg_flowrate': round(self.df['flowrate'].mean(), 2),
            'avg_pressure': round(self.df['pressure'].mean(), 2),
            'avg_temperature': round(self.df['temperature'].mean(), 2),
            'min_flowrate': round(self.df['flowrate'].min(), 2),
            'max_flowrate': round(self.df['flowrate'].max(), 2),
            'min_pressure': round(self.df['pressure'].min(), 2),
            'max_pressure': round(self.df['pressure'].max(), 2),
            'min_temperature': round(self.df['temperature'].min(), 2),
            'max_temperature': round(self.df['temperature'].max(), 2),
            'units': settings.EQUIPMENT_UNITS
        }
    
    def get_type_distribution(self) -> Dict[str, int]:
        """
        Get equipment count by normalized type.
        
        Returns:
            Dictionary mapping type → count
        """
        type_counts = self.df['type'].value_counts().to_dict()
        return type_counts
    
    def get_histogram_data(self, bins: int = 10) -> Dict[str, Any]:
        """
        Generate histogram data for flowrate.
        
        Args:
            bins: Number of histogram bins
            
        Returns:
            Dictionary with:
            - bins: List of bin edges
            - counts: List of counts for each bin
            - bin_labels: List of label strings for each bin
        """
        # Create histogram
        counts, bin_edges = np.histogram(self.df['flowrate'], bins=bins)
        
        # Create bin labels
        bin_labels = []
        for i in range(len(bin_edges) - 1):
            label = f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
            bin_labels.append(label)
        
        return {
            'bins': bin_edges.tolist(),
            'counts': counts.tolist(),
            'bin_labels': bin_labels,
            'unit': settings.EQUIPMENT_UNITS['flowrate']
        }
    
    def get_scatter_data(self) -> List[Dict[str, Any]]:
        """
        Generate scatter plot data ready for visualization.
        
        Returns:
            List of dictionaries with:
            - x: pressure value
            - y: temperature value
            - size: flowrate value (for bubble size)
            - label: equipment name
            - type: equipment type
        """
        scatter_data = []
        
        for _, row in self.df.iterrows():
            scatter_data.append({
                'x': round(row['pressure'], 2),
                'y': round(row['temperature'], 2),
                'size': round(row['flowrate'], 2),
                'label': row['equipment_name'],
                'type': row['type']
            })
        
        return scatter_data
    
    def get_table_data(self) -> List[Dict[str, Any]]:
        """
        Get complete equipment data formatted for table display.
        
        Returns:
            List of equipment dictionaries with all fields
        """
        table_data = []
        
        for _, row in self.df.iterrows():
            table_data.append({
                'equipment_name': row['equipment_name'],
                'type': row['type'],
                'flowrate': round(row['flowrate'], 2),
                'pressure': round(row['pressure'], 2),
                'temperature': round(row['temperature'], 2)
            })
        
        return table_data
    
    def get_complete_analytics(self) -> Dict[str, Any]:
        """
        Get all analytics in a single call.
        
        Returns:
            Dictionary containing:
            - summary: Global summary statistics
            - type_distribution: Equipment count by type
            - histogram: Histogram data for flowrate
            - scatter: Scatter plot data
            - table: Complete table data
        """
        return {
            'summary': self.get_global_summary(),
            'type_distribution': self.get_type_distribution(),
            'histogram': self.get_histogram_data(),
            'scatter': self.get_scatter_data(),
            'table': self.get_table_data()
        }


def compute_analytics(equipment_queryset) -> Dict[str, Any]:
    """
    Compute analytics from Django queryset.
    
    Args:
        equipment_queryset: Django queryset of Equipment objects
        
    Returns:
        Complete analytics dictionary
    """
    # Convert queryset to list of dictionaries
    equipment_data = list(equipment_queryset.values(
        'equipment_name', 'type', 'flowrate', 'pressure', 'temperature'
    ))
    
    if not equipment_data:
        return {
            'summary': {
                'total_count': 0,
                'avg_flowrate': 0,
                'avg_pressure': 0,
                'avg_temperature': 0,
                'units': settings.EQUIPMENT_UNITS
            },
            'type_distribution': {},
            'histogram': {'bins': [], 'counts': [], 'bin_labels': []},
            'scatter': [],
            'table': []
        }
    
    analytics = EquipmentAnalytics(equipment_data)
    return analytics.get_complete_analytics()
