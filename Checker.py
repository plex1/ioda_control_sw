from tinydb import TinyDB, Query
import datetime


class AbstractTestCase(object):

    def __init__(self, TestCaseName, id=''):
        self.time =datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        prefix = self.time+'_' + TestCaseName
        self.logger = Logger(prefix)
        self.checker = Checker(prefix)


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
        super().__init__(TestCaseName)

    def execute(self):
        self.checker.check('is_equal', 2, 2, 'test if is equal')
        self.checker.check('is_equal', 2, 3, 'test if is equal')
        self.logger.add_dataset('measurement1', 'x', [1,2,3,4,5,6,7])

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

    def add_dataset(self, name,  dataset):
        self.db.insert({'Name': name,
                        'dataset' : dataset,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

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

    def print_summary(self):
        print('Total Checks: '+ str(self.num_checks) + ', Errors Checks: '+ str(self.num_errors))

    def print_log(self):
        print(self.db.all())


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