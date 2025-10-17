CREATE TYPE language_pref AS ENUM ('ar', 'en', 'hi');
CREATE TYPE maint_category AS ENUM ('emergency', 'urgent', 'normal');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'overdue');

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE NOT NULL,
    language_preference language_pref DEFAULT 'ar',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    owner_id INT NOT NULL CHECK (owner_id > 0),
    status VARCHAR(20) DEFAULT 'vacant',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    tenant_id INT REFERENCES tenants(id) ON DELETE SET NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date > start_date),
    rent_amount DECIMAL(10,2) NOT NULL CHECK (rent_amount > 0),
    renewal_reminders JSONB DEFAULT '[{"days":90}, {"days":60}, {"days":30}, {"days":7}]'::JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    contract_id INT REFERENCES contracts(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    status payment_status DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE technicians (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) UNIQUE NOT NULL,
    language_preference language_pref DEFAULT 'ar',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE maintenance_requests (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,
    tenant_id INT REFERENCES tenants(id) ON DELETE SET NULL,
    technician_id INT REFERENCES technicians(id) ON DELETE SET NULL,
    category maint_category NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    response_time INTERVAL NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INT REFERENCES tenants(id) ON DELETE SET NULL,
    details JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    session_id UUID
);

CREATE TABLE aggregated_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    value NUMERIC NOT NULL,
    details JSONB,
    owner_id INT,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_insights (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    score NUMERIC,
    description TEXT NOT NULL,
    data_source JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE TABLE ai_agent_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    details JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    severity VARCHAR(20) DEFAULT 'low'
);

-- Indexes
CREATE INDEX idx_payments_due_date_status ON payments(due_date, status);
CREATE INDEX idx_maintenance_category_status ON maintenance_requests(category, status);
CREATE INDEX idx_analytics_events_type_ts ON analytics_events(event_type, timestamp);
CREATE INDEX idx_user_insights_user_type ON user_insights(user_id, insight_type);

-- Triggers
CREATE OR REPLACE FUNCTION update_timestamp() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_ts BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE PROCEDURE update_timestamp();
CREATE TRIGGER update_maintenance_ts BEFORE UPDATE ON maintenance_requests FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE OR REPLACE FUNCTION log_maintenance_event() RETURNS TRIGGER AS $$
BEGIN
   INSERT INTO analytics_events (event_type, user_id, details, timestamp)
   VALUES ('maintenance_create', NEW.tenant_id, jsonb_build_object('category', NEW.category, 'property_id', NEW.property_id), NOW());
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_maintenance_after_insert
AFTER INSERT ON maintenance_requests
FOR EACH ROW EXECUTE PROCEDURE log_maintenance_event();
