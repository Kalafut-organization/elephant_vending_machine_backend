"""Experiment logging utilities.

This module contains functionality required to create a custom logger
which writes messages and the corresponding UTC timestamp to csv files.
"""

import csv
import io
import logging
from logging import FileHandler
from datetime import datetime

class CsvFormatter(logging.Formatter):
    """Instances of CsvFormatter are used to convert a LogRecord instance to text.

    CsvFormatter instances convert LogRecord instances to a properly formatted
    line in a csv file.
    """

    def __init__(self):
        """Initialize the formatter with csv writer and output buffer.

        Initialize the output buffer for csv writer to write to and a
        csv writer to create properly formatted strings for writing to csv
        files. Formatting includes comma separation of values and quotes
        surrounding all values.
        """

        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    def format(self, record):
        """ Format the specified record as text formatted for csv file.

        The specified record is formatted as csv compatible text containing
        the current UTC timestamp and the record message.

        Parameters:
            record (LogRecord): The log record to be formatted

        Returns:
            str: a string formatted as an entry for a csv file containing
            current UTC timestamp and record text
        """

        self.writer.writerow([datetime.utcnow(), record.getMessage()])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

def create_experiment_logger(file_name):
    """ Create experiment logger to log record to csv file.

    The specified record is formatted as csv compatible text containing
    the current UTC timestamp and the record message.

    Parameters:
        file_name (str): The name of the file to which the logs will be written

    Returns:
        Logger: experiment_logger instance configured to write INFO level logs
        to log directory
    """

    log_level = logging.INFO
    experiment_log_path = 'elephant_vending_machine/static/log/'
    logger = logging.getLogger('experiment_logger')
    logger.setLevel(log_level)
    experiment_log_file_handler = FileHandler(experiment_log_path + file_name)
    experiment_log_file_handler.setLevel(log_level)
    experiment_log_file_handler.setFormatter(CsvFormatter())
    logger.addHandler(experiment_log_file_handler)
    return logger
