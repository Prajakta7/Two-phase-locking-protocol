#Name: Yashika Bansal, UTA ID:1001633809
#Name:Prajakta Ganesh Jalisatgi, UTA ID:1001637722

#import statements
import mysql.connector
import sys
import os.path

#connection to DB
def connect_to_db():
    conn = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='project1')
    return conn

#main function
def main(argv):
    fileName = argv[1]
    
    db = connect_to_db()
    cursor = db.cursor()

    strQuery = 'truncate transaction'
    cursor.execute(strQuery)
    db.commit()

    strQuery = 'truncate lockTable'
    cursor.execute(strQuery)
    db.commit()
    db.close()

    #scan the input file
    if os.path.isfile(fileName):
        fileObject = open(fileName, 'r')
        cntTS = 0

        for line in fileObject.readlines():
            line = line.replace(' ', '')
            curTransList = []
            curTrans = 'T' + line[1]

            db = connect_to_db()
            cursor = db.cursor()

            strQuery = 'Select * from transaction where Tid = \'' + curTrans + '\''
    
            cursor.execute(strQuery)
            data = cursor.fetchall()
            for item in data:
                curTransList = item

            if len(curTransList) == 0:
                if line[0] == 'b':
                    cntTS = cntTS + 1
                exeInstr(line, cntTS)
            else:
                if curTransList[2] == 'Aborted':
                    print('Transaction' + curTrans + ' is aborted ')
                else:
                    if curTransList[2] == 'Blocked':

                        blockedOperations = curTransList[4]
                        line = line.replace('\n','')
                        blockedOperations = blockedOperations.replace('\n','')
                        blockedOperations = blockedOperations + line
                        
                        strQuery = 'update transaction set operation = \'' + blockedOperations + '\' where Tid = \'' + curTrans + '\''
                        cursor.execute(strQuery)
                        db.commit()
                        print('Transaction ' + curTrans +' is waiting' )
                    else:
                        exeInstr(line, cntTS)
            db.close()

#execute statements method
def exeInstr(line,cntTS):
    curTrans = 'T' + line[1]

    #read or write instruction
    if line[0] != 'b' and line[0] != 'e':
        item = line[3]

    #begin instruction
    if line[0] == 'b':
        transactionBegin(curTrans, cntTS)

    #read instruction
    if line[0] == 'r':
        item = line[3]
        readL(item, curTrans, line)

    #write instruction
    if line[0] == 'w':
        item = line[3]
        writeL(item, curTrans, line)

    #end instruction
    if line[0] == 'e':
        commit(curTrans)

#begin Trans method
def transactionBegin(curTrans, cntTS):

    strQuery = 'insert into transaction values (\'' + curTrans + '\', ' + str(cntTS) + ', \'Active\', \'\',\'\')'

    db = connect_to_db()

    cursor = db.cursor()
    cursor.execute(strQuery)

    print('Begin Transaction ' + curTrans + ' ,record created in Transaction table')
    db.commit()
    db.close()

#readLock method
def readL(item, curTrans, line):
    strQuery = 'select * from lockTable where item = \'' + item + '\''
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute(strQuery)

    dItems = cursor.fetchall()

    itemsList = []
    transHold = []
    for row in dItems:
        itemsList.append(row)
        currentItem = row
        transHold = row[2].split('-')

    if len(itemsList) == 0:
        strQuery = 'Insert into lockTable values (\'' + item + '\', \'readLed\', \'' + curTrans + '-\',\'\')'
        cursor.execute(strQuery)
        db.commit()

        strQuery = 'select * from Transaction where Tid = \'' + curTrans + '\''
        cursor.execute(strQuery)

        dItems = cursor.fetchall()
        existingItemsList = []
        for row in dItems:
            existingItemsList = row[3].split('-')

        existingItems = ''

        for row in existingItemsList:
            if row != '':
                existingItems = existingItems + row + '-'

        existingItems = existingItems + item + '-'

        strQuery = 'Update transaction set items = \'' + existingItems + '\' where Tid = \'' + curTrans + '\''
        cursor.execute(strQuery)

        db.commit()

        print('Item ' + item + ' is read locked by Transaction ' + curTrans)
    else:
        if currentItem[1] != 'writeLed':
            transHold.append(curTrans)
            holdTransactions = ''
            for row in transHold:
                if row != '':
                    holdTransactions = holdTransactions + row + '-'
            strQuery = 'Update lockTable set Tid_Holding = \'' + holdTransactions + '\', state = \'readLed\' where item = \'' + item  + '\''
            cursor.execute(strQuery)

            strQuery = 'select items from transaction where Tid = \'' + curTrans + '\''
            cursor.execute(strQuery)
            dataRows = cursor.fetchall()

            curTransItemList = []
            for row in dataRows:
                curTransItemList = row[0].split('-')
            updateItmes = ''
            curTransItemList.append(item)
            for row in curTransItemList:
                if row != '':
                    updateItmes = updateItmes + row + '-'

            strQuery = 'Update transaction set items = \'' + updateItmes + '\' where Tid = \'' + curTrans + '\''
            cursor.execute(strQuery)
            db.commit()
            print('Transaction ' + curTrans + ' granted read lock on item ' + item)
        else:
            # print('wait die read')
            holdTrans = transHold[0]
            # print(holdTrans)
            requestTrans = curTrans
            wound_wait(holdTrans, requestTrans, item, line)
    db.commit()
    db.close()

#write lock method
def writeL(item, curTrans, line):

    strQuery = 'select * from lockTable where item = \'' + item + '\''
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute(strQuery)

    dItems = cursor.fetchall()

    itemsList = []
    transHold = []
    transWait = []
    for row in dItems:
        itemsList.append(row)
        currentItem = row
        transHold = row[2].split('-')
        transWait = row[3].split('-')
    
    cmpTrans = currentItem[2]
    cmpTrans = cmpTrans.replace('-', '')

    #upgrading to write lock
    if (currentItem[1] == 'readLed') and (cmpTrans == curTrans):
        strQuery = 'Update lockTable set state = \'writeLed\' where item = \'' + item + '\''
        cursor.execute(strQuery)
        db.commit()
        # print('idhar')
        print('Item ' + item + ' is upgraded to write lock on Transaction ' + curTrans)
    else:
        # if the item is currently unlocked
        if currentItem[1] == 'Unlocked':
            # print('ya idhar')
            holdTranss = ''
            for row in transHold:
                if row != '':
                    holdTranss = holdTranss + row + '-'
            holdTranss = holdTranss + curTrans + '-'
            strQuery = 'Update lockTable set state = \'writeLed\', Tid_Holding = \''+ holdTranss + '\' where item = \'' + item + '\''
            cursor.execute(strQuery)
            db.commit()

            # update the item in transaction table
            strQuery = 'select items from transaction where Tid = \'' + curTrans + '\''
            cursor.execute(strQuery)
            dataRows = cursor.fetchall()
            # print(dataRows)
            curTransItemList = []
            for row in dataRows:
                # print(row)
                curTransItemList = row[0].split('-')
            updateItmes = ''
            curTransItemList.append(item)
            for row in curTransItemList:
                if row != '':
                    updateItmes = updateItmes + row + '-'

            strQuery = 'Update transaction set items = \'' + updateItmes + '\' where Tid = \'' + curTrans + '\''
            cursor.execute(strQuery)
            db.commit()
            print('Item ' + item + ' is write locked by Transaction ' + curTrans)
        else:
            finaltransHold = []
            # print('phir')
            # remove empty if any
            for trans in transHold:
                if trans != '' and trans != curTrans:
                    finaltransHold.append(trans)

            # call wait die method
            if len(finaltransHold) == 1:
                # print('wait die write')
                wound_wait(finaltransHold[0], curTrans, item, line)
            else:
                # print('wait die for more than one holding')
                strQuery = 'select * from transaction where Tid = \'' + curTrans + '\''
                cursor.execute(strQuery)
                curTransData = cursor.fetchall()
                curTransTimeStamp = 0
                for data in curTransData:
                    curTransTimeStamp = data[1]
                # print('Current Transaction ' + str(curTransTimeStamp))
                flag = 0
                if len(finaltransHold) > 0:
                    for THid in finaltransHold:
                        strQuery = 'select * from transaction where Tid = \'' + THid + '\''
                        cursor.execute(strQuery)
                        dItemsList = cursor.fetchall()
                        holdTransTimeStamp = 0
                        for data in dItemsList:
                            holdTransTimeStamp = data[1]
                        if curTransTimeStamp < holdTransTimeStamp:
                            flag = 1
                        else:
                            # print('Abort curTrans ' + curTrans)
                            flag = 0
                            break
                    if flag == 1:
                        strQuery='Update transaction set status = \'Blocked\', operation = \'' + line + '\' where Tid = \'' +curTrans + '\''
                        cursor.execute(strQuery)
                        db.commit()

                        waitTrans = ''
                        for row in transWait:
                            if row != '':
                                waitTrans = waitTrans + row + '-'

                        # add request Transaction to waiting list for that item
                        strQuery = 'update lockTable set Tid_waiting = \'' + waitTrans + '\' where item = \'' + item + '\''
                        cursor.execute(strQuery)
                        db.commit()

                        db.commit()
                        # print('Wait Current Transaction '+ curTrans)
                    else:
                        # print('Abort curTrans ' + curTrans)
                        abort(curTrans)

    db.commit()
    db.close()

#end Transaction method
def commit(curTrans):

    lockInstr = []

    db = connect_to_db()
    cursor = db.cursor()

    strQuery = 'select * from transaction where Tid = \'' + curTrans + '\''
    cursor.execute(strQuery)

    dItems = cursor.fetchall()
    for row in dItems:
        lockInstr = row[3].split('-')

    strQuery = 'Update transaction set Tstatus = \'commited\', items = \'\' where Tid = \'' + curTrans + '\''
    cursor.execute(strQuery)
    db.commit()

    print('Transaction ' + curTrans + ' committed successfully')

    for items in lockInstr:
        if items != '':
            unlock(curTrans, items)

    db.commit()
    db.close()

# abort method
def abort(curTrans):

    lockInstr = []

    db = connect_to_db()
    cursor = db.cursor()

    strQuery = 'select * from transaction where Tid = \'' + curTrans + '\''
    cursor.execute(strQuery)

    dItems = cursor.fetchall()
    for row in dItems:
        lockInstr = row[3].split('-')

    strQuery = 'Update transaction set Tstatus = \'Aborted\', items = \'\' where Tid = \'' + curTrans + '\''
    cursor.execute(strQuery)
    db.commit()

    print('Transaction ' + curTrans + '   aborted')

    for items in lockInstr:
        if items != '':
            unlock(curTrans, items)
    db.commit()
    db.close()

#unlock method
def unlock(curTrans, item):
    db = connect_to_db()
    cursor = db.cursor()

    strQuery = 'Select * from lockTable where item = \'' + item + '\''
    cursor.execute(strQuery)
    dItems = cursor.fetchall()

    waitTrans = []
    holdTransList = []

    for row in dItems:
        waitTrans = row[3].split('-')
        holdTransList = row[2].split('-')

    holdTrans = ''
    finalholdTransList = []
    for row in holdTransList:
        if row != '' and row != curTrans:
            holdTrans = holdTrans + row + '-'
            finalholdTransList.append(row)
    if len(finalholdTransList) == 0:
        strQuery = 'Update locktable set state = \'Unlocked\', Tid_holding = \'' + holdTrans + '\' where item = \'' + item + '\''
        cursor.execute(strQuery)
        db.commit()
    else:
        strQuery = 'Update locktable set Tid_Holding = \'' + holdTrans + '\' where item = \'' + item + '\''
        cursor.execute(strQuery)
        db.commit()
    finalwaitTrans = []
    for trans in waitTrans:
        if trans != '':
            finalwaitTrans.append(trans)

    if len(finalwaitTrans) != 0:

        curTransWaiting = finalwaitTrans[0]
        finalwaitTrans.remove(curTransWaiting)

        updateTransactionString = ''
        for row in finalwaitTrans:
            updateTransactionString = updateTransactionString + row + '-'
        strQuery = 'Update locktable set Tid_waiting = \'' + updateTransactionString + '\' where item = \'' + item + '\''
        cursor.execute(strQuery)
        db.commit()

        print('Transaction ' + curTransWaiting + ' has resumed')

        strQuery = 'Update transaction set Tstatus = \'Active\' where Tid = \'' + curTransWaiting + '\''
        cursor.execute(strQuery)
        db.commit()

        strQuery = 'select *  from transaction where Tid = \'' + curTransWaiting + '\''
        cursor.execute(strQuery)
        dItems = cursor.fetchall()

        waitInstr = []
        for row in dItems:
            waitInstr = row[4].split(';')
        fwolist = []
        for row in waitInstr:
            if row != '':
                trans = row.replace('\n','')
                finalwaitTrans.append(trans)

        for line in waitInstr:
            line = line.replace('\n', '')
            if line != '':
                exeInstr(line, 1)
                finalOperation = ''
                for ops in fwolist:
                    if ops != line:
                        finalOperation = finalOperation + ops
                strQuery = 'Update transaction set operation = \'' + finalOperation + '\' where Tid = \'' +curTrans + '\''
                cursor.execute(strQuery)
                db.commit()
        db.commit()
        db.close()

#wound_wait method
def wound_wait(holdTrans, requestTrans, currentItem, line):
    db = connect_to_db()
    cursor = db.cursor()

    query = 'select TtimeStamp from transaction where Tid = \'' + holdTrans + '\''

    cursor.execute(query)
    data = cursor.fetchall()
    holdTime = 0
    for item in data:
        holdTime = item

    query = 'select TtimeStamp from transaction where Tid = \'' + requestTrans + '\''
    cursor.execute(query)
    data = cursor.fetchall()
    requestTime = 0
    for item in data:
        requestTime = item

    if requestTime < holdTime:
        abort(holdTrans)
 
    else:
        print(requestTrans + ' Transaction will wait')
        query = 'Update transaction set Tstatus = \'Blocked\', operation = \'' + line + '\' where Tid = \'' + requestTrans + '\''
        cursor.execute(query)
        db.commit()

        query = 'select * from lockTable where item = \'' + currentItem + '\''
        cursor.execute(query)
        dList = cursor.fetchall()

        waitTrans = []
        holdTransList = []
        for row in dList:
            holdTransList = row[2].split('-')
            waitTrans = row[3].split('-')
        waitTrans = ''
        for item in waitTrans:
            if item != '':
                waitTrans = waitTrans + item + '-'
        waitTrans = waitTrans + requestTrans + '-'

        query = 'Update lockTable set Tid_waiting = \'' + waitTrans + '\' where item = \'' + currentItem + '\''
        cursor.execute(query)
        db.commit() 
    db.close()

if __name__ == '__main__':
    main(sys.argv)
