# Testes - MySQL x MongoDB

Projeto para testes de estratégias de desempenho para uma API de reserva de estoque.

## Cenários de Testes
* mongodb/app.py
  Registro de reservas mantendo o registro de falhas.
  
* mongodb/app2
  Registro de reservas descartando falhas.
  
* mysqltest/app
  Registro de reservas com o banco em auto-commit.
  
* mysqltest/app2
  Registro de reservas com transação e com o nível de isolamento READ UNCOMMITTED.
  
* mysqltest/app
  Registro de reservas com transação (convencional).
  
  
## Passado a passo para o teste
### Iniciar o serviços via docker composer.
```shell
docker-compose up
```
### Iniciar o servidor da app (teste) desejada.
```shell
gunicorn -w 8 -b 127.0.0.1:4000 -t 600 start_[mongo|mysql][|1|2|3]:app
```

### Executar o teste de desempenho.
```shell
 curl 'http://127.0.0.1:4000/create_stocks/'; \
 curl 'http://127.0.0.1:4000/load/'; \
 ab -n 1000 -c 1000 -l 'http://127.0.0.1:4000/reserves/sku-1/' ; \
 curl 'http://127.0.0.1:4000/report/'
```
 

