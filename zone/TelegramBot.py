from os import environ as env

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, ApplicationBuilder, filters

from .Parser import CHAT_ENV, BOT_TOKEN_ENV
from .Tracker import Tracker


PRODUCT = 'product'
NEWLINE = '\n'


class TelegramBot:
    def __init__(self, tracker: Tracker):
        self.tracker = tracker

        self.token = token = env.get(BOT_TOKEN_ENV)
        self.chat = chat = env.get(CHAT_ENV)

        if token is None:
            raise ValueError(f'Environment variable {BOT_TOKEN_ENV} must be set')

        if chat is None:
            raise ValueError(f'Environment variable {CHAT_ENV} must be set')

        self.chat = int(chat)

    async def _list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        await user.send_message(f'Currently tracked products:{NEWLINE}{NEWLINE}{NEWLINE.join(self.tracker.products)}')

    async def _track(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        await user.send_message('Please, send link to the product which should be tracked')

        return PRODUCT

    async def _track_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        product = update.message.text.strip()

        try:
            self.tracker.track(product)
            await user.send_message(f'Started tracking product {product}')
        except ValueError:
            await user.send_message(f'Already tracking product {product}')

        return ConversationHandler.END

    async def _ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        await user.send_message('Please, send link to the product which should be ignored')

        return PRODUCT

    async def _ignore_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        product = update.message.text.strip()

        try:
            self.tracker.ignore(product)
            await user.send_message(f'Stopped tracking product {product}')
        except ValueError:
            await user.send_message(f'Not tracking product {product}')

        return ConversationHandler.END

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user

        if user.id != self.chat:
            return

        await user.send_message('Cancelled the last operation')

        return ConversationHandler.END

    def poll(self):
        app = ApplicationBuilder().token(self.token).build()

        app.add_handler(CommandHandler('list', self._list))
        app.add_handler(
            ConversationHandler(
                entry_points = [CommandHandler('track', self._track)],
                states = {
                    PRODUCT: [MessageHandler(filters.Regex('http.+'), self._track_product)]
                },
                fallbacks = [CommandHandler('cancel', self._cancel)]
            )
        )
        app.add_handler(
            ConversationHandler(
                entry_points = [CommandHandler('ignore', self._ignore)],
                states = {
                    PRODUCT: [MessageHandler(filters.Regex('http.+'), self._ignore_product)]
                },
                fallbacks = [CommandHandler('cancel', self._cancel)]
            )
        )

        print('Started telegram bot')

        app.run_polling()
