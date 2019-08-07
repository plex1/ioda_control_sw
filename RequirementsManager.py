from tinydb import TinyDB, Query, where
import datetime
import Checker


class RequirementsManager(object):

    def __init__(self, prefix=''):
        self.db = TinyDB('db/' + prefix +'_requirements.json')
        self.query = Query()
        self.db_results = TinyDB('db/' + prefix + '_requirements_results.json')
        self.checkers = []
        self.verbose = True

    def set_checker_list(self, checker_list):
        self.checkers = checker_list

    def add_checker(self, checker):
        self.checkers.append(checker)

    def purge(self):
        self.db.purge_tables()

    def add_requirement(self, id, description):
        self.db.insert({'id': id,
                        'description' : description,
                        'time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        })

    def compliance_purge(self):
        self.db_results.purge_tables()

    def add_requirement_compliance(self, id, description, status, num_checks, num_errors):
        self.db_results.insert({'id': id,
                        'description' : description,
                        'time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'status': status,
                        'checks_total': num_checks,
                        'checks_error' : num_errors
                        })

    def collect_checks(self):
        print('Checker Results:')
        for checker in self.checkers:
            print('TestID          : ' + checker.testid)
            print('Number of checks: ' + str(checker.db_get_num_checks()))
            print('Number of errors: ' + str(checker.db_get_num_error_checks()))
            for check in checker.db.all():
                print('- Check Description: ' + check['Description'] + ', Type: ' + str(check['Type']) +
                      ', Actual: ' + str(check['Actual']) +
                      ', Expected: ' + str(check['Expected'])
                       )

            print('--')

    def check_requirements(self):

        self.compliance_purge()
        passed = True

        for req in self.db.all():
            relevant_checks = []
            for checker in self.checkers:
                # get all checks with requirement in tag
                relevant_checks = relevant_checks + checker.db.search(checker.query.Tags.any('req_'+str(req['id'])))
            req_passed = True
            num_errors = 0
            for check in relevant_checks:
                if not check['CheckOk']:
                    num_errors += 1
                    passed = False
                    req_passed = False
            if req_passed:
                status = 'Passed'
            else:
                status = 'Failed'
            self.add_requirement_compliance(req['id'], req['description'], status, len(relevant_checks), num_errors)
            if self.verbose:
                print('[Requirement] requirement ' + req['id'] + ', number of checks: ' + str(len(relevant_checks))
                      + ', number of errors: ' + str(num_errors))
            if not req_passed:
                if self.verbose:
                    print('[Requirement] [Failed] requirement ' + req['id'] + ' failed')

        return passed

    def print_results(self):
        for req in self.db_results.all():
            st = '[Requirement] [Result] requirement ' + req['id'] + ', description: ' + req['description']
            st += ', number of checks: ' + str(req['checks_total'])
            st += ', number of errors: ' + str(req['checks_error']) + ', status: ' + req['status']
            print(st)


def main():

    # list of test cases
    c1 = Checker.Checker('c1')
    c1.purge()
    c2 = Checker.Checker('c2')
    c2.purge()
    c1.check('is_equal', 1, 1, 'equal test', ['req_100'])
    c1.check('is_greater', 1, 2, 'is greater test2', ['req_101'])
    c2.check('is_equal', 1, 1, 'equal test c2', ['req_100'])

    rm = RequirementsManager('requirements_all')
    rm.purge()
    rm.add_checker(c1)
    rm.add_checker(c2)
    rm.add_requirement('100', 'equal shall work')
    rm.add_requirement('101', 'is greater shall work')
    rm.check_requirements()

    rm.print_results()

if __name__ == "__main__":
    main()
