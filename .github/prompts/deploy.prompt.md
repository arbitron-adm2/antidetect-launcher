---
name: deploy
description: Deploy to server via SSH
mode: agent
tools:
  - runInTerminal
  - terminalLastCommand
  - fetch
---

# Deploy

## Config

Edit `.config/deploy.toml` with SSH credentials.

## Workflow

1. Run tests locally
2. Verify SSH: `ssh $USER@$HOST "echo ok"`
3. Deploy: `ssh $USER@$HOST "cd $PATH && git pull && ./deploy.sh"`
4. Check: `ssh $USER@$HOST "systemctl status $SERVICE"`
5. Logs: `ssh $USER@$HOST "journalctl -u $SERVICE -f"`

## Rollback

```bash
ssh $USER@$HOST "cd $PATH && git checkout HEAD~1 && ./deploy.sh"
```

## Checklist

- [ ] Tests pass
- [ ] SSH config filled
- [ ] Deployed
- [ ] Health OK
