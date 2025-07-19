import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from .models import Restaurant, Table


@csrf_exempt
@require_POST
def restaurant_detail_by_code(request):
    try:
        payload = json.loads(request.body)
        code = payload.get("code")
        if not code:
            return HttpResponseBadRequest("Missing 'code' in request body")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    restaurant = get_object_or_404(Restaurant, code=code)
    logo_url = request.build_absolute_uri(restaurant.logo.url) if restaurant.logo else None

    return JsonResponse({
        "name": restaurant.name,
        "logo_url": logo_url,
    })


@csrf_exempt
@require_POST
def table_detail_by_code(request):
    """
    Expects JSON: { "code": "<table_code>" }
    Returns JSON: {
      "table_number": 5,
      "restaurant": {
        "name": "Pasta Palace",
        "logo_url": "https://…/media/restaurant_logos/…png"
      }
    }
    """
    # 1. Parse JSON body
    try:
        payload = json.loads(request.body)
        code = payload.get("code")
        if not code:
            return HttpResponseBadRequest("Missing 'code' in request body")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    # 2. Look up the Table (404 if not found)
    table = get_object_or_404(Table, code=code)
    restaurant = table.restaurant

    # 3. Build logo URL (or null)
    logo_url = (
        request.build_absolute_uri(restaurant.logo.url)
        if restaurant.logo
        else None
    )

    # 4. Return the JSON
    return JsonResponse({
        "table_number": table.table_number,
        "restaurant": {
            "name": restaurant.name,
            "logo_url": logo_url,
        }
    })


@csrf_exempt
@require_POST
def staff_login(request):
    """
    POST /restaurants/login/
    Body JSON:
      {
        "username": "...",
        "password": "..."
      }
    Response:
      200 + {"success": True, "restaurant_code": "..."} on OK (sessionid cookie set)
      400 on bad JSON/missing fields
      403 on invalid credentials
    """
    try:
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
    except (json.JSONDecodeError, KeyError):
        return HttpResponseBadRequest("Must provide username and password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return HttpResponseForbidden("Invalid credentials")

    # log the user in (sets session cookie)
    login(request, user)

    # return their restaurant code so the client can redirect
    restaurant_code = user.restaurant.code if user.restaurant else None
    return JsonResponse({"success": True, "restaurant_code": restaurant_code})


@require_GET
def current_user(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"detail": "Authentication required"}, status=401)

    return JsonResponse({
        "username": user.username,
        "restaurant_code": user.restaurant.code if user.restaurant else None,
    })

@csrf_exempt
@require_POST
def staff_logout(request):
    """
    POST /api/restaurants/logout/
    Clears the session cookie.
    """
    logout(request)
    return JsonResponse({"success": True})