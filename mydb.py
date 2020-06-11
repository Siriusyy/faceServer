# coding=utf-8

'''
通过facenet得到的512特征写入lmdb文件中
'''

import lmdb
import os



class mLmdb:

    def embed_to_str(self,vector):
        new_vector = [str(x) for x in vector]
        return ','.join(new_vector)

    def add_embed_to_lmdb(self,id,vector):
        if 1-os.path.exists("./data"):
            os.mkdir("./data")
        self.db_file=os.path.abspath("./data/lmdb")

        # id = str(id).encode()
        evn = lmdb.open(self.db_file);
        wfp = evn.begin(write=True)
        wfp.put(key=id.encode(), value=self.embed_to_str(vector).encode())
        wfp.commit()
        evn.close()



def str_to_embed(str):
    str_list = str.decode().split(',')
    return [float(x) for x in str_list]


if __name__ == '__main__':
    # 插入数据
    embed = mLmdb()
    embed.add_embed_to_lmdb(12, [1, 2, 0.888333, 0.12343430])

    # 遍历
    evn = lmdb.open(embed.db_file)
    wfp = evn.begin()
    for key, value in wfp.cursor():
        print
        key, str_to_embed(value)
