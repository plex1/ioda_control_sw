from tinydb import TinyDB, Query, where
import datetime


class AbstractTestCase(object):

    def __init__(self, TestCaseName, id=''):
        self.time =datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        prefix = self.time
        if id != '':
            prefix = id
        prefix = prefix+'_' + TestCaseName
        self.logger = Logger(prefix)
        self.checker = Checker(prefix)
        self.TestCaseName=TestCaseName
        self.prefix = prefix

    @staticmethod
    def gen_id(self):
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # @abstractmethod
    def exectue(self):
        print("Execute Test")

    #@abstractmethod
    def evaluate(self):
        print("Analyze Test")


class TestCase1(AbstractTestCase):

    def __init__(self, framework=[]):
        self.fw = framework
        TestCaseName = 'TestCase1'
        super().__init__(TestCaseName, id)

    def execute(self):
        self.checker.check('is_equal', 2, 2, 'test if is equal')
        self.checker.check('is_equal', 2, 3, 'test if is equal')
        self.logger.add_data('measurement1', 'x', [1, 2, 3, 4, 5, 6, 7])

    def evaluate(self):
        pass

class Logger(object):

    def __init__(self, prefix='1', purge=False):
        self.num_checks = 0
        self.num_errors = 0
        self.log = []
        self.testid = 'Test1'
        self.verbose = True
        self.tags = []
        self.db = TinyDB('db/' + prefix +'_logger.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_data(self, name, data):
        self.db.insert({'Name': name,
                        'data' : data,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_data(self, name):
        return self.db.search(self.query.Name == name)[0]['dataset']


    #def add_dataset(self, name, name_1, dataset_1, name_2, dataset_2):
    #    pass


class Checker(object):

    def __init__(self, prefix='1', purge=False):
        self.num_checks = 0
        self.num_errors = 0
        self.log = []
        self.testid = 'Test1'
        self.verbose = True
        self.print_errors = True
        self.tags = []
        self.db = TinyDB('db/' + prefix +'_checker.json')
        if purge:
            self.db.purge_tables
        self.query = Query()

    def check(self,  check_type, actual, expected, description):
        eval_checks = {
            'is_equal': (lambda actual, expected: actual == expected),
            'is_smaller': (lambda actual, expected: actual < expected),
            'is_greater': (lambda actual, expected: actual > expected),
            'is_smaller_equal': (lambda actual, expected: actual <= expected),
            'is_greater_equal': (lambda actual, expected: actual >= expected),
            'is_bit_set': (lambda actual, expected: (actual>>expected) & 1 == 1),
            'is_bit_cleared': (lambda actual, expected: (actual >> expected) & 1 == 1),
            'is_bit_equal': (lambda actual, expected: (actual >> expected['offset']) & 1 == expected['value'])
        }

        check_ok = eval_checks[check_type](actual, expected)

        if self.verbose:
            print('[Check] ' + check_type+', actual: ' + str(actual) + ', expected: '+str(expected))

        if self.verbose and (self.print_errors and (not check_ok)):
            print('[Check] [Error] ' + check_type+', actual: ' + str(actual) + ', expected: '+str(expected))

        self.log_check(check_type, actual, expected, description, check_ok)

        return check_ok

    def log_check(self, check_type, actual, expected, description, check_ok):

        self.db.insert({'Description': description,
                        'Type': check_type,
                        'Actual': actual,
                        'Expected': expected,
                        'CheckOk': check_ok,
                        'TestID': self.testid,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

        self.num_checks += 1
        if check_ok == False:
            self.num_errors += 1

    def db_get_num_checks(self):
        return len(self.db.all())

    def db_get_num_error_checks(self):
        return len(self.db.search(where('CheckOk') == False))

    def get_summary(self):
        strr='Total checks: '+ str(self.db_get_num_checks()) + ', Number of errors: ' + str(self.db_get_num_error_checks())
        return strr

    def get_log(self):
        strr=self.db.all()
        return strr

    def print_summary(self):
        print(self.get_summary())

    def print_log(self):
        print(self.get_log())

    def write_to_file(self, filename):
        f = open(filename, "w+")
        f.write(self.get_summary())
        #f.write(str(self.get_log()))
        f.close()
        pass


def main():

    checker = Checker()
    checker.check('is_equal', 2, 2, 'test if is equal')
    checker.check('is_equal', 2, 3, 'test if is equal')
    checker.print_summary()
    checker.print_log()

    tc1 = TestCase1()
    tc1.execute()


if __name__ == "__main__":
    main()