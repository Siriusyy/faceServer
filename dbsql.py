# 导入pymysql模块
import datetime

import pymysql
import configparser
import os


def getPriprietoById(id):
    cf = configparser.ConfigParser()
    cf.read(os.path.expanduser('~') + "/acs/config.ini")

    # 连接database
    conn = pymysql.connect(host=cf.get("mysql", "host"), user=cf.get("mysql", "user"),
                           password=cf.get("mysql", "password"), database=cf.get("mysql", "database"), charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cur = conn.cursor()
    # 定义要执行的SQL语句
    sql = """
    select name from proprietor where id=
    """ + str(id)
    try:
        cur.execute(sql)  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录

        # 遍历结果
        for row in results:
            name = row[0]
            return name

            # print(name)
        return None
    except Exception as e:
        raise e
    finally:
        conn.close()  # 关闭连接


def getallem():
    cf = configparser.ConfigParser()
    cf.read(os.path.expanduser('~') + "/acs/config.ini")

    # 连接database
    conn = pymysql.connect(host=cf.get("mysql", "host"), user=cf.get("mysql", "user"),
                           password=cf.get("mysql", "password"), database=cf.get("mysql", "database"), charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cur = conn.cursor()
    # 定义要执行的SQL语句
    sql = """
    select * from embedding
    """
    try:
        cur.execute(sql)  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录

        # 遍历结果

        return results
    except Exception as e:
        raise e
    finally:
        conn.close()  # 关闭连接


def insertOrUpdateEm(id, embedding):
    cf = configparser.ConfigParser()
    cf.read(os.path.expanduser('~') + "/acs/config.ini")

    # 连接database
    conn = pymysql.connect(host=cf.get("mysql", "host"), user=cf.get("mysql", "user"),
                           password=cf.get("mysql", "password"), database=cf.get("mysql", "database"), charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cur = conn.cursor()
    text = ""
    for em in embedding:
        text = text + str(em) + ","
    text = text[0:len(text) - 1]
    # 定义要执行的SQL语句
    sql = """
    select * from embedding where pid = %s   
    """

    try:
        cur.execute(sql, (id,))  # 执行sql语句
        results = cur.fetchall()  # 获取查询的所有记录
        if len(results) > 0:
            sql = """
            update embedding set embed = %s where pid = %s
            """
            res = cur.execute(sql, (text, id))  # 执行sql语句
        else:
            sql = """
                    insert into embedding values( %s,%s)
                    """
            res = cur.execute(sql, (id, text))  # 执行sql语句
        conn.commit()
        return res

    except Exception as e:
        raise e
    finally:
        conn.close()  # 关闭连接


def insertVlogs(address, name, status):
    cf = configparser.ConfigParser()
    cf.read(os.path.expanduser('~') + "/acs/config.ini")

    # 连接database
    conn = pymysql.connect(host=cf.get("mysql", "host"), user=cf.get("mysql", "user"),
                           password=cf.get("mysql", "password"), database=cf.get("mysql", "database"), charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cur = conn.cursor()

    # 定义要执行的SQL语句
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        insert into visitorlog(`date`,address,proName,status)values (%s,%s,%s,%s)
        """
    try:

        res = cur.execute(sql, (time, address, name, status))  # 执行sql语句
        conn.commit()
        return res

    except Exception as e:
        raise e
    finally:
        conn.close()  # 关闭连接


# insertVlogs("127.0.0.1","钟无艳","1")
# name = getPriprietoById("1")
# print(name)
