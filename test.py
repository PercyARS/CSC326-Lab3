import unittest
import os
from crawler import crawler

class TestCrawler(unittest.TestCase):

    _crawler = None

    def test_Document(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        with self._crawler._db_conn:
            c = self._crawler._db_conn.cursor()
            c.execute('SELECT * FROM Document WHERE doc_url=?', ('http://individual.utoronto.ca/peixizhao/',))
            result = c.fetchone()[1]
            self.assertEqual(result, 'http://individual.utoronto.ca/peixizhao/')

    def test_Lexicon(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        with self._crawler._db_conn:
            c = self._crawler._db_conn.cursor()
            c.execute('SELECT * FROM Lexicon WHERE words=?', ('facebook',))
            result = c.fetchone()[1]
            self.assertEqual(result, 'facebook')

    def test_Lexicon(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        with self._crawler._db_conn:
            c = self._crawler._db_conn.cursor()
            c.execute('SELECT * FROM Lexicon WHERE words=?', ('facebook',))
            result = c.fetchone()[1]
            self.assertEqual(result, 'facebook')

    def test_PageRank_main(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        with self._crawler._db_conn:
            c = self._crawler._db_conn.cursor()
            c.execute('SELECT * FROM Document WHERE doc_url=?', ('http://individual.utoronto.ca/peixizhao/',))
            main_doc_id = c.fetchone()[0]
            c.execute('SELECT rank FROM PageRank WHERE DocId=?', (main_doc_id,))
            result = c.fetchone()[0]
            self.assertEqual(result, 0.150000000000000027)

    def test_PageRank_branch(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        with self._crawler._db_conn:
            c = self._crawler._db_conn.cursor()
            c.execute('SELECT * FROM Document WHERE doc_url=?', ('http://individual.utoronto.ca/peixizhao/branch1.html',))
            branch_doc_id = c.fetchone()[0]
            c.execute('SELECT rank FROM PageRank WHERE DocId=?', (branch_doc_id,))
            result = c.fetchone()[0]
            self.assertEqual(result, 0.0)


    def test_invertedIndex(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        self.assertEqual(self._crawler.get_inverted_index(), {1: set([1, 2]), 2: set([1]), 3: set([1, 2]), 4: set([1, 2])
            , 5: set([1, 2]), 6: set([1, 2]), 7: set([1]), 8: set([1]), 9: set([1]), 10: set([1]), 11: set([2]),
                                                              12: set([2]), 13: set([2]), 14: set([2]), 15: set([2]), 16: set([2])})

    def test_resolvedIndex(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        self.assertEqual(self._crawler.get_resolved_inverted_index(), {u'2': set([u'http://individual.utoronto.ca/peixizhao/']),
                                                                       u'going': set([u'http://individual.utoronto.ca/peixizhao/']),
                                                                       u'what': set([u'http://individual.utoronto.ca/peixizhao/']),
                                                                       u'google': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'apple': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'baidu': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'two': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'page': set([u'http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'percy': set([u'http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'base': set([u'http://individual.utoronto.ca/peixizhao/']),
                                                                       u'facebook': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'branch': set([u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'world': set([u'http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'hi': set([u'http://individual.utoronto.ca/peixizhao/']),
                                                                       u'one': set([u'http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html']),
                                                                       u'hello': set([u'http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html'])})

    def test_invertedIndex2(self):
        """test individual element in the returned result"""
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        inverted_index_dict = self._crawler.get_inverted_index()
        self.assertEqual(inverted_index_dict[3], set([1,2]))

    def test_resolvedIndex2(self):
        with open('test_urls.txt', 'w') as f:
            f.write("http://individual.utoronto.ca/peixizhao/")
        self._crawler = crawler(None, 'test_urls.txt', 'test.db')
        self._crawler.crawl(depth = 1)
        resolved_inverted_index_dict = self._crawler.get_resolved_inverted_index()
        self.assertEqual(resolved_inverted_index_dict['page'], set(['http://individual.utoronto.ca/peixizhao/', u'http://individual.utoronto.ca/peixizhao/branch1.html']))


if __name__ == '__main__':
    # first get rid of the old db
    os.system("rm test.db")
    unittest.main()
