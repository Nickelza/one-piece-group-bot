from enum import StrEnum


class IncomeTaxEventType(StrEnum):
    BOUNTY_GIFT = 'bounty_gift'
    BOUNTY_LOAN = 'bounty_loan'
    DEVIL_FRUIT_SELL = 'devil_fruit_sell'
    DOC_Q_GAME = 'doc_q_game'
    FIGHT = 'fight'
    GAME = 'game'
    PREDICTION = 'prediction'
