import cx_Oracle
import os
import time
import threading
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
from ttkthemes import *




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


  
#Defining Widgets
 
r=Tk()
r.title("QA Process Automation Tool")
style = ThemedStyle(r)
style.set_theme("plastik")
print(style.theme_names())

stylettk=ttk.Style()
#stylettk.configure('TFrame', background='red')


# w = 799
# h = 550
 
w = 500
h = 400
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
menuTask.add_command(label="Copy Prod Rules", command=lambda:openframe("frameRules"))
menuTask.add_command(label="Gather Source Data", command=lambda:openframe("frameGatherSourceData"))
menuTask.add_command(label="SBI Validation", command=lambda:openframe("frameSbiValidation"))
mb.add_cascade(label="Task",menu=menuTask)
  
menuSettings=Menu(mb, tearoff=0)
menuSettings.add_command(label="Database", command=lambda:openframe("frameSettingsDatabase"))
mb.add_cascade(label="Settings",menu=menuSettings)

r.config(menu=mb)



frameRules = ttk.Frame(r)
frameslist["frameRules"]=frameRules
frameRules.place(x=1,y=1,height=h-1, width=w-1)

lblRulesTitle=ttk.Label(frameRules, text="Transfer Production Rules", font="helvetica 16")
lblRulesTitle.place(x=125,y=25)

lblRulesEnvironment=ttk.Label(frameRules, text="Environment: ", font="helvetica 10")
lblRulesEnvironment.place(x=100,y=75)


varEnvironment = StringVar()
#varEnvironment.set("Select Environment")
getEnvironmentList=["","QADB2","WEBUAT01"]

ddRulesEnvironment=ttk.OptionMenu(frameRules, varEnvironment, *getEnvironmentList)
ddRulesEnvironment.place(x=225, y=70)


lblRulesMapperName=ttk.Label(frameRules, text="Mapper Name: ", font="helvetica 10")
lblRulesMapperName.place(x=100,y=110)

txtRulesMapperName=ttk.Entry(frameRules, width=20)
txtRulesMapperName.place(x=225,y=110)

rbVar=StringVar()

rbRulesClientExcludeList1=ttk.Radiobutton(frameRules, text = "Auto Exclude Clients", variable = rbVar , value = "1")
rbRulesClientExcludeList1.place(x=100, y=150)
rbRulesClientExcludeList2= ttk.Radiobutton(frameRules, text = "Add Exclude Clients", variable = rbVar , value = "0")
rbRulesClientExcludeList2.place(x=250, y=150)
rbVar.set("1")

txtRulesClientExcludeList=Text(frameRules, width=25, height=2,state=DISABLED, bg="light gray")
txtRulesClientExcludeList.place(x=225,y=180)

def fn_txtRulesClientExcludeList(event):
    if rbVar.get()=="0":
        txtRulesClientExcludeList.config(state=DISABLED)
        txtRulesClientExcludeList.config(bg="light gray")
    else:
        txtRulesClientExcludeList.config(state=NORMAL)
        txtRulesClientExcludeList.config(bg="white")
        

rbRulesClientExcludeList1.bind("<Button-1>",fn_txtRulesClientExcludeList)
rbRulesClientExcludeList2.bind("<Button-1>",fn_txtRulesClientExcludeList)
rbRulesClientExcludeList1.bind("<space>",fn_txtRulesClientExcludeList)
rbRulesClientExcludeList2.bind("<space>",fn_txtRulesClientExcludeList)


lblRulesExcludeClientNotice=ttk.Label(frameRules, text="Comma Separated", font="helvetica 8")
lblRulesExcludeClientNotice.place(x=225,y=215)

pbRules=ttk.Progressbar(frameRules, orient = HORIZONTAL, length = 185, mode = 'determinate')

btnRulesCopy=ttk.Button(frameRules ,text="Copy Rules")
btnRulesCopy.place(x=225, y=250)


frameGatherSourceData = ttk.Labelframe(r, height=200, width=200, text="2")
frameslist["frameGatherSourceData"]=frameGatherSourceData

frameSbiValidation = ttk.Labelframe(r, height=200, width=200, text="3")
frameslist["frameSbiValidation"]=frameSbiValidation

frameSettingsDatabase= ttk.Labelframe(r, height=200, width=200, text="3")
frameslist["frameSettingsDatabase"]=frameSettingsDatabase





#===================Start DB Connection====================
pool=""


def startConnection():
    global sourceConnection, sourceCursor
    print("Oracle Instant Client Path: " + os.path.realpath(oracleInstantClient.replace("\\","\\\\")))
    if str(os.environ["path"]).find(oracleInstantClient)>=0:
        print("Path Exist")
    else:
        os.environ["path"]=os.path.realpath(oracleInstantClient.replace("\\","\\\\")) + os.pathsep + os.environ["path"]
        print("path added")
     
    global pool , source_pool
     
    try:
        pbRules['value']=1
        dbStatus="Connecting..."
        print(dbStatus)    
        pbRules['value']=5
    #     targetConnection = cx_Oracle.connect(connstr2)

        source_pool = cx_Oracle.SessionPool('mhidayathulla','Password@1', 'webdb:1521/webdb' , min=1, max=1, increment=0, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        pool = cx_Oracle.SessionPool('foxtrot','foxtrot', connstr3 , min=5, max=5, increment=1, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        
        
        pbRules['value']=7
     
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
    sourceConnection = source_pool.acquire()
    pbRules['value']=10
    sourceCursor=sourceConnection.cursor()
    targetCursor=targetConnection.cursor()
    pbRules['value']=15
     
    mapper_name=txtRulesMapperName.get().upper() # input("Enter Mapper Name [Ex. EVR40 or ATT40] :  ").upper()
 
    if 1==1:
        pbRules['value']=20
        over_all_time=time.perf_counter()
          
        # perform fetch and bulk insertion
#        query="Select * from test_Rules_Table WHERE SOURCE_FORMAT_NAME='EVR40'"
 
# getting client list in Target
        print("Getting Client list from Target...")
        targetCursor.execute("SELECT SHORT_NAME from CLIENT where length(short_name)=3")
        pbRules['value']=25
        target_clients=targetCursor.fetchall()
        pbRules['value']=30
        l=[p[0] for p in target_clients]
 
        query=f"Select * from {rules_table_name} WHERE SOURCE_FORMAT_NAME='{mapper_name}' AND (CLIENT_SHORT_NAME IS NULL or upper(CLIENT_SHORT_NAME) in ('" + "','".join(l).upper() + "'))"
        print(f"Deleting rules for {mapper_name}")
 
        startt=time.perf_counter()
        targetCursor.execute(f"Delete from {rules_table_name} where SOURCE_FORMAT_NAME='{mapper_name}'")
        targetConnection.commit()
        print("DELETED : " + str(targetCursor.rowcount) + " rules, Time Taken : " + str(time.perf_counter()-startt)) 
        pbRules['value']=35
        # startt=time.perf_counter()
        
        sourceCursor.execute(f"SELECT COUNT(*) from {rules_table_name} where SOURCE_FORMAT_NAME='{mapper_name}'")
        cnt1=sourceCursor.fetchone()[0]
        sourceCursor.close()
        source_pool.release(sourceConnection)

        sourceConnection=source_pool.acquire()
        sourceCursor=sourceConnection.cursor()

        print(f"Setting up plan to Insert {cnt1} rules")
        cnt2=round(cnt1/5)
        if cnt2<=1500:
            sourceCursor.arraysize = cnt2+10
            sourceCursor.prefetchrows = cnt2+10
        else:
            sourceCursor.arraysize = 1500
            sourceCursor.prefetchrows = 1500
            
        
        
        print(f"Searching rules from Production for {mapper_name} with plan route {cnt2+10}")
        
        sourceCursor.execute(query)
        pbRules['value']=40
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
            pbRules['value']=pbRules['value']+5
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
        pbRules['value']=90
        print(f"Insertion of {totrecords} rules completed successfully!")
        print(f"Total Time Taken : " + str(time.strftime("%H Hours, %M Minutes, %S Seconds", time.gmtime(time.perf_counter() - over_all_time))))
 
    else:
#    except Exception as e:
        dbStatus="Connection Error : " #+ str(e)
        print(dbStatus)
 #   finally:
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
 
def fn_ProdRules():
    checkt=time.perf_counter()
    btnRulesCopy.place_forget()
    pbRules.place(x=225, y=250)
    startConnection()
    dbConnection()
    pbRules['value']=100
    pbRules.place_forget()
    btnRulesCopy.place(x=225, y=250)
    print(time.perf_counter()-checkt)


def fn_start_prodRules():
    th_ProdRules=threading.Thread(target=fn_ProdRules)
    th_ProdRules.start()


btnRulesCopy.config(command=lambda:fn_start_prodRules())

#===================End DB Connection====================


r.mainloop()