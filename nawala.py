import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from google.oauth2 import service_account
from googleapiclient.discovery import build
import schedule
import time
import certifi
import logging
from openvpn_api import Client

# Informasi koneksi OpenVPN
OPENVPN_CONFIG_FILE = "path/to/your/openvpn/config/file.ovpn"
OPENVPN_USERNAME = "your_openvpn_username"
OPENVPN_PASSWORD = "your_openvpn_password"

# Fungsi untuk menghubungkan ke VPN menggunakan OpenVPN
def connect_to_vpn():
    client = Client("localhost", port=1337)  # Sesuaikan dengan port OpenVPN API
    client.connect(OPENVPN_CONFIG_FILE)
    client.login(OPENVPN_USERNAME, OPENVPN_PASSWORD)

# Fungsi untuk memutuskan koneksi VPN
def disconnect_from_vpn():
    client = Client("localhost", port=1337)  # Sesuaikan dengan port OpenVPN API
    client.disconnect()

# Fungsi utama untuk menjalankan bot
def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Connect to VPN
    connect_to_vpn()

    # Inisialisasi updater
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("cek", cek))
    dispatcher.add_handler(CommandHandler("ceksemua", check_and_notify))
    dispatcher.add_handler(CommandHandler("getchatid", get_chat_id))

    logger.info("Starting the bot...")
    updater.start_polling()

    # Schedule checking every 5 minutes
    job_queue = updater.job_queue
    job_queue.run_repeating(check_and_notify, interval=300, first=0, context='-4220207549')

    logger.info("Bot is running. Press Ctrl+C to stop.")
    updater.idle()

    # Disconnect from VPN when bot is stopped
    disconnect_from_vpn()

if __name__ == '__main__':
    main()
