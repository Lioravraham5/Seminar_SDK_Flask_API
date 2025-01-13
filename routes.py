from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import uuid

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
    required_fields = ['video_link', 'advertiser_link', 'advertiser_icon']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    #if not data or not all(key in data for key in required_fields):
    #    return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

    # Validate fields are strings
    for field in required_fields:
        if not isinstance(data[field], str):
            return jsonify({"error": f"The '{field}' field should be a string"}), 400

    # Create an ad object
    ad_object = {
        "_id": str(uuid.uuid4()), 
        "video_link": data['video_link'],
        "advertiser_link": data['advertiser_link'],
        "advertiser_icon": data['advertiser_icon']
    }

    # Insert the ad object into the database
    try:
        ads_collection = db ['ads']
        ads_collection.insert_one(ad_object)
        return jsonify({"message": "Ad uploaded successfully!", '_id':ad_object["_id"]}), 201
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


# 3. Create a route to update advertiser_link
@ads_blue_print.route('/update_advertiser_link/<ad_id>', methods=['PUT'])
def update_advertiser_link(ad_id):
    """
    Update the advertiser_link for an existing ad
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
                advertiser_link:
                    type: string
                    description: The new advertiser link
    responses:
        200:
            description: Advertiser link updated successfully
        404:
            description: Ad not found
        400:
            description: Invalid date format
        500:
            description: An error occurred while updating the advertiser link
    """
    data = request.json

    # Validate the input
    if not data or 'advertiser_link' not in data or not isinstance(data['advertiser_link'], str):
        return jsonify({"error": "Invalid input. 'advertiser_link' must be a string"}), 400

    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Attempt to update the advertiser_link
    try:
        ads_collection = db['ads']
        result = ads_collection.update_one(
            {"_id": ad_id},
            {"$set": {"advertiser_link": data['advertiser_link']}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Ad not found"}), 404

        return jsonify({"message": "Advertiser link updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#4. Create a route to update advertiser_icon
@ads_blue_print.route('/update_advertiser_icon/<ad_id>', methods=['PUT'])
def update_advertiser_icon(ad_id):
    """
    Update the advertiser_icon for an existing ad
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
    responses:
        200:
            description: Advertiser icon updated successfully
        404:
            description: Ad not found
        400:
            description: Invalid input
        500:
            description: An error occurred while updating the advertiser icon
    """
    data = request.json

    # Validate the input
    if not data or 'advertiser_icon' not in data or not isinstance(data['advertiser_icon'], str):
        return jsonify({"error": "Invalid input. 'advertiser_icon' must be a string"}), 400

    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Attempt to update the advertiser_icon
    try:
        ads_collection = db['ads']
        result = ads_collection.update_one(
            {"_id": ad_id},
            {"$set": {"advertiser_icon": data['advertiser_icon']}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Ad not found"}), 404

        return jsonify({"message": "Advertiser icon updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
      
# 5. Create a route to fetch all ads
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
    
# 6. Create a route to delete an ad
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
    
# 7. Create a route to delete all ads
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
