#!/bin/bash
# generate-certificate.sh

# Выдаем себе сертификат в тестовом режиме
certbot certonly --standalone --preferred-challenges http --email $DOMAIN_EMAIL -d $DOMAIN_URL --agree-tos --non-interactive


# Проверяем успешность выполнения certbot
if [ $? -eq 0 ]; then
    # Удаляем старые сертификаты
    rm -f /etc/nginx/cert.pem /etc/nginx/key.pem

    # Копируем новые сертификаты
    cp /etc/letsencrypt/live/duels.me/fullchain.pem /etc/nginx/cert.pem
    cp /etc/letsencrypt/live/duels.me/privkey.pem /etc/nginx/key.pem
else
    echo "Ошибка при получении сертификата, проверьте логи и переменные."
fi
