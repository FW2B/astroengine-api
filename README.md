# AstroEngine API

Motor de cálculo astrológico de alta precisão baseado na **Swiss Ephemeris**, desenvolvido pela **FW2B - Frameworks to Business**.

## Visão Geral

A AstroEngine API é um serviço RESTful conteinerizado que fornece cálculos astrológicos de alta precisão, incluindo mapas natais completos, sinastria, trânsitos e mapas compostos. Serve como backend de cálculo para o **Cosmic Suite**, o **Humanaize** e outras aplicações.

## Funcionalidades

- **Mapa Natal Completo:** 10 corpos celestes, Ascendente, Meio do Céu, 12 casas e aspectos natais
- **Sinastria:** Comparação inter-cartas entre duas pessoas
- **Trânsitos:** Posições planetárias atuais em relação a um mapa natal
- **Mapa Composto:** Pontos médios entre duas pessoas
- **Posições Atuais:** Posições planetárias em tempo real
- **7 Sistemas de Casas:** Placidus, Koch, Porphyrius, Regiomontanus, Campanus, Equal, Whole Sign

## Início Rápido

### Com Docker Compose (recomendado)

```bash
# Clonar o repositório
git clone https://github.com/FW2B/astroengine-api.git
cd astroengine-api

# Copiar e configurar variáveis de ambiente
cp .env.example .env

# Construir e iniciar
docker compose up -d

# Verificar se está rodando
curl http://localhost:8000/health
```

### Com Docker

```bash
docker build -t astroengine-api .
docker run -d -p 8000:8000 --name astroengine-api --restart always astroengine-api
```

### Desenvolvimento Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Documentação da API

Após iniciar o serviço, acesse:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/natal_chart` | Calcula o mapa astral natal completo |
| POST | `/synastry` | Realiza sinastria entre duas pessoas |
| POST | `/transits` | Calcula trânsitos planetários |
| POST | `/composite` | Gera o mapa composto |
| GET | `/planets/now` | Posições planetárias atuais |
| GET | `/health` | Health check |
| GET | `/source` | Link para o código-fonte (AGPL) |

## Exemplos de Uso

### Mapa Natal

```bash
curl -X POST http://localhost:8000/natal_chart \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-cosmic-suite" \
  -d '{
    "name": "Maria Silva",
    "birth_datetime_utc": "1990-03-15T14:30:00Z",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

### Sinastria

```bash
curl -X POST http://localhost:8000/synastry \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-cosmic-suite" \
  -d '{
    "person1": {
      "name": "Maria",
      "birth_datetime_utc": "1990-03-15T14:30:00Z",
      "latitude": -23.5505,
      "longitude": -46.6333
    },
    "person2": {
      "name": "João",
      "birth_datetime_utc": "1988-07-20T10:00:00Z",
      "latitude": -22.9068,
      "longitude": -43.1729
    }
  }'
```

### Posições Atuais

```bash
curl http://localhost:8000/planets/now \
  -H "X-API-Key: dev-key-cosmic-suite"
```

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `PORT` | Porta da API | `8000` |
| `LOG_LEVEL` | Nível de logging | `INFO` |
| `API_KEYS` | Chaves de API (separadas por vírgula) | `dev-key-cosmic-suite` |
| `ALLOWED_ORIGINS` | Origens CORS permitidas | `*` |
| `DEFAULT_HOUSE_SYSTEM` | Sistema de casas padrão | `placidus` |
| `DEFAULT_ORB_CONJUNCTION` | Orbe para conjunção (graus) | `8.0` |
| `DEFAULT_ORB_OPPOSITION` | Orbe para oposição (graus) | `8.0` |
| `DEFAULT_ORB_TRINE` | Orbe para trígono (graus) | `8.0` |
| `DEFAULT_ORB_SQUARE` | Orbe para quadratura (graus) | `7.0` |
| `DEFAULT_ORB_SEXTILE` | Orbe para sextil (graus) | `6.0` |

## Licença

Este software é licenciado sob a **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Isso significa que:
- Você pode usar, modificar e distribuir este software livremente.
- Se você modificar e disponibilizar este software como um serviço de rede, deve disponibilizar o código-fonte completo das suas modificações sob a mesma licença.
- Consulte o arquivo [LICENSE](LICENSE) para o texto completo da licença.

### Swiss Ephemeris

Este software utiliza a biblioteca **Swiss Ephemeris** de Astrodienst AG, Suíça. Consulte [NOTICE.md](NOTICE.md) para detalhes.

## Desenvolvido por

**FW2B - Frameworks to Business**
