import pandas as pd
import re
from collections import Counter

# Read the CSV file
df = pd.read_csv('./data/Table1_Summary_Notable_LitRev_CSV.csv')

print("="*80)
print("AGRICULTURAL LLM LITERATURE REVIEW ANALYSIS")
print("="*80)
print(f"\nTotal number of studies: {len(df)}\n")

# 1. Agricultural Sector Category Distribution
print("1. AGRICULTURAL SECTOR CATEGORY DISTRIBUTION")
print("-" * 80)
sector_counts = df['Agricultural Sector Category'].value_counts()
sector_percentages = (sector_counts / len(df) * 100).round(2)

for sector, count in sector_counts.items():
    percentage = sector_percentages[sector]
    print(f"{sector}: {count} studies ({percentage}%)")

print("\n")

# 2. AI Model Distribution
print("2. AI MODEL DISTRIBUTION")
print("-" * 80)

# Extract all models mentioned
all_models = []
for models_str in df['LLMs'].dropna():
    # Split by comma and clean up
    models = [m.strip() for m in str(models_str).split(',')]
    all_models.extend(models)

# Categorize models
model_categories = {
    'GPT': [],
    'BERT': [],
    'LLaMA': [],
    'ChatGLM': [],
    'Vision Transformers': [],
    'T5': [],
    'RoBERTa': [],
    'Other': []
}

for model in all_models:
    model_lower = model.lower()
    if 'gpt' in model_lower or 'chatgpt' in model_lower:
        model_categories['GPT'].append(model)
    elif 'bert' in model_lower and 'roberta' not in model_lower:
        model_categories['BERT'].append(model)
    elif 'llama' in model_lower:
        model_categories['LLaMA'].append(model)
    elif 'chatglm' in model_lower or 'glm' in model_lower:
        model_categories['ChatGLM'].append(model)
    elif 'vit' in model_lower or 'vision transformer' in model_lower or 'swin' in model_lower:
        model_categories['Vision Transformers'].append(model)
    elif 't5' in model_lower:
        model_categories['T5'].append(model)
    elif 'roberta' in model_lower:
        model_categories['RoBERTa'].append(model)
    else:
        model_categories['Other'].append(model)

# Count studies using each model category
total_studies = len(df)
for category, models in model_categories.items():
    count = len(models)
    percentage = (count / total_studies * 100)
    if count > 0:
        print(f"{category}: {count} mentions ({percentage:.1f}% of studies)")

print("\n")

# 3. Benchmark Dataset Analysis
print("3. BENCHMARK DATASET ANALYSIS")
print("-" * 80)

proprietary_count = 0
no_benchmark_count = 0
new_benchmark_count = 0

for dataset in df['Benchmark Dataset']:
    dataset_str = str(dataset).strip().lower()
    
    if dataset_str == 'na' or dataset_str == 'nan':
        no_benchmark_count += 1
    elif 'proprietary' in dataset_str:
        proprietary_count += 1
    elif 'custom' in dataset_str or 'self curated' in dataset_str:
        new_benchmark_count += 1

proprietary_pct = (proprietary_count / total_studies * 100)
no_benchmark_pct = (no_benchmark_count / total_studies * 100)
new_benchmark_pct = (new_benchmark_count / total_studies * 100)

print(f"Proprietary datasets: {proprietary_count} studies ({proprietary_pct:.1f}%)")
print(f"No benchmark specified (NA): {no_benchmark_count} studies ({no_benchmark_pct:.1f}%)")
print(f"New agricultural benchmarks introduced: {new_benchmark_count} studies ({new_benchmark_pct:.1f}%)")

print("\n")

# 4. Reasoning Analysis
print("4. REASONING CAPABILITIES ANALYSIS")
print("-" * 80)

logical_reasoning_count = 0
math_reasoning_count = 0

for idx, row in df.iterrows():
    logical = str(row['Logical Reasoning']).strip().lower()
    math = str(row['Mathematical Reasoning']).strip().lower()
    
    if logical == 'yes':
        logical_reasoning_count += 1
    if math == 'yes':
        math_reasoning_count += 1

logical_pct = (logical_reasoning_count / total_studies * 100)
math_pct = (math_reasoning_count / total_studies * 100)

print(f"Studies with logical reasoning: {logical_reasoning_count} ({logical_pct:.1f}%)")
print(f"Studies with mathematical reasoning: {math_reasoning_count} ({math_pct:.1f}%)")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)