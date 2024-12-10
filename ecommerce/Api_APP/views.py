from django.shortcuts import render
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests
import os
 
# Create your views here.
# Load environment variables
load_dotenv()
# Access environment variables
STEADFAST_API_KEY = os.getenv("STEADFAST_API_KEY")
STEADFAST_SECRET_KEY = os.getenv("STEADFAST_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")


@csrf_exempt  # Disabling CSRF check for the view (needed for external API calls)
def bulk_create_order(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request body
            order_data = json.loads(request.body)

            # Set headers, including Api-Key and Secret-Key for authentication
            headers = {
                "Api-Key": STEADFAST_API_KEY,  # API Key as 'Api-Key'
                "Secret-Key": STEADFAST_SECRET_KEY,  # Secret Key as 'Secret-Key'
                "Content-Type": "application/json"
            }

            # Make the POST request to the external API endpoint
            response = requests.post(f"{BASE_URL}/create_order/bulk-order", json=order_data, headers=headers)

            # Check if the request was successful
            response.raise_for_status()

            # Return the response from the API as JSON
            return JsonResponse(response.json(), safe=False)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)