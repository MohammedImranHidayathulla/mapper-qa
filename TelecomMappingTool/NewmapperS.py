from tkinter import *
import os
from tkinter import messagebox
import paramiko as pk
import threading
import time
from tkinter.ttk import Progressbar, Combobox, Notebook
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from paramiko.ssh_exception import SSHException
import sqlite3




r=Tk()
r_title="Telecom Mapper Tool"
r.title(r_title)
w = 600
h = 550
ws = r.winfo_screenwidth()
hs = r.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
r.geometry('%dx%d+%d+%d' % (w, h, x, y))
r.resizable(False, False)


lblSFTPX=15
txtSFTPX=140
sftpY=20
varServer= StringVar()
varServer.set("Select Server")


# txtSFTPServerID
# txtSFTPHost=""
# txtSFTPUserId=""
# txtSFTPPWD=""
# txtSFTPRootPath=""
# txtSFTPSearchPath=""
# txtSFTPOIRJATPath=""
# txtSFTPAppName=""
# txtSFTPJARExtn=""


sftpStatus=""

lblHeading=Label(r, text="Telecom Mapper Tool", font='Helvetica 18 bold')
lblHeading.place(x=175,y=3)

menuBar=Menu(r)
menuServer=Menu(menuBar, tearoff=0)




mainTabs=Notebook(r)
mainTabs.place(x=0,y=35)

tabNewMapperCreation=Frame(mainTabs,height=600, width=600)
tabNewMapperCreation.pack(fill=BOTH, expand=1)
mainTabs.add(tabNewMapperCreation, text="Add Mapper / Client")
newMapperFrame=LabelFrame(tabNewMapperCreation,text="New Mapper", bd=5)
newMapperFrame.place(x=100,y=50,height=200,width=400) 
lblInputVendor=Label(newMapperFrame,text="Java File Name")
lblInputVendor.place(x=30,y=25)
txtInputVendor=Entry(newMapperFrame,text="Enter Vendor Name",width=30)
txtInputVendor.place(x=170,y=25)
lblInputFilePattern=Label(newMapperFrame,text="File Pattern")
lblInputFilePattern.place(x=30,y=60)
txtInputFilePattern=Entry(newMapperFrame,text="Enter File Pattern",width=30)
txtInputFilePattern.place(x=170,y=60)
lblInputClientName=Label(newMapperFrame,text="Client Folder Name")
lblInputClientName.place(x=30,y=95)
txtInputClientName=Entry(newMapperFrame,text="Enter Client Folder Name",width=30)
txtInputClientName.place(x=170,y=95) 
lblmessage=Label(newMapperFrame, fg="black", bg="light green")
btn1=Button(newMapperFrame, bd=1, cursor="hand2")
progressCreation=Progressbar(newMapperFrame, orient = HORIZONTAL, length = 185, mode = 'determinate')
btn1.place_forget()
btn1.place(x=150,y=130)
btn2=Button(newMapperFrame, bd=1, cursor="hand2")
btn2.place_forget()
btn2.place(x=270,y=130)
lblInputVendor.config(text="Java File Name")
newMapperFrame.config(text="Add New Mapper / Add New Client")


tabErrorFilesMonitoring=Frame(mainTabs,height=600, width=600)
tabErrorFilesMonitoring.pack(fill=BOTH, expand=1)
mainTabs.add(tabErrorFilesMonitoring, text="Error Files Monitoring")
errorFilesFrame=LabelFrame(tabErrorFilesMonitoring,text="Error Files Monitoring", bd=5)
btnFetchErrorVendors=Button(errorFilesFrame,text="Error Files", bd=1, cursor="hand2")
btnFetchArchiveVendors=Button(errorFilesFrame,text="Archive Files", bd=1, cursor="hand2")
lbErrorVendors=Listbox(errorFilesFrame)
lbErrorVendorsFiles=Listbox(errorFilesFrame)
#btnFetchErrorFilesList=Button(errorFilesFrame,text=">>>>", bd=2, cursor="hand2")
btnDownloadErrorFilesList=Button(errorFilesFrame,text="Download Files", bd=1, cursor="hand2")
btnDownloadLogFile=Button(errorFilesFrame,text="Download Log", bd=1, cursor="hand2")
btnSelectFolder=Button(errorFilesFrame, bg="red",fg="yellow", text="Choose Folder", bd=2, cursor="hand2")
errorFilesFrame.place(x=30,y=50,height=410,width=520)
btnFetchErrorVendors.place(x=30,y=20)
btnFetchArchiveVendors.place(x=130,y=20)
vScrollBar1=Scrollbar(errorFilesFrame,orient=VERTICAL, command=lbErrorVendors.yview)
vScrollBar1.place(x=215,y=50, height=280)
hScrollBar1=Scrollbar(errorFilesFrame,orient=HORIZONTAL, command=lbErrorVendors.xview)
hScrollBar1.place(x=5,y=330, width=210)
lbErrorVendors.config(selectmode=EXTENDED,  yscrollcommand=vScrollBar1.set, xscrollcommand=hScrollBar1.set, exportselection=0) 
lbErrorVendors.place(x=5,y=50, height=280, width=210)
vScrollBar2=Scrollbar(errorFilesFrame,orient=VERTICAL, command=lbErrorVendorsFiles.yview)
vScrollBar2.place(x=485,y=50, height=280)
hScrollBar2=Scrollbar(errorFilesFrame,orient=HORIZONTAL, command=lbErrorVendorsFiles.xview)
hScrollBar2.place(x=245,y=330, width=240)
lbErrorVendorsFiles.config(selectmode=EXTENDED, yscrollcommand=vScrollBar2.set,xscrollcommand=hScrollBar2.set) 
lbErrorVendorsFiles.place(x=245,y=50, height=280, width=240)
lblErrorFilesCount=Label(errorFilesFrame,text="")
lblErrorFilesCount.place(x=245,y=15)
lblLogSize=Label(errorFilesFrame,text="")
lblLogSize.place(x=5,y=345)
#btnFetchErrorFilesList.place(x=210,y=150)
btnDownloadErrorFilesList.place(x=350,y=355)
btnDownloadLogFile.place(x=75,y=355)
btnOpenSelectedFolder=Button(errorFilesFrame, fg="blue",text="Open Folder", bd=0, cursor="hand2")
btnSelectFolder.place(x=315, y=20)
getDir=""
errorFiles={}
dirErrArc=""
logPath="/home/asentinel/logs/"


tabDeployJar=Frame(mainTabs,height=600, width=600)
tabDeployJar.pack(fill=BOTH, expand=1)

mainTabs.add(tabDeployJar, text="Deploy Mapper Jar")

deployJarFrame=LabelFrame(tabDeployJar,text="Deploy Mapper Jar", bd=5)
uploadProgress=Progressbar(deployJarFrame, orient = HORIZONTAL, length = 380, mode = 'determinate')
deployJarFrame.place(x=100,y=50,height=200,width=400)
ckboxDeleteOldBackups=IntVar()
chkDeleteOldBackups=Checkbutton(deployJarFrame,text = "Delete all old Backups?", variable = ckboxDeleteOldBackups)
chkDeleteOldBackups.place(x=120,y=40)
btnUploadJar=Button(deployJarFrame,text="Upload JAR", bd=1, cursor="hand2")
btnUploadJar.place(x=150,y=70)
jarFilePath=""   


tabKickoffLaunch=Frame(mainTabs,height=600, width=600)
tabKickoffLaunch.pack(fill=BOTH, expand=1)

mainTabs.add(tabKickoffLaunch, text="Manual Kickoff Launch")

frameManualkickoffLaunch=LabelFrame(tabKickoffLaunch,text="Manually Start Mapper Flow", bd=5)
frameManualkickoffLaunch.place(x=100,y=50,height=200,width=400)
lblSelectVendor=Label(frameManualkickoffLaunch,text="Select Vendor / Mapper")
lblSelectVendor.place(x=30, y=45)
getVendorsList = StringVar()
cbSelectVendor=Combobox(frameManualkickoffLaunch, textvariable=getVendorsList)
cbSelectVendor.place(x=170,y=45)
btnUploadUploadForKickOff=Button(frameManualkickoffLaunch,text="Upload Files and Launch Script", bd=1, cursor="hand2")
btnUploadUploadForKickOff.place(x=115,y=90)
progressUploadUploadForKickOff=Progressbar(frameManualkickoffLaunch, orient = HORIZONTAL, length = 180, mode = 'determinate')
getUploadSourceFiles=""



tabSettings=Frame(mainTabs,height=600, width=600)
tabSettings.pack(fill=BOTH, expand=1)

mainTabs.add(tabSettings, text="Settings")
frameSFTP=LabelFrame(tabSettings,text="SFTP Settings", bd=5)

txtSFTPServerID=Entry(frameSFTP, width=30)
txtSFTPHost=Entry(frameSFTP, width=30)
txtSFTPUserId=Entry(frameSFTP, width=30)
txtSFTPPWD=Entry(frameSFTP, width=30, show="*")
txtSFTPRootPath=Entry(frameSFTP, width=30)
txtSFTPSearchPath=Entry(frameSFTP, width=30)
txtSFTPOIRJATPath=Entry(frameSFTP, width=30)
txtSFTPLOGPath=Entry(frameSFTP, width=30)
txtSFTPAppName=Entry(frameSFTP, width=30)
txtSFTPJARExtn=Entry(frameSFTP, width=30)

chkDefaultVar=StringVar()

chkboxIsDefault=Checkbutton(frameSFTP, text="Save as Default", variable = chkDefaultVar, onvalue = "YES", offvalue = "NO")

btnSettingsSave=Button(frameSFTP,text="Save Settings", bd=1, cursor="hand2")

lblConnecting=Label(tabSettings, text="", font="helvetica 18 bold")
    

userName =""
ip =""
pwd ="" 
remote_root_path =""
oirJarPath=""
searchPath=""
applicationName=""
jarExtension=""
serverName=""
isDefault="No"
getServerList = ["ADD NEW SERVER"]
opSelectServer=""


Folders_Files=""
remote_path=""
ftp_client=""
client=""
folderName=""
applicationName=""
jarExtension=""



def connectSFTP():
    global remote_path
    global ftp_client
    global client 
    global getVendorsList
    global sftpStatus
    
    sftpStatus=f"Connecting to {serverName}....."
    lblConnecting.config(text=sftpStatus)
    
    try:
        frameSFTP.place_forget()
        lblConnecting.place(x=150, y=50)
        r.title(f"{r_title} [{sftpStatus}]")
        client = pk.SSHClient()
        client.set_missing_host_key_policy(pk.AutoAddPolicy())
        client.connect(hostname=ip, port=22, username=userName, password=pwd)
    
        remote_path = remote_root_path 
        ftp_client = client.open_sftp()
        getVendorsList=ftp_client.listdir(remote_root_path)
        cbSelectVendor["values"]=getVendorsList

        sftpStatus=f"Connected to {serverName}"
        
#         r.bind("<Button-3>", do_popup)
#         r.unbind("<Button-1>")
        r.title(f"{r_title} [{sftpStatus}] [" + str(newMapperFrame.winfo_pointerx()-newMapperFrame.winfo_rootx()) + " : " + str(newMapperFrame.winfo_pointery()-newMapperFrame.winfo_rooty()) + "]")

        
# This exception takes care of Authentication error& exceptions
    except pk.AuthenticationException:
        sftpStatus="Authentication Error"
        r.title(f"{r_title} [{sftpStatus}]")
        lblConnecting.config(sftpStatus)
            
# This exception will take care of the rest of the error& exceptions
    except Exception as e:
        sftpStatus=f"Connection Error - {e}"
        r.title(f"{r_title} [{sftpStatus}]")
        lblConnecting.config(sftpStatus)
    finally:
        lblConnecting.place_forget()
        frameSFTP.place(x=100,y=50,height=420,width=400)

    
    
def startConnectSFTP():
        threading.Thread(target=connectSFTP, daemon=True).start()


def fetchServerDetails(value):
    global userName , ip , pwd , remote_root_path , oirJarPath , searchPath, applicationName, jarExtension, serverName, isDefault, logPath
    global opSelectServer, getServerList
    lblSFTPX=15
    txtSFTPX=140
    sftpY=20

    try:
        conn = sqlite3.connect('resources/settings.db')
        cursor1= conn.execute("Select count(*) from TBL_SETTINGS")
        if value=="ADD NEW SERVER":
            txtSFTPServerID.delete(0, END)
            txtSFTPHost.delete(0, END)
            txtSFTPUserId.delete(0, END)
            txtSFTPPWD.delete(0, END)
            txtSFTPRootPath.delete(0, END)
            txtSFTPSearchPath.delete(0, END)
            txtSFTPOIRJATPath.delete(0, END)
            txtSFTPLOGPath.delete(0, END)
            txtSFTPAppName.delete(0, END)
            txtSFTPJARExtn.delete(0, END)
            chkDefaultVar.set(0)
        elif value=="":
            try:
                cursor = conn.execute("select SERVERNAME from TBL_SETTINGS")
                for rec in cursor:
                    strValue=rec[0]
# Creating dynamic Functions
                    print("Creating dynamic Functions")
                    print(f"def {rec[0]}():\n   fetchServerDetails('{rec[0]}')\n   startConnectSFTP()")
                    exec(f"def {rec[0]}():\n   fetchServerDetails('{rec[0]}')\n   startConnectSFTP()")
                    exec(f"menuServer.add_command(label='{strValue}', command={strValue} )") #, command=lambda:{strValue()}    fetchServerDetails(str(rec[0])))
                    getServerList.append(rec[0])
                    
                cursor_default = conn.execute("select SERVERNAME from TBL_SETTINGS where upper(ISDEFAULT)='YES'")
                for rec_default in cursor_default:
                    fetchServerDetails(rec_default[0])
                    startConnectSFTP()
                    
            except Exception as e:
                print("No Servers added " + str(e))
        elif value=="Save" and varServer.get()=="ADD NEW SERVER":
            print("Adding New Server")
            try:
                conn.execute(f"""INSERT INTO TBL_SETTINGS (SERVERNAME,HOSTNAME,USERNAME,PWD,ROOTPATH,SEARCHPATH,OIRJARPATH,APPLICATIONNAME,JAREXTENSION, ISDEFAULT, LOGFILEPATH)
                VALUES ('{txtSFTPServerID.get()}',
                 '{txtSFTPHost.get()}',
                  '{txtSFTPUserId.get()}', 
                  '{txtSFTPPWD.get()}', 
                  '{txtSFTPRootPath.get()}',
                  '{txtSFTPSearchPath.get()}',
                  '{txtSFTPOIRJATPath.get()}',
                  '{txtSFTPAppName.get()}',
                  '{txtSFTPJARExtn.get()}',
                  '{chkDefaultVar.get()}',
                   '{txtSFTPLOGPath.get()}')""" )
                conn.commit()
                getServerList.append(txtSFTPServerID.get())
                opSelectServer.place_forget()
                opSelectServer= OptionMenu(frameSFTP, varServer, *getServerList, command=fetchServerDetails)
                varServer.set(txtSFTPServerID.get())
                opSelectServer.place(x=txtSFTPX+10,y=sftpY-10)
                exec(f"def {txtSFTPServerID.get()}():\n   fetchServerDetails('{txtSFTPServerID.get()}')\n   startConnectSFTP()")
                exec(f"menuServer.add_command(label='{txtSFTPServerID.get()}', command={txtSFTPServerID.get()} )") #, command=lambda:{strValue()}    fetchServerDetails(str(rec[0])))
                
            except Exception as e:
                print(e)
                        
        elif value=="Save" and varServer.get()!="ADD NEW SERVER":
            print("update")
            try:
                conn.execute("""UPDATE TBL_SETTINGS 
                            SET ISDEFAULT='NO'""" )
                conn.commit()

                conn.execute("""UPDATE TBL_SETTINGS 
                            SET 
                            SERVERNAME='"""+txtSFTPServerID.get() +"""',
                            HOSTNAME='""" +txtSFTPHost.get() + """',
                            USERNAME='"""+txtSFTPUserId.get()+"""',
                            PWD='"""+txtSFTPPWD.get()+"""',
                            ROOTPATH='"""+txtSFTPRootPath.get()+"""',
                            SEARCHPATH='"""+txtSFTPSearchPath.get()+"""',
                            OIRJARPATH='"""+txtSFTPOIRJATPath.get()+"""',
                            APPLICATIONNAME='"""+txtSFTPAppName.get()+"""',
                            JAREXTENSION='"""+txtSFTPJARExtn.get()+"""',
                            LOGFILEPATH='"""+ txtSFTPLOGPath.get() +"""',
                            ISDEFAULT='""" + chkDefaultVar.get() + """' WHERE UPPER(SERVERNAME)='""" + varServer.get() +"'" )
                conn.commit()
                
                
                getServerList.remove(varServer.get())
                getServerList.append(txtSFTPServerID.get())
                
                menuServer.delete(varServer.get())
                exec(f"def {txtSFTPServerID.get()}():\n   fetchServerDetails('{txtSFTPServerID.get()}')\n   startConnectSFTP()")
                exec(f"menuServer.add_command(label='{txtSFTPServerID.get()}', command={txtSFTPServerID.get()} )") #, command=lambda:{strValue()}    fetchServerDetails(str(rec[0])))
                
                opSelectServer.place_forget()
                opSelectServer= OptionMenu(frameSFTP, varServer, *getServerList, command=fetchServerDetails)
                varServer.set(txtSFTPServerID.get())
                opSelectServer.place(x=txtSFTPX+10,y=sftpY-10)
                
                
                    
            except Exception as e:
                print(e)
        else:
            try:
                
                cursor = conn.execute(f"select SERVERNAME,HOSTNAME,USERNAME,PWD,ROOTPATH,SEARCHPATH,OIRJARPATH,APPLICATIONNAME,JAREXTENSION,LOGFILEPATH,ISDEFAULT from TBL_SETTINGS WHERE SERVERNAME='{value}'")
                for r in cursor:
                    serverName=r[0]
                    txtSFTPServerID.delete(0, END)
                    txtSFTPServerID.insert(0,serverName)
                    ip = r[1] 
                    txtSFTPHost.delete(0, END)
                    txtSFTPHost.insert(0,ip)
                    userName = r[2]
                    txtSFTPUserId.delete(0, END)
                    txtSFTPUserId.insert(0,userName)
                    pwd = r[3] 
                    txtSFTPPWD.delete(0, END)
                    txtSFTPPWD.insert(0,pwd)
                    remote_root_path = r[4] 
                    txtSFTPRootPath.delete(0, END)
                    txtSFTPRootPath.insert(0,remote_root_path)
                    searchPath = r[5]
                    txtSFTPSearchPath.delete(0, END)
                    txtSFTPSearchPath.insert(0,searchPath)
                    oirJarPath = r[6]
                    txtSFTPOIRJATPath.delete(0, END)
                    txtSFTPOIRJATPath.insert(0,oirJarPath)
                    applicationName = r[7]
                    txtSFTPAppName.delete(0, END)
                    txtSFTPAppName.insert(0,applicationName)
                    jarExtension = r[8]
                    txtSFTPJARExtn.delete(0, END)
                    txtSFTPJARExtn.insert(0,jarExtension)
                    logPath = r[9]
                    txtSFTPLOGPath.delete(0, END)
                    txtSFTPLOGPath.insert(0,logPath)
                    chkDefaultVar.set(r[10])
                    varServer.set(value)
            except Exception as e:
                print(e)
    except:
        conn.execute('''CREATE TABLE TBL_SETTINGS
        (SERVERNAME TEXT PRIMARY KEY     NOT NULL,
        HOSTNAME TEXT    NOT NULL,
        USERNAME           TEXT    NOT NULL,
        PWD            TEXT    NOT NULL,
        ROOTPATH        TEXT    NOT NULL,
        SEARCHPATH         TEXT    NOT NULL,
        OIRJARPATH        TEXT    NOT NULL,
        APPLICATIONNAME         TEXT    NOT NULL,                          
        JAREXTENSION        TEXT    NOT NULL,
        ISDEFAULT        TEXT    NOT NULL,
        LOGFILEPATH      TEXT    NOT NULL);''')
    finally:
        conn.close()
        
menuBar.add_cascade(label="Select Server", menu=menuServer)        









# 
# r.bind("<Button-1>", do_popup)

fetchServerDetails("")


frameSFTP.place(x=100,y=50,height=420,width=400)
opSelectServer= OptionMenu(frameSFTP, varServer, *getServerList, command=fetchServerDetails)
opSelectServer.place(x=txtSFTPX+10,y=sftpY-10)

sftpY=sftpY+30
lblServerID=Label(frameSFTP,text="Server Name: ")
lblServerID.place(x=lblSFTPX, y=sftpY)
txtSFTPServerID.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblHost=Label(frameSFTP,text="Host Name: ")
lblHost.place(x=lblSFTPX, y=sftpY)
txtSFTPHost.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPUserId=Label(frameSFTP,text="UserName: ")
lblSFTPUserId.place(x=lblSFTPX, y=sftpY)
txtSFTPUserId.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPPWD=Label(frameSFTP,text="Password: ")
lblSFTPPWD.place(x=lblSFTPX, y=sftpY)
txtSFTPPWD.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPRootPath=Label(frameSFTP,text="Root Path: ")
lblSFTPRootPath.place(x=lblSFTPX, y=sftpY)
txtSFTPRootPath.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPSearchPath=Label(frameSFTP,text="Search Path: ")
lblSFTPSearchPath.place(x=lblSFTPX, y=sftpY)
txtSFTPSearchPath.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPOIRJATPath=Label(frameSFTP,text="OIR JAR Path: ")
lblSFTPOIRJATPath.place(x=lblSFTPX, y=sftpY)
txtSFTPOIRJATPath.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPLOGPath=Label(frameSFTP,text="Log File Path: ")
lblSFTPLOGPath.place(x=lblSFTPX, y=sftpY)
txtSFTPLOGPath.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPAppName=Label(frameSFTP,text="Application Name: ")
lblSFTPAppName.place(x=lblSFTPX, y=sftpY)
txtSFTPAppName.place(x=txtSFTPX,y=sftpY)
sftpY=sftpY+30
lblSFTPJARExtn=Label(frameSFTP,text="JAR Extension: ")
lblSFTPJARExtn.place(x=lblSFTPX, y=sftpY)
txtSFTPJARExtn.place(x=txtSFTPX,y=sftpY)

sftpY=sftpY+40
txtSFTPX=txtSFTPX+10
btnSettingsSave.place(x=txtSFTPX,y=sftpY, width=100)
chkboxIsDefault.place(x=txtSFTPX+110,y=sftpY)
mainTabs.select(0)



#     
#     
# def settingsDB(mode=""):
#     global userName , ip , pwd , remote_root_path , oirJarPath , searchPath, applicationName, jarExtension
#     conn = sqlite3.connect('resources/settings.db')
#     logging.info("[" + time.strftime("%Y-%m-%d %H:%M:%S") + f"] Connecting DB to Collect Settings")    
#     try:
#         if mode=="SELECT":
#             cursor = conn.execute("select * from TBL_SETTINGS")
#             for r in cursor:
#                 ip = r[0] 
#                 txtSFTPHost.delete(0, END)
#                 txtSFTPHost.insert(0,r[0])
#                 userName = r[1]
#                 txtSFTPUserId.delete(0, END)
#                 txtSFTPUserId.insert(0,r[1])
#                 pwd = r[2] 
#                 txtSFTPPWD.delete(0, END)
#                 txtSFTPPWD.insert(0,r[2])
#                 remote_root_path = r[3] 
#                 txtSFTPRootPath.delete(0, END)
#                 txtSFTPRootPath.insert(0,r[3])
#                 searchPath = r[4]
#                 txtSFTPSearchPath.delete(0, END)
#                 txtSFTPSearchPath.insert(0,r[4])
#                 oirJarPath = r[5]
#                 txtSFTPOIRJATPath.delete(0, END)
#                 txtSFTPOIRJATPath.insert(0,r[5])
#                 applicationName = r[6]
#                 txtSFTPAppName.delete(0, END)
#                 txtSFTPAppName.insert(0,r[6])
#                 jarExtension = r[7]
#                 txtSFTPJARExtn.delete(0, END)
#                 txtSFTPJARExtn.insert(0,r[7])
#             startConnectSFTP()
#         elif mode=="UPDATE":
#             conn.execute("""UPDATE TBL_SETTINGS 
#                         SET HOSTNAME='""" +txtSFTPHost.get() + """',
#                         USERNAME='"""+txtSFTPUserId.get()+"""',
#                         PWD='"""+txtSFTPPWD.get()+"""',
#                         ROOTPATH='"""+txtSFTPRootPath.get()+"""',
#                         SEARCHPATH='"""+txtSFTPSearchPath.get()+"""',
#                         OIRJARPATH='"""+txtSFTPOIRJATPath.get()+"""',
#                         APPLICATIONNAME='"""+txtSFTPAppName.get()+"""',
#                         JAREXTENSION='"""+txtSFTPJARExtn.get()+"""'""" )
#             conn.commit()
#             settingsDB("SELECT")
#             
#             
#     except sqlite3.OperationalError as e:
#         logging.exception("[" + time.strftime("%Y-%m-%d %H:%M:%S") + f"] {e}")
#         conn.execute('''CREATE TABLE TBL_SETTINGS
#              (HOSTNAME TEXT PRIMARY KEY     NOT NULL,
#              USERNAME           TEXT    NOT NULL,
#              PWD            TEXT    NOT NULL,
#              ROOTPATH        TEXT    NOT NULL,
#              SEARCHPATH         TEXT    NOT NULL,
#              OIRJARPATH        TEXT    NOT NULL,
#              APPLICATIONNAME         TEXT    NOT NULL,                          
#              JAREXTENSION        TEXT    NOT NULL);''')
#         logging.exception("[" + time.strftime("%Y-%m-%d %H:%M:%S") + f"] Table created successfully")
#         conn.execute("INSERT INTO TBL_SETTINGS (HOSTNAME,USERNAME,PWD,ROOTPATH,SEARCHPATH,OIRJARPATH,APPLICATIONNAME,JAREXTENSION) VALUES (' ', ' ', ' ', ' ', ' ',' ',' ',' ' )" )
#         conn.commit()
#         mainTabs.select(4)
#     finally:
#         conn.close()
    
    
#btnSettingsSave.config(command=lambda:settingsDB("UPDATE"))
#settingsDB("SELECT")


btnSettingsSave.config(command=lambda:fetchServerDetails("Save"))



# userName = "mhidayathulla_sftp"
# ip = "dc1qacmddb06.prod.tangoe.com"
# pwd = "mhidayathulla_sftpeb99"
# remote_root_path = "/qamap2/external_tables/Imran/"
# oirJarPath = "/qamap2/external_tables/Imran/"
# searchPath = "/qamap2/*/Imran/*"


# txtSFTPUserId.insert("end","asentinel")
# logging.info(txtSFTPUserId.get())
# txtSFTPHost.insert(END,"dc1prodtemedi1.prod.tangoe.com" )
# txtSFTPPWD.insert(END, "fisher1715")
# txtSFTPRootPath.insert(END,"/usr/pgdata/auto_edi/vans/")
# txtSFTPOIRJATPath.insert(END,"/usr/pgdata/auto_edi/bin/oirxmlgenerator2/")
# txtSFTPSearchPath.insert(END,"~/auto_edi/vans/*/asentinel/errordir/*")
# jarExtension=".jar" 
# applicationName="asentinel"
subFolders=["in",
                   "out",
                   "transferin", 
                   "transferout", 
                   "work", 
                   "effin", 
                   "effout", 
                   "errordir", 
                   "in_archive", 
                   "out_archive", 
                   "complete",
                   "undefined"]




def startNewVendorCreation(fnType):
    
    global getVendorsList
    currFolder=txtInputVendor.get().strip().lower()
    mapperName=txtInputVendor.get().strip()
    filePattern=txtInputFilePattern.get().strip()
    clientName=txtInputClientName.get().strip().lower()
    
    errMessage=""
    if currFolder=="":
        errMessage=errMessage + "Folder Name Missing\n"
    if filePattern=="":
        errMessage=errMessage + "File Pattern Missing\n"
    if clientName=="":
        errMessage = errMessage + "Client Name Missing"
         
    if errMessage!="":
        messagebox.showerror(title="Error", message=errMessage)
        return 

    progressCreation.place(x=170,y=130)
    btn1.place_forget()
    btn2.place_forget()
    
    txtInputVendor.config(state=DISABLED)
    txtInputClientName.config(state=DISABLED)
    txtInputFilePattern.config(state=DISABLED)
             
    remote_path = remote_root_path + currFolder
     
    if fnType=="Mapper":
        progressCreation["value"]=0
        try:
            ftp_client.mkdir(remote_path) #Create remote path
        except IOError:
            print(currFolder + " Vendor already exist")
    
        progressCreation["value"]=5        
        try:
            ftp_client.mkdir(remote_path + f"/{applicationName}") #Create remote path
        except IOError:
            print(f"{applicationName} Folder already exist")
        
        progressCreation["value"]=10
        
            
        for i in subFolders:
            progressCreation["value"]=progressCreation["value"]+ (50/len(subFolders))
            try:
                ftp_client.mkdir(remote_path + f"/{applicationName}/" + str(i).lower()) #Create remote path
            except IOError:
                print(str(i).lower() + " Folder Already exist")
                 
                
# Creating Break Script
        breakScript=open("resources/break_sample.sh","r+").read()
        breakScriptW=open("resources/break.sh","w")
        breakScriptW.write(breakScript.replace("<<VENDORNAME>>", currFolder, 1).replace("<<MAPPERNAME>>", mapperName, 1).replace("<<FILEPATTERN>>", "'" + filePattern + "'", 1).replace("<<CLIENTNAME>>", clientName, 1))
        breakScriptW.close()
        progressCreation["value"]=70
        
# Creating Launch Script
        launchScript=open("resources/launch_sample.sh","r+").read()
        launchScriptW=open("resources/launch.sh","w")
        launchScriptW.write(launchScript.replace("<<VENDORNAME>>", currFolder, 1))
        launchScriptW.close()
        progressCreation["value"]=80
    
# Upload
        filepath = "resources/break.sh"
        ftp_client.put(filepath,remote_path+"/break.sh")
        stdin,stdout,stderr=client.exec_command("chmod 775 " + remote_path+"/break.sh")
        progressCreation["value"]=90
        
        filepath = "resources/launch.sh"
        ftp_client.put(filepath,remote_path+"/launch.sh")
        stdin,stdout,stderr=client.exec_command("chmod 775 " + remote_path+"/launch.sh")
        progressCreation["value"]=95
        
        os.remove("resources/break.sh", dir_fd=None)
        os.remove("resources/launch.sh", dir_fd=None)
        progressCreation["value"]=100
        lblmessage.config(text="New Mapper setup Completed Successfully ! ! !")
        
    elif fnType=="Client":
        progressCreation["value"]=0
        filepath = "resources/break.sh"
        ftp_client.get(remote_path+"/break.sh",filepath)
# Creating Break Script
        breakScript=open("resources/break.sh","r+").read().split("\n")
        linePosition=0
        getContent=""
        
        for i in range(len(breakScript),0,-1):
            if breakScript[int(i)-1].find("/home/asentinel/editransfer/")>0:
                linePosition=i
                break
        
        for j in range(0,len(breakScript)):
            getContent=getContent + breakScript[j] + "\n"
            if j==linePosition-1:
                getContent=getContent + "find ./transferout/ -maxdepth 1 -iname '" + filePattern + "' -exec mv {} /home/asentinel/editransfer/" + clientName + "/in/ \;" + "\n"
            progressCreation["value"]=progressCreation["value"]+ (80/len(breakScript))
            
        breakScriptW=open("resources/break.sh","w")
        breakScriptW.write(getContent)
        breakScriptW.close()
        ftp_client.put(filepath,remote_path+"/break.sh")
        progressCreation["value"]=100
        lblmessage.config(text="Added New Client (" + clientName.upper() + ") Successfully !")
        
    
    getVendorsList=ftp_client.listdir(remote_root_path)
    cbSelectVendor["values"]=getVendorsList
    progressCreation.place_forget()
    progressCreation["value"]=0
    btn1.place(x=150,y=130)
    btn2.place(x=270,y=130)
    txtInputVendor.config(state=NORMAL)
    txtInputClientName.config(state=NORMAL)
    txtInputFilePattern.config(state=NORMAL)

    lblmessage.place(x=75,y=0)
    txtInputClientName.delete(0, END)
    txtInputFilePattern.delete(0, END)
    txtInputVendor.delete(0, END)
    time.sleep(5)
    lblmessage.place_forget()
    
    return


def startNewCreationThread(fnType):
    if sftpStatus.upper().find("CONNECTED")>=0:
        t4=threading.Thread(target=lambda:startNewVendorCreation(fnType))
        t4.start()
    else:
        do_popup("startNewCreationThread")
        
        

btn1.config(text="Add New Mapper", command=lambda:startNewCreationThread("Mapper"))
btn2.config(text="Add New Client", command=lambda:startNewCreationThread("Client"))





def fetchErrorsFiles_Command():
    btnFetchErrorVendors.place_forget()
    btnFetchArchiveVendors.place_forget()
    progressFetchErrors=Progressbar(errorFilesFrame,orient = HORIZONTAL, length = 100, mode = 'determinate')
    progressFetchErrors.place(x=50,y=20)
    lbErrorVendors.delete(0, END)    
    lbErrorVendorsFiles.delete(0, END)
    
    global errorFiles
    
    getPathPosition=0
    getVendorName=""
    getFileName=""
    errorFiles={}
    
    getMainPathPosition=searchPath.find("*")-1
    
    try:
        if dirErrArc=="in_archive":
            searchPathM=searchPath + ".zip"
        else:
            searchPathM=searchPath
        stdin, stdout, stderr= client.exec_command(f"ls -ltr {searchPathM.replace('errordir',dirErrArc)}")
        stdout=stdout.readlines()
        
        for line in stdout:
            progressFetchErrors["value"]=progressFetchErrors["value"]+(100/len(stdout))
            getPathPosition=str(line).replace("~", "", 1).find(searchPath.replace("~", "", 1)[0:getMainPathPosition])
            getVendorName=str(line)[getPathPosition+len(searchPath.replace("~","")[0:getMainPathPosition]):]
            getPathPosition=len(getVendorName.split("/"))-1
            getFileName=getVendorName.split("/")[getPathPosition]
            getVendorName=getVendorName.split("/")[0]
            
            if getVendorName in errorFiles:
                errorFiles[getVendorName]= f"{getFileName}#" + errorFiles[getVendorName]
            else:
                errorFiles[getVendorName]= getFileName
            
        progressFetchErrors["value"]=100
        time.sleep(0.2)
        
        for keys in errorFiles:
            lbErrorVendors.insert(END,keys)


    except SSHException:
        print(SSHException)
    finally:
        progressFetchErrors.place_forget()
        btnFetchErrorVendors.place(x=30,y=20)
        btnFetchArchiveVendors.place(x=130,y=20)
    
    return 
    

def fetchErrorFiles():

    btnFetchErrorVendors.place_forget()
    progressFetchErrors=Progressbar(errorFilesFrame,orient = HORIZONTAL, length = 100, mode = 'determinate')
    progressFetchErrors.place(x=50,y=20)
    lbErrorVendors.delete(0, END)
    errorPath=""
    global Folders_Files
    Folders_Files=""
    
    totalDir=len(ftp_client.listdir(remote_path))
    progressFetchErrors["value"]=0
    for folders in ftp_client.listdir(remote_path):
        errorPath=remote_path+folders+f"/{applicationName}/errordir"
        progressFetchErrors["value"]=progressFetchErrors["value"]+(100/totalDir)
        try:
            ftp_client.chdir(errorPath)
            Folders_Files=Folders_Files + folders
            for errorFiles in ftp_client.listdir(errorPath):
                try:
                    Folders_Files=Folders_Files + "#" + errorFiles 
                except Exception as e:
                    print(e)
            Folders_Files=Folders_Files +"~"
        except Exception as e:
            print(e)
        
        
    progressFetchErrors["value"]=0
    for splitFolders in Folders_Files.split("~"):
        progressFetchErrors["value"]=progressFetchErrors["value"]+(100/len(Folders_Files.split("~")))
        if splitFolders.find("#")>0:
            lbErrorVendors.insert(END,splitFolders.split("#")[0])
        
    
    progressFetchErrors.place_forget()
    btnFetchErrorVendors.place(x=50,y=20)
    return 

def startErrorFetch(_dir):
    global dirErrArc
    if sftpStatus.upper().find("CONNECTED")>=0:
        dirErrArc=_dir
        t2=threading.Thread(target=fetchErrorsFiles_Command, daemon=True)
        t2.start()
    else:
        do_popup()



def fetchErrorFilesList_Command(event=""):
    try:
        global folderName
        folderName=lbErrorVendors.get(ANCHOR)
        lbErrorVendorsFiles.delete(0, END)
        for sub_files in str(errorFiles[folderName]).replace("\n","").split("#"):
            lbErrorVendorsFiles.insert(END,sub_files)
    except Exception as e:
        print(e)
    
    lblErrorFilesCount.config(text="Files Count:\n" + str(lbErrorVendorsFiles.size()))
    lblLogSize.config(text="")

    

def fetchErrorFilesList(event=""):
    global folderName
    lbErrorVendorsFiles.delete(0, END)
    for splitFolders in Folders_Files.split("~"):
        if splitFolders.find("#")>0:
            if lbErrorVendors.get(ANCHOR)==splitFolders.split("#")[0]:
                folderName=lbErrorVendors.get(ANCHOR)
                for sub_files in splitFolders.split("#"):
                    lbErrorVendorsFiles.insert(END,sub_files)
    lbErrorVendorsFiles.delete(0,0)
       


def downloadErrorFiles():
    if len(getDir)>0:
        downloadProgress=Progressbar(errorFilesFrame,orient = HORIZONTAL, length = 100, mode = 'determinate')
        downloadProgress.place(x=350,y=355)
        btnDownloadErrorFilesList.place_forget()
        btnDownloadLogFile.config(state=DISABLED)
        lbErrorVendorsFiles.config(state=DISABLED)
        downloadProgress["value"]=10
        folderName1=folderName.upper()
        os.makedirs(getDir + "/" + folderName1, exist_ok=True)
        for selectedFiles in lbErrorVendorsFiles.curselection():
            ftp_client.get(remote_path+f"{folderName}/{applicationName}/{dirErrArc}/{lbErrorVendorsFiles.get(selectedFiles)}",f"{getDir}/{folderName1}/{lbErrorVendorsFiles.get(selectedFiles)}")
            downloadProgress["value"]=downloadProgress["value"]+(100/len(lbErrorVendorsFiles.curselection()))
            
        downloadProgress.place_forget()
        lbErrorVendorsFiles.config(state=NORMAL)
        btnDownloadErrorFilesList.place(x=350,y=355)
        btnDownloadLogFile.config(state=NORMAL)
    else:
        btnSelectFolder.place_forget()
        time.sleep(0.1)
        btnSelectFolder.place(x=315, y=20)
        time.sleep(0.05)
        btnSelectFolder.place_forget()
        time.sleep(0.1)
        btnSelectFolder.place(x=315, y=20)
        time.sleep(0.05)
        btnSelectFolder.place(x=315, y=20)
        selectDirectory()
        if len(getDir)>0:
            downloadErrorFiles()
  
  
def startTh():
    global t1
    if sftpStatus.upper().find("CONNECTED")>=0:
        t1=threading.Thread(target=downloadErrorFiles, daemon=True)
        t1.start()
    else:
        do_popup("startTh")

t1=threading.Thread(target=downloadErrorFiles, daemon=True)

def downloadLogFile():
    if len(getDir)>0:
        downloadLogProgress=Progressbar(errorFilesFrame,orient = HORIZONTAL, length = 100, mode = 'determinate')
        downloadLogProgress.place(x=75,y=355)
        btnDownloadLogFile.place_forget()
        btnDownloadErrorFilesList.config(state=DISABLED)
        lbErrorVendors.config(state=DISABLED)
        stdin, stdout, stderr= client.exec_command(f"ls -sh {logPath}{folderName}.log")
        stdout=stdout.readlines()
        for line in stdout:
            lblLogSize.config(text="Log Size:\n" + str(line).replace(f" {logPath}{folderName}.log","").strip())
        downloadLogProgress["value"]=40
        ftp_client.get(f"{logPath}{folderName}.log",f"{getDir}/{folderName}.log")
        
        downloadLogProgress["value"]=100
            
        downloadLogProgress.place_forget()
        lbErrorVendors.config(state=NORMAL)
        btnDownloadLogFile.place(x=75,y=355)
        btnDownloadErrorFilesList.config(state=NORMAL)
    else:
        btnSelectFolder.place_forget()
        time.sleep(0.1)
        btnSelectFolder.place(x=315, y=20)
        time.sleep(0.05)
        btnSelectFolder.place_forget()
        time.sleep(0.1)
        btnSelectFolder.place(x=315, y=20)
        time.sleep(0.05)
        btnSelectFolder.place(x=315, y=20)
        selectDirectory()
        if len(getDir)>0:
            downloadLogFile()
        
def startThLog():
    global thStartLog
    if sftpStatus.upper().find("CONNECTED")>=0:
        thStartLog=threading.Thread(target=downloadLogFile, daemon=True)
        thStartLog.start()
    else:
        do_popup("startThLog")



def selectDirectory():
    global getDir
    getDir=askdirectory()
    if len(getDir)>0:
        btnSelectFolder.config(text="Folder Selected", fg="black", bg="light green")
        btnOpenSelectedFolder.place(x=420, y=22)
        btnOpenSelectedFolder.config(command=lambda:os.system('explorer "' + os.path.realpath(getDir) + '"'))
#        btnOpenSelectedFolder.config(command=lambda:subprocess.Popen('explorer "' + os.path.normpath(getDir) + '"',shell=True))
    
lbErrorVendors.bind("<<ListboxSelect>>", fetchErrorFilesList_Command) #fetchErrorFilesList)
#btnFetchErrorFilesList.config(command=fetchErrorFilesList_Command) 
btnDownloadErrorFilesList.config(command=startTh)
btnDownloadLogFile.config(command=startThLog)
btnSelectFolder.config(command=selectDirectory)
btnFetchErrorVendors.config(command=lambda:startErrorFetch("errordir"))
btnFetchArchiveVendors.config(command=lambda:startErrorFetch("in_archive"))

    

def uploadJAR():
    now=time.strftime("%Y%m%d%H%M%S")
    jarFileName=str(os.path.basename(jarFilePath))
    jarFileNamebk=jarFileName[0:jarFileName.find(jarExtension)] + "_bk_"
                    
    fullRemoteJarPath=oirJarPath+jarFileName
    fullRemoteBackupJar=oirJarPath+jarFileName.replace(jarExtension,f"_bk_{now}{jarExtension}")
    
    btnUploadJar.place_forget()
    uploadProgress.place(x=1,y=60,height=40)    
    uploadProgress["value"]=80
    for folder in ftp_client.listdir(oirJarPath):
        if folder.find(jarFileNamebk)>=0 and folder.find(jarExtension)>0 and folder !=os.path.basename(fullRemoteBackupJar) and ckboxDeleteOldBackups.get()==1:
            ftp_client.remove(oirJarPath+folder)
            continue
        
        if folder==jarFileName:
            ftp_client.rename(fullRemoteJarPath,fullRemoteBackupJar)
        
    ftp_client.put(jarFilePath, fullRemoteJarPath)
    uploadProgress["value"]=100
    uploadProgress.place_forget()
    btnUploadJar.place(x=150,y=70)

def startUploadJar():
    global jarFilePath
    if sftpStatus.upper().find("CONNECTED")>=0:
        jarFilePath=askopenfilename(title="Select Files") 
        if len(jarFilePath)>0:
            t3=threading.Thread(target=uploadJAR, daemon=True)
            t3.start()
    else:
        do_popup("startUploadJar")

btnUploadJar.config(command=startUploadJar)



def UploadSourceFilesLaunch():
    btnUploadUploadForKickOff.place_forget()
    progressUploadUploadForKickOff.place(x=115, y=90)
    progressUploadUploadForKickOff["value"]=0
    for file in getUploadSourceFiles:
        ftp_client.put(file, remote_root_path+cbSelectVendor.get()+"/"+ applicationName+"/in/"+os.path.basename(file))
        progressUploadUploadForKickOff["value"]=progressUploadUploadForKickOff["value"]+(100/len(getUploadSourceFiles))
        

    stdin, stdout, stderr= client.exec_command(f"{remote_root_path}{cbSelectVendor.get()}/launch.sh")
    
    stdout=stdout.readlines()
    stderr=stderr.readlines()
    messagebox.showerror(title="Error List", message=stderr)
    progressUploadUploadForKickOff.place_forget()
    btnUploadUploadForKickOff.place(x=115, y=90)
    progressUploadUploadForKickOff["value"]=0

def startUploadSourceFilesLaunch():
    global getUploadSourceFiles
    if sftpStatus.upper().find("CONNECTED")>=0:
        getUploadSourceFiles=askopenfilenames()
        if len(getUploadSourceFiles)>0:
            threadUploadSourceFiles=threading.Thread(target=UploadSourceFilesLaunch, daemon=True)
            threadUploadSourceFiles.start()
    else:
        do_popup("startUploadSourceFilesLaunch")


btnUploadUploadForKickOff.config(command=startUploadSourceFilesLaunch)
        

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        try:
            ftp_client.close()
            client.close()
        except:
            pass
        r.destroy()

def getPos(event):
    r.title(f"{r_title} [{sftpStatus}] [" + str(errorFilesFrame.winfo_pointerx()-errorFilesFrame.winfo_rootx()) + " : " + str(errorFilesFrame.winfo_pointery()-errorFilesFrame.winfo_rooty()) + "]")


def do_popup(func=""):
    try:
        menuServer.tk_popup(r.winfo_pointerx(),r.winfo_pointery())
        
    finally:
        menuServer.grab_release()
        if sftpStatus.upper().find("CONNECTED")>=0:
            if func=="startNewCreationThread":
                startNewCreationThread()
            elif func=="startTh":
                startTh()
            elif func=="startUploadJar":
                startUploadJar()
            elif func=="startUploadSourceFilesLaunch":
                startUploadSourceFilesLaunch()

 
r.bind("<Motion>",getPos)
r.protocol("WM_DELETE_WINDOW", on_closing)
r.config(menu=menuBar)
r.mainloop()


