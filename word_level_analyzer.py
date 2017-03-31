from collections import Counter, defaultdict
import thulac
import pickle
import os
import argparse

import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

# 对全唐诗分词
def cut_qts_to_words(qts_file, saved_words_file):
  save_dir = os.path.dirname((saved_words_file))
  dumped_file = os.path.join(save_dir, 'qts_words_stat_result.pkl')

  if os.path.exists(dumped_file) and os.path.exists(saved_words_file):
    print('find preprocessed data, loading directly...')
    with open(dumped_file, 'rb') as f:
      char_counter, author_counter, vocab, word_counter, genre_counter = pickle.load(f)
  else:
    char_counter = Counter()  # 字频统计
    author_counter = Counter()  # 每个作者的写诗篇数
    vocab = set()  # 词汇库
    word_counter = Counter()  # 词频统计
    genre_counter = defaultdict(Counter)  # 针对每个词性的Counter

    fid_save = open(saved_words_file, 'w', encoding = 'utf-8')
    lex_analyzer = thulac.thulac()  # 分词器
    line_cnt = 0
    with open(qts_file, 'r', encoding = 'utf-8') as f:
      for line in f:
        text_segs = line.split()
        author = text_segs[2]
        author_counter[author] += 1

        poem = text_segs[-1]
        # 去除非汉字字符
        valid_char_list = [c for c in poem if '\u4e00' <= c <= '\u9fff' or c == '，' or c == '。']
        for char in valid_char_list:
          char_counter[char] += 1

        regularized_poem = ''.join(valid_char_list)
        word_genre_pairs = lex_analyzer.cut(regularized_poem)

        word_list = []
        for word, genre in word_genre_pairs:
          word_list.append(word)
          vocab.add(word)
          word_counter[word] += 1
          genre_counter[genre][word] += 1

        save_line = ' '.join(word_list)
        fid_save.write(save_line + '\n')

        if line_cnt % 10 == 0:
          print('%d poets processed.' % line_cnt)
        line_cnt += 1

    fid_save.close()
    # 存储下来
    dumped_data = [char_counter, author_counter, vocab, word_counter, genre_counter]
    with open(dumped_file, 'wb') as f:
      pickle.dump(dumped_data, f)

  return char_counter, author_counter, genre_counter

# 将分词结果转换为向量
def word2vec(words_file):
  save_dir = os.path.dirname((words_file))
  vector_file = os.path.join(save_dir, 'word_vectors.model')

  if os.path.exists(vector_file):
    print('find word vector file, loading directly...')
    model = Word2Vec.load(vector_file)
  else:
    print('calculating word vectors...')
    model = Word2Vec(LineSentence(words_file), size=400, window=3, min_count=10,
                     workers=multiprocessing.cpu_count())
    # 将计算结果存储起来，下次就不用重新计算了
    model.save(vector_file)

  return model

def print_stat_results(char_counter, author_counter, genre_counter, vector_model):
  def print_counter(counter):
    for k, v in counter:
      print(k, v)
  # 诗人写作数量排名
  print('\n诗人写作数量排名')
  print_counter(author_counter.most_common(10))

  # 基于字的分析
  print('\n\n基于字的分析')
  # 常用字排名
  print('\n常用字排名')
  print_counter(char_counter.most_common(12))
  # 季节排名
  print('\n季节排名')
  for c in ['春', '夏', '秋', '冬']:
    print(c, char_counter[c])
  # 颜色排名
  print('\n颜色排名')
  colors = ['红', '白', '青', '蓝', '绿', '紫', '黑', '黄']
  for c in colors:
    print(c, char_counter[c])
  # 植物排名
  print('\n植物排名')
  plants = ['梅', '兰', '竹', '菊', '松', '柳', '枫', '桃', '梨', '杏']
  for p in plants:
    print(p, char_counter[p])
  # 动物排名
  print('\n动物排名')
  age_animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
  for a in age_animals:
    print(a, char_counter[a])

  # 基于词的分析
  print('\n\n基于词的分析')
  # 地名排名
  print('\n地名词排名')
  print_counter(genre_counter['ns'].most_common(10))
  # 时间排名
  print('\n时间词排名')
  print_counter(genre_counter['t'].most_common(10))
  # 场景排名
  print('\n场景词排名')
  print_counter(genre_counter['s'].most_common(10))


  # 基于词向量的分析
  print('\n\n基于词向量的分析')
  # print(vector_model['今日'])
  def print_similar_words(word):
    print('\n与"%s"比较意思比较接近的词' % word)
    print_counter(vector_model.most_similar(word))

  print_similar_words('天子')
  print_similar_words('寂寞')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--qts_path', type=str, default='data/qts_zhs.txt',
                      help='file path of Quan Tangshi')
  parser.add_argument('--words_path', type=str, default='save/qts_words_list.txt',
                      help='file path to save Quan Tangshi words data')
  args = parser.parse_args()

  # 检查存储目录是否存在
  save_dir = os.path.dirname(args.words_path)
  if not os.path.isdir(save_dir):
    os.makedirs(save_dir)

  char_counter, author_counter, genre_counter = cut_qts_to_words(args.qts_path, args.words_path)
  vector_model = word2vec(args.words_path)

  print_stat_results(char_counter, author_counter, genre_counter, vector_model)


if __name__ == '__main__':
    main()
