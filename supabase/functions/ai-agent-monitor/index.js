export const handler = async () => {
  const { createClient } = require('@supabase/supabase-js');
  const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

  const { data: metrics } = await supabase.rpc('calculate_occupancy_rate', { owner_id_param: 1 });
  await supabase.from('ai_agent_logs').insert({
    event_type: 'system_health',
    details: { occupancy_rate: metrics },
    severity: 'low'
  });

  const { data: webhook_logs } = await supabase.from('analytics_events').select('*').eq('event_type', 'message_sent').order('timestamp', { ascending: false }).limit(10);
  const avg_response_time = webhook_logs.reduce((acc, log) => acc + (log.details.response_time || 0), 0) / webhook_logs.length;
  await supabase.from('ai_agent_logs').insert({
    event_type: 'api_performance',
    details: { avg_response_time_ms: avg_response_time },
    severity: avg_response_time > 1000 ? 'high' : 'medium'
  });

  return { status: 'Monitoring completed' };
};
