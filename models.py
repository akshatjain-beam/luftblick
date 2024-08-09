from flask_sqlalchemy import SQLAlchemy
import bson

# Initialize SQLAlchemy
db = SQLAlchemy()


class CalibrationData(db.Model):
    """
    Represents calibration data for Pandora instruments.

    This model stores information about calibration files, including metadata
    and the file content itself.
    """

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Filename of the calibration file (unique identifier)
    filename = db.Column(db.String, unique=True, nullable=False)

    # Pandora instrument ID
    pandora_id = db.Column(db.String, nullable=False)

    # Spectrometer ID
    spectrometer_id = db.Column(db.String, nullable=False)

    # Version of the calibration file
    version = db.Column(db.Integer, nullable=False)

    # Validity date of the calibration
    validity_date = db.Column(db.String, nullable=False)

    # Binary content of the calibration file
    content = db.Column(db.LargeBinary, nullable=False)

    def set_content(self, json_data):
        """
        Set the content of the calibration file.
        This method converts the input JSON data to BSON format before storing.

        Args:
            json_data (dict): The calibration data in JSON format.
        """
        self.content = bson.dumps(json_data)

    def get_content(self):
        """
        Retrieve the content of the calibration file.
        This method converts the stored BSON data back to JSON format.

        Returns:
            dict: The calibration data in JSON format.
        """
        return bson.loads(self.content)
