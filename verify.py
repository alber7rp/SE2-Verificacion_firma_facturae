# -*- coding: utf-8 -*-
import requests
import xml.etree.ElementTree as ET
import base64
import re
from termcolor import colored

requests.packages.urllib3.disable_warnings() # Deshabilitar warnings

print(colored("*** MISTIC: Seminario en empresa 2: Verificación de firma sobre factura electrónica ***", 'red'))
print(colored("########################### Alberto Gabriel Ruiz Pérez ################################ \n", 'blue'))

url="https://uoc.safelayer.com:8080/trustedx-gw/SoapGateway"
headers = {'content-type': 'application/soap+xml', 'SOAPAction': 'verify'}

treetemplate = ET.parse('./files/tx_request_template.xml') # Plantilla SOAP
roottemplate = treetemplate.getroot()
Base64XML = roottemplate.find('{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}VerifyRequest/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}InputDocuments/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}Document/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}Base64XML')

while(True):

    pathfactura = str(input(colored("Introduce la ruta del fichero la factura (firmada): ", 'yellow')))

    # Obtener factura y convertirla a formato base64 
    facturastring = open(pathfactura, "r").read()
    facturabase64 = base64.b64encode(bytes(str(facturastring), 'utf-8'))
    Base64XML.text = facturabase64.decode('utf-8') # Incluimos la factura (en base64) dentro de la plantilla SOAP

    # Extraer los valores que consideremos de la factura (emisor, receptor, fecha, precio, etc)
    facturatree = ET.ElementTree(ET.fromstring(facturastring))
    facturaroot = facturatree.getroot()
    Emisor = {}
    Emisor["name"] = facturaroot.find('Parties/SellerParty/LegalEntity/CorporateName').text
    Emisor["DNI"] = facturaroot.find('Parties/SellerParty/TaxIdentification/TaxIdentificationNumber').text
    Receptor = {}
    Receptor["name"] = facturaroot.find('Parties/BuyerParty/LegalEntity/CorporateName').text
    Receptor["DNI"] = facturaroot.find('Parties/BuyerParty/TaxIdentification/TaxIdentificationNumber').text
    Fecha = facturaroot.find('Invoices/Invoice/InvoiceIssueData/IssueDate').text
    Precio = facturaroot.find('FileHeader/Batch/TotalInvoicesAmount/TotalAmount').text
    Moneda = facturaroot.find('FileHeader/Batch/InvoiceCurrencyCode').text

    print(colored("\nInformación sobre la factura:",'magenta'))
    print(colored("Fecha > ",'blue'), Fecha)
    print(colored("Precio total > ",'blue'), Precio, Moneda)
    print(colored("Emisor > ",'blue'), Emisor["name"], ' (', Emisor["DNI"], ")")
    print(colored("Receptor > ",'blue'), Receptor["name"], ' (', Receptor["DNI"], ")")

    # Generamos una request HTTP con el paquete contruido SOAP
    body = ET.tostring(roottemplate)
    response = requests.post(url,data=body,headers=headers,verify=False)

    # Obtenemos los resultados de verificación para mostrarlo por pantalla
    treeresponse = ET.ElementTree(ET.fromstring(response.content))
    rootresponse = treeresponse.getroot()

    Result = rootresponse.find('{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}VerifyResponse/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}Result')
    ResultMajor = Result.find('{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}ResultMajor').text
    ResultMinor = Result.find('{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}ResultMinor').text

    
    print(colored("\nResultado de la verificación:",'magenta'))

    if(re.match('.*Success.*', ResultMajor) == None):
        print ("ResultMajor: ", colored(ResultMajor,'red'))
    else:
        print ("ResultMajor: ", colored(ResultMajor,'green'))

    if(re.match('.*ValidSignature_OnAllDocuments.*', ResultMinor) == None):
        print ("ResultMinor: ", colored(ResultMinor,'red'))
    else:
        print ("ResultMinor: ", colored(ResultMinor,'green'))

    if((re.match('.*Success.*', ResultMajor) == None) or (re.match('.*ValidSignature_OnAllDocuments.*', ResultMinor) == None)):
        ResultMessage = Result.find('{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}ResultMessage').text
        print (colored("\nMotivo de error: ",'cyan'))
        print ("ResultMessage: ", ResultMessage)
    else:
        SignerIdentity = rootresponse.find('{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}VerifyResponse/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}OptionalOutputs/{http://www.docs.oasis-open.org/dss/2004/06/oasis-dss-1.0-core-schema-wd-27.xsd}SignerIdentity').text
        print(colored("SignerIdentity > ",'blue'), SignerIdentity)

    if(str(input(colored("\n\n¿Quieres realizar otra verificación? (s/n): ", 'yellow'))) != 's'):
        break 
