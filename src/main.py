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
import sys
import sms
import sms_msg
import config
import sim
import gsm

#
# START DEBUG
#
import SER
SER.set_speed('9600')
class SERstdout:
    def write(self,s):
        SER.send('%d %s\r\n' % (MOD.secCounter(), s))
sys.stdout = SERstdout()
sys.stderr = SERstdout()
#
# END DEBUG
#

#
# Defines
#
CFG = config.Config('settings.ini')

#
# Functions
#
def sendAlarm(text):
    r = -1;
    for num in CFG.getList('ALARMPHONES'):
        print 'Send alarm to: %s' % (num)
        r = sms.sendSms(sms_msg.SmsMessage('0', num, '', text))
    return r

#
# Main
#
def main():
    try:
        print 'Start CFG init'
        CFG.read()
        CFG.dump()
        
        print 'Start GSM init'
        gsm.init()
        
        print 'Start SMS init'
        sms.init()
        
        print 'Start read IMEI'
        imei = gsm.readImei()
        print 'IMEI: %s' % (imei)
        
        print 'Start read CCID'
        currentCCID = gsm.readCCID()
        print 'CCID: %s' % (currentCCID)
        if(currentCCID == "ERROR"):
            print 'Error reading CCID'
            return
        
        print 'Start read saved CCID'
        savedCCID = sim.readSavedCCID()
        print 'Saved CCID: %s' % (savedCCID)
        if(savedCCID == ""):
            print 'Save CCID: %s' % (currentCCID)
            sim.writeSavedCCID(currentCCID)
            
            if(int(CFG.get('SENDREGISTRATION')) > 0):
                message = 'Registration. IMEI: %s CCID: %s' % (imei, currentCCID)
                print message + '\r\n'
                sendAlarm(message)

            MOD.sleep(2)
            return
        
        if(currentCCID != savedCCID):
            print 'Wait for network registration...'
            gsm.waitRegister()
            
            creg = gsm.readCREG()
            cops = gsm.readCOPS()
            
            message = 'ALARM! IMEI: %s oldCCID: %s newCCID: %s CREG: %s COPS: %s' % (imei, savedCCID, currentCCID, creg, cops)
            
            print message
            r = sendAlarm(message)
            if(r == 0):
                print 'SMS Sent. Save CCID: %s' % (currentCCID)
                if(int(CFG.get('REWRITECCID')) > 0):
                    sim.writeSavedCCID(currentCCID)
                    MOD.sleep(2)
                return
            return
        else:
            print 'CCID not changed'
            return

    except Exception, e:
        print 'Unhandled exception: %s' % e
        return
        
if __name__ == "__main__":
    main()
