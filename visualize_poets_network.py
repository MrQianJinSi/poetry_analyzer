import pickle
import argparse
import os
import math

# 如果需要，可以用opencc实现繁体和简体之间的转换
# 需要在电脑上安装opencc
# opencc = 'opencc -i echart_visualize/poets_network_early.html -o echart_visualize/poets_network_early_zhs.html -c zht2zhs.ini'


# 直接获取排名前visulize_range的引用关系
def get_concerned_relations_by_range(reference_relations_counter, visulize_range):
  # 获取引用关系
  relations = reference_relations_counter.most_common(visulize_range)
  max_refer_count = relations[0][1]
  min_refer_count = relations[-1][1]

  return relations, max_refer_count, min_refer_count

# 获取指定诗人群体之间的引用关系，适合画出某个群体内部的网络
def get_concerned_relations_by_authors(reference_relations_counter, authors):
  # 获取指定作者群体内部的引用关系
  relations = []
  max_refer_count = 0
  min_refer_count = 10000
  for (refered_by, refered), count in reference_relations_counter.items():
    # 不统计自引用的count
    if refered_by == refered:
      continue
    if refered_by in authors and refered in authors:
      if count > max_refer_count:
        max_refer_count = count
      if count < min_refer_count:
        min_refer_count = count

      relations.append(((refered_by, refered), count))

  return relations, max_refer_count, min_refer_count

# 有些时候如果画出所有关系会显得非常拥挤，用count_to_plot_threshold来控制最小显示出来的关系
# 只有引用数大于等于count_to_plot_threshold的关系才会显示出来
def generate_html_page(relations, max_refer_count, min_refer_count, saved_html_file, count_to_plot_threshold = 1):
  html_dir = os.path.dirname(saved_html_file)
  html_head_path = os.path.join(html_dir, 'html_head.txt')
  html_tail_path = os.path.join(html_dir, 'html_tail.txt')

  min_link_width = 0.5
  max_link_width = 3.0

  # 因为引用关系的强弱范围很大，对其开方降低变化范围，画图更直观
  max_refer_count = math.sqrt(max_refer_count)
  min_refer_count = math.sqrt(min_refer_count)
  width_slope = (max_link_width - min_link_width) / (max_refer_count - min_refer_count)
  # 格式化links数据
  links_text = 'links: [\n'
  links_item_format = """{source: '%s', target: '%s',
  lineStyle:{normal:{width: %f}}},
  """
  filtered_authors = set()
  for (refered_by, refered), count in relations:
    # 跳过自引用，不然有可能画出孤立节点
    if refered_by == refered:
      continue
    # 小于门限跳过
    if count < count_to_plot_threshold:
      continue

    filtered_authors.add(refered_by)
    filtered_authors.add(refered)
    count = math.sqrt(count)
    line_width = min_link_width + width_slope * (count - min_refer_count)
    links_text += links_item_format % (refered_by, refered, line_width)

  links_text += '],\n'

  # 格式化node数据
  data_text = 'data:[\n'
  data_item_format = "{name: '%s'},\n"
  for author in filtered_authors:
    data_text += data_item_format % author

  data_text += '],\n'

  # 读取html的head和tail部分
  with open(html_head_path, 'r', encoding = 'utf-8') as f:
    head_text = f.read()

  with open(html_tail_path, 'r', encoding = 'utf-8') as f:
    tail_text = f.read()

  # 合并存储为html
  with open(saved_html_file, 'w', encoding = 'utf-8') as f:
    f.write(head_text + data_text + links_text + tail_text)


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--relations_path', type=str, default='save/reference_relations.pkl',
                      help='file to load relations data')
  parser.add_argument('--data_dir', type=str, default='data',
                      help='directory to load authors file')
  parser.add_argument('--html_dir', type=str, default='html',
                      help='directory to save html page')

  args = parser.parse_args()

  with open(args.relations_path, 'rb') as f:
    reference_relations_counter, reference_relations_text = pickle.load(f)

  # 生成全唐排名前100的关系图
  relations, max_refer_count, min_refer_count = get_concerned_relations_by_range(reference_relations_counter, 100)
  saved_html = os.path.join(args.html_dir, 'full_tang_poets_net.html')
  generate_html_page(relations, max_refer_count, min_refer_count, saved_html)

  # 生成初唐、盛唐、中唐、晚唐四个时期的诗人关系图
  #                      诗人名字文件              社交关系图网页              引用数门限
  files_name_array = [('early_tang_poets.txt', 'early_tang_poets_net.html',  1),
                      ('high_tang_poets.txt',  'high_tang_poets_net.html',   2),
                      ('middle_tang_poets.txt','middle_tang_poets_net.html', 2),
                      ('late_tang_poets.txt',  'late_tang_poets_net.html',   1)]

  for authors_file_name, html_file_name, threshold in files_name_array:
    authors_file_path = os.path.join(args.data_dir, authors_file_name)
    with open(authors_file_path, 'r', encoding='utf-8') as f:
      text = f.read()
    authors = set(text.split())

    relations, max_refer_count, min_refer_count = get_concerned_relations_by_authors(reference_relations_counter, authors)

    saved_html = os.path.join(args.html_dir, html_file_name)
    generate_html_page(relations, max_refer_count, min_refer_count, saved_html, threshold)


if __name__ == '__main__':
  main()
