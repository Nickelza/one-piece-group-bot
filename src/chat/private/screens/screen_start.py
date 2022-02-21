from telegram import Update


def manage(update: Update, context) -> None:
    """
    Manage the start screen.
    :param update: The update.
    :type update: telegram.Update
    :param context: The context.
    :type context: telegram.ext.CallbackContext
    :return: None
    :rtype: None
    """

    text = "Welcome to @onepiecegroup Bot!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
