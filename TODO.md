# TODO — tg

## Roadmap

### MCP Server
- [ ] Create `tg-mcp` MCP server — expose tg commands as MCP tools for Claude and other agents
  - [ ] `tg_send_bot` — send via bot from any agent
  - [ ] `tg_read_chat` — read conversations from any agent
  - [ ] `tg_user_send` — send as user from any agent
  - [ ] Streamable-HTTP transport (homelab deploy via Traefik)

### User API
- [ ] `tg user forward CHAT MSG_ID TARGET` — forward a message
- [ ] `tg user search QUERY` — global search across all chats
- [x] `tg user download CHAT MSG_ID` — download media from a message
- [ ] `tg user groups` — list groups with member counts
- [ ] `tg user channel CHANNEL` — channel-specific commands (posts, subscribers)

### Bot API
- [ ] `tg bot create` — guided bot creation via BotFather
- [ ] `tg bot stats` — message/user statistics (if analytics enabled)
- [ ] `tg bot broadcast MSG` — send to all known chats

### DX / Quality
- [ ] Shell completion (`tg --install-completion`)
- [ ] Config validation on startup (warn on missing TG_API_ID)
- [ ] `tg user sync` — force entity cache refresh
- [ ] Unit tests for Bot API layer (pytest + httpx mock)
- Mode Daemon / Watch (tg watch) : au lieu d'interroger la CLI à intervalles réguliers (tg updates), avoir une commande qui écoute le flux en live comme un tail -f des messages entrants.

- [ ] Scinder la logique lourde de Typer pour mieux organiser l'architecture (notamment si ajout de 10+ commandes plus tard).
