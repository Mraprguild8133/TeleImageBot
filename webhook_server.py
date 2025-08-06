#!/usr/bin/env python3
"""
Flask web server for Telegram Bot webhook management and status monitoring.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory
from telegram import Bot
from telegram.error import TelegramError
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = None

# Web Service 
PORT = os.getenv("PORTS")
# Statistics tracking
stats = {
    'start_time': datetime.now(),
    'images_processed': 0,
    'active_users': set(),
    'recent_activities': []
}

def get_bot_instance():
    """Get or create bot instance."""
    global bot
    if bot is None and BOT_TOKEN:
        bot = Bot(token=BOT_TOKEN)
    return bot

def add_activity(action, details, activity_type='info'):
    """Add activity to recent activities log."""
    activity = {
        'action': action,
        'details': details,
        'type': activity_type,
        'timestamp': datetime.now().isoformat()
    }
    
    stats['recent_activities'].insert(0, activity)
    # Keep only last 50 activities
    stats['recent_activities'] = stats['recent_activities'][:50]

@app.route('/')
def index():
    """Serve the main dashboard."""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/api/bot/status')
def bot_status():
    """Get current bot status."""
    try:
        bot_instance = get_bot_instance()
        if bot_instance is None:
            return jsonify({
                'status': 'error',
                'message': 'Bot token not configured',
                'uptime': '0s'
            })
        
        # Try to get bot info to verify connection
        asyncio.run(bot_instance.get_me())
        
        uptime = datetime.now() - stats['start_time']
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        return jsonify({
            'status': 'running',
            'mode': 'polling',  # You can detect this based on webhook status
            'uptime': uptime_str,
            'images_processed': stats['images_processed'],
            'active_users': len(stats['active_users']),
            'message': 'Bot is running normally'
        })
        
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Telegram API error: {str(e)}',
            'uptime': '0s'
        })
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'uptime': '0s'
        })

@app.route('/api/webhook/info')
def webhook_info():
    """Get current webhook information."""
    try:
        bot_instance = get_bot_instance()
        if bot_instance is None:
            return jsonify({'error': 'Bot not configured'})
        
        webhook_info = asyncio.run(bot_instance.get_webhook_info())
        
        return jsonify({
            'url': webhook_info.url,
            'has_custom_certificate': webhook_info.has_custom_certificate,
            'pending_update_count': webhook_info.pending_update_count,
            'last_error_date': webhook_info.last_error_date.isoformat() if webhook_info.last_error_date else None,
            'last_error_message': webhook_info.last_error_message,
            'max_connections': webhook_info.max_connections,
            'allowed_updates': webhook_info.allowed_updates
        })
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/webhook/set', methods=['POST'])
def set_webhook():
    """Set webhook URL."""
    try:
        data = request.get_json()
        url = data.get('url')
        secret_token = data.get('secret_token')
        drop_pending_updates = data.get('drop_pending_updates', False)
        
        if not url:
            return jsonify({'success': False, 'message': 'URL is required'})
        
        bot_instance = get_bot_instance()
        if bot_instance is None:
            return jsonify({'success': False, 'message': 'Bot not configured'})
        
        # Set webhook
        result = asyncio.run(bot_instance.set_webhook(
            url=url,
            secret_token=secret_token if secret_token else None,
            drop_pending_updates=drop_pending_updates
        ))
        
        if result:
            add_activity('Webhook Set', f'URL: {url}', 'success')
            return jsonify({'success': True, 'message': 'Webhook set successfully'})
        else:
            add_activity('Webhook Set Failed', f'URL: {url}', 'error')
            return jsonify({'success': False, 'message': 'Failed to set webhook'})
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        add_activity('Webhook Error', str(e), 'error')
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/webhook/delete', methods=['DELETE'])
def delete_webhook():
    """Delete webhook (switch to polling)."""
    try:
        bot_instance = get_bot_instance()
        if bot_instance is None:
            return jsonify({'success': False, 'message': 'Bot not configured'})
        
        result = asyncio.run(bot_instance.delete_webhook())
        
        if result:
            add_activity('Webhook Deleted', 'Switched to polling mode', 'info')
            return jsonify({'success': True, 'message': 'Webhook deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete webhook'})
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/activity/recent')
def recent_activities():
    """Get recent activities."""
    return jsonify(stats['recent_activities'])

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming webhook updates from Telegram."""
    try:
        update_data = request.get_json()
        
        # Log the webhook call
        add_activity('Webhook Received', 'Update received from Telegram', 'info')
        
        # Here you would process the update
        # For now, we'll just acknowledge it
        logger.info(f"Received webhook update: {update_data}")
        
        return '', 200
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        add_activity('Webhook Error', str(e), 'error')
        return '', 500

# Statistics update functions
def increment_processed_images():
    """Increment processed images counter."""
    stats['images_processed'] += 1

def add_active_user(user_id):
    """Add user to active users set."""
    stats['active_users'].add(user_id)

def cleanup_old_activities():
    """Cleanup old activities periodically."""
    while True:
        time.sleep(3600)  # Run every hour
        cutoff_time = datetime.now() - timedelta(hours=24)
        stats['recent_activities'] = [
            activity for activity in stats['recent_activities']
            if datetime.fromisoformat(activity['timestamp']) > cutoff_time
        ]

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_activities, daemon=True)
    cleanup_thread.start()
    
    # Add startup activity
    add_activity('Server Started', 'Webhook server initialized', 'success')
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
