# Ad Management API
This is an Ad Management API built using Flask and MongoDB that allows you to upload, update, delete, and fetch  Video ads. 
It provides various endpoints for interacting with advertisements in the application and in the database.

## Overview
This API is designed to handle advertisements in a system. 
It allows the management of Video ads by uploading new ads, updating existing ones, fetching random ads, and deleting ads, among other operations. 
The API uses MongoDB for storing ad data and provides JSON-based responses.

## Features
- **Upload ads:** Add new ad entries to the database.
- **Update ads:** Modify the fields of an existing ad.
- **Delete ads:** Remove individual ads or all ads at once.
- **Fetch ads:** Retrieve a random ad or fetch all ads.
- **Create packages:** Create a package object for storing events related to the app's advertisements.

## Endpoints
### 1. Upload Ad
`POST /upload_ad`
- **Description:** Uploads a new ad object to the `ads` collection MongoDB database.
- **Parameters:** 
  - **Body:** video_link, advertiser_link, advertiser_icon, price_per_click, price_per_impression, number_of_clicks, number_of_impressions.
- **Response:** Returns a success message with the ad ID if the ad is uploaded, or an error message if any required fields are missing or there is an issue with the database.
```
{
  "video_link": "string",
  "advertiser_link": "string",
  "advertiser_icon": "string",
  "price_per_click": "number",
  "price_per_impression": "number",
  "number_of_clicks": "integer",
  "number_of_impressions": "integer"
}
```
### 2. Get Random Ad
`GET /get_ad`
- **Description:** Fetches a random ad from the MongoDB database.
- **Parameters:** none
- **Response:**
  - 200: Random ad object returned  
  - 404: No ads available
  - 500: Internal server error.

### 3. Update Ad
`PUT /update_ad/<ad_id>`
- **Description:** Updates one or more fields of an existing ad object.
- **Parameters:**
  - **ad_id (in path):** The ID of the ad to update (required).
  - **Body:** A JSON object containing the fields to update. At least one field must be provided.
- **Response:**
  - 200: Ad updated successfully.
  - 404: Ad not found.
  - 400: Invalid input or missing fields.
  - 500: An error occurred while updating the ad.

### 4. Get All Ads
`GET /get_all_ads`
- **Description:** Fetches all advertisement objects from the MongoDB database.
- **Parameters:** none
- **Response:**
  - 200: The list of ad objects was fetched successfully.
  - 500: An error occurred while fetching the ad objects

### 5. Delete Ad
`DELETE /delete_ad/<ad_id>`
- **Description:** Deletes an advertisement object from the MongoDB database by its ID.
- **Parameters:**
  - **ad_id (in path):** The ID of the ad object to delete (required).
- **Response:**
  - 200: Ad deleted successfully.
  - 404: Ad not found.
  - 500: An error occurred while deleting the ad.

### 6. Delete All Ads
`DELETE /delete_all_ads`
- **Description:** Deletes all advertisement objects from the MongoDB database.
- **Parameters:** none
- **Response:**
  - 200: All ads deleted successfully.
  - 404: No ads to delete (if the collection is empty).
  - 500: An error occurred while deleting the ads.

### 7. Create Package
`POST /create_package/<package_name>`
- **Description:** Creates a new package object for an app with an empty ads_events array in the `packages` collection in the MongoDB database.
  If the package already exists, it returns a success message without creating a new package.
- **Parameters:**
  - **package_name (in path):** The unique package name of the aoolication.
- **Response:**
  - 200: Package created successfully or already exists.
  - 500: An error occurred while creating the package.
- Example of a package object:
```
{
  "_id": "com.example.myapp",
  "ads_events": []
}

```

### 8. Add Ad Event to Package
`POST /add_ad_event/<package_name>`
- **Description:** Adds an ad event to a specified package, where each event contains information about the ad: `ad_id`, whether it was clicked (`is_clicked`), and the event timestamp (`date_time`).
   The timestamp will be automatically calculated at the time the event is added to the package.
- **Parameters:**
  - **package_name (in path):** The package name of the app to which the ad event will be added.
  - **body (in body):** The ad event data that contains the following properties:
    1. <ins>ad_id (string):</ins> The unique ID of the ad.
    2. <ins>is_clicked (boolean):</ins> Whether the ad was clicked.
- **Response:**
  - 200: Ad event added successfully.
  - 404: Package or ad not found.
  - 400: Invalid input.
  - 500: An error occurred while adding the ad event.
- Example of an ad_event object added to the `ads_events` array in the package:
```
{
  "ad_id": "ad_12345",
  "date_time": "2025-01-24T12:00:00",  // Timestamp generated at the time of event creation
  "is_clicked": true
}

```

### 9. Get Ad Analytics
`GET /ad_analytics/<ad_id>`
- **Description:** Fetches analytics for a specific ad, including the number of clicks, impressions, revenue generated, and the ratio of clicks to impressions. This helps in understanding the performance of the ad.
- **Parameters:**
  - **ad_id (in path):** The unique ID of the ad for which analytics are to be fetched.
- **Response:**
  - 200: The analytics data for the specified ad is returned successfully.
  - 404: The ad with the provided ad_id is not found.
  - 500: An error occurred while fetching the analytics.
- Example Response:
```
{
  "ad_id": "ad_12345",
  "number_of_clicks": 150,
  "number_of_impressions": 5000,
  "total_revenue": 350.50,
  "click_impression_ratio": 0.03
}
```

### 10. Get All Ads Analytics
`GET /all_ad_analytics`
- **Description:** Fetches analytics for all ads in the database, including the number of clicks, impressions, revenue generated, and the ratio of clicks to impressions for each ad.
  This route provides a complete overview of the ad performance across all ads.
- **Response:**
  - 200: A list of analytics data for all ads is returned successfully.
  - 500: An error occurred while fetching the analytics



