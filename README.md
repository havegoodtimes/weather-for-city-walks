# weather-for-city-walks

**Описание возможных ошибок сервиса**

*Неверное название города* - прогноз погоды для города не запрашивается, сервис возвращает сообщение "Город не найден. Проверьте, что вы правильно написали название города."

*Ошибка 400* - город существует, но для него не найден прогноз погоды на следующий день; сервис продолжает работать, при отсутствии прогноза для города возвращает сообщение "Не найден прогноз погоды для города"

*Ошибка 401 или 403* - проблемы с ключом для API (неправильно написан или перестал работать); сервис продолжает работать (прогноз погоды не запрашивается), при попытке запроса рекомендаций сервис возвращает сообщение "Нет доступа к сервису прогноза погоды"

*Ошибка 404* - неправильный URL для запроса к AccuWeather API; сервис продолжает работать; если не удаётся выполнить запрос из-за неправильного URL, сервис возвращает сообщение "Произошла ошибка при запросе к сервису прогноза погоды."

*Ошибка 500* - ошибка на стороне Accuweather, API перестал работать; сервис продолжает работать, при запросе рекомендаций возвращается сообщение "Сервис прогноза погоды перестал работать"

*Ошибка 503* - превышен лимит запросов к AccuWeather API; сервис продолжает работать (прогноз погоды не запрашивается), при попытке запроса рекомендаций возвращает сообщение "Вы достигли лимита запросов. Попробуйте запросить рекомендации завтра."

*Неизвестная ошибка* - если ошибку не удалось распознать, сервис продолжает работать, при попытке запроса рекомендаций возвращает сообщение "Произошла неизвестная ошибка"
