import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status = False):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`) VALUES(?,?)", (user_id,status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def update_subscription_price(self, user_id, price):
        """Обновляем цену у подписки"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `price` = ? WHERE `user_id` = ?", (price, user_id))

    def add_message_count(self, user_id, i = 1 ):
        """Увеличиваем счетчик отправленных сообщений на 1"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `alerts_sent` = `alerts_sent` + ? WHERE `user_id` = ?", (i,user_id))

    def update_subscription_last_request(self, user_id, last_request, last_message_id):
        """Обновляем last_request"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `last_request` = ? , `last_message_id` = ?   WHERE `user_id` = ?", (last_request, last_message_id, user_id)) 

    def get_last_message_id(self, user_id):
        """Проверяем, содержимое last_message_id"""
        with self.connection:
            result = self.cursor.execute('SELECT `last_message_id` FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return result[0][0]                      

    def update_subscription_book_id(self, user_id):
        """Обновляем, содержимое url из last_request"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `url` = `last_request` WHERE `user_id` = ?", (user_id,)) 
        
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()