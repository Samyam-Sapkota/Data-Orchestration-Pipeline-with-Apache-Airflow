import pandas as pd
import re
import numpy as np

def clean_laptop_data(df):
    """
    Clean and transform scraped laptop data
    """
    # Read the data as df
    # df = data.copy()
    
    print(f"Original shape: {df.shape}")
    print(f"Original columns: {df.columns.tolist()}\n")
    
    # 1. Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    # 2. Handle missing/zero ratings
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['count'] = pd.to_numeric(df['count'].str.split(" ").str[0], errors='coerce')
    df['total_ratings'] = pd.to_numeric(df['total_ratings'], errors='coerce')
    
    # 3. Clean price columns - remove commas and convert to numeric
    df['price_before_discount'] = pd.to_numeric(df['price_before_discount'], errors='coerce')
    df['price_after_discount'] = pd.to_numeric(df['price_after_discount'], errors='coerce')
    df['percent_discount'] = pd.to_numeric(df['percent_discount'], errors='coerce')
    
    # 4. Calculate actual discount if prices exist
    df['actual_discount_amount'] = df['price_before_discount'] - df['price_after_discount']
    
    # 5. Extract brand from title
    def extract_brand(title):
        if pd.isna(title):
            return None
        brands = ['Acer', 'Dell', 'HP', 'Lenovo', 'Asus', 'ASUS', 'Apple', 'xLab', 'Great Asia', 'CHUWI','MSI','Microsoft']
        for brand in brands:
            if brand.lower() in title.lower():
                return brand
        return 'Unknown'
    
    df['brand'] = df['title'].apply(extract_brand)
    
    # 6. Extract processor info
    def extract_processor(title):
        if pd.isna(title):
            return {'processor_type': None, 'processor_gen': None}
        
        title_lower = title.lower()
        
        # Intel processors
        intel_match = re.search(r'(core\s*)?i(\d)\s*[-\s]?\s*(\d+th\s*gen)?', title_lower)
        if intel_match:
            proc_type = f"Intel Core i{intel_match.group(2)}"
            gen_match = re.search(r'(\d+)th\s*gen', title_lower)
            gen = gen_match.group(1) if gen_match else None
            return {'processor_type': proc_type, 'processor_gen': gen}
        
        # AMD Ryzen
        ryzen_match = re.search(r'ryzen\s*(\d|[579])\s*(\d{4}[a-z]*)?', title_lower)
        if ryzen_match:
            proc_type = f"AMD Ryzen {ryzen_match.group(1)}"
            return {'processor_type': proc_type, 'processor_gen': None}
        
        # Celeron
        if 'celeron' in title_lower:
            return {'processor_type': 'Intel Celeron', 'processor_gen': None}
        
        # Apple M series
        m_match = re.search(r'm(\d)', title_lower)
        if m_match:
            return {'processor_type': f"Apple M{m_match.group(1)}", 'processor_gen': None}
        
        return {'processor_type': 'Unknown', 'processor_gen': None}
    
    processor_info = df['title'].apply(extract_processor)
    df['processor_type'] = [x['processor_type'] for x in processor_info]
    df['processor_gen'] = [x['processor_gen'] for x in processor_info]
    
    # 7. Extract RAM size
    def extract_ram(title):
        if pd.isna(title):
            return None
        match = re.search(r'(\d+)\s*gb\s*ram', title.lower())
        return int(match.group(1)) if match else None
    
    df['ram_gb'] = df['title'].apply(extract_ram)
    
    # 8. Extract storage size and type
    def extract_storage(title):
        if pd.isna(title):
            return {'storage_size': None, 'storage_type': None}
        
        title_lower = title.lower()
        
        # Extract size
        size_match = re.search(r'(\d+)\s*(gb|tb)\s*(ssd|hdd)', title_lower)
        if size_match:
            size = int(size_match.group(1))
            unit = size_match.group(2)
            storage_type = size_match.group(3) if size_match.group(3) else None
            
            # Convert to GB
            if unit == 'tb':
                size = size * 1024
            
            # Try to find storage type if not found
            if not storage_type:
                if 'ssd' in title_lower:
                    storage_type = 'ssd'
                elif 'hdd' in title_lower:
                    storage_type = 'hdd'
            
            return {'storage_size': size, 'storage_type': storage_type.upper() if storage_type else None}
        
        return {'storage_size': None, 'storage_type': None}
    
    storage_info = df['title'].apply(extract_storage)
    df['storage_gb'] = [x['storage_size'] for x in storage_info]
    df['storage_type'] = [x['storage_type'] for x in storage_info]
    
    # 9. Extract screen size
    def extract_screen_size(title):
        if pd.isna(title):
            return None
        match = re.search(r'(\d+\.?\d*)\s*["\']?\s*(?:inch)?', title.lower())
        if match:
            size = float(match.group(1))
            # Filter out unrealistic sizes
            if 10 <= size <= 20:
                return size
        return None
    
    df['screen_size_inch'] = df['title'].apply(extract_screen_size)
    
    # 10. Extract graphics card info
    def extract_graphics(title):
        if pd.isna(title):
            return {'gpu_brand': None, 'gpu_model': None}
        
        title_lower = title.lower()
        
        # NVIDIA
        nvidia_match = re.search(r'(rtx|gtx)\s*(\d{4})', title_lower)
        if nvidia_match:
            return {
                'gpu_brand': 'NVIDIA',
                'gpu_model': f"{nvidia_match.group(1).upper()} {nvidia_match.group(2)}"
            }
        
        # AMD Radeon
        if 'radeon' in title_lower:
            return {'gpu_brand': 'AMD', 'gpu_model': 'Radeon'}
        
        # Intel integrated
        if any(x in title_lower for x in ['intel uhd', 'intel iris', 'iris xe']):
            return {'gpu_brand': 'Intel', 'gpu_model': 'Integrated'}
        
        return {'gpu_brand': None, 'gpu_model': None}
    
    graphics_info = df['title'].apply(extract_graphics)
    df['gpu_brand'] = [x['gpu_brand'] for x in graphics_info]
    df['gpu_model'] = [x['gpu_model'] for x in graphics_info]
    
    # 11. Check if gaming laptop
    def is_gaming_laptop(title):
        if pd.isna(title):
            return False
        gaming_keywords = ['gaming', 'nitro', 'tuf', 'victus', 'loq', 'rog']
        return any(keyword in title.lower() for keyword in gaming_keywords)
    
    df['is_gaming'] = df['title'].apply(is_gaming_laptop)
    
    # 12. Add price category
    def categorize_price(price):
        if pd.isna(price):
            return 'Unknown'
        elif price < 50000:
            return 'Budget'
        elif price < 80000:
            return 'Mid-Range'
        elif price < 120000:
            return 'Premium'
        else:
            return 'High-End'
    
    df['price_category'] = df['price_after_discount'].apply(categorize_price)
    
    # 13. Clean URL
    df['url'] = df['url'].str.strip()
    
    # 14. Extract product ID from URL
    def extract_product_id(url):
        if pd.isna(url):
            return None
        match = re.search(r'-i(\d+)\.html', url)
        return match.group(1) if match else None
    
    df['product_id'] = df['url'].apply(extract_product_id)
    
    # 15. Add data quality flag
    df['has_complete_info'] = (
        df['rating'].notna() &
        df['price_after_discount'].notna() &
        df['brand'].notna() &
        df['processor_type'].notna() &
        df['ram_gb'].notna()
    )
    
    # 16. Handle duplicates
    df['is_duplicate'] = df.duplicated(subset=['title'], keep='first')
    
    # 17. Sort by rating and total ratings
    df = df.sort_values(['rating', 'total_ratings'], ascending=[False, False])
    
    # 18. Reorder columns for better readability
    column_order = [
        'product_id', 'title', 'brand', 'price_category',
        'price_before_discount', 'price_after_discount', 
        'actual_discount_amount', 'percent_discount',
        'rating', 'total_ratings', 'count',
        'processor_type', 'processor_gen', 'ram_gb',
        'storage_gb', 'storage_type', 'screen_size_inch',
        'gpu_brand', 'gpu_model', 'is_gaming',
        'description', 'url', 'has_complete_info', 'is_duplicate'
    ]
    
    # Only reorder columns that exist
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]
    
    print(f"\nCleaned shape: {df.shape}")
    print(f"\nNew columns added: {[col for col in df.columns if col not in ['title', 'score', 'count', 'rating', 'total_ratings', 'price_before_discount', 'price_after_discount', 'percent_discount', 'description', 'url']]}")
    print(f"\nData quality summary:")
    print(f"  - Complete info: {df['has_complete_info'].sum()} / {len(df)}")
    print(f"  - Duplicates: {df['is_duplicate'].sum()}")
    print(f"\nBrand distribution:\n{df['brand'].value_counts()}")
    print(f"\nPrice category distribution:\n{df['price_category'].value_counts()}")
    
    return df

# # Usage
# if __name__ == "__main__":
#     # Clean the data
#     cleaned_df = clean_laptop_data('laptops.csv')
    
#     # Save cleaned data
#     cleaned_df.to_csv('laptops_cleaned.csv', index=False)
#     print("\nCleaned data saved to 'laptops_cleaned.csv'")
    
#     # Optional: Save only non-duplicate, complete records
#     clean_subset = cleaned_df[
#         (~cleaned_df['is_duplicate']) & 
#         (cleaned_df['has_complete_info'])
#     ]
#     clean_subset.to_csv('laptops_clean_subset.csv', index=False)
#     print(f"Clean subset saved to 'laptops_clean_subset.csv' ({len(clean_subset)} records)")