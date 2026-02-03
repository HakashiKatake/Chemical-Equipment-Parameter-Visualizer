"""
Main Desktop Application

PyQt5-based desktop application for Chemical Equipment Parameter Visualizer
Mirrors web functionality with native UI
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QListWidget, QTabWidget, QComboBox,
    QHeaderView, QStackedWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from api_client import APIClient


class APIThread(QThread):
    """Thread for API calls to prevent UI blocking"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class LoginWindow(QWidget):
    """Login/Register Window"""
    login_success = pyqtSignal(str)  # Emits username
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Equipment Visualizer - Login')
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel('Chemical Equipment\nParameter Visualizer')
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setMinimumHeight(35)
        layout.addWidget(self.username_input)
        
        # Email (for registration)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Email (for registration)')
        self.email_input.setMinimumHeight(35)
        self.email_input.hide()
        layout.addWidget(self.email_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton('Login')
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton('Register')
        self.register_btn.setMinimumHeight(40)
        self.register_btn.clicked.connect(self.toggle_register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        # Status label
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.is_register_mode = False
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
    
    def toggle_register(self):
        self.is_register_mode = not self.is_register_mode
        if self.is_register_mode:
            self.email_input.show()
            self.login_btn.setText('Register')
            self.register_btn.setText('Back to Login')
        else:
            self.email_input.hide()
            self.login_btn.setText('Login')
            self.register_btn.setText('Register')
        self.status_label.setText('')
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText('Please fill in all fields')
            self.status_label.setStyleSheet('color: #e74c3c;')
            return
        
        self.status_label.setText('Authenticating...')
        self.status_label.setStyleSheet('color: #3498db;')
        self.login_btn.setEnabled(False)
        
        if self.is_register_mode:
            email = self.email_input.text().strip()
            self.api_thread = APIThread(self.api_client.register, username, password, email)
        else:
            self.api_thread = APIThread(self.api_client.login, username, password)
        
        self.api_thread.finished.connect(self.on_auth_success)
        self.api_thread.error.connect(self.on_auth_error)
        self.api_thread.start()
    
    def on_auth_success(self, data):
        self.login_success.emit(data['username'])
        self.close()
    
    def on_auth_error(self, error):
        self.status_label.setText(f'Error: {error}')
        self.status_label.setStyleSheet('color: #e74c3c;')
        self.login_btn.setEnabled(True)


class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_histogram(self, histogram_data):
        """Plot flowrate histogram"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = histogram_data['bin_labels']
        counts = histogram_data['counts']
        unit = histogram_data['unit']
        
        ax.bar(range(len(labels)), counts, color='#3498db', edgecolor='black', linewidth=0.5)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_xlabel(f'Flowrate ({unit})')
        ax.set_ylabel('Count')
        ax.set_title('Flowrate Distribution', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie(self, type_distribution):
        """Plot type distribution pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        types = list(type_distribution.keys())
        counts = list(type_distribution.values())
        
        ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax.set_title('Equipment Type Distribution', fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_scatter(self, scatter_data, units):
        """Plot pressure vs temperature scatter"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        x_vals = [point['x'] for point in scatter_data]
        y_vals = [point['y'] for point in scatter_data]
        
        ax.scatter(x_vals, y_vals, alpha=0.6, c='#e74c3c', s=100, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(f"Pressure ({units['pressure']})")
        ax.set_ylabel(f"Temperature ({units['temperature']})")
        ax.set_title('Pressure vs Temperature', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()


class MainWindow(QMainWindow):
    """Main Application Window"""
    
    def __init__(self, api_client, username):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.datasets = []
        self.current_dataset_id = None
        self.current_analytics = None
        
        self.init_ui()
        self.load_datasets()
    
    def init_ui(self):
        self.setWindowTitle(f'Equipment Visualizer - {self.username}')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Header
        header = QLabel(f'Welcome, {self.username}')
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)
        
        # Upload section
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton('Upload CSV File')
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setMinimumHeight(40)
        upload_layout.addWidget(upload_btn)
        
        refresh_btn = QPushButton('Refresh Datasets')
        refresh_btn.clicked.connect(self.load_datasets)
        refresh_btn.setMinimumHeight(40)
        upload_layout.addWidget(refresh_btn)
        
        upload_layout.addStretch()
        main_layout.addLayout(upload_layout)
        
        # Content area
        content_layout = QHBoxLayout()
        
        # Left panel - Dataset list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel('Dataset History:'))
        
        self.dataset_list = QListWidget()
        self.dataset_list.itemClicked.connect(self.on_dataset_selected)
        left_layout.addWidget(self.dataset_list)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)
        content_layout.addWidget(left_panel)
        
        # Right panel - Tabs
        self.tabs = QTabWidget()
        self.tabs.setMinimumWidth(700)
        
        # Summary tab
        self.summary_widget = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_widget, 'Summary')
        
        # Charts tab
        charts_widget = QWidget()
        charts_layout = QVBoxLayout()
        charts_layout.setContentsMargins(10, 10, 10, 10)
        
        chart_tabs = QTabWidget()
        self.histogram_chart = ChartWidget()
        self.histogram_chart.setMinimumHeight(400)
        self.pie_chart = ChartWidget()
        self.pie_chart.setMinimumHeight(400)
        self.scatter_chart = ChartWidget()
        self.scatter_chart.setMinimumHeight(400)
        
        chart_tabs.addTab(self.histogram_chart, 'Histogram')
        chart_tabs.addTab(self.pie_chart, 'Type Distribution')
        chart_tabs.addTab(self.scatter_chart, 'Scatter Plot')
        
        charts_layout.addWidget(chart_tabs)
        charts_widget.setLayout(charts_layout)
        self.tabs.addTab(charts_widget, 'Charts')
        
        # Table tab
        self.table_widget = QWidget()
        self.setup_table_tab()
        self.tabs.addTab(self.table_widget, 'Data Table')
        
        content_layout.addWidget(self.tabs, stretch=1)
        
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
        
        # Apply styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTabWidget::pane {
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                border: 1px solid #ddd;
                border-bottom: none;
                color: #2c3e50;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ecf0f1;
                color: #2c3e50;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QComboBox {
                color: #2c3e50;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 5px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #2c3e50;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #ddd;
            }
        """)
    
    def setup_summary_tab(self):
        """Setup summary statistics tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.summary_label = QLabel('Select a dataset to view analytics')
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary_label.setMinimumHeight(300)
        self.summary_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: white;
                border-radius: 5px;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.summary_label, stretch=1)
        
        self.download_btn = QPushButton('Download PDF Report')
        self.download_btn.clicked.connect(self.download_report)
        self.download_btn.setEnabled(False)
        self.download_btn.setMinimumHeight(40)
        layout.addWidget(self.download_btn)
        
        self.summary_widget.setLayout(layout)
    
    def setup_table_tab(self):
        """Setup data table tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Filter by type:'))
        self.type_filter = QComboBox()
        self.type_filter.addItem('All')
        self.type_filter.currentTextChanged.connect(self.apply_table_filter)
        self.type_filter.setMinimumWidth(150)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setDefaultSectionSize(150)
        self.data_table.setSortingEnabled(True)
        self.data_table.setAlternatingRowColors(True)
        layout.addWidget(self.data_table)
        
        self.table_widget.setLayout(layout)
    
    def load_datasets(self):
        """Load user datasets"""
        self.dataset_list.clear()
        self.api_thread = APIThread(self.api_client.list_datasets)
        self.api_thread.finished.connect(self.on_datasets_loaded)
        self.api_thread.error.connect(lambda e: QMessageBox.critical(self, 'Error', f'Failed to load datasets: {e}'))
        self.api_thread.start()
    
    def on_datasets_loaded(self, datasets):
        """Handle loaded datasets"""
        self.datasets = datasets
        for dataset in datasets:
            item_text = f"{dataset['filename']}\n{dataset['equipment_count']} equipment"
            self.dataset_list.addItem(item_text)
        
        if datasets:
            self.dataset_list.setCurrentRow(0)
            self.on_dataset_selected(self.dataset_list.item(0))
    
    def on_dataset_selected(self, item):
        """Handle dataset selection"""
        row = self.dataset_list.row(item)
        dataset = self.datasets[row]
        self.current_dataset_id = dataset['id']
        
        # Load analytics
        self.api_thread = APIThread(self.api_client.get_analytics, self.current_dataset_id)
        self.api_thread.finished.connect(self.on_analytics_loaded)
        self.api_thread.error.connect(lambda e: QMessageBox.critical(self, 'Error', f'Failed to load analytics: {e}'))
        self.api_thread.start()
    
    def on_analytics_loaded(self, analytics):
        """Handle loaded analytics"""
        self.current_analytics = analytics
        
        # Update summary
        summary = analytics['summary']
        summary_text = f"""
<h2>Summary Statistics</h2>
<p><b>Total Equipment:</b> {summary['total_count']}</p>

<h3>Flowrate ({summary['units']['flowrate']})</h3>
<p>
Average: {summary['avg_flowrate']:.2f}<br>
Range: {summary['min_flowrate']:.2f} - {summary['max_flowrate']:.2f}
</p>

<h3>Pressure ({summary['units']['pressure']})</h3>
<p>
Average: {summary['avg_pressure']:.2f}<br>
Range: {summary['min_pressure']:.2f} - {summary['max_pressure']:.2f}
</p>

<h3>Temperature ({summary['units']['temperature']})</h3>
<p>
Average: {summary['avg_temperature']:.2f}<br>
Range: {summary['min_temperature']:.2f} - {summary['max_temperature']:.2f}
</p>
        """
        self.summary_label.setText(summary_text)
        self.download_btn.setEnabled(True)
        
        # Update charts
        self.histogram_chart.plot_histogram(analytics['histogram'])
        self.pie_chart.plot_pie(analytics['type_distribution'])
        self.scatter_chart.plot_scatter(analytics['scatter'], summary['units'])
        
        # Update table
        self.populate_table(analytics['table'], summary['units'])
    
    def populate_table(self, data, units):
        """Populate data table"""
        self.data_table.setRowCount(len(data))
        
        # Update type filter
        self.type_filter.clear()
        self.type_filter.addItem('All')
        types = sorted(set(item['type'] for item in data))
        self.type_filter.addItems(types)
        
        for row, item in enumerate(data):
            self.data_table.setItem(row, 0, QTableWidgetItem(item['equipment_name']))
            self.data_table.setItem(row, 1, QTableWidgetItem(item['type']))
            self.data_table.setItem(row, 2, QTableWidgetItem(f"{item['flowrate']:.2f}"))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{item['pressure']:.2f}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{item['temperature']:.2f}"))
        
        self.data_table.resizeColumnsToContents()
    
    def apply_table_filter(self, filter_type):
        """Apply type filter to table"""
        for row in range(self.data_table.rowCount()):
            if filter_type == 'All':
                self.data_table.setRowHidden(row, False)
            else:
                type_item = self.data_table.item(row, 1)
                if type_item and type_item.text() == filter_type:
                    self.data_table.setRowHidden(row, False)
                else:
                    self.data_table.setRowHidden(row, True)
    
    def upload_file(self):
        """Upload CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select CSV File',
            '',
            'CSV Files (*.csv)'
        )
        
        if file_path:
            self.api_thread = APIThread(self.api_client.upload_dataset, file_path)
            self.api_thread.finished.connect(self.on_upload_success)
            self.api_thread.error.connect(lambda e: QMessageBox.critical(self, 'Upload Error', f'Failed to upload: {e}'))
            self.api_thread.start()
    
    def on_upload_success(self, data):
        """Handle successful upload"""
        QMessageBox.information(self, 'Success', 'File uploaded successfully!')
        self.load_datasets()
    
    def download_report(self):
        """Download PDF report"""
        if not self.current_dataset_id:
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Report',
            f'equipment_report_{self.current_dataset_id}.pdf',
            'PDF Files (*.pdf)'
        )
        
        if save_path:
            try:
                self.api_client.download_report(self.current_dataset_id, save_path)
                QMessageBox.information(self, 'Success', 'Report downloaded successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to download report: {str(e)}')


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern flat style
    
    api_client = APIClient()
    
    # Show login window
    login_window = LoginWindow(api_client)
    
    def on_login_success(username):
        main_window = MainWindow(api_client, username)
        main_window.show()
    
    login_window.login_success.connect(on_login_success)
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
