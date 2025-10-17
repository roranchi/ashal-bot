CREATE OR REPLACE FUNCTION calculate_occupancy_rate(owner_id_param INT) RETURNS NUMERIC AS $$
DECLARE
   total_properties INT;
   occupied INT;
BEGIN
   SELECT COUNT(*) INTO total_properties FROM properties WHERE owner_id = owner_id_param;
   SELECT COUNT(*) INTO occupied FROM properties WHERE owner_id = owner_id_param AND status = 'occupied';
   IF total_properties = 0 THEN RETURN 0; END IF;
   RETURN (occupied::NUMERIC / total_properties) * 100;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION calculate_churn_risk(tenant_id_param INT) RETURNS NUMERIC AS $$
DECLARE
   late_payments INT;
BEGIN
   SELECT COUNT(*) INTO late_payments FROM payments p 
   JOIN contracts c ON p.contract_id = c.id 
   WHERE c.tenant_id = tenant_id_param AND p.status = 'overdue';
   
   RETURN CASE 
      WHEN late_payments > 3 THEN 0.8
      WHEN late_payments > 1 THEN 0.5
      ELSE 0.2
   END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
