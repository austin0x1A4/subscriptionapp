from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from .forms import UploadFileForm
from .models import Company, IndexPerformance, StockPerformance
import os
import pandas as pd
import json
import datetime
from django.conf import settings

def upload_file(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to upload files.")
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            industry = form.cleaned_data['industry']
            handle_uploaded_file(request.FILES['file'], industry)
            return HttpResponseRedirect('/success/')
    else:
        form = UploadFileForm()
    return render(request, 'stockist/upload.html', {'form': form})

def handle_uploaded_file(f, industry):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    df = pd.read_excel(file_path)
    df = clean_data(df)
    ranked_companies = rank_companies(df)
    save_ranked_companies(ranked_companies, industry)

def clean_data(df):
    df = df.rename(columns=lambda x: x.strip().replace(" ", "_").replace("Company_Name", "company_name"))

    numeric_columns = [
        'Price_Performance_(52_Weeks)',
        'Total_Return_(1_Yr_Annualized)',
        'Beta_(1_Year_Annualized)',
        'Standard_Deviation_(1_Yr_Annualized)'
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=numeric_columns)

    return df

def rank_companies(df):
    df['Score'] = (
        df['Price_Performance_(52_Weeks)'] +
        df['Total_Return_(1_Yr_Annualized)'] +
        (1 - df['Beta_(1_Year_Annualized)']) -
        df['Standard_Deviation_(1_Yr_Annualized)']
    )
    
    df = df.sort_values(by='Score', ascending=False)
    return df[['company_name', 'Score']].to_dict('records')

def save_ranked_companies(ranked_companies, industry):
    industry_dir = os.path.join(settings.MEDIA_ROOT, 'ranked_companies', industry)
    if not os.path.exists(industry_dir):
        os.makedirs(industry_dir)
    
    file_path = os.path.join(industry_dir, f'{industry}_ranked_companies.json')
    with open(file_path, 'w') as f:
        json.dump(ranked_companies, f)

def top_performers(request):
    today = datetime.date.today()
    
    top_indices_performers = IndexPerformance.objects.filter(date=today).order_by('-change')[:10]
    top_stocks_performers = StockPerformance.objects.filter(date=today).order_by('-score')[:10]

    selected_industry = request.GET.get('industry', 'All')

    all_companies = []
    industry_dir = os.path.join(settings.MEDIA_ROOT, 'ranked_companies')
    
    for industry in os.listdir(industry_dir):
        if os.path.isdir(os.path.join(industry_dir, industry)):
            file_path = os.path.join(industry_dir, industry, f'{industry}_ranked_companies.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    companies = json.load(f)
                    for company in companies:
                        company['industry'] = industry
                    all_companies.extend(companies)

    if selected_industry != 'All':
        filtered_companies = [company for company in all_companies if company['industry'] == selected_industry]
    else:
        filtered_companies = sorted(all_companies, key=lambda x: x['Score'], reverse=True)

    context = {
        'companies': filtered_companies,
        'user': request.user,
        'form': UploadFileForm(),
        'top_indices_performers': top_indices_performers,
        'top_stocks_performers': top_stocks_performers,
        'selected_industry': selected_industry
    }

    return render(request, 'stockist/top_performers.html', context)

def get_companies_by_industry(request):
    industry = request.GET.get('industry', 'All')
    industry_dir = os.path.join(settings.MEDIA_ROOT, 'ranked_companies')
    companies = []

    if industry != 'All':
        file_path = os.path.join(industry_dir, industry, f'{industry}_ranked_companies.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                companies = json.load(f)
    else:
        for ind in os.listdir(industry_dir):
            file_path = os.path.join(industry_dir, ind, f'{ind}_ranked_companies.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    ind_companies = json.load(f)
                    for company in ind_companies:
                        company['industry'] = ind
                    companies.extend(ind_companies)

    return JsonResponse(companies, safe=False)

def success(request):
    return render(request, 'stockist/success.html')

def get_top_indices(request):
    today = datetime.date.today()
    top_indices_performers = IndexPerformance.objects.filter(date=today).order_by('-change')[:10]
    indices_data = [{'name': performer.name, 'change': performer.change} for performer in top_indices_performers]
    return JsonResponse({'top_indices_performers': indices_data})

def get_top_stocks(request):
    today = datetime.date.today()
    top_stocks_performers = StockPerformance.objects.filter(date=today).order_by('-score')[:10]
    stocks_data = [{'name': performer.name, 'score': performer.score, 'change': performer.change,
                    'market_cap': performer.market_cap, 'volume': performer.volume} for performer in top_stocks_performers]
    return JsonResponse({'top_stocks_performers': stocks_data})