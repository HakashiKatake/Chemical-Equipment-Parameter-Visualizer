"""
PDF Report Generation

Server-side PDF report generation with:
- Dataset metadata
- Summary statistics
- Charts (histogram, scatter, type distribution)
- Complete data table
- Clean, minimal layout
"""
import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from typing import Dict, Any
from datetime import datetime
from django.conf import settings


def generate_pdf_report(dataset, analytics_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate a PDF report for a dataset.
    
    Args:
        dataset: Dataset model instance
        analytics_data: Complete analytics dictionary
        
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = io.BytesIO()
    
    # Create PDF with multiple pages
    with PdfPages(buffer) as pdf:
        # Page 1: Title and Summary
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Chemical Equipment Analysis Report', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # Dataset metadata
        metadata_text = f"""Dataset Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Filename: {dataset.filename}
Uploaded: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}
User: {dataset.user.username}
Equipment Count: {dataset.row_count}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        plt.text(0.1, 0.88, metadata_text, fontsize=10, 
                verticalalignment='top', family='monospace')
        
        # Summary statistics
        summary = analytics_data['summary']
        summary_text = f"""Summary Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Equipment: {summary['total_count']}

Flowrate ({summary['units']['flowrate']}):
  Average: {summary['avg_flowrate']:.2f}
  Range: {summary['min_flowrate']:.2f} - {summary['max_flowrate']:.2f}

Pressure ({summary['units']['pressure']}):
  Average: {summary['avg_pressure']:.2f}
  Range: {summary['min_pressure']:.2f} - {summary['max_pressure']:.2f}

Temperature ({summary['units']['temperature']}):
  Average: {summary['avg_temperature']:.2f}
  Range: {summary['min_temperature']:.2f} - {summary['max_temperature']:.2f}
"""
        
        plt.text(0.1, 0.65, summary_text, fontsize=10,
                verticalalignment='top', family='monospace')
        
        # Type distribution
        type_dist = analytics_data['type_distribution']
        dist_text = "Equipment Distribution by Type:\n" + "━" * 44 + "\n\n"
        for eq_type, count in sorted(type_dist.items()):
            dist_text += f"  {eq_type:20s} : {count:3d}\n"
        
        plt.text(0.1, 0.33, dist_text, fontsize=10,
                verticalalignment='top', family='monospace')
        
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: Charts
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Data Visualizations', fontsize=16, fontweight='bold')
        
        # 1. Flowrate Histogram
        ax1 = axes[0, 0]
        hist_data = analytics_data['histogram']
        if hist_data['counts']:
            ax1.bar(range(len(hist_data['bin_labels'])), hist_data['counts'],
                   color='#4A90E2', edgecolor='black', linewidth=0.5)
            ax1.set_xticks(range(len(hist_data['bin_labels'])))
            ax1.set_xticklabels(hist_data['bin_labels'], rotation=45, ha='right', fontsize=8)
            ax1.set_xlabel(f"Flowrate ({hist_data['unit']})", fontsize=10)
            ax1.set_ylabel('Count', fontsize=10)
            ax1.set_title('Flowrate Distribution', fontsize=12, fontweight='bold')
            ax1.grid(axis='y', alpha=0.3)
        
        # 2. Type Distribution Pie Chart
        ax2 = axes[0, 1]
        if type_dist:
            types = list(type_dist.keys())
            counts = list(type_dist.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
            ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90,
                   colors=colors)
            ax2.set_title('Equipment Type Distribution', fontsize=12, fontweight='bold')
        
        # 3. Pressure vs Temperature Scatter
        ax3 = axes[1, 0]
        scatter_data = analytics_data['scatter']
        if scatter_data:
            x_vals = [point['x'] for point in scatter_data]
            y_vals = [point['y'] for point in scatter_data]
            sizes = [point['size'] for point in scatter_data]
            # Normalize sizes for visualization
            sizes_normalized = [(s / max(sizes)) * 300 + 20 for s in sizes]
            
            ax3.scatter(x_vals, y_vals, s=sizes_normalized, alpha=0.6,
                       c='#E94B3C', edgecolors='black', linewidth=0.5)
            ax3.set_xlabel(f"Pressure ({summary['units']['pressure']})", fontsize=10)
            ax3.set_ylabel(f"Temperature ({summary['units']['temperature']})", fontsize=10)
            ax3.set_title('Pressure vs Temperature\n(bubble size = flowrate)', 
                         fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # 4. Box plot for all parameters
        ax4 = axes[1, 1]
        table_data = analytics_data['table']
        if table_data:
            flowrates = [row['flowrate'] for row in table_data]
            pressures = [row['pressure'] for row in table_data]
            temperatures = [row['temperature'] for row in table_data]
            
            # Normalize for comparison
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            data_normalized = scaler.fit_transform(
                [[f, p, t] for f, p, t in zip(flowrates, pressures, temperatures)]
            )
            
            bp = ax4.boxplot([data_normalized[:, 0], data_normalized[:, 1], data_normalized[:, 2]],
                            labels=['Flowrate', 'Pressure', 'Temperature'],
                            patch_artist=True)
            
            colors = ['#4A90E2', '#50C878', '#FFB347']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            ax4.set_ylabel('Normalized Value', fontsize=10)
            ax4.set_title('Parameter Distribution (Normalized)', 
                         fontsize=12, fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 3: Data Table
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('Complete Equipment Data', fontsize=16, fontweight='bold')
        
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        if table_data:
            # Prepare table data
            headers = ['Equipment Name', 'Type', 
                      f"Flowrate\n({summary['units']['flowrate']})",
                      f"Pressure\n({summary['units']['pressure']})",
                      f"Temperature\n({summary['units']['temperature']})"]
            
            table_rows = []
            for row in table_data:
                table_rows.append([
                    row['equipment_name'],
                    row['type'],
                    f"{row['flowrate']:.2f}",
                    f"{row['pressure']:.2f}",
                    f"{row['temperature']:.2f}"
                ])
            
            table = ax.table(cellText=table_rows, colLabels=headers,
                           cellLoc='left', loc='center',
                           colWidths=[0.25, 0.2, 0.15, 0.15, 0.15])
            
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)
            
            # Style header
            for i in range(len(headers)):
                cell = table[(0, i)]
                cell.set_facecolor('#4A90E2')
                cell.set_text_props(weight='bold', color='white')
            
            # Alternate row colors
            for i in range(1, len(table_rows) + 1):
                for j in range(len(headers)):
                    cell = table[(i, j)]
                    if i % 2 == 0:
                        cell.set_facecolor('#F0F0F0')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = f'Equipment Analysis Report - {dataset.filename}'
        d['Author'] = 'Chemical Equipment Parameter Visualizer'
        d['Subject'] = 'Equipment Data Analysis'
        d['Keywords'] = 'Equipment, Analysis, Chemical, Data'
        d['CreationDate'] = datetime.now()
    
    buffer.seek(0)
    return buffer
