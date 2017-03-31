import sqlite3
from collections import defaultdict

# 读取全唐诗
def read_qts(file_name):
  qts_list = []
  authors_set = set()
  # 逐行读取诗歌
  with open(file_name, 'r', encoding = 'utf-8') as f:
    for line in f:
      text_segs = line.split()
      title = text_segs[1]
      author = text_segs[2]
      poem = text_segs[-1]

      authors_set.add(author)

      # 去除非汉字字符
      valid_char_list = [c for c in poem if '\u4e00' <= c <= '\u9fff' or c == '，' or c == '。']
      validated_poem = ''.join(valid_char_list)
      # 按照作者、标题、内容的格式保存
      qts_list.append((author, title, validated_poem))

  return qts_list, authors_set


# 从CBDB中获取诗人们的别名
def get_alter_names_from_CBDB(db_file, authors_set, manual_defuzzy_authors_id):
  tang_begin_year = 618  # 唐朝建立年份
  tang_end_year = 907  # 唐朝灭亡年份

  # 手动排查的诗人集合
  mannual_defuzzy_authors = set(manual_defuzzy_authors_id.keys())

  authors_not_in_CBDB = set()
  fuzzy_authors = set()
  fuzzy_authors_details = {}
  alter_names_dict = defaultdict(set)

  conn = sqlite3.connect(db_file)
  cursor = conn.cursor()
  for author in authors_set:
    # 如果在手动排查集合中，直接使用
    if author in mannual_defuzzy_authors:
      author_id = manual_defuzzy_authors_id[author]
    else: # 否则从CBDB中查询
      # import ipdb; ipdb.set_trace()
      # 某些诗人的名字在全唐诗中和CBDB中不一致，用模糊搜索更好
      # 比如"贯休"在CBDB中的名字为"释贯休"
      author_pattern = '%' + author
      cursor.execute('SELECT c_personid, c_birthyear, c_deathyear FROM BIOG_MAIN WHERE c_name_chn LIKE?',
                     (author_pattern,))
      person_info_list = cursor.fetchall()

      # 排除重名现象
      # 具体策略请参考我的微信公众号(mrqianjinsi)文章《计算机告诉你，唐朝诗人之间的关系到底是什么样的？》
      candidate_author_ids = []
      # import ipdb; ipdb.set_trace()
      for person_id, birth_year, death_year in person_info_list:
        if birth_year and death_year:  # 生卒年俱全
          if birth_year < tang_end_year and death_year > tang_begin_year:
            # 一旦找到一个生卒年俱全且和唐朝有交集的，就不看其他的了
            candidate_author_ids = [person_id]
            break
        elif birth_year or death_year:  # 只有生年或者卒年
          year = birth_year if birth_year else death_year
          if year > tang_begin_year and year < tang_end_year:
            candidate_author_ids.append(person_id)

      # 候选名单为空或者多于一个人的候选名单都不要
      if not candidate_author_ids:
        authors_not_in_CBDB.add(author)
        # print('can\'t find valid items for %s' % author)
        continue
      elif len(candidate_author_ids) > 1:
        fuzzy_authors.add(author)
        fuzzy_authors_details[author] = candidate_author_ids
        # print('fuzzy authors: %s' % author)
        continue

      author_id = candidate_author_ids[0]

    # 根据author_id找出诗人别名
    cursor.execute('SELECT c_alt_name_chn FROM ALTNAME_DATA WHERE c_personid=?',
                   (author_id,))
    alt_name_list = cursor.fetchall()
    for alt_name in alt_name_list:
      # 不要只有一个字的别称
      if len(alt_name[0]) > 1:
        alter_names_dict[author].add(alt_name[0])

  conn.close()

  # 经过CBDB过滤过的诗人，接下来只分析这些人之间的关系
  authors_filtered_by_CBDB = authors_set - authors_not_in_CBDB - fuzzy_authors

  return alter_names_dict, authors_filtered_by_CBDB
