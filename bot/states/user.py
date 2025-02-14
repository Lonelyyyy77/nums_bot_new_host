from aiogram.fsm.state import StatesGroup, State


class AuthState(StatesGroup):
    phone = State()
    code = State()
    confirm_disable_2fa = State()