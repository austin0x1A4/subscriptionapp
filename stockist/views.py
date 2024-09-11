from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from .forms import UploadFileForm
import json
from django.conf import settings
import csv
import yfinance as yf
from .utils import get_stock_data, validate_stock_symbol
import os
import pandas as pd
from django.core.paginator import Paginator
from django.urls import reverse


def upload_file(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to upload files.")
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            industry = form.cleaned_data['industry']
            handle_uploaded_file(request.FILES['file'], industry)
            return HttpResponseRedirect(f"{reverse('upload_file')}?success=1")
    else:
        form = UploadFileForm()

    # Check if there's a success parameter in the URL to show a message
    success_message = request.GET.get('success')
    return render(request, 'stockist/upload.html', {'form': form, 'success_message': success_message})



def handle_uploaded_file(f, industry):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, f.name)
    
    # Save the uploaded file temporarily
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)
    df = clean_data(df)

    # Add the selected 'Industry' as a new column
    df['Industry'] = industry

    # Define the path to the master CSV file
    master_file_path = os.path.join(upload_dir, 'master_stock_data.csv')

    # If the master file exists, append to it; otherwise, create a new one
    if os.path.exists(master_file_path):
        df.to_csv(master_file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(master_file_path, index=False)

    

def clean_data(df):
    print("Columns before renaming:", df.columns)

    # Rename columns
    df = df.rename(columns={
        'Company Name': 'company_name',
        'Symbol': 'Symbol'
    })

    print("Columns after renaming:", df.columns)

    # Retain only the 'Symbol' and 'company_name' columns
    try:
        df = df[['Symbol', 'company_name']]
    except KeyError as e:
        print(f"KeyError: {e}")
        raise

    # Drop rows with missing values in 'Symbol' and 'company_name' columns
    df = df.dropna(subset=['Symbol', 'company_name'])

    return df

def stock_dashboard(request):
    # Path to the saved JSON file
    json_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'stock_data.json')
    
    try:
        with open(json_path, 'r') as json_file:
            stock_data = json.load(json_file)
    except FileNotFoundError:
        return render(request, 'stockist/error.html', {'errors': ['Stock data not found. Please run the management command to generate the data.']})
    except Exception as e:
        return render(request, 'stockist/error.html', {'errors': [str(e)]})

    all_stocks = stock_data.get('all_stocks', [])
    most_active = stock_data.get('most_active', [])
    top_gainers = stock_data.get('top_gainers', [])
    top_losers = stock_data.get('top_losers', [])

    df = pd.DataFrame(all_stocks)
    df['change_percent'] = pd.to_numeric(df['change_percent'], errors='coerce')
    df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce')

    industries = sorted(set(df['industry'].dropna().unique()))

    selected_industry = request.GET.get('industry', 'All')
    sort_by = request.GET.get('sort_by', 'change_percent')

    if selected_industry != 'All':
        df = df[df['industry'] == selected_industry]

    if sort_by == 'market_cap':
        df = df.sort_values(by='market_cap', ascending=False)
    elif sort_by == 'volume':
        df = df.sort_values(by='volume', ascending=False)
    elif sort_by == 'change_percent':
        df = df.sort_values(by='change_percent', ascending=False)
    else:
        df = df.sort_values(by='current_price', ascending=False)
    
    # Convert the filtered data back to a list of dictionaries
    all_stocks = df.to_dict('records')

    # Paginate the data (20 stocks per page)
    paginator = Paginator(all_stocks, 20)  # Show 20 stocks per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page of stocks

    context = {
        'page_obj': page_obj,  # Pass the page object to the template
        'all_stocks': df.to_dict('records'),
        'industries': industries,
        'selected_industry': selected_industry,
        'selected_sort': sort_by,
        'most_active': most_active,
        'top_gainers': top_gainers,
        'top_losers': top_losers,
    }

    return render(request, 'stockist/stock_dashboard.html', context)




def success(request):
    return render(request, 'stockist/success.html')

