from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import app.keyboards as kb
from app.database.requests import (set_user,
                                   set_basket, get_basket, get_item_by_id, delete_basket)

router = Router()
hel = """
Вітаю вас у нашому магазині!
Тут ви знайдете свої улюблені кросівки від відомих брендів
Щодо замовлень писати на цей контакт: YOUR_NUMBER
"""

@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await set_user(message.from_user.id)
        await message.answer_sticker('CAACAgIAAxkBAAJ8CWXWaZSwgjIL-mpIuzo4p1c6L9umAAJwEwACfmKxSR0TN_eGUEvWNAQ')
        await message.answer(text=hel, reply_markup=kb.main)
    else:
        await message.answer('Ви повернулися на головну')
        await message.message.answer("Ласкаво просимо до cheps_shop!",
                                     reply_markup=kb.main)


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(text='Оберіть категорію:',
                                     reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Виберіть товар',
                                     reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item = await get_item_by_id(callback.data.split('_')[1])
    await callback.answer('')
    await callback.message.answer_photo(photo=item.photo,
                                        caption=f'{item.name}\n\n{item.description}\n\nЦіна: {item.price} гривень',
                                        reply_markup=await kb.basket(item.id))


@router.callback_query(F.data.startswith('order_'))
async def basket(callback: CallbackQuery):
    await set_basket(callback.from_user.id, callback.data.split('_')[1])
    await callback.answer('Товар доданий до кошика')


@router.callback_query(F.data == 'mybasket')
async def mybasket(callback: CallbackQuery):
    await callback.answer('')
    basket = await get_basket(callback.from_user.id)
    counter = 0
    for item_info in basket:
        item = await get_item_by_id(item_info.item)
        await callback.message.answer_photo(photo=item.photo,
                                            caption=f'{item.name}\n\n{item.description}\n\nЦіна: {item.price} гривень',
                                            reply_markup=await kb.delete_from_basket(item.id))
        counter += 1
    await callback.message.answer('Ваш кошик пустий') if counter == 0 else await callback.answer('')


@router.callback_query(F.data.startswith('delete_'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_basket(callback.from_user.id, callback.data.split('_')[1])
    await callback.message.delete()
    await callback.answer('Ви видалили товар із кошика')