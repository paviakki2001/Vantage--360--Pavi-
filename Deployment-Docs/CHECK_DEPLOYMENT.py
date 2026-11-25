"""Validate the supplied dashboard data and Python syntax without executing the app."""
from pathlib import Path
import ast, json, sys
root = Path(__file__).resolve().parent
required = [
    'dashboard/app.py',
    'dashboard/executive_app.py',
    'src/data_analysis/dashboard_validation.py',
    'data/processed/master_dataset.parquet',
    'data/processed/customer_retention_analysis.parquet',
    'data/processed/customer_ltv_analysis.parquet',
    'data/processed/week5/manifest.json',
    'reports/week5_da11_executive_analytics_report.md',
]
missing = [name for name in required if not (root/name).is_file()]
for name in ['dashboard/app.py','dashboard/executive_app.py','src/data_analysis/dashboard_validation.py']:
    ast.parse((root/name).read_text(encoding='utf-8'), filename=name)
manifest = json.loads((root/'data/processed/week5/manifest.json').read_text(encoding='utf-8'))
print('Missing:', missing or 'None')
print('KPI analytics failures:', manifest.get('analytics_failures'))
print('AI approval:', manifest.get('ai_approval'))
print('Threshold approval:', manifest.get('threshold_approval'))
print('Deployment files valid:', not missing)
sys.exit(bool(missing))
