import cx_Oracle
import os
import time
import threading
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk, scrolledtext
from ttkthemes import *
import sqlite3
from tkinter import messagebox


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

connDict={"QADB2":{"HOST":"qadb2","PORT":"1521","SID":"qadb2","UID":"foxtrot","PWD":"foxtrot","ISPROD":"NO"},
          "WEBUAT01":{"HOST":"webuat01","PORT":"1521","SID":"webuat01", "UID":"foxtrot","PWD":"foxtrot","ISPROD":"NO"},
          "WEBDB":{"HOST":"webdb","PORT":"1521","SID":"webdb", "UID":"mhidayathulla","PWD":"Password@1","ISPROD":"YES"}}
ConnectDBNames=["SRC","TGT"]
  
#Defining Widgets
 
r=Tk()
r.title("QA Process Automation Tool")
style = ThemedStyle(r)
style.set_theme("scidgreen")
print(style.theme_names())

stylettk=ttk.Style()
#stylettk.configure('TScrolledText', background='red')


# w = 799
# h = 550
 
w = 500
h = 500
ws = r.winfo_screenwidth()
hs = r.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
r.geometry('%dx%d+%d+%d' % (w, h, x, y-50))
r.resizable(False, False)
  
  
frameslist={}
  
def openframe(frameN):
    for key in frameslist:
        if key!=frameN:
            frameslist[key].place_forget()
        else:
            frameslist[key].place(x=1,y=1,height=h-1, width=w-1)
        
    
  
mb= Menu(r)
menuFile=Menu(mb, tearoff=0)
menuFile.add_command(label="Exit", command=r.destroy)
mb.add_cascade(label="File",menu=menuFile)
  
menuTask=Menu(mb, tearoff=0)
menuTask.add_command(label="Copy Rules", command=lambda:openframe("frameRules"))
menuTask.add_command(label="Gather Source Data", command=lambda:openframe("frameGatherSourceData"))
menuTask.add_command(label="SBI Validation", command=lambda:openframe("frameSbiValidation"))
mb.add_cascade(label="Task",menu=menuTask)
  
menuSettings=Menu(mb, tearoff=0)
menuSettings.add_command(label="Database", command=lambda:openframe("frameSettingsDatabase"))
mb.add_cascade(label="Settings",menu=menuSettings)

#r.config(menu=mb)



frameRules = ttk.Frame(r)
frameslist["frameRules"]=frameRules
frameRules.place(x=1,y=1,height=h-1, width=w-1)

lblRulesTitle=ttk.Label(frameRules, text="Rules Transfer Mode", font="helvetica 16")
lblRulesTitle.place(x=150,y=15)



lblRulesEnvironment=ttk.Label(frameRules, text="Source :                           Target :", font="helvetica 10")
lblRulesEnvironment.place(x=100,y=75)



varSrcEnvironment = StringVar()
varTgtEnvironment = StringVar()
#varEnvironment.set("Select Environment")
getEnvironmentList=["Select DB","QADB2","WEBUAT01","WEBDB"]

ddRulesSourceEnvironment=ttk.OptionMenu(frameRules, varSrcEnvironment, *getEnvironmentList)
ddRulesSourceEnvironment.place(x=100, y=100)

ddRulesTargetEnvironment=ttk.OptionMenu(frameRules, varTgtEnvironment, *getEnvironmentList)
ddRulesTargetEnvironment.place(x=260, y=100)


lblRulesMapperName=ttk.Label(frameRules, text="Mapper Name: ", font="helvetica 10")
lblRulesMapperName.place(x=100,y=140)

txtRulesMapperName=ttk.Entry(frameRules, width=20)
txtRulesMapperName.place(x=225,y=140)

lblRulesMultiMapperNotice=ttk.Label(frameRules, text="Comma Separated for more Mappers (ex: EVR40, ATT40)", font="helvetica 7")
lblRulesMultiMapperNotice.place(x=225,y=165)


def fn_txtRulesClientExcludeList(value):
    clientlist=""
    if value==0:
        txtRulesClientExcludeList.config(state=DISABLED)
        txtRulesClientExcludeList.config(bg="light gray")
    elif value==1:
        txtRulesClientExcludeList.config(state=NORMAL)
        txtRulesClientExcludeList.config(bg="white")
    


rbVar=IntVar()

rbRulesClientExcludeList1=ttk.Radiobutton(frameRules, text = "Auto Exclude Clients", variable = rbVar , value = 0, command=lambda:fn_txtRulesClientExcludeList(0))
rbRulesClientExcludeList1.place(x=100, y=180)
rbRulesClientExcludeList2= ttk.Radiobutton(frameRules, text = "Add Exclude Clients", variable = rbVar , value = 1, command=lambda:fn_txtRulesClientExcludeList(1))
rbRulesClientExcludeList2.place(x=250, y=180)
rbVar.set(0)

txtRulesClientExcludeList=Text(frameRules, width=25, height=2,state=DISABLED, bg="light gray")
txtRulesClientExcludeList.place(x=225,y=210)

lblRulesExcludeClientNotice=ttk.Label(frameRules, text="Comma Separated (ex: MIC, DMO, UT1)", font="helvetica 8")
lblRulesExcludeClientNotice.place(x=225,y=250)

pbRules=ttk.Progressbar(frameRules, orient = HORIZONTAL, length = 185, mode = 'determinate')

btnRulesCopy=ttk.Button(frameRules ,text="Copy Rules")
btnRulesCopy.place(x=225, y=280)


lblRulesLog=ttk.Label(frameRules, text="Rules Copy Log", font="helvetica 8")
lblRulesLog.place(x=30,y=310)

# txtRulesLog=Text(frameRules, width=55, height=9)
# txtRulesLog.place(x=25, y=330)

txtRulesLog=scrolledtext.ScrolledText(frameRules, width=70, height=9, font="helvetica 8")
txtRulesLog.place(x=30, y=330)

frameGatherSourceData = ttk.Labelframe(r, height=200, width=200, text="2")
frameslist["frameGatherSourceData"]=frameGatherSourceData

frameSbiValidation = ttk.Labelframe(r, height=200, width=200, text="3")
frameslist["frameSbiValidation"]=frameSbiValidation

frameSettingsDatabase= ttk.Frame(r, height=200, width=200)
frameslist["frameSettingsDatabase"]=frameSettingsDatabase

lblDBID=ttk.Label(frameSettingsDatabase, text="DB Name : ")
lblDBID.place(x=100, y=45)
txtDBID=ttk.Entry(frameSettingsDatabase, width=30)
txtDBID.place(x=100, y=65)
lblDBHost=ttk.Label(frameSettingsDatabase, text="Host / IP : ")
lblDBHost.place(x=100, y=65)
txtDBHost=ttk.Entry(frameSettingsDatabase, width=30)
txtDBHost.place(x=200, y=65)
lblDBUserId=ttk.Label(frameSettingsDatabase, text="User ID : ")
lblDBUserId.place(x=100, y=85)
txtDBUserId=ttk.Entry(frameSettingsDatabase, width=30)
txtDBUserId.place(x=200, y=85)
lblDBPwd=ttk.Label(frameSettingsDatabase, text="Password : ")
lblDBPwd.place(x=100, y=105)
txtDBPWD=ttk.Entry(frameSettingsDatabase, width=30, show="*")
txtDBPWD.place(x=200, y=105)
txtDBPort=ttk.Entry(frameSettingsDatabase, width=5)
txtDBPort.place(x=400, y=65)
txtDBServiceName=ttk.Entry(frameSettingsDatabase, width=30)


chkDefaultVar=StringVar()

chkboxIsDefault=ttk.Checkbutton(frameSettingsDatabase, text="Save as Default", variable = chkDefaultVar, onvalue = "YES", offvalue = "NO")

btnSettingsSave=ttk.Button(frameSettingsDatabase,text="Save Settings")




def fullduration(seconds):
    return str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(seconds)))


#===================Start DB Connection====================
pool=""


def startConnection():
    global dbStatus
    if dbStatus.upper()!="CONNECTED" or varSrcEnvironment.get()!=ConnectDBNames[0] or varTgtEnvironment.get()!=ConnectDBNames[1]:
        global sourceConnection, sourceCursor
        txtRulesLog.insert(END, "======================================================================")
        txtRulesLog.see(END)
        print("Oracle Instant Client Path: " + os.path.realpath(oracleInstantClient.replace("\\","\\\\")))
        txtRulesLog.insert(END, "Oracle Instant Client Path: " + os.path.realpath(oracleInstantClient.replace("\\","\\\\")) + "\n")
        if str(os.environ["path"]).find(oracleInstantClient)>=0:
            print("Path Exist")
            txtRulesLog.insert(END,"Path Exist\n")
        else:
            os.environ["path"]=os.path.realpath(oracleInstantClient.replace("\\","\\\\")) + os.pathsep + os.environ["path"]
            print("path added")
            txtRulesLog.insert(END,"Path Added\n")
        global pool , source_pool

        try:
            pbRules['value']=1
            dbStatus="Connecting..."
            print(dbStatus)
            txtRulesLog.insert(END,f"{dbStatus}\n")
            txtRulesLog.see(END)
            pbRules['value']=5
            
            source_pool = cx_Oracle.SessionPool(connDict[varSrcEnvironment.get()]["UID"],connDict[varSrcEnvironment.get()]["PWD"], f'{connDict[varSrcEnvironment.get()]["HOST"]}:{connDict[varSrcEnvironment.get()]["PORT"]}/{connDict[varSrcEnvironment.get()]["SID"]}' , min=1, max=1, increment=0, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
            pool = cx_Oracle.SessionPool(connDict[varTgtEnvironment.get()]["UID"],connDict[varTgtEnvironment.get()]["PWD"], f'{connDict[varTgtEnvironment.get()]["HOST"]}:{connDict[varTgtEnvironment.get()]["PORT"]}/{connDict[varTgtEnvironment.get()]["SID"]}' , min=5, max=5, increment=1, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
            
            pbRules['value']=7

            dbStatus="Connected"
            ConnectDBNames[0]=varSrcEnvironment.get()
            ConnectDBNames[1]=varTgtEnvironment.get()
            print(f"{dbStatus} to {ConnectDBNames[0]} / {ConnectDBNames[1]}")
            txtRulesLog.insert(END,f"{dbStatus} to {ConnectDBNames[0]} / {ConnectDBNames[1]}\n")
        
        except Exception as e:
            print(e)
            txtRulesLog.insert(END,e)
        
        txtRulesLog.see(END)

def insertRules(getRows,prep_insert_rec,progressValue):
    global totrecords
    local_counter=counter
    poolTime=time.perf_counter()
    targetConnection2 = pool.acquire()
    targetConnection2.autocommit=True
    targetCursor2=targetConnection2.cursor()
    print(f"Rules Insert in batch {local_counter}")
    txtRulesLog.insert(END,f"Rules Insert in batch {local_counter}\n")
    txtRulesLog.see(END)
    #targetCursor2.executemany("insert into V_BILLING_DATA_RULES values (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27)", getRows)
    targetCursor2.executemany(prep_insert_rec, getRows)
     
    totrecords+=targetCursor2.rowcount
    print(f"INSERTED : {targetCursor2.rowcount} rules in batch {local_counter}, Time Taken: {fullduration(time.perf_counter()-poolTime)}")
    txtRulesLog.insert(END,f"INSERTED : {targetCursor2.rowcount} rules in batch {local_counter}, Time Taken: {fullduration(time.perf_counter()-poolTime)}\n")
    txtRulesLog.see(END)
    pool.release(targetConnection2)
    pbRules['value']=pbRules['value']+progressValue
 
 
def deleteRules(delete_query, delcounter,progressValue): 
    global totrecords
    pooldelTime=time.perf_counter()
    tgt_con_delete=pool.acquire()
    tgt_con_delete.autocommit=True
    tgt_cur_delete=tgt_con_delete.cursor()
    print(f"Rules Delete in batch {delcounter}")
    txtRulesLog.insert(END,f"Rules Delete in batch {delcounter}\n")
    txtRulesLog.see(END)
    tgt_cur_delete.execute(delete_query)
    totrecords+=tgt_cur_delete.rowcount
    print(f"DELETED : {tgt_cur_delete.rowcount} rules in batch {delcounter}, Time Taken : {fullduration(time.perf_counter()-pooldelTime)}") 
    txtRulesLog.insert(END,f"DELETED : {tgt_cur_delete.rowcount} rules in batch {delcounter}, Time Taken : {fullduration(time.perf_counter()-pooldelTime)}\n")
    txtRulesLog.see(END)
    pool.release(tgt_con_delete)
    pbRules['value']=pbRules['value']+progressValue
 
 
def dbConnection(mapperName):
    global cursor, dbStatus, conn, mapper_name, connstr1, connstr2, sourceConnection, targetConnection, sourceCursor, targetCursor, target_clients
    global over_all_time, prep_insert_rec, totrecords
    targetConnection=pool.acquire()
    sourceConnection = source_pool.acquire()
    pbRules['value']=8
    sourceCursor=sourceConnection.cursor()
    targetCursor=targetConnection.cursor()
    pbRules['value']=9
     
    mapper_name=mapperName
    txtRulesLog.insert(END, f"------------------------------STARTING RULES FOR {mapper_name} Mapper-----------------------------\n")
    txtRulesLog.see(END)
         
    if 1==1:
        pbRules['value']=10
        over_all_time=time.perf_counter()
          
        # perform fetch and bulk insertion
#        query="Select * from test_Rules_Table WHERE SOURCE_FORMAT_NAME='{mapper_name}'"
        
# getting client list in Target
        print("Getting Client list from Target...")
        if rbVar.get()==0:
            txtRulesLog.insert(END,"Getting Client list from Target...\n")
            txtRulesLog.see(END)
            targetCursor.execute("SELECT SHORT_NAME from CLIENT where length(short_name)=3")
            pbRules['value']=15
            target_clients=targetCursor.fetchall()
            pbRules['value']=20
            l=[p[0] for p in target_clients]
            clientlist="upper(CLIENT_SHORT_NAME) in ('" + "','".join(l).upper() + "')"
        elif rbVar.get()==1:
            clientlist="upper(CLIENT_SHORT_NAME) NOT in ('" + "','".join(client.strip().upper() for client in txtRulesClientExcludeList.get("1.0",END).split(","))+ "')"
    
        print(clientlist)
        
 
        query=f"Select * from {rules_table_name} WHERE SOURCE_FORMAT_NAME='{mapper_name}' AND (CLIENT_SHORT_NAME IS NULL or {clientlist})"
        print(f"Deleting rules for {mapper_name}")
        txtRulesLog.insert(END,f"Deleting rules for {mapper_name}\n")
        txtRulesLog.see(END)
        
        delete_start_time =time.perf_counter()
        totrecords=0
        delcounter=1
        delprocesses=[]
        delqueries=[f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and LOCATOR_PATH='/ATTRIBUTES/LKPCHRGCHARGE' and upper(CHARGE_TYPE_NAME) not in ('OCC','ACCESS')",
                    f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and LOCATOR_PATH='/ATTRIBUTES/LKPCHRGCHARGE' and upper(CHARGE_TYPE_NAME) in ('OCC','ACCESS')",
                    f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and LOCATOR_PATH='/ATTRIBUTES/LKPCHRGUSAGE' and upper(SERVICE_TYPE_NAME) = 'VOICE'",
                    f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and LOCATOR_PATH='/ATTRIBUTES/LKPCHRGUSAGE' and upper(SERVICE_TYPE_NAME) = 'DATA'",
                    f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and LOCATOR_PATH='/ATTRIBUTES/LKPCHRGUSAGE' and upper(SERVICE_TYPE_NAME) = 'SMS'",
                    f"Delete from V_billing_data_rules where source_format_name='{mapper_name}' and ((LOCATOR_PATH='/ATTRIBUTES/LKPCHRGUSAGE' and upper(SERVICE_TYPE_NAME) not in ('VOICE','DATA','SMS')) or (LOCATOR_PATH is null))"]
        progressValue=40/(len(delqueries)+1)
        for delquery in delqueries:
            delete_t1=threading.Thread(target=deleteRules, args=(delquery,delcounter,progressValue,), daemon=True)
            delete_t1.start()
            delprocesses.append(delete_t1)
            delcounter+=1
        
        for delprocess in delprocesses:
            delprocess.join()
        
        deleteRules(f"Delete from V_billing_data_rules where source_format_name='{mapper_name}'",len(delqueries)+1,progressValue)
        
        print(f"Total Time to Delete {totrecords} rules : " + fullduration(time.perf_counter() - delete_start_time))
        txtRulesLog.insert(END,f"Total Time to Delete {totrecords} rules : " + fullduration(time.perf_counter() - delete_start_time) + "\n")
        txtRulesLog.see(END)
        #pbRules['value']=35
        # startt=time.perf_counter()
        
        insert_start_time=time.perf_counter()
        
        sourceCursor.execute(f"SELECT COUNT(*) from {rules_table_name} where SOURCE_FORMAT_NAME='{mapper_name}' AND (CLIENT_SHORT_NAME IS NULL or {clientlist})")
        cnt1=sourceCursor.fetchone()[0]
        sourceCursor.close()
        source_pool.release(sourceConnection)

        sourceConnection=source_pool.acquire()
        sourceCursor=sourceConnection.cursor()

        print(f"Setting up plan to Insert {cnt1} rules")
        txtRulesLog.insert(END,f"Setting up plan to Insert {cnt1} rules\n")
        txtRulesLog.see(END)
        divValue=5
        arrayThreshold=1500
        cnt2=round(cnt1/divValue)
        
        if cnt2<=arrayThreshold:
            sourceCursor.arraysize = cnt2+10
            sourceCursor.prefetchrows = cnt2+10
        else:
            sourceCursor.arraysize = arrayThreshold
            sourceCursor.prefetchrows = arrayThreshold
            divValue=cnt1/arrayThreshold
            
        
        print(f"Searching rules for {mapper_name} with plan route {cnt2+10}")
        txtRulesLog.insert(END,f"Searching rules for {mapper_name} with plan route {cnt2+10}\n")
        txtRulesLog.see(END)
        
        sourceCursor.execute(query)
        #pbRules['value']=40
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
        progressValue=40/divValue
        while True:
#            pbRules['value']=pbRules['value']+(50/divValue)
            time.sleep(2)
            rows=sourceCursor.fetchmany()
            if not rows:
                break      
            print(f"Fetching rules for batch {counter}")
            txtRulesLog.see(END)
            txtRulesLog.insert(END,f"Fetching rules for batch {counter}\n")
            t1=threading.Thread(target=insertRules, args=(rows,prep_insert_rec,progressValue,), daemon=True)
            t1.start()
            processes.append(t1)
            counter+=1
 
        for process in processes:
            process.join()
 
        pbRules['value']=90
        print(f"Insertion of {totrecords} rules completed successfully!")
        txtRulesLog.insert(END,f"Insertion of {totrecords} rules completed successfully!\n")
        print("Inserted in " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - insert_start_time))))
        txtRulesLog.insert(END,"Inserted in " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - insert_start_time))) + "\n")
        print(f"Total Time Taken : " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - over_all_time))))
        txtRulesLog.insert(END,f"Total Time Taken : " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - over_all_time))) + "\n")
        sourceCursor.close()
        source_pool.release(sourceConnection)
        txtRulesLog.see(END)
    else:
# #    except Exception as e:
#         dbStatus="Connection Error : " #+ str(e)
#         print(dbStatus)
#  #   finally:
#         print("Connection Closed...")
#         try:
#             pool.close()
#             sourceCursor.close()
#             targetCursor.close()
#         except:
#             pass
#         try:
#             sourceConnection.close()
#             targetConnection.close()
#         except:
#             pass
        txtRulesLog.see(END)
        pass
    
    return dbStatus
 
def fn_ProdRules():
    for mapper in txtRulesMapperName.get().upper().split(","):
        checkt=time.perf_counter()
        btnRulesCopy.place_forget()
        pbRules.place(x=225, y=280)
        startConnection()
        dbConnection(mapper.strip().upper())
        pbRules['value']=100
        pbRules.place_forget()
        btnRulesCopy.place(x=225, y=280)
        txtRulesLog.insert(END, f"------------------------------COPIED RULES FOR {mapper.strip().upper()} Mapper-----------------------------\n")
        txtRulesLog.see(END)
        
    print(fullduration(time.perf_counter()-checkt))
    txtRulesLog.insert(END, "======================================================================")
    txtRulesLog.see(END)


def fn_start_prodRules():
    if varSrcEnvironment.get().upper()=="SELECT DB" or varTgtEnvironment.get().upper()=="SELECT DB":
        messagebox.showerror("Missing DB Selection", "Kindly select both Source and Target Database before running")
    elif(varSrcEnvironment.get()==varTgtEnvironment.get()):
        messagebox.showerror("Source and Target are Same", f"Selected Source DB and Target DB are same\n{varSrcEnvironment.get()} == {varTgtEnvironment.get()}")
    elif(connDict[varTgtEnvironment.get()]["ISPROD"]=="YES"):
        messagebox.showerror("Invalid Selection", f"Target cannot be set to Production instance \n{varTgtEnvironment.get()}")
    else:
        th_ProdRules=threading.Thread(target=fn_ProdRules)
        th_ProdRules.start()


btnRulesCopy.config(command=lambda:fn_start_prodRules())

#===================End DB Connection====================


r.mainloop()