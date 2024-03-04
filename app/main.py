from fastapi import FastAPI, HTTPException
from dotenv import dotenv_values

import psycopg2
import uvicorn

from datetime import datetime
from pydantic import BaseModel, Field

import os

app = FastAPI()
conf = dotenv_values()

sqlHost = conf['HOST']
sqlPort = conf['PORT']
sqlDB   = conf['DB']
sqlUser = conf['USER']
sqlPass = conf['PASS']


class TaskModel (BaseModel):
    status_task : bool  = Field(validation_alias='СтатусЗакрытия')
    close_at    : str   = None
    shift_tasks : str   = Field(validation_alias='ПредставлениеЗаданияНаСмену')
    lice        : str   = Field(validation_alias='Линия')
    shift       : str   = Field(validation_alias='Смена')
    brigade     : str   = Field(validation_alias='Бригада')
    batch_num   : int   = Field(validation_alias='НомерПартии')
    batch_date  : str   = Field(validation_alias='ДатаПартии')
    nomenclat   : str   = Field(validation_alias='Номенклатура')
    code_ekn    : str   = Field(validation_alias='КодЕКН')
    id_rc       : str   = Field(validation_alias='ИдентификаторРЦ')
    date_start  : str   = Field(validation_alias='ДатаВремяНачалаСмены')
    date_end    : str   = Field(validation_alias='ДатаВремяОкончанияСмены')

class ProductModel (BaseModel):
    id_product      : str   = Field(validation_alias='УникальныйКодПродукта')
    lot_id          : int   = Field(validation_alias='НомерПартии')
    lot_data        : str   = Field(validation_alias='ДатаПартии')
    is_aggregated   : None  = None
    aggregated_at   : None  = None

@app.get('/')
def mainGet():
    return {'Page': 'Hello'}

@app.post('/task')
def mainTask(task: TaskModel):
    if task.status_task != False:
        task.close_at = str(datetime.now())
    task_json = task.__dict__
    q = "SELECT id FROM task_list WHERE batch_num = " + str(task.batch_num) + " AND batch_date = '" + str(task.batch_date)+ "' LIMIT 100"
    result = sqlQuery(q)#return tuple in list
    

    if result == []:
        task_keys, task_values = keysValues(task_json)
        q = 'INSERT INTO "task_list" (%s) VALUES (%s);' % (task_keys, task_values)
        result = sqlQuery(q)
        return q +str(result)
    else:
        id = result[0][0]
        q = 'UPDATE task_list SET %s WHERE id=' % str(task_json).replace("': ",'=').replace('{','').replace('}','').replace('None', 'null')
        q = q.replace(" '"," ") + str(id)
        result = sqlQuery(q)
        return q

@app.get('/task_{id}')
def searchTask(id: int):
    q = 'SELECT id_product FROM task_list as t1 join product_list as t2 ON batch_num=lot_id WHERE t1.id = ' + str(id)
    f = sqlQuery(q)
    if f != []:
        return {'id_product': f}
    else:
        return HTTPException(status_code=404, detail='Task with ID ' + str(id) + ' not found')
    
@app.post('/task_e{id}')
def editTask(id: int, body: dict):

    # Надо подумать над этим блоком
    # Данные на изменения принимаются
    # Но надо решить вопрос с теми данными, необходимо изменить в связи с изменениями первых
    # Что то бы сдеать с данными, которые лишние в запросе

    q = 'SELECT * FROM task_list WHERE id = ' + str(id)
    scan = sqlQuery(q)
    if scan != []:
        print('dsd')
        if 'status_task' in body:
            print(1)
            if body['status_task'] != scan[0][1]: print(scan[0][1])
            else: print(scan[0]) 

        q = 'UPDATE task_list SET ' + str(body).replace("': ",'=').replace("{'",'').replace('}','').replace(" '", "") + ' WHERE id=' + str(id)
        result = sqlQuery(q)
        return result
    else:
        return HTTPException(status_code=404, detail='ID not foud')

@app.post('/addproduct')
def mainAddProduct(lot: list[ProductModel]):
    outdata = ''

    for x in range(len(lot)):
        idd = lot[x].id_product

        q = "SELECT id_product FROM product_list where id_product = '" + lot[x].id_product +"'"
        qq = "SELECT id FROM task_list WHERE batch_num = " + str(lot[x].lot_id) + " AND batch_date = '" + str(lot[x].lot_data)+ "' LIMIT 100"
       
        result = sqlQuery(qq)
        scan = sqlQuery(q)
        
        if scan == [] and result != []:

            lot[x].is_aggregated = False
            lot[x].aggregated_at = None
            lot[x] = lot[x].__dict__
            lot_keys, lot_values = keysValues(lot[x])

            q = 'INSERT INTO "product_list" (%s) VALUES (%s);' % (lot_keys, lot_values)
            sqlQuery(q)

            outdata += str(idd) + ', '

    return outdata

@app.get('/aggregated')
def mainAggregated(id: int | None = 'null', id_prod: str | None = 'null'):
    q = "SELECT id,is_aggregated,aggregated_at,id_product  FROM product_list WHERE id=" + str(id) + " AND id_product = '" + id_prod + "'"
    scan = sqlQuery(q)
    print (scan[0][2])
    if scan == []:
        return HTTPException(status_code=404, detail="Product not found")
    elif len(scan) > 1: 
        return HTTPException(status_code=400, detail="unique code is attached to another batch")
    elif scan[0][1]==True:
        return HTTPException(status_code=400, detail="unique code already used at " + str(scan[0][2]))
    else:
        qq = "UPDATE product_list SET is_aggregated = true, aggregated_at='" + str(datetime.now()) + "' WHERE id=" + str(scan[0][0])
        sqlQuery(qq)
        return {'Уникальный код' : scan[0][3]}

def keysValues(dictionary):
    """
    !!!Внимание!!! \n
    На вход передавать только dict, проверок на дурока нет \n
    Превращает dict в две строки, первая только из ключей, вторая только из значений.
    """
    return str(list(dictionary.keys())).replace("'", "").replace('[', '').replace(']',''), str(list(dictionary.values())).replace('[', '').replace(']','').replace('None', 'null')
    

def sqlQuery(query):
    """
    Выполняет запрос в базе PostgreSQL\n
    Строка запроса должна быть передана на входе, на выходе в случаи:\n
    - Успеха - результат вывода или "no results to fetch"\n
    - Ошибки - описание ошибки\n

    При каждом отключении от базы, будет уведомление в консоль
    """
    try:
        sqlConnect = psycopg2.connect(
            host = sqlHost,
            port = sqlPort,
            user = sqlUser, 
            password = sqlPass,
            dbname = sqlDB
        )

        with sqlConnect.cursor() as cursor:
            cursor.execute(query)
            sqlConnect.commit()
            show = cursor.fetchall()
            return show
    except (Exception, psycopg2.Error) as error:
        print (error)
        return error
    finally:
        if sqlConnect:
            sqlConnect.close()
            print("Connection closed")

if __name__ == '__main__':

    host = os.environ.get("REMOTE_PLAY_HOST", "0.0.0.0")
    port = os.environ.get("REMOTE_PLAY_PORT", 7000)
    uvicorn.run(app, host=host, port=port )