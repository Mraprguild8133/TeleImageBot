// Telegram Bot Webhook Manager JavaScript

class BotManager {
    constructor() {
        this.apiBase = '/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Webhook form submission
        document.getElementById('webhook-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.setWebhook();
        });

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(e.target.getAttribute('href'));
            });
        });
    }

    async loadInitialData() {
        await this.refreshBotStatus();
        await this.getWebhookInfo();
        await this.loadActivityLog();
    }

    startStatusUpdates() {
        // Update status every 30 seconds
        setInterval(() => {
            this.refreshBotStatus();
        }, 30000);

        // Update activity log every 60 seconds
        setInterval(() => {
            this.loadActivityLog();
        }, 60000);
    }

    async refreshBotStatus() {
        try {
            const response = await fetch(`${this.apiBase}/bot/status`);
            const data = await response.json();
            
            this.updateBotStatus(data);
        } catch (error) {
            console.error('Failed to refresh bot status:', error);
            this.updateBotStatus({
                status: 'error',
                message: 'Failed to connect to bot',
                uptime: '--'
            });
        }
    }

    updateBotStatus(data) {
        const statusElement = document.getElementById('bot-status');
        const modeElement = document.getElementById('bot-mode');
        const lastUpdateElement = document.getElementById('last-update');
        const uptimeElement = document.getElementById('uptime');
        const imagesProcessedElement = document.getElementById('images-processed');
        const activeUsersElement = document.getElementById('active-users');

        // Update status badge
        statusElement.className = 'badge';
        if (data.status === 'running') {
            statusElement.classList.add('bg-success');
            statusElement.textContent = 'Running';
        } else if (data.status === 'stopped') {
            statusElement.classList.add('bg-danger');
            statusElement.textContent = 'Stopped';
        } else {
            statusElement.classList.add('bg-warning');
            statusElement.textContent = 'Unknown';
        }

        // Update other fields
        modeElement.textContent = data.mode || 'Polling';
        lastUpdateElement.textContent = new Date().toLocaleTimeString();
        uptimeElement.textContent = data.uptime || '--';
        imagesProcessedElement.textContent = data.images_processed || '--';
        activeUsersElement.textContent = data.active_users || '--';
    }

    async setWebhook() {
        const url = document.getElementById('webhook-url').value;
        const secretToken = document.getElementById('secret-token').value;
        const dropPendingUpdates = document.getElementById('drop-pending-updates').checked;

        if (!url) {
            this.showError('Please enter a webhook URL');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/webhook/set`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    secret_token: secretToken || null,
                    drop_pending_updates: dropPendingUpdates
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Webhook set successfully!');
                await this.getWebhookInfo();
                this.logActivity('Webhook set', `URL: ${url}`, 'success');
            } else {
                this.showError(result.message || 'Failed to set webhook');
                this.logActivity('Webhook set failed', result.message, 'error');
            }
        } catch (error) {
            this.showError('Error setting webhook: ' + error.message);
            this.logActivity('Webhook error', error.message, 'error');
        }
    }

    async deleteWebhook() {
        if (!confirm('Are you sure you want to delete the webhook? This will switch the bot back to polling mode.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/webhook/delete`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Webhook deleted successfully!');
                await this.getWebhookInfo();
                this.logActivity('Webhook deleted', 'Switched to polling mode', 'info');
            } else {
                this.showError(result.message || 'Failed to delete webhook');
            }
        } catch (error) {
            this.showError('Error deleting webhook: ' + error.message);
        }
    }

    async getWebhookInfo() {
        try {
            const response = await fetch(`${this.apiBase}/webhook/info`);
            const data = await response.json();
            
            this.displayWebhookInfo(data);
        } catch (error) {
            console.error('Failed to get webhook info:', error);
            this.displayWebhookInfo({
                has_custom_certificate: false,
                pending_update_count: 0,
                url: null
            });
        }
    }

    displayWebhookInfo(data) {
        const webhookInfoElement = document.getElementById('webhook-info');
        
        if (data.url) {
            webhookInfoElement.innerHTML = `
                <div class="col-md-6">
                    <h6><i class="bi bi-link-45deg text-success"></i> Webhook Active</h6>
                    <p><strong>URL:</strong><br><code class="webhook-url">${data.url}</code></p>
                    <p><strong>Has Certificate:</strong> ${data.has_custom_certificate ? 'Yes' : 'No'}</p>
                </div>
                <div class="col-md-6">
                    <h6><i class="bi bi-clock text-info"></i> Status</h6>
                    <p><strong>Pending Updates:</strong> ${data.pending_update_count}</p>
                    <p><strong>Last Error:</strong> ${data.last_error_message || 'None'}</p>
                    <p><strong>Max Connections:</strong> ${data.max_connections || 'Default'}</p>
                </div>
            `;
        } else {
            webhookInfoElement.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> No webhook configured. Bot is running in polling mode.
                    </div>
                </div>
            `;
        }
    }

    generateWebhookUrl() {
        const domain = window.location.host;
        const protocol = window.location.protocol;
        const suggestedUrl = `${protocol}//${domain}/webhook`;
        
        document.getElementById('webhook-url').value = suggestedUrl;
    }

    generateSecretToken() {
        // Generate a random secret token
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < 32; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        document.getElementById('secret-token').value = result;
    }

    async loadActivityLog() {
        try {
            const response = await fetch(`${this.apiBase}/activity/recent`);
            const activities = await response.json();
            
            this.displayActivityLog(activities);
        } catch (error) {
            console.error('Failed to load activity log:', error);
            this.displayActivityLog([]);
        }
    }

    displayActivityLog(activities) {
        const activityLogElement = document.getElementById('activity-log');
        
        if (activities.length === 0) {
            activityLogElement.innerHTML = `
                <div class="text-muted text-center">
                    <i class="bi bi-clock-history"></i> No recent activities
                </div>
            `;
            return;
        }

        const activitiesHtml = activities.map(activity => `
            <div class="activity-item ${activity.type}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${activity.action}</strong>
                        <p class="mb-1">${activity.details}</p>
                    </div>
                    <small class="activity-timestamp">${this.formatTimestamp(activity.timestamp)}</small>
                </div>
            </div>
        `).join('');

        activityLogElement.innerHTML = activitiesHtml;
    }

    logActivity(action, details, type = 'info') {
        // Add activity to local log (in a real implementation, this would be sent to server)
        const activity = {
            action,
            details,
            type,
            timestamp: new Date().toISOString()
        };
        
        console.log('Activity logged:', activity);
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }

    switchSection(sectionId) {
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        document.querySelector(`[href="${sectionId}"]`).classList.add('active');
        
        // Show/hide sections (in a more complex app, this would route to different views)
        console.log(`Switching to section: ${sectionId}`);
    }

    showSuccess(message) {
        document.getElementById('success-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        modal.show();
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
}

// Global functions for button clicks
function refreshStatus() {
    window.botManager.refreshBotStatus();
}

function generateWebhookUrl() {
    window.botManager.generateWebhookUrl();
}

function generateSecretToken() {
    window.botManager.generateSecretToken();
}

function deleteWebhook() {
    window.botManager.deleteWebhook();
}

function getWebhookInfo() {
    window.botManager.getWebhookInfo();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.botManager = new BotManager();
});