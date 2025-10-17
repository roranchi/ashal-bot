from typing import Dict, List
from supabase import Client
from datetime import datetime
import pandas as pd
import os

def generate_aggregated_metrics(supabase: Client, owner_id: int, period: str = 'monthly') -> Dict:
    query = supabase.table('properties').select('*').eq('owner_id', owner_id).execute()
    df = pd.DataFrame(query.data)
    occupancy = (df[df['status'] == 'occupied'].shape[0] / df.shape[0]) * 100 if not df.empty else 0
    metrics = {'occupancy_rate': occupancy, 'generated_at': datetime.now().isoformat()}
    
    supabase.table('aggregated_metrics').insert({
        'metric_type': 'occupancy_rate',
        'period': period,
        'value': occupancy,
        'details': metrics,
        'owner_id': owner_id
    }).execute()
    
    supabase.table('ai_agent_logs').insert({
        'event_type': 'analytics_generated',
        'details': metrics,
        'severity': 'low'
    }).execute()
    
    return metrics

def generate_user_insights(supabase: Client, user_id: int) -> Dict:
    events = supabase.table('analytics_events').select('*').eq('user_id', user_id).execute()
    df = pd.DataFrame(events.data)
    
    if df.empty:
        return {'score': 0, 'description': 'No data'}
    
    churn_score = df[df['event_type'] == 'payment_overdue'].shape[0] / len(df) if len(df) > 0 else 0
    insight = {
        'insight_type': 'churn_prediction',
        'score': churn_score,
        'description': f"Churn risk: {churn_score*100:.2f}% based on {len(df)} events"
    }
    
    supabase.table('user_insights').insert(insight).execute()
    supabase.table('ai_agent_logs').insert({
        'event_type': 'insight_generated',
        'details': insight,
        'severity': 'medium'
    }).execute()
    
    return insight
