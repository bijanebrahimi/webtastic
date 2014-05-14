import re
import os
from hashlib import md5
from fileentry import FileEntry

class SourceTree:
  """ Class doc """
  path = None
  tree = {}
  hash_tree = {}
  
  def __init__ (self, path="source"):
    """ Class initialiser """
    if path is not None:
      self.path = path
      self.__traverse__()
    else:
      # TODO: raise ValueError Exception
      pass
  
  def __traverse__ (self):
    """ Function doc """
    for dirname, dirnames, filenames in os.walk(self.path):
      for filename in filenames:
        file_path=os.path.join(dirname, filename)
        keys = dirname.split("/")
        keys.append(filename)
        keys.append(file_path)
        self.set_names(*keys)
        self.hash_tree[md5(file_path).hexdigest()] = FileEntry(file_path, self.path)
  
  def __recursive_values__(self, node):
    res = []
    for key in node:
      if isinstance(node[key], str):
        res.append(node[key])
      else:
        res += self.__recursive_values__(node[key])
    return res
  
  def set_names(self, *args):
    dic = self.tree
    for key in args[:-2]:
        dic = dic.setdefault(key, {})
    dic[args[-2]] = args[-1]
  
  def get_names(self, *args):
    dic = self.tree
    for key in args[:-1]:
      dic = dic.setdefault(key, {})
    return dic.get(args[-1], None)

  def get_file_names(self, *args):
    files = self.get_names(*args)
    return filter(lambda x: x if x[-3:]=='.md' else None, files)
  
  def get_dir_names(self, *args):
    files = self.get_names(*args)
    return filter(lambda x: x if x[-3:]!='.md' else None, files)
  
  def get_all_file_names(self, *args):
    base = self.get_names(*args)
    return self.__recursive_values__(base)
  
  def get_entries(self, *args):
    filenames = self.get_file_names(*args)
    path=os.path.join(*args)
    res = []
    for filename in filenames:
      filepath = os.path.join(path, filename)
      res.append(self.hash_tree[md5(filepath).hexdigest()])
    return res
  
  def get_all_entries(self, *args):
    filenames = self.get_all_file_names(*args)
    path=os.path.join(*args)
    res = []
    for filename in filenames:
      res.append(self.hash_tree[md5(filename).hexdigest()])
    return res
