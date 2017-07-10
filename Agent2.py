# coding=gbk
import socket
import sys
import pymongo
import json
import struct
import pyMongo
import threading
import os
import tarfile
import base64


def conn_thread(conn, addr):  # TCP�������˴����߼�
    print('Accept new connection from %s:%s.' % addr)  # �����µ���������
    msg = conn.recv(1024)
    req = eval(msg.decode('utf-8'))  # ���ͻ��˵�������Ϣת��Ϊ�ֵ�����
    print(req)
    handle_req(conn, req)
    print("������������ϣ����ڶϿ�����...")
    conn.close()
    print("�����ѹر�...\n")


def handle_req(conn, req):  # ����ǰ������
    if req['type'] == 'list_all_shapes':  # ǰ�����̨�������󣬻�ȡ�����Ŀ¼
        response = {
            "type": "list_all_shapes",
            "all_shapenames": list_all_shapes()
        }
        filename = req['clientfilename']
        send_j_response(conn,response,filename)

    elif req['type'] == 'list_doc_tree':  # ǰ�����̨�������󣬻�ȡָ���ڲ�Ŀ¼
        doc_tree = list_doc_tree(req['doc_tree_name'])
        doc_tree = eval(doc_tree)
        filename = req['clientfilename']
        send_j_response(conn, doc_tree, filename)

    elif req['type'] == 'log_in':  # ǰ�����̨�������������¼
        response = {
            "type": "log_in",
            "error_message": check_user(req['user_name'], req['user_password']),
            "user_name": req['user_name'],
            "user_authority": get_user_authority(req['user_name'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'modify':  # ǰ�����˷����޸��û���Ϣ����
        response = {
            "type": "modify",
            "error_message": modify_user(req['user_name'], req['user_password'], req['user_authority'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'list_all_users':  # ǰ��Ҫ���г������û�
        response = {
            "type": "list_all_users",
            "users_num": count_users(),
            "all_users": get_user_list()
        }
        send_j_response(conn, response)

    elif req['type'] == 'add_user':  # ǰ��Ҫ������û�
        response = {
            "type": "add_user",
            "error_message": add_user(req['user_name'], req['user_password'], req['user_authority'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'delete_user':  # ǰ��Ҫ��ɾ���û�
        response = {
            "type": "delete_user",
            "error_message": del_user(req['user_name'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'download_file':  # ǰ�����̨�������󣬻��ָ���ļ�
        new_filename = name_switch(req['file_name']['which_file'])
        send_file(conn, find_file(new_filename, req['file_name'],req['clientfilename']))
        # if req['ack'] == 1:
            # file = find_file(new_filename, req['file_name'])
            # print(conn.send(file))
        # else:
            # file_length, file_authority = get_file_information(new_filename, req['file_name'])
            # response = {
                # "type": "download_file",
                # "file_length": file_length,
                # "file_authority": file_authority,
                # "file_name": req['file_name']['which_file']
            # }
            # send_j_response(conn, response)
    else:
        print('Wrong request!')


def send_j_response(conn, res, filename):  # ��ǰ̨����jsonѹ����
    #��jsonд���ļ�
    #filename = 'req_ALEX_20170708142032_list_all_shapes.json'
    fp = open(filename, 'w')
    fp.write(json.dumps(res))
    fp.close()
	
    #��json�ļ����ѹ��
    filename = filename.replace(".json",".tar.gz")
    t = tarfile.open(filename, "w:gz")
    filename = filename.replace(".tar.gz",".json")
    t.add(filename)
    t.close()
    filename = filename.replace(".json",".tar.gz")
    s_filename = filename.encode("UTF-8")
	
    #��client�˷����ļ�ͷ������ѹ�������ƺʹ�С
   # msg = 'OK'
    #conn.sendall(msg.encode('utf-8'))
    fhead = struct.pack('<128s11I', s_filename, 0, 0, 0, 0, 0, 0, 0, 0, os.stat(filename).st_size, 0, 0)
    conn.send(fhead)
	
    #��client�˷���ѹ����
    t = open(filename, 'rb')
    while 1:
        filedata = t.read(1024)
        if not filedata: break
        conn.sendall(filedata)
    t.close()
    os.remove(filename)
    filename = filename.replace(".tar.gz",".json")
    os.remove(filename)
    print(res)

def send_file(conn, filename):
	#���ļ����ѹ��
    filename = filename.replace(".dat",".tar.gz")
    t = tarfile.open(filename, "w:gz")
    filename = filename.replace(".tar.gz",".dat")
    t.add(filename)
    t.close()
    filename = filename.replace(".dat",".tar.gz")
    s_filename = filename.encode("UTF-8")
	
    #��client�˷����ļ�ͷ������ѹ�������ƺʹ�С
    #msg = 'OK'
    #conn.sendall(msg.encode('utf-8'))
    fhead = struct.pack('<128s11I', s_filename, 0, 0, 0, 0, 0, 0, 0, 0, os.stat(filename).st_size, 0, 0)
    conn.send(fhead)
	
    #��client�˷���ѹ����
    t = open(filename, 'rb')
    while 1:
        filedata = t.read(1024)
        if not filedata: break
        conn.sendall(filedata)
    t.close()
    os.remove(filename)
    filename = filename.replace(".tar.gz",".dat")
    os.remove(filename)

def name_switch(old_filename):
    if old_filename == "Input_ConfigForceMoment.dat":
        new_filename = "configForceMoment"

    elif old_filename == "Input_ConfigSolver.dat":
        new_filename = "configSolver"

    elif old_filename == "Out_Record.dat":
        new_filename = "record"

    # ֻƥ�䡮Out_AeroCoeGroup000�����ַ�
    elif old_filename.find('Out_AeroCoeGroup000') != -1:  # Out_AeroCoeGroup000*Total.dat,*�ű����֣�ÿ�����ֱ�ʾ��ͬ����������1��ʾȫ������
        new_filename = "forceMomentGroup"

    elif old_filename == "Out_TecFileFieldBnd.dat":
        new_filename = "fieldPatchsTec"

    elif old_filename == "statistics":
        new_filename = "statistics"

    elif old_filename == "shape":
        new_filename = "shape"

    else:
        print('Wrong name_switch!')
        new_filename = 'null'

    return new_filename


def find_file(filename, obj, clientfilename):#filename���ļ������ݿ�������֣�obj��ǰ�˷������ļ������Ϣ
    if filename == "statistics":
        item = db["STATISTICS"].find_one({"shape_name": obj[shape_name]})
        db_file_id = item[filename]["db_file_id"]

    elif filename == "shape":
        item = db["SHAPE"].find_one({"shape_name": obj[shape_name]})
        db_file_id = item[filename]["db_file_id"]

    else:
        seq = (obj["shape_name"], obj["grid_name"])
        col_name = "_".join(seq)
        con = search_condition(obj)
        item = db[col_name].find_one(con)
        if filename == "forceMomentGroup":
            which_file_num = obj['which_file_num'] - 1  # �����ݿ��� 0���ļ���ʾ�����ļ���Ϣ
            db_file_id = item[filename][which_file_num]["db_file_id"]
        else:
            db_file_id = item[filename]["db_file_id"]

    bytes_data = pyMongo.getFile(fs, db_file_id)
    fp = open(clientfilename,'wb')
    fp.write(bytes_data)
    fp.close()
    return clientfilename


def search_condition(obj):  # ���ɲ�ѯ�����ֶ�
    con = {
        'H': obj["h"],
        'M': obj["m"],
        'a': obj["a"],
        'b': obj["b"]
    }
    max_num = 2000000000  # ����һ�������������ɾ������Ҫ�Ĳ�ѯ����
    if obj["h"] == max_num:
        del con['H']
    if obj["m"] == max_num:
        del con['M']
    if obj["a"] == max_num:
        del con['a']
    if obj["b"] == max_num:
        del con['b']

    print(con)
    return con


# def get_file_size(filename,obj):
# if filename == "statistics":
# item = db["STATISTICS"].find_one({"shape_name":shape_name })
# file_size = item[filename]["file_size"]

# elif filename =="shape":
# item = db["SHAPE"].find_one({"shape_name":shape_name })
# file_size = item[filename]["file_size"]

# else :
# seq = (obj["shape_name"],obj["grid_name"])
# col_name ="_".join(seq)
# con = search_condition(obj)
# item = db[col_name].find_one(con)
# if filename == "forceMomentGroup":
# which_file_num = obj['which_file_num'] - 1 #�����ݿ��� 0���ļ���ʾ�����ļ���Ϣ
# file_size = item[filename][which_file_num]["file_size"]
# else:
# file_size = item[filename]["file_size"]

# return file_size

def get_file_information(filename, obj):
    if filename == "statistics":
        item = db["STATISTICS"].find_one({"shape_name": shape_name})
        file_size = item[filename]["file_size"]
        file_authority = item[filename]["file_authority"]

    elif filename == "shape":
        item = db["SHAPE"].find_one({"shape_name": shape_name})
        file_size = item[filename]["file_size"]
        file_authority = item[filename]["file_authority"]

    else:
        seq = (obj["shape_name"], obj["grid_name"])
        col_name = "_".join(seq)
        con = search_condition(obj)
        item = db[col_name].find_one(con)
        if filename == "forceMomentGroup":
            which_file_num = obj['which_file_num'] - 1  # �����ݿ��� 0���ļ���ʾ�����ļ���Ϣ
            file_size = item[filename][which_file_num]["file_size"]
            file_authority = item[filename][which_file_num]["file_authority"]
        else:
            file_size = item[filename]["file_size"]
            file_authority = item[filename]["file_authority"]

    return file_size, file_authority


def list_all_shapes():  # ����������������δ����û�����ݵ������
    name_arr = []  # ����������������
    for item in db.DOCTREE.find():
        print(item["doc_tree_name"])
        name_arr.append(item["doc_tree_name"])
    return name_arr


def list_doc_tree(name):  # �������������Ҷ�Ӧ��Ŀ¼������û���򷵻�null
    doc_tree = 'null'
    for item in db.DOCTREE.find({"doc_tree_name": name}):
        doc_tree = item["content"]
    return doc_tree


def check_user(name, password):  # ��֤�û��������Ƿ���ȷ��δ�����û��������ڣ�
    for item in db.USERS.find({"user_name": name}):  # δ��������������ע��ʱ��������
        print(item["user_name"] + ',' + item["user_password"])
        if item["user_password"] == password:
            return 1
        else:
            return 0


def get_user_authority(name):  # ��֤�û�Ȩ��
    for item in db.USERS.find({"user_name": name}):
        print(item["user_name"] + 'authority :' + str(item["user_authority"]))
        return item["user_authority"]


def modify_user(name, new_password, new_authority):  # �޸��û���Ϣ
    for item in db.USERS.find({"user_name": name}):
        print('�޸�ǰ��' + item["user_name"] + ',' + item["user_password"] + ',' + str(item["user_authority"]))
        db.USERS.update({"user_name": name}, {"$set": {"user_password": new_password, "user_authority": new_authority}})
        item2 = db.USERS.find_one({"user_name": name})
        print('�޸ĺ�' + item2["user_name"] + ',' + item2["user_password"] + ',' + str(item2["user_authority"]))
    return 1


def add_user(name, password, authority):  # ǰ�˹���Ա����û�
    if db.USERS.find({"user_name": name}).count() == 0:  # ���Ʋ�������
        db.USERS.insert({"user_name": name, "user_password": password, "user_authority": authority})
        item2 = db.USERS.find_one({"user_name": name})
        print('��ӣ�' + item2["user_name"] + ',' + item2["user_password"] + ',' + str(item2["user_authority"]))
        return 1
    else:
        return 0


def del_user(name):  # ǰ�˹���Աɾ���û�
    item = db.USERS.remove({"user_name": name})
    if item['n'] == 1:
        return 1
    else:
        return 0


def count_users():  # �����û�����
    users_num = db.USERS.find().count()
    return users_num


def get_user_list():  # ��������û���Ϣ�б�
    user_arr = []
    for item in db.USERS.find({}, {"_id": 0}):
        j_user_arr = json.dumps(item)
        user_arr.append(j_user_arr)
    print(user_arr)
    return user_arr

if __name__ == "__main__":
    cli, db, fs = pyMongo.get_cli_db_fs()
    print(" ���ݿ��������")
    s = socket.socket()

    host = socket.gethostname()
    port = 4396
    s.bind((host, port))

    s.listen(5)
    print("������������...")

    while True:
        sock, addr = s.accept()  # ����һ��������
        t1 = threading.Thread(target=conn_thread, kwargs={"conn": sock, "addr": addr})
        t1.start()
