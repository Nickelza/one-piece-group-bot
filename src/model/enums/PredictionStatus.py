from enum import IntEnum


class PredictionStatus(IntEnum):
    NEW = 1
    SENT = 2
    BETS_CLOSED = 3
    RESULT_SET = 4


PREDICTION_STATUS_NAME_MAP = {
    PredictionStatus.NEW: "New",
    PredictionStatus.SENT: "Open",
    PredictionStatus.BETS_CLOSED: "Bets closed",
    PredictionStatus.RESULT_SET: "Result set"
}


def get_prediction_status_name_by_key(prediction_status: PredictionStatus) -> str:
    return PREDICTION_STATUS_NAME_MAP[prediction_status]


def get_all_prediction_status_names() -> list[str]:
    return [get_prediction_status_name_by_key(status) for status in PredictionStatus]


def get_active_prediction_status_names() -> list[str]:
    return [get_prediction_status_name_by_key(status) for status in PredictionStatus
            if status is not PredictionStatus.RESULT_SET]


def get_prediction_status_by_name(name: str) -> PredictionStatus:
    return list(PREDICTION_STATUS_NAME_MAP.keys())[list(PREDICTION_STATUS_NAME_MAP.values()).index(name)]


def get_prediction_status_by_list_of_names(names: list[str]) -> list[PredictionStatus]:
    return [get_prediction_status_by_name(name) for name in names]
