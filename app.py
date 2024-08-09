from flask import Flask, request, jsonify, abort
from models import db, CalibrationData
from sqlalchemy.exc import SQLAlchemyError
import os
import re
import bson

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///calibration.db"
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


def parse_filename(filename):
    """
    Parse the calibration filename to extract relevant information.

    Args:
        filename (str): The name of the calibration file.

    Returns:
        tuple: A tuple containing (pandora_id, spectrometer_id, version, validity_date),
               or None if the filename doesn't match the expected pattern.
    """
    match = re.match(r"Pandora(\d+)s(\d+)_CF_v(\d+)d(\d{8})\.txt", filename)
    if not match:
        return None
    return match.groups()


def extract_file_details(file_content):
    """
    Extract key-value pairs from the file content.

    Args:
        file_content (str): The content of the calibration file.

    Returns:
        dict: A dictionary containing extracted key-value pairs.
    """
    data = {}
    for line in file_content.splitlines():
        if "->" in line:
            key, value = line.split("->", 1)
            data[key.strip()] = value.strip()
    return data


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({"error": "Bad Request", "message": str(error.description)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({"error": "Not Found", "message": str(error.description)}), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    return (
        jsonify({"error": "Internal Server Error", "message": str(error.description)}),
        500,
    )


@app.route("/api/process_files", methods=["POST"])
def process_files():
    """
    Process calibration files in the specified directory and store their data in the database.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
    """
    directory = "./calibration_files"
    added, skipped, errors = 0, 0, 0
    error_messages = []

    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist")

        # Iterate through files in the directory
        for filename in os.listdir(directory):
            if not filename.endswith(".txt"):
                continue

            try:
                # Parse filename and extract details
                parsed = parse_filename(filename)
                if not parsed:
                    continue

                pandora_id, spectrometer_id, version, validity_date = parsed
                file_path = os.path.join(directory, filename)

                # Read file content
                with open(file_path, "r") as file:
                    content = file.read()

                file_details = extract_file_details(content)

                # Check if file already exists in database
                existing_entry = CalibrationData.query.filter_by(
                    filename=filename
                ).first()

                if existing_entry:
                    skipped += 1
                else:
                    # Create new database entry
                    new_data = CalibrationData(
                        filename=filename,
                        pandora_id=pandora_id,
                        spectrometer_id=spectrometer_id,
                        version=int(version),
                        validity_date=validity_date,
                    )
                    new_data.set_content(file_details)
                    db.session.add(new_data)
                    added += 1

            except Exception as e:
                errors += 1
                error_messages.append(f"Error processing file {filename}: {str(e)}")
                continue

        # Commit changes to database
        db.session.commit()
        return (
            jsonify(
                {
                    "added": added,
                    "skipped": skipped,
                    "errors": errors,
                    "error_messages": error_messages,
                }
            ),
            200,
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"error": "An unexpected error occurred", "details": str(e)}),
            500,
        )


@app.route("/api/query", methods=["GET"])
def query_calibration_data():
    """
    Query calibration data based on provided keys.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
    """
    try:
        keys = request.json
        if not keys or not isinstance(keys, list):
            abort(400, description="Invalid or missing keys in request body")

        query = CalibrationData.query
        results = query.all()

        response = []
        for row in results:
            content = row.get_content()
            matched_content = {key: content.get(key) for key in keys if key in content}
            if matched_content:
                response.append(
                    {"filename": row.filename, "matched_content": matched_content}
                )

        return jsonify(response), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return (
            jsonify({"error": "An unexpected error occurred", "details": str(e)}),
            500,
        )


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Perform a health check on the application.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
    """
    try:
        # Perform a simple database query to check DB health
        CalibrationData.query.limit(1).all()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "details": str(e)}), 500


@app.route("/api/get_content", methods=["GET"])
def get_content():
    """
    Retrieve content for a specific calibration file.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
    """
    try:
        filename = request.args.get("filename")

        if not filename:
            abort(400, description="Filename parameter is required")

        entry = CalibrationData.query.filter_by(filename=filename).first()

        if not entry:
            abort(
                404, description=f"No calibration data found for filename: {filename}"
            )

        content = entry.get_content()
        return (
            jsonify(
                {
                    "filename": entry.filename,
                    "pandora_id": entry.pandora_id,
                    "spectrometer_id": entry.spectrometer_id,
                    "version": entry.version,
                    "validity_date": entry.validity_date,
                    "content": content,
                }
            ),
            200,
        )

    except bson.errors.BSONDecodeError:
        abort(500, description="Error decoding content data")
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return (
            jsonify({"error": "An unexpected error occurred", "details": str(e)}),
            500,
        )


@app.route("/api/calibration_files", methods=["GET"])
def get_calibration_file_info():
    """
    Retrieve information about all calibration files.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
    """
    try:
        files = CalibrationData.query.with_entities(
            CalibrationData.filename,
            CalibrationData.pandora_id,
        ).all()
        file_info = [
            {
                "filename": file.filename,
                "pandora_id": file.pandora_id,
            }
            for file in files
        ]
        return jsonify({"calibration_files": file_info, "count": len(file_info)}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return (
            jsonify({"error": "An unexpected error occurred", "details": str(e)}),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
