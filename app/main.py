from fastapi import FastAPI
from dotenv import dotenv_values
from psycopg2.extensions import AsIs

import psycopg2
import uvicorn


from datetime import datetime, date
from pydantic import BaseModel, Field

import os
import json

app = FastAPI()
conf = dotenv_values()

sqlHost = conf['HOST']
sqlPort = conf['PORT']
sqlDB   = conf['DB']
sqlUser = conf['USER']
sqlPass = conf['PASS']


class TaskModel (BaseModel):
    statustask: bool     = Field(validation_alias='СтатусЗакрытия')
    closeat   : None = None
    shifttasks: str      = Field(validation_alias='ПредставлениеЗаданияНаСмену')
    lice      : str      = Field(validation_alias='Линия')
    shift     : str      = Field(validation_alias='Смена')
    brigade   : str      = Field(validation_alias='Бригада')
    batchnum  : int      = Field(validation_alias='НомерПартии')
    batchdate : date     = Field(validation_alias='ДатаПартии')
    nomenclat : str      = Field(validation_alias='Номенклатура')
    codeekn   : str      = Field(validation_alias='КодЕКН')
    idRC      : str      = Field(validation_alias='ИдентификаторРЦ')
    datestart : datetime = Field(validation_alias='ДатаВремяНачалаСмены')
    dateend   : datetime = Field(validation_alias='ДатаВремяОкончанияСмены')


@app.post('/task')
def mainTask(task : TaskModel):
    if task.statustask != False:
        task.closeat = datetime.now()
    ff1 = task.batchnum
    ff2 = task.batchdate
    f = sqlTask(dict(task), str(ff1), str(ff2))
    return f

def sqlTask(task, parm1, parm2):
    try:
        columns = task.keys()
        value = [task[column] for column in columns]

        insert_state = 'INSERT INTO "task_list" (%s) VALUES %s;'

        sqlConnect = psycopg2.connect(
            host = sqlHost,
            port = sqlPort,
            user = sqlUser, 
            password = sqlPass,
            dbname = sqlDB
        )
        
        with sqlConnect.cursor() as cursor:

            cursor.execute('SELECT id FROM task_list WHERE batchnum='+ parm1)
            cheak1 = cursor.fetchall()

            cursor.execute("SELECT id FROM task_list WHERE batchdate='"+parm2+"'")
            cheak2 = cursor.fetchall()

            if cheak1 == [] and cheak2 == []:
                cursor.execute(insert_state, (AsIs(','.join(columns)), tuple(value)))
                sqlConnect.commit()
                return 'goood'
            else:
                
                if cheak1 != []: cheak1=cheak1[0][0] 
                else: cheak1 = -1
                
                if cheak2 != []: cheak2=cheak2[0][0]
                else: cheak2 = -1
                
                if cheak1 == cheak2: cheak1
                else: cheak1 = cheak1+cheak2+1

                re = 'DELETE FROM task_list WHERE id='+str(cheak1)
                
                cursor.execute(re)
                cursor.execute(insert_state, (AsIs(','.join(columns)), tuple(value)))
                sqlConnect.commit()
                return 're:good'
    except:
        return 'error'
    finally:
        if sqlConnect:
            sqlConnect.close()
            print("Connection closed")

if __name__ == '__main__':

    host = os.environ.get("REMOTE_PLAY_HOST", "0.0.0.0")
    port = os.environ.get("REMOTE_PLAY_PORT", 7000)
    uvicorn.run(app, host=host, port=port )