# -*- coding: utf-8 -*-
import yaml
from yaml import Loader, SafeLoader
import re
import os
from hashlib import md5


def construct_yaml_str(self, node):
  # Override the default string handling function 
  # to always return unicode objects
  return self.construct_scalar(node)
Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

def utf8(func):
  def inner(*args, **kwargs):
    output = func(*args, **kwargs)
    if isinstance(output, str):
      output = output.decode('utf8')
    return output
  return inner


class FileEntry:
  """ Class doc """
  root = None
  path = None
  data = None
  data_content = None
  data_attr = {}
  
  def __init__ (self, path="./", root=None):
    """ Class initialiser """
    # TODO: add ERROR handlers for bad path
    self.path = path
    if root is None:
      root = re.search("^([^/]+)", path).groups()[0]
    self.root = root
    self.__parse__()
  
  def __parse__(self):
    f = open(self.path)
    self.data =f.read()
    try:
      # FIXME: possible only yaml content is broken
      data_attr, data_content = self.data.split("-"*10)[1:]
      
      self.data_attr = yaml.load(data_attr)
      self.data_content = data_content
    except:
      # TODO: Raise an Exception
      pass
  
  def attr (self, key=None):
    """ Function doc """
    return self.data_attr.get(key, None)
  
  def __getattr__ (self, key):
    """ Function doc """
    if key in self.__dict__:
      return self.__dict__[key]
    elif key in self.data_attr:
      return self.data_attr[key]
    else:
      return None
  
  @property
  def attrs (self):
    """ Function doc """
    return self.data_attr
  
  @property
  @utf8
  def content (self):
    """ Function doc """
    if self.data_content:
      return self.data_content
  
  @property
  def basename (self):
    """ Function doc """
    return os.path.split(self.path)[1][:-3]
  
  @property
  def name (self):
    """ Function doc """
    return os.path.split(self.path)[1]
  
  @property
  def link (self):
    """ Function doc """
    return self.path.replace(self.root, '').replace('.md', '.html')
  
  @property
  def ctime (self):
    """ Function doc """
    return int(os.path.getctime(self.path))
  
  @property
  def mtime (self):
    """ Function doc """
    return int(os.path.getmtime(self.path))
  
  @property
  def atime (self):
    """ Function doc """
    return int(os.path.getatime(self.path))


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
