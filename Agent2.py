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


def conn_thread(conn, addr):  # TCP服务器端处理逻辑
    print('Accept new connection from %s:%s.' % addr)  # 接受新的连接请求
    msg = conn.recv(1024)
    req = eval(msg.decode('utf-8'))  # 将客户端的请求信息转换为字典类型
    print(req)
    handle_req(conn, req)
    print("本次请求处理完毕，正在断开连接...")
    conn.close()
    print("连接已关闭...\n")


def handle_req(conn, req):  # 处理前端请求
    if req['type'] == 'list_all_shapes':  # 前端向后台发送请求，获取最外层目录
        response = {
            "type": "list_all_shapes",
            "all_shapenames": list_all_shapes()
        }
        filename = req['clientfilename']
        send_j_response(conn,response,filename)

    elif req['type'] == 'list_doc_tree':  # 前端向后台发送请求，获取指定内层目录
        doc_tree = list_doc_tree(req['doc_tree_name'])
        doc_tree = eval(doc_tree)
        filename = req['clientfilename']
        send_j_response(conn, doc_tree, filename)

    elif req['type'] == 'log_in':  # 前端向后台发送请求，请求登录
        response = {
            "type": "log_in",
            "error_message": check_user(req['user_name'], req['user_password']),
            "user_name": req['user_name'],
            "user_authority": get_user_authority(req['user_name'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'modify':  # 前端向后端发送修改用户信息请求
        response = {
            "type": "modify",
            "error_message": modify_user(req['user_name'], req['user_password'], req['user_authority'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'list_all_users':  # 前端要求列出所有用户
        response = {
            "type": "list_all_users",
            "users_num": count_users(),
            "all_users": get_user_list()
        }
        send_j_response(conn, response)

    elif req['type'] == 'add_user':  # 前端要求添加用户
        response = {
            "type": "add_user",
            "error_message": add_user(req['user_name'], req['user_password'], req['user_authority'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'delete_user':  # 前端要求删除用户
        response = {
            "type": "delete_user",
            "error_message": del_user(req['user_name'])
        }
        send_j_response(conn, response)

    elif req['type'] == 'download_file':  # 前端向后台发送请求，获得指定文件
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


def send_j_response(conn, res, filename):  # 向前台发送json压缩包
    #将json写入文件
    #filename = 'req_ALEX_20170708142032_list_all_shapes.json'
    fp = open(filename, 'w')
    fp.write(json.dumps(res))
    fp.close()
	
    #将json文件打包压缩
    filename = filename.replace(".json",".tar.gz")
    t = tarfile.open(filename, "w:gz")
    filename = filename.replace(".tar.gz",".json")
    t.add(filename)
    t.close()
    filename = filename.replace(".json",".tar.gz")
    s_filename = filename.encode("UTF-8")
	
    #向client端发送文件头，包括压缩包名称和大小
   # msg = 'OK'
    #conn.sendall(msg.encode('utf-8'))
    fhead = struct.pack('<128s11I', s_filename, 0, 0, 0, 0, 0, 0, 0, 0, os.stat(filename).st_size, 0, 0)
    conn.send(fhead)
	
    #向client端发送压缩包
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
	#将文件打包压缩
    filename = filename.replace(".dat",".tar.gz")
    t = tarfile.open(filename, "w:gz")
    filename = filename.replace(".tar.gz",".dat")
    t.add(filename)
    t.close()
    filename = filename.replace(".dat",".tar.gz")
    s_filename = filename.encode("UTF-8")
	
    #向client端发送文件头，包括压缩包名称和大小
    #msg = 'OK'
    #conn.sendall(msg.encode('utf-8'))
    fhead = struct.pack('<128s11I', s_filename, 0, 0, 0, 0, 0, 0, 0, 0, os.stat(filename).st_size, 0, 0)
    conn.send(fhead)
	
    #向client端发送压缩包
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

    # 只匹配‘Out_AeroCoeGroup000’的字符
    elif old_filename.find('Out_AeroCoeGroup000') != -1:  # Out_AeroCoeGroup000*Total.dat,*号表数字，每个数字表示不同部件。数字1表示全部部件
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


def find_file(filename, obj, clientfilename):#filename是文件在数据库里的名字，obj是前端发来的文件相关信息
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
            which_file_num = obj['which_file_num'] - 1  # 在数据库中 0号文件表示所有文件信息
            db_file_id = item[filename][which_file_num]["db_file_id"]
        else:
            db_file_id = item[filename]["db_file_id"]

    bytes_data = pyMongo.getFile(fs, db_file_id)
    fp = open(clientfilename,'wb')
    fp.write(bytes_data)
    fp.close()
    return clientfilename


def search_condition(obj):  # 构成查询条件字段
    con = {
        'H': obj["h"],
        'M': obj["m"],
        'a': obj["a"],
        'b': obj["b"]
    }
    max_num = 2000000000  # 定义一个特殊参数，来删除不需要的查询条件
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
# which_file_num = obj['which_file_num'] - 1 #在数据库中 0号文件表示所有文件信息
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
            which_file_num = obj['which_file_num'] - 1  # 在数据库中 0号文件表示所有文件信息
            file_size = item[filename][which_file_num]["file_size"]
            file_authority = item[filename][which_file_num]["file_authority"]
        else:
            file_size = item[filename]["file_size"]
            file_authority = item[filename]["file_authority"]

    return file_size, file_authority


def list_all_shapes():  # 查找所有外形名（未考虑没有数据的情况）
    name_arr = []  # 定义外形名字数组
    for item in db.DOCTREE.find():
        print(item["doc_tree_name"])
        name_arr.append(item["doc_tree_name"])
    return name_arr


def list_doc_tree(name):  # 根据外形名查找对应的目录树，若没有则返回null
    doc_tree = 'null'
    for item in db.DOCTREE.find({"doc_tree_name": name}):
        doc_tree = item["content"]
    return doc_tree


def check_user(name, password):  # 验证用户名密码是否正确（未考虑用户名不存在）
    for item in db.USERS.find({"user_name": name}):  # 未考虑重名，建议注册时不可重名
        print(item["user_name"] + ',' + item["user_password"])
        if item["user_password"] == password:
            return 1
        else:
            return 0


def get_user_authority(name):  # 验证用户权限
    for item in db.USERS.find({"user_name": name}):
        print(item["user_name"] + 'authority :' + str(item["user_authority"]))
        return item["user_authority"]


def modify_user(name, new_password, new_authority):  # 修改用户信息
    for item in db.USERS.find({"user_name": name}):
        print('修改前；' + item["user_name"] + ',' + item["user_password"] + ',' + str(item["user_authority"]))
        db.USERS.update({"user_name": name}, {"$set": {"user_password": new_password, "user_authority": new_authority}})
        item2 = db.USERS.find_one({"user_name": name})
        print('修改后；' + item2["user_name"] + ',' + item2["user_password"] + ',' + str(item2["user_authority"]))
    return 1


def add_user(name, password, authority):  # 前端管理员添加用户
    if db.USERS.find({"user_name": name}).count() == 0:  # 控制不能重名
        db.USERS.insert({"user_name": name, "user_password": password, "user_authority": authority})
        item2 = db.USERS.find_one({"user_name": name})
        print('添加；' + item2["user_name"] + ',' + item2["user_password"] + ',' + str(item2["user_authority"]))
        return 1
    else:
        return 0


def del_user(name):  # 前端管理员删除用户
    item = db.USERS.remove({"user_name": name})
    if item['n'] == 1:
        return 1
    else:
        return 0


def count_users():  # 计算用户数量
    users_num = db.USERS.find().count()
    return users_num


def get_user_list():  # 获得所有用户信息列表
    user_arr = []
    for item in db.USERS.find({}, {"_id": 0}):
        j_user_arr = json.dumps(item)
        user_arr.append(j_user_arr)
    print(user_arr)
    return user_arr

if __name__ == "__main__":
    cli, db, fs = pyMongo.get_cli_db_fs()
    print(" 数据库链接完毕")
    s = socket.socket()

    host = socket.gethostname()
    port = 4396
    s.bind((host, port))

    s.listen(5)
    print("服务正在启动...")

    while True:
        sock, addr = s.accept()  # 接收一个新连接
        t1 = threading.Thread(target=conn_thread, kwargs={"conn": sock, "addr": addr})
        t1.start()
