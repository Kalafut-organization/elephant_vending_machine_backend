import csv
import io
import logging
import pytest
import re

from elephants_cse5911.elephant_vending_machine.libraries.experiment_logger import CsvFormatter, create_experiment_logger

class MockLogRecord:
    def __init__(self, message):
        self.message = message

    def getMessage(self):
        return self.message

class MockFileHandler:
    def __init__(self, path):
        self.path = path

    def setLevel(self, log_level):
        self.log_level = log_level

    def setFormatter(self, formatter):
        self.formatter = formatter

formatter = CsvFormatter()

def test_csv_formatter_creation():
    formatter.writer.writerow(['test'])
    assert formatter.output.getvalue() == '"test"\r\n'
    formatter.output.truncate(0)
    formatter.output.seek(0)
    assert isinstance(formatter.output, io.StringIO)

def test_csv_formatter_format_empty():
    message = ''
    formatted_message = formatter.format(MockLogRecord(message))
    LOG_ENTRY_REGEX = r'^\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}\",\"\"$'
    assert re.match(LOG_ENTRY_REGEX, formatted_message)

def test_csv_formatter_format_basic_message():
    message = 'some_text'
    LOG_ENTRY_REGEX = r'^\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}\",\"some_text\"$'
    formatted_message = formatter.format(MockLogRecord(message))
    assert re.match(LOG_ENTRY_REGEX, formatted_message)

def test_csv_formatter_format_message_with_spaces():
    message = 'more complex text'
    LOG_ENTRY_REGEX = r'^\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}\",\"more complex text\"$'
    formatted_message = formatter.format(MockLogRecord(message))
    assert re.match(LOG_ENTRY_REGEX, formatted_message)

def test_csv_formatter_format_message_with_double_quotes():
    message = 'this text "contains a quote"'
    LOG_ENTRY_REGEX = r'^\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}\",\"this text \"\"contains a quote\"\"\"$'
    formatted_message = formatter.format(MockLogRecord(message))
    assert re.match(LOG_ENTRY_REGEX, formatted_message)

def test_create_experiment_logger(monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.libraries.experiment_logger.create_experiment_logger', lambda path: MockFileHandler(path))
    exp_logger = create_experiment_logger('unittest.csv')
    assert exp_logger.level == logging.INFO
    assert exp_logger.name == 'experiment_logger'
