import os
import json
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')


def setup_ieee_style():
    """Configure matplotlib for IEEE journal compliance"""
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 9,
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'figure.titlesize': 10,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',
        'axes.linewidth': 0.5,
        'grid.linewidth': 0.3,
    })
    
    # IEEE column widths
    SINGLE_COL_WIDTH = 3.5  # inches
    DOUBLE_COL_WIDTH = 7.16  # inches
    MAX_HEIGHT = 8.0  # inches (leaving space for caption)
    
    return SINGLE_COL_WIDTH, DOUBLE_COL_WIDTH, MAX_HEIGHT

SINGLE_COL, DOUBLE_COL, MAX_HEIGHT = setup_ieee_style()


def load_original_datasets(dew_math_ds_fpath, dew_natqa_ds_fpath):
    """Load the original JSON datasets for analysis"""
    print("\n" + "="*60)
    print("=== LOADING ORIGINAL DATASETS FOR ANALYSIS ===")
    print("="*60)
    
    try:
        # Load DEW-MathQ dataset
        with open(dew_math_ds_fpath, 'r', encoding='utf-8') as f:
            math_data = json.load(f)
        
        # Load DEW-LogiQ dataset  
        with open(dew_natqa_ds_fpath, 'r', encoding='utf-8') as f:
            natqa_data = json.load(f)
        
        print(f"DEW-MathQ loaded: {len(math_data)} questions")
        print(f"DEW-LogiQ loaded: {len(natqa_data)} questions")
        
        return math_data, natqa_data
        
    except FileNotFoundError as e:
        print(f"Dataset file not found: {e}")
        print("Please ensure the JSON files are in the correct location")
        return None, None

def load_and_prepare_data(dew_math_results_fpath, dew_natqa_results_fpath):
    """Load datasets and perform initial cleaning"""
    try:
        # Load datasets
        dew_math = pd.read_csv(dew_math_results_fpath)
        dew_natqa = pd.read_csv(dew_natqa_results_fpath)

        print(f"DEW-MathQ loaded: {len(dew_math)} samples")
        print(f"DEW-LogiQ loaded: {len(dew_natqa)} samples")

        # Compute foundation metrics (more meaningful)
        print("\n--- Computing Foundation Metrics ---")
        math_foundation = compute_foundation_metrics(dew_math, "DEW-MathQ")
        natqa_foundation = compute_foundation_metrics(dew_natqa, "DEW-LogiQ")
        
        # return dew_math_clean, dew_natqa_clean, math_foundation, natqa_foundation
        return dew_math, dew_natqa, math_foundation, natqa_foundation
        
    except FileNotFoundError as e:
        print(f"Dataset file not found: {e}")
        print("Please update file paths in the load_and_prepare_data() function")
        return None, None, None, None

def compute_foundation_metrics(df, dataset_name):
    """Compute meaningful foundation metrics for interpretation"""
    print(f"\n{dataset_name} Foundation Analysis:")
    
    foundation = {}
    
    # 1. Dataset Scope and Scale
    foundation['total_samples'] = len(df)
    foundation['unique_models'] = df['model'].nunique()
    foundation['unique_strategies'] = df['eval_strategy'].nunique()
    foundation['unique_domains'] = df['domain'].nunique()
    
    print(f"Scale: {foundation['total_samples']} samples across {foundation['unique_models']} models")
    print(f"Scope: {foundation['unique_strategies']} strategies, {foundation['unique_domains']} domains")
    
    # 2. Balance and Distribution
    strategy_distribution = df['eval_strategy'].value_counts()
    model_distribution = df['model'].value_counts()
    
    foundation['strategy_balance'] = strategy_distribution.std() / strategy_distribution.mean()
    foundation['model_balance'] = model_distribution.std() / model_distribution.mean()
    
    print(f"Strategy balance coefficient: {foundation['strategy_balance']:.2f} (lower = more balanced)")
    print(f"Model balance coefficient: {foundation['model_balance']:.2f}")
    
    # 3. Performance Range and Variation
    foundation['accuracy_range'] = df['is_correct'].agg(['min', 'max', 'mean', 'std'])
    foundation['confidence_range'] = df['llm_confidence'].agg(['min', 'max', 'mean', 'std'])
    
    print(f"Accuracy range: [{foundation['accuracy_range']['min']:.1f}, {foundation['accuracy_range']['max']:.1f}], mean: {foundation['accuracy_range']['mean']:.2f}")
    print(f"Confidence range: [{foundation['confidence_range']['min']:.2f}, {foundation['confidence_range']['max']:.2f}], mean: {foundation['confidence_range']['mean']:.2f}")
    
    # 4. Data Quality Indicators
    foundation['missing_responses'] = df.isnull().sum().sum()
    foundation['confidence_outliers'] = len(df[(df['llm_confidence'] < 0) | (df['llm_confidence'] > 1)])
    
    # 5. Flow Strategy Presence
    flow_strategies = [s for s in df['eval_strategy'].unique() if 'flow' in s.lower()]
    foundation['has_flow_strategy'] = len(flow_strategies) > 0
    foundation['flow_strategy_names'] = flow_strategies
    foundation['flow_sample_size'] = len(df[df['eval_strategy'].isin(flow_strategies)]) if flow_strategies else 0
    
    if foundation['has_flow_strategy']:
        print(f"Flow strategies detected: {flow_strategies}")
        print(f"Flow strategy sample size: {foundation['flow_sample_size']}")
    else:
        print("No flow strategies detected in dataset")
        
    return foundation

def create_dataset_analysis_visualizations_split(math_stats, natqa_stats, dir_name="figures"):
    """Create dataset analysis visualizations split into two IEEE-compliant figures"""
    print("\n=== Creating Dataset Analysis Visualizations (Split) ===")
    
    # FIGURE 0A: Bar Charts (Question Types and Text Lengths)
    fig_0a, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.5))
    
    # Plot 1: Question Type Distribution (Combined)
    all_question_types = set(list(math_stats['question_type_counts'].keys()) + 
                           list(natqa_stats['question_type_counts'].keys()))
    
    math_counts = [math_stats['question_type_counts'].get(qt, 0) for qt in all_question_types]
    natqa_counts = [natqa_stats['question_type_counts'].get(qt, 0) for qt in all_question_types]
    
    x = range(len(all_question_types))
    width = 0.35
    
    _ = ax1.bar([i - width/2 for i in x], math_counts, width, 
                   label='DEW-MathQ', color='steelblue', alpha=0.8, edgecolor='black', linewidth=0.5)
    _ = ax1.bar([i + width/2 for i in x], natqa_counts, width,
                   label='DEW-LogiQ', color='orange', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax1.set_xlabel('Question Type', fontsize=9)
    ax1.set_ylabel('Count', fontsize=9)
    ax1.set_title('Question Type Distribution', fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(all_question_types, rotation=45, ha='right', fontsize=8)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Text Length Comparison
    length_categories = ['Question', 'MC Options']
    math_lengths = [np.mean(math_stats['question_lengths']), np.mean(math_stats['option_lengths'])]
    natqa_lengths = [np.mean(natqa_stats['question_lengths']), np.mean(natqa_stats['option_lengths'])]
    
    x2 = range(len(length_categories))
    bars3 = ax2.bar([i - width/2 for i in x2], math_lengths, width,
                   label='DEW-MathQ', color='steelblue', alpha=0.8, edgecolor='black', linewidth=0.5)
    bars4 = ax2.bar([i + width/2 for i in x2], natqa_lengths, width,
                   label='DEW-LogiQ', color='orange', alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax2.set_xlabel('Text Component', fontsize=9)
    ax2.set_ylabel('Average Word Length', fontsize=9)
    ax2.set_title('Text Length Comparison', fontsize=10)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(length_categories, fontsize=9)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 10,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=7)
    
    # Add IEEE subfigure labels
    ax1.text(0.5, -0.25, '(a)', transform=ax1.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    ax2.text(0.5, -0.25, '(b)', transform=ax2.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for subfigure labels
    plt.savefig(f'{dir_name}\\figure_dewmathq_dewlogiq_analysis_bars.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{dir_name}\\figure_dewmathq_dewlogiq_analysis_bars.png', dpi=300, bbox_inches='tight')
    print("Figure 0a (Bar Charts) saved as PDF & PNG")
    
    # FIGURE 0B: Pie Charts (Domain/Category Distributions)
    fig_0b, (ax3, ax4) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 4))
    
    # Plot 3: DEW-MathQ Domain Distribution (Top 8)
    top_math_domains = dict(math_stats['domain_counts'].most_common(8))
    wedges3, _, _ = ax3.pie(top_math_domains.values(), autopct='%1.1f%%', 
                                         startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(top_math_domains))))
    ax3.set_title('DEW-MathQ: Top 8 Domains', fontsize=10)
    
    # Create legend for domains with shorter labels
    legend_labels_math = []
    for domain in top_math_domains.keys():
        if len(domain) > 25:
            legend_labels_math.append(domain[:22] + "...")
        else:
            legend_labels_math.append(domain)
    
    ax3.legend(wedges3, legend_labels_math, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    
    # Plot 4: DEW-LogiQ Category Distribution (Top 8)
    top_natqa_categories = dict(natqa_stats['category_counts'].most_common(8))
    wedges4, _, _ = ax4.pie(top_natqa_categories.values(), autopct='%1.1f%%',
                                         startangle=90, colors=plt.cm.Set2(np.linspace(0, 1, len(top_natqa_categories))))
    ax4.set_title('DEW-LogiQ: Top 8 Categories', fontsize=10)
    
    # Create legend for categories with shorter labels
    legend_labels_natqa = []
    for cat in top_natqa_categories.keys():
        if len(cat) > 25:
            legend_labels_natqa.append(cat[:22] + "...")
        else:
            legend_labels_natqa.append(cat)
    
    ax4.legend(wedges4, legend_labels_natqa, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    
    # Add IEEE subfigure labels
    ax3.text(0.5, -0.15, '(a)', transform=ax3.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    ax4.text(0.5, -0.15, '(b)', transform=ax4.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)  # Make room for subfigure labels
    plt.savefig(f'{dir_name}\\figure_0b_dewmathq_dewlogiq_analysis_pies.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{dir_name}\\figure_0b_dewmathq_dewlogiq_analysis_pies.png', dpi=300, bbox_inches='tight')
    print("Figure 0b (Pie Charts) saved as PDF & PNG")
    
    return fig_0a, fig_0b

def analyze_question_types(questions, dataset_name):
    """Analyze question type patterns (what/which/how/etc.)"""
    print(f"\n--- {dataset_name} Question Type Analysis ---")
    
    question_starters = []
    
    for question in questions:
        q_text = question.lower().strip()

        if dataset_name == "DEW-MathQ":
            q_text = q_text.split("\n\nquestion: ")[-1]
        
        # Extract first word or phrase
        if q_text.startswith('what '):
            question_starters.append('What')
        elif q_text.startswith('which '):
            question_starters.append('Which')
        elif q_text.startswith('how '):
            question_starters.append('How')
        elif q_text.startswith('when '):
            question_starters.append('When')
        elif q_text.startswith('where '):
            question_starters.append('Where')
        elif q_text.startswith('why '):
            question_starters.append('Why')
        elif q_text.startswith('calculate '):
            question_starters.append('Calculate')
        elif q_text.startswith('determine '):
            question_starters.append('Determine')
        elif q_text.startswith('find '):
            question_starters.append('Find')
        elif q_text.startswith('if '):
            question_starters.append('If')
        else:
            question_starters.append('Other')
    
    question_type_counts = Counter(question_starters)
    
    print(f"Question Type Distribution:")
    for q_type, count in question_type_counts.most_common():
        percentage = (count / len(questions)) * 100
        print(f"   {q_type:<12}: {count:3d} ({percentage:5.1f}%)")
    
    return question_type_counts

def analyze_math_dataset_structure(math_data):
    """Analyze DEW-MathQ dataset structure and content"""
    print(f"\n--- DEW-MathQ Dataset Structure Analysis ---")
    
    # Domain analysis
    domains = [item.get('domain', 'Unknown') for item in math_data]
    domain_counts = Counter(domains)
    
    print(f"Domain Distribution ({len(set(domains))} unique domains):")
    for domain, count in domain_counts.most_common():
        percentage = (count / len(math_data)) * 100
        print(f"   {domain:<40}: {count:3d} ({percentage:5.1f}%)")
    
    # Extract questions and multiple choice options
    questions = []
    multiple_choice_combinations = []
    
    for item in math_data:
        # Question text
        question_text = item.get('gold_problem', '')
        questions.append(question_text)
        
        # Multiple choice options - navigate the nested structure
        mc_options = item.get('multiple_choice_options', {})
        if mc_options:
            # Get the single key-value pair
            for _, options_dict in mc_options.items():
                options_list = options_dict.get('options', [])
                
                # Handle the case where options are dictionaries with value, unit, is_correct
                combined_options_parts = []
                for option in options_list:
                    if isinstance(option, dict):
                        # Extract value and unit from dictionary
                        value = option.get('value', '')
                        unit = option.get('unit', '')
                        option_text = f"{value} {unit}".strip()
                        combined_options_parts.append(option_text)
                    else:
                        # If it's already a string, use it directly
                        combined_options_parts.append(str(option))
                
                # Combine all options into one string
                combined_options = ' '.join(combined_options_parts)
                multiple_choice_combinations.append(combined_options)
        else:
            multiple_choice_combinations.append('')
    
    # Text length analysis
    question_lengths = [len(q.split()) for q in questions if q]
    option_lengths = [len(opts) for opts in multiple_choice_combinations if opts]
    
    print(f"\nText Length Statistics:")
    print(f"   Question Length       - Mean: {np.mean(question_lengths):.1f}, Median: {np.median(question_lengths):.1f}, Max: {max(question_lengths)}")
    print(f"   MC Options Length     - Mean: {np.mean(option_lengths):.1f}, Median: {np.median(option_lengths):.1f}, Max: {max(option_lengths)}")
    
    # Question type analysis
    question_type_counts = analyze_question_types(questions, "DEW-MathQ")
    
    return {
        'domain_counts': domain_counts,
        'question_lengths': question_lengths,
        'option_lengths': option_lengths,
        'question_type_counts': question_type_counts,
        'total_questions': len(math_data),
        'unique_domains': len(set(domains))
    }

def analyze_natqa_dataset_structure(natqa_data):
    """Analyze DEW-LogiQ dataset structure and content"""
    print(f"\n--- DEW-LogiQ Dataset Structure Analysis ---")
    
    # Category and subcategory analysis
    categories = [item.get('category', 'Unknown') for item in natqa_data]
    subcategories = [item.get('subcategory', 'Unknown') for item in natqa_data]
    
    category_counts = Counter(categories)
    subcategory_counts = Counter(subcategories)
    
    print(f"Category Distribution ({len(set(categories))} unique categories):")
    for category, count in category_counts.most_common():
        percentage = (count / len(natqa_data)) * 100
        print(f"   {category:<50}: {count:3d} ({percentage:5.1f}%)")
    
    print(f"\nSubcategory Distribution ({len(set(subcategories))} unique subcategories):")
    for subcategory, count in subcategory_counts.most_common()[:10]:  # Top 10
        percentage = (count / len(natqa_data)) * 100
        print(f"   {subcategory:<50}: {count:3d} ({percentage:5.1f}%)")
    
    # Extract text components
    questions = []
    multiple_choice_combinations = []
    knowledge_contexts = []
    
    for item in natqa_data:
        # Question text
        question_text = item.get('question', '')
        questions.append(question_text)
        
        # Multiple choice options - combine all answer options
        answer_truth = item.get('answer_truth', '')
        answer_a = item.get('answer_option_A', '')
        answer_b = item.get('answer_option_B', '')
        answer_c = item.get('answer_option_C', '')
        
        combined_options = f"{answer_truth} {answer_a} {answer_b} {answer_c}".strip()
        multiple_choice_combinations.append(combined_options)
        
        # Knowledge context
        knowledge_context = item.get('knowledge_context', '')
        knowledge_contexts.append(knowledge_context)
    
    # Text length analysis
    question_lengths = [len(q.split()) for q in questions if q]
    option_lengths = [len(opts) for opts in multiple_choice_combinations if opts]
    context_lengths = [len(ctx) for ctx in knowledge_contexts if ctx]
    
    print(f"\nText Length Statistics:")
    print(f"   Question Length       - Mean: {np.mean(question_lengths):.1f}, Median: {np.median(question_lengths):.1f}, Max: {max(question_lengths)}")
    print(f"   MC Options Length     - Mean: {np.mean(option_lengths):.1f}, Median: {np.median(option_lengths):.1f}, Max: {max(option_lengths)}")
    print(f"   Knowledge Context     - Mean: {np.mean(context_lengths):.1f}, Median: {np.median(context_lengths):.1f}, Max: {max(context_lengths)}")
    
    # Question type analysis
    question_type_counts = analyze_question_types(questions, "DEW-LogiQ")
    
    return {
        'category_counts': category_counts,
        'subcategory_counts': subcategory_counts,
        'question_lengths': question_lengths,
        'option_lengths': option_lengths,
        'context_lengths': context_lengths,
        'question_type_counts': question_type_counts,
        'total_questions': len(natqa_data),
        'unique_categories': len(set(categories)),
        'unique_subcategories': len(set(subcategories))
    }

def create_dataset_summary_table(math_stats, natqa_stats):
    """Create comprehensive dataset summary table"""
    print("\n=== Dataset Summary Table ===")
    
    summary_data = {
        'Metric': [
            'Total Questions',
            'Unique Domains/Categories',
            'Unique Subdomains/Subcategories',
            'Avg Question Length (words)',
            'Avg MC Options Length (words)',
            'Avg Knowledge Context Length (words)',
            'Most Common Question Type',
            'Domain/Category Coverage'
        ],
        'DEW-MathQ': [
            math_stats['total_questions'],
            math_stats['unique_domains'],
            'N/A',  # Math doesn't have subdomains in this structure
            f"{np.mean(math_stats['question_lengths']):.0f}",
            f"{np.mean(math_stats['option_lengths']):.0f}",
            'N/A',  # Math doesn't have knowledge context
            math_stats['question_type_counts'].most_common(1)[0][0],
            'Mathematical water management'
        ],
        'DEW-LogiQ': [
            natqa_stats['total_questions'],
            natqa_stats['unique_categories'],
            natqa_stats['unique_subcategories'],
            f"{np.mean(natqa_stats['question_lengths']):.0f}",
            f"{np.mean(natqa_stats['option_lengths']):.0f}",
            f"{np.mean(natqa_stats['context_lengths']):.0f}",
            natqa_stats['question_type_counts'].most_common(1)[0][0],
            'Conceptual water management'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    print("Dataset Summary:")
    print(summary_df.to_string(index=False))
    
    return summary_df

def run_phase_dataset_analysis(dew_math_ds_fpath, dew_natqa_ds_fpath):
    """Dataset Analysis (Updated with split figures)"""
    print("\n" + "="*60)
    print("=== DATASET ANALYSIS ===")
    print("="*60)
    
    # Load original datasets
    math_data, natqa_data = load_original_datasets(dew_math_ds_fpath, dew_natqa_ds_fpath)
    
    if math_data is None or natqa_data is None:
        print("Cannot proceed without datasets")
        return None, None, None
    
    # Analyze dataset structures
    math_stats = analyze_math_dataset_structure(math_data)
    natqa_stats = analyze_natqa_dataset_structure(natqa_data)
    
    # Create summary table
    summary_table = create_dataset_summary_table(math_stats, natqa_stats)
    
    # Create split visualizations
    fig_0a, fig_0b = create_dataset_analysis_visualizations_split(math_stats, natqa_stats)
    
    print("Key insights:")
    print(f"- DEW-MathQ: {math_stats['total_questions']} questions across {math_stats['unique_domains']} domains")
    print(f"- DEW-LogiQ: {natqa_stats['total_questions']} questions across {natqa_stats['unique_categories']} categories")
    print(f"- Question types vary between datasets (mathematical vs conceptual focus)")
    print(f"- Text complexity differs significantly between domains")
    print("- Figure 0a: Bar charts (question types and text lengths)")
    print("- Figure 0b: Pie charts (domain/category distributions)")
    
    return math_stats, natqa_stats, summary_table, fig_0a, fig_0b


def create_domain_strategy_interaction_heatmap(math_domain_strategy, natqa_domain_strategy, dir_name="figures"):
    """Create Domain × Strategy interaction visualization"""
    print("\n=== Creating Domain × Strategy Interaction Heatmap ===")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 5))
    
    # DEW-MathQ: Domain × Strategy heatmap
    math_pivot = math_domain_strategy['domain_strategy_performance']['Accuracy_Mean'].unstack(fill_value=0)
    im1 = ax1.imshow(math_pivot.values, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
    ax1.set_xticks(range(len(math_pivot.columns)))
    ax1.set_xticklabels(math_pivot.columns, rotation=45, ha='right', fontsize=7)
    ax1.set_yticks(range(len(math_pivot.index)))
    ax1.set_yticklabels(math_pivot.index, fontsize=7)
    # ax1.set_title('DEW-MathQ: Domain × Strategy Performance', fontsize=10)
    ax1.set_xlabel('Strategy', fontsize=9)
    ax1.set_ylabel('Domain', fontsize=9)
    
    # Add values to heatmap
    for i in range(len(math_pivot.index)):
        for j in range(len(math_pivot.columns)):
            if math_pivot.iloc[i, j] > 0:
                ax1.text(j, i, f'{math_pivot.iloc[i, j]:.2f}', 
                        ha="center", va="center", color="black", fontsize=6)
    
    # DEW-LogiQ: Domain × Strategy heatmap  
    natqa_pivot = natqa_domain_strategy['domain_strategy_performance']['Accuracy_Mean'].unstack(fill_value=0)
    im2 = ax2.imshow(natqa_pivot.values, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
    ax2.set_xticks(range(len(natqa_pivot.columns)))
    ax2.set_xticklabels(natqa_pivot.columns, rotation=45, ha='right', fontsize=7)
    ax2.set_yticks(range(len(natqa_pivot.index)))
    ax2.set_yticklabels(natqa_pivot.index, fontsize=7)
    # ax2.set_title('DEW-LogiQ: Domain × Strategy Performance', fontsize=10)
    ax2.set_xlabel('Strategy', fontsize=9)
    # ax2.set_ylabel('Domain', fontsize=9)
    
    # Add values to heatmap
    for i in range(len(natqa_pivot.index)):
        for j in range(len(natqa_pivot.columns)):
            if natqa_pivot.iloc[i, j] > 0:
                ax2.text(j, i, f'{natqa_pivot.iloc[i, j]:.2f}', 
                        ha="center", va="center", color="black", fontsize=6)
    
    # Add colorbar
    # cbar = plt.colorbar(im2, ax=[ax1, ax2], shrink=0.8, aspect=20)
    # cbar.set_label('Pass@1 Score', fontsize=8)
    cbar_ax = fig.add_axes([1, 0.20, 0.03, 0.7])  # [left, bottom, width, height]
    cbar = plt.colorbar(im2, cax=cbar_ax, shrink=0.8, aspect=20)
    cbar.set_label('Pass@1 Score', fontsize=8)

    # Add IEEE subfigure labels
    ax1.text(0.5, -0.15, '(a)', transform=ax1.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    ax2.text(0.5, -0.15, '(b)', transform=ax2.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    
    plt.tight_layout()
    plt.savefig(f'{dir_name}\\figure_domain_strategy_interactions.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{dir_name}\\figure_domain_strategy_interactions.png', dpi=300, bbox_inches='tight')
    print("Figure_domain_strategy_interactions saved as PDF & PNG")
    
    return fig

def analyze_domain_performance(df, dataset_name):
    """Analyze performance across domains"""
    print(f"\n--- {dataset_name} Domain Performance Analysis ---")
    
    # Domain performance summary
    domain_summary = df.groupby('domain').agg({
        'is_correct': ['mean', 'std', 'count'],
        'llm_confidence': ['mean', 'std']
    }).round(3)
    
    domain_summary.columns = ['Accuracy_Mean', 'Accuracy_Std', 'Count', 'Confidence_Mean', 'Confidence_Std']
    
    # Model performance by domain
    domain_model_performance = df.groupby(['domain', 'model']).agg({
        'is_correct': 'mean',
        'llm_confidence': 'mean'
    }).round(3)
    
    # Difficulty ranking
    domain_difficulty = domain_summary.sort_values('Accuracy_Mean')
    print(f"Domain difficulty ranking (easiest to hardest):")
    for domain, row in domain_difficulty.iterrows():
        print(f"   {domain}: {row['Accuracy_Mean']:.2f} ± {row['Accuracy_Std']:.2f}")
    
    return {
        'domain_summary': domain_summary,
        'domain_model_performance': domain_model_performance,
        'domain_difficulty_ranking': domain_difficulty
    }

def analyze_domain_strategy_interactions(df, dataset_name):
    """Analyze how strategies perform across different domains"""
    print(f"\n--- {dataset_name} Domain × Strategy Interactions ---")
    
    # Performance matrix: Domain × Strategy
    domain_strategy_performance = df.groupby(['domain', 'eval_strategy']).agg({
        'is_correct': ['mean', 'std', 'count'],
        'llm_confidence': ['mean', 'std']
    }).round(3)
    
    domain_strategy_performance.columns = ['Accuracy_Mean', 'Accuracy_Std', 'Count', 'Confidence_Mean', 'Confidence_Std']
    
    # Best strategy per domain
    best_strategies_per_domain = {}
    for domain in df['domain'].unique():
        domain_data = df[df['domain'] == domain]
        strategy_performance = domain_data.groupby('eval_strategy')['is_correct'].mean()
        if len(strategy_performance) > 0:
            best_strategy = strategy_performance.idxmax()
            best_score = strategy_performance.max()
            best_strategies_per_domain[domain] = {'strategy': best_strategy, 'score': best_score}
            print(f"Best strategy for {domain}: {best_strategy} ({best_score:.2f})")
    
    # Strategy effectiveness by domain (flow advantage calculation)
    flow_strategies = [s for s in df['eval_strategy'].unique() if 'flow' in s.lower()]
    baseline_strategies = [s for s in df['eval_strategy'].unique() if 'flow' not in s.lower()]
    
    domain_flow_advantage = {}
    if flow_strategies and baseline_strategies:
        for domain in df['domain'].unique():
            domain_data = df[df['domain'] == domain]
            flow_perf = domain_data[domain_data['eval_strategy'].isin(flow_strategies)]['is_correct'].mean()
            baseline_perf = domain_data[domain_data['eval_strategy'].isin(baseline_strategies)]['is_correct'].mean()
            domain_flow_advantage[domain] = flow_perf - baseline_perf
        
        print(f"Flow advantage computed for {len(domain_flow_advantage)} domains")
    
    return {
        'domain_strategy_performance': domain_strategy_performance,
        'best_strategies_per_domain': best_strategies_per_domain,
        'domain_flow_advantage': domain_flow_advantage
    }

def analyze_flow_strategy_by_domain(df, dataset_name):
    """Analyze flow strategy effectiveness across domains"""
    print(f"\n--- {dataset_name} Flow Strategy Domain Analysis ---")
    
    flow_strategies = [s for s in df['eval_strategy'].unique() if 'flow' in s.lower()]
    if not flow_strategies:
        print("No flow strategies found")
        return {}
    
    flow_data = df[df['eval_strategy'].isin(flow_strategies)]
    baseline_data = df[~df['eval_strategy'].isin(flow_strategies)]
    
    # Domain-specific flow effectiveness
    domain_flow_effectiveness = {}
    for domain in df['domain'].unique():
        domain_flow = flow_data[flow_data['domain'] == domain]['is_correct'].mean()
        domain_baseline = baseline_data[baseline_data['domain'] == domain]['is_correct'].mean()
        effectiveness = domain_flow - domain_baseline
        domain_flow_effectiveness[domain] = {
            'flow_performance': domain_flow,
            'baseline_performance': domain_baseline,
            'advantage': effectiveness
        }
        print(f"{domain}: Flow advantage = {effectiveness:.2f}")
    
    return domain_flow_effectiveness

def analyze_cross_domain_generalization(dew_math, dew_natqa):
    """Analyze model generalization across domains and datasets"""
    print("\n--- Cross-Domain Generalization Analysis ---")
    
    # Model performance correlation across datasets
    math_model_perf = dew_math.groupby('model')['is_correct'].mean()
    natqa_model_perf = dew_natqa.groupby('model')['is_correct'].mean()
    
    # Find common models
    common_models = set(math_model_perf.index) & set(natqa_model_perf.index)
    
    if len(common_models) > 1:
        math_common = math_model_perf[list(common_models)]
        natqa_common = natqa_model_perf[list(common_models)]
        
        cross_dataset_correlation = math_common.corr(natqa_common)
        print(f"Cross-dataset model correlation: {cross_dataset_correlation:.2f}")
    else:
        cross_dataset_correlation = None
        print("Insufficient common models for correlation analysis")
    
    # Domain consistency within models
    model_consistency = {}
    for model in common_models:
        math_domains = dew_math[dew_math['model'] == model].groupby('domain')['is_correct'].mean()
        natqa_domains = dew_natqa[dew_natqa['model'] == model].groupby('domain')['is_correct'].mean()
        
        math_std = math_domains.std()
        natqa_std = natqa_domains.std()
        
        model_consistency[model] = {
            'math_domain_variance': math_std,
            'natqa_domain_variance': natqa_std,
            'overall_consistency': -(math_std + natqa_std)  # Lower variance = higher consistency
        }
    
    print(f"Model consistency analysis completed for {len(model_consistency)} models")
    
    return {
        'cross_dataset_correlation': cross_dataset_correlation,
        'model_consistency': model_consistency,
        'common_models': list(common_models)
    }

def run_phase_domain_strategy_interactions(dew_math, dew_natqa):
    """Execute Phase: Domain × Strategy Interactions Analysis"""
    print("\n" + "="*50)
    print("=== Domain × Strategy Interactions ===")
    print("="*50)
    
    print("\n--- A: Domain Performance Analysis ---")
    math_domain_stats = analyze_domain_performance(dew_math, "DEW-MathQ")
    natqa_domain_stats = analyze_domain_performance(dew_natqa, "DEW-LogiQ")
    
    print("\n--- B: Domain × Strategy Interactions ---")
    math_domain_strategy = analyze_domain_strategy_interactions(dew_math, "DEW-MathQ")
    natqa_domain_strategy = analyze_domain_strategy_interactions(dew_natqa, "DEW-LogiQ")
    
    print("\n--- C: Flow Strategy Domain Effectiveness ---")
    math_flow_domain = analyze_flow_strategy_by_domain(dew_math, "DEW-MathQ")
    natqa_flow_domain = analyze_flow_strategy_by_domain(dew_natqa, "DEW-LogiQ")
    
    print("\n--- D: Cross-Domain Generalization ---")
    cross_domain_analysis = analyze_cross_domain_generalization(dew_math, dew_natqa)
    
    
    fig3c = create_domain_strategy_interaction_heatmap(math_domain_strategy, natqa_domain_strategy)
    plt.show()
    
    return math_domain_stats, natqa_domain_stats, math_domain_strategy, natqa_domain_strategy


def create_figure_F_model_confidence_scatter(math_model_conf, natqa_model_conf, dir_name="figures"):
    """Part 1: Model Confidence vs Accuracy Scatter Plots with Manual Symbol Mapping"""
    print("\n===Part 1: Model Confidence Scatter Analysis ===")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.5))

    # the models: 'o3', 'gemini-2.5-pro', 'Claude-sonnet-4', 'Phi-4-reasoning-plus', 'Qwen3-30B'

    manual_symbol_map = {
        'Claude-sonnet-4': 'd',          # thin_diamond
        'gemini-2.5-pro': 's',           # square
        'o3': 'o',                       # circle
        'Qwen3-30B': 'X',                # x filled
        'default': '8'                   # octagon for any unmapped models
    }
    
    # Helper function to get symbol for model
    def get_symbol(model_name):
        return manual_symbol_map.get(model_name, manual_symbol_map['default'])
    
    # Plot 1: Model Confidence vs Accuracy (DEW-MathQ)
    models = list(math_model_conf.keys())
    confidences = [math_model_conf[m]['mean_confidence'] for m in models]
    accuracies = [math_model_conf[m]['accuracy'] for m in models]
    correlations = [math_model_conf[m].get('conf_acc_correlation', 0) for m in models]
    
    # Plot each model with its manually assigned symbol, colored by correlation
    for i, model in enumerate(models):
        print(f"{model = }")
        ax1.scatter(confidences[i], accuracies[i], 
                   c=correlations[i], cmap='RdYlBu_r', 
                   s=120, alpha=0.8, marker=get_symbol(model), 
                   edgecolors='black', linewidth=0.5, vmin=0, vmax=1)
    
    ax1.set_xlabel('Mean Confidence', fontsize=9)
    ax1.set_ylabel('Accuracy', fontsize=9)
    # ax1.set_title('DEW-MathQ: Model Confidence vs Accuracy', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0.5, 1.0)
    ax1.set_ylim(0.4, 1.0)
    
    # Plot 2: Model Confidence vs Accuracy (DEW-LogiQ)
    models_natqa = list(natqa_model_conf.keys())
    confidences_natqa = [natqa_model_conf[m]['mean_confidence'] for m in models_natqa]
    accuracies_natqa = [natqa_model_conf[m]['accuracy'] for m in models_natqa]
    correlations_natqa = [natqa_model_conf[m].get('conf_acc_correlation', 0) for m in models_natqa]
    
    # Plot each model with its manually assigned symbol, colored by correlation
    for i, model in enumerate(models_natqa):
        ax2.scatter(confidences_natqa[i], accuracies_natqa[i], 
                   c=correlations_natqa[i], cmap='RdYlBu_r', 
                   s=120, alpha=0.8, marker=get_symbol(model), 
                   edgecolors='black', linewidth=0.5, vmin=0, vmax=1)
    
    ax2.set_xlabel('Mean Confidence', fontsize=9)
    ax2.set_ylabel('Accuracy', fontsize=9)
    # ax2.set_title('DEW-LogiQ: Model Confidence vs Accuracy', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.5, 1.0)
    ax2.set_ylim(0.4, 1.0)
    
    # Create legend with manually assigned symbols
    all_models = sorted(list(set(models + models_natqa)))
    legend_elements = []
    for model in all_models:
        # Clean model names for legend
        clean_name = model.replace('_', '-').replace('reasoning-plus', 'reas+')
        if len(clean_name) > 15:
            clean_name = clean_name[:15] + "..."
        
        legend_elements.append(plt.Line2D([0], [0], marker=get_symbol(model), 
                                        color='white', linestyle='None', markersize=8,
                                        markerfacecolor='white', markeredgecolor='black', 
                                        markeredgewidth=0.5, label=clean_name))
    
    # Position legend
    fig.legend(handles=legend_elements, loc='center right', bbox_to_anchor=(0.90, 0.5),
              fontsize=7, title='Models', title_fontsize=8, frameon=True, 
              fancybox=True, shadow=False)
    
    # Adjust subplot spacing
    plt.subplots_adjust(left=0.08, right=0.75, bottom=0.2, top=0.9, wspace=0.25)
    
    # Add colorbar
    # cbar_ax = fig.add_axes([0.08, 0.05, 0.6, 0.03])  # [left, bottom, width, height]
    cbar_ax = fig.add_axes([0.08, 0.04, 0.6, 0.03])  # [left, bottom, width, height]
    dummy_scatter = ax2.scatter([], [], c=[], cmap='RdYlBu_r', vmin=0, vmax=1)
    cbar = plt.colorbar(dummy_scatter, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Confidence-Accuracy Correlation', fontsize=8)

    # Add IEEE subfigure labels
    ax1.text(0.5, -0.4, '(a)', transform=ax1.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    ax2.text(0.5, -0.4, '(b)', transform=ax2.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')    
    
    plt.savefig(f'{dir_name}\\figure_F_part1_model_confidence_scatter.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{dir_name}\\figure_F_part1_model_confidence_scatter.png', dpi=300, bbox_inches='tight')
    print("Figure F Part 1 saved with manual symbol mapping")
    
    # Print the symbol mapping for reference
    print("\nSymbol Mapping Used:")
    for model in all_models:
        print(f"   {model}: {get_symbol(model)}")
    
    return fig

def create_figure_F_model_calibration_comparison(math_model_conf, natqa_model_conf, 
                                                math_calibration, natqa_calibration, 
                                                dir_name="figures"):
    """Model Calibration Quality Comparison"""
    print("\n===Model Calibration Comparison ===")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(DOUBLE_COL, 4))
    
    # Plot 1: Model Calibration Quality (ECE comparison)
    math_models_cal = list(math_calibration.keys())
    natqa_models_cal = list(natqa_calibration.keys())
    
    # Find common models for comparison
    common_models_cal = list(set(math_models_cal) & set(natqa_models_cal))
    common_models_cal.sort()  # Sort for consistency
    
    if common_models_cal:
        math_ece_common = [round(math_calibration[m]['ece'], 2)for m in common_models_cal]
        natqa_ece_common = [round(natqa_calibration[m]['ece'], 2) for m in common_models_cal]
        
        x_pos = range(len(common_models_cal))
        width = 0.35
        
        bars1 = ax1.bar([round(x - width/2, 2) for x in x_pos], math_ece_common, width, 
                       label='DEW-MathQ', color='steelblue', alpha=0.8, edgecolor='black', linewidth=0.5)
        bars2 = ax1.bar([round(x + width/2, 2) for x in x_pos], natqa_ece_common, width, 
                       label='DEW-LogiQ', color='orange', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax1.set_xlabel('Model', fontsize=9)
        ax1.set_ylabel('Expected Calibration Error', fontsize=9)
        # ax1.set_title('Model Calibration Quality (ECE)', fontsize=10)
        ax1.set_xticks(x_pos)
        
        # Clean model names for x-axis labels
        clean_model_names = []
        for model in common_models_cal:
            clean_name = model.replace('_', '-').replace('reasoning-plus', 'reas+')
            if len(clean_name) > 10:
                clean_name = clean_name[:10] + "..."
            clean_model_names.append(clean_name)
        
        ax1.set_xticklabels(clean_model_names, rotation=45, ha='right', fontsize=8)
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels with better positioning to avoid overlap
        max_bar_height = max(max(math_ece_common), max(natqa_ece_common))
        label_offset = max_bar_height * 0.03  # 3% of max height for spacing
        
        for i, (bar, val) in enumerate(zip(bars1, math_ece_common)):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + label_offset,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=7)
        
        for i, (bar, val) in enumerate(zip(bars2, natqa_ece_common)):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + label_offset,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=7)
        
        # Adjust y-axis to accommodate labels
        ax1.set_ylim(0, max_bar_height * 1.15)
    
    # Plot 2: Overconfidence Rate Comparison
    models = list(math_model_conf.keys())
    models_natqa = list(natqa_model_conf.keys())
    
    # Find common models for overconfidence comparison
    common_models_overconf = list(set(models) & set(models_natqa))
    common_models_overconf.sort()  # Sort for consistency
    
    if common_models_overconf:
        math_overconf_common = [math_model_conf[m]['overconfidence_rate'] for m in common_models_overconf]
        natqa_overconf_common = [natqa_model_conf[m]['overconfidence_rate'] for m in common_models_overconf]
        
        x_pos = range(len(common_models_overconf))
        
        bars3 = ax2.bar([x - width/2 for x in x_pos], math_overconf_common, width, 
                       label='DEW-MathQ', color='steelblue', alpha=0.8, edgecolor='black', linewidth=0.5)
        bars4 = ax2.bar([x + width/2 for x in x_pos], natqa_overconf_common, width, 
                       label='DEW-LogiQ', color='orange', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax2.set_xlabel('Model', fontsize=9)
        ax2.set_ylabel('Overconfidence Rate (%)', fontsize=9)
        # ax2.set_title('Model Overconfidence Rates', fontsize=10)
        ax2.set_xticks(x_pos)
        
        # Clean model names for x-axis labels
        clean_model_names = []
        for model in common_models_overconf:
            clean_name = model.replace('_', '-').replace('reasoning-plus', 'reas+')
            if len(clean_name) > 10:
                clean_name = clean_name[:10] + "..."
            clean_model_names.append(clean_name)
        
        ax2.set_xticklabels(clean_model_names, rotation=45, ha='right', fontsize=8)
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels with better positioning to avoid overlap
        max_bar_height = max(max(math_overconf_common), max(natqa_overconf_common))
        label_offset = max_bar_height * 0.03  # 3% of max height for spacing
        
        for i, (bar, val) in enumerate(zip(bars3, math_overconf_common)):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + label_offset,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=7)
        
        for i, (bar, val) in enumerate(zip(bars4, natqa_overconf_common)):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + label_offset,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=7)
        
        # Adjust y-axis to accommodate labels
        ax2.set_ylim(0, max_bar_height * 1.15)


    # Add IEEE subfigure labels
    ax1.text(0.5, -0.3, '(a)', transform=ax1.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman')
    ax2.text(0.5, -0.3, '(b)', transform=ax2.transAxes, ha='center', va='top', 
             fontsize=8, family='Times New Roman') 
        
    plt.tight_layout()
    plt.savefig(f'{dir_name}\\figure_F_part2_model_calibration_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{dir_name}\\figure_F_part2_model_calibration_comparison.png', dpi=300, bbox_inches='tight')
    print("Figure F saved as PDF & PNG")
    
    return fig

def create_split_figure_F(math_model_conf, natqa_model_conf, 
                          math_calibration, natqa_calibration, dir_name="figures"):
    """Create both parts of the split Figure F (supposed to be final/last plot)"""
    print("\n=== Creating Split Figure F ===")
    
    # Create Part 1: Scatter plots with symbol legend
    figF_part1 = create_figure_F_model_confidence_scatter(
        math_model_conf, natqa_model_conf, dir_name
    )
    
    # Create Part 2: Calibration comparison
    figF_part2 = create_figure_F_model_calibration_comparison(
        math_model_conf, natqa_model_conf, 
        math_calibration, natqa_calibration, dir_name
    )
    
    return figF_part1, figF_part2

def analyze_model_specific_confidence_patterns(df, dataset_name, over_confidence_threshold=0.8):
    """Analyze confidence patterns for each model"""
    print(f"\n--- {dataset_name} Model-Specific Confidence Analysis ---")
    
    model_confidence_analysis = {}
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        if len(model_data) < 10:  # Skip models with insufficient data
            continue
        
        # Basic confidence statistics
        confidence_stats = {
            'mean_confidence': model_data['llm_confidence'].mean(),
            'confidence_std': model_data['llm_confidence'].std(),
            'accuracy': model_data['is_correct'].mean(),
            'sample_size': len(model_data)
        }
        
        # Confidence-accuracy correlation
        if len(model_data) > 1:
            confidence_stats['conf_acc_correlation'] = model_data['llm_confidence'].corr(
                model_data['is_correct'].astype(int)
            )
        
        # Confidence calibration (Brier score)
        brier_score = np.mean((model_data['llm_confidence'] - model_data['is_correct'].astype(int))**2)
        confidence_stats['brier_score'] = brier_score
        
        # Overconfidence detection
        high_conf_wrong = model_data[(model_data['llm_confidence'] >= over_confidence_threshold) & (model_data['is_correct'] == False)]
        confidence_stats['overconfidence_rate'] = len(high_conf_wrong) / len(model_data) * 100
        
        # Confidence distribution by correctness
        correct_conf = model_data[model_data['is_correct'] == True]['llm_confidence'].mean()
        incorrect_conf = model_data[model_data['is_correct'] == False]['llm_confidence'].mean()
        confidence_stats['confidence_gap'] = correct_conf - incorrect_conf
        
        model_confidence_analysis[model] = confidence_stats
        
        print(f"{model}: Conf={confidence_stats['mean_confidence']:.2f}, "
              f"Acc={confidence_stats['accuracy']:.2f}, "
              f"Corr={confidence_stats.get('conf_acc_correlation', 0):.2f}")
    
    return model_confidence_analysis

def analyze_model_strategy_confidence_interactions(df, dataset_name):
    """Analyze how model confidence varies by strategy"""
    print(f"\n--- {dataset_name} Model × Strategy Confidence Interactions ---")
    
    model_strategy_confidence = {}
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        strategy_conf_patterns = {}
        
        for strategy in model_data['eval_strategy'].unique():
            strategy_data = model_data[model_data['eval_strategy'] == strategy]
            
            if len(strategy_data) >= 5:  # Minimum samples for meaningful analysis
                strategy_conf_patterns[strategy] = {
                    'mean_confidence': strategy_data['llm_confidence'].mean(),
                    'accuracy': strategy_data['is_correct'].mean(),
                    'conf_acc_correlation': strategy_data['llm_confidence'].corr(
                        strategy_data['is_correct'].astype(int)
                    ) if len(strategy_data) > 1 else np.nan,
                    'sample_size': len(strategy_data)
                }
        
        model_strategy_confidence[model] = strategy_conf_patterns
    
    # Identify models with best strategy-specific confidence reliability
    best_strategy_confidence = {}
    for model, strategies in model_strategy_confidence.items():
        if strategies:
            # Find strategy with highest confidence-accuracy correlation
            strategy_corrs = {s: data.get('conf_acc_correlation', 0) 
                            for s, data in strategies.items() 
                            if not np.isnan(data.get('conf_acc_correlation', np.nan))}
            
            if strategy_corrs:
                best_strategy = max(strategy_corrs.keys(), key=lambda x: strategy_corrs[x])
                best_strategy_confidence[model] = {
                    'best_strategy': best_strategy,
                    'correlation': strategy_corrs[best_strategy],
                    'confidence': strategies[best_strategy]['mean_confidence'],
                    'accuracy': strategies[best_strategy]['accuracy']
                }
    
    print(f"Model-strategy confidence patterns analyzed for {len(model_strategy_confidence)} models")
    
    return model_strategy_confidence, best_strategy_confidence

def analyze_model_calibration_quality(df, dataset_name):
    """Analyze calibration quality for each model"""
    print(f"\n--- {dataset_name} Model Calibration Quality ---")
    
    def calculate_ece(confidence, is_correct, n_bins=10):
        """Calculate Expected Calibration Error"""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i+1]
            
            in_bin = (confidence > bin_lower) & (confidence <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = is_correct[in_bin].mean()
                avg_confidence_in_bin = confidence[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    model_calibration = {}
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        if len(model_data) >= 20:  # Minimum samples for calibration analysis
            # Calculate calibration metrics
            ece = calculate_ece(model_data['llm_confidence'], model_data['is_correct'])
            brier = np.mean((model_data['llm_confidence'] - model_data['is_correct'].astype(int))**2)
            
            # Reliability (correlation)
            reliability = model_data['llm_confidence'].corr(model_data['is_correct'].astype(int))
            
            # Resolution (how well confidence discriminates correct from incorrect)
            correct_conf = model_data[model_data['is_correct'] == True]['llm_confidence']
            incorrect_conf = model_data[model_data['is_correct'] == False]['llm_confidence']
            
            if len(correct_conf) > 0 and len(incorrect_conf) > 0:
                from scipy.stats import mannwhitneyu
                _, p_value = mannwhitneyu(correct_conf, incorrect_conf, alternative='two-sided')
                resolution_significant = p_value < 0.05
            else:
                resolution_significant = False
            
            model_calibration[model] = {
                'ece': ece,
                'brier_score': brier,
                'reliability': reliability,
                'resolution_significant': resolution_significant,
                'mean_confidence': model_data['llm_confidence'].mean(),
                'accuracy': model_data['is_correct'].mean(),
                'calibration_quality': 'Well-calibrated' if ece < 0.1 else 'Poorly-calibrated' # see https://arxiv.org/html/2501.19047v2
            }
    
    # Rank models by calibration quality
    calibration_ranking = sorted(model_calibration.items(), 
                               key=lambda x: x[1]['ece'])
    
    print(f"Model calibration ranking (best to worst):")
    for i, (model, metrics) in enumerate(calibration_ranking[:5]):
        print(f"   {i+1}. {model}: ECE={metrics['ece']:.2f}, "
              f"Reliability={metrics['reliability']:.2f}")
    
    return model_calibration, calibration_ranking

def run_phase_model_specific_confidence_analysis(dew_math, dew_natqa):
    """Execute Phase: Model-Specific Confidence Analysis"""
    print("\n" + "="*50)
    print("=== Phase: Model-Specific Confidence Analysis ===")
    print("="*50)
    
    # Model Confidence Patterns
    print("\n---Model Confidence Patterns ---")
    math_model_conf = analyze_model_specific_confidence_patterns(dew_math, "DEW-MathQ")
    natqa_model_conf = analyze_model_specific_confidence_patterns(dew_natqa, "DEW-LogiQ")
    
    # Model × Strategy Confidence Interactions
    print("\n--- Model × Strategy Confidence Interactions ---")
    math_model_strategy_conf, math_best_strategy_conf = analyze_model_strategy_confidence_interactions(dew_math, "DEW-MathQ")
    natqa_model_strategy_conf, natqa_best_strategy_conf = analyze_model_strategy_confidence_interactions(dew_natqa, "DEW-LogiQ")
    
    # Model Calibration Quality
    print("\n---Model Calibration Quality ---")
    math_calibration, math_cal_ranking = analyze_model_calibration_quality(dew_math, "DEW-MathQ")
    natqa_calibration, natqa_cal_ranking = analyze_model_calibration_quality(dew_natqa, "DEW-LogiQ")
    
    
    print("Key insights:")
    print("- Model-specific confidence patterns identified")
    print("- Model × Strategy confidence interactions mapped")
    print("- Model calibration quality assessed")
    print("- Best confidence-strategy combinations found")
    
    return (math_model_conf, natqa_model_conf, 
            math_model_strategy_conf, natqa_model_strategy_conf,
            math_calibration, natqa_calibration)


def apply_naming_updates(dew_math_clean, dew_natqa_clean):
    """Apply the new naming conventions to the datasets"""
    
    # Update strategy names in DEW-MathQ dataset
    dew_math_clean['eval_strategy'] = dew_math_clean['eval_strategy'].replace({
        'flow-math': 'flow-eq',
        'terms-as-hints': 'flow-path'
    })
    
    # Update strategy names in DEW-LogiQ dataset  
    dew_natqa_clean['eval_strategy'] = dew_natqa_clean['eval_strategy'].replace({
        'flow-natqa': 'flow-map'
    })
    
    return dew_math_clean, dew_natqa_clean


if __name__ == "__main__": 

    # 1. required data inputs
    dew_math_ds_fpath = os.path(DATA_DIR, "sample_dew-mathq.json")
    dew_natqa_ds_fpath = os.path(DATA_DIR, "sample_dew-logiq.json")

    dew_math_results_fpath = os.path(DATA_DIR, "sample_llm_performance_results_on_dew-mathq.csv")
    dew_natqa_results_fpath = os.path(DATA_DIR, "sample_llm_performance_results_on_dew-logiq.csv")

    # 2. Analyses

    math_dataset_stats, natqa_dataset_stats, dataset_summary_table, fig_0a, fig_0b  = run_phase_dataset_analysis(dew_math_ds_fpath, dew_natqa_ds_fpath)

    # Load llm's performance results data
    dew_math_raw, dew_natqa_raw, _, _ = load_and_prepare_data(dew_math_results_fpath, dew_natqa_results_fpath)
    dew_math_clean, dew_natqa_clean = apply_naming_updates(dew_math_raw, dew_natqa_raw)


    math_domain_stats, natqa_domain_stats, math_domain_strategy, natqa_domain_strategy = run_phase_domain_strategy_interactions(dew_math_clean, dew_natqa_clean)

    math_model_conf_clean, natqa_model_conf_clean, math_model_strategy_conf_clean, natqa_model_strategy_conf_clean, math_calibration_clean, natqa_calibration_clean = run_phase_model_specific_confidence_analysis(dew_math_clean, dew_natqa_clean)
    figF_part1, figF_part2 = create_split_figure_F(
        math_model_conf_clean, natqa_model_conf_clean, 
        math_calibration_clean, natqa_calibration_clean
    )    
