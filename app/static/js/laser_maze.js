let socket = null;

function connectSocket() {
    // Connect to Socket.IO server, explicitly setting transport
    socket = io({
        transports: ['websocket'],
        upgrade: false
    });
    
    socket.on('connect', function() {
        console.log('Socket.IO connected');
    });
    
    socket.on('laser_event', function(data) {
        console.log('Received laser event:', data);
        handleGameEvent(data);
    });
    
    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected');
        setTimeout(connectSocket, 1000);
    });
}

function handleGameEvent(data) {
    if (data.type === 'laser_break') {
        const laserElement = document.querySelector(`[data-laser="${data.laser}"]`);
        if (laserElement) {
            laserElement.classList.add('broken');
        }
    }
}

// Connect when the page loads
document.addEventListener('DOMContentLoaded', connectSocket);// app/static/js/laser_maze.js
let socket = null;

function connectSocket() {
    // Connect to the Socket.IO server with correct path
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
        setTimeout(connectSocket, 1000); // Reconnect attempt
    });
}

function handleGameEvent(data) {
    if (data.type === 'laser_break') {
        const laserElement = document.querySelector(`[data-laser="${data.laser}"]`);
        if (laserElement) {
            laserElement.classList.add('broken');
        }
    }
}

// Connect when the page loads
document.addEventListener('DOMContentLoaded', connectSocket);// app/static/js/laser_maze.js
let socket = null;

function connectSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Socket.IO connected');
    });
    
    socket.on('laser_event', function(data) {
        handleGameEvent(data);
    });
    
    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected');
    });
}

function handleGameEvent(data) {
    if (data.type === 'laser_break') {
        const laserElement = document.querySelector(`[data-laser="${data.laser}"]`);
        if (laserElement) {
            laserElement.classList.add('broken');
        }
    }
    // Add more event handlers as needed
}

// Connect when the page loads
document.addEventListener('DOMContentLoaded', connectSocket);