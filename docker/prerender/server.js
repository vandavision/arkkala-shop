const prerender = require('prerender');

const server = prerender({
    chromeLocation: '/usr/bin/chromium-browser',
    chromeFlags: [
        '--no-sandbox',
        '--headless',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--disable-software-rasterizer',
        '--disable-setuid-sandbox',
        '--hide-scrollbars',
        '--mute-audio',
        '--remote-debugging-port=9222'
    ]
});

server.start();