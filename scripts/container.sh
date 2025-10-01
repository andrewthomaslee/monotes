#!/usr/bin/env bash
set -e  # Exit on any error
# Immediately exit if REPO_ROOT is not set
if [ -z "$REPO_ROOT" ]; then
    echo "Error: REPO_ROOT is not set. Run this script from the Nix devShell."
    exit 1
fi
cd $REPO_ROOT

# Simple script to build, load, and run Docker image with Nix
# 1. Build → 2. Load → 3. Run (with auto-cleanup)

echo "🚀 Building Docker image with Nix..."
nix build .#bff-demo-container

echo "📥 Loading image into Docker..."
IMAGE_TAG=$(docker load < result | grep -o 'bff-demo-container:[^ ]*')


SESSION_NAME="nixfastapi-container"

# Function to handle user choice when session exists
handle_existing_session() {
    echo "Tmux session 🚩'$SESSION_NAME'🚩 already exists!"
    echo ""
    echo "What would you like to do?"
    echo "1) Kill existing session and create new one"
    echo "2) Attach to existing session"
    echo "3) Cancel operation"
    echo ""

    while true; do
        read -p "Enter choice (1/2/3): " choice
        case $choice in
            1)
                echo "Killing existing session..."
                if tmux kill-session -t $SESSION_NAME 2>/dev/null; then
                    echo "Session '$SESSION_NAME' killed successfully."
                    # Continue with script to create new session
                    return 0
                else
                    echo "Failed to kill session '$SESSION_NAME'."
                    exit 1
                fi
                ;;
            2)
                echo "Attaching to existing session..."
                tmux attach-session -t $SESSION_NAME
                exit 0
                ;;
            3)
                echo "Operation cancelled."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
}

# If a session with this name already exists, ask user what to do
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    handle_existing_session
fi

docker network create --driver bridge dev-nixfastapi-network 2>/dev/null || true
docker pull mongo:8.0.13

tmux new-session -d -s $SESSION_NAME -n "🪵_Lazydocker" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:0 "lazydocker" C-m

tmux new-window -t $SESSION_NAME -n "🥭_MongoDB" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:1 "docker run --rm --network dev-nixfastapi-network -v ./data/mongo:/data/db --name mongo mongo:8.0.13 | jq" C-m

tmux new-window -t $SESSION_NAME -n "📦_Container" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:2 "docker run --rm --network dev-nixfastapi-network -p 7999:7999 --env DB_URI=mongodb://mongo --env FAKE_DATA=True "$IMAGE_TAG"" C-m

tmux new-window -t $SESSION_NAME -n "🌐_Chrome" -c "$REPO_ROOT"
tmux send-keys -t $SESSION_NAME:3 "chromium --user-data-dir=/tmp/chrome-dev --new-window --incognito --disable-cache --disk-cache-size=0 --media-cache-size=0 --remote-debugging-port=9222 http://0.0.0.0:7999" C-m

echo "Tmux created session ✨'$SESSION_NAME'✨"
tmux attach-session -t $SESSION_NAME