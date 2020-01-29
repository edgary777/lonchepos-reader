import sqlite3
from datetime import date, timedelta


database = "path"
connection = sqlite3.connect(database)
hoy = date.today()

cursor = connection.cursor()
totales = []

def cuentaPanes(folios):
    x = ""
    for folio in folios:
        x += "'" + str(folio[0]) + "', "
    query = "SELECT sum(cantidad) FROM ticketProducts WHERE folio IN ({}) AND precio > 26;".format(x[:-2])
    cursor.execute(query)
    return cursor.fetchall()[0][0]

def percentageCalculator(rawSales):
    percentage = []
    sales = 0
    for sale in rawSales:
        sales += sale[0]
    for sale in rawSales:
        percentage.append([int(sale[1]), round((sale[0] / sales) * 100, 2)])
    return percentage

query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(hoy)
cursor.execute(query)
totales.append(cursor.fetchone()) #TotalHoy

query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(hoy - timedelta(days=1))
cursor.execute(query)
totales.append(cursor.fetchone()) #Total Ayer

query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE nombre LIKE '%UBER%' AND fecha = '{}' AND cancelado <> 1;".format(hoy)
cursor.execute(query)
totales.append(cursor.fetchone()) #UBER Hoy

query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE nombre LIKE '%UBER%' AND fecha = '{}' AND cancelado <> 1;".format(hoy - timedelta(days=1))
cursor.execute(query)
totales.append(cursor.fetchone()) #UBER Ayer

query = "SELECT folio FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(hoy)
cursor.execute(query)
foliosHoy = cursor.fetchall()

query = "SELECT folio FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(hoy - timedelta(days=1))
cursor.execute(query)
foliosAyer = cursor.fetchall()

dias = [foliosHoy, foliosAyer]
cuentaPan = []

for dia in dias:
    cuentaPan.append(cuentaPanes(dia))
    

# promedio por hora de venta los ultimos 30 dias
query = "SELECT SUM(total) AS sale_total, STRFTIME('%H', hora) AS Hour FROM tickets WHERE fecha <= '{}' AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%H', hora)".format(hoy - timedelta(days=1), hoy - timedelta(days = 31))
cursor.execute(query)
hourlyRaw = cursor.fetchall()

# promedio por hora de venta los ultimos 30 dias
query = "SELECT SUM(total) AS sale_total, STRFTIME('%w', fecha) AS Hour FROM tickets WHERE fecha <= '{}' AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%w', fecha)".format(hoy - timedelta(days=1), hoy - timedelta(days = 31))
cursor.execute(query)
weekdayRaw = cursor.fetchall()

# buscador de folios para contador de panes para los ultimos 30 dias
query = "SELECT folio FROM tickets WHERE fecha <= '{}' AND fecha >= '{}' AND cancelado <> 1;".format(hoy - timedelta(days=1), hoy - timedelta(days = 31))
cursor.execute(query)
foliosPromedio = (cursor.fetchall())

# Contador de dias activos en los ultimos 30 dias
query = "SELECT COUNT(DISTINCT fecha) FROM tickets WHERE fecha <= '{}' AND fecha >= '{}';".format(hoy - timedelta(days=1), hoy - timedelta(days = 31))
cursor.execute(query)
diasVenta = cursor.fetchall()[0][0]

# promedio por hora de venta los ultimos 90 dias
query = "SELECT SUM(total) AS sale_total, STRFTIME('%H', hora) AS Hour FROM tickets WHERE fecha <= '{}' AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%H', hora)".format(hoy - timedelta(days=1), hoy - timedelta(days = 91))
cursor.execute(query)
hourlyRawQuarter = cursor.fetchall()

# promedio por dia de la semana de venta los ultimos 90 dias
query = "SELECT SUM(total) AS sale_total, STRFTIME('%w', fecha) AS Hour FROM tickets WHERE fecha <= '{}' AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%w', fecha)".format(hoy - timedelta(days=1), hoy - timedelta(days = 91))
cursor.execute(query)
weekdayRawQuarter = cursor.fetchall()

# Contador de dias activos en los ultimos 90 dias
query = "SELECT COUNT(DISTINCT fecha) FROM tickets WHERE fecha <= '{}' AND fecha >= '{}';".format(hoy - timedelta(days=1), hoy - timedelta(days = 91))
cursor.execute(query)
diasVentaQuarter = cursor.fetchall()[0][0]

hourlyPercentage = percentageCalculator(hourlyRaw)
weekdayPercentage = percentageCalculator(weekdayRaw)
quarterHourly = percentageCalculator(hourlyRawQuarter)
quarterWeekday = percentageCalculator(weekdayRawQuarter)
average = cuentaPanes(foliosPromedio) / diasVenta


print("PROMEDIO PANES ULTIMOS", diasVenta, "DIAS TRABAJADOS: ", average)
print("")
print("HOY", hoy)
print("")
print("Panes Hoy:", cuentaPan[0])
print("TOTAL HOY: $" + str(totales[0][0]))
print("UBER HOY: $" + str(totales[2][0]))
print("TOTAL SIN UBER: $" + str(totales[0][0] - totales[2][0]))
print("_______________________________")
print("Panes Ayer:", cuentaPan[1])
print("TOTAL AYER: $" + str(totales[1][0]))
print("UBER AYER: $" + str(totales[3][0]))
print("TOTAL SIN UBER AYER: $" + str(totales[1][0] - totales[3][0]))
print("_______________________________")
print("PORCENTAJES DE VENTA POR HORA DE VENTA EN LOS ULTIMOS ", diasVenta, "DIAS")
for hour in hourlyPercentage:
    print("{}:00-{}:00 = {}%".format(hour[0], hour[0] + 1, hour[1]))
diasDeLaSemana = ["DOMINGO", "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]
print("_______________________________")

print("PORCENTAJES DE VENTA POR DIA DE LA SEMANA EN LOS ULTIMOS ", diasVenta, "DIAS")
for day in weekdayPercentage:
    print("{} = {}%".format(diasDeLaSemana[day[0]], day[1]))
print("_______________________________")

print("PORCENTAJES DE VENTA POR HORA DE VENTA EN LOS ULTIMOS ", diasVentaQuarter, "DIAS")
for hour in quarterHourly:
    print("{}:00-{}:00 = {}%".format(hour[0], hour[0] + 1, hour[1]))
print("_______________________________")

print("PORCENTAJES DE VENTA POR DIA DE LA SEMANA EN LOS ULTIMOS ", diasVentaQuarter, "DIAS")
for day in quarterWeekday:
    print("{} = {}%".format(diasDeLaSemana[day[0]], day[1]))
connection.close()
input()
