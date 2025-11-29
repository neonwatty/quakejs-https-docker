# A https friendly docker image for quakejs

This repo contains a Dockerfile and associated files to conveniently package [quakejs](https://github.com/begleysm/quakejs) for easy https-friendly deployment.

A pre-built image for both linux/amd64 and linux/arm64 can be [found here](https://github.com/users/neonwatty/packages/container/package/quakejs-https).

This image is used as the base for a [convenient https deployment strategy using kamal 2](https://github.com/neonwatty/kamal-quake).

Parts of this Docker pattern were inspired by this great http-friendly [docker image for quakejs](https://github.com/treyyoder/quakejs-docker).


## Build and setup

To build the image cd into the main repo and

```bash
docker build . -t quakejs-https
```

Then run with

```bash
docker run -it -p 80:80 -p 27961:27961 -e SERVER=127.0.0.1 -e HTTP_PORT=80 quakejs-https
```

However because there are no certs (to be handled by kamal) you will only see the JS logo screen.

To use the image and see its current capabilities you will need to deploy (to localhost even) using [the current kamal setup](https://github.com/neonwatty/kamal-quake).

## HTTPS Multiplayer with Kamal 2

This image supports secure WebSocket (WSS) multiplayer when deployed with Kamal 2. The WSS proxy automatically starts when SSL certificates are available.

### Architecture

```
Browser → HTTPS (443) → kamal-proxy → Apache (80) → Game assets
Browser → WSS (27961) → wssproxy → Game server (27960, internal)
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVER` | Your domain name | `kamal-quake.xyz` |
| `HTTP_PORT` | Web server port (usually 80) | `80` |
| `GAME_PORT` | WSS proxy port for multiplayer | `27961` |

### Kamal deploy.yml Example

```yaml
service: quakejs
image: yourname/quakejs-https

servers:
  web:
    hosts:
      - YOUR_VPS_IP
    options:
      publish:
        - "27961:27961"  # WSS proxy port

volumes:
  - "/root/.local/share/kamal-proxy/ssl:/etc/ssl/kamal:ro"

proxy:
  ssl: true
  host: your-domain.xyz
  app_port: 80
  healthcheck:
    interval: 3
    path: /
    timeout: 10

env:
  SERVER: your-domain.xyz
  HTTP_PORT: 80
  GAME_PORT: 27961

registry:
  server: ghcr.io
  username: yourname
  password:
    - GITHUB_REGISTRY_TOKEN

builder:
  arch: amd64
  context: .
  dockerfile: Dockerfile

ssh:
  user: ubuntu
  keys:
    - ~/.ssh/your-key.pem
```

### Key Configuration Points

1. **Port Publishing**: Publish port 27961 for the WSS proxy
2. **SSL Volume Mount**: Mount kamal-proxy's SSL certs to `/etc/ssl/kamal`
3. **GAME_PORT**: Set to `27961` so the game client connects to the WSS proxy
4. **Domain**: The SSL certificates must match your `SERVER` domain

### How It Works

1. Kamal-proxy handles SSL termination for HTTPS on port 443
2. The container runs Apache on port 80 for game assets
3. When SSL certs are detected at `/etc/ssl/kamal/certs/${SERVER}/`, the WSS proxy starts on port 27961
4. The WSS proxy terminates TLS and forwards to the internal game server on port 27960
5. The game client is configured to connect to `wss://your-domain:27961` for multiplayer

### Deploying

```bash
# First time setup
kamal setup

# Subsequent deployments
kamal deploy
```

After deployment, visit `https://your-domain.xyz` to play Quake 3 in your browser with secure multiplayer!
