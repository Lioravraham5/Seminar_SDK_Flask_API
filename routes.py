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
                    description: The link to the video from firbase storage
                advertiser_link:
                    type: string
                    description: The link to the advertiser's website
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
    if not data or not all(key in data for key in ['video_link', 'advertiser_link']):
        return jsonify({"error": "Missing required fields: 'video_link' and 'advertiser_link'"}), 400

    # check if the video_link is a string
    if not isinstance(data['video_link'], str):
        return jsonify({"error": "The 'video_link' field should be a string"}), 400
    
    # check if the advertiser_link is a string
    if not isinstance(data['advertiser_link'], str):
        return jsonify({"error": "The 'advertiser_link' field should be a string"}), 400

    # Create an ad object
    ad_object = {
        "_id": str(uuid.uuid4()), 
        "video_link": data['video_link'],
        "advertiser_link": data['advertiser_link']
    }

    # Insert the ad object into the database
    try:
        ads_collection = db ['ads']
        ads_collection.insert_one(ad_object)
        return jsonify({"message": "Ad uploaded successfully!", '_id':ad_object["_id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Create a route to fetch an ad
@ads_blue_print.route('/get_ad/<ad_id>', methods=['GET'])
def get_ad(ad_id):
    """
    Get an ad object from the MongoDB database
    ---
    parameters:
      - name: ad_id
        in: path
        required: true
        type: string
        description: The unique identifier of the ad object
    responses:
        200:
            description: The ad object was fetched successfully
        404:
            description: The ad object was not found
        500:
            description: An error occurred while fetching the ad object
    """
    db = MongoConnectionManager.get_db()

    # Check if the database connection was successful
    if db is None:
        return jsonify({"error": "Could not connect to the database"}), 500

    # Fetch the ad object from the database
    # Attempt to find the ad by ID
    try:
        ads_collection = db['ads']
        ad = ads_collection.find_one({"_id": ad_id})

        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        # Convert the MongoDB result to a JSON-serializable format
        ad['_id'] = str(ad['_id'])  # Ensure ID is a string for JSON serialization
        return jsonify(ad), 200

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
