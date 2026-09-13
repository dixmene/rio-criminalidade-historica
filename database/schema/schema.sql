-- ==============================================================================
-- DDL PostgreSQL / PostGIS - Base Histórica da Criminalidade no RJ
-- ==============================================================================

-- 1. Tabela de Fontes Documentais
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    citation TEXT NOT NULL,
    author VARCHAR(255),
    publisher VARCHAR(255),
    source_type VARCHAR(100) NOT NULL DEFAULT 'oficial_relatorio',
    publication_date VARCHAR(50),
    document_date VARCHAR(50),
    url VARCHAR(500),
    archive_ref VARCHAR(255),
    file_hash_sha256 VARCHAR(64),
    reliability_rating INTEGER DEFAULT 5 CHECK (reliability_rating BETWEEN 1 AND 5),
    notes TEXT,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 2. Tabela de Organizações / Facções / Milícias
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    acronym VARCHAR(50),
    org_type VARCHAR(100) NOT NULL DEFAULT 'faccao_criminosa',
    foundation_year INTEGER,
    dissolution_year INTEGER,
    description TEXT,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 3. Tabela de Pessoas / Lideranças
CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    aliases VARCHAR(255),
    role_description VARCHAR(255),
    birth_year INTEGER,
    death_year INTEGER,
    notes TEXT,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 4. Tabela de Regiões / Territórios
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    region_type VARCHAR(100) NOT NULL DEFAULT 'bairro',
    municipality VARCHAR(100) NOT NULL DEFAULT 'Rio de Janeiro',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geojson_boundary TEXT,
    description TEXT,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 5. Tabela de Eventos Históricos
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL DEFAULT 'acontecimento_geral',
    date_start VARCHAR(50) NOT NULL,
    date_end VARCHAR(50),
    year INTEGER NOT NULL,
    exact_date BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT NOT NULL,
    historical_context TEXT,
    confidence_level VARCHAR(30) NOT NULL DEFAULT 'confirmado',
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 6. Proveniência de Eventos (EventSource)
CREATE TABLE IF NOT EXISTS event_sources (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    page_or_section VARCHAR(100),
    excerpt TEXT NOT NULL,
    claim_assertion TEXT,
    validation_status VARCHAR(30) NOT NULL DEFAULT 'confirmado',
    confidence_notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 7. Relações Territoriais no Tempo (TerritorialRelations)
CREATE TABLE IF NOT EXISTS territorial_relations (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    region_id INTEGER NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    date_start VARCHAR(50) NOT NULL,
    date_end VARCHAR(50),
    relation_type VARCHAR(100) NOT NULL DEFAULT 'dominio_hegemonico',
    confidence_level VARCHAR(30) NOT NULL DEFAULT 'confirmado',
    notes TEXT,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 8. Proveniência de Relações Territoriais
CREATE TABLE IF NOT EXISTS territorial_relation_sources (
    id SERIAL PRIMARY KEY,
    territorial_relation_id INTEGER NOT NULL REFERENCES territorial_relations(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    page_or_section VARCHAR(100),
    excerpt TEXT NOT NULL,
    validation_status VARCHAR(30) NOT NULL DEFAULT 'confirmado',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 9. Tabelas Associativas de Eventos
CREATE TABLE IF NOT EXISTS event_organizations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role_in_event VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS event_people (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    role_in_event VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS event_regions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    region_id INTEGER NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    specific_location_name VARCHAR(255)
);

-- Índices de Consulta Rápida
CREATE INDEX IF NOT EXISTS idx_events_year ON events(year);
CREATE INDEX IF NOT EXISTS idx_events_confidence ON events(confidence_level);
CREATE INDEX IF NOT EXISTS idx_regions_norm_name ON regions(normalized_name);
CREATE INDEX IF NOT EXISTS idx_orgs_norm_name ON organizations(normalized_name);
CREATE INDEX IF NOT EXISTS idx_people_norm_name ON people(normalized_name);
CREATE INDEX IF NOT EXISTS idx_territorial_dates ON territorial_relations(date_start, date_end);
