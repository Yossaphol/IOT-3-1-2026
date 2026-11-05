#!/bin/bash
cd ~/iot
S=iot
tmux kill-session -t $S 2>/dev/null
tmux new-session -d -s $S -n mcp "source venv/bin/activate && TUNNEL_HOST=wild-cloud-46e99bb6.tunnl.gg python mcp_server.py; bash"
tmux new-window -t $S -n api "source venv/bin/activate && uvicorn api:app --host 0.0.0.0 --port 8001; bash"
tmux new-window -t $S -n lora "source venv/bin/activate && python lora_bridge.py; bash"
tmux new-window -t $S -n tunnel "ssh -t -R 80:127.0.0.1:8000 stable@proxy.tunnl.gg; bash"
echo "เริ่มแล้ว ดูด้วย: tmux attach -t $S"