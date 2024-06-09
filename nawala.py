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
from nordvpn_connect import initialize_VPN, connect_VPN, disconnect_VPN

# Ambil nilai variabel lingkungan untuk nama pengguna dan kata sandi NordVPN
nordvpn_username = os.environ.get('NORDVPN_USERNAME')
nordvpn_password = os.environ.get('NORDVPN_PASSWORD')

# Token bot Telegram
TOKEN = "6845337341:AAEElZtlJI8-F-GBccePGhrroS4Fc_Y8CbI"

# Fungsi untuk menghubungkan ke VPN NordVPN
def connect_to_vpn():
    # Inisialisasi VPN
    initialize_VPN()

    # Hubungkan ke server NordVPN yang berlokasi di Indonesia
    connect_VPN('Indonesia')

# Fungsi untuk memutuskan koneksi VPN NordVPN
def disconnect_from_vpn():
    # Putuskan koneksi VPN
    disconnect_VPN()

# Fungsi untuk memeriksa status blokir di TrustPositif
def check_trustpositif(domain):
    url = "https://trustpositif.kominfo.go.id/cek-site"
    data = {'search': domain}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.post(url, data=data, headers=headers, verify=certifi.where())
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            result = soup.find('div', class_='well')
            if result:
                if 'diblokir' in result.text.lower():
                    return True  # Domain diblokir
                else:
                    return False  # Domain tidak diblokir
            else:
                return "Tidak dapat menemukan status blokir pada halaman."
        elif response.status_code == 403:
            return "Error: Access forbidden (403). Please check if the domain is accessible."
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk membaca data domain dari Google Sheets
def read_sheets(sheet_id, range_name):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = 'nawala.json'
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
        return values
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk memeriksa semua domain dari Google Sheets dan mengirim notifikasi jika ada yang terblokir
def check_and_notify(context: CallbackContext):
    chat_id = -4220207549
    sheet_id = '1Gs9m6Ti2fErBbRH6egpksMtHg5unqOGYm0HgBArjp9Y'
    range_name = 'Sheet27!A1:A1000'
    domains = read_sheets(sheet_id, range_name)
    if not domains:
        context.bot.send_message(chat_id=chat_id, text='Tidak ada data domain di Google Sheets.')
        return
    results = []
    for row in domains:
        if row:
            domain = row[0]
            status = check_trustpositif(domain)
            if status is True:
                results.append(f'{domain} diblokir oleh TrustPositif.')
            elif status is False:
                results.append(f'{domain} tidak diblokir oleh TrustPositif.')
            else:
                results.append(f'{domain}: {status}')
    response_message = '\n'.join(results)
    context.bot.send_message(chat_id=chat_id, text=response_message)

# Fungsi untuk memulai bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Halo! Kirimkan /cek <domain> untuk memeriksa apakah domain tersebut diblokir atau /ceksemua untuk memeriksa semua domain dalam Google Sheet.')

# Fungsi untuk memeriksa domain
def cek(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text('Penggunaan: /cek <domain>')
        return
    domain = context.args[0]
    status = check_trustpositif(domain)
    if status is True:
        update.message.reply_text(f'Domain {domain} diblokir oleh TrustPositif.')
    elif status is False:
        update.message.reply_text(f'Domain {domain} tidak diblokir oleh TrustPositif.')
    else:
        update.message.reply_text(status)


# Function to get chat ID
def get_chat_id(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text(f'Your chat ID is {chat_id}')

# Fungsi utama untuk menjalankan bot
def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Connect to NordVPN
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

    # Disconnect from NordVPN when bot is stopped
    disconnect_from_vpn()

if __name__ == '__main__':
    main()
