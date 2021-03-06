'''
Copyright (c) 2018, АО "ТЕЛЕОФИС"

Разрешается повторное распространение и использование как в виде исходного кода, так и в двоичной форме, 
с изменениями или без, при соблюдении следующих условий:

- При повторном распространении исходного кода должно оставаться указанное выше уведомление об авторском праве, 
  этот список условий и последующий отказ от гарантий.
- При повторном распространении двоичного кода должна сохраняться указанная выше информация об авторском праве, 
  этот список условий и последующий отказ от гарантий в документации и/или в других материалах, поставляемых 
  при распространении.
- Ни название АО "ТЕЛЕОФИС", ни имена ее сотрудников не могут быть использованы в качестве поддержки или 
  продвижения продуктов, основанных на этом ПО без предварительного письменного разрешения.

ЭТА ПРОГРАММА ПРЕДОСТАВЛЕНА ВЛАДЕЛЬЦАМИ АВТОРСКИХ ПРАВ И/ИЛИ ДРУГИМИ СТОРОНАМИ «КАК ОНА ЕСТЬ» БЕЗ КАКОГО-ЛИБО 
ВИДА ГАРАНТИЙ, ВЫРАЖЕННЫХ ЯВНО ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ИМИ, ПОДРАЗУМЕВАЕМЫЕ ГАРАНТИИ 
КОММЕРЧЕСКОЙ ЦЕННОСТИ И ПРИГОДНОСТИ ДЛЯ КОНКРЕТНОЙ ЦЕЛИ. НИ В КОЕМ СЛУЧАЕ НИ ОДИН ВЛАДЕЛЕЦ АВТОРСКИХ ПРАВ И НИ 
ОДНО ДРУГОЕ ЛИЦО, КОТОРОЕ МОЖЕТ ИЗМЕНЯТЬ И/ИЛИ ПОВТОРНО РАСПРОСТРАНЯТЬ ПРОГРАММУ, КАК БЫЛО СКАЗАНО ВЫШЕ, НЕ 
НЕСЁТ ОТВЕТСТВЕННОСТИ, ВКЛЮЧАЯ ЛЮБЫЕ ОБЩИЕ, СЛУЧАЙНЫЕ, СПЕЦИАЛЬНЫЕ ИЛИ ПОСЛЕДОВАВШИЕ УБЫТКИ, ВСЛЕДСТВИЕ 
ИСПОЛЬЗОВАНИЯ ИЛИ НЕВОЗМОЖНОСТИ ИСПОЛЬЗОВАНИЯ ПРОГРАММЫ (ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ПОТЕРЕЙ ДАННЫХ, ИЛИ 
ДАННЫМИ, СТАВШИМИ НЕПРАВИЛЬНЫМИ, ИЛИ ПОТЕРЯМИ ПРИНЕСЕННЫМИ ИЗ-ЗА ВАС ИЛИ ТРЕТЬИХ ЛИЦ, ИЛИ ОТКАЗОМ ПРОГРАММЫ 
РАБОТАТЬ СОВМЕСТНО С ДРУГИМИ ПРОГРАММАМИ), ДАЖЕ ЕСЛИ ТАКОЙ ВЛАДЕЛЕЦ ИЛИ ДРУГОЕ ЛИЦО БЫЛИ ИЗВЕЩЕНЫ О 
ВОЗМОЖНОСТИ ТАКИХ УБЫТКОВ.
'''

import MOD
import MDM, MDM2
import sys

def init():
    sendAT('ATE0', 'OK')
    sendAT('ATS0=0', 'OK')
    sendAT('AT+COPS=0,2', 'OK')
    sendAT('AT+CREG=2', 'OK')

def sendAT(request, response, timeout = 2, interface = 1):
    if(interface == 1):
        MDM.send(request + '\r', 2)
    else:
        MDM2.send(request + '\r', 2)
    result = -2
    data = ''
    timer = MOD.secCounter() + timeout
    while(MOD.secCounter() < timer):
        if(interface == 1):
            rcv = MDM.read()
        else:
            rcv = MDM2.read()
        if(len(rcv) > 0):
            data = data + rcv
            if(data.find(response) != -1):
                result = 0
                break
            if(data.find('ERROR') != -1):
                result = -1
                break
    return (result, data)

def waitRegister():
    while(1):
        r, d = sendAT('AT+CREG?', '+CREG: 2,1')
        if(r == 0):
            break
        MOD.sleep(20)
        
def readImei():
    r, s = sendAT('AT#CGSN', 'OK')
    if(r == 0):
        pos = s.find('#CGSN:')
        if(pos != -1):
            imei = s.replace("OK","").strip()[pos+5:]
            return imei
    return 'ERROR'

def readCCID():
    r, s = sendAT('AT#CCID', 'OK')
    if(r == 0):
        pos = s.find('#CCID:')
        if(pos != -1):
            val = s.replace("OK","").strip()[pos+5:]
            return val
    return "ERROR"

def readCOPS():
    r, s = sendAT('AT+COPS?', 'OK')
    if(r == 0):
        pos = s.find('+COPS:')
        if(pos != -1):
            val = s.replace("OK","").strip()[pos+5:]
            return val
    return "ERROR"

def readCREG():
    r, s = sendAT('AT+CREG?', 'OK')
    if(r == 0):
        pos = s.find('+CREG:')
        if(pos != -1):
            val = s.replace("OK","").strip()[pos+5:]
            return val
    return "ERROR"
