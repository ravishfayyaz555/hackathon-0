const API_URL = 'http://localhost:8000/api/status';

async function updateDashboard() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Update Status
        document.getElementById('system-status').innerText = data.status;
        
        // Update Revenue
        const revenueEl = document.getElementById('revenue');
        revenueEl.innerText = data.revenue;
        
        const reachPercent = data.reach; // Expected something like "25%"
        document.getElementById('reach-percent').innerText = reachPercent;
        document.getElementById('revenue-progress').style.width = reachPercent;

        // Update Heartbeat
        document.getElementById('last-heartbeat').innerText = data.heartbeat;
        
        // Update Tier
        document.getElementById('system-tier').innerText = data.tier;
        
        // Update Pending Actions
        document.getElementById('pending-count').innerText = data.pending_approvals;

        // Update KPIs
        document.getElementById('response-time').innerText = data.response_time;
        document.getElementById('payment-rate').innerText = data.payment_rate;

        // Update Activity Log
        const logContainer = document.getElementById('activity-log');
        logContainer.innerHTML = '';
        if (data.activity && data.activity.length > 0) {
            data.activity.forEach(msg => {
                const li = document.createElement('li');
                li.innerText = msg;
                logContainer.appendChild(li);
            });
        } else {
            logContainer.innerHTML = '<li>No recent activity logged.</li>';
        }

    } catch (err) {
        console.error('Failed to fetch dashboard status:', err);
        document.getElementById('system-status').innerText = 'Offline (Check Terminal)';
        document.getElementById('system-status').parentElement.querySelector('.pulse').style.background = '#ff4b4b';
        document.getElementById('system-status').parentElement.querySelector('.pulse').style.boxShadow = '0 0 10px #ff4b4b';
    }
}

// Initial update
updateDashboard();

// Poll every 10 seconds
setInterval(updateDashboard, 10000);
