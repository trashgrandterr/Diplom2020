import json
import os
import sys
import re
import requests
from math import sin, cos, sqrt, atan2, radians
TOKEN = os.environ['TOKEN']
YOUR_PHONE = os.environ['YOUR_PHONE']
YOUR_GOV_PASS = os.environ['YOUR_GOV_PASS']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

def get_receipt_data(data):
    #Get the file urll
    print("----Get the file url")
    received_image_dict = data["message"]["photo"]
    qr_code_photo = str(received_image_dict[1]["file_id"])
    print("qr code id: " + qr_code_photo)
    
    url_get_file = BASE_URL + "/getFile?file_id={}".format(qr_code_photo)
    file_id_request = requests.get(url_get_file)
    file_id_json = file_id_request.json() 
    file_id_path = file_id_json["result"]["file_path"]
    url_photo_link = "https://api.telegram.org/file/bot{}/".format(TOKEN) + file_id_path

    #Get QR code info and Receipt data
    print("----Get QR code info")
    qr_request_url = "https://api.qrserver.com/v1/read-qr-code/?fileurl={}".format(url_photo_link)
    print("Target:{}".format(qr_request_url))
    qr_data = requests.get(qr_request_url)
    qr_data_dict = qr_data.json()
    qr_scanned_data = str(qr_data_dict[0]["symbol"][0]["data"])
    print(qr_scanned_data)
    gov_service_response = get_qr_data_processed(qr_scanned_data)

    
    return gov_service_response


#Process QR code
def get_qr_data_processed(qr_data):

    #Get the QR code's variables
    print("---Get the QR code's variables" + qr_data)
    t=re.findall(r't=(\w+)', qr_data)[0]
    s=re.findall(r's=(\w+)', qr_data)[0]
    fn=re.findall(r'fn=(\w+)', qr_data)[0]
    i=re.findall(r'i=(\w+)', qr_data)[0]
    fp=re.findall(r'fp=(\w+)', qr_data)[0]
    #qr_data_dict = {"t" : t, "s" : s, "fn" : fn, "i" : i, "fp" : fp}

    #Get info from the government's service
    print("---Get info from the government's service")
    headers = {'Device-Id':'', 'Device-OS':''}
    #payload = {'fiscalSign': fp, 'date': t,'sum':s} 
    request_info_json = requests.get('https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss/'+fn+'/tickets/'+i+'?fiscalSign='+fp+'&sendToEmail=no',headers=headers,auth=(YOUR_PHONE, YOUR_GOV_PASS))
    print(request_info_json.status_code)
    receipt_dict = request_info_json.json()

    #product_one_name = receipt_dict["document"]["receipt"]["items"][0]["name"]
    return receipt_dict

def calcualte_cost(trip_path):
    trip_temp = trip_path
    calculted_cost = 0
    while "/" in trip_temp:
        city_pos = trip_temp.find('/')
        city = trip_temp[0:city_pos-1]
        days = re.search('\d+', city)
        city = city.replace(days, '')
        trip_temp = trip_temp[city_pos+1:]
        response = requests.get('https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=' + city +'rvsection=0&rvparse&utf8')
        data = response['query']['pages']['content']
        population_pos = data.find('<th>Население ')
        population = ''
        while data[population_pos] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            population += data[population_pos]
            population_pos += 1
        
        coords1_pos = data.find('°')
        longtitude_big = data[coords1_pos - 2 : coords1_pos]
        longtitude_small = data[coords1_pos : coords1_pos + 2]
        longtitude_str = longtitude_big + longtitude_small
        longtitude = int(longtitude_str)

        data_split = data[coords1_pos+1:]
        coords2_pos = data_split.find('°')
        latitude_big = data[coords2_pos - 2 : coords2_pos]
        latitude_small = data[coords2_pos : coords2_pos + 2]
        latitude_str = latitude_big + latitude_small
        latitude = int(longtitude_str)
        distance = coords_to_km(longtitude_big, longtitude_small, latitude_big, latitude_small)
        if distance > 100:
            calcualte_cost += days * 1600 + distance * 2
        elif distance < 100 and distance != 0:
            calcualte_cost += days * 2000 * 2 * 100/distance * 0.5 + days * 600 * 3 * 100/distance * 0.3 + distance * 2
        else: 
            calcualte_cost += days * 4900 + distance*2 
    return calculted_cost

def coords_to_km(lon1, lon2, lat1, lat2):
    R = 6373.0

    lat1 = radians(52.2296756)
    lon1 = radians(21.0122287)
    lat2 = radians(52.406374)
    lon2 = radians(16.9251681)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance  

def generatereport(userId, date, receipts):
    fileName = 'Отчет' + str(userId) + str(date) +'.pdf'
    data = []
    i = 0
    sum = 0
    full_sum = 0
    for receipt in receipts:
        purchased_items = receipt["document"]["receipt"]["items"]
        receiptId = receipt["document"]["receipt"]["kktRegId"]
        date_temp = receipt["document"]["receipt"]["dateTime"]
        date_temp_day = date_temp[0:9]
        receipt_data_temp = []
        for item in purchased_items:
            i  = i + 1
            sum = item['sum']
            full_sum += sum
            receipt_data_temp.extend([i, receiptId, date_temp_day, item, sum])
            data.append(receipt_data_temp)
        

    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from io import BytesIO
    pdf_buffer = BytesIO()

    pdf = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter
    )

    from reportlab.platypus import Table
    from reportlab.pdfbase.ttfonts import TTFont
    table = Table(data)

    # add style
    from reportlab.platypus import TableStyle
    from reportlab.lib import colors

    pdfmetrics.registerFont(TTFont('OpenSans-Bold', 'fonts/OpenSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans', 'fonts/OpenSans-Regular.ttf'))

    style = TableStyle([
        ('BACKGROUND', (0,0), (3,0), colors.gray),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),

        ('FONTNAME', (0,0), (-1,0), 'OpenSans-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
    ])
    table.setStyle(style)

    # 2) Alternate backgroud color
    rowNumb = len(data)
    for i in range(1, rowNumb):
        if i % 2 == 0:
            bc = colors.white
        else:
            bc = colors.lightgrey
        
        ts = TableStyle(
            [('BACKGROUND', (0,i),(-1,i), bc), ('FONTNAME', (0,i), (-1,i), 'OpenSans')]
        )
        table.setStyle(ts)

    # 3) Add borders
    ts = TableStyle(
        [
        ('BOX',(0,0),(-1,-1),2,colors.black),

        ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
        ('LINEABOVE',(0,2),(-1,2),2,colors.green),
        ('FONTNAME', (0,0), (-1,0), 'OpenSans-Bold'),

        ('GRID',(0,1),(-1,-1),2,colors.black),
        ]
    )
    table.setStyle(ts)

    elems = []
    elems.append(table)

    pdf.build(elems)
    pdf_value = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return pdf_value


