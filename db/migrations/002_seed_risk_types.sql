-- ============================================
-- Seed: Risk Types for Berufshaftpflicht Handwerk
-- ============================================

-- Line of Business
INSERT INTO line_of_business (code, name)
VALUES ('HAFTPFLICHT', 'Haftpflichtversicherung')
ON CONFLICT (code) DO NOTHING;

-- Product: Berufshaftpflicht Handwerk
INSERT INTO product (lob_id, code, name, version)
SELECT id, 'BERUFSHAFTPFLICHT_HANDWERK', 'Berufshaftpflicht Handwerk', 1
FROM line_of_business
WHERE code = 'HAFTPFLICHT'
ON CONFLICT (code, version) DO NOTHING;

-- Risk Types
INSERT INTO risk_type (product_id, code, name)
SELECT p.id, rt.code, rt.name
FROM product p
CROSS JOIN (VALUES
    ('DACHDECKER',  'Dachdecker'),
    ('ELEKTRIKER',  'Elektriker'),
    ('KLEMPNER',    'Klempner'),
    ('ZIMMERMANN',  'Zimmermann'),
    ('MALER',       'Maler'),
    ('SCHREINER',   'Schreiner')
) AS rt(code, name)
WHERE p.code = 'BERUFSHAFTPFLICHT_HANDWERK' AND p.version = 1
ON CONFLICT (code) DO NOTHING;
