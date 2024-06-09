import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Token Bot Telegram
TOKEN = "6845337341:AAEElZtlJI8-F-GBccePGhrroS4Fc_Y8CbI"

# Fungsi untuk mengecek apakah situs web diblokir di Indonesia
def check_website(update: Update, context: CallbackContext):
    # Mendapatkan argumen yang dikirim oleh pengguna
    website = context.args[0]
    
    # URL untuk memeriksa blokir website menggunakan API Nawala
    url = f"https://apinawala.heryad.es/api/?action=check&url={website}"
    
    # Mengirim permintaan GET ke API Nawala
    response = requests.get(url)
    
    # Mengecek status kode HTTP
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            if result["blocked"]:
                message = f"Situs {website} diblokir di Indonesia."
            else:
                message = f"Situs {website} tidak diblokir di Indonesia."
        else:
            message = "Terjadi kesalahan dalam memeriksa situs web."
    else:
        message = "Gagal memeriksa situs web. Mohon coba lagi."
    
    # Mengirim balasan ke pengguna
    update.message.reply_text(message)

# Fungsi untuk menampilkan pesan bantuan
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Gunakan perintah /checkwebsite <nama_situs> untuk memeriksa apakah suatu situs web diblokir di Indonesia.")

def main():
    # Inisialisasi updater
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Menambahkan command handler
    dispatcher.add_handler(CommandHandler("checkwebsite", check_website))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Memulai bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
