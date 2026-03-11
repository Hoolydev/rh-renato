-- ============================================================
-- SETUP SUPABASE — Agente IA Seleção de Currículos
-- Execute no SQL Editor do Supabase
-- ============================================================

-- Extensão para busca vetorial (matching semântico)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- TABELA: candidatos
-- ============================================================
CREATE TABLE IF NOT EXISTS candidatos (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cpf_raw                 TEXT UNIQUE,
  nome                    TEXT NOT NULL,
  email                   TEXT UNIQUE,
  whatsapp                TEXT,
  telefone                TEXT,

  -- Localização
  endereco_completo       TEXT,
  latitude                DECIMAL(10, 8),
  longitude               DECIMAL(11, 8),
  distancia_sede_km       DECIMAL(6, 2),

  -- Perfil profissional
  cargo_desejado          TEXT,
  formacao                TEXT,
  anos_experiencia        INTEGER DEFAULT 0,
  pretensao_salarial      TEXT,
  disponibilidade_horario TEXT,
  disponibilidade_imediata BOOLEAN DEFAULT FALSE,

  -- Arrays de competências
  habilidades_array       TEXT[] DEFAULT '{}',
  idiomas_array           TEXT[] DEFAULT '{}',
  certificacoes_array     TEXT[] DEFAULT '{}',

  -- Currículo
  curriculo_url           TEXT,
  curriculo_texto_extraido TEXT,
  linkedin_url            TEXT,

  -- Busca vetorial (embedding do perfil)
  embedding_perfil        vector(1536),

  -- Score e status
  score_medio             DECIMAL(5, 2) DEFAULT 0,
  total_candidaturas      INTEGER DEFAULT 0,
  status                  TEXT DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'contratado', 'descartado', 'fora_raio', 'banco_espera', 'qualificado')),
  fonte                   TEXT CHECK (fonte IN ('whatsapp', 'email', 'linkedin', 'indicacao', 'manual')),

  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_candidatos_status ON candidatos(status);
CREATE INDEX IF NOT EXISTS idx_candidatos_cargo ON candidatos(cargo_desejado);
CREATE INDEX IF NOT EXISTS idx_candidatos_whatsapp ON candidatos(whatsapp);
CREATE INDEX IF NOT EXISTS idx_candidatos_email ON candidatos(email);
CREATE INDEX IF NOT EXISTS idx_candidatos_distancia ON candidatos(distancia_sede_km);
CREATE INDEX IF NOT EXISTS idx_candidatos_score ON candidatos(score_medio DESC);

-- Índice vetorial para matching semântico
CREATE INDEX IF NOT EXISTS idx_candidatos_embedding
ON candidatos USING ivfflat (embedding_perfil vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- TABELA: vagas
-- ============================================================
CREATE TABLE IF NOT EXISTS vagas (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo                    TEXT NOT NULL,
  descricao                 TEXT,
  empresa                   TEXT NOT NULL,
  responsavel_email         TEXT NOT NULL,
  responsavel_whatsapp      TEXT,

  -- Localização da sede
  endereco_sede             TEXT,
  latitude_sede             DECIMAL(10, 8),
  longitude_sede            DECIMAL(11, 8),
  raio_maximo_km            INTEGER DEFAULT 15,

  -- Requisitos
  requisitos_obrigatorios   JSONB DEFAULT '[]',
  requisitos_desejados      JSONB DEFAULT '[]',

  -- Condições
  salario_min               DECIMAL(10, 2),
  salario_max               DECIMAL(10, 2),
  regime                    TEXT CHECK (regime IN ('CLT', 'PJ', 'Estágio', 'Temporário', 'Trainee')),
  disponibilidade_imediata  BOOLEAN DEFAULT FALSE,

  -- Status
  status                    TEXT DEFAULT 'aberta' CHECK (status IN ('aberta', 'em_selecao', 'encerrada', 'pausada')),
  data_abertura             TIMESTAMPTZ DEFAULT NOW(),
  prazo_candidatura         TIMESTAMPTZ,
  criada_por                UUID,

  created_at                TIMESTAMPTZ DEFAULT NOW(),
  updated_at                TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_vagas_status ON vagas(status);
CREATE INDEX IF NOT EXISTS idx_vagas_titulo ON vagas(titulo);
CREATE INDEX IF NOT EXISTS idx_vagas_data ON vagas(data_abertura DESC);

-- ============================================================
-- TABELA: candidaturas (relacionamento candidato ↔ vaga)
-- ============================================================
CREATE TABLE IF NOT EXISTS candidaturas (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidato_id          UUID NOT NULL REFERENCES candidatos(id) ON DELETE CASCADE,
  vaga_id               UUID NOT NULL REFERENCES vagas(id) ON DELETE CASCADE,

  -- Scores
  score_tecnico         DECIMAL(5, 2),
  score_geo             DECIMAL(5, 2),
  score_comportamental  DECIMAL(5, 2),
  score_final           DECIMAL(5, 2),
  posicao_ranking       INTEGER,

  -- Análise IA
  justificativa_ia      TEXT,
  pontos_fortes         JSONB DEFAULT '[]',
  pontos_atencao        JSONB DEFAULT '[]',
  recomendacao_entrevista BOOLEAN DEFAULT FALSE,

  -- Status
  status                TEXT DEFAULT 'triagem' CHECK (status IN ('triagem', 'shortlist', 'entrevista', 'aprovado', 'reprovado', 'contratado')),
  notificado_candidato  BOOLEAN DEFAULT FALSE,
  data_notificacao      TIMESTAMPTZ,

  created_at            TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(candidato_id, vaga_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_candidaturas_vaga ON candidaturas(vaga_id);
CREATE INDEX IF NOT EXISTS idx_candidaturas_candidato ON candidaturas(candidato_id);
CREATE INDEX IF NOT EXISTS idx_candidaturas_status ON candidaturas(status);
CREATE INDEX IF NOT EXISTS idx_candidaturas_score ON candidaturas(score_final DESC);

-- ============================================================
-- TABELA: sessoes_whatsapp (estado da conversa)
-- ============================================================
CREATE TABLE IF NOT EXISTS sessoes_whatsapp (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone           TEXT UNIQUE NOT NULL,
  step            INTEGER DEFAULT 0,
  dados_candidato JSONB DEFAULT '{}',
  ativo           BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessoes_phone ON sessoes_whatsapp(phone);
CREATE INDEX IF NOT EXISTS idx_sessoes_ativo ON sessoes_whatsapp(ativo);

-- ============================================================
-- TABELA: analytics_triagem
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics_triagem (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canal             TEXT, -- 'whatsapp', 'email', 'output_shortlist'
  candidato_email   TEXT,
  vaga_id           UUID,
  vaga_titulo       TEXT,
  status_triagem    TEXT,
  score_final       DECIMAL(5, 2),
  dentro_raio       BOOLEAN,
  total_avaliados   INTEGER,
  top3_scores       JSONB,
  tempo_ms          INTEGER, -- tempo de processamento
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_canal ON analytics_triagem(canal);
CREATE INDEX IF NOT EXISTS idx_analytics_data ON analytics_triagem(created_at DESC);

-- ============================================================
-- FUNÇÃO: Updated_at automático
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers updated_at
CREATE TRIGGER set_updated_at_candidatos
  BEFORE UPDATE ON candidatos
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_vagas
  BEFORE UPDATE ON vagas
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_sessoes
  BEFORE UPDATE ON sessoes_whatsapp
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- FUNÇÃO: Busca vetorial semântica de candidatos
-- ============================================================
CREATE OR REPLACE FUNCTION buscar_candidatos_similares(
  embedding_query vector(1536),
  limite INTEGER DEFAULT 20,
  score_minimo DECIMAL DEFAULT 0.6
)
RETURNS TABLE (
  id UUID,
  nome TEXT,
  email TEXT,
  whatsapp TEXT,
  cargo_desejado TEXT,
  score_medio DECIMAL,
  distancia_sede_km DECIMAL,
  status TEXT,
  similaridade DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id, c.nome, c.email, c.whatsapp, c.cargo_desejado,
    c.score_medio, c.distancia_sede_km, c.status,
    (1 - (c.embedding_perfil <=> embedding_query))::DECIMAL AS similaridade
  FROM candidatos c
  WHERE c.status IN ('ativo', 'qualificado', 'banco_espera')
    AND c.embedding_perfil IS NOT NULL
    AND (1 - (c.embedding_perfil <=> embedding_query)) >= score_minimo
  ORDER BY similaridade DESC
  LIMIT limite;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- FUNÇÃO: Purge LGPD (candidatos descartados há > 6 meses)
-- ============================================================
CREATE OR REPLACE FUNCTION purge_lgpd()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM candidatos
  WHERE status = 'descartado'
    AND updated_at < NOW() - INTERVAL '6 months';
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- RLS (Row Level Security) — Segurança por tenant
-- ============================================================
ALTER TABLE candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE vagas ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidaturas ENABLE ROW LEVEL SECURITY;

-- Policy: Service Role tem acesso total (usado pelo n8n)
CREATE POLICY "service_role_all_candidatos" ON candidatos
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_vagas" ON vagas
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_candidaturas" ON candidaturas
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all_sessoes" ON sessoes_whatsapp
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================
-- DADOS DE EXEMPLO (opcional — remova em produção)
-- ============================================================
-- INSERT INTO vagas (titulo, empresa, responsavel_email, endereco_sede, raio_maximo_km,
--   requisitos_obrigatorios, regime, salario_min, salario_max)
-- VALUES (
--   'Auxiliar Administrativo', 'Empresa Exemplo S.A.', 'rh@empresa.com',
--   'Rua das Flores, 123, Centro, São Paulo, SP, 01310-100', 15,
--   '["Ensino Médio Completo", "Excel Básico", "6 meses de experiência"]',
--   'CLT', 1800, 2200
-- );

-- ============================================================
-- VIEWS úteis para dashboard
-- ============================================================
CREATE OR REPLACE VIEW vw_dashboard_rh AS
SELECT
  (SELECT COUNT(*) FROM candidatos WHERE status = 'qualificado') AS candidatos_qualificados,
  (SELECT COUNT(*) FROM candidatos WHERE status = 'banco_espera') AS candidatos_espera,
  (SELECT COUNT(*) FROM candidatos WHERE status = 'contratado') AS candidatos_contratados,
  (SELECT COUNT(*) FROM candidatos WHERE status = 'fora_raio') AS candidatos_fora_raio,
  (SELECT COUNT(*) FROM vagas WHERE status = 'aberta') AS vagas_abertas,
  (SELECT COUNT(*) FROM vagas WHERE status = 'em_selecao') AS vagas_em_selecao,
  (SELECT ROUND(AVG(score_medio), 1) FROM candidatos WHERE status IN ('qualificado', 'banco_espera')) AS score_medio_banco,
  (SELECT COUNT(*) FROM analytics_triagem WHERE created_at > NOW() - INTERVAL '24 hours') AS triagens_hoje,
  (SELECT COUNT(*) FROM analytics_triagem WHERE canal = 'whatsapp' AND created_at > NOW() - INTERVAL '7 days') AS triagens_whatsapp_semana,
  (SELECT COUNT(*) FROM analytics_triagem WHERE canal = 'email' AND created_at > NOW() - INTERVAL '7 days') AS triagens_email_semana;

-- ============================================================
-- FIM DO SETUP
-- Execute: psql ou Supabase SQL Editor
-- ============================================================
