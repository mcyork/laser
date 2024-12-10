#!/bin/bash

# Exit on error
set -e

# Configuration
STATIC_DIR="app/static"
mkdir -p "$STATIC_DIR"/{css,js,socket.io}

# Determine platform and architecture
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "Setting up static assets for $PLATFORM on $ARCH..."

# Get appropriate Tailwind binary URL
case "$PLATFORM" in
    "Darwin")  # macOS
        if [[ "$ARCH" == "arm64" ]]; then
            TAILWIND_URL="https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64"
        else
            TAILWIND_URL="https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64"
        fi
        ;;
    "Linux")
        if [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
            TAILWIND_URL="https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-arm64"
        else
            TAILWIND_URL="https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64"
        fi
        ;;
    *)
        echo "Unsupported platform: $PLATFORM"
        exit 1
        ;;
esac

# Download Tailwind CSS
echo "Downloading Tailwind CSS..."
curl -L "$TAILWIND_URL" -o tailwindcss
chmod +x tailwindcss

# Download Socket.IO client
echo "Downloading Socket.IO client..."
curl -L "https://cdn.socket.io/4.7.2/socket.io.min.js" -o "$STATIC_DIR/socket.io/socket.io.js"

# Create base CSS file
cat > "$STATIC_DIR/css/base.css" << EOF
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
.laser-status .indicator {
    transition: background-color 0.3s ease;
}

.laser-status.broken .indicator {
    background-color: theme('colors.red.500');
}
EOF

# Create Tailwind config
cat > "tailwind.config.js" << EOF
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# Build Tailwind CSS
./tailwindcss -i "$STATIC_DIR/css/base.css" -o "$STATIC_DIR/css/tailwind.min.css" --minify -c tailwind.config.js

# Create custom CSS
cat > "$STATIC_DIR/css/laser_maze.css" << EOF
/* Add any custom styles here */
.laser-status {
    transition: all 0.3s ease;
}

#timer {
    text-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
}
EOF

# Create JavaScript file with Socket.IO support
cat > "$STATIC_DIR/js/laser_maze.js" << EOF
let socket = null;

function connectSocket() {
    socket = io({
        path: '/socket.io'
    });
    
    socket.on('connect', function() {
        console.log('Socket.IO connected');
    });
    
    socket.on('laser_event', function(data) {
        handleGameEvent(data);
    });
    
    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected');
        setTimeout(connectSocket, 1000);
    });
}

function handleGameEvent(data) {
    if (data.type === 'laser_break') {
        const laserElement = document.querySelector(\`[data-laser="\${data.laser}"]\`);
        if (laserElement) {
            laserElement.classList.add('broken');
        }
    }
}

document.addEventListener('DOMContentLoaded', connectSocket);
EOF

# Clean up
rm tailwindcss

echo "Static assets setup complete for $PLATFORM on $ARCH!"