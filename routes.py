from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import uuid
from datetime import datetime

# Initialize Blueprint
ads_blue_print = Blueprint('ads', __name__)

# Reference the ads collection
db = MongoConnectionManager.get_db()
ads_collection = db['ads']  # Collection name

# 1. Create a route to upload an ad
@ads_blue_print.route('/upload_ad', methods=['POST'])
def upload_ad():
    """
    Upload an ad object to the MongoDB database
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                video_link:
                    type: string
                    description: The link to the video ad
                advertiser_link:
                    type: string
                    description: The link to the advertiser's website
                advertiser_icon:
                    type: string
                    description: The URL to the advertiser's icon image
                price_per_click:
                    type: number
                    description: The price per click for the ad
                price_per_impression:
                    type: number
                    description: The price per impression for the ad
                number_of_clicks:
                    type: integer
                    description: The number of clicks on the ad (optional)
                number_of_impressions:
                    type: integer
                    description: The number of times the ad has been presented in the app (optional)
    responses:
        200:
            description: Ad uploaded successfully
        400:
            description: The request was invalid
        500:
            description: An error occurred while uploading the ad
    """
    data = request.json

    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500
    
    # Check if the required fields are present
    required_fields = ['video_link', 'advertiser_link', 'advertiser_icon', 'price_per_click', 'price_per_impression']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    # Validate 'video_link', 'advertiser_link', and 'advertiser_icon' as strings
    for field in ['video_link', 'advertiser_link', 'advertiser_icon']:
        if not isinstance(data[field], str):
            return jsonify({"error": f"The '{field}' field should be a string"}), 400
    
    # Validate 'price_per_click' and 'price_per_impression' as numbers
    for field in ['price_per_click', 'price_per_impression']:
        if not isinstance(data[field], (int, float)):
            return jsonify({"error": f"The '{field}' field should be a number"}), 400
    
    # Validate 'number_of_clicks' and 'number_of_impressions' as integers (defaults to 0)
    for field in ['number_of_clicks', 'number_of_impressions']:
        if field in data and not isinstance(data[field], int):
            return jsonify({"error": f"The '{field}' field should be an integer"}), 400

    # Create an ad object with the new fields
    ad_object = {
        "_id": str(uuid.uuid4()), 
        "video_link": data['video_link'],
        "advertiser_link": data['advertiser_link'],
        "advertiser_icon": data['advertiser_icon'],
        "number_of_clicks": data.get('number_of_clicks', 0),  # Default to 0 if not provided
        "number_of_impressions": data.get('number_of_impressions', 0),  # Default to 0 if not provided
        "price_per_click": data['price_per_click'],
        "price_per_impression": data['price_per_impression']
    }

    # Insert the ad object into the database
    try:
        ads_collection = db['ads']
        ads_collection.insert_one(ad_object)
        return jsonify({"message": "Ad uploaded successfully!", '_id': ad_object["_id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 2. Create a route to fetch a random ad
@ads_blue_print.route('/get_ad', methods=['GET'])
def get_random_ad():
    """
    Get a random ad object from the MongoDB database
    ---
    responses:
        200:
            description: A random ad object was fetched successfully
        404:
            description: No ads available in the database
        500:
            description: An error occurred while fetching the ad object
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    try:
        ads_collection = db['ads']
        # Use MongoDB's $sample aggregation stage to fetch a random document
        random_ad_cursor = ads_collection.aggregate([{"$sample": {"size": 1}}])
        random_ad = next(random_ad_cursor, None)  # Get the first (and only) result

        if not random_ad:
            return jsonify({"error": "No ads available"}), 404

        # Convert the MongoDB result to a JSON-serializable format
        random_ad['_id'] = str(random_ad['_id'])  # Ensure ID is a string for JSON serialization
        return jsonify(random_ad), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Create a route to update one or more fields in an ad object
@ads_blue_print.route('/update_ad/<ad_id>', methods=['PUT'])
def update_ad(ad_id):
    """
    Update one or more fields of an existing ad object
    ---
    parameters:
      - name: ad_id
        in: path
        required: true
        type: string
        description: The ID of the ad to update
      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                advertiser_icon:
                    type: string
                    description: The new advertiser icon URL
                advertiser_link:
                    type: string
                    description: The new advertiser link
                number_of_clicks:
                    type: integer
                    description: The number of clicks for the ad
                number_of_impressions:
                    type: integer
                    description: The number of impressions for the ad
                price_per_click:
                    type: number
                    description: The price per click for the ad
                price_per_impression:
                    type: number
                    description: The price per impression for the ad
                video_link:
                    type: string
                    description: The new video link for the ad
    responses:
        200:
            description: Ad updated successfully
        404:
            description: Ad not found
        400:
            description: Invalid input
        500:
            description: An error occurred while updating the ad
    """
    data = request.json

    # Define the expected field types for validation
    expected_field_types = {
        'advertiser_icon': str,
        'advertiser_link': str,
        'number_of_clicks': int,
        'number_of_impressions': int,
        'price_per_click': (int, float),
        'price_per_impression': (int, float),
        'video_link': str
    }

    # Validate the input
    if not data:
        return jsonify({"error": "Request body is empty. Please provide data to update."}), 400

    update_data = {}
    errors = []

    for key, value in data.items():
        if key not in expected_field_types:
            errors.append(f"Invalid field '{key}' provided.")
        elif not isinstance(value, expected_field_types[key]):
            expected_type_name = (
                "integer or float" if isinstance(expected_field_types[key], tuple) 
                else expected_field_types[key].__name__
            )
            errors.append(f"Field '{key}' must be of type {expected_type_name}.")
        else:
            # Add valid fields to the update_data
            update_data[key] = value

    if errors:
        return jsonify({"error": "Invalid input", "details": errors}), 400

    if not update_data:
        return jsonify({"error": "No valid fields to update. Please provide at least one valid field."}), 400

    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Attempt to update the ad
    try:
        ads_collection = db['ads']
        result = ads_collection.update_one(
            {"_id": ad_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Ad not found"}), 404

        return jsonify({"message": "Ad updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
      
# 4. Create a route to fetch all ads
@ads_blue_print.route('/get_all_ads', methods=['GET'])
def get_all_ads():
    """
    Get all ad objects from the MongoDB database
    ---
    responses:
        200:
            description: The list of ad objects was fetched successfully
        500:
            description: An error occurred while fetching the ad objects
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Fetch all ad objects from the database
    try:
        ads_collection = db['ads']
        ads = list(ads_collection.find())  # Convert cursor to list

        # Convert _id to string for all ad objects
        for ad in ads:
            ad['_id'] = str(ad['_id'])  # Ensure ID is a string for JSON serialization

        return jsonify(ads), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 5. Create a route to delete an ad
@ads_blue_print.route('/delete_ad/<ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    """
    Delete an ad object from the MongoDB database by ID
    ---
    parameters:
      - name: ad_id
        in: path
        required: true
        type: string
        description: The ID of the ad object to delete
    responses:
        200:
            description: Ad deleted successfully
        404:
            description: Ad not found
        500:
            description: An error occurred while deleting the ad
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Attempt to delete the ad object by ID
    try:
        ads_collection = db['ads']
        result = ads_collection.delete_one({"_id": ad_id})

        if result.deleted_count == 0:
            return jsonify({"error": "Ad not found"}), 404

        return jsonify({"message": "Ad deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 6. Create a route to delete all ads
@ads_blue_print.route('/delete_all_ads', methods=['DELETE'])
def delete_all_ads():
    """
    Delete all ad objects from the MongoDB database
    ---
    responses:
        200:
            description: All ads deleted successfully
        500:
            description: An error occurred while deleting all ads
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Attempt to delete all ad objects
    try:
        ads_collection = db['ads']
        result = ads_collection.delete_many({})  # Delete all documents in the collection

        if result.deleted_count == 0:
            return jsonify({"message": "No ads to delete"}), 404

        return jsonify({"message": "All ads deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#7. # Create a route to create a package object
@ads_blue_print.route('/create_package/<package_name>', methods=['POST'])
def create_package(package_name):
    """
    Create a new package object for an app with an empty ads_events array.
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
        description: The unique package name for the app.
    responses:
        200:
            description: Package created successfully or already exists.
        500:
            description: An error occurred while creating the package.
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    try:
        packages_collection = db['packages']

        # Check if the package already exists
        existing_package = packages_collection.find_one({"_id": package_name})
        if existing_package:
            # Return success if the package already exists
            return jsonify({"message": f"Package '{package_name}' already exists."}), 200

        # Create the package object
        package_object = {
            "_id": package_name,
            "ads_events": []  # Empty array for ads_events
        }

        # Insert the package object into the database
        packages_collection.insert_one(package_object)
        return jsonify({"message": f"Package '{package_name}' created successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 8. Create a route to add an ad_event to a package
@ads_blue_print.route('/add_ad_event/<package_name>', methods=['POST'])
def add_ad_event(package_name):
    """
    Add an ad_event to the specified package
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
        description: The package name of the app
      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                ad_id:
                    type: string
                    description: The unique ID of the ad
                is_clicked:
                    type: boolean
                    description: Indicates whether the ad was clicked
    responses:
        200:
            description: Ad event added successfully
        404:
            description: Package or ad not found
        400:
            description: Invalid input
        500:
            description: An error occurred while adding the ad event
    """
    data = request.json

    # Check if the required fields are present
    required_fields = ['ad_id', 'is_clicked']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Validate 'ad_id' as a string
    if not isinstance(data['ad_id'], str):
        return jsonify({"error": "'ad_id' must be a string"}), 400

    # Validate 'is_clicked' as a boolean
    if not isinstance(data['is_clicked'], bool):
        return jsonify({"error": "'is_clicked' must be a boolean"}), 400

    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Calculate the current date_time using datetime.now()
    date_time = datetime.now().isoformat()

    try:
        packages_collection = db['packages']
        ads_collection = db['ads']

        # Find the package by package_name
        package = packages_collection.find_one({"_id": package_name})
        if not package:
            return jsonify({"error": "Package not found"}), 404

        # Find the ad by ad_id
        ad = ads_collection.find_one({"_id": data['ad_id']})
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        # Create the ad_event object
        ad_event = {
            "ad_id": data['ad_id'],
            "date_time": date_time,
            "is_clicked": data['is_clicked']
        }

        # Add the ad_event to the ads_events array
        packages_collection.update_one(
            {"_id": package_name},
            {"$push": {"ads_events": ad_event}}
        )

        # Increment the number_of_impressions in the ads collection
        ads_collection.update_one(
            {"_id": data['ad_id']},
            {"$inc": {"number_of_impressions": 1}}
        )

        # Increment the number_of_clicks in the ads collection if is_clicked is true
        if data['is_clicked']:
            ads_collection.update_one(
                {"_id": data['ad_id']},
                {"$inc": {"number_of_clicks": 1}}
            )

        return jsonify({"message": "Ad event added successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 9. Create a route to fetch analytics for a specific ad
@ads_blue_print.route('/ad_analytics/<ad_id>', methods=['GET'])
def get_ad_analytics(ad_id):
    """
    Get analytics for a specific ad, including the number of clicks, impressions, revenue generated, 
    and the ratio of clicks to impressions.
    ---
    parameters:
        - name: ad_id
          in: path
          type: string
          required: true
          description: The ID of the ad
    responses:
        200:
            description: Analytics data for the specified ad
        404:
            description: Ad not found
        500:
            description: An error occurred while fetching the ad analytics
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    try:
        ads_collection = db['ads']
        
        # Fetch the ad with the given ID (querying by 'ad_id' directly)
        ad = ads_collection.find_one({"_id": ad_id})

        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        # Ensure necessary fields are present
        number_of_clicks = ad.get('number_of_clicks', 0)
        number_of_impressions = ad.get('number_of_impressions', 0)
        price_per_click = ad.get('price_per_click', 0.0)
        price_per_impression = ad.get('price_per_impression', 0.0)

        # Calculate the total revenue
        total_revenue = (price_per_click * number_of_clicks) + (price_per_impression * number_of_impressions)

        # Calculate the ratio of clicks to impressions (handle division by zero)
        if number_of_impressions > 0:
            click_impression_ratio = number_of_clicks / number_of_impressions
        else:
            click_impression_ratio = 0  # Avoid division by zero

        # Prepare the response
        response = {
            "ad_id": ad_id,
            "number_of_clicks": number_of_clicks,
            "number_of_impressions": number_of_impressions,
            "total_revenue": round(total_revenue, 2),  # Rounded to 2 decimal places
            "click_impression_ratio": round(click_impression_ratio, 4)  # Rounded to 4 decimal places
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 10. Create a route to fetch analytics for all ads
@ads_blue_print.route('/all_ad_analytics', methods=['GET'])
def get_all_ad_analytics():
    """
    Get analytics for all ads, including the number of clicks, impressions, revenue generated, 
    and the ratio of clicks to impressions for each ad.
    ---
    responses:
        200:
            description: A list of analytics data for all ads
        500:
            description: An error occurred while fetching the ads analytics
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    try:
        ads_collection = db['ads']
        
        # Fetch all ads from the collection
        ads = ads_collection.find()

        # Prepare the list to store analytics for all ads
        all_ads_analytics = []

        # Iterate over each ad and calculate analytics
        for ad in ads:
            ad_id = str(ad["_id"])  # Get the ad_id (using _id field in MongoDB)
            number_of_clicks = ad.get('number_of_clicks', 0)
            number_of_impressions = ad.get('number_of_impressions', 0)
            price_per_click = ad.get('price_per_click', 0.0)
            price_per_impression = ad.get('price_per_impression', 0.0)

            # Calculate the total revenue
            total_revenue = (price_per_click * number_of_clicks) + (price_per_impression * number_of_impressions)

            # Calculate the ratio of clicks to impressions (handle division by zero)
            if number_of_impressions > 0:
                click_impression_ratio = number_of_clicks / number_of_impressions
            else:
                click_impression_ratio = 0  # Avoid division by zero

            # Prepare the analytics data for this ad
            ad_analytics = {
                "ad_id": ad_id,
                "number_of_clicks": number_of_clicks,
                "number_of_impressions": number_of_impressions,
                "total_revenue": round(total_revenue, 2),
                "click_impression_ratio": round(click_impression_ratio, 4)
            }

            all_ads_analytics.append(ad_analytics)

        # Return the list of all ads analytics
        return jsonify(all_ads_analytics), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500