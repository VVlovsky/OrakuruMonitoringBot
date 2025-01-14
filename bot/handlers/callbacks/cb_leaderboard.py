# -*- coding: utf-8 -*-

from asyncio import gather

from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from ..states import Page

from bot.db.table_methods import leaderboard
from bot.ans_templates import WelcomeMessage
from bot.keyboards import TurnLeaderboardPageKeyboard, MainMenuKeyboard


async def leaderboard_page(call: CallbackQuery):
    last_note_id = leaderboard.get_rows_count()

    note_text = (leaderboard.get_row_by_id(note_id=1)).text
    text_response = 'Leaderboard. Page %s/%s\n' % (1, last_note_id) + note_text

    await gather(
        call.message.edit_text(
            text=text_response, reply_markup=TurnLeaderboardPageKeyboard(1, last_note_id), disable_web_page_preview=True
        ),
        Page.note_id.set()
    )


async def turn_leaderboard_page(call: CallbackQuery, state: FSMContext):
    current_note_id = (await state.get_data()).get('page')
    last_note_id = leaderboard.get_rows_count()

    if call.data == 'next_leaderboard_page':

        if len(await state.get_data()) == 0:
            current_note_id = 2

            note_text = (leaderboard.get_row_by_id(current_note_id)).text
            text_response = 'Leaderboard. Page %s/%s\n' % (current_note_id, last_note_id) + note_text

            response = call.message.edit_text(
                    text=text_response, reply_markup=TurnLeaderboardPageKeyboard(current_note_id, last_note_id), disable_web_page_preview=True
                )

            await gather(response, state.update_data(page=2))

        else:
            current_note_id += 1

            note_text = (leaderboard.get_row_by_id(current_note_id)).text
            text_response = 'Leaderboard. Page %s/%s\n' % (current_note_id, last_note_id) + note_text

            response = call.message.edit_text(
                    text=text_response, reply_markup=TurnLeaderboardPageKeyboard(current_note_id, last_note_id), disable_web_page_preview=True
                )

            await gather(response, state.update_data(page=current_note_id))

    elif call.data == 'back_leaderboard_page':
        current_note_id -= 1

        note_text = (leaderboard.get_row_by_id(current_note_id)).text
        text_response = 'Leaderboard. Page %s/%s\n' % (current_note_id, last_note_id) + note_text

        response = call.message.edit_text(
                text=text_response, reply_markup=TurnLeaderboardPageKeyboard(current_note_id, last_note_id), disable_web_page_preview=True
            )

        await gather(response, state.update_data(page=current_note_id))

    elif call.data == 'back_to_menu':
        response = call.message.edit_text(text=WelcomeMessage, reply_markup=MainMenuKeyboard)

        await gather(response, state.finish())


def register_leaderboard_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(
        leaderboard_page, lambda CallbackQuery: CallbackQuery.data == 'show_leaderboard'
    )

    dp.register_callback_query_handler(turn_leaderboard_page, state=Page.note_id)