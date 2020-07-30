import sqlite3
from datetime import date, timedelta


database = "C:\Program Files\lonchepos1.1.0_w10\database.db"
connection = sqlite3.connect(database)
hoy = date.today()

diasDeLaSemana = ["DOMINGO", "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]

cursor = connection.cursor()
totales = []

def cuentaPanes(timeframe, onlyOne=False, hourly=False, notToday=False):
    fecha = hoy - timedelta(days=timeframe)
    if notToday:
        notToday =  "AND tickets.fecha <> DATE('now') "
    else:
        notToday = ""
    if onlyOne is True:
        query = "SELECT COALESCE(SUM(ticketProducts.cantidad), 0) FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE ticketProducts.precio > 26 AND tickets.fecha = '{}' {}AND tickets.cancelado <> 1;".format(fecha, notToday)
    elif hourly is True and onlyOne is False:
        query = "SELECT STRFTIME('%H', tickets.hora), SUM(ticketProducts.cantidad) FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE tickets.fecha >= '{}' {}AND tickets.cancelado <> 1 AND ticketProducts.precio > 26 GROUP BY STRFTIME('%H', tickets.hora);".format(fecha, notToday)
    elif hourly is True and onlyOne is True:
        query = "SELECT STRFTIME('%H', tickets.hora), SUM(ticketProducts.cantidad) FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE tickets.fecha = '{}' {}AND tickets.cancelado <> 1 AND ticketProducts.precio > 26 GROUP BY STRFTIME('%H', tickets.hora);".format(fecha, notToday)
    else:
        query = "SELECT COALESCE(SUM(ticketProducts.cantidad), 0) FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE ticketProducts.precio > 26 AND tickets.fecha >= '{}' {}AND tickets.cancelado <> 1;".format(fecha, notToday)
    query = query
    cursor.execute(query)
    if hourly:
        result = cursor.fetchall()
    else:
        result = cursor.fetchall()[0][0]
    return result

def percentageCalculator(rawSales):
    percentage = []
    sales = 0
    for sale in rawSales:
        sales += sale[0]
    for sale in rawSales:
        percentage.append([int(sale[1]), round((sale[0] / sales) * 100, 2)])
    return percentage


def calculadoraTotales(timeframe):
    time = hoy - timedelta(days=timeframe)
    query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(time)
    cursor.execute(query)
    ct = cursor.fetchone()
    return ct

def calculadoraTotalesUber(timeframe):
    time = hoy - timedelta(days=timeframe)
    query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE nombre LIKE '%UBER%' AND fecha = '{}' AND cancelado <> 1;".format(time)
    cursor.execute(query)
    ctu = cursor.fetchone()
    return ctu

def ventaPorHora(timeframe):
    time = hoy - timedelta(days=timeframe)
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%H', hora) AS Hour FROM tickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%H', hora)".format(time)
    cursor.execute(query)
    vph = cursor.fetchall()
    return vph

def ventaPorDiaSemana(timeframe):
    time = hoy - timedelta(days=timeframe)
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%w', fecha) AS Hour FROM tickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%w', fecha)".format(time)
    cursor.execute(query)
    vpds = cursor.fetchall()
    return vpds

def contadorDiasActivos(timeframe):
    time = hoy - timedelta(days=timeframe)
    query = "SELECT COUNT(DISTINCT fecha) FROM tickets WHERE fecha <> DATE('now') AND fecha >= '{}';".format(time)
    cursor.execute(query)
    cda = cursor.fetchall()[0][0]
    return cda

for i in range(2):
    totales.append(calculadoraTotales(i)[0])
    totales.append(calculadoraTotalesUber(i)[0])

diasVenta = contadorDiasActivos(31)
diasVentaQuarter = contadorDiasActivos(91)

hourlyRaw = ventaPorHora(31)
hourlyRawQuarter = ventaPorHora(91)
weekdayRaw = ventaPorDiaSemana(31)
weekdayRawQuarter = ventaPorDiaSemana(91)

hourlyPercentage = percentageCalculator(hourlyRaw)
weekdayPercentage = percentageCalculator(weekdayRaw)

quarterHourly = percentageCalculator(hourlyRawQuarter)
quarterWeekday = percentageCalculator(weekdayRawQuarter)

average = cuentaPanes(diasVenta + (31 - diasVenta), notToday=True) / diasVenta

panesMesPromedioHora = [[panesHora[0], round(panesHora[1]/diasVenta, 1)] for panesHora in cuentaPanes(diasVenta + (31 - diasVenta), hourly=True, notToday=True)]
panesCuartoPromedioHora = [[panesHora[0], round(panesHora[1]/diasVentaQuarter, 1)] for panesHora in cuentaPanes(diasVentaQuarter + (91 - diasVenta), hourly=True, notToday=True)]
print("PROMEDIO PANES ULTIMOS", diasVenta, "DIAS TRABAJADOS: ", average)
print("")
print("HOY", hoy)
print("")
print("Panes Hoy:", cuentaPanes(0, onlyOne=True))
print("TOTAL HOY: $" + str(totales[0]))
print("UBER HOY: $" + str(totales[1]))
print("TOTAL SIN UBER: $" + str(totales[0] - totales[1]))
print("_______________________________")
print("Panes Ayer:", cuentaPanes(1, onlyOne=True))
print("TOTAL AYER: $" + str(totales[2]))
print("UBER AYER: $" + str(totales[3]))
print("TOTAL SIN UBER AYER: $" + str(totales[2] - totales[3]))
print("_______________________________")
print("PORCENTAJES DE VENTA Y TOTAL DE PANES POR HORA DE VENTA EN LOS ULTIMOS", diasVenta, "Y", diasVentaQuarter, "DIAS")
for hour in range(len(quarterHourly)):
    print("{}:00-{}:00 = {}% - {} PANES  \t|| {}% - {} PANES".format("0" + str(hourlyPercentage[hour][0]) if int(hourlyPercentage[hour][0]) < 10 else hourlyPercentage[hour][0],
                                     hourlyPercentage[hour][0] + 1,
                                     hourlyPercentage[hour][1],
                                     panesMesPromedioHora[hour][1],
                                     quarterHourly[hour][1],
                                     panesCuartoPromedioHora[hour][1]
                                     ))
print("_______________________________")

print("PORCENTAJES DE VENTA POR DIA DE LA SEMANA EN LOS ULTIMOS", diasVenta, "Y", diasVentaQuarter, "DIAS")
try:
    for day in weekdayPercentage:
        print("{} = \t{}%\t|| {}%".format(diasDeLaSemana[day[0]], day[1], quarterWeekday[day[0]][1]))
except IndexError:
    print("{} = \t{}%\t|| {}%".format(diasDeLaSemana[day[0]], day[1], quarterWeekday[day[0] - 1][1]))
print("_______________________________")

connection.close()
input()

