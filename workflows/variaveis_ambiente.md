# Variáveis de Ambiente — n8n

Configure em: **Settings → Variables** no n8n

## APIs Obrigatórias

| Variável | Descrição | Onde obter |
|---|---|---|
| `ANTHROPIC_API_KEY` | Chave da API Claude (Anthropic) | console.anthropic.com |
| `GOOGLE_MAPS_API_KEY` | Chave Google Maps (Geocoding + Distance Matrix) | console.cloud.google.com |
| `EVOLUTION_API_URL` | URL da sua Evolution API (ex: `https://evolution.seudominio.com`) | Self-hosted |
| `EVOLUTION_API_KEY` | Chave da Evolution API | Config da sua instância |
| `EVOLUTION_INSTANCE` | Nome da instância WhatsApp | Config da sua instância |

## Supabase

| Variável | Descrição |
|---|---|
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_SERVICE_KEY` | Service Role Key (Settings → API) |

> **Credenciais no n8n:** Crie uma credencial `Supabase API` com URL e Service Key. Use o ID da credencial nos nós Supabase (`SUPABASE_CREDENTIAL_ID`).

## E-mail (IMAP/SMTP)

| Variável | Descrição |
|---|---|
| `EMAIL_VAGAS` | E-mail de recebimento (ex: `vagas@empresa.com`) |

> **Credenciais no n8n:** Crie credenciais `IMAP` e `SMTP` separadas com os dados do seu provedor.

## Configurações da Empresa

| Variável | Descrição | Exemplo |
|---|---|---|
| `EMPRESA_NOME` | Nome da empresa | `Empresa Exemplo S.A.` |
| `ENDERECO_SEDE` | Endereço padrão da sede | `Rua das Flores, 123, São Paulo, SP` |
| `RAIO_MAXIMO_KM` | Raio padrão de distância | `15` |
| `EMAIL_RH` | E-mail do RH responsável | `rh@empresa.com` |
| `WHATSAPP_SUPORTE` | WhatsApp de suporte ao candidato | `(11) 99999-0000` |
| `N8N_BASE_URL` | URL base do seu n8n | `https://n8n.seudominio.com` |
| `PAINEL_URL` | URL do painel de gestão | `https://painel.empresa.com` |

## Credenciais a Criar no n8n

1. **Supabase API** (ID: `SUPABASE_CREDENTIAL_ID`)
   - URL do projeto Supabase
   - Service Role Key

2. **IMAP** (ID: `IMAP_CREDENTIAL_ID`)
   - Host, porta, usuário, senha do e-mail

3. **SMTP** (ID: `SMTP_CREDENTIAL_ID`)
   - Host, porta, usuário, senha do e-mail

4. **Google OAuth2** (para Google Calendar nos comandos APROVAR)
   - Criar via Google Cloud Console

## Ordem de Importação dos Workflows

1. `WF-05_Notify_Output.json` (webhooks de saída)
2. `WF-04_Matching_Engine.json` (depende do WF-05)
3. `WF-03_Cadastro_Vaga.json` (depende do WF-04)
4. `WF-02_Parsing_Email.json` (independente)
5. `WF-01_Onboarding_WhatsApp.json` (independente)

## Checklist de Configuração

- [ ] Executar `supabase_setup.sql` no Supabase SQL Editor
- [ ] Configurar todas as variáveis no n8n (Settings → Variables)
- [ ] Criar credenciais Supabase, IMAP, SMTP no n8n
- [ ] Importar workflows na ordem acima
- [ ] Substituir `SUPABASE_CREDENTIAL_ID`, `IMAP_CREDENTIAL_ID`, `SMTP_CREDENTIAL_ID` pelos IDs reais
- [ ] Ativar os workflows
- [ ] Configurar webhook da Evolution API apontando para WF-01 URL
- [ ] Testar fluxo completo com candidato de teste
