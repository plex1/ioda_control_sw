from tinydb import TinyDB, Query, where
import datetime


class DataLogger(object):

    def __init__(self, prefix='1', purge=False):
        self.num_checks = 0
        self.num_errors = 0
        self.log = []
        self.testid = 'Test1'
        self.stage = 'T'
        self.verbose = True
        self.tags = []
        self.db = TinyDB('db/' + prefix +'_logger.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    # stage: T: check during test execution
    #        P: check during post processing (evaluate)
    def set_stage(self, stage):
        self.stage = stage

    def remove_stage(self, stage):
        self.db.remove(where('Stage') == stage)

    def start_eval(self):
        self.set_stage('P')
        self.remove_stage('P')

    def start_exec(self):
        self.set_stage('T')
        self.remove_stage('T')

    def add_data(self, name, data):
        self.db.insert({'Name': name,
                        'data' : data,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'Stage': self.stage
                        })

    def get_data(self, name):
        return self.db.search(self.query.Name == name)[0]['data']


class Checker(object):

    def __init__(self, prefix='1', purge=False): #todo: add testcase/ testid, also add it as a field in the db
        self.num_checks = 0
        self.num_errors = 0
        self.log = []
        self.testid = prefix
        self.verbose = True
        self.print_errors = True
        self.tags = []
        self.db = TinyDB('db/' + prefix +'_checker.json')
        self.prefix = prefix
        self.stage = 'T'
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def purge(self):
        self.db.purge_tables()

    def clear_tags(self):
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    # stage: T: check during test execution
    #        P: check during post processing (evaluate)
    def set_stage(self, stage):
        self.stage = stage

    def remove_stage(self, stage):
        self.db.remove(where('Stage') == stage)

    def start_eval(self):
        self.set_stage('P')
        self.remove_stage('P')

    def start_exec(self):
        self.set_stage('T')
        self.remove_stage('T')

    def check(self,  check_type, actual, expected, description, additional_tags=[]):
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

        self.log_check(check_type, actual, expected, description, check_ok, additional_tags)

        return check_ok

    def log_check(self, check_type, actual, expected, description, check_ok, additional_tags):

        self.db.insert({'Description': description,
                        'Type': check_type,
                        'Actual': actual,
                        'Expected': expected,
                        'CheckOk': check_ok,
                        'TestID': self.testid,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'Stage' : self.stage,
                        'Tags' : self.tags + additional_tags
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


if __name__ == "__main__":
    main()