import aiohttp
import logging
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_API_URL, HTTP_TIMEOUT, HTTP_STATUS_SUCCESS, HEALTH_MAX

logger = logging.getLogger(__name__)

class TelegramClient:
    """
    Клиент для работы с Telegram Bot API.
    Отправляет уведомления пользователям через бота.
    """
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.api_url = f"{TELEGRAM_API_URL}{self.bot_token}"
        
        if not self.bot_token or self.bot_token == "your_bot_token_here":
            logger.warning("TELEGRAM_BOT_TOKEN не установлен или установлен по умолчанию. Уведомления не будут отправляться.")
            self.bot_token = None
    
    async def send_message(self, chat_id: str, message: str) -> bool:
        """
        Отправляет сообщение пользователю через Telegram бота.
        
        Args:
            chat_id (str): ID чата пользователя
            message (str): Текст сообщения
            
        Returns:
            bool: True если сообщение отправлено успешно, False в противном случае
        """
        if not self.bot_token:
            logger.debug("Пропуск отправки сообщения: TELEGRAM_BOT_TOKEN не установлен")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
                ) as response:
                    if response.status == HTTP_STATUS_SUCCESS:
                        logger.info(f"Сообщение отправлено пользователю {chat_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка отправки сообщения: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            return False
    
    async def send_low_health_notification(self, chat_id: str, pet_name: str, health: int, stage: str) -> bool:
        """
        Отправляет уведомление о низком здоровье питомца.
        
        Args:
            chat_id (str): ID чата пользователя
            pet_name (str): Имя питомца
            health (int): Текущее здоровье
            stage (str): Стадия питомца
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        message = f"[!] <b>Внимание!</b>\n\n"
        message += f"Питомец <b>{pet_name}</b> нуждается в помощи!\n"
        message += f"Стадия: <b>{stage}</b>\n"
        message += f"Здоровье: <b>{health}/{HEALTH_MAX}</b>\n\n"
        message += "Срочно помогите своему питомцу!"
        
        return await self.send_message(chat_id, message)

    async def send_auction_outbid(self, chat_id: str, auction_id: int, amount: int) -> bool:
        message = (
            f"[Auction] <b>Ваша ставка перебита</b>\n\n"
            f"Аукцион: <b>#{auction_id}</b>\n"
            f"Новая текущая цена: <b>{amount}</b> монет"
        )
        return await self.send_message(chat_id, message)

    async def send_auction_won(self, chat_id: str, auction_id: int, price: int) -> bool:
        message = (
            f"[Auction] <b>Вы выиграли!</b>\n\n"
            f"Аукцион: <b>#{auction_id}</b>\n"
            f"Итоговая цена: <b>{price}</b> монет"
        )
        return await self.send_message(chat_id, message)

    async def send_pet_sold(self, chat_id: str, auction_id: int, price: int, buyer_name: str = None) -> bool:
        message = (
            f"[Auction] <b>Питомец продан</b>\n\n"
            f"Аукцион: <b>#{auction_id}</b>\n"
            f"Итоговая цена: <b>{price}</b> монет\n"
        )
        
        if buyer_name:
            message += f"Покупатель: <b>{buyer_name}</b>"
        else:
            message += "Покупатель: <b>Неизвестный игрок</b>"
        
        return await self.send_message(chat_id, message)

    async def send_auction_expired(self, chat_id: str, auction_id: int) -> bool:
        message = (
            f"[Auction] <b>Аукцион завершён</b>\n\n"
            f"Аукцион: <b>#{auction_id}</b>\n"
            f"Ставок не было. Лот не продан."
        )
        return await self.send_message(chat_id, message)
    
    async def send_death_notification(self, chat_id: str, pet_name: str, stage: str) -> bool:
        """
        Отправляет уведомление о смерти питомца.
        
        Args:
            chat_id (str): ID чата пользователя
            pet_name (str): Имя питомца
            stage (str): Стадия питомца
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        message = f"[X] <b>Питомец умер!</b>\n\n"
        message += f"К сожалению, <b>{pet_name}</b> умер на стадии <b>{stage}</b>.\n\n"
        message += "Игра окончена. Создайте нового питомца для продолжения!"
        
        return await self.send_message(chat_id, message)
    
    async def send_stage_transition_notification(self, chat_id: str, pet_name: str, old_stage: str, new_stage: str) -> bool:
        """
        Отправляет уведомление о переходе питомца на новую стадию.
        
        Args:
            chat_id (str): ID чата пользователя
            pet_name (str): Имя питомца
            old_stage (str): Предыдущая стадия
            new_stage (str): Новая стадия
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        message = f"[*] <b>Питомец вырос!</b>\n\n"
        message += f"<b>{pet_name}</b> перешел с <b>{old_stage}</b> на <b>{new_stage}</b>!\n\n"
        message += "Поздравляем! Продолжайте заботиться о своем питомце!"
        
        return await self.send_message(chat_id, message)

# Глобальный экземпляр клиента
telegram_client = TelegramClient() 