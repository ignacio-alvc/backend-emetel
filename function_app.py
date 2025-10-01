import azure.functions as func
import logging
import os
import json
import pyodbc
import datetime
#from fikrfg

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    f"UID={os.getenv('DB_USERNAME')};"
    f"PWD={os.getenv('DB_PASSWORD')}"
)

def json_converter(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()



@app.route(route="getWorkers")
def getWorkers(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Función getWorkers (Python V2) procesando una petición.')

    filter_state = req.params.get('estado')

    sql_query = "SELECT * FROM dbo.trabajador"
    params = []

    if filter_state:
        sql_query += " WHERE estado = ?"
        params.append(filter_state)

    results = []
    try:
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
        return func.HttpResponse(
            body=json.dumps(results, default=json_converter),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error en la base de datos: {e}")
        return func.HttpResponse(
            f"Error al consultar la base de datos: {e}",
            status_code=500
        )