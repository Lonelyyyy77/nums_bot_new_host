from aiogram import Router


async def start_router(dp) -> Router():
    from ..handlers.command_start import router as command_start_router

    dp.include_router(command_start_router)

async def user_routers(dp) -> Router():
    from ..handlers.user.send_num import router as user_send_num_router

    dp.include_router(user_send_num_router)


async def admin_routers(dp) -> Router():
    from ..handlers.admin.admin_panel import router as admin_panel_router

    dp.include_router(admin_panel_router)