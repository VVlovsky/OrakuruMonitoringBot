# -*- coding: utf-8 -*-

from asyncio import gather

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from ..states import SetValidatorAddress

from bot.db.table_methods import temporary_data, username_node
from bot.ans_templates import WelcomeMessage, AskAddress, ValidatorNotFound, ValidatorStatistic
from bot.keyboards import BackHomeKeyboard, MainMenuKeyboard, SearchValidatorAgainKeyboard


async def check_validator(call: CallbackQuery, state: FSMContext):
    if call.data == 'back_to_menu':
        await gather(
            state.finish(), call.message.edit_text(text=WelcomeMessage, reply_markup=MainMenuKeyboard)
        )

    else:

        try:
            username = call.from_user['username']
        except Exception as e:
            print(e)
            username = None
        row_with_address = username_node.get_row_by_username(username=username)

        if call.data == 'try_find_validator_again' and row_with_address:
            row_with_address = None
            username_node.delete_row_by_username(username=username)

        if not row_with_address:
            call_data = await call.message.edit_text(
                text=AskAddress, reply_markup=BackHomeKeyboard
            )
            print(call_data)
            await gather(
                SetValidatorAddress.address.set(), state.update_data(message_data=call_data)
            )

        else:
            await show_validator_stats(call, state)


def generate_response(address, stats, call_):
    short_address = address[0:4] + '...' + address[-5:-1]

    rank, score, response_time, responses = stats.id, stats.score, stats.response_time, stats.responses

    response = call_.edit_text(
        text=ValidatorStatistic % (rank, address, short_address, score, responses, round(response_time, 2)),
        reply_markup=SearchValidatorAgainKeyboard, disable_web_page_preview=True
    )

    return response


async def show_new_validator(call: Message or CallbackQuery, state: FSMContext):
    if isinstance(call, CallbackQuery):
        response = call.message.edit_text(text=WelcomeMessage, reply_markup=MainMenuKeyboard)

        await gather(response, state.finish())

    else:
        call_: CallbackQuery.message = (await state.get_data()).get('message_data')

        address = call.text
        stats = temporary_data.get_row_by_address(address)
        print(stats)

        if not stats:
            response = call_.edit_text(text=ValidatorNotFound, reply_markup=SearchValidatorAgainKeyboard)

            await gather(call.delete(), response)

        else:
            response = generate_response(address, stats, call_)
            username_node.paste_row(
                username=call_['chat']['username'], address=address
            )
            username_node.commit()

            await gather(call.delete(), response)


async def show_validator_stats(call: Message or CallbackQuery, state: FSMContext):
    call_: CallbackQuery.message = (await state.get_data()).get('message_data')
    print(call_)
    username = call.from_user['username']

    row_with_address = username_node.get_row_by_username(username=username)
    if not row_with_address:
        await show_new_validator(call, state)
    else:
        address = row_with_address.address
        stats = temporary_data.get_row_by_address(address)
        if call_:
            response = generate_response(address, stats, call_)
            await gather(call.delete(), response)
        else:
            response = generate_response(address, stats, call.message)
            await gather(response)
    await state.finish()


def register_validator_callback(dp: Dispatcher):
    dp.register_callback_query_handler(
        check_validator, lambda CallbackQuery: CallbackQuery.data in [
            'check_validator', 'try_find_validator_again', 'back_to_menu'
        ]
    )

    dp.register_message_handler(show_validator_stats, state=SetValidatorAddress)
    dp.register_callback_query_handler(show_validator_stats, state=SetValidatorAddress)
