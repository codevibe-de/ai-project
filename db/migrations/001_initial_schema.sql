-- ============================================
-- Initial Schema: Angebots-Erstellungs-Tool
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Line of Business (Versicherungssparte)
-- ============================================
CREATE TABLE line_of_business (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code       VARCHAR(50)  NOT NULL UNIQUE,
    name       VARCHAR(200) NOT NULL,
    description TEXT,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- Product (Versicherungsprodukt)
-- ============================================
CREATE TABLE product (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lob_id        UUID NOT NULL REFERENCES line_of_business(id),
    code          VARCHAR(50)  NOT NULL,
    name          VARCHAR(200) NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1,
    valid_from    DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until   DATE,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    metadata      JSONB DEFAULT '{}',
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (code, version)
);

CREATE INDEX idx_product_lob_id ON product(lob_id);
CREATE INDEX idx_product_active ON product(is_active, valid_from, valid_until);

-- ============================================
-- Risk Type (Risikotyp innerhalb eines Produkts)
-- ============================================
CREATE TABLE risk_type (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES product(id),
    code       VARCHAR(50)  NOT NULL UNIQUE,
    name       VARCHAR(200) NOT NULL,
    description TEXT,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_type_product_id ON risk_type(product_id);

-- ============================================
-- Product Rule (Regelbasierte Produktzuordnung)
-- ============================================
CREATE TABLE product_rule (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id     UUID NOT NULL REFERENCES product(id),
    rule_type      VARCHAR(50)  NOT NULL,
    field_name     VARCHAR(100) NOT NULL,
    operator       VARCHAR(20)  NOT NULL,
    expected_value JSONB NOT NULL,
    priority       INTEGER NOT NULL DEFAULT 0,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_product_rule_product_id ON product_rule(product_id);

-- ============================================
-- Rating Factor (Kalkulationsfaktoren)
-- ============================================
CREATE TABLE rating_factor (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id    UUID NOT NULL REFERENCES product(id),
    code          VARCHAR(50)  NOT NULL,
    name          VARCHAR(200) NOT NULL,
    data_type     VARCHAR(20)  NOT NULL,
    is_required   BOOLEAN NOT NULL DEFAULT TRUE,
    default_value JSONB,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (product_id, code)
);

CREATE INDEX idx_rating_factor_product_id ON rating_factor(product_id);

-- ============================================
-- Customer Request (Kundenanfrage)
-- ============================================
CREATE TABLE customer_request (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_email_id  VARCHAR(255),
    received_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    raw_email_body   TEXT,
    lob_code         VARCHAR(50),
    risk_type_code   VARCHAR(50),
    business_type    VARCHAR(200),
    rating_inputs    JSONB DEFAULT '{}',
    extraction_meta  JSONB DEFAULT '{}',
    status           VARCHAR(20) NOT NULL DEFAULT 'NEW',
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customer_request_status ON customer_request(status);
CREATE UNIQUE INDEX idx_customer_request_email_id ON customer_request(source_email_id) WHERE source_email_id IS NOT NULL;

-- ============================================
-- Offer (Angebot)
-- ============================================
CREATE TABLE offer (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_request_id UUID NOT NULL REFERENCES customer_request(id),
    product_id          UUID NOT NULL REFERENCES product(id),
    premium_amount      DECIMAL(12, 2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'EUR',
    valid_until         DATE,
    rating_snapshot     JSONB DEFAULT '{}',
    offer_document      TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_offer_customer_request_id ON offer(customer_request_id);
CREATE INDEX idx_offer_product_id ON offer(product_id);
CREATE INDEX idx_offer_status ON offer(status);

-- ============================================
-- updated_at Trigger
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_line_of_business_updated_at BEFORE UPDATE ON line_of_business FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_risk_type_updated_at BEFORE UPDATE ON risk_type FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_product_updated_at BEFORE UPDATE ON product FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_product_rule_updated_at BEFORE UPDATE ON product_rule FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_rating_factor_updated_at BEFORE UPDATE ON rating_factor FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customer_request_updated_at BEFORE UPDATE ON customer_request FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_offer_updated_at BEFORE UPDATE ON offer FOR EACH ROW EXECUTE FUNCTION update_updated_at();
