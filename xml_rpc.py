# -*-coding:utf-8-*-
import xmlrpclib
import csv
import os
import subprocess
import logging
import pandas
import magic



# XML-RPC credentials to access the database PLEASE CHANGE
#dbname = 'mmp.lincersolucoes.com.br'
dbname = 'mmp.lincersolucoes.com.br'
user = 'admin'
pwd = 'mmp@2018'
host = "mmp.lincersolucoes.com.br"
port = 10073

com = xmlrpclib.ServerProxy("http://%s:%s/xmlrpc/common" % (host, port))
uid = com.login(dbname, user, pwd)
sock = xmlrpclib.ServerProxy("http://%s:%s/xmlrpc/object" % (host, port))
print 'Logged in to ' + dbname


full_path = "/home/tosin/Documents/LincerProjects/Decisões.xlsx"

BUF_SIZE = 65536
csv.field_size_limit(1000 * 1024 * 1024)

subprocess.call(["libreoffice", "--headless", "--convert-to", "csv", full_path])
extension = full_path.split(".")[-1]
converted_file = full_path[:-len(extension)] + 'csv'

with open(converted_file, 'rb') as csvfile:
	csvfile.seek(0)
	file_reader = csv.reader(csvfile, delimiter=',')
	header = file_reader.next()
	counter = 0
	for row in file_reader:
		dossie_name = row[0].strip().decode('iso-8859-1').encode('utf8')
		tipo_sentenca_name  =  row[1].strip().decode('iso-8859-1').encode('utf8')
		dossie = sock.execute_kw(dbname, uid, pwd,'dossie.dossie', 'search',[[['name', '=', dossie_name]]])
		sentenca = sock.execute_kw(dbname, uid, pwd,'tipo.sentenca', 'search',[[['name', '=', tipo_sentenca_name]]])
		print dossie
		print sentenca
		counter += 1
		print 'Processing row: %s' %counter

		#if dossie and sentenca:
		print dossie_name
		rowdb = {'dossie_id': dossie[0],'tipo_sentenca_id': sentenca[0]}
		row_id = sock.execute(dbname, uid, pwd, 'dossie.sentenca', 'create', rowdb)
        	#'field2': row[1].decode('iso-8859-1').encode('utf8'),
        #else:
        #	print 'Could not process row: %s' %counter
        #	print 'Because dossie or sentenca was not found %s - %s' %(dossie_name,tipo_sentenca_name)
 		
 		




