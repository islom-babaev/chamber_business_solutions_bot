import asyncio,config

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold
from states import NAME, COMPANY_NAME, POSITION, PHONE_NUM, DOMAIN
from models import Participant

loop = asyncio.get_event_loop()

bot = Bot(token=config.bot_token, loop=loop)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    await state.set_state(NAME)
    await message.reply("Введите Ваше ФИО:")



@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(state='*', func=lambda message: message.text.lower() == 'cancel')
async def cancel_handler(message: types.Message):

    with dp.current_state(chat=message.chat.id, user=message.from_user.id) as state:

        if await state.get_state() is None:
            return

        await state.reset_state(with_data=True)
        await message.reply('Отменено.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=NAME)
async def process_name(message: types.Message):
    with dp.current_state(chat=message.chat.id, user=message.from_user.id) as state:
        await state.update_data(name=message.text)
        await state.set_state(COMPANY_NAME)

    await message.reply("Введите название Вашей компании:")

@dp.message_handler(state=COMPANY_NAME)
async def process_age(message: types.Message):
    with dp.current_state(chat=message.chat.id, user=message.from_user.id) as state:
        await state.set_state(DOMAIN)
        await state.update_data(company_name=message.text)

    await message.reply("Введите сферу деятельности Вашей компании:")


@dp.message_handler(state=DOMAIN)
async def process_age(message: types.Message):
    with dp.current_state(chat=message.chat.id, user=message.from_user.id) as state:
        await state.set_state(POSITION)
        await state.update_data(domain=message.text)

    await message.reply("Введите свою должность:")

@dp.message_handler(state=POSITION)
async def process_age(message: types.Message):
    with dp.current_state(chat=message.chat.id, user=message.from_user.id) as state:
        await state.set_state(PHONE_NUM)
        await state.update_data(position=message.text)

    await message.reply("Введите свой номер телефона:")


@dp.message_handler(state=PHONE_NUM)
async def process_gender(message: types.Message):
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    data = await state.get_data()
    data['phone_num'] = message.text

    markup = types.ReplyKeyboardRemove()

    await bot.send_message(message.chat.id, "Спасибо за регистрацию!")

    participant = Participant(username=message.from_user.username, name=data['name'], company_name=data['company_name'], domain=data['domain'], position=data['position'],
                              phone_num=data['phone_num'])
    print(participant.username,participant.name, participant.company_name, participant.domain, participant.position, participant.phone_num)
    participant.save()
    await bot.send_message(config.chat_id,
        text(
            text('ФИО:', bold(data['name'])),
            text('Компания:', data['company_name']),
            text('Сфера Деятельности:', data['domain']),
            text('Должность:', data['position']),
            text('Номер телефона:', data['phone_num']),
            text('Username:', message.from_user.username),
        sep='\n'), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

    await bot.send_message(message.chat.id,
                           text(
                               text('ФИО:', bold(data['name'])),
                               text('Компания:', data['company_name']),
                               text('Сфера Деятельности:', data['domain']),
                               text('Должность:', data['position']),
                               text('Номер телефона:', data['phone_num']),
                               text('Username:', "@{}".format(message.from_user.username)),
                               sep='\n'), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

    await state.finish()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True, on_shutdown=shutdown)