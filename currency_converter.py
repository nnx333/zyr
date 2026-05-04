import sys
import json
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class CurrencyConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "YOUR_API_KEY_HERE"  # Замените на свой API ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.currencies = self.get_available_currencies()
        self.history = self.load_history()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Currency Converter")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Currency Converter")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Currency selection layout
        currency_layout = QHBoxLayout()
        
        # From currency
        from_layout = QVBoxLayout()
        from_label = QLabel("From:")
        from_label.setFont(QFont("Arial", 12))
        self.from_currency = QComboBox()
        self.from_currency.addItems(sorted(self.currencies.keys()))
        self.from_currency.setCurrentText("USD")
        from_layout.addWidget(from_label)
        from_layout.addWidget(self.from_currency)
        
        # Swap button
        swap_button = QPushButton("⇄")
        swap_button.setFixedSize(50, 50)
        swap_button.setFont(QFont("Arial", 18))
        swap_button.clicked.connect(self.swap_currencies)
        swap_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
        """)
        
        # To currency
        to_layout = QVBoxLayout()
        to_label = QLabel("To:")
        to_label.setFont(QFont("Arial", 12))
        self.to_currency = QComboBox()
        self.to_currency.addItems(sorted(self.currencies.keys()))
        self.to_currency.setCurrentText("EUR")
        to_layout.addWidget(to_label)
        to_layout.addWidget(self.to_currency)
        
        currency_layout.addLayout(from_layout)
        currency_layout.addWidget(swap_button)
        currency_layout.addLayout(to_layout)
        main_layout.addLayout(currency_layout)
        
        # Amount input
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        amount_label.setFont(QFont("Arial", 12))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount...")
        self.amount_input.textChanged.connect(self.clear_result)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        main_layout.addLayout(amount_layout)
        
        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_currency)
        self.convert_button.setMinimumHeight(50)
        main_layout.addWidget(self.convert_button)
        
        # Result label
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("margin: 20px 0; color: #2196F3;")
        main_layout.addWidget(self.result_label)
        
        # History table
        history_label = QLabel("Conversion History")
        history_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(history_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "From", "To", "Amount", "Result"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_history_to_table()
        main_layout.addWidget(self.history_table)
        
        # Clear history button
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        main_layout.addWidget(clear_button)
        
        central_widget.setLayout(main_layout)
        
    def get_available_currencies(self):
        """Get list of available currencies"""
        return {
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "AUD": "Australian Dollar",
            "CAD": "Canadian Dollar",
            "CHF": "Swiss Franc",
            "CNY": "Chinese Yuan",
            "INR": "Indian Rupee",
            "RUB": "Russian Ruble",
            "BRL": "Brazilian Real",
            "MXN": "Mexican Peso",
            "KRW": "South Korean Won",
            "SEK": "Swedish Krona",
            "NOK": "Norwegian Krone"
        }
        
    def clear_result(self):
        self.result_label.setText("")
        
    def swap_currencies(self):
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        self.from_currency.setCurrentText(to_curr)
        self.to_currency.setCurrentText(from_curr)
        
    def validate_amount(self, amount_text):
        try:
            amount = float(amount_text)
            if amount <= 0:
                return False, "Amount must be a positive number"
            return True, amount
        except ValueError:
            return False, "Please enter a valid number"
            
    def get_exchange_rate(self, from_currency, to_currency):
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url)
            data = response.json()
            
            if data["result"] == "success":
                return True, data["conversion_rate"]
            else:
                return False, f"API Error: {data['error-type']}"
        except Exception as e:
            return False, f"Connection Error: {str(e)}"
            
    def convert_currency(self):
        amount_text = self.amount_input.text()
        valid, result = self.validate_amount(amount_text)
        
        if not valid:
            self.show_error(result)
            return
            
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        
        self.convert_button.setEnabled(False)
        self.convert_button.setText("Converting...")
        
        success, rate = self.get_exchange_rate(from_curr, to_curr)
        
        if success:
            converted_amount = result * rate
            self.result_label.setText(f"{result:.2f} {from_curr} = {converted_amount:.2f} {to_curr}")
            self.add_to_history(from_curr, to_curr, result, converted_amount)
        else:
            self.show_error(rate)
            
        self.convert_button.setEnabled(True)
        self.convert_button.setText("Convert")
        
    def add_to_history(self, from_curr, to_curr, amount, result):
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversion = {
            "date": date_str,
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result
        }
        self.history.append(conversion)
        self.save_history()
        self.add_row_to_table(conversion)
        
    def add_row_to_table(self, conversion):
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(conversion["date"]))
        self.history_table.setItem(row, 1, QTableWidgetItem(conversion["from"]))
        self.history_table.setItem(row, 2, QTableWidgetItem(conversion["to"]))
        self.history_table.setItem(row, 3, QTableWidgetItem(f"{conversion['amount']:.2f}"))
        self.history_table.setItem(row, 4, QTableWidgetItem(f"{conversion['result']:.2f}"))
        
    def load_history_to_table(self):
        self.history_table.setRowCount(0)
        for conversion in self.history:
            self.add_row_to_table(conversion)
            
    def save_history(self):
        try:
            with open("history.json", "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self.show_error(f"Failed to save history: {str(e)}")
            
    def load_history(self):
        try:
            with open("history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception:
            return []
            
    def clear_history(self):
        reply = QMessageBox.question(self, "Clear History", 
                                     "Are you sure you want to clear all history?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history = []
            self.history_table.setRowCount(0)
            self.save_history()
            
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        
def main():
    app = QApplication(sys.argv)
    window = CurrencyConverter()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
