# coding=utf-8


import os
import dbsql
from annoy import AnnoyIndex


def str2embed(str):
    str_list = str.split(',')
    return [float(x) for x in str_list]


class face_annoy:
    def __init__(self):
        self.f = 512
        self.annoy_index_path = os.path.abspath(os.path.expanduser('~')+"/acs/data/face_vector.nn")
        self.num_trees = 100

        self.annoy = AnnoyIndex(self.f)
        if os.path.isfile(self.annoy_index_path):
            self.annoy.load(self.annoy_index_path)

    # 从lmdb文件中建立annoy索引
    def create_index_from_lmdb(self):
        # 遍历
        # lmdb_file = self.lmdb_file
        rows = dbsql.getallem()
        if len(rows)>0:

            annoy = AnnoyIndex(self.f)
            for row in rows:
                key = row[0]
                value = str2embed(row[1])
                annoy.add_item(key, value)

            annoy.build(self.num_trees)
            annoy.save(self.annoy_index_path)

    # 重新加载索引
    def reload(self):
        self.annoy.unload()
        self.annoy.load(self.annoy_index_path)

    # 根据人脸特征找到相似的
    def query_vector(self, face_vector):
        n = 1
        return self.annoy.get_nns_by_vector(face_vector, n, include_distances=True)


if __name__ == '__main__':
    annoy = face_annoy()
    annoy.create_index_from_lmdb()
