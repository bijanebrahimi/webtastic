#!/usr/bin/python
from lib import SourceTree
import jinja2
import markdown
import os
import datetime
import re

TEMPLATE_PATH = "./template/"
TEMPLATE_OPTIONS = {}


def write_file (path, content):
  """ Function doc """
  f = open(path, 'w')
  f.write(content.encode('utf8'))
  f.close()
  # TODO: return by Exceptions
  return True

def main():
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH), **TEMPLATE_OPTIONS)
  def markdownify(text):
    return markdown.markdown(text)
  def sort_navbar (items):
    return sorted(items, key = lambda x: x.navbar.get('row', None) if x.navbar is not None else 'Z' , reverse=False)
  def sort_ctime (items, reverse=False):
    return sorted(items, key = lambda x: x.ctime , reverse=reverse)
  def printable_date (timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return datetime.datetime.strftime(date, "%B %d, %Y")
  def iso_date (timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return datetime.datetime.strftime(date, "%Y-%m-%dT%H:%M:%SZ")
  def short_story (content):
    titles = []
    for title in re.findall("((\* )?##[^\n]+)", content):
      titles.append(title[0])
    short_story_body = '\n'.join(titles)
    return short_story_body
    
  env.filters.update(markdown=markdownify)
  env.filters.update(sort_navbar=sort_navbar)
  env.filters.update(sort_ctime=sort_ctime)
  env.filters.update(printable_date=printable_date)
  env.filters.update(iso_date=iso_date)
  env.filters.update(short_story=short_story)
    
  source = SourceTree('source')
  
  for entry in source.get_all_entries('source'):
    if entry.content is not None:
      # TODO: define default layout
      print 'html' + entry.link
      template = env.get_template('%s.html' % entry.attr('layout'))
      output_file = os.path.join('html/', entry.link[1:])
      output_content = template.render(page=entry, source=source)
      write_file(output_file, output_content)
      # print template.render(page=entry)
  
  # for f in tree.all_files():
  #   generate_html_file(f)
  #   f.url, f.name, f.attr('author'), f.attr('content')
  #
  # for f in tree.files('source'): => tree.root_files
  #   add_header_link(f)
  #   f.url, f.name, f.title, f.row
  pass

if __name__ == '__main__':
  main()
