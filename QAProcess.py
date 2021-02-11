import cx_Oracle
import os
import time
import threading

#Try GIT

# Defining Variables
dbStatus="Not Connected"
oracleInstantClient=r"_instantclient_19_9_64_lite_test"
cursor=""
conn=""
mapper_name=""
rules_table_name="V_BILLING_DATA_RULES"
target_clients=""
counter=1
totrecords=0
global getRows, targetCursor
getRows=[]
prep_insert_rec=""
connstr1='mhidayathulla/Password@1@webdb:1521/webdb'
connstr2='foxtrot/foxtrot@qadb2:1521/qadb2'
connstr3='qadb2:1521/qadb2'

print("Oracle Instant Client Path: " + os.path.realpath(oracleInstantClient.replace("\\","\\\\")))
if str(os.environ["path"]).find(oracleInstantClient)>=0:
    print("Path Exist")
else:
    os.environ["path"]=os.path.realpath(oracleInstantClient.replace("\\","\\\\")) + os.pathsep + os.environ["path"]
    print("path added")



try:
    dbStatus="Connecting..."
    print(dbStatus)    
    sourceConnection = cx_Oracle.connect(connstr1)
#     targetConnection = cx_Oracle.connect(connstr2)
    pool = cx_Oracle.SessionPool('foxtrot','foxtrot', connstr3 , min=5, max=5, increment=1, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
    sourceCursor=sourceConnection.cursor()
    sourceCursor.arraysize = 500
    sourceCursor.prefetchrows = 500

    dbStatus="Connected"
    print(dbStatus)
except Exception as e:
    print(e)


def insertRules(getRows,prep_insert_rec):
    global totrecords
    local_counter=counter
    poolTime=time.perf_counter()
    targetConnection2 = pool.acquire()
    targetConnection2.autocommit=True
    targetCursor2=targetConnection2.cursor()
    print(f"Rules Insert in {local_counter},  Start time {poolTime} secs")
    #targetCursor2.executemany("insert into V_BILLING_DATA_RULES values (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27)", getRows)
    targetCursor2.executemany(prep_insert_rec, getRows)
    
    totrecords+=targetCursor2.rowcount
    print(f"Rules Insert in {local_counter},  End time {time.perf_counter()} secs. Time Taken: {time.perf_counter()-poolTime} Secs, for Inserting {targetCursor2.rowcount}")
    pool.release(targetConnection2)



def dbConnection():
    global cursor, dbStatus, conn, mapper_name, connstr1, connstr2, sourceConnection, targetConnection, sourceCursor, targetCursor, target_clients
    global over_all_time, prep_insert_rec, totrecords
    targetConnection=pool.acquire()
    targetCursor=targetConnection.cursor()
    
    
    mapper_name=input("Enter Mapper Name [Ex. EVR40 or ATT40] :  ").upper()

    try:
        over_all_time=time.perf_counter()
         
        # perform fetch and bulk insertion
#        query="Select * from test_Rules_Table WHERE SOURCE_FORMAT_NAME='EVR40'"

# getting client list in Target
        print("Getting Client list from Target...")
        targetCursor.execute("SELECT SHORT_NAME from CLIENT where length(short_name)=3")
        target_clients=targetCursor.fetchall()
        l=[p[0] for p in target_clients]

        query=f"Select * from {rules_table_name} WHERE SOURCE_FORMAT_NAME='{mapper_name}' AND (CLIENT_SHORT_NAME IS NULL or upper(CLIENT_SHORT_NAME) in ('" + "','".join(l).upper() + "'))"
        print(f"Deleting rules for {mapper_name}")
        startt=time.perf_counter()
        targetCursor.execute(f"Delete from {rules_table_name} where SOURCE_FORMAT_NAME='{mapper_name}'")
        targetConnection.commit()
        print("DELETED : " + str(targetCursor.rowcount) + " rules, Time Taken : " + str(time.perf_counter()-startt)) 
         
        # startt=time.perf_counter()
        print(f"Searching rules from Production for {mapper_name}")
        sourceCursor.execute(query)
        col_names = [row[0] for row in sourceCursor.description]
        prep_insert_rec=""
        for i in range(1,len(col_names)+1):
            prep_insert_rec = prep_insert_rec + f":{i} "
         
        prep_insert_rec =f"insert into {rules_table_name} values ({prep_insert_rec.strip().replace(' ',', ')})"
        #print(prep_insert_rec)
        # print("Execute 1 : " + str(time.perf_counter()-startt))
        
        global counter, getRows
        counter=1
        totrecords=0
        processes=[]
        pool.release(targetConnection)
        while True:
                   
            time.sleep(2)
            rows=sourceCursor.fetchmany()
            if not rows:
                break      
            print(f"Fetching rules for batch {counter}")
            t1=threading.Thread(target=insertRules, args=(rows,prep_insert_rec,), daemon=True)
            t1.start()
            processes.append(t1)
            counter+=1


        for process in processes:
            process.join()



#         try:
#             targetConnection.commit()
#         except Exception as e:
#             print(counter, e)

        print(f"Insertion of {totrecords} rules completed successfully!")
        print(f"Total Time Taken : " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - over_all_time))))


    except Exception as e:
        dbStatus="Connection Error : " + str(e)
        print(dbStatus)
    finally:
        if str(input("Repeat Copying of Rules (Y/N)? : ")).upper()=="Y":
            dbConnection()
        else:
            print("Connection Closed...")
            try:
                pool.close()
                sourceCursor.close()
                targetCursor.close()
            except:
                pass
            try:
                sourceConnection.close()
                targetConnection.close()
            except:
                pass
         
    return dbStatus


dbConnection()


#startTHdbConnection()
#r.mainloop()